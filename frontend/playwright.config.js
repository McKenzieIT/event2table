import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright Configuration for Event2Table E2E Testing
 * Phase 3: Automated Testing Implementation
 */
export default defineConfig({
  testDir: './test/e2e',

  // Fully parallelize tests
  fullyParallel: true,

  // Fail on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,

  // Retry on CI only
  retries: process.env.CI ? 2 : 0,

  // Limit workers on CI for stability
  workers: process.env.CI ? 1 : undefined,

  // Reporter configuration
  reporter: [
    ['html', { outputFolder: 'test/e2e/playwright-report' }],
    ['json', { outputFile: 'test/e2e/results.json' }],
    ['junit', { outputFile: 'test/e2e/results.xml' }],
    ['list'] // Show test results in console
  ],

  // Shared settings for all tests
  use: {
    // Base URL for tests
    baseURL: 'http://localhost:5173',

    // Collect trace when retrying the test for better debugging
    trace: 'on-first-retry',

    // Screenshot on failure only
    screenshot: 'only-on-failure',

    // Record video on failure
    video: 'retain-on-failure',

    // Global timeout for all actions
    actionTimeout: 10000, // 10 seconds
    navigationTimeout: 30000, // 30 seconds
  },

  // Test projects
  projects: [
    {
      name: 'smoke',
      testMatch: /.*\.smoke\.spec\.js/,
      testIgnore: /.*\.(regression|critical)\.spec\.js/,
      timeout: 60000, // 1 minute per test
    },
    {
      name: 'regression',
      testMatch: /.*\.regression\.spec\.js/,
      timeout: 120000, // 2 minutes per test
    },
    {
      name: 'critical',
      testMatch: /.*\.critical\.spec\.js/,
      timeout: 120000, // 2 minutes per test
    }
  ],

  // Run your local dev server before starting the tests
  // webServer: {
  //   command: 'npm run dev',
  //   url: 'http://localhost:5173',
  //   reuseExistingServer: !process.env.CI,
  //   timeout: 120000,
  // },
});
