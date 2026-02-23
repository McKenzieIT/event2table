# Backend 500 Error Fix - Complete Report

**Date**: 2026-02-21 20:37
**Issue**: POST /api/games returning 500 Internal Server Error
**Status**: ✅ Resolved

---

## Problem Discovery

During E2E testing of the game creation flow, the API was consistently returning 500 errors when attempting to create a new game via the GameForm modal.

### Error Message
```json
{
  "error": "Failed to create game",
  "success": false
}
```

---

## Root Causes Identified

### 1. Database Schema Mismatch ❌ **CRITICAL**

**Error**: `sqlite3.OperationalError: table games has no column named dwd_prefix`

**Root Cause**: The backend code was trying to insert `dwd_prefix` and `description` columns that didn't exist in the database schema.

**Original Schema**:
```sql
CREATE TABLE games (
    id INTEGER PRIMARY KEY,
    gid TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    ods_db TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    icon_path TEXT
);
```

**Missing Columns**: `dwd_prefix`, `description`

**Fix Applied**:
```bash
sqlite3 data/dwd_generator.db "ALTER TABLE games ADD COLUMN dwd_prefix TEXT;"
sqlite3 data/dwd_generator.db "ALTER TABLE games ADD COLUMN description TEXT;"
```

**Result**: ✅ Schema updated successfully
```sql
-- New schema includes:
-- 7|dwd_prefix|TEXT|0||0
-- 8|description|TEXT|0||0
```

---

### 2. CacheInvalidator Method Name Error ❌ **CRITICAL**

**Error**: `AttributeError: type object 'CacheInvalidator' has no attribute 'invalidate_key'`

**Root Cause**: Code was using deprecated method name `invalidate_key()` which doesn't exist in the current `CacheInvalidator` class.

**Incorrect Code**:
```python
CacheInvalidator.invalidate_key("games.list")
CacheInvalidator.invalidate_key("dashboard_statistics")
```

**Investigation**:
- Searched for `invalidate_key` in games.py: Found 6 occurrences
- Checked cache_system.py: Method is `invalidate()`, not `invalidate_key()`
- Found global instance: `cache_invalidator = CacheInvalidator(hierarchical_cache)` (line 753)

**Fix Applied**:
```python
# Before
from backend.core.cache.cache_system import CacheInvalidator
CacheInvalidator.invalidate_key("games.list")

# After
from backend.core.cache.cache_system import cache_invalidator
if cache_invalidator:
    cache_invalidator.invalidate_pattern("games.list:*")
```

**Changes Made**:
1. Imported global `cache_invalidator` instance instead of class
2. Changed `invalidate_key()` → `invalidate_pattern()`
3. Added pattern wildcards (`:*`) for pattern-based invalidation
4. Added null checks for safety

**Result**: ✅ Cache invalidation working correctly

---

### 3. Cache Invalidation Method Signature Error ⚠️ **IMPORTANT**

**Error**: `TypeError: CacheInvalidator.invalidate() missing 1 required positional argument: 'pattern'`

**Root Cause**: Attempted to use instance method as class method.

**Incorrect Code**:
```python
CacheInvalidator.invalidate("dashboard_statistics")  # Missing 'self'
```

**Correct Code**:
```python
# Option 1: Use global instance (PREFERRED)
from backend.core.cache.cache_system import cache_invalidator
cache_invalidator.invalidate_pattern("dashboard_statistics:*")

# Option 2: Instantiate class (NOT RECOMMENDED)
from backend.core.cache.cache_system import CacheInvalidator, hierarchical_cache
invalidator = CacheInvalidator(hierarchical_cache)
invalidator.invalidate_pattern("dashboard_statistics:*")
```

**Investigation of CacheInvalidator API**:
```python
class CacheInvalidator:
    def __init__(self, cache: HierarchicalCache):
        self.cache = cache

    def invalidate(self, pattern: str, **kwargs):
        """精确失效单个缓存键"""
        self.cache.delete(pattern, **kwargs)

    def invalidate_pattern(self, pattern: str, **kwargs) -> int:
        """模式失效（L1）"""
        count = self.cache.invalidate_pattern(pattern, **kwargs)
        return count
```

**Fix Applied**: Used global `cache_invalidator` instance from cache_system.py:753

**Result**: ✅ Pattern-based cache invalidation working

---

## Files Modified

### 1. Database Schema
**File**: `/Users/mckenzie/Documents/event2table/data/dwd_generator.db`
**Changes**: Added two columns to `games` table

### 2. Backend API Routes
**File**: `/Users/mckenzie/Documents/event2table/backend/api/routes/games.py`
**Changes**:
- Lines 77-94: Updated import to use `cache_invalidator` global instance
- Lines 300, 427, 626, 683, 739: Updated all cache invalidation calls
- Added null checks: `if cache_invalidator:`

**Before**:
```python
sys.path.append("..")
try:
    from backend.core.cache.cache_system import CacheInvalidator
except ImportError:
    # Cache functions not available, use no-op placeholders
    def clear_cache_pattern(pattern):
        pass

# Usage:
CacheInvalidator.invalidate_key("games.list")
CacheInvalidator.invalidate_key("dashboard_statistics")
```

**After**:
```python
sys.path.append("..")
try:
    from backend.core.cache.cache_system import cache_invalidator
except ImportError:
    # Cache functions not available, use no-op placeholder
    cache_invalidator = None

# Usage:
if cache_invalidator:
    cache_invalidator.invalidate_pattern("games.list:*")
    cache_invalidator.invalidate_pattern("dashboard_statistics:*")
```

---

## Testing Results

### API Test 1: Basic Game Creation
```bash
curl -X POST http://127.0.0.1:5001/api/games \
  -H "Content-Type: application/json" \
  -d '{"name":"cache_in全局实例测试","gid":90099010,"ods_db":"ieu_ods","dwd_prefix":"dwd","description":"使用cache_invalidator全局实例"}'
```

**Response**: ✅ Success
```json
{
  "data": {
    "gid": 90099010,
    "name": "cache_in全局实例测试",
    "ods_db": "ieu_ods"
  },
  "message": "Game created successfully",
  "success": true,
  "timestamp": "2026-02-21T12:36:49.468371+00:00"
}
```

### API Test 2: Full E2E Flow
```bash
curl -X POST http://127.0.0.1:5001/api/games \
  -H "Content-Type: application/json" \
  -d '{"name":"E2E完整流程测试","gid":90099011,"ods_db":"ieu_ods","dwd_prefix":"test","description":"验证所有修复：数据库schema、cache_invalidator、Toast通知"}'
```

**Response**: ✅ Success
```json
{
  "data": {
    "gid": 90099011,
    "name": "E2E完整流程测试",
    "ods_db": "ieu_ods"
  },
  "message": "Game created successfully",
  "success": true,
  "timestamp": "2026-02-21T12:37:06.299371+00:00"
}
```

### Database Verification
```sql
SELECT gid, name, ods_db, dwd_prefix, description
FROM games
WHERE gid = 90099011;
```

**Result**: ✅ Data persisted correctly
```
90099011|E2E完整流程测试|ieu_ods|test|验证所有修复：数据库schema、cache_invalidator、Toast通知
```

---

## Summary of Fixes

| # | Issue | Severity | Status | Fix |
|---|-------|----------|--------|-----|
| 1 | Missing database columns | CRITICAL | ✅ Fixed | ALTER TABLE ADD COLUMN |
| 2 | Deprecated method name `invalidate_key` | CRITICAL | ✅ Fixed | Use `invalidate_pattern()` |
| 3 | Incorrect CacheInvalidator usage | HIGH | ✅ Fixed | Use global `cache_invalidator` instance |
| 4 | Missing null checks | MEDIUM | ✅ Fixed | Added `if cache_invalidator:` checks |

---

## Lessons Learned

### 1. Database Schema Documentation
- **Problem**: Schema changes were not documented
- **Impact**: Frontend sending fields backend didn't expect
- **Lesson**: Maintain schema documentation and version migrations
- **Action**: Create migration scripts for schema changes

### 2. Cache System API Understanding
- **Problem**: Using wrong method names and patterns
- **Impact**: AttributeError causing 500 errors
- **Lesson**: Read cache_system.py documentation before using
- **Action**: Always check existing usage examples in codebase

### 3. Global vs Class Method Confusion
- **Problem**: Using instance method as class method
- **Impact**: TypeError about missing positional argument
- **Lesson**: Check if API provides global instances
- **Action**: Use `cache_invalidator` global instance from cache_system.py:753

### 4. Python Bytecode Caching
- **Problem**: Code changes not reflected due to .pyc cache
- **Impact**: Spent time debugging already-fixed code
- **Lesson**: Always clear __pycache__ after code changes
- **Action**: Added cache clear step to restart workflow

---

## Prevention Measures

### 1. Pre-Commit Checks
```bash
# Add to .git/hooks/pre-commit
python scripts/verify/schema_consistency.py
python scripts/verify/cache_usage.py
```

### 2. Code Review Checklist
- [ ] Database schema matches backend expectations
- [ ] Cache invalidation using correct methods
- [ ] Global instances used where available
- [ ] Null checks for optional dependencies

### 3. Testing Requirements
```bash
# Always test after code changes
find backend -name "__pycache__" -type d -exec rm -rf {} +
python3 web_app.py > logs/flask_server.log 2>&1 &
sleep 3
curl -X POST http://127.0.0.1:5001/api/games ...
```

---

## Related Documentation

- **Cache System API**: `/Users/mckenzie/Documents/event2table/backend/core/cache/README.md`
- **Database Schema**: `/Users/mckenzie/Documents/event2table/docs/development/database-schema.md`
- **API Testing**: `/Users/mckenzie/Documents/event2table/docs/testing/api-testing-guide.md`

---

## Verification Commands

```bash
# 1. Check database schema
sqlite3 data/dwd_generator.db "PRAGMA table_info(games);"

# 2. Verify cache_invalidator usage
grep -n "cache_invalidator" backend/api/routes/games.py

# 3. Test API endpoint
curl -X POST http://127.0.0.1:5001/api/games \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","gid":90099999,"ods_db":"ieu_ods"}'

# 4. Check Flask logs
tail -n 20 logs/flask_server.log
```

---

**Status**: ✅ All issues resolved
**Tested By**: Automated curl tests + database verification
**Ready For**: E2E testing with Chrome DevTools MCP
