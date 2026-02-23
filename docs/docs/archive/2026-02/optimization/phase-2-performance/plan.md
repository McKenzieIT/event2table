# Phase 2: 性能优化

> **阶段**: P2 - 高优先级 | **预计时间**: 3-4小时 | **并行任务**: 3个

---

## 📋 优化清单

### 问题1: N+1查询 - common_params同步函数 🔴 高

**位置**: `backend/services/parameters/common_params.py:123-131`

**问题**: 循环中为每个事件单独查询参数列表

**当前代码**:
```python
# ❌ N+1查询：每个event单独查询
for event in events:
    params = fetch_all_as_dict(
        "SELECT param_name, param_name_cn FROM event_params WHERE event_id = ?",
        (event["id"],)
    )
```

**修复方案**:
```python
# ✅ 批量查询
event_ids = [e["id"] for e in events]
placeholders = ",".join(["?"] * len(event_ids))
all_params = fetch_all_as_dict(
    f"SELECT event_id, param_name, param_name_cn FROM event_params WHERE event_id IN ({placeholders})",
    tuple(event_ids)
)

# 按event_id分组
params_by_event = {}
for param in all_params:
    event_id = param["event_id"]
    if event_id not in params_by_event:
        params_by_event[event_id] = []
    params_by_event[event_id].append(param)

# 分配给事件
for event in events:
    event["params"] = params_by_event.get(event["id"], [])
```

**性能提升**: 100次查询 → 1次查询（99%↓）

---

### 问题2: N+1查询 - 事件导入器 🔴 高

**位置**: `backend/services/events/event_importer.py:53-96`

**问题**: 批量导入时对每个事件执行多次独立查询

**修复方案**:
```python
# ✅ 预加载已存在的事件
event_names = [e.event_code for e in events_data]
placeholders = ",".join(["?"] * len(event_names))
existing_events = fetch_all_as_dict(
    f"SELECT event_name FROM log_events WHERE game_gid = ? AND event_name IN ({placeholders})",
    (game_gid, *event_names)
)
existing_set = {e["event_name"] for e in existing_events}

# 批量插入新事件
new_events = [e for e in events_data if e.event_code not in existing_set]
# ... 批量插入逻辑
```

---

### 问题3: N+1查询 - 参数库批量检查 🔴 高

**位置**: `backend/api/routes/parameters.py:725-750`

**问题**: 循环中执行独立查询

**修复方案**:
```python
# ✅ 批量查询
param_conditions = []
param_values = []
for param in parameters:
    param_conditions.append("(param_name = ? AND template_id = ?)")
    param_values.extend([param["param_name"], param["template_id"]])

where_clause = " OR ".join(param_conditions)
library_params = fetch_all_as_dict(
    f"SELECT * FROM param_library WHERE {where_clause}",
    tuple(param_values)
)
```

---

### 问题4: 重复的game_gid转换（3处）🟠 中

**位置**: `backend/api/routes/parameters.py:217-246, 333-356, 536-559`

**问题**: 同一请求中多次执行 `SELECT id FROM games WHERE gid = ?`

**修复方案**:
```python
# ✅ 使用Flask请求上下文缓存
from flask import g

def get_game_id_from_gid_cached(game_gid: int) -> Optional[int]:
    """带缓存的game_gid转game_id"""
    cache_key = f"game_id_{game_gid}"
    if cache_key in g:
        return g.get(cache_key)
    
    game = fetch_one_as_dict("SELECT id FROM games WHERE gid = ?", (game_gid,))
    if game:
        g.set(cache_key, game["id"])
        return game["id"]
    return None
```

---

### 问题5: 缺少分页限制（2处）🟠 中

**位置**:
- `backend/api/routes/flows.py:79-86`
- `backend/services/event_node_builder/__init__.py:493`

**问题**: 查询没有LIMIT限制，大数据量可能导致内存问题

**修复方案**:
```python
# ✅ 添加分页参数
def list_flows():
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 50, type=int)
    page_size = min(page_size, 100)  # 限制最大100
    
    offset = (page - 1) * page_size
    flows = fetch_all_as_dict(
        "SELECT * FROM flow_templates WHERE ... ORDER BY updated_at DESC LIMIT ? OFFSET ?",
        (page_size, offset)
    )
```

---

### 问题6: Dashboard统计多次独立查询 🟠 中

**位置**: `backend/api/routes/dashboard.py:121-221`

**问题**: 6个独立COUNT查询

**修复方案**:
```python
# ✅ 合并为联合查询
stats = fetch_one_as_dict("""
    SELECT
        (SELECT COUNT(*) FROM games) as total_games,
        (SELECT COUNT(*) FROM log_events) as total_events,
        (SELECT COUNT(*) FROM event_params) as total_params,
        (SELECT COUNT(*) FROM flow_templates WHERE is_active = 1) as total_flows
""")
```

---

### 问题7: 参数统计查询未使用索引优化 🟠 中

**位置**: `backend/api/routes/parameters.py:359-403`

**问题**: 4个独立统计查询可合并，且缺少复合索引

**修复方案**:
```python
# 1. 添加数据库索引
# migration/add_indexes.sql
CREATE INDEX IF NOT EXISTS idx_event_params_event_active 
ON event_params(event_id, is_active);

CREATE INDEX IF NOT EXISTS idx_log_events_game_gid 
ON log_events(game_gid);

# 2. 合并统计查询
stats = fetch_one_as_dict("""
    SELECT
        COUNT(*) as total,
        SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active,
        SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) as inactive
    FROM event_params
    WHERE event_id IN (SELECT id FROM log_events WHERE game_gid = ?)
""", (game_gid,))
```

---

### 问题8: 批量删除游戏时逐个检查关联 🟠 中

**位置**: `backend/api/routes/games.py:568-580`

**问题**: 循环中为每个游戏单独查询事件数量

**修复方案**:
```python
# ✅ 批量检查
gids = [g["gid"] for g in games]
placeholders = ",".join(["?"] * len(gids))
event_counts = fetch_all_as_dict(
    f"SELECT game_gid, COUNT(*) as count FROM log_events WHERE game_gid IN ({placeholders}) GROUP BY game_gid",
    tuple(gids)
)
count_map = {e["game_gid"]: e["count"] for e in event_counts}

# 检查每个游戏
for game in games:
    event_count = count_map.get(game["gid"], 0)
    if event_count > 0:
        errors.append(f"Game {game['name']} has {event_count} events")
```

---

### 问题9: 缓存使用不一致 🟡 低

**位置**: `backend/api/routes/events.py` vs `backend/api/routes/games.py`

**问题**: games.py使用Flask-Caching，events.py未使用

**修复方案**: 统一使用Flask-Caching或分层缓存系统

---

### 问题10: event_nodes搜索分页硬编码 🟡 低

**位置**: `backend/services/event_node_builder/__init__.py:493`

**问题**: `LIMIT 100` 是硬编码值

**修复方案**: 支持分页参数，参考问题5

---

## 🚀 执行计划

### 并行subagent任务分配

```
Subagent 1: 修复N+1查询问题（高优先级）
├── services/parameters/common_params.py (批量查询)
├── services/events/event_importer.py (预加载)
└── api/routes/parameters.py (批量检查)

Subagent 2: 优化数据库查询和索引
├── api/routes/parameters.py (重复转换 + 统计合并)
├── api/routes/dashboard.py (统计合并)
├── api/routes/games.py (批量检查)
└── 创建数据库迁移脚本（添加索引）

Subagent 3: 添加分页和缓存优化
├── api/routes/flows.py (分页)
├── services/event_node_builder/__init__.py (分页)
└── 统一缓存使用策略
```

---

## ✅ 验证步骤

1. **性能测试**:
   ```bash
   # 运行性能测试
   pytest backend/test/unit/core/cache/test_cache_performance.py -v
   ```

2. **查询分析**:
   ```bash
   # 启用SQL查询日志
   sqlite3 data/dwd_generator.db
   .expert
   .eqp on
   SELECT ...  # 查看查询计划
   ```

3. **基准测试**:
   - 记录优化前后的API响应时间
   - 验证大数据量场景（1000+事件）

---

## 🎯 预期成果

- ✅ 3个N+1查询修复，性能提升80-99%
- ✅ 数据库索引优化，查询速度提升50%+
- ✅ 分页和缓存优化，内存占用降低30%
- ✅ 统计查询合并，API响应时间降低40%

**性能提升预测**:
- API P95响应时间: 79.75ms → <50ms (37%↓)
- 大数据量场景响应时间: 2-3s → <500ms (75%↓)

**下一步**: [Phase 3 - 架构重构](../phase-3-architecture/plan.md)
