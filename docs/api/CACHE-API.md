# Cache API

**缓存管理API**

**版本**: 8.0.0
**文件**: `backend/api/routes/cache.py`

---

## 概述

Cache API提供完整的缓存管理功能，包括统计查询、键管理、失效操作和监控告警。

**核心特性**:
- ✅ 缓存统计查询
- ✅ 缓存键管理
- ✅ 缓存失效操作
- ✅ 性能监控
- ✅ 容量预测
- ✅ 智能预热

---

## 端点分类

### 统计和监控 (5 endpoints)

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/cache/stats` | 获取缓存统计 |
| GET | `/api/cache/stats/detailed` | 获取详细统计 |
| GET | `/api/cache/monitoring/alerts` | 获取告警列表 |
| GET | `/api/cache/monitoring/metrics` | 获取Prometheus指标 |
| GET | `/api/cache/monitoring/trends` | 获取性能趋势 |

### 缓存键管理 (4 endpoints)

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/cache/keys` | 列出缓存键 |
| GET | `/api/cache/keys/search` | 搜索缓存键 |
| GET | `/api/cache/keys/<key>` | 获取键详情 |
| DELETE | `/api/cache/keys/<key>` | 删除键 |

### 缓存操作 (3 endpoints)

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/cache/clear` | 清空所有缓存 |
| POST | `/api/cache/invalidate/game/<game_gid>` | 失效游戏缓存 |
| POST | `/api/cache/invalidate/event/<event_id>` | 失效事件缓存 |

### 容量监控 (3 endpoints)

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/cache/capacity/l1` | 获取L1容量 |
| GET | `/api/cache/capacity/l2` | 获取L2容量 |
| GET | `/api/cache/capacity/prediction` | 容量预测 |

### 布隆过滤器 (2 endpoints)

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/cache/bloom-filter/rebuild` | 重建布隆过滤器 |
| GET | `/api/cache/bloom-filter/stats` | 布隆过滤器统计 |

### 智能预热 (2 endpoints)

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/cache/warm-up/predict` | 预测热点键 |
| POST | `/api/cache/warm-up/execute` | 执行预热 |

### 降级管理 (2 endpoints)

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/cache/degradation/status` | 获取降级状态 |
| POST | `/api/cache/degradation/switch` | 切换降级模式 |

---

## 核心端点详情

### GET /api/cache/stats

获取缓存统计信息。

**响应示例**:
```json
{
  "success": true,
  "timestamp": "2026-03-01T10:00:00",
  "l1_cache": {
    "size": 450,
    "capacity": 1000,
    "usage": "45.0%",
    "hits": 15234,
    "sets": 3456,
    "evictions": 123
  },
  "l2_cache": {
    "total_keys": 5000,
    "memory_used": "256MB",
    "hit_rate": "85.2%"
  },
  "overall": {
    "total_requests": 20000,
    "total_hits": 17000,
    "hit_rate": "85.0%"
  }
}
```

---

### POST /api/cache/clear

清空所有缓存。

**响应示例**:
```json
{
  "success": true,
  "message": "缓存已清空: L1=450条, L2=5000个键",
  "details": {
    "l1_cleared": 450,
    "l2_cleared": 5000,
    "total_cleared": 5450
  }
}
```

---

### POST /api/cache/invalidate/game/<game_gid>

失效游戏相关缓存。

**响应示例**:
```json
{
  "success": true,
  "message": "游戏缓存已失效: 15个键",
  "game_gid": 10000147,
  "invalidated_keys": [
    "games:detail:gid:10000147",
    "events:list:game_gid:10000147",
    "parameters:all:game_gid:10000147"
  ]
}
```

---

## 相关文档

- [缓存系统文档](../cache/README.md) - 完整缓存文档
- [5分钟快速开始](../cache/quickstart/5-minute-guide.md) - 快速上手
