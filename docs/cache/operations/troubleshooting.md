# 缓存系统故障排除手册

> **面向**: 运维人员、开发者
> **目标**: 10分钟内解决80%的常见问题
> **版本**: 1.0

---

## 🚨 紧急故障处理流程

当遇到缓存故障时，按以下优先级处理：

```
1️⃣ 确认问题影响范围 (用户、功能、数据)
2️⃣ 检查Redis服务状态 (redis-cli ping)
3️⃣ 查看应用日志 (logs/app.log | grep -i cache)
4️⃣ 查看缓存统计 (curl /api/cache/stats)
5️⃣ 根据症状定位问题 (参考下文)
6️⃣ 应用修复方案
7️⃣ 验证问题已解决
```

---

## 🔴 P0 级别问题（影响所有用户）

### 问题1: 所有API返回500错误

**症状**:
- 所有API请求都返回500错误
- 应用日志显示Redis连接错误
- 用户完全无法访问系统

**紧急处理** (2分钟内完成):

```bash
# 1. 检查Redis服务
redis-cli ping

# 2. 如果Redis未启动，启动Redis
brew services start redis  # macOS
# 或
sudo systemctl start redis  # Linux

# 3. 如果Redis启动失败，启用缓存降级模式
# 修改环境变量
export CACHE_DEGRADE_MODE=true
# 重启应用
python3 web_app.py
```

**根本原因排查**:
```bash
# 检查Redis日志
tail -f /usr/local/var/log/redis.log  # macOS
# 或
journalctl -u redis -f  # Linux

# 常见原因:
# - Redis进程被杀掉
# - Redis内存不足
# - Redis配置错误
```

**预防措施**:
- 配置Redis自动重启
- 启用缓存降级策略
- 监控Redis服务状态

---

### 问题2: 缓存命中率突然降到0%

**症状**:
- 监控显示缓存命中率从80%降到<10%
- API响应时间显著增加
- 数据库负载激增

**诊断步骤**:
```bash
# 1. 查看缓存统计
curl http://127.0.0.1:5001/api/cache/stats

# 2. 检查Redis是否FLUSHALL
redis-cli DBSIZE  # 应显示>0，如果为0说明被清空

# 3. 检查是否有大量缓存失效
redis-cli --scan --pattern "cache:*" | wc -l
```

**解决方案**:

**场景A: Redis被FLUSHALL (缓存被清空)**
```bash
# 预热缓存（恢复常用数据）
curl -X POST http://127.0.0.1:5001/api/cache/warmup

# 检查是否有定时任务误执行FLUSHALL
crontab -l | grep redis
```

**场景B: TTL设置过短**
```python
# 检查代码中的TTL设置
grep -r "@cached(ttl=" backend/

# 调整过短的TTL
# @cached(ttl=60)  # ❌ 太短
@cached(ttl=1800)  # ✅ 调整为30分钟
```

**场景C: 缓存键冲突**
```python
# 添加key_prefix避免冲突
@cached(ttl=3600, key_prefix="events:game")
def get_events(game_gid):
    pass
```

---

### 问题3: Redis内存使用率>90%

**症状**:
- `redis-cli INFO memory` 显示 `used_memory_percentage > 90`
- Redis开始淘汰键（evictions增加）
- 缓存命中率下降

**紧急处理** (5分钟内完成):

```bash
# 1. 查看内存使用详情
redis-cli INFO memory

# 2. 查看大对象（>1MB）
redis-cli --bigkeys

# 3. 清理不需要的缓存（谨慎！）
# 方法1: 清理特定前缀
redis-cli --scan --pattern "cache:temp:*" | xargs redis-cli DEL

# 方法2: 清理所有缓存（慎用！）
redis-cli FLUSHALL
```

**长期解决方案**:

**配置最大内存**:
```bash
# redis.conf
maxmemory 1gb
maxmemory-policy allkeys-lru  # 淘汰最少使用的键
```

**优化缓存策略**:
```python
# 减少大对象缓存
# ❌ 不要缓存整个大表
@cached(ttl=3600)
def get_all_logs():  # 可能有百万行
    return fetch_all_as_dict('SELECT * FROM logs')

# ✅ 改为分页缓存
@cached(ttl=600, key_prefix="logs:page")
def get_logs_page(page: int, size: int = 100):
    return fetch_all_as_dict(
        'SELECT * FROM logs LIMIT ? OFFSET ?',
        (size, page * size)
    )
```

---

## 🟡 P1 级别问题（影响部分用户）

### 问题4: 特定游戏数据缓存未生效

**症状**:
- 某个游戏的API返回旧数据
- 其他游戏正常
- 数据库已更新，但API仍返回旧数据

**诊断步骤**:
```bash
# 1. 检查特定游戏的缓存
redis-cli GET "cache:games:10000147"

# 2. 检查是否有残留缓存
redis-cli KEYS "*10000147*"

# 3. 手动清理该游戏的所有缓存
redis-cli --scan --pattern "*10000147*" | xargs redis-cli DEL
```

**解决方案**:

**原因1: 数据更新后未清理缓存**
```python
# 确保使用@cache_invalidate装饰器
@cache_invalidate
def update_game(game_gid, data):
    execute_update('UPDATE games SET ... WHERE gid = ?', (game_gid,))
```

**原因2: 缓存键不一致**
```python
# 检查缓存键是否一致
# ❌ 不一致的键
cache.set("game_10000147", data)
cache.get("games:10000147")  # 键不匹配

# ✅ 使用统一的键格式
cache.set(f"games:{game_gid}", data)
cache.get(f"games:{game_gid}")
```

---

### 问题5: 缓存导致数据不一致

**症状**:
- 用户A修改数据后，用户B仍看到旧数据
- 不同API返回的数据不一致
- 数据库和API返回不一致

**诊断步骤**:
```bash
# 1. 对比数据库和缓存数据
# 数据库
sqlite3 data/dwd_generator.db "SELECT * FROM games WHERE gid = 10000147;"

# 缓存
redis-cli GET "cache:games:10000147"

# 2. 检查缓存TTL
redis-cli TTL "cache:games:10000147"
```

**解决方案**:

**立即修复**: 清理不一致的缓存
```bash
# 清理特定缓存
redis-cli DEL "cache:games:10000147"

# 或清理所有缓存（如果不确定范围）
redis-cli FLUSHALL
```

**长期修复**: 确保数据更新时清理缓存
```python
from backend.core.cache.decorators import cache_invalidate

@cache_invalidate
def update_game(game_gid: int, data: dict):
    """更新游戏，自动清理相关缓存"""
    execute_update(
        'UPDATE games SET name = ?, description = ? WHERE gid = ?',
        (data['name'], data['description'], game_gid)
    )
    # 装饰器自动清理所有相关缓存
```

---

### 问题6: 新部署后缓存未预热

**症状**:
- 新部署的应用首次访问很慢
- 数据库负载高
- 用户体验差

**解决方案**:

**自动预热** (推荐):
```python
# scripts/warmup_cache.py
from backend.core.cache.cache_system import cache_result
from backend.core.database.converters import fetch_all_as_dict

def warmup_cache():
    """应用启动时预热缓存"""
    print("Warming up cache...")

    # 预热游戏列表
    games = fetch_all_as_dict('SELECT * FROM games WHERE active = 1')
    for game in games:
        cache_result.set(f"games:{game['gid']}", game, ttl=3600)

    print(f"Cache warmed up: {len(games)} games")

if __name__ == "__main__":
    warmup_cache()
```

**启动脚本**:
```bash
#!/bin/bash
# scripts/start_with_warmup.sh

# 启动应用
python3 web_app.py &
APP_PID=$!

# 等待应用启动
sleep 5

# 预热缓存
python3 scripts/warmup_cache.py

echo "Application started and cache warmed up"
wait $APP_PID
```

---

## 🟢 P2 级别问题（不影响主要功能）

### 问题7: 缓存统计不准确

**症状**:
- 命中率计算错误
- 统计数据与实际不符

**诊断**:
```bash
# 重置统计
curl -X POST http://127.0.0.1:5001/api/cache/stats/reset

# 等待5分钟，重新查看
curl http://127.0.0.1:5001/api/cache/stats
```

**原因**:
- 统计计数器溢出
- 统计重置时机不当

**解决方案**: 定期重置统计（如每天凌晨）
```python
import schedule
import time

def reset_cache_stats():
    from backend.core.cache.monitoring import CacheMonitor
    monitor = CacheMonitor()
    monitor.reset_stats()
    print("Cache stats reset")

# 每天凌晨3点重置
schedule.every().day.at("03:00").do(reset_cache_stats)

while True:
    schedule.run_pending()
    time.sleep(60)
```

---

### 问题8: 日志中大量缓存相关警告

**症状**:
- 日志显示大量 "Cache miss" 警告
- 日志增长过快

**解决方案**:

**调整日志级别**:
```python
# backend/core/config/config.py
import logging

# 生产环境使用INFO级别
logging.getLogger("backend.core.cache").setLevel(logging.INFO)

# 开发环境使用DEBUG级别
if os.environ.get("FLASK_ENV") == "development":
    logging.getLogger("backend.core.cache").setLevel(logging.DEBUG)
```

---

## 🛠️ 故障诊断工具

### 诊断脚本

```bash
#!/bin/bash
# scripts/diagnose_cache.sh

echo "=== 缓存系统诊断 ==="
echo ""

echo "1. Redis服务状态:"
redis-cli ping || echo "❌ Redis服务未启动"
echo ""

echo "2. Redis内存使用:"
redis-cli INFO memory | grep used_memory
echo ""

echo "3. 缓存统计:"
curl -s http://127.0.0.1:5001/api/cache/stats | python3 -m json.tool
echo ""

echo "4. 缓存键数量:"
echo "Total keys: $(redis-cli DBSIZE)"
echo ""

echo "5. 慢查询:"
redis-cli SLOWLOG GET 5
echo ""

echo "6. 应用日志（最近10条缓存相关）:"
tail -n 100 logs/app.log | grep -i cache | tail -n 10
echo ""

echo "=== 诊断完成 ==="
```

### 监控面板

```python
# backend/api/routes/cache_monitoring.py
from flask import jsonify
from backend.core.cache.monitoring import CacheMonitor

@cache_bp.route('/monitoring/health')
def cache_health_check():
    """缓存健康检查"""
    monitor = CacheMonitor()

    stats = {
        "status": "healthy",
        "redis_connected": monitor.is_redis_connected(),
        "hit_rate": monitor.get_hit_rate(),
        "memory_usage": monitor.get_memory_usage(),
        "total_keys": monitor.get_total_keys(),
        "alerts": []
    }

    # 告警检查
    if stats["hit_rate"] < 0.7:
        stats["alerts"].append("Hit rate below 70%")
        stats["status"] = "warning"

    if stats["memory_usage"] > 0.9:
        stats["alerts"].append("Memory usage above 90%")
        stats["status"] = "critical"

    if not stats["redis_connected"]:
        stats["alerts"].append("Redis disconnected")
        stats["status"] = "critical"

    return jsonify(stats)
```

---

## 📞 需要帮助？

如果以上方法都无法解决问题：

1. **收集诊断信息**:
   ```bash
   bash scripts/diagnose_cache.sh > cache_diagnostic.txt
   ```

2. **查看详细日志**:
   ```bash
   tail -n 500 logs/app.log | grep -i cache > cache_logs.txt
   ```

3. **参考更多文档**:
   - [快速开始指南](../quickstart/5-minute-guide.md)
   - [常见问题FAQ](../quickstart/faq.md)
   - [开发者指南](../development/developer-guide.md)

---

## 🔄 回滚方案

如果新引入的缓存功能导致问题，紧急回滚方案：

### 方案1: 禁用缓存（5分钟）

```python
# backend/core/config/config.py
CACHE_ENABLED = False  # 全局禁用缓存
```

### 方案2: 缩短TTL（临时）

```python
# 将所有TTL临时设置为60秒
@cached(ttl=60)  # 从3600改为60
def get_events(game_gid):
    pass
```

### 方案3: 切换到仅L1缓存

```python
# 禁用Redis，仅使用L1内存缓存
REDIS_ENABLED = False
L1_CACHE_ENABLED = True
```

---

**文档版本**: 1.0
**最后更新**: 2026-02-25
**相关文档**: [快速开始](../quickstart/5-minute-guide.md) | [FAQ](../quickstart/faq.md) | [部署运维](../operations/deployment.md)
