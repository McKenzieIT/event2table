#!/usr/bin/env python3
"""
更新知识图谱 - 添加新提取的经验

添加1个新经验到知识图谱：
1. 示例驱动Prompt验证方法 (P1)
"""

import json
from pathlib import Path
from datetime import datetime

def main():
    kg_dir = Path('.claude/skills/update-docs/kg/storage')

    # 读取现有知识图谱
    with open(kg_dir / 'kg_nodes.json', 'r') as f:
        nodes_data = json.load(f)
    with open(kg_dir / 'kg_edges.json', 'r') as f:
        edges_data = json.load(f)
    with open(kg_dir / 'kg_metadata.json', 'r') as f:
        metadata = json.load(f)

    # 适应当前格式：nodes可能是list或dict
    if isinstance(nodes_data, dict):
        nodes = nodes_data.get('nodes', [])
    else:
        nodes = nodes_data

    if isinstance(edges_data, dict):
        edges = edges_data.get('edges', [])
    else:
        edges = edges_data

    print(f"更新前: {len(nodes)} 个节点, {len(edges)} 条边")

    # 当前时间戳
    now = datetime.now().isoformat()

    # ===== 添加新经验节点 =====

    # 经验1: 示例驱动Prompt验证方法
    exp1_node = {
        "id": "solution:example-driven-prompt-validation",
        "type": "solution",
        "title": "示例驱动Prompt验证方法",
        "description": "使用多Prompt对比测试和量化评分确定最优Prompt策略",
        "category": "Project Management",
        "priority": "P1",
        "tags": ["Prompt Engineering", "Testing", "Validation", "Data-Driven"],
        "source": "docs/archive/reports/2026-03/PROMPT-ROUND-1-RESULTS.md",
        "target_document": "docs/lessons-learned/project-management.md",
        "created_at": now,
        "updated_at": now,
        "_metadata": {
            "quality_score": 0.98,
            "extraction_date": "2026-03-24",
            "extraction_method": "manual",
            "test_data": {
                "test_documents": 4,
                "test_prompts": 5,
                "total_test_cases": 20,
                "completion_rate": "100%"
            }
        }
    }
    nodes.append(exp1_node)

    # ===== 添加源文档节点 =====

    # 源文档1: PROMPT-ROUND-1-RESULTS.md
    source1_node = {
        "id": "doc:prompt-round-1-results",
        "type": "document",
        "title": "Prompt验证测试Round 1结果报告",
        "file_path": "docs/archive/reports/2026-03/PROMPT-ROUND-1-RESULTS.md",
        "is_archived": True,
        "archived_location": "docs/archive/reports/2026-03/PROMPT-ROUND-1-RESULTS.md",
        "archived_date": "2026-03-24",
        "created_at": "2026-03-24",
        "updated_at": "2026-03-24"
    }
    nodes.append(source1_node)

    # ===== 添加目标文档节点 =====

    # 目标文档1: project-management.md
    # 检查是否已存在
    target1_id = "doc:project-management"
    if not any(n["id"] == target1_id for n in nodes):
        target1_node = {
            "id": target1_id,
            "type": "document",
            "title": "项目管理经验文档",
            "file_path": "docs/lessons-learned/project-management.md",
            "is_archived": False,
            "created_at": None,
            "updated_at": "2026-03-24",
            "experience_count": 18
        }
        nodes.append(target1_node)
    else:
        # 更新现有节点
        for n in nodes:
            if n["id"] == target1_id:
                n["updated_at"] = "2026-03-24"
                n["experience_count"] = 18
                break

    # ===== 添加边（关系） =====

    # 边1: 解决方案从源文档提取
    edges.append({
        "id": "edge:extracted-from-4",
        "source": "solution:example-driven-prompt-validation",
        "target": "doc:prompt-round-1-results",
        "type": "SOLUTION_EXTRACTED_FROM",
        "weight": 1.0,
        "created_at": now
    })

    # 边2: 解决方案添加到目标文档
    edges.append({
        "id": "edge:added-to-4",
        "source": "solution:example-driven-prompt-validation",
        "target": "doc:project-management",
        "type": "SOLUTION_ADDED_TO",
        "weight": 1.0,
        "created_at": now
    })

    # 边3: 概念关联
    edges.append({
        "id": "edge:concept-5",
        "source": "concept:prompt-engineering",
        "target": "solution:example-driven-prompt-validation",
        "type": "CONCEPT_RELATED_TO",
        "weight": 0.95,
        "created_at": now
    })

    edges.append({
        "id": "edge:concept-6",
        "source": "concept:testing",
        "target": "solution:example-driven-prompt-validation",
        "type": "CONCEPT_RELATED_TO",
        "weight": 0.90,
        "created_at": now
    })

    edges.append({
        "id": "edge:concept-7",
        "source": "concept:validation",
        "target": "solution:example-driven-prompt-validation",
        "type": "CONCEPT_RELATED_TO",
        "weight": 0.92,
        "created_at": now
    })

    # ===== 更新元数据 =====

    metadata["node_count"] = len(nodes)
    metadata["edge_count"] = len(edges)
    metadata["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    metadata["last_update_action"] = "添加1个新经验：示例驱动Prompt验证方法"
    metadata["incremental_update_counter"] = metadata.get("incremental_update_counter", 0) + 1

    # ===== 保存更新后的知识图谱 =====

    # 保存节点（适应当前格式）
    if isinstance(nodes_data, dict) and "metadata" in nodes_data:
        nodes_output = {
            "nodes": nodes,
            "metadata": nodes_data.get("metadata", {})
        }
    else:
        nodes_output = nodes

    with open(kg_dir / 'kg_nodes.json', 'w') as f:
        json.dump(nodes_output, f, indent=2, ensure_ascii=False)

    # 保存边
    if isinstance(edges_data, dict) and "metadata" in edges_data:
        edges_output = {
            "edges": edges,
            "metadata": edges_data.get("metadata", {})
        }
    else:
        edges_output = edges

    with open(kg_dir / 'kg_edges.json', 'w') as f:
        json.dump(edges_output, f, indent=2, ensure_ascii=False)

    with open(kg_dir / 'kg_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"✅ 更新后: {len(nodes)} 个节点, {len(edges)} 条边")
    print(f"✅ 新增节点: 2个 (1个解决方案 + 1个源文档)")
    print(f"✅ 新增边: 5条")
    print(f"✅ 增量更新计数: {metadata['incremental_update_counter']}")
    print(f"✅ 最后更新: {metadata['last_updated']}")

    return {
        "nodes_added": 2,
        "edges_added": 5,
        "metadata": metadata
    }

if __name__ == "__main__":
    result = main()
    print("\n知识图谱更新完成！")
