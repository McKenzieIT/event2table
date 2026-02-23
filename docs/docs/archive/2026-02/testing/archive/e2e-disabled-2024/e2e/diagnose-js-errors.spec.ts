import { test, expect } from '@playwright/test';

test('Diagnose JS errors', async ({ page }) => {
  // Collect console errors
  const errors: string[] = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });

  await page.goto('/#/games');
  await page.waitForTimeout(5000);

  // Check for errors
  console.log('Console errors:', errors.length);
  errors.forEach(err => console.log('  -', err));

  // Check if script loaded
  const scriptTags = await page.locator('script[src]').all();
  console.log('Script tags:', scriptTags.length);
  for (const script of scriptTags) {
    const src = await script.getAttribute('src');
    console.log('  -', src);
  }

  // Check window location
  const hash = await page.evaluate(() => window.location.hash);
  console.log('URL hash:', hash);
});
