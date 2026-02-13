"""
SQL构建通用工具函数模块

提供SQL语句构建的通用函数，支持HiveQL语法。

作者: Claude Code
版本: 1.0.0
创建日期: 2026-02-09

功能分类:
- 聚合函数生成器
- 字段处理工具
- JOIN构建器
- GROUP BY构建器

使用示例:
    >>> from backend.core.sql_builder import (
    ...     AggregateFunctionBuilder,
    ...     get_field_name,
    ...     GroupByBuilder
    ... )
    >>>
    >>> # 构建聚合SQL
    >>> sql = AggregateFunctionBuilder.build_aggregate_sql('COUNT', 'user_id', 'user_count')
    >>> print(sql)
    'COUNT(user_id) AS user_count'
"""

from typing import Dict, List, Optional, Callable

# ============================================================================
# 聚合函数生成器
# ============================================================================


class AggregateFunctionBuilder:
    """
    SQL聚合函数构建器

    使用策略模式支持不同的聚合函数。
    """

    # 内置聚合函数模板
    AGGREGATE_TEMPLATES = {
        "COUNT": lambda field, alias: f'COUNT({field or "*"}) AS {alias}',
        "SUM": lambda field, alias: f"SUM(CAST({field} AS DOUBLE)) AS {alias}",
        "AVG": lambda field, alias: f"AVG(CAST({field} AS DOUBLE)) AS {alias}",
        "MIN": lambda field, alias: f"MIN({field}) AS {alias}",
        "MAX": lambda field, alias: f"MAX({field}) AS {alias}",
        "COUNT_DISTINCT": lambda field, alias: f"COUNT(DISTINCT {field}) AS {alias}",
        "GROUP_CONCAT": lambda field, alias: f"GROUP_CONCAT({field}) AS {alias}",
    }

    @classmethod
    def build_aggregate_sql(
        cls, func: str, field: str, alias: str, custom_builder: Optional[Callable] = None
    ) -> str:
        """
        构建聚合函数SQL

        Args:
            func: 聚合函数名（COUNT, SUM, AVG等）
            field: 字段名
            alias: 别名
            custom_builder: 自定义构建函数（可选）

        Returns:
            SQL片段

        Example:
            >>> sql = AggregateFunctionBuilder.build_aggregate_sql('COUNT', 'user_id', 'user_count')
            >>> print(sql)
            'COUNT(user_id) AS user_count'
        """
        func_upper = func.upper()

        # 使用自定义构建器（如果提供）
        if custom_builder:
            return custom_builder(func, field, alias)

        # 使用内置模板
        if func_upper in cls.AGGREGATE_TEMPLATES:
            return cls.AGGREGATE_TEMPLATES[func_upper](field, alias)

        # 默认：直接使用函数名
        return f"{func}({field}) AS {alias}"

    @classmethod
    def register_aggregate_function(cls, name: str, builder: Callable) -> None:
        """
        注册自定义聚合函数

        Args:
            name: 函数名
            builder: 构建函数，签名: (field: str, alias: str) -> str

        Example:
            >>> def build_percentile(field: str, alias: str) -> str:
            ...     return f'PERCENTILE({field}, 0.95) AS {alias}'
            >>> AggregateFunctionBuilder.register_aggregate_function('PERCENTILE', build_percentile)
        """
        cls.AGGREGATE_TEMPLATES[name.upper()] = builder


# ============================================================================
# 字段处理工具
# ============================================================================


def get_field_name(field: Dict, fallback_key: str = "name") -> str:
    """
    从字段字典中获取字段名（支持多种键名）

    Args:
        field: 字段字典
        fallback_key: 备用键名

    Returns:
        字段名

    Example:
        >>> field = {'fieldName': 'user_id'}
        >>> get_field_name(field)
        'user_id'
        >>>
        >>> field = {'name': 'user_id'}
        >>> get_field_name(field)
        'user_id'
    """
    return field.get("fieldName") or field.get(fallback_key, "")


def normalize_field_list(fields: List[Dict]) -> List[Dict]:
    """
    标准化字段列表，统一字段名键

    Args:
        fields: 字段列表

    Returns:
        标准化后的字段列表，每个字段包含:
            - name: 字段名
            - alias: 别名
            - type: 数据类型

    Example:
        >>> fields = [{'fieldName': 'x', 'alias': 'y'}]
        >>> normalized = normalize_field_list(fields)
        >>> print(normalized)
        [{'name': 'x', 'alias': 'y', 'type': 'string'}]
    """
    normalized = []
    for field in fields:
        normalized.append(
            {
                "name": get_field_name(field),
                "alias": field.get("alias") or get_field_name(field),
                "type": field.get("type") or field.get("fieldType") or "string",
            }
        )
    return normalized


# ============================================================================
# JOIN构建器
# ============================================================================


class JoinBuilder:
    """
    SQL JOIN语句构建器
    """

    JOIN_TYPES = {
        "INNER": "INNER JOIN",
        "LEFT": "LEFT OUTER JOIN",
        "RIGHT": "RIGHT OUTER JOIN",
        "FULL": "FULL OUTER JOIN",
        "CROSS": "CROSS JOIN",
    }

    @classmethod
    def build_join_clause(
        cls,
        join_type: str,
        left_table: str,
        right_table: str,
        on_condition: str,
        left_fields: Optional[List[str]] = None,
        right_fields: Optional[List[str]] = None,
    ) -> str:
        """
        构建JOIN子句

        Args:
            join_type: JOIN类型（INNER, LEFT, RIGHT, FULL）
            left_table: 左表名
            right_table: 右表名
            on_condition: ON条件
            left_fields: 左表字段列表（可选）
            right_fields: 右表字段列表（可选）

        Returns:
            JOIN SQL子句

        Example:
            >>> join_sql = JoinBuilder.build_join_clause(
            ...     'LEFT', 'events', 'users',
            ...     'events.user_id = users.id'
            ... )
            >>> print(join_sql)
            'LEFT OUTER JOIN users ON events.user_id = users.id'
        """
        join_sql = cls.JOIN_TYPES.get(join_type.upper(), "INNER JOIN")

        clause = f"{join_sql} {right_table} ON {on_condition}"

        return clause


# ============================================================================
# GROUP BY构建器
# ============================================================================


class GroupByBuilder:
    """
    GROUP BY子句构建器
    """

    @classmethod
    def build_group_by_clause(
        cls, group_fields: List[Dict], select_fields: Optional[List[Dict]] = None
    ) -> str:
        """
        构建GROUP BY子句

        Args:
            group_fields: 分组字段列表
            select_fields: SELECT字段列表（用于验证）

        Returns:
            GROUP BY子句

        Example:
            >>> fields = [{'fieldName': 'region'}, {'fieldName': 'category'}]
            >>> clause = GroupByBuilder.build_group_by_clause(fields)
            >>> print(clause)
            'GROUP BY region, category'
        """
        if not group_fields:
            return ""

        field_names = [get_field_name(f) for f in group_fields if get_field_name(f)]

        if not field_names:
            return ""

        return f"GROUP BY {', '.join(field_names)}"


# 导出列表
__all__ = [
    # 聚合函数
    "AggregateFunctionBuilder",
    # 字段处理
    "get_field_name",
    "normalize_field_list",
    # JOIN
    "JoinBuilder",
    # GROUP BY
    "GroupByBuilder",
]
