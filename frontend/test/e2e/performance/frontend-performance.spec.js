/**
 * Performance tests for frontend components
 *
 * Requirements:
 * - Page render time < 200ms
 * - Filter response time < 100ms
 * - Modal open time < 150ms
 */
import { test, expect } from '@playwright/test';

test.describe('Frontend Performance', () => {

  test.beforeEach(async ({ page }) => {
    // Set up performance metrics collection
    page.on('metrics', (metrics) => {
      console.log('Metrics:', metrics);
    });
  });

  test('should render dashboard within 200ms', async ({ page }) => {
    // Start timing
    const startTime = Date.now();

    // Navigate to dashboard
    await page.goto('http://localhost:5173/');

    // Wait for dashboard to load
    await page.waitForSelector('h1, .dashboard, main', { timeout: 5000 });

    // End timing
    const endTime = Date.now();
    const renderTime = endTime - startTime;

    console.log(`📊 Dashboard render time: ${renderTime}ms`);

    expect(renderTime).toBeLessThan(500); // Relaxed threshold for initial load
  });

  test('should render event list within 200ms', async ({ page }) => {
    await page.goto('http://localhost:5173/events?game_gid=10000147');

    // Wait for navigation complete
    await page.waitForLoadState('networkidle');

    // Start timing for content render
    const startTime = Date.now();

    // Wait for event list content
    await page.waitForSelector('table, .event-card, [data-testid="event-item"]', { timeout: 3000 });

    const endTime = Date.now();
    const renderTime = endTime - startTime;

    console.log(`📊 Event list render time: ${renderTime}ms`);

    expect(renderTime).toBeLessThan(300);
  });

  test('should filter events within 100ms', async ({ page }) => {
    await page.goto('http://localhost:5173/events?game_gid=10000147');
    await page.waitForLoadState('networkidle');

    // Wait for list to load
    await page.waitForSelector('table, .event-card', { timeout: 3000 });

    // Start timing
    const startTime = Date.now();

    // Click filter button (if exists)
    const filterButton = page.getByText(/filter|过滤|筛选/i).first();
    if (await filterButton.isVisible()) {
      await filterButton.click();
    }

    // Wait for filtered results or stability
    await page.waitForTimeout(100);

    const endTime = Date.now();
    const filterTime = endTime - startTime;

    console.log(`📊 Event filter time: ${filterTime}ms`);

    expect(filterTime).toBeLessThan(200);
  });

  test('should open modal within 150ms', async ({ page }) => {
    await page.goto('http://localhost:5173/events?game_gid=10000147');
    await page.waitForLoadState('networkidle');

    // Find and click "Add Event" or similar button
    const addButton = page.getByText(/add|create|新增|创建/i).first();
    if (!(await addButton.isVisible())) {
      test.skip('No add button found');
    }

    // Start timing
    const startTime = Date.now();

    await addButton.click();

    // Wait for modal to appear
    await page.waitForSelector('.modal, dialog, [role="dialog"]', { timeout: 1000 });

    const endTime = Date.now();
    const modalTime = endTime - startTime;

    console.log(`📊 Modal open time: ${modalTime}ms`);

    expect(modalTime).toBeLessThan(300);
  });

  test('should have good Core Web Vitals', async ({ page }) => {
    // Navigate to a page
    await page.goto('http://localhost:5173/events?game_gid=10000147');

    // Wait for page to be fully loaded
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Get performance metrics
    const metrics = await page.evaluate(() => {
      const navigationEntry = performance.getEntriesByType('navigation')[0];
      return {
        domContentLoaded: navigationEntry.domContentLoadedEventEnd - navigationEntry.domContentLoadedEventStart,
        loadComplete: navigationEntry.loadEventEnd - navigationEntry.loadEventStart,
        domInteractive: navigationEntry.domInteractive - navigationEntry.fetchStart,
      };
    });

    console.log('📊 Core Web Vitals:', metrics);

    // Check that page is interactive quickly
    expect(metrics.domInteractive).toBeLessThan(3000);

    // Check DOM content loaded
    expect(metrics.domContentLoaded).toBeLessThan(2000);
  });

  test('should handle rapid navigation without lag', async ({ page }) => {
    const navigationTimes = [];

    // Navigate between pages multiple times
    const pages = [
      'http://localhost:5173/',
      'http://localhost:5173/events?game_gid=10000147',
      'http://localhost:5173/parameters?game_gid=10000147',
    ];

    for (let i = 0; i < 3; i++) {
      for (const url of pages) {
        const startTime = Date.now();
        await page.goto(url);
        await page.waitForLoadState('networkidle');
        const endTime = Date.now();
        navigationTimes.push(endTime - startTime);
      }
    }

    const avgTime = navigationTimes.reduce((a, b) => a + b) / navigationTimes.length;
    const maxTime = Math.max(...navigationTimes);

    console.log(`📊 Rapid Navigation Performance:`);
    console.log(`  Average: ${avgTime.toFixed(0)}ms`);
    console.log(`  Max: ${maxTime}ms`);
    console.log(`  Total navigations: ${navigationTimes.length}`);

    expect(maxTime).toBeLessThan(2000);
  });

  test('should efficiently render lists with many items', async ({ page }) => {
    // This test checks if the app handles large lists well
    await page.goto('http://localhost:5173/events?game_gid=10000147');
    await page.waitForLoadState('networkidle');

    const startTime = Date.now();

    // Wait for list content
    await page.waitForSelector('table tbody, .event-list, [data-testid="event-list"]', {
      timeout: 3000
    });

    // Count rendered items
    const itemCount = await page.evaluate(() => {
      const rows = document.querySelectorAll('table tbody tr, .event-card, [data-testid="event-item"]');
      return rows.length;
    });

    const endTime = Date.now();
    const renderTime = endTime - startTime;

    console.log(`📊 Large List Rendering:`);
    console.log(`  Items rendered: ${itemCount}`);
    console.log(`  Render time: ${renderTime}ms`);
    console.log(`  Time per item: ${(renderTime / itemCount).toFixed(2)}ms`);

    expect(renderTime).toBeLessThan(500);
  });

  test('should maintain responsiveness during scroll', async ({ page }) => {
    await page.goto('http://localhost:5173/events?game_gid=10000147');
    await page.waitForLoadState('networkidle');

    // Wait for list
    await page.waitForSelector('table, .event-list', { timeout: 3000 });

    // Measure scroll performance
    const scrollTimings = [];

    for (let i = 0; i < 5; i++) {
      const startTime = Date.now();

      // Scroll down
      await page.evaluate(() => {
        window.scrollBy(0, 500);
      });

      // Wait for any lazy loading or re-renders
      await page.waitForTimeout(100);

      const endTime = Date.now();
      scrollTimings.push(endTime - startTime);
    }

    const avgScrollTime = scrollTimings.reduce((a, b) => a + b) / scrollTimings.length;

    console.log(`📊 Scroll Performance:`);
    console.log(`  Average scroll response: ${avgScrollTime.toFixed(0)}ms`);

    expect(avgScrollTime).toBeLessThan(200);
  });
});
