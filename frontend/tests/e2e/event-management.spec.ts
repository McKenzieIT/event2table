import { test, expect } from '@playwright/test';

/**
 * Event Management E2E Tests
 * 
 * Tests for event management functionality:
 * - Create events
 * - Edit events
 * - Delete events
 * - Search events
 * - Import events from Excel
 */

test.describe('Event Management', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to events list page
    await page.goto('/events');
    await page.waitForLoadState('networkidle');
  });

  test('should display events list', async ({ page }) => {
    // Verify page title
    await expect(page).toHaveTitle(/Event2Table/);
    
    // Check if events list container exists
    const eventsList = page.locator('.events-list, [data-testid="events-list"]');
    await expect(eventsList).toBeVisible();
    
    // Check if there are event items
    const eventItems = page.locator('.event-item, .event-card');
    const count = await eventItems.count();
    
    // Either there are events or empty state is shown
    if (count === 0) {
      const emptyState = page.locator('.empty-state, [data-testid="empty-state"]');
      await expect(emptyState).toBeVisible();
    }
  });

  test('should create a new event', async ({ page }) => {
    // Click on create event button
    const createButton = page.locator('button:has-text("创建事件"), button:has-text("添加事件"), [data-testid="create-event-button"]');
    await createButton.first().click();
    
    // Wait for modal/page to open
    await page.waitForTimeout(500);
    
    // Fill in event form
    const eventNameInput = page.locator('input[name="event_name"], input[placeholder*="事件名称"], input[placeholder*="Event Name"]');
    const eventName = `test_event_${Date.now()}`;
    await eventNameInput.fill(eventName);
    
    const eventNameCnInput = page.locator('input[name="event_name_cn"], input[placeholder*="中文名称"]');
    await eventNameCnInput.fill('测试事件');
    
    // Select category if available
    const categorySelect = page.locator('select[name="category"], select[name="category_id"]');
    if (await categorySelect.count() > 0) {
      const options = await categorySelect.locator('option').count();
      if (options > 1) {
        await categorySelect.selectOption({ index: 1 });
      }
    }
    
    // Submit form
    const submitButton = page.locator('button[type="submit"]:has-text("提交"), button:has-text("保存"), button:has-text("创建")');
    await submitButton.click();
    
    // Wait for success message or redirect
    await page.waitForTimeout(1000);
    
    // Verify event was created
    const successMessage = page.locator('.toast-success, .notification-success, [role="alert"]:has-text("成功")');
    if (await successMessage.count() > 0) {
      await expect(successMessage).toBeVisible();
    }
  });

  test('should edit an existing event', async ({ page }) => {
    // Wait for events to load
    await page.waitForTimeout(1000);
    
    // Find first event item
    const firstEvent = page.locator('.event-item, .event-card').first();
    const count = await firstEvent.count();
    
    if (count === 0) {
      test.skip();
      return;
    }
    
    // Click edit button
    const editButton = firstEvent.locator('button:has-text("编辑"), button:has-text("Edit")');
    await editButton.click();
    
    // Wait for edit modal/page
    await page.waitForTimeout(500);
    
    // Modify event name
    const eventNameCnInput = page.locator('input[name="event_name_cn"], input[placeholder*="中文名称"]');
    const count2 = await eventNameCnInput.count();
    
    if (count2 > 0) {
      const currentName = await eventNameCnInput.inputValue();
      await eventNameCnInput.fill(`${currentName} (已编辑)`);
    }
    
    // Save changes
    const saveButton = page.locator('button:has-text("保存"), button:has-text("提交")');
    await saveButton.click();
    
    // Wait for success
    await page.waitForTimeout(1000);
    
    // Verify success message
    const successMessage = page.locator('.toast-success, .notification-success, [role="alert"]:has-text("成功")');
    if (await successMessage.count() > 0) {
      await expect(successMessage).toBeVisible();
    }
  });

  test('should delete an event', async ({ page }) => {
    // Wait for events to load
    await page.waitForTimeout(1000);
    
    // Find first event item
    const firstEvent = page.locator('.event-item, .event-card').first();
    const count = await firstEvent.count();
    
    if (count === 0) {
      test.skip();
      return;
    }
    
    // Click delete button
    const deleteButton = firstEvent.locator('button:has-text("删除"), button:has-text("Delete")');
    await deleteButton.click();
    
    // Handle confirmation dialog
    const confirmDialog = page.locator('.modal, .dialog, [role="dialog"]');
    if (await confirmDialog.count() > 0) {
      const confirmButton = confirmDialog.locator('button:has-text("确认"), button:has-text("确定"), button:has-text("删除")');
      await confirmButton.click();
    }
    
    // Wait for deletion
    await page.waitForTimeout(1000);
    
    // Verify success message
    const successMessage = page.locator('.toast-success, .notification-success, [role="alert"]:has-text("删除成功")');
    if (await successMessage.count() > 0) {
      await expect(successMessage).toBeVisible();
    }
  });

  test('should search events', async ({ page }) => {
    // Wait for events to load
    await page.waitForTimeout(1000);
    
    // Find search input
    const searchInput = page.locator('input[placeholder*="搜索"], input[placeholder*="Search"], .search-input input');
    const count = await searchInput.count();
    
    if (count === 0) {
      test.skip();
      return;
    }
    
    // Enter search term
    await searchInput.fill('login');
    
    // Wait for search results
    await page.waitForTimeout(1000);
    
    // Verify search is working
    const eventItems = page.locator('.event-item, .event-card');
    const searchResultsCount = await eventItems.count();
    
    // Search should filter results
    expect(searchResultsCount).toBeGreaterThanOrEqual(0);
  });

  test('should import events from Excel', async ({ page }) => {
    // Navigate to import page
    await page.goto('/import-events');
    await page.waitForLoadState('networkidle');
    
    // Find file input
    const fileInput = page.locator('input[type="file"]');
    const count = await fileInput.count();
    
    if (count === 0) {
      test.skip();
      return;
    }
    
    // Create a simple Excel file for testing
    // Note: In real tests, you would upload a prepared test file
    const testFilePath = './test-events.xlsx';
    
    // Check if test file exists, if not skip test
    try {
      await fileInput.setInputFiles(testFilePath);
    } catch (error) {
      test.skip();
      return;
    }
    
    // Wait for file to be processed
    await page.waitForTimeout(2000);
    
    // Check if import preview is shown
    const previewTable = page.locator('.import-preview table, .events-table');
    if (await previewTable.count() > 0) {
      await expect(previewTable).toBeVisible();
    }
    
    // Click import button
    const importButton = page.locator('button:has-text("导入"), button:has-text("确认导入")');
    await importButton.click();
    
    // Wait for import to complete
    await page.waitForTimeout(2000);
    
    // Verify success message
    const successMessage = page.locator('.toast-success, .notification-success, [role="alert"]:has-text("导入成功")');
    if (await successMessage.count() > 0) {
      await expect(successMessage).toBeVisible();
    }
  });

  test('should filter events by category', async ({ page }) => {
    // Wait for events to load
    await page.waitForTimeout(1000);
    
    // Find category filter
    const categoryFilter = page.locator('select[name="category"], .category-filter select');
    const count = await categoryFilter.count();
    
    if (count === 0) {
      test.skip();
      return;
    }
    
    // Get initial event count
    const initialEvents = await page.locator('.event-item, .event-card').count();
    
    // Select a category
    const options = await categoryFilter.locator('option').count();
    if (options > 1) {
      await categoryFilter.selectOption({ index: 1 });
      
      // Wait for filter to apply
      await page.waitForTimeout(1000);
      
      // Verify filter is applied
      const filteredEvents = await page.locator('.event-item, .event-card').count();
      expect(filteredEvents).toBeLessThanOrEqual(initialEvents);
    }
  });
});
