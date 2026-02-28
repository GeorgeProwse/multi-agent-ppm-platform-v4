#!/usr/bin/env node
/**
 * Takes a screenshot of the built PPM Platform web app using Playwright.
 *
 * Usage:
 *   node ops/scripts/take-screenshot.mjs [output-path]
 *
 * Requires: built frontend in apps/web/frontend/dist (run `vite build` first)
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

// ── Mock data for all pages ──────────────────────────────────────────

const sessionMock = {
  authenticated: true,
  subject: 'demo.user',
  tenant_id: 'acme-corp',
  roles: ['ppm-admin'],
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
      { id: 'CHR-103', name: 'Data Lake Consolidation', owner: 'Maria Garcia', status: 'Draft', updated: '2026-02-28' },
    ],
    risks: [
      { id: 'RSK-01', title: 'Vendor delivery delay on infra module', severity: 'High', owner: 'James Lee' },
      { id: 'RSK-02', title: 'Key resource attrition risk', severity: 'Medium', owner: 'Sarah Chen' },
      { id: 'RSK-03', title: 'Regulatory compliance gap', severity: 'High', owner: 'Maria Garcia' },
    ],
    issues: [
      { id: 'ISS-01', title: 'CI pipeline intermittent failures', status: 'Open', owner: 'DevOps Team' },
      { id: 'ISS-02', title: 'API rate limit exceeded on staging', status: 'In Progress', owner: 'James Lee' },
    ],
    healthMetrics: [
      { label: 'Schedule', value: 'Green', status: 'success' },
      { label: 'Budget', value: 'Amber', status: 'warning' },
      { label: 'Scope', value: 'Green', status: 'success' },
      { label: 'Quality', value: 'Green', status: 'success' },
    ],
    relatedItems: [
      { id: 'PRG-01', name: 'Cloud Modernisation Program', status: 'Active', owner: 'Sarah Chen' },
      { id: 'PRG-02', name: 'Digital Customer Experience', status: 'Active', owner: 'James Lee' },
    ],
    wbs: [
      { name: 'Phase 1 – Discovery', children: ['Stakeholder interviews', 'Current state assessment', 'Requirements gathering'] },
      { name: 'Phase 2 – Design', children: ['Architecture design', 'UX wireframes', 'Data model'] },
      { name: 'Phase 3 – Build', children: ['Sprint 1', 'Sprint 2', 'Sprint 3', 'Integration testing'] },
    ],
    requirements: [
      { id: 'REQ-01', title: 'SSO integration with corporate IdP', priority: 'High', status: 'Approved' },
      { id: 'REQ-02', title: 'Multi-tenant data isolation', priority: 'High', status: 'In Progress' },
      { id: 'REQ-03', title: 'Offline mobile support', priority: 'Medium', status: 'Backlog' },
    ],
  },
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
  {
    approval_id: 'APR-2003', run_id: 'RUN-502', step_id: 'step-budget',
    status: 'pending', created_at: '2026-02-24T11:00:00Z', updated_at: '2026-02-24T11:00:00Z',
    metadata: {
      request_type: 'Budget Change Request', request_id: 'BCR-018',
      approvers: ['demo.user', 'cfo.office'], deadline: '2026-02-28',
      details: { project: 'Data Lake Consolidation', amount: '+$85,000', reason: 'Additional storage capacity' },
    },
  },
];

const agentsMock = [
  {
    agent_id: 'intake-agent', catalog_id: 'intake-agent', display_name: 'Intake Agent',
    description: 'Processes new project intake requests, validates business cases, and routes to approvers.',
    category: 'Portfolio', enabled: true, capabilities: ['intake.process', 'intake.validate', 'intake.route'],
    parameters: [
      { name: 'auto_validate', display_name: 'Auto-validate', description: 'Automatically validate business case fields', param_type: 'boolean', required: false, default_value: true, current_value: true },
      { name: 'routing_strategy', display_name: 'Routing Strategy', description: 'How to select approvers', param_type: 'select', required: true, default_value: 'round-robin', current_value: 'round-robin', options: ['round-robin', 'load-balanced', 'manual'] },
    ],
  },
  {
    agent_id: 'risk-agent', catalog_id: 'risk-agent', display_name: 'Risk Assessment Agent',
    description: 'Identifies, scores, and monitors project risks using historical data and AI analysis.',
    category: 'Project', enabled: true, capabilities: ['risk.identify', 'risk.score', 'risk.monitor'],
    parameters: [
      { name: 'risk_threshold', display_name: 'Risk Threshold', description: 'Minimum risk score to flag', param_type: 'number', required: true, default_value: 0.6, current_value: 0.6, min_value: 0, max_value: 1 },
    ],
  },
  {
    agent_id: 'scheduling-agent', catalog_id: 'scheduling-agent', display_name: 'Scheduling Agent',
    description: 'Generates and optimises project schedules, manages dependencies, and detects conflicts.',
    category: 'Project', enabled: true, capabilities: ['schedule.generate', 'schedule.optimise', 'dependency.resolve'],
    parameters: [],
  },
  {
    agent_id: 'budget-agent', catalog_id: 'budget-agent', display_name: 'Budget Forecasting Agent',
    description: 'Tracks budget utilisation, forecasts spend, and alerts on variance thresholds.',
    category: 'Portfolio', enabled: true, capabilities: ['budget.track', 'budget.forecast', 'budget.alert'],
    parameters: [
      { name: 'variance_pct', display_name: 'Variance Alert %', description: 'Alert when variance exceeds this percentage', param_type: 'number', required: true, default_value: 10, current_value: 10, min_value: 1, max_value: 50 },
    ],
  },
  {
    agent_id: 'resource-agent', catalog_id: 'resource-agent', display_name: 'Resource Allocation Agent',
    description: 'Balances resource demand across projects, identifies conflicts, and suggests reallocation.',
    category: 'Program', enabled: true, capabilities: ['resource.allocate', 'resource.balance', 'conflict.detect'],
    parameters: [],
  },
  {
    agent_id: 'reporting-agent', catalog_id: 'reporting-agent', display_name: 'Reporting Agent',
    description: 'Compiles status reports, executive summaries, and KPI dashboards from project data.',
    category: 'Portfolio', enabled: false, capabilities: ['report.status', 'report.executive', 'kpi.dashboard'],
    parameters: [
      { name: 'schedule', display_name: 'Report Schedule', description: 'How often to generate reports', param_type: 'select', required: true, default_value: 'weekly', current_value: 'weekly', options: ['daily', 'weekly', 'biweekly', 'monthly'] },
    ],
  },
];

const demoRunMock = {
  demo_run_id: 'demo-run-20260228',
  started_at: '2026-02-28T08:00:00Z',
  total_agents_executed: 25,
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

/** Set up API mocking for an authenticated page. */
async function setupAuthRoutes(pg) {
  await pg.route('**/v1/**', (route) => {
    const u = route.request().url();
    if (process.env.DEBUG) console.log(`  [mock] ${route.request().method()} ${u}`);
    if (u.includes('/v1/session')) return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(sessionMock) });
    if (u.includes('/v1/api/roles')) return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(rolesMock) });
    if (u.includes('/v1/config')) return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ feature_flags: {} }) });

    // Page-specific mocks
    if (u.includes('/v1/api/portfolios/') || u.includes('/v1/api/programs/') || u.includes('/v1/api/projects/'))
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(portfolioDashboard) });
    if (u.includes('/v1/api/pipeline/'))
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ stages: ['Intake','Planning','Execution','Closing'], items: [] }) });
    if (u.includes('/v1/workflows/approvals'))
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(approvalsMock) });
    if (u.includes('/v1/agents/config'))
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(agentsMock) });
    if (u.includes('/v1/connectors'))
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) });
    if (u.includes('/v1/orchestration/config'))
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ default_routing: [], last_updated_by: 'system' }) });
    if (u.includes('/v1/demo/run-log'))
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(demoRunMock) });
    if (u.includes('/v1/api/demo/sor'))
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ outbox: [], applied_changes: [] }) });

    return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({}) });
  });

  // Intercept demo data static file fallback
  await pg.route('**/data/demo/**', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(demoRunMock) }),
  );
  await pg.route('**/demo/demo_run_log.json', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(demoRunMock) }),
  );
}

/** Dismiss tour/walkthrough overlays. */
async function dismissOverlays(pg) {
  const maybeLater = pg.locator('text=Maybe later');
  if (await maybeLater.isVisible({ timeout: 3000 }).catch(() => false)) {
    await maybeLater.click();
    await pg.waitForTimeout(400);
  }
  const skipTour = pg.locator('text=Skip tour');
  if (await skipTour.isVisible({ timeout: 2000 }).catch(() => false)) {
    await skipTour.click();
    await pg.waitForTimeout(400);
  }
}

/** Navigate to a page, dismiss overlays, wait, and screenshot. */
async function capturePage(context, baseUrl, pagePath, outFile) {
  const pg = await context.newPage();
  pg.on('console', (msg) => {
    if (msg.type() === 'error') console.log(`  [page error] ${msg.text()}`);
  });
  pg.on('pageerror', (err) => console.log(`  [page crash] ${err.message}`));
  await setupAuthRoutes(pg);
  await pg.goto(`${baseUrl}${pagePath}`, { waitUntil: 'networkidle' });
  await dismissOverlays(pg);
  await pg.waitForTimeout(1200);
  await pg.screenshot({ path: outFile, fullPage: false });
  console.log(`Screenshot saved to ${outFile}`);
  await pg.close();
}

async function main() {
  // Start a Vite dev server with proxy DISABLED so Playwright route
  // interceptors handle all API calls with mock responses.
  const stripProxyPlugin = {
    name: 'strip-proxy',
    configResolved(config) {
      // Remove all proxy rules so /v1/*, /config/*, etc. are served as
      // SPA fallback instead of being forwarded to a backend.
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

    // 1) Home page
    await capturePage(context, url, '/', screenshotPath('web-home-three-panel-default'));

    // 2) Portfolio workspace
    await capturePage(context, url, '/portfolio/port-001', screenshotPath('web-portfolio-workspace-default'));

    // 3) Intake form
    await capturePage(context, url, '/intake/new', screenshotPath('web-intake-new-project-form-default'));

    // 4) Portfolio directory
    await capturePage(context, url, '/portfolios', screenshotPath('web-portfolios-directory-default'));

    // 5) Agent config
    await capturePage(context, url, '/config/agents', screenshotPath('web-config-agents-default'));

    // 6) Demo run (25 agents)
    await capturePage(context, url, '/demo-run', screenshotPath('web-demo-run-agents-default'));

    // 7) Login page (unauthenticated)
    const loginPage = await context.newPage();
    await loginPage.route('**/v1/**', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ authenticated: false }) }),
    );
    await loginPage.route('**/session', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ authenticated: false }) }),
    );
    await loginPage.goto(url, { waitUntil: 'networkidle' });
    await loginPage.waitForTimeout(1500);
    await loginPage.screenshot({ path: screenshotPath('web-login-default'), fullPage: false });
    console.log(`Screenshot saved to ${screenshotPath('web-login-default')}`);
    await loginPage.close();
  } finally {
    if (browser) await browser.close();
    await server.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
