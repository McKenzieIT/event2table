# Test Running Quick Reference

**Last Updated**: 2026-02-13
**Purpose**: Quick guide to running tests in the new directory structure

---

## Test Directory Structure

```
test/
├── e2e/              # End-to-end tests (Playwright)
├── unit/             # Unit tests (pytest)
├── integration/      # Integration tests (pytest)
├── performance/      # Performance tests (Playwright)
├── helpers/          # Test helper scripts
└── fixtures/         # Test fixtures

frontend/tests/
├── unit/            # Frontend unit tests
├── integration/     # Frontend integration tests
└── e2e/            # (Removed - moved to test/e2e/)
```

---

## Running Tests

### Python Tests (pytest)

#### Run All Unit Tests
```bash
cd /Users/mckenzie/Documents/event2table
pytest test/unit/ -v
```

#### Run Specific Test Category
```bash
# API tests
pytest test/unit/backend/api/ -v

# Core tests
pytest test/unit/backend/core/ -v

# Service tests
pytest test/unit/backend/services/ -v
```

#### Run Integration Tests
```bash
pytest test/integration/ -v
```

#### Run Specific Test File
```bash
pytest test/unit/backend/api/test_games_api.py -v
```

#### Run Specific Test
```bash
pytest test/unit/backend/api/test_games_api.py::test_get_games -v
```

### E2E Tests (Playwright)

#### Run All E2E Tests
```bash
cd frontend
npm run test:e2e
```

#### Run Specific Category
```bash
# Critical tests
npx playwright test test/e2e/critical/

# Smoke tests
npx playwright test test/e2e/smoke/

# HQL-V2 tests
npx playwright test test/e2e/hql-v2/

# API contract tests
npx playwright test test/e2e/api-contract/
```

#### Run With UI Mode
```bash
npx playwright test test/e2e/ --ui
```

#### Run Debug Mode
```bash
npx playwright test test/e2e/ --debug
```

### Performance Tests

```bash
cd frontend
npm run test:performance
```

---

## Test Organization by Purpose

### Critical Tests (test/e2e/critical/)
- Essential user workflows
- Core functionality
- Must pass before merging PR

**Files**: 5
- canvas-workflow.spec.ts
- event-management.spec.ts
- events-workflow.spec.ts
- game-management.spec.ts
- hql-generation.spec.ts

### Smoke Tests (test/e2e/smoke/)
- Quick sanity checks
- Basic functionality verification
- Run after every deployment

**Files**: 3
- quick-smoke.spec.ts
- screenshots.spec.ts
- smoke-tests.spec.ts

### HQL-V2 Tests (test/e2e/hql-v2/)
- HQL V2 generator tests
- Incremental generation
- Multi-event support

**Files**: 5
- hql-preview-v2.spec.ts
- hql-preview.spec.ts
- hql-v2-self-healing.spec.ts
- multi-events.spec.ts
- v2-demo.spec.ts

### API Contract Tests (test/e2e/api-contract/)
- API contract validation
- Frontend-backend API consistency
- API documentation verification

**Files**: 3
- api-contract-tests.spec.ts
- contract-validation.spec.ts
- frontend-api-integration.spec.ts

---

## Unit Tests Organization

### Backend API Tests (test/unit/backend/api/)
- API endpoint tests
- Request/response validation
- Error handling

**Files**: 7

### Backend Core Tests (test/unit/backend/core/)
- Cache system tests
- Database operations
- Security utilities
- Core utilities

**Files**: 23
- cache/ (7 files)
- database/ (2 files)
- security/ (3 files)
- root (11 files)

### Backend Service Tests (test/unit/backend/services/)
- Business logic tests
- Service layer tests
- Canvas, events, HQL, parameters

**Files**: 14

---

## Common Commands

### Run Tests With Coverage

```bash
# Python tests with coverage
pytest test/unit/ --cov=backend --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Run Tests in Parallel

```bash
# Python tests (pytest-xdist)
pytest test/unit/ -n auto

# Playwright tests (default)
npx playwright test --workers=4
```

### Run Failed Tests Only

```bash
# Python tests
pytest test/unit/ --lf

# Playwright tests
npx playwright test --last-failed
```

### View Test Results

```bash
# Python test results
cat test-results/pytest-results.txt

# Playwright HTML report
npx playwright show-report
```

---

## Troubleshooting

### "Module not found" Error

```bash
# Ensure you're in the project root
cd /Users/mckenzie/Documents/event2table

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### "Playwright command not found" Error

```bash
cd frontend
npm install
npx playwright install
```

### Test Database Issues

```bash
# Reinitialize test database
rm -f data/test_database.db*
python scripts/setup/init_db.py

# Or run with FLASK_ENV=testing
FLASK_ENV=testing pytest test/unit/
```

### Port Already in Use

```bash
# Kill process on port 5001
lsof -ti:5001 | xargs kill -9

# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run unit tests
        run: |
          pip install -r requirements.txt
          pytest test/unit/ -v

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: |
          cd frontend
          npm install
          npx playwright install
      - name: Run E2E tests
        run: |
          cd frontend
          npm run test:e2e
```

---

## Quick Reference Card

| Test Type | Command | Location |
|-----------|---------|----------|
| All Unit Tests | `pytest test/unit/ -v` | test/unit/ |
| API Tests | `pytest test/unit/backend/api/ -v` | test/unit/backend/api/ |
| Core Tests | `pytest test/unit/backend/core/ -v` | test/unit/backend/core/ |
| Service Tests | `pytest test/unit/backend/services/ -v` | test/unit/backend/services/ |
| Integration Tests | `pytest test/integration/ -v` | test/integration/ |
| E2E Tests | `cd frontend && npm run test:e2e` | test/e2e/ |
| Critical Tests | `npx playwright test test/e2e/critical/` | test/e2e/critical/ |
| Smoke Tests | `npx playwright test test/e2e/smoke/` | test/e2e/smoke/ |
| HQL-V2 Tests | `npx playwright test test/e2e/hql-v2/` | test/e2e/hql-v2/ |
| Performance Tests | `cd frontend && npm run test:performance` | test/performance/ |

---

## Related Documentation

- [Full Migration Report](./reports/test-migration-report-2026-02-13.md)
- [E2E Testing Guide](./e2e-testing-guide.md)
- [Architecture Documentation](../development/architecture.md)
- [CLAUDE.md](../../CLAUDE.md)

---

**Version**: 1.0
**Last Updated**: 2026-02-13
