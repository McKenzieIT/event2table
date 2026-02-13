# Integration Tests

Integration tests for the Event2Table project.

## Structure

```
test/integration/
├── backend/              # Backend integration tests
│   ├── api/             # API endpoint integration tests
│   ├── database/        # Database integration tests
│   └── workflows/       # Business workflow integration tests
├── frontend/            # Frontend integration tests
│   ├── api/             # Frontend API call integration tests
│   └── workflows/       # Frontend workflow integration tests
├── conftest.py          # Shared fixtures
└── README.md            # This file
```

## Running Integration Tests

### Run all integration tests:
```bash
pytest test/integration/ -v
```

### Run specific integration test suite:
```bash
# Backend API tests
pytest test/integration/backend/api/ -v

# Backend database tests
pytest test/integration/backend/database/ -v

# Backend workflow tests
pytest test/integration/backend/workflows/ -v
```

### Run with integration marker:
```bash
pytest -m integration -v
```

## Important Notes

1. **Test Database**: Integration tests use a separate test database to avoid polluting production data
2. **Fixtures**: Shared fixtures are defined in `conftest.py`
3. **Test Data**: Use `TEST_` prefix for test data to avoid conflicts
4. **Cleanup**: Tests should clean up after themselves

## Test Organization

### Backend API Tests (`backend/api/`)
Tests for individual API endpoints:
- `test_api_games.py` - Games API endpoints
- `test_api_events.py` - Events API endpoints
- `test_api_categories.py` - Categories API endpoints

### Backend Database Tests (`backend/database/`)
Tests for database operations and migrations:
- `test_game_gid_migration.py` - Game ID migration tests

### Backend Workflow Tests (`backend/workflows/`)
Tests for complex business workflows:
- `test_create_batch_integration.py` - Batch creation workflow

### Frontend Tests (`frontend/`)
Frontend integration tests (to be implemented)

## Writing New Integration Tests

1. Place the test file in the appropriate subdirectory
2. Use `@pytest.mark.integration` decorator
3. Use fixtures from `conftest.py` when possible
4. Clean up test data after tests
5. Follow the project coding standards

Example:
```python
import pytest

@pytest.mark.integration
class TestMyFeature:
    """Test my feature integration"""

    def test_feature_works(self, integration_client):
        """Test that feature works end-to-end"""
        response = integration_client.get('/api/endpoint')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
```
