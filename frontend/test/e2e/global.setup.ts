/**
 * Playwright Global Setup for E2E Tests
 *
 * This file runs once before all E2E tests to:
 * 1. Seed test data (games, events, parameters)
 * 2. Verify backend server is accessible
 * 3. Ensure test database is ready
 *
 * Usage: Referenced in playwright.config.ts as globalSetup
 */

import { FullConfig } from '@playwright/test';
import { seedTestGamesFromFixture } from './helpers/setup-test-data';

/**
 * Global setup function - runs before all tests
 */
async function globalSetup(config: FullConfig) {
  console.log('\n═══════════════════════════════════════════════════════════');
  console.log('🚀 Playwright E2E Test - Global Setup');
  console.log('═══════════════════════════════════════════════════════════\n');

  // Step 1: Verify backend server is running
  console.log('1️⃣  Verifying backend server...');
  const backendUrl = 'http://127.0.0.1:5001';
  try {
    const response = await fetch(`${backendUrl}/api/health`).catch(() => null);
    if (response) {
      console.log(`   ✅ Backend server is running (${backendUrl})`);
    } else {
      // Try games endpoint as fallback
      const gamesResponse = await fetch(`${backendUrl}/api/games`).catch(() => null);
      if (gamesResponse) {
        console.log(`   ✅ Backend server is running (${backendUrl})`);
      } else {
        console.warn(`   ⚠️  Backend server may not be running. Tests may fail.`);
        console.warn(`   💡 Start backend with: python3 web_app.py`);
      }
    }
  } catch (error) {
    console.warn(`   ⚠️  Could not verify backend server: ${error}`);
  }

  // Step 2: Seed test data from fixture
  console.log('\n2️⃣  Seeding test data from fixtures...');
  try {
    const games = await seedTestGamesFromFixture();
    console.log(`   ✅ Seeded ${games.length} test games:`);
    games.forEach((game: any) => {
      console.log(`      - GID: ${game.gid} | Name: ${game.name}`);
    });
  } catch (error) {
    console.error(`   ❌ Failed to seed test data: ${error}`);
    console.warn(`   ⚠️  Tests may fail due to missing test data.`);
    console.warn(`   💡 Run manually: python3 scripts/test/setup_e2e_test_data.py`);
  }

  // Step 3: Verify frontend dev server
  console.log('\n3️⃣  Verifying frontend server...');
  const frontendUrl = 'http://localhost:5173';
  try {
    const response = await fetch(frontendUrl).catch(() => null);
    if (response) {
      console.log(`   ✅ Frontend server is running (${frontendUrl})`);
    } else {
      console.warn(`   ⚠️  Frontend server may not be running.`);
      console.warn(`   💡 Start frontend with: cd frontend && npm run dev`);
    }
  } catch (error) {
    console.warn(`   ⚠️  Could not verify frontend server: ${error}`);
  }

  console.log('\n═══════════════════════════════════════════════════════════');
  console.log('✅ Global setup complete. Starting tests...\n');
  console.log('═══════════════════════════════════════════════════════════\n');
}

export default globalSetup;
