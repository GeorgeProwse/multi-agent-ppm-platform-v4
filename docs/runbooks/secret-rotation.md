# Secret Rotation Runbook

This runbook defines the procedures for rotating secrets safely across all environments.

## Rotation cadence
- **JWT signing keys:** every 90 days.
- **Database credentials:** every 180 days or upon personnel change.
- **Connector API tokens:** every 90 days.
- **Service principals:** every 180 days.

## Rotation process
1. **Generate new secret value** in Azure Key Vault.
2. **Stage the new secret** alongside the existing version.
3. **Update configuration** to use the new version (Key Vault version pin or updated secret name).
4. **Roll deployments** to pick up new secrets.
5. **Validate** authentication, connectors, and workflows.
6. **Revoke old secret** after validation completes.

## Validation checks
- API `/api/v1/status` returns `healthy`.
- Connector sync jobs authenticate successfully.
- Audit log events continue to ingest.

## Emergency rotation
- Trigger immediate rotation if compromise is suspected.
- Notify security and update incident record.
- Force logout of user sessions if JWT keys are rotated.

## Tracking
- Record rotation date, owner, and next due date in the secrets inventory.
- Use Key Vault access logs to confirm rotation success.
