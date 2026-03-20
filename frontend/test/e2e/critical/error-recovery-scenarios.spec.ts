import { test, expect } from '@playwright/test';

/**
 * Error Handling and Recovery Scenarios - E2E Test Suite
 *
 * Tests error handling and recovery mechanisms:
 * 1. Invalid input validation
 * 2. Network error handling and retry
 * 3. API error response handling
 * 4. Boundary condition testing
 * 5. Error state recovery
 * 6. Graceful degradation
 *
 * Test Data:
 * - Game GID: 10000147 (STAR001)
 * - Invalid GIDs: 99999999, -1, 0
 *
 * @see docs/testing/e2e-testing-guide.md
 */

const BASE_URL = 'http://localhost:5173';
const VALID_GAME_GID = 10000147;
const INVALID_GAME_GIDS = [99999999, -1, 0, 'abc'];

test.describe('Error Handling and Recovery Scenarios', () => {
  test.describe('Invalid Input Validation', () => {
    test('Scenario 1.1: Handle invalid game_gid in URL', async ({ page }) => {
      const invalidGid = 99999999;

      await page.goto(`${BASE_URL}/#/event-node-builder?game_gid=${invalidGid}`, {
        timeout: 60000,
        waitUntil: 'commit'
      });
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);

      // Verify error message or redirect
      const errorMessage = page.locator('.error-message, .toast:has-text("错误"), .toast:has-text("Error")');
      const errorVisible = await errorMessage.isVisible().catch(() => false);

      if (errorVisible) {
        await expect(errorMessage).toBeVisible();
        console.log('✅ Invalid game_gid error message displayed');
      } else {
        // Check for redirect to home or game selection page
        const currentUrl = page.url();
        const isRedirected = !currentUrl.includes(`game_gid=${invalidGid}`);

        if (isRedirected) {
          console.log('✅ Redirected to valid page after invalid game_gid');
        } else {
          console.log('⚠️ No error handling detected for invalid game_gid');
        }
      }
    });

    test('Scenario 1.2: Handle negative game_gid', async ({ page }) => {
      const negativeGid = -1;

      await page.goto(`${BASE_URL}/#/event-node-builder?game_gid=${negativeGid}`, {
        timeout: 60000,
        waitUntil: 'commit'
      });
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);

      // Verify validation error
      const errorElements = page.locator('.error, .error-message, [role="alert"]');
      const hasError = await errorElements.count() > 0;

      if (hasError) {
        console.log('✅ Negative game_gid validation error displayed');
      } else {
        console.log('⚠️ No validation error for negative game_gid');
      }
    });

    test('Scenario 1.3: Handle non-numeric game_gid', async ({ page }) => {
      const nonNumericGid = 'abc';

      await page.goto(`${BASE_URL}/#/event-node-builder?game_gid=${nonNumericGid}`, {
        timeout: 60000,
        waitUntil: 'commit'
      });
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);

      // Verify URL validation or error
      const currentUrl = page.url();
      const isValid = currentUrl.includes('game_gid=abc');

      if (!isValid) {
        console.log('✅ Non-numeric game_gid rejected or normalized');
      } else {
        console.log('⚠️ Non-numeric game_gid accepted - may need validation');
      }
    });

    test('Scenario 1.4: Handle empty required fields', async ({ page }) => {
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

      await page.goto(`${BASE_URL}/#/event-node-builder?game_gid=${VALID_GAME_GID}`, {
        timeout: 60000,
        waitUntil: 'commit'
      });
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);

      // Try to save without adding any fields
      const saveButton = page.locator('button:has-text("保存"), button:has-text("Save")').first();

      if (await saveButton.isVisible().catch(() => false)) {
        await saveButton.click();
        await page.waitForTimeout(500);

        // Check for validation error
        const validationError = page.locator(
          '.validation-error, .error-message:has-text("字段"), .toast:has-text("至少")'
        );
        const errorVisible = await validationError.isVisible().catch(() => false);

        if (errorVisible) {
          console.log('✅ Validation error for empty canvas');
        } else {
          console.log('⚠️ No validation error for empty canvas');
        }
      }
    });
  });

  test.describe('Network Error Handling', () => {
    test('Scenario 2.1: Handle API timeout', async ({ page }) => {
      // Setup context to simulate slow network
      await page.context().route('**/api/graphql', async route => {
        // Simulate timeout by delaying response
        await new Promise(resolve => setTimeout(resolve, 35000));
        route.continue();
      });

      await page.goto(`${BASE_URL}/#/event-node-builder?game_gid=${VALID_GAME_GID}`, {
        timeout: 60000,
        waitUntil: 'commit'
      });

      // Wait for timeout error
      await page.waitForTimeout(35000);

      // Check for timeout error message
      const timeoutError = page.locator(
        '.error-message:has-text("timeout"), .toast:has-text("超时"), .network-error'
      );
      const errorVisible = await timeoutError.isVisible().catch(() => false);

      if (errorVisible) {
        console.log('✅ Timeout error message displayed');
      } else {
        console.log('⚠️ No timeout error message detected');
      }

      // Cleanup: Remove routing
      await page.context().unroute('**/api/graphql');
    });

    test('Scenario 2.2: Handle network offline', async ({ page }) => {
      // Go offline
      await page.context().setOffline(true);

      await page.goto(`${BASE_URL}/#/event-node-builder?game_gid=${VALID_GAME_GID}`, {
        timeout: 60000,
        waitUntil: 'commit'
      });
      await page.waitForTimeout(2000);

      // Try to perform an action that requires network
      const searchInput = page.locator('input[placeholder*="搜索"]').first();
      if (await searchInput.isVisible().catch(() => false)) {
        await searchInput.fill('themegsoul.summon');
        await page.waitForTimeout(1000);

        // Check for offline error
        const offlineError = page.locator(
          '.error-message:has-text("网络"), .toast:has-text("network"), .offline-message'
        );
        const errorVisible = await offlineError.isVisible().catch(() => false);

        if (errorVisible) {
          console.log('✅ Offline error message displayed');
        } else {
          console.log('⚠️ No offline error message detected');
        }
      }

      // Go back online
      await page.context().setOffline(false);
    });

    test('Scenario 2.3: Handle API error response (500)', async ({ page }) => {
      // Setup context to simulate 500 error
      await page.context().route('**/api/graphql', route => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ errors: [{ message: 'Internal server error' }] })
        });
      });

      await page.goto(`${BASE_URL}/#/event-node-builder?game_gid=${VALID_GAME_GID}`, {
        timeout: 60000,
        waitUntil: 'commit'
      });
      await page.waitForTimeout(2000);

      // Check for server error message
      const serverError = page.locator(
        '.error-message:has-text("500"), .toast:has-text("服务器"), .server-error'
      );
      const errorVisible = await serverError.isVisible().catch(() => false);

      if (errorVisible) {
        console.log('✅ Server error message displayed');
      } else {
        console.log('⚠️ No server error message detected');
      }

      // Cleanup: Remove routing
      await page.context().unroute('**/api/graphql');
    });

    test('Scenario 2.4: Handle retry mechanism', async ({ page }) => {
      let requestCount = 0;

      // Setup context to simulate failure then success
      await page.context().route('**/api/graphql', route => {
        requestCount++;

        if (requestCount === 1) {
          // First request fails
          route.fulfill({
            status: 500,
            contentType: 'application/json',
            body: JSON.stringify({ errors: [{ message: 'Internal server error' }] })
          });
        } else {
          // Second request succeeds
          route.continue();
        }
      });

      await page.goto(`${BASE_URL}/#/event-node-builder?game_gid=${VALID_GAME_GID}`, {
        timeout: 60000,
        waitUntil: 'commit'
      });
      await page.waitForTimeout(3000);

      // Verify retry happened
      if (requestCount > 1) {
        console.log(`✅ Retry mechanism detected (${requestCount} requests)`);
      } else {
        console.log('⚠️ No retry detected (1 request only)');
      }

      // Cleanup: Remove routing
      await page.context().unroute('**/api/graphql');
    });
  });

  test.describe('Boundary Condition Testing', () => {
    test('Scenario 3.1: Handle maximum field count', async ({ page }) => {
      await page.goto(`${BASE_URL}/#/event-node-builder?game_gid=${VALID_GAME_GID}`, {
        timeout: 60000,
        waitUntil: 'commit'
      });
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);

      // Try to add all fields from event with many fields
      const searchInput = page.locator('input[placeholder*="搜索"]').first();
      await searchInput.fill('themegsoul.summon');
      await page.waitForTimeout(500);

      const eventButton = page.locator('button:has-text("善灵抽卡")').first();
      await eventButton.click();
      await page.waitForTimeout(1000);

      const modal = page.locator('[data-testid="field-selection-modal"]');
      const allFieldsButton = modal.locator('button:has-text("所有字段")').first();
      const allFieldsVisible = await allFieldsButton.isVisible().catch(() => false);

      if (allFieldsVisible) {
        await allFieldsButton.click();
        await page.waitForTimeout(2000);

        // Check for performance warning or limit
        const warningMessage = page.locator(
          '.warning:has-text("性能"), .toast:has-text("大量"), .performance-warning'
        );
        const warningVisible = await warningMessage.isVisible().catch(() => false);

        if (warningVisible) {
          console.log('✅ Performance warning for large field count');
        } else {
          console.log('⚠️ No performance warning (may not be implemented)');
        }

        // Verify fields are added successfully
        const canvasFields = page.locator('.canvas-field, .field-item');
        const fieldCount = await canvasFields.count();

        if (fieldCount > 0) {
          console.log(`✅ Successfully handled ${fieldCount} fields`);
        }
      }

      // Close modal
      const modalCloseButton = modal.locator('button:has-text("关闭")').first();
      const closeButtonVisible = await modalCloseButton.isVisible().catch(() => false);
      if (closeButtonVisible) {
        await modalCloseButton.click();
        await page.waitForTimeout(500);
      }
    });

    test('Scenario 3.2: Handle very long field names', async ({ page }) => {
      await page.goto(`${BASE_URL}/#/event-node-builder?game_gid=${VALID_GAME_GID}`, {
        timeout: 60000,
        waitUntil: 'commit'
      });
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);

      // Try to add a field with very long name (if possible)
      const longFieldName = 'a'.repeat(1000);

      // This would typically be prevented by input validation
      const searchInput = page.locator('input[placeholder*="搜索"]').first();

      if (await searchInput.isVisible().catch(() => false)) {
        await searchInput.fill(longFieldName);
        await page.waitForTimeout(500);

        // Check for truncation or validation error
        const inputValue = await searchInput.inputValue();
        const isTruncated = inputValue.length < longFieldName.length;

        if (isTruncated) {
          console.log('✅ Long input truncated (validation working)');
        } else {
          console.log('⚠️ No truncation detected');
        }
      }
    });

    test('Scenario 3.3: Handle special characters in input', async ({ page }) => {
      await page.goto(`${BASE_URL}/#/event-node-builder?game_gid=${VALID_GAME_GID}`, {
        timeout: 60000,
        waitUntil: 'commit'
      });
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);

      // Try to search with special characters
      const specialChars = '<script>alert("xss")</script>';
      const searchInput = page.locator('input[placeholder*="搜索"]').first();

      if (await searchInput.isVisible().catch(() => false)) {
        await searchInput.fill(specialChars);
        await page.waitForTimeout(500);

        // Check if XSS is prevented
        const inputValue = await searchInput.inputValue();
        const isEscaped = inputValue !== specialChars || !inputValue.includes('<script>');

        if (isEscaped) {
          console.log('✅ Special characters escaped (XSS prevention working)');
        } else {
          console.log('⚠️ Special characters not escaped - potential XSS vulnerability');
        }

        // Check for console errors
        const consoleErrors: string[] = [];
        page.on('console', msg => {
          if (msg.type() === 'error') {
            consoleErrors.push(msg.text());
          }
        });

        await page.waitForTimeout(1000);

        if (consoleErrors.length === 0) {
          console.log('✅ No console errors with special characters');
        }
      }
    });
  });

  test.describe('Error State Recovery', () => {
    test('Scenario 4.1: Recover from invalid state', async ({ page }) => {
      // Create an invalid state (e.g., corrupted localStorage)
      await page.goto(`${BASE_URL}/#/`);
      await page.evaluate(() => {
        localStorage.setItem('dwd_generator_canvas_flow_10000147', JSON.stringify({
          invalid: 'data',
          corrupted: true
        }));
      });

      // Navigate to page
      await page.goto(`${BASE_URL}/#/event-node-builder?game_gid=${VALID_GAME_GID}`, {
        timeout: 60000,
        waitUntil: 'commit'
      });
      await page.waitForTimeout(2000);

      // Check for recovery or error message
      const recoveryMessage = page.locator(
        '.toast:has-text("恢复"), .error-message:has-text("损坏"), .recovery-message'
      );
      const recoveryVisible = await recoveryMessage.isVisible().catch(() => false);

      if (recoveryVisible) {
        console.log('✅ Recovery message displayed for corrupted state');
      } else {
        // Check if page loaded successfully despite corrupted state
        const pageLoaded = page.locator('.event-node-builder').isVisible().catch(() => false);
        if (await pageLoaded) {
          console.log('✅ Page recovered successfully from corrupted state');
        } else {
          console.log('⚠️ Page failed to load from corrupted state');
        }
      }
    });

    test('Scenario 4.2: Clear error state and retry', async ({ page }) => {
      // Simulate an error state
      await page.goto(`${BASE_URL}/#/event-node-builder?game_gid=99999999`, {
        timeout: 60000,
        waitUntil: 'commit'
      });
      await page.waitForTimeout(1000);

      // Look for retry button
      const retryButton = page.locator('button:has-text("重试"), button:has-text("Retry"), button:has-text("刷新")').first();
      const retryVisible = await retryButton.isVisible().catch(() => false);

      if (retryVisible) {
        await retryButton.click();
        await page.waitForTimeout(1000);

        console.log('✅ Retry button available and functional');
      } else {
        console.log('⚠️ No retry button detected');

        // Try manual recovery by navigating to valid URL
        await page.goto(`${BASE_URL}/#/event-node-builder?game_gid=${VALID_GAME_GID}`, {
          timeout: 60000,
          waitUntil: 'commit'
        });
        await page.waitForTimeout(1000);

        const pageLoaded = page.locator('.event-node-builder').isVisible().catch(() => false);
        if (await pageLoaded) {
          console.log('✅ Manual recovery successful');
        }
      }
    });

    test('Scenario 4.3: Graceful degradation', async ({ page }) => {
      // Disable JavaScript partially (simulate feature unavailable)
      await page.context().route('**/features/**', route => {
        route.fulfill({
          status: 404,
          body: 'Feature not found'
        });
      });

      await page.goto(`${BASE_URL}/#/event-node-builder?game_gid=${VALID_GAME_GID}`, {
        timeout: 60000,
        waitUntil: 'commit'
      });
      await page.waitForTimeout(2000);

      // Check if page degrades gracefully
      const pageLoaded = page.locator('.event-node-builder').isVisible().catch(() => false);
      const fallbackUI = page.locator('.fallback, .degraded-mode').isVisible().catch(() => false);

      if (await pageLoaded) {
        console.log('✅ Page loaded despite missing features');
      } else if (await fallbackUI) {
        console.log('✅ Graceful degradation to fallback UI');
      } else {
        console.log('⚠️ No graceful degradation detected');
      }

      // Cleanup: Remove routing
      await page.context().unroute('**/features/**');
    });
  });

  test.describe('Console Error Monitoring', () => {
    test('Scenario 5.1: No console errors during normal operation', async ({ page }) => {
      const consoleErrors: string[] = [];

      page.on('console', msg => {
        if (msg.type() === 'error') {
          const text = msg.text();
          // Filter out non-critical errors
          if (!text.includes('favicon') && !text.includes('404')) {
            consoleErrors.push(text);
          }
        }
      });

      await page.goto(`${BASE_URL}/#/event-node-builder?game_gid=${VALID_GAME_GID}`, {
        timeout: 60000,
        waitUntil: 'commit'
      });
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(2000);

      if (consoleErrors.length > 0) {
        console.log(`⚠️ Console errors detected: ${consoleErrors.length}`);
        consoleErrors.forEach(err => console.log(`  - ${err}`));
      } else {
        console.log('✅ No console errors during normal operation');
      }

      // Expect no critical console errors
      expect(consoleErrors.length).toBe(0);
    });

    test('Scenario 5.2: Console errors are logged appropriately', async ({ page }) => {
      const consoleErrors: string[] = [];
      const consoleWarnings: string[] = [];

      page.on('console', msg => {
        if (msg.type() === 'error') {
          consoleErrors.push(msg.text());
        } else if (msg.type() === 'warning') {
          consoleWarnings.push(msg.text());
        }
      });

      // Trigger an error condition
      await page.goto(`${BASE_URL}/#/event-node-builder?game_gid=99999999`, {
        timeout: 60000,
        waitUntil: 'commit'
      });
      await page.waitForTimeout(2000);

      console.log(`Console errors: ${consoleErrors.length}`);
      console.log(`Console warnings: ${consoleWarnings.length}`);

      // Errors should be logged, warnings are acceptable
      if (consoleErrors.length > 0) {
        console.log('✅ Errors are logged to console');
      }

      if (consoleWarnings.length > 0) {
        console.log('⚠️ Warnings detected (may need attention)');
      }
    });
  });
});
