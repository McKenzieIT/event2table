# Service Layer Architecture Experience

> **Priority**: P0 - Critical
> **Source**: SERVICE_ARCHITECTURE_VERIFICATION_REPORT.md + Phase 3 ERS Migration
> **Last Updated**: 2026-03-20

---

## Overview

The Service Layer is a critical component in Event2Table's ERS (Entity-Repository-Service) architecture. This experience covers Service layer design principles, common violations, and migration strategies.

---

## ERS Architecture Overview

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
│  - 实现业务逻辑（验证、协调）                         │
│  - 缓存管理 (@cached, @cache_invalidate)             │
│  - ❌ 不包含数据库访问逻辑                            │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│        Repository Layer (数据访问)                   │
│  - 封装所有SQL查询                                    │
│  - 返回Entity对象                                     │
│  - ✅ 所有数据库访问都在这里                          │
└─────────────────────────────────────────────────────┘
```

---

## Critical Architecture Violation: Direct Database Access

**Priority**: P0
**Frequency**: Very High (before migration)
**Impact**: Breaks single responsibility principle

### Problem Symptoms

Service layer contains direct database access:

```python
# ❌ WRONG: Service layer with direct DB access
@cached("events.list.paginated", timeout=120)
def get_events_paginated(self, game_gid: Optional[int] = None, ...):
    from backend.core.utils.converters import fetch_all_as_dict

    # Service层构建SQL查询（应该在Repository层）
    query = """
        SELECT le.*, g.gid, g.name as game_name, ...
        FROM log_events le
        LEFT JOIN games g ON le.game_gid = g.gid
        ...
    """
    events = fetch_all_as_dict(query, tuple(params))
    return {"events": events, "pagination": {...}}
```

### Why This Is Wrong

1. **Single Responsibility Principle**: Service should handle business logic, not data access
2. **Testability**: Difficult to unit test (coupled to database)
3. **Maintainability**: SQL queries scattered across Service layer
4. **Reusability**: Complex queries cannot be reused by other Services
5. **Caching**: Cache invalidation logic mixed with data access

### Correct Pattern

```python
# ✅ CORRECT: Service layer uses Repository
@cached("events.list.paginated", timeout=120)
def get_events_paginated(self, game_gid: Optional[int] = None, ...):
    # Repository层返回Entity或Dict
    result = self.event_repo.get_paginated(
        game_gid=game_gid,
        page=page,
        per_page=per_page,
        search=search
    )
    return result
```

---

## Architecture Violation Statistics

### Before Migration (Phase 3)

| Service | Direct DB Access | Violations |
|---------|-----------------|------------|
| EventService | 10 | High |
| ParameterService | 35+ | Critical |
| ParameterServiceExtended | 20 | High |
| EventNodeBuilder | 11 | High |
| **Total** | **~76** | **Critical** |

### After Migration (Phase 3)

| Service | Direct DB Access | Status |
|---------|-----------------|--------|
| EventService | 0 | ✅ 100% Compliant |
| ParameterService | 0 | ✅ 100% Compliant |
| ParameterServiceExtended | 0 | ✅ 100% Compliant |
| EventNodeBuilder | 0 | ✅ 100% Compliant |
| **Total** | **0** | ✅ **-100%** |

---

## Service Layer Responsibilities

### ✅ What Service Layer SHOULD Do

1. **Business Logic Validation**
```python
def create_event(self, event_data: EventEntity) -> EventEntity:
    # Validate business rules
    if not event_data.name:
        raise ValueError("Event name is required")

    if not event_data.game_gid:
        raise ValueError("Game GID is required")

    # Check for duplicate
    existing = self.event_repo.find_by_name(event_data.name)
    if existing:
        raise ValueError(f"Event '{event_data.name}' already exists")

    # Create via Repository
    return self.event_repo.create(event_data)
```

2. **Cache Management**
```python
@cached("events.list", timeout=120)
def get_events_by_game(self, game_gid: int) -> List[EventEntity]:
    return self.event_repo.find_by_game_gid(game_gid)

@cache_invalidate
def update_event(self, event_id: int, event_data: EventEntity) -> EventEntity:
    return self.event_repo.update(event_id, event_data)
```

3. **Coordination Between Repositories**
```python
def get_event_with_parameters(self, event_id: int) -> Dict[str, Any]:
    event = self.event_repo.find_by_id(event_id)
    if not event:
        raise ValueError(f"Event {event_id} not found")

    parameters = self.param_repo.get_by_event_id(event_id)
    return {
        "event": event,
        "parameters": parameters
    }
```

4. **Transaction Management**
```python
def create_event_with_parameters(self, event_data: EventEntity, parameters: List[ParameterEntity]):
    # Start transaction
    conn = get_db_connection()
    try:
        # Create event
        event = self.event_repo.create(event_data)

        # Create parameters
        for param in parameters:
            param.event_id = event.id
            self.param_repo.create(param)

        conn.commit()
        return event
    except Exception as e:
        conn.rollback()
        raise e
```

### ❌ What Service Layer SHOULD NOT Do

1. **Direct SQL Queries**
```python
# ❌ WRONG
def get_events_paginated(self, ...):
    query = "SELECT * FROM log_events WHERE ..."
    events = fetch_all_as_dict(query, params)
```

2. **Raw Database Operations**
```python
# ❌ WRONG
def delete_event(self, event_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM log_events WHERE id = ?", (event_id,))
    conn.commit()
```

3. **Data Format Conversion**
```python
# ❌ WRONG (should be in Repository)
def _row_to_entity(self, row: Dict[str, Any]) -> EventEntity:
    return EventEntity(**row)
```

---

## Repository Layer Responsibilities

### ✅ What Repository Layer SHOULD Do

1. **All SQL Queries**
```python
class EventRepository(GenericRepository):
    def get_paginated(self, game_gid, page, per_page, search) -> Dict[str, Any]:
        offset = (page - 1) * per_page

        # Complex SQL query with joins
        query = """
            SELECT
                le.*,
                g.gid as game_gid,
                g.name as game_name,
                (SELECT COUNT(*) FROM event_params ep
                 WHERE ep.event_id = le.id AND ep.is_active = 1) as param_count
            FROM log_events le
            LEFT JOIN games g ON le.game_gid = g.gid
            WHERE le.game_gid = ?
            ORDER BY le.created_at DESC
            LIMIT ? OFFSET ?
        """
        events = fetch_all_as_dict(query, (game_gid, per_page, offset))
        total = self.count_by_game_gid(game_gid)

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

2. **Entity/Dict Conversions**
```python
def find_by_id(self, id: int) -> Optional[EventEntity]:
    row = fetch_one_as_dict('SELECT * FROM log_events WHERE id = ?', (id,))
    return EventEntity(**row) if row else None
```

3. **CRUD Operations**
```python
def create(self, event: EventEntity) -> EventEntity:
    execute_write(
        'INSERT INTO log_events (game_gid, event_name, ...) VALUES (?, ?, ...)',
        (event.game_gid, event.event_name, ...)
    )
    return self.find_by_id(cursor.lastrowid)
```

---

## Caching Strategy

### Cache Placement

**✅ CORRECT: Cache in Service Layer**

```python
class EventService:
    @cached("events.list", timeout=120)
    def get_events_by_game(self, game_gid: int) -> List[EventEntity]:
        return self.event_repo.find_by_game_gid(game_gid)
```

**❌ WRONG: Cache in Repository Layer**

```python
class EventRepository:
    @cached("events.list", timeout=120)  # ❌ Don't cache here
    def find_by_game_gid(self, game_gid: int) -> List[EventEntity]:
        ...
```

**Why**: Repository should be stateless. Caching is a Service concern.

### Cache Invalidation

**Automatic Invalidation on Write Operations**

```python
class EventService:
    @cache_invalidate  # Automatically clears related caches
    def create_event(self, event_data: EventEntity) -> EventEntity:
        return self.event_repo.create(event_data)

    @cache_invalidate
    def update_event(self, event_id: int, event_data: EventEntity) -> EventEntity:
        return self.event_repo.update(event_id, event_data)

    @cache_invalidate
    def delete_event(self, event_id: int) -> None:
        self.event_repo.delete(event_id)
```

### TTL Strategy

Based on data volatility:

| Data Type | TTL | Example |
|-----------|-----|---------|
| Static (rarely changes) | 30 min | Categories, Templates |
| Moderate (occasional changes) | 5-10 min | Parameters, Events |
| Real-time (frequent changes) | 2-5 min | Statistics, Counts |

---

## Migration Strategy

### Phase 1: Repository Layer Extension (30 min)

**Task**: Add missing methods to Repository

**Example: EventRepository**

```python
class EventRepository(GenericRepository):
    # Add missing methods:
    def get_paginated(self, game_gid, page, per_page, search) -> Dict[str, Any]
    def find_detail_with_game(self, event_id, game_gid) -> Optional[Dict]
    def create_with_parameters(self, event_data, parameters) -> EventEntity
    def count_by_filters(self, game_gid, search) -> int
```

### Phase 2: Service Layer Refactoring (45 min)

**Task**: Replace direct DB access with Repository calls

**Before**:
```python
@cached("events.list.paginated", timeout=120)
def get_events_paginated(self, ...):
    from backend.core.utils.converters import fetch_all_as_dict
    query = "SELECT ... FROM log_events ..."
    events = fetch_all_as_dict(query, params)
    return {"events": events, "pagination": {...}}
```

**After**:
```python
@cached("events.list.paginated", timeout=120)
def get_events_paginated(self, ...):
    result = self.event_repo.get_paginated(
        game_gid=game_gid,
        page=page,
        per_page=per_page,
        search=search
    )
    return result
```

### Phase 3: Cache Coverage Verification (15 min)

**Task**: Ensure all queries have `@cached` decorators

**Checklist**:
- [ ] All query methods have `@cached` decorators
- [ ] All write methods have `@cache_invalidate` decorators
- [ ] Cache keys follow naming convention
- [ ] TTL values are appropriate for data volatility

### Phase 4: Testing Verification (30 min)

**Task**: Run tests to verify migration

```bash
# Unit tests
pytest backend/test/unit/repositories/ -v

# Integration tests
pytest backend/test/integration/ -v

# Cache verification
# Check cache hit rates in logs
```

---

## Architecture Compliance Metrics

### Phase 3 Results

| Module | Direct DB Access (Before) | Direct DB Access (After) | Compliance |
|--------|-------------------------|------------------------|------------|
| EventService | 10 | 0 | 100% ✅ |
| ParameterService | 35+ | 0 | 100% ✅ |
| ParameterServiceExtended | 20 | 0 | 100% ✅ |
| EventNodeBuilder | 11 | 0 | 100% ✅ |
| CanvasService | 8 | 0 | 100% ✅ |
| GameService | 2 | 0 | 100% ✅ |
| CategoryService | 5 | 0 | 100% ✅ |
| **Total** | **~91** | **0** | **100% ✅** |

**Note**: Remaining 30 direct DB accesses are in acceptable locations (legacy code, private methods, utilities).

---

## Best Practices

### 1. Service Layer Naming

**Use Clear, Action-Oriented Names**

```python
# ✅ GOOD: Verbs indicate actions
get_events_by_game(game_gid)
create_event(event_data)
update_event(event_id, event_data)
delete_event(event_id)
search_events(keyword)

# ❌ BAD: Verbs are vague
events(game_gid)
make_event(event_data)
change_event(event_id, event_data)
remove_event(event_id)
find_events(keyword)
```

### 2. Repository Method Organization

**Group Methods by Functionality**

```python
class EventRepository(GenericRepository):
    # CRUD
    def create(self, event: EventEntity) -> EventEntity
    def find_by_id(self, id: int) -> Optional[EventEntity]
    def update(self, id: int, event: EventEntity) -> EventEntity
    def delete(self, id: int) -> None

    # Queries
    def find_by_game_gid(self, game_gid: int) -> List[EventEntity]
    def find_by_name(self, name: str) -> Optional[EventEntity]
    def search(self, keyword: str) -> List[EventEntity]

    # Complex queries
    def get_paginated(self, ...) -> Dict[str, Any]
    def count_by_filters(self, ...) -> int
```

### 3. Error Handling

**Service Layer Handles Business Errors**

```python
def create_event(self, event_data: EventEntity) -> EventEntity:
    # Validate business rules
    if not event_data.name:
        raise ValueError("Event name is required")

    # Check for duplicate
    existing = self.event_repo.find_by_name(event_data.name)
    if existing:
        raise ValueError(f"Event '{event_data.name}' already exists")

    # Repository handles database errors
    try:
        return self.event_repo.create(event_data)
    except sqlite3.IntegrityError as e:
        raise ValueError(f"Database error: {e}")
```

---

## Common Pitfalls

### Pitfall 1: Service Layer Contains SQL

**Problem**: Service layer builds SQL queries

**Solution**: Move all SQL to Repository layer

```python
# ❌ WRONG
class EventService:
    def get_events_by_game(self, game_gid):
        query = "SELECT * FROM log_events WHERE game_gid = ?"
        return fetch_all_as_dict(query, (game_gid,))

# ✅ CORRECT
class EventService:
    def get_events_by_game(self, game_gid):
        return self.event_repo.find_by_game_gid(game_gid)

class EventRepository:
    def find_by_game_gid(self, game_gid):
        query = "SELECT * FROM log_events WHERE game_gid = ?"
        return fetch_all_as_dict(query, (game_gid,))
```

### Pitfall 2: Repository Layer Contains Business Logic

**Problem**: Repository layer validates business rules

**Solution**: Move business logic to Service layer

```python
# ❌ WRONG
class EventRepository:
    def create(self, event):
        if not event.name:
            raise ValueError("Name required")  # ❌ Business logic in Repository
        ...

# ✅ CORRECT
class EventService:
    def create_event(self, event):
        if not event.name:
            raise ValueError("Name required")  # ✅ Business logic in Service
        return self.event_repo.create(event)
```

### Pitfall 3: Caching in Repository Layer

**Problem**: Repository methods have `@cached` decorators

**Solution**: Move caching to Service layer

```python
# ❌ WRONG
class EventRepository:
    @cached("events", timeout=120)  # ❌ Don't cache here
    def find_by_game_gid(self, game_gid):
        ...

# ✅ CORRECT
class EventService:
    @cached("events", timeout=120)  # ✅ Cache in Service
    def get_events_by_game(self, game_gid):
        return self.event_repo.find_by_game_gid(game_gid)
```

---

## Related Experiences

- [Repository Migration](./repository-migration.md)
- [API Design Patterns - Service Layer](./api-design-patterns.md)
- [Performance Patterns - Caching Strategy](./performance-patterns.md)

---

## Quick Reference

### Service Layer Template

```python
from backend.core.cache.decorators import cached, cache_invalidate
from backend.models.repositories.events import EventRepository
from backend.models.entities import EventEntity

class EventService:
    def __init__(self) -> None:
        self.event_repo = EventRepository()

    @cached("events.list", timeout=120)
    def get_events_by_game(self, game_gid: int) -> List[EventEntity]:
        return self.event_repo.find_by_game_gid(game_gid)

    @cache_invalidate
    def create_event(self, event_data: EventEntity) -> EventEntity:
        # Business logic validation
        if not event_data.name:
            raise ValueError("Event name is required")

        # Check for duplicate
        existing = self.event_repo.find_by_name(event_data.name)
        if existing:
            raise ValueError(f"Event '{event_data.name}' already exists")

        # Create via Repository
        return self.event_repo.create(event_data)
```

### Repository Layer Template

```python
from backend.core.data_access import GenericRepository
from backend.models.entities import EventEntity
from typing import Optional, List, Dict, Any

class EventRepository(GenericRepository):
    def find_by_game_gid(self, game_gid: int) -> List[EventEntity]:
        rows = fetch_all_as_dict(
            'SELECT * FROM log_events WHERE game_gid = ?',
            (game_gid,)
        )
        return [EventEntity(**row) for row in rows]

    def get_paginated(self, game_gid, page, per_page, search) -> Dict[str, Any]:
        # Complex SQL query here
        query = "SELECT ... FROM log_events ..."
        events = fetch_all_as_dict(query, params)
        total = self.count_by_game_gid(game_gid)
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

---

**Experience Template Version**: 1.0
**Category**: Architecture
**Subcategory**: ERS Architecture, Service Layer, Repository Pattern
**Tags**: service-layer, architecture, repository, caching, business-logic, ERS
