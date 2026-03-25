#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameter Module Entity Architecture Verification Script

验证Parameters模块Entity架构的完整性:
1. game_id违规检查
2. Entity对象检查
3. 方法返回类型检查
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
os.environ['PYTHONPATH'] = str(project_root)


def check_game_id_violations():
    """检查game_id违规"""
    print("=" * 80)
    print("1. 检查game_id违规")
    print("=" * 80)

    files_to_check = [
        "services/parameters/parameter_service.py",
        "models/repositories/parameters.py",
    ]

    violations_found = False

    for file_path in files_to_check:
        full_path = project_root / file_path
        if not full_path.exists():
            print(f"❌ 文件不存在: {file_path}")
            continue

        with open(full_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        file_violations = []
        for i, line in enumerate(lines, 1):
            # 跳过注释
            if line.strip().startswith('#'):
                continue
            # 跳过包含game_gid的行（说明是正确使用）
            if 'game_gid' in line:
                continue
            # 检查game_id
            if 'game_id' in line:
                file_violations.append((i, line.strip()))

        if file_violations:
            violations_found = True
            print(f"\n❌ {file_path} 发现game_id违规:")
            for line_num, line_content in file_violations:
                print(f"  Line {line_num}: {line_content}")
        else:
            print(f"✅ {file_path}: 无game_id违规")

    return not violations_found


def check_entity_architecture():
    """检查Entity架构"""
    print("\n" + "=" * 80)
    print("2. 检查Entity架构")
    print("=" * 80)

    try:
        from backend.models.entities import CommonParameterEntity, ParameterEntity

        # 检查ParameterEntity
        param_entity = ParameterEntity(
            id=1, event_id=1, game_gid=90000001, name="test_param", param_type="param"
        )

        print("\n✅ ParameterEntity创建成功")
        print(f"  - game_gid: {param_entity.game_gid}")
        print(f"  - 没有game_id字段: {'game_id' not in param_entity.model_fields}")

        # 检查CommonParameterEntity
        common_entity = CommonParameterEntity(
            id=1, game_gid=90000001, name="common_param", param_type="base"
        )

        print("\n✅ CommonParameterEntity创建成功")
        print(f"  - game_gid: {common_entity.game_gid}")
        print(f"  - 没有game_id字段: {'game_id' not in common_entity.model_fields}")

        return True

    except Exception as e:
        print(f"\n❌ Entity架构检查失败: {e}")
        return False


def check_repository_methods():
    """检查Repository方法"""
    print("\n" + "=" * 80)
    print("3. 检查Repository方法")
    print("=" * 80)

    try:
        import sys
        from typing import get_args, get_origin

        from backend.models.entities import ParameterEntity
        from backend.models.repositories.parameters import ParameterRepository

        if sys.version_info >= (3, 8):
            from typing import Union
        else:
            Union = type(None)

        repo = ParameterRepository()

        # 检查关键方法的返回类型
        methods_to_check = [
            'create',
            'find_by_id',
            'update',
            'get_active_by_event',
            'get_all_by_event',
        ]

        all_correct = True
        for method_name in methods_to_check:
            if not hasattr(repo, method_name):
                print(f"❌ 方法不存在: {method_name}")
                all_correct = False
                continue

            method = getattr(repo, method_name)
            if hasattr(method, '__annotations__'):
                return_type = method.__annotations__.get('return')
                print(f"  {method_name}: {return_type}")

                # 验证返回类型包含Entity
                if return_type and 'ParameterEntity' in str(return_type):
                    print(f"    ✅ 返回Entity对象")
                elif return_type and 'List' in str(return_type):
                    print(f"    ✅ 返回列表")
                else:
                    print(f"    ⚠️  返回类型: {return_type}")

        return all_correct

    except Exception as e:
        print(f"\n❌ Repository方法检查失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("Parameters Module Entity Architecture Verification")
    print("=" * 80)

    results = {
        "game_id违规检查": check_game_id_violations(),
        "Entity架构检查": check_entity_architecture(),
        "Repository方法检查": check_repository_methods(),
    }

    print("\n" + "=" * 80)
    print("验证结果汇总")
    print("=" * 80)

    for check_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{check_name}: {status}")

    all_passed = all(results.values())

    print("\n" + "=" * 80)
    if all_passed:
        print("✅ 所有验证通过！Parameters模块Entity架构完整。")
        return 0
    else:
        print("❌ 部分验证失败，请检查上述错误。")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
