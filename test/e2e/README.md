# Unified E2E Test Suite

Consolidated end-to-end testing for Event2Table application.

## Directory Structure

```
test/e2e/
├── critical/         # Critical user journey tests (P0 priority)
│   ├── game-management.spec.ts      # Game CRUD operations
│   ├── event-management.spec.ts     # Event CRUD operations
│   ├── hql-generation.spec.ts      # HQL generation workflow
│   └── canvas-workflow.spec.ts     # Canvas and flow builder
├── smoke/           # Quick smoke tests
│   ├── quick-smoke.spec.ts          # Fast smoke tests
│   ├── smoke-tests.spec.ts          # Comprehensive smoke tests
│   └── screenshots.spec.ts         # Visual regression tests
├── api-contract/    # API contract validation
│   ├── contract-validation.spec.ts  # API contract tests
│   └── api-contract-tests.spec.ts  # API integration tests
└── playwright.config.ts             # Playwright configuration
```

## Running Tests

### Run All Tests
```bash
cd test/e2e
npx playwright test
```

### Run Specific Test Suites

```bash
# Critical user journeys only
npx playwright test --project=critical

# Smoke tests only
npx playwright test --project=smoke

# API contract tests only
npx playwright test --project=api-contract
```

### Run Specific Test Files

```bash
# Game management tests
npx playwright test critical/game-management.spec.ts

# Event management tests
npx playwright test critical/event-management.spec.ts

# Canvas workflow tests
npx playwright test critical/canvas-workflow.spec.ts
```

### Run Tests in UI Mode

```bash
npx playwright test --ui
```

### Run Tests in Debug Mode

```bash
npx playwright test --debug
```

## Test Categories

### Critical Tests (P0 Priority)

These tests cover the most critical user workflows that must work correctly:

- **Game Management**: Create, read, update, delete games
- **Event Management**: Create, read, update, delete events
- **HQL Generation**: Generate HQL for events and parameters
- **Canvas Workflow**: Visual flow builder functionality

**When to run**: Before every release, after any database schema changes, after any major refactoring.

### Smoke Tests

Quick tests to verify basic functionality and catch obvious regressions:

- **Page Loading**: All major pages load without errors
- **Navigation**: Routing and navigation work correctly
- **API Connectivity**: Backend API is accessible
- **Basic Operations**: Basic CRUD operations work

**When to run**: After every code change, before committing, in CI pipeline.

### API Contract Tests

Tests that validate API contracts between frontend and backend:

- **Endpoint Availability**: All API endpoints exist
- **Request/Response Format**: Correct JSON structure
- **Error Handling**: Proper HTTP status codes
- **Data Validation**: Input validation and sanitization

**When to run**: After any API changes, after any model changes, in CI pipeline.

## Test Data

Tests use the following test data:

- **Game GID**: 10000147 (default test game)
- **Database**: SQLite test database (`data/test_database.db`)
- **Test Games**: Created with random GIDs in 90000000+ range to avoid conflicts

## Prerequisites

Before running E2E tests:

1. **Backend server running**: `python web_app.py` (port 5001)
2. **Frontend server running**: `cd frontend && npm run dev` (port 5173) OR
3. **Use production backend**: Tests can run against backend at `http://127.0.0.1:5001`

## Troubleshooting

### Tests Fail with "Game context required"

Ensure the backend server is running and the test database is initialized:
```bash
python scripts/setup/init_db.py
python web_app.py
```

### Tests Fail with "Connection Refused"

Ensure the correct server is running:
```bash
# Backend
python web_app.py

# Frontend (optional, tests use backend directly)
cd frontend && npm run dev
```

### Tests Timeout

Increase timeouts in `playwright.config.ts`:
```typescript
use: {
  actionTimeout: 30000,  // Increase from 15000
  navigationTimeout: 60000,  // Increase from 30000
}
```

## Legacy Tests

The original test files remain in their original locations:
- Legacy E2E tests: `test/e2e/*.spec.ts` (root level)
- Frontend E2E tests: `frontend/tests/e2e/*.spec.ts`

These are deprecated and will be migrated gradually. New tests should use the unified structure.

## Test Coverage Metrics

Current test coverage:
- **Critical Tests**: 4 test files covering main workflows
- **Smoke Tests**: 3 test files covering basic functionality
- **API Contract Tests**: 2 test files covering API contracts

Total: **9 consolidated test files** (up from scattered tests across 2 directories)

## Next Steps

1. ✅ Create unified directory structure
2. ✅ Copy existing tests to appropriate categories
3. ✅ Update Playwright configuration
4. ⏳ Add more critical workflow tests
5. ⏳ Migrate remaining legacy tests
6. ⏳ Set up CI/CD integration

## Contributing

When adding new E2E tests:

1. Determine the appropriate category (critical/smoke/api-contract)
2. Name the test file descriptively: `feature-name.spec.ts`
3. Follow existing test patterns and naming conventions
4. Use `data-testid` attributes for reliable element selection
5. Clean up test data in `afterEach` hooks
6. Update this README if adding new test categories
