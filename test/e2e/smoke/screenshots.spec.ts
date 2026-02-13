/**
 * Screenshot Tests - Capture visual state of pages
 */

import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:5173';

test.use({
  video: 'off',
  screenshot: 'only-on-failure',
});

test.describe('Page Screenshots', () => {
  test('capture homepage', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 10000 });
    await page.screenshot({ path: 'screenshots/homepage.png' });
  });

  test('capture games page', async ({ page }) => {
    await page.goto(`${BASE_URL}/#/games`, { waitUntil: 'domcontentloaded', timeout: 10000 });
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'screenshots/games.png' });
  });

  test('capture events page', async ({ page }) => {
    await page.goto(`${BASE_URL}/#/events`, { waitUntil: 'domcontentloaded', timeout: 10000 });
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'screenshots/events.png' });
  });

  test('capture parameters page', async ({ page }) => {
    await page.goto(`${BASE_URL}/#/parameters`, { waitUntil: 'domcontentloaded', timeout: 10000 });
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'screenshots/parameters.png' });
  });

  test('capture canvas page', async ({ page }) => {
    await page.goto(`${BASE_URL}/#/canvas`, { waitUntil: 'domcontentloaded', timeout: 10000 });
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'screenshots/canvas.png' });
  });

  test('capture field builder page', async ({ page }) => {
    await page.goto(`${BASE_URL}/#/field-builder`, { waitUntil: 'domcontentloaded', timeout: 10000 });
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'screenshots/field-builder.png' });
  });
});
