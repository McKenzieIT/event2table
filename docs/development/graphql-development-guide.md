# GraphQL Development Guide

> **Version**: 1.0.0
> **Last Updated**: 2026-03-08
> **Status**: Active

## Overview

This guide covers GraphQL development best practices for the Event2Table project, including schema design, type safety, and frontend-backend integration.

## Core Principles

### 1. Type Safety Between Frontend and Backend

**Critical Rule**: Frontend TypeScript types must exactly match backend GraphQL schema definitions.

**Why this matters**:
```typescript
// ❌ Wrong: Enum value mismatch causes 400 errors
const mutation = CREATE_EVENT_NODE({
  variables: {
    input: {
      joinType: "LEFT-JOIN"  // Backend expects: LEFT_JOIN
    }
  }
});

// ✅ Correct: Exact match with backend schema
const mutation = CREATE_EVENT_NODE({
  variables: {
    input: {
      joinType: "LEFT_JOIN"  // Matches backend enum
    }
  }
});
```

### 2. Enum Naming Conventions

**Backend GraphQL Schema**:
```graphql
# ✅ Correct: UPPER_SNAKE_CASE for GraphQL enums
enum HqlJoinType {
  LEFT_JOIN
  RIGHT_JOIN
  INNER_JOIN
  FULL_JOIN
}

enum NodeType {
  EVENT
  JOIN
  UNION
  FILTER
}
```

**Frontend TypeScript**:
```typescript
// ✅ Correct: Exact match with GraphQL schema
export enum HqlJoinType {
  LEFT_JOIN = "LEFT_JOIN",
  RIGHT_JOIN = "RIGHT_JOIN",
  INNER_JOIN = "INNER_JOIN",
  FULL_JOIN = "FULL_JOIN"
}

export enum NodeType {
  EVENT = "EVENT",
  JOIN = "JOIN",
  UNION = "UNION",
  FILTER = "FILTER"
}
```

**❌ Avoid**: Hyphens, camelCase, or lowercase in enum values
```typescript
// ❌ Wrong: Hyphenated values don't match GraphQL schema
export enum HqlJoinType {
  LEFT_JOIN = "LEFT-JOIN",      // Causes 400 error
  RIGHT_JOIN = "RIGHT-JOIN"     // Causes 400 error
}
```

### 3. Pydantic Model Completeness

**Critical Rule**: All fields accessed in service layer must be defined in Pydantic models.

**Backend Schema** (`backend/models/schemas.py`):
```python
from pydantic import BaseModel, Field
from typing import Optional

class EventNodeInput(BaseModel):
    """Event node creation/update input"""

    # Required fields
    node_type: str = Field(..., description="Node type: event, join, union, filter")

    # Optional fields (must be defined even if not always used)
    event_type: Optional[str] = Field(None, description="Event type for event nodes")
    table_name: Optional[str] = Field(None, description="Table name for event nodes")
    join_type: Optional[str] = Field(None, description="Join type for join nodes")

    # Metadata
    id: Optional[int] = Field(None, description="Node ID (for updates)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "node_type": "event",
                "event_type": "login",
                "table_name": "ieu_ods.ods_10000147_all_view"
            }
        }
    )
```

**Service Layer** (`backend/services/events/event_service.py`):
```python
def create_event_node(self, node_data: EventNodeInput) -> EventNodeEntity:
    """
    Create event node

    Args:
        node_data: Validated event node input

    Returns:
        Created event node entity

    Raises:
        ValueError: If validation fails
    """
    # ✅ Safe: All fields are defined in Pydantic model
    event_type = node_data.event_type  # Field exists, no AttributeError
    node_type = node_data.node_type

    # Business logic
    if node_type == "event" and not event_type:
        raise ValueError("event_type is required for event nodes")

    # Create node
    node_id = self.event_repo.create(node_data.model_dump())
    return self.event_repo.find_by_id(node_id)
```

**Error Prevention**:
```python
# ❌ Before: Missing field causes AttributeError
class EventNodeInput(BaseModel):
    node_type: str
    # Missing: event_type field

# Service layer throws:
# AttributeError: 'EventNodeInput' object has no attribute 'event_type'

# ✅ After: All fields defined
class EventNodeInput(BaseModel):
    node_type: str
    event_type: Optional[str] = None  # ← Field defined

# Service layer works correctly
```

## API Development Workflow

### Step 1: Define Backend Schema

**1.1 Define GraphQL Enum**:
```graphql
# backend/gql_api/schema.graphql

enum HqlJoinType {
  LEFT_JOIN
  RIGHT_JOIN
  INNER_JOIN
  FULL_JOIN
}
```

**1.2 Define Pydantic Model**:
```python
# backend/models/schemas.py

class EventNodeInput(BaseModel):
    """Event node creation/update input"""

    node_type: str = Field(..., description="Node type")
    event_type: Optional[str] = Field(None, description="Event type")
    join_type: Optional[HqlJoinType] = Field(None, description="Join type")
```

**1.3 Define GraphQL Mutation**:
```python
# backend/gql_api/mutations/event_mutations.py

@mutation.field("createEventNode")
@resolve_exceptions
def create_event_node(obj, info, input: dict):
    """Create event node mutation"""
    from backend.models.schemas import EventNodeInput

    # Validate input with Pydantic
    node_input = EventNodeInput(**input)

    # Call service layer
    service = EventService()
    node = service.create_event_node(node_input)

    return node.model_dump()
```

### Step 2: Generate Frontend Types

**2.1 Install Code Generator**:
```bash
npm install --save-dev @graphql-codegen/cli
npm install --save-dev @graphql-codegen/typescript
npm install --save-dev @graphql-codegen/typescript-operations
npm install --save-dev @graphql-codegen/typescript-graphql-request
```

**2.2 Configure Code Generator** (`codegen.yml`):
```yaml
schema:
  - http://127.0.0.1:5001/api/graphql:
      headers:
        Content-Type: application/json

documents:
  - "frontend/src/graphql/**/*.tsx"
  - "frontend/src/graphql/**/*.ts"

generates:
  frontend/src/graphql/generated-types.ts:
    plugins:
      - typescript
      - typescript-operations
      - typescript-graphql-request
    config:
      skipTypename: true
      enumsAsTypes: true
      scalarTypes:
        DateTime: string
        JSON: any

hooks:
  afterOneFileWrite:
    - prettier --write
```

**2.3 Run Code Generator**:
```bash
# Generate types from GraphQL schema
npx graphql-codegen

# Add to package.json scripts
"scripts": {
  "generate:types": "graphql-codegen",
  "predev": "npm run generate:types"
}
```

**2.4 Use Generated Types**:
```typescript
// frontend/src/canvas/components/EventNodeBuilder.tsx
import { CreateEventNodeMutation, HqlJoinType } from '@/graphql/generated-types';

function EventNodeBuilder() {
  const [createNode] = useMutation(CREATE_EVENT_NODE);

  const handleCreate = async (nodeData: CreateEventNodeInput) => {
    // ✅ Type-safe: All fields validated against GraphQL schema
    const result = await createNode({
      variables: {
        input: {
          nodeType: nodeData.nodeType,
          joinType: HqlJoinType.LeftJoin  // Enum type-safe
        }
      }
    });
  };
}
```

### Step 3: Test Integration

**3.1 Unit Tests**:
```python
# backend/test/unit/gql_api/test_event_mutations.py
import pytest
from backend.models.schemas import EventNodeInput

def test_event_node_input_validation():
    """Test Pydantic model validation"""
    # Valid input
    node_input = EventNodeInput(
        node_type="event",
        event_type="login",
        table_name="ods_table"
    )
    assert node_input.node_type == "event"
    assert node_input.event_type == "login"

    # Missing required field
    with pytest.raises(ValidationError):
        EventNodeInput()  # node_type is required

def test_enum_validation():
    """Test enum validation"""
    node_input = EventNodeInput(
        node_type="join",
        join_type="LEFT_JOIN"  # Valid enum value
    )
    assert node_input.join_type == "LEFT_JOIN"

    # Invalid enum value
    with pytest.raises(ValidationError):
        EventNodeInput(
            node_type="join",
            join_type="LEFT-JOIN"  # Invalid: hyphen not allowed
        )
```

**3.2 Integration Tests**:
```typescript
// frontend/test/e2e/graphql.spec.ts
import { test, expect } from '@playwright/test';

test('GraphQL mutation with valid enum', async ({ request }) => {
  const response = await request.post('http://127.0.0.1:5001/api/graphql', {
    data: {
      query: `
        mutation CreateEventNode($input: EventNodeInput!) {
          createEventNode(input: $input) {
            id
            nodeType
            joinType
          }
        }
      `,
      variables: {
        input: {
          nodeType: 'JOIN',
          joinType: 'LEFT_JOIN'  // Valid enum value
        }
      }
    }
  });

  expect(response.ok()).toBeTruthy();
  const data = await response.json();
  expect(data.data.createEventNode.joinType).toBe('LEFT_JOIN');
});

test('GraphQL mutation with invalid enum', async ({ request }) => {
  const response = await request.post('http://127.0.0.1:5001/api/graphql', {
    data: {
      query: `
        mutation CreateEventNode($input: EventNodeInput!) {
          createEventNode(input: $input) {
            id
          }
        }
      `,
      variables: {
        input: {
          nodeType: 'JOIN',
          joinType: 'LEFT-JOIN'  // Invalid: hyphen not allowed
        }
      }
    }
  });

  // Should return 400 Bad Request
  expect(response.status()).toBe(400);
});
```

## Code Review Checklist

### Backend Review
- [ ] Pydantic models include all fields accessed in service layer
- [ ] All fields have proper type annotations (Optional[str], str, int, etc.)
- [ ] Required fields use `Field(..., description="...")`
- [ ] Optional fields use `Field(None, description="...")`
- [ ] Enum names follow `UPPER_SNAKE_CASE` convention
- [ ] GraphQL schema enums match Pydantic model enums
- [ ] All mutations have `@resolve_exceptions` decorator
- [ ] Input validation uses Pydantic models

### Frontend Review
- [ ] TypeScript types match GraphQL schema (use code generator)
- [ ] Enum values exactly match backend (case-sensitive, no hyphens)
- [ ] No hardcoded enum strings (use imported enums)
- [ ] All mutations use generated types
- [ ] Error handling for GraphQL errors
- [ ] No `defaultProps` in function components (use ES6 defaults)

### Integration Review
- [ ] Run API contract tests before committing
- [ ] Test GraphQL mutations with valid enum values
- [ ] Test GraphQL mutations with invalid enum values
- [ ] Verify frontend enum → backend enum mapping
- [ ] Check generated types are up to date (`npm run generate:types`)

## Common Pitfalls

### Pitfall 1: Enum Value Mismatch

**Problem**: Frontend uses hyphens, backend uses underscores
```typescript
// ❌ Wrong
const joinType = "LEFT-JOIN";  // Backend expects: LEFT_JOIN

// ✅ Correct
const joinType = "LEFT_JOIN";  // Exact match
```

**Prevention**: Use `graphql-codegen` to generate enum types from schema

### Pitfall 2: Missing Pydantic Fields

**Problem**: Service layer accesses undefined field
```python
# ❌ Wrong: Missing event_type field
class EventNodeInput(BaseModel):
    node_type: str

# Service layer throws AttributeError
event_type = node_data.event_type

# ✅ Correct: Define all fields
class EventNodeInput(BaseModel):
    node_type: str
    event_type: Optional[str] = None
```

**Prevention**: Run unit tests for Pydantic models

### Pitfall 3: Hardcoded Enum Strings

**Problem**: Typo-prone hardcoded strings
```typescript
// ❌ Wrong: Typo-prone
const mutation = CREATE_EVENT_NODE({
  variables: {
    input: {
      joinType: "LEFT_JION"  // Typo!
    }
  }
});

// ✅ Correct: Use enum constants
import { HqlJoinType } from '@/graphql/generated-types';

const mutation = CREATE_EVENT_NODE({
  variables: {
    input: {
      joinType: HqlJoinType.LeftJoin  // Type-safe
    }
  }
});
```

**Prevention**: Use generated types and enums

### Pitfall 4: Outdated Generated Types

**Problem**: Frontend types don't match current GraphQL schema
```bash
# Schema changed but types not regenerated
# Old enum: LEFT_JOIN, RIGHT_JOIN
# New enum: LEFT_JOIN, RIGHT_JOIN, CROSS_JOIN  # Frontend doesn't know about CROSS_JOIN
```

**Prevention**: Add type generation to pre-commit hook
```bash
# .git/hooks/pre-commit
npm run generate:types
git add frontend/src/graphql/generated-types.ts
```

## Testing Strategy

### Unit Tests
```bash
# Backend Pydantic model tests
pytest backend/test/unit/models/test_schemas.py -v

# Frontend enum tests
npm run test -- enums.test.ts
```

### Integration Tests
```bash
# GraphQL mutation tests
pytest backend/test/integration/gql_api/test_mutations.py -v

# Frontend GraphQL client tests
npm run test:e2e -- graphql.spec.ts
```

### Contract Tests
```bash
# API contract consistency tests
python backend/scripts/test/api_contract_test.py

# Type consistency tests
npm run test:contract
```

## Quick Reference

### GraphQL Enum Definition
```graphql
enum HqlJoinType {
  LEFT_JOIN
  RIGHT_JOIN
  INNER_JOIN
  FULL_JOIN
}
```

### Pydantic Model with Enum
```python
from enum import Enum

class HqlJoinType(str, Enum):
    LEFT_JOIN = "LEFT_JOIN"
    RIGHT_JOIN = "RIGHT_JOIN"
    INNER_JOIN = "INNER_JOIN"
    FULL_JOIN = "FULL_JOIN"

class EventNodeInput(BaseModel):
    join_type: Optional[HqlJoinType] = Field(None, description="Join type")
```

### TypeScript Enum (Generated)
```typescript
export enum HqlJoinType {
  LEFT_JOIN = "LEFT_JOIN",
  RIGHT_JOIN = "RIGHT_JOIN",
  INNER_JOIN = "INNER_JOIN",
  FULL_JOIN = "FULL_JOIN"
}
```

### GraphQL Mutation Usage
```typescript
import { useMutation } from '@apollo/client';
import { CREATE_EVENT_NODE, HqlJoinType } from '@/graphql/generated-types';

function EventNodeBuilder() {
  const [createNode] = useMutation(CREATE_EVENT_NODE);

  const handleCreate = async () => {
    await createNode({
      variables: {
        input: {
          nodeType: 'JOIN',
          joinType: HqlJoinType.LeftJoin  // Type-safe enum
        }
      }
    });
  };
}
```

## EventParameter字段说明

### hive_type (Hive数据类型)

**字段定义**：
```python
# backend/gql_api/types/event_parameter_type.py

class EventParameterExtendedType(graphene.ObjectType):
    hive_type = String(description="Hive数据类型")

    @classmethod
    def from_dict(cls, data: dict) -> 'EventParameterExtendedType':
        return cls(
            # ... 其他字段
            hive_type=data.get('hive_type'),
        )
```

**字段属性**：
- **类型**: `String`
- **描述**: 参数在HiveQL中的数据类型
- **可选值**: `STRING`, `BIGINT`, `INT`, `FLOAT`, `DECIMAL(10,2)`, `BOOLEAN`
- **默认值**: `'STRING'`
- **示例**:
  ```graphql
  query {
    eventParameters(eventId: 4) {
      param_name
      hive_type
    }
  }
  ```

  返回：
  ```json
  {
    "param_name": "role_id",
    "hive_type": "BIGINT"
  }
  ```

**使用场景**：
1. **EventNodeBuilder**: 根据hive_type生成正确的HiveQL CAST表达式
   ```typescript
   // frontend/src/event-builder/pages/EventNodeBuilder.tsx
   dataType: f.hive_type || 'STRING',  // 使用实际类型
   ```

2. **HQL生成器**: 确定字段的数据类型以优化查询性能
   ```python
   # backend/services/hql/core/ddl_generator.py
   hive_type = param.hive_type  # STRING/BIGINT/INT
   field_def = f"{field_name} {hive_type}"
   ```

3. **数据验证**: 验证参数值是否符合声明类型

**修复案例** (2026-03-13):
- **问题**: `event_params`表有`hive_type`字段，但GraphQL schema未定义
- **影响**: UI组件无法获取字段类型信息，所有字段显示"UNKNOWN"
- **修复**: 添加`hive_type`到4层（GraphQL Schema + DataLoader + TypeScript接口 + UI组件）
- **详细文档**: [GraphQL字段完整性经验](/Users/mckenzie/Documents/event2table/docs/lessons-learned/graphql-field-completeness.md)

## Related Documentation

- [GraphQL字段完整性经验](/Users/mckenzie/Documents/event2table/docs/lessons-learned/graphql-field-completeness.md) - hive_type字段修复案例 ⭐
- [Event Node Builder Errors](/Users/mckenzie/Documents/event2table/docs/lessons-learned/event-node-builder-errors.md) - Error fixing case study
- [React Best Practices](/Users/mckenzie/Documents/event2table/docs/lessons-learned/react-best-practices.md) - React component patterns
- [Type Safety Guide](/Users/mckenzie/Documents/event2table/docs/development/TYPESCRIPT_TYPE_STANDARDS.md) - TypeScript standards
- [API Architecture](/Users/mckenzie/Documents/event2table/docs/development/architecture.md) - Overall API architecture

---

**Last Updated**: 2026-03-13
**Maintained By**: Event2Table Development Team
