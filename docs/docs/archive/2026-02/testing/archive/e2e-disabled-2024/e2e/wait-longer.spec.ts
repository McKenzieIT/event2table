import { test, expect } from '@playwright/test';

test('Wait longer for React', async ({ page }) => {
  await page.goto('/#/games');

  // Wait up to 15 seconds for React
  await page.waitForTimeout(15000);

  const appRoot = await page.locator('#app-root').innerHTML();
  console.log('App root HTML length:', appRoot.length);

  if (appRoot.length > 0) {
    console.log('First 500 chars:', appRoot.substring(0, 500));
  }

  // Check for any elements
  const anyElements = await page.locator('#app-root *').count();
  console.log('Children in app-root:', anyElements);
});
