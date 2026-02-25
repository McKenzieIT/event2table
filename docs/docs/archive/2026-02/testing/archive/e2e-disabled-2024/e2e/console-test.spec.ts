import { test, expect } from '@playwright/test';

test.describe('Console Error Check', () => {
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

  test('Console test - check for errors', async ({ page }) => {
  // Capture console messages
  const logs: string[] = [];
  const errors: string[] = [];

  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();
    if (type === 'error') {
      errors.push(text);
      console.log('Browser ERROR:', text);
    } else if (type === 'warn') {
      console.log('Browser WARN:', text);
    } else {
      logs.push(text);
      console.log('Browser LOG:', text);
    }
  });

  page.on('pageerror', error => {
    console.log('Page ERROR:', error.message);
    errors.push(error.message);
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

  // Wait for app-root
  await page.waitForSelector('#app-root', { timeout: 10000 });

  // Wait for React to potentially render
  await page.waitForTimeout(5000);

  // Check content
  const appRootContent = await page.locator('#app-root').innerHTML();
  console.log('app-root content:', appRootContent);

  // Check if there were any errors
  console.log('Total errors:', errors.length);
  console.log('Total logs:', logs.length);

  // Take screenshot
  await page.screenshot({ path: 'console-test.png' });
  });
});
