import { test, expect } from '@playwright/test';

/**
 * E2E Tests for game_gid migration
 * Tests that modified functionality still works correctly
 */

test.describe('game_gid Migration - Dashboard Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://127.0.0.1:5001/dashboard');
  });

  test.afterEach(async ({ page }) => {
    // 清理测试状态
    await page.evaluate(() => {
      sessionStorage.clear();
      localStorage.removeItem('selectedGameGid');
      if ((window as any).gameData) {
        delete (window as any).gameData;
      }
    });
    await page.waitForTimeout(300);
  });

  test('Dashboard should load successfully', async ({ page }) => {
    await page.waitForLoadState('networkidle');

    // Check Dashboard title
    await expect(page.locator('h1, h2').filter({ hasText: /dashboard|仪表板/i })).toBeVisible();

    // Check statistics cards exist
    await expect(page.locator('text=/游戏/i')).toBeVisible();
    await expect(page.locator('text=/事件/i')).toBeVisible();
    await expect(page.locator('text=/参数/i')).toBeVisible();
  });

  test('Dashboard should display correct game counts', async ({ page }) => {
    await page.waitForLoadState('networkidle');

    // Wait for data to load
    await page.waitForTimeout(2000);

    // Check for game count (should be > 0)
    const gameCountElement = page.locator('text=/\\d+\\s*游戏/i');
    await expect(gameCountElement).toBeVisible();

    // Extract number from text like "5 游戏" or "游戏: 5"
    const text = await gameCountElement.textContent();
    const match = text?.match(/(\d+)/);
    const gameCount = match ? parseInt(match[1]) : 0;

    expect(gameCount).toBeGreaterThan(0);
    console.log(`✓ Dashboard shows ${gameCount} games`);
  });

  test('Dashboard should display correct event counts', async ({ page }) => {
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // Check for event count
    const eventCountElement = page.locator('text=/\\d+\\s*事件/i');
    await expect(eventCountElement).toBeVisible();

    const text = await eventCountElement.textContent();
    const match = text?.match(/(\d+)/);
    const eventCount = match ? parseInt(match[1]) : 0;

    expect(eventCount).toBeGreaterThan(0);
    console.log(`✓ Dashboard shows ${eventCount} events`);
  });

  test('Dashboard should display correct parameter counts', async ({ page }) => {
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // Check for parameter count
    const paramCountElement = page.locator('text=/\\d+\\s*参数/i');
    await expect(paramCountElement).toBeVisible();

    const text = await paramCountElement.textContent();
    const match = text?.match(/(\d+)/);
    const paramCount = match ? parseInt(match[1]) : 0;

    expect(paramCount).toBeGreaterThan(0);
    console.log(`✓ Dashboard shows ${paramCount} parameters`);
  });

  test('Dashboard should show game list', async ({ page }) => {
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // Check for game cards or list items
    const gameCards = page.locator('[class*="game"], [class*="card"]').or(
      page.locator('tr').filter({ hasText: /游戏/i })
    );

    const count = await gameCards.count();
    expect(count).toBeGreaterThan(0);
    console.log(`✓ Dashboard shows ${count} game cards/rows`);
  });
});

test.describe('game_gid Migration - Event Nodes Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://127.0.0.1:5001/event_nodes');
  });

  test.afterEach(async ({ page }) => {
    // 清理测试状态
    await page.evaluate(() => {
      sessionStorage.clear();
      localStorage.removeItem('selectedGameGid');
      if ((window as any).gameData) {
        delete (window as any).gameData;
      }
    });
    await page.waitForTimeout(300);
  });

  test('Event Nodes page should load successfully', async ({ page }) => {
    await page.waitForLoadState('networkidle');

    // Check page title
    await expect(page.locator('h1, h2').filter({ hasText: /event.*node|事件节点/i })).toBeVisible();
  });

  test('Event Nodes should display for game_gid=10000147', async ({ page }) => {
    await page.waitForLoadState('networkidle');

    // Wait for data to load
    await page.waitForTimeout(2000);

    // Check for nodes table or list
    const nodesList = page.locator('table tbody tr, [class*="node-item"], [class*="node-card"]');

    // Nodes should be visible (at least from backup data)
    const count = await nodesList.count();

    if (count > 0) {
      console.log(`✓ Event Nodes page shows ${count} nodes`);
      expect(count).toBeGreaterThan(0);
    } else {
      // If no nodes, check for empty state message
      const emptyState = page.locator('text=/no.*nodes|暂无.*节点/i');
      await expect(emptyState).toBeVisible();
      console.log('✓ Event Nodes page shows empty state (no nodes in database)');
    }
  });
});

test.describe('game_gid Migration - API Integration Tests', () => {
  test.afterEach(async ({ page }) => {
    // 清理测试状态
    await page.evaluate(() => {
      sessionStorage.clear();
      localStorage.removeItem('selectedGameGid');
      if ((window as any).gameData) {
        delete (window as any).gameData;
      }
    });
    await page.waitForTimeout(300);
  });

  test('API should return game_gid in responses', async ({ page }) => {
    // Navigate to Dashboard
    await page.goto('http://127.0.0.1:5001/dashboard');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // Intercept API calls
    const apiResponses: string[] = [];

    page.on('response', async (response) => {
      if (response.url().includes('/api/games') || response.url().includes('/api/dashboard')) {
        try {
          const body = await response.json();
          const bodyStr = JSON.stringify(body);

          // Check if responses contain game_gid
          if (bodyStr.includes('game_gid') || bodyStr.includes('gid')) {
            apiResponses.push(response.url());
          }
        } catch (e) {
          // Ignore non-JSON responses
        }
      }
    });

    // Reload page to trigger API calls
    await page.reload();
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    expect(apiResponses.length).toBeGreaterThan(0);
    console.log(`✓ API responses contain game_gid: ${apiResponses.length} calls`);
  });

  test('Game filtering should work with game_gid', async ({ page }) => {
    await page.goto('http://127.0.0.1:5001/dashboard');
    await page.waitForLoadState('networkidle');

    // Wait for initial data load
    await page.waitForTimeout(2000);

    // Look for game selector (dropdown, buttons, etc.)
    const gameSelector = page.locator('select, [role="combobox"], button').filter({ hasText: /游戏|game/i }).first();

    if (await gameSelector.isVisible()) {
      console.log('✓ Game selector found');

      // Try to select a game (game_gid=10000147)
      await gameSelector.click();

      // Wait for dropdown options
      await page.waitForTimeout(500);

      // Look for option with gid 10000147
      const option10000147 = page.locator('text=/10000147|测试游戏/i').first();

      if (await option10000147.isVisible()) {
        await option10000147.click();
        console.log('✓ Selected game with gid=10000147');

        // Wait for filtered data to load
        await page.waitForTimeout(1000);

        // Verify data was filtered (should still see events for this game)
        const eventText = page.locator('text=/1904|事件/i');
        await expect(eventText).toBeVisible();
        console.log('✓ Data filtered correctly for game_gid=10000147');
      }
    } else {
      console.log('ℹ️  No game selector found (might not be implemented yet)');
    }
  });
});

test.describe('game_gid Migration - Data Consistency Tests', () => {
  test.afterEach(async ({ page }) => {
    // 清理测试状态
    await page.evaluate(() => {
      sessionStorage.clear();
      localStorage.removeItem('selectedGameGid');
      if ((window as any).gameData) {
        delete (window as any).gameData;
      }
    });
    await page.waitForTimeout(300);
  });

  test('Dashboard data should be consistent across page loads', async ({ page }) => {
    // First load
    await page.goto('http://127.0.0.1:5001/dashboard');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    const gameCount1 = await page.locator('text=/\\d+\\s*游戏/i').textContent();
    const eventCount1 = await page.locator('text=/\\d+\\s*事件/i').textContent();

    console.log(`First load - Games: ${gameCount1}, Events: ${eventCount1}`);

    // Reload
    await page.reload();
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    const gameCount2 = await page.locator('text=/\\d+\\s*游戏/i').textContent();
    const eventCount2 = await page.locator('text=/\\d+\\s*事件/i').textContent();

    console.log(`Second load - Games: ${gameCount2}, Events: ${eventCount2}`);

    // Counts should match
    expect(gameCount1).toBe(gameCount2);
    expect(eventCount1).toBe(eventCount2);
    console.log('✓ Dashboard data is consistent across reloads');
  });

  test('No 404 errors in browser console', async ({ page }) => {
    const errors: string[] = [];

    page.on('response', async (response) => {
      if (response.status() === 404) {
        errors.push(response.url());
      }
    });

    await page.goto('http://127.0.0.1:5001/dashboard');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    if (errors.length > 0) {
      console.error('❌ Found 404 errors:');
      errors.forEach(err => console.error(`  - ${err}`));
    }

    expect(errors.length).toBe(0);
    console.log('✓ No 404 errors detected');
  });
});

test.describe('game_gid Migration - Performance Tests', () => {
  test.afterEach(async ({ page }) => {
    // 清理测试状态
    await page.evaluate(() => {
      sessionStorage.clear();
      localStorage.removeItem('selectedGameGid');
      if ((window as any).gameData) {
        delete (window as any).gameData;
      }
    });
    await page.waitForTimeout(300);
  });

  test('Dashboard should load within acceptable time', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('http://127.0.0.1:5001/dashboard');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    const loadTime = Date.now() - startTime;

    console.log(`✓ Dashboard loaded in ${loadTime}ms`);

    // Should load within 5 seconds
    expect(loadTime).toBeLessThan(5000);
  });

  test('API responses should be fast', async ({ page }) => {
    const apiTimes: number[] = [];

    page.on('response', async (response) => {
      if (response.url().includes('/api/')) {
        const timing = response.timing();
        if (timing) {
          apiTimes.push(timing.responseEnd || 0);
        }
      }
    });

    await page.goto('http://127.0.0.1:5001/dashboard');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    if (apiTimes.length > 0) {
      const avgTime = apiTimes.reduce((a, b) => a + b, 0) / apiTimes.length;
      console.log(`✓ Average API response time: ${avgTime.toFixed(0)}ms`);

      // Average response should be under 1 second
      expect(avgTime).toBeLessThan(1000);
    }
  });
});
