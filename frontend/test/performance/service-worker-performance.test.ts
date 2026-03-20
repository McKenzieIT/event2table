/**
 * Service Worker Performance Tests
 * TDD Approach: RED phase - Test before implementation
 *
 * These tests verify that PWA caching improves load performance
 */

import { test, expect } from '@playwright/test';

test.describe('Service Worker Performance', () => {
  test('should register service worker on production build', async ({ page }) => {
    // Navigate to app
    await page.goto('/');

    // Wait for service worker registration
    await page.waitForTimeout(3000);

    // Check if service worker is registered
    const swRegistered = await page.evaluate(() => {
      return navigator.serviceWorker.getRegistration().then(reg => reg !== undefined);
    });

    // Initially this will fail (RED phase)
    // After PWA implementation, this will pass (GREEN phase)
    expect(swRegistered).toBe(true);
  });

  test('first load should complete in reasonable time', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const endTime = Date.now();
    const loadTime = endTime - startTime;

    // First load should be under 5 seconds
    expect(loadTime).toBeLessThan(5000);

    console.log(`First load time: ${loadTime}ms`);
  });

  test('static assets should be cached on second visit', async ({ page, context }) => {
    // First visit - cache assets
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Get resource timing for first visit
    const firstVisitTimings = await page.evaluate(() => {
      return performance.getEntriesByType('resource')
        .filter(r => r.name.includes('.js') || r.name.includes('.css'))
        .map(r => ({
          name: r.name,
          duration: r.duration,
          transferSize: (r as PerformanceResourceTiming).transferSize
        }));
    });

    // Close page and revisit (should use cache)
    await page.close();
    const page2 = await context.newPage();

    const startTime = Date.now();
    await page2.goto('/');
    await page2.waitForLoadState('networkidle');
    const secondVisitTime = Date.now() - startTime;

    // Get resource timing for second visit
    const secondVisitTimings = await page2.evaluate(() => {
      return performance.getEntriesByType('resource')
        .filter(r => r.name.includes('.js') || r.name.includes('.css'))
        .map(r => ({
          name: r.name,
          duration: r.duration,
          transferSize: (r as PerformanceResourceTiming).transferSize
        }));
    });

    console.log('First visit timings:', firstVisitTimings.length, 'resources');
    console.log('Second visit timings:', secondVisitTimings.length, 'resources');
    console.log('Second visit time:', secondVisitTime, 'ms');

    // Second visit should be faster (cached)
    // This will initially fail (RED), pass after PWA (GREEN)
    expect(secondVisitTime).toBeLessThan(2000); // Should be under 2s with cache
  });

  test('should have manifest file', async ({ page }) => {
    const response = await page.request.get('/manifest.webmanifest');

    // Initially this will fail (404)
    // After PWA implementation, this will pass (200)
    expect(response.status()).toBe(200);

    const manifest = await response.json();
    expect(manifest).toHaveProperty('name');
    expect(manifest).toHaveProperty('short_name');
  });

  test('should have PWA meta tags', async ({ page }) => {
    await page.goto('/');

    const themeColor = await page.locator('meta[name="theme-color"]').getAttribute('content');
    expect(themeColor).toBe('#ffffff');

    const appleMobileCapable = await page.locator('meta[name="apple-mobile-web-app-capable"]').getAttribute('content');
    expect(appleMobileCapable).toBe('yes');
  });
});

test.describe('Service Worker Cache Strategy', () => {
  test('should cache static assets (JS/CSS)', async ({ page }) => {
    await page.goto('/');

    // Wait for service worker to be ready
    await page.waitForTimeout(3000);

    // Check cache status
    const cacheNames = await page.evaluate(async () => {
      const caches = await window.caches.keys();
      return caches;
    });

    console.log('Available caches:', cacheNames);

    // Should have at least one cache
    expect(cacheNames.length).toBeGreaterThan(0);

    // Check if static assets are cached
    const cachedRequests = await page.evaluate(async () => {
      const cacheNames = await window.caches.keys();
      const allRequests: string[] = [];

      for (const cacheName of cacheNames) {
        const cache = await window.caches.open(cacheName);
        const requests = await cache.keys();
        allRequests.push(...requests.map(r => r.url));
      }

      return allRequests;
    });

    console.log('Cached requests:', cachedRequests.length);

    // Should have cached JS/CSS files
    const hasJsOrCss = cachedRequests.some(url =>
      url.includes('.js') || url.includes('.css')
    );

    expect(hasJsOrCss).toBe(true);
  });

  test('should cache external fonts', async ({ page }) => {
    await page.goto('/');

    // Wait for service worker
    await page.waitForTimeout(3000);

    // Check if Google Fonts are cached
    const fontsCached = await page.evaluate(async () => {
      const cacheNames = await window.caches.keys();
      const allRequests: string[] = [];

      for (const cacheName of cacheNames) {
        const cache = await window.caches.open(cacheName);
        const requests = await cache.keys();
        allRequests.push(...requests.map(r => r.url));
      }

      return allRequests.filter(url => url.includes('fonts.googleapis.com'));
    });

    console.log('Cached font URLs:', fontsCached);

    // Should cache Google Fonts
    expect(fontsCached.length).toBeGreaterThan(0);
  });
});
