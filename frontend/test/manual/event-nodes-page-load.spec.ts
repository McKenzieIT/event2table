import { test, expect } from '@playwright/test';

test.describe('Event Nodes Page - Manual Test', () => {
  test('should load without "Cannot read properties of undefined" error', async ({ page }) => {
    // 监听所有控制台消息
    const consoleErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // 访问 Event Nodes 页面
    await page.goto('http://localhost:5173/#/event-nodes?game_gid=10000147');

    // 等待页面完全加载
    await page.waitForTimeout(5000);

    // 检查是否有 "Cannot read properties of undefined" 错误
    const undefinedErrors = consoleErrors.filter(err =>
      err.includes('Cannot read properties of undefined') ||
      err.includes('reading \'find\'')
    );

    console.log('控制台错误数量:', consoleErrors.length);
    console.log('Undefined 属性错误:', undefinedErrors.length);

    // 验证：不应该有 undefined 属性错误
    expect(undefinedErrors.length).toBe(0);

    // 验证：页面标题应该存在
    const title = await page.title();
    expect(title).toBeTruthy();

    console.log('✅ 页面加载成功，没有 undefined 属性错误');
  });

  test('should display event nodes table', async ({ page }) => {
    await page.goto('http://localhost:5173/#/event-nodes?game_gid=10000147');

    // 等待表格加载
    await page.waitForTimeout(3000);

    // 检查页面是否有内容
    const bodyText = await page.evaluate(() => document.body.innerText);
    console.log('页面文本长度:', bodyText.length);

    // 页面应该有内容（不是空白页）
    expect(bodyText.length).toBeGreaterThan(0);

    console.log('✅ 页面有内容显示');
  });
});
