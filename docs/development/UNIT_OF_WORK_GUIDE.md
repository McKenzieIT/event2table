# Unit of Work Pattern - Implementation Guide

## Overview

The Unit of Work (UoW) pattern is a critical infrastructure component that manages database transactions and domain events in the Event2Table backend. This guide covers the enhanced implementation with complete transaction safety, domain event publishing, and operation tracking.

## Table of Contents

1. [Architecture](#architecture)
2. [Core Concepts](#core-concepts)
3. [Usage Patterns](#usage-patterns)
4. [Domain Events](#domain-events)
5. [Event Handlers](#event-handlers)
6. [Best Practices](#best-practices)
7. [Migration Guide](#migration-guide)
8. [Troubleshooting](#troubleshooting)

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  Application Layer                       │
│  (API Routes, Application Services, Commands/Handlers)  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Unit of Work (Transaction Boundary)         │
│  - BEGIN/COMMIT/ROLLBACK                                 │
│  - Repository Lazy Loading                               │
│  - Domain Event Registration                             │
│  - Operation Tracking                                    │
└────────┬────────────────────────────────────┬───────────┘
         │                                    │
         ▼                                    ▼
┌────────────────────┐            ┌──────────────────────────┐
│   Repositories     │            │   Domain Event Publisher  │
│  (Data Access)     │            │   (Event Dispatch)        │
│  - Parameters      │            └────────┬─────────────────┘
│  - Common Params   │                     │
│  - Games           │                     ▼
│  - Events          │            ┌──────────────────────────┐
└────────────────────┘            │   Event Handlers         │
                                  │  - Cache Invalidation    │
                                  │  - Audit Logging         │
                                  │  - Analytics Updates     │
                                  └──────────────────────────┘
```

### File Structure

```
backend/infrastructure/
├── persistence/
│   ├── unit_of_work_enhanced.py        # Main UoW implementation
│   ├── unit_of_work.py                 # Legacy implementation (deprecated)
│   └── repositories/
│       ├── parameter_repository_impl.py
│       ├── common_parameter_repository_impl.py
│       └── ...
└── events/
    ├── domain_event_publisher.py       # Event publishing system
    └── parameter_event_handlers.py     # Parameter event handlers

backend/application/services/
└── parameter_app_service_uow.py        # Example service using UoW
```

---

## Core Concepts

### 1. Transaction Management

The Unit of Work ensures **atomic operations** - all changes within a transaction are committed together or rolled back on failure.

**Key Principles:**
- **BEGIN IMMEDIATE**: Starts transaction with exclusive lock for writes
- **COMMIT**: Persists all changes and publishes domain events
- **ROLLBACK**: Discards all changes and clears pending events

### 2. Repository Lazy Loading

Repositories are created only when first accessed, improving performance:

```python
with UnitOfWork() as uow:
    # Repository not created yet
    param = uow.parameters.find_by_id(123)  # Created on first access
    # Repository reused for subsequent access
    param2 = uow.parameters.find_by_id(124)
```

**Benefits:**
- Faster initialization
- Memory efficient
- Connection injection ensures transaction consistency

### 3. Domain Event Publishing

Domain events represent important business occurrences. They are:
- Registered during transaction
- Published **only after successful commit**
- Discarded on rollback

**Event Flow:**
```
Business Operation → Register Event → Commit → Publish Event → Handlers Execute
```

### 4. Operation Tracking

All operations are tracked for audit purposes:

```python
uow.add_operation("Changed parameter type", {
    'parameter_id': 123,
    'old_type': 'string',
    'new_type': 'int'
})
```

---

## Usage Patterns

### Pattern 1: Context Manager (Recommended)

Use for automatic transaction management with cleanup:

```python
from backend.infrastructure.persistence.unit_of_work_enhanced import UnitOfWork

def update_parameter_type(parameter_id: int, new_type: str):
    with UnitOfWork() as uow:
        # Get repository
        param_repo = uow.parameters

        # Load parameter
        param = param_repo.find_by_id(parameter_id)
        if not param:
            raise ValueError(f"Parameter not found: {parameter_id}")

        # Update parameter
        updated_param = param.with_type(new_type)
        param_repo.save(updated_param)

        # Register domain event
        uow.register_event(ParameterTypeChanged(
            parameter_id=parameter_id,
            old_type=param.param_type,
            new_type=new_type,
            game_gid=param.game_gid
        ))

        # Track operation
        uow.add_operation("Changed parameter type", {
            'parameter_id': parameter_id,
            'old_type': param.param_type,
            'new_type': new_type
        })

    # Auto-commit on success, auto-rollback on exception
```

**Pros:**
- Automatic cleanup
- Exception safety
- Clean syntax

### Pattern 2: Decorator

Use for automatic UoW injection:

```python
from backend.infrastructure.persistence.unit_of_work_enhanced import unit_of_work

@unit_of_work()
def change_parameter_type(uow: UnitOfWork, parameter_id: int, new_type: str) -> Dict:
    """UoW automatically injected as first parameter"""
    param_repo = uow.parameters
    param = param_repo.find_by_id(parameter_id)
    updated_param = param.with_type(new_type)
    param_repo.save(updated_param)

    # Register event
    uow.register_event(ParameterTypeChanged(...))

    # Auto-commit, auto-rollback, auto-publish events
    return updated_param.to_dict()

# Usage (no UoW parameter needed)
result = change_parameter_type(123, 'int')
```

**Pros:**
- Minimal boilerplate
- Automatic transaction management
- Clean API interface

**Cons:**
- Less explicit about transaction boundaries
- Harder to use multiple UoW instances

### Pattern 3: Manual Mode

Use when you need fine-grained control:

```python
def complex_operation():
    uow = UnitOfWork()
    try:
        uow.begin()

        # Multiple operations
        param_repo = uow.parameters
        common_repo = uow.common_params

        param = param_repo.find_by_id(123)
        param_repo.save(param.with_type('int'))

        common_repo.delete_by_game(90000001)
        common_repo.save(common_param)

        # Register events
        uow.register_event(ParameterTypeChanged(...))
        uow.register_event(CommonParametersRecalculated(...))

        uow.commit()  # Commits and publishes events

    except Exception as e:
        uow.rollback()
        raise
    finally:
        uow.close()
```

**Pros:**
- Maximum control
- Explicit transaction boundaries
- Easy to debug

**Cons:**
- More verbose
- Must remember to close connection

---

## Domain Events

### Event Types

Parameter-related domain events:

| Event | When Published | Handler Actions |
|-------|---------------|-----------------|
| `ParameterTypeChanged` | Parameter type successfully changed | Invalidate caches, log audit |
| `ParameterCountChanged` | Total parameter count changes | Trigger recalculation |
| `CommonParametersRecalculated` | Common params recalculated | Invalidate common param caches |
| `ParameterActivated` | Parameter reactivated | Invalidate caches |
| `ParameterDeactivated` | Parameter soft deleted | Invalidate caches, mark dependents |
| `ParameterValidationFailed` | Validation fails | Log for monitoring, alert |

### Registering Events

```python
from backend.domain.events.parameter_events import ParameterTypeChanged

# In your service method
uow.register_event(ParameterTypeChanged(
    parameter_id=123,
    old_type='string',
    new_type='int',
    game_gid=90000001,
    changed_by='system'  # or session['username']
))
```

### Event Publishing

Events are automatically published by UnitOfWork after successful commit:

```python
# In UnitOfWork.commit()
self.connection.commit()  # 1. Commit database
self._publish_events()     # 2. Publish events
```

**Event Publisher Dispatch:**
```
Event → DomainEventPublisher → All Subscribed Handlers
```

---

## Event Handlers

### Built-in Handlers

Located in `backend/infrastructure/events/parameter_event_handlers.py`:

```python
class ParameterEventHandler:
    @staticmethod
    def handle_parameter_type_changed(event: ParameterTypeChanged):
        # 1. Invalidate parameter cache
        CacheInvalidator.invalidate_key(f'parameter:{event.parameter_id}')

        # 2. Invalidate game parameter list caches
        CacheInvalidator.invalidate_pattern(f'parameters:game:{event.game_gid}:*')

        # 3. Log audit trail
        logger.info(f"Parameter type changed: {event.parameter_id}")

        # TODO: Invalidate dependent HQL configurations
```

### Registering Handlers

During application initialization:

```python
from backend.infrastructure.events.parameter_event_handlers import register_parameter_event_handlers

# Register all parameter event handlers
router = register_parameter_event_handlers()
```

### Creating Custom Handlers

```python
# 1. Create handler function
def my_custom_handler(event: ParameterTypeChanged):
    # Custom logic
    send_notification(event.game_gid, f"Parameter {event.parameter_id} changed")

# 2. Subscribe to events
from backend.infrastructure.events.domain_event_publisher import get_domain_event_publisher

publisher = get_domain_event_publisher()
publisher.subscribe(ParameterTypeChanged, my_custom_handler)
```

---

## Best Practices

### ✅ DO

1. **Always use Unit of Work for write operations**
   ```python
   # Good
   with UnitOfWork() as uow:
       uow.parameters.save(param)
   ```

2. **Register domain events before commit**
   ```python
   uow.register_event(ParameterTypeChanged(...))
   # Commit will publish the event
   ```

3. **Use decorator for service methods**
   ```python
   @unit_of_work()
   def service_method(uow, ...):
       # Automatic transaction management
   ```

4. **Track operations for audit**
   ```python
   uow.add_operation("Updated parameter", {...})
   ```

5. **Use context manager for automatic cleanup**
   ```python
   with UnitOfWork() as uow:
       # Auto-commit, auto-rollback, auto-close
   ```

### ❌ DON'T

1. **Don't use Unit of Work for read-only operations**
   ```python
   # Bad - unnecessary transaction
   with UnitOfWork() as uow:
       param = uow.parameters.find_by_id(123)  # Read-only

   # Good - direct repository access
   param_repo = ParameterRepositoryImpl()
   param = param_repo.find_by_id(123)
   ```

2. **Don't forget to close in manual mode**
   ```python
   # Bad
   uow = UnitOfWork()
   uow.begin()
   # ... operations ...
   uow.commit()
   # Missing: uow.close()

   # Good
   try:
       uow.begin()
       # ... operations ...
       uow.commit()
   finally:
       uow.close()
   ```

3. **Don't publish events manually**
   ```python
   # Bad - events won't be published on rollback
   publisher.publish(event)

   # Good - let UoW handle it
   uow.register_event(event)
   ```

4. **Don't reuse UoW instances**
   ```python
   # Bad - UoW is not thread-safe
   uow = UnitOfWork()
   uow.begin()

   # Good - create new instance per request
   with UnitOfWork() as uow:
       # ...
   ```

---

## Migration Guide

### From Manual Transaction Management

**Before:**
```python
def update_parameter(param_id: int, new_type: str):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("BEGIN")

        cursor.execute("UPDATE event_params SET ...")
        conn.commit()

        # Manual cache invalidation
        CacheInvalidator.invalidate_key(f'parameter:{param_id}')

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
```

**After:**
```python
@unit_of_work()
def update_parameter(uow: UnitOfWork, param_id: int, new_type: str):
    param_repo = uow.parameters
    param = param_repo.find_by_id(param_id)
    param_repo.save(param.with_type(new_type))

    # Event handler will invalidate cache
    uow.register_event(ParameterTypeChanged(...))
```

### From Existing Service

**Before:**
```python
class ParameterAppService:
    def __init__(self):
        self.param_repo = ParameterRepositoryImpl()

    def change_type(self, param_id: int, new_type: str):
        param = self.param_repo.find_by_id(param_id)
        self.param_repo.save(param.with_type(new_type))

        # Manual cache invalidation
        CacheInvalidator.invalidate_key(f'parameter:{param_id}')
```

**After:**
```python
class ParameterAppService:
    @unit_of_work()
    def change_type(self, uow: UnitOfWork, param_id: int, new_type: str):
        param_repo = uow.parameters
        param = param_repo.find_by_id(param_id)
        param_repo.save(param.with_type(new_type))

        # Automatic cache invalidation via event handler
        uow.register_event(ParameterTypeChanged(...))
```

---

## Troubleshooting

### Issue: "No active connection" Error

**Cause:** Trying to access repositories before calling `begin()`

**Solution:**
```python
# Bad
uow = UnitOfWork()
param = uow.parameters.find_by_id(123)  # Error!

# Good
with UnitOfWork() as uow:  # Calls begin() automatically
    param = uow.parameters.find_by_id(123)
```

### Issue: Events Not Published

**Cause:** Transaction was rolled back or events registered after commit

**Solution:**
```python
# Bad
with UnitOfWork() as uow:
    param = uow.parameters.find_by_id(123)
    uow.parameters.save(param)
# Event registered outside transaction - won't publish!
uow.register_event(ParameterTypeChanged(...))

# Good
with UnitOfWork() as uow:
    param = uow.parameters.find_by_id(123)
    uow.parameters.save(param)
    uow.register_event(ParameterTypeChanged(...))  # Before exit
```

### Issue: Cache Not Invalidated

**Cause:** Event handlers not registered

**Solution:**
```python
# In application initialization
from backend.infrastructure.events.parameter_event_handlers import register_parameter_event_handlers

register_parameter_event_handlers()
```

### Issue: Repository Connection Mismatch

**Cause:** Repository using different connection than UoW

**Solution:**
```python
# UoW automatically injects connection
param_repo = uow.parameters  # Connection injected automatically
```

---

## Performance Considerations

### 1. Connection Pooling

Currently using SQLite with single connection per UoW. For production with PostgreSQL/MySQL:
- Configure connection pool in `get_db_connection()`
- UoW will automatically use pooled connections

### 2. Repository Caching

Repositories are cached within UoW instance:
```python
# Same repository instance reused
repo1 = uow.parameters
repo2 = uow.parameters
assert repo1 is repo2  # True
```

### 3. Event Handler Performance

Event handlers execute synchronously after commit. For slow handlers:
- Use async handlers (see `AsyncDomainEventPublisher`)
- Offload to background tasks
- Use message queue for eventual consistency

---

## Testing

### Unit Tests

Test UoW behavior with mock connections:

```python
@patch('backend.infrastructure.persistence.unit_of_work_enhanced.get_db_connection')
def test_commit_success(mock_get_db):
    uow = UnitOfWork()
    uow.begin()
    # ... operations ...
    uow.commit()
```

### Integration Tests

Test real database transactions:

```python
def test_full_crud_cycle(integration_db):
    with UnitOfWork(integration_db) as uow:
        uow.connection.execute("INSERT INTO ...")

    # Verify data persisted
    conn = sqlite3.connect(integration_db)
    # ... assertions ...
```

---

## References

- **Martin Fowler's Unit of Work Pattern**: https://martinfowler.com/eaaCatalog/unitOfWork.html
- **Domain-Driven Design**: Eric Evans
- **Implementation Files**:
  - `backend/infrastructure/persistence/unit_of_work_enhanced.py`
  - `backend/infrastructure/events/domain_event_publisher.py`
  - `backend/infrastructure/events/parameter_event_handlers.py`

---

**Version**: 1.0
**Last Updated**: 2026-02-23
**Author**: Event2Table Development Team
