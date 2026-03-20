/**
 * API Setup Helper for E2E Tests
 *
 * Provides utilities to ensure backend API is ready before running tests.
 * This prevents test failures due to backend not being available.
 */

import { request } from '@playwright/test';

// Backend configuration
const API_BASE_URL = process.env.API_BASE_URL || 'http://127.0.0.1:5001';
const HEALTH_ENDPOINT = `${API_BASE_URL}/api/health`;

// Retry configuration
const DEFAULT_MAX_RETRIES = 30;
const DEFAULT_RETRY_INTERVAL = 1000; // 1 second

/**
 * Wait for backend to be ready
 *
 * Continuously polls the health endpoint until it responds with a healthy status
 * or the maximum number of retries is reached.
 *
 * @param maxRetries - Maximum number of retries (default: 30)
 * @param retryInterval - Interval between retries in ms (default: 1000)
 * @returns Promise that resolves when backend is ready
 * @throws Error if backend is not ready after max retries
 *
 * @example
 * ```typescript
 * // Default settings (30 retries, 1 second interval)
 * await ensureBackendReady();
 *
 * // Custom settings (60 retries, 2 second interval)
 * await ensureBackendReady(60, 2000);
 * ```
 */
export async function ensureBackendReady(
  maxRetries: number = DEFAULT_MAX_RETRIES,
  retryInterval: number = DEFAULT_RETRY_INTERVAL
): Promise<void> {
  console.log(`🔍 Checking backend health at ${HEALTH_ENDPOINT}...`);

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = await request.get(HEALTH_ENDPOINT, {
        timeout: 5000,
      });

      if (response.ok()) {
        const data = await response.json();

        // Check if response indicates healthy status
        if (data.success === true && data.data?.status === 'healthy') {
          console.log(`✅ Backend is ready (attempt ${attempt}/${maxRetries})`);
          console.log(`   Status: ${data.data.status}`);
          console.log(`   Timestamp: ${data.data.timestamp}`);
          return;
        } else {
          console.warn(`⚠️  Backend responded but not healthy:`, data);
        }
      } else {
        console.warn(`⚠️  Health check returned status ${response.status()}`);
      }
    } catch (error) {
      // Log retry attempts with progress indicator
      const progress = `[${attempt}/${maxRetries}]`;
      console.log(`⏳ ${progress} Backend not ready yet, retrying in ${retryInterval}ms...`);

      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, retryInterval));
    }
  }

  // If we get here, backend is not ready
  throw new Error(
    `❌ Backend not ready after ${maxRetries} attempts. ` +
    `Please ensure the backend server is running at ${API_BASE_URL}\n` +
    `💡 Run: python3 web_app.py`
  );
}

/**
 * Quick health check (no retries)
 *
 * Performs a single health check without retrying.
 * Useful for tests that need to verify backend status without waiting.
 *
 * @returns Promise<boolean> - true if backend is healthy, false otherwise
 *
 * @example
 * ```typescript
 * const isHealthy = await checkBackendHealth();
 * if (!isHealthy) {
 *   console.log('Backend is not healthy');
 * }
 * ```
 */
export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await request.get(HEALTH_ENDPOINT, {
      timeout: 5000,
    });

    if (response.ok()) {
      const data = await response.json();
      return data.success === true && data.data?.status === 'healthy';
    }

    return false;
  } catch (error) {
    console.error('Health check failed:', error);
    return false;
  }
}

/**
 * Get backend health information
 *
 * Returns detailed health information from the backend.
 *
 * @returns Promise with health data or null if unavailable
 *
 * @example
 * ```typescript
 * const health = await getBackendHealth();
 * if (health) {
 *   console.log('Backend status:', health.status);
 *   console.log('Backend timestamp:', health.timestamp);
 * }
 * ```
 */
export async function getBackendHealth(): Promise<{
  status: string;
  timestamp: string;
  service: string;
} | null> {
  try {
    const response = await request.get(HEALTH_ENDPOINT, {
      timeout: 5000,
    });

    if (response.ok()) {
      const data = await response.json();
      return data.data || null;
    }

    return null;
  } catch (error) {
    console.error('Failed to get health info:', error);
    return null;
  }
}
