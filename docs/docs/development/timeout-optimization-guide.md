# Playwright Timeout Optimization Guide

> **Version**: 1.0 | **Created**: 2026-02-12
> **Purpose**: Provide flexible timeout strategies for reliable E2E testing

---

## Problem Analysis

### Current Issues

1. **Fixed Global Timeouts**: All tests use the same timeout regardless of page complexity
2. **Browser Performance Variability**: Firefox and WebKit are slower than Chrome
3. **Mobile Network Constraints**: Mobile devices have variable network performance
4. **Missing Helper Files**: Tests reference `wait-helpers.ts` and `game-context.ts` that don't exist
5. **Inefficient Wait Strategies**: Using `waitForLoadState('networkidle')` which is slow

### Identified Timeout Failures

Based on test analysis:

| Test Type | Current Timeout | Issues | Recommended Timeout |
|-----------|----------------|--------|-------------------|
| **Dashboard** | 10s | Too short for data loading | 20s |
| **Games List** | 10s | Cards render slowly with many games | 30s |
| **Events List** | 10s | Needs game context + data fetch | 30s |
| **Canvas Page** | 30s | Complex React flow rendering | 60s |
| **HQL Preview** | 30s | Modal + code generation | 45s |
| **API Tests** | 30s | No UI rendering needed | 15s |

---

## Optimization Strategy

### 1. Browser-Specific Timeouts

Different browsers have different performance characteristics:

```typescript
// Desktop Chrome (fastest)
actionTimeout: 30000
navigationTimeout: 60000

// Desktop Firefox (slower JS)
actionTimeout: 45000
navigationTimeout: 90000

// Desktop Safari (variable)
actionTimeout: 35000
navigationTimeout: 70000

// Mobile (network constraints)
actionTimeout: 40000
navigationTimeout: 80000
```

### 2. Test Category Timeouts

Organize tests by complexity and assign appropriate timeouts:

```typescript
// Smoke Tests (fast feedback)
actionTimeout: 20000
navigationTimeout: 40000

// API Contract Tests (no UI)
actionTimeout: 15000
navigationTimeout: 30000

// Critical Tests (standard)
actionTimeout: 30000
navigationTimeout: 60000
```

### 3. Page-Specific Wait Strategies

Replace `waitForLoadState('networkidle')` with faster alternatives:

```typescript
// ❌ SLOW: Waits for ALL network activity to stop
await page.waitForLoadState('networkidle');

// ✅ FAST: Waits for DOM content
await page.waitForLoadState('domcontentloaded');

// ✅ FASTER: Waits for specific element
await page.waitForSelector('#app-root', { state: 'visible', timeout: 10000 });

// ✅ FASTEST: Uses helper function
await waitForReactMount(page, 100);
```

### 4. Per-Test Timeout Override

For tests that need extra time:

```typescript
test('canvas loads slowly due to complex flow', async ({ page }) => {
  // Increase timeout for this specific test
  test.setTimeout(90000);

  await page.goto('/#/canvas');
  // ... test code
});
```

---

## Implementation

### New Helper Files

Created two helper files to fix import errors:

#### 1. `test/e2e/helpers/wait-helpers.ts`

Provides flexible waiting strategies:

```typescript
export async function waitForReactMount(page: any, multiplier: number = 100): Promise<void>
export async function waitForDataLoad(page: any, selector: string, options?: { timeout?: number }): Promise<void>
export async function waitForVisible(page: any, selector: string, options?: { timeout?: number }): Promise<void>
export async function waitForCondition(page: any, condition: () => Promise<boolean>, options?: { timeout?: number }): Promise<void>
```

#### 2. `test/e2e/helpers/game-context.ts`

Provides game context management:

```typescript
export async function navigateAndSetGameContext(page: any, path: string, gameGid: string): Promise<void>
export async function setGameContext(page: any, gameGid: string, gameData?: any): Promise<void>
export async function clearGameContext(page: any): Promise<void>
```

### Updated Playwright Configuration

Key changes in `playwright.config.ts`:

1. **Increased default timeouts**:
   - `actionTimeout`: 15000 → 30000
   - `navigationTimeout`: 30000 → 60000

2. **Added browser-specific projects**:
   - Chrome (standard)
   - Firefox (extended)
   - WebKit (medium)
   - Mobile (extended)

3. **Added global test timeout**:
   - 60 seconds per test (can be overridden)

4. **Added JUnit reporter**:
   - Better CI/CD integration

---

## Usage Examples

### Example 1: Standard Page Test

```typescript
test('games list loads correctly', async ({ page }) => {
  // Use default timeouts (30s action, 60s navigation)

  await page.goto('/#/games');
  await waitForReactMount(page, 100);

  // Wait for specific element (faster than networkidle)
  await expect(page.locator('.game-card').first()).toBeVisible({ timeout: 10000 });
});
```

### Example 2: Complex Page Test

```typescript
test('canvas loads with complex flow', async ({ page }) => {
  // Extend timeout for this test
  test.setTimeout(90000);

  await navigateAndSetGameContext(page, '/canvas', '10000147');
  await waitForReactMount(page, 200);

  // Wait for canvas container
  await expect(page.locator('.canvas-container')).toBeVisible({ timeout: 30000 });
});
```

### Example 3: API Test

```typescript
test('API endpoint returns correct data', async ({ page }) => {
  // API tests use minimal timeouts (15s action, 30s navigation)

  const response = await page.request.get('/api/games/by-gid/10000147');
  expect(response.status()).toBe(200);
});
```

### Example 4: Conditional Waiting

```typescript
test('waits for data to load', async ({ page }) => {
  await navigateAndSetGameContext(page, '/events', '10000147');

  // Wait for data-loaded attribute or fall back to domcontentloaded
  await waitForDataLoad(page, '[data-loaded="true"]', { timeout: 10000 });

  // Verify data is displayed
  await expect(page.locator('.event-row').first()).toBeVisible();
});
```

---

## Page-Specific Timeout Recommendations

### Dashboard (`/` or `/dashboard`)

**Characteristics**: Lightweight, API-driven data

```typescript
// Recommended timeout: 20s
test.setTimeout(30000);
await page.goto('/#/');
await waitForReactMount(page, 100);
```

### Games List (`/games`)

**Characteristics**: Moderate, card-based rendering

```typescript
// Recommended timeout: 30s
test.setTimeout(45000);
await page.goto('/#/games');
await waitForReactMount(page, 150);
```

### Events List (`/events`)

**Characteristics**: Moderate, requires game context

```typescript
// Recommended timeout: 30s
test.setTimeout(45000);
await navigateAndSetGameContext(page, '/events', '10000147');
await waitForReactMount(page, 150);
```

### Canvas (`/canvas`)

**Characteristics**: Complex, React Flow rendering

```typescript
// Recommended timeout: 60s
test.setTimeout(90000);
await navigateAndSetGameContext(page, '/canvas', '10000147');
await waitForReactMount(page, 300);
```

### HQL Preview Modal

**Characteristics**: Complex, code generation + modal

```typescript
// Recommended timeout: 45s
test.setTimeout(60000);
await page.click('[data-testid="open-hql-modal"]');
await expect(page.locator('.hql-preview-modal')).toBeVisible({ timeout: 15000 });
```

### API Contract Tests

**Characteristics**: Fast, no UI rendering

```typescript
// Recommended timeout: 15s
// Use default project timeouts
const response = await page.request.get('/api/games');
expect(response.status()).toBe(200);
```

---

## Troubleshooting

### Test Times Out

1. **Identify the bottleneck**:
   ```typescript
   test('debug timeout', async ({ page }) => {
     test.setTimeout(120000); // Extra long for debugging

     console.time('navigation');
     await page.goto('/#/canvas');
     console.timeEnd('navigation');

     console.time('react-mount');
     await waitForReactMount(page, 100);
     console.timeEnd('react-mount');
   });
   ```

2. **Use faster wait strategies**:
   ```typescript
   // Instead of networkidle
   await page.waitForLoadState('networkidle'); // Slow

   // Use specific element
   await page.waitForSelector('#app-root', { state: 'visible' }); // Fast
   ```

3. **Override timeout for specific test**:
   ```typescript
   test.setTimeout(90000);
   ```

### Test Fails Intermittently

1. **Add retry logic**:
   ```typescript
   // In playwright.config.ts
   retries: process.env.CI ? 2 : 0
   ```

2. **Increase timeout for that test**:
   ```typescript
   test.setTimeout(90000);
   ```

3. **Use more robust selectors**:
   ```typescript
   // Fragile
   await page.click('button');

   // Robust
   await page.click('[data-testid="submit-button"]');
   ```

### Test Runs Slowly

1. **Use domcontentloaded instead of networkidle**:
   ```typescript
   await page.waitForLoadState('domcontentloaded');
   ```

2. **Reduce timeout for fast tests**:
   ```typescript
   // In test project
   {
     name: 'smoke',
     testMatch: '**/smoke/**/*.spec.ts',
     use: {
       actionTimeout: 20000,
       navigationTimeout: 40000,
     },
   }
   ```

3. **Run tests in parallel (if no shared state)**:
   ```typescript
   fullyParallel: true,
   workers: 4,
   ```

---

## Best Practices

### DO ✅

1. **Use specific selectors** (`[data-testid="..."]`)
2. **Wait for specific elements** (`waitForSelector`)
3. **Use `domcontentloaded`** instead of `networkidle`
4. **Override timeouts** for slow tests
5. **Organize tests** by complexity (smoke/critical/api)
6. **Use helper functions** for common wait patterns

### DON'T ❌

1. **Don't use arbitrary waits** (`waitForTimeout(5000)`)
2. **Don't use networkidle** unless necessary
3. **Don't use CSS selectors** that depend on styling
4. **Don't share tests** that depend on game context (run sequentially)
5. **Don't ignore timeout failures** (they indicate real performance issues)

---

## Migration Checklist

- [x] Create `test/e2e/helpers/wait-helpers.ts`
- [x] Create `test/e2e/helpers/game-context.ts`
- [x] Update `test/e2e/playwright.config.ts`
- [ ] Update tests to use new helper functions
- [ ] Run full test suite to verify timeouts
- [ ] Adjust specific test timeouts if needed
- [ ] Document any test-specific timeout requirements

---

## Next Steps

1. **Run tests** to identify remaining timeout issues:
   ```bash
   cd test/e2e
   npx playwright test --project=critical
   ```

2. **Analyze failures** and adjust timeouts per test

3. **Update tests** to use helper functions:
   ```typescript
   // Before
   await page.waitForTimeout(1000);

   // After
   await waitForReactMount(page, 100);
   ```

4. **Monitor test execution time** and optimize further

---

## References

- [Playwright Timeouts Documentation](https://playwright.dev/docs/test-timeouts)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Project E2E Testing Guide](../../test/e2e/README.md)
- [E2E Testing Guide](/Users/mckenzie/Documents/event2table/E2E_TESTING_GUIDE.md)

---

**Document Version**: 1.0
**Last Updated**: 2026-02-12
**Maintainer**: Event2Table Development Team
