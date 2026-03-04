# Business Case Agent Tests

## Purpose

Hold test assets for Business Case & Investment Analysis to validate business case
generation, ROI calculation, scenario analysis, and investment recommendations.

## What's inside

- `README.md`: Documentation for this directory.
- `test_business_case_investment_agent.py`: Unit tests for the BusinessCaseInvestmentAgent.

## How to run / develop / test

```bash
pytest agents/portfolio-management/business-case-agent/tests
```

## Configuration

No component-specific configuration; tests rely on shared repo fixtures in `tests/` and `.env`.

## Troubleshooting

- No tests collected: add `test_*.py` modules alongside this README.
- Import errors: ensure the repo root is on `PYTHONPATH` (run from repo root).
