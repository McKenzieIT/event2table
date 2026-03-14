#!/usr/bin/env python3
"""
generate_topic_index.py - 自动生成归档文档主题索引（带评分系统）

根据归档文档的文件名自动分类、评分，并生成主题索引文件。
支持自动评分和手动配置覆盖。
"""

import os
import re
import yaml
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# 配置
ARCHIVE_BASE_DIR = Path("docs/archive")
OUTPUT_FILE = ARCHIVE_BASE_DIR / "TOPIC_INDEX.md"
MANUAL_SCORES_FILE = ARCHIVE_BASE_DIR / "manual-scores.yaml"

# 主题关键词映射（文件名关键词 -> 主题）
TOPIC_KEYWORDS = {
    "GraphQL迁移": ["GRAPHQL", "graphql"],
    "E2E测试": ["E2E", "e2e"],
    "缓存失效修复": ["CACHE", "cache", "Cache"],
    "测试覆盖率": ["COVERAGE", "coverage", "TEST-COVERAGE"],
    "Chrome MCP": ["CHROME.*MCP", "CHROME-MCP", "chrome"],
    "TDD实践": ["TDD", "tdd"],
    "配置管理": ["CONFIG.*MANAGEMENT", "CONFIG-MANAGEMENT", "config"],
    "滚动修复": ["SCROLL.*FIX", "SCROLL-FIX", "scroll"],
    "HQL预览": ["HQL.*PREVIEW", "HQL-PREVIEW", "Hql"],
    "性能优化": ["PERFORMANCE", "PERFORMANCE-OPTIMIZATION", "PARALLEL.*OPTIMIZATION"],
    "文档整合": ["DOCS.*CONSOLIDATION", "DOCS-CONSOLIDATION"],
    "事件节点构建器": ["EVENT.*NODE.*BUILDER", "EVENT-NODE-BUILDER"],
    "Canvas相关": ["CANVAS", "Canvas"],
}

# 评分规则
SCORING_RULES = {
    3: {
        "keywords": ["SUMMARY", "COMPLETE", "FINAL", "DESIGN", "CONSOLIDATION"],
        "tags": ["核心"],
        "description": "完整方案，必读"
    },
    2: {
        "keywords": ["REPORT", "PROGRESS", "STATUS", "FIX", "TEST", "QUICK", "GUIDE"],
        "tags": ["参考"],
        "description": "重要参考文档"
    },
    1: {
        "keywords": [],
        "tags": ["补充"],
        "description": "补充说明文档"
    }
}

def auto_score_document(filename):
    """根据文件名自动评分

    返回: (score, tags)
    - score: 1-3星
    - tags: 标签列表
    """
    # 3星文档
    if any(kw in filename for kw in SCORING_RULES[3]["keywords"]):
        tags = SCORING_RULES[3]["tags"].copy()
        # 添加主题标签
        if "GRAPHQL" in filename:
            tags.append("GraphQL")
        elif "E2E" in filename or "TEST" in filename:
            tags.append("测试")
        elif "CACHE" in filename:
            tags.append("缓存")
        return 3, tags

    # 2星文档
    elif any(kw in filename for kw in SCORING_RULES[2]["keywords"]):
        tags = SCORING_RULES[2]["tags"].copy()
        # 添加主题标签
        if "GRAPHQL" in filename:
            tags.append("GraphQL")
        elif "E2E" in filename or "TEST" in filename:
            tags.append("测试")
        elif "CACHE" in filename:
            tags.append("缓存")
        return 2, tags

    # 1星文档（默认）
    else:
        return 1, SCORING_RULES[1]["tags"].copy()

def load_manual_scores():
    """加载手动评分配置

    返回: dict {filename: {score, tags, override, reason}}
    """
    if not MANUAL_SCORES_FILE.exists():
        return {}

    try:
        with open(MANUAL_SCORES_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"⚠️  加载手动评分配置失败: {e}")
        return {}

def get_document_score(filename):
    """获取文档评分（优先使用手动配置）

    返回: (score, tags, override, reason)
    """
    manual_scores = load_manual_scores()

    # 检查手动配置
    if filename in manual_scores:
        config = manual_scores[filename]
        score = config.get('score', 1)
        tags = config.get('tags', [])
        override = config.get('override', False)
        reason = config.get('reason', '')
        return score, tags, override, reason

    # 使用自动评分
    score, tags = auto_score_document(filename)
    return score, tags, False, ""

def classify_document(filename):
    """根据文件名分类文档"""
    for topic, keywords in TOPIC_KEYWORDS.items():
        for keyword in keywords:
            if re.search(keyword, filename, re.IGNORECASE):
                return topic
    return "其他"

def find_all_archive_docs():
    """扫描所有归档文档"""
    archive_docs = []

    # 扫描2026年的所有归档
    year_dirs = ARCHIVE_BASE_DIR.glob("202[0-9]/*/reports")
    for reports_dir in year_dirs:
        if reports_dir.is_dir():
            for file in reports_dir.glob("*.md"):
                # 计算相对路径
                rel_path = file.relative_to(ARCHIVE_BASE_DIR)
                archive_docs.append({
                    'filename': file.name,
                    'filepath': rel_path,
                    'full_path': file
                })

    return archive_docs

def generate_markdown_index(docs_by_topic):
    """生成Markdown格式的主题索引（带评分系统）"""
    output = []
    output.append("# 归档文档主题索引\n")
    output.append(f"> 按主题快速查找历史文档，无需记住具体日期\n")
    output.append(f"> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    output.append(f"> **文档总数**: {sum(len(docs) for docs in docs_by_topic.values())} 个\n")
    output.append(f"> **主题数量**: {len(docs_by_topic)} 个\n\n")

    output.append("---\n\n")
    output.append("## 📋 快速导航\n\n")

    # 生成目录
    for i, (topic, docs) in enumerate(sorted(docs_by_topic.items()), 1):
        anchor = topic.lower().replace(" ", "-").replace("迁移", "migration").replace("修复", "fix")
        output.append(f"{i}. [{topic}]({anchor}) ({len(docs)}个)\n")

    output.append("\n---\n\n")

    # 生成评分统计
    output.append("## 📊 评分统计\n\n")
    output.append("| 评分 | 文档数量 | 占比 | 说明 |\n")
    output.append("|------|---------|------|------|\n")

    # 统计各评分等级的文档数量
    total_docs = sum(len(docs) for docs in docs_by_topic.values())
    score_counts = {1: 0, 2: 0, 3: 0}

    for docs in docs_by_topic.values():
        for doc_info in docs:
            score = doc_info.get('score', 1)
            score_counts[score] += 1

    output.append(f"| ⭐⭐⭐ 核心文档 | {score_counts[3]} | {score_counts[3]/total_docs*100:.0f}% | 必读，完整方案 |\n")
    output.append(f"| ⭐⭐ 重要参考 | {score_counts[2]} | {score_counts[2]/total_docs*100:.0f}% | 重要，值得参考 |\n")
    output.append(f"| ⭐ 补充材料 | {score_counts[1]} | {score_counts[1]/total_docs*100:.0f}% | 补充，可选阅读 |\n")

    output.append("\n---\n\n")

    # 按主题输出详细内容
    for topic, docs in sorted(docs_by_topic.items()):
        # 生成锚点ID
        anchor = topic.lower().replace(" ", "-")

        output.append(f"## {topic}\n\n")

        # 查找关联的经验文档
        if "GraphQL" in topic:
            output.append("**📖 经验文档**：[api-design-patterns.md - GraphQL迁移策略](../lessons-learned/api-design-patterns.md#graphql迁移策略--p0极其重要---2026-03-13新增)\n\n")
        elif "E2E" in topic or ("测试" in topic and "覆盖率" not in topic):
            output.append("**📖 经验文档**：[testing-guide.md - Chrome MCP测试流程](../lessons-learned/testing-guide.md)\n\n")
        elif "缓存" in topic:
            output.append("**📖 经验文档**：[performance-patterns.md - 缓存失效诊断](../lessons-learned/performance-patterns.md#缓存失效诊断与修复--p0极其重要---2026-03-13新增)\n\n")
        elif "性能" in topic:
            output.append("**📖 经验文档**：[performance-patterns.md - 性能优化模式](../lessons-learned/performance-patterns.md)\n\n")

        # 按评分分组
        three_star = [d for d in docs if d.get('score', 1) == 3]
        two_star = [d for d in docs if d.get('score', 1) == 2]
        one_star = [d for d in docs if d.get('score', 1) == 1]

        # 输出3星文档
        if three_star:
            output.append(f"### ⭐⭐⭐ 核心文档（{len(three_star)}个）- 必读 ⭐\n\n")
            for doc_info in sorted(three_star, key=lambda x: x['filename']):
                filename = doc_info['filename']
                filepath = doc_info['filepath']
                tags = doc_info.get('tags', [])
                tags_str = ' '.join([f'#{tag}' for tag in tags]) if tags else ''
                output.append(f"- [{filename}]({filepath})\n")
                if tags_str:
                    output.append(f"  - 标签: {tags_str}\n")
            output.append("\n")

        # 输出2星文档
        if two_star:
            output.append(f"### ⭐⭐ 重要参考（{len(two_star)}个）\n\n")
            for doc_info in sorted(two_star, key=lambda x: x['filename']):
                filename = doc_info['filename']
                filepath = doc_info['filepath']
                tags = doc_info.get('tags', [])
                tags_str = ' '.join([f'#{tag}' for tag in tags]) if tags else ''
                output.append(f"- [{filename}]({filepath})\n")
                if tags_str:
                    output.append(f"  - 标签: {tags_str}\n")
            output.append("\n")

        # 输出1星文档
        if one_star:
            output.append(f"### ⭐ 补充材料（{len(one_star)}个）\n\n")
            for doc_info in sorted(one_star, key=lambda x: x['filename']):
                filename = doc_info['filename']
                filepath = doc_info['filepath']
                output.append(f"- [{filename}]({filepath})\n")
            output.append("\n")

        output.append("---\n\n")

    # 添加使用说明
    output.append("## 🔍 使用说明\n\n")
    output.append("### 按主题查找\n")
    output.append("1. 点击上方「快速导航」中的主题链接\n")
    output.append("2. 浏览该主题下的文档（按评分分组）\n")
    output.append("3. 优先阅读 ⭐⭐⭐ 核心文档\n\n")

    output.append("### 搜索关键词\n\n")
    output.append("```bash\n")
    output.append("# 在所有归档中搜索关键词\n")
    output.append("rg \"缓存失效\" docs/archive/\n\n")
    output.append("# 在特定主题中搜索\n")
    output.append("rg \"GraphQL\" docs/archive/2026/03-march/\n")
    output.append("```\n\n")

    output.append("### 按日期查找\n\n")
    output.append("- [2026年3月](2026/03-march/) (65个报告)\n")
    output.append("- [2026年2月](2026/02-february/)\n")

    return "".join(output)

def generate_index():
    """生成主题索引的主函数"""
    print("🔍 开始扫描归档文档...")

    # 1. 扫描所有文档
    all_docs = find_all_archive_docs()

    if not all_docs:
        print("❌ 未找到任何归档文档！")
        print(f"   搜索路径: {ARCHIVE_BASE_DIR}/202[0-9]/*/reports/")
        return

    print(f"✅ 找到 {len(all_docs)} 个归档文档")

    # 2. 按主题分类并评分
    topics = defaultdict(list)
    score_counts = {1: 0, 2: 0, 3: 0}
    manual_count = 0

    for doc_info in all_docs:
        # 主题分类
        topic = classify_document(doc_info['filename'])

        # 评分
        score, tags, override, reason = get_document_score(doc_info['filename'])

        # 添加评分信息到doc_info
        doc_info['score'] = score
        doc_info['tags'] = tags
        doc_info['override'] = override

        # 统计
        score_counts[score] += 1
        if override:
            manual_count += 1

        topics[topic].append(doc_info)

    print(f"✅ 分类完成，共 {len(topics)} 个主题")
    print(f"✅ 评分完成: ⭐⭐×{score_counts[3]} ⭐×{score_counts[2]} ⭐×{score_counts[1]}")

    # 打印分类统计
    print("\n📊 文档分类统计:")
    for topic, docs in sorted(topics.items()):
        three_star = sum(1 for d in docs if d['score'] == 3)
        two_star = sum(1 for d in docs if d['score'] == 2)
        one_star = sum(1 for d in docs if d['score'] == 1)
        print(f"   {topic}: {len(docs)} 个 (⭐⭐×{three_star} ⭐×{two_star} ⭐×{one_star})")

    # 3. 生成Markdown索引
    print(f"\n📝 生成主题索引...")
    markdown_content = generate_markdown_index(topics)

    # 4. 确保输出目录存在
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # 5. 写入文件
    OUTPUT_FILE.write_text(markdown_content, encoding="utf-8")

    print(f"\n✅ 主题索引已生成: {OUTPUT_FILE}")
    print(f"   总文档数: {len(all_docs)} 个")
    print(f"   主题数量: {len(topics)} 个")
    print(f"   手动调整: {manual_count} 个")

    # 6. 验证
    print("\n🔍 验证索引质量...")
    indexed_count = sum(len(docs) for docs in topics.values())
    if indexed_count == len(all_docs):
        print(f"✅ 所有文档已正确分类和评分 ({indexed_count}/{len(all_docs)})")
    else:
        print(f"⚠️ 部分文档未分类 ({indexed_count}/{len(all_docs)})")

if __name__ == "__main__":
    generate_index()
