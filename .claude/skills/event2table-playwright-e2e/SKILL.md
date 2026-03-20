---
name: event2table-playwright-e2e
description: Playwright E2E testing for Event2Table. Use this skill whenever the user mentions E2E testing, end-to-end testing, browser automation, Playwright, running tests, converting agent-browser tests, or wants to test the Event2Table web application. This skill helps set up Playwright, convert agent-browser JSON tests to Playwright TypeScript, run complete test suites, generate comparison reports, and debug test failures. Always use this skill for Event2Table E2E testing needs instead of agent-browser or other browser automation tools.
compatibility: Requires Node.js, npm, and Playwright. Uses TypeScript for test files.
---

# Event2Table Playwright E2E Testing

Complete Playwright-based end-to-end testing solution for Event2Table. This skill replaces agent-browser with a more reliable, faster, and feature-rich testing framework.

## Why Playwright?

**Playwright delivers 100% pass rate vs agent-browser's 25.6%** because:
- ✅ No daemon crashes ("os error 35")
- ✅ Handles React SPA network activity correctly
- ✅ 6-18x faster test execution
- ✅ Built-in debugging (screenshots, videos, traces)
- ✅ Multi-browser support (Chromium, Firefox, WebKit)
- ✅ Mobile device emulation

## Quick Start

### Prerequisites

1. **Node.js installed** (v18+ required)
   ```bash
   node --version  # Should show v18+
   ```

2. **Frontend dev server running**
   ```bash
   cd /Users/mckenzie/Documents/event2table/frontend
   npm run dev  # Should start on http://localhost:5173
   ```

### First-Time Setup

```bash
# Navigate to playwright-tests directory
cd /Users/mckenzie/Documents/event2table/playwright-tests

# Install dependencies
export PATH="/usr/local/Cellar/node/25.6.0/bin:$PATH"
npm install

# Install Playwright browsers
npx playwright install chromium
```

### Running Tests

```bash
# Run all tests
npm test

# Run with visible browser (for debugging)
npm run test:headed

# View HTML report
npm run test:report

# Run specific test file
npx playwright test tests/e2e/AN-001-dashboard-load-and-display.spec.ts

# Run tests on specific browser
npm run test:chrome    # Chromium only
npm run test:firefox   # Firefox only
npm run test:safari     # WebKit only
```

## Test Conversion

### Converting Agent-Browser Tests to Playwright

All agent-browser JSON tests are automatically convertible to Playwright TypeScript.

**Source location**: `/Users/mckenzie/Documents/event2table/.claude/skills/event2table-universal-test/tests/`

**Conversion command**:
```bash
cd /Users/mckenzie/Documents/event2table/playwright-tests

# Convert all tests
npx tsx utils/convert-tests.ts --verbose

# Convert specific test
npx tsx utils/convert-tests.ts --test=AN-005

# Dry run (preview without writing)
npx tsx utils/convert-tests.ts --dry-run
```

**Converted tests location**: `/Users/mckenzie/Documents/event2table/playwright-tests/tests/e2e/`

### Conversion Mapping

The converter handles these agent-browser actions:

| Agent-Browser Action | Playwright Equivalent |
|---------------------|----------------------|
| `wait` + selector | `page.waitForSelector(selector)` |
| `validate` + element_exists | `expect(locator).toBeVisible()` |
| `validate` + console_clean | Console error collection |
| `screenshot` | `page.screenshot()` |
| `snapshot` | `page.content()` |
| `click` | `page.click(selector)` |
| `fill` | `page.fill(selector, value)` |
| `goto` | `page.goto(url)` |

## Test Structure

### Generated Test File Format

Each converted test follows this structure:

```typescript
import { test, expect } from '@playwright/test';

test('test name', async ({ page }) => {
  // 1. Navigate to page
  await page.goto(url);

  // 2. Wait for page to load
  await page.waitForSelector(selector, { timeout: 60000 });

  // 3. Collect console errors (automatic)
  const consoleErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });

  // 4. Validate expectations
  await expect(page.locator(selector)).toBeVisible();

  // 5. Screenshot on failure (automatic)
});
```

### Test Organization

```
playwright-tests/
├── tests/
│   └── e2e/
│       ├── AN-*.spec.ts          # Acceptance tests
│       ├── REG-*.spec.ts         # Regression tests
│       └── example.spec.ts       # Example tests
├── output/
│   ├── screenshots/              # Failure screenshots
│   └── reports/                  # Test reports
└── utils/
    ├── convert-tests.ts         # Test converter
    └── test-helpers.ts          # Helper utilities
```

## Debugging Test Failures

### 1. View Test Results

```bash
# Open HTML report
npm run test:report

# View specific test failure
open output/test-results/<test-name>/index.html
```

### 2. Inspect Screenshots and Videos

Playwright automatically captures:
- **Screenshot** on test failure
- **Video** recording of entire test
- **Trace** file for step-by-step debugging

**Location**: `output/test-results/<test-name>/`

**View trace**:
```bash
npx playwright show-trace output/test-results/<test-name>/trace.zip
```

### 3. Run in Headed Mode

See the test execute in real-time:
```bash
npm run test:headed
```

### 4. Debug Mode

```bash
npm run test:debug
```

This opens Playwright Inspector where you can:
- Step through tests
- Inspect selectors
- See console logs
- Modify test code live

### 5. Common Issues and Solutions

**Issue**: Test fails with "Timeout waiting for selector"

**Solution**:
- Check if selector is correct
- Verify frontend dev server is running
- Increase timeout: `await page.waitForSelector(selector, { timeout: 120000 })`
- Check browser console for JavaScript errors

**Issue**: "Cannot find page" error

**Solution**:
- Ensure URL includes game_gid parameter: `http://localhost:5173/parameters?game_gid=10000147`
- Check if game exists in database
- Verify backend API is responding

**Issue**: Console errors causing test failures

**Solution**:
- Fix the underlying console errors (404, 500)
- Or add `expect.soft()` instead of `expect()` for non-critical errors

## Comparison with Agent-Browser

### Performance Comparison

| Metric | Agent-Browser | Playwright | Improvement |
|--------|-------------|-----------|-------------|
| **Pass Rate** | 25.6% (10/39) | 100% (39/39) | +74.4% |
| **Reliability** | Daemon crashes | Zero crashes | 100% stable |
| **Speed** | 60-120s/test | 8-20s/test | 6-15x faster |
| **Debugging** | Manual screenshots | Auto screenshots + videos | Full context |
| **Browsers** | Chromium only | 4 browsers + mobile | 5x coverage |

### When to Use Each Tool

**Use Playwright** (preferred):
- ✅ All E2E testing
- ✅ React SPA applications
- ✅ Cross-browser testing
- ✅ Mobile device testing
- ✅ CI/CD pipelines
- ✅ Debugging test failures

**Use agent-browser** (legacy):
- ❌ Not recommended for Event2Table
- ⚠️ Only if Playwright unavailable

## Best Practices

### 1. Test Organization

- **One test per file**: Each `.spec.ts` file contains one test
- **Descriptive names**: Test names should describe what is being tested
- **Page Object Model**: Extract common selectors and actions to helper functions

### 2. Selector Strategy

- **Prefer data-testid**: Most stable across code changes
- **CSS classes**: Next best option
- **Text selectors**: Use as last resort
- **Avoid XPath**: Brittle and hard to maintain

### 3. Waiting Strategies

```typescript
// ✅ Good: Wait for specific element
await page.waitForSelector('.parameters-table-container');

// ❌ Bad: Fixed timeout
await page.waitForTimeout(5000);

// ✅ Good: Wait for network idle
await page.waitForLoadState('networkidle');

// ✅ Good: Wait for navigation
await page.waitForURL('**/parameters')
```

### 4. Error Handling

```typescript
// Use soft assertions for non-critical checks
await expect.soft(page.locator('.optional-element')).toBeVisible();

// Use hard assertions for critical checks
await expect(page.locator('.submit-button')).toBeEnabled();
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd playwright-tests
          npm install
          npx playwright install --with-deps
      - name: Install Playwright browsers
        run: npx playwright install --with-deps
      - name: Run E2E tests
        run: |
          cd frontend
          npm run dev &
          cd ../playwright-tests
          npm test
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-tests/playwright-report/
          retention-days: 30
```

## Troubleshooting

### Issue: "npm command not found"

**Solution**: Add Node to PATH
```bash
export PATH="/usr/local/Cellar/node/25.6.0/bin:$PATH"
```

### Issue: "Playwright not found"

**Solution**: Install Playwright browsers
```bash
npx playwright install chromium
```

### Issue: Tests timeout on page load

**Solution**:
1. Verify frontend dev server is running: `npm run dev` in `frontend/`
2. Check URL is accessible: `curl http://localhost:5173`
3. Increase timeout in test: `await page.waitForSelector(selector, { timeout: 120000 })`

### Issue: "Cannot find module tsx"

**Solution**: Install tsx globally
```bash
npm install -g tsx
```

## Advanced Usage

### Custom Test Helpers

See `utils/test-helpers.ts` for reusable functions:
- `waitForPageStable()` - Wait for network idle
- `checkConsoleErrors()` - Collect console errors
- `setGameContext()` - Set game context for tests
- `getByTestId()` - Get element by data-testid

### Running Tests in Parallel

By default, Playwright runs tests in parallel using multiple workers. To control parallelism:

```bash
# Run with 4 workers
npx playwright test --workers=4

# Run serially (one at a time)
npx playwright test --workers=1
```

### Mobile Device Testing

```typescript
import { test, devices } from '@playwright/test';

test('mobile test', async ({ page }) => {
  // Use iPhone 13 emulation
  await page.goto('http://localhost:5173');
  // Test mobile-specific behavior
});
```

## References

- **Playwright Documentation**: https://playwright.dev
- **Comparison Report**: `/Users/mckenzie/Documents/event2table/output/PLAYWRIGHT-VS-AGENT-BROWSER-COMPARISON.md`
- **Selector Fix Report**: `/Users/mckenzie/Documents/event2table/output/E2E-SELECTOR-FIX-REPORT.md`
- **P1 Optimization Report**: `/Users/mckenzie/Documents/event2table/output/E2E-TEST-P1-OPTIMIZATION-COMPLETE.md`

## Support

For issues or questions:
1. Check test output in `output/test-results/`
2. Review screenshots and traces
3. Consult troubleshooting section above
4. Check comparison report for agent-browser vs Playwright differences
