# 缓存系统最佳实践

> **版本**: 1.0 | **最后更新**: 2026-02-27 | **目标读者**: 后端开发者
>
> 本文档提供Event2Table缓存系统的完整最佳实践指南，帮助开发者避免常见错误，提升缓存效率。

---

## 📚 目录

1. [TTL设置策略](#ttl设置策略)
2. [缓存键命名规范](#缓存键命名规范)
3. [读写分离模式](#读写分离模式)
4. [避免缓存大对象](#避免缓存大对象)
5. [缓存失效策略](#缓存失效策略)
6. [错误处理和降级](#错误处理和降级)
7. [性能优化技巧](#性能优化技巧)
8. [反模式警告](#反模式警告)
9. [代码审查清单](#代码审查清单)

---

## TTL设置策略

### 核心原则

**TTL（Time To Live）必须根据数据变化频率设置**，过长导致数据不新鲜，过短导致缓存命中率低。

### TTL选择指南

| 数据类型 | 推荐TTL | 理由 | 示例 |
|---------|---------|------|------|
| **静态配置** | 7200-86400秒 | 几乎不变，可长期缓存 | 系统配置、游戏基础信息 |
| **低频变化** | 3600秒 | 小时级变化 | 游戏列表、事件类别 |
| **中频变化** | 1800秒 | 30分钟级变化 | 事件列表、参数配置 |
| **高频变化** | 300-600秒 | 5-10分钟级变化 | 用户会话、临时数据 |
| **准实时数据** | 60秒 | 接近实时 | 在线用户数、实时统计 |

### ✅ 正确示例

```python
# 1. 静态配置数据 - 长TTL
@cached(ttl=7200)  # 2小时
def get_system_config():
    """系统配置几乎不变"""
    return fetch_one_as_dict('SELECT * FROM system_config')

# 2. 游戏列表 - 中长TTL
@cached(ttl=3600)  # 1小时
def get_active_games():
    """游戏列表变化不频繁"""
    return fetch_all_as_dict('SELECT * FROM games WHERE active = 1')

# 3. 事件列表 - 中等TTL
@cached(ttl=1800)  # 30分钟
def get_events(game_gid: int):
    """事件配置偶尔变化"""
    return fetch_all_as_dict('SELECT * FROM log_events WHERE game_gid = ?', (game_gid,))

# 4. 实时统计 - 短TTL
@cached(ttl=60)  # 1分钟
def get_online_users():
    """在线用户数频繁变化"""
    return fetch_one_as_dict('SELECT COUNT(*) as count FROM user_sessions WHERE last_active > ?', (time.time() - 300,))
```

### ❌ 错误示例

```python
# 错误1: 实时数据使用长TTL
@cached(ttl=3600)  # ❌ 数据可能过期1小时
def get_realtime_stats():
    return fetch_one_as_dict('SELECT COUNT(*) as online_users FROM user_sessions')

# 错误2: 所有数据使用相同TTL
@cached(ttl=3600)  # ❌ 不区分数据类型
def get_system_config():
    pass

@cached(ttl=3600)  # ❌ 相同TTL
def get_realtime_stats():
    pass

# 错误3: TTL为0或不设置
@cached(ttl=0)  # ❌ 缓存立即失效
def get_events():
    pass

@cached()  # ❌ 默认TTL可能不合理
def get_games():
    pass
```

### 动态TTL技巧

**防止缓存雪崩**：为大量缓存设置随机TTL偏移

```python
import random

# ✅ 正确：添加随机偏移（±5分钟）
@cached(ttl=3600 + random.randint(-300, 300))
def get_events(game_gid: int):
    """防止同时失效导致缓存雪崩"""
    pass

# ✅ 正确：基于参数动态TTL
def get_dynamic_ttl(data_type: str) -> int:
    ttl_map = {
        "static": 7200,
        "low_freq": 3600,
        "mid_freq": 1800,
        "high_freq": 600,
        "realtime": 60
    }
    return ttl_map.get(data_type, 1800)

@cached(ttl=lambda: get_dynamic_ttl("mid_freq"))
def get_events(game_gid: int):
    pass
```

---

## 缓存键命名规范

### 核心原则

**缓存键必须遵循统一命名规范**，避免键冲突，便于管理和清理。

### 命名规范

**格式**:
```
{prefix}:{module}:{entity}:{identifier}
```

**示例**:
```
cache:games:get_game:10000147
cache:events:get_events:game_gid=10000147
cache:params:get_params:event_id=123
```

### ✅ 正确示例

```python
# 1. 使用key_prefix避免冲突
@cached(ttl=3600, key_prefix="games:active")
def get_active_games():
    """明确的键前缀"""
    pass

@cached(ttl=1800, key_prefix="events:game")
def get_events(game_gid: int):
    """参数自动添加到键后"""
    pass

# 2. 层级化命名
@cached(ttl=3600, key_prefix="hql:templates")
def get_hql_template(template_name: str):
    """按层级组织"""
    pass

# 3. 包含完整上下文
@cached(ttl=1800, key_prefix="params:event")
def get_event_params(event_id: int):
    """包含事件上下文"""
    pass
```

### ❌ 错误示例

```python
# 错误1: 键前缀太通用
@cached(ttl=3600, key_prefix="data")
def get_games():
    """❌ 容易与其他缓存冲突"""
    pass

@cached(ttl=1800, key_prefix="data")
def get_events():
    """❌ 键冲突"""
    pass

# 错误2: 不使用key_prefix
@cached(ttl=3600)
def get_data():
    """❌ 自动生成的键不直观"""
    pass

# 错误3: 键名过长或过短
@cached(ttl=3600, key_prefix="a")  # ❌ 过短，不清晰
def get_games():
    pass

@cached(ttl=3600, key_prefix="very:long:prefix:that:is:hard:to:read")  # ❌ 过长
def get_games():
    pass
```

### 缓存键最佳实践

**1. 使用业务语义**
```python
# ✅ 正确：业务语义清晰
@cached(ttl=3600, key_prefix="games:gid")
def get_game_by_gid(game_gid: int):
    pass

# ❌ 错误：技术实现细节
@cached(ttl=3600, key_prefix="table:games:query:select")
def get_game_by_gid(game_gid: int):
    pass
```

**2. 避免特殊字符**
```python
# ✅ 正确：使用安全的分隔符
@cached(ttl=3600, key_prefix="games:10000147")
def get_game():
    pass

# ❌ 错误：使用特殊字符
@cached(ttl=3600, key_prefix="games/10000147")
def get_game():
    pass

# ❌ 错误：包含空格
@cached(ttl=3600, key_prefix="games 10000147")
def get_game():
    pass
```

**3. 长度控制**
```python
# ✅ 正确：简洁但清晰
@cached(ttl=3600, key_prefix="events:game")
def get_events_by_game(game_gid: int):
    pass

# ❌ 错误：过于冗长
@cached(ttl=3600, key_prefix="log_events:filtered_by_game_gid_from_database")
def get_events_by_game(game_gid: int):
    pass
```

---

## 读写分离模式

### 核心原则

**读操作使用缓存，写操作清理缓存**，确保数据一致性。

### 基础模式

```python
from backend.core.cache.decorators import cached, cache_invalidate

# ✅ 读：使用缓存
@cached(ttl=1800)
def get_events(game_gid: int):
    return fetch_all_as_dict('SELECT * FROM log_events WHERE game_gid = ?', (game_gid,))

# ✅ 写：清理缓存
@cache_invalidate
def create_event(game_gid: int, event_data: dict):
    return execute_insert('INSERT INTO log_events ...')

# ✅ 更：清理缓存
@cache_invalidate
def update_event(event_id: int, event_data: dict):
    execute_update('UPDATE log_events SET ... WHERE id = ?', (event_id,))

# ✅ 删：清理缓存
@cache_invalidate
def delete_event(event_id: int):
    execute_update('DELETE FROM log_events WHERE id = ?', (event_id,))
```

### 高级模式：关联缓存失效

**场景**：修改游戏信息时，清理所有相关缓存

```python
from backend.core.cache.cache_system import cache_result

@cache_invalidate
def update_game(game_gid: int, game_data: dict):
    """更新游戏并清理所有相关缓存"""
    # 1. 更新数据库
    execute_update('UPDATE games SET ... WHERE gid = ?', (game_gid,))

    # 2. 清理游戏基础信息缓存
    cache_result.delete(f"games:{game_gid}")

    # 3. 清理该游戏的关联缓存
    cache_result.delete_many(pattern=f"events:game:{game_gid}*")
    cache_result.delete_many(pattern=f"params:game:{game_gid}*")
    cache_result.delete_many(pattern=f"hql:game:{game_gid}*")

    return game_gid
```

### ✅ 正确示例

```python
# 1. 完整的CRUD缓存管理
class EventService:
    @cached(ttl=1800, key_prefix="events:list")
    def get_events(self, game_gid: int):
        return fetch_all_as_dict('SELECT * FROM log_events WHERE game_gid = ?', (game_gid,))

    @cached(ttl=1800, key_prefix="events:detail")
    def get_event(self, event_id: int):
        return fetch_one_as_dict('SELECT * FROM log_events WHERE id = ?', (event_id,))

    @cache_invalidate
    def create_event(self, game_gid: int, event_data: dict):
        event_id = execute_insert('INSERT INTO log_events ...')
        # 装饰器自动清理 events:list:*
        return event_id

    @cache_invalidate
    def update_event(self, event_id: int, event_data: dict):
        execute_update('UPDATE log_events SET ... WHERE id = ?', (event_id,))
        # 装饰器自动清理 events:detail:{event_id} 和 events:list:*

    @cache_invalidate
    def delete_event(self, event_id: int):
        execute_update('DELETE FROM log_events WHERE id = ?', (event_id,))
        # 装饰器自动清理相关缓存
```

### ❌ 错误示例

```python
# 错误1: 写操作后不清理缓存
def update_event(event_id: int, event_data: dict):
    execute_update('UPDATE log_events SET name = ? WHERE id = ?', (event_data['name'], event_id))
    # ❌ 缓存未清理，导致数据不一致

# 错误2: 读操作不使用缓存
def get_events(game_gid: int):
    # ❌ 每次都查询数据库，性能差
    return fetch_all_as_dict('SELECT * FROM log_events WHERE game_gid = ?', (game_gid,))

# 错误3: 写操作也使用缓存
@cached(ttl=3600)
def create_event(event_data: dict):
    # ❌ 写操作不应该缓存
    return execute_insert('INSERT INTO log_events ...')

# 错误4: 手动管理缓存（容易遗漏）
def update_event(event_id: int, event_data: dict):
    execute_update('UPDATE log_events SET name = ? WHERE id = ?', (event_data['name'], event_id))
    # ❌ 需要手动清理，容易遗漏
    cache.delete(f"events:{event_id}")
```

### Cache Tags模式（推荐）

**使用标签批量清理相关缓存**:

```python
# 设置缓存时添加标签
cache.set("events:10000147", data, ttl=3600, tags=["games:10000147"])
cache.set("params:10000147", data, ttl=3600, tags=["games:10000147"])
cache.set("hql:10000147", data, ttl=3600, tags=["games:10000147"])

# 批量清理
@cache_invalidate
def update_game(game_gid: int, game_data: dict):
    execute_update('UPDATE games SET ... WHERE gid = ?', (game_gid,))
    # 清理所有带该标签的缓存
    cache.delete_many(tags=["games:{game_gid}"])
```

---

## 避免缓存大对象

### 核心原则

**单个缓存对象必须 < 1MB**，避免内存浪费和性能问题。

### 问题分析

**缓存大对象的后果**:
- 内存占用过高，导致缓存淘汰频繁
- 序列化/反序列化耗时，降低缓存性能
- 网络传输慢，影响Redis性能
- 可能导致OOM（内存溢出）

### ✅ 正确示例

**1. 分页缓存**

```python
# ❌ 错误：缓存整个大表
@cached(ttl=3600)
def get_all_logs():
    return fetch_all_as_dict('SELECT * FROM logs')  # 可能有百万行

# ✅ 正确：分页缓存
@cached(ttl=600, key_prefix="logs:page")
def get_logs_page(page: int, size: int = 100):
    offset = page * size
    return fetch_all_as_dict('SELECT * FROM logs LIMIT ? OFFSET ?', (size, offset))
```

**2. 字段选择缓存**

```python
# ❌ 错误：缓存所有字段
@cached(ttl=3600)
def get_events_full(game_gid: int):
    return fetch_all_as_dict('SELECT * FROM log_events WHERE game_gid = ?', (game_gid,))

# ✅ 正确：只缓存需要的字段
@cached(ttl=1800, key_prefix="events:summary")
def get_events_summary(game_gid: int):
    return fetch_all_as_dict('''
        SELECT id, name, event_type
        FROM log_events
        WHERE game_gid = ?
    ''', (game_gid,))
```

**3. 数据压缩**

```python
import pickle
import zlib

@cached(ttl=3600)
def get_large_data():
    """压缩大数据"""
    data = fetch_large_data()

    # 压缩数据
    compressed = zlib.compress(pickle.dumps(data))

    # 检查大小
    if len(compressed) > 1024 * 1024:  # > 1MB
        raise ValueError("Data too large to cache")

    return compressed
```

**4. 拆分缓存**

```python
# ❌ 错误：缓存整个游戏配置
@cached(ttl=3600)
def get_game_full_config(game_gid: int):
    return {
        "basic": get_basic_info(game_gid),
        "events": get_all_events(game_gid),
        "params": get_all_params(game_gid),
        "hql_templates": get_all_templates(game_gid)
    }

# ✅ 正确：拆分为多个缓存
@cached(ttl=7200, key_prefix="games:basic")
def get_game_basic(game_gid: int):
    return get_basic_info(game_gid)

@cached(ttl=1800, key_prefix="games:events")
def get_game_events(game_gid: int):
    return get_all_events(game_gid)

@cached(ttl=1800, key_prefix="games:params")
def get_game_params(game_gid: int):
    return get_all_params(game_gid)
```

### 缓存大小验证

**在开发阶段验证缓存大小**:

```python
import pickle

def validate_cache_size(func):
    """装饰器：验证缓存对象大小"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        # 序列化检查大小
        serialized = pickle.dumps(result)
        size_mb = len(serialized) / (1024 * 1024)

        if size_mb > 1:
            logger.warning(f"Cache object too large: {size_mb:.2f}MB")

        return result
    return wrapper

@cached(ttl=3600)
@validate_cache_size
def get_events(game_gid: int):
    return fetch_all_as_dict('SELECT * FROM log_events WHERE game_gid = ?', (game_gid,))
```

---

## 缓存失效策略

### 核心原则

**数据修改时必须清理缓存**，确保数据一致性。

### 失效策略分类

**1. 精确失效**
```python
@cache_invalidate
def update_event(event_id: int, event_data: dict):
    """精确清理单个事件缓存"""
    execute_update('UPDATE log_events SET ... WHERE id = ?', (event_id,))
    # 自动清理: events:detail:{event_id}
```

**2. 模式失效**
```python
@cache_invalidate
def update_game(game_gid: int, game_data: dict):
    """清理所有相关缓存"""
    execute_update('UPDATE games SET ... WHERE gid = ?', (game_gid,))
    # 自动清理: games:{game_gid}*
    cache.delete_many(pattern=f"events:game:{game_gid}*")
    cache.delete_many(pattern=f"params:game:{game_gid}*")
```

**3. 关联失效**
```python
@cache_invalidate
def update_event_category(category_id: int, category_data: dict):
    """更新类别时清理所有事件缓存"""
    execute_update('UPDATE event_categories SET ... WHERE id = ?', (category_id,))
    # 清理该类别下所有事件的缓存
    cache.delete_many(pattern="events:list:*")
```

**4. 版本失效**
```python
def get_events_with_version(game_gid: int, version: str = None):
    """使用版本号控制缓存"""
    if not version:
        version = get_current_version(game_gid)

    cache_key = f"events:{game_gid}:v{version}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data

    data = fetch_all_as_dict('SELECT * FROM log_events WHERE game_gid = ?', (game_gid,))
    cache.set(cache_key, data, ttl=1800)
    return data

def invalidate_events_cache(game_gid: int):
    """更新版本号使旧缓存失效"""
    new_version = int(time.time())
    cache.set(f"events:version:{game_gid}", new_version, ttl=86400)
```

### ✅ 正确示例

**完整CRUD的缓存管理**:

```python
class EventRepository:
    @cached(ttl=1800, key_prefix="events:detail")
    def get_event(self, event_id: int):
        return fetch_one_as_dict('SELECT * FROM log_events WHERE id = ?', (event_id,))

    @cached(ttl=1800, key_prefix="events:list")
    def get_events_by_game(self, game_gid: int):
        return fetch_all_as_dict('SELECT * FROM log_events WHERE game_gid = ?', (game_gid,))

    @cache_invalidate
    def create_event(self, game_gid: int, event_data: dict):
        event_id = execute_insert('INSERT INTO log_events ...')
        # 自动清理 events:list:{game_gid}
        return event_id

    @cache_invalidate
    def update_event(self, event_id: int, event_data: dict):
        execute_update('UPDATE log_events SET ... WHERE id = ?', (event_id,))
        # 自动清理 events:detail:{event_id} 和 events列表

    @cache_invalidate
    def delete_event(self, event_id: int):
        execute_update('DELETE FROM log_events WHERE id = ?', (event_id,))
        # 自动清理所有相关缓存
```

### ❌ 错误示例

```python
# 错误1: 删除缓存不准确
def update_event(event_id: int, event_data: dict):
    execute_update('UPDATE log_events SET ... WHERE id = ?', (event_id,))
    cache.delete("events:*")  # ❌ 清理范围过大，误删其他缓存

# 错误2: 忘记清理缓存
def update_event(event_id: int, event_data: dict):
    execute_update('UPDATE log_events SET ... WHERE id = ?', (event_id,))
    # ❌ 完全忘记清理缓存

# 错误3: 缓存清理在事务之前
def update_event(event_id: int, event_data: dict):
    cache.delete(f"events:{event_id}")  # ❌ 清理过早
    execute_update('UPDATE log_events SET ... WHERE id = ?', (event_id,))
    # 如果更新失败，缓存已被删除，导致不一致

# 正确：先更新数据库，再清理缓存
def update_event(event_id: int, event_data: dict):
    execute_update('UPDATE log_events SET ... WHERE id = ?', (event_id,))
    cache.delete(f"events:{event_id}")  # ✅ 更新成功后再清理
```

---

## 错误处理和降级

### 核心原则

**缓存不可用时不影响业务**，实现优雅降级。

### 降级策略

**1. L1缓存降级**

```python
from backend.core.cache.degradation import DegradationStrategy

cache = DegradationStrategy()

def get_with_fallback(key: str, query_fn, ttl: int = 3600):
    """带降级的缓存查询"""
    try:
        # 尝试L2缓存（Redis）
        data = cache.get_l2(key)
        if data:
            return data
    except RedisConnectionError:
        logger.warning("Redis unavailable, falling back to L1 cache")

    # 尝试L1缓存
    data = cache.get_l1(key)
    if data:
        return data

    # 都未命中，查询数据库
    data = query_fn()
    cache.set_l1(key, data, ttl=600)  # 仅缓存L1
    return data
```

**2. 数据库降级**

```python
def get_events_safe(game_gid: int):
    """安全的缓存查询，完全降级"""
    try:
        # 尝试缓存
        return get_events_cached(game_gid)
    except Exception as e:
        logger.error(f"Cache error: {e}")

        try:
            # 降级到数据库
            return fetch_all_as_dict('SELECT * FROM log_events WHERE game_gid = ?', (game_gid,))
        except Exception as db_error:
            logger.error(f"Database error: {db_error}")
            return []  # 最终降级：返回空列表
```

**3. 超时控制**

```python
import signal
from contextlib import contextmanager

@contextmanager
def timeout(seconds):
    """超时上下文管理器"""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")

    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)

def get_events_with_timeout(game_gid: int, timeout_sec: int = 5):
    """带超时的缓存查询"""
    try:
        with timeout(timeout_sec):
            return get_events_cached(game_gid)
    except TimeoutError:
        logger.warning(f"Cache query timeout, falling back to DB")
        return fetch_all_as_dict('SELECT * FROM log_events WHERE game_gid = ?', (game_gid,))
```

### 错误监控

**缓存失败告警**:

```python
from backend.core.cache.monitoring import CacheMonitor

monitor = CacheMonitor()

def get_events_monitored(game_gid: int):
    """带监控的缓存查询"""
    try:
        return get_events_cached(game_gid)
    except Exception as e:
        # 记录失败
        monitor.record_failure("get_events", str(e))

        # 发送告警（失败率超过阈值）
        if monitor.get_failure_rate("get_events") > 0.1:
            send_alert(f"Cache failure rate too high: {monitor.get_failure_rate('get_events')}")

        # 降级到数据库
        return fetch_all_as_dict('SELECT * FROM log_events WHERE game_gid = ?', (game_gid,))
```

---

## 性能优化技巧

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

### 3. 缓存预热

```python
def warmup_cache_on_startup():
    """应用启动时预热缓存"""
    logger.info("Starting cache warmup...")

    # 1. 预热热门游戏
    popular_games = fetch_all_as_dict('SELECT * FROM games WHERE active = 1 ORDER BY popularity DESC LIMIT 100')
    for game in popular_games:
        cache.set(f"games:{game['gid']}", game, ttl=3600)

    # 2. 预热常用参数
    common_params = fetch_all_as_dict('SELECT * FROM event_params WHERE is_common = 1')
    cache.set("params:common", common_params, ttl=7200)

    # 3. 预热事件列表
    for game in popular_games:
        events = fetch_all_as_dict('SELECT * FROM log_events WHERE game_gid = ?', (game['gid'],))
        cache.set(f"events:list:{game['gid']}", events, ttl=1800)

    logger.info(f"Cache warmup completed: {len(popular_games)} games, {len(common_params)} params")
```

### 4. 懒加载优化

```python
def get_events_lazy(game_gid: int):
    """懒加载：只缓存访问过的数据"""
    cache_key = f"events:list:{game_gid}"

    # 检查缓存
    cached = cache.get(cache_key)
    if cached:
        return cached

    # 未命中，查询数据库
    events = fetch_all_as_dict('SELECT * FROM log_events WHERE game_gid = ?', (game_gid,))

    # 只缓存有访问量的数据
    if len(events) > 0:
        cache.set(cache_key, events, ttl=1800)

    return events
```

### 5. 缓存更新策略

**Cache-Aside模式（推荐）**:
```python
def update_event_optimized(event_id: int, event_data: dict):
    """优化的更新策略"""
    # 1. 更新数据库
    execute_update('UPDATE log_events SET ... WHERE id = ?', (event_id,))

    # 2. 删除缓存（而不是更新）
    cache.delete(f"events:detail:{event_id}")

    # 3. 下次读取时自动加载新数据
```

**Write-Through模式**:
```python
def update_event_write_through(event_id: int, event_data: dict):
    """写穿透：同时更新数据库和缓存"""
    # 1. 更新数据库
    execute_update('UPDATE log_events SET ... WHERE id = ?', (event_id,))

    # 2. 立即更新缓存
    event = fetch_one_as_dict('SELECT * FROM log_events WHERE id = ?', (event_id,))
    cache.set(f"events:detail:{event_id}", event, ttl=1800)
```

---

## 反模式警告

### 反模式1: 缓存和数据库不一致

**问题**：更新数据库后忘记清理缓存

```python
# ❌ 错误
def update_event(event_id: int, event_data: dict):
    execute_update('UPDATE log_events SET name = ? WHERE id = ?', (event_data['name'], event_id))
    # 忘记清理缓存

# ✅ 正确
@cache_invalidate
def update_event(event_id: int, event_data: dict):
    execute_update('UPDATE log_events SET name = ? WHERE id = ?', (event_data['name'], event_id))
    # 装饰器自动清理缓存
```

**后果**：用户看到过期数据，导致业务错误

---

### 反模式2: 缓存穿透

**问题**：查询不存在的数据导致每次都查询数据库

```python
# ❌ 错误：没有缓存空值
def get_event(event_id: int):
    event = cache.get(f"events:{event_id}")
    if not event:
        event = fetch_one_as_dict('SELECT * FROM log_events WHERE id = ?', (event_id,))
        if event:
            cache.set(f"events:{event_id}", event, ttl=1800)
    return event

# ✅ 正确：缓存空值
def get_event(event_id: int):
    event = cache.get(f"events:{event_id}")
    if not event:
        event = fetch_one_as_dict('SELECT * FROM log_events WHERE id = ?', (event_id,))
        # 缓存空值，防止穿透
        cache.set(f"events:{event_id}", event, ttl=60)
    return event
```

**后果**：恶意请求不存在的数据导致数据库压力过大

---

### 反模式3: 缓存雪崩

**问题**：大量缓存同时失效导致数据库压力激增

```python
# ❌ 错误：所有缓存相同TTL
@cached(ttl=3600)
def get_events(game_gid: int):
    pass

# ✅ 正确：添加随机偏移
import random

@cached(ttl=3600 + random.randint(-300, 300))
def get_events(game_gid: int):
    pass
```

**后果**：缓存同时失效，数据库瞬间承受巨大压力

---

### 反模式4: 缓存击穿

**问题**：热点数据过期时大量请求同时查询数据库

```python
# ❌ 错误：无保护
def get_hot_event(event_id: int):
    event = cache.get(f"events:{event_id}")
    if not event:
        # 大量请求同时到达，都查询数据库
        event = fetch_one_as_dict('SELECT * FROM log_events WHERE id = ?', (event_id,))
        cache.set(f"events:{event_id}", event, ttl=1800)
    return event

# ✅ 正确：使用互斥锁
import threading

lock = threading.Lock()

def get_hot_event(event_id: int):
    event = cache.get(f"events:{event_id}")
    if not event:
        with lock:
            # 双重检查
            event = cache.get(f"events:{event_id}")
            if not event:
                event = fetch_one_as_dict('SELECT * FROM log_events WHERE id = ?', (event_id,))
                cache.set(f"events:{event_id}", event, ttl=1800)
    return event
```

**后果**：热点数据过期时数据库压力激增

---

### 反模式5: 缓存大对象

**问题**：缓存整个大表导致内存占用过高

```python
# ❌ 错误
@cached(ttl=3600)
def get_all_logs():
    return fetch_all_as_dict('SELECT * FROM logs')  # 百万行数据

# ✅ 正确
@cached(ttl=600, key_prefix="logs:page")
def get_logs_page(page: int, size: int = 100):
    return fetch_all_as_dict('SELECT * FROM logs LIMIT ? OFFSET ?', (size, page * size))
```

**后果**：内存占用过高，缓存淘汰频繁

---

### 反模式6: 过度缓存

**问题**：缓存了不应该缓存的数据

```python
# ❌ 错误：缓存一次性数据
@cached(ttl=3600)
def generate_report():
    """生成报告，每次都不同"""
    return expensive_report_generation()

# ✅ 正确：不缓存
def generate_report():
    """生成报告，每次都不同"""
    return expensive_report_generation()

# ❌ 错误：缓存随机数据
@cached(ttl=3600)
def get_random_quote():
    """随机名言，每次应该不同"""
    return fetch_random_quote()

# ✅ 正确：不缓存
def get_random_quote():
    """随机名言，每次应该不同"""
    return fetch_random_quote()
```

**后果**：业务逻辑错误，数据不正确

---

## 代码审查清单

### 强制检查项

每个使用缓存的功能必须完成以下检查：

- [ ] **是否使用了 `@cached` 装饰器？**
  - 所有查询函数必须使用缓存装饰器
  - 参数化查询自动生成不同的缓存键

- [ ] **TTL是否合理？**
  - 静态数据：3600-7200秒
  - 中等变化：1800秒
  - 实时数据：60秒
  - 是否添加了随机偏移防止雪崩？

- [ ] **数据更新时是否调用了 `@cache_invalidate`？**
  - CREATE操作必须清理缓存
  - UPDATE操作必须清理缓存
  - DELETE操作必须清理缓存

- [ ] **缓存键是否遵循命名规范？**
  - 格式：`{prefix}:{module}:{function}:{args}`
  - 使用 `key_prefix` 避免键冲突
  - 键名是否有业务语义？

- [ ] **是否避免了缓存大对象？**
  - 单个缓存对象 < 1MB
  - 是否使用了分页？
  - 是否只缓存需要的字段？

- [ ] **是否添加了缓存验证？**
  - 开发环境检查 `X-Cache-Status` 响应头
  - 生产环境监控缓存命中率
  - 是否有缓存失败告警？

- [ ] **是否实现了降级策略？**
  - Redis不可用时的降级方案
  - 缓存超时的处理
  - 数据库不可用时的最终降级

- [ ] **是否有防缓存击穿/穿透/雪崩的措施？**
  - 热点数据使用互斥锁
  - 缓存空值防止穿透
  - TTL随机偏移防止雪崩

### 性能检查项

- [ ] **缓存命中率是否达标？**
  - 目标：> 80%
  - 监控方式：`/api/cache/stats`

- [ ] **响应时间是否改善？**
  - 缓存命中：~5ms (L1) / ~50ms (L2)
  - 缓存未命中：~500ms
  - 性能提升：100-1000倍

- [ ] **数据库负载是否降低？**
  - 目标：降低80%
  - 监控数据库QPS

### 安全检查项

- [ ] **缓存数据是否脱敏？**
  - 不缓存敏感信息（密码、Token）
  - 不缓存用户隐私数据

- [ ] **缓存键是否安全？**
  - 不包含敏感信息
  - 使用哈希处理用户ID

---

## 验证和测试

### 开发环境验证

```bash
# 1. 检查缓存是否生效
curl -i http://127.0.0.1:5001/api/events?game_gid=10000147
# 响应头应包含: X-Cache-Status: HIT 或 MISS

# 2. 查看缓存统计
curl http://127.0.0.1:5001/api/cache/stats

# 3. 直接查看Redis
redis-cli GET "cache:events:10000147"

# 4. 清理所有缓存
redis-cli FLUSHALL
```

### 单元测试

```python
def test_cache_hit():
    """测试缓存命中"""
    # 第一次调用
    events1 = get_events(10000147)

    # 第二次调用（应该命中缓存）
    events2 = get_events(10000147)

    assert events1 == events2

def test_cache_invalidation():
    """测试缓存失效"""
    # 获取事件
    events1 = get_events(10000147)
    assert len(events1) == 10

    # 创建新事件
    create_event(10000147, {"name": "new_event"})

    # 再次获取，应该返回新数据
    events2 = get_events(10000147)
    assert len(events2) == 11
```

---

## 📚 相关文档

- [缓存系统文档中心](../README.md)
- [5分钟快速开始](../quickstart/5-minute-guide.md)
- [开发者指南](./developer-guide.md)
- [故障排除手册](../operations/troubleshooting.md)
- [部署运维文档](../operations/deployment.md)

---

**文档版本**: 1.0
**最后更新**: 2026-02-27
**维护者**: Event2Table Development Team
