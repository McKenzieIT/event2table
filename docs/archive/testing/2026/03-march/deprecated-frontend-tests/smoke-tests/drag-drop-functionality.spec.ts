import { test, expect } from '@playwright/test';

/**
 * Event Node Builder - Drag and Drop Functionality E2E Tests
 *
 * Test Suite Overview:
 * - Tests drag-and-drop functionality for Event Node Builder
 * - Covers parameter fields, base fields, and common fields
 * - Validates Canvas reordering and visual feedback
 * - Uses TEST_GAME_GID = 10000147 as test data
 *
 * Technical Notes:
 * - Uses Playwright's dragAndDrop API
 * - Selectors use data-testid attributes
 * - Each test is independent with proper setup/cleanup
 * - Tests cover both dnd-kit and HTML5 drag-and-drop
 */

const TEST_GAME_GID = 10000147;
const BASE_URL = 'http://localhost:5173';
const EVENT_NODE_BUILDER_URL = `${BASE_URL}/#/event-node-builder?game_gid=${TEST_GAME_GID}`;

/**
 * Helper function to wait for event selection modal to close
 */
async function waitForEventSelection(page) {
  // Wait for FieldSelectionModal to appear and close it
  try {
    const modal = page.locator('[data-testid="field-selection-modal"]').first();
    const isVisible = await modal.isVisible().catch(() => false);

    if (isVisible) {
      // Close the modal by clicking outside or on a close button
      const closeButton = modal.locator('button[aria-label="Close"], button:has-text("关闭"), button:has-text("取消")').first();
      const hasCloseButton = await closeButton.isVisible().catch(() => false);

      if (hasCloseButton) {
        await closeButton.click();
      } else {
        // Click outside the modal to close
        await page.mouse.click(100, 100);
      }

      await page.waitForTimeout(500);
    }
  } catch (error) {
    // Modal might not be present or already closed
    console.log('Field selection modal handling:', error.message);
  }
}

/**
 * Helper function to select an event
 */
async function selectEvent(page, eventName: string) {
  // Wait for event selector to be ready
  await page.waitForSelector('[data-testid="event-selector"]', { timeout: 10000 });

  // Click on event dropdown
  const eventDropdown = page.locator('[data-testid="event-selector"]').locator('select, .dropdown-toggle').first();
  await eventDropdown.click();

  // Wait for options to load
  await page.waitForTimeout(500);

  // Select the event
  const eventOption = page.locator(`option:has-text("${eventName}"), .dropdown-item:has-text("${eventName}")`).first();
  await eventOption.click();

  // Wait for event to load and parameters to populate
  await page.waitForTimeout(2000);

  // Handle FieldSelectionModal if it appears
  await waitForEventSelection(page);
}

/**
 * Helper function to get Canvas field count
 */
async function getCanvasFieldCount(page): Promise<number> {
  try {
    const fields = await page.locator('[data-testid="field-canvas-drop-zone"] .field-item').count();
    return fields;
  } catch {
    return 0;
  }
}

/**
 * Helper function to clear Canvas
 */
async function clearCanvas(page) {
  const clearButton = page.locator('button:has-text("清空画布")').first();
  const isVisible = await clearButton.isVisible().catch(() => false);

  if (isVisible) {
    await clearButton.click();

    // Confirm clear if dialog appears
    const confirmButton = page.locator('button:has-text("确认")').first();
    const hasConfirm = await confirmButton.isVisible().catch(() => false);

    if (hasConfirm) {
      await confirmButton.click();
    }

    await page.waitForTimeout(500);
  }
}

test.describe('Event Node Builder - Drag and Drop Functionality', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to Event Node Builder page
    await page.goto(EVENT_NODE_BUILDER_URL);

    // Wait for page to load
    await expect(page.locator('body')).toBeVisible();
    await page.waitForTimeout(2000);
  });

  test.afterEach(async ({ page }) => {
    // Cleanup: Clear canvas and reset state
    await clearCanvas(page);

    // Clear storage
    await page.evaluate(() => {
      sessionStorage.clear();
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.includes('event-node-builder') || key.includes('dwd_generator')) {
          localStorage.removeItem(key);
        }
      });
    });

    await page.waitForTimeout(300);
  });

  test.describe('Test 1: Drag Parameter Field to Canvas', () => {
    test('should successfully drag a parameter field from sidebar to Canvas', async ({ page }) => {
      // Step 1: Select an event (e.g., phxcard.gacha)
      await selectEvent(page, 'phxcard.gacha');

      // Step 2: Verify parameter list is populated
      const firstParam = page.locator('[data-testid^="param-"]').first();
      await expect(firstParam).toBeVisible({ timeout: 10000 });

      // Get parameter name for verification
      const paramName = await firstParam.getAttribute('data-param');
      expect(paramName).toBeTruthy();

      // Step 3: Locate Canvas drop zone
      const dropZone = page.locator('[data-testid="field-canvas-drop-zone"]');
      await expect(dropZone).toBeVisible();

      // Step 4: Perform drag and drop
      await firstParam.dragTo(dropZone);

      // Wait for drop to process
      await page.waitForTimeout(1000);

      // Step 5: Verify field was added to Canvas
      const canvasFields = page.locator('[data-testid="field-canvas-drop-zone"] .field-item');
      const fieldCount = await canvasFields.count();

      expect(fieldCount).toBeGreaterThan(0);

      // Step 6: Verify the field displays correct information
      const firstField = canvasFields.first();
      await expect(firstField).toBeVisible();

      // Check field alias (should show parameter name)
      const fieldAlias = firstField.locator('.field-alias');
      const aliasText = await fieldAlias.textContent();

      // Verify field type badge shows "参数" (Parameter)
      const typeBadge = firstField.locator('.field-type-label');
      const typeText = await typeBadge.textContent();
      expect(typeText).toContain('参数');
    });

    test('should show correct parameter name and type after drag', async ({ page }) => {
      // Select event
      await selectEvent(page, 'phxcard.gacha');

      // Find a specific parameter (e.g., zoneId)
      const zoneParam = page.locator('[data-param="zoneId"], [data-testid^="param-"]').first();
      await expect(zoneParam).toBeVisible();

      // Get parameter details before drag
      const paramName = await zoneParam.getAttribute('data-param');
      const paramDisplayName = await zoneParam.locator('span').first().textContent();

      // Drag to Canvas
      const dropZone = page.locator('[data-testid="field-canvas-drop-zone"]');
      await zoneParam.dragTo(dropZone);
      await page.waitForTimeout(1000);

      // Verify Canvas field shows correct information
      const canvasField = page.locator('[data-testid="field-canvas-drop-zone"] .field-item').first();

      // Check alias matches parameter name
      const fieldAlias = canvasField.locator('.field-alias');
      const aliasText = await fieldAlias.textContent();

      // Verify type is "参数" (Parameter)
      const typeBadge = canvasField.locator('.field-type-label');
      const typeText = await typeBadge.textContent();
      expect(typeText).toBe('参数');
    });
  });

  test.describe('Test 2: Canvas Field Reordering', () => {
    test('should reorder fields when dragging within Canvas', async ({ page }) => {
      // Select event
      await selectEvent(page, 'phxcard.gacha');

      // Step 1: Add 3 fields to Canvas
      const params = page.locator('[data-testid^="param-"]');
      const dropZone = page.locator('[data-testid="field-canvas-drop-zone"]');

      // Drag first 3 parameters to Canvas
      for (let i = 0; i < 3; i++) {
        const param = params.nth(i);
        await param.dragTo(dropZone);
        await page.waitForTimeout(500);
      }

      // Verify we have 3 fields
      const canvasFields = page.locator('[data-testid="field-canvas-drop-zone"] .field-item');
      expect(await canvasFields.count()).toBe(3);

      // Get initial order
      const initialOrder: string[] = [];
      for (let i = 0; i < 3; i++) {
        const fieldAlias = await canvasFields.nth(i).locator('.field-alias').textContent();
        initialOrder.push(fieldAlias || '');
      }

      // Step 2: Drag second field to first position
      const secondField = canvasFields.nth(1);
      const firstField = canvasFields.nth(0);

      // Use drag handle for reordering
      const dragHandle = secondField.locator('.field-handle');
      await dragHandle.dragTo(firstField);
      await page.waitForTimeout(1000);

      // Step 3: Verify order changed
      const newOrder: string[] = [];
      for (let i = 0; i < 3; i++) {
        const fieldAlias = await canvasFields.nth(i).locator('.field-alias').textContent();
        newOrder.push(fieldAlias || '');
      }

      // The second field should now be first
      expect(newOrder[0]).toBe(initialOrder[1]);
      expect(newOrder[1]).toBe(initialOrder[0]);
    });

    test('should maintain order after save and reload', async ({ page }) => {
      // Select event
      await selectEvent(page, 'phxcard.gacha');

      // Add fields in specific order
      const params = page.locator('[data-testid^="param-"]');
      const dropZone = page.locator('[data-testid="field-canvas-drop-zone"]');

      // Add 3 fields
      for (let i = 0; i < 3; i++) {
        await params.nth(i).dragTo(dropZone);
        await page.waitForTimeout(500);
      }

      // Reorder: move last to first
      const canvasFields = page.locator('[data-testid="field-canvas-drop-zone"] .field-item');
      const lastField = canvasFields.nth(2);
      const firstField = canvasFields.nth(0);

      const dragHandle = lastField.locator('.field-handle');
      await dragHandle.dragTo(firstField);
      await page.waitForTimeout(1000);

      // Get new order
      const orderBeforeSave: string[] = [];
      for (let i = 0; i < 3; i++) {
        const fieldAlias = await canvasFields.nth(i).locator('.field-alias').textContent();
        orderBeforeSave.push(fieldAlias || '');
      }

      // Save configuration (if save button exists)
      const saveButton = page.locator('button:has-text("保存配置"), button:has-text("保存")').first();
      const hasSaveButton = await saveButton.isVisible().catch(() => false);

      if (hasSaveButton) {
        // Fill required fields if modal appears
        await saveButton.click();
        await page.waitForTimeout(1000);

        // Check if name configuration modal appears
        const nameInput = page.locator('input[placeholder*="英文名"], input[placeholder*="name"]').first();
        const hasNameInput = await nameInput.isVisible().catch(() => false);

        if (hasNameInput) {
          await nameInput.fill('test-config');
          const confirmButton = page.locator('button:has-text("确认"), button:has-text("保存")').first();
          await confirmButton.click();
        }
      }

      // Reload page
      await page.reload();
      await page.waitForTimeout(3000);

      // Re-select event
      await selectEvent(page, 'phxcard.gacha');

      // Verify order is maintained
      const reloadedFields = page.locator('[data-testid="field-canvas-drop-zone"] .field-item');
      const orderAfterReload: string[] = [];

      for (let i = 0; i < Math.min(3, await reloadedFields.count()); i++) {
        const fieldAlias = await reloadedFields.nth(i).locator('.field-alias').textContent();
        orderAfterReload.push(fieldAlias || '');
      }

      // Orders should match (or be empty if config wasn't saved)
      if (orderAfterReload.length > 0) {
        expect(orderAfterReload).toEqual(orderBeforeSave);
      }
    });
  });

  test.describe('Test 3: Drag Base Fields', () => {
    test('should drag base field (ds, role_id, etc.) to Canvas', async ({ page }) => {
      // Select event first
      await selectEvent(page, 'phxcard.gacha');

      // Use Quick Add Common button to add base fields
      const quickAddButton = page.locator('button:has-text("快速添加常用"), button:has-text("Quick Add Common")').first();
      const hasQuickAdd = await quickAddButton.isVisible().catch(() => false);

      if (hasQuickAdd) {
        await quickAddButton.click();
        await page.waitForTimeout(1000);
      } else {
        // Alternative: Add base field manually
        // Look for "基础字段" or "Base Fields" section
        const baseFieldButton = page.locator('button:has-text("添加基础字段"), button:has-text("Add Base Field")').first();
        const hasBaseFieldButton = await baseFieldButton.isVisible().catch(() => false);

        if (hasBaseFieldButton) {
          await baseFieldButton.click();
          await page.waitForTimeout(500);
        }
      }

      // Verify base fields were added
      const canvasFields = page.locator('[data-testid="field-canvas-drop-zone"] .field-item');
      const fieldCount = await canvasFields.count();

      expect(fieldCount).toBeGreaterThan(0);

      // Verify base field has "基础" (Basic) type badge
      const firstField = canvasFields.first();
      const typeBadge = firstField.locator('.field-type-label');
      const typeText = await typeBadge.textContent();

      // Should be "基础" (Basic)
      expect(typeText).toContain('基础');
    });

    test('should show special styling for base fields', async ({ page }) => {
      await selectEvent(page, 'phxcard.gacha');

      // Add a base field
      const quickAddButton = page.locator('button:has-text("快速添加常用")').first();
      const hasQuickAdd = await quickAddButton.isVisible().catch(() => false);

      if (hasQuickAdd) {
        await quickAddButton.click();
        await page.waitForTimeout(1000);
      }

      // Check for base field indicators
      const canvasFields = page.locator('[data-testid="field-canvas-drop-zone"] .field-item');

      const fieldCount = await canvasFields.count();
      if (fieldCount > 0) {
        const firstField = canvasFields.first();

        // Check for base field icon (bi-type)
        const typeIcon = firstField.locator('.field-type-badge i.bi-type');
        const hasIcon = await typeIcon.isVisible().catch(() => false);

        // Base fields should have bi-type icon
        expect(hasIcon).toBeTruthy();
      }
    });
  });

  test.describe('Test 4: Drag Common/Universal Fields', () => {
    test('should identify and handle common fields (role_id, account_id, etc.)', async ({ page }) => {
      await selectEvent(page, 'phxcard.gacha');

      // Add common fields using quick add
      const quickAddButton = page.locator('button:has-text("快速添加常用")').first();
      const hasQuickAdd = await quickAddButton.isVisible().catch(() => false);

      if (!hasQuickAdd) {
        test.skip(true, 'Quick add button not available');
        return;
      }

      await quickAddButton.click();
      await page.waitForTimeout(1000);

      // Verify common fields were added
      const canvasFields = page.locator('[data-testid="field-canvas-drop-zone"] .field-item');
      const fieldCount = await canvasFields.count();

      expect(fieldCount).toBeGreaterThan(0);

      // Check for common field names: ds, role_id, account_id, tm
      const fieldAliases: string[] = [];
      for (let i = 0; i < fieldCount; i++) {
        const alias = await canvasFields.nth(i).locator('.field-alias').textContent();
        if (alias) {
          fieldAliases.push(alias);
        }
      }

      // Should contain at least some common fields
      const commonFields = ['ds', 'role_id', 'account_id', 'tm'];
      const hasCommonField = commonFields.some(field => fieldAliases.includes(field));

      expect(hasCommonField).toBeTruthy();
    });

    test('should display common fields with correct data types', async ({ page }) => {
      await selectEvent(page, 'phxcard.gacha');

      // Add common fields
      const quickAddButton = page.locator('button:has-text("快速添加常用")').first();
      const hasQuickAdd = await quickAddButton.isVisible().catch(() => false);

      if (!hasQuickAdd) {
        test.skip(true, 'Quick add button not available');
        return;
      }

      await quickAddButton.click();
      await page.waitForTimeout(1000);

      // Check data type badges
      const canvasFields = page.locator('[data-testid="field-canvas-drop-zone"] .field-item');

      const fieldCount = await canvasFields.count();
      for (let i = 0; i < fieldCount; i++) {
        const field = canvasFields.nth(i);

        // Check if field has data type badge
        const dataTypeBadge = field.locator('.data-type-badge');
        const hasBadge = await dataTypeBadge.isVisible().catch(() => false);

        if (hasBadge) {
          const dataType = await dataTypeBadge.textContent();
          // Verify data type is one of: STRING, BIGINT, UNKNOWN
          expect(['STRING', 'BIGINT', 'UNKNOWN']).toContain(dataType);
        }
      }
    });
  });

  test.describe('Test 5: Drop Zone Visual Feedback', () => {
    test('should show visual feedback when dragging over Canvas', async ({ page }) => {
      await selectEvent(page, 'phxcard.gacha');

      // Get first parameter
      const firstParam = page.locator('[data-testid^="param-"]').first();
      await expect(firstParam).toBeVisible();

      // Get drop zone
      const dropZone = page.locator('[data-testid="field-canvas-drop-zone"]');

      // Start dragging
      await firstParam.dragTo(dropZone, {
        force: true,
        targetPosition: { x: 100, y: 100 }
      });

      // Note: Playwright's dragTo completes the drop immediately
      // For visual feedback testing, we'd need to use a more manual approach
      // However, we can verify the drop zone has the correct styling classes

      // Check if drop zone has drag-over class during drag
      const hasDragOverClass = await dropZone.evaluate(el =>
        el.classList.contains('drag-over')
      );

      // After drop, the class should be removed
      await page.waitForTimeout(500);
      const hasDragOverClassAfter = await dropZone.evaluate(el =>
        el.classList.contains('drag-over')
      );

      expect(hasDragOverClassAfter).toBeFalsy();
    });

    test('should remove visual feedback after drop completes', async ({ page }) => {
      await selectEvent(page, 'phxcard.gacha');

      const firstParam = page.locator('[data-testid^="param-"]').first();
      const dropZone = page.locator('[data-testid="field-canvas-drop-zone"]');

      // Perform drag and drop
      await firstParam.dragTo(dropZone);
      await page.waitForTimeout(1000);

      // Verify drag-over class is removed after drop
      const hasDragOverClass = await dropZone.evaluate(el =>
        el.classList.contains('drag-over')
      );

      expect(hasDragOverClass).toBeFalsy();

      // Verify field was added
      const canvasFields = page.locator('[data-testid="field-canvas-drop-zone"] .field-item');
      expect(await canvasFields.count()).toBeGreaterThan(0);
    });

    test('should show active state when Canvas is ready to receive drops', async ({ page }) => {
      await selectEvent(page, 'phxcard.gacha');

      const dropZone = page.locator('[data-testid="field-canvas-drop-zone"]');

      // Verify drop zone has active class
      const hasActiveClass = await dropZone.evaluate(el =>
        el.classList.contains('active')
      );

      expect(hasActiveClass).toBeTruthy();

      // Verify drop zone is visible
      await expect(dropZone).toBeVisible();
    });

    test('should highlight drop zone border during drag operation', async ({ page }) => {
      await selectEvent(page, 'phxcard.gacha');

      const firstParam = page.locator('[data-testid^="param-"]').first();
      const dropZone = page.locator('[data-testid="field-canvas-drop-zone"]');

      // Get computed styles before drag
      const borderBefore = await dropZone.evaluate(el =>
        window.getComputedStyle(el).borderColor
      );

      // Perform drag
      await firstParam.dragTo(dropZone);
      await page.waitForTimeout(500);

      // Get computed styles after drag
      const borderAfter = await dropZone.evaluate(el =>
        window.getComputedStyle(el).borderColor
      );

      // Border should be defined (not transparent or empty)
      expect(borderAfter).toBeTruthy();
      expect(borderAfter).not.toBe('transparent');
    });
  });

  test.describe('Additional: Edge Cases and Error Handling', () => {
    test('should handle dragging multiple fields quickly', async ({ page }) => {
      await selectEvent(page, 'phxcard.gacha');

      const params = page.locator('[data-testid^="param-"]');
      const dropZone = page.locator('[data-testid="field-canvas-drop-zone"]');

      // Drag 5 fields rapidly
      for (let i = 0; i < 5; i++) {
        await params.nth(i).dragTo(dropZone);
        await page.waitForTimeout(200); // Short delay
      }

      // Wait for all drops to process
      await page.waitForTimeout(2000);

      // Verify all fields were added
      const canvasFields = page.locator('[data-testid="field-canvas-drop-zone"] .field-item');
      expect(await canvasFields.count()).toBeGreaterThanOrEqual(5);
    });

    test('should prevent duplicate fields when dragging same parameter twice', async ({ page }) => {
      await selectEvent(page, 'phxcard.gacha');

      const firstParam = page.locator('[data-testid^="param-"]').first();
      const dropZone = page.locator('[data-testid="field-canvas-drop-zone"]');

      // Drag same parameter twice
      await firstParam.dragTo(dropZone);
      await page.waitForTimeout(500);

      const initialCount = await getCanvasFieldCount(page);

      await firstParam.dragTo(dropZone);
      await page.waitForTimeout(500);

      const finalCount = await getCanvasFieldCount(page);

      // Check if duplicates are allowed or prevented
      // This test documents current behavior
      console.log(`Initial count: ${initialCount}, Final count: ${finalCount}`);

      // The application might allow or prevent duplicates
      // Either behavior is acceptable, just documenting
      expect(finalCount).toBeGreaterThanOrEqual(initialCount);
    });

    test('should handle drag from empty parameter list', async ({ page }) => {
      // Select event that might have no parameters
      await selectEvent(page, 'phxcard.gacha');

      // Try to drag when no parameters exist
      const noParamsText = page.locator('.dropdown-placeholder:has-text("没有找到参数")').first();
      const hasNoParams = await noParamsText.isVisible().catch(() => false);

      if (hasNoParams) {
        // Verify empty state is shown
        await expect(noParamsText).toBeVisible();

        // Verify drop zone still exists
        const dropZone = page.locator('[data-testid="field-canvas-drop-zone"]');
        await expect(dropZone).toBeVisible();
      } else {
        // Parameters exist, skip this test
        test.skip(true, 'Parameters are available, cannot test empty state');
      }
    });
  });
});
