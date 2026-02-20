#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper functions for HQL preview V2 API routes

This module provides reusable functions for handling common operations
in HQL preview endpoints, reducing code duplication.
"""

from typing import Tuple, Any, Dict
from werkzeug.exceptions import BadRequest
import logging

from backend.core.utils import (
    json_success_response,
    json_error_response,
    success_response,
)

logger = logging.getLogger(__name__)


def parse_json_request() -> Tuple[bool, Any, str]:
    """
    Parse JSON from request with error handling

    Returns:
        Tuple of (is_valid, data, error_message)
    """
    from flask import request

    try:
        data = request.get_json(force=False)
        if data is None:
            return False, None, "Invalid JSON format"
        return True, data, ""
    except BadRequest:
        return False, None, "Invalid JSON format"


def validate_required_fields(
    data: Dict[str, Any], required_fields: list
) -> Tuple[bool, str]:
    """
    Validate that required fields are present in data

    Args:
        data: Request data dictionary
        required_fields: List of required field names

    Returns:
        Tuple of (is_valid, error_message)
    """
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"{field} is required"
    return True, ""


def handle_hql_generation_error(
    e: Exception, endpoint_name: str = ""
) -> Tuple[Any, int]:
    """
    Standardized error handling for HQL generation endpoints

    Args:
        e: The exception that occurred
        endpoint_name: Name of the endpoint (for logging)

    Returns:
        Tuple of (jsonify_response, status_code)
    """
    error_msg = str(e)

    if "not found" in error_msg.lower():
        logger.warning(f"{endpoint_name} - Resource not found: {error_msg}")
        return json_error_response(error_msg, status_code=404)

    if isinstance(e, ValueError):
        logger.warning(f"{endpoint_name} - Validation error: {error_msg}")
        return json_error_response(error_msg, status_code=400)

    logger.exception(f"{endpoint_name} - Unexpected error: {error_msg}")
    return json_error_response(f"Failed to generate HQL: {error_msg}", status_code=500)


def format_timestamp() -> str:
    """
    Get current UTC timestamp in ISO format

    Returns:
        ISO formatted timestamp string
    """
    from datetime import datetime

    return datetime.utcnow().isoformat() + "Z"


def build_success_response(
    data: Dict[str, Any], include_timestamp: bool = True
) -> Dict[str, Any]:
    """
    Build a standardized success response

    Args:
        data: Response data
        include_timestamp: Whether to include timestamp

    Returns:
        Response dictionary
    """
    if include_timestamp:
        data["generated_at"] = format_timestamp()
    return success_response(data=data)[0]
