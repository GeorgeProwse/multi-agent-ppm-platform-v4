# Event Contracts

This document describes event topics, payload schemas, and versioning rules for inter-agent
communication. Payloads are JSON objects wrapped in a shared envelope with tracing metadata.

## Envelope

All events share the following envelope fields:

| Field | Type | Description |
| --- | --- | --- |
| `event_name` | string | Topic name (e.g. `demand.created`). |
| `event_id` | string | Unique event identifier. |
| `timestamp` | RFC3339 datetime | Event creation time. |
| `tenant_id` | string | Tenant identifier. |
| `payload` | object | Event-specific payload. |
| `correlation_id` | string | Cross-service correlation identifier. |
| `trace_id` | string | OpenTelemetry trace identifier. |

## Domain Events

### demand.created

Payload:

| Field | Type | Description |
| --- | --- | --- |
| `demand_id` | string | Demand record identifier. |
| `source` | string | Intake source (e.g. CRM, portal). |
| `title` | string | Demand title. |
| `submitted_by` | string | Actor who submitted the demand. |
| `submitted_at` | RFC3339 datetime | Submission timestamp. |

### business_case.created

Payload:

| Field | Type | Description |
| --- | --- | --- |
| `business_case_id` | string | Business case identifier. |
| `demand_id` | string | Related demand record. |
| `project_name` | string | Proposed project name. |
| `created_at` | RFC3339 datetime | Creation timestamp. |
| `owner` | string | Business case owner. |

### portfolio.prioritized

Payload:

| Field | Type | Description |
| --- | --- | --- |
| `portfolio_id` | string | Portfolio identifier. |
| `cycle` | string | Planning cycle label. |
| `prioritized_at` | RFC3339 datetime | Prioritization timestamp. |
| `ranked_projects` | array[string] | Ordered list of project IDs. |

### program.created

Payload:

| Field | Type | Description |
| --- | --- | --- |
| `program_id` | string | Program identifier. |
| `name` | string | Program name. |
| `portfolio_id` | string | Associated portfolio. |
| `created_at` | RFC3339 datetime | Creation timestamp. |
| `owner` | string | Program owner. |

### charter.created

Payload:

| Field | Type | Description |
| --- | --- | --- |
| `charter_id` | string | Charter identifier. |
| `project_id` | string | Project identifier. |
| `created_at` | RFC3339 datetime | Creation timestamp. |
| `owner` | string | Charter owner. |

### wbs.created

Payload:

| Field | Type | Description |
| --- | --- | --- |
| `wbs_id` | string | Work breakdown structure identifier. |
| `project_id` | string | Project identifier. |
| `created_at` | RFC3339 datetime | Creation timestamp. |
| `baseline_date` | RFC3339 datetime | Optional baseline date. |

### project.transitioned

Payload:

| Field | Type | Description |
| --- | --- | --- |
| `project_id` | string | Project identifier. |
| `from_stage` | string | Previous lifecycle stage. |
| `to_stage` | string | New lifecycle stage. |
| `transitioned_at` | RFC3339 datetime | Transition time. |
| `actor_id` | string | Actor who transitioned the project. |

### schedule.baseline.locked

Payload:

| Field | Type | Description |
| --- | --- | --- |
| `project_id` | string | Project identifier. |
| `schedule_id` | string | Schedule identifier. |
| `locked_at` | RFC3339 datetime | Baseline lock timestamp. |
| `baseline_version` | string | Baseline version label. |

### schedule.delay

Payload:

| Field | Type | Description |
| --- | --- | --- |
| `project_id` | string | Project identifier. |
| `schedule_id` | string | Schedule identifier. |
| `delay_days` | integer | Number of delayed days. |
| `reason` | string | Delay reason summary. |
| `detected_at` | RFC3339 datetime | Detection timestamp. |

### approval.created

Payload:

| Field | Type | Description |
| --- | --- | --- |
| `approval_id` | string | Approval identifier. |
| `resource_type` | string | Resource type requiring approval. |
| `resource_id` | string | Resource identifier. |
| `stage` | string | Stage gate or approval stage. |
| `created_at` | RFC3339 datetime | Creation timestamp. |

### approval.decision

Payload:

| Field | Type | Description |
| --- | --- | --- |
| `approval_id` | string | Approval identifier. |
| `decision` | string | `approved`, `rejected`, or `deferred`. |
| `decided_at` | RFC3339 datetime | Decision timestamp. |
| `approver_id` | string | Approver identifier. |
| `comments` | string | Optional decision notes. |

### audit.*

Audit events reuse the canonical audit schema from `data/schemas/audit-event.schema.json`.
The event `payload` matches the audit-event schema, and the envelope `event_name` must
start with `audit.` (e.g. `audit.agent.policy`).

## Versioning

- Event payload changes must be backward compatible within a major version.
- Additive fields are allowed without version bumps.
- Breaking changes require a new event name suffix or major version update in payload metadata.
