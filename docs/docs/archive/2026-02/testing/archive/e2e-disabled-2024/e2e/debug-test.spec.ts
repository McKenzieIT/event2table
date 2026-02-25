import { test, expect } from '@playwright/test';

test.describe('Debug Test', () => {
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

  test('Debug - Check page content', async ({ page }) => {
  // 设置游戏数据
  await page.goto('/#/');
  await page.evaluate(() => {
    localStorage.setItem('selectedGameGid', '10000147');
    window.gameData = {
      id: 16,
      gid: '10000147',
      name: '游戏 10000147',
      ods_db: 'ieu_ods',
    };
  });

  // 访问事件节点构建器页面
  await page.goto('/#/event-node-builder?game_gid=10000147');
  await page.waitForLoadState('networkidle');

  // Take a screenshot
  await page.screenshot({ path: 'debug-screenshot.png', fullPage: true });

  // Get page content
  const content = await page.content();
  console.log('Page length:', content.length);

  // Check for specific elements
  const eventNodeBuilder = await page.locator('.event-node-builder').count();
  console.log('event-node-builder count:', eventNodeBuilder);

  const loadingDiv = await page.locator('.event-node-builder-loading').count();
  console.log('event-node-builder-loading count:', loadingDiv);

  // Wait for 5 seconds and try again
  await page.waitForTimeout(5000);

  const eventNodeBuilder2 = await page.locator('.event-node-builder').count();
  console.log('After 5s - event-node-builder count:', eventNodeBuilder2);

  // Take another screenshot
  await page.screenshot({ path: 'debug-screenshot-5s.png', fullPage: true });
  });
});
