# E2E tests

This directory contains e2e tests for the platform.

## Scope
- Test modules that exercise the platform's cross-cutting behavior.
- Fixtures, helpers, and sample payloads needed for these tests.
- Any contract or environment notes required to run them locally.

## Coverage
The suite currently covers 18 end-to-end scenarios across the API gateway, identity, workflow engine,
core services, and key app surfaces.

## Running locally
```bash
pytest tests/e2e
```
