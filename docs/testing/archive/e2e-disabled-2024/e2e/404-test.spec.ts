import { test, expect } from '@playwright/test';

test.describe('404 Error Detection', () => {
  test.afterEach(async ({ page }) => {
    // 清理测试状态
    await page.evaluate(() => {
      sessionStorage.clear();
      // 清除 Canvas 缓存和游戏上下文
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

  test('404 test - find missing resource', async ({ page }) => {
  // Capture all network requests
  const requests: { url: string; status: number | null }[] = [];

  page.on('request', request => {
    const url = request.url();
    console.log('Request:', url);
  });

  page.on('response', response => {
    const url = response.url();
    const status = response.status();
    requests.push({ url, status });

    if (status >= 400) {
      console.log(`Response ERROR ${status}:`, url);
    }
  });

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
  });

  // 访问事件节点构建器页面
  await page.goto('/#/event-node-builder?game_gid=10000147');

  // Wait
  await page.waitForTimeout(5000);

  // Print all failed requests
  console.log('\n=== Failed Requests ===');
  requests.filter(r => r.status && r.status >= 400).forEach(r => {
    console.log(`${r.status}: ${r.url}`);
  });
  });
});