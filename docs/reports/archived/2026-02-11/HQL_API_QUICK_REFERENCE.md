# HQL Generation API - Quick Reference Card

## Base Endpoint
```
POST http://localhost:5001/hql-preview-v2/api/generate
```

---

## Supported Request Formats

### Format 1: Standard (Recommended)
Each event contains its own `game_gid` and `event_id`:

```json
{
  "events": [
    {
      "game_gid": 10000147,
      "event_id": 1
    }
  ],
  "fields": [...],
  "options": {...}
}
```

### Format 2: Top-Level game_gid (Backward Compatible)
`game_gid` at top level is merged into all events:

```json
{
  "game_gid": "10000147",
  "events": [
    {"event_id": 1},
    {"event_id": 2}
  ],
  "fields": [...],
  "options": {...}
}
```

---

## Field Naming Conventions

Both naming conventions are supported:

| Purpose | camelCase | snake_case |
|---------|-----------|------------|
| Field name | `fieldName` | `field_name` |
| Field type | `fieldType` | `field_type` |
| JSON path | `jsonPath` | `json_path` |
| Aggregate function | `aggregateFunc` | `aggregate_func` |
| Custom expression | `customExpression` | `custom_expression` |
| Fixed value | `fixedValue` | `fixed_value` |
| Logical operator | `logicalOp` | `logical_op` |

---

## Request Parameters

### events (required)
Array of event objects. Each event must have:
- `game_gid` (int/string): Game GID
- `event_id` (int/string): Event ID from database
- `name`/`event_name` (optional): Event name (if not querying DB)

### fields (required)
Array of field objects. Each field must have:
- `fieldName`/`field_name` (string): Field name
- `fieldType`/`field_type` (string): One of: `base`, `param`, `custom`, `fixed`

Optional field properties:
- `alias` (string): Field alias in output
- `jsonPath`/`json_path` (string): For `param` type fields
- `aggregateFunc`/`aggregate_func` (string): Aggregate function (COUNT, SUM, AVG, MAX, MIN)
- `customExpression`/`custom_expression` (string): For `custom` type fields
- `fixedValue`/`fixed_value` (any): For `fixed` type fields

### where_conditions (optional)
Array of condition objects:
- `field` (string): Field name
- `operator` (string): One of: `=`, `!=`, `>`, `<`, `>=`, `<=`, `LIKE`, `IN`, `NOT IN`, `IS NULL`, `IS NOT NULL`
- `value` (any): Condition value
- `logicalOp`/`logical_op` (string): `AND` or `OR` (default: `AND`)

### options (optional)
- `mode` (string): `single`, `join`, or `union` (default: `single`)
- `sql_mode` (string): `VIEW`, `PROCEDURE`, or `CUSTOM` (default: `VIEW`)
- `include_comments` (boolean): Add comments to HQL (default: `false`)
- `include_performance` (boolean): Include performance analysis (default: `false`)

---

## Response Format

### Success (200 OK)
```json
{
  "success": true,
  "data": {
    "hql": "SELECT ...",
    "generated_at": "2026-02-11T01:00:00Z",
    "cached": true
  },
  "timestamp": "2026-02-11T01:00:00Z"
}
```

### With Performance Analysis
```json
{
  "success": true,
  "data": {
    "hql": "SELECT ...",
    "generated_at": "2026-02-11T01:00:00Z",
    "performance": {
      "score": 85,
      "issues": [...],
      "metrics": {...}
    }
  }
}
```

### Errors

**400 Bad Request** - Invalid input:
```json
{
  "success": false,
  "error": "Field must have either 'fieldName' or 'field_name'",
  "timestamp": "2026-02-11T01:00:00Z"
}
```

**404 Not Found** - Event or game doesn't exist:
```json
{
  "success": false,
  "error": "Event not found: id=99999",
  "timestamp": "2026-02-11T01:00:00Z"
}
```

**500 Internal Server Error** - Server error:
```json
{
  "success": false,
  "error": "Failed to generate HQL: ...",
  "timestamp": "2026-02-11T01:00:00Z"
}
```

---

## Examples

### Example 1: Basic Single Event
```bash
curl -X POST http://localhost:5001/hql-preview-v2/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "events": [{"game_gid": 10000147, "event_id": 1}],
    "fields": [
      {"fieldName": "role_id", "fieldType": "base"},
      {"fieldName": "zone_id", "fieldType": "param", "jsonPath": "$.zone_id"}
    ],
    "options": {"mode": "single", "include_comments": true}
  }'
```

### Example 2: Union Multiple Events
```bash
curl -X POST http://localhost:5001/hql-preview-v2/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "game_gid": "10000147",
    "events": [{"event_id": 1}, {"event_id": 2}],
    "fields": [{"field_name": "role_id", "field_type": "base"}],
    "options": {"mode": "union"}
  }'
```

### Example 3: With WHERE Conditions
```bash
curl -X POST http://localhost:5001/hql-preview-v2/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "events": [{"game_gid": 10000147, "event_id": 1}],
    "fields": [{"fieldName": "role_id", "fieldType": "base"}],
    "where_conditions": [
      {"field": "zone_id", "operator": "=", "value": 1, "logicalOp": "AND"}
    ],
    "options": {"mode": "single"}
  }'
```

---

## Field Types

### 1. base
Direct column reference from the table.
```json
{"fieldName": "role_id", "fieldType": "base"}
```

### 2. param
Extract from JSON `params` field using JSON path.
```json
{"fieldName": "zone_id", "fieldType": "param", "jsonPath": "$.zone_id"}
```

### 3. custom
Custom HQL expression.
```json
{"fieldName": "custom_field", "fieldType": "custom", "customExpression": "COUNT(DISTINCT role_id)"}
```

### 4. fixed
Fixed constant value.
```json
{"fieldName": "game", "fieldType": "fixed", "fixedValue": 10000147}
```

---

## Modes

### single
Single event query.
```hql
SELECT role_id FROM ieu_ods.ods_10000147_all_view WHERE ds = '${ds}'
```

### union
Combine multiple events with UNION ALL.
```hql
SELECT role_id FROM ... WHERE ds = '${ds}'
UNION ALL
SELECT role_id FROM ... WHERE ds = '${ds}'
```

### join
Join multiple events (requires `join_config`).
```hql
SELECT a.role_id, b.zone_id
FROM table1 AS a
INNER JOIN table2 AS b
ON a.role_id = b.role_id
```

---

## Testing

Run the verification test:
```bash
python3 /Users/mckenzie/Documents/event2table/test_hql_api_fix.py
```

Expected output:
```
Total: 6/6 tests passed (100%)
🎉 All tests passed! HQL Generation API is working correctly.
```

---

## Troubleshooting

**Issue**: 404 Event not found
- **Solution**: Verify `event_id` exists in database. Check `/api/events?game_gid=X`

**Issue**: 404 Game not found
- **Solution**: Verify `game_gid` exists in database. Check `/api/games`

**Issue**: 400 Field validation error
- **Solution**: Ensure all fields have either camelCase or snake_case names

**Issue**: 500 Server error
- **Solution**: Check server logs for traceback. Most likely a code bug.

---

## Additional Endpoints

- **GET /hql-preview-v2/api/status** - API status and features
- **POST /hql-preview-v2/api/generate-debug** - Generate with debug info
- **POST /hql-preview-v2/api/validate** - Validate HQL syntax
- **POST /hql-preview-v2/api/analyze** - Analyze HQL performance
- **GET /hql-preview-v2/api/cache-stats** - Get cache statistics
- **POST /hql-preview-v2/api/cache-clear** - Clear cache

---

## Quick Start Checklist

- [ ] Server is running: `python3 web_app.py`
- [ ] Verify server: `curl http://localhost:5001/api/games`
- [ ] Get events: `curl http://localhost:5001/api/events?game_gid=10000147`
- [ ] Note the `event_id` values you want to use
- [ ] Test HQL generation with your event_id
- [ ] Run verification test: `python3 test_hql_api_fix.py`
