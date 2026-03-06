# Event Nodes API 文档

**版本**: 9.0.0
**最后更新**: 2026-03-05
**架构**: ERS (Entity-Repository-Service)

---

## 概述

Event Nodes API提供事件节点管理功能，用于在Canvas系统中配置单个事件的字段、WHERE条件和HQL生成规则。事件节点是Canvas流程的基本构建块。

### 特性

- **节点配置**: 配置事件的基础字段、参数字段
- **WHERE条件**: 支持复杂的WHERE条件构建
- **实时预览**: HQL实时生成和预览
- **版本管理**: 节点配置版本控制
- **批量操作**: 支持批量导入导出节点配置

---

## 端点列表

### List Event Nodes

**GET /api/event-nodes**

获取事件节点列表（分页）。

**查询参数**:
- `game_gid` (int, required): 游戏GID
- `event_id` (int, optional): 事件ID（过滤特定事件的节点）
- `page` (int, optional): 页码，默认1
- `limit` (int, optional): 每页数量，默认20
- `is_active` (bool, optional): 是否激活

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5001/api/event-nodes?game_gid=10000147&page=1&limit=20"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "nodes": [
      {
        "id": 1,
        "event_id": 1,
        "game_gid": 10000147,
        "node_name": "Login Node",
        "node_type": "single",
        "is_active": true,
        "created_at": "2026-03-05T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 45,
      "total_pages": 3
    }
  },
  "message": "Event nodes retrieved successfully"
}
```

**错误码**:
- 400: 缺少必填参数
- 500: 服务器错误

---

### Get Event Node

**GET /api/event-nodes/<id>**

获取单个事件节点的详细信息。

**路径参数**:
- `id` (int, required): 节点ID

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5001/api/event-nodes/1"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "event_id": 1,
    "game_gid": 10000147,
    "node_name": "Login Node",
    "node_type": "single",
    "table_name": "dwd.v_dwd_10000147_login_di",
    "field_config": {
      "base_fields": ["ds", "role_id", "account_id", "utdid"],
      "param_fields": [
        {
          "name": "zone_id",
          "param_type": "param",
          "json_path": "$.zoneId"
        }
      ]
    },
    "where_config": {
      "conditions": [
        {
          "field": "zone_id",
          "operator": "=",
          "value": "1"
        }
      ]
    },
    "hql_template": "-- Auto-generated HQL\nSELECT ...",
    "is_active": true,
    "created_at": "2026-03-05T10:00:00Z",
    "updated_at": "2026-03-05T11:00:00Z"
  }
}
```

**错误码**:
- 404: 节点不存在

---

### Create Event Node

**POST /api/event-nodes**

创建新的事件节点。

**请求体**:
```json
{
  "event_id": 1,
  "game_gid": 10000147,
  "node_name": "Login Node",
  "node_type": "single",
  "field_config": {
    "base_fields": ["ds", "role_id", "account_id", "utdid"],
    "param_fields": [
      {
        "name": "zone_id",
        "param_type": "param",
        "json_path": "$.zoneId"
      }
    ]
  },
  "where_config": {
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

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "event_id": 1,
    "game_gid": 10000147,
    "node_name": "Login Node",
    "node_type": "single",
    "is_active": true,
    "created_at": "2026-03-05T10:00:00Z"
  },
  "message": "Event node created successfully"
}
```

**错误码**:
- 400: 参数验证失败
- 404: 事件不存在
- 409: 节点名称已存在
- 500: 服务器错误

---

### Update Event Node

**PUT /api/event-nodes/<id>**
**PATCH /api/event-nodes/<id>**

更新事件节点配置。

**路径参数**:
- `id` (int, required): 节点ID

**请求体** (PATCH - 部分更新):
```json
{
  "node_name": "Updated Login Node",
  "where_config": {
    "conditions": [
      {
        "field": "zone_id",
        "operator": ">",
        "value": "1"
      }
    ]
  }
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "node_name": "Updated Login Node",
    "updated_at": "2026-03-05T12:00:00Z"
  },
  "message": "Event node updated successfully"
}
```

**错误码**:
- 400: 参数验证失败
- 404: 节点不存在
- 500: 服务器错误

---

### Delete Event Node

**DELETE /api/event-nodes/<id>**

删除事件节点。

**路径参数**:
- `id` (int, required): 节点ID

**请求示例**:
```bash
curl -X DELETE "http://127.0.0.1:5001/api/event-nodes/1"
```

**响应示例**:
```json
{
  "success": true,
  "message": "Event node deleted successfully"
}
```

**错误码**:
- 404: 节点不存在
- 500: 服务器错误

---

## 数据模型

### Event Node Entity

```json
{
  "id": 1,
  "event_id": 1,
  "game_gid": 10000147,
  "node_name": "Login Node",
  "node_type": "single|join|union",
  "table_name": "dwd.v_dwd_10000147_login_di",
  "field_config": {
    "base_fields": ["ds", "role_id", "account_id", "utdid"],
    "param_fields": [
      {
        "name": "zone_id",
        "param_type": "param",
        "json_path": "$.zoneId"
      }
    ]
  },
  "where_config": {
    "conditions": [
      {
        "field": "zone_id",
        "operator": "=|!=|>|<|>=|<=|LIKE|IN",
        "value": "1"
      }
    ],
    "logic": "AND|OR"
  },
  "hql_template": "-- Auto-generated HQL",
  "is_active": true,
  "created_at": "2026-03-05T10:00:00Z",
  "updated_at": "2026-03-05T11:00:00Z"
}
```

### Node Types

**Single Node** (单事件):
- 处理单个事件
- 配置基础字段和参数字段
- 支持WHERE条件

**Join Node** (Join):
- 支持多表JOIN
- 配置JOIN类型和条件

**Union Node** (Union):
- 支持多表UNION
- 合并多个事件的数据

---

## 使用示例

### 创建并使用事件节点

```javascript
// 1. 创建事件节点
const createEventNode = async () => {
  const response = await fetch('/api/event-nodes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      event_id: 1,
      game_gid: 10000147,
      node_name: 'Login Node',
      node_type: 'single',
      field_config: {
        base_fields: ['ds', 'role_id', 'account_id', 'utdid'],
        param_fields: [
          {
            name: 'zone_id',
            param_type: 'param',
            json_path: '$.zoneId'
          }
        ]
      },
      where_config: {
        conditions: [
          {
            field: 'zone_id',
            operator: '=',
            value: '1'
          }
        ]
      }
    })
  });
  return response.json();
};

// 2. 获取节点详情
const getEventNode = async (nodeId) => {
  const response = await fetch(`/api/event-nodes/${nodeId}`);
  return response.json();
};

// 3. 更新节点配置
const updateEventNode = async (nodeId) => {
  const response = await fetch(`/api/event-nodes/${nodeId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      where_config: {
        conditions: [
          {
            field: 'zone_id',
            operator: '>',
            value: '1'
          }
        ]
      }
    })
  });
  return response.json();
};

// 使用示例
createEventNode().then(result => {
  console.log('Node created:', result.data.id);
  return getEventNode(result.data.id);
}).then(result => {
  console.log('Node details:', result.data);
  return updateEventNode(result.data.id);
}).then(result => {
  console.log('Node updated:', result.data);
});
```

### 列出并筛选节点

```javascript
// 获取特定事件的所有节点
const getEventNodes = async (gameGid, eventId) => {
  const response = await fetch(
    `/api/event-nodes?game_gid=${gameGid}&event_id=${eventId}`
  );
  return response.json();
};

// 获取激活的节点
const getActiveNodes = async (gameGid) => {
  const response = await fetch(
    `/api/event-nodes?game_gid=${gameGid}&is_active=true`
  );
  return response.json();
};

// 使用示例
getEventNodes(10000147, 1).then(result => {
  console.log('Event nodes:', result.data.nodes);
  console.log('Pagination:', result.data.pagination);
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
  "error": "Validation error: node_name is required",
  "message": "Node name is required. Must be 1-200 characters."
}
```

**404 Not Found - 节点不存在**:
```json
{
  "success": false,
  "error": "Event node 999 not found",
  "message": "Event node 999 not found. Check the node_id or create the node first."
}
```

**409 Conflict - 节点名称已存在**:
```json
{
  "success": false,
  "error": "Event node 'Login Node' already exists for event 1",
  "message": "Event node 'Login Node' already exists. Use PUT to update or DELETE to remove."
}
```

---

## 与Canvas API的关系

Event Nodes API和Canvas API紧密相关：

- **Event Nodes API**: 管理单个事件节点的配置
- **Canvas API**: 管理多个事件节点的组合和流程

**典型工作流程**:
1. 使用Event Nodes API创建和配置单个事件节点
2. 使用Canvas API将多个节点组合成流程
3. 使用Canvas API生成完整的HQL

---

## 性能优化

### 缓存策略

**节点数据缓存**:
- TTL: 300秒 (5分钟)
- 失效条件: 节点更新、删除

### 分页支持

**标准分页参数**:
- `page`: 页码（默认1）
- `limit`: 每页数量（默认20，最大100）

---

## 相关文档

- **[Canvas API文档](CANVAS-API.md)** - Canvas流程管理
- **[Events API文档](EVENTS-API.md)** - 事件管理
- **[HQL生成器文档](../hql/)** - HQL生成器详细说明
- **[经验文档 - Canvas最佳实践](../canvas/)** - Canvas架构和使用说明

---

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0.0 | 2026-02-18 | Event Nodes API初始版本 |
| 2.0.0 | 2026-03-01 | Repository Pattern迁移 |
| 3.0.0 | 2026-03-05 | 节点配置优化和WHERE条件增强 |
