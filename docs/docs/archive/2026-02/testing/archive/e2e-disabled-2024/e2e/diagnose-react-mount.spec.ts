import { test, expect } from '@playwright/test';

test('Diagnose React mount', async ({ page }) => {
  await page.goto('/#/games');

  // Wait longer for React to mount
  await page.waitForTimeout(10000);

  // Check app-root children
  const appRoot = page.locator('#app-root');
  const childrenCount = await appRoot.locator('*').count();
  console.log('App root children count:', childrenCount);

  // Get innerHTML of app-root
  const innerHTML = await appRoot.innerHTML();
  console.log('App root innerHTML length:', innerHTML.length);
  console.log('App root innerHTML (first 500 chars):', innerHTML.substring(0, 500));

  // Check for loading spinners
  const spinners = page.locator('.spinner-border, .loading-container');
  const spinnersCount = await spinners.count();
  console.log('Loading spinners:', spinnersCount);

  // Check for any text
  const allText = await page.locator('*').allTextContents();
  const nonEmptyText = allText.filter(t => t.trim().length > 0);
  console.log('Non-empty text elements:', nonEmptyText.length);
  console.log('Sample texts:', nonEmptyText.slice(0, 10));
});
