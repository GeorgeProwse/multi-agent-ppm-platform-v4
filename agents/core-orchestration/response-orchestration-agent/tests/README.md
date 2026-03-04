# Response Orchestration Agent Tests

## Purpose

Hold test assets for Response Orchestration to validate multi-agent query coordination,
parallel/sequential execution, and response aggregation.

## What's inside

- `README.md`: Documentation for this directory.
- `test_response_orchestration_agent.py`: Unit tests for the ResponseOrchestrationAgent.

## How to run / develop / test

    pytest agents/core-orchestration/response-orchestration-agent/tests

## Configuration

No component-specific configuration; tests rely on shared repo fixtures in `tests/` and `.env`.

## Troubleshooting

- No tests collected: add `test_*.py` modules alongside this README.
- Import errors: ensure the repo root is on `PYTHONPATH` (run from repo root).
