# UI Screenshot Assets

This folder centralizes UI screenshots used in documentation and product artifacts. Store all UI captures here so docs and release notes can link to a single, curated source of truth.

## Naming conventions

Use descriptive, kebab-case filenames with the app surface, feature, and context:

```
<app>-<surface>-<feature>-<context>-<YYYYMMDD>.png
```

Examples:

- `web-workspace-portfolio-overview-default-20250115.png`
- `admin-console-settings-roles-edit-20250115.png`

## Expected resolution

- Preferred: **1920×1080** (16:9) for full-page views.
- Acceptable: **1440×900** for laptop-sized captures.
- Avoid scaling in post-processing; capture at the native resolution of the viewport.

## Capture guidelines

- Capture screenshots from the running UI in `apps/web` or `apps/admin-console`.
- Use seed/demo data that does not contain customer or personal information.
- Ensure UI chrome is consistent (no dev tools panels, no debug banners, no local-only feature flags).
- Capture in light mode unless explicitly documenting a dark theme variant.
- If multiple states are required, include a short suffix (e.g., `-empty`, `-filled`, `-hover`).

## File organization

- Store raw and final assets directly in this folder.
- If you need subfolders, group by app (e.g., `web/`, `admin-console/`).

## Binary diff note

PNG screenshots are binary assets, so some PR viewers (especially on mobile) cannot render a text diff and may display a "binary files not supported" message. If you hit that limitation, create the PR from the main GitHub web UI (desktop) or from the CLI; the assets will still be included in the change set even if the diff view fails to render.

## Generating screenshots

Run the Playwright-based capture script (requires a built frontend):

```bash
cd apps/web/frontend && npx vite build
node ops/scripts/take-screenshot.mjs [optional-output-path]
```

The script starts a Vite dev server, mocks backend API responses, and captures multiple screens at 1920×1080.

## Recent captures (all nav pages)

**Navigate**
- `web-home-three-panel-default-20260228.png` — Home dashboard with quick-action chips
- `web-demo-run-agents-default-20260228.png` — Demo Run showing all 25 agent executions
- `web-enterprise-uplift-default-20260228.png` — Enterprise Uplift with demand table and scenario compare
- `web-portfolios-directory-default-20260228.png` — Portfolio directory with search
- `web-programs-directory-default-20260228.png` — Program directory with search
- `web-projects-directory-default-20260228.png` — Project directory with search

**Work**
- `web-intake-form-default-20260228.png` — Multi-step intake form (Step 1 of 4)
- `web-approvals-pending-default-20260228.png` — My Approvals with pending items and audit trail
- `web-intake-approvals-default-20260228.png` — Intake Approvals with approve/reject cards

**Insights**
- `web-analytics-dashboard-default-20260228.png` — Analytics Dashboard with trend charts and warnings
- `web-documents-repository-default-20260228.png` — Document Repository with version sidebar
- `web-lessons-learned-default-20260228.png` — Lessons Learned with capture form and library

**Admin (Hub Admin)**
- `web-config-agents-default-20260228.png` — Configuration Center: Agents tab
- `web-config-connectors-default-20260228.png` — Configuration Center: Connectors tab
- `web-config-workflows-default-20260228.png` — Configuration Center: Workflows tab
- `web-config-prompts-default-20260228.png` — Prompt Manager with create form and library
- `web-workflow-monitor-default-20260228.png` — Workflow Monitoring with instances and timeline
- `web-methodology-editor-default-20260228.png` — Methodology Editor with stages, activities, and gates

**Auth**
- `web-login-default-20260228.png` — Login / sign-in page

### Legacy placeholders

- `web-login-default-20260208.png`
- `web-intake-new-project-form-default-20260208.png`
- `web-project-workspace-three-panel-default-20260208.png`
