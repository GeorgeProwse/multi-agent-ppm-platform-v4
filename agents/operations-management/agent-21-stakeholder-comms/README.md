# Agent 21: Stakeholder Comms Specification

## Purpose

Define the responsibilities, workflows, and integration points for Agent 21: Stakeholder Comms. This README captures how the agent is expected to behave in the multi-agent orchestration flow.

## What's inside

- `agents/operations-management/agent-21-stakeholder-comms/src`: Implementation source for this component.
- `agents/operations-management/agent-21-stakeholder-comms/tests`: Test suites and fixtures.
- `agents/operations-management/agent-21-stakeholder-comms/Dockerfile`: Container build recipe for local or CI use.

## How it's used

Referenced by the agent runtime and orchestration docs when routing requests, and discovered by `tools/agent_runner` during local execution.

## How to run / develop / test

Run the agent locally with the shared runner:

```bash
python -m tools.agent_runner run-agent --name agent-21-stakeholder-comms --dry-run
```

Run unit tests (if present):

```bash
pytest agents/operations-management/agent-21-stakeholder-comms/tests
```

## Configuration

Agent runtime configuration is centralized in `.env` (see `.env.example`) and shared agent settings such as `MAX_AGENT_CONCURRENCY` and `AGENT_TIMEOUT_SECONDS`. Check the agent implementation under `src/` for any additional required environment variables.

### OAuth scopes (Microsoft Graph)

Ensure the Azure app registration includes the following scopes (delegated or application, depending on your deployment):

- `Mail.Send` (Exchange/Outlook email)
- `Calendars.ReadWrite` (meeting scheduling, invites, availability)
- `OnlineMeetings.ReadWrite` (Teams meeting links)
- `Chat.ReadWrite` or `ChannelMessage.Send` (Teams messaging)
- `User.Read` (basic profile resolution)

### Required environment variables

Communication channels and integrations:

- `EXCHANGE_TOKEN` or `EXCHANGE_TOKEN_SECRET_NAME` (Microsoft Graph token; optional Azure Key Vault secret name)
- `TEAMS_TOKEN` or `TEAMS_TOKEN_SECRET_NAME` (Teams Graph token; optional Azure Key Vault secret name)
- `SLACK_BOT_TOKEN` or `SLACK_BOT_TOKEN_SECRET_NAME` (Slack bot token; optional Azure Key Vault secret name)
- `COMMUNICATIONS_KEYVAULT_URL` (Azure Key Vault URL when using secret names)
- `GRAPH_BASE_URL` (optional, defaults to `https://graph.microsoft.com/v1.0`)

Email fallbacks:

- `AZURE_COMMUNICATION_SERVICES_CONNECTION_STRING` (ACS Email connection string)
- `SENDGRID_API_KEY` and `SENDGRID_FROM_EMAIL` (SendGrid fallback)

AI + analytics:

- `AZURE_TEXT_ANALYTICS_ENDPOINT` and `AZURE_TEXT_ANALYTICS_KEY` (sentiment analysis)
- `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_API_VERSION`
- `AZURE_ML_ENDPOINT` and `AZURE_ML_API_KEY` (engagement scoring)

Workflow automation + audit logging:

- `LOGIC_APPS_TRIGGER_URL` or `POWER_AUTOMATE_TRIGGER_URL` (workflow triggers)
- `SERVICE_BUS_CONNECTION_STRING` plus `SERVICE_BUS_TOPIC` or `SERVICE_BUS_QUEUE`

Data storage:

- `STAKEHOLDER_COMMS_DB_URL` (e.g., `postgresql+psycopg://user:pass@host/db`)

CRM sync (Salesforce connector):

- `SALESFORCE_INSTANCE_URL`, `SALESFORCE_CLIENT_ID`, `SALESFORCE_CLIENT_SECRET`, `SALESFORCE_REFRESH_TOKEN`
- `SALESFORCE_TOKEN_URL` (from connector manifest)
- Optional: `SALESFORCE_CONTACT_ENDPOINT`, `SALESFORCE_CONTACT_QUERY`

### Local run + deploy

Local development:

```bash
python -m tools.agent_runner run-agent --name agent-21-stakeholder-comms --dry-run
```

Docker build and run:

```bash
docker build -t stakeholder-comms-agent agents/operations-management/agent-21-stakeholder-comms
docker run --env-file .env stakeholder-comms-agent
```

## Troubleshooting

- `run-agent` fails with missing entrypoint: ensure a Python module exists under `src/`.
- Runtime errors about missing secrets: populate the required env vars in `.env`.
- Docker execution fails: verify Docker is running and the agent has a `Dockerfile`.
