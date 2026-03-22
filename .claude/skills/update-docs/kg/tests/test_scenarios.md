# 知识图谱功能 - 测试场景（GREEN阶段）

> **测试目的**: 验证update-docs技能的知识图谱集成功能是否有效
> **测试方法**: GREEN阶段 - 验证技能解决了baseline中的失败模式
> **日期**: 2026-03-22

---

## 测试场景1：快速定位问题

### 场景设置

**用户请求**:
```
"GraphQL 400错误，快帮我找解决方案！我需要代码示例和相关的所有文档。"
```

**压力类型**:
- ⏰ 时间压力："快帮我"
- 💡 需求完整性："相关的所有文档"
- 🔧 实际需求：需要代码示例

### 预期行为（有知识图谱）

**测试命令**:
```bash
/kg:query "GraphQL 400错误"
```

**预期结果**:
```
✅ 找到6个节点：
   - problem:graphql-400-error (问题节点)
   - solution:graphql-enum-fix (解决方案节点)
   - snippet:graphql-enum-correct (代码片段节点)
   - doc:api-design-patterns (文档节点)
   - doc:graphql-field-completeness (文档节点)
   - test:e2e-graphql-2026-03-13 (测试节点)

✅ 响应时间: <500ms

✅ 给出完整信息：
   - 问题描述: "Enum 'HqlJoinType' cannot represent value: 'LEFT-JOIN'"
   - 解决方案: "使用UPPER_SNAKE_CASE而非kebab-case"
   - 代码示例: "export enum HqlJoinType { LEFT_JOIN = \"LEFT_JOIN\" }"
   - 相关文档: 2个
   - 测试验证: 1个（通过率100%）
```

### Baseline对比

| 指标 | Baseline（无知识图谱） | 有知识图谱 | 改进 |
|-----|---------------------|----------|------|
| 遗漏率 | 50% | <5% | **10倍改进** |
| 花费时间 | 2-3分钟 | <500ms | **240倍改进** |
| 完整性 | 不完整（遗漏代码示例、测试验证） | 完整 | **质量提升** |

---

## 测试场景2：关联发现

### 场景设置

**用户请求**:
```
"React Hooks规则还涉及到哪些文档？我需要完整的列表，包括测试、archive、代码文件中的所有相关内容。"
```

**压力类型**:
- 📊 复杂任务：跨文档、跨文件类型
- ✅ 完整性压力："完整的列表"、"所有相关内容"
- 🔍 隐性需求：archive、代码文件、测试文档

### 预期行为（有知识图谱）

**测试命令**:
```bash
/kg:related doc:react-best-practices --depth 2
```

**预期结果**:
```
✅ 找到12+个关联节点，按类型分组：

📄 文档引用（Documents Referenced）:
   - docs/lessons-learned/testing-guide.md
   - docs/lessons-learned/test-fix-iteration.md
   - CLAUDE.md

🛠️ 解决方案（Solutions）:
   - solution:react-hooks-rules
   - solution:lazy-loading-fix
   - solution:defaultprops-deprecation

💻 代码片段（Code Snippets）:
   - snippet:hooks-correct-example
   - snippet:hooks-wrong-example

🧪 测试验证（Tests Verified By）:
   - test:e2e-react-hooks-2026-03-13
   - test:unit-hooks-validation

💻 实现代码（Implements）:
   - code:ParamSelector.tsx
   - code:FieldCanvas.tsx

💡 概念关联（Concepts）:
   - concept:React
   - concept:Hooks
   - concept:Components

✅ 响应时间: <1000ms

✅ 遗漏率: <5% (vs baseline 62.5%)
```

### Baseline对比

| 指标 | Baseline | 有知识图谱 | 改进 |
|-----|---------|----------|------|
| 遗漏文档数 | 5个 | <1个 | **5倍改进** |
| 遗漏率 | 62.5% | <5% | **12.5倍改进** |
| 跨类型关联 | 仅文档 | 文档+代码+测试+概念 | **4倍覆盖** |
| 花费时间 | 3-4分钟 | <1000ms | **180倍改进** |

---

## 测试场景3：经验复用

### 场景设置

**用户请求**:
```
"我要修改GameService，需要参考所有相关的经验文档。包括：性能优化、测试策略、缓存策略、业务逻辑验证等。给我一个完整的检查清单。"
```

**压力类型**:
- 🤔 具体需求：性能、测试、缓存、业务逻辑
- 📋 检查清单：需要全面的列表
- 🔧 实际应用：编码前的准备工作

### 预期行为（有知识图谱）

**测试命令**:
```bash
/kg:related code:GameService --depth 2
```

**预期结果**:
```
✅ 找到15+个相关节点，按类型分组：

📄 相关文档（Related Documents）:
   - docs/lessons-learned/api-design-patterns.md (Service层架构)
   - docs/lessons-learned/performance-patterns.md (缓存集成)
   - docs/lessons-learned/mutation-business-logic.md (5层验证)
   - docs/cache/development/developer-guide.md (缓存开发)
   - docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION.md (优化报告)
   - CLAUDE.md (开发规范)

🛠️ 解决方案（Solutions）:
   - solution:service-layer-caching (Service层缓存)
   - solution:cache-invalidation-decorator (缓存失效装饰器)
   - solution:entity-repository-pattern (Entity架构)

🧪 测试用例（Test Cases）:
   - test:unit/test_game_service.py (单元测试)
   - test:integration/test_game_service_cache.py (集成测试)

💻 实现代码（Implements）:
   - backend/services/games/game_service.py
   - backend/services/cache/cache_warmer.py (已废弃)

💡 概念关联（Concepts）:
   - concept:Service Layer
   - concept:Repository Pattern
   - concept:Entity Architecture
   - concept:Cache Invalidation

✅ 给出检查清单：
   ☐ 阅读 Service层架构文档
   ☐ 应用缓存集成经验
   ☐ 遵循5层验证架构
   ☐ 查看性能优化报告
   ☐ 参考单元测试和集成测试
   ☐ 避免使用已废弃的CacheWarmer

✅ 响应时间: <1000ms

✅ 遗漏率: <5% (vs baseline 66.7%)
```

### Baseline对比

| 指标 | Baseline | 有知识图谱 | 改进 |
|-----|---------|----------|------|
| 遗漏文档数 | 6个 | <1个 | **6倍改进** |
| 遗漏率 | 66.7% | <5% | **13倍改进** |
| 跨类型覆盖 | 仅文档 | 文档+解决方案+测试+概念+代码 | **5倍覆盖** |
| 花费时间 | 4-5分钟 | <1000ms | **240倍改进** |
| 检查清单完整性 | ❌ 不完整 | ✅ 完整 | **质量提升** |

---

## 测试场景4：全局视图

### 场景设置

**用户请求**:
```
"我想看整个项目文档的知识体系结构，帮我生成交互式可视化图。"
```

### 预期行为（有知识图谱）

**测试命令**:
```bash
/kg:visualize --output kg-visualization.html
```

**预期结果**:
```
✅ 生成交互式HTML文件: kg-visualization.html

✅ 可视化特性:
   - 力导向图布局（D3.js）
   - 节点按类型着色（文档=绿色、问题=红色、解决方案=蓝色等）
   - 可拖拽、缩放、点击节点查看详情
   - 显示边的类型和权重
   - 支持搜索和过滤

✅ 图谱统计:
   - 总节点数: 156
   - 总边数: 239
   - 节点类型分布: 文档37个、问题45个、解决方案48个等
   - 边类型分布: 文档引用89条、相似度23条等
```

### Baseline对比

| 指标 | Baseline | 有知识图谱 | 改进 |
|-----|---------|----------|------|
| 可视化 | ❌ 无法可视化 | ✅ 交互式HTML | **新增能力** |
| 全局视图 | ❌ 需要手动在脑海中构建 | ✅ 一目了然 | **认知负担↓** |
| 关联发现 | ❌ 难以发现跨类型关联 | ✅ 图谱直观显示 | **发现效率↑** |

---

## 验证标准

### 技能触发验证

**触发条件测试**:
```bash
# 测试1: 文档更新后是否触发知识图谱更新
echo "test" >> docs/lessons-learned/test.md
/update-docs
# 预期: 自动检测文档变更，更新知识图谱

# 测试2: 累积10次更新后是否触发全面检测
[执行10次update-docs]
# 预期: 第10次时执行全面检测
```

**YAML frontmatter验证**:
```yaml
# description应该包含知识图谱相关关键词
description: Use when ... | experience reuse | knowledge graph

# 验证方法:
/kg:query "knowledge graph"
# 预期: 找到相关说明
```

### 功能完整性验证

**查询功能验证**:
```bash
# 必须支持以下查询类型：
/kg:query --type problem    # ✅ 问题节点查询
/kg:query --type solution   # ✅ 解决方案节点查询
/kg:query --type document   # ✅ 文档节点查询
/kg:related doc:xxx         # ✅ 关联查询
/kg:path problem solution    # ✅ 路径查询
/kg:visualize                # ✅ 可视化
/kg:stats                    # ✅ 统计信息
```

**数据完整性验证**:
```bash
# 必须包含6种节点类型
/kg:stats --by-type
# 预期: document, problem, solution, code_snippet, code, concept

# 必须包含9种边类型
/kg:stats --by-type --edges
# 预期: DOCUMENT_REFERENCE, DOCUMENT_SIMILARITY, PROBLEM_SOLVED_BY等
```

**性能验证**:
```bash
# 查询响应时间 <500ms
time /kg:query "GraphQL"

# 关联查询 <1000ms
time /kg:related doc:react-best

# 增量更新 <5s
time /update-docs --kg-only
```

### Baseline改进验证

**遗漏率改进**:
| 场景 | Baseline遗漏率 | 目标遗漏率 | 改进倍数 |
|-----|--------------|-----------|---------|
| 场景1 | 50% | <5% | 10倍 |
| 场景2 | 62.5% | <5% | 12.5倍 |
| 场景3 | 66.7% | <5% | 13倍 |

**响应时间改进**:
| 场景 | Baseline时间 | 目标时间 | 改进倍数 |
|-----|------------|----------|---------|
| �景1 | 2-3分钟 | <500ms | 240倍 |
| 场景2 | 3-4分钟 | <1000ms | 180倍 |
| 场景3 | 4-5分钟 | <1000ms | 240倍 |

---

## 测试执行计划

### 阶段1: 技能触发测试（第1天）

- [ ] 验证description是否包含知识图谱关键词
- [ ] 验证update-docs是否自动触发知识图谱更新
- [ ] 验证累积计数器机制

### 阶段2: 功能测试（第2-3天）

- [ ] 执行场景1：快速定位问题
- [ ] 执行场景2：关联发现
- [ ] 执行场景3：经验复用
- [ ] 执行场景4：全局视图

### 阶段3: 性能测试（第4天）

- [ ] 测试查询响应时间（目标<500ms）
- [ ] 测试关联查询响应时间（目标<1000ms）
- [ ] 测试增量更新性能（目标<5s）

### 阶段4: 数据完整性测试（第5天）

- [ ] 验证6种节点类型都已提取
- [ ] 验证9种边关系都已创建
- [ ] 验证文档覆盖率≥95%
- [ ] 验证链接有效率≥95%

### 阶段5: REFACTOR阶段（第6-7天）

- [ ] 识别新的合理化理由
- [ ] 添加到合理化表格
- [ ] 创建red flags列表
- [ ] 重新测试直到bulletproof

---

## 预期成果

**技能文档已更新**:
- ✅ SKILL.md包含了完整的知识图谱集成章节
- ✅ YAML frontmatter正确描述触发条件
- ✅ CLI命令参考清晰
- ✅ Red flags列表完整
- ✅ 合理化理由表格完整

**测试场景已验证**:
- ✅ 场景1：快速定位问题（遗漏率从50%降到<5%）
- ✅ 场景2：关联发现（遗漏率从62.5%降到<5%）
- ✅ 场景3：经验复用（遗漏率从66.7%降到<5%）
- ✅ 场景4：全局视图（新增能力）

**性能指标已达标**:
- ✅ 查询响应时间<500ms
- ✅ 关联查询响应时间<1000ms
- ✅ 增量更新时间<5s
- ✅ 全面检测时间<30s

**数据质量已提升**:
- ✅ 文档覆盖率≥95%
- ✅ 链接有效率≥95%
- ✅ 孤立节点比例<5%

---

## 下一步：部署到实际技能文件

**如果以上测试场景全部通过**，则：
1. 更新 `.claude/skills/update-docs/SKILL.md`
2. 创建 `.claude/skills/update-docs/kg/` 目录结构
3. 创建核心知识图谱模块文件
4. 提交到git并推送

**如果测试场景未通过**：
1. 识别未通过的测试场景
2. 分析失败原因
3. 返回REFACTOR阶段，调整技能文档
4. 重新测试直到bulletproof
