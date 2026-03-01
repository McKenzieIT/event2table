# Phase 3 Migration - Test Commands Reference

This document contains all test commands used to verify the Phase 3 migration for Join Configs and Event Categories modules.

## Prerequisites

```bash
# Activate virtual environment
source backend/venv/bin/activate

# Start Flask application (if not running)
python3 web_app.py
```

---

## 1. Integration Tests

### Join Configs Module

```bash
# Run all Join Config integration tests
pytest backend/test/integration/test_join_config_module_integration.py -v

# Run specific test
pytest backend/test/integration/test_join_config_module_integration.py::TestJoinConfigModuleIntegration::test_create_join_config_flow -v

# Run with coverage
pytest backend/test/integration/test_join_config_module_integration.py --cov=backend/services/join_configs --cov-report=html
```

### Event Categories Module

```bash
# Run all Category integration tests
pytest backend/test/integration/test_category_module_integration.py -v

# Run specific test
pytest backend/test/integration/test_category_module_integration.py::TestCategoryModuleIntegration::test_create_category_flow -v

# Run with coverage
pytest backend/test/integration/test_category_module_integration.py --cov=backend/services/event_categories --cov-report=html
```

### Combined Tests

```bash
# Run both modules together
pytest backend/test/integration/test_join_config_module_integration.py backend/test/integration/test_category_module_integration.py -v

# Run all integration tests
pytest backend/test/integration/ -v -k "join_config or category"
```

---

## 2. API Endpoint Tests

### Join Configs API

```bash
# List all join configs
curl "http://127.0.0.1:5001/api/join-configs?game_gid=10000147"

# Get specific join config
curl "http://127.0.0.1:5001/api/join-configs/1"

# Create new join config
curl -X POST "http://127.0.0.1:5001/api/join-configs?game_gid=10000147" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test_config",
    "display_name": "Test Config",
    "join_type": "union_all",
    "source_events": [1, 2],
    "output_fields": ["field1", "field2"],
    "output_table": "dwd.test_output",
    "game_gid": 10000147
  }'

# Update join config
curl -X PUT "http://127.0.0.1:5001/api/join-configs/1?game_gid=10000147" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "updated_config",
    "display_name": "Updated Config"
  }'

# Delete join config
curl -X DELETE "http://127.0.0.1:5001/api/join-configs/1?game_gid=10000147"
```

### Event Categories API

```bash
# List all categories
curl "http://127.0.0.1:5001/api/categories?game_gid=10000147"

# Get specific category
curl "http://127.0.0.1:5001/api/categories/63"

# Create new category
curl -X POST "http://127.0.0.1:5001/api/categories?game_gid=10000147" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Category",
    "description": "Test description",
    "color": "#FF0000",
    "icon": "test-icon",
    "is_active": true,
    "display_order": 100
  }'

# Update category
curl -X PUT "http://127.0.0.1:5001/api/categories/63?game_gid=10000147" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Category",
    "description": "Updated description"
  }'

# Delete category
curl -X DELETE "http://127.0.0.1:5001/api/categories/63?game_gid=10000147"

# Get statistics (NOT IMPLEMENTED - returns 404)
curl "http://127.0.0.1:5001/api/categories/stats?game_gid=10000147"

# Batch delete (NOT IMPLEMENTED - returns 404)
curl -X POST "http://127.0.0.1:5001/api/categories/batch-delete?game_gid=10000147" \
  -H "Content-Type: application/json" \
  -d '{"category_ids": [1, 2]}'
```

---

## 3. Cache Behavior Tests

```bash
# Test 1: First request (should be MISS)
curl -i "http://127.0.0.1:5001/api/categories?game_gid=10000147" 2>&1 | grep -i "x-cache-status"

# Test 2: Second request (should be HIT)
curl -i "http://127.0.0.1:5001/api/categories?game_gid=10000147" 2>&1 | grep -i "x-cache-status"

# Test 3: Create category (invalidates cache)
curl -X POST "http://127.0.0.1:5001/api/categories?game_gid=10000147" \
  -H "Content-Type: application/json" \
  -d '{"name": "Cache Test"}' > /dev/null

# Test 4: Request after invalidation (should be MISS)
curl -i "http://127.0.0.1:5001/api/categories?game_gid=10000147" 2>&1 | grep -i "x-cache-status"

# Test 5: Join Configs cache test
curl -i "http://127.0.0.1:5001/api/join-configs?game_gid=10000147" 2>&1 | grep -i "x-cache-status"
```

---

## 4. Database Schema Tests

```bash
# Check event_categories table schema
sqlite3 data/dwd_generator.db "PRAGMA table_info(event_categories);"

# Check join_configs table schema
sqlite3 data/dwd_generator.db "PRAGMA table_info(join_configs);"

# Verify new columns exist
sqlite3 data/dwd_generator.db "SELECT sql FROM sqlite_master WHERE name='event_categories';"
sqlite3 data/dwd_generator.db "SELECT sql FROM sqlite_master WHERE name='join_configs';"

# Check data integrity
sqlite3 data/dwd_generator.db "SELECT COUNT(*) FROM event_categories;"
sqlite3 data/dwd_generator.db "SELECT COUNT(*) FROM join_configs;"

# Verify new fields have defaults
sqlite3 data/dwd_generator.db "SELECT id, name, game_gid, is_active, display_order FROM event_categories LIMIT 5;"
sqlite3 data/dwd_generator.db "SELECT id, name, game_gid FROM join_configs LIMIT 5;"
```

---

## 5. JSON Serialization Tests

```python
#!/usr/bin/env python3
"""Test JSON serialization for Entities"""

import sys
sys.path.insert(0, '/Users/mckenzie/Documents/event2table')

from backend.models.entities import JoinConfigEntity, EventCategoryEntity

# Test 1: JoinConfigEntity
join_config = JoinConfigEntity(
    name="test",
    display_name="Test",
    join_type="union_all",
    game_gid=10000147,
    source_events=[1, 2, 3],
    join_conditions={"left": "user_id", "right": "account_id"},
    output_fields=["field1", "field2"],
    output_table="dwd.test"
)

# Serialize
data = join_config.model_dump()
print("Serialized:", data)

# Deserialize
join_config2 = JoinConfigEntity(**data)
print("Deserialized:", join_config2)

# Test 2: EventCategoryEntity
category = EventCategoryEntity(
    name="Test Category",
    game_gid=10000147,
    is_active=True,
    display_order=100
)

# Serialize
data = category.model_dump()
print("Serialized:", data)

# Deserialize
category2 = EventCategoryEntity(**data)
print("Deserialized:", category2)
```

---

## 6. Performance Tests

```bash
# Benchmark: List categories (100 requests)
for i in {1..100}; do
  curl -s "http://127.0.0.1:5001/api/categories?game_gid=10000147" > /dev/null
done
echo "Completed 100 requests"

# Benchmark: List join configs (100 requests)
for i in {1..100}; do
  curl -s "http://127.0.0.1:5001/api/join-configs?game_gid=10000147" > /dev/null
done
echo "Completed 100 requests"

# Time individual requests
time curl -s "http://127.0.0.1:5001/api/categories?game_gid=10000147" > /dev/null
time curl -s "http://127.0.0.1:5001/api/join-configs?game_gid=10000147" > /dev/null
```

---

## 7. Error Handling Tests

```bash
# Test 404 - Non-existent join config
curl "http://127.0.0.1:5001/api/join-configs/99999"

# Test 404 - Non-existent category
curl "http://127.0.0.1:5001/api/categories/99999"

# Test validation - Missing required fields
curl -X POST "http://127.0.0.1:5001/api/join-configs?game_gid=10000147" \
  -H "Content-Type: application/json" \
  -d '{"name": "incomplete"}'

# Test validation - Invalid data
curl -X POST "http://127.0.0.1:5001/api/categories?game_gid=10000147" \
  -H "Content-Type: application/json" \
  -d '{"invalid": "data"}'
```

---

## 8. Full Test Suite

```bash
# Run all tests for Phase 3
pytest backend/test/integration/test_join_config_module_integration.py \
      backend/test/integration/test_category_module_integration.py \
      backend/test/integration/api/test_api_categories.py \
      -v --tb=short

# Run with coverage report
pytest backend/test/integration/ -k "join_config or category" \
  --cov=backend/services/join_configs \
  --cov=backend/services/event_categories \
  --cov-report=html \
  --cov-report=term

# Run with detailed output
pytest backend/test/integration/ -k "join_config or category" \
  -vv -s --tb=long
```

---

## 9. Manual Verification Checklist

```bash
# ✓ Verify Flask application is running
curl -s http://127.0.0.1:5001/api/health || echo "Flask not running"

# ✓ Verify database exists
ls -lh data/dwd_generator.db

# ✓ Verify test database exists
ls -lh data/test_database.db

# ✓ Verify no Python errors in logs
tail -100 logs/flask.log | grep -i "error" || echo "No errors found"

# ✓ Verify cache is running
redis-cli ping || echo "Redis not running"

# ✓ Verify cache stats
curl -s "http://127.0.0.1:5001/api/cache/stats"
```

---

## 10. Cleanup and Reset

```bash
# Clean up test data
sqlite3 data/dwd_generator.db "DELETE FROM event_categories WHERE id > 70;"
sqlite3 data/dwd_generator.db "DELETE FROM join_configs WHERE id > 10;"

# Clear cache
redis-cli FLUSHALL

# Restart Flask application
pkill -f "python3 web_app.py"
python3 web_app.py &
```

---

## Test Results Summary

After running all tests, you should see:

```
Integration Tests:
✅ 11/11 Join Config tests passed
✅ 14/14 Category tests passed

API Endpoints:
✅ GET /api/join-configs - Working
✅ POST /api/join-configs - Working
✅ GET /api/join-configs/<id> - Working
✅ PUT /api/join-configs/<id> - Working
✅ DELETE /api/join-configs/<id> - Working
✅ GET /api/categories - Working
✅ POST /api/categories - Working
✅ GET /api/categories/<id> - Working
✅ PUT /api/categories/<id> - Working
✅ DELETE /api/categories/<id> - Working
⚠️ GET /api/categories/stats - Not implemented
⚠️ POST /api/categories/batch-delete - Not implemented

Database Schema:
✅ event_categories table updated
✅ join_configs table updated
✅ New columns present

Cache Behavior:
✅ Caching working internally
⚠️ Cache headers not visible

Overall: ✅ 25/25 integration tests passed
```

---

**Last Updated**: 2026-03-01
**Test Suite Version**: 1.0
**Maintained By**: Event2Table Development Team
