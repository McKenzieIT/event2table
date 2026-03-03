/**
 * Test to verify EventsList loads correctly
 */

import { test, expect } from '@playwright/test';

test('EventsList should load', async ({ page, context }) => {
  // Clear cache
  await context.clearCookies();
  await context.clearPermissions();

  // Set up console error monitoring
  const consoleErrors: string[] = [];
  const pageErrors: string[] = [];

  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });

  page.on('pageerror', error => {
    pageErrors.push(error.message);
    console.log('Page error:', error.message);
  });

  // Navigate to events list with game context
  await page.goto('/#/events?game_gid=10000147', { waitUntil: 'networkidle' });

  // Wait for React app to mount
  await page.waitForTimeout(3000);

  // Log errors
  if (consoleErrors.length > 0) {
    console.log('Console errors:', consoleErrors);
  }

  if (pageErrors.length > 0) {
    console.log('Page errors:', pageErrors);
  }

  // Check if add button exists
  const addButton = page.locator('[data-testid="add-event-button"]');
  const buttonCount = await addButton.count();
  console.log('Add event button count:', buttonCount);

  // Check page content
  const bodyText = await page.evaluate(() => document.body.innerText);
  console.log('Page text (first 500 chars):', bodyText.substring(0, 500));

  // List all elements with data-testid
  const testIds = await page.evaluate(() => {
    const elements = document.querySelectorAll('[data-testid]');
    return Array.from(elements).slice(0, 20).map(el => el.getAttribute('data-testid'));
  });
  console.log('Available data-testids:', testIds);

  // Take screenshot
  await page.screenshot({ path: 'eventslist-debug.png' });
});
