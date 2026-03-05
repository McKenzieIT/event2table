#!/usr/bin/env python3
"""
检查文档中的死链接

用法:
    python scripts/tools/check_doc_links.py
"""

import re
from pathlib import Path
from typing import List, Tuple

def find_markdown_links(content: str) -> List[str]:
    """查找markdown文件中的所有链接"""
    # 匹配 [text](url) 格式的链接
    # 只匹配.md文件链接，排除http/https链接
    pattern = r'\[([^\]]+)\]\((?!http)([^)]+\.md[^)]*)\)'
    matches = re.findall(pattern, content)
    # matches是元组列表(text, url)，我们只需要url部分
    return [url for text, url in matches]

def resolve_link_path(link: str, source_file: Path, base_path: Path) -> Path:
    """解析相对路径为绝对路径"""
    if link.startswith("http://") or link.startswith("https://"):
        return None  # 外部链接，跳过

    # 解析相对路径
    if link.startswith("../"):
        # 向上查找
        target = source_file.parent
        for _ in link.count("../"):
            target = target.parent if target != target.parent else target
        # 移除开头的 ../
        remaining = link.lstrip("../")
        target = target / remaining
    elif link.startswith("./"):
        # 当前目录
        target = source_file.parent / link.lstrip("./")
    else:
        # 相对于base_path
        target = base_path / link

    return target.resolve()

def check_links(base_path: Path) -> List[Tuple[str, str]]:
    """检查所有markdown文件的链接"""
    dead_links = []

    # 查找所有markdown文件（排除archive目录）
    md_files = [f for f in base_path.rglob("*.md") if "archive" not in str(f)]

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8")
            links = find_markdown_links(content)

            for link in links:
                target_path = resolve_link_path(link, md_file, base_path)

                if target_path is None:
                    continue  # 外部链接

                if not target_path.exists():
                    rel_source = md_file.relative_to(base_path)
                    dead_links.append((str(rel_source), link))
        except Exception as e:
            print(f"⚠️  读取文件失败: {md_file.relative_to(base_path)} - {e}")

    return dead_links

def main():
    """主函数"""
    # 设置基础路径
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent.parent
    base_path = project_root / "docs"

    print(f"🔍 检查文档链接: {base_path}")
    print(f"{'='*60}")

    # 检查链接
    dead_links = check_links(base_path)

    if dead_links:
        print(f"❌ 发现 {len(dead_links)} 个死链接:\n")
        for source, target in dead_links:
            print(f"  源文件: {source}")
            print(f"  目标:   {target}")
            print()
        return 1
    else:
        print("✅ 所有链接有效")
        return 0

if __name__ == "__main__":
    exit(main())
