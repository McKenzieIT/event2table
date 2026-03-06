# GraphQL API 文档

**版本**: 9.0.0
**最后更新**: 2026-03-05
**端点**: `http://127.0.0.1:5001/graphql`

---

## 概述

Event2Table提供完整的GraphQL API，支持灵活的数据查询和变更操作。GraphQL API与REST API共享相同的Entity-Repository-Service架构，提供统一的业务逻辑层。

### 特性

- **灵活查询**: 客户端精确指定需要的数据
- **批量操作**: 一次请求获取多个资源
- **类型安全**: 基于Pydantic Entity的强类型系统
- **性能优化**: DataLoader优化N+1查询问题
- **实时更新**: 支持Subscriptions（部分功能）

### 统计

- **查询操作**: 27个
- **变更操作**: 34个
- **订阅操作**: 8个
- **总操作数**: 78个

---

## 快速开始

### 基本请求

**端点**: `POST http://127.0.0.1:5001/graphql`

**请求示例**:
```javascript
fetch('http://127.0.0.1:5001/graphql', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: `
      query GetGames($limit: Int) {
        games(limit: $limit) {
          id
          gid
          name
          odsDb
          isActive
          eventCount
        }
      }
    `,
    variables: {
      limit: 10
    }
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

**响应示例**:
```json
{
  "data": {
    "games": [
      {
        "id": 1,
        "gid": 10000147,
        "name": "STAR001",
        "odsDb": "ieu_ods",
        "isActive": true,
        "eventCount": 57
      }
    ]
  }
}
```

### Apollo Client 集成

```javascript
import { ApolloClient, InMemoryCache, gql } from '@apollo/client';

const client = new ApolloClient({
  uri: 'http://127.0.0.1:5001/graphql',
  cache: new InMemoryCache()
});

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

// 使用useQuery Hook
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

---

## 核心操作

### 查询 (Queries)

#### Games

**GetGames** - 获取游戏列表
```graphql
query GetGames($limit: Int, $offset: Int) {
  games(limit: $limit, offset: $offset) {
    id
    gid
    name
    odsDb
    description
    isActive
    eventCount
    createdAt
  }
}
```

**GetGameByGid** - 根据GID获取游戏
```graphql
query GetGameByGid($gid: ID!) {
  gameByGid(gid: $gid) {
    id
    gid
    name
    odsDb
    description
  }
}
```

#### Events

**GetEvents** - 获取事件列表
```graphql
query GetEvents($gameGid: Int!, $limit: Int) {
  events(gameGid: $gameGid, limit: $limit) {
    id
    name
    tableName
    categoryId
    isActive
  }
}
```

**GetEventById** - 获取事件详情
```graphql
query GetEventById($eventId: ID!) {
  event(eventId: $eventId) {
    id
    name
    tableName
    category {
      id
      name
    }
    parameters {
      id
      name
      paramType
    }
  }
}
```

#### Parameters

**GetParameters** - 获取参数列表
```graphql
query GetParameters($gameGid: Int!) {
  parameters(gameGid: $gameGid) {
    id
    name
    paramType
    jsonPath
    isActive
  }
}
```

#### Categories

**GetCategories** - 获取分类列表
```graphql
query GetCategories($gameGid: Int!) {
  categories(gameGid: $gameGid) {
    id
    name
    description
    isActive
    eventCount
  }
}
```

#### Flows

**GetFlows** - 获取流程列表
```graphql
query GetFlows($gameGid: Int!) {
  flows(gameGid: $gameGid) {
    id
    flowName
    category
    description
    isActive
  }
}
```

#### Join Configs

**GetJoinConfigs** - 获取Join配置列表
```graphql
query GetJoinConfigs($gameGid: Int!) {
  joinConfigs(gameGid: $gameGid) {
    id
    configName
    joinType
    leftTable
    rightTable
    joinCondition
  }
}
```

### 变更 (Mutations)

#### Create Game
```graphql
mutation CreateGame($input: GameInput!) {
  createGame(input: $input) {
    id
    gid
    name
    odsDb
  }
}
```

**Variables**:
```json
{
  "input": {
    "gid": "90000001",
    "name": "Test Game",
    "odsDb": "ieu_ods",
    "description": "Test game description"
  }
}
```

#### Update Game
```graphql
mutation UpdateGame($gameId: ID!, $input: GameInput!) {
  updateGame(gameId: $gameId, input: $input) {
    id
    gid
    name
    odsDb
  }
}
```

#### Delete Game
```graphql
mutation DeleteGame($gameId: ID!) {
  deleteGame(gameId: $gameId) {
    success
    message
  }
}
```

#### Create Event
```graphql
mutation CreateEvent($input: EventInput!) {
  createEvent(input: $input) {
    id
    name
    tableName
    categoryId
  }
}
```

**Variables**:
```json
{
  "input": {
    "gameGid": 10000147,
    "name": "test_event",
    "tableName": "dwd.v_dwd_10000147_test_event_di",
    "categoryId": 1
  }
}
```

#### Create Parameter
```graphql
mutation CreateParameter($input: ParameterInput!) {
  createParameter(input: $input) {
    id
    name
    paramType
    jsonPath
  }
}
```

**Variables**:
```json
{
  "input": {
    "eventId": 1,
    "name": "zone_id",
    "paramType": "param",
    "jsonPath": "$.zoneId"
  }
}
```

#### Batch Delete Events
```graphql
mutation BatchDeleteEvents($eventIds: [ID!]!) {
  batchDeleteEvents(eventIds: $eventIds) {
    success
    deletedCount
    message
  }
}
```

### 订阅 (Subscriptions)

**EventCreated** - 订阅新事件创建
```graphql
subscription OnEventCreated($gameGid: Int!) {
  eventCreated(gameGid: $gameGid) {
    id
    name
    tableName
    createdAt
  }
}
```

**ParameterUpdated** - 订阅参数更新
```graphql
subscription OnParameterUpdated($gameGid: Int!) {
  parameterUpdated(gameGid: $gameGid) {
    id
    name
    paramType
    updatedAt
  }
}
```

---

## 错误处理

### 错误响应格式

```json
{
  "data": null,
  "errors": [
    {
      "message": "Validation error: game_gid is required",
      "path": ["games"],
      "extensions": {
        "code": "VALIDATION_ERROR",
        "statusCode": 400
      }
    }
  ]
}
```

### 常见错误

**400 Bad Request - 验证错误**:
```json
{
  "errors": [
    {
      "message": "Variable '$gid' got invalid value",
      "extensions": {
        "code": "BAD_USER_INPUT"
      }
    }
  ]
}
```

**404 Not Found - 资源不存在**:
```json
{
  "data": {
    "gameByGid": null
  },
  "errors": [
    {
      "message": "Game with gid 99999999 not found",
      "path": ["gameByGid"]
    }
  ]
}
```

**500 Internal Server Error**:
```json
{
  "data": null,
  "errors": [
    {
      "message": "Internal server error",
      "extensions": {
        "code": "INTERNAL_SERVER_ERROR"
      }
    }
  ]
}
```

---

## 性能优化

### DataLoader优化

GraphQL API使用DataLoader模式解决N+1查询问题：

**性能提升**:
- EventLoader: ↓82% 查询次数
- ParameterLoader: ↓98% 查询次数
- CategoryLoader: ↓98% 查询次数

**使用示例**:
```javascript
// DataLoader自动批量加载
const GET_EVENTS_WITH_PARAMS = gql`
  query GetEventsWithParams($gameGid: Int!) {
    events(gameGid: $gameGid) {
      id
      name
      parameters {  # DataLoader自动批量加载参数
        id
        name
        paramType
      }
      category {  # DataLoader自动批量加载分类
        id
        name
      }
    }
  }
`;
```

### 查询复杂度限制

**最大复杂度**: 1000
**最大深度**: 10

**超出限制的查询将被拒绝**:
```json
{
  "errors": [
    {
      "message": "Query has complexity 1500, which exceeds the maximum allowed complexity of 1000"
    }
  ]
}
```

### 缓存策略

**Apollo Client 缓存配置**:
```javascript
const client = new ApolloClient({
  uri: 'http://127.0.0.1:5001/graphql',
  cache: new InMemoryCache({
    typePolicies: {
      Query: {
        fields: {
          games: {
            merge(existing = [], incoming) {
              return incoming;  // 完全替换而非合并
            }
          }
        }
      }
    }
  })
});
```

---

## 类型系统

### 核心类型

**Game**:
```graphql
type Game {
  id: ID!
  gid: String!
  name: String!
  odsDb: String!
  description: String
  dwdPrefix: String
  isActive: Boolean!
  eventCount: Int
  createdAt: DateTime
  updatedAt: DateTime
}
```

**Event**:
```graphql
type Event {
  id: ID!
  name: String!
  tableName: String!
  gameGid: Int!
  category: Category
  parameters: [Parameter!]!
  isActive: Boolean!
  createdAt: DateTime
  updatedAt: DateTime
}
```

**Parameter**:
```graphql
type Parameter {
  id: ID!
  name: String!
  paramNameCn: String
  paramType: String!
  jsonPath: String
  event: Event!
  isActive: Boolean!
  createdAt: DateTime
  updatedAt: DateTime
}
```

**Category**:
```graphql
type Category {
  id: ID!
  name: String!
  description: String
  gameGid: Int!
  isActive: Boolean!
  eventCount: Int
  events: [Event!]!
  createdAt: DateTime
  updatedAt: DateTime
}
```

### 输入类型

**GameInput**:
```graphql
input GameInput {
  gid: String!
  name: String!
  odsDb: String!
  description: String
  dwdPrefix: String
}
```

**EventInput**:
```graphql
input EventInput {
  gameGid: Int!
  name: String!
  tableName: String!
  categoryId: Int
}
```

**ParameterInput**:
```graphql
input ParameterInput {
  eventId: Int!
  name: String!
  paramNameCn: String
  paramType: String!
  jsonPath: String
}
```

---

## 最佳实践

### 1. 查询字段选择

**❌ 不推荐 - 查询所有字段**:
```graphql
query GetGames {
  games {
    id
    gid
    name
    odsDb
    description
    dwdPrefix
    isActive
    eventCount
    createdAt
    updatedAt
  }
}
```

**✅ 推荐 - 只查询需要的字段**:
```graphql
query GetGames {
  games {
    id
    name
    isActive
  }
}
```

### 2. 批量查询

**❌ 不推荐 - 多次请求**:
```javascript
const game1 = await query({ gameId: 1 });
const game2 = await query({ gameId: 2 });
const game3 = await query({ gameId: 3 });
```

**✅ 推荐 - 一次请求**:
```graphql
query GetGames($gameIds: [ID!]!) {
  game1: game(gameId: $gameIds[0]) { id name }
  game2: game(gameId: $gameIds[1]) { id name }
  game3: game(gameId: $gameIds[2]) { id name }
}
```

### 3. 错误处理

```javascript
const { loading, error, data } = useQuery(GET_GAMES);

if (loading) return <Loading />;
if (error) {
  // 处理GraphQL错误
  if (error.networkError) {
    return <Error message="Network error" />;
  }
  if (error.graphQLErrors) {
    return <Error message={error.graphQLErrors[0].message} />;
  }
  return <Error message="Unknown error" />;
}
return <GamesList data={data.games} />;
```

### 4. 分页查询

```graphql
query GetEventsPaginated($gameGid: Int!, $page: Int!, $limit: Int!) {
  events(gameGid: $gameGid, page: $page, limit: $limit) {
    id
    name
    tableName
  }
}
```

---

## 调试工具

### GraphiQL

访问 `http://127.0.0.1:5001/graphql` 查看交互式API文档（如果已启用）。

### Apollo DevTools

安装浏览器扩展：
- Chrome: [Apollo Client Devtools](https://chrome.google.com/webstore/detail/apollo-client-devtools/jdkknkkbebbapilgoeccciglkfbmbnfm)

### GraphQL Playground

```bash
# 启动GraphQL Playground（如果配置）
npm install -g graphql-playground
graphql-playground --endpoint http://127.0.0.1:5001/graphql
```

---

## 相关文档

- **[REST API文档](README.md)** - RESTful API完整文档
- **[REST到GraphQL迁移指南](REST_TO_GRAPHQL_MIGRATION.md)** - 从REST迁移到GraphQL
- **[GraphQL迁移最终报告](../graphql-migration/GRAPHQL_MIGRATION_FINAL_REPORT.md)** - GraphQL迁移完整记录
- **[经验文档 - API设计模式](../lessons-learned/api-design-patterns.md)** - API设计最佳实践

---

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0.0 | 2026-02-20 | GraphQL API初始版本 |
| 2.0.0 | 2026-02-25 | 完整集成DataLoader |
| 3.0.0 | 2026-03-03 | Repository Pattern迁移完成 |
