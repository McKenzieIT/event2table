#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backend core security module

Provides security utilities including SQL injection prevention,
input validation, output encoding, CSRF protection, rate limiting,
and security headers.
"""

# SQL validation
from .sql_validator import SQLValidator

# Authentication and authorization
from .authentication import (
    authenticated,
    check_auth_context,
    check_user_permission,
    require_permission,
)

# CSRF protection
from .csrf import (
    generate_csrf_token,
    init_csrf_protection,
    csrf_protect,
    validate_csrf_token,
)

# Rate limiting
from .rate_limiter import (
    rate_limit,
    DEFAULT_RATE_LIMIT_REQUESTS,
    DEFAULT_RATE_LIMIT_WINDOW,
    STRICT_RATE_LIMIT_REQUESTS,
    STRICT_RATE_LIMIT_WINDOW,
)

# Security headers
from .headers import add_security_headers

# Request validators
from .validators import (
    require_json,
    validate_content_length,
    sanitize_filename,
)

# Path validation
from .path_validator import PathValidator

# Error sanitization
from .error_sanitizer import sanitize_error

__all__ = [
    # SQL validation
    'SQLValidator',
    # Authentication and authorization
    'authenticated',
    'require_permission',
    'check_auth_context',
    'check_user_permission',
    # CSRF protection
    'generate_csrf_token',
    'validate_csrf_token',
    'csrf_protect',
    'init_csrf_protection',
    # Rate limiting
    'rate_limit',
    'DEFAULT_RATE_LIMIT_REQUESTS',
    'DEFAULT_RATE_LIMIT_WINDOW',
    'STRICT_RATE_LIMIT_REQUESTS',
    'STRICT_RATE_LIMIT_WINDOW',
    # Security headers
    'add_security_headers',
    # Request validators
    'require_json',
    'validate_content_length',
    'sanitize_filename',
    # Path validation
    'PathValidator',
    # Error sanitization
    'sanitize_error',
]
