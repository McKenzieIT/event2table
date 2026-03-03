import { test, expect } from '@playwright/test';
import { navigateToPage, PAGE_PATHS } from '../helpers/url-helper';

test.describe('Debug Events Page', () => {
  test.afterEach(async ({ page }) => {
    // 清理测试状态
    await page.evaluate(() => {
      sessionStorage.clear();
      localStorage.removeItem('selectedGameGid');
      localStorage.removeItem('eventsFilters');
      localStorage.removeItem('eventsSearchQuery');
      if ((window as any).gameData) {
        delete (window as any).gameData;
      }
    });
    await page.waitForTimeout(300);
  });

  test('check what is actually rendered', async ({ page }) => {
    // Listen for console messages
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log('Browser console error:', msg.text());
      }
    });

    // Listen for JavaScript errors
    page.on('pageerror', exception => {
      console.log('Browser page error:', exception);
    });

    await navigateToPage(page, PAGE_PATHS.EVENTS, { gameGid: '3' });
    await page.waitForTimeout(3000);

    // Get page content
    const content = await page.content();
    console.log('Page HTML length:', content.length);

    // Check for app-root
    const appRoot = await page.locator('#app-root').count();
    console.log('app-root count:', appRoot);

    // Check for events-list-page
    const eventsPage = await page.locator('.events-list-page').count();
    console.log('events-list-page count:', eventsPage);

    // Check for any text content in app-root
    const appRootText = await page.locator('#app-root').textContent();
    console.log('app-root text length:', appRootText?.length || 0);
    console.log('app-root text preview:', appRootText?.substring(0, 200) || 'empty');

    // Check if script loaded
    const scripts = await page.locator('script[src*="/frontend/dist/"]').count();
    console.log('React scripts loaded:', scripts);

    // Take screenshot
    await page.screenshot({ path: 'debug-screenshot.png' });
  });
});
