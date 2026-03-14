"""
HQL V2 核心服务使用示例

演示如何使用完全独立的HQL生成核心服务
"""

import sys
from pathlib import Path

# 添加hql_v2到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.hql.core.generator import HQLGenerator
from backend.services.hql.models.event import Condition, Event, Field


def example_1_simple_hql():
    """示例1: 生成简单HQL"""
    print("=" * 60)
    print("示例1: 生成简单HQL")
    print("=" * 60)

    generator = HQLGenerator()

    # 创建事件
    event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")

    # 创建字段
    fields = [
        Field(name="ds", type="base"),
        Field(name="role_id", type="base"),
        Field(name="account_id", type="base"),
        Field(name="utdid", type="base"),
    ]

    # 生成HQL
    hql = generator.generate(events=[event], fields=fields, conditions=[])

    print(hql)
    print()


def example_2_with_param_fields():
    """示例2: 包含参数字段"""
    print("=" * 60)
    print("示例2: 包含参数字段")
    print("=" * 60)

    generator = HQLGenerator()

    event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")

    fields = [
        Field(name="ds", type="base"),
        Field(name="role_id", type="base"),
        Field(name="zone_id", type="param", json_path="$.zone_id", alias="zone"),
        Field(name="level", type="param", json_path="$.level", alias="player_level"),
    ]

    hql = generator.generate(events=[event], fields=fields, conditions=[])

    print(hql)
    print()


def example_3_with_conditions():
    """示例3: 包含WHERE条件"""
    print("=" * 60)
    print("示例3: 包含WHERE条件")
    print("=" * 60)

    generator = HQLGenerator()

    event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")

    fields = [
        Field(name="ds", type="base"),
        Field(name="role_id", type="base"),
        Field(name="level", type="param", json_path="$.level"),
    ]

    conditions = [
        Condition(field="level", operator=">", value=10),
        Condition(field="zone_id", operator="=", value=1),
    ]

    hql = generator.generate(events=[event], fields=fields, conditions=conditions)

    print(hql)
    print()


def example_4_with_aggregates():
    """示例4: 包含聚合函数"""
    print("=" * 60)
    print("示例4: 包含聚合函数")
    print("=" * 60)

    generator = HQLGenerator()

    event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")

    fields = [
        Field(name="ds", type="base"),
        Field(name="role_id", type="base", aggregate_func="COUNT", alias="login_count"),
        Field(
            name="level", type="param", json_path="$.level", aggregate_func="AVG", alias="avg_level"
        ),
    ]

    hql = generator.generate(events=[event], fields=fields, conditions=[])

    print(hql)
    print()


def example_5_debug_mode():
    """示例5: 调试模式"""
    print("=" * 60)
    print("示例5: 调试模式")
    print("=" * 60)

    from backend.services.hql.core.generator import DebuggableHQLGenerator

    generator = DebuggableHQLGenerator()

    event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")

    fields = [
        Field(name="role_id", type="base"),
        Field(name="zone_id", type="param", json_path="$.zone_id"),
    ]

    conditions = [Condition(field="zone_id", operator="=", value=1)]

    # 使用debug模式生成
    result = generator.generate(
        events=[event], fields=fields, conditions=conditions, debug=True  # 启用调试模式
    )

    # 打印调试信息
    print("调试跟踪:")
    print(f"事件: {result['events']}")
    print(f"字段: {result['fields']}")
    print(f"条件: {result['conditions']}")
    print("\n生成步骤:")
    for step in result["steps"]:
        print(f"  - {step['step']}: {step.get('result', '')}")
    print("\n最终HQL:")
    print(result["final_hql"])
    print()


if __name__ == "__main__":
    print("\n")
    print("🚀 HQL V2 核心服务使用示例")
    print("=" * 60)
    print()

    # 运行所有示例
    example_1_simple_hql()
    example_2_with_param_fields()
    example_3_with_conditions()
    example_4_with_aggregates()
    example_5_debug_mode()

    print("=" * 60)
    print("✅ 所有示例运行完成！")
    print("=" * 60)
