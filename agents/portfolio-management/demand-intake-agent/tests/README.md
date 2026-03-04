# Demand Intake Agent Tests

## Purpose

Hold test assets for Demand Intake to validate request submission, NLP categorization,
duplicate detection, and pipeline query.

## What's inside

- `README.md`: Documentation for this directory.
- `test_demand_intake_agent.py`: Unit tests for the DemandIntakeAgent.

## How to run / develop / test

    pytest agents/portfolio-management/demand-intake-agent/tests

## Configuration

No component-specific configuration; tests rely on shared repo fixtures in `tests/` and `.env`.

## Troubleshooting

- No tests collected: add `test_*.py` modules alongside this README.
- Import errors: ensure the repo root is on `PYTHONPATH` (run from repo root).
