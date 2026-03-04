# Financial Management Agent Tests

## Purpose

Hold test assets for Financial Management to validate budget creation, cost tracking,
forecasting, variance analysis, EVM calculations, and profitability metrics.

## What's inside

- `README.md`: Documentation for this directory.
- `test_financial_management_agent.py`: Unit tests for the FinancialManagementAgent.

## How to run / develop / test

```bash
pytest agents/delivery-management/financial-management-agent/tests
```

## Configuration

No component-specific configuration; tests rely on shared repo fixtures in `tests/` and `.env`.

## Troubleshooting

- No tests collected: add `test_*.py` modules alongside this README.
- Import errors: ensure the repo root is on `PYTHONPATH` (run from repo root).
