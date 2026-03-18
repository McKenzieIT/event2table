# 缓存系统部署运维文档

> **面向**: 运维人员、DevOps
> **目标**: 指导生产环境部署和运维
> **版本**: 1.0

---

## 📋 部署前准备

### 1. 系统要求

| 组件 | 最低要求 | 推荐配置 |
|------|---------|---------|
| **Redis** | 2.6+ | 6.0+ |
| **Python** | 3.9+ | 3.10+ |
| **内存** | 512MB | 2GB+ |
| **磁盘** | 1GB | 10GB+ |

### 2. 依赖检查

```bash
# 检查Redis版本
redis-cli --version

# 检查Redis服务状态
redis-cli ping

# 检查Python版本
python3 --version

# 检查依赖包
pip list | grep -E "redis|pybloom"
```

---

## 🚀 生产环境部署

### 配置清单

#### Redis配置

```bash
# /etc/redis/redis.conf

# 内存限制
maxmemory 1gb
maxmemory-policy allkeys-lru

# 持久化配置
save 900 1        # 900秒内至少1个key变化则保存
save 300 10       # 300秒内至少10个key变化则保存
save 60 10000     # 60秒内至少10000个key变化则保存

# AOF持久化（可选，更安全但性能稍差）
appendonly yes
appendfsync everysec

# 日志级别
loglevel notice

# 最大客户端连接数
maxclients 10000

# 慢查询配置
slowlog-log-slower-than 10000  # 10ms
slowlog-max-len 128
```

#### 应用配置

```python
# backend/core/config/config.py

class CacheConfig:
    """缓存配置"""

    # Redis连接
    REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
    REDIS_DB = int(os.environ.get("REDIS_DB", 0))
    REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)

    # L1缓存配置
    L1_CACHE_ENABLED = True
    L1_MAX_SIZE = 1000  # 最多缓存1000个对象
    L1_TTL = 600  # L1默认TTL 10分钟

    # 缓存降级
    DEGRADE_ENABLED = True  # Redis不可用时自动降级到L1
    DEGRADE_THRESHOLD = 3  # 连续失败3次后降级

    # 监控配置
    MONITORING_ENABLED = True
    STATS_RESET_INTERVAL = 86400  # 每天重置统计
```

#### 环境变量

```bash
# .env.production

# Redis配置
REDIS_HOST=redis.internal.example.com
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your-secure-password

# 缓存配置
CACHE_ENABLED=true
L1_CACHE_ENABLED=true
DEGRADE_ENABLED=true

# 监控配置
MONITORING_ENABLED=true
```

---

## 📊 监控指标

### 核心指标

| 指标 | 目标值 | 告警阈值 | 说明 |
|------|--------|---------|------|
| **缓存命中率** | >80% | <70% | hit_rate = hits / (hits + misses) |
| **平均响应时间** | <100ms | >200ms | 缓存命中时的响应时间 |
| **P99响应时间** | <200ms | >500ms | 99%请求的响应时间 |
| **内存使用率** | <80% | >90% | Redis内存使用百分比 |
| **键数量** | 监控趋势 | 增长过快 | DBSIZE |
| **驱逐次数** | 0 | >100/分钟 | evicted_keys |
| **连接数** | <100 | >500 | connected_clients |

### 监控命令

```bash
# 1. 实时监控Redis
redis-cli MONITOR

# 2. 查看慢查询
redis-cli SLOWLOG GET 10

# 3. 查看统计信息
redis-cli INFO stats

# 4. 查看内存使用
redis-cli INFO memory

# 5. 查看客户端连接
redis-cli CLIENT LIST
```

### 监控脚本

```bash
#!/bin/bash
# scripts/monitor_cache.sh

# 阈值配置
HIT_RATE_THRESHOLD=0.7
MEMORY_THRESHOLD=0.9
EVICTION_THRESHOLD=100

# 获取缓存统计
STATS=$(curl -s http://127.0.0.1:5001/api/cache/stats)
HIT_RATE=$(echo $STATS | jq -r '.hit_rate')

# 获取Redis内存使用
MEMORY_INFO=$(redis-cli INFO memory)
MEMORY_PERCENT=$(echo $MEMORY_INFO | grep used_memory_percentage | awk '{print $2}' | tr -d '\r')

# 获取驱逐次数
EVICTIONS=$(redis-cli INFO stats | grep evicted_keys | awk '{print $2}')

# 检查并告警
if (( $(echo "$HIT_RATE < $HIT_RATE_THRESHOLD" | bc -l) )); then
    echo "⚠️  WARNING: Cache hit rate below ${HIT_RATE_THRESHOLD}: ${HIT_RATE}"
fi

if (( $(echo "$MEMORY_PERCENT > $MEMORY_THRESHOLD" | bc -l) )); then
    echo "🔴 CRITICAL: Redis memory usage above ${MEMORY_THRESHOLD}: ${MEMORY_PERCENT}%"
fi

if [ "$EVICTIONS" -gt "$EVICTION_THRESHOLD" ]; then
    echo "⚠️  WARNING: Too many evictions: $EVICTIONS/minute"
fi
```

---

## 🔧 性能调优

### TTL优化

**原则**: 在数据新鲜度和性能之间找到平衡

| 数据类型 | 推荐TTL | 调优依据 |
|---------|---------|---------|
| 游戏基础信息 | 3600秒 | 变化频率低（小时级） |
| 事件列表 | 1800秒 | 变化频率中等（30分钟级） |
| 参数配置 | 7200秒 | 变化频率低（天级） |
| 实时统计 | 60秒 | 接近实时 |
| 用户会话 | 600秒 | 安全性考虑 |

**动态调整TTL**:
```python
def get_dynamic_ttl(data_type: str) -> int:
    """根据数据类型返回动态TTL"""
    ttl_map = {
        "games": 3600,
        "events": 1800,
        "params": 7200,
        "stats": 60,
    }
    return ttl_map.get(data_type, 600)

@cached(ttl=get_dynamic_ttl("events"))
def get_events(game_gid):
    pass
```

### 并发优化

```python
# 使用连接池
import redis.connection
redis.connection.ConnectionPool.from_url(
    f"redis://:{password}@{host}:{port}/{db}",
    max_connections=50
)
```

### 内存优化

```python
# 1. 使用数据压缩
import pickle
import zlib

def set_compressed(key, value, ttl):
    compressed = zlib.compress(pickle.dumps(value))
    cache.set(key, compressed, ttl)

def get_compressed(key):
    data = cache.get(key)
    if data:
        return pickle.loads(zlib.decompress(data))
    return None

# 2. 限制缓存对象大小
@cached(ttl=3600, max_size=1024*1024)  # 最多1MB
def get_large_data():
    pass

# 3. 分片缓存（大对象拆分为多个小对象）
def set_sharded(key, data, shard_size=1024*1024):
    serialized = pickle.dumps(data)
    shards = [serialized[i:i+shard_size] for i in range(0, len(serialized), shard_size)]
    for i, shard in enumerate(shards):
        cache.set(f"{key}:shard:{i}", shard, ttl=3600)
    cache.set(f"{key}:metadata", {"shard_count": len(shards)}, ttl=3600)

def get_sharded(key):
    metadata = cache.get(f"{key}:metadata")
    if not metadata:
        return None
    shards = []
    for i in range(metadata["shard_count"]):
        shard = cache.get(f"{key}:shard:{i}")
        if shard:
            shards.append(shard)
    return pickle.loads(b''.join(shards))
```

---

## 📈 容量规划

### 容量评估公式

```
总缓存容量 = (平均对象大小 × 缓存对象数量) / 命中率 / 内存利用率

示例：
- 平均对象大小: 10KB
- 缓存对象数量: 100,000
- 目标命中率: 80%
- 内存利用率: 70%

总缓存容量 = (10KB × 100,000) / 0.8 / 0.7
           = 1.79GB

推荐配置: 2GB Redis内存
```

### 实例规格建议

| 用户规模 | 并发数 | Redis内存 | 应用内存 | 实例规格 |
|---------|-------|----------|---------|---------|
| <1,000 | <50 | 512MB | 1GB | 2核4G |
| 1,000-10,000 | 50-500 | 2GB | 4GB | 4核8G |
| 10,000-100,000 | 500-5000 | 8GB | 16GB | 8核32G |
| >100,000 | >5000 | 32GB+ | 64GB+ | 16核64G+ |

### 扩容策略

**水平扩展** (推荐):
```
使用Redis Cluster或分片
- 每个分片最多处理50,000 QPS
- 建议每分片内存 <10GB
- 使用一致性哈希分配key
```

**垂直扩展**:
```
升级单机配置
- 简单但成本高
- 有单点故障风险
- 适合小规模应用
```

---

## 🔄 部署流程

### 首次部署

```bash
# 1. 安装Redis
brew install redis  # macOS
# 或
sudo apt-get install redis-server  # Ubuntu

# 2. 配置Redis
sudo cp redis.conf /etc/redis/redis.conf
sudo vim /etc/redis/redis.conf

# 3. 启动Redis
sudo systemctl start redis
sudo systemctl enable redis

# 4. 验证Redis
redis-cli ping  # 应输出 PONG

# 5. 设置Redis密码（可选）
redis-cli CONFIG SET requirepass "your-password"

# 6. 安装Python依赖
pip install redis pybloom-live

# 7. 配置环境变量
cp .env.example .env.production
vim .env.production

# 8. 初始化数据库
python3 scripts/setup/init_db.py

# 9. 预热缓存
python3 scripts/warmup_cache.py

# 10. 启动应用
python3 web_app.py
```

### 滚动更新（零停机）

```bash
# 1. 部署新版本到新服务器
scp -r backend/* user@new-server:/app/

# 2. 在新服务器预热缓存
ssh user@new-server "cd /app && python3 scripts/warmup_cache.py"

# 3. 验证新版本健康
curl http://new-server:5001/api/health

# 4. 切换流量
# 方法1: 使用负载均衡器
# 方法2: 更新DNS记录
# 方法3: 使用服务网格

# 5. 监控新版本
watch -n 5 'curl -s http://new-server:5001/api/cache/stats'
```

---

## 🛡️ 备份和恢复

### Redis备份

```bash
# 1. 手动备份（RDB）
redis-cli BGSAVE
# 备份文件位于: /var/lib/redis/dump.rdb

# 2. 自动备份（定时任务）
crontab -e
# 每天凌晨3点备份
0 3 * * * redis-cli BGSAVE && cp /var/lib/redis/dump.rdb /backup/redis/dump_$(date +\%Y\%m\%d).rdb

# 3. AOF备份（如果启用）
cp /var/lib/redis/appendonly.aof /backup/redis/appendonly_$(date +%Y%m%d).aof
```

### Redis恢复

```bash
# 1. 停止Redis
sudo systemctl stop redis

# 2. 恢复备份文件
cp /backup/redis/dump_20260225.rdb /var/lib/redis/dump.rdb

# 3. 启动Redis
sudo systemctl start redis

# 4. 验证数据
redis-cli DBSIZE
```

---

## 🚨 故障恢复

### 场景1: Redis服务崩溃

```bash
# 1. 检查Redis状态
sudo systemctl status redis

# 2. 查看Redis日志
sudo journalctl -u redis -n 100

# 3. 重启Redis
sudo systemctl restart redis

# 4. 如果重启失败，检查配置
redis-cli --test-memory 1  # 测试1GB内存

# 5. 应用会自动降级到L1缓存
# 确认降级模式已启用
grep DEGRADE_ENABLED backend/core/config/config.py
```

### 场景2: Redis内存不足

```bash
# 1. 查看内存使用
redis-cli INFO memory

# 2. 手动淘汰键
redis-cli --scan --pattern "cache:temp:*" | xargs redis-cli DEL

# 3. 如果持续OOM，增加maxmemory
redis-cli CONFIG SET maxmemory 2gb

# 4. 永久修改配置
vim /etc/redis/redis.conf
# maxmemory 2gb
```

### 场景3: 缓存雪崩（大量键同时过期）

```bash
# 1. 立即预热缓存
curl -X POST http://127.0.0.1:5001/api/cache/warmup

# 2. 添加随机TTL偏移（预防）
# 在代码中实现
import random

@cached(ttl=3600 + random.randint(0, 300))  # 3600-3900秒随机
def get_events(game_gid):
    pass
```

---

## 📞 支持和联系

- **故障排除手册**: [troubleshooting.md](./troubleshooting.md)
- **开发者指南**: [developer-guide.md](../development/developer-guide.md)
- **技术文档索引**: [README.md](../README.md)

---

**文档版本**: 1.0
**最后更新**: 2026-02-25
**相关文档**: [故障排除](./troubleshooting.md) | [快速开始](../quickstart/5-minute-guide.md)
