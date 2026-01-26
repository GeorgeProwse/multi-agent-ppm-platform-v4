# Secret Initialization Runbook

This runbook documents how to bootstrap secrets for new environments.

## Scope
- Azure Key Vault secrets
- Kubernetes SecretProviderClass configuration
- Service principal credentials for CI/CD

## Initial bootstrap
1. **Create Key Vault**
   - Provision Key Vault via Terraform (`infra/terraform/main.tf`).
2. **Create secret namespace**
   - Use a dedicated prefix per environment (e.g., `prod-`, `staging-`).
3. **Seed baseline secrets**
   - Database connection strings
   - Redis connection strings
   - JWT signing keys and JWKS URL
   - Connector API credentials (Jira, ServiceNow, Azure DevOps)
4. **Configure Kubernetes CSI driver**
   - Apply `infra/kubernetes/secret-provider-class.yaml`.
   - Verify workloads mount secrets at runtime.

## Validation
- `kubectl describe pod` shows CSI mount ready.
- API gateway `/api/v1/status` returns `healthy`.
- Identity service can validate JWTs using Key Vault-backed secrets.

## Rotation readiness
- Ensure each secret has an owner, rotation schedule, and alternate version.
- Verify alerting for Key Vault access failures.
