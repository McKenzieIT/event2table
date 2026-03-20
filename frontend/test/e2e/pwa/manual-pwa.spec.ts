import { test, expect } from '@playwright/test';

/**
 * Manual PWA Testing Script
 *
 * Run with: npx playwright test test/e2e/pwa/manual-pwa-test.ts --headed
 */

test.describe('PWA Manual Testing', () => {
  test('Service Worker Registration', async ({ page }) => {
    // Navigate to homepage
    await page.goto('/');

    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Check Service Worker registration
    const swRegistered = await page.evaluate(async () => {
      const registration = await navigator.serviceWorker.ready;
      return {
        active: registration.active?.state,
        scope: registration.scope,
        waiting: registration.waiting?.state,
        installing: registration.installing?.state
      };
    });

    console.log('Service Worker State:', JSON.stringify(swRegistered, null, 2));

    // In development, SW is disabled by config
    // In production, it should be activated
    if (process.env.NODE_ENV === 'production') {
      expect(swRegistered.active).toBe('activated');
    } else {
      console.log('⚠️  Service Worker is disabled in development mode');
    }
  });

  test('Manifest Loading', async ({ page }) => {
    await page.goto('/');

    // Check manifest link
    const manifestHref = await page.evaluate(() => {
      const link = document.querySelector('link[rel="manifest"]');
      return link?.getAttribute('href');
    });

    console.log('Manifest Href:', manifestHref);

    expect(manifestHref).toBeTruthy();

    // Fetch and validate manifest
    const manifestResponse = await page.request.get(manifestHref!);
    const manifest = await manifestResponse.json();

    console.log('Manifest:', JSON.stringify(manifest, null, 2));

    expect(manifest).toMatchObject({
      name: 'Event2Table - Data Warehouse HQL Generator',
      short_name: 'Event2Table',
      display: 'standalone'
    });

    expect(manifest.icons).toBeDefined();
    expect(manifest.icons.length).toBeGreaterThan(0);
  });

  test('Cache Storage', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check cache storage
    const cacheInfo = await page.evaluate(async () => {
      const cacheNames = await caches.keys();
      const cachesInfo = [];

      for (const name of cacheNames) {
        const cache = await caches.open(name);
        const keys = await cache.keys();
        cachesInfo.push({
          name,
          count: keys.length,
          urls: keys.slice(0, 5).map(req => req.url) // First 5 URLs
        });
      }

      return cachesInfo;
    });

    console.log('Cache Storage:', JSON.stringify(cacheInfo, null, 2));

    // In production, should have workbox caches
    if (process.env.NODE_ENV === 'production') {
      expect(cacheInfo.length).toBeGreaterThan(0);
      expect(cacheInfo.some(c => c.name.includes('workbox'))).toBeTruthy();
    }
  });

  test('Performance Metrics', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const loadTime = Date.now() - startTime;

    console.log('Page Load Time:', loadTime, 'ms');

    // Get performance metrics
    const metrics = await page.evaluate(() => {
      const perfData = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      return {
        domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
        loadComplete: perfData.loadEventEnd - perfData.loadEventStart,
        totalLoadTime: perfData.loadEventEnd - perfData.fetchStart
      };
    });

    console.log('Performance Metrics:', JSON.stringify(metrics, null, 2));

    // Target: Load within 2 seconds
    expect(loadTime).toBeLessThan(2000);
  });
});

test.afterAll(async () => {
  console.log('\n✅ PWA Manual Tests Completed');
  console.log('📝 Check console output for detailed information');
});
