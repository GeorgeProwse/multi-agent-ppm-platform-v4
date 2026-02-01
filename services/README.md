# Services

## Purpose

Catalog backend services that power data sync, policy enforcement, and telemetry.

## What's inside

- `services/audit-log`: Subdirectory containing audit log assets for this area.
- `services/auth-service`: Subdirectory containing authentication service assets for this area.
- `services/data-sync-service`: Subdirectory containing data sync service assets for this area.
- `services/data-lineage-service`: Subdirectory containing data lineage service assets for this area.
- `services/data-service`: Subdirectory containing data service assets for this area.
- `services/identity-access`: Subdirectory containing identity access assets for this area.
- `services/notification-service`: Subdirectory containing notification service assets for this area.
- `services/agent-runtime`: Subdirectory containing agent runtime assets for this area.
- `services/policy-engine`: Subdirectory containing policy engine assets for this area.
- `services/telemetry-service`: Subdirectory containing telemetry service assets for this area.
- `services/realtime-coedit-service`: Subdirectory containing real-time co-editing assets for this area.

## Service descriptions & endpoints

Each service runs a FastAPI application (default port `8080`) with health checks at `/healthz`.

| Service | Description | Primary endpoints |
| --- | --- | --- |
| Audit Log | Immutable audit trail with retention and WORM storage enforcement. | `POST /v1/audit/events`, `GET /v1/audit/events/{event_id}` |
| Auth Service | Exchanges OAuth2/OIDC tokens and validates JWTs. | `POST /v1/auth/login`, `POST /v1/auth/refresh`, `POST /v1/auth/logout`, `POST /v1/auth/validate` |
| Agent Runtime | Hosts agent registry, orchestration, and connector integration for the platform. | `GET /v1/agents`, `POST /v1/agents/{agent_id}/execute`, `POST /v1/orchestration/run` |
| Data Sync Service | Runs connector sync jobs, tracks status, and manages conflicts. | `POST /v1/sync/run`, `GET /v1/sync/status/{job_id}`, `GET /v1/sync/conflicts` |
| Data Lineage Service | Captures lineage events and quality summaries. | `POST /v1/lineage/events`, `GET /v1/lineage/graph`, `GET /v1/quality/summary` |
| Data Service | Manages schemas and canonical entities. | `POST /v1/schemas`, `GET /v1/schemas`, `POST /v1/entities/{schema_name}` |
| Identity & Access | Validates auth tokens and supports SCIM provisioning. | `POST /v1/auth/validate`, `POST /v1/scim/v2/Users`, `GET /v1/scim/v2/Groups` |
| Notification Service | Sends email/chat/webhook notifications. | `POST /v1/notifications/send` |
| Policy Engine | Evaluates RBAC/ABAC policy decisions. | `POST /v1/policies/evaluate`, `POST /v1/rbac/evaluate`, `POST /v1/abac/evaluate` |
| Telemetry Service | Ingests telemetry payloads for observability. | `POST /v1/telemetry/ingest` |
| Realtime Coedit Service | Manages collaborative document editing sessions. | `POST /v1/sessions`, `GET /v1/sessions/{session_id}`, `GET /v1/ws/documents/{document_id}` |

## How it's used

Services are discovered by `tools/component_runner` and deployed via Helm and Terraform resources under `infra/`.

## How to run / develop / test

List services and run one locally:

```bash
python -m tools.component_runner list --type service
python -m tools.component_runner run --type service --name audit-log --dry-run
```

## Configuration

Services use shared `.env` settings plus service-specific env vars documented in each service README.

## Troubleshooting

- Service not listed: ensure the service folder exists under `services/`.
- Startup errors: confirm database and external service endpoints are reachable.
