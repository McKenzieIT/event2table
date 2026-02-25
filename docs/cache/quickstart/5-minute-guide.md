# Event2Table 缓存系统 - 5分钟快速开始指南

> **面向**: 新用户、开发者
> **目标**: 5分钟内掌握缓存系统核心用法
> **前置要求**: Redis服务已启动

---

## 缓存带来的3个核心价值 ⚡

### 1. 性能提升 100-1000倍
```
无缓存: 500ms (数据库查询)
有缓存: 5ms (L1内存) / 50ms (L2 Redis)
```

### 2. 数据库负载降低 80%
- 缓存命中时无需查询数据库
- 高并发场景下数据库压力骤减

### 3. 用户体验提升
- API响应时间从秒级降到毫秒级
- 页面加载更流畅

---

## 3步快速配置 ⚙️

### 步骤1: 验证Redis连接 (1分钟)

```bash
# 检查Redis服务状态
redis-cli ping

# 应输出: PONG

# 如果未启动，启动Redis
redis-server
```

### 步骤2: 启用缓存装饰器 (2分钟)

在需要缓存的后端函数上添加 `@cached` 装饰器：

```python
from backend.core.cache.decorators import cached

@cached(ttl=3600)  # 缓存1小时
def get_events(game_gid: int):
    """获取游戏的所有事件"""
    return fetch_all_as_dict(
        'SELECT * FROM log_events WHERE game_gid = ?',
        (game_gid,)
    )

@cached(ttl=1800)  # 缓存30分钟
def get_parameters(game_gid: int):
    """获取游戏的所有参数"""
    return fetch_all_as_dict(
        'SELECT ep.* FROM event_params ep
         INNER JOIN log_events le ON ep.event_id = le.id
         WHERE le.game_gid = ?',
        (game_gid,)
    )
```

**TTL选择建议**:
- 游戏基础信息: `3600秒` (1小时)
- 事件列表: `1800秒` (30分钟)
- 参数配置: `7200秒` (2小时)
- 实时统计数据: `60秒` (1分钟)

### 步骤3: 数据更新时清理缓存 (2分钟)

当数据发生变化时，使用 `@cache_invalidate` 清理缓存：

```python
from backend.core.cache.decorators import cached, cache_invalidate

@cached(ttl=3600)
def get_events(game_gid: int):
    return fetch_all_as_dict(
        'SELECT * FROM log_events WHERE game_gid = ?',
        (game_gid,)
    )

@cache_invalidate
def create_event(game_gid: int, event_data: dict):
    """创建新事件时自动清理缓存"""
    # 插入数据库
    event_id = insert_event(event_data)

    # 返回后，get_events(game_gid) 的缓存会自动失效
    return event_id

@cache_invalidate
def update_event(event_id: int, event_data: dict):
    """更新事件时自动清理缓存"""
    # 更新数据库
    update_event_in_db(event_id, event_data)

    # 返回后，相关缓存会自动失效

@cache_invalidate
def delete_event(event_id: int):
    """删除事件时自动清理缓存"""
    # 删除数据库记录
    delete_event_from_db(event_id)

    # 返回后，相关缓存会自动失效
```

---

## 验证缓存生效 ✅

### 方法1: 查看HTTP响应头

```bash
# 第一次请求（缓存未命中）
curl -i http://127.0.0.1:5001/api/events?game_gid=10000147

# 响应头应包含:
# X-Cache-Status: MISS

# 第二次请求（缓存命中）
curl -i http://127.0.0.1:5001/api/events?game_gid=10000147

# 响应头应包含:
# X-Cache-Status: HIT
```

### 方法2: 使用缓存API

```bash
# 查看缓存统计
curl http://127.0.0.1:5001/api/cache/stats

# 返回示例:
{
  "hits": 1450,
  "misses": 230,
  "hit_rate": 0.863,  # 命中率86.3%
  "total_keys": 520
}
```

### 方法3: Redis直接查看

```bash
# 查看所有缓存键
redis-cli KEYS "cache:*"

# 查看特定缓存
redis-cli GET "cache:events:10000147"

# 查看缓存TTL（剩余时间）
redis-cli TTL "cache:events:10000147"
```

---

## 常见问题速查 📚

### Q: 缓存未生效怎么办？

**检查清单**:
1. ✅ Redis服务是否启动？`redis-cli ping`
2. ✅ 装饰器是否正确应用？检查函数上有 `@cached(ttl=xxx)`
3. ✅ TTL是否合理？`ttl=0` 会导致缓存立即过期
4. ✅ 缓存键是否冲突？不同函数使用不同的键前缀

### Q: 数据更新后缓存未清理？

**解决方案**:
```python
# ❌ 错误: 直接修改数据库，缓存未清理
def update_event(event_id, data):
    db.execute("UPDATE log_events SET ...")

# ✅ 正确: 使用 @cache_invalidate
@cache_invalidate
def update_event(event_id, data):
    db.execute("UPDATE log_events SET ...")
```

### Q: 如何禁用缓存？

```python
# 方法1: 设置TTL=0
@cached(ttl=0)
def get_events(game_gid):
    pass  # 缓存立即过期，相当于禁用

# 方法2: 临时移除装饰器
# @cached(ttl=3600)  # 注释掉装饰器
def get_events(game_gid):
    pass
```

### Q: 缓存占用内存过大？

```bash
# 查看Redis内存使用
redis-cli INFO memory

# 清理所有缓存（慎用！）
redis-cli FLUSHALL

# 清理特定前缀的缓存
redis-cli --scan --pattern "cache:events:*" | xargs redis-cli DEL
```

---

## 下一步学习 🎯

你已经掌握了基础用法，接下来可以学习：

1. **[故障排除手册](../operations/troubleshooting.md)** - 解决常见问题
2. **[开发者指南](../development/developer-guide.md)** - 深入了解高级功能
3. **[部署运维文档](../operations/deployment.md)** - 生产环境配置

---

## 快速代码片段参考 📝

### 基础缓存
```python
from backend.core.cache.decorators import cached

@cached(ttl=3600)
def get_games():
    return fetch_all_as_dict('SELECT * FROM games')
```

### 参数化缓存键
```python
@cached(ttl=1800)
def get_event(event_id: int):
    return fetch_one_as_dict(
        'SELECT * FROM log_events WHERE id = ?',
        (event_id,)
    )
```

### 缓存失效
```python
from backend.core.cache.decorators import cache_invalidate

@cache_invalidate
def create_game(game_data: dict):
    return insert_game(game_data)
```

### 自定义缓存键
```python
from backend.core.cache.decorators import cached

@cached(ttl=3600, key_prefix="custom:games")
def get_games_list():
    return fetch_all_as_dict('SELECT * FROM games')
```

---

**文档版本**: 1.0
**最后更新**: 2026-02-25
**相关文档**: [README](../README.md) | [FAQ](./faq.md) | [故障排除](../operations/troubleshooting.md)
