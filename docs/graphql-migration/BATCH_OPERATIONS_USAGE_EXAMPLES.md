# 批量操作GraphQL使用示例

本文档提供批量操作GraphQL mutations的使用示例。

---

## 📝 基础使用

### 1. 批量删除Games

```graphql
mutation BatchDeleteGames {
    batchDeleteGames(ids: [1, 2, 3]) {
        ok
        deletedCount
        errors
    }
}
```

**响应示例**:
```json
{
    "data": {
        "batchDeleteGames": {
            "ok": true,
            "deletedCount": 3,
            "errors": null
        }
    }
}
```

### 2. 批量更新Games

```graphql
mutation BatchUpdateGames {
    batchUpdateGames(
        updates: [
            {id: 1, name: "Updated Game 1", isActive: true},
            {id: 2, name: "Updated Game 2", isActive: false}
        ]
    ) {
        ok
        updatedCount
        errors
    }
}
```

**响应示例**:
```json
{
    "data": {
        "batchUpdateGames": {
            "ok": true,
            "updatedCount": 2,
            "errors": null
        }
    }
}
```

### 3. 批量创建Games

```graphql
mutation BatchCreateGames {
    batchCreateGames(
        games: [
            {gid: 100001, name: "New Game 1", odsDb: "ods_game_100001"},
            {gid: 100002, name: "New Game 2", odsDb: "ods_game_100002"}
        ]
    ) {
        ok
        games {
            gid
            name
            odsDb
        }
        createdCount
        errors
    }
}
```

**响应示例**:
```json
{
    "data": {
        "batchCreateGames": {
            "ok": true,
            "games": [
                {"gid": 100001, "name": "New Game 1", "odsDb": "ods_game_100001"},
                {"gid": 100002, "name": "New Game 2", "odsDb": "ods_game_100002"}
            ],
            "createdCount": 2,
            "errors": null
        }
    }
}
```

---

## 🎯 Events批量操作

### 1. 批量删除Events

```graphql
mutation BatchDeleteEvents {
    batchDeleteEvents(ids: [10, 20, 30, 40]) {
        ok
        deletedCount
        errors
    }
}
```

**响应示例**:
```json
{
    "data": {
        "batchDeleteEvents": {
            "ok": true,
            "deletedCount": 4,
            "errors": null
        }
    }
}
```

### 2. 批量更新Events - 更新名称

```graphql
mutation BatchUpdateEventNames {
    batchUpdateEvents(
        ids: [10, 20, 30]
        updates: {
            eventName: "Updated Event Name"
            eventNameCn: "更新的事件名称"
        }
    ) {
        ok
        updatedCount
        errors
    }
}
```

**响应示例**:
```json
{
    "data": {
        "batchUpdateEvents": {
            "ok": true,
            "updatedCount": 3,
            "errors": null
        }
    }
}
```

### 3. 批量更新Events - 更新分类

```graphql
mutation BatchUpdateEventCategories {
    batchUpdateEvents(
        ids: [10, 20, 30]
        updates: {
            categoryId: 5
            includeInCommonParams: 1
        }
    ) {
        ok
        updatedCount
        errors
    }
}
```

**响应示例**:
```json
{
    "data": {
        "batchUpdateEvents": {
            "ok": true,
            "updatedCount": 3,
            "errors": null
        }
    }
}
```

---

## 🔄 Flows批量操作

### 1. 批量删除Flows

```graphql
mutation BatchDeleteFlows {
    batchDeleteFlows(ids: [100, 200, 300]) {
        ok
        deletedCount
        errors
    }
}
```

**响应示例**:
```json
{
    "data": {
        "batchDeleteFlows": {
            "ok": true,
            "deletedCount": 3,
            "errors": null
        }
    }
}
```

### 2. 批量更新Flows - 更新名称和描述

```graphql
mutation BatchUpdateFlowInfo {
    batchUpdateFlows(
        ids: [100, 200]
        updates: {
            name: "Updated Flow Name"
            description: "Updated flow description"
        }
    ) {
        ok
        updatedCount
        errors
    }
}
```

**响应示例**:
```json
{
    "data": {
        "batchUpdateFlows": {
            "ok": true,
            "updatedCount": 2,
            "errors": null
        }
    }
}
```

### 3. 批量更新Flows - 激活/停用

```graphql
mutation BatchToggleFlows {
    batchUpdateFlows(
        ids: [100, 200, 300]
        updates: {isActive: 1}
    ) {
        ok
        updatedCount
        errors
    }
}
```

**响应示例**:
```json
{
    "data": {
        "batchUpdateFlows": {
            "ok": true,
            "updatedCount": 3,
            "errors": null
        }
    }
}
```

---

## ⚠️ 错误处理示例

### 1. 部分成功

```graphql
mutation BatchDeleteEvents {
    batchDeleteEvents(ids: [1, 2, 999999]) {
        ok
        deletedCount
        errors
    }
}
```

**响应示例** (ID 999999不存在):
```json
{
    "data": {
        "batchDeleteEvents": {
            "ok": false,
            "deletedCount": 2,
            "errors": [
                "Failed to delete event 999999: Event not found"
            ]
        }
    }
}
```

### 2. 验证错误 - 空名称

```graphql
mutation BatchUpdateEvents {
    batchUpdateEvents(
        ids: [1, 2]
        updates: {eventName: ""}
    ) {
        ok
        updatedCount
        errors
    }
}
```

**响应示例**:
```json
{
    "data": {
        "batchUpdateEvents": {
            "ok": false,
            "updatedCount": 0,
            "errors": ["event_name cannot be empty"]
        }
    }
}
```

### 3. 验证错误 - 超长名称

```graphql
mutation BatchUpdateEvents {
    batchUpdateEvents(
        ids: [1]
        updates: {eventName: "a...a"}  # 201个字符
    ) {
        ok
        updatedCount
        errors
    }
}
```

**响应示例**:
```json
{
    "data": {
        "batchUpdateEvents": {
            "ok": false,
            "updatedCount": 0,
            "errors": ["event_name exceeds maximum length of 200 characters"]
        }
    }
}
```

---

## 🔧 高级用法

### 使用变量

```graphql
mutation BatchUpdateEvents($ids: [Int!]!, $updates: EventUpdateInput!) {
    batchUpdateEvents(ids: $ids, updates: $updates) {
        ok
        updatedCount
        errors
    }
}
```

**变量**:
```json
{
    "ids": [1, 2, 3, 4, 5],
    "updates": {
        "eventName": "Batch Updated Event",
        "categoryId": 10
    }
}
```

### 批量操作后查询

```graphql
mutation BatchUpdateAndQuery {
    batchUpdateEvents(
        ids: [1, 2, 3]
        updates: {eventName: "Updated"}
    ) {
        ok
        updatedCount
        errors
    }
}

query GetUpdatedEvents {
    events(limit: 10) {
        id
        eventName
        updatedAt
    }
}
```

---

## 📊 性能建议

### 1. 批量大小

建议单次批量操作不超过100个ID:

```graphql
# ✅ 推荐
mutation BatchDelete {
    batchDeleteEvents(ids: [1, 2, 3, ..., 50])
}

# ⚠️ 不推荐
mutation BatchDelete {
    batchDeleteEvents(ids: [1, 2, 3, ..., 500])
}
```

### 2. 分批处理

对于大量数据,建议分批处理:

```javascript
// JavaScript示例
const allIds = [1, 2, 3, ..., 500];
const batchSize = 50;

for (let i = 0; i < allIds.length; i += batchSize) {
    const batch = allIds.slice(i, i + batchSize);
    await graphqlClient.mutate({
        mutation: BATCH_DELETE_EVENTS,
        variables: { ids: batch }
    });
}
```

### 3. 错误处理

始终检查`ok`字段和`errors`数组:

```javascript
const result = await graphqlClient.mutate({
    mutation: BATCH_UPDATE_EVENTS,
    variables: { ids: [1, 2, 3], updates: {...} }
});

if (!result.data.batchUpdateEvents.ok) {
    console.error('Batch operation failed:', result.data.batchUpdateEvents.errors);
    // 处理错误
}
```

---

## 🎯 最佳实践

1. **验证输入**: 在发送请求前验证数据
2. **处理错误**: 检查`ok`和`errors`字段
3. **合理分批**: 控制批量大小
4. **记录日志**: 记录批量操作结果
5. **用户反馈**: 提供清晰的操作结果反馈

---

**文档版本**: 1.0
**最后更新**: 2026-02-26
**维护者**: Event2Table开发团队
