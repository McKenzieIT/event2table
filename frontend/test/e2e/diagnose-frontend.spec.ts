/**
 * 诊断前端加载问题
 *
 * 使用 Playwright 获取浏览器控制台错误
 */

import { test, expect } from '@playwright/test';

test.describe('Frontend Loading Diagnosis', () => {
  test('should capture console errors', async ({ page }) => {
    // 收集所有控制台消息
    const consoleLogs: string[] = [];
    const consoleErrors: string[] = [];

    page.on('console', msg => {
      const text = msg.text();
      consoleLogs.push(`[${msg.type()}] ${text}`);

      if (msg.type() === 'error') {
        consoleErrors.push(text);
      }
    });

    // 导航到页面
    await page.goto('http://localhost:5173');

    // 等待页面加载
    await page.waitForTimeout(5000);

    // 输出所有控制台日志
    console.log('\n=== 浏览器控制台日志 ===');
    consoleLogs.forEach(log => console.log(log));

    // 输出错误日志
    if (consoleErrors.length > 0) {
      console.log('\n=== 错误日志 ===');
      consoleErrors.forEach(err => console.error(err));
    }

    // 检查页面状态
    const content = await page.content();
    const hasLoadingText = content.includes('Loading Event2Table...');

    console.log('\n=== 页面状态 ===');
    console.log(`是否卡在加载: ${hasLoadingText}`);
    console.log(`页面内容长度: ${content.length}`);

    // 截图
    await page.screenshot({ path: 'test-results/frontend-loading-diagnosis.png' });
    console.log('\n截图已保存: test-results/frontend-loading-diagnosis.png');
  });
});
