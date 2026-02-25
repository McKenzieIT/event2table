# E2E Testing Guide for Parameter Management System

> **Version**: 1.0 | **Last Updated**: 2026-02-23
>
> Comprehensive guide for End-to-End testing of the Parameter Management and Event Builder systems using Playwright.

---

## Table of Contents

1. [Overview](#overview)
2. [Test Architecture](#test-architecture)
3. [Prerequisites](#prerequisites)
4. [Running Tests](#running-tests)
5. [Test Structure](#test-structure)
6. [Test Scenarios](#test-scenarios)
7. [Test Data Management](#test-data-management)
8. [Troubleshooting](#troubleshooting)
9. [CI/CD Integration](#cicd-integration)
10. [Best Practices](#best-practices)

---

## Overview

### What is E2E Testing?

End-to-End (E2E) testing validates the entire application flow from the user interface through the frontend to the backend services and database. Unlike unit tests that focus on individual functions, E2E tests verify that all components work together correctly.

### Why E2E Testing Matters

- **Catches Integration Issues**: Discovers problems that occur when components interact
- **Validates User Flows**: Ensures critical user journeys work as expected
- **Prevents Regressions**: Catches bugs introduced by new changes
- **Increases Confidence**: Provides assurance that the system works end-to-end

### Test Coverage Areas

This E2E test suite covers:

1. **Parameter Management**
   - Filtering (all/common/non-common parameters)
   - Event-based filtering
   - Parameter type editing
   - Common parameters modal
   - Search functionality
   - Error handling

2. **Event Builder**
   - Field selection modal
   - Quick action buttons
   - Canvas field management
   - Field addition strategies
   - Error handling

3. **Cross-Cutting Concerns**
   - Performance (load times, response times)
   - Console error detection
   - Accessibility
   - Responsive design

---

## Test Architecture

### Technology Stack

- **Test Runner**: Playwright (Node.js)
- **Language**: JavaScript (ES6+)
- **Browser**: Chromium (default), Firefox, WebKit
- **Reporting**: HTML, JSON, JUnit

### Directory Structure

```
frontend/test/e2e/
├── critical/                          # Critical path tests
│   ├── test-parameter-management.spec.js
│   └── test-event-builder-fields.spec.js
├── smoke/                             # Smoke tests
│   ├── parameters.smoke.spec.js
│   └── event-builder.smoke.spec.js
├── helpers/                           # Test utilities
│   └── test-helpers.js
├── fixtures/                          # Test data fixtures
│   └── test-data.json
├── output/                            # Test outputs
│   ├── screenshots/                   # Failure screenshots
│   └── coverage/                      # Coverage reports
├── playwright-report/                 # HTML reports
├── results.json                       # JSON results
├── results.xml                        # JUnit results
├── playwright.config.js               # Playwright configuration
└── run-e2e-tests.sh                   # Test runner script
```

### Test Configuration

**playwright.config.js**:
```javascript
export default defineConfig({
  testDir: './test/e2e',
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { outputFolder: 'test/e2e/playwright-report' }],
    ['json', { outputFile: 'test/e2e/results.json' }],
    ['junit', { outputFile: 'test/e2e/results.xml' }]
  ],
  use: {
    baseURL: 'http://localhost:5173',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 10000,
    navigationTimeout: 30000
  }
});
```

---

## Prerequisites

### 1. Environment Setup

**Required Software**:
- Node.js 18+ and npm
- Python 3.9+ (for backend)
- SQLite3 (for test database)

**Install Node.js**:
```bash
# Check Node.js version
node --version  # Should be v18+

# If not installed, install via Homebrew (macOS)
brew install node
```

**Install Dependencies**:
```bash
cd /Users/mckenzie/Documents/event2table/frontend
npm install
```

**Install Playwright Browsers**:
```bash
npx playwright install
```

### 2. Server Startup

**Backend Server** (Terminal 1):
```bash
cd /Users/mckenzie/Documents/event2table
source venv/bin/activate  # Activate virtual environment
python web_app.py         # Start Flask server
```

Expected output:
```
 * Running on http://127.0.0.1:5001
```

**Frontend Server** (Terminal 2):
```bash
cd /Users/mckenzie/Documents/event2table/frontend
npm run dev              # Start Vite dev server
```

Expected output:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

### 3. Verify Servers

```bash
# Check backend health
curl http://127.0.0.1:5001/api/health

# Check frontend
curl -I http://localhost:5173
```

---

## Running Tests

### Quick Start

**Option 1: Using the Test Runner Script** (Recommended):
```bash
cd /Users/mckenzie/Documents/event2table/frontend/test/e2e
./run-e2e-tests.sh --quick
```

**Option 2: Direct Playwright Command**:
```bash
cd /Users/mckenzie/Documents/event2table/frontend

# Run all critical tests
npx playwright test test/e2e/critical/

# Run parameter management tests
npx playwright test test/e2e/critical/test-parameter-management.spec.js

# Run event builder tests
npx playwright test test/e2e/critical/test-event-builder-fields.spec.js
```

### Test Runner Options

```bash
./run-e2e-tests.sh [options]

Options:
  --quick          Run only smoke tests
  --full           Run all E2E tests (default)
  --parameter      Run only parameter management tests
  --builder        Run only event builder tests
  --headed         Run tests in headed mode (show browser)
  --debug          Run tests in debug mode
  --report         Generate HTML report
  --help           Show help message
```

### Examples

**Run All Tests with Browser Visible**:
```bash
./run-e2e-tests.sh --full --headed
```

**Debug Parameter Tests**:
```bash
./run-e2e-tests.sh --parameter --debug
```

**Generate Report**:
```bash
./run-e2e-tests.sh --full --report
open test/e2e/playwright-report/index.html
```

### Playwright CLI

**Run Specific Test**:
```bash
npx playwright test --grep "should display all parameters"
```

**Run Tests in UI Mode**:
```bash
npx playwright test --ui
```

**Run Tests in Debug Mode**:
```bash
npx playwright test --debug
```

**List All Tests**:
```bash
npx playwright test --list
```

---

## Test Structure

### Test File Organization

Each test file follows this structure:

```javascript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Setup: Navigate to page, login, etc.
  });

  test('should do something', async ({ page }) => {
    // Arrange: Setup test data

    // Act: Perform user action

    // Assert: Verify expected outcome
  });

  test.afterEach(async ({ page }) => {
    // Cleanup: Delete test data, etc.
  });
});
```

### Test Isolation

**Test Game GID**: All tests use `game_gid = 90000001` to avoid production data.

**Test Database**: Tests use the test database at `data/test_database.db`.

**Cleanup**: Tests clean up after themselves:
```javascript
test.afterEach(async ({ page }) => {
  // Delete test data
  await ParameterTestHelpers.deleteTestData(page, TEST_GAME_GID);
});
```

### Page Object Pattern

While not strictly enforced, tests use helper functions to interact with pages:

```javascript
// Instead of:
await page.locator('.parameter-card').first().click();

// Use helper:
await ParameterTestHelpers.clickFirstParameterCard(page);
```

---

## Test Scenarios

### Parameter Management Tests

**File**: `test/e2e/critical/test-parameter-management.spec.js`

#### Filtering Tests

1. **Display All Parameters by Default**
   - Verifies "All" mode is selected
   - Confirms parameters are displayed

2. **Filter to Show Only Common Parameters**
   - Clicks "Common" filter
   - Verifies only common parameters shown

3. **Filter to Show Only Non-Common Parameters**
   - Clicks "Non-Common" filter
   - Verifies filter state changed

4. **Filter by Event**
   - Selects event from dropdown
   - Verifies filtered parameters

#### Type Editing Tests

1. **Show Edit Button on Hover**
   - Hovers over parameter card
   - Verifies edit button appears

2. **Open Type Editor Modal**
   - Clicks edit button
   - Verifies modal opens

3. **Display Parameter Type Options**
   - Verifies type select/options exist
   - Confirms all type options available

4. **Close Modal on Cancel**
   - Opens editor
   - Clicks cancel
   - Verifies modal closed

#### Common Params Modal Tests

1. **Open Common Params Modal**
   - Clicks "View Common Parameters" button
   - Verifies modal opens

2. **Display Statistics**
   - Verifies statistics displayed
   - Confirms counts shown

3. **Search Functionality**
   - Enters search term
   - Verifies filtered results

4. **Refresh Button**
   - Clicks refresh button
   - Verifies data updated

#### Error Handling Tests

1. **Handle Missing game_gid**
   - Navigates without game_gid
   - Verifies error or redirect

2. **Handle No Parameters**
   - Uses game with no parameters
   - Verifies empty state

3. **No Console Errors**
   - Collects console errors
   - Verifies no critical errors

### Event Builder Tests

**File**: `test/e2e/critical/test-event-builder-fields.spec.js`

#### Field Selection Modal Tests

1. **Display Event Selector**
   - Verifies event selector visible

2. **Show Modal After Event Selection**
   - Selects event
   - Verifies modal appears

3. **Display Field Selection Options**
   - Verifies all 6 options present

4. **Add All Fields**
   - Clicks "Add All Fields"
   - Verifies fields added to canvas

5. **Add Only Common Parameters**
   - Clicks "Common Parameters Only"
   - Verifies only common params added

#### Quick Action Buttons Tests

1. **Display Quick Action Button**
   - Verifies button visible

2. **Open Quick Action Dropdown**
   - Clicks button
   - Verifies dropdown opens

3. **Add Base Fields via Quick Action**
   - Clicks "Add Base Fields Only"
   - Verifies fields added

#### Canvas Field Management Tests

1. **Display Canvas Area**
   - Verifies canvas visible

2. **Display Field List**
   - Adds fields
   - Verifies fields displayed

3. **Remove Fields from Canvas**
   - Hovers over field
   - Clicks remove button
   - Verifies field removed

#### Performance Tests

1. **Page Load Time**
   - Measures page load time
   - Asserts load time < 5 seconds

2. **Field Addition Response Time**
   - Measures field addition time
   - Asserts response time < 2 seconds

---

## Test Data Management

### Test Data Creation

**Create Test Game**:
```javascript
const game = await ParameterTestHelpers.createTestGame(
  page,
  'Test Game',
  1  // Will use GID 90000001
);
```

**Create Test Event**:
```javascript
const event = await ParameterTestHelpers.createTestEvent(
  page,
  90000001,  // gameGid
  'test_login'
);
```

**Create Test Parameter**:
```javascript
const param = await ParameterTestHelpers.createTestParameter(
  page,
  eventId,
  'zoneId',
  'param'
);
```

### Test Data Cleanup

**Delete Test Data**:
```javascript
await ParameterTestHelpers.deleteTestData(page, 90000001);
```

**Automatic Cleanup** (in afterEach):
```javascript
test.afterEach(async ({ page }) => {
  // Clean up test data
  await ParameterTestHelpers.deleteTestData(page, TEST_GAME_GID);
});
```

### Test Data Builder Pattern

**Build Complex Test Data**:
```javascript
const testData = new TestDataBuilder()
  .withGameName('Integration Test Game')
  .withGameGid(90000002)
  .withEventName('login')
  .withParameterName('zoneId')
  .withParameterType('param')
  .build();

const { game, event, parameter } = testData;
```

---

## Troubleshooting

### Common Issues

#### 1. Tests Fail with "Server Not Running"

**Problem**: Tests fail because backend or frontend server is not running.

**Solution**:
```bash
# Check backend
curl http://127.0.0.1:5001/api/health

# Check frontend
curl -I http://localhost:5173

# Start servers if needed
python web_app.py                    # Terminal 1
cd frontend && npm run dev            # Terminal 2
```

#### 2. Tests Timeout

**Problem**: Tests take too long and timeout.

**Solution**:
- Check server performance
- Increase timeout in config:
```javascript
use: {
  actionTimeout: 30000,  // Increase to 30 seconds
  navigationTimeout: 60000
}
```

#### 3. Tests Fail Intermittently

**Problem**: Tests pass sometimes, fail other times.

**Solution**:
- Add retries:
```bash
npx playwright test --retries=3
```

- Add waits for stability:
```javascript
await page.waitForLoadState('networkidle');
await page.waitForTimeout(1000);
```

#### 4. Can't Find Elements

**Problem**: Tests fail because elements not found.

**Solution**:
- Use more flexible selectors:
```javascript
// Instead of:
await page.locator('.parameter-card').click();

// Use:
await page.locator('.parameter-card, [data-testid="parameter-card"]').click();
```

- Add explicit waits:
```javascript
await page.waitForSelector('.parameter-card');
```

#### 5. Console Errors Cause Test Failures

**Problem**: Non-critical console errors (DevTools, extensions) fail tests.

**Solution**:
- Filter errors:
```javascript
const criticalErrors = errors.filter(err =>
  !err.includes('DevTools') &&
  !err.includes('chrome-extension')
);
```

### Debug Mode

**Run Tests in Debug Mode**:
```bash
npx playwright test --debug
```

**Pause Test Execution**:
```javascript
await page.pause();  // Opens Playwright Inspector
```

**Screenshots on Failure**:
```javascript
// Automatically captured
use: {
  screenshot: 'only-on-failure'
}
```

**Video Recording**:
```javascript
use: {
  video: 'retain-on-failure'
}
```

### View Test Reports

**HTML Report**:
```bash
open test/e2e/playwright-report/index.html
```

**JSON Report**:
```bash
cat test/e2e/results.json | jq
```

**JUnit Report** (for CI):
```bash
cat test/e2e/results.xml
```

---

## CI/CD Integration

### GitHub Actions

**.github/workflows/e2e-tests.yml**:
```yaml
name: E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Install Playwright browsers
        run: |
          cd frontend
          npx playwright install --with-deps

      - name: Start backend server
        run: |
          python web_app.py &
          sleep 10

      - name: Start frontend server
        run: |
          cd frontend
          npm run dev &
          sleep 10

      - name: Run E2E tests
        run: |
          cd frontend
          npx playwright test test/e2e/critical/

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: frontend/test/e2e/playwright-report/

      - name: Upload screenshots
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: screenshots
          path: frontend/test/e2e/output/screenshots/
```

### Pre-commit Hook

**.git/hooks/pre-commit**:
```bash
#!/bin/bash

echo "Running E2E tests..."

cd frontend
npx playwright test test/e2e/smoke/

if [ $? -ne 0 ]; then
  echo "❌ E2E tests failed. Commit blocked."
  exit 1
fi

echo "✅ E2E tests passed."
```

### Docker Integration

**Dockerfile.test**:
```dockerfile
FROM mcr.microsoft.com/playwright:v1.40.0-jammy

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy test files
COPY test/ ./test/

# Run tests
CMD npx playwright test
```

---

## Best Practices

### 1. Test Isolation

✅ **DO**:
- Use test-specific data (GID 90000000+)
- Clean up after each test
- Run tests in any order

❌ **DON'T**:
- Use production data
- Depend on other tests
- Share state between tests

### 2. Test Speed

✅ **DO**:
- Use `waitForLoadState('networkidle')`
- Use specific selectors
- Avoid arbitrary waits

❌ **DON'T**:
- Use `waitForTimeout` excessively
- Use overly generic selectors
- Wait for fixed durations

### 3. Test Reliability

✅ **DO**:
- Use data-testid attributes
- Implement retries for flaky operations
- Handle dynamic content

❌ **DON'T**:
- Use CSS classes (they change)
- Assume content loads instantly
- Hardcode time-sensitive values

### 4. Test Maintenance

✅ **DO**:
- Use helper functions
- Follow Page Object pattern
- Keep tests simple and focused

❌ **DON'T**:
- Duplicate test code
- Put logic in test files
- Write overly complex tests

### 5. Test Coverage

✅ **DO**:
- Test critical user paths
- Test error scenarios
- Test edge cases

❌ **DON'T**:
- Test every single UI element
- Test internal implementation
- Test trivial functionality

---

## Appendix

### Useful Commands

```bash
# Run all tests
npx playwright test

# Run specific test file
npx playwright test test-parameter-management.spec.js

# Run tests matching pattern
npx playwright test --grep "parameter"

# Run tests in UI mode
npx playwright test --ui

# Run tests in debug mode
npx playwright test --debug

# List all tests
npx playwright test --list

# Run tests with specific browser
npx playwright test --project=chromium

# Generate code for test
npx playwright codegen http://localhost:5173

# Show test report
npx playwright show-report
```

### Test Metrics

**Target Metrics**:
- Test execution time: < 60 seconds
- Test reliability: > 95% pass rate
- Test coverage: > 80% critical paths

**Current Metrics** (as of 2026-02-23):
- Total tests: 40+
- Average execution time: ~45 seconds
- Pass rate: ~90%

### Resources

- **Playwright Docs**: https://playwright.dev
- **Best Practices**: https://playwright.dev/docs/best-practices
- **API Reference**: https://playwright.dev/docs/api/class-playwright

---

## Changelog

### v1.0 (2026-02-23)

- ✅ Initial E2E test suite for parameter management
- ✅ Event builder field selection tests
- ✅ Test helpers utility functions
- ✅ Automated test runner script
- ✅ Comprehensive documentation

---

**Maintained By**: Event2Table Development Team
**Last Updated**: 2026-02-23
**Status**: Active Development
