#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Security Headers Module

Provides security header middleware to enhance HTTP response security.
"""

import os

from flask import request


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

    # 🆕 开发模式: 检测是否为开发环境
    is_dev = (
        os.environ.get("FLASK_ENV") == "development"
        or os.environ.get("FLASK_DEBUG", "").lower() == "true"
    )

    if is_dev:
        # 开发模式: 放宽CSP, 允许Vite开发服务器
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
        # 生产模式: 严格的CSP策略
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


__all__ = ["add_security_headers"]
