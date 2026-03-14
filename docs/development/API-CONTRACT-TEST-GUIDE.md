# API Contract Test Guide

> **Last Updated**: 2026-03-08
> **Status**: ✅ All Tests Passing
> **Test Script**: `scripts/test/api_contract_test.py`

## Overview

The API Contract Test Suite validates consistency between frontend and backend API contracts, ensuring that:

1. **GraphQL Enum Consistency** - Frontend and backend enum values match
2. **Backend API Endpoints** - All referenced endpoints exist and are implemented
3. **Parameter Naming Conventions** - Correct use of `game_gid` vs `game_id`
4. **Mutation Parameter Types** - GraphQL mutations use correct parameter types
5. **Type Import Consistency** - Frontend imports types from correct locations

## Quick Start

### Running All Tests

```bash
# Activate virtual environment
source backend/venv/bin/activate

# Run all tests
python scripts/test/api_contract_test.py

# Expected output: ✅ ALL TESTS PASSED
```

### Running Specific Tests

```bash
# Run only GraphQL enum consistency test
python scripts/test/api_contract_test.py --test graphql_enum_consistency

# Run only parameter naming convention test
python scripts/test/api_contract_test.py --test parameter_naming_convention

# Run with verbose output
python scripts/test/api_contract_test.py --verbose
```

## Test Details

### Test 1: GraphQL Enum Consistency

**Purpose**: Verify that frontend TypeScript types match backend GraphQL enum definitions.

**Validates**:
- `FieldOptionType` (frontend) vs `FieldTypeEnum` (backend)
- Filter modes match between frontend and backend
- Enum values use correct format (hyphens for GraphQL compliance)

**Enum Values**:
```typescript
// Frontend (FieldOptionType)
type FieldOptionType = 'all' | 'params' | 'non-common' | 'common' | 'base';
```

```python
# Backend (FieldTypeEnum)
class FieldTypeEnum(Enum):
    ALL = "all"
    PARAMS = "params"
    NON_COMMON = "non-common"  # Note: hyphen, not underscore
    COMMON = "common"
    BASE = "base"
```

**Critical Note**: GraphQL enums MUST use hyphens (`non-common`), not underscores (`non_common`).

### Test 2: Backend API Endpoints Existence

**Purpose**: Verify that all GraphQL mutations and queries referenced by frontend exist in backend.

**Validates**:
- GraphQL schema file exists (`backend/gql_api/schema_parameter_management.py`)
- Critical mutations are defined:
  - `batch_add_fields_to_canvas` (Python) / `batchAddFieldsToCanvas` (GraphQL)
  - `parametersManagement` query
- Enum types are defined:
  - `FieldTypeEnum`
  - `FilterModeEnum`
- Mutation files exist in `backend/gql_api/mutations/`

**Note**: Python backend uses snake_case (`batch_add_fields_to_canvas`), but GraphQL exposes camelCase (`batchAddFieldsToCanvas`).

### Test 3: Parameter Naming Convention (game_gid vs game_id)

**Purpose**: Ensure frontend uses correct parameter names for business logic.

**Validates**:
- Frontend uses `game_gid` for API calls and GraphQL queries
- `game_id` is only used for legitimate database operations (e.g., `fetchGameById`)
- No suspicious uses of `game_id` in API URLs or query parameters

**Legitimate Uses of game_id**:
```typescript
// ✅ OK: Fetching by database ID
export async function fetchGameById(gameId: number): Promise<Game> {
  const response = await fetch(`/api/games/${gameId}`);
  // ...
}
```

**Suspicious Uses of game_id**:
```typescript
// ❌ BAD: Using game_id in API calls for business logic
const response = await fetch(`/api/events?game_id=${gameId}`);
// Should be: game_gid
```

### Test 4: GraphQL Mutation Parameter Types

**Purpose**: Verify that GraphQL mutation parameters match frontend expectations.

**Validates**:
- Backend mutation parameters are correctly defined
- Frontend uses correct parameter names and types
- Required parameters are present on both sides

**Parameter Mapping**:
```python
# Backend (Python - snake_case)
class BatchAddFieldsToCanvasMutation(graphene.Mutation):
    class Arguments:
        event_id = Int(required=True)  # Python uses snake_case
        field_type = Argument(FieldTypeEnum, required=True)
```

```typescript
// Frontend (GraphQL - camelCase)
const [batchAddFields] = useMutation(BATCH_ADD_FIELDS_TO_CANVAS, {
  variables: {
    eventId: 123,        // GraphQL uses camelCase
    fieldType: 'all'     // Enum value
  }
});
```

### Test 5: Type Import Consistency

**Purpose**: Ensure frontend components import and define types correctly.

**Validates**:
- `FieldOptionType` is defined in frontend components
- All required enum values are present
- Types are imported from correct paths

## Current Test Status

✅ **All Tests Passing** (2026-03-08)

```
Total Tests: 5
Passed: 5
Failed: 0

✅ GraphQL Enum Consistency: PASSED
✅ Backend API Endpoints: PASSED
✅ Parameter Naming Convention: PASSED
✅ Mutation Parameter Types: PASSED
✅ Type Import Consistency: PASSED
```

## Troubleshooting

### Test Failures

If tests fail, review the error messages to identify:

1. **Missing enum values**: Add missing values to both frontend and backend
2. **Missing mutations**: Implement missing GraphQL mutations
3. **Parameter mismatches**: Update parameter names to match conventions
4. **Type import errors**: Fix import paths in frontend components

### Common Issues

#### Issue: "GraphQL Mutation not found"

**Cause**: Mutation is defined in Python but not exposed in GraphQL schema.

**Solution**: Add mutation to `ParameterManagementMutations` class:
```python
class ParameterManagementMutations(ObjectType):
    batch_add_fields_to_canvas = BatchAddFieldsToCanvasMutation.Field(
        description="批量添加字段到画布"
    )
```

#### Issue: "Frontend missing parameter"

**Cause**: Frontend mutation call doesn't include required parameters.

**Solution**: Update frontend mutation call:
```typescript
batchAddFields({
  variables: {
    eventId: event.id,
    fieldType: 'all'
  }
})
```

#### Issue: "Suspicious game_id usage"

**Cause**: Using `game_id` instead of `game_gid` in API calls.

**Solution**: Replace `game_id` with `game_gid`:
```typescript
// ❌ Wrong
fetch(`/api/events?game_id=${gameId}`)

// ✅ Correct
fetch(`/api/events?game_gid=${gameGid}`)
```

## Integration with CI/CD

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Run API contract tests before committing

echo "Running API contract tests..."
python scripts/test/api_contract_test.py

if [ $? -ne 0 ]; then
    echo "❌ API contract tests failed. Commit blocked."
    exit 1
fi

echo "✅ API contract tests passed. Proceeding with commit."
```

### GitHub Actions

Add to `.github/workflows/api-contract-test.yml`:
```yaml
name: API Contract Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Run API contract tests
        run: |
          source backend/venv/bin/activate
          python scripts/test/api_contract_test.py
```

## Extending the Test Suite

### Adding New Tests

1. Create a new test function following the naming convention:
   ```python
   def test_new_feature() -> Tuple[bool, List[str]]:
       """Test description"""
       print_header("🧪 Test X: New Feature")
       errors = []

       # Test logic here

       return len(errors) == 0, errors
   ```

2. Add to test list in `run_all_tests()`:
   ```python
   tests = [
       # ... existing tests
       ("New Feature", test_new_feature),
   ]
   ```

3. Add to `--test` argument mapping in `main()`:
   ```python
   test_map = {
       # ... existing tests
       'new_feature': test_new_feature,
   }
   ```

### Adding New Enum Validations

1. Add enum values to test constants:
   ```python
   FRONTEND_NEW_ENUM = ['value1', 'value2']
   BACKEND_NEW_ENUM_VALUES = ['value1', 'value2']
   ```

2. Update `test_graphql_enum_consistency()` to check new enum.

## Best Practices

1. **Run tests before committing**: Always run the full test suite before committing changes
2. **Fix failures immediately**: Don't ignore test failures
3. **Keep tests updated**: Add new tests when adding new API endpoints or types
4. **Use descriptive names**: Use clear, descriptive test names
5. **Document changes**: Update this guide when adding new tests

## Related Documentation

- [CLAUDE.md - Development Workflow](../../CLAUDE.md)
- [GraphQL Schema](../../backend/gql_api/schema_parameter_management.py)
- [Frontend Type Definitions](../../frontend/src/shared/types/)
- [API Development Guide](api-development.md)

## Support

For issues or questions:
1. Check the error message in test output
2. Review this guide's troubleshooting section
3. Check related documentation
4. Ask in team chat or create an issue

---

**Maintained by**: Event2Table Development Team
**Last Review**: 2026-03-08
**Next Review**: 2026-03-15
