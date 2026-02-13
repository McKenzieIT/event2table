import { test, expect } from '@playwright/test';

test.describe('Test with dev server workaround', () => {
  test('check if we can manually render React', async ({ page }) => {
    // Navigate to a simple URL
    await page.goto('/#/');

    // Wait longer
    await page.waitForTimeout(3000);

    // Try to manually trigger React rendering by checking if main.jsx was called
    const hasReactRoot = await page.evaluate(() => {
      // Check if ReactDOM.createRoot was ever called
      return (window as any).__REACT_ROOT_MOUNTED__ === true;
    });
    console.log('React manually mounted flag:', hasReactRoot);

    // Check for any JavaScript errors in the page
    const errors = await page.evaluate(() => {
      return (window as any).__errors__ || [];
    });
    console.log('Captured errors:', errors);
  });
});
