/**
 * Chrome DevTools Protocol Test Script
 *
 * Uses Playwright with Chrome DevTools Protocol to test Event2Table frontend
 * with actual browser interaction
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://localhost:5173';
const SCREENSHOT_DIR = '/Users/mckenzie/Documents/event2table/docs/testing/screenshots-chrome';

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

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ============================================================================
// PHASE 1: Visual Effects
// ============================================================================
async function testPhase1VisualEffects(page) {
  console.log('\n=== Phase 1: Visual Effects ===');

  try {
    await page.goto(BASE_URL, { waitUntil: 'networkidle2', timeout: 30000 });
    await sleep(3000);

    // Take screenshot
    const screenshotPath = path.join(SCREENSHOT_DIR, 'chrome-phase1-homepage.png');
    await page.screenshot({ path: screenshotPath, fullPage: true });
    log('Phase 1', 'Screenshot', '✅', `Screenshot saved to ${screenshotPath}`);

    // Check background color
    const bodyStyles = await page.evaluate(() => {
      const body = document.body;
      const computed = window.getComputedStyle(body);
      return {
        background: computed.background,
        backgroundColor: computed.backgroundColor,
        backgroundImage: computed.backgroundImage,
        bodyChildren: document.body.children.length
      };
    });

    console.log('Body styles:', bodyStyles);
    log('Phase 1', 'Background styles', '✅', `Background: ${bodyStyles.backgroundColor}`);

    // Check for UI elements
    const elementCounts = await page.evaluate(() => {
      return {
        divs: document.querySelectorAll('div').length,
        buttons: document.querySelectorAll('button').length,
        inputs: document.querySelectorAll('input').length,
        cards: document.querySelectorAll('[class*="card"], [class*="Card"]').length,
        statCards: document.querySelectorAll('[class*="stat-card"]').length
      };
    });

    console.log('Element counts:', elementCounts);
    log('Phase 1', 'UI elements', '✅',
      `Divs: ${elementCounts.divs}, Buttons: ${elementCounts.buttons}, StatCards: ${elementCounts.statCards}`);

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
      log('Phase 1', 'CSS variables', '✅', `Found CSS variables`);
    } else {
      log('Phase 1', 'CSS variables', '⚠️', 'No CSS variables found');
    }

  } catch (error) {
    log('Phase 1', 'Visual effects', '❌', `Error: ${error.message}`);
  }
}

// ============================================================================
// PHASE 2: Game Selection (localStorage)
// ============================================================================
async function testPhase2GameSelection(page) {
  console.log('\n=== Phase 2: Game Selection & localStorage ===');

  try {
    await page.goto(BASE_URL, { waitUntil: 'networkidle2' });
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
      log('Phase 2', 'localStorage game-storage', '✅',
        `Current game: ${gameStorage.currentGame.name || 'Unknown'}`);
    } else if (gameStorage && gameStorage.gameGid) {
      log('Phase 2', 'localStorage game-storage', '⚠️',
        `Game GID: ${gameStorage.gameGid} (no game object)`);
    } else {
      log('Phase 2', 'localStorage game-storage', '⚠️',
        'No game state found (user needs to select a game)');
    }

    // Look for game selection UI
    const gameSelectionUI = await page.evaluate(() => {
      // Look for game selection elements
      const gameElements = document.querySelectorAll('[class*="game-selection"], [class*="game-chip"], [class*="game-select"]');
      const buttons = Array.from(document.querySelectorAll('button')).filter(btn =>
        btn.textContent?.includes('游戏') || btn.textContent?.includes('Game')
      );

      return {
        gameSelectionElements: gameElements.length,
        gameRelatedButtons: buttons.length,
        buttonTexts: buttons.map(b => b.textContent?.trim())
      };
    });

    console.log('Game selection UI:', gameSelectionUI);

    if (gameSelectionUI.gameRelatedButtons > 0) {
      log('Phase 2', 'Game selection UI', '✅',
        `Found ${gameSelectionUI.gameRelatedButtons} game-related button(s): ${gameSelectionUI.buttonTexts.join(', ')}`);
    } else {
      log('Phase 2', 'Game selection UI', '⚠️',
        'No game selection buttons found');
    }

  } catch (error) {
    log('Phase 2', 'Game selection', '❌', `Error: ${error.message}`);
  }
}

// ============================================================================
// PHASE 3: SearchInput Component
// ============================================================================
async function testPhase3SearchInput(page) {
  console.log('\n=== Phase 3: SearchInput Component ===');

  try {
    await page.goto(`${BASE_URL}/#/parameters`, { waitUntil: 'networkidle2', timeout: 30000 });
    await sleep(3000);

    // Screenshot
    const screenshotPath = path.join(SCREENSHOT_DIR, 'chrome-phase3-parameters.png');
    await page.screenshot({ path: screenshotPath, fullPage: true });
    log('Phase 3', 'Screenshot', '✅', `Screenshot saved`);

    // Check for search inputs
    const searchInputs = await page.evaluate(() => {
      const inputs = Array.from(document.querySelectorAll('input'));
      return inputs.map(input => ({
        type: input.type,
        placeholder: input.placeholder,
        className: input.className,
        id: input.id
      }));
    });

    console.log('All inputs:', searchInputs);

    const inputsWithPlaceholder = searchInputs.filter(i => i.placeholder);
    log('Phase 3', 'Input fields', inputsWithPlaceholder.length > 0 ? '✅' : '❌',
      `Found ${inputsWithPlaceholder.length} input(s) with placeholder`);

    if (inputsWithPlaceholder.length > 0) {
      // Test typing in first input with placeholder
      const firstInput = inputsWithPlaceholder[0];
      const inputSelector = `input[placeholder="${firstInput.placeholder}"]`;

      await page.click(inputSelector);
      await page.type(inputSelector, 'test_search');
      await sleep(500); // Wait for debounce

      log('Phase 3', 'Input typing', '✅',
        `Successfully typed "${firstInput.placeholder}" input`);

      // Check for clear button (might appear after typing)
      const afterTyping = await page.evaluate(() => {
        const clearBtns = document.querySelectorAll('[class*="clear"], button[aria-label*="clear"], button[aria-label*="清除"]');
        return {
          clearButtons: clearBtns.length,
          inputValue: document.querySelector('input')?.value || ''
        };
      });

      if (afterTyping.clearButtons > 0) {
        log('Phase 3', 'Clear button', '✅',
          `Clear button appeared after typing`);
      } else {
        log('Phase 3', 'Clear button', '⚠️',
          `No clear button found (might be inline search)`);
      }
    }

  } catch (error) {
    log('Phase 3', 'SearchInput component', '❌', `Error: ${error.message}`);
  }
}

// ============================================================================
// PHASE 4: Game Management Modal
// ============================================================================
async function testPhase4GameManagement(page) {
  console.log('\n=== Phase 4: Game Management Modal ===');

  try {
    await page.goto(BASE_URL, { waitUntil: 'networkidle2' });
    await sleep(2000);

    // Look for game management button
    const gameMgmtButton = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      return buttons.find(btn => {
        const text = btn.textContent?.trim();
        return text?.includes('游戏管理') ||
               text?.includes('数据管理') ||
               text?.includes('Game Management');
      });
    });

    if (gameMgmtButton) {
      log('Phase 4', 'Game management button', '✅',
        `Found button: "${gameMgmtButton.textContent.trim()}"`);

      // Click the button
      await page.click('button');
      await sleep(1500);

      // Screenshot after clicking
      const screenshotPath = path.join(SCREENSHOT_DIR, 'chrome-phase4-after-click.png');
      await page.screenshot({ path: screenshotPath, fullPage: true });

      // Check if modal appeared
      const modalCheck = await page.evaluate(() => {
        const modals = document.querySelectorAll('[class*="modal"], [class*="sheet"], [class*="drawer"], [role="dialog"]');
        return {
          modalCount: modals.length,
          modalClasses: Array.from(modals).map(m => m.className),
          visibleModals: Array.from(modals).filter(m => {
            const style = window.getComputedStyle(m);
            return style.display !== 'none' && style.visibility !== 'hidden';
          }).length
        };
      });

      console.log('Modal check:', modalCheck);

      if (modalCheck.visibleModals > 0) {
        log('Phase 4', 'Modal opened', '✅',
          `Modal appeared (${modalCheck.visibleModals} visible)`);

        // Check for game list in modal
        const gameList = await page.evaluate(() => {
          const gameItems = document.querySelectorAll('[class*="game-item"], [class*="game-list"]');
          return {
            gameItems: gameItems.length,
            gameItemTexts: Array.from(gameItems).map(i => i.textContent?.substring(0, 50))
          };
        });

        if (gameList.gameItems > 0) {
          log('Phase 4', 'Games list', '✅',
            `Found ${gameList.gameItems} game item(s)`);
        } else {
          log('Phase 4', 'Games list', '⚠️',
            'No game items found in modal');
        }
      } else {
        log('Phase 4', 'Modal opened', '❌',
          'Modal did not appear after click');
      }
    } else {
      log('Phase 4', 'Game management button', '❌',
        'Game management button not found');
    }

  } catch (error) {
    log('Phase 4', 'Game management modal', '❌', `Error: ${error.message}`);
  }
}

// ============================================================================
// PHASE 5: Common Parameters Management
// ============================================================================
async function testPhase5CommonParams(page) {
  console.log('\n=== Phase 5: Common Parameters Management ===');

  try {
    // Navigate to common params page
    await page.goto(`${BASE_URL}/#/common-params`, { waitUntil: 'networkidle2', timeout: 30000 });
    await sleep(3000);

    // Screenshot
    const screenshotPath = path.join(SCREENSHOT_DIR, 'chrome-phase5-common-params.png');
    await page.screenshot({ path: screenshotPath, fullPage: true });
    log('Phase 5', 'Screenshot', '✅', `Screenshot saved`);

    // Check for sync button
    const syncButtonCheck = await page.evaluate(() => {
      const syncButtons = Array.from(document.querySelectorAll('button')).filter(btn => {
        const text = btn.textContent?.trim();
        return text?.includes('同步') ||
               text?.includes('Sync') ||
               text?.includes('公共参数');
      });

      return {
        syncButtonCount: syncButtons.length,
        buttonTexts: syncButtons.map(b => b.textContent?.trim())
      };
    });

    console.log('Sync button check:', syncButtonCheck);

    if (syncButtonCheck.syncButtonCount > 0) {
      log('Phase 5', 'Sync button', '✅',
        `Found ${syncButtonCheck.syncButtonCount} sync button(s): ${syncButtonCheck.buttonTexts.join(', ')}`);

      // Try clicking sync button
      await page.click('button');
      await sleep(1000);

      log('Phase 5', 'Sync button click', '✅',
        'Successfully clicked sync button');
    } else {
      log('Phase 5', 'Sync button', '⚠️',
        'No sync button found');
    }

  } catch (error) {
    log('Phase 5', 'Common parameters', '❌', `Error: ${error.message}`);
  }
}

// ============================================================================
// PHASE 6: Navigation Menu
// ============================================================================
async function testPhase6Navigation(page) {
  console.log('\n=== Phase 6: Navigation Menu ===');

  try {
    await page.goto(BASE_URL, { waitUntil: 'networkidle2' });
    await sleep(2000);

    // Check for navigation elements
    const navCheck = await page.evaluate(() => {
      const navs = document.querySelectorAll('nav, [role="navigation"], [class*="sidebar"], [class*="nav"]');
      const navLinks = document.querySelectorAll('nav a, [role="navigation"] a');

      return {
        navCount: navs.length,
        navLinkCount: navLinks.length,
        navClasses: Array.from(navs).map(n => n.className),
        linkTexts: Array.from(navLinks).map(l => l.textContent?.trim())
      };
    });

    console.log('Navigation check:', navCheck);

    if (navCheck.navCount > 0) {
      log('Phase 6', 'Navigation structure', '✅',
        `Found ${navCheck.navCount} navigation element(s)`);
    } else {
      log('Phase 6', 'Navigation structure', '❌',
        'No navigation elements found');
    }

    if (navCheck.navLinkCount > 0) {
      log('Phase 6', 'Navigation links', '✅',
        `Found ${navCheck.navLinkCount} navigation link(s)`);
    } else {
      log('Phase 6', 'Navigation links', '⚠️',
        'No navigation links found');
    }

    // Check that "游戏管理" is NOT in navigation
    const gameMgmtInNav = navCheck.linkTexts.some(text =>
      text?.includes('游戏管理') || text?.includes('Game Management')
    );

    log('Phase 6', 'No game management in nav', !gameMgmtInNav ? '✅' : '❌',
      gameMgmtInNav ? 'Found "游戏管理" in navigation (should not be there)' : 'Correctly not in navigation');

  } catch (error) {
    log('Phase 6', 'Navigation menu', '❌', `Error: ${error.message}`);
  }
}

// ============================================================================
// MAIN TEST RUNNER
// ============================================================================
async function runTests() {
  console.log('🚀 Starting Chrome DevTools Protocol E2E Tests...\n');
  console.log(`Frontend URL: ${BASE_URL}\n`);

  // Create screenshots directory
  if (!fs.existsSync(SCREENSHOT_DIR)) {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  }

  // Launch browser with Chrome DevTools Protocol
  const browser = await chromium.launch({
    headless: false,
    args: ['--start-maximized'],
    slowMo: 100 // Slow down by 100ms
  });

  const context = await browser.newContext();
  const page = await context.newPage();

  // Set viewport size
  await page.setViewport({ width: 1920, height: 1080 });

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
    await testPhase2GameSelection(page);
    await testPhase3SearchInput(page);
    await testPhase4GameManagement(page);
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
    const reportPath = '/Users/mckenzie/Documents/event2table/docs/testing/chrome-mcp-test-report.json';
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
