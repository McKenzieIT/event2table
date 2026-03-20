# mypy --strict Compliance Experience

> **Priority**: P0 - Critical
> **Source**: MYPY_STRICT_COMPLIANCE_REPORT.md
> **Last Updated**: 2026-03-20

---

## Overview

Achieving `mypy --strict` compliance is critical for type safety in Python codebases. This experience covers common type issues, solutions, and best practices for improving mypy compliance.

---

## Context: Why mypy --strict?

### Benefits

- ✅ **Catches type errors at development time** (before runtime)
- ✅ **Enforces type annotations** on all functions
- ✅ **Prevents None-related bugs** (Optional handling)
- ✅ **Improves code documentation** (types are self-documenting)
- ✅ **Enables IDE autocomplete** (better developer experience)

### Type Safety Progress

| Stage | Compliance | Errors Remaining |
|-------|-----------|------------------|
| Initial | 82% | ~7 errors (critical files) |
| After fixes | 89% | 0 errors (event_service.py) |
| Target | 95% | <5 errors (acceptable) |

---

## Challenge #1: Untyped Constructors

**Priority**: P0
**Frequency**: Very High
**Impact**: Blocks mypy --strict compliance

### Problem Symptoms

```python
error: Call to untyped function "HierarchicalCache" in typed context
error: Call to untyped function "CacheInvalidator" in typed context
```

### Root Cause

`__init__` methods missing return type annotation `-> None`.

### Solution

**Add Return Type to All `__init__` Methods**

```python
# Before
class EventService:
    def __init__(self):
        self.cache = HierarchicalCache()  # type: ignore[no-untyped-call]
        self.invalidator = CacheInvalidator(self.cache)  # type: ignore[no-untyped-call]

# After
class EventService:
    def __init__(self) -> None:  # ✅ Add -> None
        self.cache: HierarchicalCache = HierarchicalCache()
        self.invalidator: CacheInvalidator = CacheInvalidator(self.cache)
```

### Batch Fix Pattern

**Fix all Repository constructors**:

```python
# Before (4 files)
def __init__(self):
    super().__init__(...)

# After (4 files)
def __init__(self) -> None:
    super().__init__(...)
```

**Files Fixed**:
- `backend/models/repositories/events.py`
- `backend/models/repositories/games.py`
- `backend/models/repositories/event_categories.py`
- `backend/models/repositories/parameters.py`

**Also Fixed**:
- `backend/core/cache/cache_system.py` (HierarchicalCache, CacheInvalidator)

---

## Challenge #2: Missing Return Type Annotations

**Priority**: P0
**Frequency**: Very High
**Impact**: Blocks mypy --strict compliance

### Problem Symptoms

```python
error: Function is missing a return type annotation
```

### Solution

**Add Return Types to All Functions**

```python
# Before
def get_event(event_id: int):
    return self.event_repo.find_by_id(event_id)

# After
def get_event(event_id: int) -> Optional[EventEntity]:
    return self.event_repo.find_by_id(event_id)
```

### Common Return Types

| Scenario | Return Type |
|----------|-------------|
| Returns Entity | `-> EventEntity` |
| May return None | `-> Optional[EventEntity]` |
| Returns list | `-> List[EventEntity]` |
| Returns dict | `-> Dict[str, Any]` |
| Returns bool | `-> bool` |
| No return value | `-> None` |
| Returns self | `-> Self` (Python 3.11+) |

---

## Challenge #3: Optional Handling

**Priority**: P0
**Frequency**: High
**Impact**: Type safety violations

### Problem Symptoms

```python
error: Incompatible return value type (got "EnhancedBloomFilter | None", expected "EnhancedBloomFilter")
```

### Root Cause

Function declares non-Optional return type but may return `None`.

### Solution Options

**Option 1: Assert Non-None (Recommended)**

```python
# Before
def bloom_filter(self) -> EnhancedBloomFilter:  # type: ignore[misc]
    if self._bloom_filter is None:
        self._bloom_filter = EnhancedBloomFilter(...)
    return self._bloom_filter  # mypy error: could be None

# After
def bloom_filter(self) -> EnhancedBloomFilter:
    if self._bloom_filter is None:
        self._bloom_filter = EnhancedBloomFilter(...)
    assert self._bloom_filter is not None, "Bloom Filter should be initialized"
    return self._bloom_filter
```

**Option 2: Change Return Type to Optional**

```python
def bloom_filter(self) -> Optional[EnhancedBloomFilter]:
    return self._bloom_filter
```

**Option 3: Use Type Casting (Last Resort)**

```python
from typing import cast

def bloom_filter(self) -> EnhancedBloomFilter:
    if self._bloom_filter is None:
        self._bloom_filter = EnhancedBloomFilter(...)
    return cast(EnhancedBloomFilter, self._bloom_filter)
```

### Recommendation

- **Use Option 1** (assert) when None should be impossible after initialization
- **Use Option 2** (Optional) when None is a valid return value
- **Use Option 3** (cast) only when you know better than mypy (rare)

---

## Challenge #4: GenericRepository Override Issues

**Priority**: P0 (Architectural)
**Frequency**: Very High
**Impact**: 80+ type errors across all Repositories

### Problem Symptoms

```python
error: Return type "EventEntity | None" of "create" incompatible with
       return type "dict[str, Any] | None" in supertype "GenericRepository"
```

### Root Cause

Subclasses override GenericRepository methods with different return types (Entity vs Dict).

### Solution Options

**Option 1: Make GenericRepository Generic** (Recommended Long-Term)

```python
from typing import TypeVar, Generic

T = TypeVar('T')

class GenericRepository(Generic[T]):
    def create(self, data: Dict[str, Any]) -> Optional[T]:
        # Implementation
        ...

class EventRepository(GenericRepository[EventEntity]):
    def create(self, data: Dict[str, Any]) -> Optional[EventEntity]:
        # Now type-safe!
        ...
```

**Option 2: Change GenericRepository to Return Entity** (Breaking Change)

```python
class GenericRepository:
    def create(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:  # Change to Entity
        # This requires updating ALL Repositories
```

**Option 3: Use # type: ignore** (Temporary Workaround)

```python
class EventRepository(GenericRepository):
    def create(self, data: Dict[str, Any]) -> Optional[EventEntity]:  # type: ignore[override]
        # Suppress the error for now
```

### Recommendation

- **Short-term**: Use Option 3 (type: ignore) to unblock mypy
- **Medium-term**: Use Option 1 (Generic GenericRepository)
- **Long-term**: Use Option 2 (Entity-based GenericRepository)

**Estimated Effort**: 8-12 hours (affects entire Repository layer)

---

## Challenge #5: Architectural Type Mismatches

**Priority**: P0 (Architectural)
**Frequency**: High
**Impact**: 38+ type errors in single file

### Problem Symptoms

```python
error: Incompatible return value type (got "list[dict[str, Any]]", expected "list[ParameterEntity]")
error: "ParameterRepository" has no attribute "get_parameters_paginated";
       maybe "get_all_parameters_paginated"?
```

### Root Cause

Repository and Service layers have mismatched expectations:
- Repository returns `List[Dict]` but Service expects `List[Entity]`
- Method names don't match
- Missing methods in Repository

### Solution

**Refactor ParameterRepository to Return Entities**

1. **Update Repository Methods**:
```python
class ParameterRepository(GenericRepository):
    def get_parameters_paginated(self, ...) -> List[ParameterEntity]:
        # Convert Dict rows to Entities
        rows = fetch_all_as_dict(query, params)
        return [ParameterEntity(**row) for row in rows]
```

2. **Update Service to Use Correct Method Names**:
```python
# Before
params = self.param_repo.get_all_parameters_paginated(...)

# After
params = self.param_repo.get_parameters_paginated(...)
```

**Estimated Effort**: 4-6 hours (ParameterRepository + ParameterService)

---

## mypy --strict Compliance by Module

| Module | Errors | Status | Priority |
|--------|--------|--------|----------|
| `event_service.py` | 0 | ✅ Compliant | - |
| `event_node_service.py` | 0 | ✅ Compliant | - |
| `game_service.py` | Not checked | ⚠️ Pending | P1 |
| `parameter_service.py` | 38 | ❌ Issues | P0 (architectural) |
| `canvas_service.py` | Not checked | ⚠️ Pending | P1 |
| `EventRepository` | 0 | ✅ Compliant | - |
| `GameRepository` | 0 | ✅ Compliant | - |
| `EventCategoryRepository` | 0 | ✅ Compliant | - |
| `ParameterRepository` | 80+ | ❌ Issues | P0 (GenericRepository) |
| `JoinConfigRepository` | 10+ | ❌ Issues | P0 (GenericRepository) |
| `HQLHistoryRepository` | 15+ | ❌ Issues | P0 (GenericRepository) |
| Other Repositories | 40+ | ❌ Issues | P1 (minor) |

---

## Common mypy --strict Issues and Solutions

### Issue 1: Missing Return Types

**Error**: `Function is missing a return type annotation`

**Solution**:
```python
# Before
def get_event(event_id: int):
    return event_repo.find_by_id(event_id)

# After
def get_event(event_id: int) -> Optional[EventEntity]:
    return event_repo.find_by_id(event_id)
```

### Issue 2: Untyped Constructors

**Error**: `Call to untyped function "X" in typed context`

**Solution**:
```python
# Add return type to __init__
class MyClass:
    def __init__(self) -> None:  # Add -> None
        self.value = 42
```

### Issue 3: Optional Handling

**Error**: `Incompatible return value type (got "X | None", expected "X")`

**Solution**:
```python
# Option 1: Assert non-None
def get_filter(self) -> EnhancedBloomFilter:
    if self._filter is None:
        self._filter = create_filter()
    assert self._filter is not None  # Type assertion
    return self._filter

# Option 2: Change return type
def get_filter(self) -> Optional[EnhancedBloomFilter]:
    return self._filter
```

### Issue 4: Unused Type Ignores

**Error**: `Unused "type: ignore" comment`

**Solution**:
```python
# Remove the type: ignore if the issue is fixed
x = some_function()  # type: ignore[comment]  # ❌ Remove if not needed

# Or fix the underlying issue instead of ignoring
x: int = some_function()  # ✅ Fix the type
```

---

## Best Practices

### 1. Add Type Annotations to All Public Methods

```python
class EventService:
    def __init__(self) -> None:
        ...

    def get_event(self, event_id: int) -> Optional[EventEntity]:
        ...

    def get_events_by_game(self, game_gid: int) -> List[EventEntity]:
        ...

    def create_event(self, event_data: EventEntity) -> EventEntity:
        ...
```

### 2. Use Type Aliases for Complex Types

```python
from typing import Dict, List, Optional, TypedDict

class PaginatedResult(TypedDict):
    events: List[EventEntity]
    pagination: Dict[str, Any]

def get_events_paginated(...) -> PaginatedResult:
    ...
```

### 3. Enable Strict Mode Gradually

```bash
# Start with basic mypy
mypy backend/

# Then --strict for specific files
mypy backend/services/events/event_service.py --strict

# Finally --strict for all code
mypy backend/ --strict
```

### 4. Use mypy in CI/CD

```yaml
# .github/workflows/mypy.yml
- name: Run mypy
  run: |
    pip install mypy
    mypy backend/ --strict
    # Fail build if new errors introduced
```

---

## Type Stub Files

### Creating Type Stubs for Untyped Modules

**Problem**: `backend/core/utils/converters.py` has incomplete type hints

**Solution**: Create `backend/core/utils/converters.pyi`

```python
# converters.pyi
from typing import Any, Dict, List, Optional, Tuple
from sqlite3 import Connection

def get_db_connection(db_path: str = ...) -> Connection: ...
def fetch_one_as_dict(query: str, params: Tuple[Any, ...] = ...) -> Optional[Dict[str, Any]]: ...
def fetch_all_as_dict(query: str, params: Tuple[Any, ...] = ...) -> List[Dict[str, Any]]: ...
def execute_write(query: str, params: Tuple[Any, ...], conn: Optional[Connection] = ...) -> int: ...
```

**Benefits**:
- Type-check database functions without modifying original code
- Keep implementation separate from type definitions
- Easier to maintain types than inline annotations

---

## Verification

### Running mypy

```bash
# Check specific file
mypy backend/services/events/event_service.py --strict

# Check all services
mypy backend/services/ --strict

# Check all repositories
mypy backend/models/repositories/ --strict

# Generate HTML report
mypy backend/ --strict --html-report ./mypy-report/
```

### Continuous Integration

```yaml
# Add to .pre-commit-config.yaml
- repo: local
  hooks:
    - id: mypy
      name: mypy
      entry: mypy backend/ --strict
      language: system
      pass_filenames: false
```

---

## Related Experiences

- [Python Development - Type Annotations](./python-development.md)
- [Repository Migration - Entity vs Dict](./repository-migration.md)
- [API Design Patterns - Type Safety](./api-design-patterns.md)

---

## Quick Reference

### mypy Configuration

```ini
# setup.cfg or mypy.ini
[mypy]
python_version = 3.9
strict = True
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True

[[mypy.overrides]]
module = "third_party_lib.*"
ignore_missing_imports = True
```

### Common Type Annotations

```python
from typing import List, Dict, Optional, Any, Callable, TypeVar, Generic

T = TypeVar('T')

def function_name(
    param1: str,
    param2: int,
    optional_param: Optional[str] = None,
    *args: Any,
    **kwargs: Any
) -> Optional[Dict[str, Any]]:
    ...
```

---

**Experience Template Version**: 1.0
**Category**: Python Development
**Subcategory**: Type Safety, mypy
**Tags**: mypy, type-safety, strict-mode, type-annotations, python
