# Backend API Quick Reference Guide

**Last Updated**: 2026-03-02
**Status**: ✅ All endpoints operational

---

## Critical Rules ⚠️

### 1. Use Correct Endpoint Names

❌ **WRONG**:
```javascript
fetch('/api/parameters')  // 404 Not Found
```

✅ **CORRECT**:
```javascript
fetch('/api/parameters/all?game_gid=10000147')  // 200 OK
```

### 2. Always Pass `game_gid` Parameter

❌ **WRONG**:
```javascript
fetch('/api/categories')  // 400 Bad Request: "game_gid required"
```

✅ **CORRECT**:
```javascript
fetch('/api/categories?game_gid=10000147')  // 200 OK
```

### 3. Handle Pagination

```javascript
// Page 1 (default)
fetch('/api/parameters/all?game_gid=10000147&page=1&limit=50')

// Page 2
fetch('/api/parameters/all?game_gid=10000147&page=2&limit=50')
```

---

## Categories API

### List Categories

```javascript
// GET /api/categories?game_gid=<gid>
const response = await fetch('/api/categories?game_gid=10000147');
const data = await response.json();

// Response:
{
  "success": true,
  "data": [
    {
      "id": 57,
      "name": "登录/认证",
      "description": null,
      "is_active": true,
      "created_at": "Thu, 12 Feb 2026 08:41:09 GMT"
    },
    ...
  ]
}
```

### Get Single Category

```javascript
// GET /api/categories/<id>
const response = await fetch('/api/categories/57');
const data = await response.json();
```

### Create Category

```javascript
// POST /api/categories
const response = await fetch('/api/categories', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({name: 'New Category'})
});
```

### Update Category

```javascript
// PUT /api/categories/<id>
const response = await fetch('/api/categories/57', {
  method: 'PUT',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({name: 'Updated Name'})
});
```

### Delete Category

```javascript
// DELETE /api/categories/<id>
const response = await fetch('/api/categories/57', {
  method: 'DELETE'
});
```

### Batch Delete Categories

```javascript
// POST /api/categories/batch-delete
const response = await fetch('/api/categories/batch-delete', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({category_ids: [57, 58, 59]})
});
```

### Get Category Stats

```javascript
// GET /api/categories/stats?game_gid=<gid>
const response = await fetch('/api/categories/stats?game_gid=10000147');
const data = await response.json();
```

---

## Parameters API

### List All Parameters

```javascript
// GET /api/parameters/all?game_gid=<gid>
const response = await fetch('/api/parameters/all?game_gid=10000147');
const data = await response.json();

// Response:
{
  "success": true,
  "data": {
    "parameters": [
      {
        "param_name": "guildId",
        "param_name_cn": "guild_id",
        "base_type": "int",
        "events_count": 1688,
        "is_common": 1,
        "usage_count": 1688
      },
      ...
    ],
    "total": 2162,
    "page": 1,
    "has_more": true
  }
}
```

### With Filters

```javascript
// Search parameters
const response = await fetch('/api/parameters/all?game_gid=10000147&search=zone');

// Filter by type
const response = await fetch('/api/parameters/all?game_gid=10000147&type=int');

// Pagination
const response = await fetch('/api/parameters/all?game_gid=10000147&page=2&limit=100');
```

### Get Parameter Details

```javascript
// GET /api/parameters/<param_name>/details?game_gid=<gid>
const response = await fetch('/api/parameters/zoneId/details?game_gid=10000147');
const data = await response.json();
```

### Get Parameter Stats

```javascript
// GET /api/parameters/stats?game_gid=<gid>
const response = await fetch('/api/parameters/stats?game_gid=10000147');
const data = await response.json();

// Response:
{
  "success": true,
  "data": {
    "total_unique_params": 2162,
    "total_event_params": 36718,
    "common_params_count": 0,
    "data_type_distribution": [
      {"base_type": "int", "count": 1801},
      {"base_type": "array", "count": 270},
      {"base_type": "string", "count": 130},
      {"base_type": "boolean", "count": 100},
      {"base_type": "map", "count": 13}
    ]
  }
}
```

### Search Parameters

```javascript
// POST /api/parameters/search
const response = await fetch('/api/parameters/search', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    game_gid: 10000147,
    keyword: 'zone',
    data_type: 'int'  // optional
  })
});
```

### Get Common Parameters

```javascript
// GET /api/parameters/common?game_gid=<gid>
const response = await fetch('/api/parameters/common?game_gid=10000147');
const data = await response.json();
```

### Validate Parameter Name

```javascript
// GET /api/parameters/validate?game_gid=<gid>&param_name=<name>
const response = await fetch('/api/parameters/validate?game_gid=10000147&param_name=zoneId');
const data = await response.json();

// Response:
{
  "success": true,
  "data": {
    "valid": true,
    "exists": true
  }
}
```

### Update Parameter

```javascript
// PUT /api/parameters/<id>
const response = await fetch('/api/parameters/123', {
  method: 'PUT',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    param_name: 'zoneId',
    param_name_cn: '区域ID'
  })
});
```

---

## Error Handling

### Standard Error Response Format

```json
{
  "success": false,
  "error": "Error message",
  "message": "Detailed error description",
  "status_code": 400
}
```

### Common Error Codes

| Code | Meaning | Example |
|------|---------|---------|
| 400 | Bad Request | Missing `game_gid` parameter |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate category name |
| 500 | Internal Server Error | Server error |

### Example Error Handling

```javascript
try {
  const response = await fetch('/api/categories?game_gid=10000147');
  const data = await response.json();

  if (!response.ok || !data.success) {
    throw new Error(data.error || 'Request failed');
  }

  // Handle success
  console.log(data.data);
} catch (error) {
  console.error('API Error:', error.message);
}
```

---

## Testing Endpoints

### Using curl

```bash
# Test categories
curl "http://127.0.0.1:5001/api/categories?game_gid=10000147"

# Test parameters
curl "http://127.0.0.1:5001/api/parameters/all?game_gid=10000147"

# Test stats
curl "http://127.0.0.1:5001/api/parameters/stats?game_gid=10000147"

# Pretty print JSON
curl "http://127.0.0.1:5001/api/categories?game_gid=10000147" | jq
```

### Using Browser Console

```javascript
// Quick test
fetch('/api/categories?game_gid=10000147')
  .then(r => r.json())
  .then(console.log);

// With error handling
fetch('/api/categories?game_gid=10000147')
  .then(r => {
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  })
  .then(data => {
    if (!data.success) throw new Error(data.error);
    console.log(data.data);
  })
  .catch(console.error);
```

---

## Performance Notes

### Caching

- Categories API: Cached for 30 minutes (1800s)
- Parameters API: Cached for 5 minutes (300s)
- Stats API: Cached for 5 minutes (300s)

### Pagination

- Default page size: 50 items
- Maximum page size: 100 items
- Use pagination for large datasets (2000+ parameters)

### Response Times

- Cached requests: <100ms
- Uncached requests: 200-500ms
- Large queries (stats): 500-1000ms

---

## Common Pitfalls

### 1. Wrong Endpoint Name

❌ **Wrong**:
```javascript
fetch('/api/parameters')  // 404
```

✅ **Correct**:
```javascript
fetch('/api/parameters/all')  // 200
```

### 2. Missing game_gid

❌ **Wrong**:
```javascript
fetch('/api/categories')  // 400: "game_gid required"
```

✅ **Correct**:
```javascript
fetch('/api/categories?game_gid=10000147')  // 200
```

### 3. Not Handling Pagination

❌ **Wrong**:
```javascript
// Only gets first 50 items
const data = await fetch('/api/parameters/all?game_gid=10000147')
  .then(r => r.json());
```

✅ **Correct**:
```javascript
// Gets all pages
async function getAllParameters(gameGid) {
  let page = 1;
  let allParams = [];

  while (true) {
    const response = await fetch(
      `/api/parameters/all?game_gid=${gameGid}&page=${page}&limit=100`
    );
    const data = await response.json();

    allParams = allParams.concat(data.data.parameters);

    if (!data.data.has_more) break;
    page++;
  }

  return allParams;
}
```

---

## Need Help?

- **Full API Documentation**: See `/Users/mckenzie/Documents/event2table/docs/api/`
- **Error Investigation Report**: `docs/reports/2026-03-02/BACKEND-API-ERROR-INVESTIGATION-REPORT.md`
- **Backend Logs**: `/tmp/flask_output.log` or `logs/flask.log`

---

**Last Updated**: 2026-03-02
**Server Status**: ✅ Running on http://127.0.0.1:5001
