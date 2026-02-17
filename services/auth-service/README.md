# Auth Service

Authentication service handling OAuth2/OIDC token exchange and JWT validation.

## Directory structure

| Folder | Description |
| --- | --- |
| [src/](./src/) | Service implementation (auth.py, main.py) |
| [tests/](./tests/) | Test suites |

## Key files

| File | Description |
| --- | --- |
| `main.py` | Application entrypoint |
| `Dockerfile` | Container build definition |

## Generated docs

- Endpoint reference (source of truth): [`docs/generated/services/auth-service.md`](../../docs/generated/services/auth-service.md).
- Regenerate with: `python ops/tools/codegen/generate_docs.py`.
