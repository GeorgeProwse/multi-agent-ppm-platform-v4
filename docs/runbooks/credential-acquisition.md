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

## Least privilege checklist
- [ ] Remove unused credentials after onboarding.
- [ ] Audit access quarterly.
- [ ] Enforce MFA for interactive accounts.
