#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Common Parameters API Routes - Refactored to use ParameterService

This module provides API endpoints for managing common parameters.
It has been refactored to use ParameterService instead of direct database access.

Architecture:
- API Layer (this file) → Service Layer (ParameterService) → Repository Layer (ParameterRepository) → Database
"""

from flask import Blueprint, request
from backend.core.logging import get_logger
from backend.core.utils import json_success_response, json_error_response
from backend.services.parameters.parameter_service import ParameterService

logger = get_logger(__name__)

common_params_bp = Blueprint("common_params", __name__)


@common_params_bp.route("/api/common-params", methods=["GET"])
def list_common_params():
    """API: List common parameters for a specific game"""
    try:
        # Get game_gid from query parameters
        game_gid = request.args.get("game_gid", type=int)

        logger.info(f"[DEBUG] list_common_params called with game_gid={game_gid}")

        if not game_gid:
            return json_error_response("game_gid is required", status_code=400)

        # Use ParameterService
        service = ParameterService()
        common_params = service.get_common_params(game_gid)

        return json_success_response(data=common_params)

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error fetching common params: {e}")
        return json_error_response("Failed to fetch common params", status_code=500)


@common_params_bp.route("/api/common-params/sync", methods=["POST"])
def sync_common_params():
    """
    API: Sync common parameters for a game

    Analyzes all events for the specified game and identifies parameters
    that appear in 80% or more of events. These are automatically marked
    as common parameters.
    """
    data = request.get_json()

    if not data:
        return json_error_response("Request data is required", status_code=400)

    game_gid = data.get("game_gid") or data.get("game_id")

    if not game_gid:
        return json_error_response("game_gid is required", status_code=400)

    try:
        # Use ParameterService
        service = ParameterService()
        result = service.sync_common_params(game_gid)

        return json_success_response(
            data=result,
            message=f"Synced {result['added']} common parameters from {result['total_events']} events",
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return json_error_response(str(e), status_code=404)
    except Exception as e:
        logger.error(f"Error syncing common params: {e}", exc_info=True)
        return json_error_response(
            f"Failed to sync common parameters: {str(e)}", status_code=500
        )


@common_params_bp.route("/api/common-params/<int:param_id>", methods=["DELETE"])
def delete_common_param(param_id):
    """API: Delete a common parameter"""
    try:
        # Use ParameterService
        service = ParameterService()
        service.delete_common_param(param_id)

        return json_success_response(message="Common parameter deleted")

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return json_error_response(str(e), status_code=404)
    except Exception as e:
        logger.error(f"Error deleting common param: {e}")
        return json_error_response("Failed to delete common parameter", status_code=500)


@common_params_bp.route("/api/common-params/bulk-delete", methods=["DELETE", "POST"])
@common_params_bp.route(
    "/api/common-params/batch", methods=["DELETE"]
)  # Alias for frontend compatibility
def bulk_delete_common_params():
    """API: Bulk delete common parameters"""
    data = request.get_json() if request.data else {}

    ids = data.get("ids", [])

    if not ids:
        return json_error_response("ids list is required", status_code=400)

    if not isinstance(ids, list):
        return json_error_response("ids must be a list", status_code=400)

    try:
        # Use ParameterService
        service = ParameterService()
        deleted_count = service.batch_delete_common_params(ids)

        return json_success_response(
            data={"deleted": deleted_count},
            message=f"Deleted {deleted_count} common parameters",
        )

    except Exception as e:
        logger.error(f"Error bulk deleting common params: {e}")
        return json_error_response("Failed to delete common parameters", status_code=500)
