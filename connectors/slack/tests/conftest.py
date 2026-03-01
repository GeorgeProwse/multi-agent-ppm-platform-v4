"""
Pytest configuration for Slack connector tests.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
_PATHS = [
    REPO_ROOT / "vendor" / "stubs",
    REPO_ROOT / "vendor",
    REPO_ROOT,
    REPO_ROOT / "connectors" / "sdk" / "src",
    REPO_ROOT / "connectors" / "slack" / "src",
    REPO_ROOT / "packages" / "common" / "src",
    REPO_ROOT / "packages" / "feature-flags" / "src",
    REPO_ROOT / "packages" / "observability" / "src",
    REPO_ROOT / "packages" / "security" / "src",
]

for path in _PATHS:
    p = str(path)
    if p not in sys.path:
        sys.path.insert(0, p)
