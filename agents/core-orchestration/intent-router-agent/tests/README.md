# Intent Router Agent Tests

## Purpose

Hold test assets for Intent Router to validate NLP-based intent classification,
query disambiguation, multi-intent detection, and agent routing.

## What's inside

- `README.md`: Documentation for this directory.
- `test_intent_router_agent.py`: Unit tests for the IntentRouterAgent.

## How to run / develop / test

    pytest agents/core-orchestration/intent-router-agent/tests

## Configuration

No component-specific configuration; tests rely on shared repo fixtures in `tests/` and `.env`.

## Troubleshooting

- No tests collected: add `test_*.py` modules alongside this README.
- Import errors: ensure the repo root is on `PYTHONPATH` (run from repo root).
