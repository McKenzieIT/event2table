# Categories API

**事件分类管理API**

**版本**: 8.0.0 (Phase 5增强)
**文件**: `backend/api/routes/categories.py`
**架构**: CategoryService → EventCategoryRepository → EventCategoryEntity

---

## 概述

分类API提供事件分类的完整CRUD操作，支持批量操作和统计查询。

**核心特性**:
- ✅ 完整CRUD操作
- ✅ 批量删除和更新
- ✅ 分类统计信息
- ✅ 自动缓存管理
- ✅ Pydantic验证

**架构变更**:
- Phase 5: 新增统计和批量更新端点
- Phase 3: 迁移到CategoryService
- Phase 1: 基础CRUD实现

---

## 端点列表

| 方法 | 端点 | 描述 | Phase |
|------|------|------|-------|
| GET | `/api/categories` | 列出分类 | Phase 1 |
| GET | `/api/categories/<id>` | 获取单个分类 | Phase 1 |
| POST | `/api/categories` | 创建分类 | Phase 1 |
| PUT/PATCH | `/api/categories/<id>` | 更新分类 | Phase 1 |
| DELETE | `/api/categories/<id>` | 删除分类 | Phase 1 |
| POST | `/api/categories/batch-delete` | 批量删除 | Phase 3 |
| PUT | `/api/categories/batch-update` | 批量更新 | Phase 5 |
| GET | `/api/categories/stats` | 获取统计 | Phase 5 |

---

## 端点详情

### GET /api/categories

列出分类，按游戏过滤。

**查询参数**:
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| game_gid | int | ✅ | 游戏业务GID |

**请求示例**:
```bash
GET /api/categories?game_gid=10000147
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "充值/付费",
      "event_count": 1903,
      "created_at": "2026-02-01T00:00:00",
      "updated_at": "2026-02-28T12:00:00"
    },
    {
      "id": 2,
      "name": "战斗",
      "event_count": 45,
      "created_at": "2026-02-01T00:00:00",
      "updated_at": "2026-02-28T12:00:00"
    }
  ]
}
```

**错误响应**:
| 状态码 | 描述 |
|--------|------|
| 400 | game_gid参数缺失 |
| 404 | 游戏不存在 |

**Service层**: `CategoryService.get_all_categories(game_gid)`
**缓存策略**: 无缓存（实时数据）

---

### GET /api/categories/<id>

获取单个分类详情。

**路径参数**:
| 参数 | 类型 | 描述 |
|------|------|------|
| id | int | 分类ID |

**请求示例**:
```bash
GET /api/categories/1
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "充值/付费",
    "event_count": 1903,
    "created_at": "2026-02-01T00:00:00",
    "updated_at": "2026-02-28T12:00:00"
  }
}
```

**错误响应**:
| 状态码 | 描述 |
|--------|------|
| 404 | 分类不存在 |

**Service层**: `CategoryService.get_category_by_id(id)`

---

### POST /api/categories

创建新分类。

**请求体**:
```json
{
  "name": "新分类名称"
}
```

**字段验证**:
| 字段 | 类型 | 必填 | 验证规则 |
|------|------|------|----------|
| name | string | ✅ | 长度1-200，非空 |

**请求示例**:
```bash
POST /api/categories
Content-Type: application/json

{
  "name": "社交互动"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "Category created successfully",
  "data": {
    "id": 10,
    "name": "社交互动",
    "event_count": 0,
    "created_at": "2026-03-01T10:00:00",
    "updated_at": "2026-03-01T10:00:00"
  }
}
```

**错误响应**:
| 状态码 | 描述 |
|--------|------|
| 400 | 名称验证失败 |
| 409 | 分类名称已存在 |

**Service层**: `CategoryService.create_category(category_data)`

---

### PUT/PATCH /api/categories/<id>

更新分类名称。

**路径参数**:
| 参数 | 类型 | 描述 |
|------|------|------|
| id | int | 分类ID |

**请求体**:
```json
{
  "name": "更新后的分类名称"
}
```

**请求示例**:
```bash
PUT /api/categories/1
Content-Type: application/json

{
  "name": "付费行为"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "Category updated successfully",
  "data": {
    "id": 1,
    "name": "付费行为",
    "event_count": 1903,
    "updated_at": "2026-03-01T10:30:00"
  }
}
```

**错误响应**:
| 状态码 | 描述 |
|--------|------|
| 400 | 名称验证失败 |
| 404 | 分类不存在 |
| 409 | 分类名称已存在 |

**Service层**: `CategoryService.update_category(id, updates)`

---

### DELETE /api/categories/<id>

删除分类。

**路径参数**:
| 参数 | 类型 | 描述 |
|------|------|------|
| id | int | 分类ID |

**请求示例**:
```bash
DELETE /api/categories/10
```

**响应示例**:
```json
{
  "success": true,
  "message": "Category deleted successfully"
}
```

**错误响应**:
| 状态码 | 描述 |
|--------|------|
| 404 | 分类不存在 |

**注意事项**:
- 如果分类下有关联事件，删除会失败
- 建议使用批量删除API处理关联事件

**Service层**: `CategoryService.delete_category(id)`

---

### POST /api/categories/batch-delete

批量删除分类。

**请求体**:
```json
{
  "category_ids": [1, 2, 3, 4, 5]
}
```

**字段验证**:
| 字段 | 类型 | 必填 | 验证规则 |
|------|------|------|----------|
| category_ids | array | ✅ | 最多100个ID，所有ID必须是正整数 |

**请求示例**:
```bash
POST /api/categories/batch-delete
Content-Type: application/json

{
  "category_ids": [10, 11, 12]
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "Successfully deleted 2 out of 3 categories (1 failed)",
  "data": {
    "deleted_count": 2,
    "failed_ids": [12],
    "failed_reasons": {
      "12": "Category has 5 associated events"
    }
  }
}
```

**错误响应**:
| 状态码 | 描述 |
|--------|------|
| 400 | category_ids验证失败 |
| 400 | 超过100个ID限制 |

**Service层**: `CategoryService.batch_delete_categories(category_ids)`

---

### PUT /api/categories/batch-update (Phase 5新增)

批量更新分类。

**请求体**:
```json
{
  "ids": [1, 2, 3],
  "updates": {
    "name": "统一名称"
  }
}
```

**字段验证**:
| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| ids | array | ✅ | 分类ID列表 |
| updates | object | ✅ | 要更新的字段 |

**请求示例**:
```bash
PUT /api/categories/batch-update
Content-Type: application/json

{
  "ids": [10, 11],
  "updates": {
    "name": "社交互动（更新）"
  }
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "Updated 2 categories",
  "data": {
    "updated_count": 2
  }
}
```

**Service层**: `CategoryService.batch_update_categories(ids, updates)`

---

### GET /api/categories/stats (Phase 5新增)

获取分类统计信息。

**查询参数**:
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| game_gid | int | ❌ | 游戏GID（可选，用于过滤） |

**请求示例**:
```bash
# 获取全局统计
GET /api/categories/stats

# 获取特定游戏统计
GET /api/categories/stats?game_gid=10000147
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total_categories": 15,
    "active_categories": 12,
    "categories_with_events": 10,
    "category_breakdown": [
      {
        "id": 1,
        "name": "充值/付费",
        "event_count": 1903,
        "percentage": 85.2
      },
      {
        "id": 2,
        "name": "战斗",
        "event_count": 45,
        "percentage": 2.0
      }
    ]
  }
}
```

**Service层**: `CategoryService.get_statistics(game_gid)`
**缓存策略**: 1800秒TTL

---

## 数据模型

### EventCategoryEntity

```python
class EventCategoryEntity(BaseModel):
    """事件分类实体"""
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=200)
    event_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

---

## 性能指标

| 操作 | 平均响应时间 | 缓存命中率 |
|------|--------------|------------|
| GET /api/categories | 45ms | N/A |
| POST /api/categories | 120ms | N/A |
| GET /api/categories/stats | 55ms | 85% |

---

## 使用场景

### 1. 创建分类并关联事件

```javascript
// 1. 创建分类
const category = await fetch('/api/categories', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({name: '社交互动'})
}).then(r => r.json());

// 2. 创建事件并关联分类
const event = await fetch('/api/events', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    game_gid: 10000147,
    event_name: 'friend_request',
    event_name_cn: '好友请求',
    category_id: category.data.id
  })
}).then(r => r.json());
```

### 2. 批量管理分类

```javascript
// 批量删除空分类
const categoriesToDelete = [10, 11, 12];
const result = await fetch('/api/categories/batch-delete', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({category_ids: categoriesToDelete})
}).then(r => r.json());

console.log(`Deleted ${result.data.deleted_count} categories`);
console.log(`Failed: ${result.data.failed_ids}`);
```

### 3. 获取分类统计

```javascript
// 获取特定游戏的分类统计
const stats = await fetch('/api/categories/stats?game_gid=10000147')
  .then(r => r.json());

console.log(`Total categories: ${stats.data.total_categories}`);
console.log(`Categories with events: ${stats.data.categories_with_events}`);

// 显示分类分布
stats.data.category_breakdown.forEach(cat => {
  console.log(`${cat.name}: ${cat.event_count} events (${cat.percentage}%)`);
});
```

---

## 错误处理

### 常见错误

| 错误 | 状态码 | 原因 | 解决方案 |
|------|--------|------|----------|
| `game_gid is required` | 400 | 缺少game_gid参数 | 提供game_gid查询参数 |
| `Game not found` | 404 | 游戏不存在 | 检查game_gid是否正确 |
| `Category not found` | 404 | 分类不存在 | 检查分类ID |
| `Category already exists` | 409 | 分类名称重复 | 使用不同的名称 |
| `Category has associated events` | 400 | 分类下有事件 | 先移除或删除关联事件 |

### 错误响应示例

```json
{
  "success": false,
  "error": "Category with name '充值/付费' already exists",
  "message": "Category already exists"
}
```

---

## 相关文档

- [Events API](EVENTS-API.md) - 事件管理
- [Games API](GAMES-API.md) - 游戏管理
- [架构设计](../development/architecture.md) - ERS架构
- [缓存系统](../cache/README.md) - 缓存策略
