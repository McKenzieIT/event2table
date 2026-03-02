# Events API

**事件管理API**

**版本**: 8.0.0 (Phase 5完全迁移)
**文件**: `backend/api/routes/events.py`
**架构**: EventService → EventRepository → EventEntity

---

## 概述

事件API提供日志事件的完整CRUD操作，支持分页、搜索、批量操作和参数管理。

**核心特性**:
- ✅ 完整CRUD操作
- ✅ 分页和搜索
- ✅ 批量删除和更新
- ✅ 事件参数管理
- ✅ 自动缓存管理
- ✅ Pydantic验证

**架构变更**:
- Phase 5: 完全迁移到EventService
- Phase 3: 引入分页和批量操作
- Phase 1: 基础CRUD实现

---

## 端点列表

| 方法 | 端点 | 描述 | Phase |
|------|------|------|-------|
| GET | `/api/events` | 列出事件（分页） | Phase 3 |
| GET | `/api/events/<id>` | 获取事件详情 | Phase 1 |
| POST | `/api/events` | 创建事件 | Phase 1 |
| PUT/PATCH | `/api/events/<id>` | 更新事件 | Phase 1 |
| DELETE | `/api/events/batch` | 批量删除 | Phase 3 |
| PUT | `/api/events/batch-update` | 批量更新 | Phase 5 |
| GET | `/api/events/<id>/parameters` | 获取事件参数 | Phase 2 |
| GET | `/api/events/<event_id>/params` | 获取参数（别名） | Phase 2 |

---

## 端点详情

### GET /api/events

列出事件，支持分页和搜索。

**查询参数**:
| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| game_gid | int | ❌ | - | 游戏业务GID |
| page | int | ❌ | 1 | 页码 |
| per_page | int | ❌ | 20 | 每页数量（最大100） |
| search | string | ❌ | - | 搜索关键词（事件名称） |

**请求示例**:
```bash
# 基础查询
GET /api/events?game_gid=10000147

# 分页查询
GET /api/events?game_gid=10000147&page=2&per_page=50

# 搜索
GET /api/events?game_gid=10000147&search=login
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "events": [
      {
        "id": 1,
        "game_gid": 10000147,
        "name": "login",
        "name_cn": "登录",
        "category_id": 1,
        "category_name": "账号相关",
        "include_in_common_params": 1,
        "created_at": "2026-02-01T00:00:00",
        "updated_at": "2026-02-28T12:00:00"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 150,
      "total_pages": 8
    }
  }
}
```

**错误响应**:
| 状态码 | 描述 |
|--------|------|
| 400 | 分页参数错误 |

**Service层**: `EventService.get_events_paginated(game_gid, page, per_page, search)`
**缓存策略**: 1800秒TTL
**性能**: <100ms (缓存命中)

---

### GET /api/events/<id>

获取单个事件详情。

**路径参数**:
| 参数 | 类型 | 描述 |
|------|------|------|
| id | int | 事件ID |

**查询参数**:
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| game_gid | int | ✅ | 游戏业务GID |

**请求示例**:
```bash
GET /api/events/1?game_gid=10000147
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "game_gid": 10000147,
    "name": "login",
    "name_cn": "登录",
    "category_id": 1,
    "category_name": "账号相关",
    "include_in_common_params": 1,
    "parameter_count": 8,
    "created_at": "2026-02-01T00:00:00",
    "updated_at": "2026-02-28T12:00:00"
  }
}
```

**错误响应**:
| 状态码 | 描述 |
|--------|------|
| 400 | game_gid参数缺失 |
| 404 | 事件不存在 |

**Service层**: `EventService.get_event_detail_with_game(id, game_gid)`

---

### POST /api/events

创建新事件。

**请求体**:
```json
{
  "game_gid": 10000147,
  "event_name": "logout",
  "event_name_cn": "登出",
  "category_id": 1,
  "include_in_common_params": 1,
  "param_names": ["role_id", "logout_reason"],
  "param_names_cn": ["角色ID", "登出原因"],
  "param_types": [1, 2],
  "param_descriptions": ["角色唯一标识", "登出原因说明"]
}
```

**字段验证**:
| 字段 | 类型 | 必填 | 验证规则 |
|------|------|------|----------|
| game_gid | int | ✅ | 游戏必须存在 |
| event_name | string | ✅ | 长度1-200，XSS防护 |
| event_name_cn | string | ✅ | 长度1-200，XSS防护 |
| category_id | int | ❌ | 分类ID（不存在则创建默认分类） |
| include_in_common_params | int | ❌ | 是否包含在通用参数（0/1） |
| param_names | array | ❌ | 参数名称列表 |
| param_names_cn | array | ❌ | 参数中文名称列表 |
| param_types | array | ❌ | 参数类型ID列表 |
| param_descriptions | array | ❌ | 参数描述列表 |

**请求示例**:
```bash
POST /api/events
Content-Type: application/json

{
  "game_gid": 10000147,
  "event_name": "level_up",
  "event_name_cn": "升级",
  "category_id": 3,
  "param_names": ["role_id", "old_level", "new_level"],
  "param_names_cn": ["角色ID", "旧等级", "新等级"],
  "param_types": [1, 2, 2],
  "param_descriptions": ["角色唯一标识", "升级前等级", "升级后等级"]
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "Event created successfully",
  "data": {
    "event_id": 151
  }
}
```

**错误响应**:
| 状态码 | 描述 |
|--------|------|
| 400 | 参数验证失败 |
| 404 | 游戏或分类不存在 |

**Service层**: `EventService.create_event_with_parameters(event_data, parameters)`

---

### PUT/PATCH /api/events/<id>

更新事件信息。

**路径参数**:
| 参数 | 类型 | 描述 |
|------|------|------|
| id | int | 事件ID |

**请求体**:
```json
{
  "event_name": "logout",
  "event_name_cn": "登出",
  "category_id": 1,
  "include_in_common_params": 1
}
```

**字段验证**: 同POST（所有字段可选）

**请求示例**:
```bash
PUT /api/events/1
Content-Type: application/json

{
  "event_name": "login_success",
  "event_name_cn": "登录成功",
  "category_id": 1
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "Event updated successfully"
}
```

**错误响应**:
| 状态码 | 描述 |
|--------|------|
| 400 | 参数验证失败 |
| 404 | 事件不存在 |

**Service层**: `EventService.update_event_with_invalidation(id, ...)`

---

### DELETE /api/events/batch

批量删除事件。

**请求体**:
```json
{
  "ids": [1, 2, 3, 4, 5]
}
```

**字段验证**:
| 字段 | 类型 | 必填 | 验证规则 |
|------|------|------|----------|
| ids | array | ✅ | 事件ID列表 |

**请求示例**:
```bash
DELETE /api/events/batch
Content-Type: application/json

{
  "ids": [100, 101, 102]
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "Deleted 3 events",
  "data": {
    "deleted_count": 3
  }
}
```

**Service层**: `EventService.batch_delete_events(ids)`

---

### PUT /api/events/batch-update (Phase 5新增)

批量更新事件。

**请求体**:
```json
{
  "ids": [1, 2, 3],
  "updates": {
    "category_id": 5,
    "include_in_common_params": 0
  }
}
```

**请求示例**:
```bash
PUT /api/events/batch-update
Content-Type: application/json

{
  "ids": [10, 11, 12],
  "updates": {
    "category_id": 3,
    "include_in_common_params": 1
  }
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "Updated 3 events",
  "data": {
    "updated_count": 3
  }
}
```

**Service层**: `EventService.batch_update_events(ids, updates)`

---

### GET /api/events/<id>/parameters

获取事件的参数列表。

**路径参数**:
| 参数 | 类型 | 描述 |
|------|------|------|
| id | int | 事件ID |

**请求示例**:
```bash
GET /api/events/1/parameters
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "param_name": "role_id",
      "param_name_cn": "角色ID",
      "template_id": 1,
      "param_type": "int",
      "param_description": "角色唯一标识",
      "is_active": 1
    },
    {
      "id": 2,
      "param_name": "zone_id",
      "param_name_cn": "区域ID",
      "template_id": 2,
      "param_type": "string",
      "param_description": "所在区域",
      "is_active": 1
    }
  ]
}
```

**Service层**: `EventService.get_event_parameters(id)`

---

### GET /api/events/<event_id>/params

获取事件参数（别名端点）。

**功能**: 与 `/api/events/<id>/parameters` 完全相同

**请求示例**:
```bash
GET /api/events/1/params
```

---

## 数据模型

### EventEntity

```python
class EventEntity(BaseModel):
    """事件实体"""
    id: Optional[int] = None
    game_gid: int = Field(..., description="游戏业务GID")
    name: str = Field(..., min_length=1, max_length=200)
    name_cn: str = Field(..., min_length=1, max_length=200)
    category_id: Optional[int] = None
    include_in_common_params: int = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator('name', 'name_cn')
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """防止XSS攻击"""
        import html
        return html.escape(v.strip())
```

---

## 性能指标

| 操作 | 平均响应时间 | 缓存命中率 |
|------|--------------|------------|
| GET /api/events | 88ms | 85% |
| POST /api/events | 150ms | N/A |
| GET /api/events/<id> | 55ms | 90% |
| PUT /api/events/<id> | 130ms | N/A |

---

## 使用场景

### 1. 创建事件并添加参数

```javascript
// 创建事件
const event = await fetch('/api/events', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    game_gid: 10000147,
    event_name: 'purchase',
    event_name_cn: '购买',
    category_id: 1,
    param_names: ['item_id', 'price', 'currency'],
    param_names_cn: ['物品ID', '价格', '货币'],
    param_types: [1, 2, 2],
    param_descriptions: ['购买的物品ID', '价格', '货币类型']
  })
}).then(r => r.json());

console.log(`Event created with ID: ${event.data.event_id}`);
```

### 2. 分页浏览事件

```javascript
let page = 1;
const perPage = 20;

async function loadEvents() {
  const response = await fetch(
    `/api/events?game_gid=10000147&page=${page}&per_page=${perPage}`
  );
  const data = await response.json();

  console.log(`Page ${data.data.pagination.page} of ${data.data.pagination.total_pages}`);
  console.log(`Total events: ${data.data.pagination.total}`);

  data.data.events.forEach(event => {
    console.log(`${event.name}: ${event.name_cn}`);
  });
}

loadEvents();
```

### 3. 批量更新事件分类

```javascript
// 批量更新事件的分类
const eventIds = [10, 11, 12, 13, 14];
const result = await fetch('/api/events/batch-update', {
  method: 'PUT',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    ids: eventIds,
    updates: {
      category_id: 3,
      include_in_common_params: 1
    }
  })
}).then(r => r.json());

console.log(`Updated ${result.data.updated_count} events`);
```

### 4. 获取事件参数

```javascript
// 获取事件的参数列表
const eventId = 1;
const response = await fetch(`/api/events/${eventId}/parameters`);
const data = await response.json();

console.log(`Event has ${data.data.length} parameters:`);
data.data.forEach(param => {
  console.log(`- ${param.param_name} (${param.param_type}): ${param.param_name_cn}`);
});
```

---

## 错误处理

### 常见错误

| 错误 | 状态码 | 原因 | 解决方案 |
|------|--------|------|----------|
| `event_name cannot be empty` | 400 | 事件名称为空 | 提供有效的事件名称 |
| `exceeds maximum length` | 400 | 字段长度超限 | 检查字段长度（<200） |
| `Game not found` | 404 | 游戏不存在 | 检查game_gid |
| `Category not found` | 404 | 分类不存在 | 提供有效的category_id |
| `Event not found` | 404 | 事件不存在 | 检查事件ID |

---

## 相关文档

- [Categories API](CATEGORIES-API.md) - 分类管理
- [Parameters API](PARAMETERS-API.md) - 参数管理
- [Games API](GAMES-API.md) - 游戏管理
- [缓存系统](../cache/README.md) - 缓存策略
