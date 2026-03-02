# GraphQL API文档

> **最后更新**: 2026-03-02
> **状态**: 活跃开发
> **使用率**: 84.3% (113次调用)

---

## 快速开始

### 端点

**GraphQL Endpoint**: `http://127.0.0.1:5001/graphql`

### 认证

```bash
# 使用curl访问GraphQL
curl -X POST http://127.0.0.1:5001/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ games { gid name } }"}'
```

### Playground

**GraphQL Playground**: `http://127.0.0.1:5001/graphql-playground`

---

## 查询 (Queries)

### 游戏管理

```graphql
# 获取所有游戏
query GetGames {
  games {
    gid
    name
    odsDb
    description
    eventCount
  }
}

# 根据GID获取游戏
query GetGameByGid($gid: Int!) {
  game(gid: $gid) {
    gid
    name
    odsDb
    description
  }
}

# 搜索游戏
query SearchGames($name: String!) {
  searchGames(name: $name) {
    gid
    name
    odsDb
  }
}
```

### 事件管理

```graphql
# 获取所有事件
query GetEvents($gameGid: Int!) {
  events(gameGid: $gameGid) {
    id
    name
    table
    category
  }
}

# 根据ID获取事件
query GetEventById($id: Int!) {
  event(id: $id) {
    id
    name
    table
    category
  }
}

# 搜索事件
query SearchEvents($name: String!, $gameGid: Int!) {
  searchEvents(name: $name, gameGid: $gameGid) {
    id
    name
    table
  }
}
```

### 参数管理

```graphql
# 获取所有参数
query GetParameters($gameGid: Int!) {
  parameters(gameGid: $gameGid) {
    id
    name
    type
    category
  }
}

# 获取公共参数
query GetCommonParameters($gameGid: Int!) {
  commonParams(gameGid: $gameGid) {
    id
    name
    type
  }
}

# 搜索参数
query SearchParameters($name: String!, $gameGid: Int!) {
  searchParameters(name: $name, gameGid: $gameGid) {
    id
    name
    type
  }
}
```

---

## 变更 (Mutations)

### 游戏管理

```graphql
# 创建游戏
mutation CreateGame($input: GameCreateInput!) {
  createGame(input: $input) {
    gid
    name
    odsDb
  }
}

# 更新游戏
mutation UpdateGame($gid: Int!, $input: GameUpdateInput!) {
  updateGame(gid: $gid, input: $input) {
    gid
    name
    odsDb
  }
}

# 删除游戏
mutation DeleteGame($gid: Int!) {
  deleteGame(gid: $gid) {
    success
    message
  }
}
```

### 事件管理

```graphql
# 创建事件
mutation CreateEvent($input: EventCreateInput!) {
  createEvent(input: $input) {
    id
    name
    table
  }
}

# 更新事件
mutation UpdateEvent($id: Int!, $input: EventUpdateInput!) {
  updateEvent(id: $id, input: $input) {
    id
    name
    table
  }
}

# 删除事件
mutation DeleteEvent($id: Int!) {
  deleteEvent(id: $id) {
    success
    message
  }
}
```

### 参数管理

```graphql
# 创建参数
mutation CreateParameter($input: ParameterCreateInput!) {
  createParameter(input: $input) {
    id
    name
    type
  }
}

# 更新参数
mutation UpdateParameter($id: Int!, $input: ParameterUpdateInput!) {
  updateParameter(id: $id, input: $input) {
    id
    name
    type
  }
}

# 删除参数
mutation DeleteParameter($id: Int!) {
  deleteParameter(id: $id) {
    success
    message
  }
}
```

---

## 订阅 (Subscriptions)

> **注意**: 订阅功能正在开发中

```graphql
# 订阅游戏变更
subscription OnGameChange {
  gameChanged {
    gid
    name
    action
  }
}
```

---

## 类型定义

### Game

```graphql
type Game {
  gid: Int!
  name: String!
  odsDb: String!
  description: String
  eventCount: Int
  createdAt: DateTime
  updatedAt: DateTime
}
```

### Event

```graphql
type Event {
  id: Int!
  name: String!
  table: String!
  category: String
  gameGid: Int!
  createdAt: DateTime
  updatedAt: DateTime
}
```

### Parameter

```graphql
type Parameter {
  id: Int!
  name: String!
  type: String!
  category: String
  gameGid: Int!
  createdAt: DateTime
  updatedAt: DateTime
}
```

---

## 错误处理

### 错误格式

```json
{
  "errors": [
    {
      "message": "Game not found",
      "path": ["game"],
      "extensions": {
        "code": "GAME_NOT_FOUND",
        "timestamp": "2026-03-02T10:00:00Z"
      }
    }
  ],
  "data": {
    "game": null
  }
}
```

### 常见错误码

| 错误码 | 描述 | HTTP状态码 |
|--------|------|------------|
| `GAME_NOT_FOUND` | 游戏不存在 | 404 |
| `EVENT_NOT_FOUND` | 事件不存在 | 404 |
| `PARAMETER_NOT_FOUND` | 参数不存在 | 404 |
| `VALIDATION_ERROR` | 输入验证失败 | 400 |
| `INTERNAL_ERROR` | 内部服务器错误 | 500 |

---

## 性能优化

### 查询复杂度

```graphql
# ✅ 推荐：只查询需要的字段
query GetGamesOptimized {
  games {
    gid
    name
  }
}

# ❌ 避免：查询所有字段（性能问题）
query GetGamesAllFields {
  games {
    gid
    name
    odsDb
    description
    eventCount
    createdAt
    updatedAt
  }
}
```

### 分页

```graphql
# 使用分页减少数据传输
query GetEventsPaginated($gameGid: Int!, $page: Int!, $perPage: Int!) {
  events(gameGid: $gameGid, page: $page, perPage: $perPage) {
    id
    name
    table
  }
}
```

---

## 相关文档

### 设计文档
- [GraphQL Schema设计](../graphql-migration/V2_API_GRAPHQL_SCHEMA_DESIGN.md)
- [批量操作Schema设计](../graphql-migration/BATCH_OPERATIONS_GRAPHQL_SCHEMA_DESIGN.md)

### 迁移文档
- [REST到GraphQL迁移](./REST_TO_GRAPHQL_MIGRATION.md)
- [GraphQL迁移计划](../GRAPHQL_MIGRATION_PLAN.md)
- [GraphQL迁移进度](../GRAPHQL_MIGRATION_PROGRESS.md)
- [GraphQL迁移最终报告](../GRAPHQL_MIGRATION_FINAL_REPORT.md)

### 实现文档
- [GraphQL API文档](../GRAPHQL_API_DOCUMENTATION.md)
- [GraphQL完整文档](../GRAPHQL_COMPLETE_DOCUMENTATION.md)

### 修改记录
- [GraphQL Mutations重构总结](../reports/2026-02-26/graphql-mutations-refactoring-summary.md)
- [GraphQL迁移速查表](../reports/2026-02-26/graphql-migrations-cheatsheet.md)

---

## 开发指南

### 本地开发

```bash
# 启动GraphQL服务器
python3 web_app.py

# 访问GraphQL Playground
open http://127.0.0.1:5001/graphql-playground
```

### 测试

```bash
# 运行GraphQL测试
pytest backend/test/graphql/ -v

# 验证Schema
python scripts/verify_graphql_schema.py
```

---

## 支持

如有问题，请查看：
- [API文档索引](./README.md)
- [经验文档 - API设计模式](../docs/lessons-learned/api-design-patterns.md)
- [GraphQL官方文档](https://graphql.org/learn/)
