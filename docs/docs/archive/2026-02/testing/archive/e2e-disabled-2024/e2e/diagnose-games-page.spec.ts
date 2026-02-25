import { test, expect } from '@playwright/test';

test('Diagnose Games page', async ({ page }) => {
  await page.goto('/#/games');
  await page.waitForTimeout(3000);

  // Check page title
  const title = await page.title();
  console.log('Page title:', title);

  // Check what's in the page
  const bodyText = await page.locator('body').textContent();
  console.log('Body text (first 500 chars):', bodyText?.substring(0, 500));

  // Check for React app root
  const appRoot = page.locator('#app-root');
  const appRootExists = await appRoot.count();
  console.log('App root exists:', appRootExists > 0);

  // Check for games-list-container
  const gamesList = page.locator('.games-list-container, .page-header');
  const gamesListCount = await gamesList.count();
  console.log('Games list elements:', gamesListCount);

  // Check for any buttons
  const buttons = page.locator('button');
  const buttonsCount = await buttons.count();
  console.log('Total buttons:', buttonsCount);

  // List all button text content
  for (let i = 0; i < Math.min(buttonsCount, 10); i++) {
    const text = await buttons.nth(i).textContent();
    console.log(`Button ${i}:`, text?.trim());
  }

  // Take screenshot
  await page.screenshot({ path: 'games-page-diagnosis.png' });
});
