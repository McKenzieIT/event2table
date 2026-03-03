import { test, expect } from '@playwright/test';
import { navigateToPage, PAGE_PATHS } from '../helpers/url-helper';

test.describe('Debug Main Layout', () => {
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

  test('Debug: Check MainLayout rendering', async ({ page }) => {
  // Capture all console messages
  page.on('console', msg => {
    console.log('BROWSER CONSOLE:', msg.type(), msg.text());
  });

  // Capture network requests
  const apiCalls: string[] = [];
  page.on('request', request => {
    const url = request.url();
    if (url.includes('/api/')) {
      console.log('API REQUEST:', url);
      apiCalls.push(url);
    }
  });

  // Navigate to canvas page
  console.log('TESTER: Navigating to canvas page...');
  await navigateToPage(page, PAGE_PATHS.CANVAS, { gameGid: '10000147' });

  // Wait for app-root
  console.log('TESTER: Waiting for app-root...');
  await page.waitForSelector('#app-root', { state: 'visible', timeout: 10000 });
  console.log('TESTER: app-root is visible');

  // Wait for React to initialize
  await page.waitForTimeout(8000);

  // Check what's in the DOM
  const appRootHTML = await page.locator('#app-root').innerHTML();
  console.log('TESTER: app-root innerHTML length:', appRootHTML.length);

  // Check gameData
  const gameData = await page.evaluate(() => {
    return {
      gameData: (window as any).gameData,
      locationHash: window.location.hash,
      locationSearch: window.location.search,
      hasMainLayout: !!(document as any).querySelector('.app-shell'),
      hasSidebar: !!(document as any).querySelector('.sidebar'),
    };
  });

  console.log('TESTER: Final state:', JSON.stringify(gameData, null, 2));
  console.log('TESTER: Total API calls:', apiCalls.length);
  console.log('TESTER: API calls:', apiCalls);

  // This test will always pass - it's just for debugging
  expect(true).toBe(true);
  });
});
