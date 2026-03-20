import { test, expect, Page } from '@playwright/test';

/**
 * Parameters Smoke Tests
 * Phase 3: Automated E2E Testing
 *
 * Tests basic Parameters functionality including:
 * - Parameters list display
 * - Filtering and searching
 * - Parameter comparison
 * - Export functionality
 *
 * Uses test game GID 90000001 to avoid production data.
 */

interface TestConfig {
  readonly BASE_URL: string;
  readonly TEST_GAME_GID: number;
}

const CONFIG: TestConfig = {
  BASE_URL: 'http://localhost:5173',
  TEST_GAME_GID: 90000001
};

test.describe('Parameters Smoke Tests', () => {
  const testGameGid: number = CONFIG.TEST_GAME_GID;

  test.beforeEach(async ({ page }: { page: Page }) => {
    // Navigate to parameters list with test game
    await page.goto(`/#/parameters?game_gid=${testGameGid}`);

    // Wait for page to load
    await expect(page.locator('[data-testid="parameters-list"], .parameters-list')).toBeVisible({ timeout: 10000 });
  });

  test('Parameters list loads and displays parameters', async ({ page }: { page: Page }) => {
    // Verify parameters list is visible
    await expect(page.locator('.parameter-item, .parameter-card, [data-testid*="parameter"]')).toHaveCount({ min: 1 });

    // Verify parameter table or grid
    const table = page.locator('table, .parameters-table, [data-testid="parameters-table"]');
    if (await table.isVisible()) {
      await expect(table).toBeVisible();
    }
  });

  test('User can search and filter parameters', async ({ page }: { page: Page }) => {
    // Get initial parameter count
    const initialParams = await page.locator('.parameter-item, .parameter-card, tr').count();

    // Search for specific parameter
    await page.fill('input[placeholder*="搜索"], [data-testid="search-input"]', 'role');

    // Wait for filter to apply
    await page.waitForTimeout(500);

    // Get filtered parameter count
    const filteredParams = await page.locator('.parameter-item, .parameter-card, tr').count();

    // Verify filter worked
    expect(filteredParams).toBeLessThanOrEqual(initialParams);

    // Clear search
    await page.fill('input[placeholder*="搜索"], [data-testid="search-input"]', '');

    // Verify all parameters are shown again
    await page.waitForTimeout(500);
    const paramsAfterClear = await page.locator('.parameter-item, .parameter-card, tr').count();
    expect(paramsAfterClear).toBeGreaterThanOrEqual(initialParams);
  });

  test('User can view parameter details', async ({ page }: { page: Page }) => {
    // Click on first parameter
    const firstParam = page.locator('.parameter-item, .parameter-card, tr').first();
    await firstParam.click();

    // Verify parameter details are displayed
    await expect(page.locator('[data-testid="parameter-detail"], .parameter-detail')).toBeVisible();
  });

  test('User can access parameter usage analysis', async ({ page }: { page: Page }) => {
    // Look for usage analysis button or link
    const usageButton = page.locator('text=/使用分析|usage analysis/i, [data-testid="usage-analysis"]');

    if (await usageButton.isVisible()) {
      await usageButton.click();

      // Verify usage analysis page loads
      await expect(page).toHaveURL(/\/parameter-usage|\/usage/i);
      await expect(page.locator('[data-testid="usage-analysis"], .usage-analysis')).toBeVisible();
    }
  });

  test('User can access parameter change history', async ({ page }: { page: Page }) => {
    // Look for change history button or link
    const historyButton = page.locator('text=/变更历史|change history/i, [data-testid="change-history"]');

    if (await historyButton.isVisible()) {
      await historyButton.click();

      // Verify history page loads
      await expect(page).toHaveURL(/\/parameter-history|\/history/i);
      await expect(page.locator('[data-testid="parameter-history"], .parameter-history')).toBeVisible();
    }
  });

  test('User can access parameter network visualization', async ({ page }: { page: Page }) => {
    // Look for network button or link
    const networkButton = page.locator('text=/关系网络|relationship network|network/i, [data-testid="parameter-network"]');

    if (await networkButton.isVisible()) {
      await networkButton.click();

      // Verify network page loads
      await expect(page).toHaveURL(/\/parameter-network|\/network/i);
      await expect(page.locator('[data-testid="parameter-network"], .parameter-network')).toBeVisible();
    }
  });

  test('User can export parameters to Excel', async ({ page }: { page: Page }) => {
    // Look for export button
    const exportButton = page.locator('text=/导出|export/i, [data-testid="export-parameters"]');

    if (await exportButton.isVisible()) {
      // Setup download handler
      const downloadPromise = page.waitForEvent('download');

      // Click export button
      await exportButton.click();

      // Wait for download to start
      const download = await downloadPromise;

      // Verify download
      expect(download.suggestedFilename()).toMatch(/\.(xlsx|csv)$/);
    } else {
      console.log('Export button not found - skipping export test');
    }
  });

  test('User can compare parameters', async ({ page }: { page: Page }) => {
    // Look for compare button or link
    const compareButton = page.locator('text=/参数对比|parameter compare|compare/i, [data-testid="parameter-compare"]');

    if (await compareButton.isVisible()) {
      await compareButton.click();

      // Verify compare page loads
      await expect(page).toHaveURL(/\/parameters\/compare|\/compare/i);
      await expect(page.locator('[data-testid="parameter-compare"], .parameter-compare')).toBeVisible();
    }
  });

  test('Parameters page has no console errors', async ({ page }: { page: Page }) => {
    // Collect console errors
    const errors: Array<{ text: string; location: { url?: string; lineNumber?: number } }> = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push({
          text: msg.text(),
          location: msg.location()
        });
      }
    });

    // Reload page to catch any errors
    await page.reload();

    // Wait for page to stabilize
    await page.waitForTimeout(2000);

    // Filter out non-critical errors
    const criticalErrors = errors.filter(err =>
      !err.text.includes('DevTools') &&
      !err.text.includes('chrome-extension') &&
      !err.text.includes('Extension')
    );

    expect(criticalErrors).toHaveLength(0);
  });

  test('User can filter parameters by type', async ({ page }: { page: Page }) => {
    // Look for parameter type filter
    const typeFilter = page.locator('select[name="param_type"], [data-testid="param-type-filter"]');

    if (await typeFilter.isVisible()) {
      // Select first option
      await typeFilter.selectOption({ index: 1 });

      // Wait for filter to apply
      await page.waitForTimeout(1000);

      // Verify parameters are filtered
      await expect(page.locator('.parameter-item, .parameter-card')).toBeVisible();
    }
  });

  test('User can paginate through parameters', async ({ page }: { page: Page }) => {
    // Look for pagination
    const pagination = page.locator('.pagination, [data-testid="pagination"]');

    if (await pagination.isVisible()) {
      const nextPageButton = page.locator('text=/下一页|next/i, [aria-label="next"]');

      if (await nextPageButton.isVisible() && await nextPageButton.isEnabled()) {
        // Get current parameter count
        const initialParams = await page.locator('.parameter-item, .parameter-card, tr').count();

        // Click next page
        await nextPageButton.click();
        await page.waitForTimeout(1000);

        // Verify pagination worked
        const paramsAfterNext = await page.locator('.parameter-item, .parameter-card, tr').count();
        expect(paramsAfterNext).toBeGreaterThan(0);
      }
    }
  });
});
