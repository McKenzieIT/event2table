#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
业务逻辑辅助函数

可复用的跨Service业务逻辑

设计原则:
1. 纯函数 (无状态)
2. 广泛复用 (3+处使用)
3. 业务相关 (非技术工具)

使用标准:
- ✅ 3个以上Service使用的逻辑 → 工具函数
- ✅ 纯函数逻辑(无状态,无副作用) → 工具函数
- ❌ 业务规则(需要验证、状态管理) → 保留在Service层
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from backend.models.entities import EventEntity, ParameterEntity


# ============================================================================
# 验证函数
# ============================================================================


def validate_game_gid(game_gid: Any) -> None:
    """
    验证game_gid格式

    Args:
        game_gid: 游戏GID

    Raises:
        ValueError: 格式不符合要求
    """
    if game_gid is None:
        raise ValueError("game_gid cannot be None")
    if not isinstance(game_gid, int):
        raise ValueError("game_gid must be an integer")
    if game_gid < 0:
        raise ValueError("game_gid must be positive")
    if len(str(game_gid)) > 50:
        raise ValueError("game_gid too long (max 50 digits)")


def validate_table_name(table_name: str) -> str:
    """
    验证并清理表名,防止SQL注入

    Args:
        table_name: 原始表名

    Returns:
        清理后的安全表名

    Raises:
        ValueError: 表名包含危险字符
    """
    if not table_name:
        raise ValueError("table_name cannot be empty")

    # 移除危险字符
    dangerous_chars = [";", "--", "/*", "*/", "xp_", "exec(", "union"]
    for char in dangerous_chars:
        if char.lower() in table_name.lower():
            raise ValueError(f"table_name contains dangerous character: {char}")

    # 只保留字母、数字、下划线、点
    safe_name = "".join(c for c in table_name if c.isalnum() or c in "_.")
    return safe_name


def validate_event_name(event_name: str) -> str:
    """
    验证事件名称格式

    Args:
        event_name: 事件名称

    Returns:
        清理后的事件名称

    Raises:
        ValueError: 事件名称格式不正确
    """
    if not event_name:
        raise ValueError("event_name cannot be empty")

    # 移除前后空格
    event_name = event_name.strip()

    # 只允许字母、数字、下划线
    if not re.match(r"^[a-zA-Z0-9_]+$", event_name):
        raise ValueError(
            "event_name can only contain letters, numbers, and underscores"
        )

    return event_name


# ============================================================================
# 统计函数
# ============================================================================


def calculate_event_statistics(events: List[EventEntity]) -> Dict[str, int]:
    """
    计算事件统计信息

    Args:
        events: 事件列表

    Returns:
        统计信息字典,包含:
        - total: 总事件数
        - with_params: 有参数的事件数
        - base_events: 基础事件数
        - custom_events: 自定义事件数
    """
    return {
        "total": len(events),
        "with_params": sum(1 for e in events if e.param_count and e.param_count > 0),
        "base_events": sum(1 for e in events if e.name and e.name.startswith("base_")),
        "custom_events": sum(
            1 for e in events if e.name and not e.name.startswith("base_")
        ),
    }


def calculate_param_usage(params: List[ParameterEntity]) -> Dict[str, int]:
    """
    计算参数使用统计

    Args:
        params: 参数列表

    Returns:
        统计信息字典,包含:
        - total: 总参数数
        - base_params: 基础参数数
        - json_params: JSON参数数
        - common_params: 公共参数数
    """
    return {
        "total": len(params),
        "base_params": sum(1 for p in params if p.param_type == "base"),
        "json_params": sum(1 for p in params if p.json_path),
        "common_params": sum(1 for p in params if p.is_common),
    }


# ============================================================================
# 数据转换函数
# ============================================================================


def sanitize_name(name: str) -> str:
    """
    清理名称字段,防止XSS攻击

    Args:
        name: 原始名称

    Returns:
        转义后的安全名称
    """
    import html

    if name:
        return html.escape(name.strip())
    return name


def generate_table_name(
    game_gid: int, event_name: str, ods_db: str = "ieu_ods"
) -> str:
    """
    生成ODS表名

    Args:
        game_gid: 游戏GID
        event_name: 事件名称
        ods_db: ODS数据库名

    Returns:
        完整表名: {ods_db}.ods_{game_gid}_{event_name}

    Example:
        >>> generate_table_name(10000147, "login", "ieu_ods")
        'ieu_ods.ods_10000147_login'
    """
    # 验证输入
    validate_game_gid(game_gid)
    validate_event_name(event_name)

    # 清理事件名称
    safe_event = validate_event_name(event_name)

    return f"{ods_db}.ods_{game_gid}_{safe_event}"


def generate_dwd_table_name(
    game_gid: int, event_name: str, dwd_prefix: str = "dwd"
) -> str:
    """
    生成DWD表名

    Args:
        game_gid: 游戏GID
        event_name: 事件名称
        dwd_prefix: DWD表前缀

    Returns:
        完整表名: {dwd_prefix}.v_dwd_{game_gid}_{event_name}_di

    Example:
        >>> generate_dwd_table_name(10000147, "login", "dwd")
        'dwd.v_dwd_10000147_login_di'
    """
    # 验证输入
    validate_game_gid(game_gid)
    validate_event_name(event_name)

    # 清理事件名称
    safe_event = validate_event_name(event_name)

    return f"{dwd_prefix}.v_dwd_{game_gid}_{safe_event}_di"


# ============================================================================
# HQL生成辅助函数
# ============================================================================


def format_json_path(json_path: Optional[str]) -> str:
    """
    格式化JSON路径为HiveQL表达式

    Args:
        json_path: JSON路径 (如 $.zoneId)

    Returns:
        HiveQL表达式 (如 get_json_object(params, '$.zoneId'))

    Example:
        >>> format_json_path("$.zoneId")
        "get_json_object(params, '$.zoneId')"
        >>> format_json_path(None)
        'NULL'
    """
    if not json_path:
        return "NULL"
    return f"get_json_object(params, '{json_path}')"


def build_hql_field_alias(field_name: str) -> str:
    """
    构建HQL字段别名 (snake_case)

    Args:
        field_name: 原始字段名

    Returns:
        别名 (如 zone_id)

    Example:
        >>> build_hql_field_alias("zoneId")
        'zone_id'
        >>> build_hql_field_alias("roleId")
        'role_id'
    """
    # camelCase to snake_case
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", field_name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def format_hql_field(
    field_name: str, json_path: Optional[str] = None, param_type: str = "base"
) -> str:
    """
    格式化HQL字段定义

    Args:
        field_name: 字段名称
        json_path: JSON路径 (param类型需要)
        param_type: 参数类型 (base/param/common/calculate)

    Returns:
        HQL字段表达式

    Example:
        >>> format_hql_field("role_id", param_type="base")
        'role_id'

        >>> format_hql_field("zone_id", "$.zoneId", "param")
        "get_json_object(params, '$.zoneId') AS zone_id"
    """
    alias = build_hql_field_alias(field_name)

    if param_type == "base":
        return alias
    elif param_type == "param":
        json_expr = format_json_path(json_path)
        return f"{json_expr} AS {alias}"
    elif param_type == "common":
        return alias
    elif param_type == "calculate":
        return f"/* {field_name} */ AS {alias}"
    else:
        return alias


# ============================================================================
# 缓存相关函数
# ============================================================================


def build_cache_key(prefix: str, **kwargs) -> str:
    """
    构建缓存键

    Args:
        prefix: 键前缀
        **kwargs: 键值对参数

    Returns:
        格式化的缓存键: prefix:key1:value1:key2:value2

    Example:
        >>> build_cache_key("game", gid=10000147)
        'game:gid:10000147'
        >>> build_cache_key("event", game_gid=10000147, event_name="login")
        'event:event_name:login:game_gid:10000147'
    """
    parts = [prefix]
    for key, value in sorted(kwargs.items()):
        parts.append(f"{key}:{value}")
    return ":".join(parts)


def build_game_cache_key(game_gid: int) -> str:
    """
    构建游戏缓存键

    Args:
        game_gid: 游戏GID

    Returns:
        游戏缓存键
    """
    return build_cache_key("game", gid=game_gid)


def build_event_cache_key(game_gid: int, event_name: str) -> str:
    """
    构建事件缓存键

    Args:
        game_gid: 游戏GID
        event_name: 事件名称

    Returns:
        事件缓存键
    """
    return build_cache_key("event", game_gid=game_gid, name=event_name)


# ============================================================================
# 数据验证辅助函数
# ============================================================================


def is_valid_game_gid(game_gid: Any) -> bool:
    """
    检查game_gid是否有效 (不抛出异常)

    Args:
        game_gid: 游戏GID

    Returns:
        True如果有效,否则False
    """
    try:
        validate_game_gid(game_gid)
        return True
    except (ValueError, TypeError):
        return False


def is_safe_table_name(table_name: str) -> bool:
    """
    检查表名是否安全 (不抛出异常)

    Args:
        table_name: 表名

    Returns:
        True如果安全,否则False
    """
    try:
        validate_table_name(table_name)
        return True
    except (ValueError, TypeError):
        return False


# ============================================================================
# 类型转换辅助函数
# ============================================================================


def python_type_to_hive_type(python_type: str) -> str:
    """
    将Python类型转换为Hive类型

    Args:
        python_type: Python类型名

    Returns:
        Hive类型名

    Example:
        >>> python_type_to_hive_type("int")
        'INT'
        >>> python_type_to_hive_type("str")
        'STRING'
        >>> python_type_to_hive_type("float")
        'DOUBLE'
    """
    type_mapping = {
        "int": "BIGINT",
        "str": "STRING",
        "float": "DOUBLE",
        "bool": "BOOLEAN",
        "datetime": "STRING",
        "list": "ARRAY<STRING>",
        "dict": "MAP<STRING, STRING>",
    }

    return type_mapping.get(python_type, "STRING")
