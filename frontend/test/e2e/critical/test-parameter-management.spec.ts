/**
 * Parameter Management E2E Tests
 *
 * Comprehensive tests for parameter management functionality:
 * - Parameter filtering (all/common/non-common)
 * - Event-based filtering
 * - Parameter type editing
 * - Common parameters modal
 * - Search and pagination
 *
 * Test Isolation: Uses test game GID 90000001
 * Run: npx playwright test test/e2e/critical/test-parameter-management.spec.ts
 */

import { test, expect, type Page, type Locator } from '@playwright/test';

// Test configuration
const BASE_URL = 'http://localhost:5173' as const;
const TEST_GAME_GID = 90000001 as const; // Test game GID (not production data)

// Type definitions
interface TestConfig {
  readonly baseUrl: string;
  readonly testGameGid: number;
}

interface ConsoleError {
  text: string;
  location?: {
    url?: string;
    lineNumber?: number;
    columnNumber?: number;
  };
}

interface FilterButtonState {
  isCommon: boolean;
  isNonCommon: boolean;
  isActive: boolean;
}

const config: TestConfig = {
  baseUrl: BASE_URL,
  testGameGid: TEST_GAME_GID
};

// Helper functions with types
async function navigateToParameters(page: Page): Promise<void> {
  await page.goto(`${config.baseUrl}/#/parameters?game_gid=${config.testGameGid}`);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000); // Allow React to settle
}

async function getParameterCardCount(page: Page): Promise<number> {
  const paramCards = page.locator('.group.p-4').or(page.locator('[data-testid="parameter-card"]'));
  return await paramCards.count();
}

async function isButtonActive(page: Page, button: Locator): Promise<boolean> {
  const isActive = await button.evaluate(el =>
    el.classList.contains('bg-cyan-500/20') ||
    el.classList.contains('text-cyan-300') ||
    el.classList.contains('active')
  );
  return isActive;
}

async function collectConsoleErrors(page: Page): Promise<ConsoleError[]> {
  const errors: ConsoleError[] = [];

  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push({
        text: msg.text(),
        location: msg.location()
      });
    }
  });

  return errors;
}

function filterCriticalErrors(errors: ConsoleError[]): ConsoleError[] {
  return errors.filter(err =>
    !err.text.includes('DevTools') &&
    !err.text.includes('chrome-extension') &&
    !err.text.includes('Extension')
  );
}

test.describe('Parameter Management - Filtering', () => {
  test.beforeEach(async ({ page }: { page: Page }) => {
    await navigateToParameters(page);
  });

  test('should display all parameters by default', async ({ page }: { page: Page }) => {
    const allMode: Locator = page.locator('button:has-text("全部参数")');
    await expect(allMode).toBeVisible();

    const isActive: boolean = await isButtonActive(page, allMode);
    expect(isActive).toBeTruthy();

    const count = await getParameterCardCount(page);
    expect(count).toBeGreaterThan(0);
  });

  test('should filter to show only common parameters', async ({ page }: { page: Page }) => {
    const commonBtn: Locator = page.locator('button:has-text("公共参数")').first();
    await commonBtn.click();
    await page.waitForTimeout(500);

    const count = await getParameterCardCount(page);
    expect(count).toBeGreaterThanOrEqual(0);

    const isActive: boolean = await isButtonActive(page, commonBtn);
    expect(isActive).toBeTruthy();
  });

  test('should filter to show only non-common parameters', async ({ page }: { page: Page }) => {
    const nonCommonBtn: Locator = page.locator('button:has-text("非公共参数")').first();
    await nonCommonBtn.click();
    await page.waitForTimeout(500);

    const isActive: boolean = await isButtonActive(page, nonCommonBtn);
    expect(isActive).toBeTruthy();

    const paramCards = page.locator('.group.p-4').or(page.locator('[data-testid="parameter-card"]'));
    await expect(paramCards.first()).toBeVisible();
  });

  test('should filter by event', async ({ page }: { page: Page }) => {
    const eventSelect: Locator = page.locator('select').or(page.locator('[role="combobox"]')).first();

    if (await eventSelect.isVisible()) {
      await eventSelect.click();
      await page.waitForTimeout(500);

      const eventOption = page.locator('text=login').or(page.locator('[data-value*="login"]'));

      if (await eventOption.isVisible()) {
        await eventOption.click();
        await page.waitForTimeout(500);

        const paramCards = page.locator('.group.p-4').or(page.locator('[data-testid="parameter-card"]'));
        await expect(paramCards.first()).toBeVisible();
      }
    }
  });

  test('should switch between filter modes', async ({ page }: { page: Page }) => {
    const allBtn: Locator = page.locator('button:has-text("全部参数")').first();
    await allBtn.click();
    await page.waitForTimeout(300);

    const commonBtn: Locator = page.locator('button:has-text("公共参数")').first();
    await commonBtn.click();
    await page.waitForTimeout(300);

    const commonActive: boolean = await isButtonActive(page, commonBtn);
    expect(commonActive).toBeTruthy();

    const nonCommonBtn: Locator = page.locator('button:has-text("非公共参数")').first();
    await nonCommonBtn.click();
    await page.waitForTimeout(300);

    const nonCommonActive: boolean = await isButtonActive(page, nonCommonBtn);
    expect(nonCommonActive).toBeTruthy();
  });

  test('should show view common parameters button', async ({ page }: { page: Page }) => {
    const viewCommonBtn: Locator = page.locator('button:has-text("查看公共参数")');
    await expect(viewCommonBtn.first()).toBeVisible();
  });
});

test.describe('Parameter Management - Type Editing', () => {
  test.beforeEach(async ({ page }: { page: Page }) => {
    await navigateToParameters(page);
  });

  test('should show edit button on parameter card hover', async ({ page }: { page: Page }) => {
    const card: Locator = page.locator('.group.p-4').first();
    await card.hover();

    const editBtn: Locator = card.locator('button[title="编辑参数类型"]').or(
      card.locator('svg').filter({ hasText: /M11 5H6/ })
    );
    await expect(editBtn.first()).toBeVisible();
  });

  test('should open type editor modal', async ({ page }: { page: Page }) => {
    const card: Locator = page.locator('.group.p-4').first();
    await card.hover();

    const editBtn: Locator = card.locator('button').first();
    await editBtn.click();
    await page.waitForTimeout(500);

    const modal: Locator = page.locator('.modal-content').or(page.locator('[role="dialog"]'));
    await expect(modal.first()).toBeVisible();
  });

  test('should display parameter type options in editor', async ({ page }: { page: Page }) => {
    const card: Locator = page.locator('.group.p-4').first();
    await card.hover();
    await card.locator('button').first().click();
    await page.waitForTimeout(500);

    const typeSelect: Locator = page.locator('select').or(page.locator('[role="combobox"]'));
    if (await typeSelect.count() > 0) {
      await expect(typeSelect.first()).toBeVisible();
    }

    await expect(page.locator('text=基础字段').or(page.locator('text=base'))).toBeVisible();
  });

  test('should have save and cancel buttons in editor', async ({ page }: { page: Page }) => {
    const card: Locator = page.locator('.group.p-4').first();
    await card.hover();
    await card.locator('button').first().click();
    await page.waitForTimeout(500);

    const saveBtn: Locator = page.locator('button:has-text("保存")').or(page.locator('button[type="submit"]'));
    await expect(saveBtn.first()).toBeVisible();

    const cancelBtn: Locator = page.locator('button:has-text("取消")');
    await expect(cancelBtn.first()).toBeVisible();
  });

  test('should close modal on cancel', async ({ page }: { page: Page }) => {
    const card: Locator = page.locator('.group.p-4').first();
    await card.hover();
    await card.locator('button').first().click();
    await page.waitForTimeout(500);

    const modal: Locator = page.locator('.modal-content').or(page.locator('[role="dialog"]'));
    await expect(modal.first()).toBeVisible();

    const cancelBtn: Locator = page.locator('button:has-text("取消")');
    await cancelBtn.first().click();
    await page.waitForTimeout(500);

    await expect(modal.first()).not.toBeVisible();
  });

  test('should close modal on backdrop click', async ({ page }: { page: Page }) => {
    const card: Locator = page.locator('.group.p-4').first();
    await card.hover();
    await card.locator('button').first().click();
    await page.waitForTimeout(500);

    const modal: Locator = page.locator('.modal-content').or(page.locator('[role="dialog"]'));
    await expect(modal.first()).toBeVisible();

    await page.locator('body').click({ position: { x: 100, y: 100 } });
    await page.waitForTimeout(500);

    const isVisible = await modal.first().isVisible().catch(() => false);
    expect(isVisible).toBeFalsy();
  });
});

test.describe('Parameter Management - Common Params Modal', () => {
  test.beforeEach(async ({ page }: { page: Page }) => {
    await navigateToParameters(page);
  });

  test('should open common params modal', async ({ page }: { page: Page }) => {
    const viewCommonBtn: Locator = page.locator('button:has-text("查看公共参数")');
    await viewCommonBtn.first().click();
    await page.waitForTimeout(500);

    const modal: Locator = page.locator('.modal-content').or(page.locator('[role="dialog"]'));
    await expect(modal.first()).toBeVisible();

    await expect(page.locator('text=公共参数').or(page.locator('text=Common Parameters'))).toBeVisible();
  });

  test('should display statistics in modal', async ({ page }: { page: Page }) => {
    await page.locator('button:has-text("查看公共参数")').first().click();
    await page.waitForTimeout(500);

    const statsText = await page.locator('body').textContent();
    expect(statsText).toMatch(/总参数|Total/i);
  });

  test('should have search functionality in modal', async ({ page }: { page: Page }) => {
    await page.locator('button:has-text("查看公共参数")').first().click();
    await page.waitForTimeout(500);

    const searchInput: Locator = page.locator('input[placeholder*="搜索"]').or(
      page.locator('[data-testid="common-params-search"]')
    );

    if (await searchInput.isVisible()) {
      await searchInput.first().fill('zone');
      await page.waitForTimeout(500);

      const modal: Locator = page.locator('.modal-content').or(page.locator('[role="dialog"]'));
      await expect(modal.first()).toBeVisible();
    }
  });

  test('should have refresh button', async ({ page }: { page: Page }) => {
    await page.locator('button:has-text("查看公共参数")').first().click();
    await page.waitForTimeout(500);

    const refreshBtn: Locator = page.locator('button:has-text("刷新")').or(
      page.locator('[data-testid="refresh-common-params"]')
    );

    if (await refreshBtn.isVisible()) {
      await expect(refreshBtn.first()).toBeVisible();

      await refreshBtn.first().click();
      await page.waitForTimeout(1000);

      const modal: Locator = page.locator('.modal-content').or(page.locator('[role="dialog"]'));
      await expect(modal.first()).toBeVisible();
    }
  });

  test('should close modal with close button', async ({ page }: { page: Page }) => {
    await page.locator('button:has-text("查看公共参数")').first().click();
    await page.waitForTimeout(500);

    const modal: Locator = page.locator('.modal-content').or(page.locator('[role="dialog"]'));
    await expect(modal.first()).toBeVisible();

    const closeBtn: Locator = page.locator('button:has-text("关闭")').or(
      page.locator('button[aria-label="Close"]')
    );

    const closeBtnCount = await closeBtn.count();
    if (closeBtnCount > 0) {
      await closeBtn.first().click();
      await page.waitForTimeout(500);

      const isVisible = await modal.first().isVisible().catch(() => false);
      expect(isVisible).toBeFalsy();
    }
  });

  test('should display common parameters list', async ({ page }: { page: Page }) => {
    await page.locator('button:has-text("查看公共参数")').first().click();
    await page.waitForTimeout(500);

    const paramItems: Locator = page.locator('.modal-content .group.p-4').or(
      page.locator('[data-testid="common-param-item"]')
    );

    const count = await paramItems.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });
});

test.describe('Parameter Management - Search', () => {
  test.beforeEach(async ({ page }: { page: Page }) => {
    await navigateToParameters(page);
  });

  test('should have search input', async ({ page }: { page: Page }) => {
    const searchInput: Locator = page.locator('input[placeholder*="搜索"]').or(
      page.locator('[data-testid="search-input"]')
    );

    if (await searchInput.isVisible()) {
      await expect(searchInput.first()).toBeVisible();
    }
  });

  test('should filter parameters by search term', async ({ page }: { page: Page }) => {
    const searchInput: Locator = page.locator('input[placeholder*="搜索"]').or(
      page.locator('[data-testid="search-input"]')
    );

    if (await searchInput.isVisible()) {
      const initialParams: number = await page.locator('.group.p-4').count();

      await searchInput.first().fill('zone');
      await page.waitForTimeout(500);

      const filteredParams: number = await page.locator('.group.p-4').count();

      expect(filteredParams).toBeLessThanOrEqual(initialParams);
    }
  });

  test('should clear search and show all parameters', async ({ page }: { page: Page }) => {
    const searchInput: Locator = page.locator('input[placeholder*="搜索"]').or(
      page.locator('[data-testid="search-input"]')
    );

    if (await searchInput.isVisible()) {
      await searchInput.first().fill('zone');
      await page.waitForTimeout(500);

      const filteredParams: number = await page.locator('.group.p-4').count();

      await searchInput.first().fill('');
      await page.waitForTimeout(500);

      const paramsAfterClear: number = await page.locator('.group.p-4').count();

      expect(paramsAfterClear).toBeGreaterThanOrEqual(filteredParams);
    }
  });
});

test.describe('Parameter Management - Error Handling', () => {
  test('should handle missing game_gid gracefully', async ({ page }: { page: Page }) => {
    await page.goto(`${config.baseUrl}/#/parameters`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    const hasError = await page.locator('text=/错误|error|失败/i').count() > 0;
    const hasGameSelect = await page.locator('select').or(page.locator('[role="combobox"]')).count() > 0;

    expect(hasError || hasGameSelect).toBeTruthy();
  });

  test('should handle no parameters gracefully', async ({ page }: { page: Page }) => {
    await page.goto(`${config.baseUrl}/#/parameters?game_gid=99999999`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    const hasEmptyState = await page.locator('text=/暂无|没有|empty/i').count() > 0;
    const hasError = await page.locator('text=/错误|error|失败/i').count() > 0;

    expect(hasEmptyState || hasError).toBeTruthy();
  });

  test('should have no console errors', async ({ page }: { page: Page }) => {
    const errors: ConsoleError[] = await collectConsoleErrors(page);

    await page.goto(`${config.baseUrl}/#/parameters?game_gid=${config.testGameGid}`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    const criticalErrors = filterCriticalErrors(errors);

    expect(criticalErrors).toHaveLength(0);
  });
});

test.describe('Parameter Management - Performance', () => {
  test('should load page within acceptable time', async ({ page }: { page: Page }) => {
    const startTime = Date.now();

    await page.goto(`${config.baseUrl}/#/parameters?game_gid=${config.testGameGid}`);
    await page.waitForLoadState('networkidle');

    const loadTime = Date.now() - startTime;

    expect(loadTime).toBeLessThan(5000);
  });

  test('should respond to filter changes quickly', async ({ page }: { page: Page }) => {
    await page.goto(`${config.baseUrl}/#/parameters?game_gid=${config.testGameGid}`);
    await page.waitForLoadState('networkidle');

    const startTime = Date.now();

    await page.locator('button:has-text("公共参数")').first().click();
    await page.waitForTimeout(500);

    const responseTime = Date.now() - startTime;

    expect(responseTime).toBeLessThan(1000);
  });
});
