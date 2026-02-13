# Responsive Design Testing Guide

> **Version**: 1.0 | **Created**: 2026-02-12
> **Purpose**: Guide for testing responsive design across different viewports

---

## Overview

The responsive design tests verify that the Event2Table application works correctly across different screen sizes:
- **Mobile**: 375x667 (iPhone SE)
- **Tablet**: 768x1024 (iPad)
- **Desktop**: 1920x1080 (Full HD)
- **Widescreen**: 2560x1440 (2K)

---

## Problem Analysis

### Original Issue

The responsive design tests in `smoke-tests.spec.ts` were failing with:

```
Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:5173/
```

### Root Causes

1. **Dev Server Not Running**: Tests were executed without the Vite dev server running
2. **Test Configuration Conflict**: Responsive tests used `page.setViewportSize()` but Playwright's device presets (Mobile Chrome, Mobile Safari) override manual viewport settings
3. **Test Redundancy**: Responsive tests ran in ALL projects (chromium, firefox, webkit, mobile), creating 15 duplicate tests instead of 3 unique tests

### Solution Implemented

1. **Separate Test File**: Created `responsive-design.spec.ts` with dedicated viewport tests
2. **Project Isolation**: Configured Playwright to run responsive tests in a separate project without device emulation
3. **Auto-Start Server**: Added `webServer` configuration to auto-start Vite dev server if not running
4. **Better Assertions**: Enhanced responsive tests to verify sidebar behavior, layout, and no horizontal scroll

---

## File Structure

```
frontend/tests/e2e/
├── smoke-tests.spec.ts          # Core smoke tests (no responsive tests)
├── responsive-design.spec.ts     # NEW: Dedicated responsive tests
├── api-tests.spec.ts            # API integration tests
├── screenshots.spec.ts           # Visual regression tests
└── quick-smoke.spec.ts          # Quick smoke tests
```

---

## Test Configuration

### Playwright Projects

```typescript
// playwright.config.ts
projects: [
  {
    name: 'chromium',          // Desktop Chrome - all tests except responsive
    testIgnore: ['**/responsive-design.spec.ts']
  },
  {
    name: 'Mobile Chrome',      // Mobile device - all tests except responsive
    testIgnore: ['**/responsive-design.spec.ts']
  },
  {
    name: 'responsive-design',   // Dedicated responsive project
    testMatch: '**/responsive-design.spec.ts'
  }
]
```

### Viewport Configuration

```typescript
// responsive-design.spec.ts
test.describe('Responsive Design - Mobile Viewport', () => {
  test.use({
    viewport: { width: 375, height: 667 }, // iPhone SE
  });

  test('should load homepage on mobile viewport', async ({ page }) => {
    // Test implementation
  });
});
```

---

## Running Responsive Tests

### 1. Run Only Responsive Tests

```bash
cd /Users/mckenzie/Documents/event2table/frontend

# Run responsive tests only
npx playwright test responsive-design.spec.ts

# Run with UI
npx playwright test responsive-design.spec.ts --ui

# Run with debug mode
npx playwright test responsive-design.spec.ts --debug
```

### 2. Run All E2E Tests (including responsive)

```bash
# Run all E2E tests
npx playwright test

# Run all E2E tests for specific project
npx playwright test --project=chromium
npx playwright test --project=responsive-design
```

### 3. Run Specific Viewport Test

```bash
# Run only mobile tests
npx playwright test -g "Mobile Viewport"

# Run only tablet tests
npx playwright test -g "Tablet Viewport"

# Run only desktop tests
npx playwright test -g "Desktop Viewport"
```

---

## Test Coverage

### Mobile Viewport (375x667)

**Tests**:
- [x] Homepage loads without console errors
- [x] Games page navigates correctly
- [x] Mobile menu toggle is visible (if present)
- [x] Sidebar is collapsed or hidden
- [x] No horizontal scroll

**Expected Behavior**:
- Sidebar collapsed or hidden (`transform: translateX(-100%)`)
- Content fits in 375px width
- Mobile menu toggle visible

### Tablet Viewport (768x1024)

**Tests**:
- [x] Homepage loads without console errors
- [x] Events page navigates correctly
- [x] Sidebar is visible
- [x] Sidebar shows text content
- [x] No horizontal scroll

**Expected Behavior**:
- Sidebar fully visible
- Sidebar text not collapsed
- Content fits in 768px width

### Desktop Viewport (1920x1080)

**Tests**:
- [x] Homepage loads without console errors
- [x] Canvas page navigates correctly
- [x] Sidebar fully visible
- [x] Sidebar not collapsed
- [x] All sidebar text visible

**Expected Behavior**:
- Sidebar fully expanded
- All sidebar text visible (`opacity: 1`)
- Content uses full desktop width

### Widescreen Viewport (2560x1440)

**Tests**:
- [x] Homepage loads without console errors
- [x] Dashboard cards properly spaced
- [x] No content overflow
- [x] Cards use reasonable width

**Expected Behavior**:
- Content centered or left-aligned
- Cards have reasonable width (> 200px)
- No horizontal scroll

---

## Troubleshooting

### Issue: Tests Fail with "ERR_CONNECTION_REFUSED"

**Cause**: Dev server not running

**Solution**:
```bash
# Option 1: Manual start
cd /Users/mckenzie/Documents/event2table/frontend
npm run dev

# Option 2: Let Playwright auto-start (recommended)
# webServer config will auto-start if not running
npx playwright test
```

### Issue: Tests Timeout

**Cause**: Viewport switching + networkidle timeout

**Solution**:
```typescript
// Increase timeout for specific test
test('should load on mobile viewport', async ({ page }) => {
  await page.goto(BASE_URL, { timeout: 60000 });
  await page.waitForLoadState('networkidle', { timeout: 60000 });
});
```

### Issue: Sidebar Not Responsive

**Cause**: CSS media queries not applied

**Solution**:
```css
/* Sidebar.css */
@media (max-width: 767px) {
  .sidebar {
    transform: translateX(-100%);
  }

  .sidebar.mobile-open {
    transform: translateX(0);
  }
}
```

### Issue: Horizontal Scroll on Mobile

**Cause**: Content width exceeds viewport

**Solution**:
```css
/* Ensure content fits viewport */
.app-content {
  max-width: 100%;
  overflow-x: hidden;
}

.card {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}
```

---

## Best Practices

### 1. Test Isolation

Keep responsive tests separate from device emulation tests:
- **Responsive tests**: Manual viewport, no device emulation
- **Device tests**: Use device presets (Mobile Chrome, iPhone 12)

### 2. Assertions

Verify specific responsive behavior:
- **Mobile**: Sidebar collapsed/hidden
- **Tablet**: Sidebar visible with text
- **Desktop**: Sidebar fully expanded
- **All**: No horizontal scroll

### 3. Console Error Detection

Always check for console errors:
```typescript
const errors = setupConsoleErrorCollector(page);
// ... test actions ...
expect(errors.length).toBe(0);
```

### 4. Network Idle

Wait for network idle to ensure all resources loaded:
```typescript
await page.goto(BASE_URL);
await page.waitForLoadState('networkidle', { timeout: 30000 });
```

---

## CI/CD Integration

### GitHub Actions

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - name: Install dependencies
        run: npm ci
      - name: Install Playwright
        run: npx playwright install --with-deps
      - name: Run E2E tests
        run: npx playwright test
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
```

### Local Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running E2E tests..."

npx playwright test --project=responsive-design

if [ $? -ne 0 ]; then
  echo "E2E tests failed. Commit aborted."
  exit 1
fi
```

---

## Future Improvements

1. **Visual Regression Testing**: Add screenshot comparison for responsive layouts
2. **Performance Testing**: Measure Core Web Vitals per viewport
3. **Accessibility Testing**: Verify a11y features on mobile/tablet
4. **Touch Interaction**: Test swipe gestures on mobile viewports

---

## Resources

- [Playwright Viewport Documentation](https://playwright.dev/docs/emulation)
- [Playwright Device Emulation](https://playwright.dev/docs/emulation#devices)
- [MDN Responsive Design](https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design)
- [CSS Media Queries](https://developer.mozilla.org/en-US/docs/Web/CSS/Media_Queries)

---

**Last Updated**: 2026-02-12
**Maintainer**: Event2Table Development Team
