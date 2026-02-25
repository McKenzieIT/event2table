# 缓存系统增强模块

## 概述

本次优化为Event2Table项目的缓存系统添加了完整的防护机制、失效策略和统计监控功能。

## 新增模块

### 1. 缓存防护模块 (`protection.py`)

提供三级防护机制：

#### 1.1 布隆过滤器（防止缓存穿透）
- 使用 `pybloom_live.ScalableBloomFilter` 实现
- 自动将存在的键添加到布隆过滤器
- 拦截不存在的键查询，避免穿透到数据库

#### 1.2 分布式锁（防止缓存击穿）
- 使用线程锁实现分布式锁
- 防止热点数据过期时大量请求同时查询数据库
- 支持锁超时和自动释放

#### 1.3 TTL随机化（防止缓存雪崩）
- 在基础TTL上增加±20%的随机抖动
- 避免大量缓存同时过期

#### 使用示例

```python
from backend.core.cache.protection import cache_protection

# 使用布隆过滤器防护
result = cache_protection.get_with_bloom_filter(
    'games.detail',
    lambda: fetch_game_from_db(gid),
    ttl=300,
    gid=10000147
)

# 使用分布式锁防护
result = cache_protection.get_with_lock(
    'hot_games.list',
    lambda: fetch_hot_games(),
    ttl=60
)

# 使用完整防护
result = cache_protection.get_with_full_protection(
    'events.list',
    lambda: fetch_events(game_gid),
    ttl=300,
    use_bloom_filter=True,
    use_lock=True,
    use_random_ttl=True,
    game_gid=10000147
)
```

### 2. 缓存失效器模块 (`invalidator.py`)

提供统一的缓存失效策略管理：

#### 2.1 精确失效
- 删除特定缓存键

#### 2.2 模式失效
- 使用通配符删除匹配的键
- 同时失效L1和L2缓存

#### 2.3 关联失效
- `invalidate_game_related()` - 失效游戏相关的所有缓存
- `invalidate_event_related()` - 失效事件相关的所有缓存
- `invalidate_parameter_related()` - 失效参数相关的所有缓存

#### 使用示例

```python
from backend.core.cache.invalidator import cache_invalidator_enhanced

# 失效游戏相关缓存
invalidated_keys = cache_invalidator_enhanced.invalidate_game_related(10000147)

# 失效事件相关缓存
invalidated_keys = cache_invalidator_enhanced.invalidate_event_related(123, 10000147)

# 批量失效
patterns = [
    ('games.detail', {'gid': 10000147}),
    ('events.list', {'game_id': 10000147}),
]
count = cache_invalidator_enhanced.invalidate_batch(patterns)
```

### 3. 缓存统计模块 (`statistics.py`)

提供详细的缓存统计和性能监控：

#### 3.1 命中率统计
- L1/L2/总体命中率
- 命中次数、未命中次数

#### 3.2 性能指标统计
- 平均响应时间
- QPS（每秒查询数）
- Redis性能指标

#### 3.3 热点键分析
- 访问频率统计
- Top N热点键

#### 3.4 性能趋势
- 历史性能数据
- 趋势分析

#### 使用示例

```python
from backend.core.cache.statistics import cache_statistics

# 记录访问
cache_statistics.record_access(
    key="games:detail:gid:10000147",
    hit=True,
    level="l1",
    response_time=0.5
)

# 获取命中率统计
stats = cache_statistics.get_hit_rate_stats()

# 获取热点键
hot_keys = cache_statistics.get_hot_keys(limit=10)

# 获取性能趋势
trend = cache_statistics.get_performance_trend(hours=24)
```

### 4. 缓存管理API (`backend/api/routes/cache.py`)

提供REST API接口：

#### 4.1 统计API
- `GET /api/cache/stats` - 获取缓存统计信息
- `GET /api/cache/stats/detailed` - 获取详细统计信息

#### 4.2 键管理API
- `GET /api/cache/keys` - 列出所有缓存键
- `GET /api/cache/keys/search` - 搜索缓存键
- `GET /api/cache/keys/<key>` - 获取单个缓存键详情
- `DELETE /api/cache/keys/<key>` - 删除单个缓存键

#### 4.3 清理API
- `POST /api/cache/clear` - 清空所有缓存

#### 4.4 失效API
- `POST /api/cache/invalidate/game/<game_gid>` - 失效游戏相关缓存
- `POST /api/cache/invalidate/event/<event_id>` - 失效事件相关缓存

## 测试

### 测试文件
- `test_protection_enhanced.py` - 缓存防护测试
- `test_invalidator_enhanced.py` - 缓存失效器测试
- `test_statistics_enhanced.py` - 缓存统计测试

### 运行测试

```bash
# 运行所有缓存测试
pytest backend/test/unit/cache/test_*_enhanced.py -v

# 运行单个测试文件
pytest backend/test/unit/cache/test_protection_enhanced.py -v
```

## 依赖

新增依赖已添加到 `requirements.txt`:
- `cachetools==6.2.6` - 高级缓存工具
- `pybloom-live==4.0.0` - 布隆过滤器实现

安装依赖：
```bash
pip install -r requirements.txt
```

## 集成建议

### 1. 在Service层集成缓存防护

```python
# backend/services/games/game_service.py
from backend.core.cache.protection import cache_protection

class GameService:
    def get_game(self, gid: int) -> dict:
        """获取游戏（带完整防护）"""
        return cache_protection.get_with_full_protection(
            'games.detail',
            lambda: self._fetch_game_from_db(gid),
            ttl=300,
            gid=gid
        )
```

### 2. 在API层集成缓存失效

```python
# backend/api/routes/games.py
from backend.core.cache.invalidator import cache_invalidator_enhanced

@game_bp.route('/api/games/<int:gid>', methods=['PUT'])
def update_game(gid):
    # 更新游戏
    game = game_service.update_game(gid, request.json)
    
    # 失效相关缓存
    cache_invalidator_enhanced.invalidate_game_related(gid)
    
    return jsonify(game)
```

### 3. 定期记录性能快照

```python
# 在应用启动时启动定时任务
from backend.core.cache.statistics import cache_statistics
import threading
import time

def performance_monitor():
    while True:
        cache_statistics.record_performance_snapshot()
        time.sleep(60)  # 每分钟记录一次

thread = threading.Thread(target=performance_monitor, daemon=True)
thread.start()
```

## 性能指标

### 预期效果
- 缓存命中率提升至 85%+
- 缓存穿透减少 90%+
- 缓存击穿减少 95%+
- 平均响应时间降低 50%+

### 监控指标
- L1命中率
- L2命中率
- 总体命中率
- 平均响应时间
- QPS
- 布隆过滤器拦截次数
- 锁等待次数
- 空值缓存命中次数

## 版本历史

- v1.0.0 (2026-02-20)
  - 新增缓存防护模块（布隆过滤器、分布式锁、TTL随机化）
  - 新增缓存失效器模块（关联失效、批量失效）
  - 新增缓存统计模块（命中率、性能指标、热点键）
  - 新增缓存管理API
  - 新增完整的单元测试

## 作者

Event2Table Development Team

## 许可证

MIT License
