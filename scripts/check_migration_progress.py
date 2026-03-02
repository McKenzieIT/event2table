#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端迁移检查工具

检查前端代码中REST API的使用情况,帮助跟踪迁移进度

使用方法:
    python scripts/check_migration_progress.py
"""

import os
import re
from pathlib import Path
from collections import defaultdict


class MigrationChecker:
    """前端迁移检查器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.frontend_dir = self.project_root / "frontend" / "src"

        # REST API使用统计
        self.rest_api_usage = defaultdict(list)
        self.graphql_usage = defaultdict(list)

    def scan_frontend(self):
        """扫描前端代码"""
        print("\n" + "="*60)
        print("前端迁移进度检查")
        print("="*60)

        if not self.frontend_dir.exists():
            print(f"❌ 前端目录不存在: {self.frontend_dir}")
            return

        print(f"\n扫描目录: {self.frontend_dir}")

        # 扫描所有前端文件
        for root, dirs, files in os.walk(self.frontend_dir):
            for file in files:
                if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                    filepath = os.path.join(root, file)
                    self._analyze_file(filepath)

        # 输出结果
        self._print_results()

    def _analyze_file(self, filepath):
        """分析单个文件"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                relative_path = os.path.relpath(filepath, self.frontend_dir)

                # 检查REST API使用
                rest_matches = re.findall(r"fetch\(['\"](/api/[^'\"]+)['\"]", content)
                for match in rest_matches:
                    self.rest_api_usage[match].append(relative_path)

                # 检查GraphQL使用
                graphql_matches = re.findall(r"useQuery\((\w+)", content)
                for match in graphql_matches:
                    self.graphql_usage[match].append(relative_path)

                # 检查useMutation
                mutation_matches = re.findall(r"useMutation\((\w+)", content)
                for match in mutation_matches:
                    self.graphql_usage[f"mutation:{match}"].append(relative_path)

        except Exception as e:
            print(f"⚠️  分析文件失败 {filepath}: {e}")

    def _print_results(self):
        """输出检查结果"""
        print("\n" + "-"*60)
        print("REST API 使用情况")
        print("-"*60)

        if not self.rest_api_usage:
            print("✅ 无REST API使用,迁移完成!")
        else:
            total_calls = sum(len(files) for files in self.rest_api_usage.values())
            print(f"❌ 发现 {len(self.rest_api_usage)} 个REST API端点,共 {total_calls} 次调用\n")

            for api, files in sorted(self.rest_api_usage.items(), key=lambda x: len(x[1]), reverse=True):
                print(f"{api}: {len(files)}次")
                for file in files[:3]:  # 只显示前3个文件
                    print(f"  - {file}")
                if len(files) > 3:
                    print(f"  ... 还有{len(files)-3}个文件")
                print()

        print("\n" + "-"*60)
        print("GraphQL 使用情况")
        print("-"*60)

        if not self.graphql_usage:
            print("⚠️  未发现GraphQL使用")
        else:
            total_queries = sum(len(files) for files in self.graphql_usage.values())
            print(f"✅ 发现 {len(self.graphql_usage)} 个GraphQL操作,共 {total_queries} 次使用\n")

            for query, files in sorted(self.graphql_usage.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
                print(f"{query}: {len(files)}次")

        # 迁移进度
        self._print_progress()

    def _print_progress(self):
        """输出迁移进度"""
        print("\n" + "="*60)
        print("迁移进度统计")
        print("="*60)

        total_rest = sum(len(files) for files in self.rest_api_usage.values())
        total_graphql = sum(len(files) for files in self.graphql_usage.values())
        total = total_rest + total_graphql

        if total > 0:
            graphql_percentage = (total_graphql / total) * 100
            rest_percentage = (total_rest / total) * 100

            print(f"\n总API调用: {total}")
            print(f"GraphQL: {total_graphql} ({graphql_percentage:.1f}%)")
            print(f"REST API: {total_rest} ({rest_percentage:.1f}%)")

            print(f"\n迁移进度: {graphql_percentage:.1f}%")
            print(f"剩余工作: {total_rest} 个REST API调用需要迁移")

            # 进度条
            bar_length = 40
            filled_length = int(bar_length * graphql_percentage / 100)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            print(f"\n[{bar}] {graphql_percentage:.1f}%")

            # 建议
            print("\n" + "-"*60)
            print("迁移建议")
            print("-"*60)

            if total_rest > 0:
                print("\n优先迁移的REST API:")
                for api, files in sorted(self.rest_api_usage.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
                    print(f"  1. {api} ({len(files)}次调用)")

                print("\n迁移步骤:")
                print("  1. 查看迁移示例: frontend/src/migration/GAMES_MIGRATION_EXAMPLE.ts")
                print("  2. 使用转换工具: python scripts/rest_to_graphql_converter.py")
                print("  3. 参考迁移指南: docs/api/REST_TO_GRAPHQL_MIGRATION.md")
            else:
                print("\n✅ 所有API已迁移到GraphQL!")

        else:
            print("\n⚠️  未发现API调用")

    def generate_report(self):
        """生成迁移报告"""
        report_file = self.project_root / "docs" / "api" / "MIGRATION_PROGRESS_REPORT.md"

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 前端迁移进度报告\n\n")
            f.write(f"生成时间: {self._get_current_time()}\n\n")

            f.write("## REST API使用情况\n\n")
            if self.rest_api_usage:
                f.write(f"发现 {len(self.rest_api_usage)} 个REST API端点仍在使用:\n\n")
                for api, files in sorted(self.rest_api_usage.items()):
                    f.write(f"### {api}\n")
                    f.write(f"调用次数: {len(files)}\n\n")
                    for file in files:
                        f.write(f"- {file}\n")
                    f.write("\n")
            else:
                f.write("✅ 无REST API使用\n\n")

            f.write("## GraphQL使用情况\n\n")
            if self.graphql_usage:
                f.write(f"发现 {len(self.graphql_usage)} 个GraphQL操作:\n\n")
                for query, files in sorted(self.graphql_usage.items()):
                    f.write(f"- {query}: {len(files)}次\n")
            else:
                f.write("⚠️ 未发现GraphQL使用\n\n")

            f.write("## 迁移进度\n\n")
            total_rest = sum(len(files) for files in self.rest_api_usage.values())
            total_graphql = sum(len(files) for files in self.graphql_usage.values())
            total = total_rest + total_graphql

            if total > 0:
                graphql_percentage = (total_graphql / total) * 100
                f.write(f"- 总API调用: {total}\n")
                f.write(f"- GraphQL: {total_graphql} ({graphql_percentage:.1f}%)\n")
                f.write(f"- REST API: {total_rest} ({100-graphql_percentage:.1f}%)\n")
                f.write(f"- **迁移进度: {graphql_percentage:.1f}%**\n")

        print(f"\n✅ 迁移报告已生成: {report_file}")

    def _get_current_time(self):
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def main():
    checker = MigrationChecker()
    checker.scan_frontend()
    checker.generate_report()


if __name__ == '__main__':
    main()
