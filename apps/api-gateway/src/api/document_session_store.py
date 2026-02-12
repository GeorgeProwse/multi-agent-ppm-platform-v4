from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class DocumentSessionStore:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._initialize()

    def _initialize(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS document_sessions (
                session_id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                status TEXT NOT NULL,
                started_by TEXT NOT NULL,
                started_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                collaborators_json TEXT NOT NULL,
                content TEXT NOT NULL,
                version INTEGER NOT NULL
            )
            """
        )
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS document_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL,
                version INTEGER NOT NULL,
                content TEXT NOT NULL,
                persisted_at TEXT NOT NULL,
                persisted_by TEXT NOT NULL,
                summary TEXT,
                metadata_json TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def create_session(self, payload: dict[str, Any]) -> None:
        self._conn.execute(
            """
            INSERT INTO document_sessions (
                session_id, document_id, tenant_id, status, started_by, started_at,
                updated_at, collaborators_json, content, version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["session_id"],
                payload["document_id"],
                payload["tenant_id"],
                payload["status"],
                payload["started_by"],
                payload["started_at"],
                payload["updated_at"],
                json.dumps(payload.get("collaborators", [])),
                payload.get("content", ""),
                payload.get("version", 1),
            ),
        )
        self._conn.commit()

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT * FROM document_sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        if row is None:
            return None
        return {
            "session_id": row["session_id"],
            "document_id": row["document_id"],
            "tenant_id": row["tenant_id"],
            "status": row["status"],
            "started_by": row["started_by"],
            "started_at": row["started_at"],
            "updated_at": row["updated_at"],
            "collaborators": json.loads(row["collaborators_json"]),
            "content": row["content"],
            "version": row["version"],
        }

    def update_session(self, session_id: str, **changes: Any) -> dict[str, Any] | None:
        existing = self.get_session(session_id)
        if existing is None:
            return None
        merged = {**existing, **changes}
        self._conn.execute(
            """
            UPDATE document_sessions
            SET document_id = ?, tenant_id = ?, status = ?, started_by = ?, started_at = ?,
                updated_at = ?, collaborators_json = ?, content = ?, version = ?
            WHERE session_id = ?
            """,
            (
                merged["document_id"],
                merged["tenant_id"],
                merged["status"],
                merged["started_by"],
                merged["started_at"],
                merged["updated_at"],
                json.dumps(merged["collaborators"]),
                merged["content"],
                merged["version"],
                session_id,
            ),
        )
        self._conn.commit()
        return merged

    def record_version(
        self,
        document_id: str,
        version: int,
        content: str,
        persisted_at: str,
        persisted_by: str,
        *,
        summary: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self._conn.execute(
            """
            INSERT INTO document_versions (
                document_id, version, content, persisted_at, persisted_by, summary, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                document_id,
                version,
                content,
                persisted_at,
                persisted_by,
                summary,
                json.dumps(metadata or {}),
            ),
        )
        self._conn.commit()
