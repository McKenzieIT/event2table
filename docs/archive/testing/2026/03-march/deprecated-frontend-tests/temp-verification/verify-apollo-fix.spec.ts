/**
 * 验证 Apollo Client 修复后的状态
 */

import { test, expect } from '@playwright/test';

test.describe('Apollo Client Fix Verification', () => {
  test('should capture detailed console errors', async ({ page }) => {
    const consoleLogs: string[] = [];
    const consoleErrors: string[] = [];
    const pageErrors: string[] = [];

    // 收集所有控制台消息
    page.on('console', msg => {
      const text = msg.text();
      const type = msg.type();
      consoleLogs.push(`[${type}] ${text}`);

      if (type === 'error') {
        consoleErrors.push(text);
      }
    });

    // 收集页面错误
    page.on('pageerror', error => {
      pageErrors.push(error.toString());
      console.error('Page Error:', error);
    });

    // 导航到页面
    console.log('导航到 http://localhost:5173');
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle', timeout: 10000 });

    // 等待页面加载
    await page.waitForTimeout(5000);

    // 输出所有控制台日志
    console.log('\n=== 浏览器控制台日志 ===');
    consoleLogs.forEach(log => console.log(log));

    // 输出错误
    if (consoleErrors.length > 0) {
      console.log('\n=== 错误日志 ===');
      consoleErrors.forEach(err => console.error(err));
    }

    if (pageErrors.length > 0) {
      console.log('\n=== 页面错误 ===');
      pageErrors.forEach(err => console.error(err));
    }

    // 检查页面状态
    const content = await page.content();
    const hasLoadingText = content.includes('Loading Event2Table...');

    console.log('\n=== 页面状态 ===');
    console.log(`是否卡在加载: ${hasLoadingText}`);
    console.log(`页面内容长度: ${content.length}`);

    // 检查是否有app-root元素
    const appRoot = await page.$('#app-root');
    console.log(`app-root 元素存在: ${!!appRoot}`);

    if (appRoot) {
      const appRootContent = await appRoot.innerHTML();
      console.log(`app-root 内容长度: ${appRootContent.length}`);
      console.log(`app-root 子元素数量: ${await appRoot.evaluate(el => el.children.length)}`);
    }

    // 截图
    await page.screenshot({
      path: 'test-results/apollo-fix-verification.png',
      fullPage: true
    });
    console.log('\n截图已保存: test-results/apollo-fix-verification.png');

    // 验证Apollo Provider导入
    const hasApolloError = consoleErrors.some(err =>
      err.includes('ApolloProvider') || err.includes('@apollo_client')
    );

    console.log(`\n=== 诊断结果 ===`);
    console.log(`Apollo Provider 相关错误: ${hasApolloError ? '是 ❌' : '否 ✅'}`);
  });
});
