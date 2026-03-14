import { test, expect } from '@playwright/test';

test('Capture console errors on page load', async ({ page }) => {
  // 收集所有console消息
  const consoleLogs: string[] = [];
  const consoleErrors: string[] = [];
  const consoleWarnings: string[] = [];

  page.on('console', msg => {
    const text = `[${msg.type()}] ${msg.text()}`;
    
    if (msg.type() === 'error') {
      consoleErrors.push(text);
    } else if (msg.type() === 'warning') {
      consoleWarnings.push(text);
    } else {
      consoleLogs.push(text);
    }
  });

  // 监听页面错误
  const pageErrors: string[] = [];
  page.on('pageerror', error => {
    pageErrors.push(error.toString());
    console.error('Page error:', error);
  });

  // 监听请求失败
  const failedRequests: string[] = [];
  page.on('requestfailed', request => {
    failedRequests.push(`${request.method()} ${request.url()} - ${request.failure()?.errorText}`);
  });

  // 导航到页面
  console.log('Navigating to http://localhost:5173/#/');
  await page.goto('http://localhost:5173/#/', { waitUntil: 'networkidle' });

  // 等待5秒让React尝试挂载
  await page.waitForTimeout(5000);

  // 检查app-root状态
  const appRoot = await page.locator('#app-root');
  const appRootHTML = await appRoot.innerHTML();
  const hasContent = appRootHTML.length > 0;

  // 获取页面标题和URL
  const title = await page.title();
  const url = page.url();

  // 输出结果
  console.log('\n=== Page State ===');
  console.log(`Title: ${title}`);
  console.log(`URL: ${url}`);
  console.log(`app-root has content: ${hasContent}`);
  console.log(`app-root HTML length: ${appRootHTML.length}`);
  console.log(`app-root HTML preview: ${appRootHTML.substring(0, 200)}`);

  console.log('\n=== Console Logs ===');
  consoleLogs.forEach(log => console.log(log));

  console.log('\n=== Console Warnings ===');
  consoleWarnings.forEach(warning => console.warn(warning));

  console.log('\n=== Console Errors ===');
  consoleErrors.forEach(error => console.error(error));

  console.log('\n=== Page Errors ===');
  pageErrors.forEach(error => console.error(error));

  console.log('\n=== Failed Requests ===');
  failedRequests.forEach(req => console.error(req));

  // 截图
  await page.screenshot({ path: 'frontend/tests/debug/screenshots/console-errors.png' });
  console.log('\nScreenshot saved to: frontend/tests/debug/screenshots/console-errors.png');

  // 断言
  expect(hasContent, 'React should have mounted').toBeTruthy();
});
