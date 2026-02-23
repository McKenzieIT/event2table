import { test, expect } from '@playwright/test';

/**
 * Console Error Check Test Suite
 *
 * This test suite visits different pages and checks for console errors.
 * Helps identify runtime errors that need to be fixed.
 */

test.describe('Console Error Checks', () => {

  test('Games List page - check for console errors', async ({ page }) => {
    const consoleErrors: string[] = [];

    // Capture console errors
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // Navigate to games list page
    await page.goto('http://127.0.0.1:5001/games');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // Log any console errors
    console.log('Games List Console Errors:', consoleErrors);

    // Expect no console errors
    expect(consoleErrors.length).toBe(0);
  });

  test('Events List page - check for console errors', async ({ page }) => {
    const consoleErrors: string[] = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // Navigate to events list page with game_gid parameter
    await page.goto('http://127.0.0.1:5001/events?game_gid=10000147');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    console.log('Events List Console Errors:', consoleErrors);
    expect(consoleErrors.length).toBe(0);
  });

  test('Parameters List page - check for console errors', async ({ page }) => {
    const consoleErrors: string[] = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // Navigate to parameters list page
    await page.goto('http://127.0.0.1:5001/parameters?game_gid=10000147');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    console.log('Parameters List Console Errors:', consoleErrors);
    expect(consoleErrors.length).toBe(0);
  });

  test('Event Node Builder page - check for console errors', async ({ page }) => {
    const consoleErrors: string[] = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // Navigate to event node builder page
    await page.goto('http://127.0.0.1:5001/canvas/event-node-builder?game_gid=10000147');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);

    console.log('Event Node Builder Console Errors:', consoleErrors);
    expect(consoleErrors.length).toBe(0);
  });

  test('Dashboard page - check for console errors', async ({ page }) => {
    const consoleErrors: string[] = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // Navigate to dashboard page
    await page.goto('http://127.0.0.1:5001/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    console.log('Dashboard Console Errors:', consoleErrors);
    expect(consoleErrors.length).toBe(0);
  });
});
