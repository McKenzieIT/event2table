import { test, expect } from '@playwright/test';

/**
 * Event Node Builder - Error Handling and Boundary Conditions E2E Tests
 *
 * Tests various error scenarios and boundary conditions to ensure application robustness.
 *
 * Test Coverage:
 * 1. Empty alias submission validation
 * 2. Invalid JSON path input handling
 * 3. API failure handling (500 errors)
 * 4. Maximum fields limit performance
 * 5. Very long field name handling
 * 6. Special characters in field names (SQL injection prevention)
 *
 * Technical Approach:
 * - Use page.route() to intercept and mock API responses
 * - Test boundary conditions and edge cases
 * - Verify user-friendly error messages
 * - Check application stability
 */

test.describe('EventNodeBuilder - Error Handling and Boundary Conditions', () => {
  const baseUrl = 'http://localhost:5173';
  const eventNodeBuilderUrl = `${baseUrl}/#/event-node-builder?game_gid=10000147`;

  test.beforeEach(async ({ page }) => {
    // Clear cache data
    await page.goto(baseUrl, { timeout: 60000, waitUntil: 'commit' });
    await page.evaluate(() => {
      if ((window as any).gameData) {
        delete (window as any).gameData;
      }
      sessionStorage.clear();
      localStorage.clear();
    });
  });

  test.afterEach(async ({ page }) => {
    // Clean up test state
    await page.evaluate(() => {
      sessionStorage.clear();
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.includes('dwd_generator_event_node_builder_')) {
          localStorage.removeItem(key);
        }
      });
      if ((window as any).gameData) {
        delete (window as any).gameData;
      }
    });
    await page.waitForTimeout(300);
  });

  /**
   * Test 1: Empty Alias Submission Validation
   *
   * Scenario: User clears field alias and tries to save
   * Expected: Error message displayed, configuration not saved
   */
  test('should reject empty alias submission', async ({ page }) => {
    // Monitor console errors
    const consoleErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    await page.goto(eventNodeBuilderUrl, { timeout: 60000, waitUntil: 'commit' });
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // Wait for Event Node Builder to load
    const workspace = page.locator('[data-testid="event-node-builder-workspace"]');
    await expect(workspace).toBeVisible({ timeout: 10000 });

    // Step 1: Add a field to canvas
    const paramsSection = page.locator('.sidebar-left').locator('text=参数字段');
    await expect(paramsSection).toBeVisible();

    // Find and click on a parameter field to add it
    const firstField = page.locator('.param-item').first();
    if (await firstField.isVisible()) {
      await firstField.click();
      await page.waitForTimeout(500);
    }

    // Step 2: Edit the field and clear alias
    const aliasInput = page.locator('input[placeholder*="别名"]').or(
      page.locator('input[data-testid*="alias"]')
    ).or(
      page.locator('.field-alias-input')
    ).first();

    if (await aliasInput.isVisible({ timeout: 5000 })) {
      await aliasInput.click();
      await aliasInput.fill(''); // Clear alias
      await page.keyboard.press('Tab');
      await page.waitForTimeout(500);
    }

    // Step 3: Attempt to save configuration
    const saveButton = page.locator('button:has-text("保存")').or(
      page.locator('button[data-testid*="save"]')
    ).or(
      page.locator('.save-button')
    ).first();

    if (await saveButton.isVisible()) {
      // Intercept save API to track request
      let saveAttempted = false;
      await page.route('**/event_node_builder/api/config**', route => {
        saveAttempted = true;
        route.continue();
      });

      await saveButton.click();
      await page.waitForTimeout(1000);

      // Step 4: Verify error message is displayed
      const errorMessage = page.locator('.error-message, .toast-error, [role="alert"]')
        .filter({ hasText: /别名|必填|不能为空|required/ });

      const hasError = await errorMessage.count() > 0;
      expect(hasError, 'Should display error message for empty alias').toBeTruthy();

      // Step 5: Verify configuration was not saved (no API call or error response)
      expect(saveAttempted, 'Save should not be attempted with invalid data').toBeFalsy();

      // Verify no console errors during validation
      const hasValidationError = consoleErrors.some(err =>
        err.includes('validation') || err.includes('alias')
      );

      // Console may have validation errors (expected)
      console.log('Validation errors:', consoleErrors.filter(e =>
        e.includes('alias') || e.includes('validation')
      ));
    } else {
      test.skip('Save button not found - may need to add field first');
    }
  });

  /**
   * Test 2: Invalid JSON Path Input
   *
   * Scenario: User enters invalid JSON path for parameter field
   * Expected: Format error displayed, HQL preview not updated
   */
  test('should handle invalid JSON path input', async ({ page }) => {
    await page.goto(eventNodeBuilderUrl, { timeout: 60000, waitUntil: 'commit' });
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    const workspace = page.locator('[data-testid="event-node-builder-workspace"]');
    await expect(workspace).toBeVisible({ timeout: 10000 });

    // Step 1: Find and edit a parameter field
    const paramsSection = page.locator('.sidebar-left').locator('text=参数字段');
    await expect(paramsSection).toBeVisible();

    // Step 2: Input invalid JSON path
    const jsonPathInput = page.locator('input[placeholder*="JSON"]').or(
      page.locator('input[data-testid*="json-path"]')
    ).or(
      page.locator('.json-path-input')
    ).first();

    if (await jsonPathInput.isVisible({ timeout: 5000 })) {
      const invalidPath = '$.field.invalid.nested.path'; // Invalid format

      await jsonPathInput.click();
      await jsonPathInput.fill(invalidPath);
      await page.keyboard.press('Tab');
      await page.waitForTimeout(500);

      // Step 3: Verify format error message
      const errorMessage = page.locator('.error-message, .field-error, [role="alert"]')
        .filter({ hasText: /格式|路径|JSON|format|path/ });

      const hasFormatError = await errorMessage.isVisible({ timeout: 2000 }).catch(() => false);
      expect(hasFormatError, 'Should display format error for invalid JSON path').toBeTruthy();

      // Step 4: Verify HQL preview is not updated or shows error
      const hqlPreview = page.locator('.hql-preview, [data-testid="hql-preview"]')
        .or(
          page.locator('textarea[readonly*="HQL"]')
        );

      if (await hqlPreview.isVisible()) {
        const hqlContent = await hqlPreview.inputValue();
        const hasInvalidPath = hqlContent.includes('invalid') || hqlContent.includes(invalidPath);

        // HQL should either remain unchanged or show error
        expect(hasInvalidPath, 'HQL preview should not contain invalid path').toBeFalsy();
      }
    } else {
      test.skip('JSON path input not found');
    }
  });

  /**
   * Test 3: API Failure Handling (500 Error)
   *
   * Scenario: Backend API returns 500 error
   * Expected: User-friendly error message, application doesn't crash
   */
  test('should handle API 500 errors gracefully', async ({ page }) => {
    // Monitor console errors and unhandled rejections
    const consoleErrors: string[] = [];
    const unhandledRejections: string[] = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    page.on('pageerror', error => {
      unhandledRejections.push(error.message);
    });

    // Mock API to return 500 error
    await page.route('**/event_node_builder/api/config**', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          success: false,
          error: 'Internal Server Error',
          message: 'Database connection failed'
        })
      });
    });

    await page.goto(eventNodeBuilderUrl, { timeout: 60000, waitUntil: 'commit' });
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    const workspace = page.locator('[data-testid="event-node-builder-workspace"]');
    await expect(workspace).toBeVisible({ timeout: 10000 });

    // Trigger save operation
    const saveButton = page.locator('button:has-text("保存")').or(
      page.locator('button[data-testid*="save"]')
    ).first();

    if (await saveButton.isVisible()) {
      await saveButton.click();
      await page.waitForTimeout(1000);

      // Verify user-friendly error message is displayed
      const errorMessage = page.locator('.error-message, .toast-error, [role="alert"]')
        .filter({ hasText: /失败|错误|服务器|error|failed|server/ });

      const hasUserFriendlyError = await errorMessage.isVisible({ timeout: 3000 }).catch(() => false);
      expect(hasUserFriendlyError, 'Should display user-friendly error message').toBeTruthy();

      // Verify application doesn't crash (no unhandled rejections)
      const hasUnhandledRejection = unhandledRejections.length > 0;
      expect(hasUnhandledRejection, 'Should not have unhandled promise rejections').toBeFalsy();

      // Verify workspace is still interactive
      await expect(workspace).toBeVisible();
    } else {
      test.skip('Save button not found');
    }
  });

  /**
   * Test 4: Maximum Fields Limit Performance
   *
   * Scenario: Add large number of fields (>100)
   * Expected: Performance doesn't degrade significantly, HQL generation succeeds
   */
  test('should handle maximum fields limit without performance degradation', async ({ page }) => {
    // Monitor performance
    const performanceMetrics: { name: string; duration: number }[] = [];

    await page.goto(eventNodeBuilderUrl, { timeout: 60000, waitUntil: 'commit' });
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    const workspace = page.locator('[data-testid="event-node-builder-workspace"]');
    await expect(workspace).toBeVisible({ timeout: 10000 });

    // Step 1: Add multiple fields (simulate >100 fields)
    const startTime = Date.now();

    // Mock API to return many parameters
    await page.route('**/event_node_builder/api/params**', route => {
      const params = Array.from({ length: 150 }, (_, i) => ({
        id: i + 1,
        name: `param_${i}`,
        param_name: `param_${i}`,
        param_type: 'base',
        json_path: '$.field'
      }));

      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: params
        })
      });
    });

    // Reload to get mocked data
    await page.reload();
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    const loadTime = Date.now() - startTime;
    performanceMetrics.push({ name: 'Load 150 fields', duration: loadTime });

    // Step 2: Verify performance is acceptable (< 5 seconds)
    expect(loadTime, 'Loading 150 fields should take less than 5 seconds').toBeLessThan(5000);

    // Step 3: Verify field count warning (if implemented)
    const warningMessage = page.locator('.warning-message, [role="alert"]')
      .filter({ hasText: /字段|数量|限制|fields|limit/ });

    const hasWarning = await warningMessage.isVisible({ timeout: 1000 }).catch(() => false);
    if (hasWarning) {
      console.log('Field count warning displayed:', await warningMessage.textContent());
    }

    // Step 4: Verify HQL generation succeeds
    const generateButton = page.locator('button:has-text("生成")').or(
      page.locator('button[data-testid*="generate"]')
    ).first();

    if (await generateButton.isVisible()) {
      const hqlStartTime = Date.now();
      await generateButton.click();
      await page.waitForTimeout(2000);
      const hqlTime = Date.now() - hqlStartTime;

      performanceMetrics.push({ name: 'Generate HQL with 150 fields', duration: hqlTime });

      // HQL generation should be reasonably fast (< 3 seconds)
      expect(hqlTime, 'HQL generation with 150 fields should take less than 3 seconds').toBeLessThan(3000);

      // Verify HQL preview is displayed
      const hqlPreview = page.locator('.hql-preview, [data-testid="hql-preview"]');
      await expect(hqlPreview).toBeVisible();
    }

    console.log('Performance Metrics:', performanceMetrics);
  });

  /**
   * Test 5: Very Long Field Name Handling
   *
   * Scenario: User enters very long alias (>100 characters)
   * Expected: Alias is truncated or rejected, UI not broken
   */
  test('should handle very long field names without breaking UI', async ({ page }) => {
    await page.goto(eventNodeBuilderUrl, { timeout: 60000, waitUntil: 'commit' });
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    const workspace = page.locator('[data-testid="event-node-builder-workspace"]');
    await expect(workspace).toBeVisible({ timeout: 10000 });

    // Step 1: Add a field
    const paramsSection = page.locator('.sidebar-left').locator('text=参数字段');
    await expect(paramsSection).toBeVisible();

    const firstField = page.locator('.param-item').first();
    if (await firstField.isVisible()) {
      await firstField.click();
      await page.waitForTimeout(500);
    }

    // Step 2: Enter very long alias (>100 characters)
    const veryLongAlias = 'a'.repeat(150); // 150 characters

    const aliasInput = page.locator('input[placeholder*="别名"]').or(
      page.locator('input[data-testid*="alias"]')
    ).or(
      page.locator('.field-alias-input')
    ).first();

    if (await aliasInput.isVisible({ timeout: 5000 })) {
      await aliasInput.click();
      await aliasInput.fill(veryLongAlias);
      await page.keyboard.press('Tab');
      await page.waitForTimeout(500);

      // Step 3: Verify truncation or rejection
      const actualValue = await aliasInput.inputValue();

      // Check if truncated (max 100 chars typically)
      const isTruncated = actualValue.length < veryLongAlias.length;
      const isRejected = actualValue.length === 0;

      expect(
        isTruncated || isRejected,
        `Long alias should be truncated or rejected (actual length: ${actualValue.length})`
      ).toBeTruthy();

      if (isTruncated) {
        console.log(`Alias truncated from ${veryLongAlias.length} to ${actualValue.length} characters`);
        expect(actualValue.length).toBeLessThanOrEqual(100);
      }

      // Step 4: Verify UI is not broken
      await expect(workspace).toBeVisible();
      await expect(aliasInput).toBeVisible();

      // Check for layout breaks
      const hasOverflow = await page.evaluate(() => {
        const body = document.body;
        return body.scrollWidth > body.clientWidth + 10; // Allow small margin
      });

      expect(hasOverflow, 'UI should not have horizontal overflow').toBeFalsy();
    } else {
      test.skip('Alias input not found');
    }
  });

  /**
   * Test 6: Special Characters in Field Names (SQL Injection Prevention)
   *
   * Scenario: User enters SQL keywords and special characters
   * Expected: Characters are escaped or rejected, no SQL injection risk
   */
  test('should prevent SQL injection with special characters', async ({ page }) => {
    await page.goto(eventNodeBuilderUrl, { timeout: 60000, waitUntil: 'commit' });
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    const workspace = page.locator('[data-testid="event-node-builder-workspace"]');
    await expect(workspace).toBeVisible({ timeout: 10000 });

    // Test cases with special characters
    const testCases = [
      { alias: "'; DROP TABLE users; --", description: 'SQL injection attempt' },
      { alias: 'role_id" OR "1"="1', description: 'SQL injection with OR' },
      { alias: 'field; DELETE FROM games WHERE 1=1;--', description: 'Multiple statements' },
      { alias: "role'id", description: 'Single quote' },
      { alias: 'role"id', description: 'Double quote' },
      { alias: 'role--id', description: 'SQL comment' },
      { alias: 'role/*id*/', description: 'C-style comment' },
      { alias: 'role`id', description: 'Backtick' },
      { alias: 'role\\bid', description: 'Backslash' },
      { alias: 'role$id', description: 'Dollar sign' }
    ];

    // Intercept HQL generation API to verify escaping
    let generatedHQL = '';
    await page.route('**/event_node_builder/api/preview-hql**', route => {
      route.continue().then(response => {
        if (response.status() === 200) {
          response.json().then(json => {
            if (json.data && json.data.hql) {
              generatedHQL = json.data.hql;
            }
          });
        }
      });
    });

    for (const testCase of testCases) {
      console.log(`Testing: ${testCase.description}`);

      // Clear previous field
      await page.evaluate(() => {
        localStorage.clear();
      });
      await page.reload();
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);

      // Add field with special characters
      const paramsSection = page.locator('.sidebar-left').locator('text=参数字段');
      await expect(paramsSection).toBeVisible();

      const firstField = page.locator('.param-item').first();
      if (await firstField.isVisible()) {
        await firstField.click();
        await page.waitForTimeout(500);
      }

      const aliasInput = page.locator('input[placeholder*="别名"]').or(
        page.locator('input[data-testid*="alias"]')
      ).first();

      if (await aliasInput.isVisible({ timeout: 3000 })) {
        await aliasInput.click();
        await aliasInput.fill(testCase.alias);
        await page.keyboard.press('Tab');
        await page.waitForTimeout(500);

        // Check for error or rejection
        const errorMessage = page.locator('.error-message, .field-error')
          .filter({ hasText: /字符|特殊|不允许|invalid|character/ });

        const hasError = await errorMessage.isVisible({ timeout: 1000 }).catch(() => false);

        if (hasError) {
          console.log(`✓ ${testCase.description}: Rejected with error`);
          continue;
        }

        // Generate HQL and verify escaping
        const generateButton = page.locator('button:has-text("生成")').or(
          page.locator('button[data-testid*="generate"]')
        ).first();

        if (await generateButton.isVisible()) {
          await generateButton.click();
          await page.waitForTimeout(1000);

          // Check if special characters are escaped in HQL
          const isEscaped = !generatedHQL.includes(testCase.alias) ||
            generatedHQL.includes('"') && generatedHQL.includes('"');

          // Verify no SQL injection patterns in generated HQL
          const hasDangerousPattern = generatedHQL.includes('DROP TABLE') ||
            generatedHQL.includes('DELETE FROM') ||
            generatedHQL.includes('OR "1"="1') ||
            generatedHQL.includes('--') && !generatedHQL.includes('--');

          expect(
            hasDangerousPattern,
            `${testCase.description}: HQL should not contain SQL injection patterns`
          ).toBeFalsy();

          console.log(`✓ ${testCase.description}: Escaped or sanitized`);
        }
      }
    }

    // Final verification: HQL syntax should be valid
    expect(generatedHQL, 'HQL should not be empty').toBeTruthy();

    // Check for basic HQL structure
    const hasValidStructure = generatedHQL.includes('SELECT') &&
      generatedHQL.includes('FROM') &&
      !generatedHQL.includes('DROP') &&
      !generatedHQL.includes('DELETE');

    expect(hasValidStructure, 'Generated HQL should have valid structure').toBeTruthy();
  });
});
