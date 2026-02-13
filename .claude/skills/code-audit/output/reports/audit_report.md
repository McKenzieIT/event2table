# Event2Table Code Audit Report

**Date**: 2026-02-11
**Mode**: Quick Audit
**Target**: backend/
**Files Scanned**: 103 Python files
**Tool**: Quick Code Audit Script

---

## 📊 Executive Summary

| Metric | Count |
|--------|-------|
| **Total Issues** | 243 |
| **🔴 CRITICAL** | 2 |
| **🟠 HIGH** | 47 |
| **🟡 MEDIUM** | 100 |
| **🟢/🔵 LOW/INFO** | 94 |

---

## 🚨 Critical Issues (2)

### 1. SQL Injection Risk in Database Module
**File**: `backend/core/database/database.py:1436`
**Severity**: 🔴 CRITICAL
**Issue**: f-string in SQL query (PRAGMA statement)
```python
cursor.execute(f"PRAGMA user_version = {version}")
```
**Recommendation**: Use parameterized query
```python
cursor.execute("PRAGMA user_version = ?", (version,))
```

### 2. SQL Injection Risk in Database Module
**File**: `backend/core/database/database.py:2734`
**Severity**: 🔴 CRITICAL
**Issue**: f-string in SQL query (PRAGMA statement)
```python
cursor.execute(f"PRAGMA user_version = {target_version}")
```
**Recommendation**: Use parameterized query
```python
cursor.execute("PRAGMA user_version = ?", (target_version,))
```

---

## 🟠 High Priority Issues (47)

### Game GID Compliance (47 issues)

**Summary**: Found 47 instances where `game_id` is used instead of `game_gid` for data associations.

**Rule**:
- ✅ `game_gid` (business GID): For all data associations
- ❌ `game_id` (database auto-increment): Only for games table primary key

**Top Affected Files**:
1. `backend/core/database/database.py` - Multiple SQL constraints
2. `backend/core/performance.py:213` - Function parameter `get_events_api(game_id, page)`
3. `backend/api/routes/*.py` - Various API endpoints

**Example Issues**:
```python
# ❌ WRONG - Using game_id in WHERE clause
WHERE game_id = ?

# ❌ WRONG - Function parameter
def get_events_api(game_id, page):

# ❌ WRONG - SQL constraint
UNIQUE(game_id, param_id, alias)

# ✅ CORRECT - Use game_gid
WHERE game_gid = ?
def get_events_api(game_gid, page):
UNIQUE(game_gid, param_id, alias)
```

---

## 🟡 Medium Priority Issues (100)

### 1. Code Complexity (12 issues)

High cyclomatic complexity detected in:

| File | Complexity | Functions | Action |
|------|-----------|-----------|--------|
| `backend/core/database/database.py` | 210 | 29 | 🔴 Refactor needed |
| `backend/core/utils.py` | 136 | 53 | 🟡 Consider splitting |
| `backend/models/events.py` | 109 | 39 | 🟡 Extract services |
| `backend/api/routes/parameters.py` | 88 | 12 | 🟡 Simplify logic |
| `backend/api/routes/hql_preview_v2.py` | 81 | 15 | 🟡 Extract helpers |

**Recommendations**:
- Refactor `database.py` into smaller modules
- Extract business logic from route handlers
- Split complex functions into smaller, testable units

### 2. Testing Coverage (94 issues - INFO level)

**Summary**: 94 implementation files lack corresponding test files.

**Missing Test Coverage**:
- Core utilities: `backend/core/*.py`
- API routes: `backend/api/routes/*.py`
- Services: `backend/services/**/*.py`

**Recommendation**:
- Aim for 80% test coverage
- Prioritize tests for:
  - Security-critical functions
  - Data access layer
  - API endpoints

---

## 📈 Detailed Statistics by Category

| Category | Issues | Severity Breakdown |
|----------|--------|-------------------|
| **GAME_GID** | 135 | MEDIUM: 135 |
| **SECURITY** | 2 | CRITICAL: 2 |
| **COMPLEXITY** | 12 | MEDIUM: 12 |
| **TESTING** | 94 | INFO: 94 |

---

## 🎯 Priority Action Items

### Immediate (P0 - This Week)
1. ✅ **Fix SQL Injection Issues** (2 issues)
   - Replace f-strings with parameterized queries
   - Estimated effort: 15 minutes

### High Priority (P1 - This Month)
2. ✅ **Fix Game GID Compliance** (47 issues)
   - Replace `game_id` with `game_gid` in all data associations
   - Update API contracts and documentation
   - Estimated effort: 4-6 hours

### Medium Priority (P2 - Next Quarter)
3. ✅ **Refactor High Complexity Files** (5 files)
   - `database.py` (210 complexity) - Split into modules
   - `utils.py` (136 complexity) - Group related functions
   - `events.py` (109 complexity) - Extract services
   - Route handlers - Simplify logic
   - Estimated effort: 2-3 weeks

4. ✅ **Improve Test Coverage** (94 files)
   - Start with critical paths (security, data access)
   - Add integration tests for API endpoints
   - Set up coverage tracking
   - Estimated effort: Ongoing

---

## 📝 Notes

### False Positives
The audit may flag some legitimate `game_id` uses:
- Games table primary key references
- Database schema definitions
- Variable names that contain "game_id" but aren't used for data associations

### Exclusions
- Test files are excluded from game_gid checks
- Comments are excluded from all checks
- Games table operations are excluded

---

## 🔄 Continuous Improvement

### Recommendations
1. **Pre-commit Hooks**: Run quick audit before commits
2. **CI/CD Integration**: Add audit to build pipeline
3. **Code Review Checklist**: Include game_gid compliance
4. **Documentation**: Update CLAUDE.md with examples

### Tools
- Use `/code-audit --quick` for daily development
- Use `/code-audit --deep` for comprehensive analysis
- Review reports in `.claude/skills/code-audit/output/reports/`

---

**Generated by**: Event2Table Code Audit Skill
**Report Location**: `.claude/skills/code-audit/output/reports/audit_report.md`
**Next Audit**: Run after addressing P0/P1 issues
