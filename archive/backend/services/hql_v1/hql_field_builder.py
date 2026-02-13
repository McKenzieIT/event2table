#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HQL字段构建器

提供统一的HQL字段表达式生成功能，包括：
- 字段名转义（反引号）
- JSON解析（get_json_object）
- 类型转换（CAST）
"""

from typing import Dict, Any, Optional
from enum import Enum


class FieldType(Enum):
    """字段类型枚举"""
    BASE = 'base'      # 基础字段（ds, role_id等）
    PARAM = 'param'    # 参数字段（从params JSON中提取）
    CUSTOM = 'custom'  # 自定义字段（使用hql_template）
    FIXED = 'fixed'    # 固定值字段


class HqlFieldBuilder:
    """HQL字段构建器"""

    # 基础字段列表（不需要JSON解析）
    BASE_FIELDS = {'ds', 'role_id', 'account_id', 'utdid', 'envinfo', 'tm', 'ts'}

    # 类型转换映射：base_type -> CAST类型
    TYPE_CAST_MAPPING = {
        'int': 'BIGINT',
        'bigint': 'BIGINT',
        'float': 'DOUBLE',
        'decimal': 'DOUBLE',
        'string': None,      # 不转换
        'boolean': None,     # 不转换
        'array': None,       # 不转换（保留JSON字符串）
        'map': None,         # 不转换（保留JSON字符串）
    }

    @staticmethod
    def escape_field_name(field_name: str, field_type: str) -> str:
        """
        转义字段名（参数字段需要反引号）

        Args:
            field_name: 字段名
            field_type: 字段类型（'base', 'param', 'custom', 'fixed'）

        Returns:
            转义后的字段名

        Example:
            >>> HqlFieldBuilder.escape_field_name('type', 'param')
            '`type`'
            >>> HqlFieldBuilder.escape_field_name('ds', 'base')
            'ds'
        """
        if field_type in (FieldType.PARAM.value, FieldType.CUSTOM.value):
            return f"`{field_name}`"
        return field_name

    @staticmethod
    def build_field_expression(
        field_name: str,
        field_type: str,
        base_type: Optional[str] = None,
        hql_template: Optional[str] = None
    ) -> str:
        """
        构建字段表达式（带JSON解析和类型转换）

        Args:
            field_name: 字段名
            field_type: 字段类型（'base', 'param', 'custom', 'fixed'）
            base_type: 基础类型（string, int, bigint等）
            hql_template: HQL解析模板

        Returns:
            字段表达式

        Example:
            >>> HqlFieldBuilder.build_field_expression('packId', 'param', 'bigint')
            'CAST(get_json_object(params, \\'$.packId\\') AS BIGINT)'
            >>> HqlFieldBuilder.build_field_expression('ds', 'base')
            'ds'
            >>> HqlFieldBuilder.build_field_expression('custom_expr', 'custom', None, 'get_json_object(params, \\'$.xxx\\')')
            'get_json_object(params, \\'$.xxx\\')'
            >>> HqlFieldBuilder.build_field_expression('fixed_value', 'fixed')
            "'fixed_value'"
        """
        # 基础字段直接返回
        if field_type == FieldType.BASE.value:
            return field_name

        # 参数字段需要JSON解析
        if field_type == FieldType.PARAM.value:
            if hql_template:
                # 使用模板（已包含CAST）
                expression = hql_template.format(param_name=field_name)
            else:
                # 手动构建
                expression = f"get_json_object(params, '$.{field_name}')"

                # 添加类型转换
                cast_type = HqlFieldBuilder.TYPE_CAST_MAPPING.get(base_type)
                if cast_type:
                    expression = f"CAST({expression} AS {cast_type})"
            return expression

        # 自定义字段使用hql_template
        if field_type == FieldType.CUSTOM.value:
            if hql_template:
                return hql_template
            return field_name

        # 固定值字段返回带引号的字符串
        if field_type == FieldType.FIXED.value:
            return f"'{field_name}'"

        # 默认返回字段名
        return field_name

    @staticmethod
    def build_select_field(
        field_name: str,
        field_type: str,
        alias: Optional[str] = None,
        base_type: Optional[str] = None,
        hql_template: Optional[str] = None
    ) -> str:
        """
        构建SELECT字段语句

        Args:
            field_name: 字段名
            field_type: 字段类型
            alias: 别名
            base_type: 基础类型
            hql_template: HQL解析模板

        Returns:
            SELECT字段语句

        Example:
            >>> HqlFieldBuilder.build_select_field('packId', 'param', 'pid', 'bigint')
            'CAST(get_json_object(params, \\'$.packId\\') AS BIGINT) AS `packId`'
        """
        # 构建字段表达式
        expression = HqlFieldBuilder.build_field_expression(
            field_name, field_type, base_type, hql_template
        )

        # 转义别名（参数字段需要反引号）
        safe_alias = alias if alias else field_name
        escaped_alias = HqlFieldBuilder.escape_field_name(safe_alias, field_type)

        return f"{expression} AS {escaped_alias}"

    @staticmethod
    def build_where_condition(
        field_name: str,
        field_type: str,
        operator: str,
        value: Any,
        base_type: Optional[str] = None,
        hql_template: Optional[str] = None,
        values: Optional[list] = None
    ) -> str:
        """
        构建WHERE条件语句

        Args:
            field_name: 字段名
            field_type: 字段类型
            operator: 操作符（=, !=, >, <, >=, <=, IN, NOT IN, BETWEEN, LIKE, IS NULL, IS NOT NULL）
            value: 值（单值操作符使用）
            values: 值列表（IN, NOT IN, BETWEEN使用）
            base_type: 基础类型
            hql_template: HQL解析模板

        Returns:
            WHERE条件语句

        Example:
            >>> HqlFieldBuilder.build_where_condition('packId', 'param', '>', '100', 'bigint')
            'CAST(get_json_object(params, \\'$.packId\\') AS BIGINT) > 100'
        """
        # 构建字段表达式
        field_expr = HqlFieldBuilder.build_field_expression(
            field_name, field_type, base_type, hql_template
        )

        # 空值判断
        if operator in ('IS NULL', 'IS NOT NULL'):
            return f"{field_expr} {operator}"

        # IN操作符
        if operator in ('IN', 'NOT IN'):
            if not values or len(values) == 0:
                raise ValueError(f"{operator} 操作符需要至少1个值")

            # 根据类型格式化值
            formatted_values = HqlFieldBuilder._format_values(values, base_type)
            values_str = ', '.join(formatted_values)
            return f"{field_expr} {operator} ({values_str})"

        # BETWEEN操作符
        if operator in ('BETWEEN', 'NOT BETWEEN'):
            if not values or len(values) < 2:
                raise ValueError("BETWEEN 操作符需要2个值")

            formatted_values = HqlFieldBuilder._format_values(values[:2], base_type)
            return f"{field_expr} {operator} {formatted_values[0]} AND {formatted_values[1]}"

        # LIKE操作符
        if operator == 'LIKE':
            if not value:
                raise ValueError("LIKE 操作符需要值")
            return f"{field_expr} LIKE '%{value}%'"

        # 单值操作符（=, !=, >, <, >=, <=）
        if value is None:
            raise ValueError(f"{operator} 操作符需要值")

        formatted_value = HqlFieldBuilder._format_value(value, base_type)
        return f"{field_expr} {operator} {formatted_value}"

    @staticmethod
    def _format_value(value: Any, base_type: Optional[str]) -> str:
        """
        格式化单个值

        Args:
            value: 值
            base_type: 基础类型

        Returns:
            格式化后的值
        """
        # 数字类型不需要引号
        if base_type in ('int', 'bigint', 'float', 'decimal'):
            return str(value)

        # 字符串类型需要单引号，并转义内部单引号
        if isinstance(value, str):
            escaped_value = value.replace("'", "''")
            return f"'{escaped_value}'"

        return str(value)

    @staticmethod
    def _format_values(values: list, base_type: Optional[str]) -> list:
        """
        格式化值列表

        Args:
            values: 值列表
            base_type: 基础类型

        Returns:
            格式化后的值列表
        """
        return [HqlFieldBuilder._format_value(v, base_type) for v in values]
