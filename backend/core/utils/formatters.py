"""
格式化函数模块

提供统一的字符串、表名、字段名格式化功能。

作者: Claude Code
版本: 1.0.0
创建日期: 2026-02-10

功能分类:
- 表名格式化 (format_table_name)
- 字段名格式化 (format_field_name)
- 错误响应格式化 (format_error_response)
- HQL格式化辅助函数

使用示例:
    >>> from backend.core.utils.formatters import (
    ...     format_table_name,
    ...     format_field_name,
    ...     format_error_response
    ... )
    >>>
    >>> # 格式化表名
    >>> table_name = format_table_name("user_events", game_gid=10000147)
    >>>
    >>> # 格式化字段名
    >>> field_name = format_field_name("user_id", "用户ID")
    >>>
    >>> # 格式化错误响应
    >>> error_dict = format_error_response(Exception("Test error"))
"""

import re
from typing import Dict, Any, Optional, List
from backend.core.logging import get_logger

logger = get_logger(__name__)


# ============================================================================
# 表名格式化函数
# ============================================================================


def format_table_name(
    base_name: str,
    game_gid: Optional[int] = None,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
) -> str:
    """
    格式化数据库表名

    Args:
        base_name: 基础表名
        game_gid: 游戏GID（可选）
        prefix: 表名前缀（可选）
        suffix: 表名后缀（可选）

    Returns:
        格式化后的表名

    Example:
        >>> # 基础表名
        >>> table = format_table_name("events")
        >>> print(table)  # 'events'
        >>>
        >>> # 带游戏GID
        >>> table = format_table_name("events", game_gid=10000147)
        >>> print(table)  # 'events_10000147'
        >>>
        >>> # 带前缀和后缀
        >>> table = format_table_name("events", prefix="v_", suffix="_di")
        >>> print(table)  # 'v_events_di'
    """
    parts = []

    if prefix:
        parts.append(prefix)

    parts.append(base_name)

    if game_gid is not None:
        parts.append(str(game_gid))

    if suffix:
        parts.append(suffix)

    # 用下划线连接所有部分
    table_name = "_".join(parts)

    # 清理特殊字符（点号替换为下划线）
    table_name = table_name.replace(".", "_")

    return table_name


def format_dwd_table_name(game_gid: int, event_name: str, dwd_prefix: str = "ieu_cdm") -> str:
    """
    生成DWD层表名

    Args:
        game_gid: 游戏GID
        event_name: 事件名称
        dwd_prefix: DWD层前缀（默认ieu_cdm）

    Returns:
        DWD表名

    Example:
        >>> table = format_dwd_table_name(10000147, "login")
        >>> print(table)  # 'ieu_cdm.v_dwd_10000147_login_di'
    """
    # 清理事件名中的特殊字符（点号替换为下划线）
    clean_name = event_name.replace(".", "_")

    # 目标表名: {prefix}.v_dwd_{game_gid}_{event}_di
    return f"{dwd_prefix}.v_dwd_{game_gid}_{clean_name}_di"


def format_ods_table_name(game_gid: int, ods_db: str = "ieu_ods") -> str:
    """
    生成ODS层表名

    Args:
        game_gid: 游戏GID
        ods_db: ODS数据库名

    Returns:
        ODS表名

    Example:
        >>> table = format_ods_table_name(10000147)
        >>> print(table)  # 'ieu_ods.ods_10000147_all_view'
    """
    return f"{ods_db}.ods_{game_gid}_all_view"


# ============================================================================
# 字段名格式化函数
# ============================================================================


def format_field_name(
    field_name: str, field_alias: Optional[str] = None, aggregate_func: Optional[str] = None
) -> str:
    """
    格式化SQL字段名

    Args:
        field_name: 字段名
        field_alias: 字段别名（可选）
        aggregate_func: 聚合函数（可选，如COUNT, SUM等）

    Returns:
        格式化后的字段表达式

    Example:
        >>> # 简单字段
        >>> field = format_field_name("user_id")
        >>> print(field)  # 'user_id'
        >>>
        >>> # 带别名
        >>> field = format_field_name("user_id", "uid")
        >>> print(field)  # 'user_id AS uid'
        >>>
        >>> # 带聚合函数
        >>> field = format_field_name("user_id", aggregate_func="COUNT")
        >>> print(field)  # 'COUNT(user_id)'
    """
    if aggregate_func:
        result = f"{aggregate_func}({field_name})"
    else:
        result = field_name

    if field_alias:
        result += f" AS {field_alias}"

    return result


def format_field_list(
    fields: List[Dict[str, str]], aggregate_func: Optional[str] = None
) -> List[str]:
    """
    批量格式化字段列表

    Args:
        fields: 字段字典列表，每个字典包含:
            - name: 字段名
            - alias: 字段别名（可选）
        aggregate_func: 聚合函数（可选）

    Returns:
        格式化后的字段表达式列表

    Example:
        >>> fields = [
        ...     {"name": "user_id", "alias": "uid"},
        ...     {"name": "event_name", "alias": "event"}
        ... ]
        >>> formatted = format_field_list(fields)
        >>> print(formatted)
        ['user_id AS uid', 'event_name AS event']
    """
    result = []
    for field in fields:
        field_name = field.get("name")
        field_alias = field.get("alias")
        formatted = format_field_name(field_name, field_alias, aggregate_func)
        result.append(formatted)
    return result


# ============================================================================
# 错误响应格式化函数
# ============================================================================


def format_error_response(
    error: Exception, context: str = "", include_traceback: bool = False
) -> Dict[str, Any]:
    """
    格式化错误响应

    Args:
        error: 异常对象
        context: 错误上下文信息
        include_traceback: 是否包含堆栈跟踪

    Returns:
        标准化的错误响应字典

    Example:
        >>> try:
        ...     # some operation
        ...     pass
        ... except Exception as e:
        ...     error_dict = format_error_response(e, context="Create event")
        ...     return jsonify(error_dict), 500
    """
    error_type = type(error).__name__
    error_message = str(error)

    response = {"error": error_message, "error_type": error_type, "status": "error"}

    if context:
        response["context"] = context

    if include_traceback:
        import traceback

        response["traceback"] = traceback.format_exc()

    logger.error(f"Error in {context or 'operation'}: {error_type} - {error_message}")

    return response


# ============================================================================
# HQL格式化辅助函数
# ============================================================================


def format_hql_select(fields: List[str]) -> str:
    """
    格式化HQL SELECT子句

    Args:
        fields: 字段列表

    Returns:
        SELECT子句字符串

    Example:
        >>> select = format_hql_select(["user_id", "event_name"])
        >>> print(select)  # 'SELECT\\n  user_id,\\n  event_name'
    """
    if not fields:
        return "SELECT 1"

    indented_fields = [f"  {field}" for field in fields]
    return "SELECT\n" + ",\n".join(indented_fields)


def format_hql_from(table: str, alias: Optional[str] = None) -> str:
    """
    格式化HQL FROM子句

    Args:
        table: 表名
        alias: 表别名（可选）

    Returns:
        FROM子句字符串

    Example:
        >>> from_clause = format_hql_from("events", "e")
        >>> print(from_clause)  # 'FROM events AS e'
    """
    if alias:
        return f"FROM {table} AS {alias}"
    return f"FROM {table}"


def format_hql_join(join_type: str, table: str, alias: str, on_condition: str) -> str:
    """
    格式化HQL JOIN子句

    Args:
        join_type: JOIN类型（INNER, LEFT, RIGHT, FULL）
        table: 表名
        alias: 表别名
        on_condition: JOIN条件

    Returns:
        JOIN子句字符串

    Example:
        >>> join = format_hql_join("LEFT", "users", "u", "e.user_id = u.id")
        >>> print(join)  # 'LEFT JOIN users AS u ON e.user_id = u.id'
    """
    return f"{join_type} JOIN {table} AS {alias} ON {on_condition}"


def format_hql_where(conditions: List[str]) -> str:
    """
    格式化HQL WHERE子句

    Args:
        conditions: 条件列表

    Returns:
        WHERE子句字符串

    Example:
        >>> where = format_hql_where(["user_id > 0", "event_time IS NOT NULL"])
        >>> print(where)  # 'WHERE\\n  user_id > 0\\n  AND event_time IS NOT NULL'
    """
    if not conditions:
        return ""

    indented_conditions = [f"  {cond}" for cond in conditions]
    return "WHERE\n" + "\n  AND ".join(indented_conditions)


def format_hql_group_by(fields: List[str]) -> str:
    """
    格式化HQL GROUP BY子句

    Args:
        fields: 分组字段列表

    Returns:
        GROUP BY子句字符串

    Example:
        >>> group_by = format_hql_group_by(["user_id", "event_name"])
        >>> print(group_by)  # 'GROUP BY\\n  user_id,\\n  event_name'
    """
    if not fields:
        return ""

    indented_fields = [f"  {field}" for field in fields]
    return "GROUP BY\n" + ",\n".join(indented_fields)


def format_hql(
    select_fields: List[str],
    from_table: str,
    where_conditions: Optional[List[str]] = None,
    group_by_fields: Optional[List[str]] = None,
    joins: Optional[List[str]] = None,
) -> str:
    """
    完整的HQL语句格式化

    Args:
        select_fields: SELECT字段列表
        from_table: FROM表名
        where_conditions: WHERE条件列表（可选）
        group_by_fields: GROUP BY字段列表（可选）
        joins: JOIN子句列表（可选）

    Returns:
        完整的HQL语句

    Example:
        >>> hql = format_hql(
        ...     select_fields=["user_id", "COUNT(*) AS cnt"],
        ...     from_table="events",
        ...     where_conditions=["event_date = '2024-01-01'"],
        ...     group_by_fields=["user_id"]
        ... )
        >>> print(hql)
    """
    parts = []

    # SELECT
    parts.append(format_hql_select(select_fields))

    # FROM
    parts.append(format_hql_from(from_table))

    # JOINs
    if joins:
        parts.extend(joins)

    # WHERE
    if where_conditions:
        parts.append(format_hql_where(where_conditions))

    # GROUP BY
    if group_by_fields:
        parts.append(format_hql_group_by(group_by_fields))

    return "\n".join(parts)


# ============================================================================
# 字符串清理和格式化
# ============================================================================


def clean_identifier(name: str) -> str:
    """
    清理标识符（表名、字段名等）

    - 转换为小写
    - 替换空格和特殊字符为下划线
    - 移除重复的下划线

    Args:
        name: 原始标识符

    Returns:
        清理后的标识符

    Example:
        >>> clean = clean_identifier("User Event Name")
        >>> print(clean)  # 'user_event_name'
    """
    # 转换为小写
    name = name.lower()

    # 替换空格和特殊字符为下划线
    name = re.sub(r"[^a-z0-9_]+", "_", name)

    # 移除重复的下划线
    name = re.sub(r"_+", "_", name)

    # 移除首尾的下划线
    name = name.strip("_")

    return name


# 导出列表
__all__ = [
    # 表名格式化
    "format_table_name",
    "format_dwd_table_name",
    "format_ods_table_name",
    # 字段名格式化
    "format_field_name",
    "format_field_list",
    # 错误响应格式化
    "format_error_response",
    # HQL格式化
    "format_hql_select",
    "format_hql_from",
    "format_hql_join",
    "format_hql_where",
    "format_hql_group_by",
    "format_hql",
    # 字符串清理
    "clean_identifier",
]
