# Knowledge Graph Integration

知识图谱集成模块 - 为update-docs技能提供智能文档检索和关联发现能力。

## 核心价值

1. **快速定位**：根据问题描述快速找到相关文档、解决方案（<500ms）
2. **关联发现**：发现文档之间的隐式关联关系
3. **经验复用**：在编码时自动推荐相关经验
4. **全局视图**：可视化展示整个文档知识体系

## 目录结构

```
kg/
├── core/               # 核心模块
│   ├── graph.py       # 图数据结构
│   ├── query_engine.py # 查询引擎
│   ├── node_manager.py # 节点管理器
│   ├── edge_manager.py # 边管理器
│   ├── incremental_updater.py # 增量更新器
│   └── visualizer.py  # 可视化生成器
├── extractors/         # 提取器模块
│   ├── document_metadata_extractor.py
│   ├── problem_solution_extractor.py
│   ├── code_snippet_extractor.py
│   ├── code_doc_mapper_extractor.py
│   ├── concept_extractor.py
│   ├── ast_semantic_extractor.py
│   └── test_case_extractor.py
├── storage/            # 数据存储
│   ├── kg_nodes.json   # 节点数据
│   ├── kg_edges.json   # 边数据
│   ├── kg_metadata.json # 元数据
│   ├── kg_edge_indices.json # 边索引
│   ├── kg_change_history.json # 变更历史
│   └── README.md       # 存储说明
├── output/             # 输出目录
│   ├── visualizations/ # 可视化HTML
│   ├── queries/        # 查询结果
│   └── reports/        # 分析报告
└── tests/              # 测试文档
    ├── baseline_test_results.md # Baseline测试结果
    ├── test_scenarios.md # 测试场景
    └── REFACTOR_ANALYSIS.md # REFACTOR分析
```

## 使用方式

知识图谱功能已集成到update-docs技能中，无需手动调用。

### 自动更新

```bash
# 执行update-docs时自动更新知识图谱
/update-docs

# 只更新知识图谱（不更新文档）
/update-docs --kg-only

# 强制全量重建知识图谱
/update-docs --kg-rebuild

# 跳过知识图谱更新
/update-docs --skip-kg
```

### 查询命令

```bash
# 关键词查询
/kg:query "GraphQL 400错误"

# 关联查询
/kg:related doc:react-best-practices

# 路径查询
/kg:path problem:graphql-400 solution:graphql-enum-fix

# 可视化
/kg:visualize --output kg-vis.html

# 统计信息
/kg:stats --coverage
```

## 数据模型

### 节点类型（6种）

1. **document** - 文档节点（docs/**/*.md）
2. **problem** - 问题场景节点（从文档提取）
3. **solution** - 解决方案节点（从文档提取）
4. **code_snippet** - 代码片段节点（文档中的代码块）
5. **code** - 代码节点（backend/**/*.py, frontend/src/**/*.{ts,tsx}）
6. **concept** - 概念节点（技术概念：GraphQL、React Hooks等）

### 边关系（9种）

1. **DOCUMENT_REFERENCE** - 文档引用边
2. **DOCUMENT_SIMILARITY** - 文档相似度边
3. **PROBLEM_SOLVED_BY** - 问题解决边
4. **SOLUTION_ALTERNATIVE** - 解决方案对比边
5. **SOLUTION_EXAMPLE** - 代码示例边
6. **SOLUTION_VERIFIED_BY** - 测试验证边
7. **CODE_DOCUMENTATION** - 代码映射边
8. **CODE_IMPLEMENTS** - 代码依赖边
9. **CONCEPT_RELATED_TO** - 概念关联边

## 性能指标

| 操作 | 目标时间 |
|------|---------|
| 关键词查询 | <500ms |
| 关联查询（2跳） | <1000ms |
| 增量更新（10个文档） | <5s |
| 全面检测 | <30s |

## 测试验证

详见 `tests/` 目录：
- baseline_test_results.md - Baseline测试结果（60%遗漏率）
- test_scenarios.md - 测试场景（预期<5%遗漏率）
- REFACTOR_ANALYSIS.md - REFACTOR阶段分析（15个合理化全部封堵）

## 维护状态

- **版本**: 1.0.0
- **创建日期**: 2026-03-22
- **最后更新**: 2026-03-22
- **状态**: 设计完成，待实施

## 下一步

按照实施计划（`/Users/mckenzie/.claude/plans/typed-crunching-lake.md`）进行分阶段实施：
1. Phase 1: 基础架构（graph.py, node_manager.py, edge_manager.py）
2. Phase 2: 提取器完善（7种提取器）
3. Phase 3: 查询与可视化（query_engine.py, visualizer.py）
4. Phase 4: update-docs集成（incremental_updater.py）
5. Phase 5: 测试与优化（单元测试、性能测试）
