# REST API移除计划

## 移除原则

根据前端使用情况和GraphQL覆盖度,分阶段移除REST API。

## 阶段1: 立即移除 (无前端使用)

以下REST API模块已完全迁移到GraphQL,且无前端直接调用,可立即移除:

### 1. Dashboard API
- **文件**: `backend/api/routes/dashboard.py`
- **GraphQL替代**: `dashboardStats`, `gameStats`, `allGameStats` queries
- **前端使用**: 无
- **状态**: ✅ 可立即移除

### 2. Templates API
- **文件**: `backend/api/routes/templates.py`
- **GraphQL替代**: `template`, `templates`, `searchTemplates` queries
- **前端使用**: 无
- **状态**: ✅ 可立即移除

### 3. Nodes API
- **文件**: `backend/api/routes/nodes.py`
- **GraphQL替代**: `node`, `nodes` queries
- **前端使用**: 无
- **状态**: ✅ 可立即移除

## 阶段2: 逐步迁移后移除 (前端仍在使用)

以下REST API需要前端迁移完成后才能移除:

### 1. Games API
- **文件**: `backend/api/routes/games.py`
- **GraphQL替代**: `game`, `games`, `searchGames` queries
- **前端使用**: 8次调用
- **迁移优先级**: 🔴 高
- **预计移除时间**: 2周后

### 2. Events API
- **文件**: `backend/api/routes/events.py`
- **GraphQL替代**: `event`, `events`, `searchEvents` queries
- **前端使用**: 1次调用 (batch)
- **迁移优先级**: 🟡 中
- **预计移除时间**: 3周后

### 3. Parameters API
- **文件**: `backend/api/routes/parameters.py`
- **GraphQL替代**: `parameter`, `parameters` queries
- **前端使用**: 1次调用
- **迁移优先级**: 🟡 中
- **预计移除时间**: 3周后

### 4. Categories API
- **文件**: `backend/api/routes/categories.py`
- **GraphQL替代**: `category`, `categories` queries
- **前端使用**: 1次调用 (batch)
- **迁移优先级**: 🟡 中
- **预计移除时间**: 3周后

### 5. Flows API
- **文件**: `backend/api/routes/flows.py`
- **GraphQL替代**: `flow`, `flows` queries
- **前端使用**: 2次调用
- **迁移优先级**: 🟡 中
- **预计移除时间**: 3周后

## 阶段3: 长期保留 (特殊用途)

以下REST API因特殊用途需长期保留:

### 1. HQL生成API
- **文件**: `backend/api/routes/hql_generation.py`, `hql_preview_v2.py`
- **原因**: 命令型操作,REST更合适
- **状态**: ⚙️ 长期保留

### 2. 字段构建器API
- **文件**: `backend/api/routes/field_builder.py`
- **原因**: 单表简单CRUD,迁移收益低
- **状态**: ⚙️ 长期保留

### 3. 监控API
- **文件**: `backend/api/routes/monitoring.py`
- **原因**: 运维监控用途
- **状态**: ⚙️ 长期保留

### 4. 缓存管理API
- **文件**: `backend/api/routes/cache.py`
- **原因**: 运维管理用途
- **状态**: ⚙️ 长期保留

### 5. V1适配器API
- **文件**: `backend/api/routes/v1_adapter.py`
- **原因**: 兼容性适配层
- **状态**: ⚠️ 待评估,可能移除

## 移除步骤

### 步骤1: 标记为废弃
```python
@api_bp.route('/api/dashboard', methods=['GET'])
@deprecation_warning  # 添加废弃警告
def get_dashboard():
    # 现有实现
    pass
```

### 步骤2: 添加迁移提示
在响应中添加GraphQL替代方案:
```json
{
  "data": {...},
  "_deprecated": true,
  "_warning": "此API已废弃,请使用GraphQL",
  "_graphql_query": "dashboardStats"
}
```

### 步骤3: 监控使用情况
记录API调用频率,确认无使用后移除:
```python
logger.warning(f"Deprecated API called: {request.path}")
```

### 步骤4: 移除代码
确认无使用后,删除路由文件和注册:
```python
# 从 backend/api/__init__.py 移除导入
# 删除路由文件
```

## 移除时间表

| 阶段 | API模块 | 移除时间 | 负责人 |
|------|---------|---------|--------|
| 阶段1 | dashboard, templates, nodes | 2026-03-15 | 后端团队 |
| 阶段2 | games | 2026-03-22 | 前端+后端 |
| 阶段2 | events, parameters, categories, flows | 2026-03-29 | 前端+后端 |
| 阶段3 | v1_adapter (评估) | 2026-04-15 | 架构师 |

## 风险评估

### 低风险 🟢
- dashboard, templates, nodes: 无前端使用,GraphQL完整覆盖

### 中风险 🟡
- games, events, parameters, categories, flows: 需前端迁移配合

### 高风险 🔴
- 无

## 回滚计划

如果移除后发现问题:
1. 从Git历史恢复路由文件
2. 重新注册Blueprint
3. 重启服务

## 成功标准

- [ ] 所有阶段1 API已移除
- [ ] 前端已迁移到GraphQL
- [ ] 无API调用错误
- [ ] 性能无下降
- [ ] 文档已更新

---

**创建日期**: 2026-03-01  
**最后更新**: 2026-03-01  
**维护者**: Event2Table团队
