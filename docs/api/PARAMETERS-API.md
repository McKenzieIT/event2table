# Parameters API

**参数管理API**

**版本**: 8.0.0 (Phase 5大幅扩展)
**文件**: `backend/api/routes/parameters.py`
**架构**: ParameterService → ParameterRepository → ParameterEntity

---

## 概述

参数API提供事件参数的完整管理功能，包括参数查询、搜索、统计和参数库关联。

**核心特性**:
- ✅ 参数去重查询
- ✅ 参数搜索和过滤
- ✅ 参数统计分析
- ✅ 参数库关联
- ✅ ALTER TABLE SQL生成
- ✅ 分层缓存（70%性能提升）

**架构变更**:
- Phase 5: 新增8个高级端点
- Phase 3: 迁移到ParameterService
- Phase 1: 基础CRUD实现

---

## 端点列表

### 基础CRUD (5 endpoints)

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/parameters/all` | 获取所有参数（去重） |
| GET | `/api/parameters/<id>` | 获取单个参数 |
| POST | `/api/parameters` | 创建参数 |
| PUT | `/api/parameters/<id>` | 更新参数 |
| DELETE | `/api/parameters/<id>` | 删除参数 |

### 查询和统计 (4 endpoints)

| 方法 | 端点 | 描述 | Phase |
|------|------|------|-------|
| GET | `/api/parameters/<param_name>/details` | 获取参数详情 | Phase 3 |
| GET | `/api/parameters/stats` | 获取参数统计 | Phase 5 |
| POST | `/api/parameters/search` | 搜索参数 | Phase 5 |
| GET | `/api/parameters/common` | 获取通用参数 | Phase 3 |

### 参数库管理 (3 endpoints)

| 方法 | 端点 | 描述 | Phase |
|------|------|------|-------|
| GET | `/api/param-library/check` | 检查参数库 | Phase 4 |
| POST | `/api/event-params/<param_id>/link-library` | 关联到参数库 | Phase 4 |
| POST | `/api/param-library/batch-check` | 批量检查参数库 | Phase 5 |

### 其他功能 (4 endpoints)

| 方法 | 端点 | 描述 | Phase |
|------|------|------|-------|
| GET | `/api/parameters/validate` | 验证参数名称 | Phase 3 |
| GET | `/api/alter-table/<param_id>` | 生成ALTER TABLE SQL | Phase 5 |

---

## 核心端点详情

### GET /api/parameters/all

获取所有参数（按参数名去重）。

**查询参数**:
| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| game_gid | int | ✅ | - | 游戏业务GID |
| game_id | int | ❌ | - | 游戏数据库ID（向后兼容） |
| search | string | ❌ | - | 搜索关键词 |
| type | string | ❌ | - | 参数类型过滤 |
| page | int | ❌ | 1 | 页码 |
| limit | int | ❌ | 50 | 每页数量（最大100） |

**请求示例**:
```bash
# 基础查询
GET /api/parameters/all?game_gid=10000147

# 搜索和过滤
GET /api/parameters/all?game_gid=10000147&search=role&type=int&page=1&limit=20
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "parameters": [
      {
        "param_name": "role_id",
        "param_name_cn": "角色ID",
        "base_type": "int",
        "events_count": 15,
        "usage_count": 45,
        "is_common": 1
      },
      {
        "param_name": "zone_id",
        "param_name_cn": "区域ID",
        "base_type": "string",
        "events_count": 8,
        "usage_count": 12,
        "is_common": 0
      }
    ],
    "total": 150,
    "page": 1,
    "has_more": true
  }
}
```

**性能指标**:
- 优化前: 267ms
- 优化后: 88ms (67%提升)
- 缓存命中率: 85%

**Service层**: `ParameterService.get_all_parameters(game_gid, ...)`
**缓存策略**: L1 60秒 + L2 300秒

---

### GET /api/parameters/<param_name>/details

获取参数详细信息（跨事件使用情况）。

**路径参数**:
| 参数 | 类型 | 描述 |
|------|------|------|
| param_name | string | 参数名称 |

**查询参数**:
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| game_gid | int | ✅ | 游戏业务GID |

**请求示例**:
```bash
GET /api/parameters/role_id/details?game_gid=10000147
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "param_name": "role_id",
    "param_name_cn": "角色ID",
    "base_type": "int",
    "events": [
      {
        "event_id": 1,
        "event_name": "login",
        "param_name_cn": "角色ID",
        "template_id": 1
      },
      {
        "event_id": 5,
        "event_name": "level_up",
        "param_name_cn": "角色ID",
        "template_id": 1
      }
    ],
    "usage_count": 15,
    "events_count": 8
  }
}
```

**Service层**: `ParameterService.get_parameter_details(param_name, game_gid)`

---

### GET /api/parameters/stats (Phase 5新增)

获取参数统计信息。

**查询参数**:
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| game_gid | int | ✅ | 游戏业务GID |

**请求示例**:
```bash
GET /api/parameters/stats?game_gid=10000147
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total_parameters": 450,
    "unique_parameters": 150,
    "common_parameters": 25,
    "type_distribution": {
      "int": 120,
      "string": 180,
      "bigint": 75,
      "double": 75
    },
    "top_parameters": [
      {
        "param_name": "role_id",
        "usage_count": 45,
        "events_count": 15
      }
    ]
  }
}
```

**Service层**: `ParameterService.get_parameter_stats(game_gid)`

---

### POST /api/parameters/search (Phase 5新增)

搜索参数。

**请求体**:
```json
{
  "game_gid": 10000147,
  "keyword": "role",
  "data_type": "int"
}
```

**字段验证**:
| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| game_gid | int | ✅ | 游戏业务GID |
| keyword | string | ✅ | 搜索关键词 |
| data_type | string | ❌ | 数据类型过滤 |

**请求示例**:
```bash
POST /api/parameters/search
Content-Type: application/json

{
  "game_gid": 10000147,
  "keyword": "level"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "param_name": "level",
      "param_name_cn": "等级",
      "base_type": "int",
      "events_count": 5,
      "usage_count": 12
    },
    {
      "param_name": "old_level",
      "param_name_cn": "旧等级",
      "base_type": "int",
      "events_count": 2,
      "usage_count": 3
    }
  ]
}
```

**Service层**: `ParameterService.search_parameters(keyword, game_gid, data_type)`

---

### GET /api/parameters/common

获取通用参数列表。

**查询参数**:
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| game_gid | int | ✅ | 游戏业务GID |

**请求示例**:
```bash
GET /api/parameters/common?game_gid=10000147
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "param_name": "role_id",
      "param_name_cn": "角色ID",
      "param_type": "int",
      "events": ["login", "logout", "level_up"]
    },
    {
      "param_name": "zone_id",
      "param_name_cn": "区域ID",
      "param_type": "string",
      "events": ["login", "enter_zone"]
    }
  ]
}
```

**Service层**: `ParameterService.get_common_params(game_gid)`

---

### GET /api/parameters/validate

验证参数名称。

**查询参数**:
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| game_gid | int | ❌ | 游戏业务GID |
| param_name | string | ✅ | 参数名称 |

**请求示例**:
```bash
GET /api/parameters/validate?game_gid=10000147&param_name=role_id
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "valid": true,
    "exists": true,
    "suggestions": []
  }
}
```

**Service层**: `ParameterService.validate_parameter_name(param_name, game_gid)`

---

## 参数库管理

### GET /api/param-library/check

检查参数是否存在于参数库。

**查询参数**:
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| param_name | string | ✅ | 参数名称 |
| template_id | int | ✅ | 模板ID |

**请求示例**:
```bash
GET /api/param-library/check?param_name=role_id&template_id=1
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "exists": true,
    "library_param": {
      "id": 10,
      "param_name": "role_id",
      "param_name_cn": "角色ID",
      "template_id": 1
    }
  }
}
```

---

### POST /api/event-params/<param_id>/link-library

关联事件参数到参数库。

**路径参数**:
| 参数 | 类型 | 描述 |
|------|------|------|
| param_id | int | 事件参数ID |

**请求体**:
```json
{
  "library_id": 10
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "参数已关联到库",
  "data": {
    "event_param_id": 5,
    "library_id": 10
  }
}
```

---

### POST /api/param-library/batch-check

批量检查参数库。

**请求体**:
```json
{
  "parameters": [
    {"param_name": "role_id", "template_id": 1},
    {"param_name": "zone_id", "template_id": 2}
  ]
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "role_id": {
      "exists": true,
      "library_param": {...}
    },
    "zone_id": {
      "exists": false,
      "library_param": null
    }
  }
}
```

---

## ALTER TABLE SQL生成

### GET /api/alter-table/<param_id>

生成ALTER TABLE SQL语句。

**路径参数**:
| 参数 | 类型 | 描述 |
|------|------|------|
| param_id | int | 通用参数ID |

**请求示例**:
```bash
GET /api/alter-table/1
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "param": {
      "id": 1,
      "param_name": "zone_id",
      "param_name_cn": "区域ID",
      "param_type": "string",
      "table_name": "dwd_common_params",
      "game_name": "STAR001",
      "gid": 10000147
    },
    "alter_sql": "-- ALTER TABLE Statement\nALTER TABLE dwd_common_params ADD COLUMN IF NOT EXISTS zone_id STRING COMMENT '区域ID';"
  }
}
```

**Service层**: `ParameterService.get_alter_table_sql(param_id)`

---

## 性能优化

### 分层缓存

**L1缓存（热数据）**:
- TTL: 60秒
- 容量: 1000条
- 命中率: 70%

**L2缓存（共享缓存）**:
- TTL: 300秒
- 容量: 无限制
- 命中率: 85%

**性能提升**:
| 操作 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 获取参数列表 | 267ms | 88ms | 67% |
| 搜索参数 | 350ms | 120ms | 66% |
| 参数统计 | 420ms | 150ms | 64% |

---

## 使用场景

### 1. 获取参数列表（分页）

```javascript
const page = 1;
const limit = 50;
const response = await fetch(
  `/api/parameters/all?game_gid=10000147&page=${page}&limit=${limit}`
);
const data = await response.json();

console.log(`Total: ${data.data.total}`);
console.log(`Has more: ${data.data.has_more}`);

data.data.parameters.forEach(param => {
  console.log(`${param.param_name}: ${param.usage_count}次使用`);
});
```

### 2. 搜索参数

```javascript
const result = await fetch('/api/parameters/search', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    game_gid: 10000147,
    keyword: 'level',
    data_type: 'int'
  })
}).then(r => r.json());

result.data.forEach(param => {
  console.log(`Found: ${param.param_name} (${param.events_count} events)`);
});
```

### 3. 生成ALTER TABLE SQL

```javascript
const paramId = 1;
const result = await fetch(`/api/alter-table/${paramId}`)
  .then(r => r.json());

console.log('ALTER TABLE SQL:');
console.log(result.data.alter_sql);
```

---

## 相关文档

- [Events API](EVENTS-API.md) - 事件管理
- [Categories API](CATEGORIES-API.md) - 分类管理
- [缓存系统](../cache/README.md) - 分层缓存详解
