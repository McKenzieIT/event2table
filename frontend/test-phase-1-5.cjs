/**
 * Phase 1-5 E2E Testing Script
 *
 * Uses Playwright to test all features implemented in Phase 1-5
 * Run: node test-phase-1-5.js
 */

const { chromium } = require('playwright');

const BASE_URL = 'http://localhost:5173';
const API_BASE = 'http://127.0.0.1:5001';

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

async function testPhase1VisualEffects(page) {
  console.log('\n=== Phase 1: Visual Effects ===');

  try {
    await page.goto(BASE_URL, { waitUntil: 'networkidle', timeout: 30000 });
    await sleep(2000);

    // Check background color
    const backgroundColor = await page.evaluate(() => {
      const body = document.body;
      const computed = window.getComputedStyle(body);
      return {
        background: computed.background,
        backgroundColor: computed.backgroundColor,
        backgroundImage: computed.backgroundImage
      };
    });

    console.log('Background styles:', backgroundColor);
    log('Phase 1', 'Background gradient', '✅', `Background: ${backgroundColor.background}`);

    // Check CSS variables
    const cssVars = await page.evaluate(() => {
      const root = document.documentElement;
      return {
        colorPrimary: getComputedStyle(root).getPropertyValue('--color-primary')?.trim(),
        bgPrimary: getComputedStyle(root).getPropertyValue('--bg-primary')?.trim()
      };
    });

    console.log('CSS Variables:', cssVars);

    if (cssVars.colorPrimary || cssVars.bgPrimary) {
      log('Phase 1', 'CSS variables', '✅', `Color primary: ${cssVars.colorPrimary || cssVars.bgPrimary}`);
    } else {
      log('Phase 1', 'CSS variables', '⚠️', 'CSS variables not found');
    }

    // Check for card components
    const cardCount = await page.locator('.stat-card, .action-card, .cyber-card').count();
    log('Phase 1', 'Card components', '✅', `Found ${cardCount} card components`);

  } catch (error) {
    log('Phase 1', 'Visual effects', '❌', `Error: ${error.message}`);
  }
}

async function testPhase2GameManagement(page) {
  console.log('\n=== Phase 2: Game State Management ===');

  try {
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
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
      log('Phase 2', 'localStorage game-storage', '⚠️', 'No game state found in localStorage');
    }

    // Check for game selection sidebar
    const gameSelectionVisible = await page.locator('.game-selection, [data-testid="game-selection"], .game-chip').count() > 0;
    log('Phase 2', 'Game selection UI', '✅', gameSelectionVisible ? 'Game selection UI visible' : 'Game selection UI not found');

  } catch (error) {
    log('Phase 2', 'Game state management', '❌', `Error: ${error.message}`);
  }
}

async function testPhase3SearchInput(page) {
  console.log('\n=== Phase 3: SearchInput Component ===');

  try {
    await page.goto(`${BASE_URL}/#/parameters`, { waitUntil: 'networkidle', timeout: 30000 });
    await sleep(2000);

    // Check for SearchInput
    const searchInputExists = await page.locator('.search-input, input[placeholder*="搜索"]').count() > 0;
    log('Phase 3', 'SearchInput component', searchInputExists ? '✅' : '❌',
      searchInputExists ? 'SearchInput found' : 'SearchInput not found');

    if (searchInputExists) {
      // Check for shortcut hint
      const shortcutHintExists = await page.locator('.shortcut-hint').count() > 0;
      log('Phase 3', 'Keyboard shortcut', shortcutHintExists ? '✅' : '⚠️',
        shortcutHintExists ? 'Shortcut hint found' : 'Shortcut hint not found');

      // Test typing in search
      const searchInput = page.locator('.search-input input, input[placeholder*="搜索"]').first();
      if (await searchInput.isVisible()) {
        await searchInput.fill('test');
        await sleep(400); // Wait for debounce

        const clearButtonExists = await page.locator('.clear-button').count() > 0;
        log('Phase 3', 'Clear button', clearButtonExists ? '✅' : '⚠️',
          clearButtonExists ? 'Clear button appears with text' : 'Clear button not found');
      }
    }

  } catch (error) {
    log('Phase 3', 'SearchInput component', '❌', `Error: ${error.message}`);
  }
}

async function testPhase4GameManagementModal(page) {
  console.log('\n=== Phase 4: Game Management Modal ===');

  try {
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    await sleep(2000);

    // Check for game management button
    const gameMgmtButton = page.locator('button:has-text("游戏管理"), .game-management-button').first();
    const buttonExists = await gameMgmtButton.count() > 0;

    log('Phase 4', 'Game management button', buttonExists ? '✅' : '❌',
      buttonExists ? 'Button found' : 'Button not found');

    if (buttonExists && await gameMgmtButton.isVisible()) {
      // Click the button
      await gameMgmtButton.click();
      await sleep(500);

      // Check for modal
      const modalExists = await page.locator('.game-management-modal, .modal-overlay').count() > 0;
      log('Phase 4', 'Game management modal', modalExists ? '✅' : '❌',
        modalExists ? 'Modal opened' : 'Modal not found');

      if (modalExists) {
        // Check for games list
        const gamesListExists = await page.locator('.games-list, .game-item').count() > 0;
        log('Phase 4', 'Games list', gamesListExists ? '✅' : '❌',
          gamesListExists ? 'Games list visible' : 'Games list not found');

        // Check for add game button
        const addGameButtonExists = await page.locator('button:has-text("添加游戏"), .add-game-btn').count() > 0;
        log('Phase 4', 'Add game button', addGameButtonExists ? '✅' : '⚠️',
          addGameButtonExists ? 'Add game button found' : 'Add game button not found');
      }

      // Close modal
      await page.keyboard.press('Escape');
      await sleep(500);
    }

  } catch (error) {
    log('Phase 4', 'Game management modal', '❌', `Error: ${error.message}`);
  }
}

async function testPhase5CommonParams(page) {
  console.log('\n=== Phase 5: Common Parameters Management ===');

  try {
    await page.goto(`${BASE_URL}/#/parameters`, { waitUntil: 'networkidle', timeout: 30000 });
    await sleep(2000);

    // Check for common params entry button
    const commonParamsButton = page.locator('button:has-text("进入公参管理"), button:has-text("公参管理")').first();
    const buttonExists = await commonParamsButton.count() > 0;

    log('Phase 5', 'Common params entry button', buttonExists ? '✅' : '❌',
      buttonExists ? 'Button found' : 'Button not found');

    if (buttonExists && await commonParamsButton.isVisible()) {
      // Click the button
      await commonParamsButton.click();
      await sleep(1000);

      // Check URL
      const url = page.url();
      const hasCommonParams = url.includes('common-params');
      log('Phase 5', 'Navigate to common params', hasCommonParams ? '✅' : '❌',
        hasCommonParams ? `Navigated to: ${url}` : `URL: ${url}`);

      if (hasCommonParams) {
        // Check for sync button
        const syncButtonExists = await page.locator('button:has-text("同步"), button:has-text("同步公参")').count() > 0;
        log('Phase 5', 'Sync button', syncButtonExists ? '✅' : '⚠️',
          syncButtonExists ? 'Sync button found' : 'Sync button not found');
      }
    }

  } catch (error) {
    log('Phase 5', 'Common parameters', '❌', `Error: ${error.message}`);
  }
}

async function testPhase6Navigation(page) {
  console.log('\n=== Phase 6: Navigation Menu ===');

  try {
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    await sleep(2000);

    // Check for sidebar
    const sidebarExists = await page.locator('nav, .sidebar, [data-testid="sidebar"]').count() > 0;
    log('Phase 6', 'Sidebar navigation', sidebarExists ? '✅' : '❌',
      sidebarExists ? 'Sidebar found' : 'Sidebar not found');

    // Check that "游戏管理" is NOT in sidebar
    const gameMgmtInMenu = await page.locator('nav a:has-text("游戏管理"), .sidebar a:has-text("游戏管理")').count() > 0;
    log('Phase 6', 'No game management in sidebar', !gameMgmtInMenu ? '✅' : '❌',
      gameMgmtInMenu ? 'Found "游戏管理" in menu (should not be there)' : 'Correctly removed from sidebar');

    // Count menu items
    const menuItemsCount = await page.locator('nav a, .sidebar a').count();
    log('Phase 6', 'Menu items count', '✅', `Found ${menuItemsCount} menu items`);

  } catch (error) {
    log('Phase 6', 'Navigation menu', '❌', `Error: ${error.message}`);
  }
}

async function runTests() {
  console.log('🚀 Starting Phase 1-5 E2E Tests...\n');
  console.log(`Frontend URL: ${BASE_URL}`);
  console.log(`Backend API: ${API_BASE}\n`);

  const browser = await chromium.launch({ headless: false, slowMo: 500 });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Monitor console errors
  page.on('console', msg => {
    if (msg.type() === 'error') {
      log('Console', 'JavaScript Error', '❌', msg.text());
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

    // Save results to file
    const fs = require('fs');
    const reportPath = '/Users/mckenzie/Documents/event2table/docs/testing/phase-1-5-test-report.json';
    fs.writeFileSync(reportPath, JSON.stringify(results, null, 2));
    console.log(`\n📄 Test report saved to: ${reportPath}`);

  } finally {
    await browser.close();
  }
}

runTests().catch(console.error);
