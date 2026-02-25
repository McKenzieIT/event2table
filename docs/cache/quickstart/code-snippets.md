# 缓存系统常用代码片段

> **面向**: 开发者
> **内容**: 可直接复制使用的代码模板

---

## 🟢 基础用法

### 1. 简单缓存

```python
from backend.core.cache.decorators import cached
from backend.core.database.converters import fetch_all_as_dict

@cached(ttl=3600)  # 缓存1小时
def get_all_games():
    """获取所有游戏"""
    return fetch_all_as_dict('SELECT * FROM games')
```

### 2. 参数化缓存

```python
@cached(ttl=1800)
def get_events_by_game(game_gid: int):
    """获取指定游戏的事件列表"""
    return fetch_all_as_dict(
        'SELECT * FROM log_events WHERE game_gid = ?',
        (game_gid,)
    )

@cached(ttl=1800)
def get_event_by_id(event_id: int):
    """获取指定事件详情"""
    return fetch_one_as_dict(
        'SELECT * FROM log_events WHERE id = ?',
        (event_id,)
    )
```

### 3. 缓存失效

```python
from backend.core.cache.decorators import cache_invalidate

@cache_invalidate
def create_event(game_gid: int, event_data: dict):
    """创建新事件，自动清理缓存"""
    query = '''
        INSERT INTO log_events (game_gid, name, description)
        VALUES (?, ?, ?)
    '''
    return execute_insert(query, (game_gid, event_data['name'], event_data['description']))

@cache_invalidate
def update_event(event_id: int, event_data: dict):
    """更新事件，自动清理缓存"""
    query = '''
        UPDATE log_events
        SET name = ?, description = ?
        WHERE id = ?
    '''
    execute_update(query, (event_data['name'], event_data['description'], event_id))

@cache_invalidate
def delete_event(event_id: int):
    """删除事件，自动清理缓存"""
    execute_update('DELETE FROM log_events WHERE id = ?', (event_id,))
```

---

## 🟡 高级用法

### 4. 自定义缓存键

```python
from backend.core.cache.decorators import cached

# 使用key_prefix避免键冲突
@cached(ttl=3600, key_prefix="games:list")
def get_active_games():
    return fetch_all_as_dict('SELECT * FROM games WHERE active = 1')

@cached(ttl=3600, key_prefix="games:stats")
def get_game_stats(game_gid: int):
    return fetch_one_as_dict(
        'SELECT COUNT(*) as event_count FROM log_events WHERE game_gid = ?',
        (game_gid,)
    )
```

### 5. 条件缓存

```python
from backend.core.cache.decorators import cached

@cached(ttl=600)  # 短TTL，接近实时
def get_realtime_stats(game_gid: int):
    """实时统计，缓存1分钟"""
    return fetch_one_as_dict(
        'SELECT COUNT(*) as online_users FROM user_sessions WHERE game_gid = ?',
        (game_gid,)
    )

def get_event_with_cache(event_id: int, use_cache: bool = True):
    """可选是否使用缓存"""
    if use_cache:
        return get_event_by_id(event_id)  # 使用缓存
    else:
        return fetch_one_as_dict('SELECT * FROM log_events WHERE id = ?', (event_id,))  # 不使用缓存
```

### 6. 层级缓存 (L1 + L2)

```python
from backend.core.cache.cache_hierarchical import HierarchicalCache

# 创建层级缓存实例
cache = HierarchicalCache()

def get_game_config(game_gid: int):
    """使用L1+L2层级缓存"""
    cache_key = f"games:config:{game_gid}"

    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    # 缓存未命中，查询数据库
    config = fetch_one_as_dict(
        'SELECT * FROM game_configs WHERE game_gid = ?',
        (game_gid,)
    )

    # 写入缓存（L1: 10分钟, L2: 1小时）
    cache.set(cache_key, config, ttl=3600, l1_ttl=600)

    return config
```

### 7. Bloom Filter防止缓存穿透

```python
from backend.core.cache.bloom_filter_enhanced import BloomFilterCache

# 创建Bloom Filter缓存
cache = BloomFilterCache()

def get_event_with_bloom_filter(event_id: int):
    """使用Bloom Filter防止查询不存在的ID"""
    cache_key = f"events:{event_id}"

    # 先检查Bloom Filter
    if not cache.exists_in_bloom(cache_key):
        # Bloom Filter说不存在，直接返回None
        return None

    # Bloom Filter说可能存在，查询缓存或数据库
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    # 查询数据库
    event = fetch_one_as_dict('SELECT * FROM log_events WHERE id = ?', (event_id,))

    if event:
        # 数据存在，加入Bloom Filter和缓存
        cache.add_to_bloom_filter(cache_key)
        cache.set(cache_key, event, ttl=1800)
    else:
        # 数据不存在，加入Bloom Filter防止重复查询
        cache.add_to_bloom_filter(cache_key)

    return event
```

---

## 🔧 工具函数

### 8. 批量清理缓存

```python
from backend.core.cache.cache_system import cache_result

def clear_game_cache(game_gid: int):
    """清理特定游戏的所有缓存"""
    patterns = [
        f"games:{game_gid}",
        f"events:{game_gid}",
        f"params:{game_gid}",
    ]

    for pattern in patterns:
        cache_result.delete_many(pattern)

    print(f"Cleared all cache for game {game_gid}")
```

### 9. 缓存预热

```python
from backend.core.cache.cache_system import cache_result

def warmup_cache_for_game(game_gid: int):
    """为指定游戏预热缓存"""
    # 预加载游戏基础信息
    game = fetch_one_as_dict('SELECT * FROM games WHERE gid = ?', (game_gid,))
    cache_result.set(f"games:{game_gid}", game, ttl=3600)

    # 预加载事件列表
    events = fetch_all_as_dict('SELECT * FROM log_events WHERE game_gid = ?', (game_gid,))
    cache_result.set(f"events:{game_gid}", events, ttl=1800)

    # 预加载参数配置
    params = fetch_all_as_dict('''
        SELECT ep.* FROM event_params ep
        INNER JOIN log_events le ON ep.event_id = le.id
        WHERE le.game_gid = ?
    ''', (game_gid,))
    cache_result.set(f"params:{game_gid}", params, ttl=3600)

    print(f"Cache warmed up for game {game_gid}")

# 应用启动时预热
def warmup_on_startup():
    """应用启动时预热常用数据"""
    active_games = fetch_all_as_dict('SELECT gid FROM games WHERE active = 1')
    for game in active_games:
        warmup_cache_for_game(game['gid'])
```

### 10. 缓存统计和监控

```python
from backend.core.cache.monitoring import CacheMonitor

def get_cache_stats():
    """获取缓存统计信息"""
    monitor = CacheMonitor()

    return {
        "hits": monitor.get_hits(),
        "misses": monitor.get_misses(),
        "hit_rate": monitor.get_hit_rate(),
        "total_keys": monitor.get_total_keys(),
        "memory_usage": monitor.get_memory_usage(),
        "l1_hits": monitor.get_l1_hits(),
        "l2_hits": monitor.get_l2_hits(),
    }

# 定期输出统计信息
def log_cache_stats():
    """每5分钟输出一次统计"""
    stats = get_cache_stats()
    print(f"[Cache] Hit Rate: {stats['hit_rate']:.2%}, "
          f"Total Keys: {stats['total_keys']}, "
          f"L1 Hits: {stats['l1_hits']}, "
          f"L2 Hits: {stats['l2_hits']}")
```

---

## 🚀 性能优化

### 11. 批量查询缓存

```python
from backend.core.cache.cache_system import cache_result

def get_games_batch(game_gids: list[int]) -> dict[int, dict]:
    """批量获取游戏，优先使用缓存"""
    result = {}
    missed_gids = []

    # 先从缓存获取
    for gid in game_gids:
        cached = cache_result.get(f"games:{gid}")
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
            cache_result.set(f"games:{gid}", game, ttl=3600)

    return result
```

### 12. 缓存更新策略 (Cache-Aside Pattern)

```python
from backend.core.cache.cache_system import cache_result

def update_event_with_cache(event_id: int, event_data: dict):
    """更新事件，使用Cache-Aside模式"""
    # 1. 更新数据库
    execute_update('UPDATE log_events SET name = ? WHERE id = ?',
                   (event_data['name'], event_id))

    # 2. 删除旧缓存（而不是更新）
    cache_result.delete(f"events:{event_id}")

    # 3. 下次读取时会自动加载新数据
    return get_event_by_id(event_id)
```

### 13. 多级缓存降级

```python
from backend.core.cache.degradation import DegradationStrategy

cache = DegradationStrategy()

def get_with_fallback(key: str, query_fn, ttl: int = 3600):
    """带降级的缓存查询"""
    # 尝试L1缓存
    data = cache.get_l1(key)
    if data:
        return data

    # 尝试L2缓存（Redis）
    try:
        data = cache.get_l2(key)
        if data:
            cache.set_l1(key, data, ttl=600)  # 回写L1
            return data
    except Exception as e:
        print(f"Redis error: {e}, falling back to database")

    # 降级到数据库
    data = query_fn()
    cache.set_l1(key, data, ttl=600)  # 仅缓存L1
    return data
```

---

## 🧪 测试相关

### 14. 禁用缓存进行测试

```python
import os

@cached(ttl=3600)
def get_events(game_gid: int):
    return fetch_all_as_dict('SELECT * FROM log_events WHERE game_gid = ?', (game_gid,))

# 测试时临时禁用
def test_get_events():
    # 设置环境变量禁用缓存
    os.environ['CACHE_ENABLED'] = 'false'

    events = get_events(10000147)
    assert events is not None
```

### 15. 清理测试缓存

```python
import pytest

@pytest.fixture(autouse=True)
def clear_cache_before_each_test():
    """每个测试前清理缓存"""
    from backend.core.cache.cache_system import cache_result
    cache_result.flush_all()
    yield
    # 测试后再次清理
    cache_result.flush_all()
```

---

## 📋 实用模板

### 16. CRUD完整模板

```python
from backend.core.cache.decorators import cached, cache_invalidate
from backend.core.database.converters import fetch_all_as_dict, fetch_one_as_dict, execute_insert, execute_update

# READ: 使用缓存
@cached(ttl=1800)
def get_events(game_gid: int):
    return fetch_all_as_dict('SELECT * FROM log_events WHERE game_gid = ?', (game_gid,))

@cached(ttl=1800)
def get_event(event_id: int):
    return fetch_one_as_dict('SELECT * FROM log_events WHERE id = ?', (event_id,))

# CREATE: 自动清理缓存
@cache_invalidate
def create_event(game_gid: int, name: str, description: str):
    return execute_insert(
        'INSERT INTO log_events (game_gid, name, description) VALUES (?, ?, ?)',
        (game_gid, name, description)
    )

# UPDATE: 自动清理缓存
@cache_invalidate
def update_event(event_id: int, name: str, description: str):
    execute_update(
        'UPDATE log_events SET name = ?, description = ? WHERE id = ?',
        (name, description, event_id)
    )

# DELETE: 自动清理缓存
@cache_invalidate
def delete_event(event_id: int):
    execute_update('DELETE FROM log_events WHERE id = ?', (event_id,))
```

---

## 💡 最佳实践

### 17. 缓存键命名规范

```python
# ✅ 好的命名: 层级清晰，语义明确
"games:10000147"                    # 单个游戏
"games:10000147:events"             # 游戏的事件列表
"games:10000147:params:login"       # 游戏的登录参数
"events:12345"                      # 单个事件
"user:67890:permissions"            # 用户权限

# ❌ 差的命名: 语义不清，容易冲突
"game"                              # 不明确
"data"                              # 太泛泛
"temp"                              # 无意义
```

### 18. TTL设置模板

```python
# 永不变化的数据
@cached(ttl=86400)  # 24小时
def get_system_config():
    pass

# 很少变化的数据
@cached(ttl=3600)  # 1小时
def get_games_list():
    pass

# 中等变化频率
@cached(ttl=1800)  # 30分钟
def get_events_list(game_gid):
    pass

# 经常变化的数据
@cached(ttl=300)   # 5分钟
def get_online_users():
    pass

# 接近实时的数据
@cached(ttl=60)    # 1分钟
def get_realtime_stats():
    pass
```

---

**文档版本**: 1.0
**最后更新**: 2026-02-25
**相关文档**: [快速开始](./5-minute-guide.md) | [FAQ](./faq.md) | [开发者指南](../development/developer-guide.md)
