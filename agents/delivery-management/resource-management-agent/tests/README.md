# Resource Management Agent Tests

## Purpose

Hold test assets for Resource Management to validate resource pool management, capacity planning,
skill matching, utilization tracking, and HR integration.

## What's inside

- `README.md`: Documentation for this directory.
- `test_resource_management_agent.py`: Unit tests for the ResourceCapacityAgent.

## How it's used

These tests are collected by `pytest` when running `make test` and help validate agent-specific
behavior alongside shared agent runtime checks.

## How to run / develop / test

```bash
pytest agents/delivery-management/resource-management-agent/tests
```

## Configuration

No component-specific configuration; tests rely on shared repo fixtures in `tests/` and `.env`.

## Troubleshooting

- No tests collected: add `test_*.py` modules alongside this README.
- Import errors: ensure the repo root is on `PYTHONPATH` (run from repo root).
