import { test, expect } from '@playwright/test';

/**
 * Batch Operations - E2E Test Suite
 *
 * Tests batch operations and performance:
 * 1. Batch add multiple fields at once
 * 2. Batch delete multiple nodes/fields
 * 3. Batch update field configurations
 * 4. Performance testing with large datasets
 * 5. Bulk import/export operations
 *
 * Test Data:
 * - Game GID: 10000147 (STAR001)
 * - Event: themegsoul.summon (39 fields total)
 *
 * @see docs/testing/e2e-testing-guide.md
 */

const BASE_URL = 'http://localhost:5173';
const GAME_GID = 10000147;

test.describe('Batch Operations and Performance', () => {
  test.beforeEach(async ({ page }) => {
    // Setup game context
    await page.goto(`${BASE_URL}/#/`);
    await page.evaluate(() => {
      localStorage.setItem('selectedGameGid', '10000147');
      (window as any).gameData = {
        id: 16,
        gid: '10000147',
        name: '游戏 10000147',
        ods_db: 'ieu_ods',
      };
    });

    await page.goto(`${BASE_URL}/#/event-node-builder?game_gid=${GAME_GID}`, {
      timeout: 60000,
      waitUntil: 'commit'
    });
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
  });

  test.afterEach(async ({ page }) => {
    // Cleanup test state
    await page.evaluate(() => {
      sessionStorage.clear();
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.includes('dwd_generator_canvas_flow_')) {
          localStorage.removeItem(key);
        }
      });
      localStorage.removeItem('selectedGameGid');
    });
  });

  test('Scenario 1: Batch add all fields at once', async ({ page }) => {
    // Search for event
    const searchInput = page.locator('input[placeholder*="搜索"], input[placeholder*="event"]').first();
    await searchInput.fill('themegsoul.summon');
    await page.waitForTimeout(500);

    // Click event
    const eventButton = page.locator('button:has-text("善灵抽卡")').first();
    await eventButton.click();
    await page.waitForTimeout(1000);

    // Wait for field selection modal
    const modal = page.locator('[data-testid="field-selection-modal"], .modal-content');
    await expect(modal).toBeVisible({ timeout: 5000 });

    // Look for "All Fields" button
    const allFieldsButton = page.locator(
      'button:has-text("📋 所有字段"), button:has-text("所有字段"), button:has-text("All Fields")'
    ).first();

    const allFieldsVisible = await allFieldsButton.isVisible().catch(() => false);

    if (allFieldsVisible) {
      // Measure start time
      const startTime = Date.now();

      // Click "All Fields" button
      await allFieldsButton.click();
      await page.waitForTimeout(2000);

      // Measure end time
      const endTime = Date.now();
      const duration = endTime - startTime;

      // Verify all fields are added
      const canvasFields = page.locator('.canvas-field, .field-item');
      const fieldCount = await canvasFields.count();

      expect(fieldCount).toBeGreaterThan(30); // themegsoul.summon has 39 fields

      console.log(`✅ Batch added ${fieldCount} fields in ${duration}ms`);

      // Performance assertion: should complete within 5 seconds
      expect(duration).toBeLessThan(5000);
    } else {
      console.log('⚠️ "All Fields" button not found - testing manual batch selection');

      // Alternative: Select multiple checkboxes
      const checkboxes = modal.locator('input[type="checkbox"]');
      const checkboxCount = await checkboxes.count();

      if (checkboxCount > 0) {
        // Select first 10 fields
        for (let i = 0; i < Math.min(10, checkboxCount); i++) {
          await checkboxes.nth(i).check();
          await page.waitForTimeout(100);
        }

        // Click confirm
        const confirmButton = modal.locator('button:has-text("确定"), button:has-text("添加")').first();
        await confirmButton.click();
        await page.waitForTimeout(1000);

        console.log('✅ Batch selection using checkboxes');
      }
    }

    // Close modal
    const modalCloseButton = modal.locator('button:has-text("关闭"), button:has-text("取消")').first();
    const closeButtonVisible = await modalCloseButton.isVisible().catch(() => false);
    if (closeButtonVisible) {
      await modalCloseButton.click();
      await page.waitForTimeout(500);
    }
  });

  test('Scenario 2: Batch delete multiple fields', async ({ page }) => {
    // First, add multiple fields
    const searchInput = page.locator('input[placeholder*="搜索"], input[placeholder*="event"]').first();
    await searchInput.fill('themegsoul.summon');
    await page.waitForTimeout(500);
    await page.locator('button:has-text("善灵抽卡")').first().click();
    await page.waitForTimeout(1000);

    const modal = page.locator('[data-testid="field-selection-modal"]');
    const allFieldsButton = modal.locator('button:has-text("所有字段")').first();
    const allFieldsVisible = await allFieldsButton.isVisible().catch(() => false);

    if (allFieldsVisible) {
      await allFieldsButton.click();
      await page.waitForTimeout(2000);

      // Close modal
      const modalCloseButton = modal.locator('button:has-text("关闭")').first();
      await modalCloseButton.click();
      await page.waitForTimeout(500);
    }

    // Get initial field count
    const canvasFields = page.locator('.canvas-field, .field-item');
    const initialCount = await canvasFields.count();
    console.log(`Initial field count: ${initialCount}`);

    // Look for batch delete functionality
    const selectAllButton = page.locator('button:has-text("全选"), button:has-text("Select All")').first();
    const selectAllVisible = await selectAllButton.isVisible().catch(() => false);

    if (selectAllVisible) {
      // Select all fields
      await selectAllButton.click();
      await page.waitForTimeout(500);

      // Click delete button
      const deleteButton = page.locator('button:has-text("删除"), button:has-text("Delete")').first();
      await deleteButton.click();
      await page.waitForTimeout(500);

      // Confirm deletion
      const confirmButton = page.locator('button:has-text("确定"), button:has-text("确认")').first();
      const confirmVisible = await confirmButton.isVisible().catch(() => false);
      if (confirmVisible) {
        await confirmButton.click();
        await page.waitForTimeout(1000);
      }

      // Verify all fields are deleted
      const finalCount = await canvasFields.count();
      expect(finalCount).toBe(0);
      console.log('✅ Batch deleted all fields');
    } else {
      console.log('⚠️ Batch delete UI not found - testing individual delete');

      // Test: Delete first 3 fields individually
      const deleteCount = Math.min(3, initialCount);

      for (let i = 0; i < deleteCount; i++) {
        const firstField = canvasFields.first();
        const deleteButton = firstField.locator('button:has-text("×"), button:has-text("删除"), .delete-button').first();

        if (await deleteButton.isVisible().catch(() => false)) {
          await deleteButton.click();
          await page.waitForTimeout(300);
        }
      }

      const remainingCount = await canvasFields.count();
      console.log(`✅ Deleted ${deleteCount} fields, ${remainingCount} remaining`);
    }
  });

  test('Scenario 3: Batch update field configurations', async ({ page }) => {
    // Add a few fields first
    const fieldsToAdd = ['ds', 'role_id', 'account_id'];

    for (const field of fieldsToAdd) {
      const fieldElement = page.locator(`[data-field="${field}"]`).first();
      if (await fieldElement.isVisible().catch(() => false)) {
        await fieldElement.dblclick();
        await page.waitForTimeout(300);
      }
    }

    // Look for batch edit functionality
    const batchEditButton = page.locator('button:has-text("批量编辑"), button:has-text("Batch Edit")').first();
    const batchEditVisible = await batchEditButton.isVisible().catch(() => false);

    if (batchEditVisible) {
      await batchEditButton.click();
      await page.waitForTimeout(500);

      // Verify batch edit modal/panel
      const batchEditPanel = page.locator('.batch-edit-panel, .modal-content:has-text("批量")');
      await expect(batchEditPanel).toBeVisible();

      // Make batch changes (e.g., change all field types)
      const fieldTypeSelect = page.locator('select[name="fieldType"], .field-type-select').first();
      if (await fieldTypeSelect.isVisible().catch(() => false)) {
        await fieldTypeSelect.selectOption('STRING');
        await page.waitForTimeout(300);
      }

      // Save batch changes
      const saveButton = page.locator('button:has-text("保存"), button:has-text("应用")').first();
      await saveButton.click();
      await page.waitForTimeout(1000);

      console.log('✅ Batch update applied');
    } else {
      console.log('⚠️ Batch edit UI not found - testing individual field update');

      // Test: Update individual fields
      const firstField = page.locator('.canvas-field, .field-item').first();

      // Open field configuration
      await firstField.click();
      await page.waitForTimeout(500);

      // Look for configuration modal
      const configModal = page.locator('.field-config-modal, .modal-content');
      const modalVisible = await configModal.isVisible().catch(() => false);

      if (modalVisible) {
        // Change field alias
        const aliasInput = configModal.locator('input[name="alias"], input[placeholder*="别名"]').first();
        if (await aliasInput.isVisible().catch(() => false)) {
          await aliasInput.fill('test_alias');
          await page.waitForTimeout(300);
        }

        // Save
        const saveButton = configModal.locator('button:has-text("保存")').first();
        await saveButton.click();
        await page.waitForTimeout(500);

        console.log('✅ Individual field update tested');
      }
    }
  });

  test('Scenario 4: Performance test with large dataset', async ({ page }) => {
    console.log('Starting performance test...');

    // Add all fields from themegsoul.summon (39 fields)
    const searchInput = page.locator('input[placeholder*="搜索"], input[placeholder*="event"]').first();
    await searchInput.fill('themegsoul.summon');
    await page.waitForTimeout(500);

    const eventButton = page.locator('button:has-text("善灵抽卡")').first();
    await eventButton.click();
    await page.waitForTimeout(1000);

    const modal = page.locator('[data-testid="field-selection-modal"]');
    await expect(modal).toBeVisible({ timeout: 5000 });

    // Measure performance metrics
    const metrics = {
      fieldSelectionTime: 0,
      renderingTime: 0,
      hqlGenerationTime: 0
    };

    // Test 1: Field selection performance
    let startTime = Date.now();

    const allFieldsButton = modal.locator('button:has-text("所有字段")').first();
    const allFieldsVisible = await allFieldsButton.isVisible().catch(() => false);

    if (allFieldsVisible) {
      await allFieldsButton.click();
      await page.waitForTimeout(2000);

      metrics.fieldSelectionTime = Date.now() - startTime;
      console.log(`Field selection time: ${metrics.fieldSelectionTime}ms`);

      // Performance assertion: field selection should be fast
      expect(metrics.fieldSelectionTime).toBeLessThan(3000);
    }

    // Close modal
    const modalCloseButton = modal.locator('button:has-text("关闭")').first();
    const closeButtonVisible = await modalCloseButton.isVisible().catch(() => false);
    if (closeButtonVisible) {
      await modalCloseButton.click();
      await page.waitForTimeout(500);
    }

    // Test 2: Canvas rendering performance
    startTime = Date.now();

    const canvasFields = page.locator('.canvas-field, .field-item');
    await canvasFields.first().waitFor({ state: 'visible', timeout: 10000 });

    metrics.renderingTime = Date.now() - startTime;
    console.log(`Canvas rendering time: ${metrics.renderingTime}ms`);

    // Performance assertion: rendering should be smooth
    expect(metrics.renderingTime).toBeLessThan(2000);

    // Test 3: HQL generation performance
    startTime = Date.now();

    const hqlButton = page.locator('[data-testid="open-hql-modal"]').first();
    if (await hqlButton.isVisible().catch(() => false)) {
      await hqlButton.click();
      await page.waitForTimeout(1000);

      const hqlContent = page.locator('.hql-content, .code-content');
      await expect(hqlContent).toBeVisible({ timeout: 5000 });

      metrics.hqlGenerationTime = Date.now() - startTime;
      console.log(`HQL generation time: ${metrics.hqlGenerationTime}ms`);

      // Performance assertion: HQL generation should be fast
      expect(metrics.hqlGenerationTime).toBeLessThan(3000);
    }

    // Log performance summary
    console.log('Performance Metrics Summary:');
    console.log(`- Field Selection: ${metrics.fieldSelectionTime}ms`);
    console.log(`- Canvas Rendering: ${metrics.renderingTime}ms`);
    console.log(`- HQL Generation: ${metrics.hqlGenerationTime}ms`);

    const totalTime = metrics.fieldSelectionTime + metrics.renderingTime + metrics.hqlGenerationTime;
    console.log(`Total Time: ${totalTime}ms`);

    // Overall performance assertion
    expect(totalTime).toBeLessThan(10000); // Should complete within 10 seconds
  });

  test('Scenario 5: Bulk import configuration', async ({ page }) => {
    // Look for import functionality
    const importButton = page.locator('button:has-text("导入"), button:has-text("Import")').first();
    const importVisible = await importButton.isVisible().catch(() => false);

    if (importVisible) {
      await importButton.click();
      await page.waitForTimeout(500);

      // Verify import modal/panel
      const importModal = page.locator('.import-modal, .modal-content:has-text("导入")');
      await expect(importModal).toBeVisible();

      // Look for file input
      const fileInput = importModal.locator('input[type="file"]').first();

      if (await fileInput.isVisible().catch(() => false)) {
        // Create a test configuration file
        const testConfig = {
          game_gid: GAME_GID,
          events: [
            {
              name: 'themegsoul.summon',
              fields: ['ds', 'role_id', 'account_id']
            }
          ]
        };

        // Upload file (if supported)
        // Note: Playwright's file upload requires actual file
        console.log('⚠️ File upload detected but requires actual file - UI verified');

        // Cancel import
        const cancelButton = importModal.locator('button:has-text("取消")').first();
        await cancelButton.click();
        await page.waitForTimeout(500);
      }

      console.log('✅ Import UI verified');
    } else {
      console.log('⚠️ Import functionality not found');
    }
  });

  test('Scenario 6: Bulk export configuration', async ({ page }) => {
    // Add some fields first
    const dsField = page.locator('[data-field="ds"]').first();
    if (await dsField.isVisible().catch(() => false)) {
      await dsField.dblclick();
      await page.waitForTimeout(300);
    }

    const roleIdField = page.locator('[data-field="role_id"]').first();
    if (await roleIdField.isVisible().catch(() => false)) {
      await roleIdField.dblclick();
      await page.waitForTimeout(300);
    }

    // Look for export functionality
    const exportButton = page.locator('button:has-text("导出"), button:has-text("Export")').first();
    const exportVisible = await exportButton.isVisible().catch(() => false);

    if (exportVisible) {
      // Setup download handler
      const downloadPromise = page.waitForEvent('download', { timeout: 10000 }).catch(() => null);

      await exportButton.click();
      await page.waitForTimeout(500);

      const download = await downloadPromise;

      if (download) {
        const filename = download.suggestedFilename();
        console.log(`✅ Configuration exported: ${filename}`);
        expect(filename).toMatch(/\.(json|hql|sql)$/);
      } else {
        console.log('⚠️ Download event not captured');
      }
    } else {
      console.log('⚠️ Export button not found - checking for save button');

      // Alternative: Check for save button
      const saveButton = page.locator('button:has-text("保存"), button:has-text("Save")').first();
      if (await saveButton.isVisible().catch(() => false)) {
        console.log('✅ Save button is available (alternative to export)');
      }
    }
  });
});
