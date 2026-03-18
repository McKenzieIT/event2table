#!/usr/bin/env python3
"""
文档整合脚本 - 按照update-docs skill逻辑实现

此脚本实现了以下功能:
1. 扫描docs/目录下的所有markdown文件
2. 识别重复或相似的文档
3. 将重复文档中的关键经验提取到docs/lessons-learned/对应的经验文档中
4. 将处理过的旧文档归档到docs/archive/目录下
5. 更新CLAUDE.md中的经验文档索引

执行方式:
    python scripts/scheduled/doc_consolidation_by_skill.py
"""

import os
import sys
import re
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import hashlib

# 项目路径
PROJECT_DIR = Path("/Users/mckenzie/Documents/event2table")
DOCS_DIR = PROJECT_DIR / "docs"
LOG_FILE = PROJECT_DIR / "logs" / "doc-consolidation.log"
ERROR_LOG = PROJECT_DIR / "logs" / "doc-consolidation-error.log"

# 受保护的文件列表（绝不会被归档）
PROTECTED_FILES = {
    PROJECT_DIR / "CLAUDE.md",
    PROJECT_DIR / "README.md",
    PROJECT_DIR / "CHANGELOG.md",
    PROJECT_DIR / "package.json",
    PROJECT_DIR / "requirements.txt",
}

# 日志函数
def log(message, error=False):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}\n"
    print(log_msg, end="")

    log_file = ERROR_LOG if error else LOG_FILE
    log_file.parent.mkdir(exist_ok=True)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_msg)

def get_file_hash(filepath):
    """计算文件内容的哈希值"""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def find_all_markdown_files(directory):
    """递归查找所有markdown文件"""
    md_files = []
    for root, dirs, files in os.walk(directory):
        # 跳过archive目录
        if 'archive' in root:
            continue
        for file in files:
            if file.endswith('.md'):
                file_path = Path(root) / file
                # 只添加存在的文件
                if file_path.exists():
                    # 跳过受保护的文件
                    if file_path not in PROTECTED_FILES:
                        md_files.append(file_path)
    return md_files

def extract_document_content(filepath):
    """提取文档内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        log(f"读取文件失败 {filepath}: {e}", error=True)
        return None

def find_similar_documents(files, similarity_threshold=0.3):
    """
    查找相似的文档
    基于标题和内容相似度
    """
    similar_groups = []

    for i, file1 in enumerate(files):
        content1 = extract_document_content(file1)
        if content1 is None:
            continue

        title1 = file1.stem
        group = [file1]

        for file2 in files[i+1:]:
            content2 = extract_document_content(file2)
            if content2 is None:
                continue

            # 检查标题相似度
            title2 = file2.stem
            title_similarity = calculate_title_similarity(title1, title2)

            # 检查内容相似度
            content_similarity = calculate_content_similarity(content1, content2)

            if title_similarity > similarity_threshold or content_similarity > 0.5:
                group.append(file2)

        if len(group) > 1:
            similar_groups.append(group)

    return similar_groups

def calculate_title_similarity(title1, title2):
    """计算标题相似度"""
    # 简单的包含关系检查
    title1_lower = title1.lower()
    title2_lower = title2.lower()

    # 完全相同
    if title1_lower == title2_lower:
        return 1.0

    # 一个包含另一个
    if title1_lower in title2_lower or title2_lower in title1_lower:
        return 0.7

    # 检查关键词重叠
    words1 = set(title1_lower.split('-'))
    words2 = set(title2_lower.split('-'))
    if words1 & words2:  # 交集
        overlap = len(words1 & words2) / max(len(words1), len(words2))
        return overlap * 0.5

    return 0.0

def calculate_content_similarity(content1, content2):
    """计算内容相似度 (简化版)"""
    # 提取关键段落
    headers1 = re.findall(r'^#+\s+(.+)$', content1, re.MULTILINE)
    headers2 = re.findall(r'^#+\s+(.+)$', content2, re.MULTILINE)

    if not headers1 or not headers2:
        return 0.0

    # 比较标题重叠
    set1 = set([h.lower().strip() for h in headers1])
    set2 = set([h.lower().strip() for h in headers2])

    if not set1 or not set2:
        return 0.0

    intersection = set1 & set2
    union = set1 | set2

    if not union:
        return 0.0

    return len(intersection) / len(union)

def identify_document_type(filepath):
    """识别文档类型"""
    content = extract_document_content(filepath)
    if not content:
        return "unknown"

    path_str = str(filepath).lower()

    # 根据路径和内容识别类型
    if 'test' in path_str:
        return "testing"
    elif 'optimization' in path_str or 'performance' in path_str:
        return "optimization"
    elif 'api' in path_str:
        return "api"
    elif 'deployment' in path_str:
        return "deployment"
    elif 'architecture' in path_str:
        return "architecture"
    elif 'lesson' in path_str or 'learned' in path_str:
        return "lesson-learned"
    else:
        return "general"

def archive_document(filepath, archive_category):
    """归档文档到指定类别"""
    # 检查文件是否受保护
    if filepath in PROTECTED_FILES:
        log(f"⚠️  跳过受保护文件: {filepath}")
        return None

    # 创建归档目录
    archive_dir = DOCS_DIR / "archive" / archive_category
    archive_dir.mkdir(parents=True, exist_ok=True)

    # 创建日期子目录
    date_str = datetime.now().strftime("%Y-%m")
    date_dir = archive_dir / date_str
    date_dir.mkdir(exist_ok=True)

    # 目标路径
    target_path = date_dir / filepath.name

    # 如果文件已存在，添加后缀
    if target_path.exists():
        base_name = filepath.stem
        counter = 1
        while target_path.exists():
            new_name = f"{base_name}_{counter}{filepath.suffix}"
            target_path = date_dir / new_name
            counter += 1

    # 移动文件
    try:
        shutil.move(str(filepath), str(target_path))
        log(f"归档文件: {filepath} -> {target_path}")
        return target_path
    except Exception as e:
        log(f"归档失败 {filepath}: {e}", error=True)
        return None

def update_archive_index(archive_category, archived_files):
    """更新归档索引"""
    index_path = DOCS_DIR / "archive" / archive_category / "ARCHIVED_INDEX.md"

    # 读取现有索引
    existing_content = ""
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()

    # 准备新条目
    date_str = datetime.now().strftime("%Y-%m-%d")
    new_entry = f"\n## {date_str} 归档\n\n"

    for filepath, archived_path in archived_files:
        rel_path = filepath.relative_to(PROJECT_DIR)
        archive_rel_path = archived_path.relative_to(PROJECT_DIR)
        new_entry += f"- `{rel_path}` → `{archive_rel_path}`\n"

    # 追加到索引
    with open(index_path, 'a', encoding='utf-8') as f:
        f.write(new_entry)

    log(f"更新归档索引: {index_path}")

def extract_experiences_to_lessons_learned(similar_groups):
    """
    从相似文档组中提取经验到docs/lessons-learned/
    """
    experiences_dir = DOCS_DIR / "lessons-learned"
    experiences_dir.mkdir(exist_ok=True)

    extraction_summary = []

    for group in similar_groups:
        # 选择保留最新的文档
        existing_files = [f for f in group if f.exists()]
        if not existing_files:
            continue

        sorted_files = sorted(existing_files, key=lambda f: f.stat().st_mtime, reverse=True)
        primary_doc = sorted_files[0]
        duplicate_docs = sorted_files[1:]

        # 提取内容
        primary_content = extract_document_content(primary_doc)
        if not primary_content:
            continue

        # 识别经验类型
        doc_type = identify_document_type(primary_doc)

        # 确定目标经验文档
        target_lesson_file = get_target_lesson_file(doc_type, experiences_dir)
        if not target_lesson_file:
            log(f"无法确定经验文档类型: {doc_type}", error=True)
            continue

        # 提取关键经验 (简化版)
        key_learnings = extract_key_learnings(primary_content)

        # 追加到经验文档
        if key_learnings:
            append_to_lesson_file(target_lesson_file, primary_doc, key_learnings)
            extraction_summary.append({
                'primary': primary_doc,
                'duplicates': duplicate_docs,
                'lesson_file': target_lesson_file,
                'doc_type': doc_type
            })

    return extraction_summary

def get_target_lesson_file(doc_type, experiences_dir):
    """根据文档类型确定目标经验文件"""
    lesson_files = {
        'testing': 'testing-guide.md',
        'optimization': 'performance-patterns.md',
        'api': 'api-design-patterns.md',
        'deployment': 'deployment-operations.md',
        'architecture': 'project-management.md',  # 架构经验
        'general': 'debugging-skills.md'
    }

    filename = lesson_files.get(doc_type)
    if filename:
        return experiences_dir / filename
    return None

def extract_key_learnings(content):
    """从文档中提取关键经验"""
    learnings = []

    # 提取标题
    headers = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)

    # 提取列表项
    list_items = re.findall(r'^[\-\*]\s+(.+)$', content, re.MULTILINE)

    # 提取标记为重要/关键的内容
    important_markers = ['重要', '关键', '注意', '必须', '应该', '✅', '⚠️', '❌']
    important_lines = []
    for line in content.split('\n'):
        line = line.strip()
        if any(marker in line for marker in important_markers):
            important_lines.append(line)

    # 如果有足够的内容，返回经验摘要
    if len(headers) > 0 or len(list_items) > 5 or len(important_lines) > 3:
        return {
            'headers': headers[:5],  # 最多5个标题
            'list_items': list_items[:10],  # 最多10个列表项
            'important': important_lines[:10]  # 最多10个重要内容
        }

    return None

def append_to_lesson_file(lesson_file, source_doc, key_learnings):
    """追加经验到目标文件"""
    # 准备新内容
    source_rel = source_doc.relative_to(PROJECT_DIR)
    date_str = datetime.now().strftime("%Y-%m-%d")

    new_section = f"\n### 来自 {source_rel} ({date_str})\n\n"

    if key_learnings['headers']:
        new_section += "**关键主题**:\n"
        for header in key_learnings['headers']:
            new_section += f"- {header}\n"
        new_section += "\n"

    if key_learnings['important']:
        new_section += "**重要经验**:\n"
        for item in key_learnings['important'][:5]:
            new_section += f"- {item}\n"
        new_section += "\n"

    # 追加到文件
    try:
        with open(lesson_file, 'a', encoding='utf-8') as f:
            f.write(new_section)
        log(f"追加经验到: {lesson_file.relative_to(PROJECT_DIR)}")
    except Exception as e:
        log(f"追加经验失败 {lesson_file}: {e}", error=True)

def update_claude_md_index(extraction_summary):
    """更新CLAUDE.md中的经验文档索引"""
    claude_md = PROJECT_DIR / "CLAUDE.md"

    if not claude_md.exists():
        log("CLAUDE.md不存在，跳过索引更新")
        return

    # 读取现有内容
    with open(claude_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否需要更新
    if "### 经验文档快速查找" not in content:
        # 添加新的索引章节
        new_section = "\n## 经验文档快速查找 ⭐ **极其重要**\n\n"
        new_section += "> **🚨 所有项目经验已整合到经验文档系统，避免重复，持续更新**\n\n"
        new_section += "### 核心经验文档\n"

        # 添加经验文档链接
        experiences_dir = DOCS_DIR / "lessons-learned"
        if experiences_dir.exists():
            for md_file in sorted(experiences_dir.glob('*.md')):
                rel_path = md_file.relative_to(PROJECT_DIR)
                title = md_file.stem.replace('-', ' ').title()
                new_section += f"- **[{title}]**([{rel_path}])\n"

        content += new_section

        # 写回文件
        with open(claude_md, 'w', encoding='utf-8') as f:
            f.write(content)

        log("更新CLAUDE.md索引")

def main():
    """主函数"""
    log("=" * 60)
    log("🚀 开始执行文档整合任务")
    log("=" * 60)

    try:
        # Phase 1: 扫描所有markdown文件
        log("\n=== Phase 1: 扫描文档 ===")
        all_files = find_all_markdown_files(DOCS_DIR)
        log(f"找到 {len(all_files)} 个markdown文件")

        # Phase 2: 识别相似文档
        log("\n=== Phase 2: 识别相似文档 ===")
        similar_groups = find_similar_documents(all_files)
        log(f"发现 {len(similar_groups)} 组相似文档")

        # Phase 3: 提取经验到lessons-learned
        log("\n=== Phase 3: 提取经验 ===")
        extraction_summary = extract_experiences_to_lessons_learned(similar_groups)
        log(f"提取了 {len(extraction_summary)} 组经验到docs/lessons-learned/")

        # Phase 4: 归档旧文档
        log("\n=== Phase 4: 归档旧文档 ===")
        archived_by_category = defaultdict(list)

        for group in similar_groups:
            # 保留最新的，归档其他
            # 过滤掉不存在的文件
            existing_files = [f for f in group if f.exists()]
            if not existing_files:
                continue

            sorted_files = sorted(existing_files, key=lambda f: f.stat().st_mtime, reverse=True)
            primary_doc = sorted_files[0]
            duplicate_docs = sorted_files[1:]

            for duplicate in duplicate_docs:
                if not duplicate.exists():
                    continue
                doc_type = identify_document_type(duplicate)
                archived_path = archive_document(duplicate, doc_type)
                if archived_path:
                    archived_by_category[doc_type].append((duplicate, archived_path))

        # 更新归档索引
        for category, files in archived_by_category.items():
            update_archive_index(category, files)

        log(f"归档了 {sum(len(files) for files in archived_by_category.values())} 个文档")

        # Phase 5: 更新索引
        log("\n=== Phase 5: 更新索引 ===")
        update_claude_md_index(extraction_summary)

        # 完成总结
        log("\n" + "=" * 60)
        log("✅ 文档整合任务完成")
        log("=" * 60)
        log(f"处理的相似文档组: {len(similar_groups)}")
        log(f"提取的经验组: {len(extraction_summary)}")
        log(f"归档的文档: {sum(len(files) for files in archived_by_category.values())}")

        return 0

    except Exception as e:
        log(f"\n❌ 执行失败: {e}", error=True)
        import traceback
        log(traceback.format_exc(), error=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
