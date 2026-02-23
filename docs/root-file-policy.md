# Root File Policy

This policy defines what is allowed at repository root and why.

## Policy goals

- Keep root navigable for contributors and automation.
- Preserve discovery conventions required by core tooling.
- Route non-root-sensitive artifacts into domain folders (`docs/`, `ops/`, `ops/scripts/`, etc.).

## Root allowlist categories

### 1) Root-sensitive toolchain files (must stay)

These are resolved by default by package managers, build tools, CI, or local workflows:

- `pyproject.toml`
- `pnpm-workspace.yaml`
- `pnpm-lock.yaml`
- `Makefile`
- `mkdocs.yml`
- `.pre-commit-config.yaml`
- `.gitignore`
- `README.md`
- `CONTRIBUTING.md`
- `LICENSE`
- `SECURITY.md`

### 2) Consolidated ops files (moved out of root)

These were previously loose at root and are now organised under `ops/`:

- `ops/docker/docker-compose.yml`
- `ops/docker/docker-compose.test.yml`
- `ops/config/alembic.ini`
- `ops/config/.env.example`
- `ops/config/.env.demo`
- `ops/requirements/requirements.txt`
- `ops/requirements/requirements-dev.txt`
- `ops/requirements/requirements.in`
- `ops/requirements/requirements-dev.in`
- `ops/requirements/requirements-demo.txt`

### 3) Consolidated docs (moved into docs/)

- `docs/CHANGELOG.md`
- `docs/REPO_STRUCTURE.md`

### 4) Root-level compatibility modules (temporary allowlist)

The following modules currently have direct imports from multiple packages and services and remain at root until a dedicated import migration phase is complete:

- `prompt_registry.py`
- `runtime_flags.py`
- `pydantic_settings.py`

### 5) Approved root directories

Top-level domain directories are allowed for monorepo organization:

- `agents/`, `apps/`, `ops/config/`, `data/`, `packages/ui-kit/design-system/`, `docs/`, `examples/`, `ops/infra/`,
  `integrations/`, `ops/`, `packages/`, `ops/config/`, `agents/runtime/prompts/`, `ops/scripts/`, `services/`, `tests/`

## Change process for root additions

1. Prefer placing new files in an existing domain folder.
2. If a new root file is required, document rationale in this policy file as part of the same change.
3. Update `ops/tools/check_root_layout.py` allowlist in the same PR.
4. Ensure `make check-root-layout` passes.

## Explicit non-goals (phase 1)

- No risky relocations of compatibility modules.
- No breaking changes to Python or Node install/discovery flows.
