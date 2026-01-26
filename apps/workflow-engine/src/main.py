from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from audit import emit_audit_event
from storage import WorkflowStore

logger = logging.getLogger("workflow-engine")
logging.basicConfig(level=logging.INFO)

WORKFLOW_ROOT = Path(__file__).resolve().parents[1]
DEFINITIONS_DIR = WORKFLOW_ROOT / "workflows" / "definitions"
DB_PATH = Path(os.getenv("WORKFLOW_DB_PATH", "apps/workflow-engine/storage/workflows.db"))

app = FastAPI(title="Workflow Engine", version="0.1.0")
store = WorkflowStore(DB_PATH)


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "workflow-engine"


class WorkflowStartRequest(BaseModel):
    workflow_id: str
    tenant_id: str
    classification: str
    payload: dict[str, Any]
    actor: dict[str, Any]


class WorkflowRunResponse(BaseModel):
    run_id: str
    workflow_id: str
    tenant_id: str
    status: str
    created_at: str
    updated_at: str


class WorkflowUpdateRequest(BaseModel):
    status: str


def _load_definition(workflow_id: str) -> dict[str, Any]:
    path = DEFINITIONS_DIR / f"{workflow_id}.workflow.yaml"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Workflow definition not found")
    return yaml.safe_load(path.read_text())


@app.get("/healthz", response_model=HealthResponse)
async def healthz() -> HealthResponse:
    return HealthResponse()


@app.post("/workflows/start", response_model=WorkflowRunResponse)
async def start_workflow(request: WorkflowStartRequest) -> WorkflowRunResponse:
    definition = _load_definition(request.workflow_id)
    run_id = str(uuid4())
    instance = store.create(run_id, request.workflow_id, request.tenant_id, request.payload)

    emit_audit_event(
        tenant_id=request.tenant_id,
        actor=request.actor,
        action="workflow.started",
        resource={"id": run_id, "type": "workflow", "definition": definition.get("name")},
        classification=request.classification,
    )

    logger.info("workflow_started", extra={"run_id": run_id, "workflow_id": request.workflow_id})
    return WorkflowRunResponse(
        run_id=instance.run_id,
        workflow_id=instance.workflow_id,
        tenant_id=instance.tenant_id,
        status=instance.status,
        created_at=instance.created_at,
        updated_at=instance.updated_at,
    )


@app.get("/workflows/{run_id}", response_model=WorkflowRunResponse)
async def get_workflow(run_id: str) -> WorkflowRunResponse:
    instance = store.get(run_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return WorkflowRunResponse(
        run_id=instance.run_id,
        workflow_id=instance.workflow_id,
        tenant_id=instance.tenant_id,
        status=instance.status,
        created_at=instance.created_at,
        updated_at=instance.updated_at,
    )


@app.post("/workflows/{run_id}/status", response_model=WorkflowRunResponse)
async def update_workflow(run_id: str, request: WorkflowUpdateRequest) -> WorkflowRunResponse:
    instance = store.update_status(run_id, request.status)
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow not found")
    emit_audit_event(
        tenant_id=instance.tenant_id,
        actor={"id": "workflow-engine", "type": "system", "roles": ["integration_service"]},
        action="workflow.updated",
        resource={"id": run_id, "type": "workflow", "status": request.status},
        classification="internal",
    )
    return WorkflowRunResponse(
        run_id=instance.run_id,
        workflow_id=instance.workflow_id,
        tenant_id=instance.tenant_id,
        status=instance.status,
        created_at=instance.created_at,
        updated_at=instance.updated_at,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=False)
