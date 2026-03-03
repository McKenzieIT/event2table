# Parameter Management GraphQL API Documentation

> **Version**: 1.0
> **Last Updated**: 2026-02-23
> **Author**: Event2Table Development Team

## Overview

The Parameter Management GraphQL API provides advanced parameter management features including:

- **Parameter Filtering**: Query parameters with filtering modes (all, common, non-common)
- **Common Parameters Detection**: Automatically detect and sync common parameters across events
- **Parameter Type Management**: Change parameter types with validation
- **Event Fields Management**: Get event fields for Canvas node configuration
- **Batch Operations**: Batch add fields to Canvas configurations

---

## GraphQL Endpoint

```
POST /api/graphql
```

### Interactive Playground

```
http://127.0.0.1:5001/api/graphql
```

The GraphiQL interface provides:
- Auto-completion
- Documentation explorer
- Query history
- Real-time validation

---

## Queries

### 1. parametersManagement

Query parameters with filtering and statistics.

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `gameGid` | `Int!` | Yes | Game GID |
| `mode` | `ParameterFilterModeEnum` | No | Filter mode (default: `ALL`) |
| `eventId` | `Int` | No | Optional event ID filter |

#### Filter Modes

- `ALL`: Return all parameters
- `COMMON`: Return only common parameters (appear in >= 50% of events)
- `NON_COMMON`: Return only non-common parameters

#### Example

```graphql
query GetParametersManagement {
  parametersManagement(gameGid: 90000001, mode: ALL) {
    id
    paramName
    paramNameCn
    paramType
    paramDescription
    isCommon
    usageCount
    eventsCount
    eventCode
    eventName
    gameGid
  }
}
```

#### Response

```json
{
  "data": {
    "parametersManagement": [
      {
        "id": 1,
        "paramName": "role_id",
        "paramNameCn": "角色ID",
        "paramType": "int",
        "paramDescription": "Role identifier",
        "isCommon": true,
        "usageCount": 15,
        "eventsCount": 15,
        "eventCode": "login",
        "eventName": "User Login",
        "gameGid": 90000001
      }
    ]
  }
}
```

---

### 2. commonParameters

Query common parameters with occurrence statistics.

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `gameGid` | `Int!` | Yes | Game GID |
| `threshold` | `Float` | No | Commonality threshold 0-1 (default: 0.5) |

#### Example

```graphql
query GetCommonParameters {
  commonParameters(gameGid: 90000001, threshold: 0.5) {
    paramName
    paramType
    paramDescription
    occurrenceCount
    totalEvents
    threshold
    eventCodes
    isCommon
    commonalityScore
  }
}
```

#### Response

```json
{
  "data": {
    "commonParameters": [
      {
        "paramName": "role_id",
        "paramType": "int",
        "paramDescription": "Role identifier",
        "occurrenceCount": 15,
        "totalEvents": 20,
        "threshold": 0.5,
        "eventCodes": ["login", "logout", "level_up"],
        "isCommon": true,
        "commonalityScore": 0.75
      }
    ]
  }
}
```

---

### 3. parameterChanges

Query parameter change history (placeholder - not yet implemented).

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `gameGid` | `Int!` | Yes | Game GID |
| `parameterId` | `Int` | No | Optional parameter ID filter |
| `limit` | `Int` | No | Result limit (default: 50) |

#### Example

```graphql
query GetParameterChanges {
  parameterChanges(gameGid: 90000001, limit: 10) {
    id
    parameterId
    paramName
    changeType
    oldValue
    newValue
    changedField
    changedAt
    changedBy
  }
}
```

#### Note

> **⚠️ This query is a placeholder**. The `parameter_changes` table is not yet implemented. Returns empty list.

---

### 4. eventFields

Query event fields for EventBuilder/Canvas configuration.

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `eventId` | `Int!` | Yes | Event ID |
| `fieldType` | `FieldTypeEnum` | No | Field type filter (default: `ALL`) |

#### Field Types

- `ALL`: All fields (base + params)
- `PARAMS`: Only parameter fields
- `NON-COMMON`: Only non-common parameter fields
- `COMMON`: Only common parameter fields
- `BASE`: Only base fields

#### Example

```graphql
query GetEventFields {
  eventFields(eventId: 1, fieldType: ALL) {
    name
    displayName
    type
    category
    isCommon
    dataType
    jsonPath
    usageCount
  }
}
```

#### Response

```json
{
  "data": {
    "eventFields": [
      {
        "name": "ds",
        "displayName": "日期分区",
        "type": "BASE",
        "category": "base",
        "isCommon": true,
        "dataType": "string",
        "jsonPath": null,
        "usageCount": 0
      },
      {
        "name": "role_id",
        "displayName": "Role identifier",
        "type": "PARAMS",
        "category": "common",
        "isCommon": true,
        "dataType": "int",
        "jsonPath": "$.roleId",
        "usageCount": 0
      }
    ]
  }
}
```

---

## Mutations

### 1. changeParameterType

Change the data type of an existing parameter.

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `parameterId` | `Int!` | Yes | Parameter ID |
| `newType` | `ParameterTypeEnum!` | Yes | New parameter type |

#### Parameter Types

- `INT`: Integer
- `STRING`: String
- `ARRAY`: Array
- `BOOLEAN`: Boolean
- `MAP`: Map/Object

#### Example

```graphql
mutation ChangeParameterType {
  changeParameterType(parameterId: 1, newType: STRING) {
    success
    message
    parameter {
      id
      paramName
      paramType
    }
  }
}
```

#### Response

```json
{
  "data": {
    "changeParameterType": {
      "success": true,
      "message": "Parameter type changed to string",
      "parameter": {
        "id": 1,
        "paramName": "role_id",
        "paramType": "string"
      }
    }
  }
}
```

#### Error Handling

- **Parameter not found**: Returns `success: false` with error message
- **Invalid type**: Returns GraphQL error
- **Type change validation failed**: Returns GraphQL error

---

### 2. autoSyncCommonParameters

Automatically detect and sync common parameters for a game.

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `gameGid` | `Int!` | Yes | Game GID |
| `forceRecalculate` | `Boolean` | No | Force recalculation (default: false) |

#### Example

```graphql
mutation AutoSyncCommonParameters {
  autoSyncCommonParameters(gameGid: 90000001, forceRecalculate: false) {
    success
    message
    result {
      gameGid
      totalParameters
      commonParametersCount
      previousCommonCount
      thresholdUsed
      calculationDurationMs
      parametersAdded
      parametersRemoved
    }
  }
}
```

#### Response

```json
{
  "data": {
    "autoSyncCommonParameters": {
      "success": true,
      "message": "Common parameters already up to date",
      "result": {
        "gameGid": 90000001,
        "totalParameters": 150,
        "commonParametersCount": 25,
        "previousCommonCount": 25,
        "thresholdUsed": 0.8,
        "calculationDurationMs": 45.2,
        "parametersAdded": [],
        "parametersRemoved": []
      }
    }
  }
}
```

#### Error Handling

- **Invalid game_gid**: Returns GraphQL error
- **No events found**: Returns `success: false` with error message

---

### 3. batchAddFieldsToCanvas

Batch add fields to a Canvas node configuration.

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `eventId` | `Int!` | Yes | Event ID |
| `fieldType` | `FieldTypeEnum!` | Yes | Field type to add |

#### Example

```graphql
mutation BatchAddFieldsToCanvas {
  batchAddFieldsToCanvas(eventId: 1, fieldType: ALL) {
    success
    message
    result {
      totalCount
      successCount
      failedCount
      errors
    }
  }
}
```

#### Response

```json
{
  "data": {
    "batchAddFieldsToCanvas": {
      "success": true,
      "message": "成功添加 25 个字段",
      "result": {
        "totalCount": 25,
        "successCount": 25,
        "failedCount": 0,
        "errors": []
      }
    }
  }
}
```

#### Error Handling

- **Invalid event_id**: Returns GraphQL error
- **Invalid field_type**: Returns GraphQL error
- **No fields found**: Returns `success: false` with error message

---

## Enums

### ParameterFilterModeEnum

```graphql
enum ParameterFilterModeEnum {
  ALL
  COMMON
  NON_COMMON
}
```

### FieldTypeEnum

```graphql
enum FieldTypeEnum {
  ALL
  PARAMS
  NON-COMMON
  COMMON
  BASE
}
```

### ParameterTypeEnum

```graphql
enum ParameterTypeEnum {
  INT
  STRING
  ARRAY
  BOOLEAN
  MAP
}
```

---

## Error Handling

All mutations and queries follow GraphQL error handling conventions:

### GraphQL Errors

Returned for:
- Invalid input validation
- Authentication/authorization failures
- Schema violations

Format:

```json
{
  "errors": [
    {
      "message": "Invalid mode: INVALID. Must be one of: all, common, non_common",
      "path": ["parametersManagement"]
    }
  ]
}
```

### Business Logic Errors

Returned in mutation response for:
- Resource not found
- Business rule violations

Format:

```json
{
  "data": {
    "changeParameterType": {
      "success": false,
      "message": "Parameter not found: 999999",
      "parameter": null
    }
  }
}
```

---

## Best Practices

### 1. Use Specific Field Selection

❌ **Bad** - Fetches all fields:
```graphql
query {
  parametersManagement(gameGid: 90000001, mode: ALL) {
    id
    paramName
    # ... many more fields
  }
}
```

✅ **Good** - Fetches only needed fields:
```graphql
query {
  parametersManagement(gameGid: 90000001, mode: ALL) {
    id
    paramName
    paramType
  }
}
```

### 2. Use Aliases for Multiple Queries

```graphql
query {
  allParams: parametersManagement(gameGid: 90000001, mode: ALL) {
    id
    paramName
  }
  commonParams: parametersManagement(gameGid: 90000001, mode: COMMON) {
    id
    paramName
  }
}
```

### 3. Handle Errors Gracefully

Always check for errors in response:

```javascript
const response = await graphql(query, variables);

if (response.errors) {
  console.error('GraphQL errors:', response.errors);
  // Handle errors
} else {
  const data = response.data;
  // Process data
}
```

### 4. Use Fragments for Reusable Fields

```graphql
fragment ParameterFields on ParameterManagementType {
  id
  paramName
  paramType
  isCommon
}

query {
  parametersManagement(gameGid: 90000001, mode: ALL) {
    ...ParameterFields
  }
}
```

---

## Testing

### Run Integration Tests

```bash
# Backend integration tests
pytest backend/tests/integration/gql_api/test_parameter_resolvers.py -v

# With coverage
pytest backend/tests/integration/gql_api/test_parameter_resolvers.py --cov=backend/gql_api --cov-report=html
```

### Test Data

- **Test Database**: `data/test_database.db`
- **Test GID Range**: 90000000+ (avoids STAR001 conflict)
- **STAR001 Protection**: Never use GID 10000147 in tests

---

## Performance Considerations

### Query Complexity

- Default complexity limit: 1000
- Default depth limit: 10
- Use pagination for large datasets

### Caching

- Common parameters are cached (TTL: 1 hour)
- Use `forceRecalculate: true` to bypass cache
- Cache is invalidated on parameter changes

### Database Queries

- `parameters_management`: Single query with JOINs
- `common_parameters`: Two queries (count + aggregation)
- `event_fields`: One query + base fields in memory

---

## Future Enhancements

### Planned Features

1. **Parameter Changes Tracking**
   - Implement `parameter_changes` table
   - Track all parameter modifications
   - Audit trail with user attribution

2. **Advanced Filtering**
   - Filter by parameter name pattern
   - Filter by date range
   - Multi-event filtering

3. **Batch Operations**
   - Batch type changes
   - Batch parameter deletion
   - Batch parameter updates

4. **Real-time Updates**
   - GraphQL subscriptions for parameter changes
   - WebSocket integration
   - Live canvas updates

---

## Support

For issues or questions:

1. Check the [GraphiQL Explorer](http://127.0.0.1:5001/api/graphql)
2. Review integration tests: `backend/tests/integration/gql_api/test_parameter_resolvers.py`
3. Check application logs: `logs/flask_app.log`

---

## Changelog

### Version 1.0 (2026-02-23)

- ✅ Initial implementation
- ✅ 4 query resolvers
- ✅ 3 mutation resolvers
- ✅ Integration tests
- ✅ Complete documentation
