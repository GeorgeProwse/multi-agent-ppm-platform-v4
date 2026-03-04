# Vendor Procurement Agent Tests

## Purpose

Hold test assets for Vendor Procurement to validate vendor onboarding, RFP generation,
vendor scoring, contract management, and invoice reconciliation.

## What's inside

- `README.md`: Documentation for this directory.
- `test_vendor_procurement_agent.py`: Unit tests for the VendorProcurementAgent.

## How it's used

These tests are collected by `pytest` when running `make test` and help validate agent-specific
behavior alongside shared agent runtime checks.

## How to run / develop / test

```bash
pytest agents/delivery-management/vendor-procurement-agent/tests
```

## Configuration

No component-specific configuration; tests rely on shared repo fixtures in `tests/` and `.env`.

## Troubleshooting

- No tests collected: add `test_*.py` modules alongside this README.
- Import errors: ensure the repo root is on `PYTHONPATH` (run from repo root).
