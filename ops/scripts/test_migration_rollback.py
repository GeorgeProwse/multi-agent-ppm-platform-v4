"""Validate that all Alembic migrations have working downgrade() functions.

Imports each migration module and verifies:
1. The downgrade() function exists
2. The downgrade() function body is not a bare pass/raise NotImplementedError

This is a static analysis check -- it does not execute migrations against a
real database. For full rollback testing, use a dedicated test database.

Usage:
    python ops/scripts/test_migration_rollback.py
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VERSIONS_DIR = REPO_ROOT / "data" / "migrations" / "versions"


def check_downgrade(migration_path: Path) -> tuple[bool, str]:
    """Check if a migration has a non-trivial downgrade() function."""
    try:
        source = migration_path.read_text()
        tree = ast.parse(source, filename=str(migration_path))
    except SyntaxError as exc:
        return False, f"syntax error: {exc}"

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "downgrade":
            # Check if body is just `pass`
            if len(node.body) == 1:
                stmt = node.body[0]
                if isinstance(stmt, ast.Pass):
                    return False, "downgrade() is a bare pass"
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                    if isinstance(stmt.value.value, str):
                        return False, "downgrade() is only a docstring"
                if isinstance(stmt, ast.Raise):
                    return False, "downgrade() raises unconditionally"
            return True, "OK"

    return False, "no downgrade() function found"


def main() -> int:
    if not VERSIONS_DIR.exists():
        print(f"ERROR: {VERSIONS_DIR} not found")
        return 1

    migration_files = sorted(VERSIONS_DIR.glob("*.py"))
    if not migration_files:
        print("No migration files found.")
        return 0

    print(f"Checking {len(migration_files)} migration(s) for rollback compatibility...\n")

    failures: list[str] = []
    for path in migration_files:
        ok, reason = check_downgrade(path)
        status = "PASS" if ok else "FAIL"
        print(f"  {status}  {path.name}: {reason}")
        if not ok:
            failures.append(path.name)

    print()
    if failures:
        print(f"{len(failures)} migration(s) lack rollback support: {', '.join(failures)}")
        return 1

    print(f"All {len(migration_files)} migration(s) have rollback-capable downgrade().")
    return 0


if __name__ == "__main__":
    sys.exit(main())
