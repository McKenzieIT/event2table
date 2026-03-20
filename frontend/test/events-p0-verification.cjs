/**
 * P0 Bug Fix Verification for Events Pages
 *
 * Bug #1: Events "新增事件" button navigation
 *   Expected: Navigate to #/events/create?game_gid=10000147
 *   Previous: Navigate to #/flows ❌
 *
 * Bug #2: EventForm Cancel button
 *   Expected: Return to Events List
 *   Previous: Cannot return ❌
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// Test configuration
const BASE_URL = 'http://localhost:5173';
const GAME_GID = '10000147';
const SCREENSHOT_DIR = '/Users/mckenzie/Documents/event2table/docs/reports/2026-03-05/screenshots';

// Ensure screenshot directory exists
if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

// Test results
const results = {
  bug1_create_button: { status: 'pending', details: [] },
  bug2_cancel_button: { status: 'pending', details: [] },
  page_load: { status: 'pending', details: [] },
  console_errors: { status: 'pending', details: [] },
  api_calls: { status: 'pending', details: [] }
};

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function runTests() {
  console.log('🚀 Starting Events P0 Verification Tests...\n');

  const browser = await chromium.launch({
    headless: false,
    slowMo: 500
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });

  const page = await context.newPage();

  // Collect console errors
  const consoleErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });

  // Collect API calls
  const apiCalls = [];
  page.on('request', request => {
    const url = request.url();
    if (url.includes('/api/')) {
      apiCalls.push({
        method: request.method(),
        url: url,
        timestamp: new Date().toISOString()
      });
    }
  });

  try {
    // ========== TEST 1: Events List Page Load ==========
    console.log('📋 TEST 1: Loading Events List Page');
    console.log(`   URL: ${BASE_URL}/#/events?game_gid=${GAME_GID}`);

    await page.goto(`${BASE_URL}/#/events?game_gid=${GAME_GID}`, {
      waitUntil: 'networkidle',
      timeout: 10000
    });

    await sleep(2000);

    // Screenshot initial state
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, '01-events-list-initial.png'),
      fullPage: true
    });
    console.log('   ✅ Screenshot saved: 01-events-list-initial.png');

    // Check page structure
    const pageTitle = await page.title();
    console.log(`   Page Title: ${pageTitle}`);

    // Check for Events List elements
    const hasCreateButton = await page.locator('button:has-text("新增事件"), button:has-text("Create Event")').count() > 0;
    const hasSearchInput = await page.locator('input[placeholder*="搜索"], input[placeholder*="search"]').count() > 0;
    const hasTable = await page.locator('table').count() > 0;

    results.page_load.status = hasCreateButton || hasSearchInput || hasTable ? 'PASS' : 'FAIL';
    results.page_load.details = [
      `Page Title: ${pageTitle}`,
      `Has Create Button: ${hasCreateButton}`,
      `Has Search Input: ${hasSearchInput}`,
      `Has Table: ${hasTable}`
    ];

    console.log(`   Status: ${results.page_load.status}`);
    console.log('');

    // ========== TEST 2: P0 Bug #1 - "新增事件" Button Navigation ==========
    console.log('🐛 TEST 2: P0 Bug #1 - "新增事件" Button Navigation');

    // Find and click the "新增事件" button
    const createButtonSelectors = [
      'button:has-text("新增事件")',
      'button:has-text("Create Event")',
      'a:has-text("新增事件")',
      'a:has-text("Create Event")',
      'button:has-text("+")'
    ];

    let createButtonFound = false;
    let createButton = null;

    for (const selector of createButtonSelectors) {
      try {
        createButton = page.locator(selector).first();
        const count = await createButton.count();
        if (count > 0) {
          createButtonFound = true;
          console.log(`   ✅ Found create button with selector: ${selector}`);
          break;
        }
      } catch (e) {
        // Continue to next selector
      }
    }

    if (!createButtonFound) {
      console.log('   ❌ Create button not found!');
      results.bug1_create_button.status = 'FAIL';
      results.bug1_create_button.details = ['Create button not found on page'];
    } else {
      // Screenshot before click
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, '02-before-create-click.png'),
        fullPage: true
      });

      // Click the button
      console.log('   🖱️  Clicking "新增事件" button...');
      await createButton.click();
      await sleep(2000);

      // Check the URL after click
      const currentUrl = page.url();
      console.log(`   Current URL: ${currentUrl}`);

      // Screenshot after click
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, '03-after-create-click.png'),
        fullPage: true
      });

      // Verify navigation
      const expectedUrl = `${BASE_URL}/#/events/create?game_gid=${GAME_GID}`;
      const wrongUrl = `${BASE_URL}/#/flows`;

      if (currentUrl.includes('/events/create')) {
        console.log('   ✅ PASS: Correctly navigated to /events/create');
        results.bug1_create_button.status = 'PASS';
        results.bug1_create_button.details = [
          `Navigated to: ${currentUrl}`,
          'Expected: /events/create',
          'Match: YES'
        ];
      } else if (currentUrl.includes('/flows')) {
        console.log('   ❌ FAIL: Still navigating to /flows (BUG NOT FIXED)');
        results.bug1_create_button.status = 'FAIL';
        results.bug1_create_button.details = [
          `Navigated to: ${currentUrl}`,
          'Expected: /events/create',
          'Match: NO - Still has old bug!'
        ];
      } else {
        console.log(`   ⚠️  WARNING: Unexpected URL: ${currentUrl}`);
        results.bug1_create_button.status = 'PARTIAL';
        results.bug1_create_button.details = [
          `Navigated to: ${currentUrl}`,
          'Expected: /events/create',
          'Match: PARTIAL - URL is different but not /flows'
        ];
      }
    }

    console.log('');

    // ========== TEST 3: Events Create Page Load ==========
    console.log('📋 TEST 3: Events Create Page');

    // Navigate to create page if not already there
    if (!page.url().includes('/events/create')) {
      await page.goto(`${BASE_URL}/#/events/create?game_gid=${GAME_GID}`, {
        waitUntil: 'networkidle',
        timeout: 10000
      });
      await sleep(2000);
    }

    // Screenshot create page
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, '04-events-create-page.png'),
      fullPage: true
    });

    // Check for form elements
    const hasEventNameInput = await page.locator('input[name*="name"], input[placeholder*="name"]').count() > 0;
    const hasCancelButton = await page.locator('button:has-text("取消"), button:has-text("Cancel")').count() > 0;
    const hasSubmitButton = await page.locator('button[type="submit"], button:has-text("提交"), button:has-text("保存")').count() > 0;

    console.log(`   Has Event Name Input: ${hasEventNameInput}`);
    console.log(`   Has Cancel Button: ${hasCancelButton}`);
    console.log(`   Has Submit Button: ${hasSubmitButton}`);
    console.log('');

    // ========== TEST 4: P0 Bug #2 - Cancel Button Navigation ==========
    console.log('🐛 TEST 4: P0 Bug #2 - Cancel Button Navigation');

    if (!hasCancelButton) {
      console.log('   ❌ Cancel button not found!');
      results.bug2_cancel_button.status = 'FAIL';
      results.bug2_cancel_button.details = ['Cancel button not found on create page'];
    } else {
      // Screenshot before cancel
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, '05-before-cancel-click.png'),
        fullPage: true
      });

      // Click cancel button
      console.log('   🖱️  Clicking Cancel button...');
      const cancelButton = page.locator('button:has-text("取消"), button:has-text("Cancel")').first();
      await cancelButton.click();
      await sleep(2000);

      // Check URL after cancel
      const afterCancelUrl = page.url();
      console.log(`   Current URL: ${afterCancelUrl}`);

      // Screenshot after cancel
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, '06-after-cancel-click.png'),
        fullPage: true
      });

      // Verify navigation back to list
      if (afterCancelUrl.includes('/events') && !afterCancelUrl.includes('/create')) {
        console.log('   ✅ PASS: Cancel button returned to events list');
        results.bug2_cancel_button.status = 'PASS';
        results.bug2_cancel_button.details = [
          `Navigated to: ${afterCancelUrl}`,
          'Expected: /events (without /create)',
          'Match: YES'
        ];
      } else {
        console.log('   ❌ FAIL: Cancel button did not return to list');
        results.bug2_cancel_button.status = 'FAIL';
        results.bug2_cancel_button.details = [
          `Navigated to: ${afterCancelUrl}`,
          'Expected: /events (without /create)',
          'Match: NO'
        ];
      }
    }

    console.log('');

    // ========== TEST 5: Console Errors ==========
    console.log('🐛 TEST 5: Console Errors Check');

    await sleep(1000); // Wait for any delayed console errors

    if (consoleErrors.length === 0) {
      console.log('   ✅ PASS: No console errors');
      results.console_errors.status = 'PASS';
      results.console_errors.details = ['No errors found'];
    } else {
      console.log(`   ⚠️  WARNING: Found ${consoleErrors.length} console errors:`);
      consoleErrors.slice(0, 5).forEach((err, i) => {
        console.log(`     ${i + 1}. ${err.substring(0, 100)}...`);
      });
      results.console_errors.status = 'PARTIAL';
      results.console_errors.details = consoleErrors.slice(0, 10);
    }

    console.log('');

    // ========== TEST 6: API Calls ==========
    console.log('🌐 TEST 6: API Calls Verification');

    const eventsApiCalls = apiCalls.filter(call => call.url.includes('/api/events'));
    console.log(`   Found ${eventsApiCalls.length} /api/events calls:`);
    eventsApiCalls.slice(0, 5).forEach((call, i) => {
      console.log(`     ${i + 1}. ${call.method} - ${call.url}`);
    });

    results.api_calls.status = eventsApiCalls.length > 0 ? 'PASS' : 'PARTIAL';
    results.api_calls.details = eventsApiCalls.map(call => ({
      method: call.method,
      url: call.url,
      timestamp: call.timestamp
    }));

    console.log('');

  } catch (error) {
    console.error('❌ Test execution error:', error.message);
  } finally {
    await browser.close();
  }

  // ========== RESULTS SUMMARY ==========
  console.log('\n' + '='.repeat(60));
  console.log('📊 TEST RESULTS SUMMARY');
  console.log('='.repeat(60) + '\n');

  const testResults = [
    { name: 'P0 Bug #1: "新增事件" Button Navigation', result: results.bug1_create_button },
    { name: 'P0 Bug #2: Cancel Button Navigation', result: results.bug2_cancel_button },
    { name: 'Events List Page Load', result: results.page_load },
    { name: 'Console Errors Check', result: results.console_errors },
    { name: 'API Calls Verification', result: results.api_calls }
  ];

  let passCount = 0;
  let failCount = 0;

  testResults.forEach(({ name, result }) => {
    const status = result.status === 'PASS' ? '✅ PASS' : result.status === 'FAIL' ? '❌ FAIL' : '⚠️  PARTIAL';
    const icon = result.status === 'PASS' ? '✅' : result.status === 'FAIL' ? '❌' : '⚠️';

    console.log(`${icon} ${name}`);
    console.log(`   Status: ${status}`);
    if (result.details.length > 0) {
      result.details.slice(0, 3).forEach(detail => {
        console.log(`   - ${typeof detail === 'string' ? detail : JSON.stringify(detail)}`);
      });
    }
    console.log('');

    if (result.status === 'PASS') passCount++;
    if (result.status === 'FAIL') failCount++;
  });

  console.log('='.repeat(60));
  console.log(`Total: ${passCount} PASS, ${failCount} FAIL, ${testResults.length - passCount - failCount} PARTIAL`);
  console.log('='.repeat(60));

  // Generate markdown report
  const reportPath = '/Users/mckenzie/Documents/event2table/docs/reports/2026-03-05/EVENTS-P0-VERIFICATION.md';
  generateMarkdownReport(reportPath, testResults, apiCalls, consoleErrors);

  console.log(`\n📝 Detailed report saved to: ${reportPath}`);
  console.log(`📸 Screenshots saved to: ${SCREENSHOT_DIR}\n`);

  // Return exit code based on P0 bugs
  const p0Fixed = results.bug1_create_button.status === 'PASS' && results.bug2_cancel_button.status === 'PASS';
  if (p0Fixed) {
    console.log('🎉 ALL P0 BUGS VERIFIED AS FIXED!\n');
    return 0;
  } else {
    console.log('⚠️  SOME P0 BUGS ARE NOT FIXED!\n');
    return 1;
  }
}

function generateMarkdownReport(reportPath, testResults, apiCalls, consoleErrors) {
  const date = new Date().toISOString();

  let markdown = `# Events Pages P0 Bug Fix Verification Report

**Date**: ${date}
**Test Tool**: Playwright (Chromium)
**Game GID**: 10000147

## Executive Summary

`;

  const p0Bug1 = testResults[0].result.status;
  const p0Bug2 = testResults[1].result.status;
  const allP0Fixed = p0Bug1 === 'PASS' && p0Bug2 === 'PASS';

  markdown += `- **P0 Bug #1**: "新增事件" Button Navigation - ${p0Bug1 === 'PASS' ? '✅ FIXED' : '❌ NOT FIXED'}\n`;
  markdown += `- **P0 Bug #2**: Cancel Button Navigation - ${p0Bug2 === 'PASS' ? '✅ FIXED' : '❌ NOT FIXED'}\n`;
  markdown += `\n**Overall Status**: ${allP0Fixed ? '✅ ALL P0 BUGS FIXED' : '❌ SOME P0 BUGS REMAIN'}\n\n`;

  markdown += `## Test Environment\n\n`;
  markdown += `- **Base URL**: http://localhost:5173\n`;
  markdown += `- **Test Game**: STAR001 (GID: 10000147)\n`;
  markdown += `- **Browser**: Chromium (Playwright)\n`;
  markdown += `- **Test Type**: Automated E2E\n\n`;

  markdown += `## P0 Bug Fixes\n\n`;

  // Bug #1
  markdown += `### Bug #1: "新增事件" Button Navigation\n\n`;
  markdown += `**Description**: Events List "新增事件" button should navigate to #/events/create, not #/flows\n\n`;
  markdown += `**Expected Behavior**:\n`;
  markdown += `- Click "新增事件" button\n`;
  markdown += `- Navigate to \`#/events/create?game_gid=10000147\`\n\n`;
  markdown += `**Previous Behavior**: ❌ Navigated to \`#/flows\`\n\n`;
  markdown += `**Test Result**: ${p0Bug1 === 'PASS' ? '✅ PASS' : p0Bug1 === 'FAIL' ? '❌ FAIL' : '⚠️ PARTIAL'}\n\n`;
  if (testResults[0].result.details.length > 0) {
    markdown += `**Details**:\n`;
    testResults[0].result.details.forEach(detail => {
      markdown += `- ${detail}\n`;
    });
  }
  markdown += `\n`;

  // Bug #2
  markdown += `### Bug #2: Cancel Button Navigation\n\n`;
  markdown += `**Description**: EventForm Cancel button should return to Events List\n\n`;
  markdown += `**Expected Behavior**:\n`;
  markdown += `- Click "取消" button on Create Event page\n`;
  markdown += `- Navigate back to \`#/events?game_gid=10000147\`\n\n`;
  markdown += `**Previous Behavior**: ❌ Unable to return\n\n`;
  markdown += `**Test Result**: ${p0Bug2 === 'PASS' ? '✅ PASS' : p0Bug2 === 'FAIL' ? '❌ FAIL' : '⚠️ PARTIAL'}\n\n`;
  if (testResults[1].result.details.length > 0) {
    markdown += `**Details**:\n`;
    testResults[1].result.details.forEach(detail => {
      markdown += `- ${detail}\n`;
    });
  }
  markdown += `\n`;

  // Other tests
  markdown += `## Other Test Results\n\n`;

  testResults.slice(2).forEach(({ name, result }) => {
    const status = result.status === 'PASS' ? '✅ PASS' : result.status === 'FAIL' ? '❌ FAIL' : '⚠️ PARTIAL';
    markdown += `### ${name}\n\n`;
    markdown += `**Status**: ${status}\n\n`;
    if (result.details.length > 0) {
      markdown += `**Details**:\n`;
      result.details.slice(0, 5).forEach(detail => {
        markdown += `- ${typeof detail === 'string' ? detail : JSON.stringify(detail)}\n`;
      });
    }
    markdown += `\n`;
  });

  // API Calls
  markdown += `## API Calls\n\n`;
  markdown += `Total \`/api/events\` calls: ${apiCalls.length}\n\n`;
  if (apiCalls.length > 0) {
    markdown += `| Method | URL | Timestamp |\n`;
    markdown += `|--------|-----|-----------|\n`;
    apiCalls.slice(0, 10).forEach(call => {
      markdown += `| ${call.method} | \`${call.url}\` | ${call.timestamp} |\n`;
    });
  }
  markdown += `\n`;

  // Console Errors
  markdown += `## Console Errors\n\n`;
  if (consoleErrors.length === 0) {
    markdown += `✅ No console errors detected\n\n`;
  } else {
    markdown += `⚠️ Found ${consoleErrors.length} console errors:\n\n`;
    consoleErrors.slice(0, 10).forEach((err, i) => {
      markdown += `${i + 1}. \`${err}\`\n`;
    });
    markdown += `\n`;
  }

  // Screenshots
  markdown += `## Screenshots\n\n`;
  markdown += `All screenshots saved to: \`docs/reports/2026-03-05/screenshots/\`\n\n`;
  markdown += `1. \`01-events-list-initial.png\` - Events List initial state\n`;
  markdown += `2. \`02-before-create-click.png\` - Before clicking "新增事件"\n`;
  markdown += `3. \`03-after-create-click.png\` - After clicking "新增事件"\n`;
  markdown += `4. \`04-events-create-page.png\` - Events Create page\n`;
  markdown += `5. \`05-before-cancel-click.png\` - Before clicking "取消"\n`;
  markdown += `6. \`06-after-cancel-click.png\` - After clicking "取消"\n`;
  markdown += `\n`;

  markdown += `## Conclusion\n\n`;
  if (allP0Fixed) {
    markdown += `✅ **All P0 bugs have been successfully fixed!**\n\n`;
    markdown += `The Events pages are now working correctly:\n`;
    markdown += `- "新增事件" button navigates to the correct create page\n`;
    markdown += `- "取消" button returns to the events list\n`;
  } else {
    markdown += `⚠️ **Some P0 bugs remain unfixed**\n\n`;
    markdown += `Please review the failed tests above and make necessary fixes.\n`;
  }
  markdown += `\n`;

  markdown += `---\n`;
  markdown += `*Generated by Playwright automated test*\n`;

  fs.writeFileSync(reportPath, markdown);
  console.log('✅ Markdown report generated');
}

// Run the tests
runTests()
  .then(exitCode => {
    process.exit(exitCode);
  })
  .catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
