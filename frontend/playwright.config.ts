import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright Configuration for event2table Frontend
 *
 * Base URL: http://localhost:5173 (Vite dev server)
 * Backend API: http://127.0.0.1:5001
 *
 * Test directories:
 * - test/e2e/ - End-to-end smoke tests
 * - tests/performance/ - Performance tests
 *
 * Test Projects:
 * - Desktop browsers: chromium, firefox, webkit
 * - Mobile browsers: Mobile Chrome, Mobile Safari
 * - Responsive tests: Separate project for viewport testing
 */
export default defineConfig({
  testDir: './test',

  // Run tests in parallel
  fullyParallel: true,

  // Fail the build on CI if you accidentally left test.only in your source code
  forbidOnly: !!process.env.CI,

  // Retry on CI only
  retries: process.env.CI ? 2 : 0,

  // Opt out of parallel tests on CI
  workers: process.env.CI ? 1 : undefined,

  // Reporter configuration
  reporter: [
    ['html', { outputFolder: '../test-output/playwright/report', open: 'never' }],
    ['list'],
    ['json', { outputFile: '../test-output/playwright/results/results.json' }],
  ],

  // Shared settings for all tests
  use: {
    // Base URL for tests
    baseURL: 'http://localhost:5173',

    // Collect trace when retrying the failed test
    trace: 'on-first-retry',

    // Take screenshot on failure
    screenshot: 'only-on-failure',

    // Record video on failure
    video: 'retain-on-failure',

    // Wait for network idle before considering actions done
    actionTimeout: 10000,

    // Navigation timeout - increased for Firefox compatibility
    navigationTimeout: 60000,
  },

  // Configure projects for major browsers
  projects: [
    // Desktop browsers - Chromium runs all tests
    {
      name: 'chromium',
      testMatch: '**/*.spec.ts',
      use: {
        ...devices['Desktop Chrome'],
        actionTimeout: 10000,
        navigationTimeout: 30000,
      },
    },

    // Firefox and WebKit run only smoke tests (critical path validation)
    {
      name: 'firefox',
      testMatch: '**/smoke/*.spec.ts',
      use: {
        ...devices['Desktop Firefox'],
        // Firefox needs longer timeouts
        actionTimeout: 30000,
        navigationTimeout: 90000,
      },
    },

    {
      name: 'webkit',
      testMatch: '**/smoke/*.spec.ts',
      use: {
        ...devices['Desktop Safari'],
        actionTimeout: 15000,
        navigationTimeout: 45000,
      },
    },

    // Responsive Design Tests - Desktop viewport testing only
    // PC/Desktop focused project - tests desktop and widescreen viewports
    // Mobile and tablet viewports are NOT supported (project is desktop-focused)
    {
      name: 'responsive-design',
      testMatch: '**/responsive-design.spec.ts',
      use: {
        // Use plain browser (no device emulation)
        viewport: { width: 1920, height: 1080 }, // Desktop HD
        actionTimeout: 15000,
        navigationTimeout: 45000,
      },
    },
  ],

  // Run your local dev server before starting the tests
  // Auto-start dev server if not already running
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: true, // Reuse if already running
    timeout: 120000, // 2 minutes timeout for server startup
    stdout: 'pipe', // Capture stdout for debugging
    stderr: 'pipe', // Capture stderr for debugging
  },
});
