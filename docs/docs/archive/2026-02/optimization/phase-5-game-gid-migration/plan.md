# Phase 5: game_gid迁移

> **阶段**: P5 - 中等优先级 | **预计时间**: 4-5小时 | **并行任务**: 5个

---

## ⚠️ 重要提示

根据用户要求：
- **完全切换**：不保持向后兼容，所有API只支持game_gid
- **前端同步修改**：后端修改完成后，前端需要同步更新
- **警惕假阳性**：部分game_id使用可能是合理的（如数据库外键）

---

## 📋 迁移清单

### 问题1: Session设置错误 🔴 严重

**位置**: `backend/services/games/games.py:62, 66`

**问题**: Session中设置的是id而非gid

**修复方案**:
```python
# ❌ 错误
session["current_game_gid"] = game["id"]

# ✅ 修复
session["current_game_gid"] = game["gid"]
```

---

### 问题2: Event Nodes WHERE条件使用game_id 🔴 高

**位置**: 
- `backend/services/events/event_nodes.py:205`
- `backend/services/events/event_nodes.py:214`

**问题**: SQL查询和INSERT使用game_id

**修复方案**:
```python
# ❌ 错误
SELECT * FROM event_nodes WHERE game_id = ? AND name = ?
INSERT INTO event_nodes (game_id, name, event_id, config_json)

# ✅ 修复
SELECT * FROM event_nodes WHERE game_gid = ? AND name = ?
INSERT INTO event_nodes (game_gid, name, event_id, config_json)
```

**注意**: 需要确认event_nodes表是否已有game_gid字段

---

### 问题3: Parameter Aliases使用game_id 🔴 高

**位置**: `backend/services/parameters/parameter_aliases.py:94, 108, 116, 156, 195`

**问题**: WHERE条件和INSERT使用game_id

**修复方案**:
```python
# ❌ 错误
WHERE game_id = ? AND param_id = ?
INSERT INTO parameter_aliases (game_id, param_id, alias, ...)

# ✅ 修复
WHERE game_gid = ? AND param_id = ?
INSERT INTO parameter_aliases (game_gid, param_id, alias, ...)
```

**数据库迁移**: 需要添加game_gid字段并迁移数据

---

### 问题4: Common Params使用game_id 🔴 高

**位置**: `backend/services/parameters/common_params.py:56, 149`

**问题**: WHERE条件使用game_id

**修复方案**:
```python
# ❌ 错误
WHERE game_id = ?

# ✅ 修复
WHERE game_gid = ?
```

---

### 问题5: FlowRepository使用game_id 🔴 高

**位置**: 
- `backend/models/repositories/flow_repository.py:76`
- `backend/models/repositories/flow_repository.py:263`

**问题**: Repository查询使用game_id

**修复方案**:
```python
# ❌ 错误
WHERE game_id = ? AND is_active = 1

# ✅ 修复
WHERE game_gid = ? AND is_active = 1
```

**数据库迁移**: flow_templates表需要添加game_gid字段

---

### 问题6: API参数使用game_id 🟠 中

**位置**: 
- `backend/api/routes/events.py:307`
- `backend/api/routes/parameters.py:210, 320, 523`
- `backend/api/routes/join_configs.py:75`
- `backend/api/routes/_param_helpers.py:40`
- `backend/services/flows/routes.py:44, 262`

**问题**: API接受game_id参数而非game_gid

**修复方案**:
```python
# ❌ 错误
game_id = request.args.get("game_id", type=int)

# ✅ 修复（完全切换，不向后兼容）
game_gid = request.args.get("game_gid", type=int)
if not game_gid:
    return json_error_response("game_gid required", status_code=400)
```

---

### 问题7: JOIN条件使用game_id 🟠 中

**位置**:
- `backend/api/routes/games.py:154`
- `backend/api/routes/parameters.py:802`
- `backend/core/cache/cache_warmer.py:74`

**问题**: JOIN条件使用game_id

**修复方案**:
```python
# ❌ 错误
LEFT JOIN flow_templates ft ON ft.game_id = g.id
JOIN games g ON p.game_id = g.id

# ✅ 修复
LEFT JOIN flow_templates ft ON ft.game_gid = g.gid
JOIN games g ON p.game_gid = g.gid
```

---

### 问题8: 表名生成使用game["id"] 🟠 中

**位置**: 15处（详见完整清单）

**问题**: 部分场景使用game["id"]生成表名

**修复方案**:
```python
# ❌ 错误（用于表名生成）
table_name = f"ods_{game['id']}_all_view"

# ✅ 修复
table_name = f"ods_{game['gid']}_all_view"

# 注意：如果game["id"]用于外键关联（非表名生成），可以保留
```

---

### 问题9: Schema定义使用game_id 🟡 低

**位置**: `backend/models/schemas.py:355`

**问题**: Pydantic Schema定义game_id字段

**修复方案**:
```python
# ❌ 错误
class FlowTemplateBase(BaseModel):
    game_id: int

# ✅ 修复
class FlowTemplateBase(BaseModel):
    game_gid: int  # 使用业务GID
```

---

### 问题10: Legacy API使用game_id 🟡 低

**位置**: `backend/api/routes/legacy_api.py:133`

**问题**: 旧版API使用game_id

**修复方案**: legacy_api.py已计划废弃，可暂不修复

---

## 🗄️ 数据库迁移计划

### 需要添加game_gid字段的表

```sql
-- Migration: add_game_gid_columns.sql

-- 1. flow_templates表
ALTER TABLE flow_templates ADD COLUMN game_gid INTEGER;
UPDATE flow_templates SET game_gid = (
    SELECT gid FROM games WHERE games.id = flow_templates.game_id
);
CREATE INDEX idx_flow_templates_game_gid ON flow_templates(game_gid);

-- 2. parameter_aliases表
ALTER TABLE parameter_aliases ADD COLUMN game_gid INTEGER;
UPDATE parameter_aliases SET game_gid = (
    SELECT gid FROM games WHERE games.id = parameter_aliases.game_id
);
CREATE INDEX idx_parameter_aliases_game_gid ON parameter_aliases(game_gid);

-- 3. common_params表
ALTER TABLE common_params ADD COLUMN game_gid INTEGER;
UPDATE common_params SET game_gid = (
    SELECT gid FROM games WHERE games.id = common_params.game_id
);
CREATE INDEX idx_common_params_game_gid ON common_params(game_gid);

-- 4. event_nodes表（如果尚未有game_gid字段）
ALTER TABLE event_nodes ADD COLUMN game_gid INTEGER;
UPDATE event_nodes SET game_gid = (
    SELECT gid FROM games WHERE games.id = event_nodes.game_id
);
CREATE INDEX idx_event_nodes_game_gid ON event_nodes(game_gid);
```

---

## 🚀 执行计划

### 并行subagent任务分配

```
Subagent 1: 修复Session和Event Nodes
├── services/games/games.py (Session设置)
├── services/events/event_nodes.py (WHERE + INSERT)
└── 验证event_nodes表结构

Subagent 2: 修复Parameter相关
├── services/parameters/parameter_aliases.py
├── services/parameters/common_params.py
└── 创建数据库迁移脚本

Subagent 3: 修复FlowRepository
├── models/repositories/flow_repository.py
├── api/routes/flows.py
└── 验证flow_templates表结构

Subagent 4: 修复API参数
├── api/routes/events.py
├── api/routes/parameters.py
├── api/routes/join_configs.py
├── api/routes/_param_helpers.py
└── 移除game_id参数支持

Subagent 5: 修复JOIN条件和Schema
├── api/routes/games.py (JOIN)
├── api/routes/parameters.py (JOIN)
├── core/cache/cache_warmer.py (JOIN)
└── models/schemas.py (Schema定义)
```

---

## ✅ 验证步骤

1. **数据库迁移**:
   ```bash
   # 执行数据库迁移
   sqlite3 data/dwd_generator.db < migration/add_game_gid_columns.sql
   
   # 验证数据迁移
   sqlite3 data/dwd_generator.db "SELECT COUNT(*) FROM flow_templates WHERE game_gid IS NULL"
   ```

2. **单元测试**:
   ```bash
   pytest backend/test/unit/ -v -k "game_gid"
   ```

3. **集成测试**:
   ```bash
   # 测试game_gid参数
   curl -X GET "http://localhost:5001/api/games?game_gid=10000147"
   
   # 测试game_id参数（应返回400错误）
   curl -X GET "http://localhost:5001/api/games?game_id=1"
   ```

4. **E2E测试**:
   ```bash
   # 前端同步更新后执行E2E测试
   cd frontend
   npm run test:e2e
   ```

---

## 🎯 预期成果

- ✅ 15个文件的game_gid违规修复
- ✅ 40+处代码修改
- ✅ 4个数据库表添加game_gid字段
- ✅ API统一使用game_gid参数
- ✅ 前端同步更新（需配合）

**影响范围**:
- 后端API: 15个文件
- 数据库: 4个表结构修改
- 前端: 需要同步更新所有game_id调用

**风险**: 中高 - 需要前后端同步修改，数据库迁移需谨慎

---

## 📝 前端同步更新清单

后端完成后，前端需要同步更新：

1. **API调用**:
   - 所有 `game_id` 参数改为 `game_gid`
   - 所有 `/api/xxx?game_id=1` 改为 `/api/xxx?game_gid=10000147`

2. **组件更新**:
   - `frontend/src/analytics/pages/*.jsx` - 更新API调用
   - `frontend/src/features/*/api/*.ts` - 更新API函数

3. **测试更新**:
   - E2E测试中的game_id参数更新为game_gid

---

## 🚨 注意事项

1. **假阳性检查**:
   - 部分game_id使用是合理的（如games表主键id）
   - 外键关联可能需要保留game_id（同时保留game_gid）

2. **数据备份**:
   - 执行数据库迁移前，务必备份数据
   - `cp data/dwd_generator.db data/dwd_generator.db.backup`

3. **回滚计划**:
   - 准备回滚脚本
   - 前后端同步回滚

---

**完成标志**: 所有API只接受game_gid参数，所有SQL查询使用game_gid

**下一步**: 项目全面测试和部署
