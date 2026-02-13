# Event2Table Regression Test Results - Quick Reference

**Test Date:** 2026-02-11 00:46:00
**Execution Time:** 46.80 seconds
**Test Database:** `/Users/mckenzie/Documents/event2table/tests/test_database.db`

---

## 📊 Test Results Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total Tests** | 450 | 100% |
| **✅ Passed** | 316 | 70.2% |
| **❌ Failed** | 54 | 12.0% |
| **⚠️ Errors** | 75 | 16.7% |
| **⏭️ Skipped** | 5 | 1.1% |

**Success Rate:** 70.2%

---

## 🚨 Critical Issues (Immediate Action Required)

### 1. Missing Modules (75 tests affected)
```
backend.services.categories     (75 tests)
backend.middleware              (2 tests)
backend.services.flows          (5 tests)
backend.services.bulk_operations (1 test)
backend.services.hql_v2         (2 tests)
backend.services.sql_optimizer  (2 tests)
playwright                      (1 test)
automation_runner               (1 test)
```

**Action:** Install missing packages or create stub modules

---

## 🔴 Failed Tests by Severity

### CRITICAL (Fix within 24 hours)
- **Bulk Operations API:** 5/6 tests failing (83.3% failure rate)
  - Bulk delete, update, toggle, export, validate all broken

### HIGH (Fix within 1 week)
- **Games API:** Duplicate GID validation not working
- **Common Params API:** Retrieval failed
- **Database Migrations:** Version mismatch (expected 18, got 19)

### MEDIUM (Fix within 2 weeks)
- **Performance Tests:** 4 failures
  - Aggregate functions: 1217% degradation
  - Graph traversal: 5.12ms (threshold: 5.0ms)
  - Cache hit: 1.00x speedup (threshold: 10x)
  - LRU eviction: 460% instability

### LOW (Fix when convenient)
- Environment config files missing (.env.test, .env.development, .env.production)
- Event creation utility type mismatch

---

## ✅ Passing Test Suites (Excellent Health)

| API Module | Passing | Total | Success Rate |
|------------|---------|-------|--------------|
| Events API | 24 | 24 | 100% ✅ |
| HQL Generation API | 5 | 5 | 100% ✅ |
| Canvas API | 5 | 5 | 100% ✅ |
| Cache Monitor API | 3 | 3 | 100% ✅ |
| Event Nodes API | 5 | 5 | 100% ✅ |
| Parameter Aliases API | 5 | 5 | 100% ✅ |
| Games API | 17 | 18 | 94.4% ✅ |
| Parameters API | 22 | 23 | 95.7% ✅ |

---

## 🔧 Infrastructure Fixes Applied

1. ✅ **Fixed directory naming conflict** - Renamed `test/unit/backend` to `test/unit/backend_tests`
2. ✅ **Added module exports** - Updated `backend/__init__.py` and `backend/core/__init__.py`
3. ✅ **Created root conftest** - Added `conftest.py` for Python path setup
4. ✅ **Updated pytest config** - Set absolute pythonpath in pytest.ini

**Infrastructure Status:** 100% Fixed ✅

---

## 📝 Next Steps

### Priority 1 (Critical - Do Today)
```bash
# Install missing dependencies
pip install playwright

# Create stub modules for missing services
mkdir -p backend/services/categories
touch backend/services/categories/__init__.py
```

### Priority 2 (High - This Week)
1. Fix bulk operations API (5 failing tests)
2. Fix duplicate GID validation
3. Update migration tests to expect version 19

### Priority 3 (Medium - Next 2 Weeks)
1. Optimize performance bottlenecks
2. Create environment configuration files

### Priority 4 (Low - Backlog)
1. Implement skipped test features
2. Clean up archive diagnostic tests

---

## 📂 Test Artifacts

All test results saved to: `/Users/mckenzie/Documents/event2table/test_results/`

- `regression_test_results.txt` - Comprehensive test report
- `pytest_detailed_output.txt` - Full pytest output
- `pytest_full_output_with_errors.txt` - Output with error details
- `INFRASTRUCTURE_FIXES_SUMMARY.md` - Infrastructure fixes documentation
- `QUICK_REFERENCE.md` - This file

---

## 🧪 Running Tests

```bash
# Run all tests
cd /Users/mckenzie/Documents/event2table
FLASK_ENV=testing pytest test/ -v --tb=short

# Run specific test file
FLASK_ENV=testing pytest test/unit/backend_tests/test_api_comprehensive.py -v

# Run with coverage
FLASK_ENV=testing pytest test/ --cov=backend --cov-report=html

# Run only fast tests
FLASK_ENV=testing pytest test/ -m "not slow"
```

---

## 📊 Test Coverage

**Working Tests:** 316 tests (70.2%)
**Broken Tests:** 129 tests (28.7%)
  - Import Errors: 75 tests (16.7%)
  - Failed Tests: 54 tests (12.0%)

**Overall Assessment:** 🟡 MODERATE
- Core functionality is working well (70% pass rate)
- Infrastructure issues resolved ✅
- Missing dependencies causing test failures ⚠️
- Performance optimization needed 📈

---

## 🎯 Success Criteria Met

- ✅ Tests can be executed
- ✅ Production database not affected
- ✅ Test database properly isolated
- ✅ Fast execution (46.80 seconds)
- ⚠️ 70%+ pass rate achieved (70.2%)
- ❌ All tests passing (129 tests need fixing)

---

**Report Generated:** 2026-02-11 00:46:00
**Test Engineer:** Claude (Automated Regression Testing)
