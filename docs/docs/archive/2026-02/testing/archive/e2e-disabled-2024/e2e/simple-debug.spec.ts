import { test, expect } from '@playwright/test';

test.describe('Simple Debug', () => {
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

  test('Simple debug - check game context', async ({ page }) => {
  // 设置游戏数据
  await page.goto('/#/');
  await page.evaluate(() => {
    localStorage.setItem('selectedGameGid', '10000147');
    (window as any).gameData = {
      id: 16,
      gid: '10000147',
      name: '游戏 10000147',
      ods_db: 'ieu_ods',
    };
    console.log('Game data set:', (window as any).gameData);
  });

  // 访问事件节点构建器页面
  await page.goto('/#/event-node-builder?game_gid=10000147');

  // Listen to console messages
  page.on('console', msg => {
    console.log('Browser console:', msg.text());
  });

  // Wait for page to load
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3000);

  // Check if we're on the right page
  const url = page.url();
  console.log('Current URL:', url);

  // Check for any element
  const body = await page.locator('body').textContent();
  console.log('Body text length:', body?.length);

  // Check for loading state
  const loading = await page.locator('.event-node-builder-loading').count();
  console.log('Loading count:', loading);

  // Check for main component
  const main = await page.locator('.event-node-builder').count();
  console.log('Main component count:', main);

  // Take screenshot
  await page.screenshot({ path: 'simple-debug.png' });

  // Try to get React root
  const reactRoot = await page.locator('#root').count();
  console.log('React root count:', reactRoot);
  });
});
