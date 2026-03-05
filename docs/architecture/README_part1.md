## System Context

### Purpose

Describe who uses the Multi-Agent PPM Platform, the external systems it integrates with, and the high-level system boundary. This section anchors the logical and physical architecture in the real enterprise ecosystem.

### Architecture-level context

The platform sits between portfolio stakeholders (PMO, delivery leads, finance, resource managers) and enterprise systems of record (PPM, ERP, HR, CRM, collaboration). It provides a unified AI-assisted workflow while preserving those systems as sources of truth. The system context diagram at `docs/architecture/diagrams/c4-context.puml` captures the boundary and integrations.

### System boundary and actors

**Primary actors**
- Portfolio leaders and PMO staff using the web experience.
- Project and program managers collaborating with agents.
- Finance, resource, and compliance stakeholders reviewing gates and approvals.

**External systems**
- PPM/work management: Jira, Azure DevOps, Planview, Clarity PPM, Monday.com, Asana, Smartsheet, Microsoft Project Server.
- ERP/Finance: SAP, Workday, Oracle ERP Cloud, NetSuite.
- HR/Workforce: ADP, SAP SuccessFactors.
- GRC/Risk: RSA Archer, LogicGate, ServiceNow GRC.
- CRM: Salesforce.
- Identity: Azure AD / Okta.
- Collaboration: Slack, Microsoft Teams, Microsoft 365, SharePoint, Confluence, Google Drive, Google Calendar, Outlook, Zoom.
- Communications: Twilio, Azure Communication Services, Azure Notification Hubs.
- IoT: IoT device telemetry integrations.

**System boundary**

The platform orchestrates tasks and maintains a canonical data model. It does **not** replace upstream systems of record; connectors synchronize data bi-directionally based on policy.

### Diagram

```text
PlantUML: docs/architecture/diagrams/c4-context.puml
```

### Usage example

View the system context diagram source:

```bash
sed -n '1,160p' docs/architecture/diagrams/c4-context.puml
```

### How to verify

Confirm the diagram file exists:

```bash
ls docs/architecture/diagrams/c4-context.puml
```

Expected output: the PlantUML file path.

### Implementation status

- **Implemented**: documentation and diagram source.
- **Implemented**: connector registry includes the full set of documented external systems.

### Related docs

- [Logical Architecture](logical-architecture.md)
- [Connector Overview](../connectors/overview.md)
- [Agent Orchestration](agent-orchestration.md)

---

## Logical Architecture

### Purpose

Explain how logical components (agents, orchestration, data services, and connectors) collaborate to deliver the Multi-Agent PPM Platform capabilities.

### Architecture-level context

The logical architecture organizes the platform into three logical planes:

1. **Engagement plane** (API gateway, web prototype) in `apps/`.
2. **Decision plane** (agent orchestration and domain agents) in `agents/`.
3. **Integration and data plane** (connectors, data schemas, lineage) in `connectors/` and `data/`.

These planes are orchestrated through intent routing, task planning, and policy enforcement. Each domain agent owns canonical data entities and publishes events consumed by other agents or analytics workflows.

### Key components

- **Intent Router**: classifies user intent and routes to domain agents.
- **Response Orchestrator**: builds multi-step plans and composes responses.
- **Domain agents (Agents 03–25)**: own specific PPM domain processes (see the [Agent Catalog](../../agents/AGENT_CATALOG.md)).
- **Connector runtime**: translates between canonical schemas and external APIs.
- **Data services**: enforce schema validation, lineage capture, and quality scoring.

### Diagrams

```text
PlantUML: docs/architecture/diagrams/c4-component.puml
```

Supplementary service interaction diagram:

```text
PlantUML: docs/architecture/diagrams/service-topology.puml
```

### Usage example

Inspect the component diagram source:

```bash
sed -n '1,200p' docs/architecture/diagrams/c4-component.puml
```

### How to verify

Check that this document references the agent catalog:

```bash
rg -n "Agent Catalog" docs/architecture/logical-architecture.md
```

Expected output: a reference to `agents/AGENT_CATALOG.md`.

### Implementation status

- **Implemented**: agent runtime scaffolding, API gateway, and orchestration service.
- **Implemented**: workflow engine integration and domain agent registrations in `services/agent-runtime/`.

### Related docs

- [Agent Catalog](../../agents/AGENT_CATALOG.md)
- [Agent Orchestration](agent-orchestration.md)
- [Data Architecture](data-architecture.md)

---

## Physical Architecture

### Purpose

Describe the physical deployment topology for the Multi-Agent PPM Platform, including compute tiers, storage, networking, and environment isolation.

### Architecture-level context

The platform is designed for Azure-friendly deployment with a hub-and-spoke network model, private endpoints for data services, and workload separation by environment (dev, staging, production). The physical topology maps logical services into Azure resources such as AKS, Azure Database for PostgreSQL, Redis, and Azure Service Bus.

### Physical topology (Azure reference)

- **Ingress and edge**: Azure Front Door → Application Gateway / WAF.
- **Compute**: AKS for agent services and API gateway; optional Azure Container Apps for connectors.
- **Data**: Azure Database for PostgreSQL (operational store), Azure Cache for Redis, Azure Blob Storage for documents.
- **Messaging**: Azure Service Bus for event propagation.
- **Secrets**: Azure Key Vault; managed identities for access.

### Diagram

```text
PlantUML: docs/architecture/diagrams/c4-container.puml
```

### Usage example

View the container diagram:

```bash
sed -n '1,200p' docs/architecture/diagrams/c4-container.puml
```

### How to verify

Confirm that the diagram file exists:

```bash
ls docs/architecture/diagrams/c4-container.puml
```

Expected output: the PlantUML file path.

### Implementation status

- **Implemented**: Azure infrastructure deployment scripts in `ops/infra/terraform` and `ops/infra/kubernetes`.

### Related docs

- [Deployment Architecture](deployment-architecture.md)
- [Infrastructure README](../../ops/infra/README.md)
- [Security Architecture](security-architecture.md)

---

## Deployment Architecture

### Purpose

Explain how the platform is deployed across environments, how releases move through the pipeline, and how disaster recovery (DR) is handled.

### Architecture-level context

The deployment architecture maps logical components into Azure environments with clear separation between dev, staging, and production. CI/CD uses GitHub Actions to build containers, run tests, and publish artifacts. Infrastructure-as-code lives under `ops/infra/`.

### Environment matrix

| Environment | Purpose | Data handling | Infra path |
| --- | --- | --- | --- |
| Dev | Engineer experimentation | Synthetic/seed data only | `ops/infra/terraform/envs/dev/` |
| Staging | Pre-prod validation | Sanitized data | `ops/infra/terraform/envs/stage/` |
| Production | Customer workloads | Live data with retention policies | `ops/infra/terraform/envs/prod/` |

### Release flow

1. **Build**: GitHub Actions builds Docker images from `apps/api-gateway/Dockerfile`.
2. **Validate**: unit tests and docs checks (`ops/scripts/check-links.py`, `ops/scripts/check-placeholders.py`).
3. **Deploy**: Terraform provisions infrastructure, then Kubernetes manifests roll out services.

### Diagram

```text
PlantUML: docs/architecture/diagrams/deployment-overview.puml
```

### DR strategy

- Active-passive failover in a paired Azure region with scripted region flips.
- RPO target: 15 minutes; RTO target: 2 hours.
- Backups stored in geo-redundant storage with quarterly restore drills.

### Usage example

Show Terraform environments:

```bash
ls ops/infra/terraform
```

### How to verify

Inspect the Kubernetes deployment manifest:

```bash
sed -n '1,160p' ops/infra/kubernetes/deployment.yaml
```

Expected output: deployment spec with container image and environment variables.

### Implementation status

- **Implemented**: CI pipeline, Dockerfiles, Terraform environment overlays, and DR failover scripts.

### Related docs

- [Container Runtime Identity Policy](container-runtime-identity-policy.md)
- [Physical Architecture](physical-architecture.md)
- [Runbooks](../runbooks/)
- [Infrastructure README](../../ops/infra/README.md)

---

## AI Architecture

### Purpose

Describe the LLM provider abstraction, prompt management, and safety controls implemented in the platform.

### Architecture-level context

AI capabilities are provided through a shared LLM client package and prompt registry. Agent runtimes call the LLM client via the Intent Router and other domain agents. Prompt templates are stored and versioned in the repository for traceability and offline testing.

### Core building blocks

| Capability | Implementation | Notes |
| --- | --- | --- |
| LLM provider abstraction | `packages/llm/src/llm/client.py` | Supports `mock`, `openai`, and `azure-openai` providers. |
| Prompt registry | `agents/runtime/prompts` | YAML prompt definitions validated against `prompt.schema.json`. |
| Redaction rules | `agents/runtime/agents/runtime/prompts/prompt_registry.py` | Redacts sensitive fields from prompt payloads. |
| Intent routing | `agents/core-orchestration/intent-router-agent` | Uses LLM responses to select agent plans. |

### Provider selection and configuration

- **Mock provider (default):** Uses `LLM_MOCK_RESPONSE` or `LLM_MOCK_RESPONSE_PATH` for deterministic outputs.
- **OpenAI provider:** Set `LLM_PROVIDER=openai` and configure `LLM_API_KEY`, `LLM_MODEL`, `LLM_BASE_URL`.
- **Azure OpenAI provider:** Set `LLM_PROVIDER=azure-openai` and configure `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`.

### Prompt management

Prompt YAML files include metadata and redaction rules. The prompt registry loads prompts by agent and purpose and validates them against the schema before use.

- Prompt examples: `agents/runtime/agents/runtime/prompts/examples/*.prompt.yaml`
- Schema validation: `agents/runtime/agents/runtime/prompts/schema/prompt.schema.json`

### Safety and guardrails

- **Redaction:** The prompt registry applies redaction rules to remove sensitive fields before sending data to LLM providers.
- **RBAC enforcement:** The API gateway and policy engine enforce permissions before agent execution.
- **Deterministic testing:** Mock responses enable reproducible runs in CI and local development.

### Verification steps

List available prompt definitions:
```bash
ls agents/runtime/agents/runtime/prompts/examples
```

Inspect the LLM provider selection logic:
```bash
rg -n "LLM_PROVIDER" packages/llm/src/llm/client.py
```

### Implementation status

- **Implemented:** LLM client abstraction, mock/OpenAI/Azure providers, prompt registry with schema validation.
- **Implemented:** Prompt version promotion workflows and registry CLI tooling in `packages/llm`.

### Related docs

- [Agent Orchestration](agent-orchestration.md)
- [LLM Package README](../../packages/llm/README.md)
- [Security Architecture](security-architecture.md)

---

## Agent Orchestration

### Purpose

Describe how the platform routes user intent, plans multi-step workflows, executes tool calls, and composes responses across the 25-agent ecosystem.

### Architecture-level context

Agent orchestration sits between the experience layer (`apps/`) and domain agents (`agents/`). It coordinates intent detection, guardrails, memory/state, connector access, and response composition. The catalog of agent responsibilities is defined in the [Agent Catalog](../../agents/AGENT_CATALOG.md).

### Orchestration flow

1. **Intent routing**: the Intent Router agent classifies the user request and selects candidate agents.
2. **Plan creation**: the Response Orchestration agent builds a multi-step plan and enforces policy guardrails.
3. **Tool execution**: domain agents invoke connectors and data services using canonical schemas.
4. **State management**: results are stored in short-term state (request context) and long-term knowledge (data/lineage).
5. **Response composition**: the Response Orchestration agent synthesizes a final response and cites source data.

### Guardrails and escalation

- **Policy guardrails**: RBAC/ABAC checks are performed before tool execution.
- **Safety gates**: approvals are required for high-impact actions such as budget changes and scope changes.
- **Escalation**: if confidence is low or data is missing, the Approval Workflow agent requests human input.

### Event bus

Agent coordination relies on an event bus abstraction that can publish and subscribe to orchestration topics. Production deployments use Azure Service Bus topics via the shared `packages/event-bus` package, which exposes an async API for publishing messages and listening on subscriptions. The in-memory bus remains available for local development and unit testing.

### Sequence diagram (example flow)

```text
PlantUML: docs/architecture/diagrams/seq-intent-routing.puml
```

### Usage example

View the sequence diagram source:

```bash
sed -n '1,200p' docs/architecture/diagrams/seq-intent-routing.puml
```

### How to verify

Confirm the orchestration document references the agent catalog:

```bash
rg -n "Agent Catalog" docs/architecture/agent-orchestration.md
```

Expected output: a link to `agents/AGENT_CATALOG.md`.

### Implementation status

- **Implemented**: orchestration service manages agent lifecycle, dependency checks, policy enforcement, and Azure Service Bus-backed event distribution.

### Related docs

- [Agent Catalog](../../agents/AGENT_CATALOG.md)
- [Security Architecture](security-architecture.md)
- [Connector Overview](../connectors/overview.md)

---

## Agent Runtime

### Purpose

Define the AgentRun lifecycle, orchestrator state transitions, and transparency surfaces that expose progress and auditability to product interfaces and operators. This section complements [Agent Orchestration](#agent-orchestration) and the runtime package overview in [`agents/runtime/README.md`](../../agents/runtime/README.md).

### AgentRun lifecycle

Agent runs move through explicit, observable states that the orchestrator and UI can surface. The canonical lifecycle is:

- **queued**: A request has been accepted, persisted, and is waiting for orchestration resources.
- **running**: The orchestrator is actively dispatching work to one or more agents.
- **blocked**: Execution is paused pending input (human approval, missing data, or external dependency resolution).
- **completed**: The run finished successfully and emitted a final response.
- **failed**: The run terminated due to an error, timeout, or policy violation.

State transitions are recorded in the runtime audit log and published on the event bus so downstream services can render progress or trigger follow-up actions.

### Orchestrator interaction model

The orchestrator loop coordinates AgentRun transitions and publishes state changes through runtime hooks.

1. **Queue intake**: The runtime accepts a request, assigns an AgentRun ID, and sets the state to `queued`.
2. **Dispatch**: The orchestrator moves the run to `running`, selects agents per the orchestration plan, and invokes tool execution.
3. **Block handling**: If approvals, data dependencies, or guardrails prevent execution, the orchestrator emits a `blocked` transition and registers the blocking reason.
4. **Resolution**: Once blocking conditions clear, the orchestrator resumes and returns to `running`.
5. **Completion**: The orchestrator records either `completed` or `failed` and emits the final response payload.

Runtime hooks include audit logging, event bus publication, and state store updates so that orchestration transitions remain consistent across the runtime stack.

### Audit and event surfaces

Transparency relies on durable, queryable surfaces:

- **Audit log**: Each transition, tool call, and policy decision is written to the runtime audit facility (`agents/runtime/src/audit.py`) for compliance and troubleshooting.
- **Event bus**: The runtime publishes transition events to the event bus so downstream subscribers can react in near real time.
- **State store**: The state store persists AgentRun metadata, including the latest lifecycle state and blocking reason, for UI queries.

### UI surfaces

Product interfaces should surface AgentRun state and context to users:

- **Progress indicators**: Show queued, running, blocked, completed, and failed states with clear messaging and timestamps.
- **Explanations**: Provide human-readable summaries of why a run is blocked or failed, drawing from audit metadata.
- **Async notifications**: Deliver notifications when a blocked run resumes or completes to avoid requiring continuous polling.

### Runtime secret handling policy

Agent request and task handlers **must not** mutate process-global environment variables (e.g., `os.environ[...] = ...`). Runtime code should pass secrets through explicit inputs such as dependency-injected secret providers, per-agent context objects, or function parameters.

When integrating with legacy APIs that only accept environment variables, project secrets into a tightly scoped subprocess environment and avoid mutating the current process environment.

### Cost aggregation metadata

Agent runtime responses include `metadata.cost_summary` with:

- LLM tokens (`request`, `response`, `total`)
- External API cost totals (`api_cost_total_usd`)
- Cost by connector (`api_cost_by_connector`)

The orchestrator aggregates these values into run-level metrics under `OrchestrationResult.metrics.cost_summary` and persists the same summary in shared orchestration context.

### Related docs

- [Agent Orchestration](agent-orchestration.md)
- [Runtime README](../../agents/runtime/README.md)

---

## Workflow Architecture

### Purpose

Explain how durable workflows are defined, executed, and audited across the platform.

### Architecture-level context

Workflows are the backbone for stage-gate execution, approvals, and multi-step orchestration. The platform uses a dedicated workflow service (`apps/workflow-service`) and the Approval Workflow agent (`agents/core-orchestration/approval-workflow-agent`) to execute workflow instances, persist state in an external database, and emit audit entries to the audit log service. Orchestration services and agents call the workflow service to start, resume, and inspect workflow runs, while worker nodes pull tasks from a shared queue.

### Core components

| Component | Location | Responsibility |
| --- | --- | --- |
| Workflow engine API | `apps/workflow-service/src/main.py` | REST API for workflow lifecycle (start/status/resume). |
| Approval Workflow agent | `agents/core-orchestration/approval-workflow-agent/src/approval_workflow_agent.py` | Orchestrates workflow execution, approval chains, and task routing across worker nodes. |
| Workflow storage | `agents/core-orchestration/approval-workflow-agent/src/workflow_state_store.py` | External database-backed state store for workflow definitions, instances, and tasks. |
| Workflow task queue | `agents/core-orchestration/approval-workflow-agent/src/workflow_task_queue.py` | Queue-backed coordination for distributing workflow tasks to workers. |
| Workflow definitions | `apps/workflow-service/workflows/definitions/*.workflow.yaml` | Declarative workflow definitions. |
| Workflow registry | `apps/workflow-service/workflow_registry.py` | Discovery of workflow definitions. |
| Orchestration service | `apps/orchestration-service/src/main.py` | Calls workflow service and coordinates agent plans. |

### Workflow lifecycle

1. **Start**: Clients POST to `/v1/workflows/start` with a workflow ID and payload.
2. **Persist**: The workflow service stores a `run_id`, `workflow_id`, `tenant_id`, status, and payload in PostgreSQL (or another external database).
3. **Distribute**: Workflow tasks are enqueued to a shared message queue for worker nodes.
4. **Resume**: Orchestration services call `/v1/workflows/resume/{run_id}` or workers resume from persisted state after failures.
5. **Audit**: Workflow changes are emitted to the audit log for retention and compliance.

### Workflow definitions and fields

Workflow definitions live in `apps/workflow-service/workflows/definitions/*.workflow.yaml` and follow the schema below.

| Field | Description |
| --- | --- |
| `apiVersion` | Workflow API version (currently `ppm.workflows/v1`). |
| `kind` | Resource kind (`Workflow`). |
| `metadata.name` | Workflow identifier used by `/v1/workflows/start`. |
| `metadata.version` | Version string for the workflow. |
| `metadata.owner` | Owning service or agent. |
| `metadata.description` | Human-readable description. |
| `steps[].id` | Unique step identifier. |
| `steps[].type` | Step type (`task`, `decision`, `approval`, `notification`). |
| `steps[].next` | Next step ID (null ends the workflow). |
| `steps[].config` | Step-specific config (agent/action or channel/message). |
| `steps[].branches` | Decision branches with conditions and next steps. |
| `steps[].default_next` | Fallback next step for decisions. |
| `steps[].timeout_seconds` | Timeout window for approvals. |

### Available workflows

| Workflow | Purpose | Key steps |
| --- | --- | --- |
| `intake-triage` | Route new intake requests to the appropriate agent and notify owners. | `capture-intake` → `evaluate-risk` → `notify-owner` |
| `Publish Charter` | Draft and approve a project charter before publishing. | `draft_charter` → `approval_gate` → `publish_charter` |

### Failure handling and retries

- Workflows persist state in an external database, allowing the system to resume across nodes after process restarts.
- Retry policies are enforced by orchestration logic and workflow service status transitions.
- Worker failures are handled by marking tasks failed and leaving state in the database for retry or manual intervention.

### Operational guidance

- **State backend**: Set `WORKFLOW_DATABASE_URL` and `WORKFLOW_STATE_BACKEND=db` to enable PostgreSQL persistence.
- **Queue backend**: Set `WORKFLOW_QUEUE_BACKEND=rabbitmq` and `WORKFLOW_QUEUE_URL` to enable task distribution.
- **Tenant enforcement**: The workflow service enforces tenant ownership on reads and resumes.
- **Workflow updates**: Version workflow definitions as new YAML files and update registry usage in orchestration services.

### Verification steps

Inspect workflow definitions:
```bash
ls apps/workflow-service/workflows/definitions
```

Check workflow service routes:
```bash
rg -n "workflows" apps/workflow-service/src/main.py
```

Verify workflow instance storage includes `tenant_id`:
```bash
rg -n "tenant_id" apps/workflow-service/src/workflow_storage.py
```

### Implementation status

- **Implemented:** Workflow engine API, external database-backed storage, queue-driven task distribution, YAML workflow definitions.

### Related docs

- [Agent Orchestration](agent-orchestration.md)
- [Deployment Architecture](deployment-architecture.md)
- [Quickstart Runbook](../runbooks/quickstart.md)

---

## Connector Architecture

### Introduction

The Multi-Agent PPM Platform acts as an orchestration layer over existing enterprise systems such as PPM tools, task trackers, ERPs, HRIS, procurement systems, and collaboration platforms. Integration is therefore a critical pillar of the architecture. This section outlines the guiding principles, architectural patterns, reusable components, and monitoring strategies that underpin the platform's integration capabilities.

### Integration principles

The architecture defines five principles for integration:

**Agents own integrations:** Each agent is responsible for reading from and writing to external systems within its domain. For example, the Financial Management agent integrates with SAP for budgets and actuals, while the Resource and Capacity agent integrates with Workday or SuccessFactors for employee data. This ownership ensures domain expertise resides in the agent and reduces cross-module dependencies.

**Bi-directional synchronization:** Integrations support two-way data flows where appropriate. Changes in the PPM platform are propagated back to systems of record (e.g., updating task status in Jira), and external updates are pulled into the platform. Conflict resolution strategies (e.g., last writer wins, authoritative source) are defined per data type.

**Event-driven updates:** Whenever possible, the platform uses event hooks or webhooks from external systems to receive near real-time updates. Agents publish events when internal data changes. This reduces polling and ensures timely synchronization.

**Eventual consistency:** While real-time updates are ideal, the architecture accepts eventual consistency to balance performance and reliability. Agents reconcile differences via scheduled synchronization jobs and implement idempotent operations.

**Graceful degradation:** Integration failures are inevitable. The system handles API outages, timeouts, and throttling by queuing updates, retrying with exponential backoff, and notifying administrators. Core functionality continues using cached data, with warnings to users when data may be stale.

### API gateway pattern

All external calls pass through an API gateway that centralizes cross-cutting concerns:

**Authentication and authorization:** Validates OAuth tokens or API keys and enforces permissions.

**Rate limiting:** Protects downstream systems from overload by limiting requests per user or tenant.

**Protocol translation:** Converts between GraphQL used internally and REST, SOAP, or OData used by external systems. Also handles JSON ↔ XML conversion when needed.

**Logging and monitoring:** Records request/response metadata and latency for analytics and debugging.

**Circuit breaking and retry:** Detects repeated failures and opens circuits to prevent cascading outages. Implements configurable retry policies.

**Schema validation:** Validates request and response payloads against schemas to catch errors early.

The gateway routes calls to connectors or directly to agents for internal API requests. By consolidating these functions, it reduces duplication and simplifies agent implementations.

### Connector library

To avoid duplicating integration logic, the platform provides a reusable connector library. Each connector is implemented as a microservice (or serverless function) that exposes a consistent API to agents and handles all interactions with a specific external system. Key features include:

**Authentication management:** Supports OAuth 2.0, SAML, Basic Auth, and API tokens. Secrets are stored in a secure vault and rotated automatically.

**Request and response mapping:** Transforms platform objects into the external system's API payloads and vice versa (e.g., mapping a Task to a Jira issue).

**Pagination and throttling:** Handles paging through large result sets and respects API rate limits. Implements backoff strategies.

**Error handling and retries:** Normalizes error responses, retries transient failures, and surfaces meaningful errors to calling agents.

**Schema validation and versioning:** Validates payloads against API schemas and manages version differences to support backward compatibility.

**Bi-directional sync helpers:** Provides utilities to determine whether an update originated from the platform or the external system, preventing update loops. Implements conflict resolution strategies.

### Integration patterns by domain

Each domain agent follows specific integration patterns based on its responsibilities. Examples include:

#### Financial Management agent

**ERP integration (SAP, Oracle, Workday):** Retrieve budgets, actual costs, and forecasts via REST or OData APIs. Push budget adjustments and payment approvals back to ERP. Use scheduled batch jobs for large data extracts and event-based updates for critical changes.

**Multi-currency handling:** Convert currencies using exchange rate feeds. Sync exchange rates daily.

**Period close support:** During month-end close, lock financial periods and require manual approval before posting adjustments.

#### Resource and Capacity agent

**HRIS integration (Workday, SuccessFactors):** Pull employee profiles, skills, availability, and cost rates. Push project allocations and timesheet entries if the HR system supports it. Use delta queries to reduce data volume.

**Calendar and directory integration:** Sync with calendar systems (Outlook, Google Calendar) to create meetings for resource assignments and with directories (Azure AD) to resolve user identities.

#### Schedule and Planning agent

**Task trackers (Jira, Azure DevOps, Monday.com):** Map platform tasks to issues or user stories. Support creation, update, and status sync. Use webhooks for updates from task trackers and periodic reconciliation jobs.

**PM tools (Microsoft Project, Smartsheet):** Import/export schedules via file formats (e.g., `.mpp`) or APIs. Convert Gantt charts into the platform's timeline representation.

#### Vendor and Procurement agent

**Procurement systems (Coupa, Ariba):** Sync purchase requisitions, purchase orders, invoices, and vendor onboarding data. Implement approvals in the platform and propagate decisions to procurement systems.

**Vendor risk services:** Integrate with third-party services to perform vendor risk assessments and compliance checks (e.g., Dun & Bradstreet, LexisNexis).

#### Communications and collaboration

**Messaging platforms (Slack, Microsoft Teams):** Post updates, alerts, and meeting summaries. Support interactive bots that allow users to approve requests or update tasks directly from chat.

**Email and calendar:** Send notifications, meeting invites, and agenda documents. Integrate with Exchange/Outlook and Google Workspace.

These patterns serve as blueprints; each connector encapsulates the specific API calls, data mappings, and scheduling needs.

### Monitoring and metrics

Integration reliability is measured through metrics and dashboards. Key metrics include:

**Sync success rate:** The percentage of successful synchronization operations vs. total attempts. Target: >99%.

**Latency and throughput:** Time taken to complete API calls and number of calls per minute. Monitored to detect slowdowns or bottlenecks.

**Queue backlog:** Number of pending events or messages waiting for processing. High backlog triggers scaling or investigation.

**Error rate and types:** Frequency and classification of errors (e.g., authentication failure, rate limit exceeded). Helps prioritize fixes.

**Data freshness:** Age of data since last successful sync. Alerts when exceeding configured thresholds.

Dashboards in tools such as Grafana or Power BI visualize these metrics. Alerts notify integration teams of anomalies, and logs capture detailed information for troubleshooting.

---

## Data Architecture

### Purpose

Describe how canonical PPM data is stored, validated, synchronized, and audited across the platform.

### Architecture-level context

Data architecture ties together canonical schemas (`data/schemas/`), quality rules (`data/quality/`), lineage artifacts (`data/lineage/`), and the services that store and query the data. It enables agents and connectors to share a consistent view of portfolios, programs, projects, and work items.

### Storage layers

- **Operational store**: PostgreSQL for canonical entities.
- **Cache**: Redis for fast reads of frequently accessed data.
- **Document storage**: Blob storage for charters, contracts, and evidence files.
- **Event stream**: Service Bus for domain events and sync notifications.

### Persistence responsibilities

The platform exposes multiple storage backends so services can pick the store that matches the data shape and access pattern. The matrix below summarizes how current services use each backend and where to look in the codebase for implementation details.

| Backend | Primary responsibility | Current usage in services |
| --- | --- | --- |
| PostgreSQL | Canonical, relational PPM entities that need schema validation, joins, and strong consistency. | Data service persists schema registry and canonical entities via its SQL store; orchestration state is configured to use Postgres for durability in production. |
| Cosmos DB | Flexible document storage for semi-structured records and large JSON payloads that benefit from partitioning by tenant or document type. | Integration persistence provides a Cosmos-backed document store (`CosmosDocumentStore`) that can be wired into services needing document-style storage. |
| Redis | Low-latency cache and transient state to avoid repeated queries against operational stores. | Cache provider in integration persistence supports Redis for shared caching and can be paired with cache-aside workflows. |

### Data flow patterns

- **Connector sync** updates canonical records and emits lineage.
- **Agent writes** validate against schemas and publish domain events.
- **Analytics pipeline** consumes events for reporting via the analytics service and KPI scheduler.

### Diagram

```text
PlantUML: docs/architecture/diagrams/data-lineage.puml
```

### Usage example

Inspect the canonical project schema:

```bash
sed -n '1,80p' data/schemas/project.schema.json
```

### How to verify

Confirm lineage artifacts are present:

```bash
ls data/lineage
```

Expected output: `example-lineage.json` and `README.md`.

### Implementation status

- **Implemented**: canonical schemas, lineage artifacts, quality rules, analytics service, and data-lineage service.
- **In progress**: expanded automated lineage generation across all connectors and analytics warehouse exports.

### Related docs

- [Data Model](../data/data-model.md)
- [Data Quality](../data/data-quality.md)
- [Data Lineage](../data/lineage.md)

---

## Data Model

### Purpose

Define canonical propagation rules, conflict handling, and scenario guidance beyond the entity list documented in the canonical data model reference.

### Canonical entities and ownership

Canonical entities and primary owners are maintained in the [Canonical Data Model](../data/data-model.md). The Data Service (`services/data-service/`) stores and serves canonical entities and schema versions.

### Propagation rules (WBS → Schedule → Risk/Budget)

- **Canonical ownership first:** The owning agent or service is the source of truth for its entity; downstream systems consume canonical records rather than rewriting them.
- **Directional propagation:** Work breakdown structure (WBS) changes flow into schedule work items, which then inform downstream risk and budget entities.
- **Mode-aware application:**
  - **merge:** update only fields present in the incoming payload, preserving existing canonical values.
  - **replace:** overwrite the canonical payload with the incoming payload.
  - **enrich:** append non-null fields without overwriting existing canonical values.
- **Field-level constraints:** Only mapped target fields propagate; unmapped fields are ignored to prevent schema drift.
- **Lineage requirements:** Each propagation emits lineage metadata with source system, entity, transformation, and timestamp.

### Conflict handling and audit expectations

- **Conflict policy:**
  - **source_of_truth:** accept updates from the declared owner system.
  - **last_write_wins:** prefer the most recent `updated_at` timestamp.
  - **manual_required:** record conflicts when ownership is ambiguous or an approval gate is configured.
- **Audit trail:** Conflicts and resolution strategies must be logged with source, target, timestamps, and applied policy.
- **Review workflow:** Manual conflicts remain in a review queue until resolved and re-propagated.

### Scenario modeling (baseline vs. variants)

- **Baseline scenario:** The baseline captures the approved plan for schedule, risk, and budget. Canonical entities represent the baseline unless a scenario tag indicates otherwise.
- **Variant scenarios:** Variants inherit from the baseline and override only the changed entities. Variants must retain a pointer to the baseline identifier for traceability.
- **Propagation scope:**
  - Baseline updates cascade to variants only when explicitly rebaselined.
  - Variant updates never overwrite baseline records; they propagate only within the same scenario context.

### Canonical storage context

Canonical entities and schema versions are stored and served by the Data Service. See the [Data Service README](../../services/data-service/README.md) for implementation details.

---

## State Management

### Overview

The platform uses a **unified memory service** to persist and retrieve shared context between agents and orchestrator task executions. This reduces ad-hoc context passing and improves state consistency.

### Memory lifecycle

1. The orchestrator resolves a memory key (typically a correlation or conversation ID).
2. Existing context is loaded from memory before task execution.
3. Each agent task reads merged context and dependency outputs.
4. After task completion, the orchestrator appends history, outputs, and insights, then persists context.
5. Base agents can also save and load per-agent scoped context using `conversation_id:agent_id` keys.

### Retrieval hygiene

- Context is namespaced by memory key to avoid accidental cross-conversation leakage.
- Agent-local entries use conversation and agent identifiers.
- The orchestrator normalizes insights and keeps task output lineage in `agent_outputs`.
- TTL can be configured to evict stale context and avoid context pollution.

### Privacy and data handling

- Store only operationally necessary context.
- Avoid saving raw secrets or PII unless required by policy.
- Use TTL for temporary conversation state to reduce retention duration.
- Prefer sanitized summaries over full payloads for long-term persistence.

### Components

- `services/memory_service/memory_service.py`: in-memory and SQLite memory backend with optional TTL.
- `packages/memory_client.py`: client wrapper used by orchestrator and agents.
- `agents/runtime/src/base_agent.py`: memory helper methods (`save_context`, `load_context`).
- `agents/runtime/src/orchestrator.py`: centralized context persistence during DAG execution.

---

## Vector Store Design

### Overview

The platform supports a shard-aware FAISS-backed vector store implementation for high-volume duplicate detection and semantic retrieval workflows. The implementation centers on `FaissVectorStore` in `packages/vector_store/faiss_store.py` and a higher-level adapter `FaissBackedVectorSearchIndex` used by portfolio agents.

### Architecture

- **Storage primitive**: `FaissVectorStore`.
  - Supports configurable sharding (`num_shards`) to spread vectors across partitions.
  - Uses `IndexIVFFlat` when `faiss` is available; otherwise falls back to a NumPy cosine similarity path.
  - Exposes `add_embeddings`, `search`, `search_many`, `delete`, and `flush`.
- **Agent integration adapter**: `FaissBackedVectorSearchIndex` in `agents/common/integration_services.py`.
  - Preserves the existing `add` and `search` style used by agents.
  - Loads index tuning from `ops/ops/config/vector_store.yaml`.
  - Stores metadata separately and merges metadata into search results.

### Scalability controls

#### Sharding

- Each document ID is deterministically mapped to a shard.
- Search fans out across shards and merges top results.
- Recommended scale-up path:
  1. Increase `num_shards`.
  2. Increase `nlist`.
  3. Tune `nprobe` to balance recall vs. latency.

#### Batching

- `add_embeddings` stages vectors in per-shard queues.
- Flush occurs automatically at `batch_size` and can be forced via `flush()`.
- `search_many` provides multi-query batch execution.

#### Caching

- Internal LRU-style cache stores recent query results with TTL (`cache_ttl_seconds`) and bounded size (`cache_size`).
- The agent adapter also keeps a small query cache (`query_cache_size`) to avoid recomputation of repeated queries.

#### TTL-based retention

- Embeddings can be configured with `embedding_ttl_seconds`.
- Expired vectors are purged during add/search operations.
- Use shorter TTL for high-churn domains and longer TTL for historical benchmarking workloads.

### Operational tuning

Configure index settings in `ops/ops/config/vector_store.yaml`:

- `num_shards`: parallelism and index partitioning.
- `nlist`: coarse cluster count for IVF.
- `nprobe`: cluster probes per query.
- `batch_size`: write throughput vs. index freshness.
- `cache_size` and `cache_ttl_seconds`: query cache behavior.
- `embedding_ttl_seconds`: lifecycle cleanup window.

### Current agent usage

- Demand and Intake agent (`demand-intake-agent`) uses the `demand_intake` index profile.
- Business Case and Investment agent (`business-case-agent`) uses the `business_case` index profile.
