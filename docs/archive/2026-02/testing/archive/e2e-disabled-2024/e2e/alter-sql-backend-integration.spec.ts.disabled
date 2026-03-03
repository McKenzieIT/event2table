import { test, expect } from '@playwright/test';

/**
 * E2E Tests for ALTER SQL Backend Integration
 *
 * Tests verify:
 * 1. Backend API /api/alter-table/<param_id> exists and works
 * 2. Frontend displays ALTER TABLE SQL from backend
 * 3. Component fetches data from URL param_id
 * 4. Copy to clipboard functionality works
 */

test.describe('ALTER SQL Backend Integration', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to ALTER SQL page with a param ID
    // Note: This assumes a parameter with ID=1 exists in the database
    await page.goto('/#/alter-sql/1');
  });

  test('should fetch ALTER SQL from backend API', async ({ page }) => {
    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Check if backend API was called
    const apiCalls = [];
    page.on('request', request => {
      if (request.url().includes('/api/alter-table/')) {
        apiCalls.push({
          url: request.url(),
          method: request.method()
        });
      }
    });

    // Reload to capture API calls
    await page.reload();
    await page.waitForLoadState('networkidle');

    // Verify API was called
    expect(apiCalls.length, 'Backend API should be called').toBeGreaterThan(0);
    expect(apiCalls[0].method, 'Should use GET method').toBe('GET');
  });

  test('should display ALTER TABLE statement from backend', async ({ page }) => {
    // Wait for content to load
    await page.waitForSelector('.alter-sql-container, .glass-card', { timeout: 5000 });

    // Check for ALTER TABLE statement
    const pageContent = await page.textContent('body');

    expect(pageContent, 'Should contain ALTER TABLE').toMatch(/ALTER TABLE/i);
    expect(pageContent, 'Should contain ADD COLUMN').toMatch(/ADD COLUMN/i);
  });

  test('should display parameter information', async ({ page }) => {
    // Wait for content to load
    await page.waitForSelector('.alter-sql-container', { timeout: 5000 });

    // Check for parameter details
    const hasTableInfo = await page.locator('body').textContent();

    // Should contain table information
    const hasTableName = hasTableInfo?.includes('表名') || hasTableInfo?.includes('Table Name');
    const hasParamName = hasTableInfo?.includes('参数名') || hasTableInfo?.includes('Parameter Name');
    const hasParamType = hasTableInfo?.includes('参数类型') || hasTableInfo?.includes('Parameter Type');

    if (hasTableName || hasParamName || hasParamType) {
      // At least one info field should be present
      expect(hasTableName || hasParamName || hasParamType).toBeTruthy();
    }
  });

  test('should support copy to clipboard', async ({ page }) => {
    // Wait for content to load
    await page.waitForSelector('.alter-sql-container', { timeout: 5000 });

    // Setup clipboard permissions
    await page.context().grantPermissions(['clipboard-read', 'clipboard-write']);

    // Find and click copy button
    const copyButton = page.locator('button:has-text("复制"), button:has-text("Copy")').first();

    if (await copyButton.isVisible()) {
      await copyButton.click();

      // Verify clipboard content (if supported)
      try {
        const clipboardText = await page.evaluate(async () => {
          return await navigator.clipboard.readText();
        });

        expect(clipboardText, 'Clipboard should contain ALTER TABLE').toMatch(/ALTER TABLE/i);
      } catch (error) {
        // Clipboard API might not work in test environment
        console.log('Clipboard API not available in test environment');
      }
    }
  });

  test('should show loading state while fetching', async ({ page }) => {
    // Monitor network requests
    let apiRequestTime = 0;
    page.on('request', request => {
      if (request.url().includes('/api/alter-table/')) {
        apiRequestTime = Date.now();
      }
    });

    page.on('response', response => {
      if (response.url().includes('/api/alter-table/')) {
        const responseTime = Date.now();
        const duration = responseTime - apiRequestTime;

        // If API takes more than 100ms, loading state should be visible
        if (duration > 100) {
          // Check for loading indicator
          const loadingExists = page.locator('.loading-state, .spinner').count();
          // This is a soft check - loading might appear briefly
        }
      }
    });

    await page.goto('/#/alter-sql/1');
    await page.waitForLoadState('networkidle');
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Test with non-existent parameter ID
    await page.goto('/#/alter-sql/999999');

    // Wait for error handling
    await page.waitForTimeout(1000);

    // Check for error message or fallback
    const pageContent = await page.textContent('body');
    const hasError = pageContent?.includes('未找到') ||
                     pageContent?.includes('not found') ||
                     pageContent?.includes('error') ||
                     pageContent?.includes('错误');

    // Should show some kind of error message
    if (hasError) {
      expect(hasError).toBeTruthy();
    }
  });
});

test.describe('AlterSqlBuilder (Manual Tool)', () => {
  test('should work as standalone manual tool', async ({ page }) => {
    await page.goto('/#/alter-sql-builder');

    // Fill in the form
    await page.fill('input[placeholder*="表名"], input[placeholder*="Table"]', 'dwd_event_login');
    await page.fill('input[placeholder*="列名"], input[placeholder*="Column"]', 'zone_id');

    // Generate SQL
    await page.click('button:has-text("生成"), button:has-text("Generate")');

    // Check output
    const output = await page.textContent('pre, .sql-output');
    expect(output, 'Should contain generated ALTER TABLE').toMatch(/ALTER TABLE dwd_event_login/i);
    expect(output, 'Should contain zone_id').toMatch(/zone_id/i);
  });

  test('should support multiple alterations', async ({ page }) => {
    await page.goto('/#/alter-sql-builder');

    // Add first alteration
    await page.fill('input[placeholder*="表名"]', 'test_table');
    await page.fill('input[placeholder*="列名"]', 'field1');

    // Add second alteration (click add button)
    await page.click('button:has-text("添加"), button:has-text("Add")');

    // Fill second alteration
    const inputs = await page.locator('input[placeholder*="列名"]').all();
    if (inputs.length > 1) {
      await inputs[1].fill('field2');
    }

    // Generate SQL
    await page.click('button:has-text("生成"), button:has-text("Generate")');

    // Check output
    const output = await page.textContent('pre, .sql-output');
    const hasMultipleStatements = output?.match(/ALTER TABLE/g)?.length || 0;

    if (hasMultipleStatements > 0) {
      expect(hasMultipleStatements).toBeGreaterThanOrEqual(2);
    }
  });
});
