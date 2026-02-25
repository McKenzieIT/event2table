#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命名规范检查脚本

检查项目中的文件和代码是否符合命名规范。
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 排除的目录
EXCLUDE_DIRS = {
    'node_modules', '.git', '__pycache__', 'venv', '.pytest_cache',
    '.mypy_cache', '.ruff_cache', 'dist', 'build', '.next', 'coverage'
}

# 排除的文件
EXCLUDE_FILES = {
    '.DS_Store', '.env', '.gitignore', 'package-lock.json',
    'package.json', 'pyproject.toml', 'pytest.ini'
}


class NamingChecker:
    """命名规范检查器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.issues: List[Dict] = []

    def check_all(self) -> List[Dict]:
        """执行所有检查"""
        self._check_python_files()
        self._check_vue_files()
        self._check_typescript_files()
        self._check_directories()
        return self.issues

    def _check_python_files(self):
        """检查Python文件命名"""
        for py_file in self.project_root.rglob('*.py'):
            if self._should_exclude(py_file):
                continue

            filename = py_file.name

            # 测试文件检查
            if filename.startswith('test_'):
                continue  # 测试文件命名正确

            # 检查是否包含大写字母
            if re.search(r'[A-Z]', filename):
                self._add_issue(
                    'python_file',
                    str(py_file.relative_to(self.project_root)),
                    f"Python文件名应使用小写字母和下划线: {filename}"
                )

            # 检查是否包含连字符
            if '-' in filename:
                self._add_issue(
                    'python_file',
                    str(py_file.relative_to(self.project_root)),
                    f"Python文件名不应包含连字符: {filename}"
                )

    def _check_vue_files(self):
        """检查Vue组件文件命名"""
        for vue_file in self.project_root.rglob('*.vue'):
            if self._should_exclude(vue_file):
                continue

            filename = vue_file.stem

            # Vue组件应使用PascalCase
            if not re.match(r'^[A-Z][a-zA-Z0-9]*$', filename):
                # 允许一些特殊文件
                if filename in ['App', 'main', 'index']:
                    continue
                self._add_issue(
                    'vue_file',
                    str(vue_file.relative_to(self.project_root)),
                    f"Vue组件文件名应使用PascalCase: {filename}.vue"
                )

    def _check_typescript_files(self):
        """检查TypeScript文件命名"""
        for ts_file in self.project_root.rglob('*.ts'):
            if self._should_exclude(ts_file):
                continue

            filename = ts_file.name

            # 类型定义文件
            if filename.endswith('.d.ts'):
                continue

            # 工具文件应使用camelCase
            if not filename.startswith('test') and not filename.startswith('_'):
                if re.search(r'_', filename.replace('.ts', '')):
                    self._add_issue(
                        'typescript_file',
                        str(ts_file.relative_to(self.project_root)),
                        f"TypeScript文件名应使用camelCase: {filename}"
                    )

    def _check_directories(self):
        """检查目录命名"""
        for directory in self.project_root.rglob('*'):
            if not directory.is_dir():
                continue
            if self._should_exclude(directory):
                continue

            dirname = directory.name

            # 后端目录应使用小写字母
            if 'backend' in str(directory) or 'tests' in str(directory):
                if re.search(r'[A-Z]', dirname):
                    self._add_issue(
                        'directory',
                        str(directory.relative_to(self.project_root)),
                        f"后端目录名应使用小写字母: {dirname}"
                    )

            # 前端组件目录应使用PascalCase
            if 'components' in str(directory) and 'frontend' in str(directory):
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', dirname):
                    self._add_issue(
                        'directory',
                        str(directory.relative_to(self.project_root)),
                        f"前端组件目录应使用PascalCase: {dirname}"
                    )

    def _should_exclude(self, path: Path) -> bool:
        """检查路径是否应排除"""
        for part in path.parts:
            if part in EXCLUDE_DIRS:
                return True
        return path.name in EXCLUDE_FILES

    def _add_issue(self, category: str, path: str, message: str):
        """添加问题"""
        self.issues.append({
            'category': category,
            'path': path,
            'message': message
        })


def print_report(issues: List[Dict]):
    """打印检查报告"""
    if not issues:
        print("\n✅ 命名规范检查通过！未发现问题。")
        return

    print(f"\n❌ 发现 {len(issues)} 个命名规范问题:\n")

    # 按类别分组
    by_category: Dict[str, List[Dict]] = {}
    for issue in issues:
        category = issue['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(issue)

    # 打印每个类别的问题
    category_names = {
        'python_file': 'Python文件',
        'vue_file': 'Vue组件',
        'typescript_file': 'TypeScript文件',
        'directory': '目录'
    }

    for category, items in by_category.items():
        print(f"\n### {category_names.get(category, category)} ({len(items)}个问题)")
        print("-" * 60)
        for item in items:
            print(f"  📁 {item['path']}")
            print(f"     ⚠️  {item['message']}")
            print()


def main():
    """主函数"""
    print("=" * 60)
    print("Event2Table 命名规范检查")
    print("=" * 60)

    checker = NamingChecker(PROJECT_ROOT)
    issues = checker.check_all()

    print_report(issues)

    # 返回退出码
    sys.exit(1 if issues else 0)


if __name__ == '__main__':
    main()
