#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL优化API功能测试脚本

测试SQL优化模块的API功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_sql_optimizer_module():
    """测试SQL优化模块加载"""
    print("=" * 60)
    print("测试1: SQL优化模块加载")
    print("=" * 60)

    try:
        from backend.services.sql_optimizer.optimizer import SQLOptimizer, OptimizationResult
        print("✓ SQL优化器模块加载成功")
        print(f"  - SQLOptimizer: {SQLOptimizer}")
        print(f"  - OptimizationResult: {OptimizationResult}")
    except Exception as e:
        print(f"✗ SQL优化器模块加载失败: {e}")
        return False

    return True


def test_parser():
    """测试HQL解析器"""
    print("\n" + "=" * 60)
    print("测试2: HQL解析器")
    print("=" * 60)

    try:
        from backend.services.sql_optimizer.parser import HQLParser

        # 测试简单的SELECT语句
        hql1 = "SELECT * FROM ods_order"
        parser1 = HQLParser(hql1)
        print(f"✓ 解析成功: {hql1}")
        print(f"  - 表数量: {len(parser1.tables)}")
        print(f"  - SELECT字段: {parser1.select_columns}")

        # 测试带WHERE的SELECT语句
        hql2 = "SELECT * FROM ods_order WHERE YEAR(ds) = 2025"
        parser2 = HQLParser(hql2)
        print(f"\n✓ 解析成功: {hql2}")
        print(f"  - WHERE条件: {len(parser2.where_conditions)}")
        print(f"  - 分区函数检测: {parser2.has_function_on_partition()}")

        # 测试SELECT *
        hql3 = "SELECT id, name FROM ods_order"
        parser3 = HQLParser(hql3)
        print(f"\n✓ 解析成功: {hql3}")
        print(f"  - SELECT字段: {parser3.select_columns}")
        print(f"  - SELECT *检测: {parser3.has_select_star()}")

    except Exception as e:
        print(f"✗ HQL解析器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def test_optimizer():
    """测试优化器"""
    print("\n" + "=" * 60)
    print("测试3: SQL优化器")
    print("=" * 60)

    try:
        from backend.services.sql_optimizer.optimizer import SQLOptimizer
        optimizer = SQLOptimizer()

        # 测试1: 需要优化的HQL
        hql1 = "SELECT * FROM ods_order WHERE YEAR(ds) = 2025"
        print(f"原始HQL: {hql1}")
        result1 = optimizer.optimize(hql1)
        print(f"✓ 优化完成")
        print(f"  - 应用的规则数: {len(result1.applied_rules)}")
        print(f"  - 建议的规则数: {len(result1.suggested_rules)}")
        if result1.applied_rules:
            print(f"  - 应用的规则:")
            for rule in result1.applied_rules:
                print(f"    • {rule['name']}: {rule['description']}")

        # 测试2: 不需要优化的HQL
        hql2 = "SELECT id, name FROM ods_order WHERE ds = '2025-01-15'"
        print(f"\n原始HQL: {hql2}")
        result2 = optimizer.optimize(hql2)
        print(f"✓ 优化完成")
        print(f"  - 应用的规则数: {len(result2.applied_rules)}")
        print(f"  - 建议的规则数: {len(result2.suggested_rules)}")

    except Exception as e:
        print(f"✗ 优化器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def test_empty_hql():
    """测试空HQL处理"""
    print("\n" + "=" * 60)
    print("测试4: 空HQL处理")
    print("=" * 60)

    try:
        from backend.services.sql_optimizer.optimizer import SQLOptimizer
        optimizer = SQLOptimizer()

        hql = ""
        print(f"原始HQL: '{hql}'")
        result = optimizer.optimize(hql)
        print(f"✓ 空HQL处理完成")
        print(f"  - 优化后HQL: '{result.optimized_hql}'")
        print(f"  - 应用规则数: {len(result.applied_rules)}")

    except Exception as e:
        print(f"✗ 空HQL测试失败: {e}")
        return False

    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("SQL优化模块功能测试")
    print("=" * 60)

    results = []

    # 运行所有测试
    results.append(("模块加载", test_sql_optimizer_module()))
    results.append(("HQL解析器", test_parser()))
    results.append(("SQL优化器", test_optimizer()))
    results.append(("空HQL处理", test_empty_hql()))

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name:20s} {status}")

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n✓ 所有测试通过！SQL优化模块功能正常。")
        return 0
    else:
        print("\n✗ 部分测试失败，请检查错误信息。")
        return 1


if __name__ == '__main__':
    sys.exit(main())
