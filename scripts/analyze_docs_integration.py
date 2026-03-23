#!/usr/bin/env python3
"""
文档整合分析脚本

识别需要整合、归档和更新的文档
"""
import os
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta


def analyze_docs_structure():
    """分析docs目录结构"""
    docs_dir = Path("/Users/mckenzie/Documents/event2table/docs")

    results = {
        "total_docs": 0,
        "active_docs": 0,
        "archived_docs": 0,
        "by_directory": defaultdict(int),
        "potential_duplicates": [],
        "misplaced_docs": [],
        "outdated_root_docs": [],
    }

    # 扫描所有markdown文件
    for md_file in docs_dir.rglob("*.md"):
        results["total_docs"] += 1

        rel_path = md_file.relative_to(docs_dir)
        path_str = str(rel_path)

        # 统计归档和非归档
        if "/archive/" in path_str:
            results["archived_docs"] += 1
        else:
            results["active_docs"] += 1

        # 统计各目录文档数
        top_dir = rel_path.parts[0] if len(rel_path.parts) > 0 else "root"
        results["by_directory"][top_dir] += 1

        # 检查根目录的临时文档
        if top_dir == "root" or len(rel_path.parts) == 1:
            if "REPORT" in md_file.name or "SUMMARY" in md_file.name or "FINAL" in md_file.name:
                results["outdated_root_docs"].append(path_str)

        # 检查错误归档的经验文档
        if "/archive/lesson-learned/" in path_str or "/archive/lessons-learned/" in path_str:
            results["misplaced_docs"].append({
                "path": path_str,
                "reason": "经验文档被归档，应恢复到lessons-learned/"
            })

        # 检查archive中的重要文档（通过标题识别）
        if "/archive/" in path_str:
            try:
                content = md_file.read_text(encoding='utf-8', errors='ignore')
                # 检查是否是经验文档（包含最佳实践、模式、指南等关键词）
                if any(keyword in content for keyword in ["最佳实践", "Best Practices", "模式", "Pattern", "指南", "Guide"]):
                    # 检查是否是测试报告（应该归档）
                    if not any(keyword in path_str for keyword in ["test-report", "REPORT", "SUMMARY", "iteration"]):
                        results["misplaced_docs"].append({
                            "path": path_str,
                            "reason": "可能包含重要经验，不应归档"
                        })
            except Exception:
                pass

    # 检查重复的报告文档
    reports_dir = docs_dir / "reports"
    if reports_dir.exists():
        for report_file in reports_dir.rglob("*.md"):
            if "2026-03" in str(report_file):
                # 3月份的报告可以保留在活跃目录
                continue
            results["potential_duplicates"].append(str(report_file.relative_to(docs_dir)))

    return results


def identify_lessons_learned_duplicates():
    """识别经验文档中的重复内容"""
    lessons_dir = Path("/Users/mckenzie/Documents/event2table/docs/lessons-learned")

    if not lessons_dir.exists():
        return []

    duplicates = []

    # 检查是否有重复的主题
    themes = defaultdict(list)

    for md_file in lessons_dir.glob("*.md"):
        if md_file.name == "README.md":
            continue

        try:
            content = md_file.read_text(encoding='utf-8')
            # 提取主题（从标题或关键词）
            for keyword in ["React", "GraphQL", "API", "测试", "缓存", "性能", "安全", "部署"]:
                if keyword in content or keyword in md_file.name:
                    themes[keyword].append(md_file.name)
        except Exception:
            pass

    # 找出可能有重复的主题
    for theme, files in themes.items():
        if len(files) > 2:
            duplicates.append({
                "theme": theme,
                "files": files,
                "suggestion": f"可能有{len(files)}个文档涉及{theme}主题，考虑整合"
            })

    return duplicates


def check_knowledge_graph_usage():
    """检查知识图谱使用情况"""
    kg_dir = Path("/Users/mckenzie/.claude/skills/update-docs/kg")
    storage_dir = kg_dir / "storage"

    if not storage_dir.exists():
        return {
            "exists": False,
            "message": "知识图谱存储目录不存在，需要初始化"
        }

    # 检查存储文件
    kg_files = {
        "nodes": storage_dir / "kg_nodes.json",
        "edges": storage_dir / "kg_edges.json",
        "metadata": storage_dir / "kg_metadata.json",
    }

    status = {
        "exists": True,
        "nodes_count": 0,
        "edges_count": 0,
        "last_updated": None,
        "needs_update": False
    }

    # 读取节点数
    if kg_files["nodes"].exists():
        try:
            import json
            with open(kg_files["nodes"], 'r') as f:
                nodes = json.load(f)
                status["nodes_count"] = len(nodes)
        except Exception:
            pass

    # 读取边数
    if kg_files["edges"].exists():
        try:
            import json
            with open(kg_files["edges"], 'r') as f:
                edges = json.load(f)
                status["edges_count"] = len(edges)
        except Exception:
            pass

    # 读取元数据
    metadata_file = storage_dir / "kg_metadata.json"
    if metadata_file.exists():
        try:
            import json
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                status["last_updated"] = metadata.get("last_updated")

                # 检查是否需要更新（超过7天）
                if status["last_updated"]:
                    try:
                        last_date = datetime.strptime(status["last_updated"], "%Y-%m-%d")
                        if datetime.now() - last_date > timedelta(days=7):
                            status["needs_update"] = True
                    except Exception:
                        status["needs_update"] = True
        except Exception:
            pass

    return status


def generate_integration_report():
    """生成整合报告"""
    print("=" * 80)
    print("文档整合分析报告")
    print("=" * 80)
    print()

    # 1. 文档结构分析
    print("## 1. 文档结构统计")
    print("-" * 80)
    structure = analyze_docs_structure()

    print(f"总文档数: {structure['total_docs']}")
    print(f"活跃文档: {structure['active_docs']}")
    print(f"归档文档: {structure['archived_docs']}")
    print()
    print("主要目录文档分布:")
    for dir_name, count in sorted(structure['by_directory'].items(), key=lambda x: -x[1]):
        if count > 5:
            print(f"  - {dir_name}: {count}个文档")
    print()

    # 2. 错误归档的文档
    print("## 2. 需要恢复的文档")
    print("-" * 80)
    if structure['misplaced_docs']:
        print(f"发现 {len(structure['misplaced_docs'])} 个可能错误归档的文档:")
        print()
        for doc in structure['misplaced_docs'][:10]:  # 只显示前10个
            print(f"❌ {doc['path']}")
            print(f"   原因: {doc['reason']}")
            print()
        if len(structure['misplaced_docs']) > 10:
            print(f"... 还有 {len(structure['misplaced_docs']) - 10} 个文档")
            print()
    else:
        print("✅ 没有发现错误归档的文档")
    print()

    # 3. 根目录的临时文档
    print("## 3. 根目录的临时报告（需要归档）")
    print("-" * 80)
    if structure['outdated_root_docs']:
        print(f"发现 {len(structure['outdated_root_docs'])} 个根目录的临时报告:")
        print()
        for doc in structure['outdated_root_docs']:
            print(f"📄 {doc}")
        print()
        print("建议: 这些报告应该归档到 docs/reports/YYYY-MM/ 或整合到经验文档")
        print()
    else:
        print("✅ 根目录没有临时报告")
    print()

    # 4. 经验文档重复检查
    print("## 4. 经验文档重复分析")
    print("-" * 80)
    duplicates = identify_lessons_learned_duplicates()
    if duplicates:
        print(f"发现 {len(duplicates)} 个可能重复的主题:")
        print()
        for dup in duplicates:
            print(f"⚠️  {dup['theme']}: {', '.join(dup['files'])}")
            print(f"   建议: {dup['suggestion']}")
        print()
    else:
        print("✅ 经验文档没有明显重复")
    print()

    # 5. 知识图谱状态
    print("## 5. 知识图谱状态")
    print("-" * 80)
    kg_status = check_knowledge_graph_usage()

    if kg_status['exists']:
        print(f"✅ 知识图谱已创建")
        print(f"   节点数: {kg_status['nodes_count']}")
        print(f"   边数: {kg_status['edges_count']}")
        print(f"   最后更新: {kg_status['last_updated']}")
        print()
        if kg_status['needs_update']:
            print("⚠️  知识图谱超过7天未更新，建议更新")
        else:
            print("✅ 知识图谱状态新鲜")
    else:
        print("❌ 知识图谱不存在，需要初始化")
        print(f"   {kg_status['message']}")
    print()

    # 6. 整合建议
    print("## 6. 整合建议")
    print("-" * 80)
    print("优先级P0（必须立即执行）:")
    print("  1. 恢复错误归档的经验文档（如react-best-practices.md）")
    print("  2. 归档根目录的临时报告")
    print("  3. 更新知识图谱（如果需要）")
    print()
    print("优先级P1（建议尽快执行）:")
    print("  4. 整合重复的报告文档")
    print("  5. 更新docs/README.md索引")
    print("  6. 更新CLAUDE.md中的经验文档引用")
    print()

    print("=" * 80)
    print("报告生成完成")
    print("=" * 80)

    return structure


if __name__ == "__main__":
    generate_integration_report()
