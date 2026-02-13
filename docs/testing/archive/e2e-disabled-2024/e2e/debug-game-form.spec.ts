import { test, expect } from '@playwright/test';

test.describe('Debug Game Form', () => {
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

  test('Debug - Check for React errors', async ({ page }) => {
  // Capture all console messages
  const logs: string[] = [];
  page.on('console', msg => {
    const text = msg.text();
    logs.push(`[${msg.type()}] ${text}`);
    console.log(`[${msg.type()}] ${text}`);
  });

  await page.goto('/#/games/create', { waitUntil: 'networkidle' });

  // Wait for React to render
  await page.waitForTimeout(8000);

  // Take screenshot
  await page.screenshot({ path: 'debug-react-errors.png', fullPage: true });

  // Check if GameForm component exists in DOM
  const gameFormExists = await page.locator('.game-form-container').count();
  console.log('GameForm container count:', gameFormExists);

  // Check for Loading component
  const loadingExists = await page.locator('.loading-container, .loading-spinner').count();
  console.log('Loading component count:', loadingExists);

  // Check for NotFound page
  const notFoundText = await page.locator('text=/404|页面未找到/').count();
  console.log('NotFound count:', notFoundText);

  // List all console logs
  console.log('Total console messages:', logs.length);
  const errors = logs.filter(l => l.includes('[error]'));
  console.log('Errors:', errors);
  });
});
