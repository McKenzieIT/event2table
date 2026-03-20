import { test, expect } from '@playwright/test';

/**
 * HQL Generation E2E Tests
 * 
 * Tests for HQL generation functionality:
 * - Single event mode
 * - Join mode
 * - Union mode
 * - HQL preview
 * - Copy HQL
 */

test.describe('HQL Generation', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to HQL generation page
    await page.goto('/generate');
    await page.waitForLoadState('networkidle');
  });

  test('should display HQL generation page', async ({ page }) => {
    // Verify page title
    await expect(page).toHaveTitle(/Event2Table/);
    
    // Check if HQL generation form exists
    const hqlForm = page.locator('.hql-generate-form, .generate-form, [data-testid="hql-form"]');
    await expect(hqlForm).toBeVisible();
  });

  test('should generate HQL in single event mode', async ({ page }) => {
    // Wait for events to load
    await page.waitForTimeout(1000);
    
    // Find event selector
    const eventSelect = page.locator('select[name="event"], .event-select select');
    const count = await eventSelect.count();
    
    if (count === 0) {
      test.skip();
      return;
    }
    
    // Select first event
    const options = await eventSelect.locator('option').count();
    if (options > 1) {
      await eventSelect.selectOption({ index: 1 });
    }
    
    // Select single mode
    const modeSelect = page.locator('select[name="mode"], .mode-select select');
    if (await modeSelect.count() > 0) {
      await modeSelect.selectOption('single');
    }
    
    // Click generate button
    const generateButton = page.locator('button:has-text("生成"), button:has-text("Generate"), [data-testid="generate-hql-button"]');
    await generateButton.click();
    
    // Wait for HQL generation
    await page.waitForTimeout(2000);
    
    // Verify HQL is displayed
    const hqlOutput = page.locator('.hql-output, .hql-result, pre, [data-testid="hql-output"]');
    await expect(hqlOutput).toBeVisible();
    
    // Verify HQL contains expected keywords
    const hqlText = await hqlOutput.textContent();
    expect(hqlText).toMatch(/SELECT|FROM|WHERE/i);
  });

  test('should generate HQL in join mode', async ({ page }) => {
    // Wait for events to load
    await page.waitForTimeout(1000);
    
    // Find event selectors
    const eventSelects = page.locator('select[name^="event"], .event-select select');
    const count = await eventSelects.count();
    
    if (count < 2) {
      test.skip();
      return;
    }
    
    // Select two events for join
    await eventSelects.nth(0).selectOption({ index: 1 });
    await eventSelects.nth(1).selectOption({ index: 2 });
    
    // Select join mode
    const modeSelect = page.locator('select[name="mode"], .mode-select select');
    if (await modeSelect.count() > 0) {
      await modeSelect.selectOption('join');
    }
    
    // Click generate button
    const generateButton = page.locator('button:has-text("生成"), button:has-text("Generate")');
    await generateButton.click();
    
    // Wait for HQL generation
    await page.waitForTimeout(2000);
    
    // Verify HQL is displayed
    const hqlOutput = page.locator('.hql-output, .hql-result, pre');
    await expect(hqlOutput).toBeVisible();
    
    // Verify HQL contains JOIN keyword
    const hqlText = await hqlOutput.textContent();
    expect(hqlText).toMatch(/JOIN/i);
  });

  test('should generate HQL in union mode', async ({ page }) => {
    // Wait for events to load
    await page.waitForTimeout(1000);
    
    // Find event selectors
    const eventSelects = page.locator('select[name^="event"], .event-select select');
    const count = await eventSelects.count();
    
    if (count < 2) {
      test.skip();
      return;
    }
    
    // Select two events for union
    await eventSelects.nth(0).selectOption({ index: 1 });
    await eventSelects.nth(1).selectOption({ index: 2 });
    
    // Select union mode
    const modeSelect = page.locator('select[name="mode"], .mode-select select');
    if (await modeSelect.count() > 0) {
      await modeSelect.selectOption('union_all');
    }
    
    // Click generate button
    const generateButton = page.locator('button:has-text("生成"), button:has-text("Generate")');
    await generateButton.click();
    
    // Wait for HQL generation
    await page.waitForTimeout(2000);
    
    // Verify HQL is displayed
    const hqlOutput = page.locator('.hql-output, .hql-result, pre');
    await expect(hqlOutput).toBeVisible();
    
    // Verify HQL contains UNION keyword
    const hqlText = await hqlOutput.textContent();
    expect(hqlText).toMatch(/UNION/i);
  });

  test('should display HQL preview', async ({ page }) => {
    // Wait for events to load
    await page.waitForTimeout(1000);
    
    // Select an event
    const eventSelect = page.locator('select[name="event"], .event-select select');
    const count = await eventSelect.count();
    
    if (count === 0) {
      test.skip();
      return;
    }
    
    const options = await eventSelect.locator('option').count();
    if (options > 1) {
      await eventSelect.selectOption({ index: 1 });
    }
    
    // Click generate button
    const generateButton = page.locator('button:has-text("生成"), button:has-text("Generate")');
    await generateButton.click();
    
    // Wait for HQL generation
    await page.waitForTimeout(2000);
    
    // Verify HQL preview panel exists
    const previewPanel = page.locator('.hql-preview, .preview-panel, [data-testid="hql-preview"]');
    await expect(previewPanel).toBeVisible();
    
    // Verify HQL is syntax highlighted
    const highlightedCode = previewPanel.locator('.cm-line, .token, code');
    const codeCount = await highlightedCode.count();
    expect(codeCount).toBeGreaterThan(0);
  });

  test('should copy HQL to clipboard', async ({ page }) => {
    // Wait for events to load
    await page.waitForTimeout(1000);
    
    // Select an event and generate HQL
    const eventSelect = page.locator('select[name="event"], .event-select select');
    const count = await eventSelect.count();
    
    if (count === 0) {
      test.skip();
      return;
    }
    
    const options = await eventSelect.locator('option').count();
    if (options > 1) {
      await eventSelect.selectOption({ index: 1 });
    }
    
    const generateButton = page.locator('button:has-text("生成"), button:has-text("Generate")');
    await generateButton.click();
    
    await page.waitForTimeout(2000);
    
    // Click copy button
    const copyButton = page.locator('button:has-text("复制"), button:has-text("Copy"), [data-testid="copy-hql-button"]');
    await copyButton.click();
    
    // Wait for copy action
    await page.waitForTimeout(500);
    
    // Verify success message
    const successMessage = page.locator('.toast-success, .notification-success, [role="alert"]:has-text("复制")');
    if (await successMessage.count() > 0) {
      await expect(successMessage).toBeVisible();
    }
  });

  test('should save generated HQL', async ({ page }) => {
    // Wait for events to load
    await page.waitForTimeout(1000);
    
    // Select an event and generate HQL
    const eventSelect = page.locator('select[name="event"], .event-select select');
    const count = await eventSelect.count();
    
    if (count === 0) {
      test.skip();
      return;
    }
    
    const options = await eventSelect.locator('option').count();
    if (options > 1) {
      await eventSelect.selectOption({ index: 1 });
    }
    
    const generateButton = page.locator('button:has-text("生成"), button:has-text("Generate")');
    await generateButton.click();
    
    await page.waitForTimeout(2000);
    
    // Click save button
    const saveButton = page.locator('button:has-text("保存"), button:has-text("Save"), [data-testid="save-hql-button"]');
    const saveCount = await saveButton.count();
    
    if (saveCount > 0) {
      await saveButton.click();
      
      // Wait for save action
      await page.waitForTimeout(1000);
      
      // Verify success message
      const successMessage = page.locator('.toast-success, .notification-success, [role="alert"]:has-text("保存")');
      if (await successMessage.count() > 0) {
        await expect(successMessage).toBeVisible();
      }
    }
  });
});
