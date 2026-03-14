# Cache TTL快速参考指南

> **最后更新**: 2026-03-10
> **用途**: 快速查找合理的缓存TTL设置

---

## 🚀 快速查找表

### 按数据类型查找TTL

| 数据类型 | 推荐TTL | 理由 | 示例 |
|---------|---------|------|------|
| **实时统计** | 180秒 | 变化频繁，需要相对新鲜 | 参数使用统计 |
| **中等变化统计** | 600秒 | 变化较慢，可以较长缓存 | 事件统计 |
| **Dashboard统计** | 300秒 | 包含近期数据，需要新鲜 | Dashboard概览 |
| **游戏统计** | 1800秒 | 游戏数据中等变化 | 游戏详情统计 |
| **列表数据** | 300-1800秒 | 根据变化频率调整 | 游戏列表、事件列表 |
| **详情数据** | 600-3600秒 | 相对稳定，可以较长缓存 | 游戏详情、事件详情 |
| **配置数据** | 7200秒 | 静态配置，很少变化 | 系统配置、枚举 |

---

## 📋 标准TTL常量

```python
# backend/core/config/config.py

# 静态数据 (2小时) - 游戏列表、分类列表
CACHE_TIMEOUT_STATIC = 7200

# 半静态数据 (10分钟) - 参数、模板
CACHE_TIMEOUT_SEMI_STATIC = 600

# 动态数据 (2分钟) - 事件列表
CACHE_TIMEOUT_DYNAMIC = 120

# 实时数据 (30秒) - 搜索结果
CACHE_TIMEOUT_REALTIME = 30

# 统计数据 (5分钟)
CACHE_TIMEOUT_STATS = 300
```

---

## 🎯 使用场景示例

### 场景1: 参数使用统计

```python
from backend.core.cache.decorators import cached

@cached("parameters.usage_stats", timeout=180)
def usage_stats(game_gid: Optional[int] = None):
    """
    ⚡ TTL: 180秒 (3分钟)
    理由: 参数使用统计数据变化频率中等
    - 参数创建/更新/删除会改变统计
    - 3分钟TTL平衡了实时性和性能
    """
    pass
```

### 场景2: 事件统计

```python
from backend.core.cache.decorators import cached

@cached("events.statistics", timeout=600)
def get_event_statistics(event_id: int):
    """
    ⚡ TTL: 600秒 (10分钟)
    理由: 事件统计数据变化较慢
    - 事件统计（参数数量、使用频率等）相对稳定
    - 10分钟TTL减少数据库查询，提升性能
    """
    pass
```

### 场景3: Dashboard统计

```python
from backend.core.cache.decorators import cached

@cached(ttl=300, key_prefix="dashboard.stats")
def resolve_dashboard_stats(root, info):
    """
    ⚡ TTL: 300秒 (5分钟) + key_prefix
    理由: Dashboard统计包含"7天内数据"，需要相对新鲜的数据
    - 5分钟TTL平衡了实时性和性能
    - key_prefix避免与其他缓存键冲突
    """
    pass
```

### 场景4: 游戏列表

```python
from backend.core.cache.decorators import cached

@cached("games.list", timeout=1800)
def get_all_games(include_stats: bool = False):
    """
    ⚡ TTL: 1800秒 (30分钟)
    理由: 游戏列表中等变化频率
    - 游戏基本信息相对稳定，但事件数量变化较快
    - 30分钟TTL平衡了数据新鲜度和性能
    """
    pass
```

---

## ⚠️ 常见错误

### 错误1: TTL过长导致数据过期

```python
# ❌ 错误: 参数列表缓存2小时
@cached("parameters.list", timeout=7200)
def get_parameters():
    pass

# ✅ 正确: 参数列表缓存10分钟
@cached("parameters.list", timeout=600)
def get_parameters():
    pass
```

### 错误2: TTL过短导致性能下降

```python
# ❌ 错误: 游戏详情缓存30秒
@cached("games.detail", timeout=30)
def get_game_by_gid(game_gid: int):
    pass

# ✅ 正确: 游戏详情缓存1小时
@cached("games.detail", timeout=3600)
def get_game_by_gid(game_gid: int):
    pass
```

### 错误3: 缺少key_prefix导致键冲突

```python
# ❌ 错误: 没有key_prefix，可能与其他模块冲突
@cached(ttl=300)
def resolve_dashboard_stats(root, info):
    pass

# ✅ 正确: 添加key_prefix避免键冲突
@cached(ttl=300, key_prefix="dashboard.stats")
def resolve_dashboard_stats(root, info):
    pass
```

---

## 🔧 缓存装饰器使用指南

### 基本用法

```python
from backend.core.cache.decorators import cached

# 方式1: 使用字符串键
@cached("module.key", timeout=300)
def get_data():
    pass

# 方式2: 使用key_prefix（推荐用于GraphQL）
@cached(ttl=300, key_prefix="dashboard.stats")
def resolve_stats(root, info):
    pass
```

### 缓存失效

```python
from backend.core.cache.decorators import cache_invalidate

@cache_invalidate  # 自动失效所有相关缓存
def create_data():
    pass

@cache_invalidate("module:*")  # 失效特定模式的缓存
def update_data():
    pass
```

---

## 📊 缓存性能监控

### 检查缓存命中率

```python
from backend.core.cache.cache_system import cache_result

stats = cache_result.get_stats()
print(f"命中率: {stats['hit_rate']}%")
print(f"总键数: {stats['total_keys']}")
print(f"L1大小: {stats['l1_size']}")
print(f"L2大小: {stats['l2_size']}")
```

### 检查特定缓存键的TTL

```bash
# 使用redis-cli
redis-cli

# 查看所有键
KEYS *

# 检查特定键的TTL
TTL "parameters.usage_stats:default"
TTL "events.statistics:default"
TTL "games.list:default"
```

---

## ✅ 检查清单

在设置缓存TTL时，请确认：

- [ ] TTL是否符合数据变化特征？
- [ ] 是否添加了key_prefix避免键冲突？
- [ ] 写操作是否失效了相关缓存？
- [ ] 是否添加了TTL设置理由的注释？
- [ ] TTL是否在合理范围内（30秒-7200秒）？

---

## 📚 相关文档

- [缓存系统完整文档](/Users/mckenzie/Documents/event2table/docs/cache/)
- [TTL优化完成报告](/Users/mckenzie/Documents/event2table/docs/reports/2026-03-10/CACHE-TTL-OPTIMIZATION-SUMMARY.md)
- [性能模式 - 缓存失效](/Users/mckenzie/Documents/event2table/docs/lessons-learned/performance-patterns.md#缓存失效分析)

---

**文档版本**: 1.0
**最后更新**: 2026-03-10
**维护者**: Event2Table Development Team
