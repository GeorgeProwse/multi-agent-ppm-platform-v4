## Security Overview

The platform protects data, enforces access controls, captures audit evidence, and satisfies compliance requirements across four intersecting planes: identity (SSO), authorization (RBAC/ABAC), data protection (encryption and retention), and audit/monitoring. Security controls are documented under `docs/compliance/` and enforced by agents and infrastructure defined in `ops/infra/`.

### Identity and authentication

- **SSO**: Azure AD / Okta via OIDC or SAML.
- **Service authentication**: managed identities or mTLS between internal services.
- **API tokens**: scoped tokens for external integrations.

### Authorization model (RBAC + ABAC)

- **RBAC**: role-based permissions for portfolios, programs, and projects.
- **ABAC**: attribute-based policies scoped to data classification, region, and business unit.
- **Field-level controls**: sensitive fields are masked for restricted roles.

### Audit events

Audit events are captured for:

- Stage-gate approvals
- Budget or scope changes
- Data synchronization activity
- Authentication and authorization decisions

The audit event schema is defined in [`data/schemas/audit-event.schema.json`](../../data/schemas/audit-event.schema.json).

### Data protection and retention

- **Encryption**: TLS in transit; AES-256 at rest.
- **Secrets**: Azure Key Vault references held in `ops/config/`.
- **Retention**: see the [Retention Policy](../compliance/retention-policy.md) for standard schedules.
- **Privacy**: a DPIA template is provided in the [Privacy DPIA Template](../compliance/privacy-dpia-template.md).

### Threat model summary

The [Threat Model](../compliance/threat-model.md) identifies the top platform risks:

- Connector credential leakage
- Unauthorized cross-tenant access
- LLM prompt injection
- Data exfiltration via integrations

Mitigations include secret rotation, tenant isolation, policy guardrails, and audit logging.

### Verification

To confirm compliance documents are present, run:

```bash
ls docs/compliance
```

Expected output includes `retention-policy.md` and `threat-model.md`.

To inspect the audit event schema:

```bash
sed -n '1,120p' data/schemas/audit-event.schema.json
```

### Implementation status

- **Implemented**: documentation, audit schema, retention and DPIA templates.
- **Implemented**: IAM role mapping with Azure AD group ingestion and automated policy enforcement via the policy engine.

### Related documentation

- [Compliance Controls Mapping](../compliance/controls-mapping.md)
- [Financial Services Compliance Management Template (Australia)](../compliance/financial-services-compliance-management-template.md)
- [Retention Policy](../compliance/retention-policy.md)
- [Threat Model](../compliance/threat-model.md)

---

## Security Architecture

### Prompt injection detection and sanitisation

The runtime applies prompt injection checks to inbound user-authored prompt fields before agent processing.

#### Detection rules

`packages/llm/prompt_sanitizer.py` implements heuristic pattern checks for common attacks, including:

- attempts to ignore or override system/developer instructions,
- attempts to reveal secrets, credentials, hidden prompts, or chain-of-thought,
- role-escalation language (for example, pretending to be an admin),
- obfuscation hints around decoding hidden prompt material.

`detect_injection(prompt: str) -> bool` returns `True` if any of these patterns match.

#### Sanitisation rules

`sanitize_prompt(prompt: str) -> str` neutralises known attack phrases and high-risk formatting patterns by:

- replacing known injection phrases with `[REMOVED_INJECTION_PHRASE]`,
- neutralising triple-backtick blocks,
- HTML-encoding angle brackets.

#### BaseAgent enforcement flow

`agents/runtime/src/base_agent.py` evaluates candidate prompt fields during `execute()`.

- If injection is detected and `allow_injection: false` (default), execution is rejected with a safe user-facing error.
- If injection is detected and `allow_injection: true`, the prompt is sanitised and processing continues.
- Audit and structured logs include detection metadata: detected fields, sanitised fields, and enforcement mode.

#### Configuration

Per-agent behaviour is configurable in agent YAML files (for example `ops/config/agents/intent-router.yaml`):

```yaml
allow_injection: false
prompt_fields:
  - prompt
  - user_prompt
  - query
```

- `allow_injection` controls reject (`false`) vs sanitise-and-continue (`true`).
- `prompt_fields` defines which input keys are inspected.

---

## Security Testing

Automated static analysis and dynamic application security testing (DAST) are integrated into CI to detect vulnerabilities early.

### Tools integrated

- **Bandit**: Python static code analysis with security-focused rules.
- **OWASP ZAP baseline**: DAST against local application endpoints.

### Local execution

#### 1. Run static analysis (Bandit)

```bash
python ops/tools/run_bandit.py
```

Behaviour:

- Runs `bandit -r .` in JSON mode.
- Writes the report to `artifacts/security/bandit-report.json`.
- Exits non-zero if any **high severity** issues are found.

#### 2. Run DAST scan (OWASP ZAP baseline)

```bash
python ops/tools/run_dast.py
```

Behaviour:

- Starts a minimal built-in test app by default (or uses `--base-url` / `--app-cmd`).
- Verifies test endpoints (`/api`, `/health`) are reachable.
- Executes the ZAP baseline and stores reports in:
  - `artifacts/security/dast-report.json`
  - `artifacts/security/dast-report.html`
- Exits non-zero if any **high** or **critical** findings are detected.

Useful options:

```bash
python ops/tools/run_dast.py --base-url http://127.0.0.1:8000
python ops/tools/run_dast.py --app-cmd "uvicorn apps.api.main:app --host 127.0.0.1 --port 18080"
python ops/tools/run_dast.py --report-dir artifacts/security
```

### CI integration

The CI workflow (`.github/workflows/ci.yml`) executes both scripts and uploads generated reports as build artifacts under `security-scan-reports`.

### Interpreting reports

- **Bandit report** (`bandit-report.json`): inspect `results` for issue metadata and source locations.
- **DAST report** (`dast-report.json` / `dast-report.html`): inspect ZAP alerts. The script fails for:
  - `riskcode >= 3` (high), or
  - alerts labeled critical.

A failing security stage must be treated as a release blocker until findings are triaged and resolved or explicitly risk-accepted.

---

## Container Runtime and Identity Policy

### Monorepo-wide baseline

All first-party runtime containers in this monorepo must run as the same non-root Linux identity:

| Attribute | Value |
|-----------|-------|
| User | `appuser` |
| UID | `10001` |
| Group | `appuser` |
| GID | `10001` |

This baseline applies to services, apps, agents, and connector images unless an explicit exception is documented in this section.

### Security rationale

- Avoids privileged `root` execution at runtime.
- Provides a predictable least-privilege identity for Kubernetes/OpenShift and Docker runtimes.
- Reduces host bind-mount permission drift by keeping file ownership numerically consistent.
- Makes `COPY --chown` behaviour deterministic across images.

### Shared volumes and file ownership

To keep shared volume behaviour consistent across services:

1. Build images so application files are owned by `10001:10001`.
2. Run processes as UID/GID `10001:10001`.
3. For writable shared volumes, ensure the volume path is writable by `10001` (for example via storage class permissions, init jobs, or platform-level `fsGroup: 10001`).

Recommended Kubernetes `securityContext` alignment:

```yaml
runAsNonRoot: true
runAsUser: 10001
runAsGroup: 10001
fsGroup: 10001
allowPrivilegeEscalation: false
```

### Exceptions process

No current exceptions are required in-repo.

If a service must diverge (for example, requiring root to bind privileged ports, perform package installation at runtime, or accommodate third-party image constraints), the exception must be documented in this section with:

- service/image path,
- required UID/GID,
- specific security rationale,
- compensating controls,
- planned removal/review date.
