# Backend 数据库 Schema 问题修复计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复 Backend 数据库 schema 不匹配问题，确保 GameRepository 不再尝试插入不存在的 description 和 dwd_prefix 字段

**Architecture:** 
- 修复 GameRepository.create_batch() 方法，移除硬编码的 description 和 dwd_prefix 字段
- 验证所有相关代码路径，确保不再传递这些字段
- 运行测试验证修复

**Tech Stack:** Python, SQLite, Pydantic, pytest

---

## 问题分析

### 根本原因

从 CI 错误日志中可以看到：

```
ERROR backend.api.routes.games:games.py:162 Error creating game: table games has no column named description
```

**问题链条：**

1. ✅ **GameEntity 已修复** - 不包含 `description` 和 `dwd_prefix` 字段
2. ✅ **数据库 schema 正确** - `migration/schema.sql` 中 games 表定义正确
3. ❌ **GameRepository.create_batch() 硬编码了旧字段** - 第305-312行的 INSERT 语句包含 description 和 dwd_prefix

### 影响范围

- `backend/models/repositories/games.py:293-320` - create_batch() 方法
- `backend/test/unit/api/test_api_comprehensive.py` - 测试可能失败
- CI/CD Pipeline - 5个测试失败

---

## 修复计划

### Task 1: 修复 GameRepository.create_batch() 方法

**Files:**
- Modify: `backend/models/repositories/games.py:293-320`
- Test: `backend/test/unit/api/test_api_comprehensive.py`

- [ ] **Step 1: 读取 GameRepository.create_batch() 方法**

使用 read_file 确认当前实现：
```bash
read_file backend/models/repositories/games.py
```

关注第293-320行的 create_batch() 方法。

- [ ] **Step 2: 修复 INSERT 语句**

**修改前：**
```python
# 第305-312行
query = """
    INSERT INTO games (gid, name, ods_db, description, dwd_prefix, icon_path)
    VALUES (?, ?, ?, ?, ?, ?)
"""

# 准备参数列表
params = [
    (
        g.get('gid'),
        g.get('name'),
        g.get('ods_db', f"ods_game_{g.get('gid')}"),
        g.get('description', ''),
        g.get('dwd_prefix', 'dwd'),
        g.get('icon_path'),
    )
    for g in games_data
]
```

**修改后：**
```python
# 移除 description 和 dwd_prefix 字段
query = """
    INSERT INTO games (gid, name, ods_db, icon_path)
    VALUES (?, ?, ?, ?)
"""

# 准备参数列表
params = [
    (
        g.get('gid'),
        g.get('name'),
        g.get('ods_db', f"ods_game_{g.get('gid')}"),
        g.get('icon_path'),
    )
    for g in games_data
]
```

- [ ] **Step 3: 验证修改**

运行测试验证修复：
```bash
pytest backend/test/unit/api/test_api_comprehensive.py::TestGamesAPI::test_02_create_game_success -v
```

Expected: PASS

- [ ] **Step 4: 运行所有 Backend Unit Tests**

```bash
pytest backend/test/unit/api/test_api_comprehensive.py -v
```

Expected: 所有测试通过

- [ ] **Step 5: 提交修改**

```bash
git add backend/models/repositories/games.py
git commit -m "fix: remove description and dwd_prefix from GameRepository.create_batch()

- Remove hardcoded description and dwd_prefix fields from INSERT statement
- Align with database schema (migration/schema.sql)
- Fix CI test failures: table games has no column named description"
```

---

### Task 2: 验证其他代码路径

**Files:**
- Check: `backend/services/games/game_service.py`
- Check: `backend/api/routes/games.py`
- Check: `backend/models/entities.py`

- [ ] **Step 1: 检查 GameService.create_game() 方法**

确认 GameService.create_game() 不再传递 description 和 dwd_prefix：
```python
# backend/services/games/game_service.py:107
created_game = self.game_repo.create(game_data.model_dump())
```

`game_data` 是 GameEntity 对象，`model_dump()` 应该只返回 Entity 定义的模型字段。

- [ ] **Step 2: 验证 GameEntity 定义**

确认 GameEntity 不包含 description 和 dwd_prefix：
```python
# backend/models/entities.py
class GameEntity(BaseEntity):
    gid: int = Field(..., ge=0, description="游戏业务GID")
    name: str = Field(..., min_length=1, max_length=100, description="游戏名称")
    ods_db: str = Field(..., description="ODS数据库名称")
    icon_path: Optional[str] = Field(None, description="图标路径")
```

✅ 已确认：GameEntity 不包含 description 和 dwd_prefix 字段

- [ ] **Step 3: 提交验证**

如果验证通过，无需修改，继续下一步。

---

### Task 3: 清理缓存和测试数据

**Files:**
- Check: 测试数据库文件
- Check: 缓存文件

- [ ] **Step 1: 清理测试数据库**

CI 环境会自动创建新的测试数据库，无需手动清理。

- [ ] **Step 2: 清理本地缓存（如果需要）**

如果本地测试仍然失败，清理缓存：
```bash
rm -rf data/games_bloom_filter.pkl
rm -rf .pytest_cache
```

- [ ] **Step 3: 重新运行测试**

```bash
pytest backend/test/unit/api/test_api_comprehensive.py -v
```

Expected: 所有测试通过

---

### Task 4: 修复其他测试失败

**Files:**
- Test: `backend/test/unit/api/test_api_comprehensive.py`

根据 CI 日志，还有其他测试失败：

1. `test_01_list_games` - 数据为空
2. `test_05_get_event_detail` - KeyError: 'id'
3. `test_06_get_event_detail_not_found` - 200 != 404

- [ ] **Step 1: 分析 test_01_list_games 失败原因**

测试期望数据库中有数据，但实际为空。这可能是因为：
- 测试数据库初始化问题
- 测试数据创建失败（因为 description 问题）

修复 GameRepository.create_batch() 后，这个问题应该自动解决。

- [ ] **Step 2: 分析 test_05_get_event_detail 失败原因**

测试返回 KeyError: 'id'，说明 API 响应格式不正确。

需要检查：
- EventEntity 定义
- Event API 响应格式

- [ ] **Step 3: 分析 test_06_get_event_detail_not_found 失败原因**

测试期望返回 404，但实际返回 200。

需要检查：
- Event API 的错误处理逻辑

---

## 验收标准

### 必须满足

- [x] GameRepository.create_batch() 不再尝试插入 description 和 dwd_prefix 字段
- [ ] Backend Unit Tests 所有测试通过
- [ ] CI Pipeline 通过

### 性能指标

- 无性能回退
- 测试执行时间保持在当前范围内

---

## 风险评估

### 低风险

- **修改范围小** - 只修改一个 INSERT 语句
- **向后兼容** - 数据库 schema 已经不包含这些字段
- **测试覆盖** - 有完整的测试套件验证

### 回滚方案

如果修复引入新问题：

```bash
git revert <commit-hash>
```

---

## 后续任务

修复 Backend 测试后，需要处理：

1. **FIX-12: 修复 Frontend 测试失败**
   - SQL 格式化问题
   - 性能测试失败
   - GraphQL 测试失败

2. **FIX-13: 修复测试覆盖率问题**
   - 当前: 18.76%
   - 目标: > 70%

---

## 参考文档

- [CI 失败日志](临时文件，包含详细错误信息)
- [migration/schema.sql](数据库表定义)
- [backend/models/entities.py](GameEntity 定义)
- [backend/models/repositories/games.py](GameRepository 实现)
- [backend/services/games/game_service.py](GameService 实现)

---

**Created:** 2026-03-23
**Author:** Aone Copilot
**Status:** Ready for execution
