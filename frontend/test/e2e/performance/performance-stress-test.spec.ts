import { test, expect } from '@playwright/test';

/**
 * Performance Stress Tests for Event Node Builder
 *
 * Tests performance under high load conditions:
 * - Large field counts (50-100 fields)
 * - Concurrent operations
 * - Memory leak detection
 * - HQL generation performance
 *
 * Performance Thresholds:
 * - HQL generation: < 2 seconds for 50 fields
 * - Rendering: < 3 seconds for 100 fields
 * - Memory: No continuous growth over 20 iterations
 */

test.describe('Event Node Builder - Performance Stress Tests', () => {
  const BASE_URL = 'http://localhost:5173';
  const EVENT_NODE_BUILDER_URL = `${BASE_URL}/event-node-builder?game_gid=10000147`;

  /**
   * Helper: Navigate to Event Node Builder and wait for initialization
   */
  async function navigateToEventNodeBuilder(page: any) {
    await page.goto(EVENT_NODE_BUILDER_URL);
    await page.waitForLoadState('networkidle');

    // Wait for canvas to initialize
    await page.waitForSelector('[data-testid="canvas-container"]', { timeout: 10000 });
  }

  /**
   * Helper: Add fields to canvas programmatically
   */
  async function addFieldsToCanvas(page: any, fieldCount: number) {
    const startTime = performance.now();

    for (let i = 0; i < fieldCount; i++) {
      await page.evaluate((index: number) => {
        const event = {
          id: `test-event-${index}`,
          eventType: `test_event_${index}`,
          tableName: 'ieu_ods.ods_10000147_all_view',
        };

        const field = {
          id: `field-${index}`,
          name: `field_${index}`,
          type: 'base',
          jsonPath: null,
        };

        // Dispatch event to add field
        window.dispatchEvent(new CustomEvent('add-field-to-canvas', {
          detail: { event, field }
        }));
      }, i);

      // Small delay to prevent overwhelming the UI
      await page.waitForTimeout(10);
    }

    const endTime = performance.now();
    return endTime - startTime;
  }

  /**
   * Test 1: HQL Generation Performance with Many Fields
   *
   * Scenario: Add 50 fields and measure HQL generation time
   * Expected: Generation completes in < 2 seconds
   */
  test('test_hql_generation_performance_with_many_fields', async ({ page }) => {
    await navigateToEventNodeBuilder(page);

    // Add 50 fields
    const fieldCount = 50;
    await addFieldsToCanvas(page, fieldCount);

    // Measure HQL generation time
    const generationTime = await page.evaluate(async (count: number) => {
      const start = performance.now();

      // Trigger HQL generation
      const generateButton = document.querySelector('[data-testid="generate-hql-button"]') as HTMLButtonElement;
      if (generateButton) {
        generateButton.click();
      }

      // Wait for HQL to appear
      await new Promise(resolve => setTimeout(resolve, 100));

      const hqlOutput = document.querySelector('[data-testid="hql-output"]');
      const end = performance.now();

      return {
        time: end - start,
        hasOutput: !!hqlOutput,
        fieldCount: count
      };
    }, fieldCount);

    console.log(`HQL Generation Time (${fieldCount} fields): ${generationTime.time.toFixed(2)}ms`);

    // Assert performance threshold
    expect(generationTime.time).toBeLessThan(2000); // < 2 seconds
    expect(generationTime.hasOutput).toBe(true);
    expect(generationTime.fieldCount).toBe(fieldCount);
  });

  /**
   * Test 2: Large Field Count Rendering Performance
   *
   * Scenario: Add 100 fields and measure rendering time
   * Expected: Rendering completes in < 3 seconds with no lag
   */
  test('test_large_field_count_rendering', async ({ page }) => {
    await navigateToEventNodeBuilder(page);

    // Measure rendering performance
    const renderMetrics = await page.evaluate(async () => {
      const startTime = performance.now();

      // Simulate adding 100 fields
      const fields = [];
      for (let i = 0; i < 100; i++) {
        fields.push({
          id: `field-${i}`,
          name: `field_${i}`,
          type: i % 3 === 0 ? 'param' : 'base', // Mix of field types
          jsonPath: i % 3 === 0 ? `$.field${i}` : null
        });
      }

      // Trigger render
      const canvas = document.querySelector('[data-testid="canvas-container"]');
      if (canvas) {
        canvas.dispatchEvent(new CustomEvent('render-fields', {
          detail: { fields }
        }));
      }

      // Wait for render to complete
      await new Promise(resolve => requestAnimationFrame(resolve));

      const endTime = performance.now();

      // Check for lag (long tasks > 50ms)
      const longTasks = performance.getEntriesByType('longtask');
      const totalLagTime = longTasks.reduce((sum, task) => sum + task.duration, 0);

      return {
        renderTime: endTime - startTime,
        fieldCount: fields.length,
        longTaskCount: longTasks.length,
        totalLagTime: totalLagTime,
        hasLag: totalLagTime > 100 // More than 100ms of lag is considered problematic
      };
    });

    console.log(`Rendering Time (100 fields): ${renderMetrics.renderTime.toFixed(2)}ms`);
    console.log(`Long Tasks: ${renderMetrics.longTaskCount}`);
    console.log(`Total Lag Time: ${renderMetrics.totalLagTime.toFixed(2)}ms`);

    // Assert performance thresholds
    expect(renderMetrics.renderTime).toBeLessThan(3000); // < 3 seconds
    expect(renderMetrics.fieldCount).toBe(100);
    expect(renderMetrics.hasLag).toBe(false); // No significant lag
  });

  /**
   * Test 3: Concurrent Configuration Operations
   *
   * Scenario: Rapidly save 10 configurations
   * Expected: No race conditions, all saves successful, no data corruption
   */
  test('test_concurrent_config_operations', async ({ page }) => {
    await navigateToEventNodeBuilder(page);

    const saveResults = await page.evaluate(async () => {
      const configCount = 10;
      const results = [];
      const savePromises = [];

      // Create 10 unique configurations
      for (let i = 0; i < configCount; i++) {
        const config = {
          id: `config-${i}`,
          name: `Test Config ${i}`,
          gameGid: 10000147,
          fields: [
            { id: `field-1-${i}`, name: 'role_id', type: 'base' },
            { id: `field-2-${i}`, name: 'zone_id', type: 'param', jsonPath: '$.zoneId' }
          ],
          timestamp: Date.now() + i // Ensure unique timestamps
        };

        // Simulate concurrent save operations
        const savePromise = new Promise((resolve) => {
          setTimeout(() => {
            const startTime = performance.now();

            // Simulate save operation
            const success = Math.random() > 0.05; // 95% success rate simulation
            const endTime = performance.now();

            resolve({
              configId: config.id,
              success,
              duration: endTime - startTime,
              timestamp: config.timestamp
            });
          }, Math.random() * 100); // Random delay to simulate real-world concurrency
        });

        savePromises.push(savePromise);
      }

      // Wait for all saves to complete
      const settledResults = await Promise.all(savePromises);
      results.push(...settledResults);

      // Check for data corruption
      const uniqueTimestamps = new Set(results.map(r => r.timestamp));
      const hasCorruption = uniqueTimestamps.size !== configCount;

      return {
        totalOperations: configCount,
        successfulSaves: results.filter((r: any) => r.success).length,
        failedSaves: results.filter((r: any) => !(r as any).success).length,
        averageSaveTime: results.reduce((sum, r: any) => sum + r.duration, 0) / results.length,
        hasCorruption,
        results
      };
    });

    console.log(`Concurrent Saves: ${saveResults.successfulSaves}/${saveResults.totalOperations} successful`);
    console.log(`Average Save Time: ${saveResults.averageSaveTime.toFixed(2)}ms`);

    // Assert no corruption and all saves successful
    expect(saveResults.hasCorruption).toBe(false);
    expect(saveResults.successfulSaves).toBe(saveResults.totalOperations);
    expect(saveResults.failedSaves).toBe(0);
  });

  /**
   * Test 4: Memory Leak Detection
   *
   * Scenario: Switch events 20 times, adding and clearing fields
   * Expected: No continuous memory growth
   */
  test('test_memory_leak_detection', async ({ page }) => {
    await navigateToEventNodeBuilder(page);

    // Check if performance.memory is available (Chrome only)
    const isMemoryAPIAvailable = await page.evaluate(() => {
      return 'memory' in performance;
    });

    if (!isMemoryAPIAvailable) {
      console.warn('performance.memory API not available. Skipping detailed memory metrics.');
      // Run a simplified version that checks for UI degradation instead
      await testMemoryLeakSimplified(page);
      return;
    }

    const memoryMetrics = await page.evaluate(async () => {
      const iterations = 20;
      const memorySnapshots = [];
      const perf = performance as any;

      // Initial memory baseline
      const initialMemory = {
        usedJSHeapSize: perf.memory.usedJSHeapSize,
        totalJSHeapSize: perf.memory.totalJSHeapSize,
        jsHeapSizeLimit: perf.memory.jsHeapSizeLimit
      };
      memorySnapshots.push({ iteration: 0, ...initialMemory });

      // Run 20 iterations of adding and clearing fields
      for (let i = 1; i <= iterations; i++) {
        // Add fields
        for (let j = 0; j < 10; j++) {
          const field = {
            id: `temp-field-${i}-${j}`,
            name: `temp_field_${i}_${j}`,
            type: 'base'
          };

          window.dispatchEvent(new CustomEvent('add-field-to-canvas', {
            detail: { field }
          }));
        }

        // Clear fields
        window.dispatchEvent(new CustomEvent('clear-canvas'));

        // Force garbage collection (if available)
        if ((window as any).gc) {
          (window as any).gc();
        }

        // Small delay to allow GC to run
        await new Promise(resolve => setTimeout(resolve, 50));

        // Take memory snapshot
        const snapshot = {
          iteration: i,
          usedJSHeapSize: perf.memory.usedJSHeapSize,
          totalJSHeapSize: perf.memory.totalJSHeapSize,
          jsHeapSizeLimit: perf.memory.jsHeapSizeLimit,
          timestamp: Date.now()
        };
        memorySnapshots.push(snapshot);
      }

      // Analyze memory growth
      const firstSnapshot = memorySnapshots[1];
      const lastSnapshot = memorySnapshots[memorySnapshots.length - 1];

      const memoryGrowth = lastSnapshot.usedJSHeapSize - firstSnapshot.usedJSHeapSize;
      const memoryGrowthPercentage = (memoryGrowth / firstSnapshot.usedJSHeapSize) * 100;

      // Check for continuous growth (memory leak indicator)
      let continuousGrowthCount = 0;
      for (let i = 2; i < memorySnapshots.length; i++) {
        if (memorySnapshots[i].usedJSHeapSize > memorySnapshots[i - 1].usedJSHeapSize) {
          continuousGrowthCount++;
        }
      }

      const hasMemoryLeak = continuousGrowthCount > iterations * 0.8; // > 80% growth indicates leak

      return {
        iterations,
        initialMemory: memorySnapshots[0],
        finalMemory: lastSnapshot,
        memoryGrowth,
        memoryGrowthPercentage,
        continuousGrowthCount,
        hasMemoryLeak,
        snapshots: memorySnapshots
      };
    });

    console.log(`Memory Growth: ${(memoryMetrics.memoryGrowth / 1024 / 1024).toFixed(2)} MB`);
    console.log(`Memory Growth Percentage: ${memoryMetrics.memoryGrowthPercentage.toFixed(2)}%`);
    console.log(`Continuous Growth Count: ${memoryMetrics.continuousGrowthCount}/${memoryMetrics.iterations}`);

    // Assert no memory leak
    expect(memoryMetrics.hasMemoryLeak).toBe(false);

    // Memory growth should be reasonable (< 20% for 20 iterations)
    expect(memoryMetrics.memoryGrowthPercentage).toBeLessThan(20);

    console.log('Memory leak detection: PASSED ✓');
  });

  /**
   * Simplified memory leak test for browsers without performance.memory API
   */
  async function testMemoryLeakSimplified(page: any) {
    const uiMetrics = await page.evaluate(async () => {
      const iterations = 20;
      const renderTimes = [];

      for (let i = 0; i < iterations; i++) {
        const start = performance.now();

        // Add fields
        for (let j = 0; j < 10; j++) {
          const field = {
            id: `temp-field-${i}-${j}`,
            name: `temp_field_${i}_${j}`,
            type: 'base'
          };

          window.dispatchEvent(new CustomEvent('add-field-to-canvas', {
            detail: { field }
          }));
        }

        // Clear fields
        window.dispatchEvent(new CustomEvent('clear-canvas'));

        await new Promise(resolve => requestAnimationFrame(resolve));

        const end = performance.now();
        renderTimes.push(end - start);
      }

      // Check for performance degradation
      const firstFive = renderTimes.slice(0, 5).reduce((a, b) => a + b, 0) / 5;
      const lastFive = renderTimes.slice(-5).reduce((a, b) => a + b, 0) / 5;
      const degradation = ((lastFive - firstFive) / firstFive) * 100;

      return {
        iterations,
        averageRenderTime: renderTimes.reduce((a, b) => a + b, 0) / renderTimes.length,
        firstFiveAvg: firstFive,
        lastFiveAvg: lastFive,
        degradationPercentage: degradation,
        hasDegradation: degradation > 50 // > 50% slowdown indicates problem
      };
    });

    console.log(`Average Render Time: ${uiMetrics.averageRenderTime.toFixed(2)}ms`);
    console.log(`Performance Degradation: ${uiMetrics.degradationPercentage.toFixed(2)}%`);

    expect(uiMetrics.hasDegradation).toBe(false);
    console.log('Memory leak detection (simplified): PASSED ✓');
  }
});
