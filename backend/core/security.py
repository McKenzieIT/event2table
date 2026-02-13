#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Security Module
Provides security utilities and middleware for the application
"""

import secrets
import time
from functools import wraps
from typing import Callable, Optional, Tuple

from flask import request, session, jsonify, abort
from backend.core.logging import get_logger

logger = get_logger(__name__)


# Rate limiting constants
DEFAULT_RATE_LIMIT_REQUESTS = 100  # Default max requests per window
DEFAULT_RATE_LIMIT_WINDOW = 3600  # Default window: 1 hour in seconds
STRICT_RATE_LIMIT_REQUESTS = 50  # Stricter limit for sensitive endpoints
STRICT_RATE_LIMIT_WINDOW = 60  # Stricter window: 1 minute in seconds

# Simple in-memory rate limiter (for production, use Redis or similar)
_rate_limit_store: dict = {}


def generate_csrf_token() -> str:
    """
    Generate a secure CSRF token

    Returns:
        Random CSRF token
    """
    return secrets.token_hex(32)


def validate_csrf_token(token: Optional[str]) -> bool:
    """
    Validate CSRF token against session

    Args:
        token: Token to validate

    Returns:
        True if token is valid
    """
    if not token:
        return False

    session_token = session.get("csrf_token")
    if not session_token:
        return False

    return secrets.compare_digest(token, session_token)


def csrf_protect(f: Callable) -> Callable:
    """
    Decorator to protect routes from CSRF attacks

    Usage:
        @app.route('/form', methods=['POST'])
        @csrf_protect
        def handle_form():
            ...

    Args:
        f: Flask route function

    Returns:
        Wrapped function with CSRF protection
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Only protect state-changing methods
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            # Skip CSRF validation in testing mode
            from flask import current_app

            if not current_app.config.get("TESTING", False):
                token = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")
                if not validate_csrf_token(token):
                    logger.warning(f"CSRF validation failed for {request.endpoint}")
                    return jsonify({"success": False, "error": "Invalid CSRF token"}), 403

        return f(*args, **kwargs)

    return decorated_function


def rate_limit(
    max_requests: int = DEFAULT_RATE_LIMIT_REQUESTS, window_seconds: int = DEFAULT_RATE_LIMIT_WINDOW
):
    """
    Rate limiting decorator

    Args:
        max_requests: Maximum number of requests allowed
        window_seconds: Time window in seconds

    Usage:
        @app.route('/api/events')
        @rate_limit(max_requests=STRICT_RATE_LIMIT_REQUESTS, window_seconds=STRICT_RATE_LIMIT_WINDOW)
        def list_events():
            ...
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client identifier
            key = f"{request.remote_addr}:{request.endpoint}"

            now = int(time.time())
            window_start = now - window_seconds

            # Clean old entries
            if key in _rate_limit_store:
                _rate_limit_store[key] = [t for t in _rate_limit_store[key] if t > window_start]
            else:
                _rate_limit_store[key] = []

            # Check rate limit
            if len(_rate_limit_store[key]) >= max_requests:
                logger.warning(f"Rate limit exceeded for {key}")
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds.",
                        }
                    ),
                    429,
                )

            # Add current request
            _rate_limit_store[key].append(now)

            return f(*args, **kwargs)

        return decorated_function

    return decorator


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


def init_csrf_protection(app):
    """
    Initialize CSRF protection for the application

    This should be called after the Flask app is created

    Args:
        app: Flask application instance
    """
    from flask import g

    @app.before_request
    def ensure_csrf_token():
        """
        Ensure CSRF token exists in session before each request.

        This before_request hook automatically generates a CSRF token
        if one doesn't exist in the current session.

        Args:
            None

        Returns:
            None
        """
        if "csrf_token" not in session:
            session["csrf_token"] = generate_csrf_token()


def add_security_headers(response):
    """
    Add security headers to response

    Args:
        response: Flask response object

    Returns:
        Response with security headers added
    """
    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "SAMEORIGIN"

    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Enable XSS filter
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # 🆕 开发模式：检测是否为开发环境
    import os

    is_dev = (
        os.environ.get("FLASK_ENV") == "development"
        or os.environ.get("FLASK_DEBUG", "").lower() == "true"
    )

    if is_dev:
        # 开发模式：放宽CSP，允许Vite开发服务器
        vite_dev_url = os.environ.get("VITE_DEV_URL", "http://localhost:5173")
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            f"script-src 'self' 'unsafe-inline' 'unsafe-eval' {vite_dev_url} http://localhost:* http://127.0.0.1:* https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            f"style-src 'self' 'unsafe-inline' {vite_dev_url} http://localhost:* http://127.0.0.1:* https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
            f"font-src 'self' data: https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.gstatic.com https://fonts.googleapis.com; "
            f"img-src 'self' data: https://cdn.jsdelivr.net https://picsum.photos; "
            f"connect-src 'self' {vite_dev_url} http://localhost:* http://127.0.0.1:* ws://localhost:* ws://127.0.0.1:* https://cdn.jsdelivr.net"
        )
    else:
        # 生产模式：严格的CSP策略
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
            "font-src 'self' data: https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.gstatic.com https://fonts.googleapis.com; "
            "img-src 'self' data: https://cdn.jsdelivr.net https://picsum.photos; "
            "connect-src 'self' https://cdn.jsdelivr.net"
        )

    # Referrer Policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    return response


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
