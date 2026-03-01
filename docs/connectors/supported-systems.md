# Supported Systems

## Purpose

List connector coverage and maturity based on the current connector registry and packaged connector assets.

## Status definitions

- **production**: Certified connector with automated tests and runtime support.
- **beta**: Functional connector package with runtime support and in-progress certification.

## MCP vs REST support summary

This table summarizes whether a system is covered by REST-only connectors, MCP-only tooling, or a hybrid of the two. Use the MCP coverage docs for operation-level details.

| System | REST connector ID | MCP connector ID | Coverage | Notes |
| --- | --- | --- | --- | --- |
| ADP | `adp` | — | REST-only | REST connectors cover worker/payroll reads. |
| Archer (RSA Archer) | `archer` | — | REST-only | REST reads for risk/GRC entities. |
| Asana | `asana` | — | REST-only | REST reads/writes for projects and tasks. |
| Azure Communication Services | `azure_communication_services` | — | REST-only | REST reads/writes for SMS/email. |
| Azure DevOps | `azure_devops` | — | REST-only | REST reads/writes for projects and work items. |
| Clarity PPM | `clarity` | — | REST-only | REST reads for projects. |
| Confluence | `confluence` | — | REST-only | REST reads/writes for spaces and pages. |
| Google Calendar | `google_calendar` | — | REST-only | REST reads/writes for calendar events. |
| Google Drive | `google_drive` | — | REST-only | REST reads/writes for files and folders. |
| IoT Integrations | `iot` | — | REST-only | REST reads/writes for devices and sensor data. |
| Jira | `jira` | `jira_mcp` | MCP-ready | MCP tools cover project/issue reads and issue writes. |
| LogicGate | `logicgate` | — | REST-only | REST reads/writes for workflows and records. |
| Monday.com | `monday` | — | REST-only | REST reads/writes for boards and items. |
| Microsoft Project Server | `ms_project_server` | — | REST-only | REST reads/writes for projects and tasks. |
| NetSuite | `netsuite` | — | REST-only | REST reads for projects/customers. |
| Azure Notification Hubs | `notification_hubs` | — | REST-only | REST reads/writes for notifications. |
| Oracle ERP Cloud | `oracle` | — | REST-only | REST reads for projects and invoices. |
| Outlook | `outlook` | — | REST-only | REST reads/writes for calendar data. |
| Planview | `planview` | — | REST-only | REST reads for projects. |
| Salesforce | `salesforce` | — | REST-only | REST reads for projects. |
| SAP | `sap` | `sap_mcp` | Hybrid | MCP reads for finance/procurement; REST reads for project sync. |
| SAP SuccessFactors | `sap_successfactors` | — | REST-only | REST reads for users and jobs. |
| ServiceNow GRC | `servicenow` | — | REST-only | REST reads/writes for profiles and risks. |
| SharePoint | `sharepoint` | — | REST-only | REST reads/writes for documents and lists. |
| Slack | `slack` | `slack_mcp` | MCP-ready | MCP tools cover channels/users reads and message writes. |
| Smartsheet | `smartsheet` | — | REST-only | REST reads/writes for sheets and workspaces. |
| Microsoft Teams | `teams` | `teams_mcp` | Hybrid | MCP reads for teams/channels and message writes; REST reads for messages. |
| Twilio | `twilio` | — | REST-only | REST reads/writes for messages. |
| Workday | `workday` | `workday_mcp` | MCP-ready | MCP tools cover worker/position reads; REST handles canonical project/resource sync. |
| Zoom | `zoom` | — | REST-only | REST reads for meetings/webinars. |

## Registry status (runtime-ready)

The authoritative registry list lives in `connectors/registry/connectors.json` and is
generated from connector manifests by `connectors/registry/generate.py`.  Do not edit
the JSON file by hand — regenerate it instead:

```bash
python connectors/registry/generate.py
```

## Verification steps

- View the registry:
  ```bash
  cat connectors/registry/connectors.json
  ```
- Check for connector manifests:
  ```bash
  ls connectors/*/manifest.yaml
  ```

## Implementation status

- **Implemented:** Connector registry now includes every packaged connector.
- **Implemented:** All listed connector packages include manifests and runtime mappings.

## Related docs

- [Connector Overview](overview.md)
- [Connector Certification](certification.md)
- [Connector Data Mapping](data-mapping.md)
- [MCP Coverage Matrix](mcp-coverage-matrix.md)
