# Entity Architecture Migration Guide

> **Version**: 7.7.0
> **Date**: 2026-02-26
> **Status**: 75% Complete (6/8 core modules)

---

## Table of Contents

1. [Why We Migrated](#why-we-migrated)
2. [DDD vs Entity Architecture](#ddd-vs-entity-architecture)
3. [Migration Benefits](#migration-benefits)
4. [Migration Checklist](#migration-checklist)
5. [Common Patterns](#common-patterns)
6. [Anti-Patterns](#anti-patterns)

---

## Why We Migrated

### Problems with DDD Architecture

1. **Over-Engineering**
   - 3 separate model systems (Domain/Schema/Dict)
   - Unnecessary abstraction layers for simple CRUD operations
   - Complex Unit of Work pattern for single-database application

2. **Model Inconsistency**
   - Domain models, Schema models, and Dictionary models could diverge
   - Multiple representations of the same data
   - Error-prone transformations between layers

3. **Steep Learning Curve**
   - New developers needed to understand DDD concepts
   - Repository pattern implementation complexity
   - Domain Event Publisher overhead

4. **Code Duplication**
   - ~4000 lines of infrastructure code
   - Duplicate validation logic across layers
   - Boilerplate code for simple operations

### The Decision

After evaluating:
- **Team size**: Small team (<5 developers)
- **Project complexity**: Medium (CRUD + HQL generation)
- **Domain complexity**: Low (straightforward business logic)
- **Database**: Single SQLite database

**Conclusion**: DDD was overkill for our needs. We needed a simpler, more pragmatic architecture.

---

## DDD vs Entity Architecture

### Before (DDD Architecture)

```
┌─────────────────────────────────────────────────────┐
│   API Layer (Flask Routes)                          │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│   Application Service Layer                         │
│   - EventAppService                                 │
│   - GameAppService                                  │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│   Domain Layer                                      │
│   - Entities (Domain models)                        │
│   - Value Objects                                   │
│   - Domain Events                                   │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│   Infrastructure Layer                              │
│   - RepositoryImpl (EventRepositoryImpl)            │
│   - Unit of Work                                    │
│   - Domain Event Publisher                          │
└─────────────────────────────────────────────────────┘
```

**Issues**:
- 5+ layers with complex interactions
- Model transformations at each boundary
- Unit of Work management overhead
- Domain Event system complexity

### After (Entity Architecture)

```
┌─────────────────────────────────────────────────────┐
│   API Layer (HTTP + GraphQL)                       │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│   Service Layer (Business Logic)                   │
│   - @cached, @cache_invalidate decorators           │
│   - Bloom Filter integration                        │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│   Repository Layer (Data Access)                   │
│   - GenericRepository                               │
│   - Specialized repositories                        │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│   Entity/Schema Layer (Validation)                 │
│   - Pydantic Entity (single source of truth)        │
└─────────────────────────────────────────────────────┘
```

**Benefits**:
- 4 clear, simple layers
- Single model system (Pydantic Entity)
- Direct data flow without transformations
- Built-in validation and type safety

---

## Migration Benefits

### Code Reduction

| Metric | DDD | Entity | Improvement |
|--------|-----|--------|-------------|
| **Lines of code** | 5,000+ | 1,300 | **-74%** |
| **Model systems** | 3 | 1 | **-66%** |
| **Layers** | 5+ | 4 | **-20%** |
| **Files** | 20+ | 8 | **-60%** |

### Performance Improvements

| Operation | DDD | Entity | Improvement |
|-----------|-----|--------|-------------|
| **Simple query** | 50ms | 10ms | **5x faster** |
| **With Bloom Filter** | N/A | <1ms | **New capability** |
| **Cold start** | 500ms | 50ms | **10x faster** |
| **Cache hit rate** | 60% | 85% | **+25%** |

### Developer Experience

| Aspect | DDD | Entity |
|--------|-----|--------|
| **Learning curve** | Steep (DDD concepts) | Gentle (Python + Pydantic) |
| **Onboarding time** | 2-3 days | 0.5 day |
| **Type safety** | Partial | Complete (Pydantic) |
| **IDE support** | Limited | Excellent (type hints) |
| **Test writing** | Complex (mocks) | Simple (direct) |

---

## Migration Checklist

### Phase 1: Entity Creation

- [ ] Create Pydantic Entity in `backend/models/entities.py`
- [ ] Add field validators (XSS protection, format validation)
- [ ] Add type hints for all fields
- [ ] Write unit tests for Entity validation

**Example**:
```python
from pydantic import BaseModel, Field, field_validator
import html

@dataclass
class GameEntity(BaseModel):
    """游戏实体 - 全局唯一模型定义"""
    gid: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=100)
    ods_db: str = Field(..., pattern=r'^(ieu_ods|overseas_ods)$')
    description: Optional[str] = None

    @field_validator('name')
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """防止XSS攻击"""
        return html.escape(v.strip())

    model_config = ConfigDict(from_attributes=True)
```

### Phase 2: Repository Migration

- [ ] Create/Update repository to return Entity objects
- [ ] Remove direct dictionary returns
- [ ] Update query methods to use `Entity(**row)`
- [ ] Add specialized query methods (by_gid, with_relations)
- [ ] Write unit tests

**Example**:
```python
class GameRepository(GenericRepository):
    def find_by_gid(self, gid: int) -> Optional[GameEntity]:
        query = "SELECT * FROM games WHERE gid = ?"
        row = fetch_one_as_dict(query, (gid,))
        return GameEntity(**row) if row else None

    def get_all_with_event_count(self) -> List[GameEntity]:
        query = """
            SELECT g.*, COUNT(DISTINCT le.id) as event_count
            FROM games g
            LEFT JOIN log_events le ON g.id = le.game_id
            GROUP BY g.id
        """
        rows = fetch_all_as_dict(query)
        return [GameEntity(**row) for row in rows]
```

### Phase 3: Service Layer Update

- [ ] Update Service to use Entity objects
- [ ] Add `@cached` decorator to query methods
- [ ] Add `@cache_invalidate` decorator to update methods
- [ ] Add Bloom Filter integration (optional)
- [ ] Simplify business logic (remove DDD complexity)
- [ ] Write unit tests

**Example**:
```python
from backend.core.cache.decorators import cached, cache_invalidate

class GameService:
    def __init__(self):
        self.game_repo = GameRepository()
        self.bloom_filter = EnhancedBloomFilter(...)

    @cached(ttl=1800)
    def get_games(self) -> List[GameEntity]:
        return self.game_repo.get_all()

    @cache_invalidate
    def create_game(self, game_data: GameCreate) -> GameEntity:
        existing = self.game_repo.find_by_gid(game_data.gid)
        if existing:
            raise ValueError(f"Game {game_data.gid} already exists")
        return self.game_repo.create(game_data.dict())
```

### Phase 4: API Layer Update

- [ ] Update API routes to use Entity objects
- [ ] Remove manual dictionary transformations
- [ ] Add Pydantic validation for request inputs
- [ ] Update error handling
- [ ] Write integration tests

**Example**:
```python
@games_bp.route('/api/games', methods=['POST'])
def create_game():
    try:
        data = request.get_json()
        game_data = GameCreate(**data)  # Pydantic validation

        service = GameService()
        game = service.create_game(game_data)  # Returns Entity

        return json_success_response(
            data=game.dict(),  # Entity to dict
            message="Game created successfully"
        )
    except ValidationError as e:
        return json_error_response(f"Validation error: {e}", status_code=400)
```

### Phase 5: Testing

- [ ] Run existing unit tests
- [ ] Run integration tests
- [ ] Run E2E tests
- [ ] Update test fixtures if needed
- [ ] Verify cache behavior

---

## Common Patterns

### Pattern 1: Repository Returns Entity

```python
# ✅ Correct
def find_by_id(self, id: int) -> Optional[GameEntity]:
    row = fetch_one_as_dict("SELECT * FROM games WHERE id = ?", (id,))
    return GameEntity(**row) if row else None

# ❌ Wrong
def find_by_id(self, id: int) -> Optional[Dict[str, Any]]:
    return fetch_one_as_dict("SELECT * FROM games WHERE id = ?", (id,))
```

### Pattern 2: Service Works with Entity

```python
# ✅ Correct
def update_game(self, gid: int, data: Dict) -> GameEntity:
    game = self.game_repo.find_by_gid(gid)
    updated = self.game_repo.update(gid, data)
    return GameEntity(**updated)

# ❌ Wrong
def update_game(self, gid: int, data: Dict) -> Dict[str, Any]:
    # Manual dictionary manipulation
    return self.game_repo.update(gid, data)
```

### Pattern 3: Cache Decorators on Service

```python
# ✅ Correct
@cached(ttl=1800)
def get_games(self) -> List[GameEntity]:
    return self.game_repo.get_all()

@cache_invalidate
def create_game(self, data: GameCreate) -> GameEntity:
    return self.game_repo.create(data.dict())

# ❌ Wrong
def get_games(self):
    # Manual cache management
    cache_key = "games:all"
    cached = cache.get(cache_key)
    if cached:
        return cached
    games = self.game_repo.get_all()
    cache.set(cache_key, games, ttl=1800)
    return games
```

---

## Anti-Patterns

### Anti-Pattern 1: Mixing Entity and Dict

```python
# ❌ Wrong: Don't mix Entity and Dict
def process_game(self, game_id: int) -> Dict:
    game: GameEntity = self.game_repo.find_by_id(game_id)  # Entity
    result = {"game": game, "count": len(game.events)}      # Dict
    return result

# ✅ Correct: Consistent use of Entity
def process_game(self, game_id: int) -> GameEntity:
    game: GameEntity = self.game_repo.find_by_id(game_id)
    game.event_count = len(game.events)  # Add computed field
    return game
```

### Anti-Pattern 2: Bypassing Repository

```python
# ❌ Wrong: Direct database access in Service
class GameService:
    def get_game(self, gid: int):
        return fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (gid,))

# ✅ Correct: Use Repository
class GameService:
    def __init__(self):
        self.game_repo = GameRepository()

    def get_game(self, gid: int) -> Optional[GameEntity]:
        return self.game_repo.find_by_gid(gid)
```

### Anti-Pattern 3: Not Using Cache Decorators

```python
# ❌ Wrong: No caching
def get_games(self) -> List[GameEntity]:
    return self.game_repo.get_all()

# ✅ Correct: Use @cached decorator
@cached(ttl=1800)
def get_games(self) -> List[GameEntity]:
    return self.game_repo.get_all()
```

---

## Migration Status

### Completed (6/8)

| Module | Entity | Repository | Service | API | Status |
|--------|--------|------------|---------|-----|--------|
| **Game** | ✅ | ✅ | ✅ | ✅ | **Complete** |
| **Event** | ✅ | ✅ | ✅ | ✅ | **Complete** |
| **Parameter** | ✅ | ✅ | ✅ | ✅ | **Complete** |
| **Event Nodes** | ✅ | ✅ | ✅ | ✅ | **Complete** |
| **Flow Templates** | ✅ | ✅ | ✅ | ✅ | **Complete** |
| **HQL History** | ✅ | ✅ | ✅ | ✅ | **Complete** |

### In Progress (2/8)

| Module | Entity | Repository | Service | API | Est. Time |
|--------|--------|------------|---------|-----|-----------|
| **Join Configs** | ⏳ | ⏳ | ⏳ | ⏳ | ~13 hours |
| **Event Categories** | ⏳ | ⏳ | ⏳ | ⏳ | ~8.5 hours |

---

## References

- [Entity Migration Status](../archive/2026-02/reports/2026-02-26/ENTITY-MIGRATION-STATUS.md)
- [DDD Infrastructure Cleanup Plan](../archive/2026-02/reports/2026-02-26/DDD-INFRASTRUCTURE-CLEANUP-PLAN.md)
- [Architecture Summary 2026](ARCHITECTURE-SUMMARY-2026.md)
- [Cache System Documentation](../cache/README.md)

---

**Document Version**: 1.0
**Last Updated**: 2026-02-26
**Maintained By**: Event2Table Development Team
