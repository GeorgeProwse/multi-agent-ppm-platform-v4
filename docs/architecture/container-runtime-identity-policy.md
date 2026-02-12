# Container Runtime Identity Policy (UID/GID)

## Monorepo-wide baseline

All first-party runtime containers in this monorepo must run as the same non-root Linux identity:

- **User:** `appuser`
- **UID:** `10001`
- **Group:** `appuser`
- **GID:** `10001`

This baseline applies to services, apps, agents, and connector images unless an explicit exception is documented.

## Security rationale

- Avoids privileged `root` execution at runtime.
- Provides a predictable least-privilege identity for Kubernetes/OpenShift and Docker runtimes.
- Reduces host bind-mount permission drift by keeping file ownership numerically consistent.
- Makes `COPY --chown` behavior deterministic across images.

## Shared volumes and file ownership

To keep shared volume behavior consistent across services:

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

## Exceptions process

No current exceptions are required in-repo.

If a service must diverge (for example, requiring root to bind privileged ports, package installation at runtime, or third-party image constraints), the exception must be documented in this file with:

- service/image path,
- required UID/GID,
- specific security rationale,
- compensating controls,
- planned removal/review date.
