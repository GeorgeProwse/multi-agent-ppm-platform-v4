# Policy Engine

The policy engine evaluates policy bundles and enforces RBAC decisions for the platform. It loads
policy bundles from `services/policy-engine/policies/` and exposes an RBAC evaluation endpoint that
API gateway uses for authorization.

## Endpoints

- `POST /policies/evaluate`: Validate policy bundles.
- `POST /rbac/evaluate`: Evaluate tenant RBAC decisions.

## Run locally

```bash
python -m tools.component_runner run --type service --name policy-engine
```

## Environment variables

| Variable | Default | Description |
| --- | --- | --- |
| `POLICY_BUNDLE_PATH` | `services/policy-engine/policies/bundles/default-policy-bundle.yaml` | Bundle used for validation |

## Example

```bash
curl -X POST http://localhost:8080/rbac/evaluate \
  -H "Content-Type: application/json" \
  -d '{"tenant_id":"tenant-alpha","roles":["portfolio_admin"],"permission":"project.read"}'
```

## Tests

```bash
pytest services/policy-engine/tests
```
