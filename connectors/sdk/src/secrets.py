from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[3]
SECURITY_ROOT = REPO_ROOT / "packages" / "security" / "src"
if str(SECURITY_ROOT) not in sys.path:
    sys.path.insert(0, str(SECURITY_ROOT))

from security.secrets import resolve_secret as _resolve_secret

__all__ = ["resolve_secret"]


def resolve_secret(value: Optional[str]) -> Optional[str]:
    return _resolve_secret(value)
