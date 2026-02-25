# Event Params Schema Fix - Complete Report

**Date**: 2026-02-10
**Project**: DWD Generator (event2table)
**Issue**: Table schema mismatch causing test failures

---

## Executive Summary

Successfully identified and fixed a critical schema mismatch in the `event_params` table. The test suite expected a `json_path` column that was missing from both the database schema and the Pydantic models. This fix includes:

- ✅ Database migration to add `json_path` column
- ✅ Pydantic Schema update to include `json_path` field
- ✅ Repository layer updates
- ✅ Test file corrections
- ✅ Comprehensive verification test suite
- ✅ All parameter management tests now passing

---

## 1. Problem Analysis

### 1.1 Original Table Structure

The `event_params` table had the following columns:

```sql
CREATE TABLE event_params (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    library_id INTEGER,
    param_name TEXT NOT NULL,
    param_name_cn TEXT,
    template_id INTEGER NOT NULL,
    param_description TEXT,
    hql_config TEXT,
    is_from_library INTEGER DEFAULT 0,
    version INTEGER DEFAULT 1,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Missing**: `json_path` column

### 1.2 Test Expectations

The functional test (`manual_functional_test.py`) expected to insert:

```python
param_data = {
    "event_id": event["id"],
    "param_name": "zone_id",
    "param_name_cn": "分区ID",
    "json_path": "$.zoneId",  # ← Missing from table
    "description": "Zone identifier"
}
```

**Issues**:
1. `json_path` column didn't exist in table
2. Column name mismatch: test used `description` but table has `param_description`
3. Missing `template_id` in test data

### 1.3 Root Cause Analysis

The `json_path` field is used extensively throughout the codebase:
- HQL generation system for JSON parameter extraction
- Field definitions in HQL preview
- Canvas visualization components
- Test scripts and examples

However, it was never added to the actual database schema or Pydantic models.

---

## 2. Solution Implementation

### 2.1 Database Migration

**File**: `migration/add_json_path_to_event_params.sql`

```sql
-- Migration: Add json_path column to event_params table
-- Date: 2026-02-10

-- Add json_path column (nullable for backward compatibility)
ALTER TABLE event_params ADD COLUMN json_path TEXT;

-- Create index on json_path for better query performance
CREATE INDEX IF NOT EXISTS idx_event_params_json_path ON event_params(json_path);
```

**File**: `backend/core/database/database.py` (Migration v19)

Added automatic migration in the `migrate_db()` function:

```python
# Migration 19: Add json_path column to event_params table
if current_version < 19:
    logger.info("Migration v19: Adding json_path column to event_params...")

    try:
        cursor.execute("PRAGMA table_info(event_params)")
        columns = [column[1] for column in cursor.fetchall()]

        if "json_path" not in columns:
            cursor.execute("ALTER TABLE event_params ADD COLUMN json_path TEXT")

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_event_params_json_path
                ON event_params(json_path)
            """)

            logger.info("Migration v19: json_path column added to event_params")

        conn.commit()
        logger.info("Migration v19 completed: event_params json_path support added")

    except Exception as e:
        logger.warning(f"Migration v19: Could not add json_path column: {e}")
```

**Migration Status**:
- ✅ Applied to `dwd_generator.db` (main database)
- ✅ Applied to `tests/test_database.db` (test database)
- ✅ Automatic migration on database initialization

### 2.2 Pydantic Schema Update

**File**: `backend/models/schemas.py`

Updated `EventParameterBase` class:

```python
class EventParameterBase(BaseModel):
    """事件参数基础模型"""

    param_name: str = Field(..., min_length=1, max_length=100, description="参数英文名")
    param_name_cn: Optional[str] = Field(None, max_length=100, description="参数中文名")
    template_id: int = Field(default=1, description="参数模板ID")
    param_description: Optional[str] = Field(None, max_length=500, description="参数描述")
    json_path: Optional[str] = Field(None, max_length=200, description="JSON路径，用于从事件JSON中提取参数值")

    @validator("json_path")
    def validate_json_path(cls, v):
        """验证JSON路径格式"""
        if v:
            v = v.strip()
            # JSON路径应该以$.开头
            if not v.startswith("$."):
                raise ValueError("json_path必须以'$.'开头（例如：'$.zoneId'）")
        return v
```

**Changes**:
- ✅ Added `json_path` field to Schema
- ✅ Added validation to ensure JSON path starts with `$.`
- ✅ Made field optional (nullable) for backward compatibility
- ✅ Added clear description in Chinese and English

### 2.3 Repository Layer Update

**File**: `backend/models/repositories/parameters.py`

Updated `bulk_create_parameters()` method:

```python
cursor.execute(
    """
    INSERT INTO event_params (
        event_id, param_name, param_name_cn,
        template_id, param_description, json_path, is_active, version
    ) VALUES (?, ?, ?, ?, ?, ?, 1, 1)
""",
    (
        event_id,
        param_data["param_name"],
        param_data.get("param_name_cn", ""),
        param_data.get("template_id", 1),
        param_data.get("param_description", ""),
        param_data.get("json_path", ""),  # ← Added
    ),
)
```

### 2.4 Test File Corrections

**File**: `manual_functional_test.py`

Fixed the parameter creation test:

```python
# Before (BROKEN):
param_data = {
    "event_id": event["id"],
    "param_name": "zone_id",
    "param_name_cn": "分区ID",
    "param_type": "int",
    "json_path": "$.zoneId",
    "description": "Zone identifier"  # ← Wrong column name
}
cursor.execute(
    """INSERT INTO event_params (event_id, param_name, param_name_cn, json_path, description)
       VALUES (?, ?, ?, ?, ?)""",
    ...
)

# After (FIXED):
param_data = {
    "event_id": event["id"],
    "param_name": "zone_id",
    "param_name_cn": "分区ID",
    "template_id": 1,
    "json_path": "$.zoneId",
    "param_description": "Zone identifier"  # ← Correct column name
}
cursor.execute(
    """INSERT INTO event_params (event_id, param_name, param_name_cn, template_id, json_path, param_description)
       VALUES (?, ?, ?, ?, ?, ?)""",
    ...
)
```

---

## 3. Verification Test Suite

Created comprehensive test script: `test/event_params_schema_fix.py`

### 3.1 Test Coverage

1. **Table Schema Inspection**
   - Verifies all columns exist
   - Checks data types
   - Validates constraints

2. **Schema Alignment**
   - Ensures Pydantic Schema fields exist in table
   - Validates critical fields are present
   - Checks for `json_path` specifically

3. **JSON Path Validation**
   - Tests valid JSON paths (`$.zoneId`, `$.user.level`)
   - Tests invalid paths (rejects missing `$.` prefix)
   - Tests optional field (empty string, None)

4. **CRUD Operations**
   - Create parameter with `json_path`
   - Retrieve parameter and verify `json_path`
   - Update `json_path` field
   - Delete parameter

### 3.2 Test Results

```
======================================================================
EVENT_PARAMS SCHEMA FIX VERIFICATION TESTS
======================================================================

✅ SUCCESS: json_path column exists in table

✅ PASS: All critical Schema fields exist in table!
   Validated fields: {'param_description', 'json_path', 'template_id', 'param_name', 'param_name_cn'}

✅ SUCCESS: json_path field exists in both Schema and table

✅ PASS: Valid JSON path - '$.zoneId'
✅ PASS: Valid nested JSON path - '$.user.level'
✅ PASS: Missing $. prefix - Correctly rejected 'zoneId'
✅ PASS: Empty path (optional field)
✅ PASS: None value (optional field)
✅ PASS: Simple valid path - '$.level'

✅ PASS: Created parameter with ID 1
✅ PASS: Retrieved parameter: test_zone_id
✅ PASS: Updated parameter json_path to: $.zoneIdUpdated
✅ PASS: Parameter deleted successfully

======================================================================
TEST SUMMARY
======================================================================
Schema Alignment               ✅ PASS
JSON Path Validation           ✅ PASS
CRUD Operations                ✅ PASS

🎉 ALL TESTS PASSED! Schema fix is complete and verified.
======================================================================
```

### 3.3 Functional Test Results

```
✅ PASS Parameter Management
   Expected: 4 tests
   Passed: 4
   Failed: 0
   Partial: 0
```

All parameter management tests now pass!

---

## 4. Impact Analysis

### 4.1 Files Modified

| File | Changes | Lines Changed |
|------|---------|---------------|
| `backend/core/database/database.py` | Added Migration v19 | +30 lines |
| `backend/models/schemas.py` | Added `json_path` field & validation | +9 lines |
| `backend/models/repositories/parameters.py` | Updated `bulk_create_parameters` | +2 lines |
| `manual_functional_test.py` | Fixed column names | +6 lines |

### 4.2 Files Created

| File | Purpose |
|------|---------|
| `migration/add_json_path_to_event_params.sql` | Standalone migration script |
| `test/event_params_schema_fix.py` | Comprehensive verification test suite |

### 4.3 Database Changes

**Databases Updated**:
- `dwd_generator.db` (main) - ✅ Migrated
- `tests/test_database.db` (test) - ✅ Migrated

**Table Modified**:
- `event_params` - Added `json_path` TEXT column

**Indexes Created**:
- `idx_event_params_json_path` on `event_params(json_path)`

### 4.4 Backward Compatibility

✅ **Fully Backward Compatible**:
- `json_path` is nullable (optional)
- Existing records without `json_path` continue to work
- No breaking changes to existing API
- Migration is non-destructive

---

## 5. Usage Examples

### 5.1 Creating a Parameter with json_path

```python
from backend.models.schemas import EventParameterCreate

param = EventParameterCreate(
    param_name="zone_id",
    param_name_cn="分区ID",
    template_id=1,
    param_description="Zone identifier",
    json_path="$.zoneId"  # New field!
)
```

### 5.2 Using in HQL Generation

```python
from backend.services.hql.models.event import Field

field = Field(
    name="zone_id",
    type="param",
    json_path="$.zoneId"  # Used for JSON extraction
)
```

### 5.3 Repository Operations

```python
from backend.models.repositories.parameters import ParameterRepository

repo = ParameterRepository()

# Create with json_path
param = repo.create({
    'event_id': 1,
    'param_name': 'user_level',
    'json_path': '$.user.level',
    'template_id': 1
})

# Query by event (json_path is included in results)
params = repo.get_active_by_event(1)
for param in params:
    print(f"{param['param_name']}: {param.get('json_path', 'N/A')}")
```

---

## 6. Technical Details

### 6.1 JSON Path Format

The `json_path` field uses standard JSONPath notation:

- `$.zoneId` - Root level field
- `$.user.level` - Nested field
- `$.items[0].id` - Array element access

### 6.2 Validation Rules

- Must start with `$.` when provided
- Can be empty string or None (optional)
- Max length: 200 characters
- Validated at Pydantic model level

### 6.3 Index Performance

Created index on `json_path` for:
- Faster lookups by JSON path
- Efficient JOIN operations
- Query optimization in HQL generation

---

## 7. Success Criteria

✅ **All Criteria Met**:

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Table schema documented | ✅ | PRAGMA output shows all columns |
| Pydantic Schema matches table | ✅ | All critical fields aligned |
| No column name mismatches | ✅ | Test uses correct `param_description` |
| Parameter CRUD operations work | ✅ | All CRUD tests pass |
| Test script passes all checks | ✅ | 3/3 test categories pass |
| No regressions | ✅ | Existing tests still pass |
| Migration system updated | ✅ | Migration v19 added and tested |

---

## 8. Recommendations

### 8.1 Immediate Actions

1. ✅ **COMPLETED**: Apply migration to all database instances
2. ✅ **COMPLETED**: Update all code to use correct column names
3. ✅ **COMPLETED**: Run verification tests

### 8.2 Future Enhancements

1. **Add JSON Path Builder UI**
   - Visual JSON path selector for users
   - Preview extracted values from sample events

2. **JSON Path Validation Enhancement**
   - Validate path against actual event JSON structure
   - Provide suggestions for common fields

3. **Documentation**
   - Add JSON path examples to user documentation
   - Create tutorial for parameter extraction

4. **Testing**
   - Add integration tests for HQL generation with json_path
   - Test edge cases (malformed JSON, missing fields)

### 8.3 Monitoring

Monitor for:
- Parameters created without `json_path` (should be encouraged for param types)
- Invalid JSON path formats (should fail validation)
- Performance impact of new index

---

## 9. Conclusion

The `event_params` schema fix has been successfully implemented and verified. The key achievement is adding the `json_path` field which was expected by the test suite and used throughout the codebase but was missing from the actual database schema.

**Key Successes**:
- ✅ Schema alignment between database, Pydantic models, and tests
- ✅ Backward compatible migration
- ✅ Comprehensive test coverage
- ✅ All parameter management tests passing
- ✅ Proper validation and error handling

**Impact**:
- Fixes test failures in parameter management
- Enables proper JSON path extraction for HQL generation
- Improves data integrity with validation
- No breaking changes to existing functionality

**Status**: ✅ **COMPLETE AND VERIFIED**

---

## Appendix A: Migration Commands

For manual database migration:

```bash
# Main database
sqlite3 dwd_generator.db < migration/add_json_path_to_event_params.sql

# Test database
sqlite3 tests/test_database.db < migration/add_json_path_to_event_params.sql
```

Or let the automatic migration handle it when the application starts.

---

## Appendix B: Verification Commands

```bash
# Check table structure
sqlite3 dwd_generator.db "PRAGMA table_info(event_params);"

# Run verification tests
python3 test/event_params_schema_fix.py

# Run functional tests
python3 manual_functional_test.py
```

---

**Report Generated**: 2026-02-10
**Author**: Claude Code (Schema Fix Task)
**Version**: 1.0
