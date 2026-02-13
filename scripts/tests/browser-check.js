/**
 * Event2Table Frontend Browser-Based Test
 * Run this in the browser console at http://localhost:5173/
 */

(function() {
  console.log('🔍 Event2Table Frontend Test');
  console.log('==========================================\n');

  const results = {
    pass: [],
    fail: [],
    info: []
  };

  function test(name, condition, details = '') {
    if (condition) {
      results.pass.push({ name, details });
      console.log(`✅ PASS: ${name}`);
      if (details) console.log(`   Details: ${details}`);
    } else {
      results.fail.push({ name, details });
      console.log(`❌ FAIL: ${name}`);
      if (details) console.log(`   Details: ${details}`);
    }
  }

  function info(name, details = '') {
    results.info.push({ name, details });
    console.log(`ℹ️  INFO: ${name}`);
    if (details) console.log(`   Details: ${details}`);
  }

  // Phase 1: Visual Effects
  console.log('\n🎨 Phase 1: Visual Effects');
  console.log('----------------------------');

  // Check body background
  const body = document.body;
  const bodyStyle = window.getComputedStyle(body);
  test('Body element exists', body !== null);
  info('Body background', bodyStyle.background);
  info('Body background-color', bodyStyle.backgroundColor);

  // Check for card components
  const cards = document.querySelectorAll('[class*="card"], [class*="Card"]');
  test('Card components found', cards.length > 0, `Found ${cards.length} cards`);

  // Phase 2: Game State Management
  console.log('\n🎮 Phase 2: Game State Management');
  console.log('----------------------------');

  // Check localStorage
  const gameStorage = localStorage.getItem('game-storage');
  test('game-storage exists', gameStorage !== null);
  if (gameStorage) {
    try {
      const parsed = JSON.parse(gameStorage);
      info('game-storage content', JSON.stringify(parsed, null, 2));
    } catch (e) {
      info('game-storage parse error', e.message);
    }
  }

  // Check all localStorage keys
  const localStorageKeys = Object.keys(localStorage);
  info('All localStorage keys', localStorageKeys.join(', '));

  // Check for game selection UI
  const gameSelectors = document.querySelectorAll(
    '[class*="game"], [class*="Game"], select[name="game"]'
  );
  test('Game selection UI found', gameSelectors.length > 0);

  // Phase 3: SearchInput Component
  console.log('\n🔍 Phase 3: SearchInput Component');
  console.log('----------------------------');

  // Check for search inputs
  const searchInputs = document.querySelectorAll(
    'input[type="search"], input[placeholder*="search" i], [class*="search"] input, [class*="Search"] input'
  );
  test('Search inputs found', searchInputs.length > 0, `Found ${searchInputs.length} search inputs`);

  // Check for shortcut hints
  const shortcutHints = document.querySelectorAll(
    'kbd, [class*="shortcut"], [class*="hotkey"]'
  );
  test('Shortcut hints found', shortcutHints.length > 0, `Found ${shortcutHints.length} hints`);

  // Phase 4: Game Management
  console.log('\n⚙️  Phase 4: Game Management');
  console.log('----------------------------');

  // Check for game management button
  const gameButtons = Array.from(document.querySelectorAll('button, a')).filter(el => {
    const text = el.textContent || '';
    return text.includes('游戏管理') || text.toLowerCase().includes('game');
  });
  test('Game management button found', gameButtons.length > 0);

  // Check for modals/dialogs
  const modals = document.querySelectorAll(
    '[role="dialog"], .modal, [class*="modal"], .drawer, [class*="drawer"]'
  );
  test('Modal components found', modals.length > 0, `Found ${modals.length} modals`);

  // Phase 5: Public Parameters
  console.log('\n📋 Phase 5: Public Parameters');
  console.log('----------------------------');

  // Check for public param buttons
  const publicParamButtons = Array.from(document.querySelectorAll('button, a')).filter(el => {
    const text = el.textContent || '';
    return text.includes('公参') || text.toLowerCase().includes('public');
  });
  info('Public param buttons found', publicParamButtons.length > 0 ? `Found ${publicParamButtons.length}` : 'Not found');

  // Check for sync buttons
  const syncButtons = Array.from(document.querySelectorAll('button')).filter(el => {
    const text = el.textContent || '';
    return text.includes('同步') || text.toLowerCase().includes('sync');
  });
  info('Sync buttons found', syncButtons.length > 0 ? `Found ${syncButtons.length}` : 'Not found');

  // Phase 6: Navigation Menu
  console.log('\n🧭 Phase 6: Navigation Menu');
  console.log('----------------------------');

  // Check for navigation
  const navs = document.querySelectorAll('nav, [role="navigation"], [class*="sidebar"], [class*="nav"]');
  test('Navigation found', navs.length > 0, `Found ${navs.length} nav elements`);

  // Check that game management is NOT in main navigation
  const gameManagementInNav = Array.from(navs).some(nav => {
    const text = nav.textContent || '';
    return text.includes('游戏管理');
  });
  test('Game management not in main navigation', !gameManagementInNav);

  // List all navigation items
  navs.forEach((nav, i) => {
    const menuItems = nav.querySelectorAll('li, a, button');
    const texts = Array.from(menuItems).map(el => (el.textContent || '').trim()).filter(t => t);
    if (texts.length > 0) {
      info(`Navigation ${i+1} items`, texts.join(', '));
    }
  });

  // JavaScript Errors
  console.log('\n🐛 JavaScript Errors');
  console.log('----------------------------');

  let errorCount = 0;
  const originalError = console.error;
  console.error = function(...args) {
    errorCount++;
    originalError.apply(console, args);
  };

  // Wait a bit for any async errors
  setTimeout(() => {
    console.error = originalError;
    test('No console errors detected', errorCount === 0, `${errorCount} errors found`);

    // Summary
    console.log('\n==========================================');
    console.log('Test Summary');
    console.log('==========================================');
    console.log(`Passed: ${results.pass.length}`);
    console.log(`Failed: ${results.fail.length}`);
    console.log(`Info:   ${results.info.length}`);
    console.log(`Total:  ${results.pass.length + results.fail.length}`);

    if (results.fail.length > 0) {
      console.log('\n❌ Failed Tests:');
      results.fail.forEach(f => {
        console.log(`  - ${f.name}`);
        if (f.details) console.log(`    ${f.details}`);
      });
    }

    // Return results for programmatic access
    window.__testResults = results;
    console.log('\n💡 Results available in window.__testResults');
  }, 1000);
})();
