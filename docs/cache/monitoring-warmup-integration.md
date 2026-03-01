# 缓存监控预热集成指南

> **版本**: 1.0.0
> **日期**: 2026-02-27
> **状态**: ✅ 已实现

## 概述

本文档说明如何在 `web_app.py` 中配置缓存监控和自动预热系统集成。

## 实现的功能

### 1. 回调机制（避免循环依赖）

**问题**: `backend/core/cache/monitoring.py` (core层) 不应直接依赖 `backend/services/cache/cache_warmup.py` (services层)

**解决方案**: 使用回调函数注入模式

```python
# ✅ 正确：在 web_app.py 中注入回调
from backend.core.cache.monitoring import get_cache_alert_manager
from backend.services.cache.cache_warmup import CacheWarmer

# 创建预热器
warmer = CacheWarmer()

# 创建告警管理器（注入预热回调）
alert_manager = get_cache_alert_manager(
    hierarchical_cache,
    warmup_callback=warmer.warmup_all  # 注入回调
)
```

### 2. 支持同步和异步回调

```python
# 同步回调
def sync_warmup():
    return {"warmed": 100, "failed": 0}

alert_manager = get_cache_alert_manager(
    cache,
    warmup_callback=sync_warmup
)

# 异步回调
async def async_warmup():
    await fetch_data()
    return {"warmed": 100}

alert_manager = get_cache_alert_manager(
    cache,
    warmup_callback=async_warmup  # 自动处理异步
)
```

### 3. 预热统计信息

预热执行后，统计信息会自动记录：

```python
{
    "triggered_count": 1,           # 触发次数
    "last_triggered_time": 1740638400.0,  # 最后触发时间
    "last_trigger_result": {         # 最后触发结果
        "warmed": 100,
        "failed": 0,
        "skipped": 10
    }
}
```

### 4. 告警触发条件

自动预热会在以下情况触发：

- **总体命中率 < 50%** 持续 **5分钟** → CRITICAL → 自动预热
- **L1命中率 < 40%** 持续 **3分钟** → CRITICAL → 自动扩容L1
- **L1使用率 > 95%** 持续 **30秒** → CRITICAL → 自动扩容L1

## 配置示例

### 完整配置 (web_app.py)

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event2Table Web应用
"""

import logging
from flask import Flask
from backend.core.cache.cache_system import get_cache, hierarchical_cache
from backend.core.cache.monitoring import get_cache_alert_manager, start_monitoring_thread
from backend.services.cache.cache_warmup import CacheWarmer

logger = logging.getLogger(__name__)

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)

    # ... 其他配置 ...

    # 1. 获取缓存实例
    cache = get_cache()

    # 2. 创建预热器
    warmer = CacheWarmer()

    # 3. 应用启动时预热（可选）
    logger.info("🔥 执行启动时预热...")
    startup_stats = warmer.warmup_all(games_limit=100, events_limit=100)
    logger.info(f"✅ 启动预热完成: {startup_stats}")

    # 4. 初始化告警管理器（注入预热回调）
    alert_manager = get_cache_alert_manager(
        hierarchical_cache,
        warmup_callback=warmer.warmup_all  # 自动预热回调
    )

    # 5. 启动监控线程（每60秒检查一次）
    monitor_thread = start_monitoring_thread(
        alert_manager=alert_manager,
        check_interval=60
    )

    logger.info("✅ 缓存监控和预热系统已启动")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=False)
```

### 自定义预热策略

```python
class CustomCacheWarmer:
    """自定义预热器"""

    def __init__(self, db_connection):
        self.db = db_connection

    def warmup_critical_data(self):
        """只预热关键数据"""
        stats = {
            "games_warmed": 0,
            "events_warmed": 0,
            "params_warmed": 0
        }

        # 预热热门游戏（Top 10）
        games = self.db.execute("SELECT * FROM games ORDER BY gid LIMIT 10")
        for game in games:
            cache.set(f"games:{game['gid']}", game, ttl=3600)
            stats["games_warmed"] += 1

        # 预热常用事件
        events = self.db.execute("""
            SELECT le.* FROM log_events le
            INNER JOIN games g ON le.game_gid = g.gid
            WHERE g.gid = 10000147  # STAR001
            LIMIT 20
        """)
        for event in events:
            cache.set(f"events:{event['id']}", event, ttl=1800)
            stats["events_warmed"] += 1

        logger.info(f"✅ 自定义预热完成: {stats}")
        return stats

# 使用自定义预热器
custom_warmer = CustomCacheWarmer(db)
alert_manager = get_cache_alert_manager(
    hierarchical_cache,
    warmup_callback=custom_warmer.warmup_critical_data
)
```

## 监控和调试

### 查看预热统计

```python
# 方法1: 通过指标摘要
summary = alert_manager.get_metrics_summary()
print(f"预热触发次数: {summary['warmup_stats']['triggered_count']}")
print(f"最后预热结果: {summary['warmup_stats']['last_trigger_result']}")

# 方法2: 直接访问
print(f"预热触发次数: {alert_manager._warmup_stats['triggered_count']}")
print(f"最后触发时间: {alert_manager._warmup_stats['last_triggered_time']}")
```

### API端点（可选）

```python
# 添加到 backend/api/routes/cache.py
@cache_bp.route('/monitoring/warmup-stats', methods=['GET'])
def get_warmup_stats():
    """获取预热统计"""
    from backend.core.cache.monitoring import get_cache_alert_manager

    alert_manager = get_cache_alert_manager()
    stats = alert_manager._warmup_stats

    return jsonify({
        "triggered_count": stats["triggered_count"],
        "last_triggered_time": stats["last_triggered_time"],
        "last_trigger_result": stats["last_trigger_result"]
    })
```

### 日志输出

预热触发时的日志示例：

```
2026-02-27 00:00:00 - WARNING - 🔥 检测到缓存命中率过低，触发自动预热
2026-02-27 00:00:00 - INFO - ✅ 执行预热回调函数
2026-02-27 00:00:01 - INFO - 🔥 Warming up top 100 popular games...
2026-02-27 00:00:01 - INFO - ✅ Warmed up 100 games
2026-02-27 00:00:02 - INFO - 🔥 Warming up 100 recent events...
2026-02-27 00:00:02 - INFO - ✅ Warmed up 100 events
2026-02-27 00:00:03 - INFO - 🔥 Warming up common parameters...
2026-02-27 00:00:03 - INFO - ✅ Warmed up 50 parameters
2026-02-27 00:00:03 - INFO - ✅ 缓存预热完成: 预热 250/250 个键
2026-02-27 00:00:03 - INFO -   - 游戏: 100, 事件: 100, 参数: 50
```

## 测试

### 单元测试

```bash
# 运行预热回调测试
pytest backend/core/cache/tests/test_warmup_callback_simple.py -v

# 运行监控集成测试
pytest backend/core/cache/tests/test_monitoring_warmup_integration.py -v
```

### 手动测试

```python
# test_warmup_manual.py
from backend.core.cache.monitoring import CacheAlertManager
from backend.core.cache.cache_system import get_cache
from backend.services.cache.cache_warmup import CacheWarmer

def test_manual_warmup():
    """手动触发预热测试"""

    # 创建预热器
    warmer = CacheWarmer()

    # 创建告警管理器
    cache = get_cache()
    alert_manager = CacheAlertManager(
        cache,
        warmup_callback=warmer.warmup_all
    )

    # 手动触发预热
    print("手动触发预热...")
    alert_manager._trigger_warm_up()

    # 查看结果
    print(f"触发次数: {alert_manager._warmup_stats['triggered_count']}")
    print(f"预热结果: {alert_manager._warmup_stats['last_trigger_result']}")

if __name__ == "__main__":
    test_manual_warmup()
```

## 故障排除

### 问题1: 预热未触发

**症状**: 缓存命中率很低，但预热未触发

**排查**:
1. 检查告警管理器是否初始化
2. 检查监控线程是否运行
3. 检查回调函数是否正确注入

```python
# 检查告警管理器
alert_manager = get_cache_alert_manager()
print(f"回调函数: {alert_manager._warmup_callback}")

# 检查统计
stats = alert_manager._warmup_stats
print(f"触发次数: {stats['triggered_count']}")
```

### 问题2: 预热失败

**症状**: 预热触发但返回错误

**排查**:
1. 查看日志中的错误信息
2. 检查数据库连接
3. 检查Redis连接

```python
# 检查最后一次结果
result = alert_manager._warmup_stats['last_trigger_result']
if 'error' in result:
    print(f"预热错误: {result['error']}")
```

### 问题3: 异步回调卡死

**症状**: 异步回调导致应用挂起

**解决方案**: 使用同步包装器

```python
import asyncio

async def async_warmup():
    # 异步操作
    pass

# 同步包装器
def sync_wrapper():
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(async_warmup())

# 使用同步包装器
alert_manager = get_cache_alert_manager(
    cache,
    warmup_callback=sync_wrapper
)
```

## 最佳实践

1. **启动时预热**: 应用启动时先预热常用数据
2. **定时预热**: 设置定时任务定期预热（每5分钟）
3. **自动预热**: 监控命中率低时自动触发预热
4. **降级策略**: 回调失败时记录错误但不影响主流程
5. **监控统计**: 记录预热统计以便优化

## 相关文档

- [缓存系统文档中心](/Users/mckenzie/Documents/event2table/docs/cache/README.md)
- [5分钟快速开始](/Users/mckenzie/Documents/event2table/docs/cache/quickstart/5-minute-guide.md)
- [开发者指南](/Users/mckenzie/Documents/event2table/docs/cache/development/developer-guide.md)
- [故障排除手册](/Users/mckenzie/Documents/event2table/docs/cache/operations/troubleshooting.md)
