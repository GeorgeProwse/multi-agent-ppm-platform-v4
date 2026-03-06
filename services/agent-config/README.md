# Agent Config Service

## Purpose

Provides centralized storage and retrieval for agent configuration profiles used by runtime orchestration and governance workflows.


## Running locally

```bash
python -m tools.component_runner run --type service --name agent-config --dry-run
```

## Configuration

Configure service settings via environment variables and shared `.env` defaults in the repository root.

## Directory structure

| Folder | Description |
| --- | --- |
| [src/](./src/) | Service implementation |

## Generated docs

- Per-service endpoint reference: [`docs/generated/services/agent-config.md`](../../docs/generated/services/agent-config.md).
- Service endpoint source-of-truth index: [`docs/generated/services/README.md`](../../docs/generated/services/README.md).
- Regenerate with: `python ops/tools/codegen/generate_docs.py`.

## Ownership and support

- Owner: Platform Engineering
- Support: #ppm-platform-support

