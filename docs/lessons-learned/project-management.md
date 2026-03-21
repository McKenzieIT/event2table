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

## 文档整合管理 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [文档整合报告](../archive/2026/03-march/doc-integration-report.md) (2026-03-19)

### 核心原则

**避免文档重复 + 建立清晰引用关系**

### 问题识别

**症状**:
- 🚨 相同内容在多个文档中重复
- 🚨 文档数量过多难以维护
- 🚨 更新时需要同步多个文档
- 🚨 用户不知道哪个是权威来源

**影响**:
- ⚠️ 维护成本增加
- ⚠️ 文档不一致风险
- ⚠️ 用户困惑

### 整合策略

**1. 相似度检测**:
```python
# 使用TF-IDF + 余弦相似度检测重复内容
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def detect_similarity(doc1, doc2):
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([doc1, doc2])
    similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return similarity

# 阈值设置
# - 0.7+ (70%): 高度相似，应该整合
# - 0.5-0.7 (50-70%): 中度相似，需要人工判断
# - <0.5 (50%): 低相似度，保持独立
```

**2. 整合决策树**:
```
相似度 > 70%?
├─ 是 → 整合到权威来源
│  └─ 归档重复文档
└─ 否 → 检查功能独立性
   ├─ 功能相同 → 合并
   └─ 功能不同 → 保持独立，添加交叉引用
```

**3. 权威来源选择**:
```markdown
优先级：
1. 最全面的文档
2. 最新更新的文档
3. 在主路径的文档（docs/development/ 而非 docs/archive/）
4. 被其他文档引用最多的文档
```

### 整合实施

**阶段1: 分析**
```bash
# 运行文档相似度分析
python scripts/tools/doc_analyzer.py docs 0.7

# 输出：
# - 整合报告 (Markdown)
# - JSON数据 (用于自动化)
# - 重复组列表
```

**阶段2: 整合**
```markdown
1. 保留权威来源
2. 提取重复文档中的独特内容
3. 合并到权威来源
4. 添加引用说明
5. 更新所有引用
```

**阶段3: 归档**
```bash
# 创建归档目录
mkdir -p docs/archive/2026/03-march/

# 移动重复文档
mv docs/development/branch-protection-setup.md \
   docs/archive/2026/03-march/development/

# 添加归档说明
echo "归档于 2026-03-19，内容已整合到 github-setup-guide.md" \
  >> docs/archive/2026/03-march/development/branch-protection-setup.md
```

**阶段4: 验证**
```bash
# 检查断开的链接
find docs -name "*.md" -exec grep -H "\[.*\](" {} \; | \
  while read line; do
    link=$(echo "$line" | grep -oP '(?<=\][^\)]*\]\()[^\)]+')
    if [ ! -f "docs/$link" ]; then
      echo "断开的链接: $link"
    fi
  done
```

### 最佳实践

**✅ DO (应该做)**:
1. **创建索引文档**: 比如强制合并多个功能文档
   ```markdown
   # docs/api/README.md
   ## API索引
   - [Games API](GAMES-API.md)
   - [Events API](EVENTS-API.md)
   - [Flows API](FLOWS-API.md)
   ```

2. **使用引用而非重复**:
   ```markdown
   ❌ 错误：在每个文档中重复相同内容
   ## React Hooks规则
   1. 只在顶层调用Hooks
   2. 不在条件语句中使用Hooks

   ✅ 正确：引用权威来源
   ## React Hooks规则
   详见：[React最佳实践](../lessons-learned/react-best-practices.md#hooks规则)
   ```

3. **保持功能独立性**:
   ```python
   # EVENT-NODES-API.md vs CANVAS-API.md
   # 相似度59%，但功能不同
   # → 保持独立，添加交叉引用
   ```

4. **归档保留历史**:
   ```bash
   # 归档而非删除
   mv old-doc.md docs/archive/2026/03-march/

   # 保留引用
   # "旧版本见：archive/2026/03-march/old-doc.md"
   ```

**❌ DON'T (不应该做)**:
1. **强制合并不同功能的文档**:
   - API文档虽然格式相似，但功能不同
   - 应该创建索引文档而非合并

2. **删除旧文档**:
   - 归档而非删除
   - 保留历史记录

3. **忽略相似度阈值**:
   - 阈值太低会误判（50%以下）
   - 阈值太高会漏掉（70%以上）
   - 推荐使用65%作为初始阈值

4. **归档后不更新引用**:
   - 必须更新所有引用
   - 添加归档说明

### 工具和脚本

**文档分析脚本** (`scripts/tools/doc_analyzer.py`):
```python
# 检测文档相似度
python scripts/tools/doc_analyzer.py docs 0.65

# 输出：
# - doc-integration-report.md
# - doc-integration-report.json
```

**链接验证脚本** (`scripts/tools/verify_links.py`):
```bash
# 验证所有内部链接
python scripts/tools/verify_links.py docs/

# 输出：
# - 断开的链接列表
# - 链接健康报告
```

### 实际案例

**案例1: GitHub设置文档整合** (2026-03-19)
```
问题：
- github-setup-guide.md (431行)
- branch-protection-setup.md (151行)
- 相似度50%

分析：
- branch-protection-setup.md 的内容已在 github-setup-guide.md 中
- 但有独特的API调用方法

解决方案：
1. 将API调用方法合并到 github-setup-guide.md
2. 归档 branch-protection-setup.md
3. 更新所有引用

结果：
✅ 减少文档数量
✅ 保持内容完整性
✅ 用户体验提升
```

**案例2: API文档索引** (2026-03-19)
```
问题：
- EVENT-NODES-API.md vs CANVAS-API.md (相似度59%)
- FLOWS-API.md vs JOIN-CONFIGS-API.md (相似度53%)

分析：
- 格式相似但功能不同
- 强制合并会降低可用性

解决方案：
1. 保持文档独立
2. 创建统一索引 (docs/api/README.md)
3. 添加交叉引用

结果：
✅ 功能独立性保持
✅ 统一访问入口
✅ 清晰的文档组织
```

### 文档生命周期

```
活跃文档 (docs/)
├─ 开发指南 (docs/development/)
├─ API文档 (docs/api/)
├─ 测试文档 (docs/testing/)
└─ 经验文档 (docs/lessons-learned/)

↓ 6个月未更新或功能废弃

归档文档 (docs/archive/)
├─ 2026/03-march/
│  ├─ reports/
│  ├─ testing/
│  └─ development/
└─ ...
```

**归档触发条件**:
- ✅ 文档6个月未更新
- ✅ 功能已废弃或移除
- ✅ 临时性文档已完成使命
- ✅ 重复内容已整合

**归档结构**:
```
docs/archive/
├── {year}/{month}/
│   ├── {category}/
│   │   ├── document-name.md
│   │   └── README.md (归档说明)
```

### 代码审查清单

**文档整合时检查**:
- [ ] 是否检测了文档相似度？
- [ ] 相似度阈值是否合理（65-70%）？
- [ ] 功能是否独立？
- [ ] 是否保留了独特内容？
- [ ] 是否更新了所有引用？
- [ ] 是否正确归档（而非删除）？
- [ ] 是否添加了归档说明？

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


### 来自 docs/lessons-learned/service-architecture.md (2026-03-20)

**关键主题**:
- Service Layer Architecture Experience
- Overview
- ERS Architecture Overview
- Critical Architecture Violation: Direct Database Access
- Problem Symptoms

**重要经验**:
- │  - ❌ 不包含数据库访问逻辑                            │
- │  - ✅ 所有数据库访问都在这里                          │
- # ❌ WRONG: Service layer with direct DB access
- # Service层构建SQL查询（应该在Repository层）
- # ✅ CORRECT: Service layer uses Repository


## 代码质量改进 ⭐⭐⭐ **P0重要**

> **来源**: 代码重复消除项目（2026-03-16）
> **优先级**: P0 | **最后更新**: 2026-03-21

### 核心经验

#### 1. 代码重复的识别与量化 ⭐⭐⭐

**洞察**: 代码重复是技术债务的主要来源，必须系统化识别和消除

**代码重复统计**（2026-03-16分析）:

**后端代码**:
- 总行数: 7,624行 (backend/api/routes/)
- 重复模式:
  - 错误处理: 266个 `json_error_response` 调用
  - 异常捕获: 127个 `except Exception as e` 模式
  - 响应构建: 91个 `json_success_response` 调用
  - 参数验证: 大量重复的game_gid验证逻辑
  - 分页逻辑: 重复的page/per_page参数处理

**前端代码**:
- 总行数: 6,497行 (frontend/src/features/)
- 重复模式:
  - useState hooks: 137个模式
  - useCallback hooks: 62个模式
  - Modal状态管理: 重复的isOpen/onClose逻辑
  - 表单验证: 重复的验证逻辑
  - API错误处理: 重复的try-catch模式

**量化指标**:
- 总重复代码: ~9,500行
- 目标减少: 80%（~7,600行）
- 预期净减少: ~3,240行（新增1,000行工具代码 - 消除4,240行重复）

#### 2. 通用工具模块的设计 ⭐⭐⭐

**后端通用工具模块** (`backend/core/utils/common.py`, 450行):
- 日期时间处理
- 字符串清理和验证
- 分页参数处理
- **错误处理装饰器** - 节省1,862-2,660行
- 请求验证辅助
- 批量操作辅助
- 数据转换辅助
- 日志辅助

**前端通用工具模块** (`frontend/src/shared/utils/commonUtils.ts`, 550行):
- 表单验证
- 日期时间格式化
- 字符串处理
- API响应处理
- **Modal状态管理** - 节省300-400行
- React Hooks辅助
- 分页工具
- 类型守卫
- 数组工具

#### 3. 重构实施策略 ⭐⭐⭐

**Phase 1: 后端重构** (优先级: P0)
1. 应用 `@handle_api_errors` 装饰器到所有API端点
2. 使用 `get_pagination_params` 替换分页逻辑
3. 使用 `validate_request_json` 统一请求验证

**Phase 2: 前端重构** (优先级: P1)
1. 使用共享Modal状态管理
2. 使用通用表单验证
3. 使用统一API错误处理

**Phase 3: 测试验证** (优先级: P0)
1. 运行所有单元测试
2. 运行E2E测试
3. 性能测试
4. 代码覆盖率检查

**成功标准**:
- [ ] 代码重复从 ~9,500行 减少到 < 2,000行
- [ ] 新增工具函数代码 < 1,500行
- [ ] 净减少代码 > 3,000行
- [ ] 测试通过率 100%
- [ ] 代码覆盖率 ≥ 80%


## 文档管理经验 ⭐⭐⭐ **P0重要**

> **来源**: 2026年3月文档整合项目
> **优先级**: P0 | **最后更新**: 2026-03-21

### 核心经验

#### 1. Agent辅助分析的价值 ⭐⭐⭐

**洞察**: 使用Agent分析大量临时报告，高效提取关键经验点

**数据对比**:
- **手动分析**: 52个报告 × 10分钟/报告 = 520分钟（8.7小时）
- **Agent分析**: 52个报告 × 2分钟/报告 = 104分钟（1.7小时）
- **时间节省**: 80%

**质量提升**:
- 系统化分类整理
- 覆盖范围全面（6个主要类别）
- 经验质量高（结构化输出）

#### 2. 经验文档系统的威力 ⭐⭐⭐

**洞察**: 整合经验到经验文档系统，避免知识流失

**效果对比**:

| 维度 | 旧方式（散落报告） | 新方式（经验文档系统） |
|------|------------------|---------------------|
| 查找效率 | 需要回忆日期，逐个打开 | 按主题快速定位 |
| 经验复用 | 每次重新学习 | 直接应用经验 |
| 知识流失 | 高（报告被遗忘） | 低（经验持续维护） |
| 维护成本 | 高（散落各处） | 低（集中管理） |

#### 3. 根目录清理的重要性 ⭐⭐

**洞察**: 根目录整洁性直接影响项目可维护性

**数据对比**:
- **之前**: 56个markdown文件（52个临时报告 + 4个核心文档）
- **现在**: 3个核心文档（CLAUDE.md, README.md, CHANGELOG.md）
- **减少**: 94.6%

**根目录规范**:
```
项目根目录/
├── CLAUDE.md          # 开发规范（唯一权威来源）
├── README.md          # 项目说明
├── CHANGELOG.md       # 更新日志
└── LICENSE            # 许可证
```

**临时文档处理流程**:
1. 创建临时报告时，放在 `docs/reports/YYYY-MM/`
2. 报告完成后，提取经验到经验文档
3. 归档报告到 `docs/archive/YYYY-MM/`
4. 更新索引和引用

#### 4. 完整实现原则的实践 ⭐⭐⭐

**原则声明**:
- ❌ **禁止任何理由的简化实现**（token不足、时间紧迫）
- ❌ **禁止留空或占位符实现**（TODO、返回默认值）
- ✅ **质量优先于完整性**（部分完整 > 全部残缺）
- ✅ **透明沟通进度**（主动告知用户资源状态）

**2026-03文档整合案例**:
- ✅ 52个报告全部分析（未因token限制跳过）
- ✅ 23个经验点完整提取（未因时间限制简化）
- ✅ 14个Critical Rules全部保留
- ✅ 所有链接验证完成

**文档生命周期管理**:

**1. 活跃文档** (`docs/`)
- 经常更新
- 反映当前最佳实践
- 包括：开发指南、测试文档、API文档、经验文档

**2. 归档文档** (`docs/archive/`)
- 按主题分类
- 历史参考价值
- 组织结构：`archive/{主题}/{日期}/`

**3. 临时文档**
- 短期使用
- 完成后删除或归档

**成功标准**:
- [ ] 根目录整洁（仅保留核心文档）
- [ ] 经验文档完整（所有经验已提取）
- [ ] 归档有序（按日期+主题组织）
- [ ] 索引完整（所有文档可查找）
- [ ] 链接有效（无断开链接）

