import { test, expect } from '@playwright/test';

test('Get detailed browser console output', async ({ page }) => {
  const logs: string[] = [];
  const errors: string[] = [];
  const warnings: string[] = [];

  page.on('console', msg => {
    const text = msg.text();
    const type = msg.type();
    if (type === 'error') errors.push(text);
    else if (type === 'warning') warnings.push(text);
    else logs.push('[' + type + '] ' + text);
  });

  page.on('pageerror', error => {
    console.log('Page error:', error.toString());
  });

  await page.goto('/#/games');
  await page.waitForTimeout(5000);

  console.log('=== Warnings ===');
  warnings.forEach(w => console.log('  -', w));

  console.log('=== Errors ===');
  errors.forEach(e => console.log('  -', e));

  const moduleExecuted = await page.evaluate(() => {
    const scripts = Array.from(document.querySelectorAll('script[type="module"]'));
    return {
      scriptCount: scripts.length,
      hasAnyReact: typeof (window as any).React !== 'undefined' || typeof (window as any).ReactDOM !== 'undefined',
      bodyChildren: document.body.children.length
    };
  });

  console.log('=== Module Status ===');
  console.log(JSON.stringify(moduleExecuted, null, 2));
});
