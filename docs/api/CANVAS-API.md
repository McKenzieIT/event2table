# Canvas API 文档

**版本**: 9.0.0
**最后更新**: 2026-03-05
**架构**: ERS (Entity-Repository-Service)

---

## 概述

Canvas API提供流程可视化配置和HQL生成功能。通过Canvas，用户可以拖拽式配置事件节点、设置字段、添加WHERE条件，并实时生成HQL查询。

### 特性

- **可视化配置**: 拖拽式流程配置
- **实时预览**: HQL实时生成预览
- **多种模式**: Single、Join、Union三种HQL生成模式
- **版本控制**: 流程模板保存和版本管理
- **批量操作**: 支持批量导入导出流程

---

## 端点列表

### Canvas Health Check

**GET /canvas/api/canvas/health**

健康检查端点，用于验证Canvas服务是否正常运行。

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5001/canvas/api/canvas/health"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "canvas"
  },
  "message": "Canvas service is healthy"
}
```

---

### Save Flow

**POST /canvas/api/flows/save**

保存Canvas流程配置。

**请求体**:
```json
{
  "game_gid": 10000147,
  "flow_name": "Login Flow",
  "category": "authentication",
  "description": "User login event processing",
  "flow_data": {
    "nodes": [...],
    "connections": [...]
  }
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 123,
    "flow_name": "Login Flow",
    "game_gid": 10000147,
    "is_active": true,
    "created_at": "2026-03-05T10:00:00Z"
  },
  "message": "Flow created successfully"
}
```

**错误码**:
- 400: 缺少必填字段
- 404: 游戏不存在
- 409: 流程名称已存在
- 500: 服务器错误

---

### Get Flow

**GET /canvas/api/flows/<flowId>**

获取指定流程的详细信息。

**路径参数**:
- `flowId` (int, required): 流程ID

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5001/canvas/api/flows/123"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 123,
    "flow_name": "Login Flow",
    "game_gid": 10000147,
    "category": "authentication",
    "description": "User login event processing",
    "flow_data": {
      "nodes": [
        {
          "id": "node-1",
          "type": "event",
          "event_id": 1,
          "position": {"x": 100, "y": 100}
        }
      ],
      "connections": [...]
    },
    "is_active": true,
    "created_at": "2026-03-05T10:00:00Z",
    "updated_at": "2026-03-05T11:00:00Z"
  }
}
```

**错误码**:
- 404: 流程不存在

---

### Execute Flow / Generate HQL

**POST /canvas/api/execute**

执行流程并生成HQL查询。

**请求体**:
```json
{
  "flow_id": 123,
  "bizdate": "20260305",
  "mode": "single"
}
```

**参数说明**:
- `flow_id` (int, required): 流程ID
- `bizdate` (string, required): 业务日期，格式YYYYMMDD
- `mode` (string, optional): HQL生成模式，可选值: `single`, `join`, `union`，默认`single`

**响应示例**:
```json
{
  "success": true,
  "data": {
    "hql": "-- Auto-generated HQL\nDROP TABLE IF EXISTS dwd.v_dwd_10000147_login_di;\nCREATE TABLE dwd.v_dwd_10000147_login_di AS\nSELECT\n  ds,\n  role_id,\n  account_id,\n  get_json_object(params, '$.zoneId') AS zone_id\nFROM ieu_ods.ods_10000147_all_view\nWHERE ds = '${bizdate}'\n  AND event_name = 'login';",
    "stats": {
      "tables_created": 1,
      "rows_processed": 1000
    }
  },
  "message": "HQL generated successfully"
}
```

**错误码**:
- 400: 参数错误或流程数据无效
- 404: 流程不存在
- 500: HQL生成失败

---

### Preview Results

**POST /canvas/api/preview-results**

预览流程执行结果（不实际执行）。

**请求体**:
```json
{
  "flow_id": 123
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "flow_id": 123,
    "status": "preview_ready",
    "preview": {
      "events_count": 3,
      "parameters_count": 15,
      "estimated_tables": 3
    }
  },
  "message": "Flow preview generated successfully"
}
```

---

### Flows API (REST Endpoints)

Canvas API也提供标准的REST端点，与 `/canvas/api/*` 端点功能相同。

**GET /api/flows**
- 获取流程列表（分页）
- 参数: `game_gid`, `page`, `page_size`

**POST /api/flows**
- 创建新流程
- 功能等同于 `POST /canvas/api/flows/save`

**GET /api/flows/<flow_id>**
- 获取流程详情
- 功能等同于 `GET /canvas/api/flows/<flowId>`

**PUT /api/flows/<flow_id>**
- 更新流程

**DELETE /api/flows/<flow_id>**
- 删除流程

**POST /api/flows/generate**
- 生成HQL
- 功能等同于 `POST /canvas/api/execute`

**POST /api/flows/<flow_id>/load**
- 加载流程数据

**DELETE /api/flows/batch**
- 批量删除流程
- 请求体: `{"ids": [1, 2, 3]}`

**PUT /api/flows/batch-update**
- 批量更新流程

---

## 数据模型

### Flow Entity

```json
{
  "id": 123,
  "flow_name": "Login Flow",
  "game_gid": 10000147,
  "category": "authentication",
  "description": "User login event processing",
  "flow_data": {
    "nodes": [
      {
        "id": "node-1",
        "type": "event|join|union|filter",
        "event_id": 1,
        "position": {"x": 100, "y": 100},
        "config": {...}
      }
    ],
    "connections": [
      {
        "id": "conn-1",
        "source": "node-1",
        "target": "node-2",
        "type": "data"
      }
    ]
  },
  "is_active": true,
  "created_at": "2026-03-05T10:00:00Z",
  "updated_at": "2026-03-05T11:00:00Z"
}
```

### Node Types

**Event Node**:
```json
{
  "id": "node-1",
  "type": "event",
  "event_id": 1,
  "position": {"x": 100, "y": 100},
  "config": {
    "fields": [...],
    "conditions": [...]
  }
}
```

**Join Node**:
```json
{
  "id": "node-2",
  "type": "join",
  "position": {"x": 300, "y": 100},
  "config": {
    "join_type": "INNER|LEFT|RIGHT|FULL",
    "left_table": "table1",
    "right_table": "table2",
    "join_condition": "table1.id = table2.id"
  }
}
```

**Union Node**:
```json
{
  "id": "node-3",
  "type": "union",
  "position": {"x": 500, "y": 100},
  "config": {
    "tables": ["table1", "table2", "table3"],
    "union_all": true
  }
}
```

**Filter Node**:
```json
{
  "id": "node-4",
  "type": "filter",
  "position": {"x": 700, "y": 100},
  "config": {
    "conditions": [
      {
        "field": "zone_id",
        "operator": "=",
        "value": "1"
      }
    ]
  }
}
```

---

## 使用示例

### 创建并执行流程

```javascript
// 1. 创建流程
const createFlow = async () => {
  const response = await fetch('/canvas/api/flows/save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      game_gid: 10000147,
      flow_name: 'Login Flow',
      category: 'authentication',
      description: 'User login event processing',
      flow_data: {
        nodes: [
          {
            id: 'node-1',
            type: 'event',
            event_id: 1,
            position: { x: 100, y: 100 }
          }
        ],
        connections: []
      }
    })
  });
  return response.json();
};

// 2. 生成HQL
const generateHQL = async (flowId) => {
  const response = await fetch('/canvas/api/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      flow_id: flowId,
      bizdate: '20260305',
      mode: 'single'
    })
  });
  return response.json();
};

// 使用示例
createFlow().then(result => {
  console.log('Flow created:', result.data.id);
  return generateHQL(result.data.id);
}).then(result => {
  console.log('Generated HQL:', result.data.hql);
});
```

### 获取并预览流程

```javascript
// 获取流程详情
const getFlow = async (flowId) => {
  const response = await fetch(`/canvas/api/flows/${flowId}`);
  return response.json();
};

// 预览执行结果
const previewFlow = async (flowId) => {
  const response = await fetch('/canvas/api/preview-results', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ flow_id: flowId })
  });
  return response.json();
};

// 使用示例
getFlow(123).then(result => {
  console.log('Flow details:', result.data);
  return previewFlow(123);
}).then(result => {
  console.log('Preview:', result.data.preview);
});
```

---

## 错误处理

### 统一错误响应格式

```json
{
  "success": false,
  "error": "具体错误消息",
  "message": "用户友好的错误描述"
}
```

### 常见错误场景

**400 Bad Request - 参数验证失败**:
```json
{
  "success": false,
  "error": "Missing required field: flow_name",
  "message": "Flow name is required. Must be 1-200 characters."
}
```

**404 Not Found - 流程不存在**:
```json
{
  "success": false,
  "error": "Flow 123 not found",
  "message": "Flow 123 not found. Check the flow_id or create the flow first."
}
```

**409 Conflict - 流程名称已存在**:
```json
{
  "success": false,
  "error": "Flow 'Login Flow' already exists for game 10000147",
  "message": "Flow 'Login Flow' already exists. Use PUT to update or DELETE to remove."
}
```

**500 Internal Server Error - HQL生成失败**:
```json
{
  "success": false,
  "error": "Failed to generate HQL: Invalid join condition",
  "message": "HQL generation failed. Please check your flow configuration."
}
```

---

## 性能优化

### 缓存策略

**流程数据缓存**:
- TTL: 600秒 (10分钟)
- 失效条件: 流程更新、删除

**HQL生成缓存**:
- TTL: 300秒 (5分钟)
- 失效条件: 流程配置更新

### 分页支持

**标准分页参数**:
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认50，最大200）

---

## 相关文档

- **[Flows API文档](FLOWS-API.md)** - Flows API完整文档
- **[Event Nodes API文档](EVENT-NODES-API.md)** - 事件节点管理
- **[HQL生成器文档](../hql/)** - HQL生成器详细说明
- **[经验文档 - Canvas最佳实践](../lessons-learned/canvas-best-practices.md)** - Canvas使用经验

---

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0.0 | 2026-02-18 | Canvas API初始版本 |
| 2.0.0 | 2026-03-01 | Repository Pattern迁移 |
| 3.0.0 | 2026-03-05 | Canvas API别名端点优化 |
