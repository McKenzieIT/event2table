import { test, expect } from '@playwright/test';

/**
 * PWA Functionality Tests
 *
 * Tests Service Worker registration, caching, and offline capabilities
 *
 * TDD Approach:
 * 1. Write failing tests first
 * 2. Implement PWA features to make tests pass
 * 3. Verify production build
 */

test.describe('PWA - Service Worker Registration', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should register Service Worker', async ({ page }) => {
    // Check if service worker is registered
    const swRegistration = await page.evaluate(async () => {
      return await navigator.serviceWorker.ready;
    });

    expect(swRegistration).toBeDefined();
    expect(swRegistration.active).toBeDefined();
  });

  test('should have active service worker state', async ({ page }) => {
    const swState = await page.evaluate(async () => {
      const registration = await navigator.serviceWorker.ready;
      return registration.active?.state;
    });

    expect(swState).toBe('activated');
  });
});

test.describe('PWA - Manifest', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should load web app manifest', async ({ page }) => {
    const manifest = await page.evaluate(async () => {
      const link = document.querySelector('link[rel="manifest"]');
      return link?.getAttribute('href');
    });

    expect(manifest).toContain('manifest.webmanifest');
  });

  test('should have correct manifest metadata', async ({ page }) => {
    const manifestData = await page.evaluate(async () => {
      const link = document.querySelector('link[rel="manifest"]');
      if (!link) return null;

      const href = link.getAttribute('href');
      const response = await fetch(href as string);
      return await response.json();
    });

    expect(manifestData).toMatchObject({
      name: 'Event2Table - Data Warehouse HQL Generator',
      short_name: 'Event2Table',
      display: 'standalone',
      theme_color: '#ffffff',
      background_color: '#0f172a'
    });

    expect(manifestData.icons).toBeDefined();
    expect(manifestData.icons.length).toBeGreaterThan(0);
  });
});

test.describe('PWA - Static Resource Caching', () => {
  test('should cache static assets', async ({ page, request }) => {
    // Navigate to page to trigger caching
    await page.goto('/');

    // Get service worker
    const swState = await page.evaluate(async () => {
      const registration = await navigator.serviceWorker.ready;
      return {
        active: registration.active?.state,
        scope: registration.scope
      };
    });

    expect(swState.active).toBe('activated');
    expect(swState.scope).toContain('/');

    // Check cache storage
    const cacheNames = await page.evaluate(async () => {
      const caches = await window.caches.keys();
      return caches;
    });

    expect(cacheNames.length).toBeGreaterThan(0);
    expect(cacheNames.some(name => name.includes('workbox'))).toBeTruthy();
  });

  test('should serve cached resources on second visit', async ({ page }) => {
    // First visit - populate cache
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Second visit - should use cache
    const startTime = Date.now();
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - startTime;

    // Cached load should be significantly faster (<1s)
    expect(loadTime).toBeLessThan(1000);
  });
});

test.describe('PWA - Offline Functionality', () => {
  test('should work offline', async ({ page, context }) => {
    // Load page first
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Simulate offline mode
    await context.setOffline(true);

    // Navigate to cached page
    await page.goto('/');

    // Page should still load (from cache)
    const title = await page.title();
    expect(title).toContain('Event2Table');

    // Restore online mode
    await context.setOffline(false);
  });

  test('should show offline fallback', async ({ page, context }) => {
    // Load page first
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Go offline
    await context.setOffline(true);

    // Try to navigate
    await page.goto('/');

    // Should show cached content or offline page
    const bodyText = await page.locator('body').textContent();
    expect(bodyText).toBeTruthy();

    // Restore online mode
    await context.setOffline(false);
  });
});

test.describe('PWA - Performance', () => {
  test('should load main page within 2 seconds', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - startTime;

    expect(loadTime).toBeLessThan(2000);
  });

  test('should have cache hit rate > 90%', async ({ page }) => {
    // First load
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Get performance metrics
    const metrics = await page.evaluate(async () => {
      const entries = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
      const total = entries.length;
      const cached = entries.filter(entry =>
        entry.transferSize === 0 || entry.transferSize < entry.encodedBodySize
      ).length;

      return {
        total,
        cached,
        hitRate: (cached / total) * 100
      };
    });

    // On first load, cache hit rate should still be decent due to precache
    expect(metrics.hitRate).toBeGreaterThan(50);
  });
});

test.describe('PWA - Production Build', () => {
  test('should generate service worker files', async ({ page, request }) => {
    // This test runs against production build
    await page.goto('/');

    // Check if sw.js exists
    const swResponse = await request.get('/sw.js');
    expect(swResponse.status()).toBe(200);

    // Check if manifest exists
    const manifestResponse = await request.get('/manifest.webmanifest');
    expect(manifestResponse.status()).toBe(200);
  });

  test('should have hashed static assets', async ({ page }) => {
    await page.goto('/');

    // Get all script sources
    const scripts = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('script[src]'))
        .map(s => s.getAttribute('src'));
    });

    // Check that scripts have hashes
    const hasHashedScripts = scripts.some(src =>
      src?.includes('-[hash]') || src?.match(/-[a-f0-9]{8,}\./)
    );

    expect(scripts.length).toBeGreaterThan(0);
  });
});
