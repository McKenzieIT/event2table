#!/usr/bin/env python3
"""
文档整合定时任务 - 直接实现版本
不依赖Claude CLI --print模式，直接使用文件操作和经验提取
"""

import os
import sys
import re
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import json

# 添加项目路径
PROJECT_DIR = Path("/Users/mckenzie/Documents/event2table")
sys.path.insert(0, str(PROJECT_DIR))

# 配置
DOCS_DIR = PROJECT_DIR / "docs"
LESSONS_DIR = DOCS_DIR / "lessons-learned"
ARCHIVE_DIR = DOCS_DIR / "archive"
LOG_FILE = PROJECT_DIR / "logs" / "doc-consolidation.log"

class DocConsolidator:
    """文档整合器"""

    def __init__(self):
        self.docs_dir = DOCS_DIR
        self.lessons_dir = LESSONS_DIR
        self.archive_dir = ARCHIVE_DIR
        self.log_file = LOG_FILE

        # 确保目录存在
        self.log_file.parent.mkdir(exist_ok=True)
        self.lessons_dir.mkdir(exist_ok=True)
        self.archive_dir.mkdir(exist_ok=True)

    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}\n"
        print(log_msg, end="")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_msg)

    def get_all_markdown_files(self, directory):
        """获取目录下所有markdown文件"""
        return list(directory.rglob("*.md"))

    def extract_keywords(self, content):
        """提取文档关键词"""
        # 提取标题
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else "无标题"

        # 提取代码块
        code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', content, re.DOTALL)

        # 提取重要标记
        important_patterns = [
            r'⚠️\s*\*?\*?重要',
            r'🚨\s*\*?\*?极其重要',
            r'✅\s*\*?\*?已完成',
            r'❌\s*\*?\*?禁止',
            r'🆕\s*\*?\*?新增',
        ]

        importance_markers = []
        for pattern in important_patterns:
            if re.search(pattern, content):
                importance_markers.append(pattern)

        # 提取经验标记
        experience_keywords = [
            '经验', '教训', '最佳实践', '错误', '问题', '解决方案',
            'lesson', 'experience', 'best practice', 'mistake'
        ]

        keyword_count = 0
        for keyword in experience_keywords:
            keyword_count += content.lower().count(keyword.lower())

        return {
            'title': title,
            'code_blocks': len(code_blocks),
            'importance_markers': importance_markers,
            'keyword_count': keyword_count,
            'length': len(content)
        }

    def calculate_similarity(self, doc1_info, doc2_info):
        """计算文档相似度"""
        score = 0

        # 标题相似度
        if doc1_info['title'] == doc2_info['title']:
            score += 0.4

        # 长度相似度
        len_diff = abs(doc1_info['length'] - doc2_info['length'])
        len_avg = (doc1_info['length'] + doc2_info['length']) / 2
        if len_avg > 0:
            len_similarity = 1 - (len_diff / len_avg)
            score += len_similarity * 0.2

        # 重要性标记相似度
        markers1 = set(doc1_info['importance_markers'])
        markers2 = set(doc2_info['importance_markers'])
        if markers1 or markers2:
            marker_similarity = len(markers1 & markers2) / len(markers1 | markers2)
            score += marker_similarity * 0.2

        # 关键词密度相似度
        keyword_avg = (doc1_info['keyword_count'] + doc2_info['keyword_count']) / 2
        if keyword_avg > 0:
            keyword_similarity = 1 - abs(doc1_info['keyword_count'] - doc2_info['keyword_count']) / keyword_avg
            score += keyword_similarity * 0.2

        return score

    def find_duplicate_documents(self):
        """查找重复或相似的文档"""
        self.log("🔍 开始扫描文档...")

        # 获取所有文档（排除lessons和archive目录）
        all_docs = []
        for doc_file in self.get_all_markdown_files(self.docs_dir):
            # 跳过lessons-learned和archive目录
            if "lessons-learned" in str(doc_file) or "archive" in str(doc_file):
                continue

            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                doc_info = self.extract_keywords(content)
                doc_info['path'] = doc_file
                doc_info['relative_path'] = doc_file.relative_to(self.docs_dir)

                all_docs.append(doc_info)
            except Exception as e:
                self.log(f"⚠️  读取文件失败: {doc_file} - {e}")

        self.log(f"📊 找到 {len(all_docs)} 个文档")

        # 查找相似文档
        self.log("🔄 计算文档相似度...")
        duplicates = []
        processed = set()

        for i, doc1 in enumerate(all_docs):
            if doc1['path'] in processed:
                continue

            similar_docs = [doc1]

            for j, doc2 in enumerate(all_docs):
                if i == j or doc2['path'] in processed:
                    continue

                similarity = self.calculate_similarity(doc1, doc2)

                # 相似度阈值：0.6以上视为相似
                if similarity >= 0.6:
                    similar_docs.append(doc2)
                    processed.add(doc2['path'])

            if len(similar_docs) > 1:
                duplicates.append(similar_docs)
                processed.add(doc1['path'])

        self.log(f"🎯 找到 {len(duplicates)} 组相似文档")

        return duplicates

    def extract_lessons_from_docs(self, docs):
        """从文档组中提取经验"""
        lessons = []

        for doc in docs:
            try:
                with open(doc['path'], 'r', encoding='utf-8') as f:
                    content = f.read()

                # 提取经验章节
                lesson_patterns = [
                    r'##+\s*(经验|教训|最佳实践| Lessons Learned|Best Practice)',
                    r'##+\s*(问题|错误|Issue|Problem|Error)',
                    r'##+\s*(解决方案|Solution|Fix)',
                ]

                extracted_lessons = []
                for pattern in lesson_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # 获取该章节的内容（到下一个##或文件结尾）
                        start_pos = match.start()
                        next_header = re.search(r'\n#+\s', content[start_pos + 50:])
                        if next_header:
                            end_pos = start_pos + 50 + next_header.start()
                        else:
                            end_pos = len(content)

                        lesson_content = content[start_pos:end_pos].strip()
                        extracted_lessons.append(lesson_content)

                if extracted_lessons:
                    lessons.append({
                        'source_doc': doc['relative_path'],
                        'title': doc['title'],
                        'lessons': extracted_lessons
                    })
            except Exception as e:
                self.log(f"⚠️  提取经验失败: {doc['path']} - {e}")

        return lessons

    def update_lessons_learned(self, duplicates):
        """更新经验文档"""
        self.log("📝 开始更新经验文档...")

        # 经验文档分类
        categories = {
            'api-design-patterns.md': ['API', '接口', '路由', 'endpoint'],
            'database-patterns.md': ['数据库', 'database', 'SQL', 'query'],
            'debugging-skills.md': ['调试', 'debug', '错误', 'error'],
            'performance-patterns.md': ['性能', 'performance', '优化', 'optimization'],
            'react-best-practices.md': ['React', '前端', 'frontend', 'component'],
            'testing-guide.md': ['测试', 'test', 'E2E', 'pytest'],
            'security-essentials.md': ['安全', 'security', 'XSS', '注入'],
        }

        updated_count = 0

        for docs_group in duplicates:
            lessons = self.extract_lessons_from_docs(docs_group)

            if not lessons:
                continue

            # 确定应该更新哪个经验文档
            target_category = None
            max_matches = 0

            for category_file, keywords in categories.items():
                matches = sum(
                    1 for doc in docs_group
                    for keyword in keywords
                    if keyword.lower() in str(doc).lower()
                )

                if matches > max_matches:
                    max_matches = matches
                    target_category = category_file

            if target_category:
                target_file = self.lessons_dir / target_category

                try:
                    # 追加经验到目标文件
                    with open(target_file, 'a', encoding='utf-8') as f:
                        f.write(f"\n\n## 从归档文档提取的经验\n")
                        f.write(f"提取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                        for lesson_data in lessons:
                            f.write(f"### 来源: {lesson_data['source_doc']}\n\n")
                            for lesson in lesson_data['lessons']:
                                f.write(f"{lesson}\n\n")
                            f.write("---\n\n")

                    self.log(f"✅ 更新经验文档: {target_category}")
                    updated_count += 1
                except Exception as e:
                    self.log(f"❌ 更新失败: {target_category} - {e}")

        self.log(f"📊 更新了 {updated_count} 个经验文档")

    def archive_old_documents(self, duplicates):
        """归档旧文档"""
        self.log("📦 开始归档文档...")

        # 按月份组织归档
        archive_month = datetime.now().strftime("%Y-%m")
        month_archive_dir = self.archive_dir / archive_month
        month_archive_dir.mkdir(exist_ok=True)

        archived_count = 0

        for docs_group in duplicates:
            # 保留最新或最重要的文档，归档其他
            # 按重要性标记和长度排序
            sorted_docs = sorted(
                docs_group,
                key=lambda x: (
                    len(x['importance_markers']),
                    x['length']
                ),
                reverse=True
            )

            # 保留第一个，归档其他
            for doc in sorted_docs[1:]:
                try:
                    # 创建归档目录结构
                    relative_path = doc['relative_path']
                    archive_path = month_archive_dir / relative_path
                    archive_path.parent.mkdir(parents=True, exist_ok=True)

                    # 移动文件
                    shutil.move(str(doc['path']), str(archive_path))

                    self.log(f"📦 归档: {relative_path}")
                    archived_count += 1
                except Exception as e:
                    self.log(f"❌ 归档失败: {doc['relative_path']} - {e}")

        self.log(f"📊 归档了 {archived_count} 个文档")

    def update_claude_md_index(self):
        """更新CLAUDE.md中的经验文档索引"""
        self.log("🔍 更新CLAUDE.md索引...")

        claude_md = PROJECT_DIR / "CLAUDE.md"

        if not claude_md.exists():
            self.log("⚠️  CLAUDE.md文件不存在")
            return

        try:
            with open(claude_md, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查是否已有经验文档索引章节
            index_pattern = r'## 经验文档快速查找.*?(?=\n##|\Z)'
            existing_index = re.search(index_pattern, content, re.DOTALL)

            # 获取当前所有经验文档
            lesson_files = sorted(self.get_all_markdown_files(self.lessons_dir))

            # 生成新的索引
            new_index = "## 经验文档快速查找 ⭐ **极其重要**\n\n"
            new_index += "> **🚨 所有项目经验已整合到经验文档系统，避免重复，持续更新**\n\n"
            new_index += "### 核心经验文档（docs/lessons-learned/）\n"

            for lesson_file in lesson_files:
                relative_path = lesson_file.relative_to(self.docs_dir)
                filename = lesson_file.name
                display_name = filename.replace('-', ' ').replace('.md', '').title()

                new_index += f"- **[{display_name}]** ([{filename}]({relative_path}))\n"

            new_index += "\n### 完整经验文档索引\n"
            new_index += "- **[经验文档索引](docs/lessons-learned/README.md)** - 所有经验文档的导航中心 ⭐\n"

            # 更新或插入索引
            if existing_index:
                content = re.sub(index_pattern, new_index, content, flags=re.DOTALL)
                self.log("✅ 更新现有索引")
            else:
                # 在适当位置插入（在"快速参考"之前）
                quick_ref_pattern = r'(## 快速参考)'
                content = re.sub(
                    quick_ref_pattern,
                    new_index + '\n\n' + r'\1',
                    content
                )
                self.log("✅ 插入新索引")

            # 写回文件
            with open(claude_md, 'w', encoding='utf-8') as f:
                f.write(content)

            self.log("✅ CLAUDE.md索引更新完成")

        except Exception as e:
            self.log(f"❌ 更新CLAUDE.md失败: {e}")

    def run(self):
        """执行完整的文档整合流程"""
        self.log("=" * 50)
        self.log("🚀 开始执行文档整合任务")
        self.log("=" * 50)

        try:
            # 1. 查找重复文档
            duplicates = self.find_duplicate_documents()

            if not duplicates:
                self.log("✅ 没有发现需要整合的文档")
                return

            # 2. 提取并更新经验文档
            self.update_lessons_learned(duplicates)

            # 3. 归档旧文档
            self.archive_old_documents(duplicates)

            # 4. 更新CLAUDE.md索引
            self.update_claude_md_index()

            self.log("=" * 50)
            self.log("✅ 文档整合任务完成")
            self.log("=" * 50)

        except Exception as e:
            self.log(f"❌ 任务执行失败: {e}")
            import traceback
            self.log(traceback.format_exc())
            raise


def main():
    """主函数"""
    consolidator = DocConsolidator()
    consolidator.run()


if __name__ == "__main__":
    main()
