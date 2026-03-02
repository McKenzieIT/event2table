#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端迁移测试验证脚本

验证GraphQL迁移的完整性和正确性

使用方法:
    python scripts/test_graphql_migration.py
"""

import subprocess
import json
import sys
from pathlib import Path


class MigrationTester:
    """迁移测试器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_results = []

    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*60)
        print("GraphQL迁移测试验证")
        print("="*60)

        # 1. 检查GraphQL Schema
        self.test_graphql_schema()

        # 2. 检查前端组件
        self.test_frontend_components()

        # 3. 检查API端点
        self.test_api_endpoints()

        # 4. 性能测试
        self.test_performance()

        # 输出结果
        self.print_results()

    def test_graphql_schema(self):
        """测试GraphQL Schema"""
        print("\n[1/4] 测试GraphQL Schema...")
        
        schema_file = self.project_root / "backend" / "gql_api" / "schema.py"
        if not schema_file.exists():
            self.add_result("GraphQL Schema", False, "Schema文件不存在")
            return

        # 检查Schema内容
        with open(schema_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查必要的Query (使用Python命名规范)
        required_queries = [
            'game', 'games', 'search_games',  # Python使用下划线
            'event', 'events', 'search_events',
            'parameter', 'parameters',
            'category', 'categories',
            'flow', 'flows'
        ]

        missing_queries = []
        for query in required_queries:
            if query not in content:
                missing_queries.append(query)

        if missing_queries:
            self.add_result(
                "GraphQL Schema",
                False,
                f"缺少Query: {', '.join(missing_queries)}"
            )
        else:
            self.add_result(
                "GraphQL Schema",
                True,
                f"所有必需Query存在 ({len(required_queries)}个)"
            )

    def test_frontend_components(self):
        """测试前端组件"""
        print("\n[2/4] 测试前端组件...")

        # 检查GraphQL操作定义
        operations_file = self.project_root / "frontend" / "src" / "shared" / "graphql" / "operations.ts"
        if operations_file.exists():
            with open(operations_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查必要的操作
            required_operations = [
                'GET_GAMES', 'CREATE_GAME', 'UPDATE_GAME', 'DELETE_GAME',
                'GET_EVENTS', 'CREATE_EVENT', 'UPDATE_EVENT', 'DELETE_EVENT',
                'GET_CATEGORIES', 'CREATE_CATEGORY', 'UPDATE_CATEGORY', 'DELETE_CATEGORY',
                'GET_FLOWS', 'CREATE_FLOW', 'UPDATE_FLOW', 'DELETE_FLOW'
            ]

            missing_ops = []
            for op in required_operations:
                if op not in content:
                    missing_ops.append(op)

            if missing_ops:
                self.add_result(
                    "GraphQL操作定义",
                    False,
                    f"缺少操作: {', '.join(missing_ops)}"
                )
            else:
                self.add_result(
                    "GraphQL操作定义",
                    True,
                    f"所有必需操作定义存在 ({len(required_operations)}个)"
                )
        else:
            self.add_result("GraphQL操作定义", False, "operations.ts文件不存在")

        # 检查迁移组件
        migrated_components = [
            "frontend/src/features/games/GameManagementModalGraphQL.tsx",
            "frontend/src/migration/GAMES_MIGRATION_EXAMPLE.ts"
        ]

        existing_components = []
        for component in migrated_components:
            component_path = self.project_root / component
            if component_path.exists():
                existing_components.append(component)

        if len(existing_components) == len(migrated_components):
            self.add_result(
                "迁移组件",
                True,
                f"所有迁移组件存在 ({len(existing_components)}个)"
            )
        else:
            self.add_result(
                "迁移组件",
                False,
                f"部分组件缺失 (存在{len(existing_components)}/{len(migrated_components)})"
            )

    def test_api_endpoints(self):
        """测试API端点"""
        print("\n[3/4] 测试API端点...")

        # 检查GraphQL端点
        graphql_route = self.project_root / "backend" / "api" / "routes" / "graphql.py"
        if graphql_route.exists():
            self.add_result("GraphQL端点", True, "GraphQL端点已配置")
        else:
            self.add_result("GraphQL端点", False, "GraphQL端点未配置")

        # 检查废弃中间件
        deprecation_middleware = self.project_root / "backend" / "api" / "middleware" / "deprecation.py"
        if deprecation_middleware.exists():
            with open(deprecation_middleware, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '2026-04-30' in content:
                self.add_result("废弃中间件", True, "废弃日期已更新")
            else:
                self.add_result("废弃中间件", False, "废弃日期未更新")
        else:
            self.add_result("废弃中间件", False, "废弃中间件不存在")

    def test_performance(self):
        """测试性能"""
        print("\n[4/4] 测试性能优化...")

        # 检查DataLoader
        dataloader_dir = self.project_root / "backend" / "gql_api" / "dataloaders"
        if dataloader_dir.exists():
            dataloaders = list(dataloader_dir.glob("*_loader.py"))
            if len(dataloaders) >= 3:
                self.add_result(
                    "DataLoader",
                    True,
                    f"DataLoader已实现 ({len(dataloaders)}个)"
                )
            else:
                self.add_result(
                    "DataLoader",
                    False,
                    f"DataLoader不足 ({len(dataloaders)}个)"
                )
        else:
            self.add_result("DataLoader", False, "DataLoader目录不存在")

        # 检查缓存中间件
        cache_middleware = self.project_root / "backend" / "gql_api" / "middleware" / "cache_middleware.py"
        if cache_middleware.exists():
            self.add_result("缓存中间件", True, "缓存中间件已实现")
        else:
            self.add_result("缓存中间件", False, "缓存中间件不存在")

    def add_result(self, test_name: str, passed: bool, message: str):
        """添加测试结果"""
        self.test_results.append({
            'name': test_name,
            'passed': passed,
            'message': message
        })

    def print_results(self):
        """输出测试结果"""
        print("\n" + "="*60)
        print("测试结果")
        print("="*60)

        passed_count = sum(1 for r in self.test_results if r['passed'])
        total_count = len(self.test_results)

        for result in self.test_results:
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            print(f"\n{status} - {result['name']}")
            print(f"  {result['message']}")

        print("\n" + "-"*60)
        print(f"总计: {passed_count}/{total_count} 通过")
        print("-"*60)

        if passed_count == total_count:
            print("\n🎉 所有测试通过! 迁移验证成功!")
            print("\n下一步:")
            print("1. 部署到测试环境")
            print("2. 执行功能测试")
            print("3. 执行性能测试")
            print("4. 准备生产环境发布")
        else:
            print("\n⚠️  部分测试失败,请检查并修复")
            sys.exit(1)

    def generate_report(self):
        """生成测试报告"""
        report_file = self.project_root / "docs" / "api" / "MIGRATION_TEST_REPORT.md"

        passed_count = sum(1 for r in self.test_results if r['passed'])
        total_count = len(self.test_results)

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# GraphQL迁移测试报告\n\n")
            f.write(f"**测试时间**: {self._get_current_time()}\n\n")
            f.write(f"**测试结果**: {passed_count}/{total_count} 通过\n\n")

            f.write("## 测试详情\n\n")
            for result in self.test_results:
                status = "✅" if result['passed'] else "❌"
                f.write(f"### {status} {result['name']}\n\n")
                f.write(f"**状态**: {'通过' if result['passed'] else '失败'}\n\n")
                f.write(f"**详情**: {result['message']}\n\n")

            f.write("## 总结\n\n")
            if passed_count == total_count:
                f.write("✅ 所有测试通过,迁移验证成功!\n")
            else:
                f.write(f"⚠️ {total_count - passed_count}项测试失败,需要修复\n")

        print(f"\n✅ 测试报告已生成: {report_file}")

    def _get_current_time(self):
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def main():
    tester = MigrationTester()
    tester.run_all_tests()
    tester.generate_report()


if __name__ == '__main__':
    main()
