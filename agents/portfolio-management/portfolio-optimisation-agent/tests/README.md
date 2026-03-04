# Portfolio Optimisation Agent Tests

## Purpose

Hold test assets for Portfolio Optimisation to validate portfolio prioritization,
strategic alignment scoring, capacity-constrained optimization, and scenario analysis.

## What's inside

- `README.md`: Documentation for this directory.
- `test_portfolio_strategy_agent.py`: Unit tests for the PortfolioStrategyAgent.

## How to run / develop / test

```bash
pytest agents/portfolio-management/portfolio-optimisation-agent/tests
```

## Configuration

No component-specific configuration; tests rely on shared repo fixtures in `tests/` and `.env`.

## Troubleshooting

- No tests collected: add `test_*.py` modules alongside this README.
- Import errors: ensure the repo root is on `PYTHONPATH` (run from repo root).
