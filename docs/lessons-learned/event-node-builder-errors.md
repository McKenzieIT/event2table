# Event Node Builder Error Fixing Experience

> **Date**: 2026-03-08
> **Category**: Frontend Debugging, GraphQL Type Safety
> **Severity**: P0 - Critical bugs blocking user workflows

## Problem Overview

During the event node builder feature testing, we encountered three critical issues that prevented users from creating and configuring event nodes:

1. **API 500 Error** - Internal server error when creating event nodes
2. **GraphQL 400 Error** - Bad request due to enum value mismatch
3. **React defaultProps Warning** - Deprecated feature usage in React 18+

### Error Messages

**1. API 500 Error:**
```
[API] POST /api/events/nodes - 500 Internal Server Error
Error: 'EventNodeInput' object has no attribute 'event_type'
```

**2. GraphQL 400 Error:**
```
[GraphQL] createEventNode mutation - 400 Bad Request
Error: Enum 'HqlJoinType' cannot represent value: 'LEFT-JOIN'
Expected: LEFT_JOIN, RIGHT_JOIN, INNER_JOIN, FULL_JOIN
```

**3. React Warning:**
```
[Warning] defaultProps: Support for defaultProps will be removed from function components in a future major release.
See https://react.dev/link/defaultprops
```

## Root Cause Analysis

### Issue 1: Missing Attribute in Pydantic Model

**Root Cause**: The `EventNodeInput` Pydantic model was missing the `event_type` field that was being accessed in the service layer.

**Code Location**: `backend/models/schemas.py`

```python
# ❌ Before: Missing event_type field
class EventNodeInput(BaseModel):
    id: Optional[int] = None
    node_type: str
    table_name: Optional[str] = None
    # Missing: event_type field

# ✅ After: Added event_type field
class EventNodeInput(BaseModel):
    id: Optional[int] = None
    node_type: str
    event_type: Optional[str] = None  # ← Added
    table_name: Optional[str] = None
```

**Why this happened**:
- The service layer was accessing `event_data.event_type`
- The Pydantic model didn't define this field
- AttributeError raised when accessing undefined field

### Issue 2: GraphQL Enum Naming Mismatch

**Root Cause**: Frontend TypeScript enum used hyphens (`LEFT-JOIN`) while backend GraphQL enum used underscores (`LEFT_JOIN`).

**Frontend Code** (`frontend/src/graphql/fragments.ts`):
```typescript
// ❌ Before: Hyphenated enum values
export enum HqlJoinType {
  LEFT_JOIN = "LEFT-JOIN",      // Wrong format
  RIGHT_JOIN = "RIGHT-JOIN",    // Wrong format
  INNER_JOIN = "INNER-JOIN",    // Wrong format
  FULL_JOIN = "FULL-JOIN"       // Wrong format
}
```

**Backend GraphQL Schema**:
```graphql
# ✅ Correct: Underscore format
enum HqlJoinType {
  LEFT_JOIN
  RIGHT_JOIN
  INNER_JOIN
  FULL_JOIN
}
```

**Why this happened**:
- Frontend and backend enum definitions were created independently
- No automated type checking between frontend and backend
- Manual testing didn't catch enum format mismatch

### Issue 3: React 18+ Deprecated defaultProps

**Root Cause**: Using React's deprecated `defaultProps` feature in function components.

**Code Location**: `frontend/src/canvas/components/EventNodeBuilder.tsx`

```typescript
// ❌ Before: Using deprecated defaultProps
interface EventNodeBuilderProps {
  availableEvents?: Event[];
}

function EventNodeBuilder({ availableEvents = [] }: EventNodeBuilderProps) {
  // ...
}

EventNodeBuilder.defaultProps = {
  availableEvents: []  // Deprecated in React 18+
};
```

**Why this happened**:
- Code was written using older React patterns
- Team not aware of React 18+ changes
- No linting rules to detect deprecated features

## Fixing Steps

### Step 1: Fix Missing Pydantic Field

**File**: `backend/models/schemas.py`

```python
# Add event_type field to EventNodeInput
class EventNodeInput(BaseModel):
    """Event node creation/update input"""

    id: Optional[int] = None
    node_type: str = Field(..., description="Node type: 'event', 'join', 'union', 'filter'")
    event_type: Optional[str] = Field(None, description="Event type for event nodes")  # ← Added
    table_name: Optional[str] = Field(None, description="Table name for event nodes")
    # ... other fields
```

**Verification**:
```bash
# Run pytest tests
pytest backend/test/unit/models/test_schemas.py -v

# Check API endpoint
curl -X POST http://127.0.0.1:5001/api/events/nodes \
  -H "Content-Type: application/json" \
  -d '{"node_type": "event", "event_type": "login", "table_name": "ods_table"}'
```

### Step 2: Align GraphQL Enum Naming

**File**: `frontend/src/graphql/fragments.ts`

```typescript
// ✅ After: Aligned with backend GraphQL schema
export enum HqlJoinType {
  LEFT_JOIN = "LEFT_JOIN",
  RIGHT_JOIN = "RIGHT_JOIN",
  INNER_JOIN = "INNER_JOIN",
  FULL_JOIN = "FULL_JOIN"
}

// ✅ Add type-safe mapping function
export function toHqlJoinType(value: string): HqlJoinType {
  const upperValue = value.toUpperCase().replace('-', '_');
  if (upperValue in HqlJoinType) {
    return upperValue as HqlJoinType;
  }
  throw new Error(`Invalid HqlJoinType: ${value}`);
}
```

**Verification**:
```bash
# Test GraphQL mutation
curl -X POST http://127.0.0.1:5001/api/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { createEventNode(input: { nodeType: \"join\", joinType: LEFT_JOIN }) { id } }"
  }'
```

### Step 3: Replace defaultProps with ES6 Defaults

**File**: `frontend/src/canvas/components/EventNodeBuilder.tsx`

```typescript
// ✅ After: Using ES6 default parameters
interface EventNodeBuilderProps {
  availableEvents?: Event[];
}

function EventNodeBuilder({
  availableEvents = []  // ← ES6 default parameter
}: EventNodeBuilderProps) {
  // Component logic
}

// Remove deprecated defaultProps
// EventNodeBuilder.defaultProps = { ... }  // ← Removed
```

**Verification**:
```bash
# Check React console for warnings
npm run dev
# Open browser DevTools → Console
# Should see no defaultProps warnings
```

## Prevention Measures

### 1. Type Safety Between Frontend and Backend

**Automated Type Generation**:
```bash
# Install graphql-code-generator
npm install --save-dev @graphql-codegen/cli
npm install --save-dev @graphql-codegen/typescript
npm install --save-dev @graphql-codegen/typescript-operations

# Generate TypeScript types from GraphQL schema
npx graphql-codegen
```

**Configuration** (`codegen.yml`):
```yaml
schema: http://127.0.0.1:5001/api/graphql
documents: "frontend/src/graphql/**/*.tsx"
generates:
  frontend/src/graphql/generated-types.ts:
    plugins:
      - typescript
      - typescript-operations
```

### 2. API Contract Testing

**Add to Pre-commit Hook**:
```bash
# .git/hooks/pre-commit
python backend/scripts/test/api_contract_test.py
```

**Test Script** (`backend/scripts/test/api_contract_test.py`):
```python
def test_graphql_enum_consistency():
    """Test that frontend and backend enums match"""
    backend_enums = extract_graphql_enums()
    frontend_enums = extract_typescript_enums()

    for enum_name, values in backend_enums.items():
        assert enum_name in frontend_enums, f"Missing enum: {enum_name}"
        assert frontend_enums[enum_name] == values, \
            f"Enum mismatch: {enum_name}"
```

### 3. React 18+ Best Practices

**ESLint Rules** (`.eslintrc.js`):
```javascript
module.exports = {
  rules: {
    'react/no-default-props': 'error',  // Prevent defaultProps usage
    'react/no-deprecated': 'error',     // Prevent deprecated features
    'react/function-component-definition': [
      'error',
      {
        namedComponents: 'arrow-function'
      }
    ]
  }
}
```

**Code Review Checklist**:
- [ ] No `defaultProps` in function components
- [ ] Use ES6 default parameters: `function Component({ prop = default })`
- [ ] Use TypeScript for type safety
- [ ] Avoid React lifecycle methods in function components

### 4. Pydantic Model Validation

**Pre-commit Hook**:
```python
# backend/scripts/test/validate_schemas.py
def validate_schema_attributes():
    """Validate all Pydantic models have required fields"""
    schema_file = Path("backend/models/schemas.py")
    content = schema_file.read_text()

    # Extract all Pydantic models
    models = re.findall(r'class (\w+)\(BaseModel\):', content)

    for model in models:
        # Check if model has docstring
        # Check if fields have descriptions
        # Check if required fields are marked with Field(...)
```

## Code Review Checklist

Use this checklist when reviewing event node builder or similar features:

### Backend (GraphQL + Pydantic)
- [ ] Pydantic models include all fields accessed in service layer
- [ ] All fields have proper type annotations
- [ ] Required fields use `Field(..., description="...")`
- [ ] Optional fields use `Field(None, description="...")`
- [ ] Enum names follow `UPPER_SNAKE_CASE` convention
- [ ] GraphQL schema enums match Pydantic model enums

### Frontend (TypeScript + React)
- [ ] TypeScript types match GraphQL schema (use code generator)
- [ ] Enum values exactly match backend (case-sensitive)
- [ ] No `defaultProps` in function components
- [ ] Use ES6 default parameters for default values
- [ ] All props have TypeScript interfaces
- [ ] React 18+ best practices followed

### Integration
- [ ] Run API contract tests before committing
- [ ] Test GraphQL mutations with valid enum values
- [ ] Test GraphQL mutations with invalid enum values (should fail gracefully)
- [ ] Check browser console for React warnings
- [ ] Verify frontend enum → backend enum mapping

## Testing Checklist

### Unit Tests
- [ ] Pydantic model validation tests
- [ ] Enum value conversion tests
- [ ] Service layer error handling tests

### Integration Tests
- [ ] GraphQL mutation with valid inputs
- [ ] GraphQL mutation with invalid enum values
- [ ] API endpoint with missing required fields
- [ ] Frontend component rendering with default props

### E2E Tests
- [ ] Create event node via UI
- [ ] Update event node via UI
- [ ] Delete event node via UI
- [ ] Verify no console errors

## Related Documentation

- [GraphQL Best Practices](/Users/mckenzie/Documents/event2table/docs/api/README.md)
- [React Best Practices](/Users/mckenzie/Documents/event2table/docs/lessons-learned/react-best-practices.md)
- [API Development Guide](/Users/mckenzie/Documents/event2table/docs/development/api-development.md)
- [Type Safety Guide](/Users/mckenzie/Documents/event2table/docs/development/typescript-guide.md)

## Lessons Learned

1. **Type Synchronization is Critical**: Frontend and backend types must stay in sync. Use automated tools like `graphql-code-generator` to prevent drift.

2. **Pydantic Models are Single Source of Truth**: If service layer accesses a field, it must be defined in the Pydantic model. Add validation to catch missing fields early.

3. **React 18+ Changes Matter**: defaultProps is deprecated. Stay updated with React changes and adjust coding patterns accordingly.

4. **Enum Naming Consistency**: Establish and document enum naming conventions (UPPER_SNAKE_CASE for GraphQL/TypeScript). Follow them consistently across frontend and backend.

5. **Test-Driven Development Prevents Bugs**: Writing tests before implementation would have caught the missing `event_type` field and enum mismatch during development, not in production.

## Quick Reference

### Correct Enum Format

```typescript
// ✅ Correct: UPPER_SNAKE_CASE
export enum HqlJoinType {
  LEFT_JOIN = "LEFT_JOIN",
  RIGHT_JOIN = "RIGHT_JOIN",
  INNER_JOIN = "INNER_JOIN",
  FULL_JOIN = "FULL_JOIN"
}
```

### Correct Default Props Pattern

```typescript
// ✅ Correct: ES6 default parameters
interface Props {
  items?: Item[];
  onSelect?: (item: Item) => void;
}

function Component({
  items = [],  // ← Default value
  onSelect
}: Props) {
  // Component logic
}
```

### Correct Pydantic Model

```python
# ✅ Correct: All fields defined with descriptions
class EventNodeInput(BaseModel):
    """Event node creation/update input"""

    id: Optional[int] = Field(None, description="Node ID (for updates)")
    node_type: str = Field(..., description="Node type")
    event_type: Optional[str] = Field(None, description="Event type")

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()}
    )
```

---

**Last Updated**: 2026-03-08
**Maintained By**: Event2Table Development Team
