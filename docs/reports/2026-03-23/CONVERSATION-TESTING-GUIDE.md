# Claude Semantic Experience Extractor - 对话式测试指南

> **日期**: 2026-03-23
> **版本**: 1.0
> **目的**: 验证Claude语义提取器的提取质量

---

## 核心理念

**对话式测试**（Conversation-based Testing）与传统的Python脚本测试不同：

| 方面 | Python脚本测试 | 对话式测试 |
|------|---------------|-------------|
| 测试方式 | 自动化脚本 | 人机对话 |
| Claude思考 | ❌ 未触发 | ✅ 深度思考 |
| 灵活性 | 固定流程 | 动态调整 |
| 发现问题 | 自动检测 | 对话发现 |
| 验证方式 | 断言(Assert) | 人工判断 |

**关键优势**:
- ✅ 触发Claude深度思考（而非规则匹配）
- ✅ 灵活调整提取策略
- ✅ 发现边缘情况
- ✅ 验证思考质量

---

## 4轮思考工作流

### Round 1: 快速阅读（Quick Reading）

**目的**: 理解文档主题和结构，识别问题-解决方案候选

**对话提示**:
```
请阅读这份文档，快速了解主题和结构。

文档内容：
[插入文档内容]

请回答：
1. 这份文档的主题是什么？
2. 文档描述了哪些问题？
3. 文档提供了哪些解决方案？
```

**期望输出**:
- 文档主题总结
- 问题列表（候选）
- 解决方案列表（候选）

### Round 2: 深度思考（Deep Thinking）

**目的**: 分析问题根本原因，评估解决方案质量，判断经验可复用性

**对话提示**:
```
现在深入分析这份文档，提取可复用的经验。

请思考：
1. 问题的根本原因是什么？
2. 解决方案的核心思路是什么？
3. 这个经验能否复用到其他场景？
4. 经验的质量如何（0-1分）？

请以以下格式输出：
- Title: 经验标题
- Problem: 问题描述（避免与Solution重复）
- Solution: 解决方案（避免与Problem重复）
- Category: 类别（11个固定类别之一）
- Priority: P0/P1/P2
- Tags: 技术标签
- Quality Score: 0-1分
- Reason: 评分理由
```

**期望输出**:
- 结构化的Experience对象
- 质量评分和理由

### Round 3: 质量自检（Quality Self-Check）

**目的**: 检查Problem/Solution字段重复，验证经验完整性

**对话提示**:
```
请检查刚才提取的经验：

1. Problem和Solution字段是否有重复内容？
   - 如果有重复，请修正重复部分

2. 经验是否完整？
   - Problem字段是否清晰描述问题？
   - Solution字段是否提供可操作的解决方案？
   - 是否有代码示例或具体步骤？

3. 质量评分是否合理？
   - 根据以下标准重新评分：
     * 唯一性（1 - 与历史经验的最大相似度）
     * 实用性（代码示例、可操作步骤）
     * 完整性（所有字段填充、详细描述）

请输出修正后的Experience对象。
```

**期望输出**:
- 修正后的Experience对象
- 重复问题已解决
- 质量评分已更新

### Round 4: 最终输出（Final Output）

**目的**: 生成高质量的Experience对象，准备更新到lessons-learned/

**对话提示**:
```
请最终确认提取的经验：

[Experience对象内容]

请确认：
1. ✅ Problem和Solution字段无重复
2. ✅ 经验内容完整
3. ✅ 类别映射正确
4. ✅ 标签相关

如果确认无误，请输出"✅ 准备更新到经验文档"。
```

**期望输出**:
- ✅ 准备更新到经验文档
- 最终的Experience对象

---

## 5个测试场景

### 场景1: React Hooks错误提取

**测试文档**: `docs/lessons-learned/react-best-practices.md` (React Hooks规则章节)

**输入**:
```
请从React Hooks规则章节提取经验：
- 问题：违反React Hooks规则导致组件崩溃
- 解决方案：所有Hook在条件返回之前调用
```

**期望结果**:
- Title: "React Hooks规则遵守"
- Problem: 清晰描述违反规则导致的崩溃
- Solution: 描述正确的Hook调用顺序
- Category: "React"
- Quality Score: >0.8

### 场景2: Lazy Loading问题提取

**测试文档**: `docs/lessons-learned/react-best-practices.md` (Lazy Loading章节)

**输入**:
```
请从Lazy Loading章节提取经验：
- 问题：不恰当的lazy loading导致页面卡在加载状态
- 解决方案：小型组件直接导入，大型组件使用lazy loading
```

**期望结果**:
- Title: "Lazy Loading最佳实践"
- Problem: 描述双重Suspense嵌套问题
- Solution: 描述何时使用lazy loading
- Category: "React"
- Quality Score: >0.8

### 场景3: API设计模式提取

**测试文档**: `docs/lessons-learned/api-design-patterns.md` (DataLoader实施章节)

**输入**:
```
请从DataLoader实施章节提取经验：
- 问题：N+1查询问题导致性能下降
- 解决方案：使用DataLoader批量查询优化
```

**期望结果**:
- Title: "DataLoader批量查询优化"
- Problem: 描述N+1查询问题
- Solution: 描述DataLoader实施步骤
- Category: "API"
- Quality Score: >0.8

### 场景4: 缓存失效策略提取

**测试文档**: `docs/lessons-learned/performance-patterns.md` (缓存失效章节)

**输入**:
```
请从缓存失效章节提取经验：
- 问题：缓存更新后数据不一致
- 解决方案：使用@cache_invalidate装饰器自动清理缓存
```

**期望结果**:
- Title: "缓存失效装饰器自动化"
- Problem: 描述数据不一致问题
- Solution: 描述装饰器使用方法
- Category: "Performance"
- Quality Score: >0.8

### 场景5: 测试修复迭代提取

**测试文档**: `docs/lessons-learned/test-fix-iteration.md` (4轮迭代章节)

**输入**:
```
请从测试修复迭代章节提取经验：
- 问题：测试失败率从20%到100%的提升
- 解决方案：TDD + 并行执行策略
```

**期望结果**:
- Title: "TDD+并行执行策略"
- Problem: 描述测试失败问题
- Solution: 描述4轮迭代模式
- Category: "Testing"
- Quality Score: >0.8

---

## 成功标准

### 质量指标

| 指标 | 目标 | 测量方法 |
|------|------|----------|
| Problem/Solution重复率 | <5% | 人工检查 |
| 经验质量评分 | >0.7 | 对话评分 |
| 提取准确率 | >90% | 对话验证 |

### 完整性指标

| 指标 | 目标 | 测量方法 |
|------|------|----------|
| 5个场景全部测试 | ✅ | 完成清单 |
| 每个场景输出Experience对象 | ✅ | 对话验证 |
| 质量评分合理 | ✅ | 人工判断 |

---

## 测试流程

### 步骤1: 准备测试文档

```bash
# 确认测试文档存在
ls docs/lessons-learned/react-best-practices.md
ls docs/lessons-learned/api-design-patterns.md
ls docs/lessons-learned/performance-patterns.md
ls docs/lessons-learned/test-fix-iteration.md
```

### 步骤2: 执行对话式测试

对于每个场景：
1. **Round 1**: 快速阅读文档
2. **Round 2**: 深度思考提取经验
3. **Round 3**: 质量自检修正
4. **Round 4**: 最终输出确认

### 步骤3: 记录测试结果

创建测试结果文档：
```bash
docs/reports/2026-03-23/CONVERSATION-TEST-RESULTS.md
```

记录每个场景的：
- ✅ 提取的Experience对象
- ✅ 质量评分
- ✅ 发现的问题
- ✅ 改进建议

### 步骤4: 分析测试结果

生成测试报告：
- 提取准确率
- 平均质量评分
- Problem/Solution重复率
- 改进建议

---

## 示例对话

### 场景1: React Hooks错误提取

**Round 1: 快速阅读**
```
User: 请阅读React Hooks规则章节，快速了解主题和结构。

Claude: 我已经阅读了React Hooks规则章节。

主题：React Hooks规则遵守

问题列表：
- 违反Hooks规则导致组件崩溃
- Hook在条件返回之后调用

解决方案列表：
- 所有Hook在条件返回之前调用
- ESLint检测Hook规则
```

**Round 2: 深度思考**
```
User: 现在深入分析，提取可复用的经验。

Claude: 让我深度分析这个React Hooks问题。

Title: React Hooks规则遵守

Problem:
在React组件中违反Hooks调用顺序规则会导致组件崩溃。
具体表现为：第1次渲染时调用1个Hook，第2次渲染时调用2个Hook，
React检测到Hooks数量不一致，抛出"Rendered more hooks than during
the previous render"错误。

Solution:
React Hooks必须遵守两个规则：
1. 只在顶层调用Hooks（不在if、for、嵌套函数中）
2. 没有在Hooks调用之间进行条件返回

正确模式：
function Component() {
  const [state, setState] = useState()  // Hook 1
  useEffect(() => {}, [])              // Hook 2

  if (isLoading) return <Loading />    // 条件返回在所有Hook之后
  return <View />
}

错误模式：
function Component() {
  const [state, setState] = useState()

  if (isLoading) return <Loading />    // ❌ 条件返回在中间

  useEffect(() => {}, [])              // ❌ Hook在条件返回后
  return <View />
}

Category: React
Priority: P1 (重要但不紧急)
Tags: React, Hooks, ESLint
Quality Score: 0.9
Reason:
- 唯一性: 高（明确的React规则违反模式）
- 实用性: 高（提供正确和错误模式对比）
- 完整性: 高（包含错误示例、修复示例、ESLint配置）
```

**Round 3: 质量自检**
```
User: 请检查刚才提取的经验，检查重复和完整性。

Claude: 检查提取的经验...

✅ Problem和Solution字段无重复
  - Problem描述问题（组件崩溃）
  - Solution描述解决方案（正确模式）

✅ 经验完整性验证
  - Problem字段清晰描述违反规则导致的崩溃 ✅
  - Solution字段提供可操作的解决方案（正确和错误模式对比）✅
  - 包含代码示例 ✅

✅ 质量评分确认
  - 唯一性: 1.0 (明确的React特定问题)
  - 实用性: 0.9 (有代码示例)
  - 完整性: 0.9 (包含ESLint配置建议)

  综合评分: 0.93

修正后Experience对象：
[同上，无修正]
```

**Round 4: 最终输出**
```
User: 请最终确认提取的经验。

Claude: 确认提取的经验...

✅ 准备更新到经验文档

最终Experience对象：
Title: "React Hooks规则遵守"
Problem: [同上]
Solution: [同上]
Category: React
Priority: P1
Tags: React, Hooks, ESLint
Quality Score: 0.93
```

---

## 下一步

完成5个场景的对话式测试后：

1. **生成测试报告**: `docs/reports/2026-03-23/CONVERSATION-TEST-RESULTS.md`
2. **分析测试结果**: 计算准确率、平均质量评分
3. **改进建议**: 基于测试结果改进提取器

---

**测试负责人**: Claude (update-docs refactoring)
**审核状态**: ✅ 对话式测试指南已创建
**下一步**: 执行5个场景的对话式测试
