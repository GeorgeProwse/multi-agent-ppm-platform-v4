# Credential Acquisition Guide

This guide explains how operators obtain credentials required to deploy and operate the platform.

## Azure access
1. Request Azure subscription access through the access management portal.
2. Ensure you have `Contributor` and `Key Vault Secrets Officer` roles for the target resource group.
3. Verify access:
   ```bash
   az account show
   az keyvault secret list --vault-name <vault-name>
   ```

## CI/CD service principal
1. Create a service principal scoped to the resource group:
   ```bash
   az ad sp create-for-rbac \
     --name "ppm-cicd" \
     --role contributor \
     --scopes /subscriptions/<subscription-id>/resourceGroups/<rg>
   ```
2. Store output in the CI secrets vault (`AZURE_CREDENTIALS`).
3. Grant Key Vault access for secret retrieval.

## Database credentials
- Retrieve database connection strings from Key Vault.
- Validate connectivity using `psql` or application health checks.

## Connector credentials
- Jira: create API token under Atlassian account and store in Key Vault.
- ServiceNow: create integration user with read permissions.
- Azure DevOps: create PAT with `Project & Team` read scopes.

## OIDC + SCIM provisioning credentials
1. Register an OIDC application in your IdP (Okta, Entra ID, Auth0, etc.).
2. Configure redirect URI: `https://<web-host>/oidc/callback`.
3. Add custom claims:
   - `tenant_id` (string) for tenant routing.
   - `roles` (array/string) for RBAC role mapping.
4. Store the client secret in the secrets vault:
   - `OIDC_CLIENT_SECRET` (use env/file reference in runtime config).
5. Generate a long-lived SCIM provisioning token and store it in the secrets vault:
   - `SCIM_SERVICE_TOKEN` (use env/file reference in runtime config).
6. Distribute SCIM base URL and token to IdP provisioning:
   - `https://<identity-access-host>/scim/v2`
7. Rotate `SCIM_SERVICE_TOKEN` by issuing a new token, updating the secret reference, restarting `identity-access`, and updating the IdP connector with the new bearer token.

## Least privilege checklist
- [ ] Remove unused credentials after onboarding.
- [ ] Audit access quarterly.
- [ ] Enforce MFA for interactive accounts.
