#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rate Limiting Module

Provides rate limiting decorators to protect API endpoints from abuse.
"""

import time
from functools import wraps
from typing import Callable

from flask import jsonify, request

from backend.core.logging import get_logger

logger = get_logger(__name__)

# Rate limiting constants
DEFAULT_RATE_LIMIT_REQUESTS = 100  # Default max requests per window
DEFAULT_RATE_LIMIT_WINDOW = 3600  # Default window: 1 hour in seconds
STRICT_RATE_LIMIT_REQUESTS = 50  # Stricter limit for sensitive endpoints
STRICT_RATE_LIMIT_WINDOW = 60  # Stricter window: 1 minute in seconds

# Simple in-memory rate limiter (for production, use Redis or similar)
_rate_limit_store: dict = {}


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


__all__ = [
    "rate_limit",
    "DEFAULT_RATE_LIMIT_REQUESTS",
    "DEFAULT_RATE_LIMIT_WINDOW",
    "STRICT_RATE_LIMIT_REQUESTS",
    "STRICT_RATE_LIMIT_WINDOW",
]
