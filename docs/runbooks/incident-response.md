# Incident Response

This runbook outlines incident response steps, severity definitions, and escalation for the PPM platform.

## Severity Levels

| Severity | Description | Response Time |
| --- | --- | --- |
| SEV-1 | Platform outage, data loss, security breach | 15 minutes |
| SEV-2 | Major functionality degraded | 30 minutes |
| SEV-3 | Partial degradation or single service issue | 4 hours |

## RTO/RPO Reference

- **RTO (Recovery Time Objective):** 1–4 hours depending on service.
- **RPO (Recovery Point Objective):** 0–30 minutes based on data class.

## Immediate Response Steps

1. **Acknowledge alert**
   - Confirm alert severity and affected service.
   - Start incident bridge and notify stakeholders.
2. **Triage**
   - Review service dashboards and logs.
   - Confirm tenant impact and scope.
3. **Containment**
   - Disable failing deployments or rollback.
   - Isolate compromised credentials.
4. **Mitigation**
   - Apply hotfix or scale out services.
   - Route traffic to healthy region if needed.
5. **Communication**
   - Update status page every 30 minutes.
   - Provide tenant-facing updates for SEV-1/2.
6. **Resolution**
   - Confirm metrics return to SLO targets.
   - Validate tenant isolation and RBAC integrity.
7. **Post-incident**
   - Run postmortem within 5 business days.
   - Track remediation actions to closure.

## Security Incident Addendum

- Rotate secrets in Key Vault and revoke tokens.
- Validate audit log integrity and retention policies.
- Perform tenant impact assessment and notify compliance.
