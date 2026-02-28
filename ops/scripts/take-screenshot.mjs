#!/usr/bin/env node
/**
 * Takes screenshots of every navigation page in the PPM Platform web app.
 *
 * Usage:
 *   node ops/scripts/take-screenshot.mjs
 *
 * Captures every sidebar nav item at 1920×1080 using Playwright with mocked
 * API responses so no backend is needed.
 */
import { createRequire } from 'module';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname_script = path.dirname(fileURLToPath(import.meta.url));
const ROOT_DIR = path.resolve(__dirname_script, '../..');

// Resolve playwright from pnpm's nested node_modules
const playwrightPkg = path.join(
  ROOT_DIR,
  'node_modules/.pnpm/playwright@1.58.2/node_modules/playwright/index.mjs',
);
const { chromium } = await import(playwrightPkg);

// Resolve vite from the frontend workspace
const require = createRequire(
  path.join(ROOT_DIR, 'apps/web/frontend/node_modules/.package-lock.json'),
);
const { createServer } = await import(
  path.join(ROOT_DIR, 'apps/web/frontend/node_modules/vite/dist/node/index.js')
);

const FRONTEND = path.join(ROOT_DIR, 'apps/web/frontend');
const SCREENSHOTS_DIR = path.join(ROOT_DIR, 'docs/assets/ui/screenshots');
const datestamp = new Date().toISOString().slice(0, 10).replace(/-/g, '');

function screenshotPath(name) {
  return path.join(SCREENSHOTS_DIR, `${name}-${datestamp}.png`);
}

// ── Mock data ────────────────────────────────────────────────────────

const sessionMock = {
  authenticated: true,
  subject: 'demo.user',
  tenant_id: 'acme-corp',
  roles: ['ppm-admin', 'admin'],
};

const rolesMock = [
  {
    id: 'ppm-admin',
    permissions: [
      'portfolio.view', 'methodology.edit', 'intake.approve',
      'config.manage', 'llm.manage', 'analytics.view',
      'audit.view', 'roles.manage',
    ],
  },
];

const portfolioDashboard = {
  dashboard: {
    name: 'Enterprise Digital Portfolio',
    kpis: [
      { label: 'Active Projects', value: '24', delta: '+3' },
      { label: 'On Track', value: '79%', delta: '+5%' },
      { label: 'Budget Utilisation', value: '$4.2M / $5.8M' },
      { label: 'Avg Cycle Time', value: '42 days', delta: '-6 days' },
    ],
    pipeline: [
      { stage: 'Intake', count: 8, target: 10, trend: 'up' },
      { stage: 'Planning', count: 5, target: 6, trend: 'steady' },
      { stage: 'Execution', count: 9, target: 8, trend: 'up' },
      { stage: 'Closing', count: 2, target: 4, trend: 'down' },
    ],
    charters: [
      { id: 'CHR-101', name: 'Cloud Migration Phase 3', owner: 'Sarah Chen', status: 'Approved', updated: '2026-02-25' },
      { id: 'CHR-102', name: 'Customer Portal Redesign', owner: 'James Lee', status: 'In Review', updated: '2026-02-27' },
    ],
    risks: [
      { id: 'RSK-01', title: 'Vendor delivery delay on infra module', severity: 'High', owner: 'James Lee' },
      { id: 'RSK-02', title: 'Key resource attrition risk', severity: 'Medium', owner: 'Sarah Chen' },
    ],
    issues: [
      { id: 'ISS-01', title: 'CI pipeline intermittent failures', status: 'Open', owner: 'DevOps Team' },
    ],
    healthMetrics: [
      { label: 'Schedule', value: 'Green', status: 'success' },
      { label: 'Budget', value: 'Amber', status: 'warning' },
      { label: 'Scope', value: 'Green', status: 'success' },
      { label: 'Quality', value: 'Green', status: 'success' },
    ],
    relatedItems: [
      { id: 'PRG-01', name: 'Cloud Modernisation Program', status: 'Active', owner: 'Sarah Chen' },
    ],
    wbs: [
      { name: 'Phase 1 – Discovery', children: ['Stakeholder interviews', 'Current state assessment'] },
      { name: 'Phase 2 – Build', children: ['Sprint 1', 'Sprint 2', 'Integration testing'] },
    ],
    requirements: [
      { id: 'REQ-01', title: 'SSO integration with corporate IdP', priority: 'High', status: 'Approved' },
      { id: 'REQ-02', title: 'Multi-tenant data isolation', priority: 'High', status: 'In Progress' },
    ],
  },
};

const demandMock = {
  items: [
    { id: 'd1', title: 'Mobile App Redesign', status: 'in-progress', value: 50000, effort: 800, risk: 'medium', score: 87.5 },
    { id: 'd2', title: 'API Gateway Modernisation', status: 'pending', value: 75000, effort: 1200, risk: 'high', score: 65.2 },
    { id: 'd3', title: 'Data Lake Migration', status: 'completed', value: 120000, effort: 2000, risk: 'high', score: 92.1 },
    { id: 'd4', title: 'Customer Portal v3', status: 'in-progress', value: 95000, effort: 1600, risk: 'low', score: 78.8 },
    { id: 'd5', title: 'DevOps Pipeline Uplift', status: 'pending', value: 40000, effort: 600, risk: 'low', score: 71.3 },
  ],
};

const scenariosMock = {
  scenarios: [
    { id: 's1', name: 'Conservative', value_score: 125000, budget: 2000000, published: false },
    { id: 's2', name: 'Balanced Growth', value_score: 245000, budget: 3500000, published: true },
    { id: 's3', name: 'Aggressive', value_score: 425000, budget: 5000000, published: false },
  ],
};

const approvalsMock = [
  {
    approval_id: 'APR-2001', run_id: 'RUN-500', step_id: 'step-review',
    status: 'pending', created_at: '2026-02-26T09:15:00Z', updated_at: '2026-02-26T09:15:00Z',
    metadata: {
      request_type: 'Project Charter', request_id: 'CHR-102',
      approvers: ['demo.user', 'sarah.chen'], deadline: '2026-03-05',
      details: { project: 'Customer Portal Redesign', sponsor: 'James Lee', budget: '$320,000' },
    },
  },
  {
    approval_id: 'APR-2002', run_id: 'RUN-501', step_id: 'step-gate',
    status: 'pending', created_at: '2026-02-25T14:30:00Z', updated_at: '2026-02-25T14:30:00Z',
    metadata: {
      request_type: 'Stage Gate – Execution', request_id: 'PRJ-045',
      approvers: ['demo.user'], deadline: '2026-03-01',
      details: { project: 'Cloud Migration Phase 3', gate: 'G3 – Execution Entry', health: 'Green' },
    },
  },
];

const intakeApprovalsMock = [
  {
    request_id: 'REQ-001', status: 'pending', created_at: '2026-02-15T10:30:00Z',
    sponsor: { name: 'John Smith', department: 'Product Engineering', email: 'john.smith@acme.com' },
    business_case: { summary: 'Cloud-Native Payments Platform', expected_benefits: 'Reduce transaction processing time by 60%, enable real-time settlement' },
    success_criteria: { metrics: '99.99% uptime, <200ms p99 latency, PCI-DSS Level 1 compliance' },
    attachments: { summary: 'Architecture diagrams, cost-benefit analysis, vendor evaluation' },
    reviewers: ['pm-reviewer', 'security-lead'], decision: null,
  },
  {
    request_id: 'REQ-002', status: 'pending', created_at: '2026-02-20T14:00:00Z',
    sponsor: { name: 'Maria Garcia', department: 'Customer Experience', email: 'maria.garcia@acme.com' },
    business_case: { summary: 'Omnichannel Support Hub', expected_benefits: 'Consolidate 4 support channels, reduce resolution time by 35%' },
    success_criteria: { metrics: 'CSAT score >4.5, first-contact resolution >80%' },
    attachments: { summary: 'Customer journey maps, competitive analysis' },
    reviewers: ['cx-director'], decision: null,
  },
];

const analyticsTrendsMock = {
  project_id: 'demo-project', computed_at: '2026-02-28T15:30:00Z', period_count: 6,
  series: [
    {
      metric: 'budget_utilization',
      points: [
        { timestamp: '2026-01-01T00:00:00Z', value: 35.2 }, { timestamp: '2026-01-15T00:00:00Z', value: 42.5 },
        { timestamp: '2026-02-01T00:00:00Z', value: 48.3 }, { timestamp: '2026-02-15T00:00:00Z', value: 55.8 },
        { timestamp: '2026-02-22T00:00:00Z', value: 58.1 }, { timestamp: '2026-03-01T00:00:00Z', value: 61.4 },
      ],
      slope: 3.24, forecast: 65.8, forecast_method: 'linear_regression', recent_change: 2.3,
    },
    {
      metric: 'schedule_variance',
      points: [
        { timestamp: '2026-01-01T00:00:00Z', value: -5.2 }, { timestamp: '2026-01-15T00:00:00Z', value: -4.1 },
        { timestamp: '2026-02-01T00:00:00Z', value: -3.0 }, { timestamp: '2026-02-15T00:00:00Z', value: -1.2 },
        { timestamp: '2026-02-22T00:00:00Z', value: 0.8 }, { timestamp: '2026-03-01T00:00:00Z', value: 2.1 },
      ],
      slope: 1.46, forecast: 3.5, forecast_method: 'exponential_smoothing', recent_change: 1.3,
    },
    {
      metric: 'scope_completion',
      points: [
        { timestamp: '2026-01-01T00:00:00Z', value: 12 }, { timestamp: '2026-01-15T00:00:00Z', value: 24 },
        { timestamp: '2026-02-01T00:00:00Z', value: 38 }, { timestamp: '2026-02-15T00:00:00Z', value: 52 },
        { timestamp: '2026-02-22T00:00:00Z', value: 61 }, { timestamp: '2026-03-01T00:00:00Z', value: 68 },
      ],
      slope: 11.2, forecast: 79, forecast_method: 'linear_regression', recent_change: 7,
    },
    {
      metric: 'risk_exposure',
      points: [
        { timestamp: '2026-01-01T00:00:00Z', value: 0.82 }, { timestamp: '2026-01-15T00:00:00Z', value: 0.75 },
        { timestamp: '2026-02-01T00:00:00Z', value: 0.68 }, { timestamp: '2026-02-15T00:00:00Z', value: 0.61 },
        { timestamp: '2026-02-22T00:00:00Z', value: 0.54 }, { timestamp: '2026-03-01T00:00:00Z', value: 0.48 },
      ],
      slope: -0.068, forecast: 0.42, forecast_method: 'linear_regression', recent_change: -0.06,
    },
  ],
  warnings: [{ type: 'budget_overrun', message: 'Budget utilisation trending above 60%', forecast: 72.5 }],
};

const documentsMock = [
  { documentId: 'doc-001', documentKey: 'charter-alpha', projectId: 'proj-alpha', name: 'Project Charter – Alpha', docType: 'Charter', classification: 'Internal', latestVersion: 3, latestStatus: 'published', createdAt: '2026-01-15T10:00:00Z', updatedAt: '2026-02-20T14:30:00Z' },
  { documentId: 'doc-002', documentKey: 'scope-alpha', projectId: 'proj-alpha', name: 'Scope Statement', docType: 'Scope', classification: 'Internal', latestVersion: 2, latestStatus: 'draft', createdAt: '2026-02-01T09:00:00Z', updatedAt: '2026-02-25T11:15:00Z' },
  { documentId: 'doc-003', documentKey: 'risk-register', projectId: 'proj-alpha', name: 'Risk Register', docType: 'Risk', classification: 'Confidential', latestVersion: 5, latestStatus: 'published', createdAt: '2026-01-20T08:00:00Z', updatedAt: '2026-02-27T16:45:00Z' },
  { documentId: 'doc-004', documentKey: 'budget-plan', projectId: 'proj-beta', name: 'Budget Plan FY26', docType: 'Budget', classification: 'Internal', latestVersion: 1, latestStatus: 'draft', createdAt: '2026-02-10T13:00:00Z', updatedAt: '2026-02-10T13:00:00Z' },
];

const lessonsMock = [
  { lessonId: 'L-001', projectId: 'proj-alpha', stageId: 'planning', stageName: 'Planning', title: 'Stakeholder alignment prevents late-stage rework', description: 'Weekly 30-minute sync with exec sponsors identified three scope conflicts before they became blockers.', tags: ['stakeholder', 'scope'], topics: ['communications', 'governance'], createdAt: '2026-02-10T10:00:00Z', updatedAt: '2026-02-20T14:30:00Z' },
  { lessonId: 'L-002', projectId: 'proj-alpha', stageId: 'execution', stageName: 'Execution', title: 'Automated regression testing saves 2 days per sprint', description: 'Investing in CI pipeline with automated test suites reduced manual QA effort significantly.', tags: ['testing', 'automation'], topics: ['quality', 'devops'], createdAt: '2026-02-15T09:00:00Z', updatedAt: '2026-02-22T11:00:00Z' },
  { lessonId: 'L-003', projectId: 'proj-beta', stageId: 'initiate', stageName: 'Initiate', title: 'Define success metrics before funding approval', description: 'Business case was approved without quantifiable KPIs; retrospectively adding them delayed the project 3 weeks.', tags: ['metrics', 'business-case'], topics: ['governance', 'planning'], createdAt: '2026-01-28T14:00:00Z', updatedAt: '2026-02-05T10:00:00Z' },
];

const agentsMock = [
  { agent_id: 'intake-agent', catalog_id: 'intake-agent', display_name: 'Intake Agent', description: 'Processes new project intake requests, validates business cases, and routes to approvers.', category: 'Portfolio', enabled: true, capabilities: ['intake.process', 'intake.validate', 'intake.route'], parameters: [{ name: 'auto_validate', display_name: 'Auto-validate', description: 'Automatically validate business case fields', param_type: 'boolean', required: false, default_value: true, current_value: true }, { name: 'routing_strategy', display_name: 'Routing Strategy', description: 'How to select approvers', param_type: 'select', required: true, default_value: 'round-robin', current_value: 'round-robin', options: ['round-robin', 'load-balanced', 'manual'] }] },
  { agent_id: 'risk-agent', catalog_id: 'risk-agent', display_name: 'Risk Assessment Agent', description: 'Identifies, scores, and monitors project risks using historical data and AI analysis.', category: 'Project', enabled: true, capabilities: ['risk.identify', 'risk.score', 'risk.monitor'], parameters: [{ name: 'risk_threshold', display_name: 'Risk Threshold', description: 'Minimum risk score to flag', param_type: 'number', required: true, default_value: 0.6, current_value: 0.6, min_value: 0, max_value: 1 }] },
  { agent_id: 'scheduling-agent', catalog_id: 'scheduling-agent', display_name: 'Scheduling Agent', description: 'Generates and optimises project schedules and detects conflicts.', category: 'Project', enabled: true, capabilities: ['schedule.generate', 'schedule.optimise'], parameters: [] },
  { agent_id: 'budget-agent', catalog_id: 'budget-agent', display_name: 'Budget Forecasting Agent', description: 'Tracks budget utilisation, forecasts spend, and alerts on variance.', category: 'Portfolio', enabled: true, capabilities: ['budget.track', 'budget.forecast'], parameters: [{ name: 'variance_pct', display_name: 'Variance Alert %', description: 'Alert when variance exceeds this %', param_type: 'number', required: true, default_value: 10, current_value: 10, min_value: 1, max_value: 50 }] },
  { agent_id: 'resource-agent', catalog_id: 'resource-agent', display_name: 'Resource Allocation Agent', description: 'Balances resource demand across projects.', category: 'Program', enabled: true, capabilities: ['resource.allocate'], parameters: [] },
  { agent_id: 'reporting-agent', catalog_id: 'reporting-agent', display_name: 'Reporting Agent', description: 'Compiles status reports and KPI dashboards.', category: 'Portfolio', enabled: false, capabilities: ['report.status'], parameters: [{ name: 'schedule', display_name: 'Report Schedule', description: 'How often to generate reports', param_type: 'select', required: true, default_value: 'weekly', current_value: 'weekly', options: ['daily', 'weekly', 'biweekly', 'monthly'] }] },
];

const workflowInstancesMock = [
  { run_id: 'run-2026-001', workflow_id: 'publish-charter', status: 'completed', current_step_id: 'notify', created_at: '2026-02-26T10:00:00Z', updated_at: '2026-02-26T11:30:00Z' },
  { run_id: 'run-2026-002', workflow_id: 'intake-review', status: 'in-progress', current_step_id: 'approval', created_at: '2026-02-27T14:00:00Z', updated_at: '2026-02-28T09:00:00Z' },
  { run_id: 'run-2026-003', workflow_id: 'risk-assessment', status: 'completed', current_step_id: 'report', created_at: '2026-02-28T08:00:00Z', updated_at: '2026-02-28T08:45:00Z' },
];

const methodologyMock = {
  methodology_id: 'hybrid',
  stages: [
    { id: 'initiate', name: 'Initiate', exit_criteria: ['Charter approved', 'Sponsor appointed', 'Funding secured'], activities: [{ id: 'define-objectives', name: 'Define Project Objectives', description: 'Document project goals and success criteria', prerequisites: [], category: 'methodology', recommended_canvas_tab: 'document' }, { id: 'stakeholder-analysis', name: 'Stakeholder Analysis', description: 'Identify and map key stakeholders', prerequisites: ['define-objectives'], category: 'methodology', recommended_canvas_tab: 'document' }] },
    { id: 'plan', name: 'Plan', exit_criteria: ['Plan approved', 'Resources allocated', 'Schedule baselined'], activities: [{ id: 'scope-planning', name: 'Scope Planning', description: 'Define detailed project scope and deliverables', prerequisites: ['define-objectives'], category: 'methodology', recommended_canvas_tab: 'tree' }, { id: 'schedule-dev', name: 'Schedule Development', description: 'Create project timeline with milestones', prerequisites: ['scope-planning'], category: 'methodology', recommended_canvas_tab: 'gantt' }] },
    { id: 'execute', name: 'Execute', exit_criteria: ['Deliverables completed', 'Quality criteria met'], activities: [{ id: 'sprint-execution', name: 'Sprint Execution', description: 'Execute work packages in iterative sprints', prerequisites: ['schedule-dev'], category: 'delivery', recommended_canvas_tab: 'board' }] },
    { id: 'close', name: 'Close', exit_criteria: ['Handover complete', 'Lessons captured'], activities: [{ id: 'lessons-capture', name: 'Lessons Learned Capture', description: 'Document project lessons for future reference', prerequisites: [], category: 'methodology', recommended_canvas_tab: 'document' }] },
  ],
  gates: [
    { id: 'gate-initiate', name: 'Initiation Gate', stage: 'initiate', criteria: [{ id: 'charter-approved', description: 'Project charter has been approved', evidence: 'Signed charter document', check: 'Verify sponsor signature' }] },
    { id: 'gate-plan', name: 'Planning Gate', stage: 'plan', criteria: [{ id: 'plan-approved', description: 'Project plan baseline approved', evidence: 'Signed plan document', check: 'Verify schedule and budget baseline' }] },
  ],
};

const demoRunMock = {
  demo_run_id: 'demo-run-20260228', started_at: '2026-02-28T08:00:00Z', total_agents_executed: 25,
  agents: [
    { agent_id: 'intake-agent', status: 'completed', duration_seconds: 2.1, artifacts: ['intake_request.json'] },
    { agent_id: 'triage-agent', status: 'completed', duration_seconds: 1.4, artifacts: ['triage_result.json'] },
    { agent_id: 'charter-agent', status: 'completed', duration_seconds: 3.8, artifacts: ['project_charter.md'] },
    { agent_id: 'risk-agent', status: 'completed', duration_seconds: 2.9, artifacts: ['risk_register.json'] },
    { agent_id: 'scheduling-agent', status: 'completed', duration_seconds: 4.2, artifacts: ['schedule.json', 'gantt.svg'] },
    { agent_id: 'budget-agent', status: 'completed', duration_seconds: 1.8, artifacts: ['budget_forecast.json'] },
    { agent_id: 'resource-agent', status: 'completed', duration_seconds: 2.5, artifacts: ['resource_plan.json'] },
    { agent_id: 'procurement-agent', status: 'completed', duration_seconds: 3.1, artifacts: ['vendor_evaluation.json'] },
    { agent_id: 'compliance-agent', status: 'completed', duration_seconds: 1.6, artifacts: ['compliance_checklist.json'] },
    { agent_id: 'quality-agent', status: 'completed', duration_seconds: 2.0, artifacts: ['quality_plan.json'] },
    { agent_id: 'stakeholder-agent', status: 'completed', duration_seconds: 1.3, artifacts: ['stakeholder_map.json'] },
    { agent_id: 'comms-agent', status: 'completed', duration_seconds: 1.1, artifacts: ['comms_plan.md'] },
    { agent_id: 'change-agent', status: 'completed', duration_seconds: 1.9, artifacts: ['change_log.json'] },
    { agent_id: 'dependency-agent', status: 'completed', duration_seconds: 2.7, artifacts: ['dependency_graph.json'] },
    { agent_id: 'estimation-agent', status: 'completed', duration_seconds: 3.3, artifacts: ['effort_estimate.json'] },
    { agent_id: 'wbs-agent', status: 'completed', duration_seconds: 2.4, artifacts: ['wbs.json'] },
    { agent_id: 'lessons-agent', status: 'completed', duration_seconds: 1.5, artifacts: ['lessons_learned.json'] },
    { agent_id: 'reporting-agent', status: 'completed', duration_seconds: 2.8, artifacts: ['status_report.md'] },
    { agent_id: 'gate-agent', status: 'completed', duration_seconds: 1.2, artifacts: ['gate_review.json'] },
    { agent_id: 'benefits-agent', status: 'completed', duration_seconds: 1.7, artifacts: ['benefits_tracker.json'] },
    { agent_id: 'integration-agent', status: 'completed', duration_seconds: 2.2, artifacts: ['integration_sync.json'] },
    { agent_id: 'document-agent', status: 'completed', duration_seconds: 3.5, artifacts: ['document_index.json'] },
    { agent_id: 'analytics-agent', status: 'completed', duration_seconds: 4.0, artifacts: ['analytics_snapshot.json'] },
    { agent_id: 'orchestrator-agent', status: 'completed', duration_seconds: 1.0, artifacts: ['orchestration_log.json'] },
    { agent_id: 'closing-agent', status: 'completed', duration_seconds: 1.4, artifacts: ['closure_report.md'] },
  ],
};

// ── Helpers ───────────────────────────────────────────────────────────

const json = (body) => ({ status: 200, contentType: 'application/json', body: JSON.stringify(body) });

/** Set up comprehensive API mocking for all pages. */
async function setupAuthRoutes(pg) {
  await pg.route('**/v1/**', (route) => {
    const u = route.request().url();
    if (process.env.DEBUG) console.log(`  [mock] ${route.request().method()} ${u}`);

    // Auth & config
    if (u.includes('/v1/session')) return route.fulfill(json(sessionMock));
    if (u.includes('/v1/api/roles')) return route.fulfill(json(rolesMock));
    // Match /v1/config but NOT /v1/config/agents, /v1/config/connectors, etc.
    if (/\/v1\/config(\?|$)/.test(u)) return route.fulfill(json({ feature_flags: {} }));

    // Workspace dashboards
    if (/\/v1\/api\/(portfolios|programs|projects)\//.test(u) && !u.includes('/demand') && !u.includes('/prioritisation') && !u.includes('/scenarios'))
      return route.fulfill(json(portfolioDashboard));
    if (u.includes('/v1/api/pipeline/'))
      return route.fulfill(json({ stages: ['Intake', 'Planning', 'Execution', 'Closing'], items: [] }));

    // Enterprise Uplift
    if (u.includes('/demand')) return route.fulfill(json(demandMock));
    if (u.includes('/prioritisation/score'))
      return route.fulfill(json({ results: demandMock.items.map((i) => ({ id: i.id, score: i.score })) }));
    if (u.includes('/scenarios/compare')) return route.fulfill(json(scenariosMock));

    // Approvals
    if (u.includes('/v1/workflows/approvals')) return route.fulfill(json(approvalsMock));

    // Intake approvals
    if (u.includes('/v1/api/intake') && u.includes('status=pending')) return route.fulfill(json(intakeApprovalsMock));
    if (u.includes('/v1/api/intake')) return route.fulfill(json(intakeApprovalsMock));

    // Analytics
    if (u.includes('/v1/api/analytics/predictive-alerts')) return route.fulfill(json([]));
    if (u.includes('/v1/api/analytics/trends')) return route.fulfill(json(analyticsTrendsMock));

    // Config pages
    if (u.includes('/v1/agents/config')) return route.fulfill(json(agentsMock));
    if (u.includes('/v1/connectors')) return route.fulfill(json([]));
    if (u.includes('/v1/orchestration/config'))
      return route.fulfill(json({ default_routing: [], last_updated_by: 'system' }));

    // Workflow monitoring
    if (u.includes('/v1/workflows/instances') && !u.includes('/timeline'))
      return route.fulfill(json(workflowInstancesMock));
    if (u.includes('/v1/workflows/instances') && u.includes('/timeline'))
      return route.fulfill(json([]));

    // Methodology editor
    if (u.includes('/v1/api/methodology/editor')) return route.fulfill(json(methodologyMock));

    // Demo run
    if (u.includes('/v1/demo/run-log')) return route.fulfill(json(demoRunMock));
    if (u.includes('/v1/api/demo/sor'))
      return route.fulfill(json({ outbox: [], applied_changes: [] }));

    // Fallback
    return route.fulfill(json({}));
  });

  // Non-/v1/ API routes
  await pg.route('**/api/knowledge/documents**', (route) => route.fulfill(json(documentsMock)));
  await pg.route('**/api/knowledge/lessons**', (route) => route.fulfill(json(lessonsMock)));
  await pg.route('**/api/portfolios', (route) => route.fulfill(json({ items: [] })));
  await pg.route('**/api/programs', (route) => route.fulfill(json({ items: [] })));
  await pg.route('**/api/projects', (route) => route.fulfill(json({ items: [] })));
  await pg.route('**/data/demo/**', (route) => route.fulfill(json(demoRunMock)));
  await pg.route('**/demo/demo_run_log.json', (route) => route.fulfill(json(demoRunMock)));

  // Block EventSource / SSE streams that would hang
  await pg.route('**/v1/workflows/stream**', (route) => route.abort());
}

/** Dismiss tour/walkthrough overlays. */
async function dismissOverlays(pg) {
  for (const label of ['Maybe later', 'Skip tour']) {
    const btn = pg.locator(`text=${label}`);
    if (await btn.isVisible({ timeout: 2000 }).catch(() => false)) {
      await btn.click();
      await pg.waitForTimeout(300);
    }
  }
}

/**
 * Navigate to a page via direct URL, dismiss overlays, wait, and screenshot.
 * For routes that collide with React Router basename detection (paths starting
 * with /app), use captureViaNav() instead.
 */
async function capturePage(context, baseUrl, pagePath, outFile) {
  const pg = await context.newPage();
  await setupAuthRoutes(pg);
  await pg.goto(`${baseUrl}${pagePath}`, { waitUntil: 'networkidle' });
  await dismissOverlays(pg);
  await pg.waitForTimeout(1200);
  await pg.screenshot({ path: outFile, fullPage: false });
  console.log(`Screenshot saved to ${outFile}`);
  await pg.close();
}

/**
 * Navigate via clicking a sidebar nav link (for routes starting with /app
 * that break basename detection when accessed directly).
 * Opens home first, then clicks the link.
 */
async function captureViaNav(context, baseUrl, navLinkHref, outFile, { expandAdmin = false } = {}) {
  const pg = await context.newPage();
  await setupAuthRoutes(pg);
  await pg.goto(baseUrl, { waitUntil: 'networkidle' });
  await dismissOverlays(pg);

  if (expandAdmin) {
    const adminToggle = pg.locator('button:has-text("Hub Admin")');
    if (await adminToggle.isVisible({ timeout: 2000 }).catch(() => false)) {
      await adminToggle.click();
      await pg.waitForTimeout(500);
    }
  }

  const link = pg.locator(`a[href="${navLinkHref}"]`).first();
  await link.click();
  await pg.waitForTimeout(2000);
  await pg.screenshot({ path: outFile, fullPage: false });
  console.log(`Screenshot saved to ${outFile}`);
  await pg.close();
}

// ── Main ─────────────────────────────────────────────────────────────

async function main() {
  // Start Vite dev server with proxy DISABLED so Playwright route
  // interceptors handle all API calls with mock responses.
  const stripProxyPlugin = {
    name: 'strip-proxy',
    configResolved(config) {
      if (config.server?.proxy) {
        for (const key of Object.keys(config.server.proxy)) {
          delete config.server.proxy[key];
        }
      }
    },
  };
  const server = await createServer({
    root: FRONTEND,
    configFile: path.join(FRONTEND, 'vite.config.ts'),
    plugins: [stripProxyPlugin],
    server: { port: 0, strictPort: false },
  });
  await server.listen();
  const address = server.httpServer.address();
  const port = typeof address === 'object' ? address.port : 5000;
  const url = `http://localhost:${port}`;
  console.log(`Vite dev server running at ${url}`);

  let browser;
  try {
    const chromiumPath =
      process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH ||
      '/root/.cache/ms-playwright/chromium-1194/chrome-linux/chrome';
    browser = await chromium.launch({ headless: true, executablePath: chromiumPath });
    const context = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });

    // ── NAVIGATE section ──
    await capturePage(context, url, '/',                   screenshotPath('web-home-three-panel-default'));
    await capturePage(context, url, '/demo-run',           screenshotPath('web-demo-run-agents-default'));
    await capturePage(context, url, '/enterprise-uplift',  screenshotPath('web-enterprise-uplift-default'));
    await capturePage(context, url, '/portfolios',         screenshotPath('web-portfolios-directory-default'));
    await capturePage(context, url, '/programs',           screenshotPath('web-programs-directory-default'));
    await capturePage(context, url, '/projects',           screenshotPath('web-projects-directory-default'));

    // ── WORK section ──
    await capturePage(context, url, '/intake/new',         screenshotPath('web-intake-form-default'));
    // /approvals starts with /app → must use nav-click approach
    await captureViaNav(context, url, '/approvals',        screenshotPath('web-approvals-pending-default'));
    await capturePage(context, url, '/intake/approvals',   screenshotPath('web-intake-approvals-default'));

    // ── INSIGHTS section ──
    await capturePage(context, url, '/analytics/dashboard', screenshotPath('web-analytics-dashboard-default'));
    await capturePage(context, url, '/knowledge/documents', screenshotPath('web-documents-repository-default'));
    await capturePage(context, url, '/knowledge/lessons',   screenshotPath('web-lessons-learned-default'));

    // ── ADMIN section (Hub Admin expanded) ──
    await capturePage(context, url, '/config/agents',       screenshotPath('web-config-agents-default'));
    await capturePage(context, url, '/config/connectors',   screenshotPath('web-config-connectors-default'));
    await capturePage(context, url, '/config/workflows',    screenshotPath('web-config-workflows-default'));
    await capturePage(context, url, '/config/prompts',      screenshotPath('web-config-prompts-default'));
    await capturePage(context, url, '/workflows/monitoring', screenshotPath('web-workflow-monitor-default'));
    // /admin/methodology requires RequireAdminRole; navigate via sidebar
    await captureViaNav(context, url, '/admin/methodology', screenshotPath('web-methodology-editor-default'), { expandAdmin: true });

    // ── Login page (unauthenticated) ──
    const loginPage = await context.newPage();
    await loginPage.route('**/v1/**', (route) =>
      route.fulfill(json({ authenticated: false })),
    );
    await loginPage.route('**/session', (route) =>
      route.fulfill(json({ authenticated: false })),
    );
    await loginPage.goto(url, { waitUntil: 'networkidle' });
    await loginPage.waitForTimeout(1500);
    await loginPage.screenshot({ path: screenshotPath('web-login-default'), fullPage: false });
    console.log(`Screenshot saved to ${screenshotPath('web-login-default')}`);
    await loginPage.close();

    console.log('\nAll screenshots captured successfully.');
  } finally {
    if (browser) await browser.close();
    await server.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
