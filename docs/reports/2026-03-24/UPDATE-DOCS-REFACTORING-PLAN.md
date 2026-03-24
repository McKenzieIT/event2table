# update-docs技能重构计划

> **日期**: 2026-03-24
> **版本**: 1.0.0
> **类型**: 技能重构计划
> **目标**: 解决过度工程化，充分利用Claude深度思考能力

---

## 执行摘要

**核心问题**: update-docs技能严重过度工程化，声称使用"4轮反思提取"和"Claude深度思考"，但实际实现是基于正则表达式和关键词匹配的规则系统。

**重构目标**: 将889行规则提取代码替换为真正的Claude语义理解，简化架构，利用知识图谱进行快速文档定位。

**关键指标**:
- 代码量减少: 889行 → 预计200行 (-77%)
- 提取质量: 从91.7/100 → 目标99+/100
- 维护成本: 从复杂规则系统 → 简单Prompt模板
- Claude思考利用率: 从0% → 100%

---

## 第一部分：问题诊断

### 1.1 架构层级过多 ⚠️

**当前架构**:
```
WorkflowOrchestrator (558行)
  ↓
ClaudeSemanticExperienceExtractor (不存在)
  ↓
CachedReflectiveExperienceExtractor (不存在)
  ↓
ReflectiveExperienceExtractor (不存在)
  ↓
DynamicCategoryMapper (不存在)
  ↓
ExperienceExtractor (889行)
  ↓
实际: _extract_standard_format() + _fallback_rule_based_extraction()
```

**问题分析**:
1. **文档与实现脱节**: SKILL.md描述的5层架构，实际只实现1层
2. **导入错误**: `workflow_orchestrator.py:267`导入不存在的`ClaudeSemanticExperienceExtractor`
3. **虚假组件**: `ReflectiveExperienceExtractor`、`DynamicCategoryMapper`在文档中详细描述但代码中不存在
4. **过度抽象**: 为不存在的功能创建编排器

**影响**:
- 开发者困惑: 文档描述的组件无法在代码中找到
- 维护困难: 不知道应该修改哪一层
- 功能缺失: "4轮反思"根本没有实现

### 1.2 Claude思考能力未使用 ❌

**声称的功能** (SKILL.md):
```markdown
## 4轮反思提取

**第1轮**: 基于规则的初始提取
**第2轮**: 知识图谱语义分析
**第3轮**: 历史经验对比（去重检测）
**第4轮**: 深度整合和质量评分（Claude思考能力）
```

**实际实现** (`experience_extractor.py:406-449`):
```python
def _intelligent_content_analysis(self, content: str, fix_report_path: Path):
    """
    Intelligent content analysis using Prompt D (Example-driven approach)

    This method implements the WINNER from Round 1 testing (99.8/100 quality score)
    by using gold standard examples to guide extraction.
    """
    # 实际实现: 使用 _extract_problem_solution_with_quality_focus()
    # 该方法仍然是基于section解析，而非Claude API调用

    # 回退: _fallback_rule_based_extraction() 使用关键词匹配
```

**关键发现**:
1. **Prompt D模板存在但未使用**: 75-100行的Prompt D模板存储在字符串中，但从未发送给Claude
2. **无Claude API调用**: 整个`experience_extractor.py`没有任何Claude API调用
3. **"智能"分析是假的**: `_intelligent_content_analysis()`声称使用Prompt D，实际使用section解析
4. **回退机制是规则**: 当"智能"分析失败时，回退到关键词匹配

**质量影响**:
- Problem和Solution字段重复: 因为基于`## 问题`和`## 解决`section标记提取
- 无法理解上下文: 正则表达式无法理解语义
- 提取质量不稳定: 依赖文档格式而非内容理解

### 1.3 知识图谱未集成 ❌

**声称的功能** (SKILL.md):
```markdown
### 知识图谱集成 ⭐⭐⭐ **NEW**

**核心价值**:
- **快速定位**: 根据问题描述快速找到相关文档、解决方案
- **关联发现**: 发现文档之间的隐式关联关系
- **经验复用**: 在编码时自动推荐相关经验
```

**实际状态**:
1. **知识图谱组件存在但孤立**: `kg/core/graph.py`、`kg/core/query_engine.py`存在
2. **无集成**: `experience_extractor.py`未导入或使用任何知识图谱组件
3. **CLI命令可用**: `/kg:query`、`/kg:related`命令存在，但经验提取未使用
4. **QueryEngine功能完善**: 已实现`search_by_keyword()`、`get_related_nodes()`

**错失机会**:
- 无法利用知识图谱快速定位相关文档
- 无法检测重复经验（通过`get_related_nodes()`）
- 无法利用历史经验上下文提升提取质量
- 无法发现跨文档的隐式关联

### 1.4 质量问题根因分析

**问题**: 为什么`_intelligent_content_analysis()`产生低质量提取？

**根本原因**:
1. **基于Section标记提取**:
   ```python
   problem_match = re.search(
       r"##?\s*(?:问题|Problem|Issue)\s*\n+(.+?)(?=##?\s*(?:解决|Solution|Fix))",
       content, re.DOTALL
   )
   ```
   - 只要文档有`## 问题`和`## 解决`标记，就会提取
   - 不理解问题是否真实存在
   - 不理解解决方案是否有效

2. **关键词匹配回退**:
   ```python
   problem_keywords = ["错误", "失败", "问题", "bug", "error", "issue"]
   solution_keywords = ["解决", "修复", "方案", "fix", "solution"]
   ```
   - 简单统计关键词出现次数
   - 无法区分真正的问题和普通描述

3. **无语义理解**:
   - 无法判断"React Hooks崩溃"是问题还是正常描述
   - 无法判断"重新安装npm"是否是有效的解决方案
   - 无法理解上下文和因果关系

**示例**: 为什么Problem和Solution重复？

**输入文档**:
```markdown
## 问题
React应用崩溃，报错 'React has detected a change in the order of Hooks called'

## 解决方案
核心规则：React Hooks必须遵守两个核心规则
1. 只在顶层调用Hooks
2. 没有在Hooks调用之间进行条件返回
```

**规则提取结果**:
```python
{
    "problem": "## 问题\nReact应用崩溃...",  # 包含section标记
    "solution": "核心规则：React Hooks必须遵守..."  # 重复问题上下文
}
```

**原因**: 正则表达式提取的是section之间的所有内容，包括section标记本身。

**Claude理解提取** (理想):
```python
{
    "problem": "React应用崩溃，报错 'React has detected a change in the order of Hooks called'",
    "solution": "核心规则：React Hooks必须遵守两个核心规则：1. 只在顶层调用Hooks 2. 没有在Hooks调用之间进行条件返回",
    "root_cause": "Hook在条件返回后调用，导致渲染间Hook调用顺序不一致",
    "code_example": "function Component() { const data = useData(); if (isLoading) return <Loading />; return <View />; }"
}
```

---

## 第二部分：重构策略

### 2.1 设计原则

**原则1: Claude-First, Rules-Last**
- ❌ **移除**: 889行正则表达式和关键词匹配逻辑
- ✅ **使用**: Claude直接理解文档内容
- ✅ **简化**: 200行Prompt模板 + Claude API调用

**原则2: 知识图谱辅助定位**
- ✅ **使用**: `/kg:query "React Hooks"`快速定位相关文档
- ✅ **使用**: `/kg:related doc:react-best-practices`发现关联经验
- ✅ **集成**: 在经验提取前查询知识图谱

**原则3: 质量优先于数量**
- ✅ **提取**: 1-2个高质量经验
- ❌ **避免**: 3-4个低质量经验
- ✅ **标准**: 问题描述详细（>200字符）+ 解决方案具体（>400字符）+ 代码示例

**原则4: 向后兼容**
- ✅ **保留**: Experience数据结构
- ✅ **保留**: 7阶段工作流接口
- ✅ **移除**: 不存在的组件（文档修复）

### 2.2 分阶段重构计划

#### 短期 (立即执行) ⚡

**目标**: 修复关键问题，实现基础Claude集成

**Phase 1: 移除虚假架构** (1小时)
```python
# 删除不存在的导入
# workflow_orchestrator.py:267
- from core.claude_semantic_extractor import ClaudeSemanticExperienceExtractor
+ from core.experience_extractor import ExperienceExtractor

# 修复实例化
- self.claude_extractor = ClaudeSemanticExperienceExtractor(self.project_root)
+ self.experience_extractor = ExperienceExtractor(self.project_root)
```

**Phase 2: 实现真正的Claude提取** (4小时)

创建新文件: `/Users/mckenzie/.claude/skills/update-docs/core/claude_experience_extractor.py`

```python
class ClaudeExperienceExtractor:
    """使用Claude API进行真正的语义理解提取"""

    def extract_from_document(self, doc_path: Path) -> List[Experience]:
        """
        使用Claude理解文档内容并提取经验

        流程:
        1. 读取文档内容
        2. 查询知识图谱定位相关上下文
        3. 构建Prompt (使用Prompt D模板)
        4. 调用Claude API (anthropic)
        5. 解析JSON响应
        6. 验证质量评分
        """
        content = doc_path.read_text(encoding="utf-8")

        # Step 2: 查询知识图谱
        context = self._fetch_kg_context(doc_path)

        # Step 3-4: 构建Prompt并调用Claude
        prompt = self._build_prompt_d(doc_path, content, context)
        response = self._call_claude_api(prompt)

        # Step 5-6: 解析和验证
        experiences = self._parse_claude_response(response)
        validated = self._validate_quality(experiences)

        return validated

    def _call_claude_api(self, prompt: str) -> str:
        """调用Claude API (实际实现)"""
        # 使用 anthropic SDK
        from anthropic import Anthropic
        client = Anthropic(api_key=self.api_key)

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            temperature=0.3,  # 低温度保证稳定性
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text

    def _fetch_kg_context(self, doc_path: Path) -> Dict:
        """查询知识图谱获取相关上下文"""
        from kg.core.query_engine import QueryEngine
        from kg.builder import build_graph

        graph = build_graph()
        query_engine = QueryEngine(graph)

        # 从文档路径推断关键词
        keywords = self._extract_keywords_from_path(doc_path)

        # 查询相关文档和经验
        related_docs = query_engine.search_by_keyword(keywords[0], node_type="document")
        related_problems = query_engine.search_by_keyword(keywords[1], node_type="problem")

        return {
            "related_docs": [d.title for d in related_docs[:3]],
            "related_problems": [p.title for p in related_problems[:3]]
        }
```

**预期效果**:
- ✅ 真正使用Claude语义理解
- ✅ 利用知识图谱上下文
- ✅ 提取质量: 91.7/100 → 99+/100
- ✅ 代码量: 889行 → 200行 (-77%)

#### 中期 (1-2周) 🔄

**目标**: 完善知识图谱集成，实现去重和质量保证

**Phase 3: 知识图谱去重** (3天)

```python
def _check_duplicates_with_kg(self, experience: Experience) -> bool:
    """
    使用知识图谱检测重复经验

    Returns:
        True if experience is duplicate
    """
    from kg.core.query_engine import QueryEngine
    from kg.builder import build_graph

    graph = build_graph()
    query_engine = QueryEngine(graph)

    # 搜索相似问题
    similar_problems = query_engine.search_by_keyword(
        experience.problem[:50],  # 使用问题前50字作为关键词
        node_type="problem"
    )

    # 检查是否已有解决方案
    for problem in similar_problems:
        related_solutions = query_engine.get_related_nodes(
            problem.id,
            node_type="solution",
            max_depth=1
        )

        if related_solutions:
            # 计算相似度（简单版本：标题重叠）
            similarity = self._calculate_similarity(
                experience.solution,
                related_solutions[0].title
            )

            if similarity > 0.85:  # 高相似度阈值
                return True

    return False
```

**Phase 4: 质量评分优化** (2天)

```python
def _calculate_quality_score(self, experience: Experience) -> float:
    """
    计算经验质量评分 (0.0 - 1.0)

    评分维度:
    1. 唯一性 (40%): 与历史经验的最大相似度取反
    2. 实用性 (30%): 代码示例 + 可操作步骤
    3. 完整性 (30%): 所有字段填充 + 详细描述
    """
    score = 0.0

    # 唯一性
    uniqueness = 1.0 - self._max_similarity_with_history(experience)
    score += 0.4 * uniqueness

    # 实用性
    utility = 0.0
    if "```" in experience.solution:  # 有代码示例
        utility += 0.15
    if "step" in experience.solution.lower():  # 有步骤
        utility += 0.15
    score += 0.3 * utility

    # 完整性
    completeness = 0.0
    if len(experience.title) > 10:
        completeness += 0.05
    if len(experience.problem) > 200:
        completeness += 0.10
    if len(experience.solution) > 400:
        completeness += 0.10
    if experience.tags:
        completeness += 0.05
    score += 0.3 * completeness

    return round(score, 2)
```

#### 长期 (1-2月) 🚀

**目标**: 构建自适应知识图谱，实现持续学习

**Phase 5: 动态类别映射** (1周)

当前硬编码:
```python
category_mapping = {
    "React": "react-best-practices.md",
    "GraphQL": "api-design-patterns.md",
    # ... 11个固定类别
}
```

优化后（从知识图谱学习）:
```python
class DynamicCategoryMapper:
    """从知识图谱学习的动态类别映射器"""

    def classify_document(self, doc_path: Path, content: str) -> str:
        """
        使用知识图谱CONCEPT_RELATED_TO边学习类别关联

        流程:
        1. 从内容中提取概念
        2. 查询知识图谱的相关类别
        3. 选择最高分类别
        4. 更新映射（从这个分类中学习）
        """
        # 提取概念
        concepts = self._extract_concepts(content)

        # 查询知识图谱
        category_scores = {}
        for concept in concepts:
            concept_nodes = query_engine.search_by_keyword(concept, node_type="concept")
            for node in concept_nodes:
                related_docs = query_engine.get_related_nodes(node.id, max_depth=2)
                for doc in related_docs:
                    category = self._infer_category_from_doc(doc)
                    if category:
                        category_scores[category] = category_scores.get(category, 0) + 1

        # 选择最高分类别
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            self._update_mapping(doc_path, best_category)
            return best_category

        # 回退：使用语义相似度
        return self._classify_by_similarity(content)
```

**Phase 6: 知识图谱自动更新** (2周)

```python
def _update_kg_after_extraction(self, experiences: List[Experience]):
    """
    提取经验后自动更新知识图谱

    新增节点:
    - problem节点: 从experience.problem提取
    - solution节点: 从experience.solution提取
    - concept节点: 从experience.tags提取

    新增边:
    - PROBLEM_SOLVED_BY: problem → solution
    - SOLUTION_VERIFIED_BY: solution → doc_path
    - CONCEPT_RELATED_TO: concept → solution
    """
    from kg.builder import build_graph

    graph = build_graph()

    for exp in experiences:
        # 添加problem节点
        problem_id = f"problem:{hash(exp.problem)}"
        problem_node = Node(
            id=problem_id,
            type="problem",
            title=exp.title,
            content=exp.problem
        )
        graph.add_node(problem_node)

        # 添加solution节点
        solution_id = f"solution:{hash(exp.solution)}"
        solution_node = Node(
            id=solution_id,
            type="solution",
            title=exp.title,
            content=exp.solution
        )
        graph.add_node(solution_node)

        # 添加边
        edge = Edge(
            id=f"{problem_id}_solved_by_{solution_id}",
            source=problem_id,
            target=solution_id,
            type="PROBLEM_SOLVED_BY"
        )
        graph.add_edge(edge)

    # 保存知识图谱
    graph.save()
```

---

## 第三部分：实施路线图

### 3.1 优先级矩阵

| 优先级 | 任务 | 预期收益 | 预期工作量 | 风险 |
|--------|------|----------|------------|------|
| **P0** | Phase 1: 移除虚假架构 | 修复导入错误 | 1小时 | 低 |
| **P0** | Phase 2: Claude API集成 | 真正的语义理解 | 4小时 | 中 |
| **P1** | Phase 3: 知识图谱去重 | 避免重复经验 | 3天 | 低 |
| **P1** | Phase 4: 质量评分 | 质量保证 | 2天 | 低 |
| **P2** | Phase 5: 动态类别映射 | 自适应分类 | 1周 | 中 |
| **P2** | Phase 6: 知识图谱自动更新 | 持续学习 | 2周 | 高 |

### 3.2 实施检查清单

#### Phase 1: 移除虚假架构 ✅

- [ ] 修复 `workflow_orchestrator.py:267` 导入错误
- [ ] 更新 SKILL.md 移除不存在的组件描述
- [ ] 验证7阶段工作流可以正常运行
- [ ] 运行测试确保无回归

#### Phase 2: Claude API集成 ✅

- [ ] 创建 `claude_experience_extractor.py`
- [ ] 实现 `_call_claude_api()` 方法
- [ ] 实现 `_build_prompt_d()` 方法
- [ ] 实现 `_parse_claude_response()` 方法
- [ ] 实现 `_fetch_kg_context()` 方法
- [ ] 添加API密钥配置
- [ ] 测试Claude API调用
- [ ] 验证提取质量 >99/100

#### Phase 3: 知识图谱去重 ✅

- [ ] 实现 `_check_duplicates_with_kg()` 方法
- [ ] 集成到提取流程
- [ ] 测试去重准确性
- [ ] 验证无重复经验

#### Phase 4: 质量评分 ✅

- [ ] 实现 `_calculate_quality_score()` 方法
- [ ] 集成到提取流程
- [ ] 设置质量阈值 (0.7)
- [ ] 测试评分准确性

#### Phase 5: 动态类别映射 ✅

- [ ] 创建 `dynamic_category_mapper.py`
- [ ] 实现 `_classify_document()` 方法
- [ ] 实现 `_extract_concepts()` 方法
- [ ] 实现 `_infer_category_from_doc()` 方法
- [ ] 测试分类准确性
- [ ] 验证新兴技术检测

#### Phase 6: 知识图谱自动更新 ✅

- [ ] 实现 `_update_kg_after_extraction()` 方法
- [ ] 集成到提取流程
- [ ] 测试节点和边创建
- [ ] 验证图谱一致性

### 3.3 测试策略

**单元测试**:
```python
# tests/unit/test_claude_experience_extractor.py
def test_claude_api_call():
    """测试Claude API调用"""
    extractor = ClaudeExperienceExtractor()
    response = extractor._call_claude_api("测试prompt")
    assert response  # 非空响应

def test_prompt_d_template():
    """测试Prompt D模板生成"""
    extractor = ClaudeExperienceExtractor()
    prompt = extractor._build_prompt_d(doc_path, content, context)
    assert "黄金标准示例" in prompt
    assert "React Hooks" in prompt

def test_kg_context_fetch():
    """测试知识图谱上下文获取"""
    extractor = ClaudeExperienceExtractor()
    context = extractor._fetch_kg_context(doc_path)
    assert "related_docs" in context
    assert "related_problems" in context
```

**集成测试**:
```python
# tests/integration/test_extraction_workflow.py
def test_full_extraction_workflow():
    """测试完整提取流程"""
    # 1. 提取经验
    experiences = extractor.extract_from_document(doc_path)

    # 2. 验证质量
    for exp in experiences:
        assert exp.quality_score > 0.7
        assert len(exp.problem) > 200
        assert len(exp.solution) > 400

    # 3. 验证去重
    assert len(experiences) == len(set(experiences))  # 无重复
```

**质量对比测试**:
```python
# tests/integration/test_quality_comparison.py
def test_quality_comparison():
    """对比规则提取 vs Claude提取质量"""
    # 规则提取（旧方法）
    rule_based = ExperienceExtractor()
    old_experiences = rule_based.extract_from_fix_report(doc_path)
    old_quality = calculate_average_quality(old_experiences)

    # Claude提取（新方法）
    claude_extractor = ClaudeExperienceExtractor()
    new_experiences = claude_extractor.extract_from_document(doc_path)
    new_quality = calculate_average_quality(new_experiences)

    # 验证质量提升
    assert new_quality > old_quality
```

---

## 第四部分：风险管理

### 4.1 技术风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| **Claude API调用失败** | 中 | 高 | 1. 添加重试机制（最多3次）<br>2. 回退到规则提取<br>3. 缓存API响应 |
| **API成本超预算** | 中 | 中 | 1. 使用缓存减少调用<br>2. 批量提取减少请求<br>3. 设置月度预算上限 |
| **提取质量不稳定** | 低 | 中 | 1. 使用质量评分过滤<br>2. 设置质量阈值<br>3. 人工审核低质量结果 |
| **知识图谱性能** | 低 | 低 | 1. 使用LRU缓存<br>2. 限制查询深度<br>3. 异步更新图谱 |

### 4.2 实施风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| **破坏现有工作流** | 中 | 高 | 1. 保持Experience数据结构不变<br>2. 保持7阶段接口不变<br>3. 增量迁移而非重写 |
| **用户适应问题** | 低 | 中 | 1. 提供迁移文档<br>2. 保持CLI命令不变<br>3. 收集用户反馈 |
| **测试覆盖不足** | 中 | 中 | 1. 编写完整单元测试<br>2. 编写集成测试<br>3. 质量对比测试 |

---

## 第五部分：成功标准

### 5.1 功能指标

- ✅ **Claude语义理解**: 100%的提取使用Claude API
- ✅ **知识图谱集成**: 100%的提取前查询知识图谱
- ✅ **去重检测**: 重复检测准确率 >95%
- ✅ **质量评分**: 质量评分与人工判断相关性 >0.8

### 5.2 质量指标

- ✅ **提取质量**: 平均质量评分 >99/100
- ✅ **问题长度**: 问题描述平均 >200字符
- ✅ **解决方案长度**: 解决方案平均 >400字符
- ✅ **代码示例**: 包含代码示例的经验 >90%

### 5.3 性能指标

- ✅ **提取时间**: 单个文档提取 <10秒
- ✅ **知识图谱查询**: <500ms
- ✅ **API调用次数**: 每个文档 <3次
- ✅ **内存使用**: <500MB

### 5.4 维护性指标

- ✅ **代码量减少**: 从889行 → 200行 (-77%)
- ✅ **复杂度降低**: 圈复杂度 <10
- ✅ **测试覆盖率**: >80%
- ✅ **文档完整性**: 100%的组件有文档

---

## 第六部分：下一步行动

### 立即行动 (今天)

1. ✅ **Phase 1: 移除虚假架构**
   ```bash
   # 修复导入错误
   vim /Users/mckenzie/.claude/skills/update-docs/core/workflow_orchestrator.py
   ```

2. ✅ **创建重构分支**
   ```bash
   git checkout -b refactor/update-docs-claude-integration
   ```

3. ✅ **设置Claude API密钥**
   ```bash
   export ANTHROPIC_API_KEY="your-api-key"
   ```

### 本周行动

1. ✅ **Phase 2: Claude API集成**
   - 创建 `claude_experience_extractor.py`
   - 实现基础Claude API调用
   - 测试提取质量

2. ✅ **质量验证**
   - 在3个文档上测试
   - 对比规则提取 vs Claude提取
   - 验证质量提升

### 下周行动

1. ✅ **Phase 3: 知识图谱去重**
   - 实现去重检测
   - 集成到提取流程

2. ✅ **Phase 4: 质量评分**
   - 实现质量评分算法
   - 设置质量阈值

### 长期行动 (1-2月)

1. ✅ **Phase 5: 动态类别映射**
   - 实现自适应分类
   - 从知识图谱学习

2. ✅ **Phase 6: 知识图谱自动更新**
   - 实现自动更新
   - 构建自适应知识图谱

---

## 第七部分：经验总结

### 7.1 过度工程化的教训

**问题**: 889行规则提取代码，声称"Claude深度思考"实际未使用

**教训**:
1. **文档与实现必须一致**: 不要在文档中描述不存在的功能
2. **简单优于复杂**: 200行Prompt模板 > 889行正则表达式
3. **AI能力要真正使用**: 声称使用AI必须真正调用AI API
4. **过度抽象有害**: 为不存在的功能创建编排器是浪费

### 7.2 Claude思考能力的正确使用

**错误方式**:
- ❌ 存储Prompt模板但从不发送给Claude
- ❌ 使用正则表达式模拟Claude理解
- ❌ 声称"4轮反思"实际只做规则提取

**正确方式**:
- ✅ 直接调用Claude API进行语义理解
- ✅ 提供丰富的上下文（知识图谱、历史经验）
- ✅ 使用质量评分客观评估结果
- ✅ 简化架构，让Claude做它擅长的事

### 7.3 知识图谱的价值

**当前问题**: 知识图谱存在但孤立，经验提取未使用

**优化后**:
1. **快速定位**: `/kg:query "React Hooks"`快速找到相关文档
2. **去重检测**: `/kg:related`发现重复经验
3. **上下文增强**: 相关文档和经验作为提取上下文
4. **持续学习**: 提取的经验自动更新知识图谱

---

## 附录A: 代码示例

### A.1 ClaudeExperienceExtractor完整实现

```python
"""
Claude Experience Extractor - 使用Claude API进行真正的语义理解

替代889行规则提取代码，使用Claude深度思考能力。
"""
from pathlib import Path
from typing import List, Dict, Optional
from anthropic import Anthropic
import json

from core.experience_extractor import Experience, ExperienceExtractor


class ClaudeExperienceExtractor(ExperienceExtractor):
    """
    使用Claude API进行经验提取

    核心理念:
    - Claude直接理解文档内容
    - 知识图谱提供上下文
    - 质量评分过滤低质量结果
    """

    def __init__(self, project_root: Path, api_key: str):
        super().__init__(project_root)
        self.api_key = api_key
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"

    def extract_from_document(self, doc_path: Path) -> List[Experience]:
        """
        从文档提取经验（主入口）

        流程:
        1. 读取文档内容
        2. 查询知识图谱获取上下文
        3. 构建Prompt D模板
        4. 调用Claude API
        5. 解析JSON响应
        6. 验证质量评分
        7. 检查重复
        """
        content = doc_path.read_text(encoding="utf-8")

        # Step 2: 查询知识图谱
        kg_context = self._fetch_kg_context(doc_path)

        # Step 3-4: 构建Prompt并调用Claude
        prompt = self._build_prompt_d(doc_path, content, kg_context)
        claude_response = self._call_claude_api(prompt)

        # Step 5: 解析响应
        experiences = self._parse_claude_response(claude_response)

        # Step 6: 验证质量
        validated = self._validate_quality(experiences)

        # Step 7: 检查重复
        deduped = self._check_duplicates(validated)

        return deduped

    def _fetch_kg_context(self, doc_path: Path) -> Dict:
        """查询知识图谱获取相关上下文"""
        try:
            from kg.core.query_engine import QueryEngine
            from kg.builder import build_graph

            graph = build_graph()
            query_engine = QueryEngine(graph)

            # 从文档路径推断关键词
            keywords = self._extract_keywords_from_path(doc_path)

            # 查询相关文档
            related_docs = query_engine.search_by_keyword(
                keywords[0],
                node_type="document"
            )[:3]

            # 查询相关问题
            related_problems = query_engine.search_by_keyword(
                keywords[1],
                node_type="problem"
            )[:3]

            return {
                "related_docs": [d.title for d in related_docs],
                "related_problems": [p.title for p in related_problems]
            }
        except Exception as e:
            # 知识图谱查询失败，返回空上下文
            print(f"Warning: KG query failed: {e}")
            return {"related_docs": [], "related_problems": []}

    def _build_prompt_d(
        self,
        doc_path: Path,
        content: str,
        kg_context: Dict
    ) -> str:
        """构建Prompt D模板（示例驱动）"""

        # 黄金标准示例1: React Hooks
        example1 = {
            "title": "React Hooks规则遵守",
            "problem": "症状描述：React组件崩溃，报错 'React has detected a change in the order of Hooks called'\n技术原因：Hook在条件返回后调用，导致渲染间Hook调用顺序不一致",
            "solution": "核心规则：React Hooks必须遵守两个核心规则\n1. 只在顶层调用Hooks（不在if、for、嵌套函数中）\n2. 没有在Hooks调用之间进行条件返回\n\n代码示例：\n```javascript\n// ✅ 正确：所有Hook在条件返回之前\nfunction Component() {\n  const data = useData();\n  const processed = useMemo(() => {...}, [data]);\n  if (isLoading) return <Loading />;\n  return <View />;\n}\n```",
            "category": "React",
            "priority": "P1"
        }

        prompt = f"""请参考以下黄金标准示例，从文档中提取类似质量的多条经验：

**文档**: {doc_path}

**内容**:
{content}

**黄金标准示例1** (React Hooks规则):
```json
{json.dumps(example1, ensure_ascii=False)}
```

**知识图谱上下文**:
- 相关文档: {kg_context.get('related_docs', [])}
- 相关问题: {kg_context.get('related_problems', [])}

**提取要求**:
- 提取1-3个高质量经验（优先质量而非数量）
- 每个经验必须包含同样详细的问题、解决方案和代码示例
- 问题描述应包含症状描述和技术根因
- 解决方案应包含核心规则、具体步骤和代码示例
- 优先提取P0和P1优先级的经验
- **避免**: 提取泛泛而谈的内容，必须具体可操作

**输出**: JSON格式的经验列表，格式如下：
```json
[
  {{
    "title": "经验标题",
    "problem": "问题描述（包含症状+根因）",
    "solution": "解决方案（包含规则+步骤+代码）",
    "category": "类别",
    "priority": "P0/P1/P2"
  }}
]
```
"""
        return prompt

    def _call_claude_api(self, prompt: str) -> str:
        """调用Claude API"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.3,  # 低温度保证稳定性
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            raise

    def _parse_claude_response(self, response: str) -> List[Experience]:
        """解析Claude JSON响应"""
        try:
            # 提取JSON块
            json_start = response.find('[')
            json_end = response.rfind(']')

            if json_start == -1 or json_end == -1:
                raise ValueError("No JSON found in response")

            json_str = response[json_start:json_end+1]
            data = json.loads(json_str)

            # 转换为Experience对象
            experiences = []
            for item in data:
                exp = Experience(
                    title=item['title'],
                    problem=item['problem'],
                    solution=item['solution'],
                    category=item['category'],
                    priority=item['priority'],
                    source=f"Claude提取 | 质量待验证",
                    tags=[item['category'], item['priority']]
                )
                experiences.append(exp)

            return experiences
        except Exception as e:
            print(f"Error parsing Claude response: {e}")
            return []

    def _validate_quality(self, experiences: List[Experience]) -> List[Experience]:
        """验证质量评分"""
        validated = []

        for exp in experiences:
            score = self._calculate_quality_score(exp)

            # 只保留高质量经验
            if score >= 0.7:
                exp.source = f"Claude提取 | 质量:{score:.2f}"
                validated.append(exp)

        return validated

    def _calculate_quality_score(self, exp: Experience) -> float:
        """计算质量评分"""
        score = 0.0

        # 完整性 (40%)
        if len(exp.problem) > 200:
            score += 0.15
        if len(exp.solution) > 400:
            score += 0.15
        if "```" in exp.solution:
            score += 0.10

        # 实用性 (30%)
        if "step" in exp.solution.lower() or "步骤" in exp.solution:
            score += 0.15
        if "```" in exp.solution:
            score += 0.15

        # 唯一性 (30%)
        # (需要历史对比，暂时给满分)
        score += 0.30

        return round(score, 2)

    def _check_duplicates(self, experiences: List[Experience]) -> List[Experience]:
        """检查重复（简单版本：标题重复）"""
        seen_titles = set()
        deduped = []

        for exp in experiences:
            if exp.title not in seen_titles:
                seen_titles.add(exp.title)
                deduped.append(exp)

        return deduped

    def _extract_keywords_from_path(self, doc_path: Path) -> List[str]:
        """从文档路径推断关键词"""
        path_str = str(doc_path).lower()

        # 简单关键词映射
        if "react" in path_str:
            return ["React", "Hooks"]
        elif "graphql" in path_str or "api" in path_str:
            return ["GraphQL", "API"]
        elif "performance" in path_str:
            return ["Performance", "Optimization"]
        elif "testing" in path_str or "test" in path_str:
            return ["Testing", "E2E"]
        else:
            return ["General", "Documentation"]
```

### A.2 WorkflowOrchestrator修复

```python
# 修复前 (line 267)
from core.claude_semantic_extractor import ClaudeSemanticExperienceExtractor

# 修复后
from core.claude_experience_extractor import ClaudeExperienceExtractor

# 修复实例化 (line ~462)
# 修复前
self.claude_extractor = ClaudeSemanticExperienceExtractor(self.project_root)

# 修复后
self.experience_extractor = ClaudeExperienceExtractor(
    project_root=self.project_root,
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)
```

---

## 结论

update-docs技能当前存在严重的过度工程化问题：

1. **889行规则代码**可以用200行Prompt模板 + Claude API调用替代
2. **声称的"4轮反思"**实际上只做规则提取，未真正使用Claude思考
3. **知识图谱存在但孤立**，未与经验提取集成
4. **文档与实现严重脱节**，描述的组件在代码中不存在

**重构方案**:
- **短期**: 移除虚假架构，实现真正的Claude API集成
- **中期**: 集成知识图谱进行去重和质量保证
- **长期**: 构建自适应知识图谱，实现持续学习

**预期收益**:
- 代码量减少77% (889行 → 200行)
- 提取质量提升8% (91.7/100 → 99+/100)
- 维护成本大幅降低（规则系统 → Prompt模板）
- 真正利用Claude深度思考能力

---

**报告版本**: 1.0.0
**生成时间**: 2026-03-24
**作者**: Claude (update-docs技能重构Agent)
**审核**: 待用户确认
