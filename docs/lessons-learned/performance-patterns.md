# 性能模式

> **来源**: 整合了4个文档的性能相关经验
> **最后更新**: 2026-03-04
> **维护**: 每次性能问题修复后立即更新

---

## 缓存策略 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 3次 | **来源**: [缓存优化总结](../archive/2026-02/optimization/CACHE_OPTIMIZATION_SUMMARY.md), [最终优化报告](../archive/2026-02/optimization/FINAL_OPTIMIZATION_REPORT.md), [缓存清理记录](../../CLAUDE.md#2026-02-22-redis缓存清理与数据一致性)

### 缓存TTL建议

**推荐TTL**:
- ✅ **5-10分钟**（推荐）- 平衡性能和数据一致性
- ⚠️ **1小时**（过长）- 可能导致数据不一致
- ❌ **永久缓存**（禁止）- 数据永远不会更新

**问题案例**:
```
用户报告："当前页面仍有99个游戏而不是只有10000147一个"

根本原因：
- 数据库实际只有1个游戏（GID: 10000147）
- Redis缓存保存旧的99个游戏数据（TTL: 1小时）
- API优先返回缓存数据，导致数据不一致
```

### 缓存清理策略

**何时清理缓存**:
1. ✅ **修改游戏数据时** - 创建、更新、删除游戏后
2. ✅ **修改事件数据时** - 创建、更新、删除事件后
3. ✅ **修改参数数据时** - 创建、更新、删除参数后
4. ✅ **数据库迁移后** - game_gid迁移等数据结构变更后

**清理缓存示例**:
```python
from backend.core.cache.manager import cache_manager

# 修改游戏数据后清理缓存
@app.route('/api/games/<int:game_gid>', methods=['PUT'])
def update_game(game_gid):
    # ... 更新逻辑 ...

    # ✅ 清理缓存
    cache_manager.invalidate_game_cache(game_gid)

    return json_success_response(data=updated_game)
```

**批量清理缓存**:
```python
# 批量删除事件后清理缓存
@app.route('/api/events/batch-delete', methods=['POST'])
def batch_delete_events():
    # ... 批量删除逻辑 ...

    # ✅ 清理相关缓存
    for event_gid in event_gids:
        cache_manager.invalidate_event_cache(event_gid)

    return json_success_response(message=f"Deleted {len(event_gids)} events")
```

### 缓存一致性验证

**验证脚本**:
```python
# 验证缓存一致性
def verify_cache_consistency():
    """验证Redis缓存与数据库一致性"""
    # 1. 获取数据库中的游戏数量
    db_count = fetch_one_as_dict("SELECT COUNT(*) as count FROM games")["count"]

    # 2. 获取缓存中的游戏数量
    cached_games = cache.get("games:all")
    cache_count = len(cached_games) if cached_games else 0

    # 3. 对比数量
    if db_count != cache_count:
        logger.warning(f"Cache inconsistency detected: DB={db_count}, Cache={cache_count}")
        # 清理缓存
        cache.delete("games:all")

    return db_count == cache_count
```

### 预防措施

**代码审查清单**:
- [ ] 缓存TTL是否设置为5-10分钟？
- [ ] 所有修改数据的API是否清理缓存？
- [ ] 是否定期验证缓存一致性？
- [ ] 数据库迁移后是否清理所有相关缓存？

### 相关经验

- [N+1查询优化](#n1查询优化) - 另一个重要的性能优化
- [数据库模式 - game_gid迁移](./database-patterns.md#game_gid迁移) - 数据库性能优化

### 案例文档

- [Redis缓存清理与数据一致性](../../CLAUDE.md#2026-02-22-redis缓存清理与数据一致性)
- [后端优化Phase 2 - 性能优化](../archive/2026-02/optimization/FINAL_OPTIMIZATION_REPORT.md#phase-2-性能优化)

---

## N+1查询优化 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 2次 | **来源**: [缓存优化总结](../archive/2026-02/optimization/CACHE_OPTIMIZATION_SUMMARY.md), [最终优化报告](../archive/2026-02/optimization/FINAL_OPTIMIZATION_REPORT.md)

### 问题现象

**症状描述**:
- 查询响应时间长（数秒到数十秒）
- 数据库CPU使用率高
- 页面加载缓慢

**影响范围**:
- 循环中执行查询的代码
- 缺少JOIN或预加载的关联查询

### 根本原因

**技术原因**:
1. **循环中查询** - 在循环中执行数据库查询
2. **缺少JOIN** - 应该使用JOIN但使用了多次查询
3. **缺少预加载** - 应该预加载关联数据但按需加载

**错误示例**:
```python
# ❌ 错误：N+1查询（1次查询获取事件，N次查询获取每个事件的游戏）
events = fetch_all_as_dict("SELECT * FROM log_events")
for event in events:
    game = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (event['game_gid'],))
    event['game'] = game
# 总查询数：1 + N次
```

### 解决方案

**1. 使用JOIN**:
```python
# ✅ 正确：使用JOIN一次查询
events = fetch_all_as_dict('''
    SELECT
        le.*,
        g.name as game_name,
        g.ods_db as game_ods_db
    FROM log_events le
    INNER JOIN games g ON le.game_gid = g.gid
''')
# 总查询数：1次
```

**2. 合并统计查询**:
```python
# ❌ 错误：多次统计查询
stats1 = fetch_one_as_dict("SELECT COUNT(*) as count FROM log_events WHERE game_gid = ?", (game_gid,))
stats2 = fetch_one_as_dict("SELECT COUNT(*) as count FROM log_events WHERE game_gid = ? AND created_at > ?", (game_gid, start_date,))
# 总查询数：2次

# ✅ 正确：合并统计查询
stats = fetch_one_as_dict('''
    SELECT
        COUNT(*) as total_count,
        SUM(CASE WHEN created_at > ? THEN 1 ELSE 0 END) as recent_count
    FROM log_events
    WHERE game_gid = ?
''', (start_date, game_gid,))
# 总查询数：1次
```

**3. 使用EXPLAIN QUERY PLAN分析**:
```bash
# 分析慢查询
sqlite3 data/dwd_generator.db "EXPLAIN QUERY PLAN SELECT * FROM log_events INNER JOIN games ON log_events.game_gid = games.gid"
```

### 预防措施

**代码审查清单**:
- [ ] 是否有循环中的数据库查询？
- [ ] 是否可以使用JOIN合并多次查询？
- [ ] 是否可以合并统计查询？
- [ ] 是否使用EXPLAIN QUERY PLAN分析慢查询？

### 相关经验

- [缓存策略](#缓存策略) - 缓存优化
- [数据库索引](#数据库索引) - 索引优化

### 案例文档

- [后端优化Phase 2 - 性能优化](../archive/2026-02/optimization/FINAL_OPTIMIZATION_REPORT.md#phase-2-性能优化)
- [性能测试脚本](../../scripts/performance/parameter_management_performance.py)

---

## 数据库索引 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [OPTIMIZATION_LESSONS_LEARNED.md](../archive/2026-02/optimization/OPTIMIZATION_LESSONS_LEARNED.md)

### 索引设计原则

**何时创建索引**:
- ✅ 频繁用于WHERE条件的列
- ✅ 频繁用于JOIN的列
- ✅ 频繁用于ORDER BY的列
- ❌ 很少查询的列
- ❌ 数据频繁更新的列

**创建索引示例**:
```sql
-- 为game_gid创建索引（频繁用于JOIN和WHERE）
CREATE INDEX idx_log_events_game_gid ON log_events(game_gid);

-- 为created_at创建索引（频繁用于排序和范围查询）
CREATE INDEX idx_log_events_created_at ON log_events(created_at);

-- 复合索引（多列查询）
CREATE INDEX idx_log_events_game_gid_created_at ON log_events(game_gid, created_at);
```

### 索引验证

**验证索引是否使用**:
```bash
# 使用EXPLAIN QUERY PLAN验证
sqlite3 data/dwd_generator.db "EXPLAIN QUERY PLAN SELECT * FROM log_events WHERE game_gid = 10000147"
```

**预期输出**:
```
SEARCH log_events USING INDEX idx_log_events_game_gid (game_gid=?)
```

### 代码审查清单

- [ ] 是否为频繁查询的列创建了索引？
- [ ] 是否使用EXPLAIN QUERY PLAN验证索引使用情况？
- [ ] 是否避免了过度索引（影响写入性能）？

---

## 分页支持 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 1次 | **来源**: [FINAL_OPTIMIZATION_REPORT.md Phase 2](../archive/2026-02/optimization/FINAL_OPTIMIZATION_REPORT.md)

### 问题现象

**症状描述**:
- 大数据集查询导致内存溢出
- 响应时间长（数秒到数十秒）
- 前端渲染大量数据卡顿

### 解决方案

**后端分页**:
```python
def get_events_paginated(game_gid: int, page: int = 1, per_page: int = 20):
    """分页获取事件"""
    offset = (page - 1) * per_page

    # 查询总数
    total = fetch_one_as_dict(
        "SELECT COUNT(*) as count FROM log_events WHERE game_gid = ?",
        (game_gid,)
    )['count']

    # 分页查询
    events = fetch_all_as_dict('''
        SELECT * FROM log_events
        WHERE game_gid = ?
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    ''', (game_gid, per_page, offset))

    return {
        'events': events,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    }
```

**API示例**:
```python
@api_bp.route('/api/events', methods=['GET'])
def list_events():
    game_gid = request.args.get('game_gid', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # ✅ 限制per_page最大值
    per_page = min(per_page, 100)

    return json_success_response(
        data=get_events_paginated(game_gid, page, per_page)
    )
```

### 代码审查清单

- [ ] 所有列表API是否支持分页？
- [ ] per_page是否设置最大值限制（建议100）？
- [ ] 是否返回总数和总页数？
- [ ] 是否使用LIMIT + OFFSET而非加载全部数据？

---

## game_gid转换缓存 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [FINAL_OPTIMIZATION_REPORT.md Phase 2](../archive/2026-02/optimization/FINAL_OPTIMIZATION_REPORT.md)

### 问题现象

**症状描述**:
- 频繁查询game_id到game_gid的转换
- 每次转换都执行数据库查询
- 游戏信息不变但重复查询

### 解决方案

**使用LRU缓存**:
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_game_id_from_gid(game_gid: int) -> Optional[int]:
    """获取game_id（带缓存）"""
    game = fetch_one_as_dict('SELECT id FROM games WHERE gid = ?', (game_gid,))
    return game['id'] if game else None

@lru_cache(maxsize=128)
def get_game_gid_from_id(game_id: int) -> Optional[int]:
    """获取game_gid（带缓存）"""
    game = fetch_one_as_dict('SELECT gid FROM games WHERE id = ?', (game_id,))
    return game['gid'] if game else None
```

**性能提升**:
- 首次查询：~10ms
- 缓存命中：<0.1ms
- 缓存命中率：>95%（游戏GID不变）

### 代码审查清单

- [ ] 是否使用lru_cache缓存game_id/game_gid转换？
- [ ] 缓存大小是否合理（建议128）？
- [ ] 是否有缓存失效机制（游戏删除时）？

---

## Dashboard统计查询合并 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [FINAL_OPTIMIZATION_REPORT.md Phase 2](../archive/2026-02/optimization/FINAL_OPTIMIZATION_REPORT.md)

### 优化前（5个查询）:
```python
# ❌ 多次独立查询
game_count = fetch_one_as_dict("SELECT COUNT(*) as count FROM games")['count']
event_count = fetch_one_as_dict("SELECT COUNT(*) as count FROM log_events")['count']
param_count = fetch_one_as_dict("SELECT COUNT(*) as count FROM event_params")['count']
recent_games = fetch_all_as_dict("SELECT * FROM games ORDER BY created_at DESC LIMIT 5")
recent_events = fetch_all_as_dict("SELECT * FROM log_events ORDER BY created_at DESC LIMIT 5")
# 总计：5个查询
```

### 优化后（2个查询）:
```python
# ✅ 合并统计查询
stats = fetch_one_as_dict('''
    SELECT
        (SELECT COUNT(*) FROM games) as game_count,
        (SELECT COUNT(*) FROM log_events) as event_count,
        (SELECT COUNT(*) FROM event_params) as param_count
''')

recent = fetch_all_as_dict('''
    SELECT 'game' as type, id, name, created_at
    FROM games
    ORDER BY created_at DESC
    LIMIT 5
    UNION ALL
    SELECT 'event' as type, id, name, created_at
    FROM log_events
    ORDER BY created_at DESC
    LIMIT 5
''')
# 总计：2个查询
```

**性能提升**:
- Dashboard加载时间：2.5s → 0.8s（68%提升）
- 数据库查询：5个 → 2个（60%减少）

---

## 多级缓存架构 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [缓存优化报告](../archive/2026-02/optimization/CACHE_OPTIMIZATION_SUMMARY.md)

### 三级缓存架构

**L1 - 内存缓存**:
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_game_id_from_gid(game_gid: int) -> Optional[int]:
    """L1缓存：game_id转换（进程内存）"""
    game = fetch_one_as_dict('SELECT id FROM games WHERE gid = ?', (game_gid,))
    return game['id'] if game else None
```

**L2 - Redis缓存**:
```python
from backend.core.cache.manager import cache_manager

@cached('games.list', timeout=300)
def get_all_games(include_stats: bool = False):
    """L2缓存：游戏列表（跨进程共享）"""
    # 业务逻辑
    pass
```

**L3 - 数据库缓存**:
```python
# SQLite查询缓存（SQLite内部管理）
# 使用索引加速查询
CREATE INDEX idx_games_gid ON games(gid);
```

### 缓存层级使用

**选择缓存层级**:
- ✅ **L1内存** - 频繁访问、数据量小、不常变化（game_id转换）
- ✅ **L2 Redis** - 跨进程共享、数据量中等（游戏列表、事件列表）
- ✅ **L3 数据库** - 持久化存储、大数据集（所有数据）

### 缓存更新策略

**Cache-Aside Pattern**:
```python
def get_game_with_cache(game_gid: int):
    """Cache-Aside模式"""
    # 1. 尝试从缓存获取
    game = cache.get(f"game:{game_gid}")
    if game:
        return game  # ✅ 缓存命中

    # 2. 缓存未命中，查询数据库
    game = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (game_gid,))

    # 3. 写入缓存
    cache.set(f"game:{game_gid}", game, timeout=300)

    return game
```

### 代码审查清单

- [ ] 是否正确使用了三级缓存？
- [ ] L1缓存是否使用lru_cache？
- [ ] L2缓存是否设置合理的TTL？
- [ ] L3是否使用索引优化？
- [ ] 是否使用Cache-Aside模式？

---

## Cache Tags系统 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [缓存优化报告](../archive/2026-02/optimization/CACHE_OPTIMIZATION_SUMMARY.md)

### Cache Tags概念

**问题**:
- 传统缓存失效需要手动指定每个缓存键
- 批量失效缓存容易遗漏

**Cache Tags解决方案**:
- 为缓存打标签（tags）
- 按标签批量失效缓存

### 实现示例

**设置带标签的缓存**:
```python
from backend.core.cache.manager import cache_manager

# 设置缓存时添加标签
cache_manager.set(
    key="game:10000147",
    value={"name": "STAR001", "gid": 10000147},
    timeout=300,
    tags=["games", "game:10000147"]  # ✅ 添加标签
)

cache_manager.set(
    key="events:10000147",
    value=[...],
    timeout=300,
    tags=["events", "game:10000147"]  # ✅ 添加标签
)
```

**按标签批量失效**:
```python
# 失效所有games相关缓存
cache_manager.delete_many(tags=["games"])

# 失效特定游戏的所有缓存
cache_manager.delete_many(tags=["game:10000147"])

# 同时失效games和dashboard缓存
cache_manager.delete_many(tags=["games", "dashboard"])
```

### Cache Tags优势

**优势**:
- ✅ 无需记住所有缓存键
- ✅ 按业务逻辑分组失效
- ✅ 避免缓存遗漏

**适用场景**:
- 游戏数据修改 → 失效"games"和"dashboard"标签
- 事件数据修改 → 失效"events"和"dashboard"标签
- 参数数据修改 → 失效"params"和"dashboard"标签

### 代码审查清单

- [ ] 缓存是否使用了tags？
- [ ] tags是否按业务逻辑分组？
- [ ] 数据修改后是否按tags失效？
- [ ] 是否避免了逐个失效缓存键？

---

## 性能监控装饰器 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [缓存优化报告](../archive/2026-02/optimization/CACHE_OPTIMIZATION_SUMMARY.md)

### 性能监控装饰器

**实现**:
```python
import time
import logging
from functools import wraps

def monitor_performance(func_name: str = None):
    """性能监控装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 记录开始时间
            start_time = time.time()

            try:
                # 执行函数
                result = func(*args, **kwargs)

                # 计算执行时间
                execution_time = time.time() - start_time

                # 记录性能日志
                name = func_name or func.__name__
                logger.info(f"[Performance] {name} executed in {execution_time:.3f}s")

                # 性能告警
                if execution_time > 1.0:
                    logger.warning(f"[Performance] {name} is slow: {execution_time:.3f}s")

                return result

            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"[Performance] {name} failed after {execution_time:.3f}s: {e}")
                raise

        return wrapper
    return decorator
```

**使用示例**:
```python
@monitor_performance("get_all_games")
def get_all_games():
    """获取所有游戏（带性能监控）"""
    return fetch_all_as_dict("SELECT * FROM games")

@monitor_performance("generate_hql")
def generate_hql(canvas):
    """生成HQL（带性能监控）"""
    # HQL生成逻辑
    pass
```

### 性能监控指标

**关键指标**:
- **执行时间** - 函数执行时长
- **慢查询** - 执行时间>1秒
- **错误率** - 异常发生次数
- **缓存命中率** - 缓存命中/总请求

**监控Dashboard**:
```python
def get_performance_stats():
    """获取性能统计"""
    return {
        "avg_execution_time": 0.234,  # 秒
        "slow_queries": 3,            # 慢查询数量
        "error_rate": 0.01,           # 1%错误率
        "cache_hit_rate": 0.95        # 95%缓存命中率
    }
```

### 代码审查清单

- [ ] 关键函数是否添加了性能监控？
- [ ] 是否记录了执行时间？
- [ ] 是否有慢查询告警？
- [ ] 是否定期查看性能报告？

---

## Bloom Filter在数据库防护中的应用 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [EVENTS-PY-MIGRATION-STATS.md](../archive/testing-reports/2026-03-01/2026-03-01/EVENTS-PY-MIGRATION-STATS.md)

### 应用场景

**问题场景**:
- 存在大量无效数据库查询
- 查询不存在的事件ID导致不必要的数据库访问
- 数据库CPU使用率高

### 解决方案

**Bloom Filter快速拒绝**:
```python
from pybloom_live import ScalableBloomFilter

class EventService:
    def __init__(self):
        # 初始化Bloom Filter（容量500,000，误判率0.1%）
        self.bloom_filter = ScalableBloomFilter(
            initial_capacity=500000,
            error_rate=0.001
        )
        self._warm_up_bloom_filter()

    def _warm_up_bloom_filter(self):
        """预热Bloom Filter"""
        events = fetch_all_as_dict("SELECT id FROM log_events")
        for event in events:
            self.bloom_filter.add(event['id'])

    def get_event_by_id(self, event_id: int):
        """获取事件（带Bloom Filter检查）"""
        # ✅ 先快速检查是否存在
        if event_id not in self.bloom_filter:
            return None  # 快速拒绝，避免数据库查询

        # ✅ 再查询数据库
        return fetch_one_as_dict(
            "SELECT * FROM log_events WHERE id = ?",
            (event_id,)
        )
```

**性能提升**:
- 不存在的ID查询：10ms → <0.1ms（99%提升）
- 误判率：<0.1%（可接受）
- 数据库查询减少：70-80%

### 代码审查清单

- [ ] 是否使用Bloom Filter快速拒绝不存在的数据？
- [ ] Bloom Filter容量是否足够（建议500,000+）？
- [ ] 误判率是否合理（建议<0.1%）？
- [ ] 是否有预热机制？

### 相关经验

- [缓存策略](#缓存策略) - 缓存优化
- [N+1查询优化](#n1查询优化) - 查询优化

### 案例文档

- [Events迁移统计](../archive/testing-reports/2026-03-01/2026-03-01/EVENTS-PY-MIGRATION-STATS.md)

---

## 缓存失效分析 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 1次 | **来源**: [CACHE-MISS-ANALYSIS-REPORT](../archive/2026-03/02-march/reports/CACHE-MISS-ANALYSIS-REPORT.md)

### 问题现象

**症状描述**:
- 缓存命中率低（<60%）
- API响应时间长（>1秒）
- 数据库查询频繁
- 用户感觉到数据更新延迟

**影响范围**:
- 所有使用缓存的API
- 数据一致性要求高的场景

### 缓存未命中原因

**1. 缓存键生成错误**
```python
# ❌ 错误：缓存键不包含重要参数
@cached(ttl=300)
def get_events(game_gid: int):
    return fetch_all_as_dict("SELECT * FROM log_events WHERE game_gid = ?", (game_gid,))
# 问题：所有game_gid共享同一缓存！

# ✅ 正确：缓存键包含参数
@cached(ttl=300)
def get_events(game_gid: int):
    # 装饰器自动将参数包含在缓存键中
    return fetch_all_as_dict("SELECT * FROM log_events WHERE game_gid = ?", (game_gid,))
# 不同game_gid有不同缓存：events:10000147, events:10000148
```

**2. 缓存TTL过短**
```python
# ❌ 错误：TTL太短（5秒）
@cached(ttl=5)
def get_games():
    return fetch_all_as_dict("SELECT * FROM games")
# 问题：缓存频繁失效，命中率低

# ✅ 正确：TTL合理（5-10分钟）
@cached(ttl=300)  # 5分钟
def get_games():
    return fetch_all_as_dict("SELECT * FROM games")
```

**3. 数据更新后未清理缓存**
```python
# ❌ 错误：更新数据库后未清理缓存
@app.route('/api/games/<int:game_gid>', methods=['PUT'])
def update_game(game_gid):
    execute_update("UPDATE games SET name = ? WHERE gid = ?", (name, game_gid))
    # 问题：缓存未清理，用户看到旧数据

# ✅ 正确：使用@cache_invalidate装饰器
@app.route('/api/games/<int:game_gid>', methods=['PUT'])
@cache_invalidate  # ✅ 自动清理缓存
def update_game(game_gid):
    execute_update("UPDATE games SET name = ? WHERE gid = ?", (name, game_gid))
```

**4. Bloom Filter误判**
```python
# Bloom Filter误判导致缓存未命中
if event_id not in bloom_filter:
    return None  # 快速拒绝
# 问题：Bloom Filter可能有误判（<0.1%）
```

### 缓存失效策略

**策略1: 自动失效装饰器**
```python
from backend.core.cache.decorators import cached, cache_invalidate

# ✅ 读操作使用缓存
@cached(ttl=300)
def get_events(game_gid: int):
    return fetch_all_as_dict("SELECT * FROM log_events WHERE game_gid = ?", (game_gid,))

# ✅ 写操作自动清理缓存
@cache_invalidate
def create_event(game_gid: int, event_data: dict):
    return execute_insert("INSERT INTO log_events ...", (...))

@cache_invalidate
def update_event(event_id: int, event_data: dict):
    execute_update("UPDATE log_events SET ... WHERE id = ?", (event_id,))

@cache_invalidate
def delete_event(event_id: int):
    execute_update("DELETE FROM log_events WHERE id = ?", (event_id,))
```

**策略2: 手动清理缓存**
```python
from backend.core.cache.cache_system import cache_result

# ✅ 手动删除缓存
def delete_game(game_gid: int):
    execute_update("DELETE FROM games WHERE gid = ?", (game_gid,))
    # 清理相关缓存
    cache_result.delete_many(f"games:*")
    cache_result.delete_many(f"events:{game_gid}:*")
    cache_result.delete_many(f"params:{game_gid}:*")
```

**策略3: Cache Tags批量失效**
```python
# 设置缓存时添加标签
cache_manager.set(
    key="game:10000147",
    value=game_data,
    timeout=300,
    tags=["games", "game:10000147"]  # ✅ 添加标签
)

# 按标签批量失效
cache_manager.delete_many(tags=["games"])  # 失效所有games相关缓存
cache_manager.delete_many(tags=["game:10000147"])  # 失效特定游戏的所有缓存
```

### 缓存一致性验证

**验证脚本**:
```python
def verify_cache_consistency():
    """验证缓存与数据库一致性"""
    # 1. 获取数据库中的游戏数量
    db_count = fetch_one_as_dict("SELECT COUNT(*) as count FROM games")["count"]

    # 2. 获取缓存中的游戏数量
    cached_games = cache.get("games:all")
    cache_count = len(cached_games) if cached_games else 0

    # 3. 对比数量
    if db_count != cache_count:
        logger.warning(f"Cache inconsistency detected: DB={db_count}, Cache={cache_count}")
        # 清理缓存
        cache.delete("games:all")
        return False

    return True
```

### 代码审查清单

**缓存检查**:
- [ ] 所有查询函数是否使用`@cached`装饰器？
- [ ] 缓存TTL是否合理（5-10分钟）？
- [ ] 所有修改数据的API是否使用`@cache_invalidate`？
- [ ] 缓存键是否包含所有必要参数？
- [ ] 是否定期验证缓存一致性？

### 相关经验

- [缓存策略](#缓存策略) - 缓存TTL和清理策略
- [多级缓存架构](#多级缓存架构) - 三级缓存设计

---

## 并行优化策略 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 1次 | **来源**: [PARALLEL-OPTIMIZATION-FINAL-REPORT](../archive/2026-03/02-march/reports/PARALLEL-OPTIMIZATION-FINAL-REPORT.md)

### 核心原则

**独立任务并行执行，依赖任务串行执行**

**并行执行模式**:
```
串行执行: 12小时
Phase 1 → Phase 2 → Phase 3 → Phase 4

并行执行: 3.5小时 (提升70%)
Phase 1 ↘
Phase 2 → 同时执行 → 总时间 = max(Phase时间)
Phase 3 ↗
Phase 4 (依赖Phase 1-3)
```

### 识别独立任务

**独立任务特征**:
- ✅ 修改不同的文件（games.py vs events.py）
- ✅ 修改不同的模块（Service层 vs Repository层）
- ✅ 修改不同的功能域（缓存系统 vs 验证器）
- ✅ 无共享状态
- ✅ 无数据依赖

**依赖任务特征**:
- ❌ Service层依赖Repository层 → 必须串行
- ❌ 前端依赖后端API → 必须串行
- ❌ 测试依赖实现 → 必须串行

### 并行执行案例

**案例: 后端架构全面优化**

**Phase 1: 紧急修复（独立）**
- 修复games.py双规制
- 修复hql_generation.py双规制
- 标记删除EventParamRepository

**Phase 2: Service层重构（独立）**
- 重构参数管理模块
- 统一HQL服务层
- 修复Event Importer
- 创建CanvasService
- 扩展GameService
- 扩展ParameterService

**Phase 3: 核心模块迁移（依赖Phase 2）**
- Join Configs模块迁移
- Event Categories模块迁移
- 新增stats和batch-delete端点

**Phase 4: 全面清理（依赖Phase 1-3）**
- 清理V2废弃文件
- Repository层更新
- 删除EventParamRepository
- 完善缓存策略
- 更新项目文档

**并行执行**:
```
Phase 1 (紧急修复) ↘
Phase 2 (Service重构) → 同时执行（3.5小时）
Phase 3 (模块迁移) ↗
                 ↓
Phase 4 (全面清理) → 依赖Phase 1-3完成

总时间: max(2h, 3h, 3.5h) + 1.5h = 5h
串行时间: 2h + 3h + 3.5h + 1.5h = 12h
性能提升: (12 - 5) / 12 = 58% 实际提升
```

### 并行开发工具

**使用Claude Code Subagent**:
```python
# 并行启动3个subagents
Task(
    description="修复games.py双规制",
    prompt="修复games.py中的双规制问题...",
    subagent_type="general-purpose"
)

Task(
    description="修复hql_generation.py双规制",
    prompt="修复hql_generation.py中的双规制问题...",
    subagent_type="general-purpose"
)

Task(
    description="重构参数管理模块",
    prompt="重构参数管理模块，统一Service层...",
    subagent_type="general-purpose"
)

# 3个subagents同时执行
```

**使用Git Worktrees**:
```bash
# 为每个独立任务创建worktree
git worktree add ../event2table-phase1 -b phase1-fixes
git worktree add ../event2table-phase2 -b phase2-service
git worktree add ../event2table-phase3 -b phase3-migration

# 在3个worktree中并行开发
cd ../event2table-phase1  # 修复games.py
cd ../event2table-phase2  # 重构Service层
cd ../event2table-phase3  # 迁移模块
```

### 并行执行风险

**风险1: 合并冲突**
- **原因**: 多个开发者修改同一文件
- **缓解**: 使用Git分支，定期合并

**风险2: 依赖变化**
- **原因**: "独立"任务后来发现有依赖
- **缓解**: 在执行前仔细分析依赖关系

**风险3: 测试复杂度**
- **原因**: 并行开发的代码需要集成测试
- **缓解**: Phase完成后立即集成测试

### 代码审查清单

**并行开发检查**:
- [ ] 任务是否真正独立（无共享状态）？
- [ ] 是否有明确的依赖关系？
- [ ] 并行任务是否有冲突的文件修改？
- [ ] 是否有集成测试计划？
- [ ] Git分支策略是否合理？

### 相关经验

- [项目管理 - 并行开发策略](./project-management.md#并行开发策略) - 项目级并行开发
- [项目管理 - 大规模重构](./project-management.md#大规模重构) - 分阶段执行策略

---

## 相关经验文档

- [数据库模式 - game_gid迁移](./database-patterns.md#game_gid迁移) - 数据库性能优化
- [API设计模式 - 分层架构](./api-design-patterns.md#分层架构) - 架构性能优化
