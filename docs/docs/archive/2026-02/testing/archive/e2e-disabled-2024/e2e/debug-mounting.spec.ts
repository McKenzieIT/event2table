import { test, expect } from '@playwright/test';
import { navigateToPage, PAGE_PATHS } from '../helpers/url-helper';

test.describe('Debug: React App Mounting', () => {
  test.afterEach(async ({ page }) => {
    // 清理测试状态
    await page.evaluate(() => {
      sessionStorage.clear();
      localStorage.removeItem('selectedGameGid');
      localStorage.removeItem('gamesFilters');
      localStorage.removeItem('gamesSearchQuery');
      if ((window as any).gameData) {
        delete (window as any).gameData;
      }
    });
    await page.waitForTimeout(300);
  });

  test('should check for React initialization and errors', async ({ page }) => {
    // Add error handlers before navigating
    page.on('pageerror', error => {
      console.log(`PAGE ERROR: ${error.toString()}`);
      console.log(`Stack: ${error.stack}`);
    });

    page.on('load', () => {
      console.log('PAGE LOADED');
    });

    page.on('domcontentloaded', () => {
      console.log('DOM CONTENT LOADED');
    });

    // Navigate to hash route
    await navigateToPage(page, PAGE_PATHS.GAMES);

    // Wait for page to load
    await page.waitForLoadState('domcontentloaded');
    console.log('After domcontentloaded');

    // Wait for React to mount
    await page.waitForTimeout(5000);
    console.log('After 5s wait');

    // Check #app-root
    const appRootHTML = await page.locator('#app-root').innerHTML();
    console.log(`#app-root HTML length: ${appRootHTML.length}`);
    console.log(`#app-root HTML: ${appRootHTML.substring(0, 200)}`);

    // Check if React has initialized by looking for React-specific elements
    const hasReactRoot = await page.evaluate(() => {
      return !!window.__REACT_DEVTOOLS_GLOBAL_HOOK__;
    });
    console.log(`React DevTools detected: ${hasReactRoot}`);

    // Check body children
    const bodyChildren = await page.locator('body > *').count();
    console.log(`Body has ${bodyChildren} direct children`);

    // List all body children
    for (let i = 0; i < Math.min(bodyChildren, 10); i++) {
      const tagName = await page.locator(`body > *:nth-child(${i + 1})`).evaluate(el => el.tagName);
      const id = await page.locator(`body > *:nth-child(${i + 1})`).evaluate(el => el.id).catch(() => '');
      const className = await page.locator(`body > *:nth-child(${i + 1})`).evaluate(el => el.className).catch(() => '');
      console.log(`  Child ${i + 1}: <${tagName}> id="${id}" class="${className}"`);
    }

    // Check for any React-specific attributes
    const hasReactAttributes = await page.evaluate(() => {
      const appRoot = document.getElementById('app-root');
      if (!appRoot) return false;
      // Check for React internal properties
      return Object.keys(appRoot).some(key => key.startsWith('_react') || key.startsWith('__react'));
    });
    console.log(`Has React internal properties: ${hasReactAttributes}`);
  });
});
