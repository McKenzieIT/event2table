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

## DataLoader批量查询优化 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 3次 | **来源**: [GraphQL DataLoader优化报告](../reports/2026-03-07/GRAPHQL-DATALOADER-OPTIMIZATION-REPORT.md), [性能优化Phase 1-4](../reports/2026-03-07/COMPLETE-PERFORMANCE-OPTIMIZATION-REPORT-PHASE-1-4.md)

### 问题现象

**症状描述**:
- GraphQL N+1查询导致数据库负载过重
- 查询100个事件需要101次数据库查询
- API响应时间长（500ms以上）
- 数据库连接数激增

**影响范围**:
- GraphQL API的关联查询
- 事件参数批量加载
- 游戏统计查询

### 根本原因

**技术原因**:
- GraphQL resolver中每个关联对象都独立查询
- 缺乏批量加载机制
- 子查询导致指数级增长

**错误示例**:
```python
# ❌ 错误：N+1查询
def resolve_parameters_old(root, info, event_id: int):
    """每个事件独立查询参数 - 错误！"""
    return fetch_all_as_dict(
        "SELECT * FROM event_params WHERE event_id = ?",
        (event_id,)
    )
# 对于100个事件，需要100次查询
```

### 解决方案

**方案1: 增强的DataLoader实现**
```python
class EnhancedParameterLoader:
    """增强的参数批量加载器"""

    def load_by_event(self, event_id: int):
        """加载单个事件的参数"""
        return self.load(event_id)

    def load_by_events(self, event_ids: List[int]):
        """批量加载多个事件的参数"""
        return self.load_many(event_ids)

    def _batch_load_parameters(self, event_ids: List[int]):
        """批量加载参数（包含模板信息）"""
        placeholders = ','.join(['?'] * len(event_ids))
        return fetch_all_as_dict(f"""
            SELECT
                ep.*,
                pt.name as template_name
            FROM event_params ep
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE ep.event_id IN ({placeholders})
            ORDER BY ep.event_id, ep.id
        """, event_ids)

# 使用DataLoader的Resolver
def resolve_param_count(self, info):
    """使用DataLoader批量加载参数数量"""
    from backend.gql_api.dataloaders.optimized_loaders import get_parameter_loader

    loader = get_parameter_loader()
    params = loader.load(self.id)
    return len(params) if params else 0
```

**方案2: 双层缓存DataLoader**
```python
class CachedDataLoader:
    def _batch_load_with_cache(
        self,
        keys: List[Any],
        batch_load_fn: callable,
        ttl_l1: int = 60,   # L1缓存: 60秒
        ttl_l2: int = 300   # L2缓存: 300秒
    ):
        """先从缓存获取，批量加载未缓存数据"""
        # L1缓存检查
        cache_results = {}
        missing_keys = []

        for key in keys:
            cached = cache_result.get(f"loader:{self.__class__.__name__}:{key}")
            if cached:
                cache_results[key] = cached
            else:
                missing_keys.append(key)

        # 批量加载缺失的数据
        if missing_keys:
            loaded = batch_load_fn(missing_keys)
            # 写入缓存
            for key, value in zip(missing_keys, loaded):
                cache_result.set(
                    f"loader:{self.__class__.__name__}:{key}",
                    value,
                    ttl=ttl_l1
                )
                cache_results[key] = value

        return [cache_results.get(key) for key in keys]
```

### 性能提升

**优化前**:
- 事件列表查询：101次（100个事件 + 1次主查询）
- API响应时间：~500ms
- 数据库负载：高

**优化后**:
- 事件列表查询：2次（1次主查询 + 1次批量参数查询）
- API响应时间：~50ms（90%提升）
- 数据库负载：降低70-90%

**查询减少率**: 70-99%

### 代码审查清单

- [ ] 是否使用DataLoader处理一对多关系？
- [ ] 是否配置了L1/L2多层缓存？
- [ ] 是否避免了JOIN优化后的重复查询？
- [ ] 是否验证了批量加载的性能提升？

### 相关经验

- [N+1查询优化](#n1查询优化) - 通用N+1查询优化
- [多级缓存架构](#多级缓存架构) - 缓存层级设计

### 案例文档

- [GraphQL DataLoader优化报告](../reports/2026-03-07/GRAPHQL-DATALOADER-OPTIMIZATION-REPORT.md)

---

## 批量操作优化 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [性能优化Phase 1-4](../reports/2026-03-07/COMPLETE-PERFORMANCE-OPTIMIZATION-REPORT-PHASE-1-4.md)

### 问题现象

**症状描述**:
- 循环执行insert/update导致N次数据库往返
- 事务开销大，性能差
- 批量插入100条数据需要100次提交

### 根本原因

**技术原因**:
- 使用循环execute而非executemany
- 每次操作都单独提交事务
- 缺乏批量操作意识

### 解决方案

**优化前: 循环execute**
```python
# ❌ 错误：循环execute
def batch_create_parameters_old(parameters: List[dict]):
    """旧版本：循环执行"""
    for param in parameters:
        cursor.execute('''
            INSERT INTO event_params
            (event_id, name, type, value, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            param['event_id'],
            param['name'],
            param['type'],
            param['value'],
            datetime.now()
        ))
        conn.commit()  # N次提交

    return len(parameters)
```

**优化后: executemany批量执行**
```python
# ✅ 正确：executemany批量执行
def batch_create_parameters_new(parameters: List[dict]):
    """新版本：批量执行"""
    # 准备批量数据
    batch_data = [
        (
            param['event_id'],
            param['name'],
            param['type'],
            param['value'],
            datetime.now()
        )
        for param in parameters
    ]

    # 一次批量插入
    cursor.executemany('''
        INSERT INTO event_params
        (event_id, name, type, value, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', batch_data)

    conn.commit()  # 1次提交

    return len(parameters)
```

### 性能对比

**性能提升数据**:
- 旧版本：100次查询 + 100次提交
- 新版本：1次查询 + 1次提交
- 提升倍数：100x（对于100个项目）
- 数据库往返：100→1（99%减少）
- 事务开销：99%减少

### 代码审查清单

- [ ] 批量操作是否使用executemany而非循环execute？
- [ ] 事务提交次数是否从N次减少到1次？
- [ ] 是否考虑了批量大小限制（避免内存溢出）？
- [ ] 批量操作是否包含错误处理？

### 案例文档

- [性能优化Phase 1-4报告](../reports/2026-03-07/COMPLETE-PERFORMANCE-OPTIMIZATION-REPORT-PHASE-1-4.md)

---

## TTL分层设置策略 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 1次 | **来源**: [性能优化Phase 1-4](../reports/2026-03-07/COMPLETE-PERFORMANCE-OPTIMIZATION-REPORT-PHASE-1-4.md)

### 核心原则

**根据数据变化频率设置TTL**

**问题**:
- 一刀切的缓存策略导致数据不一致或性能问题
- 静态数据和动态数据使用相同TTL

### TTL分层策略

**静态数据（TTL: 1800秒 = 30分钟）**:
```python
@cached(ttl=1800, key_prefix="games.list")
def find_all(self) -> List[GameEntity]:
    """游戏列表 - 很少变化"""
    return fetch_all_as_dict("SELECT * FROM games")
```

**半静态数据（TTL: 600秒 = 10分钟）**:
```python
@cached(ttl=600, key_prefix="events.by_game")
def find_by_game(self, game_gid: int) -> List[EventEntity]:
    """事件列表 - 偶尔更新"""
    return fetch_all_as_dict("""
        SELECT * FROM log_events
        WHERE game_gid = ?
    """, (game_gid,))
```

**动态数据（TTL: 120秒 = 2分钟）**:
```python
@cached(ttl=120, key_prefix="stats.recent")
def get_recent_stats(self, hours: int = 24) -> dict:
    """统计数据 - 较频繁变化"""
    return fetch_one_as_dict("""
        SELECT
            COUNT(*) as total,
            SUM(created_at > ?) as recent
        FROM log_events
    """, (datetime.now() - timedelta(hours=hours),))
```

**实时数据（TTL: 60秒 = 1分钟）**:
```python
@cached(ttl=60, key_prefix="online.users")
def get_online_users(self) -> int:
    """在线用户 - 高频变化"""
    return fetch_one_as_dict("""
        SELECT COUNT(*) as count
        FROM user_sessions
        WHERE last_active > ?
    """, (datetime.now() - timedelta(minutes=5),))['count']
```

### TTL策略总结

| 数据类型 | TTL | 场景 | 示例 |
|---------|-----|------|------|
| 静态数据 | 1800s (30分钟) | 很少变化 | 游戏列表、分类列表、系统配置 |
| 半静态 | 600s (10分钟) | 偶尔更新 | 事件列表、参数列表、用户权限 |
| 动态 | 120s (2分钟) | 较频繁更新 | 批量查询结果、统计数据 |
| 实时 | 60s (1分钟) | 高频变化 | 在线用户、实时状态、计数器 |

### 代码审查清单

- [ ] 缓存TTL是否根据数据类型设置？
- [ ] 静态数据是否使用长TTL（30分钟）？
- [ ] 动态数据是否使用短TTL（1-2分钟）？
- [ ] 是否有TTL设置文档和标准？

### 相关经验

- [缓存策略](#缓存策略) - 缓存TTL和清理策略

### 案例文档

- [性能优化Phase 1-4报告](../reports/2026-03-07/COMPLETE-PERFORMANCE-OPTIMIZATION-REPORT-PHASE-1-4.md)

---

## Entity架构下的性能优化 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [性能优化Phase 1-4](../reports/2026-03-07/COMPLETE-PERFORMANCE-OPTIMIZATION-REPORT-PHASE-1-4.md)

### 问题现象

**症状描述**:
- Entity架构迁移后性能可能下降
- 类型检查和序列化增加开销
- 需要保持向后兼容的同时提升性能

### 解决方案

**Entity预加载和缓存**
```python
class OptimizedEntityService:
    def __init__(self):
        # 预加载Entity映射，避免运行时转换
        self._entity_cache = {}

    def find_by_gid(self, gid: int) -> Optional[GameEntity]:
        """使用缓存的Entity查找"""
        # 1. 先查缓存
        if gid in self._entity_cache:
            return self._entity_cache[gid]

        # 2. 数据库查询
        row = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (gid,))
        if not row:
            return None

        # 3. 转换为Entity（避免重复转换）
        entity = GameEntity(**row)
        self._entity_cache[gid] = entity

        return entity

    def batch_find_by_gids(self, gids: List[int]) -> List[GameEntity]:
        """批量查找Entity"""
        # 先从缓存获取
        cached_entities = []
        missing_gids = []

        for gid in gids:
            if gid in self._entity_cache:
                cached_entities.append(self._entity_cache[gid])
            else:
                missing_gids.append(gid)

        # 批量查询缺失的数据
        if missing_gids:
            rows = fetch_all_as_dict("""
                SELECT * FROM games WHERE gid IN ({})
            """.format(','.join('?'*len(missing_gids))), missing_gids)

            # 批量转换和缓存
            for row in rows:
                entity = GameEntity(**row)
                self._entity_cache[row['gid']] = entity
                cached_entities.append(entity)

        return cached_entities
```

### 性能对比

**性能数据**:
- 旧版本：每次查询都转换Entity
- 新版本：预加载Entity，避免重复转换
- 缓存命中率：>95%（gid不变的场景）
- 性能提升：2-3x（重复查询场景）

### 代码审查清单

- [ ] 是否使用了Entity预加载机制？
- [ ] 是否避免了重复的Entity转换？
- [ ] 是否利用了Entity的缓存特性？
- [ ] 是否保持了向后兼容性？

### 相关经验

- [API设计模式 - Entity架构](./api-design-patterns.md) - Entity架构设计

### 案例文档

- [性能优化Phase 1-4报告](../reports/2026-03-07/COMPLETE-PERFORMANCE-OPTIMIZATION-REPORT-PHASE-1-4.md)

---

## 并行优化策略 ⚠️ **P0极其重要 - 2026-03-05新增**

**优先级**: P0 | **出现次数**: 1次 | **来源**: [并行优化最终报告](../reports/2026-03-05/PARALLEL-OPTIMIZATION-FINAL-REPORT.md), [性能优化详细报告](../reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md)

### 问题现象

**症状描述**:
- 828个性能问题需要修复
- 串行执行需要40+小时
- 无法快速获得性能优化收益

### 根本原因

**技术原因**:
1. **缺乏并行处理机制** - 任务可以并行执行但被串行化
2. **缺少任务包设计模式** - 无法充分利用Agent并行能力
3. **无状态管理** - 无法追踪并行任务进度

### 解决方案

**1. Worker任务包设计**:

```python
# 任务包结构
{
  "worker_1_n_plus_1_p0": {
    "name": "P0 N+1 Query Fixes",
    "issues": 27,
    "priority": "P0",
    "strategy": "JOIN_PREFETCH"
  },
  "worker_2_n_plus_1_p1": {
    "name": "P1 N+1 Query Fixes",
    "issues": 503,
    "priority": "P1",
    "strategy": "BATCH_PROCESSING"
  },
  "worker_3_react": {
    "name": "React Optimization",
    "issues": 213,
    "priority": "P1",
    "strategy": "MEMO_WRAPPER"
  }
}
```

**2. 并行执行流程**:

```python
# Phase 2: 并行执行
# 1. 启动3个并行Agent
#    - Agent 1: Worker 1 (P0 N+1查询)
#    - Agent 2: Worker 2 (P1 N+1查询)
#    - Agent 3: Worker 3 (React优化)
# 2. 每个Agent独立执行，零冲突
# 3. 实时追踪进度和错误

# Phase 3: 结果汇总
# 1. 收集所有Worker结果
# 2. 合并到main分支
# 3. 生成执行报告
```

### 性能对比

| 执行方式 | 时间 | 问题处理 | 错误率 |
|---------|------|---------|--------|
| **串行执行** | 40+小时 | 828个 | 5-10% |
| **并行执行** | 13小时 | 828个 | 0% |
| **时间节省** | **67%** | - | - |

### 关键成功因素

1. **任务独立性** - Worker之间不共享状态
2. **分批处理机制** - BATCH_SIZE=50，降低风险
3. **可重复执行设计** - 自动跳过已处理文件
4. **错误隔离** - 单个文件错误不影响其他文件

### 预防措施

**代码审查清单**:
- [ ] 任务是否真正独立（无共享状态）？
- [ ] 是否有明确的依赖关系？
- [ ] 并行任务是否有冲突的文件修改？

### 相关经验

- [N+1查询优化](#n1查询优化) - N+1查询优化策略
- [批量操作优化](#批量操作优化) - 批量操作性能优化

---

## 缓存失效装饰器的自动化实现 ⚠️ **P1重要 - 2026-03-07新增**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [Dashboard实时优化报告](../reports/2026-03-07/DASHBOARD-REALTIME-OPTIMIZATION-REPORT.md), [完整性能优化报告](../reports/2026-03-07/COMPLETE-PERFORMANCE-OPTIMIZATION-REPORT-PHASE-1-4.md)

### 问题现象

**症状描述**:
- Dashboard更新延迟5分钟，缓存失效完全失效
- 新建游戏后，Dashboard仍显示旧数据
- 用户需要手动刷新才能看到最新数据

### 根本原因

**技术原因**:
1. **缓存失效机制缺失** - 修改数据后未清理缓存
2. **无自动刷新机制** - 前端依赖手动刷新
3. **缓存TTL设置过长** - 1小时TTL导致数据不新鲜

### 解决方案

**1. @cache_invalidate装饰器**:

```python
from backend.core.cache.decorators import cache_invalidate

# ✅ 写操作清理缓存
@cache_invalidate
def create_game(game_data: GameEntity) -> GameEntity:
    """创建游戏后自动清理相关缓存"""
    # 创建游戏
    game_id = self.game_repo.create(game_data)
    return self.game_repo.find_by_id(game_id)

@cache_invalidate
def update_game(game_id: int, game_data: GameEntity) -> GameEntity:
    """更新游戏后自动清理相关缓存"""
    # 更新游戏
    self.game_repo.update(game_id, game_data.model_dump())
    return self.game_repo.find_by_id(game_id)

@cache_invalidate
def delete_game(game_id: int) -> bool:
    """删除游戏后自动清理相关缓存"""
    # 删除游戏
    return self.game_repo.delete(game_id)
```

**2. 智能轮询Hook**:

```typescript
// frontend/src/hooks/useRealtimeUpdates.ts
import { useEffect, useState } from 'react';

export function useRealtimeUpdates(gameGid: number, interval: number = 10000) {
  const [data, setData] = useState(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  useEffect(() => {
    // 首次加载
    fetchData();

    // 智能轮询
    const timer = setInterval(() => {
      // 检查上次更新时间
      fetch(`/api/games/${gameGid}/last-update`)
        .then(res => res.json())
        .then(lastUpdateTimestamp => {
          const serverUpdate = new Date(lastUpdateTimestamp);

          // 如果服务器数据更新时间晚于本地，刷新数据
          if (serverUpdate > lastUpdate) {
            fetchData();
            setLastUpdate(serverUpdate);
          }
        });
    }, interval);

    return () => clearInterval(timer);
  }, [gameGid, interval]);

  return data;
}
```

### 性能对比

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| **更新延迟** | 300秒 | 10秒 | **96.7%** ↓ |
| **API调用数** | 100% | 17% | **83%** ↓ |
| **缓存命中率** | <50% | 85%+ | **70%** ↑ |
| **用户体验** | 需手动刷新 | 自动更新 | 显著提升 |

### 预防措施

**代码审查清单**:
- [ ] 所有写操作都使用`@cache_invalidate`装饰器？
- [ ] 前端是否实现智能轮询？
- [ ] 是否定期验证缓存一致性？

### 相关经验

- [缓存策略 - TTL分层设置](#缓存策略) - TTL分层策略
- [缓存策略 - 缓存清理策略](#缓存清理策略) - 缓存清理时机

---

## Dashboard实时优化 ⚠️ **P1重要 - 2026-03-07新增**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [Dashboard实时优化报告](../reports/2026-03-07/DASHBOARD-REALTIME-OPTIMIZATION-REPORT.md), [All 17组件优化完成](../reports/2026-03-07/ALL-17-COMPONENTS-OPTIMIZATION-COMPLETE.md)

### 问题现象

**症状描述**:
- Dashboard统计数据不准确
- 新建游戏后，Dashboard不显示新游戏
- 删除游戏后，Dashboard仍显示已删除游戏

### 根本原因

**技术原因**:
1. **Apollo Client缓存** - 前端Apollo Client缓存了旧数据
2. **后端缓存失效** - 后端缓存失效后前端未清理Apollo缓存
3. **缺少实时更新机制** - 前端依赖手动刷新

### 解决方案

**1. 双层缓存失效机制**:

```python
# 后端：@cache_invalidate装饰器
@cache_invalidate
def create_game(game_data: GameEntity) -> GameEntity:
    """创建游戏"""
    game_id = self.game_repo.create(game_data)
    # ✅ 后端缓存自动清理
    return self.game_repo.find_by_id(game_id)
```

```typescript
// 前端：refetchQueries清理Apollo缓存
import { useMutation, useQuery } from '@apollo/client';

export function Dashboard() {
  const { refetch } = useQuery(GET_GAMES);

  const [createGame] = useMutation(CREATE_GAME, {
    refetchQueries: true  // ✅ 自动清理Apollo缓存并重新获取
  });

  const handleCreateGame = async (gameData) => {
    await createGame({ variables: gameData });
    // ✅ Apollo自动清理缓存并重新获取数据
  };
}
```

**2. WebSocket实时更新** (高级方案):

```python
# backend/websocket/dashboard_updates.py
from flask_socketio import emit

@app.route('/api/games', methods=['POST'])
def create_game():
    game = game_service.create_game(...)

    # ✅ 通过WebSocket推送更新通知
    emit('game_created', {
        'game_gid': game.gid,
        'name': game.name
    }, room='dashboard')
```

```typescript
// 前端：监听WebSocket更新
import { useEffect } from 'react';
import { io } from 'socket.io-client';

const socket = io('http://127.0.0.1:5001');

useEffect(() => {
  // 监听游戏创建事件
  socket.on('game_created', (data) => {
    console.log('新游戏创建:', data);
    // 自动刷新Dashboard数据
    refetch();
  });

  return () => {
    socket.off('game_created');
  };
}, []);
```

### 性能对比

| 方案 | 延迟 | 复杂度 | 推荐度 |
|------|------|--------|--------|
| **refetchQueries** | 1-2秒 | 低 | ⭐⭐⭐ 简单场景 |
| **智能轮询** | 10秒轮询 | 中 | ⭐⭐⭐⭐ 平衡方案 |
| **WebSocket** | <1秒 | 高 | ⭐⭐⭐⭐ 高频更新 |

### 预防措施

**选择建议**:
- ✅ **简单场景**（低频更新）：使用refetchQueries
- ✅ **中等场景**（中频更新）：使用智能轮询
- ✅ **高频场景**（实时更新）：使用WebSocket

**代码审查清单**:
- [ ] 数据修改后是否清理了相关缓存？
- [ ] 前端是否使用了refetchQueries？
- [ ] 是否实现了智能轮询或WebSocket？

### 相关经验

- [缓存失效装饰器的自动化实现](#缓存失效装饰器的自动化实现-2026-03-07新增) - 缓存失效自动化
- [API设计模式 - GraphQL类型同步](./api-design-patterns.md#graphql类型同步规范-⚠️-p0极其重要---2026-03-09新增) - GraphQL类型同步

---

## 缓存失效诊断与修复 ⚠️ **P0极其重要 - 2026-03-13新增**

> **来源**: 4个缓存失效修复报告（2026-03-08至2026-03-13）
> **核心成果**: Systematic Debugging方法论，2分钟定位并修复3个独立根因
> **优先级**: P0

### Systematic Debugging方法论 ⭐

**核心洞察**: 缓存失效问题往往是多个独立问题叠加

**5阶段诊断流程**:
- **Phase 1**: 3个并行Subagent调查（根因分析）
- **Phase 2**: 修复设计与实施
- **Phase 3**: 代码验证
- **Phase 4**: E2E测试
- **Phase 5**: 文档更新

**成果**:
- ✅ 2分钟定位并修复3个独立根因
- ✅ 总修复时间: 80秒（P0-1: 30秒，P0-2: 30秒，P1-3: 20秒）

### 三个独立的缓存失效根因

**P0-1: 数据未保存到数据库（30秒修复）**
```python
# 问题代码
def save_config(config_id, config_data):
    # ❌ 只更新了缓存，未保存到数据库
    cache.set(f"config:{config_id}", config_data)
    return {"success": True}

# 修复代码
def save_config(config_id, config_data):
    # ✅ 先保存到数据库
    db.execute(
        "UPDATE configs SET data = ? WHERE id = ?",
        (json.dumps(config_data), config_id)
    )

    # ✅ 再更新缓存
    cache.set(f"config:{config_id}", config_data)

    return {"success": True}
```

**P0-2: 缓存键不匹配（30秒修复）**
```python
# 问题代码
@cached(ttl=1800, key_prefix="configs")
def get_stats(config_id):
    return {"count": 100}

@cache_invalidate  # ❌ 自动推断失效"configs"
def save_config(config_id, config_data):
    pass

# 问题: 实际缓存键是"event_nodes:stats:*"
# 修复: 显式指定失效键
@invalidate_cache("event_nodes:stats:*")  # ✅ 显式指定
def save_config(config_id, config_data):
    pass
```

**P1-3: SQL使用错误game_gid（20秒修复）**
```python
# 问题代码
def get_nodes(game_id):  # ❌ 使用game_id
    return fetch_all(
        "SELECT * FROM event_nodes WHERE game_id = ?",
        (game_id,)
    )

# 修复代码
def get_nodes(game_gid):  # ✅ 使用game_gid
    return fetch_all(
        "SELECT * FROM event_nodes WHERE game_gid = ?",
        (game_gid,)
    )
```

### 显式缓存失效装饰器 ⭐

**核心原则**: 避免自动推断，使用显式缓存失效

```python
# backend/core/cache/decorators.py

def invalidate_cache(*patterns):
    """
    显式缓存失效装饰器

    Args:
        *patterns: 缓存键模式（支持通配符）

    Example:
        @invalidate_cache("event_nodes:stats:*")
        @invalidate_cache("configs:*", "user:*")
        def save_config(config_id, config_data):
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 执行原函数
            result = func(*args, **kwargs)

            # 显式失效指定缓存
            for pattern in patterns:
                cache_result.delete_many(pattern)

            return result
        return wrapper
    return decorator
```

**使用示例**:
```python
from backend.core.cache.decorators import invalidate_cache

@invalidate_cache("event_nodes:stats:*")
def save_config(config_id, config_data):
    """保存配置 - 失效stats缓存"""
    pass

@invalidate_cache("event_nodes:*", "configs:*")
def update_multiple_entities(data):
    """批量更新 - 失效多个缓存"""
    pass
```

**影响函数**:
- save_config
- update_config
- delete_config
- copy_node

### 缓存失效验证最佳实践

**添加完整日志和数据库验证防止静默失败**

```python
import logging

logger = logging.getLogger(__name__)

def save_config(config_id, config_data):
    """保存配置 - 带完整验证日志"""

    # 1. 请求入口日志
    logger.info(f"[save_config] START: config_id={config_id}")

    # 2. 创建前日志
    logger.info(f"[save_config] Creating config: {config_data}")

    # 3. 执行创建
    try:
        db.execute(
            "INSERT INTO configs (id, data) VALUES (?, ?)",
            (config_id, json.dumps(config_data))
        )

        # 4. 数据库验证逻辑（关键）
        saved = db.execute(
            "SELECT * FROM configs WHERE id = ?",
            (config_id,)
        ).fetchone()

        if not saved:
            # 数据库验证失败 - 记录严重错误
            logger.error(f"[save_config] VALIDATION FAILED: config_id={config_id} not found in DB after insert")
            raise ValueError(f"Config {config_id} was not saved to database")

        logger.info(f"[save_config] VALIDATION PASSED: config_id={config_id} exists in DB")

    except Exception as e:
        # 增强的错误日志
        logger.error(f"[save_config] ERROR: config_id={config_id}, error={str(e)}", exc_info=True)
        raise

    # 5. 创建成功日志
    logger.info(f"[save_config] SUCCESS: config_id={config_id}")

    # 6. 返回前日志
    logger.info(f"[save_config] END: config_id={config_id}, returning success")

    return {"success": True, "config_id": config_id}
```

**日志完整性检查清单**:
- [ ] 请求入口日志（参数记录）
- [ ] 创建前日志（数据记录）
- [ ] 创建成功日志（确认记录）
- [ ] **数据库验证逻辑**（防止静默失败）⭐
- [ ] 返回前日志（返回值记录）
- [ ] 增强的错误日志（异常堆栈）

### 缓存失效诊断流程

**步骤1: 确认缓存状态**
```bash
# 检查Redis缓存键
redis-cli KEYS "event_nodes:*"

# 检查特定缓存值
redis-cli GET "event_nodes:stats:10000147"
```

**步骤2: 验证数据库状态**
```python
# 验证数据库记录是否存在
def verify_cache_consistency(cache_key, db_query):
    """验证缓存与数据库一致性"""
    # 从缓存读取
    cached_data = cache_result.get(cache_key)

    # 从数据库读取
    db_data = fetch_one(db_query)

    # 对比
    if cached_data != db_data:
        logger.error(f"Cache inconsistency: cache={cached_data}, db={db_data}")
        return False

    return True
```

**步骤3: 监控缓存失效**
```python
# backend/core/cache/monitoring.py

class CacheInvalidationMonitor:
    """缓存失效监控"""

    def track_invalidation(self, pattern, count):
        """记录缓存失效"""
        logger.info(f"Cache invalidation: pattern={pattern}, count={count}")
        self.metrics.record({
            'pattern': pattern,
            'count': count,
            'timestamp': datetime.now()
        })

    def verify_invalidation(self, pattern):
        """验证缓存是否已失效"""
        keys = cache_result.keys(pattern)
        if keys:
            logger.error(f"Cache not invalidated: pattern={pattern}, keys={keys}")
            return False

        logger.info(f"Cache invalidated successfully: pattern={pattern}")
        return True
```

### 相关经验

- [缓存失效装饰器的自动化实现](#缓存失效装饰器的自动化实现-2026-03-07新增) - 自动化失效
- [显式缓存失效装饰器](#显式缓存失效装饰器-⭐-2026-03-13新增) - 显式失效
- [缓存验证最佳实践](#缓存失效验证最佳实践-⭐-2026-03-13新增) - 验证方法

---

## 相关经验文档

- [数据库模式 - game_gid迁移](./database-patterns.md#game_gid迁移) - 数据库性能优化
- [API设计模式 - 分层架构](./api-design-patterns.md#分层架构) - 架构性能优化
- [API设计模式 - GraphQL实施](./api-design-patterns.md#graphql-dataloader实施) - DataLoader详细实施指南
- [API设计模式 - GraphQL类型同步规范](./api-design-patterns.md#graphql类型同步规范-⚠️-p0极其重要---2026-03-09新增) - GraphQL类型同步
- [测试指南 - TDD Red阶段经验](./testing-guide.md#tdd-red阶段经验-2026-03-09新增) - TDD实施经验

---

**文档统计**:
- P0经验点：7个
- P1经验点：6个
- 总计：13个性能优化经验点
- 最后更新：2026-03-09 🆕 新增并行优化策略、缓存失效装饰器、Dashboard实时优化

### 来自 docs/plans/2026-03-05-performance-optimization-automation.md (2026-03-18)

**关键主题**:
- Performance Optimization Automation - Implementation Plan
- Pre-requisites
- Check git status
- Check current branch
- Ensure no uncommitted changes

**重要经验**:
- print(f"✅ Saved to {output_path}")
- print(f"✅ AST analysis complete: {output_path}")
- print(f"✅ Generated task packages: {output_path}")
- print(f"   ⚠️  Skipping {file_path} (needs manual review)")
- print(f"   ❌ Error fixing {task['original_issue']['file_path']}: {e}")


### 来自 docs/lessons-learned/2026-03-07-comprehensive-optimization-experience.md (2026-03-18)

**关键主题**:
- 2026-03-07 综合性能优化经验提取
- 📊 执行摘要
- 🎯 核心经验提取
- 经验 #1: DataLoader 批量查询优化 ⭐⭐⭐
- 1. 移除 SQL 子查询，使用 DataLoader 延迟加载

**重要经验**:
- **状态**: ✅ 已完成并验证
- | **Phase 1** | N+1 查询修复 | **API 响应: 2326x** | ✅ |
- | **Phase 2** | 缓存层增强 | 缓存命中率 85%+ | ✅ |
- | **Phase 3** | 前端 React 优化 | **重渲染: 50-70% ↓** | ✅ |
- | **Phase 4** | GraphQL DataLoader | **查询数: 70-99% ↓** | ✅ |


### 来自 docs/plans/2026-03-05-performance-optimization-automation.md (2026-03-18)

**关键主题**:
- Performance Optimization Automation - Implementation Plan
- Pre-requisites
- Check git status
- Check current branch
- Ensure no uncommitted changes

**重要经验**:
- print(f"✅ Saved to {output_path}")
- print(f"✅ AST analysis complete: {output_path}")
- print(f"✅ Generated task packages: {output_path}")
- print(f"   ⚠️  Skipping {file_path} (needs manual review)")
- print(f"   ❌ Error fixing {task['original_issue']['file_path']}: {e}")


### 来自 docs/plans/2026-03-02-parallel-optimization-plan.md (2026-03-18)

**关键主题**:
- Phase 1 并行优化执行计划（方案A + 方案B）
- 📊 任务依赖分析
- 可并行执行的任务 ✅
- 有依赖的任务 ⚠️
- 🚀 并行执行计划（3个阶段）

**重要经验**:
- ### 可并行执行的任务 ✅
- | Group 1 | 分析缓存未命中原因 | 优化SELECT *查询 | ✅ 是 | 独立模块，无依赖 |
- | Group 2 | 优化缓存键策略 | 归档废弃文件 | ✅ 是 | 独立操作，无冲突 |
- | Group 3 | 调整TTL设置 | 调查剩余N+1查询 | ✅ 是 | 独立文件，无依赖 |
- | Group 4 | 缓存预热 | 最终验证 | ❌ 否 | 需要所有优化完成 |


### 来自 docs/lessons-learned/2026-03-07-comprehensive-optimization-experience.md (2026-03-18)

**关键主题**:
- 2026-03-07 综合性能优化经验提取
- 📊 执行摘要
- 🎯 核心经验提取
- 经验 #1: DataLoader 批量查询优化 ⭐⭐⭐
- 1. 移除 SQL 子查询，使用 DataLoader 延迟加载

**重要经验**:
- **状态**: ✅ 已完成并验证
- | **Phase 1** | N+1 查询修复 | **API 响应: 2326x** | ✅ |
- | **Phase 2** | 缓存层增强 | 缓存命中率 85%+ | ✅ |
- | **Phase 3** | 前端 React 优化 | **重渲染: 50-70% ↓** | ✅ |
- | **Phase 4** | GraphQL DataLoader | **查询数: 70-99% ↓** | ✅ |

