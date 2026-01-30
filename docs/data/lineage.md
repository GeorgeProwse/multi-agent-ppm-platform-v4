# Data Lineage

## Purpose

Explain how lineage is captured for connector syncs and agent transformations, with concrete examples.

## Architecture-level context

Lineage provides end-to-end traceability from external systems into canonical schemas. The connector runtime emits lineage events that are persisted in the `lineage_events` database table for audit, compliance, and analytics processes.

## Lineage capture approach

- **Trigger**: every connector sync or agent write.
- **Payload**: source system, record IDs, transformations, quality score.
- **Storage**: `lineage_events` database table (see schema below).

## Lineage storage table

`lineage_events` captures connector sync lineage events with enough metadata to filter by connector or work item.

| Column | Type | Notes |
| --- | --- | --- |
| `lineage_id` | text (PK) | Unique lineage event ID |
| `tenant_id` | text | Tenant scope |
| `connector_id` | text | Connector identifier |
| `work_item_id` | text (nullable) | Populated when target schema is `work-item` |
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

## Example lineage artifact

```json
{
  "id": "lin-2026-01-15-001",
  "connector": "jira",
  "source": {"system": "jira", "object": "project"},
  "target": {"schema": "project", "record_id": "PROJ-2026-001"}
}
```

Full example: `data/lineage/example-lineage.json`.

## Usage example

View the example lineage artifact:

```bash
sed -n '1,160p' data/lineage/example-lineage.json
```

## How to verify

Confirm the example file exists:

```bash
ls data/lineage/example-lineage.json
```

Expected output: the JSON file path.

## Example lineage queries

Query lineage by work item ID via the API gateway:

```bash
curl -H "X-Tenant-ID: tenant-a" \
  "http://localhost:8000/api/v1/lineage?work_item_id=WI-100"
```

Query lineage by connector ID via the API gateway:

```bash
curl -H "X-Tenant-ID: tenant-a" \
  "http://localhost:8000/api/v1/lineage?connector_id=jira"
```

Query lineage directly from the database:

```sql
SELECT lineage_id, connector_id, work_item_id, timestamp
FROM lineage_events
WHERE connector_id = 'jira'
ORDER BY timestamp DESC;
```

## Implementation status

- **Implemented**: automated lineage generation, storage in `lineage_events`, and query API.

## Related docs

- [Connector Overview](../connectors/overview.md)
- [Data Quality](data-quality.md)
