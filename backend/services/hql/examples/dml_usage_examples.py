"""
DML Generator 使用示例

演示如何使用DML生成器生成INSERT OVERWRITE语句
"""

from backend.services.hql.core.dml_generator import (
    DMLGenerator,
    DMLBuilderFactory,
    generate_insert_overwrite
)
from backend.services.hql.core.generator import HQLGenerator
from backend.services.hql.models.event import Event, Field, FieldType


def example_1_basic_insert_overwrite():
    """示例1: 基本INSERT OVERWRITE语句"""
    print("=" * 80)
    print("示例1: 基本INSERT OVERWRITE语句")
    print("=" * 80)

    generator = DMLGenerator()

    dml = generator.generate_insert_overwrite(
        target_table="dwd.v_dwd_10000147_login_di",
        source_query="SELECT role_id, account_id FROM ods_table",
        partition_ds="20260217"
    )

    print(dml)
    print()


def example_2_with_hql_generator():
    """示例2: 与HQL生成器配合使用"""
    print("=" * 80)
    print("示例2: 与HQL生成器配合使用（完整ETL流程）")
    print("=" * 80)

    # 1. 使用HQL生成器创建SELECT查询
    hql_generator = HQLGenerator()

    event = Event(
        name="login",
        table_name="ieu_ods.ods_10000147_all_view"
    )

    fields = [
        Field(name="ds", type=FieldType.BASE),
        Field(name="role_id", type=FieldType.BASE),
        Field(name="account_id", type=FieldType.BASE),
        Field(name="zone_id", type=FieldType.PARAM, json_path="$.zoneId"),
    ]

    select_query = hql_generator.generate(
        events=[event],
        fields=fields,
        conditions=[]
    )

    print("步骤1: 生成的SELECT查询")
    print("-" * 80)
    print(select_query)
    print()

    # 2. 使用DML生成器创建INSERT OVERWRITE语句
    dml_generator = DMLGenerator()

    dml = dml_generator.generate_insert_overwrite(
        target_table="dwd.v_dwd_10000147_login_di",
        source_query=select_query,
        partition_ds="${bizdate}",
        include_comments=True
    )

    print("步骤2: 生成的INSERT OVERWRITE语句")
    print("-" * 80)
    print(dml)
    print()


def example_3_factory_pattern():
    """示例3: 使用工厂模式"""
    print("=" * 80)
    print("示例3: 使用工厂模式（标准ETL流程）")
    print("=" * 80)

    # 使用工厂方法快速生成标准ETL DML
    dml = DMLBuilderFactory.create_etl_dml(
        dwd_prefix="dwd",
        game_gid=10000147,
        event_name="purchase",
        source_query="SELECT role_id, amount FROM ods_purchase",
        partition_ds="20260217"
    )

    print(dml)
    print()


def example_4_export_to_directory():
    """示例4: 导出到文件系统"""
    print("=" * 80)
    print("示例4: 导出到HDFS文件系统（PARQUET格式）")
    print("=" * 80)

    generator = DMLGenerator()

    dml = generator.generate_insert_overwrite_directory(
        target_directory="hdfs:///data/export/20260217/login_events",
        source_query="SELECT * FROM dwd.v_dwd_10000147_login_di",
        file_format="PARQUET",
        field_delim=","
    )

    print(dml)
    print()


def example_5_batch_insert():
    """示例5: 批量插入（UNION ALL）"""
    print("=" * 80)
    print("示例5: 批量插入多个事件（UNION ALL）")
    print("=" * 80)

    queries = [
        "SELECT role_id, 'login' AS event_type FROM ods_login WHERE ds = '${bizdate}'",
        "SELECT role_id, 'logout' AS event_type FROM ods_logout WHERE ds = '${bizdate}'",
        "SELECT role_id, 'purchase' AS event_type FROM ods_purchase WHERE ds = '${bizdate}'"
    ]

    dml = DMLBuilderFactory.create_batch_insert(
        target_table="dwd.v_dwd_10000147_all_events_di",
        source_queries=queries,
        partition_ds="20260217"
    )

    print(dml)
    print()


def example_6_convenience_function():
    """示例6: 使用便捷函数"""
    print("=" * 80)
    print("示例6: 使用便捷函数")
    print("=" * 80)

    # 直接使用便捷函数，无需创建生成器实例
    dml = generate_insert_overwrite(
        target_table="dwd.v_dwd_10000147_custom_di",
        source_query="SELECT * FROM staging_table",
        partition_ds="${ds}",
        include_comments=False
    )

    print(dml)
    print()


def example_7_real_world_scenario():
    """示例7: 真实场景 - 完整的数据抽取加载流程"""
    print("=" * 80)
    print("示例7: 真实场景 - 完整的ETL流程")
    print("=" * 80)

    # 1. 定义源表和目标表
    source_table = "ieu_ods.ods_10000147_all_view"
    target_table = "dwd.v_dwd_10000147_login_di"

    # 2. 生成复杂的SELECT查询
    hql_generator = HQLGenerator()

    event = Event(name="login", table_name=source_table)

    fields = [
        Field(name="ds", type=FieldType.BASE),
        Field(name="role_id", type=FieldType.BASE),
        Field(name="account_id", type=FieldType.BASE),
        Field(name="utdid", type=FieldType.BASE),
        Field(name="envinfo", type=FieldType.BASE),
        Field(name="tm", type=FieldType.BASE),
        Field(name="ts", type=FieldType.BASE),
        Field(name="zone_id", type=FieldType.PARAM, json_path="$.zoneId"),
        Field(name="level", type=FieldType.PARAM, json_path="$.level"),
        Field(name="ip", type=FieldType.PARAM, json_path="$.ip"),
    ]

    select_query = hql_generator.generate(
        events=[event],
        fields=fields,
        conditions=[],
        mode="single"
    )

    # 3. 生成DML语句
    dml_generator = DMLGenerator()

    dml = dml_generator.generate_insert_overwrite(
        target_table=target_table,
        source_query=select_query,
        partition_ds="${bizdate}",
        include_comments=True
    )

    print("完整ETL流程: 从ODS层抽取数据到DWD层")
    print("-" * 80)
    print(f"源表: {source_table}")
    print(f"目标表: {target_table}")
    print("分区: ds='${bizdate}'")
    print("-" * 80)
    print(dml)
    print()


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "DML Generator 使用示例集" + " " * 35 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    # 运行所有示例
    example_1_basic_insert_overwrite()
    example_2_with_hql_generator()
    example_3_factory_pattern()
    example_4_export_to_directory()
    example_5_batch_insert()
    example_6_convenience_function()
    example_7_real_world_scenario()

    print("=" * 80)
    print("所有示例运行完成！")
    print("=" * 80)
