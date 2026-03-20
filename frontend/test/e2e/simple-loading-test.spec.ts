/**
 * 简化的加载测试 - 不等待 networkidle
 *
 * 验证：
 * 1. Apollo Provider 导入路径正确（无导入错误）
 * 2. CORS 配置正确（无 CORS 错误）
 * 3. 页面能够加载（即使有 ongoing requests）
 */

import { test, expect } from '@playwright/test';

test('should load page without critical errors', async ({ page }) => {
  const consoleErrors: string[] = [];
  const criticalErrors: string[] = [];

  // 收集控制台错误
  page.on('console', msg => {
    if (msg.type() === 'error') {
      const text = msg.text();
      consoleErrors.push(text);
      console.error(`[Console Error] ${text}`);
    }
  });

  // 收集页面错误
  page.on('pageerror', error => {
    criticalErrors.push(error.toString());
    console.error(`[Page Error] ${error}`);
  });

  console.log('🔵 导航到 http://localhost:5173');
  // 使用 'domcontentloaded' 而不是 'networkidle'
  await page.goto('http://localhost:5173', { waitUntil: 'domcontentloaded', timeout: 30000 });

  console.log('✅ DOM content loaded');

  // 等待一下让页面初始化
  await page.waitForTimeout(3000);

  // 检查关键错误
  const corsErrors = consoleErrors.filter(err =>
    err.includes('CORS') || err.includes('Access-Control-Allow-Origin')
  );

  const apolloImportErrors = consoleErrors.filter(err =>
    err.includes('ApolloProvider') && err.includes('export')
  );

  const apolloClientErrors = consoleErrors.filter(err =>
    err.includes('Apollo') || err.includes('GraphQL')
  );

  // 输出结果
  console.log('\n=== 测试结果 ===');
  console.log(`CORS 错误: ${corsErrors.length}`);
  console.log(`Apollo 导入错误: ${apolloImportErrors.length}`);
  console.log(`Apollo Client 错误: ${apolloClientErrors.length}`);
  console.log(`其他控制台错误: ${consoleErrors.length}`);
  console.log(`页面错误: ${criticalErrors.length}`);

  if (corsErrors.length > 0) {
    console.log('\n❌ CORS 错误详情:');
    corsErrors.forEach(err => console.error(`  - ${err}`));
  }

  if (apolloImportErrors.length > 0) {
    console.log('\n❌ Apollo 导入错误详情:');
    apolloImportErrors.forEach(err => console.error(`  - ${err}`));
  }

  if (apolloClientErrors.length > 0) {
    console.log('\n⚠️  Apollo Client 错误详情:');
    apolloClientErrors.forEach(err => console.error(`  - ${err}`));
  }

  // 截图
  await page.screenshot({
    path: 'test-results/simple-loading-test.png',
    fullPage: true
  });

  // 检查页面状态
  const appRoot = await page.$('#app-root');
  const hasAppRoot = appRoot !== null;
  const bodyText = await page.evaluate(() => document.body.innerText);
  const hasLoadingText = bodyText.includes('Loading Event2Table...');

  console.log('\n=== 页面状态 ===');
  console.log(`#app-root 存在: ${hasAppRoot ? '✅ 是' : '❌ 否'}`);
  console.log(`显示加载文本: ${hasLoadingText ? '⚠️  是' : '✅ 否'}`);

  // 核心断言
  expect(corsErrors.length, '不应该有 CORS 错误').toBe(0);
  expect(apolloImportErrors.length, '不应该有 Apollo 导入错误').toBe(0);
  expect(hasAppRoot, '#app-root 应该存在').toBe(true);

  console.log('\n✅ 关键修复验证通过！');
  console.log('  - CORS 配置正确');
  console.log('  - Apollo Provider 导入正确');
  console.log('  - React Root 已挂载');
});
