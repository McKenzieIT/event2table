import { test, expect } from '@playwright/test';

test.describe('Console Error Detection', () => {
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

  test('Check browser console errors', async ({ page }) => {
    const errors: string[] = [];
    const warnings: string[] = [];

  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();

    if (type === 'error') {
      errors.push(text);
      console.log('❌ Console Error:', text);
    } else if (type === 'warning') {
      warnings.push(text);
      console.log('⚠️  Console Warning:', text);
    } else {
      console.log('ℹ️  Console Log:', text);
    }
  });

  page.on('pageerror', error => {
    console.log('❌ Page Error:', error.toString());
    errors.push(error.toString());
  });

  page.on('requestfailed', request => {
    const failure = request.failure();
    if (failure) {
      console.log('❌ Request Failed:', request.url(), failure.errorText);
      errors.push(`Request failed: ${request.url()} - ${failure.errorText}`);
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

  console.log('\n=== Navigating to event-node-builder ===');
  await page.goto('/#/event-node-builder?game_gid=10000147');

  // Wait for app-root
  try {
    await page.waitForSelector('#app-root', { timeout: 10000 });
    console.log('✓ Found #app-root');
  } catch (e) {
    console.log('❌ #app-root not found');
  }

  // Wait for potential React rendering
  await page.waitForTimeout(5000);

  // Check what's in app-root
  const appRootHTML = await page.locator('#app-root').innerHTML();
  console.log('\n#app-root HTML length:', appRootHTML.length);
  console.log('#app-root HTML:', appRootHTML.substring(0, 500));

  // Check body
  const bodyHTML = await page.locator('body').innerHTML();
  console.log('\nBody HTML length:', bodyHTML.length);

  // Screenshot
  await page.screenshot({ path: 'check-errors.png', fullPage: true });

  // Summary
  console.log('\n=== Summary ===');
  console.log('Errors:', errors.length);
  console.log('Warnings:', warnings.length);

  if (errors.length > 0) {
    console.log('\n=== All Errors ===');
    errors.forEach((err, i) => console.log(`${i + 1}. ${err}`));
  }
  });
});
