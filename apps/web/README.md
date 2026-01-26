# Production Web Console

Production-grade web console for the Multi-Agent PPM platform. The UI authenticates via the identity-access
service, stores tenant context, and calls the API gateway with tenant-aware headers.

## Quickstart

```bash
cd apps/web
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8501
```

Open the UI at `http://localhost:8501`.

## Features

- Token validation via `identity-access`.
- Tenant-aware calls to `api-gateway`.
- Workflow start action via `workflow-engine`.

## Configuration

Environment variables:

- `API_GATEWAY_URL` (default: `http://localhost:8000`)
- `IDENTITY_ACCESS_URL` (default: `http://localhost:8081`)
- `WORKFLOW_ENGINE_URL` (default: `http://localhost:8082`)

## Key files

- `apps/web/src/main.py`: FastAPI app serving static UI.
- `apps/web/static/`: HTML/CSS/JS assets.
