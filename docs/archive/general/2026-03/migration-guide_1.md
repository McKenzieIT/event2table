# 缓存系统迁移指南

> **面向**: 从无缓存迁移到有缓存的项目
> **目标**: 平滑、安全地引入缓存系统
> **预计时间**: 2-4小时（小型项目）| 1-2天（中型项目）| 1周（大型项目）
> **版本**: 1.0
> **最后更新**: 2026-02-27

---

## 📚 目录

1. [迁移评估](#迁移评估)
2. [迁移前准备](#迁移前准备)
3. [分步迁移流程](#分步迁移流程)
4. [迁移场景示例](#迁移场景示例)
5. [常见问题与解决方案](#常见问题与解决方案)
6. [迁移验证清单](#迁移验证清单)
7. [回滚方案](#回滚方案)
8. [性能监控与优化](#性能监控与优化)

---

## 迁移评估

### 1.1 收益评估

**在开始迁移前，先评估缓存带来的价值**：

#### 性能提升基线测试

```python
# scripts/cache/migration/baseline_test.py
"""
迁移前性能基线测试
用于对比缓存前后的性能差异
"""
import time
import statistics
from backend.core.database.converters import fetch_all_as_dict

def measure_query_performance(query: str, params: tuple, iterations: int = 100):
    """
    测量查询性能

    Args:
        query: SQL查询
        params: 查询参数
        iterations: 测试次数

    Returns:
        dict: 性能统计（平均时间、P50、P95、P99）
    """
    times = []

    for _ in range(iterations):
        start = time.perf_counter()
        result = fetch_all_as_dict(query, params)
        end = time.perf_counter()
        times.append((end - start) * 1000)  # 转换为毫秒

    return {
        "avg_ms": statistics.mean(times),
        "p50_ms": statistics.median(times),
        "p95_ms": statistics.quantiles(times, n=20)[18],  # 95th percentile
        "p99_ms": statistics.quantiles(times, n=100)[98],  # 99th percentile
        "min_ms": min(times),
        "max_ms": max(times),
    }

# 测试关键查询
def run_baseline_tests():
    """运行基线测试"""
    print("=== 缓存迁移前性能基线测试 ===\n")

    # 测试1: 游戏列表查询
    print("1. 游戏列表查询性能:")
    stats = measure_query_performance(
        "SELECT * FROM games ORDER BY name",
        (),
        iterations=50
    )
    print(f"   平均: {stats['avg_ms']:.2f}ms")
    print(f"   P95:  {stats['p95_ms']:.2f}ms")
    print(f"   P99:  {stats['p99_ms']:.2f}ms")

    # 测试2: 事件列表查询
    print("\n2. 事件列表查询性能:")
    stats = measure_query_performance(
        "SELECT * FROM log_events WHERE game_gid = ?",
        (10000147,),
        iterations=50
    )
    print(f"   平均: {stats['avg_ms']:.2f}ms")
    print(f"   P95:  {stats['p95_ms']:.2f}ms")
    print(f"   P99:  {stats['p99_ms']:.2f}ms")

    # 测试3: 参数查询
    print("\n3. 参数查询性能:")
    stats = measure_query_performance(
        """SELECT ep.* FROM event_params ep
           INNER JOIN log_events le ON ep.event_id = le.id
           WHERE le.game_gid = ?""",
        (10000147,),
        iterations=50
    )
    print(f"   平均: {stats['avg_ms']:.2f}ms")
    print(f"   P95:  {stats['p95_ms']:.2f}ms")
    print(f"   P99:  {stats['p99_ms']:.2f}ms")

    print("\n=== 基线测试完成，结果已保存 ===")

if __name__ == "__main__":
    run_baseline_tests()
```

**预期性能提升**：

| 查询类型 | 缓存前 | 缓存后（L1命中） | 缓存后（L2命中） | 提升倍数 |
|---------|--------|-----------------|-----------------|----------|
| 游戏列表 | 200ms | 1ms | 10ms | 20-200x |
| 事件列表 | 150ms | 1ms | 10ms | 15-150x |
| 参数查询 | 300ms | 1ms | 10ms | 30-300x |
| 复杂JOIN | 500ms | 1ms | 10ms | 50-500x |

### 1.2 迁移复杂度评估

**评估维度**：

| 复杂度 | 判断标准 | 预计时间 |
|--------|----------|----------|
| **简单** | • <10个查询函数<br>• 无复杂业务逻辑<br>• 无事务依赖 | 2-4小时 |
| **中等** | • 10-50个查询函数<br>• 有业务逻辑依赖<br>• 少量事务 | 1-2天 |
| **复杂** | • >50个查询函数<br>• 复杂业务逻辑<br>• 大量事务和数据一致性要求 | 1周+ |

### 1.3 风险评估

**潜在风险**：

| 风险类型 | 影响 | 概率 | 缓解措施 |
|---------|------|------|----------|
| **数据不一致** | 高 | 中 | 使用@cache_invalidate装饰器 |
| **缓存雪崩** | 高 | 低 | 添加随机TTL偏移 |
| **缓存穿透** | 中 | 低 | 使用Bloom Filter |
| **内存溢出** | 中 | 低 | 容量监控和LRU淘汰 |
| **Redis故障** | 中 | 中 | 降级到L1缓存 |

---

## 迁移前准备

### 2.1 环境检查

#### 检查清单

```bash
# 1. 检查Redis服务
redis-cli ping
# 应输出: PONG

# 2. 检查Redis版本
redis-cli INFO server | grep redis_version
# 推荐: >= 6.0

# 3. 检查Redis内存
redis-cli INFO memory | grep maxmemory
# 应配置: maxmemory 2gb

# 4. 检查Python依赖
pip list | grep redis
# 应安装: redis (>=5.0.0)

# 5. 检查缓存模块
python -c "from backend.core.cache import HierarchicalCache; print('✅ 缓存模块可用')"
```

#### 依赖安装

```bash
# 安装Redis客户端
pip install redis>=5.0.0

# 安装缓存系统依赖
pip install -r backend/requirements/cache.txt
```

### 2.2 配置准备

#### Redis配置

```bash
# redis.conf
# 最大内存限制
maxmemory 2gb

# 内存淘汰策略（LRU）
maxmemory-policy allkeys-lru

# 持久化配置（可选）
save 900 1
save 300 10
save 60 10000
```

#### 应用配置

```python
# backend/core/config/cache_config.py
"""
缓存系统配置
"""
import os

# Redis连接配置
REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)

# 缓存TTL配置
CACHE_TTL_DEFAULT = int(os.environ.get("CACHE_TTL_DEFAULT", 3600))
CACHE_TTL_SHORT = int(os.environ.get("CACHE_TTL_SHORT", 600))
CACHE_TTL_LONG = int(os.environ.get("CACHE_TTL_LONG", 7200))

# L1缓存配置
L1_CACHE_SIZE = int(os.environ.get("L1_CACHE_SIZE", 1000))
L1_CACHE_TTL = int(os.environ.get("L1_CACHE_TTL", 60))

# 缓存开关（用于紧急禁用）
CACHE_ENABLED = os.environ.get("CACHE_ENABLED", "true").lower() == "true"
```

### 2.3 备份准备

```bash
# 1. 备份数据库
cp data/dwd_generator.db data/dwd_generator.db.backup_$(date +%Y%m%d)

# 2. 备份Redis（如果已有数据）
redis-cli SAVE
cp /var/lib/redis/dump.rdb /var/lib/redis/dump.rdb.backup_$(date +%Y%m%d)

# 3. 备份当前代码
git add -A
git commit -m "backup: before cache migration"
```

---

## 分步迁移流程

### 3.1 Phase 1: 安装和配置（30分钟）

#### 步骤1: 创建缓存装饰器

```python
# backend/core/cache/decorators.py
from functools import wraps
from backend.core.cache.cache_hierarchical import HierarchicalCache
import logging

logger = logging.getLogger(__name__)

# 全局缓存实例
_cache = HierarchicalCache()

def cached(ttl: int = 3600, key_prefix: str = None):
    """
    缓存装饰器

    Args:
        ttl: 缓存生存时间（秒）
        key_prefix: 缓存键前缀（可选）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = _generate_cache_key(func, args, kwargs, key_prefix)

            # 尝试从缓存获取
            cached_data = _cache.get(cache_key)
            if cached_data is not None:
                logger.debug(f"缓存命中: {cache_key}")
                return cached_data

            # 缓存未命中，执行函数
            result = func(*args, **kwargs)

            # 写入缓存
            _cache.set(cache_key, result, ttl=ttl)
            logger.debug(f"已缓存: {cache_key}")

            return result
        return wrapper
    return decorator

def cache_invalidate(func):
    """
    缓存失效装饰器

    在数据修改后自动清理相关缓存
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

#### 步骤2: 注册缓存统计API

```python
# backend/api/routes/cache_stats.py
from flask import Blueprint, jsonify
from backend.core.cache.cache_hierarchical import hierarchical_cache

cache_stats_bp = Blueprint('cache_stats', __name__)

@cache_stats_bp.route('/api/cache/stats', methods=['GET'])
def get_cache_stats():
    """获取缓存统计信息"""
    stats = hierarchical_cache.stats
    total_requests = stats['l1_hits'] + stats['l2_hits'] + stats['misses']
    hit_rate = (stats['l1_hits'] + stats['l2_hits']) / total_requests if total_requests > 0 else 0

    return jsonify({
        "l1_hits": stats['l1_hits'],
        "l2_hits": stats['l2_hits'],
        "misses": stats['misses'],
        "hit_rate": round(hit_rate, 3),
        "total_requests": total_requests,
        "l1_evictions": stats.get('l1_evictions', 0)
    })

# 在backend/api/__init__.py中注册
from backend.api.routes import cache_stats
app.register_blueprint(cache_stats.cache_stats_bp)
```

### 3.2 Phase 2: 逐步迁移查询函数（2-8小时）

#### 迁移策略

**优先级排序**：
1. ✅ **P0 - 高频查询**（每秒>10次）→ 最大性能收益
2. ✅ **P1 - 慢查询**（>100ms）→ 显著改善用户体验
3. ✅ **P2 - 中频查询**（每分钟1-10次）→ 降低数据库负载
4. ⏭️ **P3 - 低频查询**（每小时<1次）→ 可选迁移

#### 迁移步骤

**步骤1: 识别待迁移函数**

```python
# scripts/cache/migration/identify_queries.py
"""
识别待迁移的查询函数
"""
import re
from pathlib import Path

def find_query_functions():
    """扫描代码，找到所有查询函数"""
    backend_dir = Path("backend")

    query_patterns = [
        r"fetch_one_as_dict",
        r"fetch_all_as_dict",
        r"execute_query",
    ]

    query_functions = []

    for py_file in backend_dir.rglob("*.py"):
        content = py_file.read_text()
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            for pattern in query_patterns:
                if re.search(pattern, line):
                    # 提取函数名
                    func_def = None
                    for j in range(max(0, i-20), i):
                        if re.search(r"def\s+(\w+)\s*\(", lines[j]):
                            func_def = lines[j]
                            break

                    if func_def:
                        func_name = re.search(r"def\s+(\w+)", func_def).group(1)
                        query_functions.append({
                            "file": str(py_file),
                            "line": i,
                            "function": func_name,
                            "pattern": pattern
                        })

    # 按文件分组
    grouped = {}
    for item in query_functions:
        file_path = item['file']
        if file_path not in grouped:
            grouped[file_path] = []
        grouped[file_path].append(item)

    print("=== 待迁移的查询函数 ===\n")
    for file_path, items in sorted(grouped.items()):
        print(f"\n{file_path}:")
        for item in items:
            print(f"  - Line {item['line']}: {item['function']} ({item['pattern']})")

    return grouped

if __name__ == "__main__":
    find_query_functions()
```

**步骤2: 迁移单个查询函数**

```python
# backend/models/repositories/games.py

# ❌ 迁移前
def get_all_games():
    """获取所有游戏"""
    return fetch_all_as_dict('SELECT * FROM games ORDER BY name')

# ✅ 迁移后
from backend.core.cache.decorators import cached

@cached(ttl=3600)  # 缓存1小时
def get_all_games():
    """获取所有游戏"""
    return fetch_all_as_dict('SELECT * FROM games ORDER BY name')
```

**步骤3: 迁移参数化查询**

```python
# backend/models/repositories/events.py

# ❌ 迁移前
def get_events_by_game(game_gid: int):
    """获取游戏的所有事件"""
    return fetch_all_as_dict(
        'SELECT * FROM log_events WHERE game_gid = ?',
        (game_gid,)
    )

# ✅ 迁移后（自动参数化缓存键）
from backend.core.cache.decorators import cached

@cached(ttl=1800)  # 缓存30分钟
def get_events_by_game(game_gid: int):
    """获取游戏的所有事件"""
    return fetch_all_as_dict(
        'SELECT * FROM log_events WHERE game_gid = ?',
        (game_gid,)
    )

# 不同game_gid会自动生成不同的缓存键
# get_events_by_game(10000147) → cache:events:10000147
# get_events_by_game(10000148) → cache:events:10000148
```

**步骤4: 迁移复杂查询**

```python
# backend/services/events/event_service.py

# ❌ 迁移前
def get_events_with_params(game_gid: int):
    """获取事件及其参数（复杂JOIN）"""
    events = fetch_all_as_dict(
        'SELECT * FROM log_events WHERE game_gid = ?',
        (game_gid,)
    )

    for event in events:
        event['params'] = fetch_all_as_dict(
            'SELECT * FROM event_params WHERE event_id = ?',
            (event['id'],)
        )

    return events

# ✅ 迁移后（使用更短的TTL，因为数据可能变化）
from backend.core.cache.decorators import cached

@cached(ttl=600)  # 缓存10分钟
def get_events_with_params(game_gid: int):
    """获取事件及其参数"""
    # 相同实现，但添加了缓存
    events = fetch_all_as_dict(
        'SELECT * FROM log_events WHERE game_gid = ?',
        (game_gid,)
    )

    for event in events:
        event['params'] = fetch_all_as_dict(
            'SELECT * FROM event_params WHERE event_id = ?',
            (event['id'],)
        )

    return events
```

### 3.3 Phase 3: 添加缓存失效（1-3小时）

#### 识别写操作

```python
# backend/api/routes/games.py

# ❌ 迁移前：更新游戏后缓存未清理
def update_game(game_id: int, data: dict):
    """更新游戏"""
    execute_update(
        'UPDATE games SET name = ?, ods_db = ? WHERE id = ?',
        (data['name'], data['ods_db'], game_id)
    )
    # ⚠️ 缓存未清理，导致数据不一致

# ✅ 迁移后：使用@cache_invalidate
from backend.core.cache.decorators import cache_invalidate

@cache_invalidate
def update_game(game_id: int, data: dict):
    """更新游戏"""
    execute_update(
        'UPDATE games SET name = ?, ods_db = ? WHERE id = ?',
        (data['name'], data['ods_db'], game_id)
    )
    # ✅ 装饰器自动清理相关缓存
```

#### 批量操作失效

```python
# backend/api/routes/events.py

# ❌ 迁移前
def batch_delete_events(event_ids: list[int]):
    """批量删除事件"""
    for event_id in event_ids:
        execute_update('DELETE FROM log_events WHERE id = ?', (event_id,))
    # ⚠️ 缓存未清理

# ✅ 迁移后
from backend.core.cache.decorators import cache_invalidate

@cache_invalidate
def batch_delete_events(event_ids: list[int]):
    """批量删除事件"""
    for event_id in event_ids:
        execute_update('DELETE FROM log_events WHERE id = ?', (event_id,))
    # ✅ 自动清理所有相关缓存
```

### 3.4 Phase 4: 测试和验证（1-2小时）

```python
# tests/test_cache_migration.py
"""
缓存迁移测试
"""
import pytest
from backend.core.cache import cache_hierarchical
from backend.models.repositories.games import get_all_games

@pytest.fixture(autouse=True)
def clear_cache_before_each_test():
    """每个测试前清理缓存"""
    cache_hierarchical.hierarchical_cache.flush_all()
    yield
    cache_hierarchical.hierarchical_cache.flush_all()

def test_cache_hit_on_second_call():
    """测试第二次调用命中缓存"""
    # 第一次调用（缓存未命中）
    games1 = get_all_games()
    assert cache_hierarchical.hierarchical_cache.stats['misses'] > 0

    # 第二次调用（缓存命中）
    games2 = get_all_games()
    assert cache_hierarchical.hierarchical_cache.stats['l1_hits'] > 0 or \
           cache_hierarchical.hierarchical_cache.stats['l2_hits'] > 0

    # 数据一致性
    assert games1 == games2

def test_cache_invalidation():
    """测试缓存失效"""
    from backend.models.repositories.games import update_game
    from backend.core.database.converters import fetch_one_as_dict

    # 第一次查询
    games1 = get_all_games()
    initial_count = len(games1)

    # 更新游戏
    game = fetch_one_as_dict('SELECT * FROM games LIMIT 1')
    update_game(game['id'], {'name': 'Updated Name', 'ods_db': game['ods_db']})

    # 第二次查询，应该返回最新数据
    games2 = get_all_games()
    assert len(games2) == initial_count  # 数量一致
    updated_game = [g for g in games2 if g['id'] == game['id']][0]
    assert updated_game['name'] == 'Updated Name'  # 数据已更新
```

---

## 迁移场景示例

### 4.1 场景1: 简单查询迁移

**场景**: 游戏列表查询
**复杂度**: 简单
**预计时间**: 5分钟

#### 迁移前

```python
# backend/models/repositories/games.py
from backend.core.database.converters import fetch_all_as_dict

def get_all_games():
    """获取所有游戏"""
    return fetch_all_as_dict('SELECT * FROM games ORDER BY name')
```

#### 迁移后

```python
# backend/models/repositories/games.py
from backend.core.database.converters import fetch_all_as_dict
from backend.core.cache.decorators import cached

@cached(ttl=3600)  # 缓存1小时
def get_all_games():
    """获取所有游戏"""
    return fetch_all_as_dict('SELECT * FROM games ORDER BY name')
```

#### 验证

```bash
# 第一次请求（缓存未命中）
curl -i http://127.0.0.1:5001/api/games
# X-Cache-Status: MISS

# 第二次请求（缓存命中）
curl -i http://127.0.0.1:5001/api/games
# X-Cache-Status: HIT

# 查看缓存统计
curl http://127.0.0.1:5001/api/cache/stats
{
  "l1_hits": 1,
  "l2_hits": 0,
  "misses": 1,
  "hit_rate": 0.5
}
```

### 4.2 场景2: 复杂业务逻辑迁移

**场景**: 获取游戏详情（含事件和参数统计）
**复杂度**: 中等
**预计时间**: 30分钟

#### 迁移前

```python
# backend/services/games/game_service.py
class GameService:
    def get_game_detail(self, game_gid: int) -> dict:
        """获取游戏详情（含统计信息）"""
        # 查询游戏基础信息
        game = fetch_one_as_dict(
            'SELECT * FROM games WHERE gid = ?',
            (game_gid,)
        )

        # 统计事件数量
        event_count = fetch_one_as_dict(
            'SELECT COUNT(*) as count FROM log_events WHERE game_gid = ?',
            (game_gid,)
        )['count']

        # 统计参数数量
        param_count = fetch_one_as_dict(
            '''SELECT COUNT(*) as count FROM event_params ep
               INNER JOIN log_events le ON ep.event_id = le.id
               WHERE le.game_gid = ?''',
            (game_gid,)
        )['count']

        # 组装结果
        return {
            **game,
            'event_count': event_count,
            'param_count': param_count
        }
```

#### 迁移后

```python
# backend/services/games/game_service.py
from backend.core.cache.decorators import cached

class GameService:
    @cached(ttl=1800)  # 缓存30分钟
    def get_game_detail(self, game_gid: int) -> dict:
        """获取游戏详情（含统计信息）"""
        # 相同的实现逻辑
        game = fetch_one_as_dict(
            'SELECT * FROM games WHERE gid = ?',
            (game_gid,)
        )

        event_count = fetch_one_as_dict(
            'SELECT COUNT(*) as count FROM log_events WHERE game_gid = ?',
            (game_gid,)
        )['count']

        param_count = fetch_one_as_dict(
            '''SELECT COUNT(*) as count FROM event_params ep
               INNER JOIN log_events le ON ep.event_id = le.id
               WHERE le.game_gid = ?''',
            (game_gid,)
        )['count']

        return {
            **game,
            'event_count': event_count,
            'param_count': param_count
        }

    @cache_invalidate
    def update_game(self, game_gid: int, data: dict):
        """更新游戏（自动清理缓存）"""
        execute_update(
            'UPDATE games SET name = ?, ods_db = ? WHERE gid = ?',
            (data['name'], data['ods_db'], game_gid)
        )
```

#### 优化版本（减少缓存对象大小）

```python
# backend/services/games/game_service.py
from backend.core.cache.decorators import cached

class GameService:
    @cached(ttl=1800)  # 缓存游戏基础信息
    def get_game_info(self, game_gid: int) -> dict:
        """获取游戏基础信息"""
        return fetch_one_as_dict(
            'SELECT * FROM games WHERE gid = ?',
            (game_gid,)
        )

    @cached(ttl=300)  # 缓存统计数据（5分钟，更频繁变化）
    def get_game_stats(self, game_gid: int) -> dict:
        """获取游戏统计"""
        event_count = fetch_one_as_dict(
            'SELECT COUNT(*) as count FROM log_events WHERE game_gid = ?',
            (game_gid,)
        )['count']

        param_count = fetch_one_as_dict(
            '''SELECT COUNT(*) as count FROM event_params ep
               INNER JOIN log_events le ON ep.event_id = le.id
               WHERE le.game_gid = ?''',
            (game_gid,)
        )['count']

        return {
            'event_count': event_count,
            'param_count': param_count
        }

    def get_game_detail(self, game_gid: int) -> dict:
        """获取游戏详情（组装缓存）"""
        # 从两个缓存获取数据
        game_info = self.get_game_info(game_gid)
        game_stats = self.get_game_stats(game_gid)

        return {
            **game_info,
            **game_stats
        }
```

### 4.3 场景3: 批量操作迁移

**场景**: 批量删除事件
**复杂度**: 复杂
**预计时间**: 1小时

#### 迁移前

```python
# backend/api/routes/events.py
def batch_delete_events(event_ids: list[int]):
    """批量删除事件"""
    deleted_count = 0

    for event_id in event_ids:
        # 删除事件参数
        execute_update('DELETE FROM event_params WHERE event_id = ?', (event_id,))

        # 删除事件
        execute_update('DELETE FROM log_events WHERE id = ?', (event_id,))

        deleted_count += 1

    return {
        "success": True,
        "deleted_count": deleted_count
    }
```

#### 迁移后

```python
# backend/api/routes/events.py
from backend.core.cache.decorators import cache_invalidate

@cache_invalidate
def batch_delete_events(event_ids: list[int]):
    """批量删除事件（自动清理缓存）"""
    deleted_count = 0

    for event_id in event_ids:
        # 删除事件参数
        execute_update('DELETE FROM event_params WHERE event_id = ?', (event_id,))

        # 删除事件
        execute_update('DELETE FROM log_events WHERE id = ?', (event_id,))

        deleted_count += 1

    return {
        "success": True,
        "deleted_count": deleted_count
    }

# ✅ 装饰器会自动清理所有相关缓存
# - events:{game_gid}:list
# - event:{event_id}:detail
# - params:{event_id}:list
```

#### 高级版本（精确缓存失效）

```python
# backend/api/routes/events.py
from backend.core.cache import HierarchicalCache

cache = HierarchicalCache()

def batch_delete_events(event_ids: list[int]):
    """批量删除事件（精确缓存失效）"""
    deleted_count = 0
    affected_game_gids = set()

    for event_id in event_ids:
        # 获取事件信息（用于缓存失效）
        event = fetch_one_as_dict(
            'SELECT game_gid FROM log_events WHERE id = ?',
            (event_id,)
        )

        if event:
            affected_game_gids.add(event['game_gid'])

        # 删除事件参数
        execute_update('DELETE FROM event_params WHERE event_id = ?', (event_id,))

        # 删除事件
        execute_update('DELETE FROM log_events WHERE id = ?', (event_id,))

        # 清理特定事件的缓存
        cache.delete(f"event:{event_id}")

        deleted_count += 1

    # 清理受影响游戏的列表缓存
    for game_gid in affected_game_gids:
        cache.delete(f"events:{game_gid}:list")
        cache.delete_pattern(f"events:{game_gid}:*")

    return {
        "success": True,
        "deleted_count": deleted_count
    }
```

---

## 常见问题与解决方案

### 5.1 问题1: 数据不一致

**症状**: 更新数据后，API仍返回旧数据

**根本原因**: 更新操作后未清理缓存

**解决方案**:

```python
# ❌ 错误: 更新后未清理缓存
def update_event(event_id: int, data: dict):
    execute_update('UPDATE log_events SET name = ? WHERE id = ?', (data['name'], event_id))
    # 缓存未清理

# ✅ 正确: 使用@cache_invalidate
from backend.core.cache.decorators import cache_invalidate

@cache_invalidate
def update_event(event_id: int, data: dict):
    execute_update('UPDATE log_events SET name = ? WHERE id = ?', (data['name'], event_id))
    # 装饰器自动清理相关缓存
```

### 5.2 问题2: 缓存雪崩

**症状**: 大量缓存同时过期，导致数据库压力激增

**根本原因**: 所有缓存使用相同的TTL

**解决方案**: 添加随机TTL偏移

```python
import random

@cached(ttl=3600 + random.randint(0, 300))  # 3600-3900秒
def get_events(game_gid: int):
    """添加随机偏移，防止同时过期"""
    return fetch_all_as_dict('SELECT * FROM log_events WHERE game_gid = ?', (game_gid,))
```

### 5.3 问题3: 缓存穿透

**症状**: 查询不存在的数据，每次都查询数据库

**根本原因**: 缓存不存储NULL值

**解决方案**: 使用Bloom Filter

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

### 5.4 问题4: 缓存占用内存过大

**症状**: Redis内存使用超过限制

**根本原因**: 缓存了大对象或过多数据

**解决方案**:

**方案1: 分页缓存**

```python
# ❌ 错误: 缓存整个大表
@cached(ttl=3600)
def get_all_logs():
    return fetch_all_as_dict('SELECT * FROM logs')  # 可能有百万行

# ✅ 正确: 分页缓存
@cached(ttl=600, key_prefix="logs:page")
def get_logs_page(page: int, size: int = 100):
    return fetch_all_as_dict(
        'SELECT * FROM logs LIMIT ? OFFSET ?',
        (size, page * size)
    )
```

**方案2: 使用更短的TTL**

```python
@cached(ttl=300)  # 5分钟
def get_large_dataset():
    """大对象使用短TTL"""
    return fetch_all_as_dict('SELECT * FROM large_table')
```

**方案3: 仅缓存关键数据**

```python
@cached(ttl=3600)
def get_game_list():
    """仅缓存游戏列表（不含详细信息）"""
    return fetch_all_as_dict('SELECT gid, name FROM games')  # 只选需要的列
```

---

## 迁移验证清单

### 6.1 功能验证

- [ ] **缓存命中验证**
  - [ ] 第二次调用返回缓存数据
  - [ ] HTTP响应头包含 `X-Cache-Status: HIT`
  - [ ] 缓存统计显示命中率 > 0

- [ ] **数据一致性验证**
  - [ ] 更新数据后，API返回最新数据
  - [ ] 删除数据后，API返回空结果
  - [ ] 创建数据后，API包含新数据

- [ ] **缓存失效验证**
  - [ ] 写操作后缓存被清理
  - [ ] 相关查询返回最新数据
  - [ ] 缓存统计显示misses增加

### 6.2 性能验证

```python
# tests/test_cache_performance.py
"""
缓存性能测试
"""
import time
import statistics
from backend.models.repositories.games import get_all_games
from backend.core.cache import cache_hierarchical

def test_performance_improvement():
    """测试缓存带来的性能提升"""
    iterations = 100

    # 清理缓存
    cache_hierarchical.hierarchical_cache.flush_all()

    # 测试缓存未命中性能
    times_miss = []
    for _ in range(iterations):
        start = time.perf_counter()
        get_all_games()
        end = time.perf_counter()
        times_miss.append((end - start) * 1000)

    # 测试缓存命中性能
    times_hit = []
    for _ in range(iterations):
        start = time.perf_counter()
        get_all_games()
        end = time.perf_counter()
        times_hit.append((end - start) * 1000)

    avg_miss = statistics.mean(times_miss)
    avg_hit = statistics.mean(times_hit)

    print(f"缓存未命中平均时间: {avg_miss:.2f}ms")
    print(f"缓存命中平均时间: {avg_hit:.2f}ms")
    print(f"性能提升倍数: {avg_miss / avg_hit:.1f}x")

    # 断言性能提升至少10倍
    assert avg_miss / avg_hit > 10, f"性能提升不足: {avg_miss / avg_hit:.1f}x"
```

### 6.3 压力测试

```bash
# 使用Apache Bench进行压力测试

# 测试缓存前性能
ab -n 1000 -c 10 http://127.0.0.1:5001/api/games
# 记录: Requests per second (平均)

# 清理缓存
redis-cli FLUSHALL

# 测试缓存后性能
ab -n 1000 -c 10 http://127.0.0.1:5001/api/games
# 对比: Requests per second 应该提升2-5倍
```

---

## 回滚方案

### 7.1 紧急禁用缓存

```python
# backend/core/config/cache_config.py
# 设置环境变量
CACHE_ENABLED = False  # 紧急禁用缓存

# 装饰器会检查此变量
def cached(ttl: int = 3600, key_prefix: str = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 检查缓存开关
            if not CACHE_ENABLED:
                return func(*args, **kwargs)

            # 正常缓存逻辑...
        return wrapper
    return decorator
```

### 7.2 清理所有缓存

```bash
# 清理Redis所有缓存
redis-cli FLUSHALL

# 清理特定前缀的缓存
redis-cli --scan --pattern "cache:*" | xargs redis-cli DEL
```

### 7.3 回滚代码

```bash
# 回滚到迁移前的commit
git log --oneline | grep "backup: before cache migration"
git checkout <commit-hash>

# 或使用git revert
git revert HEAD~1  # 回滚最后一次提交
```

---

## 性能监控与优化

### 8.1 缓存命中率监控

```python
# backend/api/routes/cache_monitoring.py
from flask import Blueprint, jsonify
from backend.core.cache import cache_hierarchical

monitoring_bp = Blueprint('cache_monitoring', __name__)

@monitoring_bp.route('/api/cache/health', methods=['GET'])
def cache_health_check():
    """缓存健康检查"""
    stats = cache_hierarchical.hierarchical_cache.stats
    total_requests = stats['l1_hits'] + stats['l2_hits'] + stats['misses']
    hit_rate = (stats['l1_hits'] + stats['l2_hits']) / total_requests if total_requests > 0 else 0

    # 健康评估
    if hit_rate >= 0.8:
        status = "healthy"
        message = "缓存命中率良好"
    elif hit_rate >= 0.5:
        status = "warning"
        message = "缓存命中率偏低，建议检查TTL配置"
    else:
        status = "critical"
        message = "缓存命中率过低，建议检查缓存策略"

    return jsonify({
        "status": status,
        "message": message,
        "hit_rate": round(hit_rate, 3),
        "stats": stats
    })
```

### 8.2 慢查询日志

```python
# backend/core/cache/performance_logger.py
import time
import logging

logger = logging.getLogger(__name__)

def log_slow_queries_threshold_ms: int = 100):
    """
    记录慢查询日志

    Args:
        threshold_ms: 慢查询阈值（毫秒）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration = (time.perf_counter() - start) * 1000

            if duration > threshold_ms:
                logger.warning(
                    f"慢查询检测: {func.__name__} "
                    f"耗时 {duration:.2f}ms > {threshold_ms}ms"
                )

            return result
        return wrapper
    return decorator
```

### 8.3 持续优化

**优化周期**:

| 频率 | 任务 |
|------|------|
| **每日** | 检查缓存命中率、慢查询日志 |
| **每周** | 分析缓存统计，调整TTL |
| **每月** | 清理低价值缓存，优化缓存键设计 |

**优化指标**:

```python
# scripts/cache/migration/analyze_cache_stats.py
"""
缓存统计分析
"""

def analyze_cache_stats():
    """分析缓存统计，提供优化建议"""
    stats = hierarchical_cache.stats
    total_requests = stats['l1_hits'] + stats['l2_hits'] + stats['misses']
    hit_rate = (stats['l1_hits'] + stats['l2_hits']) / total_requests if total_requests > 0 else 0

    print("=== 缓存统计分析 ===\n")
    print(f"总请求数: {total_requests}")
    print(f"L1命中: {stats['l1_hits']} ({stats['l1_hits']/total_requests*100:.1f}%)")
    print(f"L2命中: {stats['l2_hits']} ({stats['l2_hits']/total_requests*100:.1f}%)")
    print(f"未命中: {stats['misses']} ({stats['misses']/total_requests*100:.1f}%)")
    print(f"总体命中率: {hit_rate*100:.1f}%\n")

    # 优化建议
    if hit_rate < 0.5:
        print("⚠️ 命中率过低，建议:")
        print("  1. 检查TTL配置是否过短")
        print("  2. 检查缓存键是否冲突")
        print("  3. 检查是否频繁清理缓存")
    elif hit_rate < 0.8:
        print("⚠️ 命中率中等，建议:")
        print("  1. 分析未命中的查询模式")
        print("  2. 考虑预热常用数据")
    else:
        print("✅ 命中率良好，建议:")
        print("  1. 监控L1命中率")
        print("  2. 考虑增加L1缓存大小")

    # L1淘汰率
    if stats.get('l1_evictions', 0) > 1000:
        print(f"\n⚠️ L1淘汰次数过多: {stats['l1_evictions']}")
        print("  建议: 增加L1缓存大小")

if __name__ == "__main__":
    analyze_cache_stats()
```

---

## 📚 相关文档

- [5分钟快速开始指南](../quickstart/5-minute-guide.md) - 快速上手
- [开发者指南](./developer-guide.md) - 深入了解架构
- [故障排除手册](../operations/troubleshooting.md) - 解决常见问题
- [部署运维文档](../operations/deployment.md) - 生产环境配置
- [常见问题FAQ](../quickstart/faq.md) - 10个最常见问题

---

**文档版本**: 1.0
**最后更新**: 2026-02-27
**作者**: Event2Table Development Team
**反馈**: 如有问题，请在项目Issues中提出
