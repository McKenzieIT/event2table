#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Response Formatting Module

Provides standardized API response helpers for success and error responses.
"""

from datetime import datetime, timezone
from typing import Any, Tuple

from flask import jsonify


def success_response(
    data: Any = None, message: str = None, status_code: int = 200, **kwargs
) -> Tuple[dict, int]:
    """
    Create a standardized success response

    Args:
        data: Response data
        message: Optional message
        status_code: HTTP status code (default: 200)
        **kwargs: Additional fields to include in response

    Returns:
        Tuple of (response_dict, status_code)

    Example:
        return success_response(data={'id': 1}, message='Created successfully')
        # Returns: ({'success': True, 'data': {'id': 1}, 'message': 'Created successfully'}, 200)
        return success_response(data={'id': 1}, message='Created successfully', status_code=201)
        # Returns: ({'success': True, 'data': {'id': 1}, 'message': 'Created successfully'}, 201)
    """
    response = {"success": True, "timestamp": datetime.now(timezone.utc).isoformat()}
    if data is not None:
        response["data"] = data
    if message:
        response["message"] = message
    response.update(kwargs)
    return response, status_code


def error_response(error: str, status_code: int = 400, **kwargs) -> Tuple[dict, int]:
    """
    Create a standardized error response

    Args:
        error: Error message
        status_code: HTTP status code (default: 400)
        **kwargs: Additional fields to include in response

    Returns:
        Tuple of (response_dict, status_code)

    Example:
        return error_response('Invalid input', status_code=400, field='name')
        # Returns: ({'success': False, 'error': 'Invalid input', 'field': 'name'}, 400)
    """
    response = {
        "success": False,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "error": error,
    }
    response.update(kwargs)
    return response, status_code


def json_success_response(data: Any = None, message: str = None, **kwargs):
    """
    Return a JSON success response with proper headers

    This is a convenience wrapper that combines success_response() and jsonify()
    to reduce code duplication across the codebase.

    Args:
        data: Response data
        message: Optional message
        **kwargs: Additional fields to include in response

    Returns:
        Tuple of (jsonify_response, status_code)

    Example:
        return json_success_response(data={'id': 1}, message='Created successfully')
        # Returns: (jsonify({'success': True, 'data': {'id': 1}, 'message': '...'}), 200)
    """
    response, status = success_response(data, message, **kwargs)
    return jsonify(response), status


def json_error_response(error: str, status_code: int = 400, **kwargs):
    """
    Return a JSON error response with proper headers

    This is a convenience wrapper that combines error_response() and jsonify()
    to reduce code duplication across the codebase.

    Args:
        error: Error message
        status_code: HTTP status code (default: 400)
        **kwargs: Additional fields to include in response

    Returns:
        Tuple of (jsonify_response, status_code)

    Example:
        return json_error_response('Invalid input', status_code=400, field='name')
        # Returns: (jsonify({'success': False, 'error': 'Invalid input', 'field': 'name'}), 400)
    """
    response, status = error_response(error, status_code, **kwargs)
    return jsonify(response), status


__all__ = [
    'success_response',
    'error_response',
    'json_success_response',
    'json_error_response',
]
