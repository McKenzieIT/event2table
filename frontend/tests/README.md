# Playwright Testing Guide - event2table Frontend

## Quick Start

### Prerequisites
- Node.js v25.6.0 installed
- Dev server running on http://localhost:5173
- Backend API on http://127.0.0.1:5001 (optional, for full integration tests)

### Running Tests

#### 1. Screenshot Tests (Recommended - Fast & Reliable)
```bash
cd /Users/mckenzie/Documents/event2table/frontend
/usr/local/Cellar/node/25.6.0/bin/node ./node_modules/.bin/playwright test tests/e2e/screenshots.spec.ts --reporter=list
```

#### 2. Quick Smoke Tests
```bash
cd /Users/mckenzie/Documents/event2table/frontend
/usr/local/Cellar/node/25.6.0/bin/node ./node_modules/.bin/playwright test tests/e2e/quick-smoke.spec.ts --reporter=list --project=chromium
```

#### 3. Full Smoke Tests (All Browsers)
```bash
cd /Users/mckenzie/Documents/event2table/frontend
/usr/local/Cellar/node/25.6.0/bin/node ./node_modules/.bin/playwright test tests/e2e/smoke-tests.spec.ts --reporter=list
```

#### 4. API Integration Tests
```bash
cd /Users/mckenzie/Documents/event2table/frontend
/usr/local/Cellar/node/25.6.0/bin/node ./node_modules/.bin/playwright test tests/e2e/api-tests.spec.ts --reporter=list
```

#### 5. Performance Tests
```bash
cd /Users/mckenzie/Documents/event2table/frontend
/usr/local/Cellar/node/25.6.0/bin/node ./node_modules/.bin/playwright test tests/performance/canvas-performance.spec.ts --reporter=list
```

## Test Files

| File | Purpose | Tests | Status |
|------|---------|-------|--------|
| `tests/e2e/screenshots.spec.ts` | Visual verification | 6 | ✅ Working |
| `tests/e2e/quick-smoke.spec.ts` | Fast page load checks | 6 | ⚠️ Needs timeout fix |
| `tests/e2e/smoke-tests.spec.ts` | Comprehensive smoke tests | 39 | ⚠️ Needs networkidle fix |
| `tests/e2e/api-tests.spec.ts` | API integration tests | 11 | ✅ Ready |
| `tests/performance/canvas-performance.spec.ts` | Performance benchmarks | 19 | ✅ Existing |

## Viewing Test Results

### HTML Report
```bash
cd /Users/mckenzie/Documents/event2table/frontend
/usr/local/Cellar/node/25.6.0/bin/node ./node_modules/.bin/playwright show-report
```

### Screenshots
```bash
ls -lh /Users/mckenzie/Documents/event2table/frontend/screenshots/
```

## Troubleshooting

### Issue: Tests timeout after 60 seconds
**Cause**: Using `waitForLoadState('networkidle')` which never completes due to continuous polling

**Solution**: Use `domcontentloaded` or specific element selectors instead:
```typescript
// ❌ Don't do this
await page.waitForLoadState('networkidle');

// ✅ Do this instead
await page.waitForLoadState('domcontentloaded');
await page.waitForSelector('[data-testid="games-list"]');
```

### Issue: Port 5173 already in use
**Check what's running**:
```bash
lsof -ti:5173
```

**Kill existing process**:
```bash
kill -9 $(lsof -ti:5173)
```

**Start dev server**:
```bash
cd /Users/mckenzie/Documents/event2table/frontend
npm run dev
```

### Issue: Playwright browsers not installed
```bash
cd /Users/mckenzie/Documents/event2table/frontend
/usr/local/Cellar/node/25.6.0/bin/node ./node_modules/.bin/playwright install
```

## Writing New Tests

### Basic Test Template
```typescript
import { test, expect } from '@playwright/test';

test.describe('My Feature', () => {
  test('should do something', async ({ page }) => {
    // Navigate to page
    await page.goto('http://localhost:5173/#/my-page');

    // Wait for content
    await page.waitForLoadState('domcontentloaded');

    // Check element exists
    await expect(page.locator('h1')).toContainText('My Page');

    // Take screenshot
    await page.screenshot({ path: 'screenshots/my-page.png' });
  });
});
```

### Best Practices

1. **Use data-testid attributes** for reliable selectors:
   ```jsx
   <button data-testid="save-button">Save</button>
   ```
   ```typescript
   await page.click('[data-testid="save-button"]');
   ```

2. **Wait for specific elements**, not network state:
   ```typescript
   // ✅ Good
   await page.waitForSelector('[data-testid="games-list"]');

   // ❌ Bad (may timeout)
   await page.waitForLoadState('networkidle');
   ```

3. **Use assertions** to verify state:
   ```typescript
   await expect(page.locator('h1')).toBeVisible();
   await expect(page.locator('.error')).not.toBeVisible();
   ```

4. **Add helpful test names**:
   ```typescript
   test('should display error message when form is invalid', async ({ page }) => {
     // ...
   });
   ```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Playwright Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 25
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run test:e2e
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
```

## Resources

- **Playwright Docs**: https://playwright.dev
- **Test Configuration**: `/Users/mckenzie/Documents/event2table/frontend/playwright.config.ts`
- **Test Summary**: `/Users/mckenzie/Documents/event2table/PLAYWRIGHT_TEST_SUMMARY.md`
- **Screenshots**: `/Users/mckenzie/Documents/event2table/frontend/screenshots/`

## Support

For issues or questions about the tests:
1. Check the test summary document
2. Review Playwright documentation
3. Check browser console for errors
4. Verify dev server is running on port 5173
