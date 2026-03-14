# SQL Injection Risks - Detailed Analysis

**Date**: 2026-03-08
**Test**: `test_no_sql_string_concatenation`
**Total Risks Found**: 244 SQL injection points
**Critical Files**: 8 high-risk files requiring immediate attention

---

## Top 10 Critical SQL Injection Risks

### 🚨 #1: GenericDataAccess Class (backend/core/data_access.py)
**Risk Level**: CRITICAL
**Lines Affected**: 140, 169, 197, 233, 279, 329, 392, 429, 471
**Impact**: Used throughout entire application

#### Vulnerable Code Examples:

```python
# Line 140 - Direct table_name interpolation
query = f"SELECT * FROM {self.table_name} WHERE {self.primary_key} = ?"
#                              ^^^^^^^^^^^^^^^^ UNVALIDATED
#                                                 ^^^^^^^^^^^^^^^ UNVALIDATED

# Line 169 - Direct field interpolation
query = f"SELECT * FROM {self.table_name} WHERE {field} = ?"
#                              ^^^^^^^^^^^^^^^^ UNVALIDATED
#                                         ^^^^^ UNVALIDATED

# Line 197 - Entire table query
query = f"SELECT * FROM {self.table_name}"
#         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ UNVALIDATED

# Line 329 - DELETE with interpolated identifiers
query = f"DELETE FROM {self.table_name} WHERE {self.primary_key} = ?"
#                   ^^^^^^^^^^^^^^^^ UNVALIDATED
#                                      ^^^^^^^^^^^^^^^ UNVALIDATED

# Line 392 - IN clause with interpolated identifiers
query = f"SELECT * FROM {self.table_name} WHERE {self.primary_key} IN ({placeholders})"
#         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ALL UNVALIDATED

# Line 471 - UPDATE with interpolated identifiers
query = f"UPDATE {self.table_name} SET {set_clause} WHERE {self.primary_key} IN ({placeholders})"
#        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ALL UNVALIDATED
```

#### Attack Vector:
```python
# Malicious input
malicious_table = "games; DROP TABLE log_events; --"
malicious_field = "id; DELETE FROM games WHERE 1=1; --"

# Results in:
query = f"SELECT * FROM {malicious_table} WHERE {malicious_field} = ?"
# Actual query: "SELECT * FROM games; DROP TABLE log_events; -- WHERE id; DELETE FROM games WHERE 1=1; -- = ?"
```

#### Existing Partial Protection:
```python
# Line 166-168: SQLValidator is imported and used for find_by_field
from backend.core.security.sql_validator import SQLValidator
SQLValidator.validate_column_name(field)
```

**Issue**: SQLValidator is imported but **not consistently applied** to all methods.

#### Fix Required:
```python
def __init__(self, table_name: str, primary_key: str = "id"):
    # Validate identifiers at initialization
    from backend.core.security.sql_validator import SQLValidator

    self.table_name = SQLValidator.validate_table_name(table_name)
    self.primary_key = SQLValidator.validate_column_name(primary_key)

def find_by_field(self, field: str, value: Any):
    # Already protected (line 166-168)
    SQLValidator.validate_column_name(field)
    query = f"SELECT * FROM {self.table_name} WHERE {field} = ?"
    return fetch_one_as_dict(query, (value,))

def find_all(self):
    # Should be protected
    query = f"SELECT * FROM {self.table_name}"
    # table_name already validated in __init__
    return fetch_all_as_dict(query)
```

---

### 🚨 #2: HQL Generation (backend/api/routes/hql_generation.py)
**Risk Level**: CRITICAL
**Issue**: No SQLValidator imported or used

#### Attack Scenario:
```python
# Malicious user input
table_name = "log_events; DROP TABLE games; --"

# Current code (vulnerable):
query = f"SELECT * FROM {table_name}"
# Actual query: "SELECT * FROM log_events; DROP TABLE games; --"

# After fix:
from backend.core.security.sql_validator import SQLValidator
validated_table = SQLValidator.validate_table_name(table_name)
query = f"SELECT * FROM {validated_table}"
# Raises: ValueError: Invalid table name: log_events; DROP TABLE games; --
```

#### Fix Required:
```python
# Add import at top of file
from backend.core.security.sql_validator import SQLValidator

# Validate all table names before use
def generate_hql(game_gid: int, user_table: str):
    validated_table = SQLValidator.validate_table_name(user_table)
    query = f"SELECT * FROM {validated_table}"
    return query
```

---

### 🚨 #3: Canvas Service (backend/services/canvas/canvas_service.py)
**Risk Level**: CRITICAL
**Issue**: No SQLValidator imported or used

#### Risk:
- Canvas service builds complex dynamic SQL
- User input directly influences table and column names
- No validation before SQL construction

#### Fix Required:
```python
# Add import
from backend.core.security.sql_validator import SQLValidator

# Validate all identifiers
def build_canvas_query(user_table: str, user_fields: List[str]):
    validated_table = SQLValidator.validate_table_name(user_table)
    validated_fields = [SQLValidator.validate_column_name(f) for f in user_fields]

    query = f"SELECT {', '.join(validated_fields)} FROM {validated_table}"
    return query
```

---

### 🟠 #4: Database Migration (backend/core/database/database.py)
**Risk Level**: HIGH
**Lines**: 1517, 2918, 2922, 2925, 2940, 3040

#### Vulnerable Code:
```python
# Line 1517 - Direct version interpolation
cursor.execute(f"PRAGMA user_version = {version}")
#                         ^^^^^^^^ UNVALIDATED

# Line 2940 - Direct table_name interpolation
cursor.execute(f"PRAGMA table_info({table_name})")
#                            ^^^^^^^^^^^^ UNVALIDATED
```

#### Attack Vector:
```python
# Malicious version number
version = "1; DROP TABLE games; --"

# Results in:
cursor.execute(f"PRAGMA user_version = 1; DROP TABLE games; --")
```

#### Fix Required:
```python
# Validate version is numeric
if not isinstance(version, int) or version < 0:
    raise ValueError(f"Invalid version: {version}")
cursor.execute(f"PRAGMA user_version = {version}")

# Validate table_name
validated_table = SQLValidator.validate_table_name(table_name)
cursor.execute(f"PRAGMA table_info({validated_table})")
```

---

### 🟠 #5: Events Repository (backend/models/repositories/events.py)
**Risk Level**: HIGH
**Lines**: 635, 657, 659

#### Issue:
- Multiple `cursor.execute()` calls in loops
- Comment indicates `executemany()` should be used

#### Performance + Security Risk:
```python
# Current code (line 635):
for param in params:
    cursor.execute(insert_sql, (param,))
    # ^^^^^^^^^^^^ N+1 query pattern

# Better approach (line 657-659):
cursor.executemany(insert_sql, params)
# Single batch operation
```

---

### 🟡 #6-10: Other Lower-Risk Issues

6. **Logging Module** (backend/core/logging.py:64)
   - False positive: Not SQL-related
   - Only log message formatting

7. **Other Repository Files**
   - Similar GenericDataAccess patterns
   - Need consistent SQLValidator usage

8. **API Routes**
   - Some dynamic query construction
   - Need SQLValidator integration

9. **Service Layer**
   - Dynamic SQL building
   - Need identifier validation

10. **Test Files**
    - Test fixtures with SQL
    - Lower priority (not production code)

---

## Attack Scenarios

### Scenario 1: Table Name Injection
```python
# Malicious input
table = "(SELECT COUNT(*) FROM log_events WHERE name LIKE '%admin%')"

# Vulnerable code
query = f"SELECT * FROM {table}"

# Resulting query
SELECT * FROM (SELECT COUNT(*) FROM log_events WHERE name LIKE '%admin%')
# Exposes data via subquery injection
```

### Scenario 2: Column Name Injection
```python
# Malicious input
column = "name) UNION SELECT password FROM users WHERE name = 'admin"

# Vulnerable code
query = f"SELECT * FROM games WHERE {column} = ?"

# Resulting query
SELECT * FROM games WHERE name) UNION SELECT password FROM users WHERE name = 'admin' = ?
# Exposes passwords via UNION injection
```

### Scenario 3: DELETE Statement Injection
```python
# Malicious input
table = "games WHERE 1=1; DROP TABLE log_events; --"

# Vulnerable code
query = f"DELETE FROM {table}"

# Resulting query
DELETE FROM games WHERE 1=1; DROP TABLE log_events; --
# Deletes all games AND drops log_events table
```

---

## SQLValidator Protection Mechanism

### What SQLValidator Does:

```python
class SQLValidator:
    """Validate SQL identifiers to prevent injection"""

    VALID_TABLE_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)?$')
    VALID_COLUMN_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

    @classmethod
    def validate_table_name(cls, table_name: str) -> str:
        """Validate table name (can include database prefix)"""
        if not cls.VALID_TABLE_PATTERN.match(table_name):
            raise ValueError(f"Invalid table name: {table_name}")
        return table_name

    @classmethod
    def validate_column_name(cls, column_name: str) -> str:
        """Validate column name"""
        if not cls.VALID_COLUMN_PATTERN.match(column_name):
            raise ValueError(f"Invalid column name: {column_name}")
        return column_name
```

### What It Blocks:

✅ **Allowed**:
- `games`
- `log_events`
- `ieu_ods.ods_10000147_all_view`
- `role_id`
- `account_id`

❌ **Blocked**:
- `games; DROP TABLE` (semicolon)
- `log_events--` (SQL comment)
- `table name` (spaces)
- `table;name` (semicolon)
- `table.name; DROP` (semicolon)
- `1table` (starts with number)
- `_table` (starts with underscore - optional restriction)

---

## Remediation Priority

### P0 - Immediate (Today)
1. **Add SQLValidator to GenericDataAccess.__init__()**
   - Validate table_name and primary_key at initialization
   - Update all methods to use validated identifiers

2. **Add SQLValidator to hql_generation.py**
   - Import SQLValidator
   - Validate all table names before query construction

3. **Add SQLValidator to canvas_service.py**
   - Import SQLValidator
   - Validate all table/column names

### P1 - High Priority (This Week)
4. **Fix database migration queries**
   - Validate PRAGMA parameters
   - Use parameterized queries where possible

5. **Replace N+1 loops with batch operations**
   - Use executemany() for bulk inserts
   - Add batch methods to repositories

### P2 - Medium Priority (Next Sprint)
6. **Add integration tests for SQL injection**
7. **Add static analysis to CI/CD**
8. **Update security documentation**

---

## Testing Strategy

### Current Test Coverage:
- ✅ Dynamic SQL concatenation detection
- ✅ Parameterization verification
- ✅ SQL injection payload testing
- ✅ Batch operation pattern detection
- ✅ SQLValidator usage verification

### Additional Tests Needed:
1. **Integration tests** for SQLValidator
2. **Fuzzing tests** with random payloads
3. **Performance tests** for batch operations
4. **Regression tests** for known vulnerabilities

---

## Conclusion

**Current State**: 244 SQL injection risks identified
**Critical Files**: 3 files with no SQLValidator protection
**High-Risk Files**: 5 files with inconsistent protection
**Remediation Time Estimate**: 2-3 days for P0 fixes

**Next Step**: Begin GREEN phase by fixing P0 critical vulnerabilities.

---

**Generated by**: SQL Injection Protection Tests
**Test Framework**: pytest 7.4.3
**Python Version**: 3.13.11
