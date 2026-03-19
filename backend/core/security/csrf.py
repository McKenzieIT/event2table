#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSRF Protection Module

Provides CSRF token generation, validation, and route protection decorators.
"""

import secrets
from functools import wraps
from typing import Callable, Optional

from flask import jsonify, request, session

from backend.core.logging import get_logger

logger = get_logger(__name__)


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


__all__ = [
    "generate_csrf_token",
    "validate_csrf_token",
    "csrf_protect",
    "init_csrf_protection",
]
