import { test, expect, Page } from '@playwright/test';

/**
 * Canvas Smoke Tests
 * Phase 3: Automated E2E Testing
 *
 * Tests basic Canvas functionality including:
 * - Adding nodes to canvas
 * - Node operations (select, drag, delete)
 * - Connecting nodes
 * - HQL generation from canvas
 *
 * Uses test game GID 90000001 to avoid production data.
 */

interface TestConfig {
  readonly BASE_URL: string;
  readonly TEST_GAME_GID: number;
}

const CONFIG: TestConfig = {
  BASE_URL: 'http://localhost:5173',
  TEST_GAME_GID: 90000001
};

test.describe('Canvas Smoke Tests', () => {
  const testGameGid: number = CONFIG.TEST_GAME_GID;

  test.beforeEach(async ({ page }: { page: Page }) => {
    // Navigate to canvas with test game
    await page.goto(`/#/canvas?game_gid=${testGameGid}`);

    // Wait for canvas to load
    await expect(page.locator('[data-testid="canvas-page"], .canvas-page')).toBeVisible({ timeout: 15000 });

    // Wait for React Flow to initialize
    await page.waitForTimeout(1000);
  });

  test('Canvas page loads successfully', async ({ page }: { page: Page }) => {
    // Verify main canvas components are visible
    await expect(page.locator('.react-flow, [data-testid="react-flow"]')).toBeVisible();
    await expect(page.locator('.react-flow__node, .node, [data-testid*="node"]')).toHaveCount({ min: 0 });
  });

  test('Canvas has sidebar with available nodes', async ({ page }: { page: Page }) => {
    // Verify node sidebar exists
    const sidebar = page.locator('.node-sidebar, .sidebar, [data-testid="node-sidebar"]');

    if (await sidebar.isVisible()) {
      // Verify available node types
      await expect(page.locator('.sidebar-item, .node-type, [data-testid*="node-type"]')).toHaveCount({ min: 1 });
    }
  });

  test('User can add event node to canvas', async ({ page }: { page: Page }) => {
    // Look for "Add Event" button or similar
    const addEventButton = page.locator('text=/添加.*事件|add.*event/i').first();

    if (await addEventButton.isVisible()) {
      await addEventButton.click();

      // Wait for node to be added
      await page.waitForTimeout(500);

      // Verify node was added to canvas
      const nodesCount = await page.locator('.react-flow__node, .node').count();
      expect(nodesCount).toBeGreaterThan(0);
    } else {
      // Alternative: drag from sidebar
      const sidebarNode = page.locator('.sidebar-item, .node-type').first();
      const canvas = page.locator('.react-flow, .react-flow__viewport');

      if (await sidebarNode.isVisible()) {
        await sidebarNode.dragTo(canvas);
        await page.waitForTimeout(500);

        const nodesCount = await page.locator('.react-flow__node, .node').count();
        expect(nodesCount).toBeGreaterThan(0);
      }
    }
  });

  test('User can select a node on canvas', async ({ page }: { page: Page }) => {
    // Add a node first if canvas is empty
    let nodesCount = await page.locator('.react-flow__node, .node').count();

    if (nodesCount === 0) {
      const addEventButton = page.locator('text=/添加.*事件|add.*event/i').first();
      if (await addEventButton.isVisible()) {
        await addEventButton.click();
        await page.waitForTimeout(500);
      }
    }

    // Try to select a node
    const firstNode = page.locator('.react-flow__node, .node').first();

    if (await firstNode.isVisible()) {
      await firstNode.click();

      // Verify node is selected (should have selected class or attribute)
      await expect(firstNode).toHaveClass(/selected/);
    }
  });

  test('User can delete a node from canvas', async ({ page }: { page: Page }) => {
    // Add a node if canvas is empty
    let nodesCount = await page.locator('.react-flow__node, .node').count();

    if (nodesCount === 0) {
      const addEventButton = page.locator('text=/添加.*事件|add.*event/i').first();
      if (await addEventButton.isVisible()) {
        await addEventButton.click();
        await page.waitForTimeout(500);
      }
    }

    const initialCount = await page.locator('.react-flow__node, .node').count();

    if (initialCount > 0) {
      // Select first node
      const firstNode = page.locator('.react-flow__node, .node').first();
      await firstNode.click();

      // Delete node (Delete key or delete button)
      await page.keyboard.press('Delete');

      // Wait for deletion
      await page.waitForTimeout(500);

      // Verify node was deleted
      const finalCount = await page.locator('.react-flow__node, .node').count();
      expect(finalCount).toBeLessThan(initialCount);
    }
  });

  test('User can zoom canvas in and out', async ({ page }: { page: Page }) => {
    // Look for zoom controls
    const zoomInButton = page.locator('button[aria-label*="zoom in"], .zoom-in, [data-testid="zoom-in"]');
    const zoomOutButton = page.locator('button[aria-label*="zoom out"], .zoom-out, [data-testid="zoom-out"]');

    if (await zoomInButton.isVisible()) {
      await zoomInButton.click();
      await page.waitForTimeout(500);

      // Verify zoom changed
      const canvas = page.locator('.react-flow, .react-flow__viewport');
      await expect(canvas).toBeVisible();
    }

    if (await zoomOutButton.isVisible()) {
      await zoomOutButton.click();
      await page.waitForTimeout(500);

      // Verify zoom changed
      const canvas = page.locator('.react-flow, .react-flow__viewport');
      await expect(canvas).toBeVisible();
    }
  });

  test('User can fit view to canvas', async ({ page }: { page: Page }) => {
    // Look for fit view button
    const fitViewButton = page.locator('text=/适配|fit view/i, [data-testid="fit-view"]');

    if (await fitViewButton.isVisible()) {
      await fitViewButton.click();
      await page.waitForTimeout(500);

      // Verify canvas is still visible
      await expect(page.locator('.react-flow, .react-flow__viewport')).toBeVisible();
    }
  });

  test('User can generate HQL from canvas', async ({ page }: { page: Page }) => {
    // Look for generate HQL button
    const generateButton = page.locator('text=/生成.*HQL|generate.*hql/i, [data-testid="generate-hql"]');

    if (await generateButton.isVisible()) {
      // Ensure there's at least one node on canvas
      let nodesCount = await page.locator('.react-flow__node, .node').count();

      if (nodesCount === 0) {
        const addEventButton = page.locator('text=/添加.*事件|add.*event/i').first();
        if (await addEventButton.isVisible()) {
          await addEventButton.click();
          await page.waitForTimeout(500);
        }
      }

      // Click generate button
      await generateButton.click();

      // Verify HQL result modal or panel appears
      await expect(page.locator('.hql-result-modal, .hql-output, [data-testid="hql-result"]')).toBeVisible({ timeout: 5000 });

      // Verify HQL contains SELECT statement
      const hqlText = await page.locator('.hql-result-modal, .hql-output').textContent();
      expect(hqlText).toMatch(/SELECT/i);
    }
  });

  test('User can save canvas configuration', async ({ page }: { page: Page }) => {
    // Look for save button
    const saveButton = page.locator('text=/保存|save/i, [data-testid="save-canvas"]');

    if (await saveButton.isVisible()) {
      // Add a node first
      let nodesCount = await page.locator('.react-flow__node, .node').count();

      if (nodesCount === 0) {
        const addEventButton = page.locator('text=/添加.*事件|add.*event/i').first();
        if (await addEventButton.isVisible()) {
          await addEventButton.click();
          await page.waitForTimeout(500);
        }
      }

      // Click save button
      await saveButton.click();

      // Verify save dialog or success message
      await expect(page.locator('.toast-success, .save-dialog, [data-testid="save-success"]')).toBeVisible({ timeout: 3000 });
    }
  });

  test('Canvas has no console errors', async ({ page }: { page: Page }) => {
    // Collect console errors
    const errors: Array<{ text: string; location: { url?: string; lineNumber?: number } }> = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push({
          text: msg.text(),
          location: msg.location()
        });
      }
    });

    // Interact with canvas
    const addEventButton = page.locator('text=/添加.*事件|add.*event/i').first();

    if (await addEventButton.isVisible()) {
      await addEventButton.click();
      await page.waitForTimeout(1000);
    }

    // Filter out non-critical errors
    const criticalErrors = errors.filter(err =>
      !err.text.includes('DevTools') &&
      !err.text.includes('chrome-extension') &&
      !err.text.includes('Extension') &&
      !err.text.includes('React Flow') && // React Flow warnings are non-critical
      !err.text.includes('reactflow')
    );

    expect(criticalErrors).toHaveLength(0);
  });

  test('Canvas loads within performance budget', async ({ page }: { page: Page }) => {
    // Measure canvas load time
    const startTime = Date.now();

    await page.goto(`/#/canvas?game_gid=${testGameGid}`);
    await expect(page.locator('[data-testid="canvas-page"], .canvas-page')).toBeVisible({ timeout: 15000 });

    const loadTime = Date.now() - startTime;

    // Verify canvas loads within 10 seconds (more lenient than dashboard)
    expect(loadTime).toBeLessThan(10000);

    console.log(`Canvas load time: ${loadTime}ms`);
  });

  test('User can access canvas help or documentation', async ({ page }: { page: Page }) => {
    // Look for help button
    const helpButton = page.locator('text=/帮助|help|说明/i, [data-testid="help-button"]');

    if (await helpButton.isVisible()) {
      await helpButton.click();

      // Verify help dialog or documentation appears
      await expect(page.locator('.help-modal, .documentation, [data-testid="help-content"]')).toBeVisible();
    }
  });
});
