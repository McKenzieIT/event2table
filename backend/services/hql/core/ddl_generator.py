"""
DDL Generator - DDL语句生成器

负责生成Hive DDL语句（CREATE TABLE, ALTER TABLE等）
完全遵循HQL V2架构模式，无框架依赖
"""

from typing import List, Dict, Any, Optional
from ..models.event import Field


class DDLGenerator:
    """
    DDL生成器

    生成Hive DDL语句，支持：
    - CREATE TABLE (with ORC storage and partitioning)
    - ALTER TABLE (ADD/REPLACE columns)

    Examples:
        >>> from backend.services.hql.models.event import Field
        >>> from backend.services.hql.core.ddl_generator import DDLGenerator
        >>>
        >>> generator = DDLGenerator()
        >>> fields = [
        ...     Field(name="role_id", type="base"),
        ...     Field(name="zone_id", type="param", json_path="$.zone_id")
        ... ]
        >>> ddl = generator.generate_create_table("dwd.dwd_login", fields)
        >>> print(ddl)
    """

    # Hive数据类型映射
    # 默认所有字段都是STRING，除非明确指定其他类型
    HIVE_TYPE_MAPPING = {
        "STRING": "STRING",
        "BIGINT": "BIGINT",
        "INT": "INT",
        "DOUBLE": "DOUBLE",
        "FLOAT": "FLOAT",
        "BOOLEAN": "BOOLEAN",
        "TIMESTAMP": "TIMESTAMP",
        "DECIMAL": "DECIMAL(10,2)",
        "DATE": "DATE",
        "ARRAY": "ARRAY<STRING>",
        "MAP": "MAP<STRING, STRING>",
    }

    # 默认字段类型（如果未指定）
    DEFAULT_FIELD_TYPE = "STRING"

    # 分区字段配置
    PARTITION_FIELD = "ds"
    PARTITION_FIELD_TYPE = "STRING"

    # 存储格式配置
    STORAGE_FORMAT = "ORC"
    FILE_FORMAT = "ORC"

    def __init__(self):
        """初始化DDL生成器"""
        self._init_field_type_mappings()

    def _init_field_type_mappings(self):
        """
        初始化字段类型映射

        可以根据业务需求扩展映射规则
        """
        # 预留扩展点：可以根据字段名推断类型
        self.field_name_type_hints = {
            "id": "BIGINT",
            "count": "BIGINT",
            "amount": "DECIMAL(10,2)",
            "price": "DECIMAL(10,2)",
            "level": "INT",
            "score": "INT",
            "time": "TIMESTAMP",
            "date": "DATE",
            "flag": "BOOLEAN",
            "is_": "BOOLEAN",  # 前缀匹配
            "has_": "BOOLEAN",  # 前缀匹配
        }

    def generate_create_table(
        self,
        table_name: str,
        fields: List[Field],
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        生成CREATE TABLE语句

        Args:
            table_name: 目标表名（如: dwd.v_dwd_10000147_login_di）
            fields: 字段列表
            options: 额外选项
                - external: 是否为外部表（默认False）
                - stored_as: 存储格式（默认ORC）
                - partition_by: 分区字段（默认ds）
                - comment: 表注释（可选）
                - location: 表位置（可选，用于外部表）

        Returns:
            str: CREATE TABLE DDL语句

        Examples:
            >>> generator = DDLGenerator()
            >>> fields = [Field(name="role_id", type="base")]
            >>> ddl = generator.generate_create_table("dwd.table", fields)
            >>> print(ddl)
            CREATE TABLE IF NOT EXISTS dwd.table (
              `role_id` STRING COMMENT 'role_id'
            )
            PARTITIONED BY (ds STRING)
            STORED AS ORC;
        """
        if not table_name:
            raise ValueError("table_name cannot be empty")

        if not fields:
            raise ValueError("fields cannot be empty")

        options = options or {}

        # 验证表名
        self._validate_table_name(table_name)

        # 构建字段定义
        field_definitions = self._build_field_definitions(fields)

        # 获取选项
        external = options.get("external", False)
        stored_as = options.get("stored_as", self.STORAGE_FORMAT)
        partition_by = options.get("partition_by", self.PARTITION_FIELD)
        comment = options.get("comment")
        location = options.get("location")

        # 构建DDL
        ddl_parts = []

        # CREATE [EXTERNAL] TABLE
        create_clause = "CREATE EXTERNAL TABLE" if external else "CREATE TABLE"
        ddl_parts.append(f"{create_clause} IF NOT EXISTS {table_name}")

        # 字段定义
        field_defs = ",\n  ".join(field_definitions)
        ddl_parts.append(f"(\n  {field_defs}\n)")

        # 分区定义
        partition_type = self.PARTITION_FIELD_TYPE
        ddl_parts.append(f"PARTITIONED BY ({partition_by} {partition_type})")

        # 表注释
        if comment:
            ddl_parts.append(f"COMMENT '{self._escape_string(comment)}'")

        # 存储格式
        ddl_parts.append(f"STORED AS {stored_as}")

        # 外部表位置
        if location:
            ddl_parts.append(f"LOCATION '{location}'")

        return "\n".join(ddl_parts) + ";"

    def generate_alter_table(
        self,
        table_name: str,
        actions: List[str],
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        生成ALTER TABLE语句

        Args:
            table_name: 目标表名
            actions: ALTER操作列表（如: ADD COLUMN, REPLACE COLUMNS）
            options: 额外选项

        Returns:
            str: ALTER TABLE DDL语句

        Examples:
            >>> generator = DDLGenerator()
            >>> actions = ["ADD COLUMN (new_col STRING)"]
            >>> ddl = generator.generate_alter_table("dwd.table", actions)
            >>> print(ddl)
            ALTER TABLE dwd.table ADD COLUMN (new_col STRING);
        """
        if not table_name:
            raise ValueError("table_name cannot be empty")

        if not actions:
            raise ValueError("actions cannot be empty")

        options = options or {}

        # 验证表名
        self._validate_table_name(table_name)

        # 构建ALTER语句
        alter_statements = []
        for action in actions:
            ddl = f"ALTER TABLE {table_name} {action};"
            alter_statements.append(ddl)

        return "\n".join(alter_statements)

    def generate_add_columns(
        self,
        table_name: str,
        fields: List[Field],
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        生成ADD COLUMNS语句（ALTER TABLE的便捷方法）

        Args:
            table_name: 目标表名
            fields: 要添加的字段列表
            options: 额外选项

        Returns:
            str: ALTER TABLE ... ADD COLUMNS DDL语句

        Examples:
            >>> generator = DDLGenerator()
            >>> fields = [Field(name="new_col", type="base")]
            >>> ddl = generator.generate_add_columns("dwd.table", fields)
            >>> print(ddl)
            ALTER TABLE dwd.table ADD COLUMNS (
              `new_col` STRING COMMENT 'new_col'
            );
        """
        if not fields:
            raise ValueError("fields cannot be empty")

        # 构建字段定义
        field_definitions = self._build_field_definitions(fields)

        # 构建ADD COLUMNS子句
        columns_clause = ",\n  ".join(field_definitions)
        action = f"ADD COLUMNS (\n  {columns_clause}\n)"

        return self.generate_alter_table(table_name, [action], options)

    def generate_replace_columns(
        self,
        table_name: str,
        fields: List[Field],
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        生成REPLACE COLUMNS语句（ALTER TABLE的便捷方法）

        Args:
            table_name: 目标表名
            fields: 替换后的完整字段列表
            options: 额外选项

        Returns:
            str: ALTER TABLE ... REPLACE COLUMNS DDL语句

        Examples:
            >>> generator = DDLGenerator()
            >>> fields = [Field(name="role_id", type="base"), Field(name="zone_id", type="base")]
            >>> ddl = generator.generate_replace_columns("dwd.table", fields)
            >>> print(ddl)
            ALTER TABLE dwd.table REPLACE COLUMNS (
              `role_id` STRING COMMENT 'role_id',
              `zone_id` STRING COMMENT 'zone_id'
            );
        """
        if not fields:
            raise ValueError("fields cannot be empty")

        # 构建字段定义
        field_definitions = self._build_field_definitions(fields)

        # 构建REPLACE COLUMNS子句
        columns_clause = ",\n  ".join(field_definitions)
        action = f"REPLACE COLUMNS (\n  {columns_clause}\n)"

        return self.generate_alter_table(table_name, [action], options)

    def _build_field_definitions(self, fields: List[Field]) -> List[str]:
        """
        构建字段定义列表

        Args:
            fields: 字段列表

        Returns:
            List[str]: 字段定义SQL列表

        Examples:
            >>> generator = DDLGenerator()
            >>> field = Field(name="role_id", type="base")
            >>> defs = generator._build_field_definitions([field])
            >>> defs
            ['`role_id` STRING COMMENT \\'role_id\\'']
        """
        definitions = []

        for field in fields:
            # 推断Hive数据类型
            hive_type = self._infer_hive_type(field)

            # 转义字段名
            field_name = self._escape_identifier(field.name)

            # 构建字段定义
            field_def = f"{field_name} {hive_type} COMMENT '{field.name}'"

            definitions.append(field_def)

        return definitions

    def _infer_hive_type(self, field: Field) -> str:
        """
        推断字段的Hive数据类型

        Args:
            field: 字段对象

        Returns:
            str: Hive数据类型

        Examples:
            >>> generator = DDLGenerator()
            >>> field = Field(name="role_count", type="base")
            >>> generator._infer_hive_type(field)
            'BIGINT'
        """
        # 如果字段有明确的类型指定（通过自定义属性），使用它
        if hasattr(field, "hive_type") and field.hive_type:
            return field.hive_type

        # 根据字段名推断类型
        field_name_lower = field.name.lower()

        for hint, target_type in self.field_name_type_hints.items():
            if hint.endswith("_"):
                # 前缀匹配（如: is_active, has_permission）
                if field_name_lower.startswith(hint):
                    return target_type
            else:
                # 完全匹配或包含
                if hint in field_name_lower:
                    return target_type

        # 默认使用STRING类型
        return self.DEFAULT_FIELD_TYPE

    def _validate_table_name(self, table_name: str) -> bool:
        """
        验证表名是否合法

        Args:
            table_name: 表名

        Returns:
            bool: 验证通过返回True

        Raises:
            ValueError: 表名不合法
        """
        if not table_name:
            raise ValueError("table_name cannot be empty")

        # 表名格式：database.table 或 table
        # 只允许字母、数字、下划线和点
        import re

        if not re.match(
            r"^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$", table_name
        ):
            raise ValueError(
                f"Invalid table_name: {table_name}. "
                "Table name must match pattern: [database.]table_name"
            )

        return True

    def _escape_identifier(self, identifier: str) -> str:
        """
        转义SQL标识符（使用反引号）

        Args:
            identifier: 标识符

        Returns:
            str: 转义后的标识符
        """
        if not identifier:
            raise ValueError("identifier cannot be empty")

        # 转义反引号
        escaped = identifier.replace("`", "``")
        return f"`{escaped}`"

    def _escape_string(self, value: str) -> str:
        """
        转义字符串值（用于注释）

        Args:
            value: 字符串值

        Returns:
            str: 转义后的字符串
        """
        if not value:
            return ""

        # 转义单引号
        return value.replace("'", "''")

    def set_field_type_mapping(self, field_name_pattern: str, hive_type: str):
        """
        设置字段类型映射（扩展点）

        Args:
            field_name_pattern: 字段名模式（如: "amount", "is_", "price"）
            hive_type: Hive数据类型（如: "DECIMAL(10,2)", "BOOLEAN"）

        Examples:
            >>> generator = DDLGenerator()
            >>> generator.set_field_type_mapping("score", "INT")
            >>> generator.set_field_type_mapping("ratio", "DOUBLE")
        """
        self.field_name_type_hints[field_name_pattern] = hive_type

    def set_default_field_type(self, hive_type: str):
        """
        设置默认字段类型

        Args:
            hive_type: Hive数据类型（如: "STRING", "BIGINT"）

        Examples:
            >>> generator = DDLGenerator()
            >>> generator.set_default_field_type("VARCHAR(255)")
        """
        if hive_type not in self.HIVE_TYPE_MAPPING.values():
            # 允许自定义类型，但发出警告
            import warnings

            warnings.warn(
                f"Custom hive_type '{hive_type}' is not a standard Hive type. "
                f"Standard types: {list(self.HIVE_TYPE_MAPPING.values())}"
            )

        self.DEFAULT_FIELD_TYPE = hive_type
