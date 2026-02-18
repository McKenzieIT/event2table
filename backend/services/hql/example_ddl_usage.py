"""
DDL Generator Example Usage

演示如何使用DDL生成器生成Hive DDL语句
"""

from backend.services.hql.models.event import Field
from backend.services.hql.core.ddl_generator import DDLGenerator


def example_create_table():
    """示例：生成CREATE TABLE语句"""
    print("=" * 60)
    print("Example 1: CREATE TABLE for Login Event")
    print("=" * 60)

    generator = DDLGenerator()

    # 定义字段
    fields = [
        Field(name="ds", type="base"),
        Field(name="role_id", type="base"),
        Field(name="account_id", type="base"),
        Field(name="zone_id", type="param", json_path="$.zoneId"),
        Field(name="level", type="param", json_path="$.level"),
        Field(name="login_time", type="base"),
    ]

    # 生成DDL
    ddl = generator.generate_create_table(
        table_name="dwd.v_dwd_10000147_login_di",
        fields=fields,
        options={
            "comment": "Login event DWD table for game 10000147",
            "stored_as": "ORC",
        },
    )

    print(ddl)
    print()


def example_alter_table_add_columns():
    """示例：生成ADD COLUMNS语句"""
    print("=" * 60)
    print("Example 2: ALTER TABLE ADD COLUMNS")
    print("=" * 60)

    generator = DDLGenerator()

    # 新增字段
    new_fields = [
        Field(name="device_type", type="base"),
        Field(name="os_version", type="base"),
    ]

    # 生成DDL
    ddl = generator.generate_add_columns(
        table_name="dwd.v_dwd_10000147_login_di",
        fields=new_fields,
    )

    print(ddl)
    print()


def example_alter_table_replace_columns():
    """示例：生成REPLACE COLUMNS语句"""
    print("=" * 60)
    print("Example 3: ALTER TABLE REPLACE COLUMNS")
    print("=" * 60)

    generator = DDLGenerator()

    # 完整字段列表
    all_fields = [
        Field(name="ds", type="base"),
        Field(name="role_id", type="base"),
        Field(name="account_id", type="base"),
        Field(name="zone_id", type="base"),
        Field(name="level", type="base"),
        Field(name="device_type", type="base"),
    ]

    # 生成DDL
    ddl = generator.generate_replace_columns(
        table_name="dwd.v_dwd_10000147_login_di",
        fields=all_fields,
    )

    print(ddl)
    print()


def example_custom_field_types():
    """示例：自定义字段类型映射"""
    print("=" * 60)
    print("Example 4: Custom Field Type Mapping")
    print("=" * 60)

    generator = DDLGenerator()

    # 设置自定义类型映射
    generator.set_field_type_mapping("score", "INT")
    generator.set_field_type_mapping("ratio", "DOUBLE")

    # 使用自定义映射
    fields = [
        Field(name="game_score", type="base"),
        Field(name="win_ratio", type="base"),
        Field(name="custom_field", type="base"),
    ]

    ddl = generator.generate_create_table(
        table_name="dwd.test_table",
        fields=fields,
    )

    print(ddl)
    print()


def example_external_table():
    """示例：生成外部表DDL"""
    print("=" * 60)
    print("Example 5: CREATE EXTERNAL TABLE")
    print("=" * 60)

    generator = DDLGenerator()

    fields = [
        Field(name="role_id", type="base"),
        Field(name="event_data", type="base"),
    ]

    ddl = generator.generate_create_table(
        table_name="ods.external_events",
        fields=fields,
        options={
            "external": True,
            "location": "/data/warehouse/ods/external_events",
            "comment": "External event table",
            "stored_as": "PARQUET",
        },
    )

    print(ddl)
    print()


def example_field_type_inference():
    """示例：字段类型推断演示"""
    print("=" * 60)
    print("Example 6: Field Type Inference Demo")
    print("=" * 60)

    generator = DDLGenerator()

    # 各种类型的字段
    fields = [
        Field(name="user_id", type="base"),  # BIGINT (contains _id)
        Field(name="login_count", type="base"),  # BIGINT (contains count)
        Field(name="player_level", type="base"),  # INT (contains level)
        Field(name="total_amount", type="base"),  # DECIMAL (contains amount)
        Field(name="price", type="base"),  # DECIMAL (contains price)
        Field(name="is_active", type="base"),  # BOOLEAN (starts with is_)
        Field(name="has_permission", type="base"),  # BOOLEAN (starts with has_)
        Field(name="event_time", type="base"),  # TIMESTAMP (contains time)
        Field(name="birth_date", type="base"),  # DATE (contains date)
        Field(name="unknown_field", type="base"),  # STRING (default)
    ]

    print("\nField Type Inference Results:")
    print("-" * 60)
    for field in fields:
        hive_type = generator._infer_hive_type(field)
        print(f"{field.name:20} -> {hive_type}")

    print()


if __name__ == "__main__":
    # 运行所有示例
    example_create_table()
    example_alter_table_add_columns()
    example_alter_table_replace_columns()
    example_custom_field_types()
    example_external_table()
    example_field_type_inference()

    print("=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)
