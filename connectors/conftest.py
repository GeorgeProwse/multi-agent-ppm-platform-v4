"""
Shared pytest configuration for all connector tests.

Bootstraps sys.path with the package source directories that connectors
transitively depend on (common, feature-flags, observability, security, etc.)
so connector test files don't need individual path setup.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

_PACKAGE_PATHS = [
    REPO_ROOT / "vendor" / "stubs",
    REPO_ROOT / "vendor",
    REPO_ROOT,
    REPO_ROOT / "connectors" / "sdk" / "src",
    REPO_ROOT / "packages" / "common" / "src",
    REPO_ROOT / "packages" / "feature-flags" / "src",
    REPO_ROOT / "packages" / "observability" / "src",
    REPO_ROOT / "packages" / "security" / "src",
]

for path in _PACKAGE_PATHS:
    p = str(path)
    if p not in sys.path:
        sys.path.insert(0, p)
