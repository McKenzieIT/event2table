import { test, expect } from '@playwright/test';

/**
 * Debug 404 errors on Parameters page
 */

test('Debug Parameters List 404 errors', async ({ page }) => {
  const failedRequests: { url: string, status: number }[] = [];

  // Capture failed requests
  page.on('requestfailed', request => {
    const failure = request.failure();
    if (failure) {
      failedRequests.push({
        url: request.url(),
        status: failure.errorCode || 0
      });
    }
  });

  // Capture console errors with details
  const consoleErrors: { message: string, url?: string }[] = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push({
        message: msg.text(),
        url: msg.location().url
      });
    }
  });

  // Navigate to parameters page
  await page.goto('http://127.0.0.1:5001/analytics/parameters?game_gid=10000147');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3000);

  // Log results
  console.log('\n=== Failed Requests ===');
  failedRequests.forEach(req => {
    console.log(`URL: ${req.url}`);
    console.log(`Status: ${req.status}`);
  });

  console.log('\n=== Console Errors ===');
  consoleErrors.forEach(err => {
    console.log(`Message: ${err.message}`);
    console.log(`URL: ${err.url || 'unknown'}`);
  });

  console.log(`\nTotal Failed Requests: ${failedRequests.length}`);
  console.log(`Total Console Errors: ${consoleErrors.length}`);
});
