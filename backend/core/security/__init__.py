#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backend core security module

Provides security utilities including SQL injection prevention,
input validation, and output encoding.
"""

from .sql_validator import SQLValidator

# 缓存安全模块 (2026-02-24新增)
try:
    from .cache_key_validator import CacheKeyValidator
    from .sensitive_data_filter import SensitiveDataFilter, SafeLoggerAdapter
    from .path_validator import PathValidator
    CACHE_SECURITY_AVAILABLE = True
except ImportError:
    CACHE_SECURITY_AVAILABLE = False

__all__ = [
    'SQLValidator',
    'CacheKeyValidator',
    'SensitiveDataFilter',
    'SafeLoggerAdapter',
    'PathValidator',
]
