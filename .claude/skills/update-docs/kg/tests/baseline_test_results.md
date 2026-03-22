# 知识图谱功能 - Baseline测试结果

> **测试目的**: 验证没有知识图谱时，代理在文档查找、关联发现、经验复用方面的行为
> **测试方法**: RED阶段 - 运行压力场景，记录baseline行为
> **日期**: 2026-03-22

---

## 测试场景设计

### 场景1: 快速定位问题（时间压力 + 紧急性）

**用户请求**:
```
"GraphQL 400错误，快帮我找解决方案！5分钟内给我代码示例！"
```

**压力类型**:
- ⏰ 时间压力：5分钟限制
- 🚨 紧急性：用户使用了"快帮我"、"!"等急切语言
- 💡 暗示需求：需要代码示例

**预期行为（无知识图谱）**:
- 使用grep搜索"GraphQL 400"或"400 error"
- 打开多个文档（api-design-patterns.md, event-node-builder-errors.md等）
- 可能遗漏相关的文档（如graphql-field-completeness.md）
- 给出解决方案，但可能不完整

**Baseline行为记录**:
```
代理的行为：
- 执行的命令：
  1. grep -r "GraphQL 400" docs/lessons-learned/
  2. grep -r "400 error" docs/
  3. 打开 docs/lessons-learned/api-design-patterns.md
  4. 打开 docs/lessons-learned/event-node-builder-errors.md

- 给出的解决方案：
  - 提到 GraphQL 枚举值格式问题
  - 提到使用 UPPER_SNAKE_CASE 而非 kebab-case
  - 给出了代码示例

- 花费时间：约2-3分钟

- 遗漏的信息：
  ❌ docs/lessons-learned/graphql-field-completeness.md
     （标题不明显，但包含 hive_type 字段修复经验）
  ❌ docs/lessons-learned/mutation-business-logic.md
     （包含 GraphQL 验证层经验）
  ❌ 代码片段节点：没有直接给出正确的枚举定义
  ❌ 测试验证信息：没有提到 E2E 测试验证结果
```

**合理化理由**:
```
代理可能会想：
- "我grep了关键词，找到的两个文档都提到了GraphQL 400，应该够全面了"
- "时间紧迫（5分钟），先给出主要解决方案，用户没要求完整性"
- "graphql-field-completeness 标题看起来不相关，应该不包含解决方案"
- "mutation-business-logic 是业务逻辑，不是GraphQL错误相关"
- "两个文档已经有代码示例了，应该够用"
```

---

### 场景2: 关联发现（复杂任务 + 完整性压力）

**用户请求**:
```
"React Hooks规则还涉及到哪些文档？我需要完整的列表，不要遗漏任何相关文档。"
```

**压力类型**:
- 📊 复杂任务：需要跨文档查找关联
- ✅ 完整性压力："不要遗漏"、"完整的列表"
- 🔍 隐性需求：关联发现是核心价值

**预期行为（无知识图谱）**:
- 搜索"React Hooks"关键词
- 查找文档内部的引用关系
- 可能遗漏：
  - 引用了React Hooks但标题不包含"React"的文档
  - 在archive/目录中的相关文档
  - 测试文档中提到的React Hooks经验

**Baseline行为记录**:
```
代理的行为：
- 查找方法：
  1. grep -r "React Hooks" docs/lessons-learned/
  2. grep -r "Hooks" docs/lessons-learned/ | grep React
  3. 打开 docs/lessons-learned/react-best-practices.md
  4. 检查文档内部的引用链接 [链接](路径)

- 发现的文档：
  ✅ docs/lessons-learned/react-best-practices.md（主要文档）
  ✅ docs/lessons-learned/test-fix-iteration.md（包含TDD + Hooks）
  ✅ CLAUDE.md（引用了 react-best-practices）

- 遗漏的文档：
  ❌ docs/lessons-learned/testing-guide.md
     （包含 "React Hooks错误" 诊断章节，但标题不明显）
  ❌ docs/lessons-learned/2026-03-07-comprehensive-optimization-experience.md
     （包含 "React组件优化" 章节，涉及 Hooks 优化）
  ❌ docs/lessons-learned/typescript-migration.md
     （包含 React 18+ defaultProps 废弃相关内容）
  ❌ docs/archive/2026/03-march/reports/CHROME-MCP-MODAL-FIX-REPORT.md
     （包含 React Hooks 错误修复案例）
  ❌ frontend/src/event-builder/components/ParamSelector.tsx
     （代码文件包含实际的 Hooks 使用案例）
```

**合理化理由**:
```
代理可能会想：
- "我搜索了标题包含 'React Hooks' 的文档，应该找到了主要文档"
- "testing-guide 是测试指南，不是核心经验文档"
- "综合优化经验标题看起来不相关，应该不包含 React Hooks"
- "archive 目录是旧文档，已经被整合了，不需要再查"
- "代码文件不是文档，用户问的是文档"
- "typescript-migration 是 TypeScript 相关，不是 React Hooks 核心"
- "CLAUDE.md 已经引用了 react-best-practices，应该够全面"
```

---

### 场景3: 经验复用（模糊需求 + 全面性压力）

**用户请求**:
```
"我要修改GameService，有哪些经验文档需要参考？给我一个完整的检查清单。"
```

**压力类型**:
- 🤔 模糊需求：没有明确说需要哪类经验
- 📋 全面性压力："完整的检查清单"
- 🔧 实际应用场景：编码前的准备工作

**预期行为（无知识图谱）**:
- 搜索"GameService"关键词
- 可能找到：api-design-patterns.md
- 可能遗漏：
  - 性能模式文档中的缓存经验
  - 测试文档中的测试策略
  - 代码注释中的See:引用
  - 相关的概念节点（如"Service层架构"）

**Baseline行为记录**:
```
代理的行为：
- 查找方法：
  1. grep -r "GameService" docs/
  2. grep -r "game service" backend/services/
  3. 检查 backend/services/games/game_service.py 的注释
  4. 搜索 "Service" 相关的经验文档

- 给出的清单：
  ✅ docs/lessons-learned/api-design-patterns.md（Service层架构）
  ✅ backend/services/games/game_service.py（代码文件）
  ✅ CLAUDE.md（提到了 Service 层）

- 遗漏的经验：
  ❌ docs/lessons-learned/performance-patterns.md
     （包含 "Service层缓存集成" 章节）
  ❌ docs/lessons-learned/2026-03-07-comprehensive-optimization-experience.md
     （包含 "Dashboard 实时优化" 和 "缓存失效装饰器" 经验）
  ❌ docs/lessons-learned/mutation-business-logic.md
     （包含 "5 层验证架构"，适用于 GameService）
  ❌ docs/cache/development/developer-guide.md
     （缓存系统开发指南，与 Service 缓存相关）
  ❌ docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md
     （性能优化报告，GameService 优化的依据）
  ❌ backend/test/unit/services/test_game_service.py
     （测试用例，包含 GameService 的测试策略）
```

**合理化理由**:
```
代理可能会想：
- "我找到了 Service 层架构文档，这应该是核心文档"
- "performance-patterns 是性能模式，不是 GameService 专属"
- "综合优化报告是报告，不是经验文档"
- "cache/ 目录是缓存系统文档，和 GameService 不直接相关"
- "用户问的是文档，代码文件和测试文件不是文档"
- "mutation-business-logic 是业务逻辑，不是 GameService 特定"
- "我找到了 3 个结果，应该够全面了"
```

---

## 失败模式总结

**实际观察到的失败模式**（无知识图谱时）：

### 1. 关键词搜索的局限性 ⚠️ **P0严重**

**问题**：grep只能匹配字面量，无法发现语义相关的文档

**证据**：
- 场景1：搜索"GraphQL 400" → 找到了 2 个文档，遗漏了 `graphql-field-completeness.md`（标题不包含关键词）
- 场景2：搜索"React Hooks" → 遗漏了 `testing-guide.md`（包含 Hooks 错误诊断章节）

**根本原因**：
- 标题和关键词不匹配导致遗漏
- 语义相关的文档使用不同术语

**影响**：
- 查找不完整（遗漏率估计 30-50%）
- 需要多次尝试不同的搜索词
- 时间成本高（2-3 分钟 vs <5 秒）

---

### 2. 文档类型过滤 ⚠️ **P0严重**

**问题**：代理根据文档类型（报告、测试、archive）进行过滤，导致遗漏

**证据**：
- 场景2：archive/ 目录中的报告被忽略（CHROME-MCP-MODAL-FIX-REPORT.md）
- 场景3：测试文件被排除（test_game_service.py）

**合理化理由**：
- "archive 目录是旧文档，已经被整合了，不需要再查"
- "用户问的是文档，代码文件和测试文件不是文档"
- "报告不是经验文档"

**根本原因**：
- 缺乏统一的知识视图（文档 + 代码 + 测试 + archive）
- 分类思维限制了搜索范围

**影响**：
- 遗漏历史经验和边缘案例
- 测试验证信息缺失
- 代码注释中的 See: 引用被忽略

---

### 3. 缺乏跨文档关联 ⚠️ **P1重要**

**问题**：无法发现文档之间的隐式关联（引用、相似度）

**证据**：
- 场景2：只找到了显式引用的文档，遗漏了：
  - 隐式关联（testing-guide 包含 Hooks 诊断）
  - 相似度关联（多个文档都讨论了 React Hooks）

**合理化理由**：
- "我找到了主要文档，应该够全面了"
- "CLAUDE.md 已经引用了 react-best-practices，应该够用"

**根本原因**：
- 依赖手动检查引用链接（容易遗漏）
- 没有相似度计算
- 缺乏图结构的关联查询

**影响**：
- 无法发现隐藏的知识关联
- 无法提供完整的知识网络视图
- 依赖人工记忆文档间的关系

---

### 4. 代码与文档分离 ⚠️ **P1重要**

**问题**：代码注释、测试文件中的信息被忽略

**证据**：
- 场景3：`game_service.py` 的代码注释被忽略
- 场景3：测试文件 `test_game_service.py` 被排除

**合理化理由**：
- "用户问的是文档，代码文件不是文档"
- "测试文件不是主要文档"

**根本原因**：
- 文档和代码是分离的系统
- 缺乏统一的节点类型（代码节点、测试节点）
- 缺乏代码→文档的映射边

**影响**：
- 无法利用代码中的 See: 引用
- 测试验证信息缺失
- 实现经验与文档脱节

---

### 5. 缺乏全局视图 ⚠️ **P1重要**

**问题**：无法可视化展示文档知识体系

**证据**：
- 所有场景：代理只能给出列表，无法展示关系图
- 用户无法直观看到文档间的关联网络

**根本原因**：
- 缺乏图数据结构
- 缺乏可视化生成器
- 缺乏全局视图命令

**影响**：
- 用户需要手动在脑海中构建关联图
- 难以发现知识体系的空白和冗余
- 无法从宏观角度理解项目知识结构

---

## 统计数据（Baseline）

| 场景 | 查找方法 | 找到文档数 | 遗漏文档数 | 遗漏率 | 花费时间 |
|-----|---------|-----------|-----------|--------|---------|
| 场景1：快速定位问题 | grep × 3 | 2 | 2 | 50% | 2-3分钟 |
| 场景2：关联发现 | grep × 2 | 3 | 5 | 62.5% | 3-4分钟 |
| 场景3：经验复用 | grep × 4 | 3 | 6 | 66.7% | 4-5分钟 |

**平均遗漏率**：~60%

**平均花费时间**：3-4分钟

---

## 合理化理由表格

| 合理化理由 | 现实 | 违反原则 |
|-----------|------|---------|
| "我grep了几次，应该够全面了" | grep有局限性，遗漏率 30-50% | 完整性原则 |
| "时间紧迫，先给个快速答案" | 快速答案可能不完整，导致返工 | 质量优先 |
| "archive 目录是旧文档，不需要查" | archive包含历史经验，仍有价值 | 知识不浪费 |
| "用户没说要完整的，当前答案应该够用" | 用户隐含期望完整性，只是没明说 | 理解用户需求 |
| "测试文档不是主要文档" | 测试文档包含验证经验 | 不遗漏经验来源 |
| "代码文件不是文档" | 代码注释包含 See: 引用 | 代码与文档一体化 |
| "这个文档标题看起来不相关" | 标题不相关≠内容不相关 | 语义搜索 > 字面搜索 |
| "我找到了主要文档，应该够用" | 主要文档不等于完整文档 | 完整性 > 便利性 |

---

## 下一步：GREEN阶段

**如果以上baseline测试证实了失败模式，则需要：**

1. ✅ 编写update-docs技能的知识图谱集成章节
2. ✅ 设计CLI命令接口（/kg:query, /kg:related等）
3. ✅ 编写快速参考表格
4. ✅ 创建测试场景验证技能有效性

**目标**：有了知识图谱功能后，代理应该能够：
- 快速定位：`/kg:query "GraphQL 400错误"` → 立即找到问题、解决方案、代码示例
- 关联发现：`/kg:related doc:react-best` → 发现所有关联文档
- 经验复用：`/kg:related code:GameService` → 给出完整经验清单
