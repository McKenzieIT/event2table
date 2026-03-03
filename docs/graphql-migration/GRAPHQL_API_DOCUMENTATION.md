# GraphQL API 文档

**版本**: 1.0  
**最后更新**: 2026-02-24  
**基础URL**: `/graphql`

---

## 📋 目录

1. [概述](#概述)
2. [快速开始](#快速开始)
3. [查询](#查询)
4. [变更](#变更)
5. [订阅](#订阅)
6. [类型定义](#类型定义)
7. [最佳实践](#最佳实践)
8. [性能优化](#性能优化)
9. [错误处理](#错误处理)

---

## 概述

Event2Table GraphQL API 提供了灵活、高效的数据查询和变更接口。相比REST API,GraphQL具有以下优势:

- ✅ **单次请求获取多个资源** - 减少网络请求次数
- ✅ **精确查询所需字段** - 避免数据冗余
- ✅ **强类型系统** - 提供完整的类型安全
- ✅ **实时订阅** - 支持WebSocket实时更新

---

## 快速开始

### GraphiQL IDE

访问 `/graphiql` 使用交互式GraphQL IDE进行查询测试。

### 基本查询示例

```graphql
query GetGames {
  games(limit: 10, offset: 0) {
    gid
    name
    eventCount
    parameterCount
  }
}
```

### 基本变更示例

```graphql
mutation CreateGame {
  createGame(gid: 123, name: "新游戏", odsDb: "game_db") {
    ok
    game {
      gid
      name
    }
    errors
  }
}
```

---

## 查询

### Games 查询

#### 获取游戏列表
```graphql
query GetGames($limit: Int, $offset: Int) {
  games(limit: $limit, offset: $offset) {
    gid
    name
    odsDb
    eventCount
    parameterCount
  }
}
```

#### 获取单个游戏
```graphql
query GetGame($gid: Int!) {
  game(gid: $gid) {
    gid
    name
    odsDb
    eventCount
    parameterCount
  }
}
```

#### 搜索游戏
```graphql
query SearchGames($query: String!) {
  searchGames(query: $query) {
    gid
    name
    odsDb
  }
}
```

### Events 查询

#### 获取事件列表
```graphql
query GetEvents($gameGid: Int!, $category: String, $limit: Int, $offset: Int) {
  events(gameGid: $gameGid, category: $category, limit: $limit, offset: $offset) {
    id
    eventName
    eventNameCn
    categoryName
    paramCount
  }
}
```

#### 获取单个事件
```graphql
query GetEvent($id: Int!) {
  event(id: $id) {
    id
    gameGid
    eventName
    eventNameCn
    categoryId
    categoryName
    sourceTable
    targetTable
    paramCount
  }
}
```

### Dashboard 查询

#### 获取仪表板统计
```graphql
query GetDashboardStats {
  dashboardStats {
    totalGames
    totalEvents
    totalParameters
    totalCategories
    eventsLast7Days
    parametersLast7Days
  }
}
```

#### 获取游戏统计
```graphql
query GetGameStats($gameGid: Int!) {
  gameStats(gameGid: $gameGid) {
    gameGid
    gameName
    eventCount
    parameterCount
    categoryCount
  }
}
```

---

## 变更

### Game 变更

#### 创建游戏
```graphql
mutation CreateGame($gid: Int!, $name: String!, $odsDb: String!) {
  createGame(gid: $gid, name: $name, odsDb: $odsDb) {
    ok
    game {
      gid
      name
      odsDb
    }
    errors
  }
}
```

#### 更新游戏
```graphql
mutation UpdateGame($gid: Int!, $name: String, $odsDb: String) {
  updateGame(gid: $gid, name: $name, odsDb: $odsDb) {
    ok
    game {
      gid
      name
      odsDb
    }
    errors
  }
}
```

#### 删除游戏
```graphql
mutation DeleteGame($gid: Int!, $confirm: Boolean) {
  deleteGame(gid: $gid, confirm: $confirm) {
    ok
    message
    errors
  }
}
```

### Event 变更

#### 创建事件
```graphql
mutation CreateEvent(
  $gameGid: Int!
  $eventName: String!
  $eventNameCn: String!
  $categoryId: Int!
  $includeInCommonParams: Boolean
) {
  createEvent(
    gameGid: $gameGid
    eventName: $eventName
    eventNameCn: $eventNameCn
    categoryId: $categoryId
    includeInCommonParams: $includeInCommonParams
  ) {
    ok
    event {
      id
      eventName
      eventNameCn
    }
    errors
  }
}
```

### 批量操作

#### 批量删除事件
```graphql
mutation BatchDeleteEvents($ids: [Int!]!) {
  batchDeleteEvents(ids: $ids) {
    ok
    deletedCount
    message
    errors
  }
}
```

---

## 订阅

### 实时事件更新
```graphql
subscription OnEventUpdated($gameGid: Int!) {
  eventUpdated(gameGid: $gameGid) {
    id
    eventName
    eventNameCn
    updatedAt
  }
}
```

### 实时参数更新
```graphql
subscription OnParameterUpdated($eventId: Int!) {
  parameterUpdated(eventId: $eventId) {
    id
    paramName
    paramNameCn
    updatedAt
  }
}
```

---

## 类型定义

### GameType
```graphql
type GameType {
  gid: Int!
  name: String!
  odsDb: String
  eventCount: Int
  parameterCount: Int
  createdAt: String
  updatedAt: String
}
```

### EventType
```graphql
type EventType {
  id: Int!
  gameGid: Int!
  eventName: String!
  eventNameCn: String!
  categoryId: Int
  categoryName: String
  sourceTable: String
  targetTable: String
  paramCount: Int
  createdAt: String
  updatedAt: String
}
```

### DashboardStatsType
```graphql
type DashboardStatsType {
  totalGames: Int!
  totalEvents: Int!
  totalParameters: Int!
  totalCategories: Int!
  eventsLast7Days: Int!
  parametersLast7Days: Int!
}
```

---

## 最佳实践

### 1. 查询优化

**✅ 推荐**: 只查询需要的字段
```graphql
query GetGames {
  games(limit: 10) {
    gid
    name
  }
}
```

**❌ 不推荐**: 查询所有字段
```graphql
query GetGames {
  games(limit: 10) {
    gid
    name
    odsDb
    eventCount
    parameterCount
    createdAt
    updatedAt
  }
}
```

### 2. 使用片段

```graphql
fragment GameFields on GameType {
  gid
  name
  eventCount
}

query GetGames {
  games(limit: 10) {
    ...GameFields
  }
}
```

### 3. 批量操作

使用批量mutation代替多次单独操作:
```graphql
mutation BatchDeleteEvents($ids: [Int!]!) {
  batchDeleteEvents(ids: $ids) {
    ok
    deletedCount
  }
}
```

---

## 性能优化

### 1. 使用DataLoader

GraphQL API使用DataLoader来优化N+1查询问题:
- 自动批量加载关联数据
- 减少数据库查询次数
- 提高响应速度

### 2. 缓存策略

- **查询缓存**: 相同查询自动缓存
- **字段缓存**: 单个字段级别缓存
- **HTTP缓存**: 支持CDN缓存

### 3. 分页

使用limit和offset进行分页:
```graphql
query GetEvents($gameGid: Int!, $limit: Int, $offset: Int) {
  events(gameGid: $gameGid, limit: $limit, offset: $offset) {
    id
    eventName
  }
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
      "locations": [{ "line": 2, "column": 3 }],
      "path": ["game"],
      "extensions": {
        "code": "GAME_NOT_FOUND",
        "timestamp": "2026-02-24T12:00:00Z"
      }
    }
  ],
  "data": {
    "game": null
  }
}
```

### 常见错误码

- `GAME_NOT_FOUND` - 游戏不存在
- `EVENT_NOT_FOUND` - 事件不存在
- `VALIDATION_ERROR` - 数据验证失败
- `UNAUTHORIZED` - 未授权访问
- `RATE_LIMIT_EXCEEDED` - 请求频率超限

---

## 限制

### 查询复杂度限制

- 最大查询深度: 10层
- 最大查询复杂度: 1000
- 单次请求最多返回: 1000条记录

### 速率限制

- 每分钟最多: 100次请求
- 每小时最多: 5000次请求

---

## 工具和资源

### GraphiQL IDE
- URL: `/graphiql`
- 功能: 交互式查询测试、自动补全、文档浏览

### 性能监控
- 工具: `graphqlPerformanceMonitor.js`
- 功能: 实时监控、性能对比、报告生成

### 测试工具
- 脚本: `test_graphql_migration.py`
- 功能: 自动化测试、验证迁移

---

## 更新日志

### v1.0 (2026-02-24)
- ✅ 初始版本发布
- ✅ 核心查询和变更实现
- ✅ 5个页面迁移完成
- ✅ 性能监控工具集成
- ✅ 批量操作支持

---

**维护团队**: Event2Table开发团队  
**技术支持**: 查看项目文档或提交Issue
