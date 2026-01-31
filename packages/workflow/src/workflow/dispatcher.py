from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from workflow.celery_app import celery_app


@dataclass
class WorkflowDispatcher:
    def dispatch_step(
        self,
        run_id: str,
        step_id: str,
        actor: dict[str, Any],
        countdown: int | None = None,
    ) -> None:
        signature = celery_app.signature("workflow.execute_step", args=[run_id, step_id, actor])
        if countdown:
            signature.apply_async(countdown=countdown)
        else:
            signature.apply_async()
