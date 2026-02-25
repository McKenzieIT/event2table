import { test, expect } from '@playwright/test';
import { navigateToPage, PAGE_PATHS } from '../helpers/url-helper';

/**
 * 简单的React应用加载测试
 * 用于验证React应用是否正确加载
 */
test.describe('React应用加载测试', () => {
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

  test('应该能加载React应用', async ({ page }) => {
    // 访问React应用基础URL
    await navigateToPage(page, PAGE_PATHS.HOME);

    console.log('URL:', page.url());

    // 等待页面加载
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(5000);

    // 检查#app-root是否存在
    const appRoot = page.locator('#app-root');
    const count = await appRoot.count();
    console.log('#app-root count:', count);

    expect(count).toBeGreaterThan(0);

    // 检查#app-root是否有内容
    if (count > 0) {
      const innerHTML = await appRoot.first().innerHTML();
      console.log('#app-root HTML length:', innerHTML.length);
      console.log('#app-root content:', innerHTML.substring(0, 200));

      // 检查是否有React内容
      const hasReactContent = innerHTML.length > 100;
      console.log('Has React content:', hasReactContent);

      // 截图
      await page.screenshot({ path: 'test-results/react-load-test.png' });
    }
  });

  test('应该能加载EventNodeBuilder页面', async ({ page }) => {
    await navigateToPage(page, PAGE_PATHS.EVENT_NODE_BUILDER, { nodeId: 7 });

    // 等待更长时间
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(8000);

    // 监听控制台
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log('Console error:', msg.text());
      }
    });

    // 检查#app-root
    const appRoot = page.locator('#app-root');
    await expect(appRoot).toBeVisible({ timeout: 10000 });

    // 等待React渲染
    await page.waitForTimeout(3000);

    // 检查是否有event-node-builder类
    const eventBuilder = page.locator('.event-node-builder');
    const eventBuilderCount = await eventBuilder.count();
    console.log('.event-node-builder count:', eventBuilderCount);

    // 截图
    await page.screenshot({
      path: 'test-results/event-builder-load.png',
      fullPage: true
    });

    // 打印body的HTML长度
    const bodyHTML = await page.locator('body').innerHTML();
    console.log('Body HTML length:', bodyHTML.length);
  });
});
