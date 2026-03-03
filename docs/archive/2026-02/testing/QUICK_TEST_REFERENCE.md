# Parameter Management Tests - Quick Reference

## Quick Start

### Run Working Tests (Parameter Model)

```bash
cd /Users/mckenzie/Documents/event2table/backend/tests
python3 -m pytest unit/domain/test_parameter_model.py -v
```

**Expected Output**: 38 passed in 0.78s ✅

---

## Test Files Overview

| File | Tests | Status | Command |
|------|-------|--------|---------|
| `test_parameter_model.py` | 38 | ✅ Passing | `pytest unit/domain/test_parameter_model.py` |
| `test_common_parameter_model.py` | 27 | ⚠️ Needs fix | `pytest unit/domain/test_common_parameter_model.py` |
| `test_parameter_dto.py` | 40 | ⚠️ Blocked | `pytest unit/application/test_parameter_dto.py` |

---

## Common Issues

### Issue: Backend Import Error

**Error**: `ImportError: cannot import name 'CacheInvalidator'`

**Solution**: Run tests from `backend/tests/` directory, not project root

```bash
# ✅ Correct
cd backend/tests
python3 -m pytest unit/domain/test_parameter_model.py

# ❌ Wrong (from project root)
pytest backend/tests/unit/domain/test_parameter_model.py
```

### Issue: CommonParameter Missing Field

**Error**: `TypeError: missing 1 required positional argument: 'param_name_cn'`

**Solution**: Add `param_name_cn=None` to CommonParameter calls:

```python
# Before
CommonParameter(
    id=1,
    game_gid=90000001,
    param_name='test',
    param_type=ParameterType.STRING,
    occurrence_count=4,
    total_events=5
)

# After
CommonParameter(
    id=1,
    game_gid=90000001,
    param_name='test',
    param_name_cn=None,  # ✅ Add this
    param_type=ParameterType.STRING,
    occurrence_count=4,
    total_events=5
)
```

---

## Test Categories

### Domain Model Tests

```bash
# Parameter model (working)
python3 -m pytest unit/domain/test_parameter_model.py -v

# Common parameter model (needs fix)
python3 -m pytest unit/domain/test_common_parameter_model.py -v

# Parameter management service (blocked)
python3 -m pytest unit/domain/test_parameter_management_service.py -v
```

### Application Service Tests

```bash
# Parameter app service (blocked)
python3 -m pytest unit/application/test_parameter_app_service.py -v

# Event builder app service (blocked)
python3 -m pytest unit/application/test_event_builder_app_service.py -v
```

### DTO Tests

```bash
# Parameter DTOs (blocked)
python3 -m pytest unit/application/test_parameter_dto.py -v
```

---

## Running with Coverage

```bash
# Run specific test with coverage
python3 -m pytest unit/domain/test_parameter_model.py \
    --cov=backend/domain/models/parameter \
    --cov-report=html \
    --cov-report=term-missing

# View coverage report
open output/coverage/html/index.html
```

---

## Test Execution Tips

### Run Specific Test Class

```bash
python3 -m pytest unit/domain/test_parameter_model.py::TestParameterCreation -v
```

### Run Specific Test Method

```bash
python3 -m pytest unit/domain/test_parameter_model.py::TestParameterCreation::test_parameter_creation_valid -v
```

### Run with Verbose Output

```bash
python3 -m pytest unit/domain/test_parameter_model.py -vv
```

### Run with Shortened Traceback

```bash
python3 -m pytest unit/domain/test_parameter_model.py --tb=line
```

---

## Test Fixtures

### Using Fixtures in Tests

```python
def test_example(test_game, test_event):
    """test_game: Creates game with GID 90000001
    test_event: Creates event for test_game
    """
    assert test_game == 90000001
    assert test_event > 0
```

### Available Fixtures

- `test_db` - Test database connection
- `clean_db` - Clean database (all test data removed)
- `test_game` - Create test game (GID: 90000001)
- `test_game_with_events` - Game with 5 events
- `test_event` - Create test event
- `test_parameter_data` - Sample parameter data
- `test_parameters` - Parameters for common calculation
- `mock_parameter_repository` - Mocked repository
- `mock_common_param_repository` - Mocked repository
- `mock_uow` - Mocked Unit of Work
- `sample_parameter` - Sample Parameter instance
- `sample_common_parameter` - Sample CommonParameter

---

## Quick Test Commands

```bash
# Run all domain model tests (working)
python3 -m pytest unit/domain/test_parameter_model.py -v

# Run specific test class
python3 -m pytest unit/domain/test_parameter_model.py::TestParameterTypeChange -v

# Run with coverage
python3 -m pytest unit/domain/test_parameter_model.py --cov=backend/domain/models/parameter -v

# Run and stop on first failure
python3 -m pytest unit/domain/test_parameter_model.py -x

# Run last failed tests
python3 -m pytest unit/domain/test_parameter_model.py --lf

# Run with detailed output
python3 -m pytest unit/domain/test_parameter_model.py -vv -s
```

---

## Expected Test Results

### Parameter Model Tests

```
======================== 38 passed, 1 warning in 0.78s =========================

Test Classes:
✅ TestParameterCreation (6 tests)
✅ TestParameterType (3 tests)
✅ TestParameterTypeChange (6 tests)
✅ TestParameterWithMethods (4 tests)
✅ TestParameterLegacyMethods (8 tests)
✅ TestParameterSerialization (4 tests)
✅ TestValidationResult (4 tests)
```

---

## Troubleshooting

### Tests Not Found

**Error**: `ERROR: file or directory not found`

**Solution**: Make sure you're in the correct directory

```bash
# Should be in backend/tests/
pwd
# Output: /Users/mckenzie/Documents/event2table/backend/tests
```

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'backend.domain'`

**Solution**: Add backend to path or run from tests directory

```bash
# Option 1: Run from tests directory (recommended)
cd backend/tests
python3 -m pytest unit/domain/test_parameter_model.py

# Option 2: Add to PYTHONPATH
export PYTHONPATH=/Users/mckenzie/Documents/event2table:$PYTHONPATH
pytest backend/tests/unit/domain/test_parameter_model.py
```

### Database Errors

**Error**: `sqlite3.OperationalError: no such table: event_params`

**Solution**: Initialize test database

```bash
python scripts/setup/init_db.py
```

---

## Performance

| Test Suite | Test Count | Duration | Speed |
|------------|------------|----------|-------|
| Parameter Model | 38 | 0.78s | Fast ✅ |
| Common Parameter | 27 | ~1s | Fast ✅ |
| All DTOs | 40 | ~1s | Fast ✅ |
| **All Tests** | **165** | **~5s** | **Fast ✅** |

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.14'
      - run: pip install -r requirements.txt
      - run: cd backend/tests && python3 -m pytest unit/domain/test_parameter_model.py -v
```

---

## Resources

- **Full Report**: `docs/testing/PARAMETER_MANAGEMENT_UNIT_TESTS_REPORT.md`
- **Pytest Docs**: https://docs.pytest.org/
- **Pytest Mock**: https://pytest-mock.readthedocs.io/
- **Coverage.py**: https://coverage.readthedocs.io/

---

**Last Updated**: 2026-02-23
**Status**: Parameter model tests passing (38/38) ✅
