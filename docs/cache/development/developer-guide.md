# 缓存系统开发者指南

> **面向**: 后端开发者
> **目标**: 深入了解缓存系统架构和高级用法
> **版本**: 1.0

---

## 📚 目录

1. [系统架构](#系统架构)
2. [核心模块](#核心模块)
3. [装饰器详解](#装饰器详解)
4. [高级功能](#高级功能)
5. [最佳实践](#最佳实践)
6. [性能优化](#性能优化)
7. [测试指南](#测试指南)

---

## 系统架构

### 三级分层缓存

```
┌─────────────────────────────────────────────────────┐
│                   应用层                              │
│  @cached, @cache_invalidate 装饰器                    │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│              HierarchicalCache                       │
│  (L1: 本地内存) ←→ (L2: Redis) ←→ (L3: 数据库)       │
│  响应时间: ~1ms       ~50ms        ~500ms             │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│               增强模块层                              │
│  • BloomFilter - 防止缓存穿透                         │
│  • CacheWarmer - 智能预热                            │
│  • DegradationStrategy - 缓存降级                     │
│  • CapacityMonitor - 容量监控                        │
└─────────────────────────────────────────────────────┘
```

### 数据流向

**读取流程**:
```
1. 应用请求 → HierarchicalCache.get(key)
2. L1缓存命中 → 返回数据 (~1ms)
3. L1未命中 → L2缓存命中 → 回写L1 → 返回数据 (~50ms)
4. L2未命中 → L3数据库查询 → 写入L2+L1 → 返回数据 (~500ms)
```

**写入流程**:
```
1. 应用写入 → @cache_invalidate 装饰器
2. 自动清理相关缓存
3. 下次读取时重新加载最新数据
```

---

## 核心模块

### 1. 装饰器模块 (decorators.py)

**位置**: `backend/core/cache/decorators.py`

#### @cached 装饰器

```python
from functools import wraps
from backend.core.cache.cache_hierarchical import HierarchicalCache

cache = HierarchicalCache()

def cached(ttl: int = 3600, key_prefix: str = None):
    """
    缓存装饰器

    Args:
        ttl: 缓存生存时间（秒）
        key_prefix: 缓存键前缀（可选）

    Example:
        @cached(ttl=1800)
        def get_events(game_gid: int):
            return fetch_all_as_dict('SELECT * FROM log_events')
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = _generate_cache_key(func, args, kwargs, key_prefix)

            # 尝试从缓存获取
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return cached_data

            # 缓存未命中，执行函数
            result = func(*args, **kwargs)

            # 写入缓存
            cache.set(cache_key, result, ttl=ttl)

            return result
        return wrapper
    return decorator
```

#### @cache_invalidate 装饰器

```python
def cache_invalidate(func):
    """
    缓存失效装饰器

    在数据修改后自动清理相关缓存

    Example:
        @cache_invalidate
        def update_event(event_id: int, data: dict):
            execute_update('UPDATE log_events SET ...')
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 执行函数（修改数据）
        result = func(*args, **kwargs)

        # 自动清理相关缓存
        _invalidate_related_cache(func, args, kwargs)

        return result
    return wrapper
```

### 2. 层级缓存 (cache_hierarchical.py)

**位置**: `backend/core/cache/cache_hierarchical.py`

```python
class HierarchicalCache:
    """三级分层缓存: L1(内存) + L2(Redis) + L3(数据库)"""

    def __init__(self):
        from backend.core.cache.lru_cache import LRUCache
        self.l1_cache = LRUCache(max_size=1000)
        self.l2_cache = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )

    def get(self, key: str):
        """三级缓存查找"""
        # L1: 本地内存缓存
        data = self.l1_cache.get(key)
        if data:
            return data

        # L2: Redis缓存
        data = self.l2_cache.get(key)
        if data:
            # 回写L1
            self.l1_cache.set(key, data, ttl=600)
            return data

        # L3: 未命中，返回None
        return None

    def set(self, key: str, value: any, ttl: int = 3600, l1_ttl: int = 600):
        """写入L1和L2缓存"""
        self.l1_cache.set(key, value, ttl=l1_ttl)
        self.l2_cache.setex(key, ttl, pickle.dumps(value))

    def delete(self, key: str):
        """删除L1和L2缓存"""
        self.l1_cache.delete(key)
        self.l2_cache.delete(key)
```

---

## 装饰器详解

### 缓存键生成策略

**规则**:
```
格式: {prefix}:{module}:{function}:{args_hash}

示例:
- "cache:events:get_events:game_gid=10000147"
- "cache:games:get_game:game_id=123"
```

**自定义键前缀**:
```python
@cached(ttl=3600, key_prefix="custom:games")
def get_active_games():
    pass
```

### TTL选择指南

| 场景 | 推荐TTL | 理由 |
|------|---------|------|
| 静态配置 | 7200-86400秒 | 几乎不变 |
| 游戏列表 | 3600秒 | 小时级变化 |
| 事件列表 | 1800秒 | 30分钟级变化 |
| 实时统计 | 60秒 | 接近实时 |
| 用户会话 | 600秒 | 安全性考虑 |

**动态TTL**:
```python
import random

@cached(ttl=3600 + random.randint(0, 300))  # 防止缓存雪崩
def get_events(game_gid):
    pass
```

---

## 高级功能

### 1. Bloom Filter 防止缓存穿透

**场景**: 防止查询不存在的数据导致每次都查询数据库

```python
from backend.core.cache.bloom_filter_enhanced import BloomFilterCache

cache = BloomFilterCache()

def get_event_with_bloom_filter(event_id: int):
    """使用Bloom Filter防止穿透"""
    cache_key = f"events:{event_id}"

    # 先检查Bloom Filter
    if not cache.exists_in_bloom(cache_key):
        # Bloom Filter确定不存在，直接返回
        return None

    # Bloom Filter说可能存在，查询缓存/数据库
    event = cache.get(cache_key)
    if event:
        return event

    # 查询数据库
    event = fetch_one_as_dict('SELECT * FROM log_events WHERE id = ?', (event_id,))

    if event:
        # 存在，加入缓存
        cache.add_to_bloom_filter(cache_key)
        cache.set(cache_key, event, ttl=1800)
    else:
        # 不存在，加入Bloom Filter防止重复查询
        cache.add_to_bloom_filter(cache_key)

    return event
```

### 2. 智能预热 (Cache Warmer)

**场景**: 应用启动时预加载常用数据

```python
from backend.core.cache.intelligent_warmer import CacheWarmer

warmer = CacheWarmer()

@warmup_on_startup(priority=1)
def warmup_popular_games():
    """预热热门游戏"""
    games = fetch_all_as_dict('SELECT * FROM games WHERE active = 1 ORDER BY popularity DESC LIMIT 100')
    for game in games:
        cache.set(f"games:{game['gid']}", game, ttl=3600)
    return len(games)

@warmup_on_startup(priority=2)
def warmup_common_params():
    """预热常用参数"""
    params = fetch_all_as_dict('SELECT * FROM event_params WHERE is_common = 1')
    cache.set("params:common", params, ttl=7200)
    return len(params)
```

### 3. 缓存降级策略

**场景**: Redis不可用时自动降级到L1缓存

```python
from backend.core.cache.degradation import DegradationStrategy

cache = DegradationStrategy()

def get_with_fallback(key: str, query_fn, ttl: int = 3600):
    """带降级的缓存查询"""
    # 尝试L2缓存（Redis）
    try:
        data = cache.get_l2(key)
        if data:
            return data
    except RedisConnectionError:
        # Redis不可用，降级到L1
        print("Redis unavailable, falling back to L1 cache")

    # 尝试L1缓存
    data = cache.get_l1(key)
    if data:
        return data

    # 都未命中，查询数据库
    data = query_fn()
    cache.set_l1(key, data, ttl=600)  # 仅缓存L1
    return data
```

### 4. 容量监控和保护

**场景**: 防止缓存占用过多内存

```python
from backend.core.cache.capacity_monitor import CapacityMonitor

monitor = CapacityMonitor()

def set_with_protection(key: str, value: any, ttl: int = 3600):
    """带容量保护的缓存写入"""
    # 检查内存使用
    if monitor.is_memory_critical():
        # 内存不足，拒绝写入
        raise MemoryError("Cache memory critical")

    # 检查对象大小
    if monitor.is_object_too_large(value):
        # 对象过大，拒绝缓存
        raise ValueError(f"Object too large: {len(pickle.dumps(value))} bytes")

    # 正常写入
    cache.set(key, value, ttl)
```

---

## 最佳实践

### ✅ 推荐做法

**1. 使用装饰器统一管理缓存**
```python
@cached(ttl=3600)
def get_events(game_gid):
    return fetch_all_as_dict('SELECT * FROM log_events WHERE game_gid = ?', (game_gid,))

@cache_invalidate
def update_event(event_id, data):
    execute_update('UPDATE log_events SET ...')
```

**2. 合理设置TTL**
```python
# 根据数据更新频率设置TTL
@cached(ttl=3600)  # 静态数据
def get_games():
    pass

@cached(ttl=1800)  # 中等变化频率
def get_events(game_gid):
    pass

@cached(ttl=60)    # 实时数据
def get_online_users():
    pass
```

**3. 使用缓存Tags进行批量清理**
```python
# 设置缓存时添加tag
cache.set("events:10000147", data, ttl=3600, tags=["games:10000147"])
cache.set("params:10000147", data, ttl=3600, tags=["games:10000147"])

# 清理所有相关缓存
cache.delete_many(tags=["games:10000147"])
```

### ❌ 避免的反模式

**1. 缓存大对象**
```python
# ❌ 错误: 缓存整个大表
@cached(ttl=3600)
def get_all_logs():
    return fetch_all_as_dict('SELECT * FROM logs')  # 可能有百万行

# ✅ 正确: 分页缓存
@cached(ttl=600, key_prefix="logs:page")
def get_logs_page(page: int, size: int = 100):
    return fetch_all_as_dict('SELECT * FROM logs LIMIT ? OFFSET ?', (size, page * size))
```

**2. 缓存频繁变化的数据**
```python
# ❌ 错误: 缓存实时统计数据
@cached(ttl=3600)  # TTL太长
def get_realtime_stats():
    return fetch_one_as_dict('SELECT COUNT(*) FROM online_users')

# ✅ 正确: 缩短TTL
@cached(ttl=60)  # 1分钟
def get_realtime_stats():
    return fetch_one_as_dict('SELECT COUNT(*) FROM online_users')
```

**3. 忘记清理缓存**
```python
# ❌ 错误: 更新数据后不清理缓存
def update_event(event_id, data):
    execute_update('UPDATE log_events SET ...')
    # 缓存未清理，导致数据不一致

# ✅ 正确: 使用@cache_invalidate
@cache_invalidate
def update_event(event_id, data):
    execute_update('UPDATE log_events SET ...')
```

---

## 性能优化

### 1. 批量查询优化

```python
def get_games_batch(game_gids: list[int]) -> dict[int, dict]:
    """批量获取游戏，优先使用缓存"""
    result = {}
    missed_gids = []

    # 先从缓存获取
    for gid in game_gids:
        cached = cache.get(f"games:{gid}")
        if cached:
            result[gid] = cached
        else:
            missed_gids.append(gid)

    # 批量查询未命中的游戏
    if missed_gids:
        placeholders = ','.join(['?' for _ in missed_gids])
        games = fetch_all_as_dict(
            f'SELECT * FROM games WHERE gid IN ({placeholders})',
            missed_gids
        )

        for game in games:
            gid = game['gid']
            result[gid] = game
            cache.set(f"games:{gid}", game, ttl=3600)

    return result
```

### 2. 并发读取优化

```python
from concurrent.futures import ThreadPoolExecutor

def get_events_with_params(game_gid: int):
    """并发获取事件和参数"""
    with ThreadPoolExecutor(max_workers=2) as executor:
        # 并发查询
        events_future = executor.submit(get_events, game_gid)
        params_future = executor.submit(get_params, game_gid)

        events = events_future.result()
        params = params_future.result()

    return {"events": events, "params": params}
```

### 3. 缓存预热策略

```python
def warmup_cache_strategy():
    """智能预热策略"""
    # 1. 预热热门数据
    popular_games = get_popular_games(limit=100)
    for game in popular_games:
        cache.set(f"games:{game['gid']}", game, ttl=3600)

    # 2. 预热最近访问的数据
    recent_access = get_recent_access_keys(limit=1000)
    for key in recent_access:
        data = query_from_db(key)
        cache.set(key, data, ttl=1800)

    # 3. 后台定时预热
    schedule.every(1).hours.do(warmup_cache_strategy)
```

---

## 测试指南

### 单元测试

```python
import pytest
from backend.core.cache.decorators import cached

@pytest.fixture(autouse=True)
def clear_cache():
    """每个测试前清理缓存"""
    cache.flush_all()
    yield
    cache.flush_all()

def test_cached_decorator():
    """测试缓存装饰器"""
    call_count = 0

    @cached(ttl=3600)
    def get_data():
        nonlocal call_count
        call_count += 1
        return {"data": "value"}

    # 第一次调用，执行函数
    result1 = get_data()
    assert call_count == 1

    # 第二次调用，从缓存读取
    result2 = get_data()
    assert call_count == 1  # 没有增加
    assert result1 == result2
```

### 集成测试

```python
def test_cache_invalidation():
    """测试缓存失效"""
    @cached(ttl=3600)
    def get_events(game_gid):
        return fetch_all_as_dict('SELECT * FROM log_events WHERE game_gid = ?', (game_gid,))

    @cache_invalidate
    def create_event(game_gid, name):
        execute_insert('INSERT INTO log_events (game_gid, name) VALUES (?, ?)', (game_gid, name))

    # 第一次查询
    events1 = get_events(10000147)
    assert len(events1) == 10

    # 创建新事件
    create_event(10000147, "new_event")

    # 再次查询，应该返回新数据
    events2 = get_events(10000147)
    assert len(events2) == 11
```

### 性能测试

```python
import time

def test_cache_performance():
    """测试缓存性能提升"""
    @cached(ttl=3600)
    def get_data():
        # 模拟慢查询
        time.sleep(0.5)
        return {"data": "value"}

    # 第一次调用（缓存未命中）
    start = time.time()
    get_data()
    duration1 = time.time() - start

    # 第二次调用（缓存命中）
    start = time.time()
    get_data()
    duration2 = time.time() - start

    # 缓存命中应该快100倍以上
    assert duration2 < duration1 / 100
```

---

## 📚 相关文档

- [快速开始指南](../quickstart/5-minute-guide.md)
- [故障排除手册](../operations/troubleshooting.md)
- [部署运维文档](../operations/deployment.md)
- [API快速参考](./api-reference.md)

---

**文档版本**: 1.0
**最后更新**: 2026-02-25
**相关文档**: [快速开始](../quickstart/5-minute-guide.md) | [故障排除](../operations/troubleshooting.md)
