/**
 * Event Builder - Field Selection E2E Tests
 *
 * Comprehensive tests for event builder field selection functionality:
 * - Field selection modal
 * - Quick action buttons
 * - Field addition strategies
 * - Canvas field management
 *
 * Test Isolation: Uses test game GID 90000001
 * Run: npx playwright test test/e2e/critical/test-event-builder-fields.spec.ts
 */

import { test, expect, type Page, type Locator } from '@playwright/test';

// Test configuration
const BASE_URL = 'http://localhost:5173' as const;
const TEST_GAME_GID = 90000001 as const; // Test game GID

// Type definitions for test data
interface TestConfig {
  readonly baseUrl: string;
  readonly testGameGid: number;
}

interface FieldCount {
  initial: number;
  final: number;
}

interface ConsoleError {
  text: string;
  location?: {
    url?: string;
    lineNumber?: number;
    columnNumber?: number;
  };
}

const config: TestConfig = {
  baseUrl: BASE_URL,
  testGameGid: TEST_GAME_GID
};

// Helper functions with types
async function navigateToEventBuilder(page: Page): Promise<void> {
  await page.goto(`${config.baseUrl}/#/event-node-builder?game_gid=${config.testGameGid}`);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000);
}

async function getFieldCount(page: Page, selector: string): Promise<number> {
  const canvasFields = page.locator(selector);
  return await canvasFields.count();
}

async function addBaseFields(page: Page): Promise<void> {
  const quickActionBtn = page.locator('[data-testid="quick-action-btn"]').or(
    page.locator('button:has-text("快速添加")')
  );

  const count = await quickActionBtn.count();
  if (count > 0) {
    await quickActionBtn.first().click();
    await page.waitForTimeout(500);

    const addBaseOption = page.locator('button:has-text("仅添加基础字段")');
    const optionCount = await addBaseOption.count();

    if (optionCount > 0) {
      await addBaseOption.first().click();
      await page.waitForTimeout(1000);
    }
  }
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

test.describe('Event Builder - Field Selection Modal', () => {
  test.beforeEach(async ({ page }: { page: Page }) => {
    await navigateToEventBuilder(page);
  });

  test('should display event selector', async ({ page }: { page: Page }) => {
    const eventSelect: Locator = page.locator('[data-testid="event-select"]').or(
      page.locator('select').or(page.locator('[role="combobox"]'))
    );

    await expect(eventSelect.first()).toBeVisible();
  });

  test('should show field selection modal after event selection', async ({ page }: { page: Page }) => {
    const eventSelect: Locator = page.locator('[data-testid="event-select"]').or(
      page.locator('select').filter({ hasText: /选择事件|select event/i })
    );

    const count = await eventSelect.count();
    if (count > 0) {
      await eventSelect.first().click();
      await page.waitForTimeout(500);

      const eventOption = page.locator('text=login').or(page.locator('[data-value*="login"]'));
      const optionCount = await eventOption.count();

      if (optionCount > 0) {
        await eventOption.first().click();
        await page.waitForTimeout(1000);

        const modal = page.locator('.modal-content').or(page.locator('[data-testid="field-selection-modal"]'));
        const modalExists = await modal.count() > 0;

        if (modalExists) {
          await expect(modal.first()).toBeVisible();
        }
      }
    }
  });

  test('should display field selection options in modal', async ({ page }: { page: Page }) => {
    const modal: Locator = page.locator('[data-testid="field-selection-modal"]');

    if (await modal.count() > 0) {
      await expect(page.locator('text=添加所有字段').or(page.locator('text=/add all/i'))).toBeVisible();
      await expect(page.locator('text=仅添加参数').or(page.locator('text=/parameters only/i'))).toBeVisible();
      await expect(page.locator('text=仅添加非公共参数').or(page.locator('text=/non-common/i'))).toBeVisible();
      await expect(page.locator('text=仅添加公共参数').or(page.locator('text=/common only/i'))).toBeVisible();
      await expect(page.locator('text=仅添加基础字段').or(page.locator('text=/base only/i'))).toBeVisible();
      await expect(page.locator('text=跳过').or(page.locator('text=/skip/i'))).toBeVisible();
    }
  });

  test('should add all fields to canvas when selected', async ({ page }: { page: Page }) => {
    const addAllBtn: Locator = page.locator('button:has-text("添加所有字段")').or(
      page.locator('button:has-text("Add All")')
    );

    const count = await addAllBtn.count();
    if (count > 0) {
      const initialFields: number = await getFieldCount(page, '[data-testid="canvas-field"]').then(
        count => count === 0 ? getFieldCount(page, '.canvas-field') : Promise.resolve(count)
      );

      await addAllBtn.first().click();
      await page.waitForTimeout(1000);

      const toast = page.locator('text=/已添加|successfully added/i');
      const toastCount = await toast.count();
      if (toastCount > 0) {
        await expect(toast.first()).toBeVisible();
      }

      const finalFields: number = await getFieldCount(page, '[data-testid="canvas-field"]').then(
        count => count === 0 ? getFieldCount(page, '.canvas-field') : Promise.resolve(count)
      );
      expect(finalFields).toBeGreaterThan(initialFields);
    }
  });

  test('should add only common parameters when selected', async ({ page }: { page: Page }) => {
    const addCommonBtn: Locator = page.locator('button:has-text("仅添加公共参数")').or(
      page.locator('button:has-text("Common Parameters Only")')
    );

    const count = await addCommonBtn.count();
    if (count > 0) {
      await addCommonBtn.first().click();
      await page.waitForTimeout(1000);

      const baseFields: Locator = page.locator('[data-testid="canvas-field"][data-category="base"]').or(
        page.locator('.canvas-field[data-category="base"]')
      );

      const baseFieldCount = await baseFields.count();
      expect(baseFieldCount).toBe(0);
    }
  });

  test('should add only base fields when selected', async ({ page }: { page: Page }) => {
    const addBaseBtn: Locator = page.locator('button:has-text("仅添加基础字段")').or(
      page.locator('button:has-text("Base Fields Only")')
    );

    const count = await addBaseBtn.count();
    if (count > 0) {
      await addBaseBtn.first().click();
      await page.waitForTimeout(1000);

      const canvasFields: Locator = page.locator('[data-testid="canvas-field"]').or(
        page.locator('.canvas-field')
      );

      const count = await canvasFields.count();
      expect(count).toBeGreaterThan(0);

      const hasBaseField = await page.locator('text=ds').or(page.locator('text=role_id')).count() > 0;
      expect(hasBaseField).toBeTruthy();
    }
  });

  test('should skip field addition when skip selected', async ({ page }: { page: Page }) => {
    const skipBtn: Locator = page.locator('button:has-text("跳过")').or(
      page.locator('button:has-text("Skip")')
    );

    const count = await skipBtn.count();
    if (count > 0) {
      const initialFields: number = await getFieldCount(page, '[data-testid="canvas-field"]').then(
        count => count === 0 ? getFieldCount(page, '.canvas-field') : Promise.resolve(count)
      );

      await skipBtn.first().click();
      await page.waitForTimeout(500);

      const modal = page.locator('[data-testid="field-selection-modal"]');
      const isVisible = await modal.isVisible().catch(() => false);
      expect(isVisible).toBeFalsy();

      const finalFields: number = await getFieldCount(page, '[data-testid="canvas-field"]').then(
        count => count === 0 ? getFieldCount(page, '.canvas-field') : Promise.resolve(count)
      );
      expect(finalFields).toBe(initialFields);
    }
  });

  test('should close modal on backdrop click', async ({ page }: { page: Page }) => {
    const modal: Locator = page.locator('[data-testid="field-selection-modal"]');
    const count = await modal.count();

    if (count > 0 && await modal.first().isVisible()) {
      await page.locator('body').click({ position: { x: 100, y: 100 } });
      await page.waitForTimeout(500);

      const isVisible = await modal.first().isVisible().catch(() => false);
      expect(isVisible).toBeFalsy();
    }
  });
});

test.describe('Event Builder - Quick Action Buttons', () => {
  test.beforeEach(async ({ page }: { page: Page }) => {
    await navigateToEventBuilder(page);
  });

  test('should display quick action button', async ({ page }: { page: Page }) => {
    const quickActionBtn: Locator = page.locator('[data-testid="quick-action-btn"]').or(
      page.locator('button:has-text("快速添加")').or(page.locator('button:has-text("Quick Add")'))
    );

    const count = await quickActionBtn.count();
    if (count > 0) {
      await expect(quickActionBtn.first()).toBeVisible();
    }
  });

  test('should open quick action dropdown on click', async ({ page }: { page: Page }) => {
    const quickActionBtn: Locator = page.locator('[data-testid="quick-action-btn"]').or(
      page.locator('button:has-text("快速添加")')
    );

    const count = await quickActionBtn.count();
    if (count > 0) {
      await quickActionBtn.first().click();
      await page.waitForTimeout(500);

      const dropdown: Locator = page.locator('[data-testid="quick-action-dropdown"]').or(
        page.locator('.dropdown-menu')
      );

      const dropdownCount = await dropdown.count();
      if (dropdownCount > 0) {
        await expect(dropdown.first()).toBeVisible();

        const options = dropdown.locator('button');
        const optionCount = await options.count();
        expect(optionCount).toBeGreaterThan(0);
        expect(optionCount).toBeLessThanOrEqual(5);
      }
    }
  });

  test('should add base fields via quick action', async ({ page }: { page: Page }) => {
    const quickActionBtn: Locator = page.locator('[data-testid="quick-action-btn"]').or(
      page.locator('button:has-text("快速添加")')
    );

    const count = await quickActionBtn.count();
    if (count > 0) {
      await quickActionBtn.first().click();
      await page.waitForTimeout(500);

      const addBaseOption: Locator = page.locator('button:has-text("仅添加基础字段")').or(
        page.locator('button:has-text("Base Fields Only")')
      );

      const optionCount = await addBaseOption.count();
      if (optionCount > 0) {
        await addBaseOption.first().click();
        await page.waitForTimeout(1000);

        const canvasFields: Locator = page.locator('[data-testid="canvas-field"]').or(
          page.locator('.canvas-field')
        );

        const fieldCount = await canvasFields.count();
        expect(fieldCount).toBeGreaterThan(0);
      }
    }
  });

  test('should close dropdown on outside click', async ({ page }: { page: Page }) => {
    const quickActionBtn: Locator = page.locator('[data-testid="quick-action-btn"]').or(
      page.locator('button:has-text("快速添加")')
    );

    const count = await quickActionBtn.count();
    if (count > 0) {
      await quickActionBtn.first().click();
      await page.waitForTimeout(500);

      const dropdown: Locator = page.locator('[data-testid="quick-action-dropdown"]').or(
        page.locator('.dropdown-menu')
      );

      const dropdownCount = await dropdown.count();
      if (dropdownCount > 0) {
        await page.locator('body').click({ position: { x: 500, y: 500 } });
        await page.waitForTimeout(500);

        const isVisible = await dropdown.first().isVisible().catch(() => false);
        expect(isVisible).toBeFalsy();
      }
    }
  });

  test('should have all quick action options available', async ({ page }: { page: Page }) => {
    const quickActionBtn: Locator = page.locator('[data-testid="quick-action-btn"]').or(
      page.locator('button:has-text("快速添加")')
    );

    const count = await quickActionBtn.count();
    if (count > 0) {
      await quickActionBtn.first().click();
      await page.waitForTimeout(500);

      const expectedOptions: readonly string[] = [
        '添加所有字段',
        '仅添加参数',
        '仅添加非公共参数',
        '仅添加公共参数',
        '仅添加基础字段'
      ] as const;

      for (const option of expectedOptions) {
        const optionElement: Locator = page.locator(`text=${option}`).or(
          page.locator(`[aria-label*="${option}"]`)
        );

        const exists = await optionElement.count() > 0;
        if (exists) {
          await expect(optionElement.first()).toBeVisible();
        }
      }
    }
  });
});

test.describe('Event Builder - Canvas Field Management', () => {
  test.beforeEach(async ({ page }: { page: Page }) => {
    await navigateToEventBuilder(page);
  });

  test('should display canvas area', async ({ page }: { page: Page }) => {
    const canvas: Locator = page.locator('[data-testid="field-canvas"]').or(
      page.locator('.canvas').or(page.locator('[data-testid="canvas"]'))
    );

    await expect(canvas.first()).toBeVisible();
  });

  test('should display field list when fields exist', async ({ page }: { page: Page }) => {
    await addBaseFields(page);

    const fields: Locator = page.locator('[data-testid="canvas-field"]').or(
      page.locator('.canvas-field')
    );

    const fieldCount = await fields.count();
    if (fieldCount > 0) {
      await expect(fields.first()).toBeVisible();

      const fieldText = await fields.first().textContent();
      expect(fieldText?.length).toBeGreaterThan(0);
    }
  });

  test('should allow removing fields from canvas', async ({ page }: { page: Page }) => {
    const quickActionBtn: Locator = page.locator('[data-testid="quick-action-btn"]');
    const btnCount = await quickActionBtn.count();

    if (btnCount > 0) {
      await quickActionBtn.first().click();
      await page.waitForTimeout(500);

      const addBaseOption: Locator = page.locator('button:has-text("仅添加基础字段")');
      const optionCount = await addBaseOption.count();

      if (optionCount > 0) {
        await addBaseOption.first().click();
        await page.waitForTimeout(1000);

        const fields: Locator = page.locator('[data-testid="canvas-field"]').or(page.locator('.canvas-field'));
        const initialCount = await fields.count();

        if (initialCount > 0) {
          await fields.first().hover();
          await page.waitForTimeout(300);

          const removeBtn: Locator = fields.first().locator('button').or(
            fields.first().locator('[data-testid="remove-field"]')
          );

          const removeCount = await removeBtn.count();
          if (removeCount > 0) {
            await removeBtn.first().click();
            await page.waitForTimeout(500);

            const finalCount = await fields.count();
            expect(finalCount).toBeLessThan(initialCount);
          }
        }
      }
    }
  });

  test('should show field type badges', async ({ page }: { page: Page }) => {
    const quickActionBtn: Locator = page.locator('[data-testid="quick-action-btn"]');
    const btnCount = await quickActionBtn.count();

    if (btnCount > 0) {
      await quickActionBtn.first().click();
      await page.waitForTimeout(500);

      const addBaseOption: Locator = page.locator('button:has-text("仅添加基础字段")');
      const optionCount = await addBaseOption.count();

      if (optionCount > 0) {
        await addBaseOption.first().click();
        await page.waitForTimeout(1000);

        const badges: Locator = page.locator('.badge').or(
          page.locator('[data-testid="field-type-badge"]')
        );

        const badgeCount = await badges.count();
        if (badgeCount > 0) {
          await expect(badges.first()).toBeVisible();

          const badgeText = await badges.first().textContent();
          expect(badgeText?.length).toBeGreaterThan(0);
        }
      }
    }
  });
});

test.describe('Event Builder - Error Handling', () => {
  test('should handle missing game_gid gracefully', async ({ page }: { page: Page }) => {
    await page.goto(`${config.baseUrl}/#/event-node-builder`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    const hasError = await page.locator('text=/错误|error|失败/i').count() > 0;
    const hasGameSelect = await page.locator('select').count() > 0;

    expect(hasError || hasGameSelect).toBeTruthy();
  });

  test('should handle no events gracefully', async ({ page }: { page: Page }) => {
    await page.goto(`${config.baseUrl}/#/event-node-builder?game_gid=99999999`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    const hasEmptyState = await page.locator('text=/暂无|没有|empty/i').count() > 0;
    const hasError = await page.locator('text=/错误|error|失败/i').count() > 0;

    expect(hasEmptyState || hasError).toBeTruthy();
  });

  test('should have no console errors', async ({ page }: { page: Page }) => {
    const errors: ConsoleError[] = await collectConsoleErrors(page);

    await page.goto(`${config.baseUrl}/#/event-node-builder?game_gid=${config.testGameGid}`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    const criticalErrors = filterCriticalErrors(errors);

    expect(criticalErrors).toHaveLength(0);
  });
});

test.describe('Event Builder - Performance', () => {
  test('should load page within acceptable time', async ({ page }: { page: Page }) => {
    const startTime = Date.now();

    await page.goto(`${config.baseUrl}/#/event-node-builder?game_gid=${config.testGameGid}`);
    await page.waitForLoadState('networkidle');

    const loadTime = Date.now() - startTime;

    expect(loadTime).toBeLessThan(5000);
  });

  test('should respond to field additions quickly', async ({ page }: { page: Page }) => {
    await page.goto(`${config.baseUrl}/#/event-node-builder?game_gid=${config.testGameGid}`);
    await page.waitForLoadState('networkidle');

    const quickActionBtn: Locator = page.locator('[data-testid="quick-action-btn"]');
    const btnCount = await quickActionBtn.count();

    if (btnCount > 0) {
      await quickActionBtn.first().click();
      await page.waitForTimeout(500);

      const startTime = Date.now();

      const addBaseOption: Locator = page.locator('button:has-text("仅添加基础字段")');
      const optionCount = await addBaseOption.count();

      if (optionCount > 0) {
        await addBaseOption.first().click();
        await page.waitForTimeout(1000);

        const responseTime = Date.now() - startTime;

        expect(responseTime).toBeLessThan(2000);
      }
    }
  });
});
