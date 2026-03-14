# Test Triage Report - 2026-03-10

## Quick Reference

| Priority | Count | Status |
|----------|-------|--------|
| **P0 - Critical** | 232 | 🔴 Immediate action required |
| **P1 - High** | 42 | 🟠 Fix within 48 hours |
| **P2 - Medium** | 28 | 🟡 Fix within 1 week |
| **P3 - Low** | 18 | 🟢 Fix within 2 weeks |

---

## P0 - Critical Issues

### 1. HQL Template Repository (22 errors)
**File**: `backend/test/unit/repositories/test_hql_template_repository.py`
**Impact**: All HQL template operations broken
**Error Type**: ImportError/AttributeError
**Symptoms**:
```
ERROR backend/test/unit/repositories/test_hql_template_repository.py::TestHQLTemplateRepository
```

**Likely Root Causes**:
- HQLTemplateRepository class missing or moved
- Database table missing (hql_templates)
- Import path incorrect

**Investigation Steps**:
1. Check if `backend/models/repositories/hql_template_repository.py` exists
2. Verify `hql_templates` table exists in database
3. Check import statements in test file

**Quick Fix**:
```bash
# Check if repository exists
find backend -name "*hql_template*"

# Check database schema
sqlite3 data/dwd_generator.db ".schema hql_templates"
```

---

### 2. XSS Protection Tests (5 errors)
**File**: `backend/test/unit/security/test_xss_protection.py`
**Impact**: Security validation not working
**Error Type**: Test execution errors

**Affected Tests**:
- `test_event_name_stores_xss_payload_directly_RED`
- `test_parameter_name_stores_xss_payload_directly_RED`
- `test_html_escape_functionality`
- `test_multiple_xss_payloads_in_event_name`
- `test_xss_payload_variations`

**Investigation Steps**:
1. Check if XSS sanitization functions exist
2. Verify test data setup
3. Check for missing imports

---

### 3. HQL Preview V2 API (31 failures)
**File**: `backend/test/unit/services/hql/test_hql_preview_v2_api.py`
**Impact**: HQL generation and preview broken

**Affected Test Classes**:
- `TestHQLPreviewV2APIBasic` (8 failures)
- `TestHQLPreviewV2APIDebug` (7 failures)
- `TestHQLPreviewV2APIValidate` (8 failures)
- `TestHQLPreviewV2APIIncremental` (8 failures)

**Common Failure Pattern**:
```python
AssertionError: Expected 200 status code, got 500
Expected HQL generation to succeed, but got server error
```

**Investigation Steps**:
1. Check backend logs for HQL generation errors
2. Verify HQL builder service is initialized
3. Check for missing dependencies in HQL V2 module

---

### 4. Batch Category Deletion (6 errors)
**File**: `backend/test/integration/test_category_batch_delete.py`
**Impact**: Batch deletion operations failing

**Affected Tests**:
- `test_batch_delete_success`
- `test_batch_delete_with_events`
- `test_batch_delete_mixed`
- `test_api_batch_delete`
- `test_api_batch_delete_with_events`

**Investigation Steps**:
1. Check if batch delete endpoint exists
2. Verify category service has batch_delete method
3. Check for database constraint violations

---

### 5. Pagination Tests (12 errors)
**File**: `backend/test/integration/api/test_pagination.py`
**Impact**: All pagination functionality broken

**Error Pattern**: All tests in `TestEventsPagination` class failing

**Investigation Steps**:
1. Check if pagination logic was refactored
2. Verify API endpoint parameters (page, page_size)
3. Check if total count calculation is broken

---

### 6. Security Integration Tests (36 failures)
**File**: `backend/test/integration/security/test_hql_generator_security.py`
**Impact**: HQL security validation failing

**Affected Test Classes**:
- `TestFieldBuilderSecurity` (9 failures)
- `TestWhereBuilderSecurity` (9 failures)
- `TestJoinBuilderSecurity` (9 failures)
- `TestUnionBuilderSecurity` (9 failures)

**Common Pattern**:
```python
AssertionError: Expected validation to reject malicious input, but it was accepted
```

**Investigation Steps**:
1. Check if SQLValidator is being used
2. Verify security rules are enforced
3. Check if validation logic was accidentally disabled

---

### 7. Graph Utils Tests (20 failures)
**File**: `backend/test/unit/core/test_graph_utils.py`
**Impact**: Canvas graph algorithms broken

**Affected Test Classes**:
- `TestBFSTraversal` (5 failures)
- `TestFindIsolatedNodes` (4 failures)
- `TestDetectCyclesDFS` (4 failures)
- `TestBuildGraphFromEdges` (4 failures)
- `TestFindStartNodes` (3 failures)
- `TestFindEndNodes` (3 failures)
- `TestCountNodeConnections` (3 failures)

**Investigation Steps**:
1. Check if graph utility functions were refactored
2. Verify graph data structure changes
3. Check for breaking changes in function signatures

---

### 8. API Comprehensive Tests (Multiple failures)
**File**: `backend/test/unit/api/test_api_comprehensive.py`
**Impact**: Core CRUD operations failing

**Failed Tests**:
- `test_02_create_game_success`
- `test_03_create_game_duplicate_gid`
- `test_06_get_event_detail_not_found`
- `test_08_create_event_success`
- `test_03_delete_category_with_events`

**Investigation Steps**:
1. Check if API routes are registered
2. Verify database migrations ran
3. Check for schema validation errors

---

### 9. Parameter Services (12 failures)
**Files**: Multiple parameter service test files
**Impact**: Parameter management degraded

**Failed Tests**:
- `test_batch_get_game_gids_by_param_ids`
- `test_get_common_params_caching`
- `test_sync_common_params_uses_batch_query`
- `test_link_to_library_success`
- `test_cache_configuration`
- `test_parameters_all_uses_game_gid`
- `test_parameter_details_uses_game_gid`
- `test_parameter_search_uses_game_gid`
- `test_parameter_validate_uses_game_gid`

**Investigation Steps**:
1. Check if ParameterService was refactored
2. Verify batch query methods exist
3. Check for game_gid migration issues

---

### 10. TypeScript Type Errors (8 errors)
**Files**: Multiple TypeScript files
**Impact**: Type safety compromised, potential runtime errors

**Error Details**:

1. **Apollo Client Configuration** (2 errors)
   - File: `src/graphql/hooks.ts`
   - Lines: 92, 384
   - Issue: `refetchOnWindowFocus` not valid in Apollo Client v3
   ```
   TS2769: No overload matches this call.
   'refetchOnWindowFocus' does not exist in type 'Options<...>'
   ```

2. **Missing Type Definitions** (3 errors)
   - File: `src/shared/types/api-types.ts`
   - Lines: 68, 73, 78
   - Missing: `Field`, `EventParam`, `Game` types
   ```
   TS2304: Cannot find name 'Field'
   TS2304: Cannot find name 'EventParam'
   TS2304: Cannot find name 'Game'
   ```

3. **Export Issues** (3 errors)
   - File: `src/shared/types/index.ts`
   - Lines: 93, 94, 100
   - Issues: Missing exports, duplicate exports
   ```
   TS2305: Module has no exported member 'adaptFieldToFrontend'
   TS2305: Module has no exported member 'adaptFieldFromFrontend'
   TS2308: Duplicate export 'WhereCondition'
   ```

**Fixes Required**:

1. Remove `refetchOnWindowFocus` from Apollo Client options
2. Add missing type definitions to `api-types.ts`
3. Fix export statements in `types/index.ts`

---

## P1 - High Priority Issues

### 1. Cache Performance Tests (5 failures)
**File**: `backend/test/unit/core/cache/test_hql_v2_cache_performance.py`
**Impact**: Cache functionality uncertain

### 2. HQL History Enhancements (10 failures)
**File**: `backend/test/unit/api/test_hql_history_enhancements.py`
**Impact**: HQL history management broken

### 3. Event Nodes API (5 failures)
**File**: `backend/test/unit/api/test_api_comprehensive.py::TestEventNodesAPI`
**Impact**: Event node operations failing

### 4. Secure Hasher Tests (4 failures)
**File**: `backend/test/unit/core/security/test_crypto.py::TestSecureHasher`
**Impact**: Cryptographic functions uncertain

### 5. Entity Tests (3 failures)
**File**: `backend/test/unit/models/test_entities.py::TestEventEntity`
**Impact**: Entity validation uncertain

---

## P2 - Medium Priority Issues

### 1. Join Builder Tests (5 failures)
**File**: `backend/test/unit/services/hql/test_join_builder.py`
**Impact**: Join functionality partially broken

### 2. Where Builder Tests (5 failures)
**File**: `backend/test/unit/services/hql/test_where_builder.py`
**Impact**: WHERE clause generation uncertain

### 3. Frontend Test Failures (~15 failures)
**Files**: Multiple frontend test files
**Impact**: Frontend functionality partially degraded

---

## Quick Fix Commands

### Backend Quick Diagnostics
```bash
# Check for missing repositories
find backend/models/repositories -name "*.py" | grep -v __pycache__

# Check database schema
sqlite3 data/dwd_generator.db ".schema" | grep -i template

# Check for import errors
cd backend
python -c "from backend.models.repositories.hql_template_repository import HQLTemplateRepository"

# Check service availability
python -c "from backend.services.hql.core.generator import HQLGenerator"
```

### Frontend Quick Diagnostics
```bash
# Check TypeScript errors
cd frontend
npm run type-check 2>&1 | grep "error TS"

# Check for missing types
grep -r "interface Field" src/shared/types/
grep -r "interface EventParam" src/shared/types/
grep -r "interface Game" src/shared/types/

# Check for duplicate exports
grep -r "export.*WhereCondition" src/shared/types/
```

---

## Recommended Fix Order

### Phase 1: Unblock Tests (Today)
1. Fix HQL Template Repository imports (22 errors)
2. Fix TypeScript type definitions (8 errors)
3. Fix XSS protection test imports (5 errors)

### Phase 2: Critical Functionality (This Week)
4. Fix HQL Preview API (31 failures)
5. Fix Batch Category Deletion (6 errors)
6. Fix Pagination (12 errors)
7. Fix Security Integration Tests (36 failures)

### Phase 3: Stabilization (Next Week)
8. Fix Graph Utils (20 failures)
9. Fix API Comprehensive (9 failures)
10. Fix Parameter Services (12 failures)

---

## Summary Statistics

**Total Issues**: 320
- P0 Critical: 232 (72.5%)
- P1 High: 42 (13.1%)
- P2 Medium: 28 (8.8%)
- P3 Low: 18 (5.6%)

**Estimated Fix Time**:
- Phase 1 (Unblock): 2-4 hours
- Phase 2 (Critical): 16-24 hours
- Phase 3 (Stabilization): 8-12 hours

**Total Estimated Time**: 26-40 hours

**Recommended Team Size**: 2-3 developers

**Timeline**:
- Week 1: Phase 1 + Phase 2 (Critical)
- Week 2: Phase 3 (Stabilization) + Regression testing

---

**Next Steps**:
1. Assign developers to each phase
2. Create GitHub issues for each failure group
3. Set up daily test execution monitoring
4. Establish fix verification process
5. Document root causes for future prevention
