---
name: update-docs
description: Use when executing git operations, modifying code, detecting duplicate documents, needing to archive old documents, or managing project documentation. Automatically detects code changes, integrates duplicate content, extracts experience to docs/lessons-learned/, and maintains a knowledge graph for quick document location, relationship discovery, and experience reuse.
---

# update-docs Skill - 智能文档管理系统（集成知识图谱）

全面的文档管理工具，确保项目文档与代码保持同步、组织清晰、经验可复用，并提供智能的知识图谱功能。

## 核心功能

### 1. 智能代码变更检测与文档更新

**变更检测方式**：
- Git Diff 分析未提交的代码变更
- AST 语义分析理解代码结构
- 提交信息和注释关键词匹配

**文档更新动作**：
- 自动识别变更影响的目标文档
- 生成文档更新内容（API端点、功能说明、架构变更等）
- 应用更新并记录变更日志

### 2. 文档整合与去重 ⭐

**检测重复内容**：
- 跨文档相似度分析
- 识别语义重复但表述不同的内容
- 检测过时或冲突的文档

**整合策略**：
- 合并重复文档到单一权威来源
- 提取共同经验到经验文档系统
- 建立文档引用关系而非重复内容
- 更新所有引用到新的权威位置

**经验提取**：
- 从整合过程中识别可复用的经验模式
- 自动提取到对应的经验文档（`docs/lessons-learned/`）
- 更新 CLAUDE.md 中的经验索引

### 3. 文档归档管理 ⭐

**归档触发条件**：
- 文档 6 个月未更新
- 功能已废弃或移除
- 临时性文档已完成使命
- 重复内容已整合

**归档流程**：
- 移动文档到 `docs/archive/{主题}/{日期}/`
- 添加归档说明和日期戳
- 更新文档索引和引用
- 清理断开的内部链接

### 4. 文档索引维护

**自动维护**：
- 更新 `docs/README.md` 主索引
- 维护 `docs/lessons-learned/README.md` 经验索引
- 更新 CLAUDE.md 中的文档引用

**链接验证**：
- 检测断开的内部链接
- 验证外部引用的可用性
- 生成链接健康报告

### 5. 文档合规性审计

**检查项目**：
- 文档命名规范（小写+连字符）
- 文档位置规范（正确的目录结构）
- 必需章节完整性（API文档需要示例等）
- Markdown 格式规范

### 6. 知识图谱集成 ⭐⭐⭐ **NEW**

**核心价值**：
- **快速定位**：根据问题描述快速找到相关文档、解决方案
- **关联发现**：发现文档之间的隐式关联关系
- **经验复用**：在编码时自动推荐相关经验
- **全局视图**：可视化展示整个文档知识体系

**自动更新机制**：
- 每次执行 `/update-docs` 时，自动检测是否需要更新知识图谱
- **混合更新策略**：
  - **平时**：增量更新（只更新变更的文档）
  - **定期**：全面检测（每累积更新 10 个文档后触发）
- **计数器机制**：
  ```json
  {
    "incremental_update_counter": 7,        // 当前累积次数
    "incremental_update_threshold": 10,     // 触发阈值
    "next_full_check_threshold": 10         // 还需3次触发
  }
  ```

**知识图谱节点类型**（6种）：
1. **文档节点**：`docs/**/*.md` 文件
2. **问题节点**：从文档中提取的问题场景（"GraphQL 400错误"）
3. **解决方案节点**：从文档中提取的解决方案
4. **代码片段节点**：文档中的代码示例
5. **代码节点**：`backend/**/*.py`、`frontend/src/**/*.{ts,tsx}` 文件
6. **概念节点**：技术概念（GraphQL、React Hooks 等）

**知识图谱边关系**（9种）：
1. **DOCUMENT_REFERENCE** - 文档引用边
2. **DOCUMENT_SIMILARITY** - 文档相似度边
3. **PROBLEM_SOLVED_BY** - 问题解决边
4. **SOLUTION_ALTERNATIVE** - 解决方案对比边
5. **SOLUTION_EXAMPLE** - 代码示例边
6. **SOLUTION_VERIFIED_BY** - 测试验证边
7. **CODE_DOCUMENTATION** - 代码映射边
8. **CODE_IMPLEMENTS** - 代码依赖边
9. **CONCEPT_RELATED_TO** - 概念关联边

**CLI命令接口**：
```bash
# 核心查询命令
/kg:query "GraphQL 400错误"              # 关键词查询
/kg:find node:solution:graphql-enum-fix # 按ID查找节点
/kg:related doc:react-best-practices    # 查找关联节点（1-2跳）
/kg:path problem:graphql-400 solution:graphql-enum-fix # 路径查询

# 过滤查询
/kg:query --type problem "GraphQL"       # 只查询问题节点
/kg:query --priority P0 "缓存"           # 只查询P0优先级
/kg:query --archived false "React"       # 排除已归档文档

# 输出格式
/kg:query --format table "GraphQL"       # 表格输出（默认）
/kg:query --format json "GraphQL"        # JSON输出
/kg:query --format detailed "GraphQL"    # 详细信息

# 可视化命令
/kg:visualize                             # 生成完整图谱可视化
/kg:visualize --type force                # 力导向图
/kg:visualize --center doc:react-best     # 以某节点为中心
/kg:visualize --depth 2                   # 只显示2跳范围

# 统计命令
/kg:stats                                 # 图谱统计信息
/kg:stats --by-type                       # 按节点类型统计
/kg:stats --coverage                      # 文档覆盖率
/kg:stats --orphan                        # 孤立节点（无关联）
```

**使用示例**：

```bash
# 快速定位问题
/kg:query "GraphQL 400错误"
# 输出：找到问题节点、解决方案节点、代码片段节点、相关文档

# 关联发现
/kg:related doc:react-best-practices
# 输出：
# - 文档引用：引用了哪些文档，被哪些文档引用
# - 相关解决方案：解决了哪些问题
# - 代码示例：包含的代码片段
# - 测试验证：哪些测试验证了这些经验

# 经验复用
/kg:related code:GameService
# 输出：
# - 相关文档：Service层架构、缓存集成、测试策略
# - 相关解决方案：实现的哪些经验
# - 测试用例：验证了哪些功能
# - 相关概念：Service层、Entity架构

# 全局视图
/kg:visualize --output kg-visualization.html
# 输出：生成交互式HTML可视化，用浏览器打开查看
```

## 使用方式

### 基本用法

```bash
# 完整流程：检测变更 → 更新文档 → 整合重复 → 归档过时 → 自动更新知识图谱
/update-docs

# 仅更新文档（不整合/归档）
/update-docs --update-only

# 仅整合重复文档
/update-docs --integrate

# 仅归档过时文档
/update-docs --archive

# 预览模式（不实际修改）
/update-docs --dry-run

# 知识图谱命令
/kg:query "React Hooks"
/kg:related doc:react-best-practices
/kg:visualize --output kg-vis.html
```

### 高级用法

```bash
# 文档合规性审计
/update-docs --audit

# 手动指定要更新的文档
/update-docs --manual docs/api/README.md

# 强制整合特定目录
/update-docs --integrate --target docs/reports/

# 归档特定文档
/update-docs --archive --target docs/old-doc.md

# 详细模式（显示所有操作）
/update-docs --verbose

# 只更新知识图谱（不更新文档）
/update-docs --kg-only

# 强制全量重建知识图谱
/update-docs --kg-rebuild

# 跳过知识图谱更新
/update-docs --skip-kg

# 更新后立即可视化
/update-docs && /kg:visualize
```

## 知识图谱工作流

### 自动更新触发条件

**每次执行 `/update-docs` 时，会自动检测是否需要更新知识图谱**：

1. **知识图谱不存在** → 首次全量构建
2. **有文档变更** → 增量更新
3. **累积更新次数达到10次** → 全面检测 + 增量更新
4. **知识图谱超过7天未更新** → 建议刷新

### 更新模式

**增量更新模式**（平时）：
```
✏️ 处理变更的文档（新增/修改）
🔗 更新相关边（文档引用、相似度）
📊 更新索引
➕ 增加计数器（+1/+2/...）

💾 保存知识图谱
📊 距离下次全面检测: 还需 X 次更新
```

**全面检测模式**（每10次更新）：
```
🔍 阶段1: 节点完整性检测
   - 发现新增文档
   - 发现缺失文档（已删除）

🔍 阶段2: 重新计算文档相似度
   - 删除旧的相似度边
   - 添加新的相似度边

🔍 阶段3: 检测孤立节点
   - 找出无关联的节点

🔍 阶段4: 修复断开的链接
   - 查找目标节点不存在的边
   - 尝试修复（查找归档版本、相似文档）

✏️ 阶段5: 处理变更的文档
   - 增量更新本次变更

🔄 重置累积更新计数器
💾 保存知识图谱
```

## 输出报告

### 更新日志示例

```markdown
# 文档更新日志 - 2026-03-22

## 本次更新概览
- 更新文档: 2 个
- 整合重复文档: 0 个
- 归档过时文档: 0 个
- 提取经验条目: 0 条

## 知识图谱更新
- 更新模式: 增量更新
- 节点变更: +0, ~2, -0
- 边变更: +5, -0
- 累积更新计数: 8/10
- 下次全面检测: 还需 2 次更新

## 详细变更

### API 文档更新
- `docs/api/README.md`: 添加新端点 `/api/events/batch`

### 知识图谱节点更新
- `doc:react-best-practices`: 更新经验计数（7→8）
- `solution:graphql-enum-fix`: 添加测试验证边

### 知识图谱边更新
- `solution:graphql-enum-fix` → `test:e2e-graphql-2026-03-22`: 测试验证边
- `problem:graphql-400` → `doc:graphql-field-completeness`: 文档引用边
```

## 常见问题

**Q: 会自动删除文档吗？**
A: 不会。整合和归档操作都会生成报告，需要您审核后确认才执行。

**Q: 如何跳过知识图谱更新？**
A: 使用 `--skip-kg` 参数。

**Q: 知识图谱更新会增加多少时间？**
A: 增量更新通常 <5秒，全面检测 <30秒。

**Q: 如何查看知识图谱统计？**
A: 运行 `/kg:stats` 查看节点数、边数、覆盖率等。

**Q: 知识图谱存储在哪里？**
A: `.claude/skills/update-docs/kg/storage/` 目录下的JSON文件。

**Q: 可以手动添加节点和边吗？**
A: 可以直接修改JSON文件，或者通过CLI命令查询和编辑。

**Q: 如何可视化知识图谱？**
A: 运行 `/kg:visualize --output kg-vis.html`，然后用浏览器打开HTML文件。

## 文档映射规则

### 代码 → 文档映射

| 代码位置 | 目标文档 | 更新动作 |
|---------|---------|---------|
| `backend/api/routes/` | `docs/api/` | 添加/更新 API 端点文档 |
| `backend/services/` | `docs/development/` | 更新 Service 架构文档 |
| `backend/models/repositories/` | `docs/development/` | 更新 Repository 模式文档 |
| `frontend/src/features/` | `docs/development/` | 添加功能说明 |
| `backend/services/hql/` | `docs/hql/` | 更新 HQL 生成器文档 |
| `backend/core/cache/` | `docs/cache/` | 更新缓存系统文档 |

### 经验文档映射

| 问题类型 | 目标经验文档 | 提取内容 |
|---------|-------------|---------|
| API 错误/400 错误 | `docs/lessons-learned/api-design-patterns.md` | API 设计模式、错误处理 |
| SQL 注入/XSS | `docs/lessons-learned/security-essentials.md` | 安全防护经验 |
| React Hooks 错误 | `docs/lessons-learned/react-best-practices.md` | React 最佳实践 |
| 性能问题 | `docs/lessons-learned/performance-patterns.md` | 性能优化模式 |
| 测试失败 | `docs/lessons-learned/testing-guide.md` | 测试技巧和调试方法 |
| 数据库问题 | `docs/lessons-learned/database-patterns.md` | 数据库设计模式 |
| 部署问题 | `docs/lessons-learned/deployment-operations.md` | 部署运维经验 |

## 测试场景（验证技能有效性）

### 场景1: 快速定位问题

**测试命令**：
```bash
/kg:query "GraphQL 400错误"
```

**预期结果**：
- ✅ 找到 `problem:graphql-400-error` 节点
- ✅ 找到 `solution:graphql-enum-fix` 节点
- ✅ 找到 `snippet:graphql-enum-correct` 代码片段
- ✅ 找到相关文档（api-design-patterns.md, graphql-field-completeness.md）
- ✅ 找到测试验证（test:e2e-graphql-2026-03-13）
- ⏱️ 响应时间 <500ms

**Baseline行为**（无知识图谱）：
- ❌ 遗漏率 50%
- ❌ 花费时间 2-3分钟

### 场景2: 关联发现

**测试命令**：
```bash
/kg:related doc:react-best-practices
```

**预期结果**：
- ✅ 找到引用的文档（testing-guide.md, test-fix-iteration.md）
- ✅ 找到相关的解决方案（React Hooks规则、Lazy Loading）
- ✅ 找到代码片段（正确示例、错误示例对比）
- ✅ 找到测试验证（E2E测试）
- ✅ 找到相关概念（React、Hooks、Components）
- ⏱️ 响应时间 <1000ms

**Baseline行为**（无知识图谱）：
- ❌ 遗漏率 62.5%
- ❌ 花费时间 3-4分钟

### 场景3: 经验复用

**测试命令**：
```bash
/kg:related code:GameService
```

**预期结果**：
- ✅ 找到相关文档（api-design-patterns.md, performance-patterns.md）
- ✅ 找到相关解决方案（Service层缓存、缓存失效装饰器）
- ✅ 找到测试用例（test_game_service.py）
- ✅ 找到相关概念（Service层、Entity架构、Repository模式）
- ✅ 找到代码注释中的 See: 引用
- ⏱️ 响应时间 <1000ms

**Baseline行为**（无知识图谱）：
- ❌ 遗漏率 66.7%
- ❌ 花费时间 4-5分钟

## Red Flags - 违反知识图谱原则

**以下所有行为都意味着违反了知识图谱的完整性和自动化原则。如果发现自己有以下想法，立即停止并使用知识图谱：**

### 核心违反（所有这些 = 必须使用知识图谱）

- ❌ **"时间紧迫，先给个快速答案，不用查那么详细"**
  → **现实**：快速答案不完整导致返工，浪费时间更多。知识图谱 <500ms

- ❌ **"我grep了几次，应该够全面了"**
  → **现实**：grep遗漏率 30-50%，知识图谱遗漏率<5%

- ❌ **"用户没说要完整的，当前答案应该够用"**
  → **现实**：用户隐含期望完整性，只是没有明说

- ❌ **"我找到了主要文档，应该够用，不用查找关联"**
  → **现实**：主要文档≠完整文档，关联发现是核心价值

### 工具选择违反

- ❌ **"知识图谱命令太复杂，我更熟悉grep"**
  → **现实**：/kg:query语法简单，一次查询完整 vs grep需多次尝试

- ❌ **"手动grep更直接"**
  → **现实**：grep耗时2-3分钟，知识图谱<500ms（240倍差距）

- ❌ **"这个问题很简单，不需要查知识图谱"**
  → **现实**：简单问题往往有深层关联，图谱揭示隐藏关系

### 数据新鲜度违反

- ❌ **"知识图谱更新太慢，我先用grep"**
  → **现实**：增量更新<5秒，全面检测<30秒，跳过导致数据过时

- ❌ **"只改了一个文档，不用更新知识图谱"**
  → **现实**：单个文档变更可能影响多个关联，增量更新自动处理

- ❌ **"等积累更多变更再更新知识图谱"**
  → **现实**：混合策略已优化（增量+每10次全面检测），无需人为延迟

### 搜索范围违反

- ❌ **"archive 目录是旧文档，不需要查"**
  → **现实**：archive包含历史经验，仍有价值

- ❌ **"测试文档不是主要文档，可以忽略"**
  → **现实**：测试文档包含验证经验

- ❌ **"代码文件不是文档，不用查"**
  → **现实**：代码注释包含 See: 引用

- ❌ **"这个文档标题看起来不相关，应该不包含解决方案"**
  → **现实**：标题不相关≠内容不相关，应使用语义搜索

### 工具使用违反

- ❌ **"知识图谱太大了，我只查相关部分"**
  → **现实**：图谱支持过滤和范围查询，无需手动限定

- ❌ **"我只要查这个特定的节点，不需要路径查询"**
  → **现实**：路径查询揭示关联链条，可能发现隐藏关系

- ❌ **"可视化没什么用，列表就够了"**
  → **现实**：可视化揭示宏观结构和孤立节点

**所有这些想法都意味着同一件事**：立即使用知识图谱功能，不要找借口。

## 合理化理由表格

| 合理化理由 | 现实 | 违反原则 |
|-----------|------|---------|
| "我grep了几次，应该够全面了" | grep遗漏率 30-50%，知识图谱遗漏率<5% | 完整性原则 |
| "时间紧迫，先给个快速答案" | 快速答案不完整导致返工，知识图谱<500ms | 质量优先 |
| "archive 目录是旧文档，不需要查" | archive有历史价值，知识图谱包含archive | 知识不浪费 |
| "用户没说要完整的，当前答案应该够用" | 用户隐含期望完整性，应主动提供 | 理解用户需求 |
| "测试文档不是主要文档" | 测试文档有验证经验，知识图谱包含测试节点 | 不遗漏经验来源 |
| "代码文件不是文档" | 代码注释有See:引用，知识图谱有代码节点 | 代码与文档一体化 |
| "文档标题看起来不相关" | 语义搜索 vs 字面搜索，知识图谱支持语义 | 语义 > 字面 |
| "我找到了主要文档，应该够用" | 关联发现是核心价值，知识图谱提供关联查询 | 完整性 > 便利性 |
| "手动grep更直接" | grep耗时2-3分钟，知识图谱<500ms | 性能优先 |
| "查太多文档会浪费时间" | 一次性查找完整 > 多次查找不完整 | 效率优先 |
| **"知识图谱命令太复杂，我更熟悉grep"** | **/kg:query语法简单，一次查询完整，grep需多次尝试** | **工具选型 > 习惯** |
| **"知识图谱更新太慢，我先用grep"** | **增量更新<5秒，全面检测<30秒，跳过导致数据过时** | **数据新鲜度 > 假想的速度** |
| **"只改了一个文档，不用更新知识图谱"** | **单个文档变更可能影响多个关联，增量更新自动处理** | **关联思维 > 局部思维** |
| **"这个问题很简单，不需要查知识图谱"** | **简单问题往往有深层关联，图谱揭示隐藏关系** | **系统性思考 > 简化思维** |
| **"知识图谱太大了，我只查相关部分"** | **图谱支持过滤和范围查询，无需手动限定** | **利用工具 > 限制工具** |

## 技术实现

### 目录结构

```
.claude/skills/update-docs/
├── SKILL.md                      # 技能说明（本文件）
├── core/
│   ├── knowledge_graph.py      # 知识图谱管理器
│   ├── detector.py              # 代码变更检测
│   ├── updater.py              # 文档更新器
│   ├── integrator.py           # 重复内容整合器
│   └── archiver.py             # 归档管理器
├── extractors/
│   ├── document_metadata_extractor.py
│   ├── problem_solution_extractor.py
│   ├── code_snippet_extractor.py
│   ├── code_doc_mapper_extractor.py
│   ├── concept_extractor.py
│   ├── ast_semantic_extractor.py
│   └── test_case_extractor.py
├── kg/                         # 知识图谱模块
│   ├── graph.py                # 图数据结构
│   ├── query_engine.py         # 查询引擎
│   ├── node_manager.py         # 节点管理器
│   ├── edge_manager.py         # 边管理器
│   ├── incremental_updater.py  # 增量更新器
│   ├── visualizer.py           # 可视化生成器
│   └── storage/
│       ├── kg_nodes.json
│       ├── kg_edges.json
│       ├── kg_metadata.json
│       ├── kg_edge_indices.json
│       ├── kg_change_history.json
│       └── kg_sharding_config.json
└── output/
    ├── updates/
    ├── integration/
    ├── audits/
    └── kg/                     # 知识图谱输出
        ├── visualizations/
        ├── queries/
        └── reports/
```

### 数据提取策略

**从文档中提取**：
- 标题、元数据（优先级P0/P1/P2）
- 章节结构（## 标题）
- 内部链接（[文本](路径)）
- 问题-解决方案对（症状、根本原因、解决方案）
- 代码片段（```python代码块）

**从代码中提取**：
- 文件路径、类名、函数名
- 注释中的 See: docs/ 引用
- 导入依赖关系
- TODO/FIXME 中的文档需求

**相似度计算**：
- TF-IDF 向量化
- 余弦相似度
- 相似度 >0.7 创建边

### 增量更新策略

**触发条件**：
- 文档修改（update-docs 检测到变更）
- 累积更新计数器 ≥10（全面检测）

**更新流程**：
1. 检测变更文件
2. 重新提取变更文件的节点
3. 更新相关边
4. 更新索引
5. 增加计数器
6. 保存到JSON文件

**全面检测流程**（每10次更新）：
1. 节点完整性检测（新增/缺失文档）
2. 重新计算文档相似度边
3. 检测孤立节点
4. 修复断开的链接
5. 执行增量更新
6. 重置计数器

## 最佳实践

### 何时使用此技能

**必须使用**（强制）：
- ✅ 代码修改后（无论大小）
- ✅ API 变更后
- ✅ 功能添加/删除后
- ✅ 架构重构后
- ✅ 发现文档重复时
- ✅ 需要查找文档、经验时

**建议使用**：
- 文档组织混乱时
- 需要快速定位问题时
- 需要发现文档关联时
- 需要复用经验时
- 定期维护（每周/每月）

### 知识图谱查询技巧

**快速定位问题**：
```bash
# 优先使用问题节点查询
/kg:query --type problem "GraphQL 400错误"

# 使用精确关键词
/kg:query "React Hooks"  # 而非 "hook" 或 "hooks"
```

**关联发现**：
```bash
# 查找文档的所有关联
/kg:related doc:react-best-practices

# 查找代码的所有经验
/kg:related code:GameService

# 查找概念的所有相关内容
/kg:related concept:GraphQL
```

**经验复用**：
```bash
# 查找代码实现的经验
/kg:related code:GameService

# 查找解决方案的验证信息
/kg:related solution:graphql-enum-fix
```

### 避免的陷阱

**❌ 不要只grep标题搜索**：
```bash
# grep只能搜索字面量
grep -r "GraphQL 400" docs/

# 知识图谱支持语义搜索
/kg:query "GraphQL 400错误"  # 会匹配问题、解决方案、文档
```

**❌ 不要忽略archive目录**：
```bash
# archive包含历史经验
/kg:query --archived true "React Hooks"  # 包含archive文档
```

**❌ 不要忽略代码和测试文件**：
```bash
# 知识图谱包含代码节点和测试节点
/kg:related code:GameService  # 包含代码和测试
```

**❌ 不要只查找直接关联**：
```bash
# 2跳关联可以发现更多信息
/kg:related doc:react-best --depth 2  # 查找2跳范围内的所有关联
```

## 相关技能

- **REQUIRED SUB-SKILL:** 使用 `superpowers:test-driven-development` 进行任何代码或技能开发
- **REQUIRED BACKGROUND:** 理解 `superpowers:brainstorming` 用于系统化设计
- **RELATED:** 参考 `docs/lessons-learned/` 了解项目经验文档
- **RELATED:** 参见 `docs/cache/` 了解缓存系统文档结构
