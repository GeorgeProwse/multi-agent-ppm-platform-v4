from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from tree_models import (
    TreeMoveRequest,
    TreeNode,
    TreeNodeCreate,
    TreeNodeUpdate,
    utc_now,
    validate_ref_for_type,
)


class TreeStore:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._lock_path = path.with_suffix(".lock")

    def list_nodes(self, tenant_id: str, project_id: str) -> list[TreeNode]:
        payload = self._load()
        nodes_raw = payload.get(tenant_id, {}).get(project_id, [])
        nodes = [TreeNode.model_validate(item) for item in nodes_raw]
        return sorted(nodes, key=lambda item: (item.sort_order, item.created_at))

    def get_node(self, tenant_id: str, project_id: str, node_id: str) -> TreeNode | None:
        payload = self._load()
        nodes_raw = payload.get(tenant_id, {}).get(project_id, [])
        for item in nodes_raw:
            if item.get("node_id") == node_id:
                return TreeNode.model_validate(item)
        return None

    def create_node(self, tenant_id: str, project_id: str, payload: TreeNodeCreate) -> TreeNode:
        payload_data = self._load()
        tenant_bucket = payload_data.setdefault(tenant_id, {})
        project_bucket = tenant_bucket.setdefault(project_id, [])
        if payload.parent_id:
            if not self._node_exists(project_bucket, payload.parent_id):
                raise ValueError("parent_id not found")
        node = TreeNode.build(tenant_id, project_id, payload)
        project_bucket.append(node.model_dump(mode="json"))
        self._write(payload_data)
        return node

    def update_node(
        self,
        tenant_id: str,
        project_id: str,
        node_id: str,
        updates: TreeNodeUpdate,
    ) -> TreeNode | None:
        payload = self._load()
        tenant_bucket = payload.setdefault(tenant_id, {})
        project_bucket = tenant_bucket.setdefault(project_id, [])
        for index, item in enumerate(project_bucket):
            if item.get("node_id") != node_id:
                continue
            node = TreeNode.model_validate(item)
            update_data = updates.model_dump(exclude_unset=True)
            if "ref" in update_data:
                update_data["ref"] = validate_ref_for_type(node.type, updates.ref)
            if update_data:
                update_data["updated_at"] = utc_now()
                node = node.model_copy(update=update_data)
                project_bucket[index] = node.model_dump(mode="json")
                self._write(payload)
            return node
        return None

    def move_node(
        self,
        tenant_id: str,
        project_id: str,
        node_id: str,
        move: TreeMoveRequest,
    ) -> TreeNode | None:
        payload = self._load()
        tenant_bucket = payload.setdefault(tenant_id, {})
        project_bucket = tenant_bucket.setdefault(project_id, [])
        node_map = {item.get("node_id"): TreeNode.model_validate(item) for item in project_bucket}
        node = node_map.get(node_id)
        if not node:
            return None
        new_parent_id = move.new_parent_id
        if new_parent_id == node_id:
            raise ValueError("cannot move node into itself")
        if new_parent_id and new_parent_id not in node_map:
            raise ValueError("parent_id not found")
        if new_parent_id and self._creates_cycle(node_id, new_parent_id, node_map):
            raise ValueError("cannot move node into its descendant")

        update_data = {
            "parent_id": new_parent_id,
            "updated_at": utc_now(),
        }
        if move.new_sort_order is not None:
            update_data["sort_order"] = move.new_sort_order
        node = node.model_copy(update=update_data)
        for index, item in enumerate(project_bucket):
            if item.get("node_id") == node_id:
                project_bucket[index] = node.model_dump(mode="json")
                break
        self._write(payload)
        return node

    def delete_node(self, tenant_id: str, project_id: str, node_id: str) -> int:
        payload = self._load()
        tenant_bucket = payload.get(tenant_id, {})
        project_bucket = tenant_bucket.get(project_id, [])
        node_map = {item.get("node_id"): TreeNode.model_validate(item) for item in project_bucket}
        if node_id not in node_map:
            return 0
        to_delete = self._collect_subtree_ids(node_id, node_map)
        remaining = [item for item in project_bucket if item.get("node_id") not in to_delete]
        tenant_bucket[project_id] = remaining
        if tenant_id in payload:
            payload[tenant_id] = tenant_bucket
        self._write(payload)
        return len(to_delete)

    def _collect_subtree_ids(self, root_id: str, node_map: dict[str, TreeNode]) -> set[str]:
        to_visit = [root_id]
        collected: set[str] = set()
        children_by_parent: dict[str | None, list[str]] = {}
        for node in node_map.values():
            children_by_parent.setdefault(node.parent_id, []).append(node.node_id)
        while to_visit:
            current = to_visit.pop()
            if current in collected:
                continue
            collected.add(current)
            to_visit.extend(children_by_parent.get(current, []))
        return collected

    def _creates_cycle(
        self, node_id: str, new_parent_id: str, node_map: dict[str, TreeNode]
    ) -> bool:
        current = new_parent_id
        while current:
            if current == node_id:
                return True
            current = node_map[current].parent_id
        return False

    def _node_exists(self, project_bucket: list[dict[str, Any]], node_id: str) -> bool:
        return any(item.get("node_id") == node_id for item in project_bucket)

    def _load(self) -> dict[str, Any]:
        if not self._path.exists():
            return {}
        with self._path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _write(self, payload: dict[str, Any]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._file_lock():
            temp_path = self._path.with_suffix(".tmp")
            with temp_path.open("w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2)
                handle.write("\n")
            temp_path.replace(self._path)

    def _file_lock(self) -> FileLock:
        return FileLock(self._lock_path)


class FileLock:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._handle: Any = None

    def __enter__(self) -> FileLock:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self._path.open("w", encoding="utf-8")
        self._lock()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._unlock()
        if self._handle:
            self._handle.close()
            self._handle = None

    def _lock(self) -> None:
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(self._handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(self._handle.fileno(), fcntl.LOCK_EX)

    def _unlock(self) -> None:
        if not self._handle:
            return
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(self._handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(self._handle.fileno(), fcntl.LOCK_UN)
