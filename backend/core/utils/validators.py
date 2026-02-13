"""
验证函数模块

提供统一的输入验证、格式检查和安全验证功能。

作者: Claude Code
版本: 1.0.0
创建日期: 2026-02-10

功能分类:
- 输入验证 (validate_event_name, validate_param_name, validate_game_gid)
- 安全验证 (sanitize_and_validate_string, validate_sql_safe)
- 业务验证 (validate_game_exists, check_games_exist)

使用示例:
    >>> from backend.core.utils.validators import (
    ...     validate_event_name,
    ...     validate_param_name,
    ...     sanitize_and_validate_string,
    ...     validate_game_gid
    ... )
    >>>
    >>> # 验证事件名
    >>> is_valid, error = validate_event_name("user_login")
    >>>
    >>> # 验证参数名
    >>> is_valid, error = validate_param_name("user_id")
    >>>
    >>> # 验证并清理字符串输入
    >>> is_valid, sanitized = sanitize_and_validate_string(
    ...     "test value",
    ...     max_length=200,
    ...     field_name="name"
    ... )
"""

import re
import html
from typing import Tuple, Optional, Dict, Any
from backend.core.database import get_db_connection
from backend.core.logging import get_logger

logger = get_logger(__name__)

# 验证模式正则表达式
EVENT_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9._]*$", re.IGNORECASE)
PARAM_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$", re.IGNORECASE)


# ============================================================================
# 输入验证函数
# ============================================================================


def validate_event_name(event_name: str) -> Tuple[bool, Optional[str]]:
    """
    验证事件名称格式

    规则:
    - 必须以字母开头
    - 只能包含字母、数字、点(.)和下划线(_)
    - 长度不超过100个字符

    Args:
        event_name: 要验证的事件名称

    Returns:
        Tuple[is_valid, error_message]
        - is_valid: 验证是否通过
        - error_message: 错误消息（验证失败时）

    Example:
        >>> is_valid, error = validate_event_name("user_login")
        >>> if is_valid:
        ...     print("Valid event name")
        ... else:
        ...     print(f"Error: {error}")
    """
    if not event_name or not event_name.strip():
        return False, "事件名不能为空"

    event_name = event_name.strip()

    if not EVENT_NAME_PATTERN.match(event_name):
        return False, "事件名格式不正确，应只包含字母、数字、点和下划线，且以字母开头"

    if len(event_name) > 100:
        return False, "事件名长度不能超过100个字符"

    return True, None


def validate_param_name(param_name: str) -> Tuple[bool, Optional[str]]:
    """
    验证参数名称格式

    规则:
    - 必须以字母开头
    - 只能包含字母、数字和下划线(_)
    - 长度不超过100个字符

    Args:
        param_name: 要验证的参数名称

    Returns:
        Tuple[is_valid, error_message]
        - is_valid: 验证是否通过
        - error_message: 错误消息（验证失败时）

    Example:
        >>> is_valid, error = validate_param_name("user_id")
        >>> if is_valid:
        ...     print("Valid parameter name")
        ... else:
        ...     print(f"Error: {error}")
    """
    if not param_name or not param_name.strip():
        return False, "参数名不能为空"

    param_name = param_name.strip()

    if not PARAM_NAME_PATTERN.match(param_name):
        return False, "参数名格式不正确，应只包含字母、数字和下划线，且以字母开头"

    if len(param_name) > 100:
        return False, "参数名长度不能超过100个字符"

    return True, None


def validate_game_gid(game_gid: int) -> Tuple[bool, Optional[str]]:
    """
    验证游戏GID

    Args:
        game_gid: 游戏业务GID

    Returns:
        Tuple[is_valid, error_message]
        - is_valid: 验证是否通过
        - error_message: 错误消息（验证失败时）

    Example:
        >>> is_valid, error = validate_game_gid(10000147)
        >>> if not is_valid:
        ...     return error_response(error, status_code=400)
    """
    if not isinstance(game_gid, int):
        return False, "游戏GID必须是整数"

    if game_gid <= 0:
        return False, "游戏GID必须是正整数"

    if game_gid > 99999999:
        return False, "游戏GID值过大"

    return True, None


def validate_game_id(game_gid: int) -> Tuple[bool, Optional[str]]:
    """
    验证游戏ID（GID的别名，为了向后兼容）

    Args:
        game_gid: 游戏ID

    Returns:
        Tuple[is_valid, error_message]
    """
    return validate_game_gid(game_gid)


# ============================================================================
# 安全验证函数
# ============================================================================

# SQL注入检测模式
SQL_INJECTION_PATTERN = re.compile(
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|OR)\b|\-\-|;|\|)", re.IGNORECASE
)


def validate_sql_safe(text: str) -> Tuple[bool, Optional[str]]:
    """
    检查潜在的SQL注入模式

    Args:
        text: 要验证的文本

    Returns:
        Tuple[is_safe, error_message]
        - is_safe: 是否安全
        - error_message: 错误消息（检测到注入模式时）

    Example:
        >>> is_safe, error = validate_sql_safe("user_input")
        >>> if not is_safe:
        ...     logger.warning(f"SQL injection detected: {error}")
    """
    if not text:
        return True, None

    text_upper = text.upper()

    # 检查危险的SQL关键字
    if SQL_INJECTION_PATTERN.search(text):
        return False, "输入包含潜在的SQL注入模式"

    return True, None


def sanitize_and_validate_string(
    value, max_length: int = 200, field_name: str = "field", allow_empty: bool = False
) -> Tuple[bool, str]:
    """
    清理和验证字符串输入（统一安全工具函数）

    防止XSS攻击、输入长度溢出等安全问题。

    Args:
        value: 要验证的值（可以是任意类型）
        max_length: 最大允许长度（默认200）
        field_name: 字段名称（用于错误消息）
        allow_empty: 是否允许空字符串（默认False）

    Returns:
        Tuple[is_valid, sanitized_value_or_error_message]
        - is_valid: 验证是否通过
        - result: 如果通过，返回清理后的值；否则返回错误消息

    Examples:
        >>> # 必填字段示例
        >>> is_valid, result = sanitize_and_validate_string(
        ...     data.get("name"),
        ...     max_length=200,
        ...     field_name="name",
        ...     allow_empty=False
        ... )
        >>> if not is_valid:
        ...     return {"error": result}
        >>> name = result

        >>> # 可选字段示例
        >>> is_valid, result = sanitize_and_validate_string(
        ...     data.get("description", ""),
        ...     max_length=1000,
        ...     field_name="description",
        ...     allow_empty=True
        ... )
        >>> if not is_valid:
        ...     return {"error": result}
        >>> description = result

    Security Features:
        - XSS防护: 使用html.escape()转义HTML特殊字符
        - 长度验证: 防止数据库截断或DoS攻击
        - 空值处理: 统一的空字符串检查
        - 类型安全: 自动转换为字符串
    """
    # 处理None值
    if value is None:
        if not allow_empty:
            return False, f"{field_name} cannot be empty"
        return True, ""

    # 转换为字符串并去除首尾空格
    value = str(value).strip()

    # 检查空字符串
    if len(value) == 0:
        if not allow_empty:
            return False, f"{field_name} cannot be empty"
        return True, ""

    # 检查长度限制
    if len(value) > max_length:
        return False, f"{field_name} exceeds maximum length of {max_length} characters"

    # 防止XSS攻击 - 转义HTML特殊字符
    # 这会转换: < → &lt;, > → &gt;, & → &amp;, " → &quot;, ' → &#x27;
    sanitized = html.escape(value)

    return True, sanitized


# ============================================================================
# 业务验证函数
# ============================================================================


def validate_game_exists(game_gid: int) -> Tuple[bool, Optional[Dict], Optional[str]]:
    """
    验证游戏是否存在

    Args:
        game_gid: 游戏业务GID

    Returns:
        Tuple[is_valid, game_dict, error_message]
        - is_valid: 游戏是否存在
        - game_dict: 游戏字典（存在时）
        - error_message: 错误消息（不存在时）

    Example:
        >>> is_valid, game, error = validate_game_exists(10000147)
        >>> if not is_valid:
        ...     return error_response(error, status_code=404)
        >>> print(game['name'])
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM games WHERE gid = ?", (game_gid,))
        game = cursor.fetchone()
        conn.close()

        if game:
            return True, dict(game), None
        else:
            return False, None, f"游戏GID {game_gid} 不存在"

    except Exception as e:
        logger.error(f"Error validating game exists: {e}")
        return False, None, f"验证游戏存在性时发生错误: {str(e)}"


def check_games_exist() -> Tuple[bool, Optional[str]]:
    """
    检查系统中是否存在任何游戏

    Returns:
        Tuple[has_games, error_message]
        - has_games: 是否存在游戏
        - error_message: 错误消息

    Example:
        >>> has_games, error = check_games_exist()
        >>> if not has_games:
        ...     flash("请先创建游戏", "warning")
        ...     return redirect(url_for('games.new_game'))
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM games")
        result = cursor.fetchone()
        conn.close()

        if result and result["count"] > 0:
            return True, None
        else:
            return False, "系统中还没有游戏，请先创建游戏"

    except Exception as e:
        logger.error(f"Error checking games exist: {e}")
        return False, f"检查游戏时发生错误: {str(e)}"


# ============================================================================
# 必填字段验证
# ============================================================================


def validate_required_fields(
    data: Dict[str, Any], required_fields: list, field_aliases: Optional[Dict[str, str]] = None
) -> Tuple[bool, Optional[str]]:
    """
    验证必填字段

    Args:
        data: 数据字典
        required_fields: 必填字段列表
        field_aliases: 字段别名映射（用于错误消息）

    Returns:
        Tuple[is_valid, error_message]
        - is_valid: 验证是否通过
        - error_message: 错误消息（验证失败时）

    Example:
        >>> data = {"name": "test", "value": "123"}
        >>> required = ["name", "value", "type"]
        >>> is_valid, error = validate_required_fields(data, required)
        >>> if not is_valid:
        ...     return {"error": error}
    """
    missing_fields = []

    for field in required_fields:
        if field not in data or not data[field]:
            # 使用别名（如果有）作为错误消息
            alias = field_aliases.get(field, field) if field_aliases else field
            missing_fields.append(alias)

    if missing_fields:
        error_msg = f"Missing required fields: {', '.join(missing_fields)}"
        return False, error_msg

    return True, None


# 导出列表
__all__ = [
    # 输入验证
    "validate_event_name",
    "validate_param_name",
    "validate_game_gid",
    "validate_game_id",
    "validate_required_fields",
    # 安全验证
    "validate_sql_safe",
    "sanitize_and_validate_string",
    # 业务验证
    "validate_game_exists",
    "check_games_exist",
    # 正则模式
    "EVENT_NAME_PATTERN",
    "PARAM_NAME_PATTERN",
    "SQL_INJECTION_PATTERN",
]
