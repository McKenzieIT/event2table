/**
 * Phase 1-5 E2E Testing Script v2
 *
 * Uses Playwright to test all features implemented in Phase 1-5
 * Run: node test-phase-1-5-v2.cjs
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://localhost:5173';
const API_BASE = 'http://127.0.0.1:5001';
const SCREENSHOT_DIR = '/Users/mckenzie/Documents/event2table/docs/testing/screenshots';

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Test results
const results = {
  passed: [],
  failed: [],
  warnings: []
};

function log(phase, feature, status, message) {
  const entry = { phase, feature, status, message, timestamp: new Date().toISOString() };
  if (status === '✅') {
    results.passed.push(entry);
  } else if (status === '❌') {
    results.failed.push(entry);
  } else {
    results.warnings.push(entry);
  }
  console.log(`[${status}] ${phase} - ${feature}: ${message}`);
}

async function waitForReactApp(page, timeout = 30000) {
  console.log('Waiting for React app to load...');
  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    const isLoaded = await page.evaluate(() => {
      // Check if React has mounted
      const appRoot = document.querySelector('#root, #app-root, [data-testid="app"]');
      if (!appRoot) return false;

      // Check if body has content
      const bodyChildren = document.body.children.length;
      if (bodyChildren === 0) return false;

      // Check if there are elements
      const hasElements = document.querySelectorAll('div, button, input').length > 5;
      return hasElements;
    });

    if (isLoaded) {
      console.log('React app loaded!');
      return true;
    }

    await sleep(500);
  }

  console.log('Timeout waiting for React app');
  return false;
}

async function testPhase1VisualEffects(page) {
  console.log('\n=== Phase 1: Visual Effects ===');

  try {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });

    // Wait for React app
    const loaded = await waitForReactApp(page);
    if (!loaded) {
      log('Phase 1', 'React app loading', '❌', 'React app did not load in time');
    }

    await sleep(3000);

    // Take a screenshot
    const screenshotPath = path.join(SCREENSHOT_DIR, 'phase1-homepage.png');
    await page.screenshot({ path: screenshotPath, fullPage: true });
    log('Phase 1', 'Screenshot', '✅', `Screenshot saved to ${screenshotPath}`);

    // Check background color
    const styles = await page.evaluate(() => {
      const body = document.body;
      const appRoot = document.querySelector('#root, #app-root');
      const target = appRoot || body;

      const computed = window.getComputedStyle(target);
      return {
        background: computed.background,
        backgroundColor: computed.backgroundColor,
        backgroundImage: computed.backgroundImage,
        bodyChildren: document.body.children.length,
        rootChildren: appRoot ? appRoot.children.length : 0
      };
    });

    console.log('Page styles:', styles);
    log('Phase 1', 'Page structure', '✅', `Body children: ${styles.bodyChildren}, Root: ${styles.rootChildren}`);

    // Check for UI elements
    const elementCounts = await page.evaluate(() => {
      return {
        divs: document.querySelectorAll('div').length,
        buttons: document.querySelectorAll('button').length,
        inputs: document.querySelectorAll('input').length,
        cards: document.querySelectorAll('[class*="card"], [class*="Card"]').length
      };
    });

    console.log('Element counts:', elementCounts);
    log('Phase 1', 'UI elements', '✅', `Divs: ${elementCounts.divs}, Buttons: ${elementCounts.buttons}, Cards: ${elementCounts.cards}`);

  } catch (error) {
    log('Phase 1', 'Visual effects', '❌', `Error: ${error.message}`);
  }
}

async function testPhase2GameManagement(page) {
  console.log('\n=== Phase 2: Game State Management ===');

  try {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await waitForReactApp(page);
    await sleep(2000);

    // Check localStorage
    const gameStorage = await page.evaluate(() => {
      const stored = localStorage.getItem('game-storage');
      if (stored) {
        try {
          return JSON.parse(stored);
        } catch (e) {
          return { error: e.message, raw: stored };
        }
      }
      return null;
    });

    console.log('Game storage data:', gameStorage);

    if (gameStorage && gameStorage.currentGame) {
      log('Phase 2', 'localStorage game-storage', '✅', `Current game: ${gameStorage.currentGame.name || 'Unknown'}`);
    } else if (gameStorage && gameStorage.gameGid) {
      log('Phase 2', 'localStorage game-storage', '⚠️', `Game GID: ${gameStorage.gameGid} (no game object)`);
    } else {
      log('Phase 2', 'localStorage game-storage', '⚠️', 'No game state found (user needs to select a game)');
    }

    // Check for game-related UI elements
    const gameUI = await page.evaluate(() => {
      const gameElements = document.querySelectorAll('[class*="game"], [data-testid*="game"], [id*="game"]');
      return Array.from(gameElements).length;
    });

    console.log('Game UI elements found:', gameUI);
    if (gameUI > 0) {
      log('Phase 2', 'Game UI elements', '✅', `Found ${gameUI} game-related UI elements`);
    } else {
      log('Phase 2', 'Game UI elements', '⚠️', 'No game UI elements found');
    }

  } catch (error) {
    log('Phase 2', 'Game state management', '❌', `Error: ${error.message}`);
  }
}

async function testPhase3SearchInput(page) {
  console.log('\n=== Phase 3: SearchInput Component ===');

  try {
    await page.goto(`${BASE_URL}/#/parameters`, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await sleep(3000);

    // Take screenshot
    const screenshotPath = path.join(SCREENSHOT_DIR, 'phase3-parameters.png');
    await page.screenshot({ path: screenshotPath, fullPage: true });
    log('Phase 3', 'Screenshot', '✅', `Screenshot saved to ${screenshotPath}`);

    // Check for any input fields
    const inputCount = await page.locator('input').count();
    log('Phase 3', 'Input fields', inputCount > 0 ? '✅' : '❌',
      `Found ${inputCount} input fields`);

    // Get all inputs info
    const allInputs = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('input')).map(input => ({
        type: input.type,
        placeholder: input.placeholder,
        className: input.className
      }));
    });

    console.log('All inputs:', allInputs);

    if (inputCount > 0) {
      // Test typing in first input
      const firstInput = page.locator('input').first();
      if (await firstInput.isVisible()) {
        await firstInput.fill('test');
        await sleep(400);
        log('Phase 3', 'Input functionality', '✅', 'Successfully typed in input');
      }
    }

  } catch (error) {
    log('Phase 3', 'SearchInput component', '❌', `Error: ${error.message}`);
  }
}

async function testPhase4GameManagementModal(page) {
  console.log('\n=== Phase 4: Game Management Modal ===');

  try {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await waitForReactApp(page);
    await sleep(2000);

    // Get all buttons text
    const buttons = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('button')).map(btn => ({
        text: btn.textContent?.trim().substring(0, 50),
        class: btn.className
      }));
    });

    console.log('All buttons:', buttons.length);

    const gameMgmtButton = buttons.find(b =>
      b.text.includes('游戏') || b.text.includes('管理')
    );

    if (gameMgmtButton) {
      log('Phase 4', 'Game management button', '✅', `Found: "${gameMgmtButton.text}"`);

      // Try to click it
      try {
        await page.locator('button', { hasText: /游戏|管理/ }).first().click();
        await sleep(1000);

        // Take screenshot
        const screenshotPath = path.join(SCREENSHOT_DIR, 'phase4-game-mgmt-modal.png');
        await page.screenshot({ path: screenshotPath, fullPage: true });

        // Check for modal
        const modalCount = await page.locator('[class*="modal"], [role="dialog"]').count();
        log('Phase 4', 'Modal opened', modalCount > 0 ? '✅' : '⚠️',
          modalCount > 0 ? `${modalCount} modal element(s) visible` : 'Modal not clearly visible');
      } catch (clickError) {
        log('Phase 4', 'Button click', '⚠️', `Could not click button: ${clickError.message}`);
      }
    } else {
      log('Phase 4', 'Game management button', '❌', 'Game management button not found');
    }

  } catch (error) {
    log('Phase 4', 'Game management modal', '❌', `Error: ${error.message}`);
  }
}

async function testPhase5CommonParams(page) {
  console.log('\n=== Phase 5: Common Parameters Management ===');

  try {
    await page.goto(`${BASE_URL}/#/parameters`, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await sleep(3000);

    // Navigate to common params directly
    await page.goto(`${BASE_URL}/#/common-params`, { waitUntil: 'domcontentloaded' });
    await sleep(3000);

    // Take screenshot
    const screenshotPath = path.join(SCREENSHOT_DIR, 'phase5-common-params.png');
    await page.screenshot({ path: screenshotPath, fullPage: true });
    log('Phase 5', 'Screenshot', '✅', `Screenshot saved to ${screenshotPath}`);

    // Check for sync button
    const syncButton = await page.locator('button', { hasText: /同步/ }).count();
    log('Phase 5', 'Sync button', syncButton > 0 ? '✅' : '⚠️',
      syncButton > 0 ? `Found ${syncButton} sync button(s)` : 'Sync button not found');

  } catch (error) {
    log('Phase 5', 'Common parameters', '❌', `Error: ${error.message}`);
  }
}

async function testPhase6Navigation(page) {
  console.log('\n=== Phase 6: Navigation Menu ===');

  try {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await waitForReactApp(page);
    await sleep(2000);

    // Check for navigation elements
    const navCount = await page.locator('nav, [role="navigation"], [class*="nav"]').count();
    log('Phase 6', 'Navigation structure', navCount > 0 ? '✅' : '❌',
      `Found ${navCount} navigation element(s)`);

    // Check all links in navigation
    const navLinks = await page.locator('nav a, [role="navigation"] a').count();
    log('Phase 6', 'Navigation links', '✅', `Found ${navLinks} navigation links`);

    // Check if "游戏管理" is in navigation
    const gameMgmtLink = await page.locator('nav a:has-text("游戏管理"), [role="navigation"] a:has-text("游戏管理")').count();
    log('Phase 6', 'No game management in nav', gameMgmtLink === 0 ? '✅' : '❌',
      gameMgmtLink > 0 ? 'Found "游戏管理" in navigation (should not be there)' : 'Correctly not in navigation');

  } catch (error) {
    log('Phase 6', 'Navigation menu', '❌', `Error: ${error.message}`);
  }
}

async function runTests() {
  console.log('🚀 Starting Phase 1-5 E2E Tests v2...\n');
  console.log(`Frontend URL: ${BASE_URL}`);
  console.log(`Backend API: ${API_BASE}\n`);

  // Create screenshots directory
  if (!fs.existsSync(SCREENSHOT_DIR)) {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  }

  const browser = await chromium.launch({
    headless: false,
    slowMo: 100,
    args: ['--start-maximized']
  });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Set viewport
  await page.setViewportSize({ width: 1920, height: 1080 });

  // Monitor console
  const consoleMessages = [];
  page.on('console', msg => {
    consoleMessages.push({
      type: msg.type(),
      text: msg.text()
    });
    if (msg.type() === 'error') {
      console.log(`[Console Error] ${msg.text()}`);
    }
  });

  // Monitor network errors
  const networkErrors = [];
  page.on('response', response => {
    if (response.status() >= 400) {
      networkErrors.push({
        url: response.url(),
        status: response.status()
      });
      console.log(`[Network Error] ${response.url()} - ${response.status()}`);
    }
  });

  try {
    await testPhase1VisualEffects(page);
    await testPhase2GameManagement(page);
    await testPhase3SearchInput(page);
    await testPhase4GameManagementModal(page);
    await testPhase5CommonParams(page);
    await testPhase6Navigation(page);

    // Print summary
    console.log('\n=== 📊 Test Summary ===');
    console.log(`✅ Passed: ${results.passed.length}`);
    console.log(`❌ Failed: ${results.failed.length}`);
    console.log(`⚠️  Warnings: ${results.warnings.length}`);
    console.log(`Total: ${results.passed.length + results.failed.length + results.warnings.length}`);

    if (results.failed.length > 0) {
      console.log('\n❌ Failed Tests:');
      results.failed.forEach(f => {
        console.log(`  - ${f.phase} - ${f.feature}: ${f.message}`);
      });
    }

    if (results.warnings.length > 0) {
      console.log('\n⚠️  Warnings:');
      results.warnings.forEach(w => {
        console.log(`  - ${w.phase} - ${w.feature}: ${w.message}`);
      });
    }

    console.log('\n📸 Console errors:');
    const consoleErrors = consoleMessages.filter(m => m.type === 'error');
    if (consoleErrors.length > 0) {
      consoleErrors.forEach(e => {
        console.log(`  [${e.type}] ${e.text}`);
      });
    } else {
      console.log('  No console errors!');
    }

    console.log('\n🌐 Network errors:');
    if (networkErrors.length > 0) {
      networkErrors.slice(0, 10).forEach(e => {
        console.log(`  ${e.status} - ${e.url}`);
      });
    } else {
      console.log('  No network errors!');
    }

    // Save results to file
    const reportPath = '/Users/mckenzie/Documents/event2table/docs/testing/phase-1-5-test-report-v2.json';
    const fullResults = {
      summary: {
        passed: results.passed.length,
        failed: results.failed.length,
        warnings: results.warnings.length,
        total: results.passed.length + results.failed.length + results.warnings.length
      },
      details: results,
      consoleErrors: consoleErrors,
      networkErrors: networkErrors.slice(0, 20)
    };
    fs.writeFileSync(reportPath, JSON.stringify(fullResults, null, 2));
    console.log(`\n📄 Test report saved to: ${reportPath}`);
    console.log(`📸 Screenshots saved to: ${SCREENSHOT_DIR}`);

  } finally {
    await browser.close();
  }
}

runTests().catch(console.error);
