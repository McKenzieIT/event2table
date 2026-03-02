# Event2Table API 文档

**V8.0.0架构** - REST API + GraphQL API

**版本**: 8.0.0
**最后更新**: 2026-03-02
**架构**: ERS (Entity-Repository-Service)
**API统计**: REST API 84端点 | GraphQL 78操作

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

---

## 架构变更 (V8.0.0)

### 双API架构

**REST API + GraphQL**:
- ✅ **REST API**: 84个端点，传统HTTP接口
- ✅ **GraphQL API**: 78个操作，113次调用，灵活查询
- ✅ **统一架构**: 共享Entity-Repository-Service层
- ✅ **渐进迁移**: REST → GraphQL平滑过渡

### ERS架构

**100% ERS架构覆盖**:
- ✅ Entity层: Pydantic模型统一数据验证
- ✅ Repository层: 数据访问抽象
- ✅ Service层: 业务逻辑封装
- ✅ API层: REST + GraphQL双端点

### 缓存系统

**缓存覆盖率100%**:
- L1缓存: 热数据60秒TTL
- L2缓存: 共享数据300秒TTL
- 自动失效: 写操作自动清理相关缓存
- 性能提升: 67% (267ms → 88ms)

### 零破坏性变更

- ✅ 所有旧API端点保持兼容
- ✅ 新增端点使用新架构
- ✅ 渐进式迁移策略

---

## API模块索引

### REST API (84个端点)

#### 核心业务模块

| 模块 | 文档 | 端点数 | 状态 |
|------|------|--------|------|
| **Categories** | [Categories API](CATEGORIES-API.md) | 8 | ✅ Phase 5增强 |
| **Events** | [Events API](EVENTS-API.md) | 9 | ✅ Phase 5完全迁移 |
| **Parameters** | [Parameters API](PARAMETERS-API.md) | 16 | ✅ Phase 5大幅扩展 |
| **Field Builder** | [Field Builder API](FIELD-BUILDER-API.md) | 6 | ✅ Phase 5新增 |

#### 支持模块

| 模块 | 文档 | 端点数 | 状态 |
|------|------|--------|------|
| **Games** | [Games API](GAMES-API.md) | 7 | ✅ Phase 1-2 |
| **Join Configs** | [Join Configs API](JOIN-CONFIGS-API.md) | 5 | ✅ Phase 3 |
| **Flows/Canvas** | [Flows API](FLOWS-API.md) | 11 | ✅ Phase 2-3 |
| **Cache** | [Cache API](CACHE-API.md) | 23 | ✅ 完整实现 |

### GraphQL API (78个操作)

| 文档 | 操作数 | 调用次数 | 状态 |
|------|--------|----------|------|
| **GraphQL API** | [GraphQL API](GRAPHQL_API.md) | 78 | 113 | ✅ 完整实现 |

**GraphQL优势**:
- ✅ 按需查询，避免over-fetching
- ✅ 单次请求获取多个资源
- ✅ 强类型Schema自动验证
- ✅ 实时订阅支持

---

## API版本管理

### 版本策略

**V8.0.0** (当前版本):
- ✅ **REST API**: 稳定版本，84个端点
- ✅ **GraphQL API**: 新一代API，78个操作
- ✅ **双API共存**: 平滑迁移路径

### API选择指南

**何时使用REST API**:
- ✅ 简单的CRUD操作
- ✅ 需要标准HTTP状态码
- ✅ 缓存策略明确
- ✅ 与现有系统集成

**何时使用GraphQL API**:
- ✅ 需要灵活的数据查询
- ✅ 复杂的关联数据获取
- ✅ 实时数据订阅
- ✅ 减少网络请求次数

### 迁移建议

**渐进式迁移路径**:
```
REST API → GraphQL混合 → 完全GraphQL
  ↓            ↓              ↓
 当前状态    推荐方案      未来目标
```

**迁移示例**:
```javascript
// REST API
const events = await fetch('/api/events?game_gid=10000147').then(r => r.json());

// GraphQL API (等效查询)
const query = gql`
  query GetEvents($gameGid: Int!) {
    events(gameGid: $gameGid) {
      id
      eventName
      eventNameCn
    }
  }
`;
const { data } = await client.query({ query, variables: { gameGid: 10000147 } });
```

### 版本兼容性

| API版本 | 状态 | 废弃计划 |
|---------|------|----------|
| REST API V8.0.0 | ✅ 稳定 | 无计划 |
| GraphQL API V1.0 | ✅ 稳定 | 无计划 |
| REST API V7.x | ⚠️ 维护模式 | 2027-01-01 |

---

## 快速参考

### 游戏上下文

**所有API需要游戏上下文** (`game_gid`):

```bash
# 推荐方式：使用业务GID
GET /api/events?game_gid=10000147

# 向后兼容：也支持game_id（将逐步废弃）
GET /api/events?game_id=1
```

### 分页参数

**支持分页的API**:

```bash
GET /api/events?page=1&per_page=20
```

- `page`: 页码（从1开始，默认1）
- `per_page`: 每页数量（默认20，最大100）

### 批量操作

**支持批量操作的API**:

```bash
# 批量删除
DELETE /api/events/batch
Body: {"ids": [1, 2, 3]}

# 批量更新
PUT /api/events/batch-update
Body: {"ids": [1, 2, 3], "updates": {...}}
```

---

## 安全性

### 输入验证

- ✅ **Pydantic Entity验证**: 自动类型检查和长度限制
- ✅ **XSS防护**: HTML实体转义
- ✅ **SQL注入防护**: 参数化查询
- ✅ **长度限制**: 防止DoS攻击

### 游戏保护

**STAR001保护规则**:
```python
# ✅ 正确：使用测试GID
TEST_GID_START = 90000000

# ❌ 错误：禁止删除生产数据
game_gid = 10000147  # STAR001 - 禁止删除
```

详见: [STAR001-GAME-PROTECTION.md](../development/STAR001-GAME-PROTECTION.md)

---

## 性能优化

### 缓存策略

**读操作**:
```python
@cached(ttl=1800)  # 30分钟缓存
def get_events(game_gid):
    ...
```

**写操作**:
```python
@cache_invalidate  # 自动清理缓存
def create_event(game_gid, data):
    ...
```

### 性能指标

| 操作 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 获取参数列表 | 267ms | 88ms | 67% |
| 获取游戏列表 | 120ms | 45ms | 63% |
| 创建事件 | 350ms | 150ms | 57% |

---

## 错误处理

### 标准错误响应

```json
{
  "success": false,
  "error": "错误描述",
  "message": "用户友好的错误消息"
}
```

### 常见错误

| 错误 | 状态码 | 解决方案 |
|------|--------|----------|
| `game_gid required` | 400 | 提供game_gid参数 |
| `Game not found` | 404 | 检查game_gid是否正确 |
| `Validation error` | 400 | 检查请求参数格式 |
| `Already exists` | 409 | 资源已存在，使用唯一标识 |

---

## 开发指南

### 前端调用示例

```javascript
// 获取游戏列表
const games = await fetch('/api/games').then(r => r.json());

// 获取事件（带分页）
const events = await fetch('/api/events?game_gid=10000147&page=1&per_page=20')
  .then(r => r.json());

// 创建事件
const result = await fetch('/api/events', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    game_gid: 10000147,
    event_name: 'login',
    event_name_cn: '登录'
  })
}).then(r => r.json());
```

### cURL示例

```bash
# 获取游戏列表
curl http://127.0.0.1:5001/api/games

# 获取事件
curl http://127.0.0.1:5001/api/events?game_gid=10000147

# 创建事件
curl -X POST http://127.0.0.1:5001/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "game_gid": 10000147,
    "event_name": "login",
    "event_name_cn": "登录"
  }'
```

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 8.0.0 | 2026-03-02 | 双API架构：REST 84端点 + GraphQL 78操作 |
| 8.0.0 | 2026-03-01 | V8.0.0架构：100% ERS覆盖、缓存100%覆盖 |
| 7.8.0 | 2026-02-26 | Entity架构统一完成 |
| 7.6.0 | 2026-02-25 | 缓存系统文档完善 |
| 7.0.0 | 2026-02-10 | ERS架构引入 |

---

## 相关文档

### 架构与开发
- [架构设计](../development/architecture.md)
- [开发指南](../development/contributing.md)
- [API开发规范](../development/api-development.md)
- [缓存系统](../cache/README.md)

### API文档
- [GraphQL API](GRAPHQL_API.md) - GraphQL接口文档
- [REST到GraphQL迁移指南](REST_TO_GRAPHQL_MIGRATION.md) - 迁移最佳实践
- [迁移进度报告](MIGRATION_PROGRESS_REPORT.md) - 迁移状态跟踪
- [API状态](API_STATUS.md) - API健康状态

### 测试与验证
- [迁移测试报告](MIGRATION_TEST_REPORT.md) - 测试覆盖
- [REST API移除计划](REST_API_REMOVAL_PLAN.md) - 废弃路线图

---

## 联系方式

- **项目**: Event2Table
- **文档维护**: Event2Table Development Team
- **最后更新**: 2026-03-02

---

## API统计总览

| API类型 | 端点/操作数 | 调用次数 | 覆盖率 | 状态 |
|---------|-------------|----------|--------|------|
| **REST API** | 84个端点 | - | 100% | ✅ 稳定 |
| **GraphQL API** | 78个操作 | 113次调用 | 100% | ✅ 稳定 |
| **总计** | 162个 | - | 100% | ✅ 生产就绪 |

**模块分布**:
- 核心业务模块: 39个REST端点 + 45个GraphQL操作
- 支持模块: 45个REST端点 + 33个GraphQL操作
- 缓存系统: 23个REST端点（共享）
- Canvas/Flows: 11个REST端点（专用）
