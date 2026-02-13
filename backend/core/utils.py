#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilities Module
Common utility functions to reduce code duplication

This module is organized into the following sections:
- Custom Exceptions
- Security Functions (XSS, SQL injection prevention)
- Validation Functions
- Database Transaction Management
- Decorators
- Game Context Helpers
- Type Conversion Helpers
- Database Query Helpers
- API Response Helpers
- HQL Exception Classes
- Security Utility Functions
"""

import html
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple, Callable
from flask import flash, redirect, url_for, jsonify
from contextlib import contextmanager
from functools import wraps

from backend.core.database import get_db_connection
from backend.core.logging import get_logger
from backend.core.config import ODSDatabase, CommonParamConfig

logger = get_logger(__name__)


# ============================================================================
# Custom Exceptions
# ============================================================================
class ValidationError(Exception):
    """验证错误"""

    def __init__(self, message: str, field: str = None):
        super().__init__(message)
        self.field = field


class NotFoundError(Exception):
    """资源未找到错误"""

    pass


class DuplicateError(Exception):
    """重复数据错误"""

    pass


class DatabaseError(Exception):
    """数据库错误"""

    pass


# ============================================================================
# Security Functions (XSS, SQL Injection Prevention)
# ============================================================================


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


# Sanitization patterns
# **代码质量优化**: Enhanced XSS patterns to catch more attack vectors
XSS_PATTERN = re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE)
XSS_EVENT_PATTERN = re.compile(r"on\w+\s*=", re.IGNORECASE)  # onclick=, onload=, etc.
XSS_JS_PATTERN = re.compile(r"javascript:", re.IGNORECASE)  # javascript:伪协议
XSS_DATA_PATTERN = re.compile(r"data:text/html", re.IGNORECASE)  # data:伪协议
XSS_IFRAME_PATTERN = re.compile(r"<iframe[^>]*>.*?</iframe>", re.IGNORECASE)
XSS_OBJECT_PATTERN = re.compile(r"<object[^>]*>.*?</object>", re.IGNORECASE)
XSS_EMBED_PATTERN = re.compile(r"<embed[^>]*>", re.IGNORECASE)
XSS_LINK_PATTERN = re.compile(r"<link[^>]*>", re.IGNORECASE)
XSS_META_PATTERN = re.compile(r"<meta[^>]*>", re.IGNORECASE)
XSS_STYLE_PATTERN = re.compile(r"<style[^>]*>.*?</style>", re.IGNORECASE)
XSS_FORM_PATTERN = re.compile(r"<form[^>]*>.*?</form>", re.IGNORECASE)
XSS_INPUT_PATTERN = re.compile(r"<input[^>]*>", re.IGNORECASE)

SQL_INJECTION_PATTERN = re.compile(
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|OR)\b|\-\-|;|\|)", re.IGNORECASE
)
EVENT_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9._]*$", re.IGNORECASE)
PARAM_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$", re.IGNORECASE)


def sanitize_html(text: str) -> str:
    """
    **代码质量优化**: Enhanced HTML sanitization to prevent XSS attacks

    Removes dangerous HTML tags, JavaScript event handlers, and
    escapes HTML special characters to prevent XSS attacks.

    Args:
        text: Text to sanitize

    Returns:
        Sanitized text with dangerous HTML removed
    """
    if not text:
        return ""

    # Remove dangerous HTML tags
    text = XSS_PATTERN.sub("", text)  # <script> tags
    text = XSS_IFRAME_PATTERN.sub("", text)  # <iframe> tags
    text = XSS_OBJECT_PATTERN.sub("", text)  # <object> tags
    text = XSS_EMBED_PATTERN.sub("", text)  # <embed> tags
    text = XSS_LINK_PATTERN.sub("", text)  # <link> tags
    text = XSS_META_PATTERN.sub("", text)  # <meta> tags
    text = XSS_STYLE_PATTERN.sub("", text)  # <style> tags
    text = XSS_FORM_PATTERN.sub("", text)  # <form> tags
    text = XSS_INPUT_PATTERN.sub("", text)  # <input> tags

    # Remove JavaScript event handlers (onclick, onload, etc.)
    text = XSS_EVENT_PATTERN.sub("", text)

    # Remove javascript: and data: pseudo-protocols
    text = XSS_JS_PATTERN.sub("", text)
    text = XSS_DATA_PATTERN.sub("", text)

    # Escape HTML special characters (do this last to catch any remaining)
    html_escape_table = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#x27;",
        "`": "&#96;",  # Backtick (ES6 template literals)
        "=": "&#61;",  # Equals sign (can be used in attributes)
    }
    return "".join(html_escape_table.get(c, c) for c in text)


def escape_output(text: str) -> str:
    """
    **代码质量优化**: Escape text for safe output in HTML templates

    Note: Jinja2 auto-escapes by default, but this is for manual output
    or when bypassing auto-escaping.

    Args:
        text: Text to escape

    Returns:
        HTML-escaped text
    """
    if not text:
        return ""

    # Use comprehensive HTML escaping
    return sanitize_html(text)


def validate_event_name(event_name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate event name format

    Args:
        event_name: Event name to validate

    Returns:
        Tuple of (is_valid, error_message)
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
    Validate parameter name format

    Args:
        param_name: Parameter name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not param_name or not param_name.strip():
        return False, "参数名不能为空"

    param_name = param_name.strip()

    if not PARAM_NAME_PATTERN.match(param_name):
        return False, "参数名格式不正确，应只包含字母、数字和下划线，且以字母开头"

    if len(param_name) > 100:
        return False, "参数名长度不能超过100个字符"

    return True, None


def validate_sql_safe(text: str) -> Tuple[bool, Optional[str]]:
    """
    Check for potential SQL injection patterns

    Args:
        text: Text to validate

    Returns:
        Tuple of (is_safe, error_message)
    """
    if not text:
        return True, None

    text_upper = text.upper()

    # Check for dangerous SQL keywords
    if SQL_INJECTION_PATTERN.search(text):
        return False, "输入包含潜在的SQL注入模式"

    return True, None


def sanitize_user_input(text: str, allow_html: bool = False) -> str:
    """
    Sanitize user input for safe storage and display

    Args:
        text: Text to sanitize
        allow_html: Whether to allow HTML (currently not supported, always sanitized)

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    text = text.strip()

    # Always sanitize HTML for security
    text = sanitize_html(text)

    # Limit length
    if len(text) > 10000:
        text = text[:10000]

    return text


@contextmanager
def db_transaction():
    """
    Context manager for database transactions with automatic commit/rollback

    Usage:
        with db_transaction() as conn:
            conn.execute(...)
            # Auto commits on success, rolls back on exception
    """
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
        logger.debug("Database transaction committed successfully")
    except Exception as e:
        conn.rollback()
        logger.error(f"Database transaction rolled back due to error: {e}")
        raise
    finally:
        conn.close()


def handle_errors(func):
    """
    **代码质量优化**: Decorator for consistent error handling in routes

    Catches common exceptions and provides user-friendly error messages
    while logging detailed errors for debugging.

    Usage:
        @events_bp.route('/events/<int:id>/edit', methods=['GET', 'POST'])
        @handle_errors
        def edit_event(id):
            # ... existing code ...
    """
    from functools import wraps
    from exceptions import ValidationError, DatabaseError, NotFoundError, DuplicateError

    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            flash(f"验证错误: {e.message}", "error")
            logger.warning(f"Validation error in {func.__name__}: {e.message}")
        except NotFoundError as e:
            flash(f"未找到: {str(e)}", "error")
            logger.warning(f"Not found in {func.__name__}: {str(e)}")
        except DuplicateError as e:
            flash(f"重复记录: {str(e)}", "error")
            logger.warning(f"Duplicate in {func.__name__}: {str(e)}")
        except DatabaseError as e:
            flash(f"数据库错误: 请稍后重试", "error")
            logger.error(f"Database error in {func.__name__}: {str(e)}", exc_info=True)
        except Exception as e:
            flash(f"系统错误: 请联系管理员", "error")
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)

        # Redirect to a safe location (can be customized per route)
        return redirect(url_for("events.list_events"))

    return decorated_function


def validate_game_exists(game_gid: int) -> Tuple[bool, Optional[Dict], Optional[str]]:
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


def batch_execute(conn, sql: str, params_list: List[Tuple]) -> int:
    """
    Execute SQL statement multiple times with different parameters

    Args:
        conn: Database connection
        sql: SQL statement with placeholders
        params_list: List of parameter tuples

    Returns:
        Number of rows affected
    """
    cursor = conn.cursor()
    for params in params_list:
        cursor.execute(sql, params)
    return cursor.rowcount


def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert a value to integer

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Integer value or default
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_str(value: Any, default: str = "") -> str:
    """
    Safely convert a value to string

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        String value or default
    """
    try:
        return str(value).strip()
    except (ValueError, TypeError):
        return default


def validate_required_fields(
    data: Dict[str, Any], required_fields: List[str]
) -> Tuple[bool, Optional[str]]:
    """
    Validate that all required fields are present and non-empty

    Args:
        data: Dictionary of field values
        required_fields: List of required field names

    Returns:
        Tuple of (is_valid, error_message)
    """
    for field in required_fields:
        value = data.get(field, "").strip()
        if not value:
            return False, f"请填写必填字段: {field}"
    return True, None


def format_error_response(error: Exception, context: str = "") -> Dict[str, Any]:
    """
    Format an error into a standardized response dictionary

    Args:
        error: The exception that occurred
        context: Additional context about where the error occurred

    Returns:
        Dictionary with error information
    """
    return {
        "success": False,
        "error": str(error),
        "error_type": type(error).__name__,
        "context": context,
    }


# ==================== #
# API Response Helpers #
# ==================== #


def success_response(
    data: Any = None, message: str = None, status_code: int = 200, **kwargs
) -> Tuple[Dict[str, Any], int]:
    """
    Create a standardized success response

    Args:
        data: Response data
        message: Optional message
        status_code: HTTP status code (default: 200)
        **kwargs: Additional fields to include in response

    Returns:
        Tuple of (response_dict, status_code)

    Example:
        return success_response(data={'id': 1}, message='Created successfully')
        # Returns: ({'success': True, 'data': {'id': 1}, 'message': 'Created successfully'}, 200)
        return success_response(data={'id': 1}, message='Created successfully', status_code=201)
        # Returns: ({'success': True, 'data': {'id': 1}, 'message': 'Created successfully'}, 201)
    """
    response = {"success": True, "timestamp": datetime.now(timezone.utc).isoformat()}
    if data is not None:
        response["data"] = data
    if message:
        response["message"] = message
    response.update(kwargs)
    return response, status_code


def error_response(error: str, status_code: int = 400, **kwargs) -> Tuple[Dict[str, Any], int]:
    """
    Create a standardized error response

    Args:
        error: Error message
        status_code: HTTP status code (default: 400)
        **kwargs: Additional fields to include in response

    Returns:
        Tuple of (response_dict, status_code)

    Example:
        return error_response('Invalid input', status_code=400, field='name')
        # Returns: ({'success': False, 'error': 'Invalid input', 'field': 'name'}, 400)
    """
    response = {
        "success": False,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "error": error,
    }
    response.update(kwargs)
    return response, status_code


def validate_json_request(required_fields: List[str] = None) -> Tuple[bool, Any, Optional[str]]:
    """
    Validate JSON request data

    Args:
        required_fields: List of required field names

    Returns:
        Tuple of (is_valid, data, error_message)
    """
    from flask import request

    if not request.is_json:
        return False, None, "Request must be JSON"

    data = request.get_json()
    if not data:
        return False, None, "Invalid JSON data"

    if required_fields:
        missing = [f for f in required_fields if f not in data or not data[f]]
        if missing:
            return False, None, f'Missing required fields: {", ".join(missing)}'

    return True, data, None


def json_success_response(data: Any = None, message: str = None, **kwargs):
    """
    Return a JSON success response with proper headers

    This is a convenience wrapper that combines success_response() and jsonify()
    to reduce code duplication across the codebase.

    Args:
        data: Response data
        message: Optional message
        **kwargs: Additional fields to include in response

    Returns:
        Tuple of (jsonify_response, status_code)

    Example:
        return json_success_response(data={'id': 1}, message='Created successfully')
        # Returns: (jsonify({'success': True, 'data': {'id': 1}, 'message': '...'}), 200)
    """
    from flask import jsonify

    response, status = success_response(data, message, **kwargs)
    return jsonify(response), status


def handle_api_errors(func: Callable) -> Callable:
    """
    API错误处理装饰器

    统一处理API异常，确保所有错误都返回标准JSON格式
    """

    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            error_msg = str(e)
            if hasattr(e, "field"):
                error_msg = f"Validation failed for field '{e.field}': {error_msg}"
            return json_error_response(error_msg, status_code=400)
        except NotFoundError as e:
            return json_error_response(str(e), status_code=404)
        except DuplicateError as e:
            return json_error_response(str(e), status_code=409)
        except DatabaseError as e:
            logger.error(f"Database error in {func.__name__}: {str(e)}")
            return json_error_response("Database operation failed", status_code=500)
        except Exception as e:
            logger.exception(f"Unexpected error in {func.__name__}: {str(e)}")
            return json_error_response("Internal server error", status_code=500)

    return decorated_function


def json_error_response(error: str, status_code: int = 400, **kwargs):
    """
    Return a JSON error response with proper headers

    This is a convenience wrapper that combines error_response() and jsonify()
    to reduce code duplication across the codebase.

    Args:
        error: Error message
        status_code: HTTP status code (default: 400)
        **kwargs: Additional fields to include in response

    Returns:
        Tuple of (jsonify_response, status_code)

    Example:
        return json_error_response('Invalid input', status_code=400, field='name')
        # Returns: (jsonify({'success': False, 'error': 'Invalid input', 'field': 'name'}), 400)
    """
    from flask import jsonify

    response, status = error_response(error, status_code, **kwargs)
    return jsonify(response), status


def validate_game_gid(game_gid: int) -> Tuple[bool, Optional[str]]:
    """
    验证游戏GID的有效性

    Args:
        game_gid: 游戏业务GID

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(game_gid, int):
        return False, "Game GID must be an integer"

    if game_gid <= 0:
        return False, "Game GID must be positive"

    game = fetch_one_as_dict("SELECT gid FROM games WHERE gid = ?", (game_gid,))
    if not game:
        return False, "Game not found"

    return True, None


def get_game_gid_param(request_obj, param_name: str = "game_gid") -> Optional[str]:
    """
    从请求中获取 game_gid 参数（支持字符串和整数类型）

    由于数据库中 games.gid 是 TEXT 类型，但部分代码使用 type=int，
    此函数提供统一的方式来获取和转换 game_gid 参数。

    Args:
        request_obj: Flask request 对象
        param_name: 参数名称（默认为 "game_gid"）

    Returns:
        game_gid 字符串，如果参数不存在返回 None

    Example:
        # 在视图函数中使用
        game_gid = get_game_gid_param(request)
        if not game_gid:
            return json_error_response("game_gid is required", status_code=400)

        # 现在 game_gid 是字符串类型，可以直接用于 SQL 查询
        game = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (game_gid,))
    """
    from flask import request

    # 尝试作为整数获取（向后兼容）
    value_int = request.args.get(param_name, type=int)
    if value_int is not None:
        return str(value_int)

    # 尝试作为字符串获取
    value_str = request.args.get(param_name, type=str)
    if value_str:
        return value_str.strip()

    # 参数不存在
    return None


# Deprecated alias for backward compatibility - use validate_game_gid instead
def validate_game_id(game_gid: int) -> Tuple[bool, Optional[str]]:
    """
    @deprecated Use validate_game_gid instead
    """
    return validate_game_gid(game_gid)


def safe_int_convert(value, default=0, min_value=None, max_value=None):
    """
    安全地转换为整数

    Args:
        value: 要转换的值
        default: 转换失败时的默认值
        min_value: 最小值限制
        max_value: 最大值限制

    Returns:
        转换后的整数
    """
    try:
        result = int(value)

        if min_value is not None and result < min_value:
            return default
        if max_value is not None and result > max_value:
            return default

        return result
    except (ValueError, TypeError):
        return default


def fetch_all_as_dict(query: str, params: Tuple = None) -> List[Dict[str, Any]]:
    """
    Execute a query and return all rows as dictionaries

    Args:
        query: SQL query string
        params: Query parameters (optional)

    Returns:
        List of row dictionaries

    Example:
        games = fetch_all_as_dict('SELECT * FROM games WHERE id = ?', (game_id,))
    """
    conn = get_db_connection()
    try:
        rows = conn.execute(query, params or ()).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def fetch_one_as_dict(query: str, params: Tuple = None) -> Optional[Dict[str, Any]]:
    """
    Execute a query and return one row as dictionary

    Args:
        query: SQL query string
        params: Query parameters (optional)

    Returns:
        Row dictionary or None if not found

    Example:
        game = fetch_one_as_dict('SELECT * FROM games WHERE id = ?', (game_id,))
    """
    conn = get_db_connection()
    try:
        row = conn.execute(query, params or ()).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def execute_write(query: str, params: Tuple = None, return_last_id: bool = False) -> int:
    """
    Execute a write query (INSERT, UPDATE, DELETE) and return affected row count or last inserted ID

    Args:
        query: SQL query string
        params: Query parameters (optional)
        return_last_id: If True, return last inserted row ID instead of rowcount

    Returns:
        Number of rows affected, or last inserted ID if return_last_id=True

    Example:
        execute_write('INSERT INTO games (name) VALUES (?)', ('Game1',))
        last_id = execute_write('INSERT INTO games (name) VALUES (?)', ('Game1',), return_last_id=True)
    """
    conn = get_db_connection()
    try:
        cursor = conn.execute(query, params or ())
        conn.commit()
        return cursor.lastrowid if return_last_id else cursor.rowcount
    finally:
        conn.close()


def execute_transaction(operations: List[Tuple[str, Tuple]]) -> int:
    """
    Execute multiple SQL operations in a single transaction

    Args:
        operations: List of (query, params) tuples

    Returns:
        Total number of rows affected

    Example:
        execute_transaction([
            ('UPDATE users SET score = score + 10 WHERE id = ?', (1,)),
            ('INSERT INTO logs (user_id, action) VALUES (?, ?)', (1, 'bonus'))
        ])
    """
    conn = get_db_connection()
    try:
        total_affected = 0
        for query, params in operations:
            cursor = conn.execute(query, params or ())
            total_affected += cursor.rowcount
        conn.commit()
        return total_affected
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_or_401(
    query: str, params: Tuple, error_message: str = "Resource not found"
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


# ==================== #
# Query Helper Functions #
# ==================== #


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
    return fetch_all_as_dict("""
        SELECT g.*,
               (SELECT COUNT(*) FROM log_events WHERE game_gid = g.gid) as event_count
        FROM games g
        ORDER BY g.name
    """)


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


# ==================== #
# Custom Exceptions     #
# ==================== #


class HQLGenerationError(Exception):
    """
    Base exception class for HQL generation errors.

    All HQL-related exceptions should inherit from this class to allow
    for easy exception handling and error categorization.

    Attributes:
        message (str): Error message
        node_id (str, optional): ID of the node causing the error
        node_type (str, optional): Type of the node
    """

    def __init__(self, message, node_id=None, node_type=None, **kwargs):
        """
        Initialize HQLGenerationError.

        Args:
            message (str): Error message
            node_id (str, optional): ID of the node causing the error
            node_type (str, optional): Type of the node
            **kwargs: Additional context information
        """
        self.message = message
        self.node_id = node_id
        self.node_type = node_type
        self.context = kwargs

        # Build full error message
        full_message = message
        if node_id:
            full_message += f" (node_id: {node_id})"
        if node_type:
            full_message += f" (node_type: {node_type})"

        super().__init__(full_message)


class EmptyFieldListError(HQLGenerationError):
    """
    Exception raised when a node's fieldList is empty.

    This occurs when a process/event node has no fields configured,
    which is required for UNION ALL and JOIN operations.

    Example:
        >>> raise EmptyFieldListError(
        ...     "节点的 fieldList 为空",
        ...     node_id="node_123",
        ...     node_type="process",
        ...     event_id=1
        ... )
    """

    def __init__(self, message, node_id=None, node_type=None, event_id=None, **kwargs):
        """
        Initialize EmptyFieldListError.

        Args:
            message (str): Error message
            node_id (str, optional): ID of the node with empty fieldList
            node_type (str, optional): Type of the node
            event_id (int, optional): Event ID if applicable
            **kwargs: Additional context information
        """
        self.event_id = event_id
        super().__init__(message, node_id, node_type, event_id=event_id, **kwargs)


class MissingJoinKeyError(HQLGenerationError):
    """
    Exception raised when a JOIN condition references a field
    that doesn't exist in the node's fieldList.

    This occurs when the JOIN conditions specify a field (e.g., role_id)
    that is not present in one of the joined tables' field configurations.

    Example:
        >>> raise MissingJoinKeyError(
        ...     "JOIN条件字段 'role_id' 在节点的 fieldList 中不存在",
        ...     node_id="node_123",
        ...     missing_key="role_id",
        ...     available_fields=["ds", "level"]
        ... )
    """

    def __init__(
        self,
        message,
        node_id=None,
        node_type=None,
        missing_key=None,
        available_fields=None,
        **kwargs,
    ):
        """
        Initialize MissingJoinKeyError.

        Args:
            message (str): Error message
            node_id (str, optional): ID of the node with missing field
            node_type (str, optional): Type of the node
            missing_key (str, optional): The missing field name
            available_fields (list, optional): List of available fields
            **kwargs: Additional context information
        """
        self.missing_key = missing_key
        self.available_fields = available_fields or []
        super().__init__(
            message,
            node_id,
            node_type,
            missing_key=missing_key,
            available_fields=available_fields,
            **kwargs,
        )


class InvalidNodeTypeError(HQLGenerationError):
    """
    Exception raised when a node has an invalid type for the operation.

    This occurs when a node that should be 'process' type is actually
    'union_all', 'join', 'output', or another type.

    Example:
        >>> raise InvalidNodeTypeError(
        ...     "左表节点类型必须是process",
        ...     node_id="node_123",
        ...     actual_type="union_all",
        ...     expected_type="process"
        ... )
    """

    def __init__(self, message, node_id=None, actual_type=None, expected_type=None, **kwargs):
        """
        Initialize InvalidNodeTypeError.

        Args:
            message (str): Error message
            node_id (str, optional): ID of the node with invalid type
            actual_type (str, optional): The actual node type
            expected_type (str, optional): The expected node type
            **kwargs: Additional context information
        """
        self.actual_type = actual_type
        self.expected_type = expected_type
        super().__init__(
            message, node_id, node_type=actual_type, expected_type=expected_type, **kwargs
        )


class MissingJoinConfigError(HQLGenerationError):
    """
    Exception raised when a JOIN node is missing required joinConfig.

    This occurs when a JOIN node doesn't have the necessary configuration
    to perform the join operation.

    Example:
        >>> raise MissingJoinConfigError(
        ...     "JOIN节点缺少joinConfig配置",
        ...     node_id="node_join_1"
        ... )
    """

    def __init__(self, message, node_id=None, **kwargs):
        """
        Initialize MissingJoinConfigError.

        Args:
            message (str): Error message
            node_id (str, optional): ID of the JOIN node
            **kwargs: Additional context information
        """
        super().__init__(message, node_id, node_type="join", **kwargs)


# ============================================================================
# Security Utility Functions
# ============================================================================


def sanitize_and_validate_string(
    value, max_length: int = 200, field_name: str = "field", allow_empty: bool = False
) -> Tuple[bool, str]:
    """
    清理和验证字符串输入（统一安全工具函数）

    防止 XSS 攻击、输入长度溢出等安全问题。

    Args:
        value: 要验证的值（可以是任意类型）
        max_length: 最大允许长度（默认 200）
        field_name: 字段名称（用于错误消息）
        allow_empty: 是否允许空字符串（默认 False）

    Returns:
        tuple: (is_valid, sanitized_value_or_error_message)
            - is_valid (bool): 验证是否通过
            - result (str): 如果通过，返回清理后的值；否则返回错误消息

    Examples:
        >>> # 必填字段示例
        >>> is_valid, result = sanitize_and_validate_string(
        ...     data.get("name"),
        ...     max_length=200,
        ...     field_name="name",
        ...     allow_empty=False
        ... )
        >>> if not is_valid:
        ...     return json_error_response(result, status_code=400)
        >>> name = result

        >>> # 可选字段示例
        >>> is_valid, result = sanitize_and_validate_string(
        ...     data.get("description", ""),
        ...     max_length=1000,
        ...     field_name="description",
        ...     allow_empty=True
        ... )
        >>> if not is_valid:
        ...     return json_error_response(result, status_code=400)
        >>> description = result

    Security Features:
        - XSS 防护: 使用 html.escape() 转义 HTML 特殊字符
        - 长度验证: 防止数据库截断或 DoS 攻击
        - 空值处理: 统一的空字符串检查
        - 类型安全: 自动转换为字符串
    """
    # 处理 None 值
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

    # 防止 XSS 攻击 - 转义 HTML 特殊字符
    # 这会转换: < → &lt;, > → &gt;, & → &amp;, " → &quot;, ' → &#x27;
    sanitized = html.escape(value)

    return True, sanitized
