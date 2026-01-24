# Configuration Files

This directory contains configuration files for the Multi-Agent PPM Platform.

## Structure

```
configs/
├── agents/              # Agent-specific configurations
│   ├── orchestration.yaml
│   ├── portfolio.yaml
│   ├── delivery.yaml
│   ├── governance.yaml
│   ├── operations.yaml
│   └── platform.yaml
├── connectors/          # External integration configurations
│   └── integrations.yaml
└── environments/        # Environment-specific configs
    ├── development.yaml
    ├── staging.yaml
    └── production.yaml
```

## Configuration Files

### Agent Configurations

- **orchestration.yaml**: Intent Router and Response Orchestration agents
- **portfolio.yaml**: Demand Intake, Business Case, Portfolio Strategy, Program Management
- **delivery.yaml**: Project Definition, Lifecycle, Schedule, Resource, Financial, Vendor agents
- **governance.yaml**: Quality, Risk, Compliance, Change Management agents
- **operations.yaml**: Release, Knowledge, Continuous Improvement, Communications agents
- **platform.yaml**: Analytics, Data Sync, Workflow, System Health agents

### Connector Configurations

- **integrations.yaml**: External system integrations (Jira, SAP, Workday, Slack, etc.)

See [Connector Specifications](../docs_markdown/integrations/specs/Connector%20&%20Integration%20Specifications.md) for details.

## Environment Variables

Configuration files support environment variable substitution using `${VAR_NAME}` syntax.

See `.env.example` in the root directory for all available environment variables.

## Usage

Configurations are loaded automatically by the platform based on the `ENVIRONMENT` variable:

```bash
ENVIRONMENT=development  # Loads development.yaml
ENVIRONMENT=production   # Loads production.yaml
```

## Overriding Configurations

You can override configurations using environment variables:

```bash
export AGENT_INTENT_ROUTER_ENABLED=false
export AGENT_MAX_CONCURRENCY=10
```

## Validation

All configuration files are validated against schemas on startup. Invalid configurations will prevent the platform from starting.
