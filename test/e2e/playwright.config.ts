import { defineConfig, devices } from '@playwright/test';

/**
 * Optimized Playwright Configuration for E2E Testing
 *
 * Key optimizations:
 * 1. Browser-specific timeouts for varying performance
 * 2. Page-specific timeout strategies
 * 3. Flexible waiting strategies
 * 4. Enhanced debugging capabilities
 *
 * Timeout Strategy:
 * - Chromium: Standard timeouts (balanced speed/reliability)
 * - Firefox: Extended timeouts (slower JS execution)
 * - WebKit: Medium timeouts (Safari variability)
 * - Mobile: Extended timeouts (network/device constraints)
 */
export default defineConfig({
  // Root test directory
  testDir: '.',

  // Run tests sequentially to avoid game context race conditions
  fullyParallel: false,

  // Fail on CI if test.only is left in code
  forbidOnly: !!process.env.CI,

  // Retry on CI only (local runs: no retry for faster feedback)
  retries: process.env.CI ? 2 : 0,

  // Single worker for stable execution
  workers: 1,

  // Global timeout for all tests (can be overridden per test)
  timeout: 60 * 1000, // 60 seconds per test

  // Reporter configuration
  reporter: [
    ['html', { outputFolder: '../playwright-report', open: 'never' }],
    ['list'],
    ['json', { outputFile: '../test-results/e2e-results.json' }],
    ['junit', { outputFile: '../test-results/junit-results.xml' }],
  ],

  // Shared settings for all tests
  use: {
    // Base URL for tests
    baseURL: 'http://127.0.0.1:5001',

    // Collect trace on first retry (for debugging failures)
    trace: 'on-first-retry',

    // Screenshot on failure
    screenshot: 'only-on-failure',

    // Video on failure
    video: 'retain-on-failure',

    // Default timeouts (can be overridden per project)
    actionTimeout: 30000, // Increased from 15000
    navigationTimeout: 60000, // Increased from 30000

    // Wait for network idle before considering actions done
    // Note: Can be overridden per-action with { waitUntil: 'domcontentloaded' }
  },

  // Test projects with browser-specific optimizations
  projects: [
    // ===== CRITICAL TESTS (P0 Priority) =====
    {
      name: 'critical',
      testMatch: '**/critical/**/*.spec.ts',
      use: {
        ...devices['Desktop Chrome'],
        // Standard timeouts for critical tests (balance speed/reliability)
        actionTimeout: 30000,
        navigationTimeout: 60000,
      },
    },

    // ===== SMOKE TESTS =====
    {
      name: 'smoke',
      testMatch: '**/smoke/**/*.spec.ts',
      use: {
        ...devices['Desktop Chrome'],
        // Shorter timeouts for smoke tests (fast feedback)
        actionTimeout: 20000,
        navigationTimeout: 40000,
      },
    },

    // ===== API CONTRACT TESTS =====
    {
      name: 'api-contract',
      testMatch: '**/api-contract/**/*.spec.ts',
      use: {
        ...devices['Desktop Chrome'],
        // Minimal timeouts for API tests (no UI rendering)
        actionTimeout: 15000,
        navigationTimeout: 30000,
      },
    },

    // ===== FIREFOX TESTS (Extended Timeouts) =====
    {
      name: 'firefox-critical',
      testMatch: '**/critical/**/*.spec.ts',
      use: {
        ...devices['Desktop Firefox'],
        // Firefox needs longer timeouts (slower JS execution)
        actionTimeout: 45000,
        navigationTimeout: 90000,
      },
    },

    // ===== WEBKIT TESTS (Medium Timeouts) =====
    {
      name: 'webkit-critical',
      testMatch: '**/critical/**/*.spec.ts',
      use: {
        ...devices['Desktop Safari'],
        // Safari variability requires medium timeouts
        actionTimeout: 35000,
        navigationTimeout: 70000,
      },
    },

    // ===== MOBILE TESTS (Extended Timeouts) =====
    {
      name: 'mobile-critical',
      testMatch: '**/critical/**/*.spec.ts',
      use: {
        ...devices['Pixel 5'],
        // Mobile devices need longer timeouts (network/device constraints)
        actionTimeout: 40000,
        navigationTimeout: 80000,
      },
    },

    // ===== ALL TESTS (Default) =====
    {
      name: 'all-e2e',
      testMatch: '**/*.spec.ts',
      testIgnore: [
        '**/node_modules/**',
        '**/dist/**',
        '**/legacy/**',
        '**/manual/**',
      ],
      use: {
        ...devices['Desktop Chrome'],
        actionTimeout: 30000,
        navigationTimeout: 60000,
      },
    },
  ],

  // ===== PAGE-SPECIFIC TIMEOUT OVERRIDES =====
  // These can be applied in tests using test.setTimeout()

  /*
   * Example usage in tests:
   *
   * test('slow page loads correctly', async ({ page }) => {
   *   // Increase timeout for this specific test
   *   test.setTimeout(90000);
   *
   *   await page.goto('/#/canvas');
   *   // ... test code
   * });
   */
});

/**
 * TIMEOUT REFERENCE GUIDE
 *
 * Standard Timeouts (Desktop Chrome):
 * - actionTimeout: 30000ms (30s) - Button clicks, form inputs, etc.
 * - navigationTimeout: 60000ms (60s) - Page navigation, routing
 *
 * Extended Timeouts (Firefox):
 * - actionTimeout: 45000ms (45s) - Slower JS engine
 * - navigationTimeout: 90000ms (90s) - Longer page loads
 *
 * Page-Specific Recommendations:
 * - Dashboard/Listing: 20-30s (lightweight)
 * - Forms/CRUD: 30-45s (moderate complexity)
 * - Canvas/HQL Builder: 60-90s (complex rendering)
 * - API Tests: 10-15s (no UI rendering)
 *
 * Wait Strategies (from wait-helpers.ts):
 * - waitForReactMount(page, 100) - Quick React mount check
 * - waitForDataLoad(page, selector, { timeout: 10000 }) - Wait for data
 * - waitForSelector(selector, { state: 'visible', timeout: 10000 }) - Wait for element
 * - waitForLoadState('domcontentloaded') - Wait for DOM (faster than 'networkidle')
 */
