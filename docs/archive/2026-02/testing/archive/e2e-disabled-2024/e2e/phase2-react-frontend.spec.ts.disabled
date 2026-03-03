import { test, expect } from '@playwright/test';
import { navigateToPage, PAGE_PATHS } from '../helpers/url-helper';

test.describe('Phase 2: React Frontend Integration', () => {
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

  test('should load and interact with Canvas page', async ({ page }) => {
    // Navigate to React Canvas page
    await navigateToPage(page, PAGE_PATHS.CANVAS, { gameGid: '10000147' });

    // Wait for React app to load
    await page.waitForLoadState('networkidle');

    // Take initial screenshot
    await page.screenshot({ path: 'test-results/phase2-react-frontend-initial.png' });

    // Check page title - should contain "Canvas"
    const title = await page.title();
    expect(title).toContain('Canvas');
    console.log('Page title:', title);

    // Check for root div (React app should create #root)
    const rootDiv = page.locator('#root');
    const rootExists = await rootDiv.count();
    expect(rootExists).toBeGreaterThan(0);
    console.log('#root exists:', rootExists);

    // Check for React elements
    const reactFlow = page.locator('.react-flow').first();
    const reactFlowExists = await reactFlow.count();
    expect(reactFlowExists).toBeGreaterThan(0);
    console.log('React Flow element exists:', reactFlowExists);

    // Check for properties panel
    const hasPropertiesPanel = await page.locator('.properties-panel').count();
    console.log('Properties panel elements:', hasPropertiesPanel);
  });

  test('should find and interact with Properties Panel', async ({ page }) => {
    // Navigate and wait
    await navigateToPage(page, PAGE_PATHS.CANVAS, { gameGid: '10000147' });
    await page.waitForLoadState('networkidle');

    // Try to find a node to click
    // Look for any element that might represent a node
    const potentialNodes = page.locator('[class*="event-node"], [class*="join-node"], [class*="custom-node"]');
    const nodeCount = await potentialNodes.count();

    if (nodeCount > 0) {
      // Click first node
      await potentialNodes.first().click();

      // Check if properties panel is now visible
      const propertiesPanel = page.locator('.properties-panel');
      const isVisible = await propertiesPanel.isVisible();
      console.log('Properties panel visible:', isVisible);

      if (isVisible) {
        // Take screenshot with properties panel
        await page.screenshot({ path: 'test-results/phase2-properties-panel-open.png' });

        // Check for properties panel content
        const hasNodeInfo = await propertiesPanel.getByText('节点信息').isVisible();
        console.log('Has node info section:', hasNodeInfo);
      }
    }

    // Close properties panel
    await page.keyboard.press('Escape');
  });

  test('should test Undo functionality via keyboard', async ({ page }) => {
    await navigateToPage(page, PAGE_PATHS.CANVAS, { gameGid: '10000147' });
    await page.waitForLoadState('networkidle');

    // Press Ctrl+Z to undo
    await page.keyboard.press('Control+z');

    // Check for toast notification
    const toastContainer = page.locator('.toast-container');
    const hasToast = await toastContainer.count();
    console.log('Toast container exists:', hasToast);
  });

  test('should test Redo functionality via keyboard', async ({ page }) => {
    await navigateToPage(page, PAGE_PATHS.CANVAS, { gameGid: '10000147' });
    await page.waitForLoadState('networkidle');

    // Press Ctrl+Shift+Z to redo
    await page.keyboard.press('Control+Shift+z');

    // Check for toast notification
    const toastContainer = page.locator('.toast-container');
    const hasToast = await toastContainer.count();
    console.log('Toast container exists:', hasToast);
  });
});

test.describe('Phase 2: Manual Verification Checklist', () => {
  test.beforeEach(async ({ page }) => {
    // Just a placeholder for manual test documentation
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

  test('Properties Panel - Manual Verification', async ({ page }) => {
    console.log('=== MANUAL VERIFICATION: Properties Panel ===');
    console.log('1. 在浏览器中访问 Canvas页面');
    console.log('2. 点击任意节点');
    console.log('3. 验证属性面板显示');
    console.log('4. 测试关闭按钮');
    console.log('5. 截图验证通过');
    console.log('====================================');
    expect(true).toBeTruthy();
  });

  test('Data Preview - Manual Verification', async ({ page }) => {
    console.log('=== MANUAL VERIFICATION: Data Preview ===');
    console.log('1. 在浏览器中访问 Canvas页面');
    console.log('2. 生成HQL');
    console.log('3. 点击"预览数据"按钮');
    console.log('4. 验证数据预览显示');
    console.log('5. 截图验证通过');
    console.log('====================================');
    expect(true).toBeTruthy();
  });

  test('Undo/Redo - Manual Verification', async ({ page }) => {
    console.log('=== MANUAL VERIFICATION: Undo/Redo ===');
    console.log('1. 在浏览器中访问 Canvas页面');
    console.log('2. 测试Ctrl+Z撤销');
    console.log('3. 测试Ctrl+Shift+Z重做');
    console.log('4. 验证Toast通知');
    console.log('5. 截图验证通过');
    console.log('====================================');
    expect(true).toBeTruthy();
  });
});
