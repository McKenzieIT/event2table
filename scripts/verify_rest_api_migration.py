#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REST API移除前二次确认脚本

验证所有REST API功能是否已迁移到GraphQL

使用方法:
    python scripts/verify_rest_api_migration.py
"""

import os
import re
from pathlib import Path
from collections import defaultdict


class RESTAPIMigrationVerifier:
    """REST API迁移验证器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.verification_results = []

    def verify_all(self):
        """执行所有验证"""
        print("\n" + "="*60)
        print("REST API移除前二次验证")
        print("="*60)

        # 1. 验证GraphQL功能完整性
        self.verify_graphql_completeness()

        # 2. 验证前端迁移状态
        self.verify_frontend_migration()

        # 3. 验证REST API使用情况
        self.verify_rest_api_usage()

        # 4. 验证测试覆盖
        self.verify_test_coverage()

        # 输出结果
        self.print_results()

    def verify_graphql_completeness(self):
        """验证GraphQL功能完整性"""
        print("\n[1/4] 验证GraphQL功能完整性...")

        # 检查GraphQL Schema
        schema_file = self.project_root / "backend" / "gql_api" / "schema.py"
        if not schema_file.exists():
            self.add_result("GraphQL Schema", False, "Schema文件不存在")
            return

        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_content = f.read()

        # 检查必要的Query和Mutation
        required_features = {
            'Query': [
                'game', 'games', 'searchGames',
                'event', 'events', 'searchEvents',
                'parameter', 'parameters',
                'category', 'categories', 'searchCategories',
                'flow', 'flows',
                'dashboardStats', 'gameStats'
            ],
            'Mutation': [
                'createGame', 'updateGame', 'deleteGame',
                'createEvent', 'updateEvent', 'deleteEvent',
                'createParameter', 'updateParameter', 'deleteParameter',
                'createCategory', 'updateCategory', 'deleteCategory',
                'createFlow', 'updateFlow', 'deleteFlow'
            ]
        }

        missing_features = []
        for feature_type, features in required_features.items():
            for feature in features:
                if feature not in schema_content:
                    missing_features.append(f"{feature_type}.{feature}")

        if missing_features:
            self.add_result(
                "GraphQL功能完整性",
                False,
                f"缺少功能: {', '.join(missing_features[:5])}"
            )
        else:
            total_features = sum(len(f) for f in required_features.values())
            self.add_result(
                "GraphQL功能完整性",
                True,
                f"所有功能已实现 ({total_features}个)"
            )

    def verify_frontend_migration(self):
        """验证前端迁移状态"""
        print("\n[2/4] 验证前端迁移状态...")

        # 检查GraphQL操作定义
        operations_file = self.project_root / "frontend" / "src" / "shared" / "graphql" / "operations.ts"
        if operations_file.exists():
            with open(operations_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 统计GraphQL操作数量
            query_count = content.count('export const GET_')
            mutation_count = content.count('export const CREATE_') + \
                           content.count('export const UPDATE_') + \
                           content.count('export const DELETE_')

            total_operations = query_count + mutation_count

            if total_operations >= 20:
                self.add_result(
                    "前端GraphQL操作",
                    True,
                    f"已定义{total_operations}个操作 (查询:{query_count}, 变更:{mutation_count})"
                )
            else:
                self.add_result(
                    "前端GraphQL操作",
                    False,
                    f"操作数量不足 ({total_operations}个)"
                )
        else:
            self.add_result("前端GraphQL操作", False, "operations.ts不存在")

        # 检查迁移组件
        migrated_components = [
            "frontend/src/features/games/GameManagementModalGraphQL.tsx",
            "frontend/src/migration/GAMES_MIGRATION_EXAMPLE.ts"
        ]

        existing = sum(1 for comp in migrated_components if (self.project_root / comp).exists())
        if existing == len(migrated_components):
            self.add_result(
                "迁移组件",
                True,
                f"所有迁移组件已创建 ({existing}个)"
            )
        else:
            self.add_result(
                "迁移组件",
                False,
                f"部分组件缺失 ({existing}/{len(migrated_components)})"
            )

    def verify_rest_api_usage(self):
        """验证REST API使用情况"""
        print("\n[3/4] 验证REST API使用情况...")

        frontend_dir = self.project_root / "frontend" / "src"
        if not frontend_dir.exists():
            self.add_result("REST API使用", False, "前端目录不存在")
            return

        # 扫描REST API使用
        rest_api_usage = defaultdict(list)
        for root, dirs, files in os.walk(frontend_dir):
            for file in files:
                if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            matches = re.findall(r"fetch\(['\"](/api/[^'\"]+)['\"]", content)
                            for match in matches:
                                rest_api_usage[match].append(os.path.relpath(filepath, frontend_dir))
                    except:
                        pass

        # 分类API
        critical_apis = ['/api/games', '/api/events', '/api/parameters', '/api/categories']
        special_apis = ['/api/generate', '/api/hql/', '/api/preview-', '/api/events/import', '/api/*/batch']

        critical_usage = {k: v for k, v in rest_api_usage.items() if any(api in k for api in critical_apis)}
        special_usage = {k: v for k, v in rest_api_usage.items() if any(api in k for api in special_apis)}

        if critical_usage:
            total_critical = sum(len(v) for v in critical_usage.values())
            self.add_result(
                "REST API使用(关键)",
                False,
                f"发现{len(critical_usage)}个关键API仍在使用,共{total_critical}次调用"
            )
        else:
            self.add_result(
                "REST API使用(关键)",
                True,
                "所有关键API已迁移到GraphQL"
            )

        if special_usage:
            total_special = sum(len(v) for v in special_usage.values())
            self.add_result(
                "REST API使用(特殊)",
                True,
                f"{len(special_usage)}个特殊用途API保留,共{total_special}次调用"
            )
        else:
            self.add_result(
                "REST API使用(特殊)",
                True,
                "无特殊用途API"
            )

    def verify_test_coverage(self):
        """验证测试覆盖"""
        print("\n[4/4] 验证测试覆盖...")

        # 检查GraphQL测试
        gql_test_dir = self.project_root / "backend" / "test" / "unit" / "gql_api"
        if gql_test_dir.exists():
            test_files = list(gql_test_dir.glob("test_*.py"))
            if len(test_files) >= 3:
                self.add_result(
                    "GraphQL测试",
                    True,
                    f"测试文件充足 ({len(test_files)}个)"
                )
            else:
                self.add_result(
                    "GraphQL测试",
                    False,
                    f"测试文件不足 ({len(test_files)}个)"
                )
        else:
            self.add_result("GraphQL测试", False, "测试目录不存在")

        # 检查迁移测试脚本
        migration_test = self.project_root / "scripts" / "test_graphql_migration.py"
        if migration_test.exists():
            self.add_result("迁移测试脚本", True, "测试脚本已创建")
        else:
            self.add_result("迁移测试脚本", False, "测试脚本不存在")

    def add_result(self, check_name: str, passed: bool, message: str):
        """添加验证结果"""
        self.verification_results.append({
            'name': check_name,
            'passed': passed,
            'message': message
        })

    def print_results(self):
        """输出验证结果"""
        print("\n" + "="*60)
        print("验证结果")
        print("="*60)

        passed_count = sum(1 for r in self.verification_results if r['passed'])
        total_count = len(self.verification_results)

        for result in self.verification_results:
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            print(f"\n{status} - {result['name']}")
            print(f"  {result['message']}")

        print("\n" + "-"*60)
        print(f"总计: {passed_count}/{total_count} 通过")
        print("-"*60)

        # 移除建议
        if passed_count == total_count:
            print("\n✅ 所有验证通过! 可以安全移除REST API")
            print("\n移除步骤:")
            print("1. 执行REST API移除脚本")
            print("2. 更新API文档")
            print("3. 通知相关用户")
            print("4. 监控系统稳定性")
        else:
            print("\n⚠️  部分验证失败,请先完成以下工作:")
            failed_checks = [r for r in self.verification_results if not r['passed']]
            for i, check in enumerate(failed_checks, 1):
                print(f"{i}. {check['name']}: {check['message']}")

    def generate_removal_checklist(self):
        """生成移除检查清单"""
        checklist_file = self.project_root / "docs" / "api" / "REST_API_REMOVAL_CHECKLIST.md"

        passed_count = sum(1 for r in self.verification_results if r['passed'])
        total_count = len(self.verification_results)

        with open(checklist_file, 'w', encoding='utf-8') as f:
            f.write("# REST API移除检查清单\n\n")
            f.write(f"**验证时间**: {self._get_current_time()}\n\n")
            f.write(f"**验证结果**: {passed_count}/{total_count} 通过\n\n")

            f.write("## 验证项目\n\n")
            for result in self.verification_results:
                status = "✅" if result['passed'] else "❌"
                f.write(f"- {status} {result['name']}: {result['message']}\n")

            f.write("\n## 移除前检查\n\n")
            f.write("### 功能验证\n")
            f.write("- [ ] 所有GraphQL查询功能正常\n")
            f.write("- [ ] 所有GraphQL变更功能正常\n")
            f.write("- [ ] 前端组件已替换\n")
            f.write("- [ ] 功能测试通过\n")
            f.write("- [ ] 性能测试达标\n\n")

            f.write("### 数据验证\n")
            f.write("- [ ] 数据一致性验证\n")
            f.write("- [ ] 缓存策略验证\n")
            f.write("- [ ] 错误处理验证\n\n")

            f.write("### 用户验证\n")
            f.write("- [ ] 用户验收测试通过\n")
            f.write("- [ ] 用户文档已更新\n")
            f.write("- [ ] 用户已通知\n\n")

            f.write("### 技术验证\n")
            f.write("- [ ] 监控系统就绪\n")
            f.write("- [ ] 回滚方案准备\n")
            f.write("- [ ] 应急预案制定\n\n")

            f.write("## 移除执行\n\n")
            f.write("### 阶段1: 低风险API\n")
            f.write("- [ ] dashboard.py\n")
            f.write("- [ ] templates.py\n")
            f.write("- [ ] nodes.py\n\n")

            f.write("### 阶段2: 中风险API\n")
            f.write("- [ ] games.py (需前端迁移完成)\n")
            f.write("- [ ] events.py (需前端迁移完成)\n")
            f.write("- [ ] parameters.py (需前端迁移完成)\n")
            f.write("- [ ] categories.py (需前端迁移完成)\n\n")

            f.write("### 阶段3: 特殊用途API\n")
            f.write("- [ ] 评估是否移除\n")
            f.write("- [ ] 如保留,更新文档说明\n\n")

            if passed_count == total_count:
                f.write("## ✅ 验证通过,可以执行移除\n")
            else:
                f.write("## ⚠️ 验证未通过,请先完成上述检查项\n")

        print(f"\n✅ 移除检查清单已生成: {checklist_file}")

    def _get_current_time(self):
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def main():
    verifier = RESTAPIMigrationVerifier()
    verifier.verify_all()
    verifier.generate_removal_checklist()


if __name__ == '__main__':
    main()
