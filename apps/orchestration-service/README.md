# Orchestration Service

Central multi-agent coordinator used by the API gateway. The orchestrator loads agent
implementations, resumes workflow state, and exposes routing through the API.

## Current state

- Orchestrator is implemented as a Python module (`apps/orchestration-service/src/orchestrator.py`).
- Workflow state persistence is stored in `apps/orchestration-service/storage/orchestration-state.json`.
- It is invoked by the API gateway at startup; there is no standalone HTTP server yet.

## Quickstart

Run the API gateway, which bootstraps the orchestrator:

```bash
make run-api
```

## How to verify

```bash
curl http://localhost:8000/api/v1/status
```

Expected response includes:

```json
{"status":"healthy","orchestrator_initialized":true,"agents_loaded":25}
```

## Key files

- `apps/orchestration-service/src/orchestrator.py`: agent lifecycle manager.
- `apps/orchestration-service/src/persistence.py`: workflow state persistence.
- `agents/**/src/*.py`: agent implementations loaded by the orchestrator.
- `apps/orchestration-service/policies/bundles/default-policy-bundle.yaml`: default policy bundle path.
