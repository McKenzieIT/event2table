import { test, expect } from '@playwright/test';
import { navigateToPage, PAGE_PATHS } from '../helpers/url-helper';

test.describe('Console Diagnostic', () => {
  test.afterEach(async ({ page }) => {
    await page.evaluate(() => {
      sessionStorage.clear();
      localStorage.removeItem('selectedGameGid');
      if ((window as any).gameData) {
        delete (window as any).gameData;
      }
    });
    await page.waitForTimeout(300);
  });

  test('Console Error Diagnostic', async ({ page }) => {
  const allLogs: any[] = [];

  // Capture all console messages
  page.on('console', msg => {
    allLogs.push({
      type: msg.type(),
      text: msg.text(),
      location: msg.location()
    });
  });

  // Capture page errors
  page.on('pageerror', error => {
    allLogs.push({
      type: 'pageerror',
      message: error.message,
      stack: error.stack
    });
  });

  console.log('Navigating to home...');
  await navigateToPage(page, PAGE_PATHS.HOME, { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);

  // Check body
  const bodyCheck = await page.evaluate(() => {
    return {
      bodyHTML: document.body.innerHTML.length,
      hasAppRoot: !!document.getElementById('app-root'),
      appRootHTML: document.getElementById('app-root')?.innerHTML.length || 0
    };
  });

  console.log('\n=== Page State ===');
  console.log('Body HTML length:', bodyCheck.bodyHTML);
  console.log('Has app-root:', bodyCheck.hasAppRoot);
  console.log('app-root HTML length:', bodyCheck.appRootHTML);

  console.log('\n=== Console Logs ===');
  allLogs.forEach((log, i) => {
    console.log(`[${i}] ${log.type}: ${log.text || log.message}`);
    if (log.location) console.log('   Location:', log.location);
    if (log.stack) console.log('   Stack:', log.stack);
  });

  // Filter important errors
  const errors = allLogs.filter(l => l.type === 'error' || l.type === 'pageerror');
  console.log(`\n=== Total Errors: ${errors.length} ===`);

  // This test is informational
  test.skip(true, 'Diagnostic complete');
  });
});
