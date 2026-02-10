# Security Testing

This project includes automated **static analysis** and **dynamic application security testing (DAST)** as part of CI to detect vulnerabilities early.

## Tools integrated

- **Bandit** for Python static code analysis with security-focused rules.
- **OWASP ZAP baseline** for DAST against local application endpoints.

## Local execution

### 1) Run static analysis (Bandit)

```bash
python ops/tools/run_bandit.py
```

Behavior:
- Runs `bandit -r .` in JSON mode.
- Writes report to `artifacts/security/bandit-report.json`.
- Exits non-zero if any **high severity** issues are found.

### 2) Run DAST scan (OWASP ZAP baseline)

```bash
python ops/tools/run_dast.py
```

Behavior:
- Starts a minimal built-in test app by default (or uses `--base-url` / `--app-cmd`).
- Verifies test endpoints (`/api`, `/health`) are reachable.
- Executes ZAP baseline and stores reports in:
  - `artifacts/security/dast-report.json`
  - `artifacts/security/dast-report.html`
- Exits non-zero if any **high** or **critical** findings are detected.

Useful options:

```bash
python ops/tools/run_dast.py --base-url http://127.0.0.1:8000
python ops/tools/run_dast.py --app-cmd "uvicorn apps.api.main:app --host 127.0.0.1 --port 18080"
python ops/tools/run_dast.py --report-dir artifacts/security
```

## CI integration

The CI workflow (`.github/workflows/ci.yml`) executes both scripts and uploads generated reports as build artifacts under `security-scan-reports`.

## Interpreting reports

- **Bandit report** (`bandit-report.json`): inspect `results` for issue metadata and source locations.
- **DAST report** (`dast-report.json` / `dast-report.html`): inspect ZAP alerts. The script currently fails for:
  - `riskcode >= 3` (high), or
  - alerts labeled critical.

A failing security stage should be treated as a release blocker until findings are triaged and resolved or explicitly risk-accepted.
