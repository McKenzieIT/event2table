import { test, expect } from '@playwright/test';
import { navigateToPage, PAGE_PATHS } from '../helpers/url-helper';

/**
 * 深入调试：追踪JS加载过程
 */
test.describe('JS加载深度调试', () => {
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

  test('跟踪资源加载过程', async ({ page }) => {
    // 启用网络监控
    const failedResources: string[] = [];
    const loadedResources: string[] = [];

    page.on('response', response => {
      const url = response.url();
      if (url.includes('/frontend/dist/')) {
        if (response.status() === 200) {
          loadedResources.push(url);
          console.log(`✓ Loaded: ${url}`);
        } else {
          failedResources.push(`${url} (${response.status()})`);
          console.log(`✗ Failed: ${url} - ${response.status()}`);
        }
      }
    });

    page.on('requestfailed', request => {
      if (request.url().includes('/frontend/dist/')) {
        console.log(`✗ Request failed: ${request.url()}`);
        console.log(`   Failure: ${request.failure().errorText}`);
      }
    });

    page.on('console', msg => {
      const type = msg.type();
      if (type === 'error') {
        console.log(`❌ Console error: ${msg.text()}`);
      } else if (type === 'warning') {
        console.log(`⚠️  Console warning: ${msg.text()}`);
      } else {
        console.log(`ℹ️  Console log: ${msg.text()}`);
      }
    });

    page.on('pageerror', error => {
      console.log(`❌ Page error: ${error.message}`);
    });

    // 导航到页面
    await navigateToPage(page, PAGE_PATHS.HOME);

    // 等待所有资源加载
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(5000);

    console.log('\n=== Resource Loading Summary ===');
    console.log(`Loaded resources: ${loadedResources.length}`);
    console.log(`Failed resources: ${failedResources.length}`);

    if (failedResources.length > 0) {
      console.log('\nFailed resources:');
      failedResources.forEach(r => console.log(`  - ${r}`));
    }

    // 检查#app-root
    const appRoot = page.locator('#app-root');
    await expect(appRoot).toBeVisible({ timeout: 15000 });

    // 等待React加载
    await page.waitForTimeout(3000);

    // 再次检查
    const appRootHTML = await appRoot.innerHTML();
    console.log(`\n#app-root HTML length after 8s: ${appRootHTML.length}`);
  });

  test('检查JS文件内容和类型', async ({ page }) => {
    // 访问JS文件URL
    const jsUrl = 'http://127.0.0.1:5001/frontend/dist/dist/assets/index-IKtIp4NP.js';

    const response = await page.request.get(jsUrl);
    const jsContent = await response.text();

    console.log('JS file size:', jsContent.length, 'bytes');

    // 检查是否是有效的JS
    if (jsContent.startsWith('import') || jsContent.includes('export default')) {
      console.log('✓ Valid ES module');
    } else {
      console.log('✗ Not a valid ES module');
      console.log('First 200 chars:', jsContent.substring(0, 200));
    }

    // 检查是否包含React相关代码
    const hasReact = jsContent.includes('React') || jsContent.includes('react');
    console.log('Contains React:', hasReact);

    // 检查语法错误（简单检查）
    const hasImportError = jsContent.includes('SyntaxError') || jsContent.includes('Failed to resolve');
    console.log('Has import errors:', hasImportError);
  });

  test('尝试直接在浏览器中运行React应用', async ({ page, context }) => {
    // 创建一个新页面
    const page2 = await context.newPage();

    // 设置超时
    page2.setDefaultTimeout(10000);

    // 直接访问React应用HTML
    await page2.goto('http://127.0.0.1:5001/', {
      waitUntil: 'networkidle'
    });

    // 监听console
    page2.on('console', msg => {
      console.log(`Console: ${msg.type()}: ${msg.text()}`);
    });

    // 等待并检查
    await page2.waitForTimeout(8000);

    const appRoot = page2.locator('#app-root');
    const count = await appRoot.count();
    console.log('#app-root count:', count);

    if (count > 0) {
      const html = await appRoot.innerHTML();
      console.log('#app-root HTML length:', html.length);
    }

    await page2.close();
  });
});
