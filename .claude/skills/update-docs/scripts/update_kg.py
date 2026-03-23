#!/usr/bin/env python3
"""
更新知识图谱 - 添加新提取的经验

添加3个新经验到知识图谱：
1. 避免过度工程化 (P0)
2. TDD驱动的Prompt工程 (P1)
3. 对话式测试方法 (P1)
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

    # 提取实际的节点和边列表
    nodes = nodes_data.get('nodes', [])
    edges = edges_data.get('edges', []) if isinstance(edges_data, dict) else edges_data

    print(f"更新前: {len(nodes)} 个节点, {len(edges)} 条边")

    # 当前时间戳
    now = datetime.now().isoformat()

    # ===== 添加新经验节点 =====

    # 经验1: 避免过度工程化
    exp1_node = {
        "id": "solution:avoid-over-engineering",
        "type": "solution",
        "title": "避免过度工程化",
        "description": "识别和避免过度工程化的原则和方法",
        "category": "Project Management",
        "priority": "P0",
        "tags": ["Simplification", "Over-engineering", "Architecture"],
        "source": "docs/reports/2026-03-24/update-docs-overengineering-audit.md",
        "target_document": "docs/lessons-learned/project-management.md",
        "created_at": now,
        "updated_at": now,
        "_metadata": {
            "quality_score": 0.95,
            "extraction_date": "2026-03-24",
            "extraction_method": "manual"
        }
    }
    nodes.append(exp1_node)

    # 经验2: TDD驱动的Prompt工程
    exp2_node = {
        "id": "solution:tdd-prompt-engineering",
        "type": "solution",
        "title": "TDD驱动的Prompt工程",
        "description": "使用测试驱动方法优化Prompt质量",
        "category": "Project Management",
        "priority": "P1",
        "tags": ["TDD", "Prompt Engineering", "Testing"],
        "source": "docs/reports/2026-03-24/PROMPT-VALIDATION-TEST-FRAMEWORK.md",
        "target_document": "docs/lessons-learned/project-management.md",
        "created_at": now,
        "updated_at": now,
        "_metadata": {
            "quality_score": 0.90,
            "extraction_date": "2026-03-24",
            "extraction_method": "manual"
        }
    }
    nodes.append(exp2_node)

    # 经验3: 对话式测试方法
    exp3_node = {
        "id": "solution:conversation-based-testing",
        "type": "solution",
        "title": "对话式测试方法",
        "description": "通过对话触发Claude深度思考的测试方法",
        "category": "Testing",
        "priority": "P1",
        "tags": ["Conversation Testing", "Claude Thinking", "Quality Validation"],
        "source": "docs/reports/2026-03-23/CONVERSATION-TESTING-GUIDE.md",
        "target_document": "docs/lessons-learned/testing-guide.md",
        "created_at": now,
        "updated_at": now,
        "_metadata": {
            "quality_score": 0.92,
            "extraction_date": "2026-03-24",
            "extraction_method": "manual"
        }
    }
    nodes.append(exp3_node)

    # ===== 添加源文档节点 =====

    # 源文档1: update-docs-overengineering-audit.md
    source1_node = {
        "id": "doc:update-docs-overengineering-audit",
        "type": "document",
        "title": "update-docs过度工程化审计报告",
        "file_path": "docs/reports/2026-03-24/update-docs-overengineering-audit.md",
        "is_archived": True,
        "archived_location": "docs/archive/reports/2026-03/update-docs-overengineering-audit.md",
        "archived_date": "2026-03-24",
        "created_at": "2026-03-24",
        "updated_at": "2026-03-24"
    }
    nodes.append(source1_node)

    # 源文档2: PROMPT-VALIDATION-TEST-FRAMEWORK.md
    source2_node = {
        "id": "doc:prompt-validation-test-framework",
        "type": "document",
        "title": "Prompt验证测试框架",
        "file_path": "docs/reports/2026-03-24/PROMPT-VALIDATION-TEST-FRAMEWORK.md",
        "is_archived": True,
        "archived_location": "docs/archive/reports/2026-03/PROMPT-VALIDATION-TEST-FRAMEWORK.md",
        "archived_date": "2026-03-24",
        "created_at": "2026-03-24",
        "updated_at": "2026-03-24"
    }
    nodes.append(source2_node)

    # 源文档3: CONVERSATION-TESTING-GUIDE.md
    source3_node = {
        "id": "doc:conversation-testing-guide",
        "type": "document",
        "title": "对话式测试指南",
        "file_path": "docs/reports/2026-03-23/CONVERSATION-TESTING-GUIDE.md",
        "is_archived": True,
        "archived_location": "docs/archive/reports/2026-03/CONVERSATION-TESTING-GUIDE.md",
        "archived_date": "2026-03-24",
        "created_at": "2026-03-23",
        "updated_at": "2026-03-24"
    }
    nodes.append(source3_node)

    # ===== 添加目标文档节点 =====

    # 目标文档1: project-management.md
    target1_node = {
        "id": "doc:project-management",
        "type": "document",
        "title": "项目管理经验文档",
        "file_path": "docs/lessons-learned/project-management.md",
        "is_archived": False,
        "created_at": None,
        "updated_at": "2026-03-24",
        "experience_count": 17
    }
    # 检查是否已存在
    if not any(n["id"] == target1_node["id"] for n in nodes):
        nodes.append(target1_node)

    # 目标文档2: testing-guide.md
    target2_node = {
        "id": "doc:testing-guide",
        "type": "document",
        "title": "测试指南经验文档",
        "file_path": "docs/lessons-learned/testing-guide.md",
        "is_archived": False,
        "created_at": None,
        "updated_at": "2026-03-24",
        "experience_count": 20
    }
    if not any(n["id"] == target2_node["id"] for n in nodes):
        nodes.append(target2_node)

    # ===== 添加边（关系） =====

    # 边1: 解决方案从源文档提取
    edges.append({
        "id": "edge:extracted-from-1",
        "source": "solution:avoid-over-engineering",
        "target": "doc:update-docs-overengineering-audit",
        "type": "SOLUTION_EXTRACTED_FROM",
        "weight": 1.0,
        "created_at": now
    })

    edges.append({
        "id": "edge:extracted-from-2",
        "source": "solution:tdd-prompt-engineering",
        "target": "doc:prompt-validation-test-framework",
        "type": "SOLUTION_EXTRACTED_FROM",
        "weight": 1.0,
        "created_at": now
    })

    edges.append({
        "id": "edge:extracted-from-3",
        "source": "solution:conversation-based-testing",
        "target": "doc:conversation-testing-guide",
        "type": "SOLUTION_EXTRACTED_FROM",
        "weight": 1.0,
        "created_at": now
    })

    # 边2: 解决方案添加到目标文档
    edges.append({
        "id": "edge:added-to-1",
        "source": "solution:avoid-over-engineering",
        "target": "doc:project-management",
        "type": "SOLUTION_ADDED_TO",
        "weight": 1.0,
        "created_at": now
    })

    edges.append({
        "id": "edge:added-to-2",
        "source": "solution:tdd-prompt-engineering",
        "target": "doc:project-management",
        "type": "SOLUTION_ADDED_TO",
        "weight": 1.0,
        "created_at": now
    })

    edges.append({
        "id": "edge:added-to-3",
        "source": "solution:conversation-based-testing",
        "target": "doc:testing-guide",
        "type": "SOLUTION_ADDED_TO",
        "weight": 1.0,
        "created_at": now
    })

    # 边3: 问题关联（过度工程化问题）
    edges.append({
        "id": "edge:solves-1",
        "source": "problem:over-engineering",
        "target": "solution:avoid-over-engineering",
        "type": "PROBLEM_SOLVED_BY",
        "weight": 1.0,
        "created_at": now
    })

    # 边4: 概念关联
    edges.append({
        "id": "edge:concept-1",
        "source": "concept:over-engineering",
        "target": "solution:avoid-over-engineering",
        "type": "CONCEPT_RELATED_TO",
        "weight": 0.9,
        "created_at": now
    })

    edges.append({
        "id": "edge:concept-2",
        "source": "concept:tdd",
        "target": "solution:tdd-prompt-engineering",
        "type": "CONCEPT_RELATED_TO",
        "weight": 0.9,
        "created_at": now
    })

    edges.append({
        "id": "edge:concept-3",
        "source": "concept:prompt-engineering",
        "target": "solution:tdd-prompt-engineering",
        "type": "CONCEPT_RELATED_TO",
        "weight": 0.9,
        "created_at": now
    })

    edges.append({
        "id": "edge:concept-4",
        "source": "concept:conversation-testing",
        "target": "solution:conversation-based-testing",
        "type": "CONCEPT_RELATED_TO",
        "weight": 0.9,
        "created_at": now
    })

    # ===== 更新元数据 =====

    metadata["node_count"] = len(nodes)
    metadata["edge_count"] = len(edges)
    metadata["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    metadata["last_update_action"] = "添加3个新经验：避免过度工程化、TDD Prompt工程、对话式测试"
    metadata["incremental_update_counter"] = metadata.get("incremental_update_counter", 0) + 1

    # ===== 保存更新后的知识图谱 =====

    with open(kg_dir / 'kg_nodes.json', 'w') as f:
        json.dump(nodes, f, indent=2, ensure_ascii=False)

    with open(kg_dir / 'kg_edges.json', 'w') as f:
        json.dump(edges, f, indent=2, ensure_ascii=False)

    with open(kg_dir / 'kg_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"✅ 更新后: {len(nodes)} 个节点, {len(edges)} 条边")
    print(f"✅ 新增节点: 8个 (3个解决方案 + 3个源文档 + 2个目标文档)")
    print(f"✅ 新增边: 10条")
    print(f"✅ 增量更新计数: {metadata['incremental_update_counter']}")
    print(f"✅ 最后更新: {metadata['last_updated']}")

    return {
        "nodes_added": len(nodes) - 2,  # 减去原有的2个
        "edges_added": len(edges) - 2,
        "metadata": metadata
    }

if __name__ == "__main__":
    result = main()
    print("\n知识图谱更新完成！")
