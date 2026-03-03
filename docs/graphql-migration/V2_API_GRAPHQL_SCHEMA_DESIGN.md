# V2 API GraphQL Schema设计文档

**项目**: Event2Table GraphQL迁移
**创建日期**: 2026-02-25
**状态**: 设计阶段

---

## 📋 文档概述

本文档定义了V2 API端点迁移到GraphQL的Schema设计。

### 迁移的V2 API端点

根据检查报告,需要迁移的V2 API端点包括:

1. **Games V2** (6个端点)
   - `GET /api/v2/games` - 获取所有游戏
   - `POST /api/v2/games` - 创建游戏
   - `GET /api/v2/games/<int:gid>` - 获取单个游戏
   - `PUT/PATCH /api/v2/games/<int:gid>` - 更新游戏
   - `DELETE /api/v2/games/<int:gid>` - 删除游戏
   - `DELETE /api/v2/games/batch` - 批量删除游戏

2. **Events V2** (需要确认)
   - `GET /api/v2/events` - 获取事件列表
   - 其他Events V2端点

3. **HQL Preview V2** (需要确认)
   - HQL预览相关端点

---

## 🏗️ GraphQL Schema设计

### 1. Games V2 Schema

#### 1.1 查询 (Queries)

```graphql
# 获取所有游戏 (V2)
query getGamesV2 {
  gamesV2 {
    id
    gid
    name
    nameCn
    odsDb
    isActive
    createdAt
    updatedAt
    eventCount
    description
  }
}

# 获取单个游戏 (V2)
query getGameV2($gid: Int!) {
  gameV2(gid: $gid) {
    id
    gid
    name
    nameCn
    odsDb
    isActive
    createdAt
    updatedAt
    description
    events {
      id
      eventName
      eventNameCn
    }
  }
}
```

#### 1.2 变更 (Mutations)

```graphql
# 创建游戏 (V2)
mutation createGameV2($input: GameV2CreateInput!) {
  createGameV2(input: $input) {
    success
    message
    game {
      id
      gid
      name
      odsDb
    }
    errors
  }
}

# 更新游戏 (V2)
mutation updateGameV2($gid: Int!, $input: GameV2UpdateInput!) {
  updateGameV2(gid: $gid, input: $input) {
    success
    message
    game {
      id
      gid
      name
      odsDb
    }
    errors
  }
}

# 删除游戏 (V2)
mutation deleteGameV2($gid: Int!) {
  deleteGameV2(gid: $gid) {
    success
    message
    errors
  }
}

# 批量删除游戏 (V2)
mutation batchDeleteGamesV2($gids: [Int!]!) {
  batchDeleteGamesV2(gids: $gids) {
    success
    message
    deletedCount
    failedCount
    errors
  }
}
```

#### 1.3 类型定义 (Types)

```graphql
# 游戏类型 (V2)
type GameV2 {
  id: Int!
  gid: Int!
  name: String!
  nameCn: String
  odsDb: String!
  isActive: Boolean!
  createdAt: String!
  updatedAt: String!
  description: String
  eventCount: Int
  events: [Event!]
}

# 游戏创建输入 (V2)
input GameV2CreateInput {
  gid: Int!
  name: String!
  nameCn: String
  odsDb: String!
  description: String
  isActive: Boolean
}

# 游戏更新输入 (V2)
input GameV2UpdateInput {
  name: String
  nameCn: String
  odsDb: String
  description: String
  isActive: Boolean
}

# 批量操作结果
type BatchOperationResult {
  success: Boolean!
  message: String!
  deletedCount: Int
  failedCount: Int
  errors: [String!]
}
```

---

### 2. Events V2 Schema

#### 2.1 查询 (Queries)

```graphql
# 获取事件列表 (V2)
query getEventsV2($gameGid: Int!, $page: Int, $perPage: Int, $category: String) {
  eventsV2(
    gameGid: $gameGid
    page: $page
    perPage: $perPage
    category: $category
  ) {
    data {
      id
      eventName
      eventNameCn
      description
      isActive
      categoryId
    }
    pagination {
      total
      page
      perPage
      totalPages
    }
  }
}
```

#### 2.2 变更 (Mutations)

```graphql
# 创建事件 (V2)
mutation createEventV2($input: EventV2CreateInput!) {
  createEventV2(input: $input) {
    success
    message
    event {
      id
      eventName
      eventNameCn
    }
    errors
  }
}

# 更新事件 (V2)
mutation updateEventV2($id: Int!, $input: EventV2UpdateInput!) {
  updateEventV2(id: $id, input: $input) {
    success
    message
    event {
      id
      eventName
      eventNameCn
    }
    errors
  }
}

# 删除事件 (V2)
mutation deleteEventV2($id: Int!) {
  deleteEventV2(id: $id) {
    success
    message
    errors
  }
}
```

#### 2.3 类型定义 (Types)

```graphql
# 事件类型 (V2)
type EventV2 {
  id: Int!
  eventName: String!
  eventNameCn: String
  description: String
  isActive: Boolean!
  categoryId: Int
  gameGid: Int!
  createdAt: String!
  updatedAt: String!
}

# 事件创建输入 (V2)
input EventV2CreateInput {
  gameGid: Int!
  eventName: String!
  eventNameCn: String
  description: String
  categoryId: Int
  isActive: Boolean
}

# 事件更新输入 (V2)
input EventV2UpdateInput {
  eventName: String
  eventNameCn: String
  description: String
  categoryId: Int
  isActive: Boolean
}

# 分页信息
type PaginationInfo {
  total: Int!
  page: Int!
  perPage: Int!
  totalPages: Int!
}

# 分页事件列表 (V2)
type PaginatedEventsV2 {
  data: [EventV2!]!
  pagination: PaginationInfo!
}
```

---

### 3. HQL Preview V2 Schema

#### 3.1 查询 (Queries)

```graphql
# 获取HQL列表 (V2)
query getHqlListV2($hqlType: String, $editedOnly: Boolean) {
  hqlListV2(hqlType: $hqlType, editedOnly: $editedOnly) {
    id
    eventName
    hqlType
    hqlContent
    isEdited
    createdAt
    updatedAt
  }
}

# 获取HQL详情 (V2)
query getHqlV2($id: Int!) {
  hqlV2(id: $id) {
    id
    eventName
    hqlType
    hqlContent
    isEdited
    createdAt
    updatedAt
    gameGid
  }
}
```

#### 3.2 变更 (Mutations)

```graphql
# 生成HQL (V2)
mutation generateHqlV2($input: HqlGenerateInput!) {
  generateHqlV2(input: $input) {
    success
    message
    hql {
      id
      hqlContent
    }
    errors
  }
}

# 验证HQL (V2)
mutation validateHqlV2($hqlContent: String!) {
  validateHqlV2(hqlContent: $hqlContent) {
    isValid
    errors
    warnings
  }
}

# 保存HQL模板 (V2)
mutation saveHqlTemplateV2($input: HqlTemplateInput!) {
  saveHqlTemplateV2(input: $input) {
    success
    message
    hql {
      id
      eventName
      hqlContent
    }
    errors
  }
}
```

#### 3.3 类型定义 (Types)

```graphql
# HQL类型 (V2)
type HqlV2 {
  id: Int!
  eventName: String!
  hqlType: String!
  hqlContent: String!
  isEdited: Boolean!
  gameGid: Int!
  createdAt: String!
  updatedAt: String!
}

# HQL生成输入
input HqlGenerateInput {
  eventId: Int!
  gameGid: Int!
  fields: [HqlFieldInput!]!
  conditions: [HqlConditionInput!]
  joinType: String
}

# HQL字段输入
input HqlFieldInput {
  name: String!
  type: String!
  jsonPath: String
}

# HQL条件输入
input HqlConditionInput {
  field: String!
  operator: String!
  value: String!
}

# HQL模板输入
input HqlTemplateInput {
  eventName: String!
  hqlContent: String!
  hqlType: String!
  gameGid: Int!
}

# HQL验证结果
type HqlValidationResult {
  isValid: Boolean!
  errors: [String!]!
  warnings: [String!]!
}
```

---

## 🔧 扩展现有Schema

### 扩展Query根类型

```graphql
extend type Query {
  # Games V2 Queries
  gamesV2: [GameV2!]!
  gameV2(gid: Int!): GameV2

  # Events V2 Queries
  eventsV2(
    gameGid: Int!
    page: Int = 1
    perPage: Int = 20
    category: String
  ): PaginatedEventsV2!

  # HQL V2 Queries
  hqlListV2(hqlType: String, editedOnly: Boolean): [HqlV2!]!
  hqlV2(id: Int!): HqlV2
}
```

### 扩展Mutation根类型

```graphql
extend type Mutation {
  # Games V2 Mutations
  createGameV2(input: GameV2CreateInput!): GameV2Result!
  updateGameV2(gid: Int!, input: GameV2UpdateInput!): GameV2Result!
  deleteGameV2(gid: Int!): OperationResult!
  batchDeleteGamesV2(gids: [Int!]!): BatchOperationResult!

  # Events V2 Mutations
  createEventV2(input: EventV2CreateInput!): EventV2Result!
  updateEventV2(id: Int!, input: EventV2UpdateInput!): EventV2Result!
  deleteEventV2(id: Int!): OperationResult!

  # HQL V2 Mutations
  generateHqlV2(input: HqlGenerateInput!): HqlResult!
  validateHqlV2(hqlContent: String!): HqlValidationResult!
  saveHqlTemplateV2(input: HqlTemplateInput!): HqlResult!
}
```

### 通用结果类型

```graphql
# 操作结果
type OperationResult {
  success: Boolean!
  message: String!
  errors: [String!]
}

# 游戏 V2 结果
type GameV2Result {
  success: Boolean!
  message: String!
  game: GameV2
  errors: [String!]
}

# 事件 V2 结果
type EventV2Result {
  success: Boolean!
  message: String!
  event: EventV2
  errors: [String!]
}

# HQL 结果
type HqlResult {
  success: Boolean!
  message: String!
  hql: HqlV2
  errors: [String!]
}
```

---

## 📊 Schema验证规则

### 输入验证

1. **GameV2CreateInput**
   - `gid`: 必须是正整数
   - `name`: 必须非空,最大长度200
   - `odsDb`: 必须是 'ieu_ods' 或 'overseas_ods'
   - `nameCn`: 最大长度200
   - `description`: 最大长度1000

2. **EventV2CreateInput**
   - `gameGid`: 必须是正整数
   - `eventName`: 必须非空,最大长度200
   - `eventNameCn`: 最大长度200
   - `description`: 最大长度1000

3. **HqlGenerateInput**
   - `eventId`: 必须是正整数
   - `gameGid`: 必须是正整数
   - `fields`: 必须至少包含一个字段

### 业务逻辑验证

1. **创建游戏**
   - GID必须唯一
   - 游戏名称不能重复

2. **删除游戏**
   - 不能删除包含事件的游戏
   - 不能删除包含模板的游戏

3. **创建事件**
   - 游戏必须存在
   - 事件名称在游戏中必须唯一

---

## 🚀 实现计划

### 第一阶段: Schema定义 (预计2-3天)

1. 创建V2类型定义文件
2. 扩展Query和Mutation根类型
3. 添加输入类型和结果类型
4. Schema验证测试

### 第二阶段: Resolver实现 (预计4-5天)

1. 实现Games V2 Resolvers
2. 实现Events V2 Resolvers
3. 实现HQL V2 Resolvers
4. 集成DataLoader
5. 单元测试

### 第三阶段: 前端集成 (预计3-4天)

1. 创建Apollo Client查询
2. 迁移前端组件
3. 测试集成
4. 性能优化

### 第四阶段: 测试和验证 (预计2-3天)

1. 单元测试
2. 集成测试
3. E2E测试
4. 性能测试

---

## 📝 注意事项

### 向后兼容性

1. 保留现有的V2 REST API作为fallback
2. GraphQL Schema设计应与REST API保持一致
3. 错误消息应保持一致

### 性能优化

1. 使用DataLoader解决N+1查询
2. 实现查询复杂度限制
3. 添加缓存层
4. 使用分页避免大结果集

### 安全性

1. 输入验证和清理
2. SQL注入防护
3. XSS防护
4. 权限控制

### 测试

1. 所有Resolvers必须有单元测试
2. 覆盖率 >= 80%
3. E2E测试覆盖核心流程
4. 性能测试满足要求

---

## 📚 参考资料

- [GraphQL Complete Documentation](./GRAPHQL_COMPLETE_DOCUMENTATION.md)
- [CLAUDE.md](../../CLAUDE.md)
- [V2 API Routes](../../backend/api/routes/games_v2.py)
- [Events V2 API Routes](../../backend/api/routes/events_v2.py)

---

**文档版本**: 1.0
**最后更新**: 2026-02-25
**维护者**: Event2Table开发团队
