# Event2Table API 文档

## 概述

Event2Table 提供了完整的 RESTful API，支持游戏管理、事件配置、参数管理、HQL生成、Canvas编辑、缓存管理等功能。

## API 版本

- **当前版本**: v2.1.0
- **基础路径**: `/api`
- **认证方式**: Bearer Token（可选）

## 核心模块

### 1. 游戏管理 API
- 文档: [GAMES-API.md](./GAMES-API.md)
- 功能: 游戏的创建、读取、更新、删除
- 端点:
  - `GET /api/games` - 获取游戏列表
  - `GET /api/games/<game_gid>` - 获取游戏详情
  - `POST /api/games` - 创建游戏
  - `PUT /api/games/<game_gid>` - 更新游戏
  - `DELETE /api/games/<game_gid>` - 删除游戏

### 2. 事件管理 API
- 文档: [EVENTS-API.md](./EVENTS-API.md)
- 功能: 事件的创建、读取、更新、删除、批量操作
- 端点:
  - `GET /api/events` - 获取事件列表
  - `GET /api/events/<event_id>` - 获取事件详情
  - `POST /api/events` - 创建事件
  - `PUT /api/events/<event_id>` - 更新事件
  - `DELETE /api/events/<event_id>` - 删除事件
  - `POST /api/events/batch-delete` - 批量删除事件

### 3. 参数管理 API
- 文档: [PARAMETERS-API.md](./PARAMETERS-API.md)
- 功能: 参数的创建、读取、更新、删除、别名管理
- 端点:
  - `GET /api/parameters` - 获取参数列表
  - `GET /api/parameters/<param_id>` - 获取参数详情
  - `POST /api/parameters` - 创建参数
  - `PUT /api/parameters/<param_id>` - 更新参数
  - `DELETE /api/parameters/<param_id>` - 删除参数

### 4. 字段构建器 API
- 文档: [FIELD-BUILDER-API.md](./FIELD-BUILDER-API.md)
- 功能: 字段构建、字段推荐、字段验证
- 端点:
  - `GET /api/field-builder/recommend` - 推荐字段
  - `POST /api/field-builder/build` - 构建字段
  - `POST /api/field-builder/validate` - 验证字段

### 5. Canvas 编辑器 API
- 文档: [CANVAS-API.md](./CANVAS-API.md)
- 功能: Canvas节点管理、连接管理、布局管理
- 端点:
  - `GET /api/canvas/<canvas_id>` - 获取Canvas
  - `POST /api/canvas` - 创建Canvas
  - `PUT /api/canvas/<canvas_id>` - 更新Canvas
  - `DELETE /api/canvas/<canvas_id>` - 删除Canvas

### 6. HQL 生成器 API
- 文档: [HQL-PREVIEW-V2-API.md](./hql/HQL-PREVIEW-V2-API.md)
- 功能: HQL生成、预览、验证、缓存
- 端点:
  - `POST /hql-preview-v2/api/preview` - 预览HQL
  - `POST /hql-preview-v2/api/generate` - 生成完整HQL
  - `POST /hql-preview-v2/api/validate` - 验证HQL
  - `GET /hql-preview-v2/api/status` - API状态
  - `GET /hql-preview-v2/api/cache-stats` - 缓存统计

### 7. 事件节点 API
- 文档: [EVENT-NODES-API.md](./EVENT-NODES-API.md)
- 功能: 事件节点管理、节点连接、节点验证
- 端点:
  - `GET /api/event-nodes` - 获取事件节点列表
  - `GET /api/event-nodes/<node_id>` - 获取节点详情
  - `POST /api/event-nodes` - 创建节点
  - `PUT /api/event-nodes/<node_id>` - 更新节点
  - `DELETE /api/event-nodes/<node_id>` - 删除节点

### 8. 分类管理 API
- 文档: [CATEGORIES-API.md](./CATEGORIES-API.md)
- 功能: 事件分类管理
- 端点:
  - `GET /api/categories` - 获取分类列表
  - `GET /api/categories/<category_id>` - 获取分类详情
  - `POST /api/categories` - 创建分类
  - `PUT /api/categories/<category_id>` - 更新分类
  - `DELETE /api/categories/<category_id>` - 删除分类
  - `POST /api/categories/batch-delete` - 批量删除分类

### 9. 仪表盘 API
- 文档: [DASHBOARD-API.md](./DASHBOARD-API.md)
- 功能: 统计数据、概览信息
- 端点:
  - `GET /api/dashboard/stats` - 获取统计数据
  - `GET /api/dashboard/overview` - 获取概览信息

### 10. 导入导出 API
- 文档: [IMPORT-EXPORT-API.md](./IMPORT-EXPORT-API.md)
- 功能: 事件导入导出、数据迁移
- 端点:
  - `POST /api/import/events` - 导入事件
  - `POST /api/export/events` - 导出事件
  - `GET /api/export/template` - 获取导入模板

### 11. GraphQL API
- 文档: [GRAPHQL-API.md](./GRAPHQL-API.md)
- 功能: GraphQL查询和变更
- 端点:
  - `POST /graphql` - GraphQL端点

### 12. 缓存管理 API
- 文档: [CACHE-API.md](./CACHE-API.md)
- 功能: 缓存统计、缓存清理、缓存预热
- 端点:
  - `GET /api/cache/stats` - 获取缓存统计
  - `POST /api/cache/clear` - 清空缓存
  - `POST /api/cache/warmup` - 缓存预热

### 13. 异步任务 API ⭐ 新增 (v2.1.0)
- 文档: [ASYNC-TASKS-API.md](./ASYNC-TASKS-API.md)
- 功能: 异步任务提交、状态查询、结果获取
- 端点:
  - `POST /api/async-tasks` - 提交异步任务
  - `GET /api/async-tasks/<task_id>` - 查询任务状态
  - `GET /api/async-tasks/<task_id>/result` - 获取任务结果
  - `GET /api/async-tasks` - 获取任务列表
  - `DELETE /api/async-tasks/<task_id>` - 取消任务

## 请求/响应格式

### 请求格式

所有API请求使用JSON格式：

```json
{
  "field1": "value1",
  "field2": "value2"
}
```

### 响应格式

#### 成功响应

```json
{
  "success": true,
  "data": {
    // 响应数据
  },
  "message": "操作成功"
}
```

#### 错误响应

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {}
  }
}
```

## 通用错误码

| 错误码 | HTTP状态码 | 描述 |
|--------|-----------|------|
| `INVALID_REQUEST` | 400 | 请求参数无效 |
| `UNAUTHORIZED` | 401 | 未授权 |
| `FORBIDDEN` | 403 | 禁止访问 |
| `NOT_FOUND` | 404 | 资源不存在 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 |

## 分页参数

所有列表API支持分页：

```
GET /api/games?page=1&page_size=20&sort_by=name&order=asc
```

参数说明：
- `page`: 页码（从1开始）
- `page_size`: 每页数量（默认20，最大100）
- `sort_by`: 排序字段
- `order`: 排序方向（asc/desc）

## 过滤参数

列表API支持过滤：

```
GET /api/events?game_gid=100001&category_id=5&status=active
```

## 异步任务使用示例

### 1. 提交异步任务

```bash
POST /api/async-tasks
Content-Type: application/json

{
  "task_type": "hql_generation",
  "params": {
    "event_id": 123,
    "mode": "join",
    "parameters": {...}
  }
}
```

响应：
```json
{
  "success": true,
  "data": {
    "task_id": "task_abc123",
    "status": "pending",
    "created_at": "2026-03-20T01:00:00Z"
  }
}
```

### 2. 查询任务状态

```bash
GET /api/async-tasks/task_abc123
```

响应：
```json
{
  "success": true,
  "data": {
    "task_id": "task_abc123",
    "status": "completed",
    "progress": 100,
    "result": {...},
    "created_at": "2026-03-20T01:00:00Z",
    "updated_at": "2026-03-20T01:00:05Z"
  }
}
```

### 3. 获取任务结果

```bash
GET /api/async-tasks/task_abc123/result
```

响应：
```json
{
  "success": true,
  "data": {
    "task_id": "task_abc123",
    "result": {
      "hql": "SELECT ...",
      "execution_time": 5000
    }
  }
}
```

## 性能优化建议

1. **使用缓存**: 对于频繁访问的数据，使用缓存API
2. **批量操作**: 使用批量API减少请求次数
3. **异步任务**: 对于耗时操作，使用异步任务API
4. **分页查询**: 大数据量查询使用分页
5. **字段过滤**: 只请求需要的字段

## 版本历史

- **v2.1.0** (2026-03-20): 新增异步任务API
- **v2.0.0** (2026-02-22): game_gid迁移，API重构
- **v1.0.0**: 初始版本

## 相关文档

- [用户手册](../user-guide/)
- [开发文档](../development/)
- [架构文档](../development/architecture.md)
- [API状态](./API_STATUS.md)

## 支持

如有问题，请联系：
- GitHub Issues: [Event2Table/issues](https://github.com/your-org/event2table/issues)
- 文档: [Event2Table Documentation](https://docs.event2table.com)
