# Repository Layer - Parameter Management

## Architecture Overview

This directory contains the concrete implementations of the repository interfaces defined in the Domain Layer. The Repository Pattern is used to abstract data access logic and provide a clean separation between the business logic and database operations.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│              Application Layer                       │
│         (Services, Controllers, API)                 │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│            Domain Layer (Interfaces)                 │
│  - IParameterRepository                              │
│  - ICommonParameterRepository                        │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│       Infrastructure Layer (Implementations)         │
│  - ParameterRepositoryImpl                           │
│  - CommonParameterRepositoryImpl                     │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│               Database (SQLite)                      │
│  - event_params table                                │
│  - common_params table                               │
└─────────────────────────────────────────────────────┘
```

## Components

### 1. ParameterRepositoryImpl

**Purpose**: Provides data access methods for event parameters stored in the `event_params` table.

**Key Features**:
- CRUD operations for event parameters
- Query parameters by game, event, or name
- Filter common vs non-common parameters
- Parameter usage statistics
- Soft delete support (sets `is_active=0`)

**Location**: `/backend/infrastructure/persistence/repositories/parameter_repository_impl.py`

**Usage Example**:
```python
from backend.infrastructure.persistence.repositories import get_parameter_repository

# Get repository instance
repo = get_parameter_repository()

# Find parameters by game
params = repo.find_by_game(game_gid=90000001)

# Find common parameters
common_params = repo.find_common_by_game(game_gid=90000001)

# Get parameter usage statistics
stats = repo.get_parameter_usage_stats(game_gid=90000001)

# Create new parameter
from backend.domain.models.parameter import Parameter
param = Parameter(
    param_name='zoneId',
    param_type='int',
    json_path='$.zoneId',
    event_id=1,
    game_gid=90000001
)
created = repo.save(param)

# Soft delete parameter
repo.delete(param_id=created.id)
```

### 2. CommonParameterRepositoryImpl

**Purpose**: Provides data access methods for common parameters stored in the `common_params` table.

**Key Features**:
- CRUD operations for common parameters
- Query by game and parameter name
- Automatic recalculation of common parameters based on threshold
- Batch deletion by game

**Location**: `/backend/infrastructure/persistence/repositories/common_parameter_repository_impl.py`

**Usage Example**:
```python
from backend.infrastructure.persistence.repositories import get_common_parameter_repository
from backend.domain.models.common_parameter import CommonParameter, ParameterType

# Get repository instance
repo = get_common_parameter_repository()

# Find common parameters by game
common_params = repo.find_by_game(game_gid=90000002)

# Recalculate common parameters for a game
# (finds parameters appearing in ≥80% of events)
new_common_params = repo.recalculate_for_game(
    game_gid=90000002,
    threshold=0.8
)

# Create common parameter manually
common_param = CommonParameter(
    id=None,
    game_gid=90000002,
    param_name='serverId',
    param_name_cn='服务器ID',
    param_type=ParameterType.STRING,
    occurrence_count=5,
    total_events=6,
    threshold=0.8
)
created = repo.save(common_param)

# Delete all common parameters for a game
repo.delete_by_game(game_gid=90000002)
```

### 3. Factory Functions

**Purpose**: Centralized repository instantiation using the Factory Pattern.

**Location**: `/backend/infrastructure/persistence/repositories/__init__.py`

**Usage**:
```python
from backend.infrastructure.persistence.repositories import (
    get_parameter_repository,
    get_common_parameter_repository
)

# Get repository instances
param_repo = get_parameter_repository()
common_param_repo = get_common_parameter_repository()
```

## Database Schema

### event_params Table

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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    json_path TEXT,
    FOREIGN KEY (event_id) REFERENCES log_events(id) ON DELETE CASCADE,
    FOREIGN KEY (library_id) REFERENCES param_library(id) ON DELETE SET NULL,
    FOREIGN KEY (template_id) REFERENCES param_templates(id),
    UNIQUE(event_id, param_name, version)
);
```

### common_params Table

```sql
CREATE TABLE common_params (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    param_name TEXT NOT NULL,
    param_name_cn TEXT,
    param_type TEXT NOT NULL,
    param_description TEXT,
    table_name TEXT NOT NULL,
    status TEXT DEFAULT 'new',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    display_name TEXT,
    game_gid INTEGER,
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
);
```

## Testing

### Running Tests

```bash
# Run all repository tests
pytest backend/tests/unit/infrastructure/repositories/ -v

# Run specific repository tests
pytest backend/tests/unit/infrastructure/repositories/test_parameter_repository_impl.py -v
pytest backend/tests/unit/infrastructure/repositories/test_common_parameter_repository_impl.py -v

# Run with coverage
pytest backend/tests/unit/infrastructure/repositories/ \
    --cov=backend.infrastructure.persistence.repositories \
    --cov-report=html \
    --cov-report=term
```

### Test Coverage

- **Total Tests**: 36 (19 for ParameterRepositoryImpl, 17 for CommonParameterRepositoryImpl)
- **Coverage**: 62% (reasonable for repository implementations)
- **All Tests**: PASSING ✅

### Test Fixtures

Tests use the following fixtures:

- `param_repository`: Fresh ParameterRepositoryImpl instance
- `common_param_repository`: Fresh CommonParameterRepositoryImpl instance
- `test_event`: Creates a test event for parameter tests (auto-cleanup)
- `test_game`: Creates a test game for common parameter tests (auto-cleanup)
- `sample_param_data`: Sample parameter data
- `sample_common_param_data`: Sample common parameter data

### Test Data Safety

**Important**: All tests use GID in the 90000000+ range to avoid conflicts with production data (STAR001 uses GID 10000147).

```python
TEST_GID = 90000001  # Safe test GID (not STAR001)
```

## Development Guidelines

### 1. SQL Injection Prevention

All SQL queries use parameterized statements:

```python
# ✅ Correct: Parameterized query
query = "SELECT * FROM event_params WHERE event_id = ?"
result = fetch_one_as_dict(query, (event_id,))

# ❌ Wrong: String concatenation (SQL injection risk)
query = f"SELECT * FROM event_params WHERE event_id = {event_id}"
```

### 2. Error Handling

Repository methods catch specific exceptions and log with context:

```python
try:
    result = fetch_one_as_dict(query, params)
    return self._dict_to_parameter(result)
except Exception as e:
    logger.error(f"Error finding parameter by ID {param_id}: {e}")
    raise  # Re-raise for Service layer to handle
```

### 3. Type Hints

All methods have complete type annotations:

```python
def find_by_id(self, param_id: int) -> Optional[Parameter]:
    """
    Find parameter by ID

    Args:
        param_id: Parameter ID

    Returns:
        Parameter object or None if not found
    """
    pass
```

### 4. Domain Model Mapping

Database rows are converted to domain models using helper methods:

```python
def _dict_to_parameter(self, data: Dict[str, Any]) -> Parameter:
    """Convert database dictionary to Parameter domain model"""
    return Parameter(
        id=data.get('id'),
        param_name=data.get('param_name', ''),
        param_type=param_type,  # Mapped from template
        ...
    )
```

## API Contract Compliance

The repository implementations comply with the interface contracts defined in:

- `backend/domain/repositories/parameter_repository.py`
- `backend/domain/repositories/common_parameter_repository.py`

All interface methods are implemented with proper signatures and behavior.

## Performance Considerations

1. **Caching**: Repository implementations can be extended with caching (see EventRepository for example)
2. **N+1 Queries**: Complex queries use JOINs to avoid N+1 problems
3. **Indexes**: Database tables have proper indexes on frequently queried columns

## Future Enhancements

1. **Caching Layer**: Add Redis caching for frequently accessed parameters
2. **Bulk Operations**: Implement bulk insert/update methods for better performance
3. **Query Builders**: Add complex query builders for advanced filtering
4. **Auditing**: Add audit trail for parameter changes

## Related Documentation

- [Domain Models](/Users/mckenzie/Documents/event2table/backend/domain/models/README.md)
- [Database Schema](/Users/mckenzie/Documents/event2table/docs/development/architecture.md)
- [Testing Guide](/Users/mckenzie/Documents/event2table/docs/testing/e2e-testing-guide.md)

## Maintenance

### Adding New Repository Methods

1. Update the interface in `backend/domain/repositories/`
2. Implement the method in the repository implementation
3. Add unit tests in `backend/tests/unit/infrastructure/repositories/`
4. Update this README with usage examples

### Database Schema Changes

When modifying database schema:

1. Update the schema documentation in this README
2. Modify the `_dict_to_parameter()` mapping methods
3. Update tests to use new schema
4. Run full test suite to verify compatibility

## Support

For issues or questions about the repository layer:

1. Check the test files for usage examples
2. Review the interface contracts in the Domain Layer
3. Consult the architecture documentation
4. Contact the development team
