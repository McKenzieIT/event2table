# 缓存失效根因分析与修复方案

**日期**: 2026-03-12
**问题**: Fix #2 (智能缓存失效) 失败 - 统计API显示1条，搜索API返回0条
**方法**: Systematic Debugging + 3并行Subagent调查

---

## 根因分析总结

通过3个并行subagent调查，发现**3个独立的根因**：

### P0-1: 数据未保存到数据库 🔴 **最严重**

**发现**:
- 数据库中GID 90000176的event_nodes记录数 = **0**
- 数据库中总共仅有1条event_nodes记录 (GID 10000147)
- 这解释了为什么搜索API永远返回0条

**可能原因**:
1. **事务未提交**: 保存操作在事务中，但事务未提交
2. **API调用失败**: GraphQL mutation返回成功，但实际未写入数据库
3. **错误的数据库连接**: 可能连接到测试数据库而非生产数据库
4. **软删除逻辑错误**: 保存后立即被标记为`is_active=0`

**影响**:
- ❌ 搜索API返回0条 (正确 - 因为数据库确实没有)
- ❌ 统计API显示1条 (错误 - 缓存脏数据)
- ❌ 用户看到数据不一致

### P0-2: 缓存键不匹配 🔴

**发现**:
```python
# 统计API缓存键 (line 511)
@cached(ttl=300, key_prefix="event_nodes:stats")
def get_event_nodes_stats():
    # 缓存键: "event_nodes:stats:get_event_nodes_stats:..."

# @cache_invalidate装饰器失效 (line 197)
@cache_invalidate
def save_config():
    # 失效: "dashboard_statistics", "configs"
    # 未失效: "event_nodes:stats" ❌
```

**根本原因**:
- `@cache_invalidate`基于函数名推断缓存键
- `save_config()` → resource="config" → 失效"configs"
- 但统计API使用`event_nodes:stats`，不匹配

**影响**:
- ❌ 即使数据保存成功，统计显示5分钟内的旧缓存数据
- ❌ 用户看到更新后的节点数不正确

### P1-3: SQL查询错误的game_gid ⚠️

**发现**:
```sql
-- Repository层SQL (line 435)
SELECT COUNT(*) FROM event_nodes en
INNER JOIN log_events e ON en.event_id = e.id
WHERE e.game_gid = ? AND en.is_active = 1  -- ❌ 使用log_events.game_gid

-- 应该使用
WHERE en.game_gid = ? AND en.is_active = 1  -- ✅ 使用event_nodes.game_gid
```

**问题场景**:
1. `event_nodes.game_gid = 90000176` (正确)
2. `log_events.game_gid = NULL` (或不同值)
3. INNER JOIN成功，但WHERE `e.game_gid = 90000176`过滤掉该记录
4. 结果：计数为0，即使有有效节点

**影响**:
- ❌ 统计API返回0，即使数据库有记录
- ❌ 数据不一致

---

## 修复方案设计

### 方案1: 修复数据保存 (P0-1) 🔴

**策略**: 添加完整日志 + 验证保存流程

**实施步骤**:
```python
# backend/services/event_node_builder/__init__.py

@event_node_builder_bp.route("/api/save", methods=["POST"])
@cache_invalidate
def save_config():
    try:
        data = request.get_json()

        # ✅ 新增: 请求入口日志
        logger.info(
            f"[SAVE_CONFIG] Request received: game_gid={data.get('game_gid')}, "
            f"name={data.get('name')}, event_id={data.get('event_id')}"
        )

        # ... 验证代码 ...

        # ✅ 新增: 创建节点前的日志
        logger.debug(f"[SAVE_CONFIG] Creating node entity: {node_entity.model_dump()}")

        created_node = event_node_service.create_node(node_entity)

        # ✅ 新增: 创建成功日志
        logger.info(
            f"[SAVE_CONFIG] Node created successfully: "
            f"node_id={created_node.id}, game_gid={game_gid}"
        )

        # ✅ 新增: 验证数据库写入
        verification = event_node_service.find_by_id(created_node.id)
        if not verification:
            logger.error(
                f"[SAVE_CONFIG] CRITICAL: Node {created_node.id} not found in DB after creation!"
            )
            raise ValueError("Node creation verification failed")

        logger.debug(f"[SAVE_CONFIG] Verification passed: node exists in DB")

        # ... 后续代码 ...

    except Exception as e:
        logger.error(f"[SAVE_CONFIG] Error: {e}", exc_info=True)
        raise
```

**验证方法**:
```bash
# 1. 实时监控保存日志
tail -f logs/backend.log | grep "\[SAVE_CONFIG\]"

# 2. 验证数据库写入
sqlite3 data/dwd_generator.db "SELECT * FROM event_nodes WHERE game_gid = 90000176 ORDER BY created_at DESC LIMIT 1"

# 3. 对比保存前后
# 保存前: COUNT(*) = 0
# 保存后: COUNT(*) = 1
```

**预期结果**:
- 日志显示完整的保存流程
- 数据库中能看到新记录
- 搜索API能返回新节点

### 方案2: 修复缓存失效 (P0-2) 🔴

**策略**: 使用显式缓存失效装饰器替代自动推断装饰器

**选项A: 使用@invalidate_cache装饰器 (推荐)**
```python
# backend/services/event_node_builder/__init__.py

from backend.core.cache.decorators import invalidate_cache

@event_node_builder_bp.route("/api/save", methods=["POST"])
@invalidate_cache("event_nodes:stats:*")  # ✅ 显式指定失效模式
def save_config():
    # ... 保存逻辑 ...
```

**选项B: 手动失效缓存**
```python
@event_node_builder_bp.route("/api/save", methods=["POST"])
def save_config():
    try:
        # ... 保存逻辑 ...

        # ✅ 手动失效统计缓存
        from backend.core.cache.cache_system import _cache

        cache_pattern = f"event_nodes:stats:*"
        _cache.delete_pattern(cache_pattern)
        logger.info(f"✅ Invalidated cache pattern: {cache_pattern}")

        # ... 返回响应 ...

    except Exception as e:
        logger.error(f"Error: {e}")
```

**选项C: 修改@cache_invalidate装饰器接受参数**
```python
# backend/core/cache/decorators.py

def cache_invalidate(func: Callable) -> Callable:
    """
    ⚡ PERF: 自动缓存失效装饰器

    Args:
        func: 需要自动失效缓存的函数
        invalid_keys: 额外需要失效的缓存键列表 (可选)
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        # 自动失效dashboard_statistics
        _cache.delete("dashboard_statistics")

        # 根据函数名推断资源键
        # ... 原有逻辑 ...

        # ✅ 新增: 支持显式指定额外的缓存键
        if hasattr(func, '_invalidate_keys'):
            for key_pattern in func._invalidate_keys:
                _cache.delete_pattern(key_pattern)
                logger.info(f"✅ Invalidated custom cache: {key_pattern}")

        return result

    return wrapper

# 使用示例
@cache_invalidate
def save_config():
    # ... 保存逻辑 ...

save_config._invalidate_keys = ["event_nodes:stats:*"]
```

**推荐**: **选项A** (使用`@invalidate_cache`装饰器)，因为：
- ✅ 现有装饰器，无需修改
- ✅ 显式指定，清晰明确
- ✅ 支持模式匹配 (`*`通配符)

### 方案3: 修复SQL查询 (P1-3) ⚠️

**策略**: 修改WHERE条件使用正确的game_gid字段

**实施代码**:
```python
# backend/models/repositories/event_node_repository.py

def count_by_game_gid(self, game_gid: int) -> int:
    """统计指定游戏的节点数量 (ERS架构)"""
    query = """
        SELECT COUNT(DISTINCT en.id) as count
        FROM event_nodes en
        INNER JOIN log_events e ON en.event_id = e.id
        WHERE en.game_gid = ? AND en.is_active = 1  -- ✅ 修复: 使用en.game_gid
    """
    result = fetch_one_as_dict(query, (game_gid,))
    return result["count"] if result else 0
```

**验证方法**:
```sql
-- 修复前 (错误)
SELECT COUNT(*) FROM event_nodes en
INNER JOIN log_events e ON en.event_id = e.id
WHERE e.game_gid = 90000176 AND en.is_active = 1;
-- 结果: 0 (因为使用错误的game_gid)

-- 修复后 (正确)
SELECT COUNT(*) FROM event_nodes en
INNER JOIN log_events e ON en.event_id = e.id
WHERE en.game_gid = 90000176 AND en.is_active = 1;
-- 结果: 1 (使用正确的game_gid)
```

---

## 并行修复执行计划

由于3个问题相互独立，可以**并行修复**：

### Phase 1: 准备工作 (5分钟)
1. 备份当前代码
2. 创建测试数据库快照
3. 准备监控脚本

### Phase 2: 并行实施 (15分钟)
```
┌─────────────────┬─────────────────┬─────────────────┐
│  Fix P0-1       │  Fix P0-2       │  Fix P1-3       │
│  (添加日志)      │  (缓存失效)      │  (SQL修复)      │
├─────────────────┼─────────────────┼─────────────────┤
│ 1. 添加入口日志 │ 1. 替换装饰器   │ 1. 修改WHERE条件 │
│ 2. 添加成功日志 │ 2. 验证缓存键   │ 2. 运行SQL测试   │
│ 3. 添加验证逻辑 │ 3. 测试失效     │ 3. 对比结果     │
└─────────────────┴─────────────────┴─────────────────┘
```

### Phase 3: 集成测试 (10分钟)
1. 清空测试数据 (GID 90000176)
2. 创建新节点 (保存API)
3. 验证数据库写入
4. 验证缓存失效
5. 验证统计准确性
6. 验证搜索API

### Phase 4: E2E验证 (5分钟)
1. 打开前端页面
2. 创建节点配置
3. 保存配置
4. 检查统计数字
5. 检查搜索结果
6. 确认一致性

---

## 验证清单

### P0-1: 数据保存验证
- [ ] 日志显示`[SAVE_CONFIG] Request received`
- [ ] 日志显示`[SAVE_CONFIG] Node created successfully`
- [ ] 日志显示`[SAVE_CONFIG] Verification passed`
- [ ] 数据库查询返回新记录
- [ ] `SELECT COUNT(*) > 0`

### P0-2: 缓存失效验证
- [ ] 保存后日志显示`Invalidated cache pattern: event_nodes:stats:*`
- [ ] 统计API返回最新数字 (非缓存值)
- [ ] 等待5分钟后，统计仍然准确

### P1-3: SQL修复验证
- [ ] 直接SQL查询返回正确计数
- [ ] Repository方法返回相同计数
- [ ] 统计API返回相同计数

---

## 预期效果

修复前:
```
统计API: "1 事件节点总数" (缓存脏数据)
搜索API: "暂无事件节点" (数据库确实为空)
❌ 数据不一致
```

修复后:
```
统计API: "1 事件节点总数" (准确)
搜索API: 显示1个节点 (准确)
✅ 数据一致
```

创建新节点后:
```
统计API: "2 事件节点总数" (实时更新)
搜索API: 显示2个节点 (包含新节点)
✅ 数据一致性 + 实时更新
```

---

## 风险评估

### 低风险
- ✅ 修改仅限于event_node_builder模块
- ✅ 不影响其他游戏的数据
- ✅ 向后兼容 (仅添加功能)

### 中风险
- ⚠️ 缓存失效可能影响性能 (每次保存都清理)
- ⚠️ 日志过多可能影响性能 (可通过日志级别控制)

### 缓解措施
- 使用DEBUG级别记录详细日志
- 使用INFO级别记录关键操作
- 定期清理日志文件

---

## 下一步行动

1. ✅ 完成根因分析 (已完成)
2. ⏳ 设计修复方案 (已完成)
3. ⏳ 用户批准修复方案
4. ⏳ 并行实施3个修复
5. ⏳ 集成测试
6. ⏳ E2E验证
7. ⏳ 更新文档

**预计总时间**: 35分钟 (准备5 + 实施15 + 测试10 + E2E 5)
