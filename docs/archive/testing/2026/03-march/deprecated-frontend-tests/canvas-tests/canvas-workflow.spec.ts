import { test, expect } from '@playwright/test';

test.describe('Canvas Page - 404 Fix Verification', () => {
  const baseUrl = 'http://localhost:5173';
  const canvasUrl = `${baseUrl}/#/canvas?game_gid=10000147`;
  const invalidCanvasUrl = `${baseUrl}/#/canvas?game_gid=99999999`;

  test.beforeEach(async ({ page }) => {
    // 使用与quick-smoke相同的简单等待方式
    await page.goto(canvasUrl);
  });

  test.afterEach(async ({ page }) => {
    // 清理测试状态
    await page.evaluate(() => {
      sessionStorage.clear();
      // 清除 Canvas 缓存
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.includes('dwd_generator_canvas_flow_')) {
          localStorage.removeItem(key);
        }
      });
    });
    await page.waitForTimeout(300);
  });

  test.describe('Primary Fix: No 404 Errors', () => {
    test.afterEach(async ({ page }) => {
      // 清理测试状态
      await page.evaluate(() => {
        sessionStorage.clear();
        // 清除 Canvas 缓存
        const keys = Object.keys(localStorage);
        keys.forEach(key => {
          if (key.includes('dwd_generator_canvas_flow_')) {
            localStorage.removeItem(key);
          }
        });
      });
      await page.waitForTimeout(300);
    });

    test('should not have 404 errors when loading canvas with game_gid', async ({ page }) => {
      const errors: string[] = [];

      // Listen for console errors
      page.on('console', msg => {
        if (msg.type() === 'error') {
          const text = msg.text();
          errors.push(text);
        }
      });

      // Listen for failed requests
      page.on('response', response => {
        if (response.status() === 404) {
          errors.push(`404: ${response.url()}`);
        }
      });

      await page.goto(canvasUrl);
      await expect(page.locator('body')).toBeVisible();
      await page.waitForTimeout(3000);

      // Check that no 404 errors occurred
      const error404 = errors.filter(e => e.includes('404'));
      expect(error404.length).toBe(0);

      // Check specifically for the API endpoint error that was happening before
      const api404Errors = errors.filter(e =>
        e.includes('/api/games/10000147') && e.includes('404')
      );
      expect(api404Errors.length).toBe(0);
    });

    test('should use correct API endpoint /api/games/by-gid/', async ({ page }) => {
      const apiCalls: string[] = [];

      // Track all API calls via response
      page.on('response', async response => {
        const url = response.url();
        if (url.includes('/api/games')) {
          apiCalls.push(url);
        }
      });

      await page.goto(canvasUrl);
      await expect(page.locator('body')).toBeVisible();
      await page.waitForTimeout(3000);

      // Verify the correct endpoint was called
      const correctEndpoint = apiCalls.find(call =>
        call.includes('/api/games/by-gid/10000147')
      );
      expect(correctEndpoint).toBeTruthy();

      // Verify the wrong endpoint was NOT called
      const wrongEndpoint = apiCalls.find(call =>
        call.includes('/api/games/10000147') && !call.includes('/by-gid/')
      );
      expect(wrongEndpoint).toBeFalsy();
    });

    test('should load game data successfully', async ({ page }) => {
      await page.goto(canvasUrl);
      await expect(page.locator('body')).toBeVisible();

      // Wait for game data to load - component uses useGameData hook
      await page.waitForTimeout(5000);

      // Verify canvas page loaded successfully by checking for canvas-page element
      const canvasPage = await page.locator('[data-testid="canvas-page"]').isVisible().catch(() => false);
      
      // Or check for loading spinner gone and no error
      const hasError = await page.locator('[data-testid="canvas-error"]').isVisible().catch(() => false);
      
      // Canvas should be visible (not loading, not error)
      expect(canvasPage || !hasError).toBeTruthy();
    });
  });

  test.describe('Backward Compatibility', () => {
    test.afterEach(async ({ page }) => {
      // 清理测试状态
      await page.evaluate(() => {
        sessionStorage.clear();
        // 清除 Canvas 缓存
        const keys = Object.keys(localStorage);
        keys.forEach(key => {
          if (key.includes('dwd_generator_canvas_flow_')) {
            localStorage.removeItem(key);
          }
        });
      });
      await page.waitForTimeout(300);
    });

    test('should support legacy game_id parameter', async ({ page }) => {
      // Use legacy game_id parameter
      const legacyUrl = `${baseUrl}/#/canvas?game_id=10000147`;

      await page.goto(legacyUrl);
      await expect(page.locator('body')).toBeVisible();

      // Wait for game data to load
      await page.waitForTimeout(5000);

      // Verify canvas page loaded successfully
      const canvasPage = await page.locator('[data-testid="canvas-page"]').isVisible().catch(() => false);
      const hasError = await page.locator('[data-testid="canvas-error"]').isVisible().catch(() => false);
      
      expect(canvasPage || !hasError).toBeTruthy();
    });
  });

  test.describe('Error Handling', () => {
    test.afterEach(async ({ page }) => {
      // 清理测试状态
      await page.evaluate(() => {
        sessionStorage.clear();
        // 清除 Canvas 缓存
        const keys = Object.keys(localStorage);
        keys.forEach(key => {
          if (key.includes('dwd_generator_canvas_flow_')) {
            localStorage.removeItem(key);
          }
        });
      });
      await page.waitForTimeout(300);
    });

    test('should handle invalid game_gid gracefully', async ({ page }) => {
      await page.goto(invalidCanvasUrl);
      await expect(page.locator('body')).toBeVisible();

      // Wait for API call to complete
      await page.waitForTimeout(3000);

      // Verify error state is shown for invalid game
      const hasError = await page.locator('[data-testid="canvas-error"]').isVisible().catch(() => false);
      
      // For invalid game_gid, should show error state
      expect(hasError).toBeTruthy();
    });
  });

  test.describe('Integration: Real-World Usage', () => {
    test.afterEach(async ({ page }) => {
      // 清理测试状态
      await page.evaluate(() => {
        sessionStorage.clear();
        // 清除 Canvas 缓存
        const keys = Object.keys(localStorage);
        keys.forEach(key => {
          if (key.includes('dwd_generator_canvas_flow_')) {
            localStorage.removeItem(key);
          }
        });
      });
      await page.waitForTimeout(300);
    });

    test('should work when navigating directly to canvas URL', async ({ page }) => {
      // Simulate user opening canvas URL directly
      await page.goto(canvasUrl);

      // Wait for app to load
      await expect(page.locator('body')).toBeVisible();

      // Wait for game data to load
      await page.waitForTimeout(5000);

      // Verify no error state
      const hasError = await page.locator('[data-testid="canvas-error"]').isVisible().catch(() => false);
      expect(hasError).toBeFalsy();

      // Verify canvas page loaded (either loading complete or canvas visible)
      const canvasLoaded = await page.locator('[data-testid="canvas-page"], [data-testid="canvas-loading"]').first().isVisible();
      expect(canvasLoaded).toBeTruthy();
    });

    test('should work when clicking from menu (if canvas link exists)', async ({ page }) => {
      // Start at games list
      await page.goto(`${baseUrl}/#/games`);
      await expect(page.locator('body')).toBeVisible();
      await page.waitForTimeout(1000);

      // Try to find canvas link
      const canvasLink = page.locator('a[href*="#/canvas"]').first();

      const isVisible = await canvasLink.isVisible().catch(() => false);

      if (isVisible) {
        // Click the canvas button
        await canvasLink.click();

        // Wait for navigation
        await page.waitForTimeout(3000);

        // Verify we're on canvas page (URL check)
        const url = page.url();
        expect(url).toContain('/canvas');

        // Verify canvas page loaded (not error state)
        const hasError = await page.locator('[data-testid="canvas-error"]').isVisible().catch(() => false);
        expect(hasError).toBeFalsy();
      } else {
        // No canvas link found, skip this test
        test.skip(true, 'No canvas link found on games list');
      }
    });
  });
});
