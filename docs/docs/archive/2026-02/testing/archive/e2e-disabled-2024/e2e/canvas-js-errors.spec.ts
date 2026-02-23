import { test, expect } from '@playwright/test';

/**
 * Canvas Page Test - Check for JavaScript errors
 */

test('HQL Canvas page - JavaScript error check', async ({ page }) => {
  const jsErrors: string[] = [];

  // Capture all console messages
  page.on('console', msg => {
    if (msg.type() === 'error') {
      jsErrors.push(msg.text());
    }
  });

  // Navigate to HQL Canvas page
  await page.goto('http://127.0.0.1:5001/canvas/node_canvas?game_gid=10000147');
  await page.waitForTimeout(5000);

  // Log results
  console.log('\n=== JavaScript Errors on Canvas Page ===');
  jsErrors.forEach((err, i) => {
    console.log(`Error ${i + 1}: ${err}`);
  });

  console.log(`\nTotal JS Errors: ${jsErrors.length}`);

  // This will fail if there are errors
  expect(jsErrors.length).toBe(0);
});
