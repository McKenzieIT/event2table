/**
 * Visual Regression Tests
 * 
 * Tests UI consistency across optimized pages
 * Uses pixelmatch for screenshot comparison
 * 
 * Run: npx playwright test test/e2e/visual/visual-regression.spec.ts
 * 
 * First run (create baseline):
 *   npx playwright test test/e2e/visual/visual-regression.spec.ts --update-baseline
 * 
 * Update baseline:
 *   UPDATE_BASELINE=1 npx playwright test test/e2e/visual/visual-regression.spec.ts
 */

import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';
import pixelmatch from 'pixelmatch';
import { PNG } from 'pngjs';
import { testPages, getPageUrl } from './pages/test-pages';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const BASE_URL = process.env.BASE_URL || 'http://localhost:5173';
const UPDATE_BASELINE = process.env.UPDATE_BASELINE === '1' || process.argv.includes('--update-baseline');

const OUTPUT_DIR = path.join(__dirname, 'output', 'visual');
const BASELINE_DIR = path.join(OUTPUT_DIR, 'baseline');
const CURRENT_DIR = path.join(OUTPUT_DIR, 'current');
const DIFF_DIR = path.join(CURRENT_DIR, 'diff');

const THRESHOLD = 0.1;

const PAGE_TIMEOUT = 90000;
const SELECTOR_TIMEOUT = 30000;

async function waitForPageContent(page: any, selector: string): Promise<boolean> {
  try {
    await page.waitForSelector(selector, { timeout: SELECTOR_TIMEOUT });
    return true;
  } catch {
    console.log(`Warning: Primary selector ${selector} not found, trying alternatives...`);
    
    const alternatives = [
      selector.replace('.games-list-page', '[class*="games-list"]'),
      selector.replace('.events-list-page', '[class*="events-list"]'),
      selector.replace('.parameters-list-container', '[class*="parameters-list"]'),
      selector.replace('.canvas-page', '[class*="canvas"]'),
      'main',
      '#root',
      '.app',
    ];
    
    for (const alt of alternatives) {
      try {
        await page.waitForSelector(alt, { timeout: 5000 });
        console.log(`Found alternative selector: ${alt}`);
        return true;
      } catch {
        continue;
      }
    }
    
    console.log(`Warning: No selector found for page content, proceeding anyway`);
    return false;
  }
}

test.describe('Visual Regression Tests', () => {
  testPages.forEach((page) => {
    test(`should match baseline screenshot for ${page.name}`, async ({ page: playwrightPage }) => {
      const screenshotName = `${page.name.toLowerCase().replace(/\s+/g, '-')}.png`;
      const baselinePath = path.join(BASELINE_DIR, screenshotName);
      const currentPath = path.join(CURRENT_DIR, screenshotName);
      const diffPath = path.join(DIFF_DIR, screenshotName);

      await playwrightPage.goto(getPageUrl(page), { timeout: PAGE_TIMEOUT, waitUntil: 'commit' });
      
      if (page.waitForSelector) {
        await waitForPageContent(playwrightPage, page.waitForSelector);
      }
      
      await playwrightPage.waitForTimeout(3000);

      const screenshot = await playwrightPage.screenshot({
        fullPage: true,
        type: 'png',
      });

      if (UPDATE_BASELINE) {
        fs.mkdirSync(BASELINE_DIR, { recursive: true });
        fs.writeFileSync(baselinePath, screenshot);
        console.log(`Updated baseline: ${baselinePath}`);
        return;
      }

      if (!fs.existsSync(baselinePath)) {
        console.log(`Baseline not found: ${baselinePath}, creating new baseline...`);
        fs.mkdirSync(BASELINE_DIR, { recursive: true });
        fs.writeFileSync(baselinePath, screenshot);
        console.log(`Created baseline: ${baselinePath}`);
        return;
      }

      fs.mkdirSync(CURRENT_DIR, { recursive: true });
      fs.mkdirSync(DIFF_DIR, { recursive: true });
      fs.writeFileSync(currentPath, screenshot);

      const baselineImage = PNG.sync.read(fs.readFileSync(baselinePath));
      const currentImage = PNG.sync.read(fs.readFileSync(currentPath));

      const { width, height } = baselineImage;
      const diff = new PNG({ width, height });

      const numDiffPixels = pixelmatch(
        baselineImage.data,
        currentImage.data,
        diff.data,
        width,
        height,
        { threshold: THRESHOLD, alpha: 0.3, antialiased: false, includeAA: false }
      );

      const totalPixels = width * height;
      const diffPercentage = (numDiffPixels / totalPixels) * 100;

      if (numDiffPixels > 0) {
        fs.writeFileSync(diffPath, PNG.sync.write(diff));
        console.log(`Diff saved: ${diffPath}`);
        console.log(`Difference: ${numDiffPixels} pixels (${diffPercentage.toFixed(2)}%)`);
      }

      expect(numDiffPixels, `Visual regression detected for ${page.name}. See ${diffPath} for diff image.`).toBe(0);
    });
  });
});

test.describe('Page Load Without Errors', () => {
  testPages.forEach((page) => {
    test(`${page.name} should load without console errors`, async ({ page: playwrightPage }) => {
      const consoleErrors: string[] = [];
      
      playwrightPage.on('console', msg => {
        if (msg.type() === 'error') {
          const text = msg.text();
          if (!text.includes('favicon.ico') && !text.includes('404')) {
            consoleErrors.push(text);
          }
        }
      });

      await playwrightPage.goto(getPageUrl(page), { timeout: PAGE_TIMEOUT, waitUntil: 'commit' });
      
      if (page.waitForSelector) {
        await waitForPageContent(playwrightPage, page.waitForSelector).catch(() => {});
      }
      
      await playwrightPage.waitForTimeout(3000);

      expect(consoleErrors, `Console errors found on ${page.name}: ${consoleErrors.join(', ')}`).toHaveLength(0);
    });
  });
});

test.describe('Critical Elements Visibility', () => {
  test('Dashboard should load successfully', async ({ page }) => {
    await page.goto(`${BASE_URL}/`, { timeout: PAGE_TIMEOUT, waitUntil: 'commit' });
    await page.waitForTimeout(3000);
    
    const dashboard = page.locator('.dashboard-container, [data-testid="dashboard-container"]');
    await expect(dashboard.first()).toBeVisible({ timeout: 60000 });
  });
});
