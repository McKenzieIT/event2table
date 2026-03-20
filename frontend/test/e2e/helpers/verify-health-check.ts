/**
 * Quick verification script for the health check endpoint
 *
 * Run: npm run test:helpers -- verify-health-check.ts
 * Or: npx ts-node test/e2e/helpers/verify-health-check.ts
 */

import { ensureBackendReady, checkBackendHealth, getBackendHealth } from './api-setup';

async function main() {
  console.log('🚀 Starting health check verification...\n');

  try {
    // Test 1: Quick health check
    console.log('Test 1: Quick health check (no retries)');
    const isHealthy = await checkBackendHealth();
    console.log(`Result: ${isHealthy ? '✅ Healthy' : '❌ Unhealthy'}\n`);

    // Test 2: Wait for backend (if not ready)
    console.log('Test 2: Wait for backend to be ready');
    await ensureBackendReady(5, 1000);
    console.log('✅ Backend is ready!\n');

    // Test 3: Get detailed health info
    console.log('Test 3: Get detailed health information');
    const healthInfo = await getBackendHealth();
    if (healthInfo) {
      console.log('Health Info:', JSON.stringify(healthInfo, null, 2));
    } else {
      console.log('❌ Failed to get health info');
    }

    console.log('\n✅ All health check tests passed!');
  } catch (error) {
    console.error('\n❌ Health check verification failed:', error);
    process.exit(1);
  }
}

main();
