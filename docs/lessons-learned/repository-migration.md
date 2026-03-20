# Repository Pattern Migration Experience

> **Priority**: P0 - Critical
> **Source**: UNIT_TEST_REPOSITORY_MIGRATION.md + Phase 3 ERS Migration
> **Last Updated**: 2026-03-20

---

## Overview

Migrating from legacy Dict-based data access to Repository pattern with Entity objects is a critical architectural transformation. This experience covers the challenges, solutions, and best practices learned during the Event2Table Repository migration.

---

## Context: The Migration Challenge

### Before Migration (Dict-Based Pattern)

```python
# Service layer directly accesses database
from backend.core.utils.converters import fetch_one_as_dict, fetch_all_as_dict

def get_events_by_game(game_gid: int):
    events = fetch_all_as_dict(
        'SELECT * FROM log_events WHERE game_gid = ?',
        (game_gid,)
    )
    return events  # Returns List[Dict[str, Any]]
```

**Problems**:
- ❌ Service layer contains database access logic
- ❌ No type safety (Dict[str, Any])
- ❌ Difficult to test (mock database)
- ❌ Inconsistent caching
- ❌ SQL scattered throughout codebase

### After Migration (Repository Pattern)

```python
# Service layer uses Repository
from backend.models.repositories.events import EventRepository

def get_events_by_game(game_gid: int):
    events = self.event_repo.find_by_game_gid(game_gid)
    return events  # Returns List[EventEntity]
```

**Benefits**:
- ✅ Clear separation of concerns (ERS architecture)
- ✅ Type safety (Entity objects)
- ✅ Easy to test (mock Repository)
- ✅ Centralized caching (@cached decorators)
- ✅ Single source of truth for data access

---

## Challenge #1: Unit Test Import Errors

**Priority**: P0
**Frequency**: Very High
**Impact**: All tests fail to run

### Problem Symptoms

After Repository architecture migration (Phase 1-4), unit tests fail with import errors:

```python
# ImportError: cannot import name 'api_list_games' from 'backend.api.routes.games'
# ImportError: cannot import name 'history_service' from 'backend.services.hql.services.history_service'
# ModuleNotFoundError: No module named 'backend.graphql.schema'
```

### Root Cause

1. **API Layer Changes**: Individual function exports removed, using Flask blueprints
2. **Service Layer Consolidation**: Services renamed/moved (e.g., `history_service`)
3. **GraphQL Migration**: Moved from `backend.graphql` to `backend.gql_api`
4. **Security Functions Removed**: CSRF, rate limiting deleted

### Solution

**Fix 1: Update API Tests to Use Blueprints**

```python
# Before
from backend.api.routes.games import (
    api_list_games,
    api_create_game,
    api_update_game,
    ...
)

# After
from backend.api.routes.games import api_bp
```

**Fix 2: Update Service Import Paths**

```python
# Before
from backend.services.hql.services.history_service import HQLHistoryService

# After
from backend.services.hql.hql_history_service import HQLHistoryService
```

**Fix 3: Update GraphQL Schema Imports**

```python
# Before
from backend.graphql.schema import schema  # or v2_schema

# After
from backend.gql_api.schema import schema
```

**Fix 4: Remove Tests for Deleted Functionality**

```python
# Delete entire file: test_v1_v2_adapter.py
# Reason: V1/V2 adapter modules removed in Phase 1-4 cleanup
```

### Test Results

| Metric | Before | After |
|--------|--------|-------|
| Import Errors | 8 files | 0 files ✅ |
| Tests Collecting | 0 (blocked) | 858 ✅ |
| Tests Passing | N/A | 729 (85%) |
| Tests Failing | N/A | 108 (13%) |

**Note**: Remaining 108 failures are test data/assertion issues, NOT import errors

---

## Challenge #2: Repository Method Signature Mismatches

**Priority**: P0
**Frequency**: High
**Impact**: Type safety violations

### Problem Symptoms

```python
# mypy error: Return type "dict[str, Any]" of "GenericRepository.find_all"
#           incompatible with return type "list[ParameterEntity]"
#           expected by "ParameterService"
```

### Root Cause

GenericRepository returns `Dict[str, Any]` but Service expects Entity objects.

### Solution Options

**Option 1: Make GenericRepository Generic** (Recommended Long-Term)

```python
from typing import TypeVar, Generic

T = TypeVar('T')

class GenericRepository(Generic[T]):
    def find_by_id(self, id: int) -> Optional[T]:
        row = fetch_one_as_dict('SELECT * FROM table WHERE id = ?', (id,))
        return Entity(**row) if row else None  # Returns Entity type
```

**Option 2: Override Methods in Subclasses** (Immediate Fix)

```python
class EventRepository(GenericRepository):
    def find_by_id(self, id: int) -> Optional[EventEntity]:
        row = fetch_one_as_dict('SELECT * FROM log_events WHERE id = ?', (id,))
        return EventEntity(**row) if row else None
```

**Option 3: Convert Dict to Entity in Service** (Workaround)

```python
def get_event(event_id: int) -> EventEntity:
    event_dict = self.event_repo.find_by_id(event_id)
    return EventEntity(**event_dict)  # Convert dict to Entity
```

### Recommendation

- **Short-term**: Use Option 2 (override in subclasses)
- **Long-term**: Use Option 1 (make GenericRepository truly generic)
- **Avoid**: Option 3 (adds clutter to Service layer)

---

## Challenge #3: Direct Database Access in Service Layer

**Priority**: P0
**Frequency**: Very High
**Impact**: Architecture violation

### Problem Symptoms

Service layer contains direct database access, violating Repository pattern:

```python
# ❌ WRONG: Service layer with direct DB access
@cached("events.list.paginated", timeout=120)
def get_events_paginated(self, game_gid: Optional[int] = None, ...):
    from backend.core.utils.converters import fetch_all_as_dict

    query = """
        SELECT le.*, g.gid, g.name as game_name, ...
        FROM log_events le
        LEFT JOIN games g ON le.game_gid = g.gid
        ...
    """
    events = fetch_all_as_dict(query, tuple(params))
    return {"events": events, "pagination": {...}}
```

### Root Cause

Repository migration incomplete - complex queries not migrated to Repository layer.

### Solution

**Step 1: Create Repository Method**

```python
# In EventRepository
class EventRepository(GenericRepository):
    def get_paginated(
        self,
        game_gid: Optional[int] = None,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        # Complex SQL query logic here
        query = "SELECT ... FROM log_events ..."
        events = fetch_all_as_dict(query, params)
        total = self.count_by_filters(game_gid, search)
        return {
            "events": events,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page
            }
        }
```

**Step 2: Update Service to Use Repository**

```python
# ✅ CORRECT: Service layer uses Repository
@cached("events.list.paginated", timeout=120)
def get_events_paginated(self, game_gid: Optional[int] = None, ...):
    result = self.event_repo.get_paginated(
        game_gid=game_gid,
        page=page,
        per_page=per_page,
        search=search
    )
    return result
```

### Migration Statistics (Phase 3)

| Service | Direct DB Access (Before) | Direct DB Access (After) | Reduction |
|---------|-------------------------|------------------------|-----------|
| EventService | 10 | 0 | -100% ✅ |
| ParameterService | 25+ | 0 | -100% ✅ |
| ParameterServiceExtended | 20 | 0 | -100% ✅ |
| EventNodeBuilder | 11 | 0 | -100% ✅ |
| **Total** | **~66** | **0** | **-100%** ✅ |

---

## Challenge #4: Test Assertion Updates

**Priority**: P1
**Frequency**: High
**Impact**: Test failures after migration

### Problem Symptoms

```python
# Test expects Dict, receives Entity
def test_get_event():
    event = service.get_event(1)
    assert event['gid'] == 10000147  # ❌ TypeError: 'EventEntity' object is not subscriptable
```

### Root Cause

Repository now returns Entity objects, but tests still expect Dict access.

### Solution

**Update Assertions to Use Entity Attributes**

```python
# Before (Dict-based)
def test_get_event():
    event = service.get_event(1)
    assert event['gid'] == 10000147
    assert event['name'] == 'Test Game'

# After (Entity-based)
def test_get_event():
    event = service.get_event(1)
    assert event.gid == 10000147  # Entity attribute access
    assert event.name == 'Test Game'
```

**Batch Update Pattern**:

```python
# Find all Dict access patterns
# grep -r "event\['gid'\]" tests/
# Replace with event.gid
```

---

## Challenge #5: Missing Repository Methods

**Priority**: P0
**Frequency**: High
**Impact**: Incomplete migration

### Problem Symptoms

Service layer calls non-existent Repository methods:

```python
# AttributeError: 'EventRepository' object has no attribute 'get_paginated'
events = self.event_repo.get_paginated(game_gid, page, per_page)
```

### Root Cause

Repository migration incomplete - not all query methods migrated.

### Solution

**Identify Missing Methods and Add to Repository**

```python
# Missing methods in EventRepository
class EventRepository(GenericRepository):
    # Missing methods to add:
    def get_paginated(self, game_gid, page, per_page, search) -> Dict[str, Any]
    def find_detail_with_game(self, event_id, game_gid) -> Optional[Dict]
    def create_with_parameters(self, event_data, parameters) -> EventEntity
    def count_by_filters(self, game_gid, search) -> int
    def get_event_parameters(self, event_id) -> List[Dict]
```

**Phase 3 Results**:

| Repository | Methods Added | Tests Created |
|------------|--------------|---------------|
| EventRepository | 4 | 12 (pagination) |
| ParameterRepository | 8 | 0 |
| EventCategoryRepository | 5 | 0 |
| EventNodeRepository | 8 | 0 |
| **Total (10 new Repositories)** | **115+** | **12** |

---

## Best Practices

### 1. Repository Method Naming

**Use Consistent Naming Conventions**:

```python
# Query methods
find_by_id(id)
find_by_game_gid(game_gid)
find_all()

# CRUD methods
create(entity)
update(id, data)
delete(id)

# Complex queries
get_paginated(...)
get_detail_with_join(...)
count_by_filters(...)
```

### 2. Return Type Consistency

**All Repository Methods Should Return**:

- `Entity` or `List[Entity]` for single/all queries
- `Optional[Entity]` for queries that may not match
- `Dict[str, Any]` for complex queries (with pagination, aggregates, etc.)
- `int` for count queries
- `bool` for existence checks

### 3. Caching Integration

**Repository Layer Should Be Stateless**:

```python
# ❌ WRONG: Caching in Repository
class EventRepository:
    @cached("events", timeout=120)
    def find_by_game_gid(self, game_gid):
        ...
```

```python
# ✅ CORRECT: Caching in Service
class EventService:
    @cached("events", timeout=120)
    def get_events_by_game(self, game_gid):
        return self.event_repo.find_by_game_gid(game_gid)
```

### 4. Test Organization

**Separate Tests by Layer**:

```
backend/test/
├── unit/
│   ├── repositories/  # Repository tests (mock DB)
│   └── services/       # Service tests (mock Repository)
└── integration/
    └── api/            # API tests (real DB)
```

---

## Migration Checklist

### Pre-Migration

- [ ] Identify all direct database access in Service layer
- [ ] Create Repository interface with required methods
- [ ] Plan caching strategy (which methods need @cached)
- [ ] Create migration branches for each Service

### Migration

- [ ] Add missing methods to Repository
- [ ] Update Service to use Repository methods
- [ ] Remove `fetch_*` and `execute_*` imports from Service
- [ ] Add/update `@cached` decorators
- [ ] Update type annotations

### Post-Migration

- [ ] Update unit tests (Dict → Entity access)
- [ ] Update integration tests
- [ ] Run mypy type checking
- [ ] Verify cache hit rates
- [ ] Performance test (before/after)

---

## Common Pitfalls

### Pitfall 1: Forgetting to Update Imports

**Problem**: Service still imports `fetch_*` functions

```python
# ❌ WRONG: Old imports remain
from backend.core.utils.converters import fetch_all_as_dict

class EventService:
    def get_events(self):
        return self.event_repo.find_all()  # But still has unused import above
```

**Solution**: Remove all unused database imports

```python
# ✅ CORRECT: Only Repository import
from backend.models.repositories.events import EventRepository

class EventService:
    def __init__(self):
        self.event_repo = EventRepository()

    def get_events(self):
        return self.event_repo.find_all()
```

### Pitfall 2: Mixing Dict and Entity Access

**Problem**: Some code uses Dict, some uses Entity

```python
# ❌ WRONG: Inconsistent access
event_dict = event_repo.find_by_id(1)  # Returns Entity
event_name = event_dict['name']  # Dict access on Entity!
```

**Solution**: Always use Entity attribute access

```python
# ✅ CORRECT: Entity attribute access
event = event_repo.find_by_id(1)  # Returns EventEntity
event_name = event.name  # Entity attribute access
```

### Pitfall 3: Not Handling Optional Returns

**Problem**: Assuming Repository always returns Entity

```python
# ❌ WRONG: No None check
event = event_repo.find_by_id(999)
event_name = event.name  # AttributeError: 'NoneType' object has no attribute 'name'
```

**Solution**: Always handle Optional returns

```python
# ✅ CORRECT: Handle None case
event = event_repo.find_by_id(999)
if event is None:
    raise ValueError(f"Event not found")
event_name = event.name
```

---

## Related Experiences

- [API Design Patterns - Repository Pattern](./api-design-patterns.md#repository-pattern)
- [Performance Patterns - Caching Strategy](./performance-patterns.md#缓存策略)
- [Python Development - GenericRepository](./python-development.md#genericsrepository类型安全)
- [Service Architecture Verification](../../archive/2026-03/03-march/reports/SERVICE_ARCHITECTURE_VERIFICATION_REPORT.md)

---

## Quick Reference

### Repository Pattern Structure

```
┌─────────────────────────────────────────────────────┐
│         API Layer (HTTP + GraphQL端点)               │
│  - 处理HTTP请求/响应                                  │
│  - 参数解析和验证 (Pydantic Entity)                   │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│           Service Layer (业务逻辑)                   │
│  - 实现业务逻辑                                       │
│  - 协调多个Repository                                │
│  - 缓存管理 (@cached, @cache_invalidate)             │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│        Repository Layer (数据访问)                   │
│  - 封装数据访问逻辑                                   │
│  - CRUD操作                                          │
│  - 返回Entity对象 (而非字典) ⭐                       │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│      Entity Layer (统一数据模型) ⭐                    │
│  - Pydantic Entity: backend/models/entities.py       │
│  - 单一真相来源 (Schema + Domain Model)              │
│  - 自动输入验证                                       │
│  - 序列化/反序列化                                    │
└─────────────────────────────────────────────────────┘
```

### Migration Commands

```bash
# Find all direct database access in Service layer
grep -r "fetch_one_as_dict\|fetch_all_as_dict\|execute_write" backend/services/

# Find all Dict access patterns in tests
grep -r "\['gid'\]\|\['name'\]" backend/test/

# Run mypy to check type errors
mypy backend/services/ --strict

# Run tests to verify migration
pytest backend/test/unit/repositories/ -v
pytest backend/test/integration/ -v
```

---

**Experience Template Version**: 1.0
**Category**: Architecture
**Subcategory**: Repository Pattern, ERS Architecture
**Tags**: repository, migration, entity, service, testing, type-safety
