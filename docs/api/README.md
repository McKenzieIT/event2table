# API 文档

> **版本**: 1.0 | **最后更新**: 2026-02-18
> **基础路径**: `http://127.0.0.1:5001`

本文档提供 Event2Table 项目的完整 API 参考。

---

## 目录

1. [游戏管理 API](#游戏管理-api)
2. [事件管理 API](#事件管理-api)
3. [参数管理 API](#参数管理-api)
4. [HQL 生成 API](#hql-生成-api)
5. [V1 适配器 API](#v1-适配器-api) 🆕
6. [Canvas API](#canvas-api)
7. [错误码定义](#错误码定义)

---

## 游戏管理 API

### GET /api/games
获取所有游戏列表

**响应示例**:
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "gid": "10000147",
      "name": "STAR001",
      "ods_db": "ieu_ods",
      "description": "测试游戏"
    }
  ]
}
```

### POST /api/games
创建新游戏

**请求体**:
```json
{
  "gid": "90000001",
  "name": "测试游戏",
  "ods_db": "ieu_ods",
  "description": "游戏描述"
}
```

### DELETE /api/games/<int:game_gid>
删除指定游戏

**参数**: `game_gid` - 游戏业务GID

### PUT /api/games/<int:game_gid>
更新游戏信息

**请求体**: 同 POST /api/games

---

## 事件管理 API

### GET /api/events
获取事件列表

**查询参数**:
- `game_gid` (required): 游戏业务GID

**示例**: `GET /api/events?game_gid=10000147`

### POST /api/events
创建新事件

**请求体**:
```json
{
  "game_gid": 10000147,
  "event_name": "role.online",
  "event_code": "1001",
  "description": "角色上线事件"
}
```

### DELETE /api/events/<int:event_id>
删除指定事件

### PUT /api/events/<int:event_id>
更新事件信息

---

## 参数管理 API

### GET /api/parameters/all
获取所有参数列表

**查询参数**:
- `game_gid` (required): 游戏业务GID

**示例**: `GET /api/parameters/all?game_gid=10000147`

### POST /api/parameters
创建新参数

**请求体**:
```json
{
  "game_gid": 10000147,
  "event_id": 1,
  "param_name": "zoneId",
  "param_code": "zone_id",
  "data_type": "string",
  "json_path": "$.zoneId",
  "description": "区服ID"
}
```

### DELETE /api/parameters/<int:param_id>
删除指定参数

---

## HQL 生成 API

### POST /api/hql-preview-v2/generate
V2 HQL 生成接口

**请求体**:
```json
{
  "events": [
    {
      "event_name": "role.online",
      "alias": "e1"
    }
  ],
  "fields": [
    {
      "field_name": "ds",
      "field_type": "base",
      "source_event": "role.online"
    },
    {
      "field_name": "zone_id",
      "field_type": "param",
      "json_path": "$.zoneId",
      "source_event": "role.online"
    }
  ],
  "conditions": [
    {
      "field": "ds",
      "operator": "=",
      "value": "${ds}"
    }
  ],
  "options": {
    "mode": "single"
  }
}
```

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "hql": "SELECT ds, get_json_object(params, '$.zoneId') AS zone_id FROM ...",
    "performance": {
      "generation_time_ms": 0.8,
      "cache_hit": false
    }
  }
}
```

### GET /api/hql-preview-v2/history
获取 HQL 生成历史

### POST /api/hql-preview-v2/history/save
保存 HQL 生成历史

---

## V1 适配器 API 🆕

V1 适配器提供向后兼容的 API 接口，允许 V1 格式请求通过适配器调用 V2 核心逻辑。

### POST /api/v1-adapter/preview-hql
V1 格式的 HQL 预览接口

**请求格式** (V1):
```json
{
  "source_events": ["zmpvp.vis"],
  "base_fields": ["ds", "role_id", "account_id"],
  "custom_fields": [
    {
      "fieldName": "serverName",
      "fieldType": "param",
      "jsonPath": "$.serverName"
    }
  ],
  "where_conditions": [
    {
      "field": "ds",
      "operator": "=",
      "value": "${ds}"
    }
  ]
}
```

**响应格式** (V1):
```json
{
  "hql": "SELECT ds, role_id, account_id FROM ...",
  "performance": {
    "generation_time_ms": 0.8,
    "cache_hit": false
  },
  "status": "success"
}
```

**字段类型映射**:
- V1 `basic` → V2 `base`
- V1 `param` → V2 `param`
- V1 `custom` → V2 `custom`
- V1 `fixed` → V2 `fixed`

### POST /api/v1-adapter/generate-with-debug
V1 格式的调试模式接口

**请求格式**: 与 `/api/v1-adapter/preview-hql` 相同

**响应格式** (V1):
```json
{
  "hql": "SELECT ...",
  "debug_info": {
    "steps": [...],
    "performance_data": {...}
  },
  "status": "success"
}
```

### GET /api/v1-adapter/status
适配器状态检查

**响应格式**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "v2_api_available": true
}
```

**性能指标**:
- V1→V2 转换: ~0.42ms
- V2→V1 转换: ~0.38ms
- Roundtrip: ~0.80ms

**详细文档**: [backend/services/hql/adapters/README.md](../backend/services/hql/adapters/README.md)

---

## Canvas API

### POST /api/canvas/flows
创建新的 Canvas 流程

**请求体**:
```json
{
  "name": "测试流程",
  "description": "流程描述",
  "nodes": [...],
  "edges": [...]
}
```

### GET /api/canvas/flows
获取所有流程

### GET /api/canvas/flows/<int:flow_id>
获取指定流程

### PUT /api/canvas/flows/<int:flow_id>
更新流程

### DELETE /api/canvas/flows/<int:flow_id>
删除流程

### POST /api/canvas/execute
执行流程并生成 HQL

---

## 错误码定义

### HTTP 状态码

| 状态码 | 说明 | 示例场景 |
|--------|------|---------|
| 200 | 成功 | 请求正常处理 |
| 400 | 请求错误 | 参数验证失败 |
| 404 | 未找到 | 资源不存在 |
| 409 | 冲突 | 资源已存在 |
| 500 | 服务器错误 | 内部错误 |

### 业务错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|---------|
| `INVALID_GAME_GID` | 游戏GID无效 | 检查game_gid参数 |
| `EVENT_NOT_FOUND` | 事件不存在 | 检查event_id参数 |
| `FIELD_TYPE_MISMATCH` | 字段类型不匹配 | 使用支持的field_type |
| `TRANSFORMATION_ERROR` | V1/V2转换失败 | 检查请求格式 |

### 错误响应格式

```json
{
  "error": "Error message",
  "details": {
    "field": "field_name",
    "reason": "详细错误原因"
  },
  "status": "error"
}
```

---

## API 使用示例

### Python 示例

```python
import requests

# V2 API 调用
response = requests.post(
    "http://127.0.0.1:5001/api/hql-preview-v2/generate",
    json={
        "events": [{"event_name": "role.online"}],
        "fields": [...],
        "conditions": [],
        "options": {"mode": "single"}
    }
)
hql = response.json()['data']['hql']

# V1 适配器调用
response = requests.post(
    "http://127.0.0.1:5001/api/v1-adapter/preview-hql",
    json={
        "source_events": ["role.online"],
        "base_fields": ["ds", "role_id"],
        "custom_fields": [...]
    }
)
hql = response.json()['hql']
```

### JavaScript 示例

```javascript
// V2 API 调用
const response = await fetch('/api/hql-preview-v2/generate', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    events: [{event_name: 'role.online'}],
    fields: [...],
    conditions: [],
    options: {mode: 'single'}
  })
});
const data = await response.json();
const hql = data.data.hql;

// V1 适配器调用
const response = await fetch('/api/v1-adapter/preview-hql', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    source_events: ['role.online'],
    base_fields: ['ds', 'role_id'],
    custom_fields: [...]
  })
});
const data = await response.json();
const hql = data.hql;
```

---

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0 | 2026-02-18 | 创建 API 文档，添加 V1 适配器端点 |
| 0.1 | 2026-02-12 | 创建占位文件 |

---

## 相关文档

- [HQL 生成器文档](../hql/README.md)
- [V1/V2 适配器文档](../backend/services/hql/adapters/README.md)
- [开发规范](../development/getting-started.md)
