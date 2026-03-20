/**
 * 完整修复验证测试
 *
 * 验证以下修复：
 * 1. Apollo Provider 导入路径修复
 * 2. Vite 配置优化
 * 3. Flask CORS 配置
 * 4. 前端不再卡在 "Loading Event2Table..."
 */

import { test, expect } from '@playwright/test';

test.describe('Complete Fix Verification', () => {
  test('should verify all fixes are working', async ({ page }) => {
    const consoleLogs: string[] = [];
    const consoleErrors: string[] = [];
    const networkErrors: string[] = [];

    // 收集控制台日志
    page.on('console', msg => {
      const text = msg.text();
      const type = msg.type();
      consoleLogs.push(`[${type}] ${text}`);

      if (type === 'error') {
        consoleErrors.push(text);
      }
    });

    // 收集网络错误
    page.on('response', response => {
      if (response.status() >= 400) {
        networkErrors.push(`${response.url()} - ${response.status()}`);
      }
    });

    // 收集页面错误
    page.on('pageerror', error => {
      console.error('Page Error:', error);
      networkErrors.push(error.toString());
    });

    console.log('🔵 导航到 http://localhost:5173');
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle', timeout: 15000 });

    // 等待页面加载
    await page.waitForTimeout(5000);

    // 输出所有控制台日志
    console.log('\n=== 浏览器控制台日志 ===');
    consoleLogs.slice(-20).forEach(log => console.log(log));

    // 检查 CORS 错误
    const corsErrors = consoleErrors.filter(err =>
      err.includes('CORS') || err.includes('Access-Control-Allow-Origin')
    );

    // 检查 Apollo 错误
    const apolloErrors = consoleErrors.filter(err =>
      err.includes('ApolloProvider') || err.includes('@apollo_client')
    );

    // 检查是否卡在加载状态
    const content = await page.content();
    const hasLoadingText = content.includes('Loading Event2Table...');
    const hasReactRoot = await page.$('#app-root') !== null;
    const appRootHasChildren = await page.evaluate(() => {
      const appRoot = document.getElementById('app-root');
      return appRoot && appRoot.children.length > 0;
    });

    // 输出测试结果
    console.log('\n=== 测试结果 ===');
    console.log(`CORS 错误: ${corsErrors.length > 0 ? '❌ 发现' : '✅ 无'}`);
    console.log(`Apollo 错误: ${apolloErrors.length > 0 ? '❌ 发现' : '✅ 无'}`);
    console.log(`卡在加载: ${hasLoadingText ? '❌ 是' : '✅ 否'}`);
    console.log(`React Root 存在: ${hasReactRoot ? '✅ 是' : '❌ 否'}`);
    console.log(`React Root 有内容: ${appRootHasChildren ? '✅ 是' : '❌ 否'}`);
    console.log(`网络错误数量: ${networkErrors.length}`);

    if (corsErrors.length > 0) {
      console.log('\n=== CORS 错误详情 ===');
      corsErrors.forEach(err => console.error(err));
    }

    if (apolloErrors.length > 0) {
      console.log('\n=== Apollo 错误详情 ===');
      apolloErrors.forEach(err => console.error(err));
    }

    if (networkErrors.length > 0) {
      console.log('\n=== 网络错误详情 ===');
      networkErrors.forEach(err => console.error(err));
    }

    // 断言验证
    expect(corsErrors.length, 'CORS 错误').toBe(0);
    expect(apolloErrors.length, 'Apollo 错误').toBe(0);
    expect(hasLoadingText, '不应卡在加载状态').toBe(false);
    expect(hasReactRoot, 'React Root 应该存在').toBe(true);

    // 截图
    await page.screenshot({
      path: 'test-results/complete-fix-verification.png',
      fullPage: true
    });
    console.log('\n✅ 截图已保存: test-results/complete-fix-verification.png');

    console.log('\n✅ 所有修复验证通过！');
  });
});
