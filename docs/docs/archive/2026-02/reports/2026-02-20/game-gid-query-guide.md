# Game GID迁移后 - 查询指南

**日期**: 2026-02-20
**迁移状态**: ✅ 已完成
**影响范围**: log_events, event_nodes 等表

---

## 🔍 核心变化

### 迁移前

```sql
-- ❌ 旧方式：使用 game_id（数据库自增ID）
SELECT * FROM log_events WHERE game_id = 58;
SELECT * FROM event_nodes WHERE game_id = 58;
```

**问题**:
- `game_id` 是数据库自增ID，可能因重建数据库而变化
- 不是业务层面的唯一标识符
- 违反了数据架构设计原则

### 迁移后

```sql
-- ✅ 新方式：使用 game_gid（业务GID）
SELECT * FROM log_events WHERE game_gid = 10000147;
SELECT * FROM event_nodes WHERE game_gid = 10000147;
```

**优势**:
- `game_gid` 是业务层面的唯一标识符（如 10000147 = STAR001）
- 稳定不变，不因数据库重建而变化
- 符合数据架构设计原则

---

## 📊 表结构变化

### log_events 表

**迁移前**:
```sql
CREATE TABLE log_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,          -- ❌ 数据库自增ID
    event_name TEXT NOT NULL,
    ...
    game_gid INTEGER,                  -- ✅ 业务GID
    ...
);
```

**迁移后**:
```sql
CREATE TABLE log_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_name TEXT NOT NULL,
    ...
    game_gid INTEGER NOT NULL,         -- ✅ 只有业务GID
    ...
);
```

### event_nodes 表

**迁移前**:
```sql
CREATE TABLE event_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,          -- ❌ 数据库自增ID
    name TEXT NOT NULL,
    ...
    game_gid INTEGER,                  -- ✅ 业务GID
    ...
);
```

**迁移后**:
```sql
CREATE TABLE event_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_gid INTEGER NOT NULL,         -- ✅ 只有业务GID
    name TEXT NOT NULL,
    ...
);
```

---

## 🔧 查询示例

### 1. 查询游戏的 所有事件

```sql
-- ✅ 迁移后：使用 game_gid
SELECT
    id,
    event_name,
    event_name_cn,
    category_id,
    source_table,
    target_table
FROM log_events
WHERE game_gid = 10000147  -- STAR001 的业务GID
LIMIT 10;
```

**结果示例**:
| id | event_name | event_name_cn | source_table | target_table |
|----|-----------|---------------|--------------|--------------|
| 55 | 25ph.pass | 25周年庆预热-战令额外奖励 | hdyl_data_sg.ods_3_all_view | dwd_25ph.pass |
| 56 | 25ph.pu | 25周年庆预热-拼图 | hdyl_data_sg.ods_3_all_view | dwd_25ph.pu |

---

### 2. 查询游戏的 事件节点

```sql
-- ✅ 迁移后：使用 game_gid
SELECT
    id,
    game_gid,
    name,
    event_id,
    config_json,
    is_active
FROM event_nodes
WHERE game_gid = 10000147;
```

**结果示例**:
| id | game_gid | name | event_id | is_active |
|----|----------|------|----------|-----------|
| 13 | 10000147 | Test Login Node | 55 | 1 |

---

### 3. 查询游戏的 所有参数（通过事件关联）

**重要**: `event_params` 表没有 `game_gid` 列，它通过 `event_id` 关联到 `log_events` 表。

```sql
-- ✅ 迁移后：通过 JOIN 查询
SELECT
    ep.id,
    ep.event_id,
    le.event_name,
    ep.param_name,
    ep.param_name_cn,
    ep.json_path
FROM event_params ep
INNER JOIN log_events le ON ep.event_id = le.id
WHERE le.game_gid = 10000147  -- 通过 log_events 的 game_gid 过滤
LIMIT 10;
```

**结果示例**:
| id | event_id | event_name | param_name | param_name_cn | json_path |
|----|----------|------------|-----------|---------------|-----------|
| 51 | 55 | 25ph.pass | serverName | 游戏服名字 | |
| 52 | 55 | 25ph.pass | roleName | 角色名 | |
| 53 | 55 | 25ph.pass | diamond | 紫金 -> 改为总元宝数 | |

---

### 4. 统计游戏的数据量

```sql
-- ✅ 迁移后：使用 game_gid
SELECT
    (SELECT COUNT(*) FROM log_events WHERE game_gid = 10000147) as event_count,
    (SELECT COUNT(*) FROM event_nodes WHERE game_gid = 10000147) as node_count,
    (SELECT COUNT(*) FROM event_params ep
     INNER JOIN log_events le ON ep.event_id = le.id
     WHERE le.game_gid = 10000147) as param_count;
```

**结果示例**:
| event_count | node_count | param_count |
|-------------|------------|-------------|
| 1903 | 1 | 36707 |

---

## 🔄 Python 代码示例

### 查询游戏事件

```python
from backend.core.database.converters import fetch_all_as_dict, fetch_one_as_dict

# ✅ 迁移后：使用 game_gid
game_gid = 10000147

# 查询游戏的所有事件
events = fetch_all_as_dict(
    'SELECT * FROM log_events WHERE game_gid = ?',
    (game_gid,)
)

# 查询游戏的事件节点
nodes = fetch_all_as_dict(
    'SELECT * FROM event_nodes WHERE game_gid = ?',
    (game_gid,)
)

# 查询游戏的所有参数（通过事件关联）
params = fetch_all_as_dict(
    '''
    SELECT ep.*, le.event_name
    FROM event_params ep
    INNER JOIN log_events le ON ep.event_id = le.id
    WHERE le.game_gid = ?
    ''',
    (game_gid,)
)
```

### API 路由示例

```python
# backend/api/routes/events.py

@games_bp.route('/api/games/<int:game_gid>/events', methods=['GET'])
def get_game_events(game_gid):
    """
    获取指定游戏的所有事件

    Args:
        game_gid: 游戏的业务GID（如 10000147）
    """
    from backend.core.database.converters import fetch_all_as_dict

    events = fetch_all_as_dict(
        'SELECT * FROM log_events WHERE game_gid = ?',
        (game_gid,)
    )

    return json_success_response(data=events)
```

---

## 🎯 关键要点

### 1. 游戏标识符对比

| 标识符 | 类型 | 稳定性 | 用途 |
|--------|------|--------|------|
| **game_id** | 数据库自增ID | ❌ 不稳定 | 仅用于 games 表主键 |
| **game_gid** | 业务GID | ✅ 稳定 | 所有数据关联 |

**示例**:
```python
# games 表
game_id = 58           # 数据库自增ID，可能变化
game_gid = 10000147    # 业务GID，稳定不变
```

### 2. 表关联关系

```
games (gid=10000147)
    ↓
log_events (game_gid=10000147) ← 直接关联
    ↓
event_params (event_id=log_events.id) ← 间接关联
```

### 3. 查询性能

**索引已重建**:
```sql
CREATE INDEX idx_log_events_game_gid ON log_events(game_gid);
CREATE INDEX idx_event_nodes_game_gid ON event_nodes(game_gid);
CREATE INDEX idx_event_params_event_id ON event_params(event_id);
```

**查询性能**: ✅ 优秀（使用索引）

---

## ⚠️ 常见错误

### ❌ 错误1: 使用 game_id 查询

```python
# ❌ 错误：game_id 列已删除
events = fetch_all_as_dict(
    'SELECT * FROM log_events WHERE game_id = ?',
    (58,)
)
# Error: no such column: game_id
```

### ✅ 正确: 使用 game_gid 查询

```python
# ✅ 正确：使用 game_gid
events = fetch_all_as_dict(
    'SELECT * FROM log_events WHERE game_gid = ?',
    (10000147,)
)
```

### ❌ 错误2: 直接查询 event_params 的 game_gid

```python
# ❌ 错误：event_params 没有 game_gid 列
params = fetch_all_as_dict(
    'SELECT * FROM event_params WHERE game_gid = ?',
    (10000147,)
)
# Error: no such column: game_gid
```

### ✅ 正确: 通过 JOIN 查询

```python
# ✅ 正确：通过 log_events JOIN
params = fetch_all_as_dict(
    '''
    SELECT ep.*
    FROM event_params ep
    INNER JOIN log_events le ON ep.event_id = le.id
    WHERE le.game_gid = ?
    ''',
    (10000147,)
)
```

---

## 📚 相关文档

- **迁移报告**: [game-gid-migration-complete-report.md](game-gid-migration-complete-report.md)
- **最终报告**: [FINAL-AUDIT-FIX-REPORT.md](FINAL-AUDIT-FIX-REPORT.md)
- **迁移计划**: [game-gid-migration-final-plan.md](game-gid-migration-final-plan.md)

---

**文档生成时间**: 2026-02-20
**适用版本**: Event2Table v7.5+
**状态**: ✅ 已验证
