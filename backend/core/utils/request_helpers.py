#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Request Handling Module

Provides request validation and error handling decorators for API endpoints.
"""

from functools import wraps
from typing import Callable, List, Tuple

from flask import flash, redirect, url_for

from backend.core.logging import get_logger
from backend.core.utils.response import json_error_response

logger = get_logger(__name__)


def validate_json_request(required_fields: List[str] | None = None) -> Tuple[bool, any, str]:
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


def handle_errors(func):
    """
    Decorator for consistent error handling in routes

    Catches common exceptions and provides user-friendly error messages
    while logging detailed errors for debugging.

    Usage:
        @events_bp.route('/events/<int:id>/edit', methods=['GET', 'POST'])
        @handle_errors
        def edit_event(id):
            # ... existing code ...
    """
    from functools import wraps

    from backend.core.errors import DatabaseError, DuplicateError, NotFoundError, ValidationError

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


def handle_api_errors(func: Callable) -> Callable:
    """
    API错误处理装饰器

    统一处理API异常, 确保所有错误都返回标准JSON格式
    """
    from backend.core.errors import DatabaseError, DuplicateError, NotFoundError, ValidationError

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


__all__ = [
    'validate_json_request',
    'handle_errors',
    'handle_api_errors',
]
