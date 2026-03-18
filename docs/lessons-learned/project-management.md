# 项目管理

> **来源**: 整合了多个报告的项目管理相关经验
> **最后更新**: 2026-03-02
> **维护**: 每次项目管理实践改进后立即更新

---

## 并行开发策略 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 多次 | **来源**: [后端架构优化报告](../archive/testing-reports/2026-03-01/2026-03-01/FINAL-ARCHITECTURE-OPTIMIZATION-REPORT.md)

### 核心概念

**使用多个subagents并行处理，效率提升3-4倍**

### 并行模式

**任务分解示例**:
```
Phase 1: 紧急修复 (subagent A) → 双规制代码清理
Phase 2: Service重构 (subagent B) → 参数管理重构
Phase 3: 模块迁移 (subagent C) → Join Configs迁移
Phase 4: 全面清理 (subagent D) → V2文件清理

同时进行 → 总体时间减少3-4倍
```

### 实施策略

**1. 任务分解原则**:
```python
# ✅ 正确：任务独立，无共享状态
Task(subagent_type="general-purpose", prompt="修复games.py双规制")
Task(subagent_type="general-purpose", prompt="修复hql_generation.py双规制")

# ❌ 错误：任务有依赖关系
Task(subagent_type="general-purpose", prompt="重构Service层")  # 需要等待Phase 1
Task(subagent_type="general-purpose", prompt="创建API层")     # 依赖Service层
```

**2. 并行执行示例**:
```python
# 启动2个并行subagent
Task(subagent_type="general-purpose", prompt="分析React Hooks错误根因")
Task(subagent_type="general-purpose", prompt="分析加载超时模式")

# 同时进行，效率提升
```

**3. 集成测试**:
```bash
# 每个Phase完成后立即测试
pytest backend/test/unit/           # 单元测试
pytest backend/test/integration/    # 集成测试
npm run test:e2e                     # E2E测试
```

### 性能数据

**Event2Table项目实际数据**:
- Phase 1-4并行开发：~4小时
- 如果串行开发：~12-16小时
- **效率提升：3-4倍**

### 代码审查清单

- [ ] 任务是否可独立执行？
- [ ] 是否有明确的输入和输出？
- [ ] 是否避免了共享状态？
- [ ] 每个任务完成后是否立即测试？

### 案例文档

- [后端架构优化报告](../archive/testing-reports/2026-03-01/2026-03-01/FINAL-ARCHITECTURE-OPTIMIZATION-REPORT.md) - Phase 1-4并行实施案例

---

## 大规模重构管理 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 1次 | **来源**: [后端架构优化报告](../archive/testing-reports/2026-03-01/2026-03-01/FINAL-ARCHITECTURE-OPTIMIZATION-REPORT.md)

### 核心原则

**阶段化迁移 + 零破坏性变更**

### Phase方法论

**分4个Phase逐步迁移**:
```
Phase 0: 紧急修复（双规制代码）
  ↓
Phase 1: Service层重构
  ↓
Phase 2: 核心模块迁移（Join Configs、Event Categories）
  ↓
Phase 3: 全面清理（V2文件、Repository层）
  ↓
Phase 4: 验证和文档更新
```

**每个Phase完成后**:
1. ✅ 运行完整测试套件（69/69测试）
2. ✅ 验证功能完整性
3. ✅ 检查性能指标
4. ✅ 更新相关文档

### 零破坏性变更保证

**1. 使用git worktree隔离开发环境**:
```bash
# 创建隔离的开发环境
git worktree add ../event2table-phase1 origin/main

# 在worktree中进行开发
cd ../event2table-phase1
# ... 开发和测试 ...

# 完成后合并回主分支
git checkout main
git merge --no-ff phase1/feature-branch
```

**2. 完整测试验证**:
```bash
# 单元测试：16/16 通过 ✅
pytest backend/test/unit/ -v

# 集成测试：25/25 通过 ✅
pytest backend/test/integration/ -v

# API契约测试：12/12 通过 ✅
python scripts/test/api_contract_test.py

# E2E测试：16/16 通过 ✅
npm run test:e2e

# 总计：69/69 (100%) ✅
```

**3. 灰度发布**:
```python
# 先在开发环境验证
FLASK_ENV=development python web_app.py

# 再在生产环境小范围测试
FLASK_ENV=production python web_app.py
```

### 回滚准备

**保留回滚路径**:
```bash
# 每个Phase完成后打tag
git tag -a phase1-complete -m "Phase 1 completed"

# 如果需要回滚
git checkout phase1-complete
```

### 代码审查清单

- [ ] 是否分多个Phase逐步迁移？
- [ ] 每个Phase完成后是否运行完整测试？
- [ ] 是否使用git worktree隔离开发？
- [ ] 是否有回滚准备？

### 案例文档

- [后端架构优化报告](../archive/testing-reports/2026-03-01/2026-03-01/FINAL-ARCHITECTURE-OPTIMIZATION-REPORT.md) - 完整Phase实施记录

---

## 零破坏性变更保证 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 多次 | **来源**: 多个报告

### 核心原则

**所有变更必须保证向后兼容**

### 兼容性检查清单

**1. API兼容性**:
```python
# ✅ 正确：保留旧API，添加新API
@app.route('/api/games/<int:game_id>', methods=['GET'])  # 旧API
def get_game_by_id(game_id): ...

@app.route('/api/games/<int:game_gid>', methods=['GET'])  # 新API
def get_game_by_gid(game_gid): ...

# ❌ 错误：直接修改旧API
@app.route('/api/games/<int:game_id>', methods=['GET'])
def get_game(game_id):  # 参数从game_id改为game_gid
    ...
```

**2. 数据库兼容性**:
```sql
-- ✅ 正确：添加新列，保留旧列
ALTER TABLE log_events ADD COLUMN game_gid INTEGER;
UPDATE log_events SET game_gid = game_id WHERE game_gid IS NULL;

-- ❌ 错误：直接删除旧列
ALTER TABLE log_events DROP COLUMN game_id;
```

**3. 前端兼容性**:
```javascript
// ✅ 正确：添加新props，保留旧props
interface GameProps {
  gameId?: number;    // 旧prop（废弃）
  gameGid?: number;   // 新prop
}

// ❌ 错误：直接修改prop
interface GameProps {
  gameGid: number;    // gameId改为gameGid
}
```

### 废弃策略

**标记废弃API**:
```python
from flask import abort

@app.route('/api/legacy/games', methods=['GET'])
def get_games_legacy():
    """
    获取游戏列表（已废弃）

    .. deprecated::
        使用 /api/games 代替
        将在 v2.0 版本移除
    """
    # 记录废弃警告
    logger.warning("Legacy API /api/legacy/games is being used")

    # 返回数据（同时返回新API链接）
    response = jsonify({"data": get_games(), "_links": {"new_api": "/api/games"}})
    response.headers['X-API-Deprecated'] = 'true'
    response.headers['X-API-Replacement'] = '/api/games'
    return response
```

### 测试验证

**兼容性测试**:
```python
def test_backward_compatibility():
    """测试向后兼容性"""
    # 旧API仍然可用
    response = client.get('/api/games/123')
    assert response.status_code == 200

    # 新API也工作
    response = client.get('/api/games?game_gid=10000147')
    assert response.status_code == 200

    # 两个API返回相同数据
    old_data = response_old.json['data']
    new_data = response_new.json['data']
    assert old_data == new_data
```

### 代码审查清单

- [ ] 是否保留了旧API？
- [ ] 是否添加了废弃标记？
- [ ] 数据库变更是否保留旧列？
- [ ] 前端props是否向后兼容？
- [ ] 是否有兼容性测试？

---

## 文档驱动开发 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 多次 | **来源**: 所有项目报告

### 核心原则

**文档与代码同步的协同开发**

### 文档先行

**功能开发流程**:
```
1. 需求文档（PRD）
   ↓
2. 设计文档（架构）
   ↓
3. API文档（接口定义）
   ↓
4. 实现代码
   ↓
5. 测试文档
   ↓
6. 更新所有文档
```

### 文档类型

**1. 需求文档**:
```markdown
# 产品需求文档 (PRD)

## 功能需求
- 用户故事
- 功能描述
- 验收标准

## 变更记录
- 2026-03-01: 新增功能X
- 2026-02-28: 修改功能Y
```

**2. 设计文档**:
```markdown
# 架构设计文档

## 系统架构
- 分层架构
- 模块划分
- 数据流向

## 技术选型
- 框架选择
- 数据库选择
- 缓存方案
```

**3. API文档**:
```markdown
# API文档

## 端点定义
- GET /api/games
- POST /api/games
- PUT /api/games/:id

## 请求/响应示例
```json
{
  "data": {...}
}
```
```

**4. 测试文档**:
```markdown
# 测试文档

## 测试用例
- 单元测试
- 集成测试
- E2E测试

## 测试结果
- 通过率
- 覆盖率
```

### 文档更新流程

**每次代码变更后**:
```bash
# 1. 更新API文档
vim docs/api/GAMES-API.md

# 2. 更新架构文档
vim docs/development/architecture.md

# 3. 更新测试文档
vim docs/testing/e2e-testing-guide.md

# 4. 更新经验文档
vim docs/lessons-learned/performance-patterns.md

# 5. 提交文档和代码
git add docs/ src/
git commit -m "feat: add new feature and update docs"
```

### 文档审查清单

**代码审查时检查**:
- [ ] 是否有对应的需求文档？
- [ ] 是否有API文档？
- [ ] 是否更新了架构文档？
- [ ] 是否有测试文档？
- [ ] 经验文档是否已更新？

---

## 相关经验文档

- [调试技能 - 并行开发](./debugging-skills.md#并行开发策略) - 并行开发具体方法
- [重构检查清单 - 技术债务管理](./refactoring-checklist.md#技术债务管理流程) - 技术债务管理
- [API设计模式 - API版本管理](./api-design-patterns.md) - API兼容性设计

### GraphQL API 文档

**更新时间**: 2026-03-12

---

### 来自 docs/development/architecture.md (2026-03-18)

**关键主题**:
- 架构设计文档
- 目录
- Repository模式详解 ⭐
- 什么是Repository模式？
- 架构对比

**重要经验**:
- 直接SQL查询 ❌
- - ❌ 数据访问逻辑散落在各处
- - ❌ 难以测试（无法Mock）
- - ❌ 代码重复
- - ❌ 缓存管理混乱


### 来自 docs/development/architecture.md (2026-03-18)

**关键主题**:
- 架构设计文档
- 目录
- Repository模式详解 ⭐
- 什么是Repository模式？
- 架构对比

**重要经验**:
- 直接SQL查询 ❌
- - ❌ 数据访问逻辑散落在各处
- - ❌ 难以测试（无法Mock）
- - ❌ 代码重复
- - ❌ 缓存管理混乱


### 来自 docs/development/architecture.md (2026-03-18)

**关键主题**:
- 架构设计文档
- 目录
- Repository模式详解 ⭐
- 什么是Repository模式？
- 架构对比

**重要经验**:
- 直接SQL查询 ❌
- - ❌ 数据访问逻辑散落在各处
- - ❌ 难以测试（无法Mock）
- - ❌ 代码重复
- - ❌ 缓存管理混乱


### 来自 docs/development/architecture.md (2026-03-18)

**关键主题**:
- 架构设计文档
- 目录
- Repository模式详解 ⭐
- 什么是Repository模式？
- 架构对比

**重要经验**:
- 直接SQL查询 ❌
- - ❌ 数据访问逻辑散落在各处
- - ❌ 难以测试（无法Mock）
- - ❌ 代码重复
- - ❌ 缓存管理混乱

