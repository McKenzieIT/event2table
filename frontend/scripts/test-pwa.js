#!/usr/bin/env node
/**
 * Manual PWA Testing Script
 * Tests Service Worker, Manifest, and Caching
 */

import puppeteer from 'puppeteer';
import { fileURLToPath } from 'url';
import path from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const BASE_URL = 'http://localhost:5173';

async function testPWA() {
  console.log('🔍 Starting PWA Tests...\n');

  const browser = await puppeteer.launch({
    headless: false,
    devtools: true
  });

  const page = await browser.newPage();

  // Test 1: Page Load
  console.log('📊 Test 1: Page Load Performance');
  const startTime = Date.now();
  await page.goto(BASE_URL, { waitUntil: 'networkidle2' });
  const loadTime = Date.now() - startTime;
  console.log(`   ✅ Page loaded in ${loadTime}ms`);
  console.log(`   ${loadTime < 2000 ? '✅' : '❌'} Target: <2000ms\n`);

  // Test 2: Service Worker Registration
  console.log('📊 Test 2: Service Worker Registration');
  const swInfo = await page.evaluate(async () => {
    try {
      const registration = await navigator.serviceWorker.ready;
      return {
        registered: true,
        active: registration.active?.state,
        scope: registration.scope
      };
    } catch (error) {
      return {
        registered: false,
        error: error.message
      };
    }
  });

  console.log(`   Service Worker: ${swInfo.registered ? '✅ Registered' : '❌ Not Registered'}`);
  if (swInfo.registered) {
    console.log(`   State: ${swInfo.active}`);
    console.log(`   Scope: ${swInfo.scope}`);
  } else {
    console.log(`   ⚠️  ${swInfo.error}`);
  }
  console.log('');

  // Test 3: Manifest
  console.log('📊 Test 3: Web App Manifest');
  const manifestInfo = await page.evaluate(async () => {
    const link = document.querySelector('link[rel="manifest"]');
    if (!link) return { found: false };

    const href = link.getAttribute('href');
    try {
      const response = await fetch(href);
      const manifest = await response.json();
      return {
        found: true,
        href,
        name: manifest.name,
        short_name: manifest.short_name,
        display: manifest.display,
        icons: manifest.icons?.length || 0
      };
    } catch (error) {
      return { found: true, error: error.message };
    }
  });

  console.log(`   Manifest: ${manifestInfo.found ? '✅ Found' : '❌ Not Found'}`);
  if (manifestInfo.found && !manifestInfo.error) {
    console.log(`   Name: ${manifestInfo.name}`);
    console.log(`   Short Name: ${manifestInfo.short_name}`);
    console.log(`   Display: ${manifestInfo.display}`);
    console.log(`   Icons: ${manifestInfo.icons}`);
  }
  console.log('');

  // Test 4: Cache Storage
  console.log('📊 Test 4: Cache Storage');
  const cacheInfo = await page.evaluate(async () => {
    try {
      const cacheNames = await caches.keys();
      const details = [];

      for (const name of cacheNames) {
        const cache = await caches.open(name);
        const keys = await cache.keys();
        details.push({
          name,
          count: keys.length
        });
      }

      return {
        success: true,
        count: cacheNames.length,
        caches: details
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  });

  console.log(`   Cache Storage: ${cacheInfo.success ? '✅ Available' : '❌ Error'}`);
  if (cacheInfo.success && cacheInfo.count > 0) {
    console.log(`   Total Caches: ${cacheInfo.count}`);
    cacheInfo.caches.forEach(c => {
      console.log(`   - ${c.name}: ${c.count} entries`);
    });
  } else if (cacheInfo.success) {
    console.log('   ⚠️  No caches found (normal for development mode)');
  }
  console.log('');

  // Test 5: Performance Metrics
  console.log('📊 Test 5: Performance Metrics');
  const metrics = await page.evaluate(() => {
    const perfData = performance.getEntriesByType('navigation')[0];
    return {
      domContentLoaded: Math.round(perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart),
      loadComplete: Math.round(perfData.loadEventEnd - perfData.loadEventStart),
      totalLoadTime: Math.round(perfData.loadEventEnd - perfData.fetchStart)
    };
  });

  console.log(`   DOM Content Loaded: ${metrics.domContentLoaded}ms`);
  console.log(`   Load Complete: ${metrics.loadComplete}ms`);
  console.log(`   Total Load Time: ${metrics.totalLoadTime}ms`);
  console.log('');

  // Summary
  console.log('═══════════════════════════════════════');
  console.log('✅ PWA Tests Completed');
  console.log('═══════════════════════════════════════');
  console.log('');
  console.log('📝 Summary:');
  console.log(`   - Page Load: ${loadTime < 2000 ? '✅ Pass' : '❌ Fail'} (${loadTime}ms)`);
  console.log(`   - Service Worker: ${swInfo.registered ? '✅ Pass' : '⚠️  Dev Mode Disabled'}`);
  console.log(`   - Manifest: ${manifestInfo.found ? '✅ Pass' : '❌ Fail'}`);
  console.log(`   - Cache Storage: ${cacheInfo.success ? '✅ Available' : '❌ Error'}`);
  console.log('');

  // Keep browser open for manual inspection
  console.log('🔍 Browser will remain open for 30 seconds for manual inspection...');
  await new Promise(resolve => setTimeout(resolve, 30000));

  await browser.close();
  console.log('✅ Tests complete!');
}

testPWA().catch(console.error);
