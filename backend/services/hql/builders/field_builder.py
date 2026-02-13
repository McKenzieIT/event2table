"""
字段构建器

负责将抽象Field模型转换为SQL字段表达式
"""

import re
from typing import Optional
from ..models.event import Field, FieldType


class FieldBuilder:
    """
    字段SQL构建器

    支持4种字段类型：
    - base: 基础字段（如: role_id）
    - param: JSON参数字段（如: get_json_object(params, '$.zone_id')）
    - custom: 自定义表达式
    - fixed: 固定常量值
    """

    # 危险的SQL关键字（用于custom_expression验证）
    DANGEROUS_KEYWORDS = [
        "DROP",
        "DELETE",
        "TRUNCATE",
        "ALTER",
        "CREATE",
        "INSERT",
        "UPDATE",
        "EXEC",
        "EXECUTE",
        "SCRIPT",
        "--",
        "/*",
        "*/",
        ";",
        "xp_",
        "sp_",
    ]

    def _validate_identifier(self, identifier: str) -> bool:
        """
        验证标识符是否安全

        只允许字母、数字、下划线和$
        """
        if not identifier:
            return False
        return bool(re.match(r"^[a-zA-Z_][a-zA-Z0-9_$]*$", identifier))

    def _escape_identifier(self, identifier: str) -> str:
        """
        转义SQL标识符（使用反引号）

        防止SQL注入
        """
        if not self._validate_identifier(identifier):
            raise ValueError(f"Invalid identifier: {identifier}")

        # 转义反引号
        escaped = identifier.replace("`", "``")
        return f"`{escaped}`"

    def _validate_custom_expression(self, expression: str) -> bool:
        """
        验证自定义表达式是否安全

        防止SQL注入
        """
        if not expression:
            return False

        # 转换为大写进行检查
        expr_upper = expression.upper()

        # 检查危险关键字
        for keyword in self.DANGEROUS_KEYWORDS:
            if keyword in expr_upper:
                raise ValueError(
                    f"Dangerous SQL keyword '{keyword}' found in custom expression. "
                    f"This could be a SQL injection attempt."
                )

        # 检查多个语句（分号）
        if ";" in expression:
            raise ValueError(
                "Multiple statements detected in custom expression. "
                "Only single expressions are allowed."
            )

        # 检查注释标记
        if "--" in expression or "/*" in expression:
            raise ValueError(
                "SQL comments detected in custom expression. " "Comments are not allowed."
            )

        return True

    def build(self, field: Field, context: Optional[dict] = None) -> str:
        """
        构建字段SQL表达式

        Args:
            field: 抽象字段模型
            context: 上下文信息（可选）

        Returns:
            str: SQL字段表达式

        Examples:
            >>> builder = FieldBuilder()
            >>> field = Field(name="role_id", type="base")
            >>> builder.build(field)
            'role_id'

            >>> field = Field(name="zone_id", type="param", json_path="$.zone_id")
            >>> builder.build(field)
            'get_json_object(params, \'$.zone_id\') AS zone_id'
        """
        if field.type == FieldType.BASE.value:
            return self._build_base_field(field)
        elif field.type == FieldType.PARAM.value:
            return self._build_param_field(field)
        elif field.type == FieldType.CUSTOM.value:
            return self._build_custom_field(field)
        elif field.type == FieldType.FIXED.value:
            return self._build_fixed_field(field)
        else:
            raise ValueError(f"Unsupported field type: {field.type}")

    def _build_base_field(self, field: Field) -> str:
        """
        构建基础字段SQL

        Examples:
            role_id
            role_id AS role
            COUNT(role_id) AS role_count
        """
        # 转义字段名（防止SQL注入）
        sql = self._escape_identifier(field.name)

        # 聚合函数
        if field.aggregate_func:
            sql = f"{field.aggregate_func}({sql})"

        # 别名（转义）
        if field.alias:
            alias = self._escape_identifier(field.alias)
            sql = f"{sql} AS {alias}"

        return sql

    def _build_param_field(self, field: Field) -> str:
        """
        构建参数字段SQL（从JSON提取）

        Examples:
            get_json_object(params, '$.zone_id') AS zone_id
            CAST(get_json_object(params, '$.level') AS BIGINT) AS level
        """
        # 构建JSON提取表达式
        json_path = field.json_path if field.json_path.startswith("$") else f"$.{field.json_path}"
        sql = f"get_json_object(params, '{json_path}')"

        # 聚合函数
        if field.aggregate_func:
            # 可能需要类型转换
            sql = f"CAST({sql} AS STRING)"
            sql = f"{field.aggregate_func}({sql})"

        # 别名（必需，因为提取表达式很长）
        alias = field.alias or field.name
        alias_escaped = self._escape_identifier(alias)
        sql = f"{sql} AS {alias_escaped}"

        return sql

    def _build_custom_field(self, field: Field) -> str:
        """
        构建自定义字段SQL

        直接使用用户提供的自定义表达式
        """
        if not field.custom_expression:
            raise ValueError("custom field must have custom_expression")

        # 验证自定义表达式（防止SQL注入）
        self._validate_custom_expression(field.custom_expression)

        sql = field.custom_expression

        # 别名（转义）
        if field.alias:
            alias = self._escape_identifier(field.alias)
            sql = f"{sql} AS {alias}"

        return sql

    def _build_fixed_field(self, field: Field) -> str:
        """
        构建固定值字段SQL

        Examples:
            'login' AS event_type
            1 AS is_active
        """
        if field.fixed_value is None:
            raise ValueError("fixed field must have fixed_value")

        # 根据值类型决定是否加引号
        if isinstance(field.fixed_value, str):
            # 转义单引号
            value = field.fixed_value.replace("'", "''")
            sql = f"'{value}'"
        elif isinstance(field.fixed_value, bool):
            sql = "TRUE" if field.fixed_value else "FALSE"
        else:
            sql = str(field.fixed_value)

        # 别名（必需，转义）
        alias = field.alias or field.name
        alias_escaped = self._escape_identifier(alias)
        sql = f"{sql} AS {alias_escaped}"

        return sql

    def build_fields(self, fields: list, context: Optional[dict] = None) -> list:
        """
        批量构建字段SQL

        Args:
            fields: 字段列表
            context: 上下文信息

        Returns:
            list: SQL字段表达式列表
        """
        return [self.build(field, context) for field in fields]
