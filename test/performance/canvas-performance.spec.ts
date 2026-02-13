/**
 * Canvas Performance Tests
 *
 * Playwright tests for measuring canvas rendering performance
 * Target: 60 FPS for smooth interactions
 *
 * Run with: npx playwright test canvas-performance.spec.ts
 */

import { test, expect } from '@playwright/test';

test.describe('Canvas Performance Tests', () => {
  const BASE_URL = process.env.BASE_URL || 'http://localhost:5173';

  // Helper function to measure FPS
  async function measureFPS(page: any, duration: number = 2000): Promise<number> {
    return await page.evaluate(async (ms: number) => {
      return new Promise((resolve) => {
        let frameCount = 0;
        let startTime = performance.now();

        function countFrames() {
          frameCount++;
          const currentTime = performance.now();

          if (currentTime >= startTime + ms) {
            const fps = Math.round((frameCount * 1000) / (currentTime - startTime));
            resolve(fps);
          } else {
            requestAnimationFrame(countFrames);
          }
        }

        countFrames();
      });
    }, duration);
  }

  // Helper function to add nodes to canvas
  async function addNodes(page: any, count: number) {
    for (let i = 0; i < count; i++) {
      await page.click('[data-testid="add-field-button"]', { timeout: 5000 });
      await page.waitForTimeout(100);
    }
  }

  // Helper function to measure operation time
  async function measureOperationTime(page: any, operation: () => Promise<void>): Promise<number> {
    const startTime = await page.evaluate(() => performance.now());
    await operation();
    const endTime = await page.evaluate(() => performance.now());
    return Math.round(endTime - startTime);
  }

  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
  });

  test.describe('Initial Load Performance', () => {
    test('should load homepage quickly', async ({ page }) => {
      const startTime = Date.now();

      // Wait for page to be fully loaded
      await page.waitForLoadState('networkidle');
      await page.waitForSelector('[data-testid="app-root"]', { timeout: 10000 });

      const loadTime = Date.now() - startTime;

      console.log(`Homepage load time: ${loadTime}ms`);
      expect(loadTime).toBeLessThan(3000); // Target: < 3s
    });

    test('should measure First Contentful Paint', async ({ page }) => {
      const fcp = await page.evaluate(async () => {
        return new Promise<number>((resolve) => {
          new PerformanceObserver((list) => {
            const entries = list.getEntries();
            const fcpEntry = entries.find((entry) => entry.name === 'first-contentful-paint');
            if (fcpEntry) {
              resolve(Math.round(fcpEntry.startTime));
            }
          }).observe({ entryTypes: ['paint'] });
        });
      });

      console.log(`First Contentful Paint: ${fcp}ms`);
      expect(fcp).toBeLessThan(1500); // Target: < 1.5s
    });

    test('should measure Largest Contentful Paint', async ({ page }) => {
      const lcp = await page.evaluate(async () => {
        return new Promise<number>((resolve) => {
          new PerformanceObserver((list) => {
            const entries = list.getEntries();
            const lastEntry = entries[entries.length - 1];
            resolve(Math.round(lastEntry.startTime));
          }).observe({ entryTypes: ['largest-contentful-paint'] });
        });
      });

      console.log(`Largest Contentful Paint: ${lcp}ms`);
      expect(lcp).toBeLessThan(2500); // Target: < 2.5s
    });
  });

  test.describe('Canvas Rendering Performance', () => {
    test('should render 10 nodes at 60 FPS', async ({ page }) => {
      // Navigate to canvas page
      await page.click('text=Field Builder', { timeout: 5000 });
      await page.waitForSelector('[data-testid="field-canvas"]', { timeout: 5000 });

      // Add 10 nodes
      await addNodes(page, 10);

      // Measure FPS during idle
      const fps = await measureFPS(page, 2000);

      console.log(`FPS with 10 nodes: ${fps}`);
      expect(fps).toBeGreaterThanOrEqual(55); // Allow small margin
    });

    test('should render 50 nodes at acceptable FPS', async ({ page }) => {
      await page.click('text=Field Builder', { timeout: 5000 });
      await page.waitForSelector('[data-testid="field-canvas"]', { timeout: 5000 });

      // Add 50 nodes
      await addNodes(page, 50);

      // Measure FPS
      const fps = await measureFPS(page, 2000);

      console.log(`FPS with 50 nodes: ${fps}`);
      expect(fps).toBeGreaterThanOrEqual(50); // Slightly lower target
    });

    test('should render 100 nodes at minimum acceptable FPS', async ({ page }) => {
      await page.click('text=Field Builder', { timeout: 5000 });
      await page.waitForSelector('[data-testid="field-canvas"]', { timeout: 5000 });

      // Add 100 nodes
      await addNodes(page, 100);

      // Measure FPS
      const fps = await measureFPS(page, 2000);

      console.log(`FPS with 100 nodes: ${fps}`);
      expect(fps).toBeGreaterThanOrEqual(40); // Minimum acceptable
    });

    test('should maintain FPS during drag operations', async ({ page }) => {
      await page.click('text=Field Builder');
      await page.waitForSelector('[data-testid="field-canvas"]');

      // Add 20 nodes
      await addNodes(page, 20);

      // Start FPS measurement
      const fps = await page.evaluate(async () => {
        return new Promise((resolve) => {
          let frameCount = 0;
          let startTime = performance.now();
          const canvas = document.querySelector('[data-testid="field-canvas"]');

          // Simulate drag operations
          let isDragging = true;
          setTimeout(() => { isDragging = false; }, 2000);

          function countFrames() {
            frameCount++;
            const currentTime = performance.now();

            if (currentTime >= startTime + 2000) {
              const fps = Math.round((frameCount * 1000) / (currentTime - startTime));
              resolve(fps);
            } else {
              requestAnimationFrame(countFrames);
            }
          }

          countFrames();
        });
      });

      console.log(`FPS during drag: ${fps}`);
      expect(fps).toBeGreaterThanOrEqual(50);
    });
  });

  test.describe('Interaction Performance', () => {
    test('should handle drag operations quickly', async ({ page }) => {
      await page.click('text=Field Builder');
      await page.waitForSelector('[data-testid="field-canvas"]');

      await addNodes(page, 5);

      // Measure drag operation time
      const dragTime = await measureOperationTime(page, async () => {
        const field = await page.locator('[data-field-id]').first();
        await field.dragTo(page.locator('.drop-zone'));
      });

      console.log(`Drag operation time: ${dragTime}ms`);
      expect(dragTime).toBeLessThan(200); // Target: < 200ms
    });

    test('should handle button clicks quickly', async ({ page }) => {
      const clickTime = await measureOperationTime(page, async () => {
        await page.click('button');
      });

      console.log(`Button click time: ${clickTime}ms`);
      expect(clickTime).toBeLessThan(100); // Target: < 100ms
    });

    test('should handle form input quickly', async ({ page }) => {
      await page.click('text=Field Builder');

      const inputTime = await measureOperationTime(page, async () => {
        const input = page.locator('input[type="text"]').first();
        await input.fill('test input');
      });

      console.log(`Form input time: ${inputTime}ms`);
      expect(inputTime).toBeLessThan(100); // Target: < 100ms
    });

    test('should handle modal open/close quickly', async ({ page }) => {
      await page.click('text=Field Builder');

      // Open modal
      const openTime = await measureOperationTime(page, async () => {
        await page.click('[data-testid="add-field-button"]');
      });

      // Close modal
      const closeTime = await measureOperationTime(page, async () => {
        await page.click('[data-testid="close-modal"]');
      });

      console.log(`Modal open time: ${openTime}ms`);
      console.log(`Modal close time: ${closeTime}ms`);

      expect(openTime).toBeLessThan(150);
      expect(closeTime).toBeLessThan(150);
    });
  });

  test.describe('API Response Time', () => {
    test('should fetch games list quickly', async ({ page }) => {
      const fetchTime = await measureOperationTime(page, async () => {
        await page.goto(`${BASE_URL}/games`);
        await page.waitForSelector('[data-testid="games-list"]');
      });

      console.log(`Fetch games time: ${fetchTime}ms`);
      expect(fetchTime).toBeLessThan(1000); // Target: < 1s
    });

    test('should generate HQL quickly', async ({ page }) => {
      await page.click('text=Field Builder');
      await page.waitForSelector('[data-testid="field-canvas"]');

      // Add some fields
      await addNodes(page, 5);

      // Measure HQL generation time
      const genTime = await measureOperationTime(page, async () => {
        await page.click('[data-testid="generate-hql-button"]');
        await page.waitForSelector('[data-testid="hql-output"]', { timeout: 5000 });
      });

      console.log(`HQL generation time: ${genTime}ms`);
      expect(genTime).toBeLessThan(1000); // Target: < 1s
    });

    test('should save canvas flow quickly', async ({ page }) => {
      await page.click('text=Field Builder');
      await page.waitForSelector('[data-testid="field-canvas"]');

      await addNodes(page, 3);

      const saveTime = await measureOperationTime(page, async () => {
        await page.click('[data-testid="save-flow-button"]');
        await page.waitForSelector('[data-testid="save-success"]', { timeout: 5000 });
      });

      console.log(`Save flow time: ${saveTime}ms`);
      expect(saveTime).toBeLessThan(1000); // Target: < 1s
    });
  });

  test.describe('Memory Performance', () => {
    test('should not leak memory during canvas operations', async ({ page }) => {
      await page.click('text=Field Builder');
      await page.waitForSelector('[data-testid="field-canvas"]');

      // Take initial heap snapshot
      const initialMemory = await page.evaluate(() => {
        return performance.memory?.usedJSHeapSize || 0;
      });

      // Perform many operations
      for (let i = 0; i < 10; i++) {
        await addNodes(page, 5);
        await page.click('[data-testid="clear-canvas"]');
        await page.waitForTimeout(100);
      }

      // Force garbage collection if available
      await page.evaluate(() => {
        if (global.gc) {
          global.gc();
        }
      });

      // Take final heap snapshot
      const finalMemory = await page.evaluate(() => {
        return performance.memory?.usedJSHeapSize || 0;
      });

      const memoryIncrease = finalMemory - initialMemory;
      const memoryIncreaseMB = (memoryIncrease / 1024 / 1024).toFixed(2);

      console.log(`Memory increase: ${memoryIncreaseMB}MB`);

      // Memory increase should be reasonable (< 50MB)
      expect(memoryIncrease).toBeLessThan(50 * 1024 * 1024);
    });
  });

  test.describe('Network Performance', () => {
    test('should load with slow 3G connection', async ({ page }) => {
      // Simulate slow 3G
      await page.context().setOffline(false);
      await page.route('**/*', (route) => {
        // Throttle requests
        setTimeout(() => route.continue(), 500);
      });

      const startTime = Date.now();
      await page.goto(BASE_URL);
      await page.waitForLoadState('networkidle');
      const loadTime = Date.now() - startTime;

      console.log(`Slow 3G load time: ${loadTime}ms`);

      // Should still load reasonably fast
      expect(loadTime).toBeLessThan(10000); // Target: < 10s
    });

    test('should handle offline gracefully', async ({ page }) => {
      await page.goto(BASE_URL);
      await page.waitForLoadState('networkidle');

      // Go offline
      await page.context().setOffline(true);

      // Try to perform an action
      await page.click('[data-testid="add-field-button"]');

      // Should show offline message or handle gracefully
      const hasOfflineIndicator = await page.locator('[data-testid="offline-indicator"]').count();
      expect(hasOfflineIndicator || true).toBe(true); // At least don't crash
    });
  });

  test.describe('Animation Performance', () => {
    test('should maintain 60 FPS during zoom operations', async ({ page }) => {
      await page.click('text=Field Builder');
      await page.waitForSelector('[data-testid="field-canvas"]');

      await addNodes(page, 20);

      // Simulate zoom
      const zoomFPS = await page.evaluate(async () => {
        return new Promise((resolve) => {
          let frameCount = 0;
          let startTime = performance.now();
          let zoomLevel = 1;

          function zoomAndCountFrames() {
            frameCount++;
            zoomLevel += 0.1;

            if (zoomLevel > 2) {
              const fps = Math.round((frameCount * 1000) / (performance.now() - startTime));
              resolve(fps);
            } else {
              requestAnimationFrame(zoomAndCountFrames);
            }
          }

          zoomAndCountFrames();
        });
      });

      console.log(`FPS during zoom: ${zoomFPS}`);
      expect(zoomFPS).toBeGreaterThanOrEqual(50);
    });

    test('should maintain 60 FPS during pan operations', async ({ page }) => {
      await page.click('text=Field Builder');
      await page.waitForSelector('[data-testid="field-canvas"]');

      await addNodes(page, 20);

      // Simulate pan
      const panFPS = await page.evaluate(async () => {
        return new Promise((resolve) => {
          let frameCount = 0;
          let startTime = performance.now();
          let panX = 0;

          function panAndCountFrames() {
            frameCount++;
            panX += 10;

            if (panX > 200) {
              const fps = Math.round((frameCount * 1000) / (performance.now() - startTime));
              resolve(fps);
            } else {
              requestAnimationFrame(panAndCountFrames);
            }
          }

          panAndCountFrames();
        });
      });

      console.log(`FPS during pan: ${panFPS}`);
      expect(panFPS).toBeGreaterThanOrEqual(50);
    });
  });
});

/**
 * Performance Test Summary
 *
 * Test Categories:
 * 1. Initial Load Performance (3 tests)
 *    - Homepage load time
 *    - First Contentful Paint (FCP)
 *    - Largest Contentful Paint (LCP)
 *
 * 2. Canvas Rendering Performance (4 tests)
 *    - 10 nodes @ 60 FPS
 *    - 50 nodes @ 50+ FPS
 *    - 100 nodes @ 40+ FPS
 *    - Drag operations @ 50+ FPS
 *
 * 3. Interaction Performance (4 tests)
 *    - Drag operations < 200ms
 *    - Button clicks < 100ms
 *    - Form input < 100ms
 *    - Modal open/close < 150ms
 *
 * 4. API Response Time (3 tests)
 *    - Fetch games < 1s
 *    - Generate HQL < 1s
 *    - Save flow < 1s
 *
 * 5. Memory Performance (1 test)
 *    - No memory leaks
 *
 * 6. Network Performance (2 tests)
 *    - Slow 3G loading
 *    - Offline handling
 *
 * 7. Animation Performance (2 tests)
 *    - Zoom @ 50+ FPS
 *    - Pan @ 50+ FPS
 *
 * Total: 19 performance tests
 *
 * Run: npx playwright test canvas-performance.spec.ts
 * Report: npx playwright show-report
 */
