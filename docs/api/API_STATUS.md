# API状态文档

## 当前API架构

Event2Table项目正在从REST API迁移到GraphQL API,本文档记录当前API状态和迁移进度。

**最后更新**: 2026-03-01

## GraphQL API (推荐)

### 端点
- **URL**: `http://localhost:5001/api/graphql`
- **IDE**: `http://localhost:5001/api/graphql` (GraphiQL)
- **方法**: POST

### 功能覆盖

#### 查询 (Queries) - 28个
- **游戏管理**: `game`, `games`, `searchGames`
- **事件管理**: `event`, `events`, `searchEvents`
- **参数管理**: `parameter`, `parameters`, `searchParameters`
- **分类管理**: `category`, `categories`, `searchCategories`
- **仪表盘**: `dashboardStats`, `gameStats`, `allGameStats`
- **模板管理**: `template`, `templates`, `searchTemplates`
- **节点管理**: `node`, `nodes`
- **流程管理**: `flow`, `flows`
- **事件参数**: `eventParameterExtended`, `paramHistory`, `paramConfig`, `validationRules`
- **Join配置**: `joinConfig`, `joinConfigs`

#### 变更 (Mutations) - 50个
- **CRUD操作**: 所有实体的create/update/delete
- **批量操作**: batch mutations
- **高级操作**: rollback, validation, config management

### 性能优势
- ✅ DataLoader批量加载,减少90%的N+1查询
- ✅ 按需获取字段,避免over-fetching
- ✅ 三级缓存架构 (L1/L2/L3)
- ✅ 查询性能提升62.5%

### 使用示例

```graphql
# 获取游戏列表
query GetGames {
  games(limit: 10, offset: 0) {
    id
    gid
    name
    eventCount
    parameterCount
  }
}

# 创建游戏
mutation CreateGame {
  createGame(gid: 10000147, name: "新游戏", ods_db: "ieu_ods") {
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

## REST API (已废弃)

### 废弃状态
- **废弃日期**: 2026-04-30
- **下线日期**: 2026-07-31
- **迁移目标**: GraphQL API

### 仍在使用的REST API

根据前端代码扫描结果,以下REST API仍在使用:

#### 高优先级迁移 (频繁使用)
1. **`/api/games`** - 9次调用
   - 文件: GameManagementModal.tsx, GameForm.tsx, useGameContext.ts等
   - GraphQL替代: `games` query
   - 迁移状态: ⚠️ 待迁移

2. **`/api/flows`** - 2次调用
   - 文件: Toolbar.tsx, Dashboard.tsx
   - GraphQL替代: `flows` query
   - 迁移状态: ⚠️ 待迁移

#### 中优先级迁移 (偶尔使用)
3. **`/api/categories`** - 1次调用
   - 文件: CategoryManagementModal.tsx
   - GraphQL替代: `categories` query
   - 迁移状态: ⚠️ 待迁移

4. **`/api/flows/execute`** - 1次调用
   - 文件: useFlowExecute.ts
   - GraphQL替代: 保留(命令型操作)
   - 迁移状态: ⚙️ 长期保留

#### 特殊用途 (长期保留)
5. **`/api/generate`** - HQL生成
   - 迁移状态: ⚙️ 长期保留 (命令型操作)

6. **`/api/hql/results`** - HQL结果查询
   - 迁移状态: ⚙️ 长期保留

7. **`/api/preview-excel`** - Excel预览
   - 迁移状态: ⚙️ 长期保留

8. **`/api/events/import`** - 事件导入
   - 迁移状态: ⚙️ 长期保留

9. **批量操作API** - `/api/*/batch`
   - 迁移状态: ⚙️ 长期保留

### 已移除的REST API

以下REST API已完全移除,由GraphQL替代:

- ✅ `dashboard.py` → GraphQL queries
- ✅ `templates.py` → GraphQL queries
- ✅ `nodes.py` → GraphQL queries
- ✅ `event_parameters.py` → GraphQL queries
- ✅ `join_configs.py` → GraphQL queries

## 迁移进度

### 总体进度
- **GraphQL使用**: 84.3% (113次调用)
- **REST API使用**: 15.7% (21次调用)
- **迁移进度**: ███████████████████████████████░░░░░░░ 84.3%

### 分阶段计划

#### 阶段1: 已完成 ✅
- 移除无前端使用的API (dashboard, templates, nodes)
- GraphQL功能完整覆盖
- 迁移工具和文档就绪

#### 阶段2: 进行中 🔄
- 迁移高频使用的API (games, flows, categories)
- 预计完成时间: 2-4周
- 负责人: 前端团队

#### 阶段3: 计划中 📋
- 评估特殊用途API的迁移可行性
- 预计完成时间: 1-3个月
- 负责人: 架构师

## 迁移资源

### 文档
- [REST到GraphQL迁移指南](./REST_TO_GRAPHQL_MIGRATION.md)
- [REST API移除计划](./REST_API_REMOVAL_PLAN.md)
- [迁移进度报告](./MIGRATION_PROGRESS_REPORT.md)

### 工具
- **迁移转换器**: `scripts/rest_to_graphql_converter.py`
- **进度检查工具**: `scripts/check_migration_progress.py`
- **API移除脚本**: `scripts/remove_rest_api_stage1.py`

### 示例代码
- **游戏管理迁移示例**: `frontend/src/migration/GAMES_MIGRATION_EXAMPLE.ts`

### 支持
- **GraphiQL IDE**: http://localhost:5001/api/graphql
- **技术支持**: 项目内部技术群
- **问题反馈**: 项目Issue仓库

## 性能对比

| 指标 | REST API | GraphQL API | 改进 |
|------|---------|-------------|------|
| 游戏列表查询 | 120ms | 45ms | 62.5% ↓ |
| 关联数据查询 | 350ms | 80ms | 77.1% ↓ |
| 批量操作 | 500ms | 150ms | 70% ↓ |
| 缓存命中率 | 60% | 85% | 41.7% ↑ |
| N+1查询 | 频繁 | 极少 | 90% ↓ |

## 注意事项

### 对于前端开发者
1. ⚠️ 所有新功能必须使用GraphQL API
2. ⚠️ 现有REST API调用需在2026-04-30前迁移
3. ✅ 使用Apollo Client进行GraphQL查询
4. ✅ 参考迁移示例和工具

### 对于后端开发者
1. ✅ GraphQL API已完整实现
2. ✅ 三级缓存架构已统一
3. ⚠️ REST API仅保留必要的特殊用途API
4. ⚠️ 废弃警告中间件已启用

### 对于运维人员
1. ✅ 监控系统已就绪
2. ✅ 缓存管理API可用
3. ⚠️ 需关注废弃API使用情况
4. ⚠️ 准备REST API下线计划

## 更新日志

### 2026-03-01
- 创建API状态文档
- 更新迁移进度至84.3%
- 添加性能对比数据
- 完善迁移资源链接

### 2026-02-28
- 归档REST API文件到archive目录
- 更新废弃日期至2026-04-30
- 创建迁移工具和文档

### 2026-02-21
- 初始REST API归档
- GraphQL API完整实现
- 启动迁移计划

---

**维护者**: Event2Table团队
**联系方式**: 项目内部技术群
