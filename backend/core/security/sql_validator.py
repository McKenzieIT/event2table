#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL标识符验证器
防止SQL注入攻击
"""
import re
from typing import Set, Union


class SQLValidator:
    """SQL标识符验证器，防止SQL注入攻击"""

    IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

    # 允许的PRAGMA键白名单
    ALLOWED_PRAGMAS: Set[str] = {
        'user_version', 'journal_mode', 'synchronous',
        'cache_size', 'foreign_keys', 'table_info',
        'index_info', 'index_list', 'temp_store',
        'locking_mode', 'page_size', 'encoding'
    }

    @classmethod
    def validate_identifier(cls, identifier: str, name: str = "identifier") -> str:
        """
        验证SQL标识符

        Args:
            identifier: 要验证的标识符
            name: 标识符名称（用于错误消息）

        Returns:
            验证后的标识符

        Raises:
            ValueError: 如果标识符无效
        """
        if not isinstance(identifier, str):
            raise ValueError(f"{name} must be a string")

        if not identifier:
            raise ValueError(f"{name} cannot be empty")

        if not cls.IDENTIFIER_PATTERN.match(identifier):
            raise ValueError(
                f"Invalid {name}: '{identifier}'. "
                f"Must be a valid SQL identifier (letters, numbers, underscores, "
                f"cannot start with a number)"
            )

        return identifier

    @classmethod
    def validate_table_name(cls, table_name: str) -> str:
        """
        验证表名

        Args:
            table_name: 要验证的表名

        Returns:
            验证后的表名

        Raises:
            ValueError: 如果表名无效
        """
        return cls.validate_identifier(table_name, "table_name")

    @classmethod
    def validate_column_name(cls, column_name: str) -> str:
        """
        验证列名

        Args:
            column_name: 要验证的列名

        Returns:
            验证后的列名

        Raises:
            ValueError: 如果列名无效
        """
        return cls.validate_identifier(column_name, "column_name")

    @classmethod
    def validate_field_whitelist(cls, field_name: str, whitelist: Set[str]) -> str:
        """
        验证字段名是否在白名单中

        Args:
            field_name: 要验证的字段名
            whitelist: 允许的字段白名单

        Returns:
            验证后的字段名

        Raises:
            ValueError: 如果字段名不在白名单中
        """
        if not isinstance(field_name, str):
            raise TypeError(f"Field name must be a string, got {type(field_name).__name__}")

        if field_name not in whitelist:
            raise ValueError(
                f"Field '{field_name}' is not allowed. "
                f"Allowed fields: {', '.join(sorted(whitelist))}"
            )

        return field_name

    @classmethod
    def sanitize_order_by(cls, order_by: str, whitelist: Set[str]) -> str:
        """
        验证并清理ORDER BY子句

        Args:
            order_by: ORDER BY子句 (例如 "name" 或 "created_at DESC")
            whitelist: 允许的字段白名单

        Returns:
            清理后的ORDER BY子句

        Raises:
            ValueError: 如果字段或方向无效
        """
        if not isinstance(order_by, str):
            raise TypeError(f"ORDER BY must be a string, got {type(order_by).__name__}")

        parts = order_by.strip().split()
        if len(parts) == 1:
            # 仅字段名
            field = cls.validate_field_whitelist(parts[0], whitelist)
            return f'"{field}"'
        elif len(parts) == 2:
            # 字段名 + 方向
            field = cls.validate_field_whitelist(parts[0], whitelist)
            direction = parts[1].upper()
            if direction not in ('ASC', 'DESC'):
                raise ValueError(f"Invalid sort direction: {direction}. Must be ASC or DESC")
            return f'"{field}" {direction}'
        else:
            raise ValueError(f"Invalid ORDER BY clause: {order_by}")

    @classmethod
    def validate_pragma_key(cls, key: str) -> str:
        """
        验证PRAGMA键名

        Args:
            key: PRAGMA键名

        Returns:
            验证后的键名

        Raises:
            ValueError: 如果键名无效或不在白名单中
        """
        key = cls.validate_identifier(key, "pragma_key")
        if key not in cls.ALLOWED_PRAGMAS:
            raise ValueError(
                f"PRAGMA key '{key}' not in allowed list. "
                f"Allowed pragmas: {', '.join(sorted(cls.ALLOWED_PRAGMAS))}"
            )
        return key

    @classmethod
    def validate_integer(cls, value: int, name: str = "value") -> int:
        """
        验证整数值

        Args:
            value: 要验证的整数值
            name: 值名称（用于错误消息）

        Returns:
            验证后的整数值

        Raises:
            ValueError: 如果值不是非负整数
        """
        if not isinstance(value, int):
            raise ValueError(f"{name} must be an integer, got {type(value).__name__}")

        if value < 0:
            raise ValueError(f"{name} must be a non-negative integer, got {value}")

        return value

    @classmethod
    def validate_pragma_value(cls, value: Union[str, int], key: str) -> Union[str, int]:
        """
        验证PRAGMA值

        Args:
            value: PRAGMA值
            key: PRAGMA键名（用于验证规则）

        Returns:
            验证后的值

        Raises:
            ValueError: 如果值无效
        """
        # 根据不同的PRAGMA键应用不同的验证规则
        if key in ['user_version', 'cache_size', 'page_size']:
            # 这些PRAGMA需要整数值
            return cls.validate_integer(value, f"PRAGMA {key}")

        elif key in ['journal_mode', 'temp_store', 'locking_mode']:
            # 这些PRAGMA需要特定的字符串值
            valid_values = {
                'journal_mode': {'DELETE', 'TRUNCATE', 'PERSIST', 'MEMORY', 'WAL', 'OFF'},
                'temp_store': {'DEFAULT', 'FILE', 'MEMORY'},
                'locking_mode': {'NORMAL', 'EXCLUSIVE'}
            }
            if key in valid_values and str(value).upper() not in valid_values[key]:
                raise ValueError(
                    f"Invalid value for {key}: '{value}'. "
                    f"Valid values: {', '.join(sorted(valid_values[key]))}"
                )
            return str(value)

        elif key == 'synchronous':
            # synchronous PRAGMA接受0/1/2/3或OFF/NORMAL/FULL/EXTRA
            if isinstance(value, int) and value in [0, 1, 2, 3]:
                return value
            if isinstance(value, str):
                upper_val = value.upper()
                if upper_val in ['OFF', '0']:
                    return 0
                elif upper_val in ['NORMAL', '1']:
                    return 1
                elif upper_val in ['FULL', '2']:
                    return 2
                elif upper_val in ['EXTRA', '3']:
                    return 3

            raise ValueError(
                f"Invalid value for {key}: '{value}'. "
                f"Must be 0/OFF, 1/NORMAL, 2/FULL, or 3/EXTRA"
            )

        elif key == 'foreign_keys':
            # foreign_keys PRAGMA需要布尔值或0/1
            if isinstance(value, bool):
                return 1 if value else 0
            if isinstance(value, int) and value in [0, 1]:
                return value
            if isinstance(value, str):
                lower_val = value.lower()
                if lower_val in ['true', '1', 'yes', 'on']:
                    return 1
                elif lower_val in ['false', '0', 'no', 'off']:
                    return 0

            raise ValueError(
                f"Invalid value for {key}: '{value}'. "
                f"Must be a boolean or 0/1"
            )

        elif key == 'encoding':
            # 编码必须是有效的字符串
            if not isinstance(value, str):
                raise ValueError(f"Encoding must be a string, got {type(value).__name__}")
            valid_encodings = {'UTF-8', 'UTF-16', 'UTF-16le', 'UTF-16be'}
            if value.upper() not in valid_encodings:
                raise ValueError(
                    f"Invalid encoding: '{value}'. "
                    f"Valid encodings: {', '.join(sorted(valid_encodings))}"
                )
            return value

        # 默认返回原值
        return value
