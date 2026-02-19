# Frontend SPA Migration Map

## State and routing baseline

- Primary console is `apps/web/frontend` mounted under `/app`.
- Global state uses Zustand with:
  - `session` (auth + user)
  - `tenantContext` (active tenant id/name)
  - feature flags and UI state
- Route guards enforce:
  - `RequireAuth` for all application routes
  - `RequireTenantContext` for tenant-scoped pages
  - `RequireAdminRole` for `/admin/*`

## Legacy route compatibility

Legacy UI pages in `apps/web/static` are no longer served by runtime compatibility switches.

Legacy endpoints now always redirect to SPA routes.

## Migration completion status

- Migration is finalized and legacy UI is retired.
- `/v1/ui/migration-map` now publishes `migration_status.legacy_ui_retired: true` as the stable completion signal for API consumers.
- Compatibility remains redirect-only for listed legacy routes.

## Route migration table

| Legacy route | SPA route | Compatibility note |
| --- | --- | --- |
| `/v1/approvals` | `/app/approvals` | Approval UI moved into SPA workflows module. |
| `/v1/workflow-monitoring` | `/app/workflows/monitoring` | Monitoring route remains realtime-capable in SPA. |
| `/v1/document-search` | `/app/knowledge/documents` | Knowledge docs search consolidated under SPA knowledge. |
| `/v1/lessons-learned` | `/app/knowledge/lessons` | Lessons moved into SPA knowledge navigation. |
| `/v1/audit-log` | `/app/admin/audit` | Admin-only route now protected by admin role guard. |

## Phased production rollout plan (`/workspace` → `/app`)

To avoid a single cutover, migration executes in two controlled phases.

### Phase A: redirect-only compatibility + monitoring

- Keep `GET /v1/workspace` active as a compatibility route and always return a redirect to `/app`.
- Instrument and monitor:
  - hits to `/workspace`
  - redirect success rate
  - post-login landing route success
- Track errors and volume until `/workspace` traffic is consistently near-zero.

### Phase B: retire legacy static/compatibility code

- After Phase A traffic thresholds are met, remove legacy static assets and remaining legacy code paths tied to the old workspace shell.
- Keep API compatibility where required (`/v1/api/*`) and preserve SPA routes under `/app/*`.

### Communication and deprecation timeline

- Publish a deprecation notice for `/workspace` compatibility behavior to users and integrators.
- Include timeline checkpoints:
  - announcement date
  - reminder window(s)
  - final retirement date for compatibility route behavior
- Link migration mapping (`/v1/ui/migration-map`) and supported `/app/*` equivalents in all communications.

### Rollback plan

- If critical client breakage appears after Phase B changes, temporarily re-enable a redirect-only `/workspace` compatibility route.
- Do **not** restore the full legacy workspace HTML shell; rollback scope is limited to compatibility redirects while client fixes are coordinated.

## Realtime integration baseline

- Frontend subscribes to realtime channels via websocket (`/ws/events`) using tenant + user context.
- Channels consumed:
  - `workflow_status`
  - `approval_update`
  - `notification`
- Realtime events are normalized in `useRealtimeStore` and consumed by workflow, approvals, and notification views.

## E2E journeys covered

Critical journey tests assert route accessibility and guard behavior for:

- login route
- dashboard/home
- approvals
- prompt manager/config pages
- connector marketplace/status path
