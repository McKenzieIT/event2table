# Knowledge Graph Core Modules

知识图谱核心模块目录。

## 模块说明

### 核心模块（core/）

- `graph.py` - 图数据结构（节点、边的增删改查）
- `query_engine.py` - 查询引擎（关键词查询、关联查询、路径查询）
- `node_manager.py` - 节点管理器（节点CRUD、节点索引）
- `edge_manager.py` - 边管理器（边CRUD、边索引）
- `incremental_updater.py` - 增量更新器（混合更新策略）
- `visualizer.py` - 可视化生成器（D3.js力导向图）

### 提取器模块（extractors/）

- `document_metadata_extractor.py` - 文档元数据提取
- `problem_solution_extractor.py` - 问题-解决方案提取
- `code_snippet_extractor.py` - 代码片段提取
- `code_doc_mapper_extractor.py` - 代码-文档映射提取
- `concept_extractor.py` - 概念节点提取
- `ast_semantic_extractor.py` - AST语义分析
- `test_case_extractor.py` - 测试用例提取

## 实现优先级

**Phase 1: 基础架构**
1. graph.py - 图数据结构
2. node_manager.py - 节点管理器
3. edge_manager.py - 边管理器
4. query_engine.py - 基础查询引擎

**Phase 2: 提取器**
5. document_metadata_extractor.py - 文档元数据提取
6. problem_solution_extractor.py - 问题-解决方案提取
7. code_snippet_extractor.py - 代码片段提取

**Phase 3: 查询与可视化**
8. query_engine.py - 高级查询（关联查询、路径查询）
9. visualizer.py - 可视化生成器

**Phase 4: update-docs集成**
10. incremental_updater.py - 增量更新器
11. 集成到update-docs技能

## API设计

### graph.py

```python
class KnowledgeGraph:
    def add_node(self, node: Node) -> bool
    def remove_node(self, node_id: str) -> bool
    def add_edge(self, edge: Edge) -> bool
    def remove_edge(self, edge_id: str) -> bool
    def get_node(self, node_id: str) -> Optional[Node]
    def get_neighbors(self, node_id: str, depth: int = 1) -> List[Node]
    def find_path(self, source_id: str, target_id: str) -> List[str]
```

### query_engine.py

```python
class QueryEngine:
    def query(self, keyword: str, **filters) -> List[Node]
    def find_related(self, node_id: str, depth: int = 1) -> Dict[str, List[Node]]
    def find_path(self, source_id: str, target_id: str) -> List[str]
```

### incremental_updater.py

```python
class IncrementalUpdater:
    def update(self, changed_files: List[str]) -> UpdateResult
    def full_check(self) -> UpdateResult
    def should_trigger_full_check(self) -> bool
```
