# 缓存监控系统使用指南

## 概述

缓存监控系统提供了全面的缓存性能监控、指标收集和告警功能，帮助开发者实时了解缓存系统的运行状态。

**版本**: 1.0.0
**日期**: 2026-03-10

## 核心功能

### 1. 性能指标收集

自动收集以下性能指标：
- **命中率统计**: L1/L2缓存命中率
- **响应时间**: 平均响应时间、最小/最大响应时间
- **请求统计**: 总请求数、命中数、未命中数
- **容量使用**: L1/L2缓存容量使用情况

### 2. 实时监控

提供实时监控功能：
- **实时指标**: 当前缓存状态
- **性能趋势**: 历史性能数据
- **告警系统**: 自动检测性能问题并告警

### 3. HTTP响应头

在API响应中添加缓存状态头：
- `X-Cache-Status`: HIT 或 MISS
- `X-Cache-Key`: 缓存键的哈希值
- `X-Response-Time`: 响应时间（毫秒）

## 快速开始

### 1. 启用缓存监控

在Flask应用初始化时启用监控：

```python
from backend.core.cache.middleware import init_cache_monitoring_middleware

# 在Flask应用创建后初始化中间件
init_cache_monitoring_middleware(app)
```

### 2. 使用带监控的缓存装饰器

```python
from backend.core.cache.decorators import cached

# 使用@cached装饰器（自动添加HTTP响应头）
@cached(ttl=1800, key_prefix="games")
def get_game_by_gid(game_gid: int):
    return fetch_one_as_dict('SELECT * FROM games WHERE gid = ?', (game_gid,))
```

### 3. 访问监控API

**获取缓存统计**:
```bash
curl http://127.0.0.1:5001/api/cache/stats
```

**获取性能摘要**:
```bash
curl http://127.0.0.1:5001/api/cache/monitoring/performance?hours=24
```

**创建监控快照**:
```bash
curl -X POST http://127.0.0.1:5001/api/cache/monitoring/snapshot
```

## API端点

### GET /api/cache/stats

获取缓存统计信息

**响应示例**:
```json
{
  "success": true,
  "timestamp": "2026-03-10T12:00:00",
  "l1_cache": {
    "size": 500,
    "capacity": 1000,
    "usage": "50.0%",
    "hits": 10000,
    "sets": 5000,
    "evictions": 100
  },
  "l2_cache": {
    "total_keys": 5000,
    "memory_used": "100MB",
    "hit_rate": "85.5%",
    "keyspace_hits": 50000,
    "keyspace_misses": 8500
  },
  "monitoring": {
    "performance_metrics": {
      "hits": 10000,
      "misses": 1500,
      "total_requests": 11500,
      "hit_rate": "86.96%",
      "avg_response_time_ms": 2.5
    },
    "recent_alerts": [
      {
        "type": "low_hit_rate",
        "severity": "warning",
        "message": "缓存命中率过低: 45.0%",
        "timestamp": "2026-03-10T12:00:00"
      }
    ],
    "alert_count": 1
  }
}
```

### GET /api/cache/monitoring/performance

获取性能指标

**查询参数**:
- `hours`: 查询的小时数（默认24）

**响应示例**:
```json
{
  "success": true,
  "timestamp": "2026-03-10T12:00:00",
  "period_hours": 24,
  "performance_summary": {
    "avg_hit_rate": 87.5,
    "min_hit_rate": 75.0,
    "max_hit_rate": 95.0,
    "avg_response_time_ms": 2.3,
    "total_snapshots": 1440
  },
  "current_metrics": {
    "hits": 10000,
    "misses": 1500,
    "total_requests": 11500,
    "hit_rate": "86.96%",
    "avg_response_time_ms": 2.5
  }
}
```

### POST /api/cache/monitoring/snapshot

创建监控快照

**响应示例**:
```json
{
  "success": true,
  "message": "✅ 监控快照已创建",
  "timestamp": "2026-03-10T12:00:00"
}
```

## 告警系统

### 告警类型

**1. 低命中率告警**
- **触发条件**: 命中率低于阈值（默认50%）
- **严重级别**: warning
- **建议**: 检查缓存策略，调整TTL

**2. 慢响应告警**
- **触发条件**: 平均响应时间高于阈值（默认100ms）
- **严重级别**: warning
- **建议**: 检查缓存性能，考虑增加缓存容量

### 告警配置

```python
from backend.core.cache.monitoring_enhanced import get_cache_monitor

# 自定义告警阈值
monitor = get_cache_monitor(cache_instance)
monitor.alert_thresholds = {
    'low_hit_rate': 60.0,      # 命中率低于60%告警
    'high_miss_rate': 40.0,    # 未命中率高于40%告警
    'slow_response': 50.0,     # 响应时间高于50ms告警
}
```

## 使用示例

### 示例1: 监控API性能

```python
from backend.core.cache.decorators import cached
from flask import jsonify

@cached(ttl=3600, key_prefix="api")
def get_expensive_data():
    # 昂贵的数据库查询
    return fetch_all_as_dict('SELECT * FROM large_table')

@app.route('/api/data')
def get_data():
    data = get_expensive_data()
    return jsonify(data)

# 检查响应头
# X-Cache-Status: HIT
# X-Cache-Key: a3f5b8c2
# X-Response-Time: 2.50ms
```

### 示例2: 监控游戏列表性能

```python
from backend.core.cache.decorators import cached

@cached(ttl=1800, key_prefix="games")
def get_all_games():
    """获取所有游戏（缓存30分钟）"""
    return game_repo.get_all()

# 第一次调用（MISS）
games = get_all_games()
# 响应头: X-Cache-Status: MISS

# 第二次调用（HIT）
games = get_all_games()
# 响应头: X-Cache-Status: HIT
```

### 示例3: 监控缓存性能趋势

```python
import requests
import time

# 记录初始性能
response = requests.get('http://127.0.0.1:5001/api/cache/stats')
initial_stats = response.json()

# 执行一些操作
for i in range(100):
    requests.get(f'http://127.0.0.1:5001/api/games/{i}')

# 等待一段时间
time.sleep(60)

# 创建快照
requests.post('http://127.0.0.1:5001/api/cache/monitoring/snapshot')

# 获取性能趋势
response = requests.get('http://127.0.0.1:5001/api/cache/monitoring/performance?hours=1')
trends = response.json()
print(f"平均命中率: {trends['performance_summary']['avg_hit_rate']:.2f}%")
```

## 最佳实践

### 1. TTL设置

根据数据变化频率设置合理的TTL：

```python
# 静态数据：长TTL（1-2小时）
@cached(ttl=7200)
def get_system_config():
    pass

# 中等变化：中TTL（30分钟）
@cached(ttl=1800)
def get_events(game_gid):
    pass

# 实时数据：短TTL（1分钟）
@cached(ttl=60)
def get_online_users():
    pass
```

### 2. 监控关键指标

定期检查以下指标：
- **命中率**: 目标 >85%
- **响应时间**: 目标 95% <500ms
- **慢查询率**: 目标 <5%
- **错误率**: 目标 <1%

### 3. 响应时间优化

```python
# 使用分层缓存优化响应时间
from backend.core.cache.decorators import cached_service

@cached_service(
    "game:{gid}",
    ttl_l1=60,    # L1缓存1分钟
    ttl_l2=1800,  # L2缓存30分钟
    key_params=['gid']
)
def get_game_by_gid(self, gid: int):
    return self.game_repo.find_by_gid(gid)
```

## 故障排除

### 问题1: 命中率过低

**症状**: 命中率 <50%

**可能原因**:
1. TTL设置过短
2. 缓存容量不足
3. 缓存键设计不合理

**解决方案**:
```python
# 增加TTL
@cached(ttl=3600)  # 从300秒增加到3600秒

# 检查缓存容量
stats = hierarchical_cache.get_stats()
print(f"L1使用率: {stats['l1_usage']}")

# 优化缓存键
@cached(ttl=1800, key_prefix="games")  # 添加key_prefix
```

### 问题2: 响应时间过长

**症状**: 平均响应时间 >100ms

**可能原因**:
1. L2缓存未启用
2. 网络延迟
3. Redis性能问题

**解决方案**:
```python
# 检查L2缓存状态
redis_client = get_redis_client()
if redis_client:
    info = redis_client.info()
    print(f"Redis响应时间: {info.get('instantaneous_ops_per_sec')} ops/sec")

# 使用L1缓存加速热点数据
@cached(ttl=60)  # 短TTL，数据存放在L1
def get_hot_data():
    pass
```

### 问题3: 监控数据不更新

**症状**: 监控指标始终为0

**可能原因**:
1. 缓存装饰器未正确使用
2. 监控中间件未初始化
3. Flask应用上下文问题

**解决方案**:
```python
# 确保初始化监控中间件
from backend.core.cache.middleware import init_cache_monitoring_middleware
init_cache_monitoring_middleware(app)

# 使用带监控的装饰器
@cached(ttl=1800, add_response_headers=True)
def monitored_function():
    pass

# 手动创建快照
from backend.core.cache.monitoring_enhanced import get_cache_monitor
monitor = get_cache_monitor(cache_instance)
monitor.create_snapshot()
```

## 性能指标参考

### 健康的缓存系统

| 指标 | 健康范围 | 警告范围 | 严重范围 |
|------|----------|----------|----------|
| **命中率** | >85% | 50-85% | <50% |
| **L1命中率** | >70% | 50-70% | <50% |
| **L2命中率** | >90% | 70-90% | <70% |
| **平均响应时间** | <5ms | 5-50ms | >50ms |
| **P95响应时间** | <10ms | 10-100ms | >100ms |
| **L1使用率** | 50-80% | 80-95% | >95% |
| **L2使用率** | <80% | 80-90% | >90% |

## 总结

缓存监控系统提供了全面的缓存性能监控功能，帮助开发者：

1. **实时监控**: 了解缓存系统的实时状态
2. **性能分析**: 识别性能瓶颈
3. **告警通知**: 及时发现性能问题
4. **趋势分析**: 了解性能变化趋势

通过合理使用监控系统，可以显著提升应用的性能和用户体验。
