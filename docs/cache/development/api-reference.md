# 缓存系统 API 参考文档

> **版本**: 3.2.0 | **最后更新**: 2026-02-27
>
> 本文档提供Event2Table缓存系统的完整API参考。

---

## 目录

1. [装饰器API](#装饰器api)
2. [HierarchicalCache类API](#hierarchicalcache类api)
3. [CacheInvalidator类API](#cacheinvalidator类api)
4. [EnhancedBloomFilter类API](#enhancedbloomfilter类api)
5. [IntelligentCacheWarmer类API](#intelligentcachewarmer类api)
6. [辅助函数API](#辅助函数api)
7. [常量和配置](#常量和配置)

---

## 装饰器API

### `@cached` - 简单缓存装饰器

缓存函数返回值到Redis。

**函数签名**:
```python
def cached(pattern: str, timeout: Optional[int] = None)
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `pattern` | str | 是 | - | 缓存模式（如 'events.list'） |
| `timeout` | Optional[int] | 否 | None | 超时时间（秒），None则使用默认TTL |

**返回值**:
- 装饰器函数

**使用示例**:

```python
from backend.core.cache import cached

@cached('events.list', timeout=300)
def get_events(game_id: int, page: int):
    """获取事件列表（缓存5分钟）"""
    return fetch_events_from_db(game_id, page)

# 调用函数时会自动缓存结果
events = get_events(game_id=1, page=1)
```

**注意事项**:
- 使用Flask-Cache作为底层存储
- 适用于简单的缓存场景
- 不支持L1内存缓存
- 缓存键由`CacheKeyBuilder.build()`生成

---

### `@cached_hierarchical` - 分层缓存装饰器

使用三级分层缓存（L1内存 + L2 Redis）。

**函数签名**:
```python
def cached_hierarchical(
    pattern: str,
    ttl_l1: int = 60,
    ttl_l2: int = 300,
    key_params: Optional[list] = None
)
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `pattern` | str | 是 | - | 缓存模式（如 'games.detail'） |
| `ttl_l1` | int | 否 | 60 | L1缓存TTL（秒） |
| `ttl_l2` | int | 否 | 300 | L2缓存TTL（秒） |
| `key_params` | Optional[list] | 否 | None | 用于构建缓存键的参数名列表 |

**返回值**:
- 装饰器函数

**使用示例**:

```python
from backend.core.cache import cached_hierarchical

# 示例1: 基础用法
@cached_hierarchical('games.detail', ttl_l1=60, ttl_l2=300)
def get_game(game_id: int):
    """获取游戏详情（L1:60秒, L2:5分钟）"""
    return fetch_game_from_db(game_id)

# 示例2: 指定键参数
@cached_hierarchical(
    'events.list',
    ttl_l1=120,
    ttl_l2=600,
    key_params=['game_gid', 'category']
)
def get_events_by_category(game_gid: int, category: str):
    """获取分类事件（包含category参数）"""
    return fetch_events(game_gid, category)
```

**注意事项**:
- **推荐使用**：相比`@cached`，性能提升10-100倍
- L1缓存命中：<1ms响应时间
- L2缓存命中：5-10ms响应时间，自动回填L1
- 支持空值缓存（防止缓存穿透）
- TTL自动抖动（±10%，防止缓存雪崩）

---

### `@cached_service` - Service层缓存装饰器

专为Service层设计的缓存装饰器（位于`decorators.py`）。

**函数签名**:
```python
def cached_service(
    key_template: str,
    ttl_l1: int = 60,
    ttl_l2: int = 300,
    key_params: Optional[list] = None
)
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `key_template` | str | 是 | - | 缓存键模板（如 'game:{gid}'） |
| `ttl_l1` | int | 否 | 60 | L1缓存TTL（秒） |
| `ttl_l2` | int | 否 | 300 | L2缓存TTL（秒） |
| `key_params` | Optional[list] | 否 | None | 用于构建缓存键的参数名列表 |

**返回值**:
- 装饰器函数

**使用示例**:

```python
from backend.core.cache.decorators import cached_service

class GameService:
    @cached_service("game:{gid}", ttl_l1=60, ttl_l2=300, key_params=['gid'])
    def get_game(self, gid: int):
        """获取游戏（Service层）"""
        return self.game_repo.find_by_gid(gid)
```

**注意事项**:
- 支持参数化键模板（如 'game:{gid}'）
- 自动提取函数参数构建缓存键
- 适用于Service层方法

---

### `@invalidate_cache` - 缓存失效装饰器

自动失效缓存。

**函数签名**:
```python
def invalidate_cache(key_pattern: str, key_params: Optional[list] = None)
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `key_pattern` | str | 是 | - | 缓存键模式，支持通配符 |
| `key_params` | Optional[list] | 否 | None | 用于构建缓存键的参数名列表 |

**返回值**:
- 装饰器函数

**使用示例**:

```python
from backend.core.cache.decorators import invalidate_cache

# 示例1: 精确失效
@invalidate_cache("game:{gid}", key_params=['gid'])
def update_game(self, gid: int, data: dict):
    """更新游戏（失效缓存）"""
    return self.game_repo.update(gid, data)

# 示例2: 模式失效
@invalidate_cache("events:{game_gid}:*", key_params=['game_gid'])
def update_event(self, game_gid: int, event_id: int, data: dict):
    """更新事件（失效所有游戏相关缓存）"""
    return self.event_repo.update(event_id, data)

# 示例3: 固定键失效
@invalidate_cache("games:list")
def create_game(self, data: dict):
    """创建游戏（失效列表缓存）"""
    return self.game_repo.create(data)
```

**注意事项**:
- 在函数执行后失效缓存
- 支持通配符模式（`*`）
- 适用于CREATE/UPDATE/DELETE操作

---

## HierarchicalCache类API

三级分层缓存管理器（L1内存 + L2 Redis + L3数据库）。

### 类初始化

**函数签名**:
```python
def __init__(
    self,
    l1_size: int = 1000,
    l1_ttl: int = 60,
    l2_ttl: int = 3600
)
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `l1_size` | int | 否 | 1000 | L1缓存大小（条数） |
| `l1_ttl` | int | 否 | 60 | L1缓存TTL（秒） |
| `l2_ttl` | int | 否 | 3600 | L2缓存TTL（秒） |

**使用示例**:

```python
from backend.core.cache import HierarchicalCache

# 创建自定义配置的缓存实例
cache = HierarchicalCache(
    l1_size=2000,  # L1缓存2000条
    l1_ttl=120,    # L1缓存2分钟
    l2_ttl=7200    # L2缓存2小时
)
```

---

### `get()` - 查询缓存

三级缓存查询（L1 → L2 → L3数据库）。

**函数签名**:
```python
def get(self, pattern: str, **kwargs) -> Optional[Any]
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `pattern` | str | 是 | - | 缓存模式（如 'games.detail'） |
| `**kwargs` | dict | 是 | - | 参数键值对（如 game_id=1） |

**返回值**:
- `Optional[Any]`: 缓存数据或None（未命中）

**使用示例**:

```python
cache = HierarchicalCache()

# 示例1: 简单查询
game = cache.get('games.detail', id=1)
if game is None:
    # 缓存未命中，查询数据库
    game = fetch_game_from_db(1)
    cache.set('games.detail', game, id=1)

# 示例2: 带多个参数
events = cache.get('events.list', game_id=1, page=1)

# 示例3: 检查是否命中
if cache.get('games.detail', id=1) is not None:
    print("缓存命中")
```

**查询流程**:
1. **L1内存缓存** (<1ms): 命中直接返回
2. **L2 Redis缓存** (5-10ms): 命中后回填L1
3. **L3数据库** (50-200ms): 返回None，由调用方查询

**注意事项**:
- 支持空值缓存（防止缓存穿透）
- L2命中自动回填L1
- 自动记录统计信息（命中率）

---

### `set()` - 写入缓存

同时写入L1和L2缓存。

**函数签名**:
```python
def set(
    self,
    pattern: str,
    data: Any,
    ttl: Optional[int] = None,
    **kwargs
)
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `pattern` | str | 是 | - | 缓存模式 |
| `data` | Any | 是 | - | 要缓存的数据 |
| `ttl` | Optional[int] | 否 | None | TTL时间（秒），None则使用默认l2_ttl |
| `**kwargs` | dict | 是 | - | 参数键值对 |

**返回值**:
- `None`

**使用示例**:

```python
cache = HierarchicalCache()

# 示例1: 基础用法
cache.set('games.detail', game_data, id=1)

# 示例2: 自定义TTL
cache.set('events.list', events_data, ttl=600, game_id=1)

# 示例3: 空值缓存
cache.set('games.detail', None, id=999)  # 自动转换为空值标记
```

**注意事项**:
- 自动应用TTL抖动（±10%，防止缓存雪崩）
- 自动处理空值缓存（使用`__EMPTY__`标记）
- L1缓存满时自动LRU淘汰
- 同时写入L1和L2，确保一致性

---

### `delete()` - 删除缓存

删除L1和L2缓存。

**函数签名**:
```python
def delete(self, pattern: str, **kwargs)
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `pattern` | str | 是 | - | 缓存模式 |
| `**kwargs` | dict | 是 | - | 参数键值对 |

**返回值**:
- `None`

**使用示例**:

```python
cache = HierarchicalCache()

# 删除特定缓存
cache.delete('games.detail', id=1)
```

---

### `invalidate()` - 精确失效

失效单个缓存键（L1和L2同时失效）。

**函数签名**:
```python
def invalidate(self, pattern: str, **kwargs) -> int
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `pattern` | str | 是 | - | 缓存模式 |
| `**kwargs` | dict | 是 | - | 参数键值对 |

**返回值**:
- `int`: 失效的缓存键数量（0-2）

**使用示例**:

```python
cache = HierarchicalCache()

# 示例1: 失效特定游戏详情缓存
count = cache.invalidate('games.detail', id=1)
print(f"已失效{count}个缓存键")

# 示例2: 失效事件列表缓存
count = cache.invalidate('events.list', game_id=1, page=1)
```

**失效流程**:
1. **构建完整缓存键**: `CacheKeyBuilder.build(pattern, **kwargs)`
2. **L1失效**: 从L1内存缓存删除键
3. **L2失效**: 从Redis缓存删除键（如果Redis可用）
4. **返回计数**: 返回实际失效的键数量

**注意事项**:
- 与`delete()`不同，此方法返回失效计数
- 适用于需要验证失效是否成功的场景
- 自动处理Redis不可用的情况（仅失效L1）

---

### `set_raw()` - 直接设置缓存

直接设置缓存值，不经过序列化（用于预热系统）。

**函数签名**:
```python
def set_raw(
    self,
    key: str,
    value: Any,
    ttl: Optional[int] = None,
    level: str = "both"
)
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `key` | str | 是 | - | 完整缓存键（不含前缀） |
| `value` | Any | 是 | - | 要设置的缓存值 |
| `ttl` | Optional[int] | 否 | None | TTL时间（秒），None则使用默认l2_ttl |
| `level` | str | 否 | "both" | 缓存级别："l1"、"l2"、"both" |

**返回值**:
- `None`

**使用示例**:

```python
cache = HierarchicalCache()

# 示例1: 预热游戏详情到L1和L2
cache.set_raw(
    'games.detail:id:1',
    game_data,
    ttl=300,
    level='both'
)

# 示例2: 仅预热到L1（极热数据）
cache.set_raw(
    'games.detail:id:1',
    game_data,
    ttl=60,
    level='l1'
)

# 示例3: 仅预热到L2（大数据）
cache.set_raw(
    'events.list:game_id:1',
    events_data,
    ttl=600,
    level='l2'
)
```

**使用场景**:
- **缓存预热**: 系统启动时预加载热点数据
- **批量导入**: 从数据库批量导入缓存
- **数据同步**: 从其他系统同步数据到缓存

**注意事项**:
- 不经过序列化，直接存储原始值
- 不添加缓存键前缀（`dwd_gen:v3:`），需要手动提供完整键
- 不处理空值缓存（不会将None转换为`__EMPTY__`）
- 适用于已知缓存键和数据的场景
- 一般使用`set()`方法，此方法主要用于性能优化

---

### `invalidate_pattern()` - 模式失效

失效匹配模式的所有L1缓存键。

**函数签名**:
```python
def invalidate_pattern(self, pattern: str, **kwargs) -> int
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `pattern` | str | 是 | - | 缓存模式 |
| `**kwargs` | dict | 是 | - | 要匹配的参数 |

**返回值**:
- `int`: 失效的键数量

**使用示例**:

```python
cache = HierarchicalCache()

# 示例1: 失效所有游戏相关缓存
count = cache.invalidate_pattern('games.*')

# 示例2: 失效特定游戏的缓存
count = cache.invalidate_pattern('events.*', game_id=1)

print(f"已失效{count}个缓存键")
```

**注意事项**:
- 仅失效L1缓存
- 使用参数感知的通配符匹配
- L2缓存需要手动删除（使用Redis命令）

---

### `get_stats()` - 获取统计信息

获取缓存统计信息。

**函数签名**:
```python
def get_stats(self) -> dict
```

**返回值**:
- `dict`: 统计信息字典

**统计字段**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `l1_size` | int | L1缓存当前条数 |
| `l1_capacity` | int | L1缓存容量 |
| `l1_usage` | str | L1缓存使用率（百分比） |
| `l1_hits` | int | L1缓存命中次数 |
| `l2_hits` | int | L2缓存命中次数 |
| `misses` | int | 缓存未命中次数 |
| `hit_rate` | str | 总命中率（百分比） |
| `l1_evictions` | int | L1缓存淘汰次数 |
| `l1_sets` | int | L1缓存写入次数 |
| `l2_sets` | int | L2缓存写入次数 |
| `total_requests` | int | 总请求次数 |
| `empty_hits` | int | 空值缓存命中次数 |

**使用示例**:

```python
cache = HierarchicalCache()

# 获取统计信息
stats = cache.get_stats()

print(f"L1命中率: {stats['l1_hits'] / stats['total_requests'] * 100:.2f}%")
print(f"总命中率: {stats['hit_rate']}")
print(f"L1缓存使用: {stats['l1_usage']}")
```

---

### `clear_l1()` - 清空L1缓存

清空L1内存缓存。

**函数签名**:
```python
def clear_l1(self)
```

**使用示例**:

```python
cache = HierarchicalCache()
cache.clear_l1()  # 清空L1缓存
```

---

### `clear_l2()` - 清空L2缓存

清空L2 Redis缓存（所有`dwd_gen:v3:`开头的键）。

**函数签名**:
```python
def clear_l2(self)
```

**使用示例**:

```python
cache = HierarchicalCache()
cache.clear_l2()  # 清空L2缓存
```

**注意事项**:
- 只删除`dwd_gen:v3:`前缀的键
- 其他Redis键不受影响

---

### `clear_all()` - 清空所有缓存

清空L1和L2缓存。

**函数签名**:
```python
def clear_all(self)
```

**使用示例**:

```python
cache = HierarchicalCache()
cache.clear_all()  # 清空L1和L2
```

---

### `reset_stats()` - 重置统计信息

重置缓存统计信息。

**函数签名**:
```python
def reset_stats(self)
```

**使用示例**:

```python
cache = HierarchicalCache()
cache.reset_stats()  # 重置统计
```

---

## CacheInvalidator类API

智能缓存失效管理器。

### 类初始化

**函数签名**:
```python
def __init__(self, cache: HierarchicalCache)
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `cache` | HierarchicalCache | 是 | - | HierarchicalCache实例 |

**使用示例**:

```python
from backend.core.cache import HierarchicalCache, CacheInvalidator

cache = HierarchicalCache()
invalidator = CacheInvalidator(cache)
```

---

### `invalidate()` - 精确失效

失效单个缓存键。

**函数签名**:
```python
def invalidate(self, pattern: str, **kwargs)
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `pattern` | str | 是 | - | 缓存模式 |
| `**kwargs` | dict | 是 | - | 参数键值对 |

**使用示例**:

```python
# 失效特定游戏的缓存
invalidator.invalidate('games.detail', id=1)
```

---

### `invalidate_pattern()` - 模式失效

失效匹配模式的所有L1缓存键。

**函数签名**:
```python
def invalidate_pattern(self, pattern: str, **kwargs) -> int
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `pattern` | str | 是 | - | 缓存模式 |
| `**kwargs` | dict | 是 | - | 要匹配的参数 |

**返回值**:
- `int`: 失效的键数量

**使用示例**:

```python
# 失效特定游戏的所有事件缓存
count = invalidator.invalidate_pattern('events.*', game_id=1)
print(f"已失效{count}个缓存键")
```

---

### `invalidate_batch()` - 批量失效

批量失效多个缓存键（使用Redis Pipeline优化）。

**函数签名**:
```python
def invalidate_batch(
    self,
    patterns: List[Tuple[str, Dict]]
) -> int
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `patterns` | List[Tuple[str, Dict]] | 是 | - | [(pattern, kwargs), ...] 列表 |

**返回值**:
- `int`: 失效的总键数

**使用示例**:

```python
# 批量失效多个缓存
patterns = [
    ('games.detail', {'id': 1}),
    ('games.list', {}),
    ('events.list', {'game_id': 1}),
]

count = invalidator.invalidate_batch(patterns)
print(f"已失效{count}个缓存键")
```

**注意事项**:
- 使用Redis Pipeline优化批量删除
- 自动降级到逐个删除（如果Redis不可用）

---

### `invalidate_game()` - 失效游戏缓存

失效游戏相关的所有缓存。

**函数签名**:
```python
def invalidate_game(self, game_id: int)
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `game_id` | int | 是 | - | 游戏ID |

**使用示例**:

```python
# 失效游戏ID为1的所有缓存
invalidator.invalidate_game(1)
```

**失效的缓存模式**:
- `games.detail` (id=game_id)
- `games.list`
- `events.list` (game_id=game_id)
- `events.*` (game_id=game_id)

---

### `invalidate_event()` - 失效事件缓存

失效事件相关的所有缓存。

**函数签名**:
```python
def invalidate_event(self, event_id: int)
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `event_id` | int | 是 | - | 事件ID |

**使用示例**:

```python
# 失效事件ID为1的所有缓存
invalidator.invalidate_event(1)
```

**失效的缓存模式**:
- `events.detail` (id=event_id)
- `params.*` (event_id=event_id)

---

## EnhancedBloomFilter类API

增强型布隆过滤器（防止缓存穿透）。

### 类初始化

**函数签名**:
```python
def __init__(
    self,
    capacity: int = 100000,
    error_rate: float = 0.001,
    persistence_path: Optional[str] = None,
    rebuild_interval: Optional[int] = None,
    persistence_interval: Optional[int] = None,
    strict_validation: bool = True
)
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `capacity` | int | 否 | 100000 | 初始容量 |
| `error_rate` | float | 否 | 0.001 | 目标误判率（0.1%） |
| `persistence_path` | str | 否 | 'data/bloom_filter.pkl' | 持久化路径 |
| `rebuild_interval` | int | 否 | 86400 | 重建间隔（秒，默认24小时） |
| `persistence_interval` | int | 否 | 300 | 持久化间隔（秒，默认5分钟） |
| `strict_validation` | bool | 否 | True | 严格路径验证（测试时设为False） |

**使用示例**:

```python
from backend.core.cache.bloom_filter_enhanced import EnhancedBloomFilter

# 创建布隆过滤器
bloom = EnhancedBloomFilter(
    capacity=100000,
    error_rate=0.001,
    persistence_path='data/bloom_filter.pkl'
)
```

---

### `add()` - 添加元素

添加元素到布隆过滤器。

**函数签名**:
```python
def add(self, key: str)
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `key` | str | 是 | - | 要添加的键 |

**使用示例**:

```python
bloom.add("cache_key_1")
bloom.add("cache_key_2")
```

---

### `contains()` - 检查元素

检查元素是否可能存在。

**函数签名**:
```python
def contains(self, key: str) -> bool
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `key` | str | 是 | - | 要检查的键 |

**返回值**:
- `bool`: True表示可能存在，False表示一定不存在

**使用示例**:

```python
if bloom.contains("cache_key_1"):
    print("可能存在")
else:
    print("一定不存在")
```

**注意事项**:
- 存在误判（False Positive）：可能返回True但实际不存在
- 不存在误判（False Negative）：返回False则一定不存在
- 误判率由`error_rate`参数控制

---

### `get_stats()` - 获取统计信息

获取布隆过滤器统计信息。

**函数签名**:
```python
def get_stats(self) -> dict
```

**返回值**:
- `dict`: 统计信息字典

**统计字段**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `total_items` | int | 实际添加的元素数量 |
| `estimated_capacity_used` | str | 预估容量使用率（百分比） |
| `false_positive_rate` | float | 目标误判率 |
| `capacity_alert` | bool | 是否达到容量告警阈值（90%） |

**使用示例**:

```python
stats = bloom.get_stats()
print(f"总元素数: {stats['total_items']}")
print(f"容量使用: {stats['estimated_capacity_used']}")
print(f"误判率: {stats['false_positive_rate']}")
```

---

### `save_to_disk()` - 保存到磁盘

手动保存布隆过滤器状态到磁盘。

**函数签名**:
```python
def save_to_disk(self) -> bool
```

**返回值**:
- `bool`: 保存是否成功

**使用示例**:

```python
success = bloom.save_to_disk()
if success:
    print("保存成功")
```

**注意事项**:
- 使用pybloom_live原生二进制格式（非pickle）
- 元数据单独保存为JSON文件（防止代码注入）

---

### `rebuild_from_redis()` - 从Redis重建

从Redis键重建布隆过滤器。

**函数签名**:
```python
def rebuild_from_redis(self) -> bool
```

**返回值**:
- `bool`: 重建是否成功

**使用示例**:

```python
success = bloom.rebuild_from_redis()
if success:
    print("重建成功")
```

**注意事项**:
- 扫描所有`dwd_gen:v3:`前缀的Redis键
- 重建过程可能较慢（取决于键数量）
- 重建后自动保存到磁盘

---

## IntelligentCacheWarmer类API

智能缓存预热器（基于历史访问预测热点）。

### 类初始化

**函数签名**:
```python
def __init__(
    self,
    access_log_size: int = 10000,
    warm_up_interval: int = 300
)
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `access_log_size` | int | 否 | 10000 | 访问日志大小 |
| `warm_up_interval` | int | 否 | 300 | 预热间隔（秒，默认5分钟） |

**使用示例**:

```python
from backend.core.cache.intelligent_warmer import IntelligentCacheWarmer

warmer = IntelligentCacheWarmer(
    access_log_size=10000,
    warm_up_interval=300
)
```

---

### `record_access()` - 记录访问

记录缓存访问到日志。

**函数签名**:
```python
def record_access(self, key: str)
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `key` | str | 是 | - | 缓存键 |

**使用示例**:

```python
warmer.record_access("dwd_gen:v3:games.detail:id:1")
```

**注意事项**:
- 自动记录时间戳
- 日志满时自动淘汰最旧记录（循环缓冲区）

---

### `predict_hot_keys()` - 预测热点键

预测未来N分钟的热点键。

**函数签名**:
```python
def predict_hot_keys(
    self,
    minutes: int = 5,
    top_n: int = 100,
    use_decay: bool = True
) -> List[str]
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `minutes` | int | 否 | 5 | 预测未来分钟数 |
| `top_n` | int | 否 | 100 | 返回前N个热点键 |
| `use_decay` | bool | 否 | True | 是否使用时间衰减 |

**返回值**:
- `List[str]`: 热点键列表（按频率降序）

**使用示例**:

```python
# 预测未来5分钟的热点键（使用时间衰减）
hot_keys = warmer.predict_hot_keys(minutes=5, top_n=100, use_decay=True)

# 预测热点键（不使用衰减）
hot_keys = warmer.predict_hot_keys(use_decay=False)
```

**预测算法**:
- **基础模式**: 统计最近1小时的访问频率
- **时间衰减**: 越近的访问权重越高（衰减因子0.95）

---

### `warm_up_cache()` - 预热缓存

预热指定的缓存键。

**函数签名**:
```python
async def warm_up_cache(
    self,
    keys: List[str],
    fetch_callback: Optional[Callable] = None
) -> Dict
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `keys` | List[str] | 是 | - | 要预热的键列表 |
| `fetch_callback` | Optional[Callable] | 否 | None | 从数据库获取数据的回调函数 |

**返回值**:
- `dict`: 预热统计

**统计字段**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `warmed` | int | 成功预热的键数 |
| `failed` | int | 预热失败的键数 |
| `skipped` | int | 跳过的键数（已在缓存中） |

**使用示例**:

```python
import asyncio

async def fetch_from_db(key):
    """从数据库获取数据"""
    # 解析键并查询数据库
    return fetch_data_from_db(key)

# 预热缓存
stats = await warmer.warm_up_cache(hot_keys, fetch_callback=fetch_from_db)
print(f"预热{stats['warmed']}个, 跳过{stats['skipped']}个, 失败{stats['failed']}个")
```

---

### `auto_warm_up()` - 自动预热

自动预测热点并预热（定时任务）。

**函数签名**:
```python
async def auto_warm_up(self, fetch_callback: Optional[Callable] = None)
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `fetch_callback` | Optional[Callable] | 否 | None | 从数据库获取数据的回调函数 |

**使用示例**:

```python
import asyncio

async def fetch_from_db(key):
    return fetch_data_from_db(key)

# 自动预热
await warmer.auto_warm_up(fetch_callback=fetch_from_db)
```

**注意事项**:
- 自动调用`predict_hot_keys()`预测热点
- 然后调用`warm_up_cache()`预热缓存

---

### `get_stats()` - 获取预热统计

获取预热统计信息。

**函数签名**:
```python
def get_stats(self) -> Dict
```

**返回值**:
- `dict`: 统计信息字典

**统计字段**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `warm_up_count` | float | 预热次数 |
| `keys_warmed` | float | 预热的键总数 |
| `last_warm_up_time` | float | 最后预热时间（Unix时间戳） |
| `prediction_accuracy` | float | 预测准确率（TODO） |

**使用示例**:

```python
stats = warmer.get_stats()
print(f"预热次数: {stats['warm_up_count']}")
print(f"预热键数: {stats['keys_warmed']}")
```

---

### `get_access_log_stats()` - 获取访问日志统计

获取访问日志统计信息。

**函数签名**:
```python
def get_access_log_stats(self) -> Dict
```

**返回值**:
- `dict`: 日志统计字典

**统计字段**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `total_access` | int | 总访问次数 |
| `recent_access` | int | 最近1小时访问次数 |
| `unique_keys` | int | 唯一键数量 |
| `buffer_capacity` | int | 缓冲区容量 |
| `buffer_usage` | str | 缓冲区使用率（百分比） |

**使用示例**:

```python
log_stats = warmer.get_access_log_stats()
print(f"总访问: {log_stats['total_access']}")
print(f"最近访问: {log_stats['recent_access']}")
print(f"唯一键: {log_stats['unique_keys']}")
```

---

## 辅助函数API

### `CacheKeyBuilder.build()` - 构建缓存键

构建标准化的缓存键。

**函数签名**:
```python
@classmethod
def build(cls, pattern: str, **kwargs) -> str
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `pattern` | str | 是 | - | 缓存模式（如 'events.list'） |
| `**kwargs` | dict | 是 | - | 参数键值对 |

**返回值**:
- `str`: 标准化的缓存键

**使用示例**:

```python
from backend.core.cache import CacheKeyBuilder

# 示例1: 无参数
key = CacheKeyBuilder.build('games.list')
# 输出: 'dwd_gen:v3:games.list'

# 示例2: 带参数
key = CacheKeyBuilder.build('games.detail', id=1)
# 输出: 'dwd_gen:v3:games.detail:id:1'

# 示例3: 多参数（自动排序）
key = CacheKeyBuilder.build('events.list', game_id=1, page=1)
key2 = CacheKeyBuilder.build('events.list', page=1, game_id=1)
# 两者输出相同: 'dwd_gen:v3:events.list:game_id:1:page:1'
```

**注意事项**:
- 参数自动排序，确保键一致性
- 添加版本前缀`dwd_gen:v3:`防止脏读

---

### `CacheKeyBuilder.build_pattern()` - 构建通配符模式

构建用于失效的通配符模式。

**函数签名**:
```python
@classmethod
def build_pattern(cls, pattern: str, **kwargs) -> str
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `pattern` | str | 是 | - | 缓存模式 |
| `**kwargs` | dict | 是 | - | 要匹配的参数（值为通配符） |

**返回值**:
- `str`: 通配符模式字符串

**使用示例**:

```python
from backend.core.cache import CacheKeyBuilder

# 示例1: 匹配所有games.list相关
pattern = CacheKeyBuilder.build_pattern('games.list')
# 输出: 'dwd_gen:v3:games.list:*'

# 示例2: 匹配特定游戏的所有缓存
pattern = CacheKeyBuilder.build_pattern('events.*', game_id=1)
# 输出: 'dwd_gen:v3:events.*:game_id:*'
```

---

### `get_cache()` - 获取Flask-Cache实例

获取Flask-Cache实例。

**函数签名**:
```python
def get_cache() -> Optional[object]
```

**返回值**:
- Flask-Cache实例或None

**使用示例**:

```python
from backend.core.cache import get_cache

cache = get_cache()
if cache:
    cache.set('key', 'value', timeout=300)
```

---

### `get_redis_client()` - 获取Redis客户端

获取Redis客户端。

**函数签名**:
```python
def get_redis_client() -> Optional[object]
```

**返回值**:
- Redis客户端或None

**使用示例**:

```python
from backend.core.cache import get_redis_client

redis_client = get_redis_client()
if redis_client:
    keys = redis_client.keys('dwd_gen:v3:*')
    print(f"找到{len(keys)}个缓存键")
```

---

### `clear_game_cache()` - 清除游戏缓存

清除游戏相关缓存（兼容性函数）。

**函数签名**:
```python
def clear_game_cache(game_id: Optional[int] = None)
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `game_id` | Optional[int] | 否 | None | 游戏ID（None表示清除所有游戏缓存） |

**使用示例**:

```python
from backend.core.cache import clear_game_cache

# 清除特定游戏缓存
clear_game_cache(game_id=1)

# 清除所有游戏缓存
clear_game_cache()
```

---

### `clear_event_cache()` - 清除事件缓存

清除事件相关缓存（兼容性函数）。

**函数签名**:
```python
def clear_event_cache(event_id: int)
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `event_id` | int | 是 | - | 事件ID |

**使用示例**:

```python
from backend.core.cache import clear_event_cache

clear_event_cache(event_id=1)
```

---

### `clear_cache_pattern()` - 清除模式缓存

清除匹配模式的所有缓存（兼容性函数）。

**函数签名**:
```python
def clear_cache_pattern(pattern: str)
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `pattern` | str | 是 | - | 缓存键模式（支持通配符） |

**使用示例**:

```python
from backend.core.cache import clear_cache_pattern

# 清除所有games相关缓存
clear_cache_pattern('games:*')
```

---

### `cache_result()` - 缓存装饰器（兼容性）

缓存装饰器（兼容性包装器）。

**函数签名**:
```python
def cache_result(
    cache_key_pattern: str,
    timeout: Optional[int] = None
)
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `cache_key_pattern` | str | 是 | - | 缓存键模式（旧格式） |
| `timeout` | Optional[int] | 否 | None | 超时时间（秒） |

**使用示例**:

```python
from backend.core.cache import cache_result

@cache_result('games:all', timeout=3600)
def get_all_games():
    return fetch_games_from_db()
```

**注意事项**:
- 兼容性函数，新代码应使用`@cached`
- 自动转换旧格式（'games:all' → 'games.all'）

---

### `parse_json_cached()` - 解析JSON（兼容性）

解析JSON字符串（兼容性函数）。

**函数签名**:
```python
def parse_json_cached(json_str: str) -> Optional[object]
```

**参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `json_str` | str | 是 | - | JSON字符串 |

**返回值**:
- 解析后的Python对象或None

**使用示例**:

```python
from backend.core.cache import parse_json_cached

data = parse_json_cached('{"key": "value"}')
```

**注意事项**:
- 兼容性函数，v3.0不再需要JSON解析缓存
- 直接使用`json.loads()`即可

---

## 常量和配置

### CacheKeyBuilder常量

```python
class CacheKeyBuilder:
    PREFIX = "dwd_gen:v3:"      # 缓存键前缀
    VERSION = "3.0"             # 版本号
```

### HierarchicalCache默认配置

```python
# 默认L1缓存配置
DEFAULT_L1_SIZE = 1000         # L1缓存容量（条）
DEFAULT_L1_TTL = 60            # L1缓存TTL（秒）

# 默认L2缓存配置
DEFAULT_L2_TTL = 3600          # L2缓存TTL（秒，1小时）
```

### EnhancedBloomFilter默认配置

```python
class EnhancedBloomFilter:
    DEFAULT_CAPACITY = 100000           # 默认容量
    DEFAULT_ERROR_RATE = 0.001          # 默认误判率（0.1%）
    PERSISTENCE_PATH = "data/bloom_filter.pkl"  # 持久化路径
    REBUILD_INTERVAL = 86400            # 重建间隔（24小时）
    PERSISTENCE_INTERVAL = 300          # 持久化间隔（5分钟）
    CAPACITY_ALERT_THRESHOLD = 0.9      # 容量告警阈值（90%）
```

### IntelligentCacheWarmer默认配置

```python
class IntelligentCacheWarmer:
    DEFAULT_ACCESS_LOG_SIZE = 10000     # 访问日志大小
    DEFAULT_WARM_UP_INTERVAL = 300      # 预热间隔（5分钟）
```

---

## 全局实例

缓存系统提供以下全局实例，可直接使用：

```python
from backend.core.cache import (
    hierarchical_cache,    # 全局HierarchicalCache实例
    cache_invalidator,     # 全局CacheInvalidator实例
    intelligent_cache_warmer,  # 全局IntelligentCacheWarmer实例
)

# 使用全局实例
data = hierarchical_cache.get('games.detail', id=1)
cache_invalidator.invalidate('games.detail', id=1)
```

---

## 类型注解

缓存系统使用以下类型注解：

```python
from typing import Any, Dict, List, Optional, Tuple, Callable

# 基础类型
CacheKey = str                    # 缓存键
CacheValue = Any                  # 缓存值
Pattern = str                     # 缓存模式

# 函数类型
FetchCallback = Callable[[str], Any]  # 数据获取回调

# 统计类型
StatsDict = Dict[str, Any]        # 统计字典
```

---

## 错误处理

缓存系统可能抛出以下异常：

```python
# 基础异常
class CacheException(Exception):
    """缓存系统基础异常"""

class CacheKeyError(CacheException):
    """缓存键错误"""

class CacheValueError(CacheException):
    """缓存值错误"""

class CacheConnectionError(CacheException):
    """缓存连接错误"""
```

**使用示例**:

```python
from backend.core.cache import CacheConnectionError

try:
    data = cache.get('games.detail', id=1)
except CacheConnectionError as e:
    logger.error(f"缓存连接失败: {e}")
    # 降级到数据库查询
    data = fetch_game_from_db(1)
```

---

## 完整使用示例

### 示例1: 游戏查询（使用装饰器）

```python
from backend.core.cache import cached_hierarchical, cache_invalidator

@cached_hierarchical('games.detail', ttl_l1=60, ttl_l2=300)
def get_game(game_id: int):
    """获取游戏详情（缓存5分钟）"""
    return fetch_game_from_db(game_id)

@cache_invalidator.invalidate('games.detail', key_params=['game_id'])
def update_game(game_id: int, data: dict):
    """更新游戏（失效缓存）"""
    result = update_game_in_db(game_id, data)
    # 装饰器自动失效缓存
    return result
```

### 示例2: 事件列表（使用缓存实例）

```python
from backend.core.cache import hierarchical_cache

def get_events(game_id: int, page: int):
    """获取事件列表"""
    # 尝试从缓存获取
    events = hierarchical_cache.get('events.list', game_id=game_id, page=page)

    if events is None:
        # 缓存未命中，查询数据库
        events = fetch_events_from_db(game_id, page)
        # 写入缓存（TTL: 5分钟）
        hierarchical_cache.set('events.list', events, ttl=300, game_id=game_id, page=page)

    return events
```

### 示例3: 批量失效（使用CacheInvalidator）

```python
from backend.core.cache import cache_invalidator

def delete_game(game_id: int):
    """删除游戏（失效所有相关缓存）"""
    # 删除数据库记录
    delete_game_from_db(game_id)

    # 失效所有游戏相关缓存
    cache_invalidator.invalidate_game(game_id)
```

### 示例4: 布隆过滤器（防止缓存穿透）

```python
from backend.core.cache.bloom_filter_enhanced import EnhancedBloomFilter
from backend.core.cache import hierarchical_cache

# 初始化布隆过滤器
bloom = EnhancedBloomFilter(capacity=100000, error_rate=0.001)

def get_game(game_id: int):
    """获取游戏（防止缓存穿透）"""
    key = f"game:{game_id}"

    # 检查布隆过滤器
    if not bloom.contains(key):
        # 一定不存在，缓存空值
        bloom.add(key)
        hierarchical_cache.set('games.detail', None, id=game_id)
        return None

    # 可能存在，查询缓存或数据库
    game = hierarchical_cache.get('games.detail', id=game_id)
    if game is None:
        game = fetch_game_from_db(game_id)
        if game:
            hierarchical_cache.set('games.detail', game, id=game_id)

    return game
```

### 示例5: 智能预热（使用IntelligentCacheWarmer）

```python
import asyncio
from backend.core.cache.intelligent_warmer import intelligent_cache_warmer

async def fetch_from_db(key: str):
    """从数据库获取数据"""
    # 解析键并查询数据库
    return fetch_data(key)

async def warm_up_cache():
    """预热缓存"""
    # 预测热点键
    hot_keys = intelligent_cache_warmer.predict_hot_keys(minutes=5, top_n=100)

    # 预热缓存
    stats = await intelligent_cache_warmer.warm_up_cache(hot_keys, fetch_from_db)
    print(f"预热完成: {stats}")

# 运行预热
asyncio.run(warm_up_cache())
```

---

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 3.2.0 | 2026-02-24 | 架构更新，统一使用cache_hierarchical.py |
| 3.1.0 | 2026-02-24 | 添加IntelligentCacheWarmer |
| 3.0.0 | 2026-01-27 | 三级分层缓存系统 |

---

## 相关文档

- **[开发者指南](developer-guide.md)** - 深入了解缓存系统架构
- **[5分钟快速开始](../quickstart/5-minute-guide.md)** - 新用户快速上手
- **[故障排除手册](../operations/troubleshooting.md)** - 解决常见问题
- **[代码片段参考](../quickstart/code-snippets.md)** - 可直接复制使用的代码模板

---

**文档维护**: Event2Table Development Team
**最后更新**: 2026-02-27
