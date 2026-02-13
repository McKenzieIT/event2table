import { test, expect } from '@playwright/test';
import { navigateToPage, PAGE_PATHS } from '../helpers/url-helper';

test.describe('Debug Canvas Page', () => {
  test.afterEach(async ({ page }) => {
    // 清理测试状态
    await page.evaluate(() => {
      sessionStorage.clear();
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.includes('dwd_generator_canvas_flow_')) {
          localStorage.removeItem(key);
        }
      });
      localStorage.removeItem('selectedGameGid');
      if ((window as any).gameData) {
        delete (window as any).gameData;
      }
    });
    await page.waitForTimeout(300);
  });

  test('should load canvas page', async ({ page }) => {
    // Navigate to canvas page - correct URL
    await navigateToPage(page, PAGE_PATHS.CANVAS, { gameGid: '10000147' });

    // Wait for page to load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // Take screenshot
    await page.screenshot({ path: 'test-results/debug-canvas-page.png' });

    // Log page title
    const title = await page.title();
    console.log('Page title:', title);

    // Check if React app loaded
    const root = page.locator('#root');
    const rootExists = await root.count();
    console.log('#root exists:', rootExists);
  });

  test('should check for canvas elements', async ({ page }) => {
    await navigateToPage(page, PAGE_PATHS.CANVAS, { gameGid: '10000147' });
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3000);

    // Wait for React app to mount
    await page.waitForSelector('#root', { timeout: 10000 }).catch(() => {
      console.log('#root not found, checking page content...');
    });

    // Look for React-related elements
    const hasReactFlow = await page.locator('.react-flow').count();
    const hasCanvasFlow = await page.locator('.react-flow-wrapper').count();
    const hasReactFlowCanvas = await page.locator('.react-flow-canvas').count();

    console.log('ReactFlow elements:', hasReactFlow);
    console.log('CanvasFlow wrapper:', hasCanvasFlow);
    console.log('ReactFlow canvas:', hasReactFlowCanvas);

    // List all main divs
    const mainDivs = await page.locator('div[class]').all();
    console.log('Divs with class:', mainDivs.length);
  });
});
