# Event2Table API 文档

**V9.0.0架构** - Repository Pattern Migration

**版本**: 9.0.0
**最后更新**: 2026-03-03
**架构**: ERS (Entity-Repository-Service) + Repository Pattern
**API统计**: REST API 84端点 | GraphQL 78操作
**迁移状态**: 6/8核心模块已迁移到Repository模式 (75%)

---

## 快速开始

### 基础信息

- **Base URL**: `http://127.0.0.1:5001/api`
- **数据格式**: JSON
- **字符编码**: UTF-8
- **认证方式**: Session-based (via Flask session)

### 统一响应格式

所有API响应遵循统一格式：

```json
{
  "success": true/false,
  "data": {...},
  "message": "操作成功",
  "error": "错误信息（仅错误时）"
}
```

### HTTP状态码

| 状态码 | 描述 | 使用场景 |
|--------|------|----------|
| 200 | OK | 请求成功 |
| 400 | Bad Request | 请求参数错误 |
| 404 | Not Found | 资源未找到 |
| 409 | Conflict | 资源冲突（如重复创建） |
| 500 | Internal Server Error | 服务器错误 |

### Critical Rules ⚠️

**1. Use Correct Endpoint Names**

❌ **WRONG**:
```javascript
fetch('/api/parameters')  // 404 Not Found
```

✅ **CORRECT**:
```javascript
fetch('/api/parameters/all?game_gid=10000147')  // 200 OK
```

**2. Always Pass `game_gid` Parameter**

❌ **WRONG**:
```javascript
fetch('/api/categories')  // 400 Bad Request: "game_gid required"
```

✅ **CORRECT**:
```javascript
fetch('/api/categories?game_gid=10000147')  // 200 OK
```

**3. Handle Pagination**

```javascript
// Page 1 (default)
fetch('/api/parameters/all?game_gid=10000147&page=1&limit=50')

// Page 2
fetch('/api/parameters/all?game_gid=10000147&page=2&limit=50')
```

---

## 架构概述 (V9.0.0)

### 双API架构

**REST API + GraphQL**:
- ✅ **REST API**: 84个端点，传统HTTP接口
- ✅ **GraphQL API**: 78个操作，113次调用，灵活查询
- ✅ **统一架构**: 共享Entity-Repository-Service层
- ✅ **渐进迁移**: REST → GraphQL平滑过渡

### ERS架构 (Entity-Repository-Service)

**100% ERS架构覆盖**:

```
┌─────────────────────────────────────────────────────┐
│         API Layer (HTTP + GraphQL端点)               │
│  - RESTful API: backend/api/routes/                  │
│  - GraphQL API: backend/gql_api/ (V2)               │
│  - 处理HTTP请求/响应                                  │
│  - 参数解析和验证 (Pydantic Entity)                   │
│  - 调用Service层                                      │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│           Service Layer (业务逻辑)                   │
│  backend/services/                                   │
│  - 实现业务逻辑                                       │
│  - 协调多个Repository                                │
│  - 缓存管理 (@cached, @cache_invalidate)             │
│  - Bloom Filter集成                                  │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│        Repository Layer (数据访问)                   │
│  backend/models/repositories/                        │
│  - GenericRepository基类                             │
│  - 封装数据访问逻辑                                   │
│  - CRUD操作                                          │
│  - 返回Entity对象 (而非Dict) ⭐                       │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│      Entity Layer (统一数据模型) ⭐                    │
│  - Pydantic Entity: backend/models/entities.py       │
│  - 单一真相来源 (Schema + Domain Model)              │
│  - 自动输入验证                                       │
│  - 序列化/反序列化                                    │
└─────────────────────────────────────────────────────┘
```

---

## API端点索引

### Categories API (8 endpoints)

| 方法 | 端点 | 描述 | Phase |
|------|------|------|-------|
| GET | `/api/categories` | 列出分类 | Phase 1 |
| GET | `/api/categories/<id>` | 获取单个分类 | Phase 1 |
| POST | `/api/categories` | 创建分类 | Phase 1 |
| PUT/PATCH | `/api/categories/<id>` | 更新分类 | Phase 1 |
| DELETE | `/api/categories/<id>` | 删除分类 | Phase 1 |
| POST | `/api/categories/batch-delete` | 批量删除分类 | Phase 3 |
| PUT | `/api/categories/batch-update` | 批量更新分类 | Phase 5 |
| GET | `/api/categories/stats` | 获取分类统计 | Phase 5 |

**详细文档**: [CATEGORIES-API.md](CATEGORIES-API.md)

**使用示例**:
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

---

### Events API (8 endpoints)

| 方法 | 端点 | 描述 | Phase |
|------|------|------|-------|
| GET | `/api/events` | 列出事件（分页） | Phase 3 |
| GET | `/api/events/<id>` | 获取事件详情 | Phase 1 |
| POST | `/api/events` | 创建事件 | Phase 1 |
| PUT/PATCH | `/api/events/<id>` | 更新事件 | Phase 1 |
| DELETE | `/api/events/batch` | 批量删除事件 | Phase 3 |
| PUT | `/api/events/batch-update` | 批量更新事件 | Phase 5 |
| GET | `/api/events/<id>/parameters` | 获取事件参数 | Phase 2 |
| GET | `/api/events/<event_id>/params` | 获取参数（别名） | Phase 2 |

**详细文档**: [EVENTS-API.md](EVENTS-API.md)

---

### Parameters API (16 endpoints)

#### 基础CRUD

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/parameters/all` | 获取所有参数（去重） |
| GET | `/api/parameters/<id>` | 获取单个参数 |
| POST | `/api/parameters` | 创建参数 |
| PUT | `/api/parameters/<id>` | 更新参数 |
| DELETE | `/api/parameters/<id>` | 删除参数 |

#### 查询和统计

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/parameters/<param_name>/details` | 获取参数详情 |
| GET | `/api/parameters/stats` | 获取参数统计 |
| POST | `/api/parameters/search` | 搜索参数 |
| GET | `/api/parameters/common` | 获取通用参数 |
| GET | `/api/parameters/validate` | 验证参数名称 |

#### 参数库管理

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/param-library/check` | 检查参数库 |
| POST | `/api/event-params/<param_id>/link-library` | 关联到参数库 |
| POST | `/api/param-library/batch-check` | 批量检查参数库 |

#### 其他功能

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/alter-table/<param_id>` | 生成ALTER TABLE SQL |

**详细文档**: [PARAMETERS-API.md](PARAMETERS-API.md)

---

### Field Builder API (6 endpoints)

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/field-builder/configs` | 列出配置 |
| GET | `/api/field-builder/configs/<id>` | 获取配置 |
| POST | `/api/field-builder/configs` | 创建配置 |
| PUT/PATCH | `/api/field-builder/configs/<id>` | 更新配置 |
| DELETE | `/api/field-builder/configs/<id>` | 删除配置 |
| POST | `/api/field-builder/preview` | 预览HQL |

**详细文档**: [FIELD-BUILDER-API.md](FIELD-BUILDER-API.md)

---

### Games API (7 endpoints)

| 方法 | 端点 | 描述 | Phase |
|------|------|------|-------|
| GET | `/api/games` | 列出游戏 | Phase 1 |
| GET | `/api/games/<id>` | 获取单个游戏 | Phase 1 |
| POST | `/api/games` | 创建游戏 | Phase 1 |
| PUT/PATCH | `/api/games/<id>` | 更新游戏 | Phase 1 |
| DELETE | `/api/games/<id>` | 删除游戏 | Phase 3 |
| GET | `/api/games/<gid>/stats` | 获取游戏统计 | Phase 2 |
| POST | `/api/games/<gid>/clone` | 克隆游戏配置 | Phase 4 |

**详细文档**: [GAMES-API.md](GAMES-API.md)

---

### Flows API (6 endpoints)

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/flows` | 列出流程 |
| GET | `/api/flows/<id>` | 获取单个流程 |
| POST | `/api/flows` | 创建流程 |
| PUT/PATCH | `/api/flows/<id>` | 更新流程 |
| DELETE | `/api/flows/<id>` | 删除流程 |
| POST | `/api/flows/<flow_id>/generate-hql` | 生成HQL |

**详细文档**: [FLOWS-API.md](FLOWS-API.md)

---

### Canvas API (4 endpoints)

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/canvas` | 列出Canvas |
| GET | `/api/canvas/<id>` | 获取Canvas |
| POST | `/api/canvas` | 创建/保存Canvas |
| POST | `/api/canvas/<canvas_id>/generate-hql` | 生成HQL |

**Note**: Canvas API endpoints are documented in the Canvas module documentation.

---

### Event Nodes API (5 endpoints)

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/event-nodes` | 列出事件节点 |
| GET | `/api/event-nodes/<id>` | 获取单个节点 |
| POST | `/api/event-nodes` | 创建节点 |
| PUT/PATCH | `/api/event-nodes/<id>` | 更新节点 |
| DELETE | `/api/event-nodes/<id>` | 删除节点 |

**Note**: Event Nodes API is documented in the Canvas module documentation.

---

### Join Configs API (8 endpoints)

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/join-configs` | 列出Join配置 |
| GET | `/api/join-configs/<id>` | 获取单个配置 |
| POST | `/api/join-configs` | 创建配置 |
| PUT/PATCH | `/api/join-configs/<id>` | 更新配置 |
| DELETE | `/api/join-configs/<id>` | 删除配置 |
| POST | `/api/join-configs/<config_id>/clone` | 克隆配置 |
| GET | `/api/join-configs/stats` | 获取配置统计 |
| POST | `/api/join-configs/batch-delete` | 批量删除 |

**Note**: Join Configs API documentation is available in the HQL module documentation.

---

### Dashboard API (3 endpoints)

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/dashboard/stats` | 获取Dashboard统计 |
| GET | `/api/dashboard/recent-events` | 获取最近事件 |
| GET | `/api/dashboard/system-health` | 系统健康检查 |

**Note**: Dashboard API is documented in the Dashboard module documentation.

---

### Import/Export API (4 endpoints)

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/import/events` | 导入事件 |
| POST | `/api/import/validate` | 验证导入数据 |
| GET | `/api/export/hql/<event_id>` | 导出HQL |
| POST | `/api/export/batch` | 批量导出 |

**Note**: Import/Export API is documented in the Events module documentation.

---

### GraphQL API (78 operations)

**端点**: `http://127.0.0.1:5001/graphql`

**查询 (Queries)**: 27个
**变更 (Mutations)**: 34个
**订阅 (Subscriptions)**: 8个

**快速开始**:
```javascript
import { useQuery, gql } from '@apollo/client';

const GET_GAMES = gql`
  query GetGames($limit: Int) {
    games(limit: $limit) {
      id
      gid
      name
      isActive
    }
  }
`;

function GamesList() {
  const { loading, error, data } = useQuery(GET_GAMES, {
    variables: { limit: 10 }
  });

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;

  return data.games.map(game => (
    <div key={game.id}>{game.name}</div>
  ));
}
```

**完整文档**: [GRAPHQL-API.md](GRAPHQL-API.md)

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
  "error": "Validation error: game_name is required",
  "message": "Game name is required. Must be 1-100 characters."
}
```

**404 Not Found - 资源不存在**:
```json
{
  "success": false,
  "error": "Game 10000147 not found",
  "message": "Game 10000147 not found. Check the gid or create the game first."
}
```

**409 Conflict - 资源冲突**:
```json
{
  "success": false,
  "error": "Game 10000147 already exists",
  "message": "Game 10000147 already exists. Use PUT to update or DELETE to remove."
}
```

**500 Internal Server Error - 服务器错误**:
```json
{
  "success": false,
  "error": "Internal server error",
  "message": "Internal server error. Please try again later or contact support."
}
```

---

## 性能优化

### 缓存策略

**Redis缓存**:
- 游戏列表: TTL 1800秒 (30分钟)
- 事件列表: TTL 300秒 (5分钟)
- 参数列表: TTL 600秒 (10分钟)
- Dashboard统计: TTL 120秒 (2分钟)

**缓存失效**:
- 创建/更新/删除操作后自动失效相关缓存
- 使用`CacheInvalidator`统一管理

### DataLoader优化

**批量加载**:
- EventLoader: ↓82% 查询次数
- ParameterLoader: ↓98% 查询次数
- CategoryLoader: ↓98% 查询次数

### 分页支持

**标准分页参数**:
- `page`: 页码（默认1）
- `limit`: 每页数量（默认20，最大100）
- `sort_by`: 排序字段
- `sort_order`: 排序方向（asc/desc）

---

## 相关文档

- **[GraphQL API文档](GRAPHQL_API.md)** - GraphQL完整文档
- **[REST到GraphQL迁移指南](REST_TO_GRAPHQL_MIGRATION.md)** - 迁移指南
- **[迁移进度报告](MIGRATION_PROGRESS_REPORT.md)** - 迁移进度
- **[经验文档 - API设计模式](../lessons-learned/api-design-patterns.md)** - API设计最佳实践
- **[经验文档 - 缓存策略](../lessons-learned/performance-patterns.md#缓存策略)** - 缓存使用规范
- **[经验文档 - 安全要点](../lessons-learned/security-essentials.md)** - API安全规范

---

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 9.0.0 | 2026-03-03 | Repository Pattern迁移，75%完成 |
| 8.0.0 | 2026-02-25 | GraphQL API完全集成 |
| 7.0.0 | 2026-02-20 | 双API架构（REST + GraphQL）|
| 6.0.0 | 2026-02-18 | game_gid迁移完成 |
| 5.0.0 | 2026-02-15 | ERS架构实施 |
| 4.0.0 | 2026-02-10 | API契约测试系统 |
| 3.0.0 | 2026-02-05 | 缓存系统集成 |
| 2.0.0 | 2026-01-30 | Service层重构 |
| 1.0.0 | 2026-01-15 | 初始版本 |
