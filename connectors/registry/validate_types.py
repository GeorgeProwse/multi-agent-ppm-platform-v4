#!/usr/bin/env python3
"""Validate that frontend TypeScript types stay in sync with connectors.json.

Checks ConnectorCategory and ConnectorStatus union types against the values
actually present in the generated registry.  Run after regenerating
connectors.json to catch drift early.

Usage:
    python connectors/registry/validate_types.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "connectors" / "registry" / "connectors.json"
TYPES_PATH = (
    REPO_ROOT
    / "apps"
    / "web"
    / "frontend"
    / "src"
    / "store"
    / "connectors"
    / "types.ts"
)


def _extract_union(ts_source: str, type_name: str) -> set[str]:
    """Extract string literal members from a TypeScript union type."""
    pattern = rf"export type {type_name}\s*=\s*([\s\S]*?);"
    match = re.search(pattern, ts_source)
    if not match:
        return set()
    return set(re.findall(r"'([^']+)'", match.group(1)))


def main() -> int:
    registry = json.loads(REGISTRY_PATH.read_text())
    ts_source = TYPES_PATH.read_text()

    registry_categories = {e["category"] for e in registry if e.get("category")}
    registry_statuses = {e["status"] for e in registry if e.get("status")}

    ts_categories = _extract_union(ts_source, "ConnectorCategory")
    ts_statuses = _extract_union(ts_source, "ConnectorStatus")

    errors: list[str] = []

    missing_categories = registry_categories - ts_categories
    if missing_categories:
        errors.append(
            f"ConnectorCategory missing values from registry: {sorted(missing_categories)}"
        )

    missing_statuses = registry_statuses - ts_statuses
    if missing_statuses:
        errors.append(
            f"ConnectorStatus missing values from registry: {sorted(missing_statuses)}"
        )

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        print(
            "\nUpdate apps/web/frontend/src/store/connectors/types.ts to match "
            "connectors/registry/connectors.json.",
            file=sys.stderr,
        )
        return 1

    print("TypeScript types are in sync with connectors.json.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
