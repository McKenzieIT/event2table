/**
 * Playwright Global Teardown for E2E Tests
 *
 * This file runs once after all E2E tests to:
 * 1. Clean up test data (optional - can be disabled for debugging)
 * 2. Generate test summary report
 * 3. Close any open resources
 *
 * Usage: Referenced in playwright.config.ts as globalTeardown
 */

import { FullConfig } from '@playwright/test';
import { cleanupTestGamesFromFixture } from './helpers/setup-test-data';

/**
 * Global teardown function - runs after all tests
 */
async function globalTeardown(config: FullConfig) {
  console.log('\n═══════════════════════════════════════════════════════════');
  console.log('🏁 Playwright E2E Test - Global Teardown');
  console.log('═══════════════════════════════════════════════════════════\n');

  // Optional: Clean up test data after all tests
  // Comment this out if you want to preserve test data for debugging
  const SKIP_CLEANUP = process.env.SKIP_TEST_CLEANUP === 'true';

  if (!SKIP_CLEANUP) {
    console.log('1️⃣  Cleaning up test data...');
    try {
      const deleted = await cleanupTestGamesFromFixture();
      console.log(`   ✅ Cleaned up test games`);
    } catch (error) {
      console.warn(`   ⚠️  Could not clean up test data: ${error}`);
      console.warn(`   💡 Set SKIP_TEST_CLEANUP=true to skip cleanup`);
    }
  } else {
    console.log('1️⃣  Skipping cleanup (SKIP_TEST_CLEANUP=true)');
    console.log('   💡 Test data preserved for debugging');
  }

  console.log('\n═══════════════════════════════════════════════════════════');
  console.log('✅ All tests complete!');
  console.log('═══════════════════════════════════════════════════════════\n');
}

export default globalTeardown;
