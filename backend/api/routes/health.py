"""
Health Check API Route

Provides a lightweight health check endpoint for E2E testing and monitoring.
This endpoint should not perform any heavy operations (no DB queries if possible).
"""

import logging
from datetime import datetime
from typing import Any, Dict, Tuple

from flask import Blueprint, request

from backend.core.utils import json_error_response, json_success_response

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__)


@health_bp.route("/api/health", methods=["GET"])
def health_check() -> Tuple[Dict[str, Any], int]:
    """
    Health check endpoint for E2E testing and monitoring

    Returns a simple JSON response indicating the API is healthy.
    This endpoint is designed to be lightweight and fast.

    Returns:
        JSON response with status and timestamp:
        {
            "status": "healthy",
            "timestamp": "2026-03-01T12:00:00.000000",
            "service": "event2table-api"
        }

    Example:
        curl http://127.0.0.1:5001/api/health
    """
    try:
        return json_success_response(
            data={
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "service": "event2table-api",
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        # Even in case of error, return a structured response
        return json_error_response(
            message="Service unhealthy",
            status_code=503,
            data={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "service": "event2table-api",
                "error": str(e),
            },
        )
