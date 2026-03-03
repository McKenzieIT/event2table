import { test, expect } from '@playwright/test';

test('Manual React init check', async ({ page }) => {
  await page.goto('/#/');

  // Wait for page load
  await page.waitForTimeout(5000);

  // Check if React is loaded globally
  const reactLoaded = await page.evaluate(() => {
    return typeof (window as any).React !== 'undefined' ||
           typeof (window as any).ReactDOM !== 'undefined';
  });
  console.log('React globally available:', reactLoaded);

  // Check if there are any script errors
  const hasError = await page.evaluate(() => {
    return document.body.classList.contains('error') ||
           document.querySelector('.error-state') !== null;
  });
  console.log('Has error elements:', hasError);

  // Check document ready state
  const readyState = await page.evaluate(() => document.readyState);
  console.log('Document readyState:', readyState);

  // Check for module scripts
  const moduleScripts = await page.evaluate(() => {
    const scripts = Array.from(document.querySelectorAll('script[type="module"]'));
    return scripts.map(s => ({
      src: s.getAttribute('src'),
      loaded: s.getAttribute('data-loaded'),
      error: s.getAttribute('data-error')
    }));
  });
  console.log('Module scripts:', JSON.stringify(moduleScripts, null, 2));
});
