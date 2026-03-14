#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backend core security module

Provides security utilities including SQL injection prevention,
input validation, and output encoding.
"""

from .sql_validator import SQLValidator

# 认证授权模块 (2026-03-09新增)
try:
    from .authentication import (
        authenticated,
        check_auth_context,
        check_user_permission,
        require_permission,
    )

    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

# 缓存安全模块 (2026-02-24新增)
try:
    from .cache_key_validator import CacheKeyValidator
    from .path_validator import PathValidator
    from .sensitive_data_filter import SafeLoggerAdapter, SensitiveDataFilter

    CACHE_SECURITY_AVAILABLE = True
except ImportError:
    CACHE_SECURITY_AVAILABLE = False

__all__ = [
    'SQLValidator',
    'authenticated',
    'require_permission',
    'check_auth_context',
    'check_user_permission',
    'CacheKeyValidator',
    'SensitiveDataFilter',
    'SafeLoggerAdapter',
    'PathValidator',
]
