# Data

> This section covers the canonical data layer of the Multi-Agent PPM platform: the entity model that normalises data across all systems, the quality rules that govern ingestion, and the lineage infrastructure that provides end-to-end traceability from external connectors to canonical schemas. Validate internal links with `python ops/scripts/check-links.py`.

## Contents

- [Overview](#overview)
- [Data Model](#data-model)
- [Data Quality](#data-quality)
- [Data Lineage](#data-lineage)

---

## Overview

The platform uses a canonical schema layer to normalise data from multiple systems. All schemas are stored in `data/schemas/` and are referenced by connectors, agents, and services to validate payloads and maintain lineage. The documents in this section describe the entities, quality rules, and lineage mechanisms that underpin agent accuracy and auditability.

Related assets:

- Schema files: `data/schemas/`
- Quality rules: `data/quality/rules.yaml`
- Lineage artifacts: `data/lineage/`
- Related architecture docs: [Data Architecture](../architecture/data-architecture.md)

Validate internal links across all docs:

```bash
python ops/scripts/check-links.py
```

---

## Data Model

### Purpose

Describe the canonical PPM entities, where their schemas live, and how agents and connectors use them.

### Architecture-level context

The platform uses a canonical schema layer to normalize data from multiple systems. Schemas are stored in `data/schemas/` and referenced by connectors, agents, and services to validate payloads and maintain lineage.

### Canonical entities

| Entity | Schema file | Primary owner (agent/service) |
| --- | --- | --- |
| Audit event | `data/schemas/audit-event.schema.json` | Audit Log Service |
| Budget | `data/schemas/budget.schema.json` | Financial Management agent |
| Demand | `data/schemas/demand.schema.json` | Demand Intake agent |
| Document | `data/schemas/document.schema.json` | Knowledge Management agent |
| Issue | `data/schemas/issue.schema.json` | Risk Management agent |
| Portfolio | `data/schemas/portfolio.schema.json` | Portfolio Optimisation agent |
| Program | `data/schemas/program.schema.json` | Program Management agent |
| Project | `data/schemas/project.schema.json` | Scope Definition agent |
| Resource | `data/schemas/resource.schema.json` | Resource Management agent |
| Risk | `data/schemas/risk.schema.json` | Risk Management agent |
| ROI | `data/schemas/roi.schema.json` | Business Case agent |
| Scenario | `data/schemas/scenario.schema.json` | Portfolio Optimisation agent |
| Vendor | `data/schemas/vendor.schema.json` | Vendor Procurement agent |
| Work item | `data/schemas/work-item.schema.json` | Schedule Planning agent |

### Platform schemas (runtime/infrastructure)

| Schema | Schema file | Owner |
| --- | --- | --- |
| Agent configuration | `data/schemas/agent_config.schema.json` | Agent Config Service |
| Agent run | `data/schemas/agent-run.schema.json` | Agent Runtime Service |

### Example payload (Project)

```json
{
  "id": "PROJ-2026-001",
  "name": "ERP Modernization",
  "status": "in_progress",
  "portfolio_id": "PORT-001",
  "program_id": "PROG-2026-01",
  "owner_email": "pm@ppm.georgeprowse91.com",
  "start_date": "2026-01-15",
  "end_date": "2026-12-20",
  "currency": "AUD"
}
```

### Viewing schema files

List all schema files:

```bash
ls data/schemas
```

Inspect the project schema:

```bash
sed -n '1,80p' data/schemas/project.schema.json
```

### Propagation rules and conflict handling

Canonical entities propagate updates between connectors, agents, and downstream consumers using explicit rules stored in the data sync service.

#### Propagation rules

- **Directional propagation:** Updates flow from a declared source system to a target canonical entity.
- **Mode-aware application:**
  - **merge:** Update only fields present in the incoming payload, preserving existing canonical values.
  - **replace:** Overwrite the canonical payload with the incoming payload.
  - **enrich:** Append non-null fields without overwriting existing canonical values.
- **Field-level constraints:** Only mapped target fields are eligible for propagation.
- **Lineage requirements:** Every propagated update emits lineage metadata with source, target, and transformation steps.

#### Conflict handling

- **source_of_truth:** Always accept updates from the declared source system.
- **last_write_wins:** Compare `updated_at` timestamps; apply the newer update and skip stale payloads.
- **manual_required:** Record conflicts for review when updates collide or policy requires human approval.
- **Audit trail:** Conflicts are logged with source, target entity, timestamps, and resolution strategy.

### Implementation status

- **Implemented:** Base schemas in `data/schemas/` and validation in the audit log service.
- **Implemented:** Schema registry APIs with versioning and promotion workflows in the data service.

---

## Data Quality

### Purpose

Define the quality scoring approach for canonical data and provide example rules used during connector sync.

### Architecture-level context

Data quality scoring is executed by the Data Synchronisation agent. Rules are stored in `data/quality/rules.yaml` and applied to incoming data before it is persisted. Scores are captured in lineage artifacts for auditability.

### Quality dimensions

- **Completeness:** Required fields are present.
- **Validity:** Values match expected formats or ranges.
- **Consistency:** Values align with canonical enums and references.
- **Timeliness:** Data freshness meets the sync policy.

### Example rules

```yaml
- id: project-required-fields
  entity: project
  checks:
    - field: project.id
      type: required
```

The full rule set is in `data/quality/rules.yaml`.

View the rules file:

```bash
sed -n '1,120p' data/quality/rules.yaml
```

Confirm the rule file exists:

```bash
ls data/quality/rules.yaml
```

### Implementation status

- **Implemented:** Baseline rules and scoring weights.
- **Implemented:** Automated remediation workflows with API-triggered fixes in the lineage service.

---

## Data Lineage

### Purpose

Explain how lineage is captured for connector syncs and agent transformations, with concrete examples.

### Architecture-level context

Lineage provides end-to-end traceability from external systems into canonical schemas. The connector runtime emits lineage events that are persisted in the `lineage_events` database table for audit, compliance, and analytics.

### Lineage capture approach

- **Trigger:** Every connector sync or agent write.
- **Payload:** Source system, record IDs, transformations, quality score.
- **Storage:** `lineage_events` database table (schema below).

### Lineage storage table

`lineage_events` captures connector sync lineage events with enough metadata to filter by connector or work item.

| Column | Type | Notes |
| --- | --- | --- |
| `lineage_id` | text (PK) | Unique lineage event ID |
| `tenant_id` | text | Tenant scope |
| `connector_id` | text | Connector identifier |
| `work_item_id` | text (nullable) | Populated when the target schema is `work-item` |
| `source_entity` | json | Source entity metadata |
| `target_entity` | json | Target entity metadata |
| `transformations` | json | Ordered list of transformation steps |
| `entity_type` | text (nullable) | Canonical entity type |
| `entity_payload` | json (nullable) | Canonical entity payload |
| `quality` | json (nullable) | Data quality metrics |
| `classification` | text | Classification label |
| `metadata` | json (nullable) | Additional metadata |
| `timestamp` | text | Sync timestamp (ISO 8601) |
| `retention_until` | text | Retention policy cutoff |

### Example lineage artifact

```json
{
  "id": "lin-2026-01-15-001",
  "connector": "jira",
  "source": {"system": "jira", "object": "project"},
  "target": {"schema": "project", "record_id": "PROJ-2026-001"}
}
```

The full example is at `data/lineage/example-lineage.json`.

View the example lineage artifact:

```bash
sed -n '1,160p' data/lineage/example-lineage.json
```

### Example lineage queries

Query lineage by work item ID via the API gateway:

```bash
curl -H "X-Tenant-ID: tenant-a" \
  "http://localhost:8000/v1/lineage?work_item_id=WI-100"
```

Query lineage by connector ID via the API gateway:

```bash
curl -H "X-Tenant-ID: tenant-a" \
  "http://localhost:8000/v1/lineage?connector_id=jira"
```

Query lineage directly from the database:

```sql
SELECT lineage_id, connector_id, work_item_id, timestamp
FROM lineage_events
WHERE connector_id = 'jira'
ORDER BY timestamp DESC;
```

### Implementation status

- **Implemented:** Automated lineage generation, storage in `lineage_events`, and the query API.

### Related docs

- [Connector Overview](../connectors/overview.md)
- [Data Quality](#data-quality)
