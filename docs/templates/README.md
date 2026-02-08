# Shared Template Library

## Purpose
Provide reusable templates that are either shared across methodologies or tailored to a specific
delivery approach. These templates align with PMBOK-style artefacts and support predictive,
agile, and hybrid delivery practices.

## What's inside
### Cross-methodology categories
- `checklists/`: Delivery, quality, and readiness checklists.
- `charters/`: Team, project, program, and governance charters.
- `plans/`: Management plans, release/acceptance plans, and UAT planning.
- `reports/`: Status, assessments, dashboards, and closure reporting.
- `registers-logs/`: Issue, risk, decision, benefits, and stakeholder registers/logs.
- `requirements/`: Scope statements, requirements libraries, and traceability.
- `risk/`: Risk analysis and assessment artefacts.
- `quality/`: Quality gates, UAT support, and quality management artefacts.
- `communications/`: Communication plans, calendars, and stakeholder comms workflows.
- `governance/`: Governance frameworks, decision models, escalation, and authority artefacts.
- `schedule/`: Schedules, WBS templates, and schedule metrics.
- `finance/`: Budgets, purchase orders, and ROI tracking.
- `resources/`: Capacity, resource, and team performance planning.
- `portfolio-program/`: Portfolio/program business cases, WBS, and prioritization.
- `product/`: Product strategy, vision, and backlog artefacts.
- `change/`: Change requests, readiness, and change-control process artefacts.
- `stakeholders/`: Stakeholder analysis, mapping, and engagement artefacts.
- `meetings/`: Meeting agendas, standups, and sprint ceremonies.

### Methodology-specific libraries
- `docs/templates/shared`: Cross-methodology plans, logs, reports, and baselines (scope, schedule,
  cost, quality, risk, procurement, resource, communications, and stakeholder artefacts), plus
  specialized guidance such as schedule risk analysis, financial risk management, and template
  customization governance.
- `docs/templates/agile`: Agile-only templates such as sprint planning, backlog management, and
  retrospectives, organized by planning, reports, risk, roles, and meetings.
- `docs/templates/hybrid`: Hybrid governance templates for milestone planning, integrated risk,
  and program-level cadence, organized by plans, resources, risk, and governance.
- `docs/templates/waterfall`: Waterfall-only artefacts such as charters, WBS, baselines, and
  closure documentation, organized by planning and assessment.

## Consolidation Policy
Templates live in this folder hierarchy only. When duplicate templates existed in methodology
folders, the most comprehensive version was retained here and references were updated to use it.
If you need a methodology-specific variant, add it under the appropriate subfolder and link to it
from the methodology map.

## How it's used
Templates are referenced by methodology maps and the cross-methodology template catalog. Tailor
sections by adding or removing rows, adapting terminology, and mapping artefacts to local
governance expectations.

## Spreadsheet Templates
Some templates are delivered as spreadsheets (e.g., cost baseline, risk register). Use Excel or
Google Sheets to edit these files and preserve formulas. If your workflow requires an online
version, upload the spreadsheet to your document repository and link it from the catalog.

## Related References
- Template catalog (`docs/product/templates-catalog.md`).
