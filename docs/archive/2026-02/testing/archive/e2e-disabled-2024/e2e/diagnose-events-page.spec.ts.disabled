import { test, expect } from '@playwright/test';

test('Diagnose Events page', async ({ page }) => {
  await page.goto('/#/events');
  await page.waitForTimeout(3000);

  // Check page title
  const title = await page.title();
  console.log('Page title:', title);

  // Check what's in app-root
  const appRootHTML = await page.locator('#app-root').innerHTML();
  console.log('App root HTML length:', appRootHTML.length);

  // Check for game prompt
  const gamePrompt = page.locator('.select-game-prompt');
  const promptCount = await gamePrompt.count();
  console.log('Game prompt count:', promptCount);

  // Check for add-event-button
  const addButton = page.locator('[data-testid="add-event-button"]');
  const buttonCount = await addButton.count();
  console.log('Add event button count:', buttonCount);

  // Check for all buttons
  const allButtons = page.locator('button');
  const allButtonsCount = await allButtons.count();
  console.log('All buttons count:', allButtonsCount);

  // List button texts
  for (let i = 0; i < Math.min(allButtonsCount, 10); i++) {
    const text = await allButtons.nth(i).textContent();
    console.log('Button', i, ':', text?.trim().substring(0, 50));
  }

  // Screenshot
  await page.screenshot({ path: 'events-page-diagnosis.png', fullPage: true });
});
