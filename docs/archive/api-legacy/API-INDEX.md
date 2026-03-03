# API索引 - 快速参考

**Event2Table API完整端点列表**

**版本**: 8.0.0
**最后更新**: 2026-03-01

---

## Categories API (8 endpoints)

| 方法 | 端点 | 描述 | Phase |
|------|------|------|-------|
| GET | `/api/categories` | 列出分类 | Phase 1 |
| GET | `/api/categories/<id>` | 获取单个分类 | Phase 1 |
| POST | `/api/categories` | 创建分类 | Phase 1 |
| PUT/PATCH | `/api/categories/<id>` | 更新分类 | Phase 1 |
| DELETE | `/api/categories/<id>` | 删除分类 | Phase 1 |
| POST | `/api/categories/batch-delete` | 批量删除分类 | Phase 3 |
| PUT | `/api/categories/batch-update` | 批量更新分类 | Phase 5 |
| GET | `/api/categories/stats` | 获取分类统计 | Phase 5 |

**详细文档**: [CATEGORIES-API.md](CATEGORIES-API.md)

---

## Events API (8 endpoints)

| 方法 | 端点 | 描述 | Phase |
|------|------|------|-------|
| GET | `/api/events` | 列出事件（分页） | Phase 3 |
| GET | `/api/events/<id>` | 获取事件详情 | Phase 1 |
| POST | `/api/events` | 创建事件 | Phase 1 |
| PUT/PATCH | `/api/events/<id>` | 更新事件 | Phase 1 |
| DELETE | `/api/events/batch` | 批量删除事件 | Phase 3 |
| PUT | `/api/events/batch-update` | 批量更新事件 | Phase 5 |
| GET | `/api/events/<id>/parameters` | 获取事件参数 | Phase 2 |
| GET | `/api/events/<event_id>/params` | 获取参数（别名） | Phase 2 |

**详细文档**: [EVENTS-API.md](EVENTS-API.md)

---

## Parameters API (16 endpoints)

### 基础CRUD

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/parameters/all` | 获取所有参数（去重） |
| GET | `/api/parameters/<id>` | 获取单个参数 |
| POST | `/api/parameters` | 创建参数 |
| PUT | `/api/parameters/<id>` | 更新参数 |
| DELETE | `/api/parameters/<id>` | 删除参数 |

### 查询和统计

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/parameters/<param_name>/details` | 获取参数详情 |
| GET | `/api/parameters/stats` | 获取参数统计 |
| POST | `/api/parameters/search` | 搜索参数 |
| GET | `/api/parameters/common` | 获取通用参数 |
| GET | `/api/parameters/validate` | 验证参数名称 |

### 参数库管理

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/param-library/check` | 检查参数库 |
| POST | `/api/event-params/<param_id>/link-library` | 关联到参数库 |
| POST | `/api/param-library/batch-check` | 批量检查参数库 |

### 其他功能

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/alter-table/<param_id>` | 生成ALTER TABLE SQL |

**详细文档**: [PARAMETERS-API.md](PARAMETERS-API.md)

---

## Field Builder API (6 endpoints)

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/field-builder/configs` | 列出配置 |
| GET | `/api/field-builder/configs/<id>` | 获取配置 |
| POST | `/api/field-builder/configs` | 创建配置 |
| PUT/PATCH | `/api/field-builder/configs/<id>` | 更新配置 |
| DELETE | `/api/field-builder/configs/<id>` | 删除配置 |
| POST | `/api/field-builder/preview` | 预览HQL |

**详细文档**: [FIELD-BUILDER-API.md](FIELD-BUILDER-API.md)

---

## Games API (7 endpoints)

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/games` | 列出游戏 |
| GET | `/api/games/<game_gid>` | 获取游戏详情 |
| POST | `/api/games` | 创建游戏 |
| PUT/PATCH | `/api/games/<game_gid>` | 更新游戏 |
| DELETE | `/api/games/<game_gid>` | 删除游戏 |
| POST | `/api/games/batch-update` | 批量更新游戏 |
| DELETE | `/api/games/batch` | 批量删除游戏 |

**详细文档**: [GAMES-API.md](GAMES-API.md)

---

## Join Configs API (5 endpoints)

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/join-configs` | 列出JOIN配置 |
| GET | `/api/join-configs/<id>` | 获取配置 |
| POST | `/api/join-configs` | 创建配置 |
| PUT/PATCH | `/api/join-configs/<id>` | 更新配置 |
| DELETE | `/api/join-configs/<id>` | 删除配置 |

**详细文档**: [JOIN-CONFIGS-API.md](JOIN-CONFIGS-API.md)

---

## Flows/Canvas API (11 endpoints)

### 流程管理

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/flows` | 列出流程 |
| GET | `/api/flows/<flow_id>` | 获取流程 |
| POST | `/api/flows` | 创建流程 |
| PUT | `/api/flows/<flow_id>` | 更新流程 |
| DELETE | `/api/flows/<flow_id>` | 删除流程 |
| POST | `/api/flows/<flow_id>/load` | 加载流程数据 |
| POST | `/api/flows/generate` | 生成HQL |

### 批量操作

| 方法 | 端点 | 描述 |
|------|------|------|
| DELETE | `/api/flows/batch` | 批量删除流程 |
| PUT | `/api/flows/batch-update` | 批量更新流程 |

### Canvas别名端点

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/canvas/api/flows/save` | 保存流程（别名） |
| GET | `/canvas/api/flows/<flowId>` | 获取流程（别名） |
| POST | `/canvas/api/execute` | 执行流程（别名） |
| GET | `/canvas/api/canvas/health` | Canvas健康检查 |
| POST | `/canvas/api/preview-results` | 预览执行结果 |

**详细文档**: [FLOWS-API.md](FLOWS-API.md)

---

## Cache API (23 endpoints)

### 统计和监控

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/cache/stats` | 获取缓存统计 |
| GET | `/api/cache/stats/detailed` | 获取详细统计 |
| GET | `/api/cache/monitoring/alerts` | 获取告警列表 |
| GET | `/api/cache/monitoring/metrics` | 获取Prometheus指标 |
| GET | `/api/cache/monitoring/trends` | 获取性能趋势 |

### 缓存键管理

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/cache/keys` | 列出缓存键 |
| GET | `/api/cache/keys/search` | 搜索缓存键 |
| GET | `/api/cache/keys/<key>` | 获取键详情 |
| DELETE | `/api/cache/keys/<key>` | 删除键 |

### 缓存操作

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/cache/clear` | 清空所有缓存 |
| POST | `/api/cache/invalidate/game/<game_gid>` | 失效游戏缓存 |
| POST | `/api/cache/invalidate/event/<event_id>` | 失效事件缓存 |

### 容量监控

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/cache/capacity/l1` | 获取L1容量 |
| GET | `/api/cache/capacity/l2` | 获取L2容量 |
| GET | `/api/cache/capacity/prediction` | 容量预测 |

### 布隆过滤器

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/cache/bloom-filter/rebuild` | 重建布隆过滤器 |
| GET | `/api/cache/bloom-filter/stats` | 布隆过滤器统计 |

### 智能预热

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/cache/warm-up/predict` | 预测热点键 |
| POST | `/api/cache/warm-up/execute` | 执行预热 |

### 降级管理

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/cache/degradation/status` | 获取降级状态 |
| POST | `/api/cache/degradation/switch` | 切换降级模式 |

**详细文档**: [CACHE-API.md](CACHE-API.md)

---

## 端点统计

### 按模块分类

| 模块 | 端点数 | Phase |
|------|--------|-------|
| Categories | 8 | Phase 5增强 |
| Events | 8 | Phase 5完全迁移 |
| Parameters | 16 | Phase 5大幅扩展 |
| Field Builder | 6 | Phase 5新增 |
| Games | 7 | Phase 1-2 |
| Join Configs | 5 | Phase 3 |
| Flows/Canvas | 11 | Phase 2-3 |
| Cache | 23 | 完整实现 |
| **总计** | **84** | - |

### 按HTTP方法分类

| 方法 | 端点数 | 占比 |
|------|--------|------|
| GET | 38 | 45% |
| POST | 28 | 33% |
| PUT | 10 | 12% |
| DELETE | 8 | 10% |
| **总计** | **84** | 100% |

---

## 架构覆盖率

### ERS架构

| 层 | 覆盖率 | 说明 |
|------|--------|------|
| Entity层 | 100% | 所有模块使用Pydantic Entity |
| Repository层 | 100% | 所有模块使用Repository模式 |
| Service层 | 100% | 所有模块使用Service封装 |
| API层 | 100% | 统一响应格式 |

### 缓存覆盖

| 类型 | 端点数 | TTL |
|------|--------|-----|
| 读缓存 | 42 | 60-1800秒 |
| 写失效 | 28 | 自动 |
| 无缓存 | 14 | 实时数据 |
| **覆盖率** | **83%** | - |

---

## 性能基准

### 平均响应时间

| 操作 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 获取参数列表 | 267ms | 88ms | 67% |
| 获取游戏列表 | 120ms | 45ms | 63% |
| 获取事件列表 | 200ms | 95ms | 53% |
| 创建事件 | 350ms | 150ms | 57% |
| 更新游戏 | 180ms | 95ms | 47% |

### 缓存命中率

| 端点类型 | 命中率 |
|----------|--------|
| 列表查询 | 85% |
| 详情查询 | 90% |
| 统计查询 | 92% |

---

## 兼容性

### 向后兼容

- ✅ 所有旧端点保持可用
- ✅ game_id参数继续支持（逐步废弃）
- ✅ 旧响应格式保持兼容

### 新特性

- ✅ game_gid参数（推荐）
- ✅ 分页支持
- ✅ 批量操作
- ✅ 统计查询

---

## 快速开始

### 1. 获取游戏列表

```bash
curl http://127.0.0.1:5001/api/games
```

### 2. 获取事件（分页）

```bash
curl "http://127.0.0.1:5001/api/events?game_gid=10000147&page=1&per_page=20"
```

### 3. 创建事件

```bash
curl -X POST http://127.0.0.1:5001/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "game_gid": 10000147,
    "event_name": "login",
    "event_name_cn": "登录"
  }'
```

### 4. 获取缓存统计

```bash
curl http://127.0.0.1:5001/api/cache/stats
```

---

## 相关文档

- [API文档首页](README.md)
- [架构设计](../development/architecture.md)
- [缓存系统](../cache/README.md)
- [开发指南](../development/contributing.md)

---

**文档版本**: 8.0.0
**最后更新**: 2026-03-01
**维护者**: Event2Table Development Team
