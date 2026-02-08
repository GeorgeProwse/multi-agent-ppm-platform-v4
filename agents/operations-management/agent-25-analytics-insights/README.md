# Agent 25: Analytics Insights Specification

## Purpose

Provide a central analytics agent that aggregates platform telemetry, computes KPIs, runs predictive
analytics, and publishes recommendations for downstream agents and dashboards.

## What's inside

- `agents/operations-management/agent-25-analytics-insights/src`: Implementation source for this component.
- `agents/operations-management/agent-25-analytics-insights/tests`: Test suites and fixtures.
- `agents/operations-management/agent-25-analytics-insights/Dockerfile`: Container build recipe for local or CI use.

## How it's used

Referenced by the agent runtime and orchestration docs when routing analytics requests. The agent
subscribes to project, resource, quality, and risk events to maintain near-real-time KPIs and
publishes insights back onto the event bus.

## Key responsibilities

- Aggregate and store analytics events/metrics in Synapse and the analytics datastore.
- Maintain KPI definitions for schedule adherence, cost variance, program performance, resource
  utilisation, defect density, risk exposure, compliance levels, and system health.
- Execute batch and streaming KPI updates using Spark or streaming pipelines.
- Train and serve predictive models for project success, risk escalation, and resource bottlenecks.
- Provide APIs for dashboards and agents to query metrics, trends, and forecasts.
- Enforce data privacy via redaction/anonymisation.

## Intended scope and boundaries

### Scope
- Operate as the *central telemetry aggregator* for platform-wide KPIs, trends, and forecasts.
- Extend the core analytics capabilities implemented by Agent 22 with additional KPI coverage,
  batch/stream processing, and multi-tenant aggregation.
- Provide analytics outputs explicitly intended for downstream agents and dashboards.

### Out of scope
- Building or owning bespoke dashboards (handled by Agent 22 Power BI/embed workflows).
- Acting as the single source of truth for raw operational data (owned by source systems and
  Agent 23 data quality ingestion workflows).
- System health alerting and incident response (owned by Agent 25 System Health Monitoring).

## Inputs and outputs

### Inputs (expected)
- Platform event bus telemetry events (schedule, finance, quality, compliance, system health).
- Metrics payloads from upstream agents (Agent 17 change config, Agent 18 release, Agent 23 data
  synchronisation/quality).
- Optional forecast requests (model type + input payload).

### Outputs (produced)
- KPI time series with trends, thresholds, and recommendations.
- Aggregated analytics payloads stored in Synapse and optionally data lake curated paths.
- Forecast responses (predictions + confidence intervals) for dashboards/agents.

## Decision responsibilities

### Owns decisions
- KPI definition extensions beyond Agent 22 defaults (schedule adherence, cost variance, program
  performance, defect density, compliance, system health).
- KPI trend interpretation and threshold status for downstream automation.
- Forecast execution scheduling and model selection when explicitly requested.

### Informs (but does not decide)
- Portfolio health narratives, anomaly narratives, and self-service analytics outputs (owned by
  Agent 22).
- Operational alerting on system health (owned by Agent 25 System Health Monitoring).

## Must / must-not behaviors

### Must
- Preserve multi-tenant separation in all aggregated outputs.
- Ingest and normalize telemetry events before KPI computation.
- Publish KPI trends and forecasts with timestamped metadata.
- Defer to Agent 22 for narrative generation and dashboards that require Power BI embedding.

### Must not
- Override Agent 22 KPI definitions unless explicitly extending with new metrics.
- Store or emit raw PII without applying redaction/anonymisation rules.
- Trigger automated incident workflows (reserved for system health monitoring).

## Overlap with Agent 22 Analytics Insights

### Overlap areas
- KPI calculation, trend analysis, and forecast tooling.
- Synapse/data lake ingestion utilities and data lineage handling.

### Handoff boundaries (resolve duplication)
- **Agent 22** owns: dashboards, narrative generation, self-service analytics, natural language
  query, portfolio health rollups, data lineage reporting.
- **Agent 25** owns: telemetry aggregation, KPI extensions, batch/stream KPI updates, forecast
  execution on request, and publishing KPI trends to downstream agents.

### Duplication resolution
- Agent 25 inherits Agent 22 baseline implementations and only *extends* KPI coverage; any changes
  to shared storage or lineage tools should be coordinated through Agent 22 to prevent schema drift.

## Functional gaps, inconsistencies, and alignment needs

### Gaps / inconsistencies
- Forecast outputs are returned without confidence intervals in Agent 25, while Agent 22 provides
  confidence interval helpers; align the response format.
- KPI ingestion events overlap with Agent 22 ingestion topics; define a single source of truth for
  event subscriptions (prefer Agent 22 topic registry).
- Agent 25 produces KPI trends without narrative text; ensure dashboards that expect narrative use
  Agent 22 outputs instead.

### Required alignment (prompt/tool/template/connector/UI)
- **Prompt/templates**: Dashboards and narrative templates should explicitly reference Agent 22 for
  narrative summaries, while Agent 25 supplies KPI trend tables and forecast payloads.
- **Tools/connectors**: Synapse, Data Lake, and ML model connectors must share configuration keys
  (`SYNAPSE_*`, `DATA_LAKE_FILE_SYSTEM`) to avoid divergent routing.
- **UI**: Analytics UI should treat Agent 25 outputs as "data feeds" and render via Agent 22
  dashboards; avoid direct embedding from Agent 25.

## Checkpoint: analytics ownership decision

- **Ownership**: Agent 22 remains the user-facing analytics and reporting owner; Agent 25 is the
  backend analytics feed and KPI extension owner.
- **Dependency map entry (ready for execution)**:
  - Upstream dependencies: Agent 17 (change config), Agent 18 (release deployment), Agent 23 (data
    synchronisation/quality), core event bus telemetry.
  - Downstream consumers: Agent 22 (dashboards/narratives), Agent 24 (workflow triggers), Agent 25
    System Health Monitoring (system health KPI ingestion).

## How to run / develop / test

Run the agent locally with the shared runner:

```bash
python -m tools.agent_runner run-agent --name agent-25-analytics-insights --dry-run
```

Run unit tests:

```bash
pytest agents/operations-management/agent-25-analytics-insights/tests
```

## Configuration

Agent runtime configuration is centralized in `.env` (see `.env.example`) and shared agent settings
such as `MAX_AGENT_CONCURRENCY` and `AGENT_TIMEOUT_SECONDS`.

Additional environment variables:

- `SYNAPSE_WORKSPACE_NAME`: Synapse workspace name.
- `SYNAPSE_SQL_POOL_NAME`: Dedicated SQL pool name.
- `DATA_LAKE_FILE_SYSTEM`: ADLS Gen2 file system name.
- `POWERBI_WORKSPACE_ID`: Power BI workspace for embedded reports.
- `POWERBI_CLIENT_ID`: Service principal/client id for Power BI embedding.
