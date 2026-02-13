import { test, expect } from '@playwright/test';
import { navigateToPage, PAGE_PATHS } from '../helpers/url-helper';
import { setGameContext } from '../helpers/game-context';

/**
 * 调试路由和组件加载
 */
test.describe('路由调试', () => {
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

  test('检查EventNodeBuilder页面实际渲染内容', async ({ page }) => {
    await setGameContext(page, '10000147');

    await navigateToPage(page, PAGE_PATHS.EVENT_NODE_BUILDER, { nodeId: 7 });

    // 等待React应用加载
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(5000);

    // 监听控制台
    page.on('console', msg => console.log('Console:', msg.text()));
    page.on('pageerror', err => console.log('Error:', err.message));

    // 打印所有顶级元素
    const bodyHTML = await page.locator('body').innerHTML();
    console.log('Body HTML length:', bodyHTML.length);

    // 检查所有可能的容器类
    const selectors = [
      '.app-shell',
      '.app-body',
      '.event-node-builder',
      '.page-content',
      '.main-content',
      '[class*="event"]',
      '[class*="builder"]'
    ];

    for (const selector of selectors) {
      const count = await page.locator(selector).count();
      if (count > 0) {
        console.log(`${selector}: ${count} element(s)`);
      }
    }

    // 打印#app-root的完整内容（前1000字符）
    const appRootContent = await page.locator('#app-root').innerHTML();
    console.log('App root content (first 1000 chars):', appRootContent.substring(0, 1000));

    // 截图
    await page.screenshot({
      path: 'test-results/debug-route-page.png',
      fullPage: true
    });
  });

  test('检查URL参数处理', async ({ page }) => {
    await setGameContext(page, '10000147');

    const testUrl = 'http://127.0.0.1:5001/#/event-node-builder?node_id=7';
    console.log('Navigating to:', testUrl);

    await page.goto(testUrl);

    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(5000);

    // 检查实际的URL（包括hash）
    const url = page.url();
    console.log('Actual URL:', url);

    // 检查location.hash
    const hash = await page.evaluate(() => window.location.hash);
    console.log('Location hash:', hash);

    // 检查search params
    const searchParams = await page.evaluate(() => window.location.search);
    console.log('Location search:', searchParams);
  });

  test('等待组件加载', async ({ page }) => {
    await setGameContext(page, '10000147');

    await navigateToPage(page, PAGE_PATHS.EVENT_NODE_BUILDER, { nodeId: 7 });

    // 等待任意非空内容
    await page.waitForLoadState('networkidle');

    // 轮询检查组件是否加载
    for (let i = 0; i < 20; i++) {
      await page.waitForTimeout(1000);

      const eventBuilder = await page.locator('.event-node-builder').count();
      const appRootHTML = await page.locator('#app-root').innerHTML();

      console.log(`Attempt ${i + 1}: .event-node-builder count = ${eventBuilder}, #app-root length = ${appRootHTML.length}`);

      if (eventBuilder > 0) {
        console.log('✓ EventNodeBuilder component loaded!');
        break;
      }
    }

    // 最终截图
    await page.screenshot({ path: 'test-results/wait-test-final.png', fullPage: true });
  });
});
