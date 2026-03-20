import { test, expect } from '@playwright/test';

test.describe('Event Nodes API - Backend Integration', () => {
  test('should return JSON from /event_node_builder/api/search endpoint', async ({ page }) => {
    // Navigate to event-nodes page with game context
    await page.goto('http://localhost:5173/#/event-nodes?game_gid=10000147');

    // Wait for API call to be made
    const apiResponse = await page.waitForResponse(response =>
      response.url().includes('/event_node_builder/api/search') &&
      response.request().method() === 'GET'
    , { timeout: 5000 }).catch(() => null);

    // Verify endpoint exists and returns JSON
    expect(apiResponse).not.toBeNull();
    expect(apiResponse?.status()).toBe(200);

    const contentType = apiResponse?.headers()['content-type'];
    expect(contentType).toMatch(/application\/json/);
  });

  test('should return JSON from /event_node_builder/api/stats endpoint', async ({ page }) => {
    // Navigate to event-nodes page with game context
    await page.goto('http://localhost:5173/#/event-nodes?game_gid=10000147');

    // Wait for stats API call
    const apiResponse = await page.waitForResponse(response =>
      response.url().includes('/event_node_builder/api/stats') &&
      response.request().method() === 'GET'
    , { timeout: 5000 }).catch(() => null);

    // Verify endpoint exists and returns JSON
    expect(apiResponse).not.toBeNull();
    expect(apiResponse?.status()).toBe(200);

    const contentType = apiResponse?.headers()['content-type'];
    expect(contentType).toMatch(/application\/json/);
  });

  test('should not return HTML 404 page for API calls', async ({ page }) => {
    await page.goto('http://localhost:5173/#/event-nodes?game_gid=10000147');

    // Monitor console for JSON parse errors
    const consoleErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // Wait for page to load
    await page.waitForTimeout(2000);

    // Should not have "Unexpected token '<', "<!DOCTYPE"... is not valid JSON" error
    const jsonParseErrors = consoleErrors.filter(err =>
      err.includes('Unexpected token') && err.includes('is not valid JSON')
    );

    expect(jsonParseErrors.length).toBe(0);
  });
});
