#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Request Validators Module

Provides decorators for validating HTTP requests including content type,
content length, and sanitizing input data.
"""

from functools import wraps
from typing import Callable

from flask import jsonify, request


def require_json(f: Callable) -> Callable:
    """
    Decorator to require JSON content type for API routes

    Usage:
        @app.route('/api/events', methods=['POST'])
        @require_json
        def create_event():
            ...

    Args:
        f: Flask route function

    Returns:
        Wrapped function that requires JSON
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return (
                jsonify({"success": False, "error": "Content-Type must be application/json"}),
                400,
            )
        return f(*args, **kwargs)

    return decorated_function


def validate_content_length(max_size: int):
    """
    Validate request content length

    Args:
        max_size: Maximum content length in bytes

    Usage:
        @app.route('/upload', methods=['POST'])
        @validate_content_length(10 * 1024 * 1024)  # 10MB
        def upload_file():
            ...
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            content_length = request.content_length
            if content_length and content_length > max_size:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": f"Request too large. Maximum size is {max_size} bytes.",
                        }
                    ),
                    413,
                )
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal attacks

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    from werkzeug.utils import secure_filename

    return secure_filename(filename)


__all__ = [
    "require_json",
    "validate_content_length",
    "sanitize_filename",
]
