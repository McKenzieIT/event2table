# Refactoring Action Plan

**Created**: 2026-02-10
**Project**: event2table
**Status**: Ready for Implementation

---

## Priority 1: Critical Duplicates (Week 1)

### Action Item 1.1: Remove Duplicate Response Functions

**Files to Modify**:
1. `/backend/core/errors.py` - Remove duplicates
2. `/backend/core/utils.py` - Keep as source of truth
3. All files importing from errors.py - Update imports

**Steps**:
```bash
# 1. Find all imports of errors module
grep -r "from backend.core.errors import" backend/ --include="*.py" | grep -E "json_.*_response"

# 2. Remove duplicate functions from errors.py
# Delete lines 39-76 in backend/core/errors.py

# 3. Update imports in all files
# Replace: from backend.core.errors import json_success_response, json_error_response
# With: from backend.core.utils import json_success_response, json_error_response
```

**Files Affected** (estimated 5-10 files):
- Check all files in `/backend/api/routes/`
- Check all files in `/backend/services/`
- Check all files in `/backend/models/`

**Testing**:
- Run all API endpoint tests
- Verify error responses still work correctly
- Check response format consistency

**Time Estimate**: 1-2 hours

---

### Action Item 1.2: Consolidate Validation Functions

**Source of Truth**: `/backend/core/utils/validators.py`

**Target Files** (estimated 15+ files):
```bash
# Find files with validation logic not using validators.py
grep -r "def validate_" backend/ --include="*.py" -A 5 | grep -v "backend/core/utils/validators.py"
```

**Migration Steps**:
1. Audit all validation functions
2. Consolidate duplicates into `validators.py`
3. Update all imports
4. Remove old implementations

**Example Migration**:
```python
# BEFORE (in utils.py)
def validate_event_name(name: str) -> Tuple[bool, Optional[str]]:
    # 50 lines of validation logic
    ...

# AFTER (use centralized version)
from backend.core.utils.validators import validate_event_name
```

**Time Estimate**: 2-3 hours

---

### Action Item 1.3: Standardize Error Handling with Decorators

**Current Pattern** (50+ occurrences):
```python
@api_bp.route("/some-endpoint", methods=["POST"])
def some_endpoint():
    try:
        data = request.get_json()
        result = process_data(data)
        return json_success_response(data=result)
    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error: {e}")
        return json_error_response(str(e), status_code=500)
```

**Target Pattern**:
```python
from backend.core.utils import handle_api_errors

@api_bp.route("/some-endpoint", methods=["POST"])
@handle_api_errors
def some_endpoint():
    data = request.get_json()
    result = process_data(data)
    return json_success_response(data=result)
```

**Files to Update** (all API routes):
```bash
# Find files without decorator
grep -r "def api_.*(" backend/api/routes/ --include="*.py" -A 20 | grep -B 20 "try:" | grep "^--$"
```

**Implementation**:
1. Identify all API endpoints without `@handle_api_errors`
2. Add decorator
3. Remove try-except blocks
4. Test error scenarios

**Time Estimate**: 2-3 hours

---

## Priority 2: Medium Priority (Week 2)

### Action Item 2.1: Create Cache Management Utilities

**New File**: `/backend/core/utils/cache.py`

```python
"""
Cache management utilities for automatic cache clearing
"""
from functools import wraps
from backend.core.cache.cache_system import clear_cache_pattern

def auto_clear_cache(*patterns):
    """
    Decorator to automatically clear cache patterns after function execution

    Usage:
        @auto_clear_cache("event:{event_id}", "game:{game_id}")
        def update_event(event_id, game_id, data):
            # ... update logic
            return result
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Format patterns with function arguments
            formatted_patterns = []
            for pattern in patterns:
                try:
                    formatted_patterns.append(pattern.format(**kwargs))
                except (KeyError, AttributeError):
                    formatted_patterns.append(pattern)

            # Clear caches
            for pattern in formatted_patterns:
                clear_cache_pattern(pattern)

            return result
        return wrapper
    return decorator
```

**Files to Refactor** (15+ files):
- `/backend/api/routes/events.py`
- `/backend/api/routes/games.py`
- `/backend/api/routes/parameters.py`
- `/backend/services/events/events.py`
- `/backend/services/games/games.py`

**Example Migration**:
```python
# BEFORE
def update_event(event_id, data):
    result = db_update(event_id, data)
    clear_cache_pattern(f"event:{event_id}")
    clear_cache_pattern("events:*")
    return result

# AFTER
from backend.core.utils.cache import auto_clear_cache

@auto_clear_cache("event:{event_id}", "events:*")
def update_event(event_id, data):
    return db_update(event_id, data)
```

**Time Estimate**: 1.5-2 hours

---

### Action Item 2.2: Migrate to GenericRepository Pattern

**Current Pattern** (40+ occurrences):
```python
from backend.core.database import get_db_connection

def get_something(id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM table WHERE id = ?", (id,))
        return cursor.fetchone()
    finally:
        conn.close()
```

**Target Pattern**:
```python
from backend.models.repositories.something import SomethingRepository

def get_something(id):
    repo = SomethingRepository()
    return repo.find_by_id(id)
```

**Files to Audit**:
```bash
# Find files with direct DB access
grep -r "get_db_connection()" backend/ --include="*.py" -l | grep -v "database.py"
```

**Steps**:
1. Identify all direct DB access patterns
2. Create missing Repository classes if needed
3. Replace with Repository methods
4. Test data access

**Time Estimate**: 3-4 hours

---

### Action Item 2.3: Fix Import Paths

**Current Anti-pattern** (35+ files):
```python
import sys
sys.path.append("..")
try:
    from backend.core.cache.cache_system import clear_cache_pattern
except ImportError:
    # handle import error
    pass
```

**Target Pattern**:
```python
from backend.core.cache.cache_system import clear_cache_pattern
```

**Solution Options**:
1. **Option A**: Set PYTHONPATH in environment
   ```bash
   export PYTHONPATH="/Users/mckenzie/Documents/event2table:$PYTHONPATH"
   ```

2. **Option B**: Use `python -m` to run as module
   ```bash
   python -m backend.api.routes.events
   ```

3. **Option C**: Install package in development mode
   ```bash
   cd /Users/mckenzie/Documents/event2table
   pip install -e .
   ```

**Files to Update**: All files with `sys.path.append("..")`

**Time Estimate**: 1 hour

---

## Priority 3: Low Priority (Week 3)

### Action Item 3.1: Complete Model Conversion Migration

**Current State**: Some files still have manual `to_dict()` methods

**Target**: All conversions use `/backend/core/utils/converters.py`

**Audit Script**:
```bash
# Find remaining to_dict implementations
grep -r "def .*_to_dict(" backend/ --include="*.py" | grep -v "converters.py"
```

**Files to Check**:
- Model files in `/backend/models/`
- Service files with conversion logic

**Time Estimate**: 1-2 hours

---

### Action Item 3.2: Split Large utils.py File

**Current**: `utils.py` has 1335 lines

**Target Structure**:
```
backend/core/utils/
├── __init__.py          # Central exports
├── validators.py        # ✅ Already created
├── formatters.py        # ✅ Already created
├── converters.py        # ✅ Already created
├── database.py          # NEW - DB operations
├── responses.py         # NEW - API responses
├── security.py          # NEW - Security functions
└── helpers.py           # NEW - Misc helpers
```

**Migration Strategy**:
1. Create new module files
2. Move related functions
3. Update imports in `__init__.py`
4. Update imports across codebase
5. Delete old functions from `utils.py`

**Time Estimate**: 2-3 hours

---

## Testing Strategy

### Unit Tests
```bash
# Run all tests
pytest test/unit/backend/

# Run specific module tests
pytest test/unit/backend/unit/test_utils.py
pytest test/unit/backend/unit/test_core_utils.py
```

### Integration Tests
```bash
# Test API endpoints
pytest test/integration/backend/

# Test database operations
pytest test/unit/backend/unit/test_database.py
```

### Manual Testing Checklist
- [ ] All API endpoints return correct responses
- [ ] Cache clearing works correctly
- [ ] Database operations function properly
- [ ] Error handling catches exceptions
- [ ] Validation rules are enforced

---

## Success Metrics

### Code Quality
- **Current**: 7 major duplicate patterns
- **Target**: < 2 major duplicate patterns
- **Measurement**: Manual code review

### Code Duplication
- **Current**: ~15-20% estimated duplication
- **Target**: < 5% duplication
- **Measurement**: pylint similarity analysis

### Maintainability
- **Current**: 1335-line utils.py file
- **Target**: Multiple focused modules (< 300 lines each)
- **Measurement**: File line counts

### Test Coverage
- **Current**: (unknown)
- **Target**: > 80% coverage
- **Measurement**: pytest-cov report

---

## Implementation Timeline

### Week 1: Critical Issues (8-10 hours)
- Day 1-2: Remove duplicate response functions (2-4 hours)
- Day 3-4: Consolidate validation functions (2-3 hours)
- Day 5: Standardize error handling (2-3 hours)

### Week 2: Medium Priority (6-8 hours)
- Day 1-2: Create cache utilities (1.5-2 hours)
- Day 3-4: Migrate to Repository pattern (3-4 hours)
- Day 5: Fix import paths (1 hour)

### Week 3: Low Priority (4-6 hours)
- Day 1-2: Complete model conversion (1-2 hours)
- Day 3-4: Split large utils.py (2-3 hours)
- Day 5: Final testing and cleanup (1 hour)

**Total Time Estimate**: 18-24 hours over 3 weeks

---

## Risk Mitigation

### Risk 1: Breaking Changes
- **Mitigation**: Comprehensive testing after each change
- **Backup**: Git commits after each action item
- **Rollback**: Keep git history for easy reversion

### Risk 2: Import Errors
- **Mitigation**: Update imports incrementally
- **Testing**: Run tests after each batch of changes
- **Verification**: Check all imports resolve correctly

### Risk 3: Performance Regression
- **Mitigation**: Benchmark critical paths before/after
- **Monitoring**: Watch for performance issues
- **Optimization**: Profile if slowdowns detected

---

## Resources Needed

### Development
- Python 3.9+ environment
- Test database access
- Git for version control

### Testing
- pytest test suite
- Integration test environment
- API testing tools (curl, Postman)

### Tools
- pylint for code analysis
- black for formatting
- pytest for testing

---

## Next Steps

1. **Review this plan** with team/stakeholders
2. **Create git branch** for refactoring work
3. **Start with Priority 1** items
4. **Commit frequently** after each action item
5. **Test thoroughly** before merging
6. **Document changes** in CHANGELOG.md

---

## Contact & Support

**Questions**: Refer to `/docs/development.md`
**Issues**: Create git issue for each action item
**Code Review**: Request review after each priority level

---

**Last Updated**: 2026-02-10
**Status**: Ready for Implementation
**Owner**: Development Team
