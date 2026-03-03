# game_id 违规详细清单

**生成时间**: 2026-02-11  
**违规总数**: 9处（6处HIGH优先级，3处LOW优先级）  

---

## HIGH优先级违规（需修复）

### 1. backend/api/routes/parameters.py

**位置**: Line 389  
**代码**:
```python
WHERE game_id = ?
```
**修复**:
```python
WHERE game_gid = ?
```

---

### 2. backend/services/parameters/parameter_aliases.py

**位置**: Line 94  
**代码**:
```python
WHERE game_id = ? AND param_id = ?
```
**修复**:
```python
WHERE game_gid = ? AND param_id = ?
```

**位置**: Line 108  
**代码**:
```python
WHERE game_id = ? AND param_id = ?
```
**修复**:
```python
WHERE game_gid = ? AND param_id = ?
```

**位置**: Line 156  
**代码**:
```python
WHERE game_id = ? AND param_id = ? AND id != ?
```
**修复**:
```python
WHERE game_gid = ? AND param_id = ? AND id != ?
```

**位置**: Line 195  
**代码**:
```python
WHERE game_id = ? AND param_id = ?
```
**修复**:
```python
WHERE game_gid = ? AND param_id = ?
```

---

### 3. backend/services/events/event_nodes.py

**位置**: Line 205  
**代码**:
```python
"SELECT * FROM event_nodes WHERE game_id = ? AND name = ?", (game_id, name)
```
**修复**:
```python
"SELECT * FROM event_nodes WHERE game_gid = ? AND name = ?", (game_gid, name)
```

**位置**: Line 338  
**代码**:
```python
WHERE game_id = ? AND param_id = ? AND alias = ?
```
**修复**:
```python
WHERE game_gid = ? AND param_id = ? AND alias = ?
```

---

## LOW优先级违规（迁移脚本，可接受）

### backend/core/database/database.py

**位置**: Line 1035  
**代码**:
```python
cursor.execute("UPDATE flow_templates SET game_id = 1 WHERE game_id IS NULL")
```
**说明**: 数据库迁移脚本，设置默认值。这是表的主键，可接受。

**位置**: Line 2347  
**代码**:
```python
cursor.execute("UPDATE flow_templates SET game_id = 1 WHERE game_id IS NULL")
```
**说明**: 数据库迁移脚本，设置默认值。这是表的主键，可接受。

---

## 修复建议

### 步骤1: 检查相关表结构

确认以下表是否已有 `game_gid` 列：
- `parameter_aliases`
- `event_nodes`

```bash
sqlite3 dwd_generator.db "PRAGMA table_info(parameter_aliases);"
sqlite3 dwd_generator.db "PRAGMA table_info(event_nodes);"
```

### 步骤2: 如果需要，添加 game_gid 列

```sql
-- 对于 parameter_aliases 表
ALTER TABLE parameter_aliases ADD COLUMN game_gid INTEGER;
CREATE INDEX idx_parameter_aliases_game_gid ON parameter_aliases(game_gid);

-- 对于 event_nodes 表  
ALTER TABLE event_nodes ADD COLUMN game_gid INTEGER;
CREATE INDEX idx_event_nodes_game_gid ON event_nodes(game_gid);
```

### 步骤3: 数据迁移

```sql
-- 迁移现有数据
UPDATE parameter_aliases 
SET game_gid = (SELECT game_gid FROM games WHERE id = game_id);

UPDATE event_nodes 
SET game_gid = (SELECT game_gid FROM games WHERE id = game_id);
```

### 步骤4: 更新代码

按照上述修复方案，逐一替换：
1. `game_id` → `game_gid`（WHERE条件）
2. `game_id` → `game_gid`（JOIN条件）
3. 变量名 `game_id` → `game_gid`

### 步骤5: 测试验证

```bash
# 运行相关测试
python3 -m pytest test/unit/backend_tests/unit/ -v -k "parameter"
python3 -m pytest test/unit/backend_tests/unit/ -v -k "event_node"
```

---

## 影响分析

### 影响范围

| 模块 | 影响程度 | 说明 |
|------|----------|------|
| 参数别名服务 | HIGH | 核心查询需要修改 |
| 事件节点服务 | HIGH | 核心查询需要修改 |
| 参数API | HIGH | API路由需要修改 |

### 风险评估

- **数据完整性**: ⚠️ 中等 - 需要正确迁移数据
- **API兼容性**: ⚠️ 中等 - 需要确保前端使用 game_gid
- **性能影响**: 🟢 低 - 添加索引后性能良好

---

## 优先级说明

### 为什么HIGH优先级需要修复？

1. **业务一致性**: 所有数据关联应使用 game_gid（业务GID）而非 game_id（数据库主键）
2. **Dashboard显示**: game_id违规可能导致Dashboard显示0事件
3. **项目规范**: CLAUDE.md明确要求使用 game_gid

### 为什么LOW优先级可接受？

1. **主键使用**: game_id 作为表的主键是正确的
2. **迁移脚本**: 仅在迁移时使用，不影响业务逻辑
3. **数据完整性**: 外键约束需要使用 game_id（主键）

---

**文档版本**: 1.0  
**下次更新**: 修复完成后
