from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class WorkflowState:
    run_id: str
    status: str
    last_checkpoint: str
    payload: dict[str, Any]


class OrchestrationStateStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(json.dumps({}))

    def load(self) -> dict[str, WorkflowState]:
        raw = json.loads(self.path.read_text())
        return {
            run_id: WorkflowState(
                run_id=run_id,
                status=data["status"],
                last_checkpoint=data["last_checkpoint"],
                payload=data.get("payload", {}),
            )
            for run_id, data in raw.items()
        }

    def save(self, states: dict[str, WorkflowState]) -> None:
        payload = {
            run_id: {
                "status": state.status,
                "last_checkpoint": state.last_checkpoint,
                "payload": state.payload,
            }
            for run_id, state in states.items()
        }
        self.path.write_text(json.dumps(payload, indent=2))
