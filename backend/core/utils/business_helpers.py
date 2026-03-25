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
- ❌ 业务规则(需要验证, 状态管理) → 保留在Service层
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

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

    # 只保留字母, 数字, 下划线, 点
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

    # 只允许字母, 数字, 下划线
    if not re.match(r"^[a-zA-Z0-9_]+$", event_name):
        raise ValueError("event_name can only contain letters, numbers, and underscores")

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
        "custom_events": sum(1 for e in events if e.name and not e.name.startswith("base_")),
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


def generate_table_name(game_gid: int, event_name: str, ods_db: str = "ieu_ods") -> str:
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


def generate_dwd_table_name(game_gid: int, event_name: str, dwd_prefix: str = "dwd") -> str:
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


# ============================================================================
# Game Context Helpers
# ============================================================================

from typing import Optional, Tuple

from flask import flash, redirect, url_for

from backend.core.config import CommonParamConfig, ODSDatabase
from backend.core.database import get_db_connection
from backend.core.utils.converters import fetch_one_as_dict


def get_game_gid_param(request_obj, param_name: str = "game_gid") -> Optional[str]:
    """
    从请求中获取 game_gid 参数（支持字符串和整数类型）

    由于数据库中 games.gid 是 TEXT 类型, 但部分代码使用 type=int,
    此函数提供统一的方式来获取和转换 game_gid 参数.

    Args:
        request_obj: Flask request 对象
        param_name: 参数名称（默认为 "game_gid"）

    Returns:
        game_gid 字符串, 如果参数不存在返回 None

    Example:
        # 在视图函数中使用
        game_gid = get_game_gid_param(request)
        if not game_gid:
            return json_error_response("game_gid is required", status_code=400)

        # Now game_gid is a string type, can be used directly in SQL queries
        game = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (game_gid,))
    """
    from flask import request

    # Try to get as integer (for backward compatibility)
    value_int = request.args.get(param_name, type=int)
    if value_int is not None:
        return str(value_int)

    # 尝试作为字符串获取
    value_str = request.args.get(param_name, type=str)
    if value_str:
        return value_str.strip()

    # 参数不存在
    return None


def require_game_with_redirect(func):
    """
    Decorator to require game selection before accessing a route

    Usage:
        @require_game_with_redirect
        @events_bp.route('/events')
        def list_events():
            ...
    """

    def wrapper(*args, **kwargs):
        exists, message = check_games_exist()
        if not exists:
            flash(message, "error")
            return redirect(url_for("games.list_games"))
        return func(*args, **kwargs)

    return wrapper


def get_ods_db_name(ods_type: str) -> str:
    """
    Get ODS database name by type

    Args:
        ods_type: ODS type ('domestic' or 'overseas')

    Returns:
        Database name
    """
    return ODSDatabase.get_db_name(ods_type)


def calculate_common_param_threshold(event_count: int, ratio: Optional[float] = None) -> int:
    """
    Calculate the threshold for common parameters

    Args:
        event_count: Total number of events
        ratio: Threshold ratio (default from config)

    Returns:
        Minimum number of events a parameter must appear in to be considered common
    """
    if ratio is None:
        ratio = CommonParamConfig.DEFAULT_THRESHOLD_RATIO

    threshold = int(event_count * ratio)
    # Ensure at least 1 event is required
    return max(1, threshold)


def check_games_exist() -> Tuple[bool, Optional[str]]:
    """
    Check if any games exist in the database

    Returns:
        Tuple of (exists, redirect_message)
    """
    conn = get_db_connection()
    try:
        count = conn.execute("SELECT COUNT(*) as count FROM games").fetchone()["count"]
        if count == 0:
            return False, "请先创建游戏"
        return True, None
    finally:
        conn.close()


def validate_game_exists(game_gid: int) -> Tuple[bool, Optional[dict], Optional[str]]:
    """
    Validate that a game exists

    Args:
        game_gid: The game GID to validate

    Returns:
        Tuple of (exists, game_dict, error_message)
    """
    conn = get_db_connection()
    try:
        game = conn.execute("SELECT * FROM games WHERE gid = ?", (game_gid,)).fetchone()
        if game:
            return True, dict(game), None
        else:
            return False, None, "游戏不存在"
    finally:
        conn.close()


# ============================================================================
# Query Helper Functions
# ============================================================================

from typing import Any, Dict, List

from backend.core.utils.converters import fetch_all_as_dict


def get_event_with_game_info(event_id: int) -> Optional[Dict[str, Any]]:
    """
    Get event with game and category details

    Args:
        event_id: Event ID

    Returns:
        Event dictionary with game and category info, or None if not found

    Example:
        event = get_event_with_game_info(123)
        if event:
            print(f"Event: {event['event_name']}, Game: {event['game_name']}")
    """
    return fetch_one_as_dict(
        """
        SELECT le.*, g.gid, g.name as game_name, g.ods_db, ec.name as category_name
        FROM log_events le
        LEFT JOIN games g ON le.game_gid = g.gid
        LEFT JOIN event_categories ec ON le.category_id = ec.id
        WHERE le.id = ?
    """,
        (event_id,),
    )


def get_game_by_gid(gid: str) -> Optional[Dict[str, Any]]:
    """
    Get game by GID

    Args:
        gid: Game GID

    Returns:
        Game dictionary or None if not found

    Example:
        game = get_game_by_gid('10000147')
        if game:
            print(f"Game: {game['name']}, ODS DB: {game['ods_db']}")
    """
    return fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (gid,))


def get_active_parameters(event_id: int) -> List[Dict[str, Any]]:
    """
    Get active parameters for an event

    Args:
        event_id: Event ID

    Returns:
        List of parameter dictionaries

    Example:
        params = get_active_parameters(123)
        for param in params:
            print(f"Parameter: {param['param_name']}, Type: {param['template_name']}")
    """
    return fetch_all_as_dict(
        """
        SELECT ep.*, pt.template_name, pt.display_name as type_display_name
        FROM event_params ep
        LEFT JOIN param_templates pt ON ep.template_id = pt.id
        WHERE ep.event_id = ? AND ep.is_active = 1
        ORDER BY ep.id
    """,
        (event_id,),
    )


def get_event_with_parameters(event_id: int) -> Optional[Dict[str, Any]]:
    """
    Get event with all its parameters in a single query

    Args:
        event_id: Event ID

    Returns:
        Dictionary with event info and parameters list, or None if not found

    Example:
        event_data = get_event_with_parameters(123)
        if event_data:
            print(f"Event: {event_data['event']['event_name']}")
            for param in event_data['parameters']:
                print(f"  - {param['param_name']}")
    """
    event = get_event_with_game_info(event_id)
    if not event:
        return None

    parameters = get_active_parameters(event_id)

    return {"event": event, "parameters": parameters}


def get_games_with_event_counts() -> List[Dict[str, Any]]:
    """
    Get all games with their event counts

    Returns:
        List of games with event count for each

    Example:
        games = get_games_with_event_counts()
        for game in games:
            print(f"Game: {game['name']}, Events: {game['event_count']}")
    """
    return fetch_all_as_dict(
        """
        SELECT g.*,
               (SELECT COUNT(*) FROM log_events WHERE game_gid = g.gid) as event_count
        FROM games g
        ORDER BY g.name
    """
    )


def check_game_has_events(game_gid: int) -> bool:
    """
    Check if a game has any events

    Args:
        game_gid: Game GID (business GID)

    Returns:
        True if game has events, False otherwise

    Example:
        if not check_game_has_events(10000147):
            print("This game has no events yet")
    """
    result = fetch_one_as_dict(
        "SELECT COUNT(*) as count FROM log_events WHERE game_gid = ?", (game_gid,)
    )
    return result["count"] > 0 if result else False


def get_categories_by_game(game_gid: int) -> List[Dict[str, Any]]:
    """
    Get all categories used by events in a specific game

    Args:
        game_gid: Game GID (business GID)

    Returns:
        List of categories with event counts

    Example:
        categories = get_categories_by_game(10000147)
        for cat in categories:
            print(f"Category: {cat['name']}, Events: {cat['event_count']}")
    """
    return fetch_all_as_dict(
        """
        SELECT ec.*,
               (SELECT COUNT(*) FROM log_events
                WHERE game_gid = ? AND category_id = ec.id) as event_count
        FROM event_categories ec
        WHERE ec.id IN (
            SELECT DISTINCT category_id FROM log_events WHERE game_gid = ?
        )
        ORDER BY ec.name
    """,
        (game_gid, game_gid),
    )


def get_or_401(
    query: str, params: tuple, error_message: str = "Resource not found"
) -> Tuple[bool, Optional[Dict], Optional[str]]:
    """
    Fetch a resource or return 401 error response

    Args:
        query: SQL query string
        params: Query parameters
        error_message: Custom error message

    Returns:
        Tuple of (found, data_dict, error_message)

    Example:
        found, game, error = get_or_401('SELECT * FROM games WHERE id = ?', (game_id,))
        if not found:
            return error_response(error, status_code=404)
    """
    data = fetch_one_as_dict(query, params)
    if not data:
        return False, None, error_message
    return True, data, None


def find_column_by_keywords(headers: List[str], keywords: List[str]) -> Optional[int]:
    """
    Intelligently find column index by keywords with fuzzy matching

    Args:
        headers: List of header names from Excel
        keywords: List of keywords to search for

    Returns:
        Column index (0-based) or None if not found
    """
    for idx, header in enumerate(headers):
        header_lower = header.lower()

        # Direct match
        for keyword in keywords:
            if keyword.lower() in header_lower:
                return idx

        # Fuzzy match - check if header contains any keyword characters
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Remove common separators and check
            header_clean = header_lower.replace("_", "").replace("-", "").replace(" ", "")
            keyword_clean = keyword_lower.replace("_", "").replace("-", "").replace(" ", "")

            # Check if keyword is a substring of header or vice versa
            if keyword_clean in header_clean or header_clean in keyword_clean:
                return idx

    return None


__all__ = [
    # 验证函数
    'validate_game_gid',
    'validate_table_name',
    'validate_event_name',
    # 统计函数
    'calculate_event_statistics',
    'calculate_param_usage',
    # 数据转换函数
    'sanitize_name',
    'generate_table_name',
    'generate_dwd_table_name',
    # HQL生成辅助函数
    'format_json_path',
    'build_hql_field_alias',
    'format_hql_field',
    # 缓存相关函数
    'build_cache_key',
    'build_game_cache_key',
    'build_event_cache_key',
    # 数据验证辅助函数
    'is_valid_game_gid',
    'is_safe_table_name',
    # 类型转换辅助函数
    'python_type_to_hive_type',
    # 游戏上下文辅助
    'get_game_gid_param',
    'require_game_with_redirect',
    'get_ods_db_name',
    'calculate_common_param_threshold',
    'check_games_exist',
    'validate_game_exists',
    # 查询辅助函数
    'get_event_with_game_info',
    'get_game_by_gid',
    'get_active_parameters',
    'get_event_with_parameters',
    'get_games_with_event_counts',
    'check_game_has_events',
    'get_categories_by_game',
    'get_or_401',
    'find_column_by_keywords',
]
