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

