/**
 * Simplified Chrome Test Script
 *
 * Quick browser interaction test using Playwright
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://localhost:5173';

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
  console.log('🚀 Starting Simplified Chrome Test...\n');
  console.log(`Frontend URL: ${BASE_URL}\n`);

  // Launch browser
  console.log('🌐 Launching Chrome browser...');
  const browser = await chromium.launch({
    headless: false,
    slowMo: 50
  });

  const context = await browser.newContext();
  const page = await context.newPage();

  // Set viewport
  await page.setViewportSize({ width: 1920, height: 1080 });

  // Monitor console
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log(`[Console Error] ${msg.text()}`);
    }
  });

  try {
    // Test 1: Navigate to homepage
    console.log('\n=== Test 1: Navigate to Homepage ===');
    await page.goto(BASE_URL, { waitUntil: 'networkidle', timeout: 30000 });
    console.log('✅ Homepage loaded');

    // Check title
    const title = await page.title();
    console.log(`Page title: ${title}`);

    // Take screenshot
    const screenshot1 = '/Users/mckenzie/Documents/event2table/docs/testing/simple-test-homepage.png';
    await page.screenshot({ path: screenshot1, fullPage: true });
    console.log(`📸 Screenshot saved: ${screenshot1}`);

    // Check for UI elements
    const elementCount = await page.evaluate(() => {
      return {
        divs: document.querySelectorAll('div').length,
        buttons: document.querySelectorAll('button').length,
        all: document.querySelectorAll('*').length
      };
    });
    console.log(`UI Elements: ${JSON.stringify(elementCount)}`);

    // Test 2: Navigate to parameters page
    console.log('\n=== Test 2: Navigate to Parameters Page ===');
    await page.goto(`${BASE_URL}/#/parameters`, { waitUntil: 'networkidle', timeout: 30000 });
    await sleep(2000);
    console.log('✅ Parameters page loaded');

    // Take screenshot
    const screenshot2 = '/Users/mckenzie/Documents/event2table/docs/testing/simple-test-parameters.png';
    await page.screenshot({ path: screenshot2, fullPage: true });
    console.log(`📸 Screenshot saved: ${screenshot2}`);

    // Check for inputs
    const inputCount = await page.evaluate(() => {
      const inputs = document.querySelectorAll('input');
      return {
        total: inputs.length,
        withPlaceholder: Array.from(inputs).filter(i => i.placeholder).length,
        placeholders: Array.from(inputs).map(i => i.placeholder)
      };
    });
    console.log(`Inputs found: ${JSON.stringify(inputCount)}`);

    // Test 3: Check localStorage
    console.log('\n=== Test 3: Check localStorage ===');
    const gameStorage = await page.evaluate(() => {
      const stored = localStorage.getItem('game-storage');
      return stored;
    });
    console.log(`Game storage: ${gameStorage || 'null (not set yet)'}`);

    // Test 4: Navigate to common params
    console.log('\n=== Test 4: Navigate to Common Params ===');
    await page.goto(`${BASE_URL}/#/common-params`, { waitUntil: 'networkidle', timeout: 30000 });
    await sleep(2000);
    console.log('✅ Common params page loaded');

    // Take screenshot
    const screenshot3 = '/Users/mckenzie/Documents/event2table/docs/testing/simple-test-common-params.png';
    await page.screenshot({ path: screenshot3, fullPage: true });
    console.log(`📸 Screenshot saved: ${screenshot3}`);

    // Test 5: Check for sync button
    const syncButton = await page.locator('button:has-text("同步")').count();
    console.log(`Sync buttons found: ${syncButton}`);

    console.log('\n✅ All basic tests completed!');

  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
  } finally {
    await browser.close();
  }
}

main().catch(console.error);
