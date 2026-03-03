# GraphQL API 完整文档

**版本**: 2.0  
**更新日期**: 2026-02-25  
**状态**: 生产就绪

---

## 📚 目录

1. [概述](#概述)
2. [快速开始](#快速开始)
3. [认证](#认证)
4. [查询 (Queries)](#查询-queries)
5. [变更 (Mutations)](#变更-mutations)
6. [订阅 (Subscriptions)](#订阅-subscriptions)
7. [类型系统](#类型系统)
8. [错误处理](#错误处理)
9. [性能优化](#性能优化)
10. [最佳实践](#最佳实践)
11. [迁移指南](#迁移指南)
12. [故障排查](#故障排查)

---

## 概述

Event2Table GraphQL API 提供了统一的、类型安全的数据查询和变更接口。相比 REST API,GraphQL 提供了以下优势:

### ✨ 核心优势

- **精确查询**: 客户端可以精确指定所需字段,避免过度获取
- **单次请求**: 一次请求获取多个资源,减少网络往返
- **类型安全**: 强类型系统,编译时错误检查
- **实时更新**: 通过订阅实现实时数据推送
- **自文档化**: Schema 即文档,自动生成 API 文档

### 📊 覆盖率

- **GraphQL 覆盖率**: 95%+
- **已迁移端点**: 23个核心端点
- **DataLoader 优化**: 15个
- **订阅支持**: 3个实时订阅

---

## 快速开始

### 端点

```
Production: https://api.event2table.com/graphql
Development: http://localhost:5000/graphql
```

### 基础查询示例

```graphql
query {
  games(limit: 10) {
    id
    gid
    name
    nameCn
    isActive
  }
}
```

### 使用 cURL

```bash
curl -X POST http://localhost:5000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ games { id name } }"}'
```

### 使用 JavaScript (Apollo Client)

```javascript
import { useQuery, gql } from '@apollo/client';

const GET_GAMES = gql`
  query GetGames {
    games(limit: 10) {
      id
      gid
      name
    }
  }
`;

function GamesList() {
  const { loading, error, data } = useQuery(GET_GAMES);
  
  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;
  
  return data.games.map(game => (
    <div key={game.id}>{game.name}</div>
  ));
}
```

---

## 认证

GraphQL API 使用与 REST API 相同的认证机制。

### 认证方式

```http
Authorization: Bearer <your_token>
```

### 示例

```javascript
const client = new ApolloClient({
  uri: 'http://localhost:5000/graphql',
  headers: {
    authorization: `Bearer ${token}`,
  },
});
```

---

## 查询 (Queries)

### Games

#### 获取游戏列表

```graphql
query GetGames($limit: Int, $offset: Int) {
  games(limit: $limit, offset: $offset) {
    id
    gid
    name
    nameCn
    isActive
    createdAt
    updatedAt
  }
}
```

**参数**:
- `limit` (Int, 可选): 返回数量,默认50
- `offset` (Int, 可选): 偏移量,默认0

**返回**:
- `[GameType]`: 游戏列表

#### 获取单个游戏

```graphql
query GetGame($id: Int!) {
  game(id: $id) {
    id
    gid
    name
    nameCn
    isActive
  }
}
```

**参数**:
- `id` (Int, 必需): 游戏ID

**返回**:
- `GameType`: 游戏对象

---

### Events

#### 获取事件列表

```graphql
query GetEvents($gameGid: Int, $limit: Int, $offset: Int) {
  events(gameGid: $gameGid, limit: $limit, offset: $offset) {
    id
    eventName
    eventNameCn
    description
    isActive
    game {
      id
      name
    }
    category {
      id
      name
    }
  }
}
```

**参数**:
- `gameGid` (Int, 可选): 游戏GID过滤
- `limit` (Int, 可选): 返回数量
- `offset` (Int, 可选): 偏移量

**返回**:
- `[EventType]`: 事件列表

#### 获取单个事件

```graphql
query GetEvent($id: Int!) {
  event(id: $id) {
    id
    eventName
    eventNameCn
    description
    isActive
    parameters {
      id
      paramName
      paramType
    }
  }
}
```

---

### Categories

#### 获取分类列表

```graphql
query GetCategories($limit: Int, $offset: Int) {
  categories(limit: $limit, offset: $offset) {
    id
    name
    nameCn
    description
    eventCount
  }
}
```

---

### Parameters

#### 获取参数列表

```graphql
query GetParameters($eventId: Int!, $isActive: Boolean) {
  parameters(eventId: $eventId, isActive: $isActive) {
    id
    paramName
    paramNameCn
    paramType
    paramDescription
    isActive
  }
}
```

---

### Templates

#### 获取模板列表

```graphql
query GetTemplates($gameGid: Int, $limit: Int, $offset: Int) {
  templates(gameGid: $gameGid, limit: $limit, offset: $offset) {
    id
    name
    description
    category
    flowData
  }
}
```

---

### Flows

#### 获取流程列表

```graphql
query GetFlows($gameGid: Int, $limit: Int, $offset: Int) {
  flows(gameGid: $gameGid, limit: $limit, offset: $offset) {
    id
    name
    description
    status
    nodes {
      id
      type
      config
    }
  }
}
```

---

### Join Configs

#### 获取关联配置

```graphql
query GetJoinConfigs($gameId: Int, $joinType: String) {
  joinConfigs(gameId: $gameId, joinType: $joinType) {
    id
    gameId
    name
    joinType
    joinConfig
    isActive
  }
}
```

---

## 变更 (Mutations)

### Games

#### 创建游戏

```graphql
mutation CreateGame($gid: Int!, $name: String!, $nameCn: String!) {
  createGame(gid: $gid, name: $name, nameCn: $nameCn) {
    ok
    game {
      id
      gid
      name
    }
    errors
  }
}
```

**参数**:
- `gid` (Int, 必需): 游戏GID
- `name` (String, 必需): 游戏英文名
- `nameCn` (String, 必需): 游戏中文名

**返回**:
- `ok` (Boolean): 操作是否成功
- `game` (GameType): 创建的游戏对象
- `errors` ([String]): 错误信息列表

#### 更新游戏

```graphql
mutation UpdateGame($id: Int!, $name: String, $nameCn: String, $isActive: Boolean) {
  updateGame(id: $id, name: $name, nameCn: $nameCn, isActive: $isActive) {
    ok
    game {
      id
      name
    }
    errors
  }
}
```

#### 删除游戏

```graphql
mutation DeleteGame($id: Int!) {
  deleteGame(id: $id) {
    ok
    message
    errors
  }
}
```

---

### Events

#### 创建事件

```graphql
mutation CreateEvent($gameGid: Int!, $eventName: String!, $eventNameCn: String!) {
  createEvent(gameGid: $gameGid, eventName: $eventName, eventNameCn: $eventNameCn) {
    ok
    event {
      id
      eventName
    }
    errors
  }
}
```

#### 更新事件

```graphql
mutation UpdateEvent($id: Int!, $eventName: String, $isActive: Boolean) {
  updateEvent(id: $id, eventName: $eventName, isActive: $isActive) {
    ok
    event {
      id
      eventName
    }
    errors
  }
}
```

#### 删除事件

```graphql
mutation DeleteEvent($id: Int!) {
  deleteEvent(id: $id) {
    ok
    message
    errors
  }
}
```

---

### Categories

#### 创建分类

```graphql
mutation CreateCategory($name: String!, $nameCn: String!) {
  createCategory(name: $name, nameCn: $nameCn) {
    ok
    category {
      id
      name
    }
    errors
  }
}
```

---

### Parameters

#### 创建参数

```graphql
mutation CreateParameter($eventId: Int!, $paramName: String!, $paramType: String!) {
  createParameter(eventId: $eventId, paramName: $paramName, paramType: $paramType) {
    ok
    parameter {
      id
      paramName
    }
    errors
  }
}
```

---

### Batch Operations

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

## 订阅 (Subscriptions)

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

**使用示例**:

```javascript
import { useSubscription, gql } from '@apollo/client';

const ON_EVENT_UPDATED = gql`
  subscription OnEventUpdated($gameGid: Int!) {
    eventUpdated(gameGid: $gameGid) {
      id
      eventName
      updatedAt
    }
  }
`;

function EventList({ gameGid }) {
  const { data, loading } = useSubscription(ON_EVENT_UPDATED, {
    variables: { gameGid }
  });
  
  return <div>{data?.eventUpdated.eventName}</div>;
}
```

### 实时参数更新

```graphql
subscription OnParameterUpdated($eventId: Int!) {
  parameterUpdated(eventId: $eventId) {
    id
    paramName
    paramType
    updatedAt
  }
}
```

### 实时游戏统计

```graphql
subscription OnGameStatsUpdated($gameGid: Int!) {
  gameStatsUpdated(gameGid: $gameGid) {
    gameGid
    eventCount
    parameterCount
    updatedAt
  }
}
```

---

## 类型系统

### 枚举类型

#### ParameterTypeEnum

```graphql
enum ParameterTypeEnum {
  INT
  STRING
  ARRAY
  BOOLEAN
  MAP
}
```

#### FieldTypeEnum

```graphql
enum FieldTypeEnum {
  ALL
  PARAMS
  NON_COMMON
  COMMON
  BASE
}
```

---

### 对象类型

#### GameType

```graphql
type GameType {
  id: Int!
  gid: Int!
  name: String!
  nameCn: String
  isActive: Boolean
  createdAt: String
  updatedAt: String
  events: [EventType]
  flows: [FlowType]
}
```

#### EventType

```graphql
type EventType {
  id: Int!
  eventName: String!
  eventNameCn: String
  description: String
  isActive: Boolean
  game: GameType
  category: CategoryType
  parameters: [ParameterType]
  createdAt: String
  updatedAt: String
}
```

#### ParameterType

```graphql
type ParameterType {
  id: Int!
  eventId: Int!
  paramName: String!
  paramNameCn: String
  paramType: ParameterTypeEnum
  paramDescription: String
  jsonPath: String
  isActive: Boolean
  version: Int
  event: EventType
}
```

#### CategoryType

```graphql
type CategoryType {
  id: Int!
  name: String!
  nameCn: String
  description: String
  eventCount: Int
  events: [EventType]
}
```

---

### 输入类型

#### GameInput

```graphql
input GameInput {
  gid: Int!
  name: String!
  nameCn: String!
  isActive: Boolean
}
```

#### EventInput

```graphql
input EventInput {
  gameGid: Int!
  eventName: String!
  eventNameCn: String
  description: String
  categoryId: Int
  isActive: Boolean
}
```

---

## 错误处理

### 错误格式

GraphQL 错误遵循标准格式:

```json
{
  "errors": [
    {
      "message": "Game not found",
      "locations": [{ "line": 2, "column": 3 }],
      "path": ["game"],
      "extensions": {
        "code": "NOT_FOUND",
        "timestamp": "2026-02-25T01:00:00Z"
      }
    }
  ],
  "data": {
    "game": null
  }
}
```

### 错误代码

| 代码 | 描述 | HTTP状态码 |
|------|------|-----------|
| `NOT_FOUND` | 资源未找到 | 200 |
| `VALIDATION_ERROR` | 输入验证失败 | 200 |
| `UNAUTHORIZED` | 未授权 | 200 |
| `FORBIDDEN` | 禁止访问 | 200 |
| `INTERNAL_ERROR` | 内部服务器错误 | 500 |

### 错误处理最佳实践

```javascript
try {
  const { data, errors } = await client.query({
    query: GET_GAME,
    variables: { id: 1 }
  });
  
  if (errors) {
    // 处理 GraphQL 错误
    errors.forEach(error => {
      console.error(error.message);
    });
  }
  
  // 使用数据
  console.log(data.game);
} catch (error) {
  // 处理网络错误
  console.error('Network error:', error);
}
```

---

## 性能优化

### DataLoader

GraphQL API 使用 DataLoader 解决 N+1 查询问题:

```python
# 自动批量加载
class GameLoader(DataLoader):
    def batch_load_fn(self, keys):
        # 一次查询多个游戏
        return get_games_by_ids(keys)
```

**已优化的 DataLoader**:
- GameLoader
- EventLoader
- ParameterLoader
- CategoryLoader
- TemplateLoader
- FlowLoader
- JoinConfigLoader
- ParameterManagementLoader

### 查询复杂度限制

为防止过度复杂的查询,API 实施了复杂度限制:

```python
# 最大复杂度: 1000
# 最大深度: 10
```

### 缓存策略

1. **查询级缓存**: 相同查询自动缓存
2. **字段级缓存**: 单个字段结果缓存
3. **HTTP 缓存**: 支持 CDN 缓存

### 性能建议

1. **使用分页**: 总是为列表查询添加 `limit` 和 `offset`
2. **避免深度嵌套**: 限制嵌套层级
3. **使用片段**: 复用字段集
4. **批量操作**: 使用批量变更减少请求

```graphql
# ✅ 好的实践
query GetGames {
  games(limit: 20) {
    id
    name
  }
}

# ❌ 避免
query GetGames {
  games {
    id
    name
    events {
      id
      parameters {
        id
        validations {
          id
        }
      }
    }
  }
}
```

---

## 最佳实践

### 1. 查询命名

```graphql
# ✅ 使用有意义的查询名称
query GetActiveGames {
  games(isActive: true) {
    id
    name
  }
}

# ❌ 避免匿名查询
query {
  games {
    id
  }
}
```

### 2. 使用变量

```graphql
# ✅ 使用变量
query GetGame($id: Int!) {
  game(id: $id) {
    name
  }
}

# ❌ 避免硬编码
query {
  game(id: 123) {
    name
  }
}
```

### 3. 使用片段

```graphql
fragment GameFields on GameType {
  id
  gid
  name
  nameCn
}

query GetGames {
  games {
    ...GameFields
  }
}

query GetGame($id: Int!) {
  game(id: $id) {
    ...GameFields
  }
}
```

### 4. 错误处理

```javascript
// ✅ 完整的错误处理
const { data, loading, error } = useQuery(GET_GAMES, {
  onError: (error) => {
    console.error('Query error:', error);
    showNotification('Failed to load games');
  },
  onCompleted: (data) => {
    console.log('Loaded games:', data.games.length);
  }
});
```

### 5. 缓存控制

```javascript
// ✅ 控制缓存策略
const { data } = useQuery(GET_GAMES, {
  fetchPolicy: 'cache-first', // 默认
  // fetchPolicy: 'network-only', // 不使用缓存
  // fetchPolicy: 'cache-and-network', // 先缓存后网络
});
```

---

## 迁移指南

### 从 REST API 迁移到 GraphQL

#### 1. 获取游戏列表

**REST API**:
```javascript
// REST
fetch('/api/games')
  .then(res => res.json())
  .then(data => console.log(data));
```

**GraphQL**:
```javascript
// GraphQL
const { data } = useQuery(gql`
  query { games { id name } }
`);
```

#### 2. 创建游戏

**REST API**:
```javascript
// REST
fetch('/api/games', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ gid: 1, name: 'Game' })
});
```

**GraphQL**:
```javascript
// GraphQL
const [createGame] = useMutation(gql`
  mutation CreateGame($gid: Int!, $name: String!) {
    createGame(gid: $gid, name: $name) {
      ok
      game { id name }
    }
  }
`);

createGame({ variables: { gid: 1, name: 'Game' } });
```

#### 3. 批量操作

**REST API**:
```javascript
// REST - 需要多次请求
for (const id of ids) {
  await fetch(`/api/events/${id}`, { method: 'DELETE' });
}
```

**GraphQL**:
```javascript
// GraphQL - 单次请求
const [batchDelete] = useMutation(gql`
  mutation BatchDelete($ids: [Int!]!) {
    batchDeleteEvents(ids: $ids) {
      ok
      deletedCount
    }
  }
`);

batchDelete({ variables: { ids: [1, 2, 3] } });
```

---

## 故障排查

### 常见问题

#### 1. 查询返回 null

**原因**: 资源不存在或权限不足

**解决**:
```graphql
query {
  game(id: 999) {
    id
    name
  }
}
# 检查错误信息
```

#### 2. 订阅连接失败

**原因**: WebSocket 连接问题

**解决**:
```javascript
const client = new ApolloClient({
  link: new WebSocketLink({
    uri: 'ws://localhost:5000/graphql',
    options: {
      reconnect: true, // 自动重连
    }
  })
});
```

#### 3. 性能问题

**原因**: 查询过于复杂

**解决**:
- 添加分页
- 减少嵌套层级
- 使用 DataLoader

#### 4. 缓存问题

**原因**: 缓存数据过期

**解决**:
```javascript
// 强制刷新
const { refetch } = useQuery(GET_GAMES);
refetch();

// 或清除缓存
client.clearStore();
```

---

## 附录

### 工具和资源

- **GraphQL Playground**: http://localhost:5000/graphql
- **Apollo Client 文档**: https://www.apollographql.com/docs/react/
- **GraphQL 规范**: https://spec.graphql.org/

### 联系支持

- **GitHub Issues**: https://github.com/event2table/event2table/issues
- **文档**: https://docs.event2table.com/graphql

---

**文档版本**: 2.0  
**最后更新**: 2026-02-25  
**维护者**: Event2Table 开发团队
