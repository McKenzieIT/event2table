# E2E Testing Quick Reference - Timeout Edition

> **Fast lookup guide for common timeout scenarios**

---

## Quick Fix: Import Errors ❌→✅

**Problem**: Tests fail with "Cannot find module '../helpers/wait-helpers'"

**Solution**:
```bash
# Helpers are now available at:
test/e2e/helpers/wait-helpers.ts
test/e2e/helpers/game-context.ts
```

---

## Quick Fix: Test Timeouts ❌→✅

**Problem**: Test fails with "Timeout 30000ms exceeded"

**Solution 1**: Use helper function
```typescript
// Before
await page.waitForTimeout(5000);

// After
await waitForReactMount(page, 100);
```

**Solution 2**: Override timeout for specific test
```typescript
test('slow canvas test', async ({ page }) => {
  test.setTimeout(90000); // 90 seconds
  // ... test code
});
```

**Solution 3**: Use faster wait strategy
```typescript
// Before (slow)
await page.waitForLoadState('networkidle');

// After (fast)
await page.waitForLoadState('domcontentloaded');
```

---

## Timeout Cheat Sheet

| Scenario | Timeout | Code |
|----------|----------|------|
| **Standard test** | 30s action / 60s nav | Use default |
| **Slow test** | 90s | `test.setTimeout(90000)` |
| **API test** | 15s action / 30s nav | Use `--project=api-contract` |
| **Firefox test** | 45s action / 90s nav | Use `--project=firefox-critical` |
| **Mobile test** | 40s action / 80s nav | Use `--project=mobile-critical` |

---

## Page-Specific Timeouts

```typescript
// Dashboard (lightweight)
test.setTimeout(30000);
await page.goto('/#/');

// Games List (moderate)
test.setTimeout(45000);
await page.goto('/#/games');

// Events List (moderate)
test.setTimeout(45000);
await navigateAndSetGameContext(page, '/events', '10000147');

// Canvas (complex)
test.setTimeout(90000);
await navigateAndSetGameContext(page, '/canvas', '10000147');
```

---

## Wait Strategy Cheat Sheet

```typescript
// ❌ SLOW: Wait for all network activity
await page.waitForLoadState('networkidle');

// ✅ FAST: Wait for DOM content
await page.waitForLoadState('domcontentloaded');

// ✅ FASTER: Wait for specific element
await page.waitForSelector('#app-root', { state: 'visible' });

// ✅ FASTEST: Use helper
await waitForReactMount(page, 100);
```

---

## Running Tests with Different Timeouts

```bash
# Run all tests with standard timeouts
npx playwright test

# Run smoke tests (faster timeouts)
npx playwright test --project=smoke

# Run critical tests (standard timeouts)
npx playwright test --project=critical

# Run API tests (minimal timeouts)
npx playwright test --project=api-contract

# Run Firefox tests (extended timeouts)
npx playwright test --project=firefox-critical
```

---

## Common Timeout Scenarios

### Scenario 1: Canvas Page Times Out

```typescript
test('canvas loads correctly', async ({ page }) => {
  // Extend timeout for complex page
  test.setTimeout(90000);

  await navigateAndSetGameContext(page, '/canvas', '10000147');
  await waitForReactMount(page, 300);

  // Wait for specific element
  await expect(page.locator('.canvas-container')).toBeVisible({ timeout: 30000 });
});
```

### Scenario 2: Events List Needs Game Context

```typescript
test('events list loads', async ({ page }) => {
  // Set game context before navigation
  await navigateAndSetGameContext(page, '/events', '10000147');
  await waitForReactMount(page, 150);

  // Verify data loaded
  await expect(page.locator('.event-row').first()).toBeVisible({ timeout: 10000 });
});
```

### Scenario 3: API Test is Too Slow

```typescript
test('API returns data', async ({ page }) => {
  // API tests use minimal timeouts automatically
  // Just use default, no need to extend
  const response = await page.request.get('/api/games');
  expect(response.status()).toBe(200);
});
```

---

## Helper Functions Quick Reference

### `waitForReactMount(page, multiplier)`

Quick check that React has mounted:

```typescript
await waitForReactMount(page, 100); // 100ms wait
```

### `waitForDataLoad(page, selector, options)`

Wait for data to load:

```typescript
await waitForDataLoad(page, '[data-loaded="true"]', { timeout: 10000 });
```

### `waitForVisible(page, selector, options)`

Wait for element to be visible:

```typescript
await waitForVisible(page, '.submit-button', { timeout: 5000 });
```

### `waitForCondition(page, condition, options)`

Wait for custom condition:

```typescript
await waitForCondition(
  page,
  async () => await page.locator('.data-loaded').count() > 0,
  { timeout: 10000, interval: 100 }
);
```

### `navigateAndSetGameContext(page, path, gameGid)`

Navigate and set game context:

```typescript
await navigateAndSetGameContext(page, '/events', '10000147');
```

### `setGameContext(page, gameGid, gameData)`

Set game context without navigation:

```typescript
await setGameContext(page, '10000147', { gid: '10000147', name: 'Test Game' });
```

### `clearGameContext(page)`

Clear game context:

```typescript
await clearGameContext(page);
```

---

## Troubleshooting

### Test fails with "Timeout exceeded"

1. **Identify slow operation**:
   ```typescript
   console.time('operation');
   await page.goto('/#/canvas');
   console.timeEnd('operation');
   ```

2. **Extend timeout**:
   ```typescript
   test.setTimeout(90000);
   ```

3. **Use faster wait**:
   ```typescript
   await page.waitForLoadState('domcontentloaded');
   ```

### Test is too slow

1. **Use faster wait strategy**:
   ```typescript
   await waitForReactMount(page, 100);
   ```

2. **Wait for specific element**:
   ```typescript
   await page.waitForSelector('#app-root', { state: 'visible' });
   ```

3. **Use smoke test project**:
   ```bash
   npx playwright test --project=smoke
   ```

### Test fails intermittently

1. **Add retry** (in `playwright.config.ts`):
   ```typescript
   retries: 2
   ```

2. **Increase timeout**:
   ```typescript
   test.setTimeout(90000);
   ```

3. **Use more robust selector**:
   ```typescript
   await page.click('[data-testid="submit-button"]');
   ```

---

## Full Documentation

For detailed information, see:
- [Timeout Optimization Guide](../../docs/development/timeout-optimization-guide.md)
- [E2E Testing README](./README.md)
- [Playwright Config](./playwright.config.ts)

---

**Version**: 1.0
**Last Updated**: 2026-02-12
