import { test, expect } from '@playwright/test';
import { navigateToPage, PAGE_PATHS } from '../helpers/url-helper';

test.describe('Debug JS Loading', () => {
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

  test('Debug: Check if JS loads and React mounts', async ({ page }) => {
    // Capture console
    page.on('console', msg => {
      console.log('BROWSER:', msg.type(), msg.text());
    });

    console.log('Navigating...');
    await navigateToPage(page, PAGE_PATHS.CANVAS, { gameGid: '10000147' });
    await page.waitForTimeout(8000);

    const domState = await page.evaluate(() => {
      const appRoot = document.getElementById('app-root');
      return {
        appRootChildren: appRoot ? appRoot.children.length : 0,
        locationHash: window.location.hash,
        windowGameData: (window as any).gameData
      };
    });

    console.log('DOM State:', JSON.stringify(domState));
    expect(true).toBe(true);
  });
});
