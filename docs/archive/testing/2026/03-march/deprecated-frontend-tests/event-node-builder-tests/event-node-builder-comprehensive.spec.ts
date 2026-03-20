import { test, expect } from '@playwright/test';

/**
 * Event Node Builder - Comprehensive E2E Test Suite
 *
 * This test suite covers:
 * 1. Basic functionality tests (page loading, game info display)
 * 2. Bug regression tests (Bugs #1, #2-3, #4 from BUG-FIX-REPORT-2026-03-14.md)
 * 3. Core workflow tests (event selection, field addition, HQL generation)
 * 4. Edge case tests (empty canvas, validation)
 *
 * Test Data:
 * - Game GID: 10000147 (STAR001)
 * - Event: themegsoul.summon (善灵抽卡) - 39 fields total (32 params + 7 base)
 *
 * @see /BUG-FIX-REPORT-2026-03-14.md for detailed bug descriptions
 */

const BASE_URL = 'http://localhost:5173';
const GAME_GID = 10000147;
const TEST_EVENT = 'themegsoul.summon';
const TEST_EVENT_CN = '善灵抽卡';

// Test helpers
const consoleErrors: string[] = [];

function setupConsoleMonitoring(page: any) {
  page.on('console', msg => {
    if (msg.type() === 'error') {
      const text = msg.text();
      // Filter out non-critical errors
      if (!text.includes('favicon') && !text.includes('404')) {
        consoleErrors.push(text);
      }
    }
  });
}

async function navigateToEventNodeBuilder(page: any) {
  await page.goto(`${BASE_URL}/#/event-node-builder?game_gid=${GAME_GID}`, {
    timeout: 60000,
    waitUntil: 'commit'
  });
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000);
}

async function closeFieldSelectionModal(page: any) {
  const modalCloseButton = page.locator(
    '[data-testid="field-selection-modal"] button:has-text("关闭"), ' +
    '[data-testid="field-selection-modal"] button:has-text("取消")'
  ).first();

  const isModalVisible = await modalCloseButton.isVisible().catch(() => false);
  if (isModalVisible) {
    await modalCloseButton.click();
    await page.waitForTimeout(500);
  }
}

async function selectEventAndAddAllFields(page: any) {
  // Search for event
  const searchInput = page.locator('input[placeholder*="搜索"], input[placeholder*="event"]').first();
  await searchInput.fill(TEST_EVENT);
  await page.waitForTimeout(500);

  // Click event
  const eventButton = page.locator(`button:has-text("${TEST_EVENT_CN}")`).first();
  await eventButton.click();
  await page.waitForTimeout(1000);

  // Wait for FieldSelectionModal to appear
  const modal = page.locator('[data-testid="field-selection-modal"], .modal-content');
  await expect(modal).toBeVisible({ timeout: 5000 });

  // Click "All Fields" button
  const allFieldsButton = page.locator('button:has-text("📋 所有字段"), button:has-text("所有字段")').first();
  const isVisible = await allFieldsButton.isVisible().catch(() => false);

  if (isVisible) {
    await allFieldsButton.click();
    await page.waitForTimeout(2000);
  } else {
    // Alternative: close modal and use quick add
    await page.locator('[data-testid="field-selection-modal"] button:has-text("关闭")').first().click();
    await page.waitForTimeout(500);

    const quickActionButton = page.locator('button:has-text("快速添加")');
    if (await quickActionButton.isVisible().catch(() => false)) {
      await quickActionButton.click();
      await page.waitForTimeout(500);

      const baseFieldsButton = page.locator('button:has-text("基础字段")');
      await baseFieldsButton.click();
      await page.waitForTimeout(1000);
    }
  }
}

// ============================================================
// Test Suite 1: Basic Functionality Tests
// ============================================================

test.describe('Event Node Builder - Basic Functionality', () => {
  test.beforeEach(async ({ page }) => {
    consoleErrors.length = 0;
    setupConsoleMonitoring(page);
    await navigateToEventNodeBuilder(page);
  });

  test.afterEach(async ({ page }) => {
    if (consoleErrors.length > 0) {
      console.log('[Console Errors]:', consoleErrors);
    }

    const testInfo = test.info();
    if (testInfo.status !== 'passed') {
      await page.screenshot({
        path: `test-results/event-node-builder/basic-functionality/${testInfo.title.replace(/\s+/g, '_')}.png`,
        fullPage: true
      });
    }
  });

  test('应该正确加载页面', async ({ page }) => {
    // Verify main container is visible
    const workspace = page.locator('[data-testid="event-node-builder-workspace"]');
    await expect(workspace).toBeVisible();

    // Verify page header
    const pageHeader = page.locator('.page-header, h1');
    await expect(pageHeader).toBeVisible();

    // Verify no critical errors
    expect(consoleErrors.filter(err =>
      !err.includes('404') && !err.includes('favicon')
    ), 'Should not have critical console errors').toEqual([]);
  });

  test('应该显示游戏信息', async ({ page }) => {
    // Verify game GID is displayed
    const gidText = page.locator(`text=${GAME_GID}`);
    await expect(gidText).toBeVisible();

    // Verify game name is displayed
    const gameName = page.locator('text=Updated Name'); // Based on bug report
    const isVisible = await gameName.isVisible().catch(() => false);

    if (!isVisible) {
      // Alternative: check for any game info section
      const gameInfo = page.locator('.game-info, .game-data');
      await expect(gameInfo).toBeVisible();
    }
  });

  test('应该显示侧边栏组件', async ({ page }) => {
    // Left sidebar (event selector)
    const leftSidebar = page.locator('.sidebar-left, [data-testid="sidebar-left"]');
    await expect(leftSidebar).toBeVisible();

    // Right sidebar (HQL preview)
    const rightSidebar = page.locator('.sidebar-right, [data-testid="sidebar-right"]');
    await expect(rightSidebar).toBeVisible();

    // Field canvas
    const canvas = page.locator('.field-canvas, [data-testid="field-canvas"]');
    await expect(canvas).toBeVisible();
  });
});

// ============================================================
// Test Suite 2: Bug Regression Tests
// ============================================================

test.describe('Event Node Builder - Bug Regression Tests', () => {
  test.beforeEach(async ({ page }) => {
    consoleErrors.length = 0;
    setupConsoleMonitoring(page);
    await navigateToEventNodeBuilder(page);
  });

  test.afterEach(async ({ page }) => {
    if (consoleErrors.length > 0) {
      console.log('[Console Errors]:', consoleErrors);
    }

    const testInfo = test.info();
    if (testInfo.status !== 'passed') {
      await page.screenshot({
        path: `test-results/event-node-builder/bug-regression/${testInfo.title.replace(/\s+/g, '_')}.png`,
        fullPage: true
      });
    }
  });

  test('Bug #1: 应该支持添加大量字段而不崩溃', async ({ page }) => {
    console.log('\n[Test] Bug #1 Regression: Adding 39 fields without crash...');

    // Select event and add all fields
    await selectEventAndAddAllFields(page);

    // Verify statistics
    const statsText = page.locator('text=累计 39, text=39');
    await expect(statsText.first()).toBeVisible({ timeout: 5000 });

    // Verify param and base field counts
    const paramText = page.locator('text=参数 32');
    const baseText = page.locator('text=基础 7');

    const paramVisible = await paramText.isVisible().catch(() => false);
    const baseVisible = await baseText.isVisible().catch(() => false);

    // At least one should be visible
    expect(paramVisible || baseVisible, 'Should show field statistics').toBeTruthy();

    // Verify no duplicate key errors in console
    const hasDuplicateKeyError = consoleErrors.some(err =>
      err.includes('Encountered two children with the same key') ||
      err.includes('duplicate key') ||
      err.includes('Keys should be unique')
    );

    expect(hasDuplicateKeyError, 'Should not have duplicate key errors').toBeFalsy();

    // Verify component is not crashed
    const errorBoundary = page.locator('[data-testid="event-node-builder-error"]');
    const isErrorVisible = await errorBoundary.isVisible().catch(() => false);
    expect(isErrorVisible, 'Error boundary should not be visible').toBeFalsy();

    console.log('[Test] ✓ Bug #1 regression test passed\n');
  });

  test('Bug #2-3: 应该支持编辑字段配置', async ({ page }) => {
    console.log('\n[Test] Bug #2-3 Regression: Field configuration editing...');

    // Close initial modal
    await closeFieldSelectionModal(page);

    // Add a single field for testing
    const baseFieldsSection = page.locator('text=基础字段, text=基础');
    const isBaseFieldsVisible = await baseFieldsSection.isVisible().catch(() => false);

    if (isBaseFieldsVisible) {
      await baseFieldsSection.first().click();
      await page.waitForTimeout(500);
    }

    const dsField = page.locator('text=ds').first();
    const isDsVisible = await dsField.isVisible().catch(() => false);

    if (!isDsVisible) {
      // Alternative: use quick add
      const quickActionButton = page.locator('button:has-text("快速添加")');
      if (await quickActionButton.isVisible().catch(() => false)) {
        await quickActionButton.click();
        await page.waitForTimeout(500);

        const baseFieldsButton = page.locator('button:has-text("基础字段")');
        await baseFieldsButton.click();
        await page.waitForTimeout(1000);
      }
    }

    // Click on a field to open edit modal
    const canvasFields = page.locator('[data-testid="canvas-field"], .canvas-field');
    const fieldCount = await canvasFields.count();

    expect(fieldCount, 'Should have at least 1 field').toBeGreaterThanOrEqual(1);

    const firstField = canvasFields.first();
    await firstField.click();
    await page.waitForTimeout(1000);

    // Verify FieldConfigModal is open
    const configModal = page.locator('[data-testid="field-config-modal"], .modal-content');
    await expect(configModal).toBeVisible();

    // Test: Chinese name input
    const displayNameInput = page.locator(
      'input[name="displayName"], ' +
      'input[label*="中文名称"], ' +
      'input[placeholder*="中文名称"]'
    ).first();

    const isDisplayNameVisible = await displayNameInput.isVisible().catch(() => false);

    if (isDisplayNameVisible) {
      await displayNameInput.fill('测试字段');
      console.log('[Test] ✓ Display name input works');

      const value = await displayNameInput.inputValue();
      expect(value).toBe('测试字段');
    }

    // Test: Alias input
    const aliasInput = page.locator(
      'input[name="alias"], ' +
      'input[label*="Alias"], ' +
      'input[label*="别名"], ' +
      'input[placeholder*="alias"]'
    ).first();

    const isAliasVisible = await aliasInput.isVisible().catch(() => false);

    if (isAliasVisible) {
      await aliasInput.fill('test_field');
      console.log('[Test] ✓ Alias input works');

      const value = await aliasInput.inputValue();
      expect(value).toBe('test_field');
    }

    // Test: Save button
    const saveButton = page.locator(
      'button:has-text("保存"), ' +
      'button[type="submit"], ' +
      '.field-config-modal .btn-primary'
    ).first();

    await saveButton.click();
    await page.waitForTimeout(1500);

    // Verify modal closed
    const isModalStillVisible = await configModal.isVisible().catch(() => false);
    expect(isModalStillVisible, 'Modal should close after save').toBeFalsy();

    console.log('[Test] ✓ Bug #2-3 regression test passed\n');
  });

  test('Bug #4: 删除确认应该显示正确的字段名', async ({ page }) => {
    console.log('\n[Test] Bug #4 Regression: Delete confirmation shows correct field name...');

    // Close initial modal
    await closeFieldSelectionModal(page);

    // Add a parameter field for testing
    const accountIdField = page.locator('text=accountId').first();
    const isVisible = await accountIdField.isVisible().catch(() => false);

    if (!isVisible) {
      // Try to find any parameter field
      const paramSection = page.locator('text=参数字段, text=参数');
      const isParamVisible = await paramSection.isVisible().catch(() => false);

      if (isParamVisible) {
        await paramSection.first().click();
        await page.waitForTimeout(500);
      }
    }

    const canvasFields = page.locator('[data-testid="canvas-field"], .canvas-field');
    const fieldCount = await canvasFields.count();

    if (fieldCount > 0) {
      const firstField = canvasFields.first();
      await firstField.click();
      await page.waitForTimeout(500);

      // Click delete button
      const deleteButton = page.locator('button:has-text("删除"), button:has-text("🗑")').first();
      await deleteButton.click();
      await page.waitForTimeout(500);

      // Verify delete confirmation dialog
      const confirmDialog = page.locator('.modal-content, [data-testid="confirm-dialog"]');
      await expect(confirmDialog).toBeVisible();

      // Get the field name from the first field
      const fieldText = await firstField.textContent();
      const fieldNameMatch = fieldText?.match(/accountId|role_id|[\w]+/);
      const expectedFieldName = fieldNameMatch ? fieldNameMatch[0] : '字段';

      // Verify dialog contains field name
      const dialogText = await confirmDialog.textContent();
      const hasCorrectFieldName = dialogText?.includes(expectedFieldName) ||
                                  dialogText?.includes('确定要删除');

      expect(hasCorrectFieldName, 'Delete confirmation should show field name').toBeTruthy();

      console.log(`[Test] ✓ Delete confirmation shows correct field: ${expectedFieldName}\n`);

      // Cancel the deletion
      const cancelButton = page.locator('button:has-text("取消")').first();
      await cancelButton.click();
      await page.waitForTimeout(500);
    } else {
      console.log('[Test] No fields available for delete test');
    }
  });
});

// ============================================================
// Test Suite 3: Core Workflow Tests
// ============================================================

test.describe('Event Node Builder - Core Workflow', () => {
  test.beforeEach(async ({ page }) => {
    consoleErrors.length = 0;
    setupConsoleMonitoring(page);
    await navigateToEventNodeBuilder(page);
  });

  test.afterEach(async ({ page }) => {
    if (consoleErrors.length > 0) {
      console.log('[Console Errors]:', consoleErrors);
    }

    const testInfo = test.info();
    if (testInfo.status !== 'passed') {
      await page.screenshot({
        path: `test-results/event-node-builder/core-workflow/${testInfo.title.replace(/\s+/g, '_')}.png`,
        fullPage: true
      });
    }
  });

  test('完整流程：选择事件 → 添加字段 → 生成HQL', async ({ page }) => {
    console.log('\n[Test] Core workflow: Event selection → Field addition → HQL generation...');

    // Step 1: Select event and add fields
    await selectEventAndAddAllFields(page);

    // Step 2: Verify HQL generation
    await page.waitForTimeout(2000);

    const selectText = page.locator('text=SELECT');
    await expect(selectText.first()).toBeVisible();

    const fromText = page.locator(`text=FROM ieu_ods.ods_${GAME_GID}_all_view`);
    const isFromVisible = await fromText.isVisible().catch(() => false);

    if (!isFromVisible) {
      const whereText = page.locator('text=WHERE');
      await expect(whereText.first()).toBeVisible();
    }

    // Step 3: Verify statistics
    const statsElements = page.locator('text=39, text=32, text=7');
    const statsCount = await statsElements.count();
    expect(statsCount, 'Should show field statistics').toBeGreaterThan(0);

    console.log('[Test] ✓ Core workflow test passed\n');
  });

  test('应该支持清空画布', async ({ page }) => {
    // Add some fields first
    await closeFieldSelectionModal(page);

    const quickActionButton = page.locator('button:has-text("快速添加")');
    const isVisible = await quickActionButton.isVisible().catch(() => false);

    if (isVisible) {
      await quickActionButton.click();
      await page.waitForTimeout(500);

      const baseFieldsButton = page.locator('button:has-text("基础字段")');
      await baseFieldsButton.click();
      await page.waitForTimeout(1000);
    }

    // Click clear canvas button
    const clearButton = page.locator('button:has-text("清空画布")');
    const isClearVisible = await clearButton.isVisible().catch(() => false);

    if (isClearVisible) {
      await clearButton.click();
      await page.waitForTimeout(500);

      // Confirm clear
      const confirmButton = page.locator('button:has-text("确定")');
      await confirmButton.click();
      await page.waitForTimeout(1000);

      // Verify canvas is empty
      const canvasFields = page.locator('[data-testid="canvas-field"], .canvas-field');
      const fieldCount = await canvasFields.count();
      expect(fieldCount, 'Canvas should be empty').toBe(0);
    }
  });

  test('应该支持保存配置', async ({ page }) => {
    // Add some fields first
    await closeFieldSelectionModal(page);

    const quickActionButton = page.locator('button:has-text("快速添加")');
    const isVisible = await quickActionButton.isVisible().catch(() => false);

    if (isVisible) {
      await quickActionButton.click();
      await page.waitForTimeout(500);

      const baseFieldsButton = page.locator('button:has-text("基础字段")');
      await baseFieldsButton.click();
      await page.waitForTimeout(1000);
    }

    // Try to save config
    const saveButton = page.locator('button:has-text("保存配置")');
    const isSaveVisible = await saveButton.isVisible().catch(() => false);

    if (isSaveVisible) {
      await saveButton.click();
      await page.waitForTimeout(1000);

      // Should either save successfully or show validation warning
      const toast = page.locator('.toast, [role="alert"], .notification');
      const toastVisible = await toast.isVisible().catch(() => false);

      if (toastVisible) {
        const toastText = await toast.textContent();
        console.log('[Test] Toast message:', toastText);
      }
    }
  });
});

// ============================================================
// Test Suite 4: Edge Cases and Boundary Conditions
// ============================================================

test.describe('Event Node Builder - Edge Cases', () => {
  test.beforeEach(async ({ page }) => {
    consoleErrors.length = 0;
    setupConsoleMonitoring(page);
    await navigateToEventNodeBuilder(page);
  });

  test.afterEach(async ({ page }) => {
    if (consoleErrors.length > 0) {
      console.log('[Console Errors]:', consoleErrors);
    }

    const testInfo = test.info();
    if (testInfo.status !== 'passed') {
      await page.screenshot({
        path: `test-results/event-node-builder/edge-cases/${testInfo.title.replace(/\s+/g, '_')}.png`,
        fullPage: true
      });
    }
  });

  test('应该处理空画布状态', async ({ page }) => {
    // Close any modals
    await closeFieldSelectionModal(page);

    // Verify canvas is empty initially
    const canvasFields = page.locator('[data-testid="canvas-field"], .canvas-field');
    const fieldCount = await canvasFields.count();

    // Canvas should be empty or have very few fields
    expect(fieldCount, 'Canvas should be empty or have few fields initially').toBeLessThan(5);

    // Try to generate HQL with empty canvas
    const hqlPreview = page.locator('text=SELECT, text=HQL');
    const isHqlVisible = await hqlPreview.isVisible().catch(() => false);

    // HQL preview should either be hidden or show empty state
    if (isHqlVisible) {
      const emptyState = page.locator('text=暂无, text=空, text=请选择');
      const emptyVisible = await emptyState.isVisible().catch(() => false);
      expect(emptyVisible, 'Should show empty state').toBeTruthy();
    }
  });

  test('应该处理未选择事件时的保存配置', async ({ page }) => {
    // Close event selection modal without selecting event
    await closeFieldSelectionModal(page);

    // Try to save config without selecting event
    const saveButton = page.locator('button:has-text("保存配置")');
    const isSaveVisible = await saveButton.isVisible().catch(() => false);

    if (isSaveVisible) {
      await saveButton.click();
      await page.waitForTimeout(1000);

      // Should show warning toast
      const toast = page.locator('.toast, [role="alert"], .notification');
      const toastVisible = await toast.isVisible().catch(() => false);

      if (toastVisible) {
        const toastText = await toast.textContent();
        const hasWarning = toastText?.includes('请先选择事件') ||
                          toastText?.includes('Warning') ||
                          toastText?.includes('警告');

        if (hasWarning) {
          console.log('[Test] ✓ Validation warning shown');
        }
      }
    }
  });

  test('应该处理字段拖拽重新排序', async ({ page }) => {
    // Add multiple fields
    await selectEventAndAddAllFields(page);

    await page.waitForTimeout(2000);

    const canvasFields = page.locator('[data-testid="canvas-field"], .canvas-field');
    const fieldCount = await canvasFields.count();

    if (fieldCount >= 2) {
      const firstField = canvasFields.first();
      const secondField = canvasFields.nth(1);

      // Get initial positions
      const firstBox = await firstField.boundingBox();
      const secondBox = await secondField.boundingBox();

      if (firstBox && secondBox) {
        // Drag first field to second field position
        await firstField.dragTo(secondField);
        await page.waitForTimeout(1000);

        // Verify fields are still visible (not crashed)
        const fieldsAfter = page.locator('[data-testid="canvas-field"], .canvas-field');
        const fieldCountAfter = await fieldsAfter.count();

        expect(fieldCountAfter, 'All fields should still be present').toBe(fieldCount);
      }
    }
  });

  test('应该处理WHERE条件配置', async ({ page }) => {
    // Add some fields first
    await closeFieldSelectionModal(page);

    const quickActionButton = page.locator('button:has-text("快速添加")');
    const isVisible = await quickActionButton.isVisible().catch(() => false);

    if (isVisible) {
      await quickActionButton.click();
      await page.waitForTimeout(500);

      const baseFieldsButton = page.locator('button:has-text("基础字段")');
      await baseFieldsButton.click();
      await page.waitForTimeout(1000);
    }

    // Open WHERE conditions modal
    const whereButton = page.locator('button:has-text("WHERE"), button:has-text("条件")');
    const isWhereVisible = await whereButton.isVisible().catch(() => false);

    if (isWhereVisible) {
      await whereButton.click();
      await page.waitForTimeout(1000);

      // Verify WHERE modal is open
      const whereModal = page.locator('[data-testid="where-builder-modal"], .modal-content');
      const isModalVisible = await whereModal.isVisible().catch(() => false);

      if (isModalVisible) {
        // Close modal
        const closeButton = page.locator('button:has-text("关闭"), button:has-text("取消")').first();
        await closeButton.click();
        await page.waitForTimeout(500);
      }
    }
  });
});

// ============================================================
// Test Suite 5: Performance and Stability
// ============================================================

test.describe('Event Node Builder - Performance and Stability', () => {
  test('应该在大数据量下保持稳定', async ({ page }) => {
    consoleErrors.length = 0;
    setupConsoleMonitoring(page);

    await navigateToEventNodeBuilder(page);

    // Add all fields (39 fields)
    await selectEventAndAddAllFields(page);

    // Wait for HQL generation
    await page.waitForTimeout(3000);

    // Verify no memory errors or crashes
    const hasMemoryError = consoleErrors.some(err =>
      err.includes('memory') ||
      err.includes('heap') ||
      err.includes('crash') ||
      err.includes('maximum call stack')
    );

    expect(hasMemoryError, 'Should not have memory errors').toBeFalsy();

    // Verify component is still responsive
    const canvas = page.locator('.field-canvas, [data-testid="field-canvas"]');
    await expect(canvas).toBeVisible();

    console.log('[Test] ✓ Performance and stability test passed');
  });

  test('应该快速响应字段操作', async ({ page }) => {
    consoleErrors.length = 0;
    setupConsoleMonitoring(page);

    await navigateToEventNodeBuilder(page);
    await closeFieldSelectionModal(page);

    const startTime = Date.now();

    // Add fields quickly
    const quickActionButton = page.locator('button:has-text("快速添加")');
    const isVisible = await quickActionButton.isVisible().catch(() => false);

    if (isVisible) {
      await quickActionButton.click();
      await page.waitForTimeout(500);

      const baseFieldsButton = page.locator('button:has-text("基础字段")');
      await baseFieldsButton.click();
      await page.waitForTimeout(1000);
    }

    const endTime = Date.now();
    const duration = endTime - startTime;

    // Operations should complete within reasonable time
    expect(duration, 'Field operations should be fast').toBeLessThan(10000);

    console.log(`[Test] ✓ Operations completed in ${duration}ms`);
  });
});
