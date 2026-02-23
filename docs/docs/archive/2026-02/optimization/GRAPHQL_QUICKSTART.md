# GraphQL API 快速启动指南

## 1. 启动应用

```bash
cd /Users/mckenzie/Documents/event2table/backend
source venv/bin/activate
python web_app.py
```

## 2. 访问GraphiQL IDE

打开浏览器访问：http://localhost:5001/api/graphql

## 3. 测试查询

### 查询游戏列表
```graphql
{
  games(limit: 5) {
    gid
    name
    odsDb
    eventCount
  }
}
```

### 查询单个游戏
```graphql
query GetGame($gid: Int!) {
  game(gid: $gid) {
    gid
    name
    odsDb
  }
}
```

变量：
```json
{
  "gid": 10000147
}
```

### 查询事件列表
```graphql
query GetEvents($gameGid: Int!, $limit: Int) {
  events(gameGid: $gameGid, limit: $limit) {
    id
    eventName
    eventNameCn
    paramCount
  }
}
```

变量：
```json
{
  "gameGid": 10000147,
  "limit": 10
}
```

### 创建游戏
```graphql
mutation CreateGame($gid: Int!, $name: String!, $odsDb: String!) {
  createGame(gid: $gid, name: $name, odsDb: $odsDb) {
    ok
    game {
      gid
      name
    }
    errors
  }
}
```

变量：
```json
{
  "gid": 99999999,
  "name": "Test Game",
  "odsDb": "ieu_ods"
}
```

## 4. 运行测试

```bash
cd /Users/mckenzie/Documents/event2table/backend
source venv/bin/activate
python test/unit/graphql/test_e2e.py
```

## 5. API端点

- GraphQL端点: `/api/graphql`
- GraphiQL IDE: `/api/graphql` (GET请求)
- 支持的HTTP方法: POST (查询和变更)

## 6. 特性

- ✅ 完整的CRUD操作
- ✅ DataLoader优化（解决N+1查询）
- ✅ 查询深度限制（最大10层）
- ✅ 查询复杂度限制（最大1000）
- ✅ 统一错误处理
- ✅ 缓存集成
- ✅ GraphiQL IDE

## 7. 注意事项

1. 目录名为 `gql_api` 而非 `graphql`（避免与graphql包冲突）
2. 使用 graphene 2.x 版本
3. 所有变更操作会自动清除相关缓存
4. 支持分页、过滤和搜索

## 8. 下一步

- 前端集成：使用Apollo Client
- 添加订阅功能
- 添加文件上传
- 添加批量操作
