#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存监控中间件
================

为Flask应用添加缓存相关的HTTP响应头

版本: 1.0.0
日期: 2026-03-10
"""

import logging
import time

from flask import g, request

logger = logging.getLogger(__name__)


def init_cache_monitoring_middleware(app):
    """
    初始化缓存监控中间件

    在请求开始时记录时间, 在响应时添加缓存状态头

    Args:
        app: Flask应用实例
    """

    @app.before_request
    def before_request():
        """请求开始: 记录开始时间"""
        g.cache_start_time = time.time()
        g.cache_status = None
        g.cache_key = None

    @app.after_request
    def after_request(response):
        """请求结束: 添加缓存状态头"""
        # 如果在缓存装饰器中设置了缓存状态
        if hasattr(g, 'cache_status') and g.cache_status:
            response.headers['X-Cache-Status'] = g.cache_status

        if hasattr(g, 'cache_key') and g.cache_key:
            # 只显示缓存键的哈希值(防止信息泄露)
            import hashlib

            key_hash = hashlib.sha256(g.cache_key.encode()).hexdigest()[:8]
            response.headers['X-Cache-Key'] = key_hash

        # 添加响应时间头
        if hasattr(g, 'cache_start_time'):
            response_time_ms = (time.time() - g.cache_start_time) * 1000
            response.headers['X-Response-Time'] = f"{response_time_ms:.2f}ms"

        return response

    logger.info("✅ 缓存监控中间件已初始化")


def set_cache_context(status: str, key: str | None = None):
    """
    设置缓存上下文（供装饰器使用）

    Args:
        status: 缓存状态 ('HIT' 或 'MISS')
        key: 缓存键（可选）
    """
    from flask import g

    g.cache_status = status
    if key:
        g.cache_key = key


logger.info("✅ 缓存监控中间件模块已加载 (1.0.0)")
