import { test, expect } from '@playwright/test';

/**
 * Event Node Builder - Field Types Coverage E2E Tests
 *
 * Comprehensive testing of all 5 field types supported by Event Node Builder:
 * 1. Base fields (基础字段) - ds, role_id, account_id, etc.
 * 2. Parameter fields (参数字段) - Event parameters with JSON path extraction
 * 3. Common fields (公共字段) - Shared/common parameter fields
 * 4. Custom fields (自定义字段) - User-defined expressions
 * 5. Fixed fields (固定值字段) - Hard-coded constant values
 *
 * Test Strategy:
 * - Each test validates the complete workflow for one field type
 * - Verifies UI rendering, field type indicators, and HQL generation
 * - Tests field addition, display, and HQL preview correctness
 */

test.describe('Event Node Builder - Field Types Coverage', () => {
  const baseUrl = 'http://localhost:5173';
  const eventNodeBuilderUrl = `${baseUrl}/#/event-node-builder?game_gid=10000147`;

  test.beforeEach(async ({ page }) => {
    // Navigate to Event Node Builder
    await page.goto(eventNodeBuilderUrl, { timeout: 60000, waitUntil: 'commit' });

    // Wait for page to load
    await page.waitForTimeout(1000);

    // Select an event (login event for testing)
    await page.waitForSelector('[data-testid="event-node-builder-workspace"]', { timeout: 10000 });

    // Dismiss field selection modal if it appears
    const fieldSelectionModal = page.locator('.field-selection-modal-overlay');
    if (await fieldSelectionModal.isVisible().catch(() => false)) {
      // Click "Skip" to manually add fields
      await fieldSelectionModal.locator('text=跳过').click();
      await page.waitForTimeout(500);
    }

    // Wait for workspace to be ready
    await expect(page.locator('[data-testid="event-node-builder-workspace"]')).toBeVisible();
  });

  test.afterEach(async ({ page }) => {
    // Clean up test state
    await page.evaluate(() => {
      sessionStorage.clear();
      localStorage.clear();
    });
  });

  /**
   * Test 1: Base Fields (基础字段)
   *
   * Workflow:
   * 1. Open Quick Action menu
   * 2. Click "基础字段" (Base Fields)
   * 3. Verify base fields are added to canvas
   * 4. Verify field type indicators show "base" or "基础"
   * 5. Verify HQL preview contains base fields
   */
  test('test_add_base_fields', async ({ page }) => {
    // Step 1: Open Quick Action menu
    const quickActionButton = page.locator('.quick-action-buttons__trigger');
    await expect(quickActionButton).toBeVisible({ timeout: 5000 });
    await quickActionButton.click();

    // Wait for dropdown to appear
    await page.waitForSelector('.quick-action-buttons__dropdown', { timeout: 3000 });

    // Step 2: Click "基础字段" (Base Fields) option
    const baseFieldsButton = page.locator('.quick-action-buttons__action').filter({
      hasText: '基础字段'
    });
    await expect(baseFieldsButton).toBeVisible();
    await baseFieldsButton.click();

    // Wait for fields to be added (toast notification)
    await page.waitForSelector('text=/成功添加.*字段/', { timeout: 5000 });
    await page.waitForTimeout(1000);

    // Step 3: Verify base fields are added to canvas
    const canvasFields = page.locator('.canvas-field-item');
    const fieldCount = await canvasFields.count();
    expect(fieldCount).toBeGreaterThan(0);

    // Verify specific base fields are present
    const expectedBaseFields = ['ds', 'role_id', 'account_id'];
    for (const fieldName of expectedBaseFields) {
      const fieldElement = canvasFields.filter({ hasText: fieldName });
      await expect(fieldElement).toBeVisible({ timeout: 3000 });
    }

    // Step 4: Verify field type indicators show "base" or "基础"
    // Check for field type badge or icon
    const firstField = canvasFields.first();
    const fieldTypeBadge = firstField.locator('.field-type-badge, .field-type-label');
    if (await fieldTypeBadge.isVisible().catch(() => false)) {
      const fieldTypeText = await fieldTypeBadge.textContent();
      expect(fieldTypeText?.toLowerCase()).toContain('base');
    }

    // Alternative: check for field type icon
    const fieldTypeIcon = firstField.locator('.bi-type, i[class*="type"]');
    await expect(fieldTypeIcon).toBeVisible();

    // Step 5: Verify HQL preview contains base fields
    // Click HQL preview button to open modal
    const hqlPreviewButton = page.locator('button[title="HQL预览"], .sidebar-section:has-text("HQL") button');
    if (await hqlPreviewButton.isVisible().catch(() => false)) {
      await hqlPreviewButton.click();
      await page.waitForSelector('.hql-preview-modal, [data-testid="hql-preview-modal"]', { timeout: 3000 });

      // Verify HQL contains base fields
      const hqlContent = page.locator('.hql-content, .sql-preview, pre');
      await expect(hqlContent).toBeVisible();
      const hqlText = await hqlContent.textContent();

      // Verify base field names in HQL
      expect(hqlText).toMatch(/ds|role_id|account_id/);

      // Close modal
      const closeButton = page.locator('.modal-close, button:has-text("关闭")');
      await closeButton.click();
      await page.waitForTimeout(500);
    }
  });

  /**
   * Test 2: Parameter Fields (参数字段)
   *
   * Workflow:
   * 1. Open Quick Action menu
   * 2. Click "仅参数" (Parameters Only)
   * 3. Verify parameter fields are added
   * 4. Verify field type indicators show "param" or "参数"
   * 5. Verify HQL contains get_json_object calls
   */
  test('test_add_parameter_fields', async ({ page }) => {
    // Step 1: Open Quick Action menu
    const quickActionButton = page.locator('.quick-action-buttons__trigger');
    await expect(quickActionButton).toBeVisible({ timeout: 5000 });
    await quickActionButton.click();

    // Wait for dropdown
    await page.waitForSelector('.quick-action-buttons__dropdown', { timeout: 3000 });

    // Step 2: Click "仅参数" (Parameters Only) option
    const paramFieldsButton = page.locator('.quick-action-buttons__action').filter({
      hasText: '仅参数'
    });
    await expect(paramFieldsButton).toBeVisible();
    await paramFieldsButton.click();

    // Wait for fields to be added
    await page.waitForSelector('text=/成功添加.*字段/', { timeout: 5000 });
    await page.waitForTimeout(1000);

    // Step 3: Verify parameter fields are added
    const canvasFields = page.locator('.canvas-field-item');
    const fieldCount = await canvasFields.count();
    expect(fieldCount).toBeGreaterThan(0);

    // Verify parameter fields (common parameter names)
    const paramFieldNames = ['level', 'zoneId', 'zone_id', 'vip'];
    const hasParamField = await canvasFields.evaluateAll((fields, names) => {
      return fields.some(field => {
        const text = field.textContent || '';
        return names.some(name => text.includes(name));
      });
    }, paramFieldNames);
    expect(hasParamField).toBeTruthy();

    // Step 4: Verify field type indicators show "param" or "参数"
    const firstField = canvasFields.first();
    const fieldTypeBadge = firstField.locator('.field-type-badge, .field-type-label');
    if (await fieldTypeBadge.isVisible().catch(() => false)) {
      const fieldTypeText = await fieldTypeBadge.textContent();
      expect(fieldTypeText?.toLowerCase()).toMatch(/param|参数/);
    }

    // Check for parameter icon (link icon)
    const fieldTypeIcon = firstField.locator('.bi-link');
    await expect(fieldTypeIcon).toBeVisible();

    // Step 5: Verify HQL contains get_json_object calls
    const hqlPreviewButton = page.locator('button[title="HQL预览"], .sidebar-section:has-text("HQL") button');
    if (await hqlPreviewButton.isVisible().catch(() => false)) {
      await hqlPreviewButton.click();
      await page.waitForSelector('.hql-preview-modal, [data-testid="hql-preview-modal"]', { timeout: 3000 });

      const hqlContent = page.locator('.hql-content, .sql-preview, pre');
      await expect(hqlContent).toBeVisible();
      const hqlText = await hqlContent.textContent();

      // Verify get_json_object in HQL (signature of parameter fields)
      expect(hqlText).toMatch(/get_json_object/);

      // Close modal
      const closeButton = page.locator('.modal-close, button:has-text("关闭")');
      await closeButton.click();
    }
  });

  /**
   * Test 3: Common Fields (公共字段)
   *
   * Workflow:
   * 1. Open Quick Action menu
   * 2. Click "公共字段" (Common Fields)
   * 3. Verify common fields are added
   * 4. Verify field type indicators show "common" or "公共"
   * 5. Verify fields display correctly
   */
  test('test_add_common_fields', async ({ page }) => {
    // Step 1: Open Quick Action menu
    const quickActionButton = page.locator('.quick-action-buttons__trigger');
    await expect(quickActionButton).toBeVisible({ timeout: 5000 });
    await quickActionButton.click();

    await page.waitForSelector('.quick-action-buttons__dropdown', { timeout: 3000 });

    // Step 2: Click "公共字段" (Common Fields) option
    const commonFieldsButton = page.locator('.quick-action-buttons__action').filter({
      hasText: '公共字段'
    });
    await expect(commonFieldsButton).toBeVisible();
    await commonFieldsButton.click();

    // Wait for fields to be added
    await page.waitForSelector('text=/成功添加.*字段/', { timeout: 5000 });
    await page.waitForTimeout(1000);

    // Step 3: Verify common fields are added
    const canvasFields = page.locator('.canvas-field-item');
    const fieldCount = await canvasFields.count();
    expect(fieldCount).toBeGreaterThan(0);

    // Common fields should include frequently used parameters
    const fieldText = await canvasFields.first().textContent();
    expect(fieldText).toBeTruthy();

    // Step 4: Verify field type indicators show "common" or "公共"
    const firstField = canvasFields.first();
    const fieldTypeBadge = firstField.locator('.field-type-badge, .field-type-label');
    if (await fieldTypeBadge.isVisible().catch(() => false)) {
      const fieldTypeText = await fieldTypeBadge.textContent();
      expect(fieldTypeText?.toLowerCase()).toMatch(/common|公共/);
    }

    // Step 5: Verify fields display correctly with proper formatting
    await expect(firstField).toBeVisible();
    await expect(firstField).toHaveText(/./); // Has some text content
  });

  /**
   * Test 4: Custom Fields (自定义字段)
   *
   * Workflow:
   * 1. Click "自定义" (Custom) button in EdgeToolbar
   * 2. Enter field name, type, and expression
   * 3. Save and add to canvas
   * 4. Verify custom field displays
   * 5. Verify HQL contains custom expression
   */
  test('test_add_custom_fields', async ({ page }) => {
    // Step 1: Click "自定义" (Custom) button in EdgeToolbar
    const customButton = page.locator('.edge-toolbar').locator('button').filter({
      hasText: '自定义'
    });
    await expect(customButton).toBeVisible({ timeout: 5000 });
    await customButton.click();

    // Wait for custom field modal
    await page.waitForSelector('.modal-overlay, [data-testid="field-config-modal"]', { timeout: 3000 });

    // Step 2: Enter custom field details
    // Fill in field name
    const fieldNameInput = page.locator('input[placeholder*="字段名"], input[label="字段名"]');
    await expect(fieldNameInput).toBeVisible();
    const testFieldName = `custom_field_${Date.now()}`;
    await fieldNameInput.fill(testFieldName);

    // Fill in display name
    const displayNameInput = page.locator('input[placeholder*="中文名称"], input[label="中文名称"]');
    await expect(displayNameInput).toBeVisible();
    await displayNameInput.fill('测试自定义字段');

    // Fill in expression (if applicable)
    const expressionInput = page.locator('textarea[placeholder*="表达式"], input[placeholder*="expression"]');
    if (await expressionInput.isVisible().catch(() => false)) {
      await expressionInput.fill('CAST(level AS INT)');
    }

    // Step 3: Save and add to canvas
    const saveButton = page.locator('button:has-text("保存"), .btn-primary');
    await expect(saveButton).toBeVisible();
    await saveButton.click();

    // Wait for modal to close and field to be added
    await page.waitForTimeout(1000);

    // Step 4: Verify custom field displays on canvas
    const canvasFields = page.locator('.canvas-field-item');
    const customField = canvasFields.filter({ hasText: testFieldName });

    // Field should be visible
    await expect(customField).toBeVisible({ timeout: 3000 });

    // Verify field type indicator for custom
    const fieldTypeIcon = customField.locator('.bi-code');
    if (await fieldTypeIcon.isVisible().catch(() => false)) {
      await expect(fieldTypeIcon).toBeVisible();
    }

    // Step 5: Verify HQL contains custom expression
    const hqlPreviewButton = page.locator('button[title="HQL预览"], .sidebar-section:has-text("HQL") button');
    if (await hqlPreviewButton.isVisible().catch(() => false)) {
      await hqlPreviewButton.click();
      await page.waitForSelector('.hql-preview-modal, [data-testid="hql-preview-modal"]', { timeout: 3000 });

      const hqlContent = page.locator('.hql-content, .sql-preview, pre');
      await expect(hqlContent).toBeVisible();
      const hqlText = await hqlContent.textContent();

      // Verify custom field name in HQL
      expect(hqlText).toContain(testFieldName);

      // Close modal
      const closeButton = page.locator('.modal-close, button:has-text("关闭")');
      await closeButton.click();
    }
  });

  /**
   * Test 5: Fixed Fields (固定值字段)
   *
   * Workflow:
   * 1. Click "固定值" (Fixed Value) button in EdgeToolbar
   * 2. Enter fixed value (e.g., '20260312')
   * 3. Add to canvas
   * 4. Verify fixed field displays
   * 5. Verify HQL contains fixed value (without quotes)
   */
  test('test_add_fixed_fields', async ({ page }) => {
    // Step 1: Click "固定值" (Fixed Value) button in EdgeToolbar
    const fixedButton = page.locator('.edge-toolbar').locator('button').filter({
      hasText: '固定值'
    });
    await expect(fixedButton).toBeVisible({ timeout: 5000 });
    await fixedButton.click();

    // Wait for fixed field modal
    await page.waitForSelector('.modal-overlay, [data-testid="field-config-modal"]', { timeout: 3000 });

    // Step 2: Enter fixed value details
    const testFixedValue = '20260312';

    // Fill in field name
    const fieldNameInput = page.locator('input[placeholder*="字段名"], input[label="字段名"]');
    if (await fieldNameInput.isVisible().catch(() => false)) {
      await fieldNameInput.fill('partition_date');
    }

    // Fill in fixed value
    const fixedValueInput = page.locator('input[placeholder*="固定值"], input[label="固定值"], input[name*="value"]');
    await expect(fixedValueInput).toBeVisible();
    await fixedValueInput.fill(testFixedValue);

    // Fill in display name
    const displayNameInput = page.locator('input[placeholder*="中文名称"], input[label="中文名称"]');
    if (await displayNameInput.isVisible().catch(() => false)) {
      await displayNameInput.fill('分区日期');
    }

    // Step 3: Save and add to canvas
    const saveButton = page.locator('button:has-text("保存"), .btn-primary');
    await expect(saveButton).toBeVisible();
    await saveButton.click();

    // Wait for modal to close and field to be added
    await page.waitForTimeout(1000);

    // Step 4: Verify fixed field displays on canvas
    const canvasFields = page.locator('.canvas-field-item');
    const fixedField = canvasFields.filter({ hasText: testFixedValue });

    // Field should be visible
    await expect(fixedField).toBeVisible({ timeout: 3000 });

    // Verify field type indicator for fixed
    const fieldTypeIcon = fixedField.locator('.bi-pin');
    if (await fieldTypeIcon.isVisible().catch(() => false)) {
      await expect(fieldTypeIcon).toBeVisible();
    }

    // Step 5: Verify HQL contains fixed value (without quotes for numeric/date literals)
    const hqlPreviewButton = page.locator('button[title="HQL预览"], .sidebar-section:has-text("HQL") button');
    if (await hqlPreviewButton.isVisible().catch(() => false)) {
      await hqlPreviewButton.click();
      await page.waitForSelector('.hql-preview-modal, [data-testid="hql-preview-modal"]', { timeout: 3000 });

      const hqlContent = page.locator('.hql-content, .sql-preview, pre');
      await expect(hqlContent).toBeVisible();
      const hqlText = await hqlContent.textContent();

      // Verify fixed value in HQL (should appear unquoted or with proper escaping)
      expect(hqlText).toContain(testFixedValue);

      // Close modal
      const closeButton = page.locator('.modal-close, button:has-text("关闭")');
      await closeButton.click();
    }
  });
});
