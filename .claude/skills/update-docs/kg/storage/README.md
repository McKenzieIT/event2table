# Knowledge Graph Storage

知识图谱数据存储目录。

## 文件说明

- `kg_nodes.json` - 节点数据（6种节点类型：document, problem, solution, code_snippet, code, concept）
- `kg_edges.json` - 边数据（9种边关系）
- `kg_metadata.json` - 元数据（版本、更新计数器、覆盖率等）
- `kg_edge_indices.json` - 边索引（按类型、源节点、目标节点索引）
- `kg_change_history.json` - 变更历史（记录每次更新的节点和边变更）
- `kg_sharding_config.json` - 分片配置（可选，用于大规模图谱）

## 数据格式

### 节点格式

```json
{
  "id": "doc:react-best-practices",
  "type": "document",
  "title": "React最佳实践",
  "file_path": "docs/lessons-learned/react-best-practices.md",
  "priority": "P0",
  "is_archived": false,
  "created_at": "2026-03-05T10:00:00Z",
  "updated_at": "2026-03-22T16:00:00Z"
}
```

### 边格式

```json
{
  "id": "edge_001",
  "source": "doc:react-best-practices",
  "target": "doc:testing-guide",
  "type": "DOCUMENT_REFERENCE",
  "weight": 1.0,
  "created_at": "2026-03-22T16:00:00Z"
}
```

## 更新策略

**混合更新策略**：
- **平时**：增量更新（只更新变更的文档）
- **定期**：全面检测（每累积更新10个文档后触发）

**计数器机制**：
- `incremental_update_counter`: 当前累积次数
- `incremental_update_threshold`: 触发阈值（10）
- `next_full_check_threshold`: 还需多少次更新触发全面检测
