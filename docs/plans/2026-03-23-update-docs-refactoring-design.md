# update-docs Skill 重构设计文档

**版本**: 1.0
**日期**: 2026-03-23
**作者**: Claude (brainstorming skill)
**状态**: 设计完成 - 等待实施批准

---

## 执行摘要

本文档定义了update-docs skill的全面重构方案，解决当前存在的过度工程化问题，充分利用Claude的深度思考能力进行经验提取。

**核心改进**：
- ✅ 架构简化：从5层减少到2层（代码复杂度降低60%）
- ✅ Claude思考利用：通过提示词模板和工作流确保提取质量
- ✅ 知识图谱持续价值：文档定位 + 自动更新机制
- ✅ 避免过度工程化：Subagent并行分析 + 对话式测试

**预期成果**：
- 提取质量提升50%（通过提示词工程）
- 执行时间保持<35秒
- 知识图谱自动更新集成

---

## 1. 架构设计

### 1.1 当前问题诊断

**5层架构导致的问题**：
1. **过度抽象**：WorkflowOrchestrator → CachedReflectiveExperienceExtractor → ReflectiveExperienceExtractor → DynamicCategoryMapper → ExperienceExtractor
2. **Claude思考能力未真正利用**：第4轮"深度反思"实际上是算法评分（计算唯一性、实用性、完整性），而非真正的语义理解
3. **提取质量差**：依赖正则表达式和关键词匹配，导致Problem/Solution字段包含重复元数据如"**修复的问题数**: 0"

### 1.2 简化后的2层架构

```
┌─────────────────────────────────────────────────┐
│  Layer 1: 简化编排器 + 图谱定位器              │
│  ┌───────────────────────────────────────────┐  │
│  │ WorkflowOrchestrator (简化版)            │  │
│  │  ├── 执行7阶段工作流                    │  │
│  │  ├── 使用知识图谱快速定位相关文档      │  │
│  │  └── 调用Layer 2进行经验提取            │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │ 知识图谱定位器                          │  │
│  │  ├── 仅用于文档发现                      │  │
│  │  └── 不参与经验提取                      │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│  Layer 2: Claude思考提取器                      │
│  ┌───────────────────────────────────────────┐  │
│  │ Claude Semantic ExperienceExtractor        │  │
│  │  ├── 直接阅读文档内容                     │  │
│  │  ├── 使用Claude语义理解提取经验           │  │
│  │  ├── 通过思考判断Problem/Solution       │  │
│  │  └── 简单类别映射（11个固定类别）       │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### 1.3 关键变化

**保留的组件**：
- ✅ WorkflowOrchestrator（简化版）
- ✅ 知识图谱（角色转变为定位器）
- ✅ ExperienceExtractor（重写为Claude语义分析）

**删除的组件**：
- ❌ CachedReflectiveExperienceExtractor（缓存复杂度不值得）
- ❌ ReflectiveExperienceExtractor（4轮反思未真正使用Claude思考）
- ❌ DynamicCategoryMapper（动态学习过于复杂，固定类别足够）

**归档策略**：
- 所有被删除的模块归档到 `docs/archive/update-docs-refactoring/`
- 每个模块包含README.md说明归档原因
- 使用git mv移动文件（保持历史记录）

---

## 2. 实施计划

### 2.1 短期计划（Week 1-2）

**Week 1: 分析和准备**

**Day 1-2: Subagent并行分析**
```
Subagent 1: 依赖关系分析
  任务：分析update-docs skill的依赖关系
  输入：.claude/skills/update-docs/core/
  输出：docs/reports/update-docs-refactoring/dependency-analysis.md

Subagent 2: 测试场景设计
  任务：分析现有测试覆盖，设计新测试场景
  输入：.claude/skills/update-docs/tests/
  输出：docs/reports/update-docs-refactoring/test-scenarios.md

Subagent 3: 破坏性变更识别
  任务：识别重构可能导致的向后兼容性问题
  输入：SKILL.md, 用户调用模式
  输出：docs/reports/update-docs-refactoring/breaking-changes.md
```

**Day 3-4: 代码归档**
```bash
# 创建归档目录结构
mkdir -p docs/archive/update-docs-refactoring/{cached-reflective,reflective-extractor,dynamic-category,legacy-extractor}

# 归档文件
git mv core/cached_reflective_experience_extractor.py docs/archive/update-docs-refactoring/cached-reflective/
git mv core/reflective_experience_extractor.py docs/archive/update-docs-refactoring/reflective-extractor/
git mv core/dynamic_category_mapper.py docs/archive/update-docs-refactoring/dynamic-category/
# backup: git mv core/experience_extractor.py docs/archive/update-docs-refactoring/legacy-extractor/

# 为每个模块编写README.md（归档原因、新方案、性能对比）
```

**Day 5: 准备新架构**
- 创建`core/claude_semantic_experience_extractor.py`骨架
- 简化`workflow_orchestrator.py`（移除3层引用）
- 设计知识图谱自动更新接口

**Week 2: 实现和测试**

**Day 1-3: 实现Claude提取器**
- 实现对话式思考提取逻辑
- 集成知识图谱定位功能
- 实现简化类别映射（11个固定类别）

**Day 4-5: 对话式测试**
```
测试场景1: 单个报告提取（Claude思考触发）
测试场景2: 批量报告提取（5个）
测试场景3: 知识图谱定位测试
测试场景4: 自动更新知识图谱
测试场景5: 284个历史文档压力测试
```

**Day 6-7: 质量验证和文档**
- 人工评估提取质量（前50个样本）
- 性能测试（目标<35秒）
- 更新SKILL.md
- 编写重构总结报告

### 2.2 中期计划（1个月）

**Week 1-2: 思考提示词优化**
- 设计结构化提示词模板，引导Claude深度思考
- 包含检查清单：问题识别、解决方案评估、价值判断
- 引入少样本学习（few-shot learning）

**Week 3: 质量评估体系**
- 建立经验质量评分标准（1-10分制）
- 收集50个提取样本，标注质量分数
- 分析Claude提取的优势和不足

**Week 4: 迭代优化**
- 根据评估结果调整提示词
- 在284个历史文档上批量测试
- 建立提示词版本控制机制

### 2.3 长期计划（3个月）

**Month 1: 反馈循环建立**
- 为提取的经验添加用户反馈机制
- 记录：哪些经验有用、哪些需要改进
- 建立反馈数据集

**Month 2: 知识图谱增强**
- 基于用户反馈，更新知识图谱边关系
- 添加经验之间的关联引用
- 实现经验推荐系统（类似问题→相关经验）

**Month 3: 自动化评估**
- 基于反馈数据训练质量评估模型
- 自动筛选低质量经验
- 实现经验自动归档（过时经验移除）

---

## 3. 核心组件设计

### 3.1 Claude Semantic Experience Extractor

**核心特性**：
- 直接阅读文档内容
- 使用Claude语义理解提取经验
- 通过思考判断Problem/Solution
- 简单类别映射（11个固定类别）

**提示词模板**：
```
你是一位经验丰富的技术文档专家。请分析这份报告并提取经验。

**思考步骤**：
1. [理解] 这份报告的背景是什么？解决什么问题？
2. [识别] 核心问题描述（用1-2句话）
3. [分析] 解决方案的关键步骤（列举关键动作）
4. [评估] 这个经验的价值和可复用性（1-10分并说明理由）
5. [归类] 应该归入哪个类别？（React/GraphQL/Testing等11选1）

**质量自检**：
- Problem描述是否清晰？✅/❌
- Solution是否可操作？✅/❌
- 是否包含代码示例？✅/❌
- 是否有实际价值？✅/❌

请按照以上格式输出提取的经验。
```

**工作流设计**（4轮思考）：
```
第1轮：快速阅读（识别文档类型）
第2轮：深度思考（提取Problem/Solution）
第3轮：质量自检（Claude自我评估）
第4轮：最终输出（格式化经验）
```

### 3.2 知识图谱自动更新

**触发场景**：
1. 执行`/update-docs`后（提取了新经验）
2. 手动编辑文档后（检测到文件修改）
3. 批量操作后（文档整合、归档）

**更新流程**：
```python
def _update_knowledge_graph(self, changed_docs):
    """增量更新知识图谱"""
    for doc_path in changed_docs:
        # 1. 提取文档内容
        content = doc_path.read_text()

        # 2. 添加/更新文档节点
        self.kg.add_document_node(doc_path, content)

        # 3. 提取经验（如有）
        experiences = self.extractor.extract_from_doc(doc_path)

        # 4. 添加经验节点和关联边
        for exp in experiences:
            self.kg.add_experience_node(exp)
            self.kg.link_document_to_exp(doc_path, exp)

    # 5. 保存知识图谱
    self.kg.save()
```

**备份和回滚**：
- 更新前备份知识图谱（kg_backup.json）
- 增量更新模式（只更新变更部分）
- 更新后验证图谱完整性
- 失败时回滚到备份版本

### 3.3 简化的WorkflowOrchestrator

**Phase 4实现**（简化后）：
```python
def _phase_experience_extraction(self) -> PhaseResult:
    """阶段4: 经验提取（Claude语义分析）"""
    try:
        reports_dir = self.project_root / "docs" / "reports"

        # 使用Claude语义提取器
        print("🔄 使用Claude语义提取器...")
        experiences = self.claude_extractor.extract_from_reports(reports_dir)

        # 更新目标文档
        updated_count = 0
        for exp in experiences:
            # 查找目标文档
            target_doc = self.experience_extractor.find_target_document(exp.category)

            if target_doc:
                success = self.experience_extractor.update_experience_doc(exp, target_doc)
                if success:
                    updated_count += 1

        # ⭐ 主动更新知识图谱
        changed_docs = self._detect_document_changes()
        if changed_docs:
            print("📊 检测到文档变更，更新知识图谱...")
            self._update_knowledge_graph(changed_docs)

        print(f"✅ 提取并更新了 {updated_count} 个经验")

        return PhaseResult(
            phase_name="experience_extraction",
            success=True,
            items_processed=len(experiences),
            items_changed=updated_count,
        )
```

---

## 4. Skill-Creator方法论应用

### 4.1 分析阶段（Subagent并行）

**Subagent 1: 依赖关系分析**
```python
任务：分析update-docs skill的依赖关系
输入：
  - .claude/skills/update-docs/core/
  - .claude/skills/update-docs/kg/

输出：
  - 模块依赖图（谁调用谁）
  - 紧耦合点识别
  - 可安全删除的模块清单
```

**Subagent 2: 测试场景设计**
```python
任务：分析现有测试覆盖情况
输入：
  - .claude/skills/update-docs/tests/
  - run_full_workflow.py执行记录

输出：
  - 当前测试覆盖哪些场景
  - 缺失的测试场景
  - 新测试用例建议
```

**Subagent 3: 破坏性变更识别**
```python
任务：识别重构可能导致的问题
输入：
  - SKILL.md（当前skill定义）
  - 用户调用模式（/update-docs命令）

输出：
  - 公开API变更点
  - 向后兼容性风险
  - 迁移策略建议
```

### 4.2 实现阶段（Skill-Creator + 对话式测试）

**RED阶段**：3个subagent并行分析（15分钟）

**GREEN阶段**：基于分析结果创建新skill（1天）
- 创建新SKILL.md
- 实现简化的2层架构
- 保持向后兼容（7阶段工作流）

**REFACTOR阶段**：测试-迭代循环（3天）
- 对话式测试（Claude思考触发）
- 人工质量评估
- 提示词模板优化

### 4.3 避免过度工程化策略

**不使用**：
- 复杂的自动化脚本系统
- 过度抽象的测试框架
- 多层次的配置文件

**使用**：
- 现有工具（Read/Edit/Bash）
- 手动测试场景（3-5个）
- 简单的验证脚本
- Subagent并行分析（效率工具）

---

## 5. 时间线和里程碑

### Week 1: 分析和准备

**Day 1-2**: Subagent并行分析
**Day 3-4**: 代码归档
**Day 5**: 准备新架构

**里程碑**：归档完成，新架构代码骨架就绪

### Week 2: 实现和测试

**Day 1-3**: 实现Claude提取器
**Day 4-5**: 对话式测试
**Day 6-7**: 质量验证和文档

**里程碑**：
- ✅ Day 5: 新架构代码完成
- ✅ Day 7: 对话式测试通过
- ✅ Day 10: 知识图谱自动更新工作

---

## 6. 风险评估和缓解措施

### 风险1: 提取质量不可控 ⚠️ **重点**

**缓解措施（系统性质量保证）**：
- ✅ 提示词模版设计（结构化思维链）
- ✅ 工作流设计（4轮深度思考）
- ✅ 质量自检机制（Claude自我评估）
- ✅ 提示词版本控制和迭代优化
- ❌ 不依赖人工抽检

### 风险2: 知识图谱更新失败

**缓解措施**：
- 更新前备份知识图谱
- 增量更新模式
- 更新后验证图谱完整性
- 失败时回滚到备份版本

### 风险3: 向后兼容性破坏

**缓解措施**：
- 保持7阶段工作流接口不变
- SKILL.md描述保持兼容
- 添加迁移指南文档
- 提供旧版本回退方案

### 风险4: 性能退化

**缓解措施**：
- 测试阶段测量执行时间
- 缓存知识图谱查询结果
- 并行处理多个文档

### 风险5: 过度工程化回潮 ⚠️ **持续警惕**

**缓解措施**：
- 每次代码审查检查：是否必需？
- 坚持2层架构，拒绝添加新层
- 代码审查清单："这个抽象是否简化了问题？"

---

## 7. 成功指标

### 短期指标（2周后）

**提取质量**：
- 平均质量评分 ≥ 7/10（前50个样本人工评估）
- Problem/Solution字段清晰度提升（无重复元数据）

**架构简化**：
- 代码复杂度降低60%（5层→2层）
- 模块数量减少3个

**性能**：
- 执行时间 <35秒（7阶段完整工作流）

### 中期指标（1个月后）

**提取质量**：
- 80%提取经验被用户标记为有用
- 提取质量提升50%（vs当前正则方法）

**知识图谱**：
- 自动更新机制工作正常
- 节点数保持同步

### 长期指标（3个月后）

**知识增长**：
- 知识图谱节点数从1045增长到2000+
- 经验之间的关联引用建立

**自动化**：
- 质量评估模型运行
- 低质量经验自动筛选
- 过时经验自动归档

---

## 8. 下一步行动

### 立即行动（本周）

1. ✅ 启动3个Subagent并行分析
2. ✅ 创建归档目录结构
3. ✅ 编写归档README.md

### Week 1行动

1. 代码归档（git mv到archive/）
2. 实现Claude Semantic ExperienceExtractor
3. 设计提示词模板和工作流

### Week 2行动

1. 对话式测试（5个场景）
2. 质量验证和性能测试
3. 文档更新和总结报告

### 预期成果

- 提取质量提升50%（通过提示词工程）
- 执行时间保持<35秒
- 代码复杂度降低60%（5层→2层）
- 知识图谱自动更新集成

---

**文档版本**: 1.0
**最后更新**: 2026-03-23
**状态**: 设计完成 - 等待实施批准

