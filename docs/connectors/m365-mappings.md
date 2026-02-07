# Microsoft 365 workload data mapping

This mapping aligns M365 workloads with required data types and identifies the preferred MCP tool key
(when configured) or the Microsoft Graph REST endpoint to use.

## Legend
- **MCP tool key**: Key looked up in `mcp_tool_map` to resolve an MCP tool name.
- **Graph REST endpoint**: Microsoft Graph path used when MCP tooling is unavailable.

## Workload → data type mapping

| Workload | User list | Last activity | Subscription data | Cost data | Last login |
| --- | --- | --- | --- | --- | --- |
| Exchange/Outlook | MCP: `users.list` / REST: `/users` | MCP: `exchange.last_activity` / REST: `/reports/getEmailActivityUserDetail` | MCP: `subscriptions.list` / REST: `/subscribedSkus` | MCP: `billing.costs` / REST: `/reports/getOffice365ActivationCounts` | MCP: `signins.list` / REST: `/auditLogs/signIns` |
| Teams | MCP: `users.list` / REST: `/users` | MCP: `teams.last_activity` / REST: `/reports/getTeamsUserActivityUserDetail` | MCP: `subscriptions.list` / REST: `/subscribedSkus` | MCP: `billing.costs` / REST: `/reports/getOffice365ActivationCounts` | MCP: `signins.list` / REST: `/auditLogs/signIns` |
| SharePoint | MCP: `users.list` / REST: `/users` | MCP: `sharepoint.last_activity` / REST: `/reports/getSharePointActivityUserDetail` | MCP: `subscriptions.list` / REST: `/subscribedSkus` | MCP: `billing.costs` / REST: `/reports/getOffice365ActivationCounts` | MCP: `signins.list` / REST: `/auditLogs/signIns` |
| Planner | MCP: `users.list` / REST: `/users` | MCP: `planner.last_activity` / REST: `/reports/getOffice365ActiveUserDetail` | MCP: `subscriptions.list` / REST: `/subscribedSkus` | MCP: `billing.costs` / REST: `/reports/getOffice365ActivationCounts` | MCP: `signins.list` / REST: `/auditLogs/signIns` |
| OneDrive | MCP: `users.list` / REST: `/users` | MCP: `onedrive.last_activity` / REST: `/reports/getOneDriveActivityUserDetail` | MCP: `subscriptions.list` / REST: `/subscribedSkus` | MCP: `billing.costs` / REST: `/reports/getOffice365ActivationCounts` | MCP: `signins.list` / REST: `/auditLogs/signIns` |
| Power BI | MCP: `users.list` / REST: `/users` | MCP: `power_bi.last_activity` / REST: `/reports/getPowerBIActivityUserDetail` | MCP: `subscriptions.list` / REST: `/subscribedSkus` | MCP: `billing.costs` / REST: `/reports/getOffice365ActivationCounts` | MCP: `signins.list` / REST: `/auditLogs/signIns` |
| Viva | MCP: `users.list` / REST: `/users` | MCP: `viva.last_activity` / REST: `/reports/getOffice365ActiveUserDetail` | MCP: `subscriptions.list` / REST: `/subscribedSkus` | MCP: `billing.costs` / REST: `/reports/getOffice365ActivationCounts` | MCP: `signins.list` / REST: `/auditLogs/signIns` |

## File references
- YAML mapping file: `connectors/m365/tool_map.yaml`
- Connector manifest: `connectors/m365/manifest.yaml`
