# 缓存系统监控和告警文档

> **面向**: 运维人员、SRE、DevOps
> **目标**: 建立完整的缓存监控告警体系
> **版本**: 1.0
> **最后更新**: 2026-02-27

---

## 📊 监控体系概览

### 三级监控架构

```
┌─────────────────────────────────────────────────────┐
│           应用层监控 (Application Layer)             │
│  - L1命中率监控                                       │
│  - 缓存性能指标                                       │
│  - 业务告警规则                                       │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│           中间件层监控 (Middleware Layer)             │
│  - Redis性能监控                                      │
│  - 连接池状态                                         │
│  - 持久化状态                                         │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│           基础设施层监控 (Infrastructure Layer)       │
│  - CPU/内存/磁盘                                      │
│  - 网络IO                                            │
│  - 系统负载                                          │
└─────────────────────────────────────────────────────┘
```

### 核心监控组件

| 组件 | 职责 | 实现位置 |
|------|------|----------|
| **CacheAlertManager** | 告警规则引擎、自动响应 | `backend/core/cache/monitoring.py` |
| **MetricsHistory** | 指标历史记录、趋势分析 | `backend/core/cache/monitoring.py` |
| **HierarchicalCache** | 缓存统计、性能采集 | `backend/core/cache/cache_system.py` |
| **Redis INFO** | Redis原生监控 | Redis内置 |

---

## 🎯 核心监控指标

### 1. 命中率指标 (Hit Rate)

#### L1缓存命中率
- **定义**: L1命中次数 / 总请求次数
- **目标值**: >60%
- **警告阈值**: <60% 持续5分钟
- **严重阈值**: <40% 持续3分钟 (触发自动扩容)

```python
# 计算公式
l1_hit_rate = l1_hits / total_requests

# 监控代码示例
from backend.core.cache.monitoring import get_cache_alert_manager

alert_manager = get_cache_alert_manager(hierarchical_cache)
summary = alert_manager.get_metrics_summary()
print(f"L1命中率: {summary['l1_hit_rate']}")  # 输出: "85.23%"
```

#### L2缓存命中率
- **定义**: L2命中次数 / L1未命中次数
- **目标值**: >70%
- **警告阈值**: <70% 持续10分钟

```python
# 计算公式
l2_hit_rate = l2_hits / (total_requests - l1_hits)
```

#### 总体命中率
- **定义**: (L1命中 + L2命中) / 总请求次数
- **目标值**: >80%
- **严重阈值**: <50% 持续5分钟 (触发自动预热)

```python
# 计算公式
overall_hit_rate = (l1_hits + l2_hits) / total_requests
```

### 2. 性能指标 (Performance)

#### QPS (Queries Per Second)
- **定义**: 每秒查询次数
- **采集方式**: `record_request()` 计数器
- **目标值**: <1000 (单实例)

```python
# 监控代码
summary = alert_manager.get_metrics_summary()
print(f"QPS: {summary['qps']}")  # 输出: "245.67"
```

#### 平均响应时间
- **定义**: 平均每次请求响应时间（毫秒）
- **目标值**: <100ms (L1), <200ms (L2)
- **警告阈值**: >200ms

```python
# 监控代码
summary = alert_manager.get_metrics_summary()
print(f"平均响应时间: {summary['avg_response_time_ms']}ms")  # 输出: "45.23ms"
```

### 3. 容量指标 (Capacity)

#### L1缓存使用率
- **定义**: L1当前条目数 / L1容量
- **目标值**: <80%
- **警告阈值**: >85% 持续1分钟
- **严重阈值**: >95% 持续30秒 (触发自动扩容)

```python
# 监控代码
stats = hierarchical_cache.get_stats()
print(f"L1使用率: {stats['l1_usage']}")  # 输出: "75.5%"
print(f"L1容量: {stats['l1_size']}/{stats['l1_capacity']}")  # 输出: "755/1000"
```

#### Redis内存使用率
- **定义**: Redis已用内存 / maxmemory
- **目标值**: <80%
- **警告阈值**: >90%

```bash
# 监控命令
redis-cli INFO memory | grep used_memory_percentage
```

### 4. 健康指标 (Health)

#### L1淘汰次数
- **定义**: L1缓存因容量满而淘汰的条目数
- **目标值**: 尽可能低
- **警告阈值**: >100/分钟

```python
# 监控代码
stats = hierarchical_cache.get_stats()
print(f"L1淘汰次数: {stats['l1_evictions']}")  # 输出: "1234"
```

#### Redis驱逐次数
- **定义**: Redis因maxmemory策略驱逐的键数
- **目标值**: 0
- **警告阈值**: >100/分钟

```bash
# 监控命令
redis-cli INFO stats | grep evicted_keys
```

---

## 🚨 告警规则配置

### 内置告警规则

`CacheAlertManager` 预配置了6条告警规则：

| 规则名称 | 监控指标 | 阈值 | 持续时间 | 级别 | 自动动作 |
|---------|---------|------|----------|------|----------|
| `l1_hit_rate_low` | L1命中率 | <60% | 5分钟 | WARNING | 无 |
| `l1_hit_rate_critical` | L1命中率 | <40% | 3分钟 | CRITICAL | 自动扩容L1 |
| `l2_hit_rate_low` | L2命中率 | <70% | 10分钟 | WARNING | 无 |
| `overall_hit_rate_critical` | 总体命中率 | <50% | 5分钟 | CRITICAL | 触发预热 |
| `l1_capacity_warning` | L1使用率 | >85% | 1分钟 | WARNING | 无 |
| `l1_capacity_critical` | L1使用率 | >95% | 30秒 | CRITICAL | 自动扩容L1 |

### 自定义告警规则

```python
from backend.core.cache.monitoring import CacheAlertManager, AlertRule, AlertLevel

# 添加自定义告警规则
custom_rule = AlertRule(
    name="response_time_critical",
    metric="avg_response_time_ms",
    threshold=500.0,  # 500ms
    duration=120,  # 2分钟
    level=AlertLevel.CRITICAL,
    action=lambda: logger.critical("响应时间过慢，考虑扩容"),
    description="平均响应时间超过500ms持续2分钟"
)

# 添加到告警管理器
alert_manager.alert_rules.append(custom_rule)
```

### 告警级别说明

| 级别 | 含义 | 颜色 | 响应时间 | 自动动作 |
|------|------|------|----------|----------|
| **INFO** | 信息通知 | 蓝色 | 工作时间 | 无 |
| **WARNING** | 警告 | 黄色 | 30分钟 | 无 |
| **CRITICAL** | 严重 | 红色 | 立即 | 自动修复 |

---

## 🤖 自动化响应动作

### 1. 自动扩容L1缓存

**触发条件**:
- L1命中率 <40% 持续3分钟
- L1使用率 >95% 持续30秒

**扩容策略**:
```python
def _auto_expand_l1(self):
    """自动扩容L1缓存 (扩容50%)"""
    current_size = self.cache.l1_size
    new_size = int(current_size * 1.5)

    logger.warning(f"🔧 自动扩容L1缓存: {current_size} → {new_size}")
    self.cache.l1_size = new_size
```

**扩容示例**:
- 初始容量: 1000条
- 第一次扩容: 1500条
- 第二次扩容: 2250条

**限制**:
- 最大容量: 10000条 (硬编码限制)
- 扩容频率: 同一规则5分钟内仅触发一次 (去重机制)

### 2. 自动预热缓存

**触发条件**:
- 总体命中率 <50% 持续5分钟

**预热策略**:
```python
def _trigger_warm_up(self):
    """触发缓存预热"""
    logger.warning("🔥 触发缓存预热")
    # TODO: 调用智能预热系统
    # from .intelligent_warmer import cache_warmer
    # cache_warmer.warm_up_cache()
```

**预热内容** (待实现):
- 热点游戏数据
- 高频事件列表
- 常用参数配置

### 3. 降级到L1缓存

**触发条件**:
- Redis连接失败
- Redis响应超时

**降级策略**:
```python
# 在cache_system.py中自动实现
try:
    cached = cache.get(key)
except Exception as e:
    logger.warning(f"⚠️ L2缓存读取失败: {e}")
    # 自动降级到L1缓存
```

---

## 📈 监控Dashboard配置

### Prometheus + Grafana

#### 1. Prometheus配置

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'event2table_cache'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:5001']
    metrics_path: '/api/cache/metrics/prometheus'
```

#### 2. 导出Prometheus指标

```python
# backend/api/routes/cache.py
from flask import Blueprint, jsonify
from backend.core.cache.monitoring import export_prometheus_metrics, get_cache_alert_manager

cache_bp = Blueprint('cache', __name__)

@cache_bp.route('/api/cache/metrics/prometheus')
def prometheus_metrics():
    """导出Prometheus格式指标"""
    alert_manager = get_cache_alert_manager()
    metrics = export_prometheus_metrics(alert_manager)
    return metrics, 200, {'Content-Type': 'text/plain'}
```

#### 3. Grafana Dashboard JSON

```json
{
  "dashboard": {
    "title": "Event2Table Cache Monitoring",
    "panels": [
      {
        "title": "Cache Hit Rate",
        "targets": [
          {
            "expr": "cache_hit_rate{level=\"l1\"}",
            "legendFormat": "L1 Hit Rate"
          },
          {
            "expr": "cache_hit_rate{level=\"l2\"}",
            "legendFormat": "L2 Hit Rate"
          },
          {
            "expr": "cache_hit_rate{level=\"overall\"}",
            "legendFormat": "Overall Hit Rate"
          }
        ],
        "type": "graph"
      },
      {
        "title": "L1 Cache Usage",
        "targets": [
          {
            "expr": "cache_l1_usage",
            "legendFormat": "L1 Usage"
          },
          {
            "expr": "cache_l1_capacity",
            "legendFormat": "L1 Capacity"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Active Alerts",
        "targets": [
          {
            "expr": "cache_alerts{level=\"warning\"}",
            "legendFormat": "Warning"
          },
          {
            "expr": "cache_alerts{level=\"critical\"}",
            "legendFormat": "Critical"
          }
        ],
        "type": "stat"
      }
    ]
  }
}
```

### 监控API接口

#### 1. 获取缓存统计

```bash
curl http://127.0.0.1:5001/api/cache/stats
```

**响应示例**:
```json
{
  "l1_size": 755,
  "l1_capacity": 1000,
  "l1_usage": "75.5%",
  "l1_hits": 4523,
  "l2_hits": 8912,
  "misses": 1234,
  "hit_rate": "91.42%",
  "l1_evictions": 567,
  "l1_sets": 5090,
  "l2_sets": 10146,
  "total_requests": 14669,
  "empty_hits": 123
}
```

#### 2. 获取活跃告警

```bash
curl http://127.0.0.1:5001/api/cache/alerts/active
```

**响应示例**:
```json
[
  {
    "rule_name": "l1_hit_rate_low",
    "metric": "l1_hit_rate",
    "current_value": "55.23%",
    "threshold": "60.00%",
    "level": "WARNING",
    "timestamp": 1740634567.123,
    "duration": 342,
    "resolved": false
  }
]
```

#### 3. 获取告警历史

```bash
curl http://127.0.0.1:5001/api/cache/alerts/history?limit=10
```

#### 4. 获取指标摘要

```bash
curl http://127.0.0.1:5001/api/cache/metrics/summary
```

**响应示例**:
```json
{
  "timestamp": 1740634567.123,
  "l1_hit_rate": "85.23%",
  "l2_hit_rate": "72.45%",
  "overall_hit_rate": "91.42%",
  "l1_usage": "75.5%",
  "qps": "245.67",
  "avg_response_time_ms": "45.23",
  "trends": {
    "l1_hit_rate_5min": {
      "min": 0.8212,
      "max": 0.8723,
      "avg": 0.8467,
      "count": 300,
      "trend": 0.0123
    },
    "l2_hit_rate_5min": {
      "min": 0.7034,
      "max": 0.7512,
      "avg": 0.7278,
      "count": 300,
      "trend": -0.0056
    },
    "overall_hit_rate_5min": {
      "min": 0.9012,
      "max": 0.9234,
      "avg": 0.9145,
      "count": 300,
      "trend": 0.0089
    }
  }
}
```

---

## 🔍 日志分析技巧

### 日志级别说明

| 级别 | 用途 | 示例 |
|------|------|------|
| **DEBUG** | 详细的缓存操作日志 | `✅ L1 HIT: dwd_gen:v3:events.list:game_id:1` |
| **INFO** | 正常操作记录 | `✅ 缓存告警管理器初始化完成` |
| **WARNING** | 告警触发 | `🚨 缓存告警: L1缓存命中率低于60%` |
| **CRITICAL** | 严重问题 | `❌ L1缓存扩容失败: ...` |
| **ERROR** | 错误异常 | `❌ 告警动作执行失败: ...` |

### 关键日志模式

#### 1. 缓存命中日志
```
✅ L1 HIT: dwd_gen:v3:events.list:game_id:1
✅ L2 HIT → L1回填: dwd_gen:v3:games.detail:id:1
❌ CACHE MISS: dwd_gen:v3:params.list:event_id:1
```

**分析技巧**:
```bash
# 统计L1命中率
grep "L1 HIT" /var/log/event2table/cache.log | wc -l

# 统计缓存未命中次数
grep "CACHE MISS" /var/log/event2table/cache.log | wc -l

# 查看最频繁的缓存键
grep "CACHE MISS" /var/log/event2table/cache.log | \
  awk '{print $NF}' | sort | uniq -c | sort -rn | head -20
```

#### 2. 告警日志
```
🚨 缓存告警: L1缓存命中率低于60%持续5分钟
   指标: l1_hit_rate
   当前值: 55.23%
   阈值: 60.00%
   持续时间: 342秒
   级别: WARNING
```

**分析技巧**:
```bash
# 统计告警次数
grep "🚨 缓存告警" /var/log/event2table/cache.log | wc -l

# 按级别统计
grep "🚨 缓存告警" /var/log/event2table/cache.log | \
  grep "WARNING" | wc -l

grep "🚨 缓存告警" /var/log/event2table/cache.log | \
  grep "CRITICAL" | wc -l
```

#### 3. 自动响应日志
```
🔧 自动扩容L1缓存: 1000 → 1500
✅ L1缓存扩容完成
🔥 触发缓存预热
```

**分析技巧**:
```bash
# 查看扩容历史
grep "自动扩容" /var/log/event2table/cache.log

# 查看预热触发次数
grep "触发缓存预热" /var/log/event2table/cache.log | wc -l
```

### ELK Stack集成

#### Logstash配置
```ruby
# logstash.conf
input {
  file {
    path => "/var/log/event2table/cache.log"
    start_position => "beginning"
    codec => multiline {
      pattern => "^%{TIMESTAMP_ISO8601}"
      negate => true
      what => "previous"
    }
  }
}

filter {
  grok {
    match => {
      "message" => [
        # 解析缓存命中日志
        "✅ L1 HIT: %{DATA:cache_key}",
        # 解析告警日志
        "🚨 缓存告警: %{DATA:alert_description}"
      ]
    }
  }

  # 解析指标
  if [alert_description] {
    grok {
      match => {
        "message" => [
          "指标: %{DATA:metric}\s+当前值: %{NUMBER:current_value}%\s+阈值: %{NUMBER:threshold}%"
        ]
      }
    }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "event2table-cache-%{+YYYY.MM.dd}"
  }
}
```

---

## 🔧 监控工具集成

### 1. Redis Exporter

```bash
# 安装Redis Exporter
docker run -d \
  --name redis_exporter \
  -p 9121:9121 \
  oliver006/redis_exporter \
  --redis.addr=redis://127.0.0.1:6379
```

**Prometheus配置**:
```yaml
scrape_configs:
  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']
```

### 2. Custom Python Exporter

```python
# backend/api/exporter.py
from prometheus_client import start_http_server, Gauge, Counter
from backend.core.cache.monitoring import get_cache_alert_manager

# 定义Prometheus指标
cache_hit_rate = Gauge('cache_hit_rate', 'Cache hit rate', ['level'])
cache_l1_usage = Gauge('cache_l1_usage', 'L1 cache usage')
cache_l1_capacity = Gauge('cache_l1_capacity', 'L1 cache capacity')
cache_alerts = Gauge('cache_alerts', 'Active alerts', ['level'])

def update_prometheus_metrics():
    """更新Prometheus指标"""
    alert_manager = get_cache_alert_manager()

    # 更新命中率
    summary = alert_manager.get_metrics_summary()
    cache_hit_rate.labels(level='l1').set(float(summary['l1_hit_rate'].rstrip('%')) / 100)
    cache_hit_rate.labels(level='l2').set(float(summary['l2_hit_rate'].rstrip('%')) / 100)
    cache_hit_rate.labels(level='overall').set(float(summary['overall_hit_rate'].rstrip('%')) / 100)

    # 更新L1使用率
    stats = alert_manager.cache.get_stats()
    cache_l1_usage.set(stats['l1_size'])
    cache_l1_capacity.set(stats['l1_capacity'])

    # 更新活跃告警
    active_alerts = alert_manager.get_active_alerts()
    warning_count = sum(1 for a in active_alerts if a['level'] == 'WARNING')
    critical_count = sum(1 for a in active_alerts if a['level'] == 'CRITICAL')
    cache_alerts.labels(level='warning').set(warning_count)
    cache_alerts.labels(level='critical').set(critical_count)

# 启动Prometheus HTTP服务器
start_http_server(8000)
```

**运行Exporter**:
```bash
python3 backend/api/exporter.py
# Prometheus指标访问: http://localhost:8000/metrics
```

### 3. Grafana Dashboard导入

1. 访问 Grafana: `http://localhost:3000`
2. 点击 "+" → "Import"
3. 粘贴Dashboard JSON (见上文)
4. 选择Prometheus数据源
5. 点击 "Import"

**推荐Dashboard**:
- Redis Dashboard (ID: 11835)
- Flask Dashboard (ID: 11203)
- Custom Event2Table Cache Dashboard

---

## 📋 监控最佳实践

### 1. 告警分级原则

| 级别 | 触发条件 | 响应时间 | 处理方式 |
|------|---------|----------|----------|
| **P0** | 系统不可用 | 立即 | 电话 + 短信 + 邮件 |
| **P1** | 功能严重受损 | 15分钟 | 短信 + 邮件 |
| **P2** | 功能部分受损 | 1小时 | 邮件 |
| **P3** | 潜在问题 | 工作时间 | 邮件 |

### 2. 告警去重策略

```python
# 告警去重机制 (已内置)
def _should_trigger_alert(self, alert: AlertEvent) -> bool:
    """判断是否应该触发告警（去重）"""
    if alert.rule_name in self.active_alerts:
        existing_alert = self.active_alerts[alert.rule_name]

        # 相同级别且1分钟内触发过，则不重复触发
        if (existing_alert.level == alert.level and
            time.time() - existing_alert.timestamp < 60):
            return False

    return True
```

**效果**: 避免告警风暴，同一告警1分钟内仅触发一次。

### 3. 监控频率建议

| 指标类型 | 采集频率 | 保留时间 |
|---------|---------|----------|
| 实时指标 (QPS/响应时间) | 1秒 | 1小时 |
| 命中率 | 5秒 | 24小时 |
| 容量指标 | 10秒 | 7天 |
| 慢查询 | 实时 | 30天 |
| 告警事件 | 实时 | 90天 |

### 4. 监控Dashboard布局

```
┌─────────────────────────────────────────────────────┐
│              Cache Monitoring Dashboard              │
├──────────┬──────────┬──────────┬─────────────────────┤
│ L1 Hit   │ L2 Hit   │ Overall  │ Active Alerts       │
│  Rate    │  Rate    │  Rate    │  Warning: 2         │
│  85.23%  │  72.45%  │  91.42%  │  Critical: 0         │
├──────────┴──────────┴──────────┴─────────────────────┤
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │          Hit Rate Trend (24h)                │   │
│  │  (Line Chart)                                │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ┌──────────────────┬──────────────────────────┐   │
│  │ L1 Usage (755/1K)│  L2 Memory (800MB/1GB)   │   │
│  │  (Gauge)         │  (Gauge)                 │   │
│  └──────────────────┴──────────────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │          QPS & Response Time                 │   │
│  │  (Dual Line Chart)                           │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

---

## 🚨 故障响应手册

### 场景1: 缓存命中率骤降

**症状**:
- 总体命中率从90%降到30%
- 数据库负载骤增
- 响应时间变慢

**排查步骤**:
1. 检查L1命中率: `curl http://127.0.0.1:5001/api/cache/stats`
2. 检查告警历史: `curl http://127.0.0.1:5001/api/cache/alerts/history`
3. 查看日志: `tail -f /var/log/event2table/cache.log | grep "CACHE MISS"`

**修复方案**:
```bash
# 方案1: 手动预热缓存
curl -X POST http://127.0.0.1:5001/api/cache/warmup

# 方案2: 扩容L1缓存 (自动触发)
# 等待自动扩容或手动调整
```

### 场景2: L1缓存满载

**症状**:
- L1使用率 >95%
- 大量L1淘汰 (l1_evictions飙升)
- L1命中率下降

**排查步骤**:
```bash
# 检查L1统计
curl http://127.0.0.1:5001/api/cache/stats | jq '.l1_evictions'

# 检查L1使用率
curl http://127.0.0.1:5001/api/cache/stats | jq '.l1_usage'
```

**修复方案**:
```python
# 方案1: 自动扩容 (L1使用率>95%持续30秒自动触发)
# 方案2: 手动扩容
from backend.core.cache.cache_system import hierarchical_cache
hierarchical_cache.l1_size = 2000  # 扩容到2000条
```

### 场景3: Redis连接失败

**症状**:
- L2命中率=0%
- 大量Redis连接错误日志
- 自动降级到L1缓存

**排查步骤**:
```bash
# 检查Redis状态
redis-cli PING

# 检查Redis日志
sudo journalctl -u redis -n 100

# 检查网络连接
telnet 127.0.0.1 6379
```

**修复方案**:
```bash
# 方案1: 重启Redis
sudo systemctl restart redis

# 方案2: 检查maxmemory设置
redis-cli CONFIG GET maxmemory

# 方案3: 清理Redis键 (紧急情况)
redis-cli FLUSHALL  # ⚠️ 谨慎使用
```

---

## 📊 监控报表模板

### 日报模板

```markdown
# 缓存系统监控日报 (2026-02-27)

## 核心指标
- 平均L1命中率: 85.23% (目标: >60%)
- 平均L2命中率: 72.45% (目标: >70%)
- 平均总体命中率: 91.42% (目标: >80%)
- 平均QPS: 245.67
- 平均响应时间: 45.23ms

## 容量使用
- L1缓存: 755/1000 (75.5%)
- Redis内存: 800MB/1GB (80%)

## 告警统计
- 今日告警次数: 3次
- WARNING级别: 3次
- CRITICAL级别: 0次

## 异常事件
- 10:30 L1命中率短暂下降至55% (持续3分钟)
- 14:20 L1使用率达到90% (自动扩容至1500条)

## 明日计划
- 继续监控L1使用率趋势
- 预计扩容Redis至2GB
```

---

## 🔗 相关文档

- **[部署运维文档](./deployment.md)** - 生产环境部署指南
- **[故障排除手册](./troubleshooting.md)** - 常见问题解决方案
- **[开发者指南](../development/developer-guide.md)** - 深入了解缓存系统架构
- **[5分钟快速开始](../quickstart/5-minute-guide.md)** - 新用户快速上手

---

**文档版本**: 1.0
**最后更新**: 2026-02-27
**维护者**: Event2Table Development Team
