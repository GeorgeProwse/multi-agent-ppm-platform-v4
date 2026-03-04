from __future__ import annotations

import sys
from pathlib import Path

import uvicorn

# Bootstrap monorepo paths. Finds common.bootstrap via repo-root relative path
# so the launcher works even when PYTHONPATH is not pre-configured externally.
_REPO_ROOT = Path(__file__).resolve().parents[2]
_COMMON_SRC = _REPO_ROOT / "packages" / "common" / "src"
if str(_COMMON_SRC) not in sys.path:
    sys.path.insert(0, str(_COMMON_SRC))

from common.bootstrap import ensure_monorepo_paths  # noqa: E402

ensure_monorepo_paths(_REPO_ROOT)

import main as service_main  # noqa: E402

app = service_main.app


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=False)
