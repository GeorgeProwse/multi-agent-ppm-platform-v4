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

const outputPath =
  process.argv[2] ||
  path.join(
    ROOT_DIR,
    'docs/assets/ui/screenshots',
    `web-home-three-panel-default-${new Date().toISOString().slice(0, 10).replace(/-/g, '')}.png`,
  );

async function main() {
  // Start a Vite preview server on an available port
  const server = await createServer({
    root: FRONTEND,
    configFile: path.join(FRONTEND, 'vite.config.ts'),
    server: { port: 0, strictPort: false },
    preview: { port: 0, strictPort: false },
  });
  await server.listen();
  const address = server.httpServer.address();
  const port = typeof address === 'object' ? address.port : 5000;
  const url = `http://localhost:${port}`;
  console.log(`Vite dev server running at ${url}`);

  let browser;
  try {
    // Use the installed Chromium binary (may differ from the version Playwright expects)
    const chromiumPath =
      process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH ||
      '/root/.cache/ms-playwright/chromium-1194/chrome-linux/chrome';
    browser = await chromium.launch({
      headless: true,
      executablePath: chromiumPath,
    });
    const context = await browser.newContext({
      viewport: { width: 1920, height: 1080 },
      deviceScaleFactor: 1,
    });
    const page = await context.newPage();

    // Intercept API calls that would fail without a backend
    const mockResponses = {
      session: {
        authenticated: true,
        subject: 'demo.user',
        tenant_id: 'acme-corp',
        roles: ['ppm-admin'],
      },
      'api/roles': [
        {
          id: 'ppm-admin',
          permissions: [
            'portfolio.view',
            'methodology.edit',
            'intake.approve',
            'config.manage',
            'llm.manage',
            'analytics.view',
            'audit.view',
            'roles.manage',
          ],
        },
      ],
      config: { feature_flags: {} },
    };

    await page.route('**/v1/**', (route) => {
      const url = route.request().url();
      for (const [key, body] of Object.entries(mockResponses)) {
        if (url.includes(`/v1/${key}`)) {
          return route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify(body),
          });
        }
      }
      // Fallback for any other API call
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({}),
      });
    });

    await page.goto(url, { waitUntil: 'networkidle' });

    // Dismiss walkthrough dialog if present (it overlays the tour)
    const maybeLater = page.locator('text=Maybe later');
    if (await maybeLater.isVisible({ timeout: 3000 }).catch(() => false)) {
      await maybeLater.click();
      await page.waitForTimeout(500);
    }

    // Dismiss onboarding tour if present
    const skipTour = page.locator('text=Skip tour');
    if (await skipTour.isVisible({ timeout: 2000 }).catch(() => false)) {
      await skipTour.click();
      await page.waitForTimeout(500);
    }

    // Give CSS transitions time to settle
    await page.waitForTimeout(1000);

    await page.screenshot({ path: outputPath, fullPage: false });
    console.log(`Screenshot saved to ${outputPath}`);

    // Also capture the login page
    const loginOutputPath = path.join(
      ROOT_DIR,
      'docs/assets/ui/screenshots',
      `web-login-default-${new Date().toISOString().slice(0, 10).replace(/-/g, '')}.png`,
    );
    const loginPage = await context.newPage();
    // For the login page, mock session as unauthenticated so the app redirects to /login
    await loginPage.route('**/v1/**', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ authenticated: false }),
      }),
    );
    // Also intercept the proxied /session and /login paths
    await loginPage.route('**/session', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ authenticated: false }),
      }),
    );
    await loginPage.goto(url, { waitUntil: 'networkidle' });
    await loginPage.waitForTimeout(1500);
    await loginPage.screenshot({ path: loginOutputPath, fullPage: false });
    console.log(`Screenshot saved to ${loginOutputPath}`);
  } finally {
    if (browser) await browser.close();
    await server.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
