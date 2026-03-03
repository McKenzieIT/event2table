# 部署与运维

> **来源**: 整合了多个报告的部署运维相关经验
> **最后更新**: 2026-03-02
> **维护**: 每次部署运维问题修复后立即更新

---

## 缓存预热策略 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 1次 | **来源**: [CACHE-COVERAGE-PHASE-4.4-IMPLEMENTATION.md](../../reports/2026-03-01/CACHE-COVERAGE-PHASE-4.4-IMPLEMENTATION.md)

### 核心原则

**生产环境缓存预热可以避免冷启动性能问题**

### 预热时机

**1. 服务启动时**:
```python
# backend/app.py
@app.before_first_request
def warm_up_cache():
    """服务启动时预热缓存"""
    from backend.services.games.game_service import GameService
    from backend.services.events.event_service import EventService

    game_service = GameService()
    event_service = EventService()

    # 预热游戏列表
    games = game_service.get_all()
    logger.info(f"Warmed up {len(games)} games")

    # 预热事件列表（最近100个）
    recent_events = event_service.get_recent_events(limit=100)
    logger.info(f"Warmed up {len(recent_events)} events")
```

**2. 低峰期预热**:
```python
# scripts/warmup_cache.py
def schedule_warmup():
    """在低峰期预热缓存"""
    import schedule

    def warmup_job():
        logger.info("Starting scheduled cache warmup...")
        warm_up_cache()
        logger.info("Cache warmup completed")

    # 每天凌晨2点预热
    schedule.every().day.at("02:00").do(warmup_job)

    while True:
        schedule.run_pending()
        time.sleep(60)
```

**3. 数据更新后预热**:
```python
# backend/api/routes/games.py
@games_bp.route('/api/games/<int:game_gid>', methods=['PUT'])
def update_game(game_gid):
    # ... 更新逻辑 ...

    # ✅ 数据更新后预热缓存
    game = game_service.get_by_gid(game_gid)
    logger.info(f"Warmed up cache for game {game_gid}")

    return json_success_response(data=game)
```

### 预热策略

**静态数据 - 完整预热**:
```python
def warm_up_static_cache():
    """预热静态数据（配置、枚举等）"""
    # 系统配置
    config = get_system_config()

    # 枚举值
    event_types = get_event_types()
    param_types = get_param_types()

    logger.info("Static data warmed up")
```

**热点数据 - 分批次预热**:
```python
def warm_up_hot_cache():
    """预热热点数据（分批次）"""
    batch_size = 100

    # 分批次预热游戏
    games = get_all_games()
    for i in range(0, len(games), batch_size):
        batch = games[i:i+batch_size]
        for game in batch:
            cache.set(f"game:{game['gid']}", game, timeout=300)
        logger.info(f"Warmed up games {i}-{i+batch_size}")
```

**大数据集 - 分页预热**:
```python
def warm_up_large_dataset():
    """预热大数据集（分页）"""
    page = 1
    per_page = 1000

    while True:
        events = get_events_paginated(page, per_page)
        if not events:
            break

        # 预热当前页
        cache.set(f"events:page:{page}", events, timeout=120)

        page += 1
        if page > 10:  # 只预热前10页
            break
```

### 代码审查清单

- [ ] 服务启动时是否预热关键缓存？
- [ ] 是否有低峰期预热计划？
- [ ] 数据更新后是否预热相关缓存？
- [ ] 大数据集是否使用分页预热？

### 案例文档

- [缓存覆盖率Phase 4.4实施](../../reports/2026-03-01/CACHE-COVERAGE-PHASE-4.4-IMPLEMENTATION.md)

---

## 环境隔离配置 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 多次 | **来源**: [CLAUDE.md](../../CLAUDE.md), 多个测试报告

### 三环境隔离

**环境定义**:
```python
# backend/core/config/config.py
import os

class Config:
    """配置基类"""

    @staticmethod
    def get_db_path():
        """根据环境返回正确的数据库路径"""
        if os.environ.get("FLASK_ENV") == "testing":
            return TEST_DB_PATH  # data/test_database.db
        if os.environ.get("FLASK_ENV") == "development":
            return DEV_DB_PATH   # data/dwd_generator_dev.db
        return DB_PATH          # data/dwd_generator.db

    @staticmethod
    def get_redis_config():
        """根据环境返回Redis配置"""
        if os.environ.get("FLASK_ENV") == "testing":
            return {"host": "localhost", "port": 6379, "db": 15}  # 测试数据库
        if os.environ.get("FLASK_ENV") == "development":
            return {"host": "localhost", "port": 6379, "db": 1}   # 开发数据库
        return {"host": "localhost", "port": 6379, "db": 0}      # 生产数据库
```

### 环境变量

**.env 文件**:
```bash
# .env.production
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=your-production-secret-key

# .env.development
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key

# .env.testing
FLASK_ENV=testing
FLASK_DEBUG=0
SECRET_KEY=test-secret-key
```

### pytest fixture配置

**测试数据库隔离**:
```python
# backend/tests/conftest.py
import pytest
from backend.core.config.config import TEST_DB_PATH, get_db_connection
from backend.core.database.init_db import init_db

@pytest.fixture(scope="session")
def db():
    """
    使用独立的测试数据库进行测试
    测试前清理，测试后保留以便调试
    """
    # 删除旧测试数据库（如果存在）
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    # 初始化测试数据库
    init_db(TEST_DB_PATH)

    # 提供测试数据库连接
    conn = get_db_connection(TEST_DB_PATH)
    yield conn
    conn.close()
```

### 代码审查清单

- [ ] 是否使用环境变量区分环境？
- [ ] 是否每个环境有独立的数据库？
- [ ] 是否每个环境有独立的Redis数据库？
- [ ] 测试是否使用独立的测试数据库？

---

## 监控指标设置 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: 缓存优化报告

### 关键监控指标

**1. 缓存命中率**:
```python
def get_cache_stats():
    """获取缓存统计"""
    stats = cache_manager.get_stats()
    return {
        "hit_rate": stats["hits"] / (stats["hits"] + stats["misses"]),
        "hits": stats["hits"],
        "misses": stats["misses"],
        "total_keys": stats["keys"]
    }

# 目标：缓存命中率 >85%
```

**2. API响应时间**:
```python
import time
from functools import wraps

def monitor_response_time(func):
    """监控API响应时间"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start

        # 记录响应时间
        logger.info(f"{func.__name__} executed in {duration:.3f}s")

        # 响应时间告警
        if duration > 1.0:
            logger.warning(f"{func.__name__} is slow: {duration:.3f}s")

        return result
    return wrapper

# 目标：95%的API响应时间 <500ms
```

**3. 数据库查询性能**:
```python
def log_slow_queries(query, params, duration):
    """记录慢查询"""
    if duration > 0.5:  # 慢查询阈值：500ms
        logger.warning(
            f"Slow query detected: {duration:.3f}s\n"
            f"Query: {query}\n"
            f"Params: {params}"
        )

# 目标：慢查询率 <5%
```

**4. 错误率**:
```python
def track_errors():
    """追踪错误率"""
    errors = get_error_stats()
    total_requests = get_request_stats()

    error_rate = errors["total"] / total_requests["total"]

    # 错误率告警
    if error_rate > 0.01:  # 1%错误率阈值
        logger.error(f"High error rate detected: {error_rate:.2%}")

    return {"error_rate": error_rate}

# 目标：错误率 <1%
```

### 监控Dashboard

```python
# backend/api/routes/monitoring.py
@monitoring_bp.route('/api/monitoring/stats')
def get_monitoring_stats():
    """获取监控统计"""
    return json_success_response({
        "cache": get_cache_stats(),
        "api": get_api_stats(),
        "database": get_database_stats(),
        "errors": get_error_stats(),
        "timestamp": datetime.now().isoformat()
    })
```

### 代码审查清单

- [ ] 是否监控缓存命中率？
- [ ] 是否监控API响应时间？
- [ ] 是否记录慢查询？
- [ ] 是否追踪错误率？
- [ ] 是否有监控Dashboard？

---

## 故障排查流程 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 多次 | **来源**: 多个故障报告

### 标准排查流程

**1. 确认问题**:
```bash
# 检查服务状态
curl http://127.0.0.1:5001/api/health

# 检查日志
tail -f logs/app.log
```

**2. 收集信息**:
```bash
# 系统资源
top
htop

# 数据库连接
lsof -i :5001

# 缓存状态
redis-cli INFO stats
```

**3. 定位问题**:
```bash
# 查看错误日志
grep ERROR logs/app.log | tail -100

# 查看慢查询
grep "Slow query" logs/app.log | tail -100

# 查看缓存命中率
grep "Cache" logs/app.log | tail -100
```

**4. 解决问题**:
- 根据日志定位具体问题
- 查看经验文档找到解决方案
- 应用修复方案
- 验证问题解决

**5. 记录经验**:
- 更新相关经验文档
- 记录问题和解决方案
- 分享给团队成员

### 常见问题诊断

**问题1: API响应慢**
```bash
# 检查缓存命中率
curl http://127.0.0.1:5001/api/cache/stats

# 检查慢查询日志
grep "Slow query" logs/app.log

# 解决方案：
# 1. 预热缓存
# 2. 优化慢查询
# 3. 添加数据库索引
```

**问题2: 数据不一致**
```bash
# 检查缓存一致性
python scripts/verify_cache_consistency.py

# 解决方案：
# 1. 清理缓存
redis-cli FLUSHALL
# 2. 重新预热缓存
python scripts/warmup_cache.py
```

**问题3: 内存占用高**
```bash
# 检查Redis内存
redis-cli INFO memory

# 检查缓存大小
redis-cli DBSIZE

# 解决方案：
# 1. 清理过期缓存
# 2. 设置合理的TTL
# 3. 避免缓存大对象
```

### 代码审查清单

- [ ] 是否有标准排查流程？
- [ ] 是否记录了常见问题和解决方案？
- [ ] 是否有监控指标帮助诊断？
- [ ] 问题解决后是否更新经验文档？

---

## 相关经验文档

- [性能模式 - 缓存策略](./performance-patterns.md#缓存策略) - 缓存使用规范
- [测试指南 - 测试隔离](./testing-guide.md#测试隔离) - 环境隔离配置
- [调试技能](./debugging-skills.md) - 问题诊断方法
