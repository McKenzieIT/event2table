/**
 * Quick Smoke Tests - Single Browser, No Video
 *
 * Fast smoke tests to verify basic functionality
 */

import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:5173';

// Disable video and screenshots for faster execution
test.use({
  video: 'off',
  screenshot: 'off',
  actionTimeout: 5000,
});

test.describe('Quick Smoke Tests', () => {
  test('homepage loads', async ({ page }) => {
    await page.goto(BASE_URL);
    await expect(page.locator('body')).toBeVisible();
  });

  test('games page loads', async ({ page }) => {
    await page.goto(`${BASE_URL}/#/games`);
    await expect(page.locator('body')).toBeVisible();
  });

  test('events page loads', async ({ page }) => {
    await page.goto(`${BASE_URL}/#/events`);
    await expect(page.locator('body')).toBeVisible();
  });

  test('parameters page loads', async ({ page }) => {
    await page.goto(`${BASE_URL}/#/parameters`);
    await expect(page.locator('body')).toBeVisible();
  });

  test('canvas page loads', async ({ page }) => {
    await page.goto(`${BASE_URL}/#/canvas`);
    await expect(page.locator('body')).toBeVisible();
  });

  test('field builder page loads', async ({ page }) => {
    await page.goto(`${BASE_URL}/#/field-builder`);
    await expect(page.locator('body')).toBeVisible();
  });
});
