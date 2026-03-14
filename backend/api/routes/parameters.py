"""
Parameters API Routes Module

This module contains all parameter-related API endpoints for managing
cross-event common parameters.

Core endpoints:
- GET /api/parameters/all - List all unique parameters
- GET /api/parameters/<param_name>/details - Get parameter details
- GET /api/parameters/stats - Get parameter statistics
- PUT /api/parameters/<id> - Update parameter
- POST /api/parameters/export - Export parameters
- POST /api/parameters/search - Search parameters
- GET /api/parameters/common - Get common parameters
- GET /api/parameters/validate - Validate parameter

Architecture Update (V9.0.0):
- Migrated to use ParameterService instead of direct database access
- Uses GameService for game validation
- Uses unified Entity model (ParameterEntity)
- Service layer handles business logic and caching
- Repository layer handles data access
- No direct database access (100% ERS architecture)

================================================================================
PARAMETER SERVICE USAGE
================================================================================
All parameter operations now go through ParameterService:
- Query operations: Use ParameterService.get_*() methods
- Mutation operations: Use ParameterService.create/update/delete()
- Caching: Automatic cache management via service decorators
- Validation: Automatic validation via Pydantic Entity models
================================================================================
"""

import logging
from functools import lru_cache
from typing import Optional

from flask import request, session

# Import cache system
from backend.core.cache.cache_system import HierarchicalCache

# Import shared utilities
from backend.core.utils import json_error_response, json_success_response, validate_json_request
from backend.services.games.game_service import GameService

# Import Service layer
from backend.services.parameters.parameter_service import ParameterService

# Cache TTL constants
PARAMETERS_ALL_CACHE_TTL = 300  # 5 minutes

# Initialize cache
hierarchical_cache = HierarchicalCache()

# Import parameter route helpers (code complexity reduction)
from backend.api.routes._param_helpers import (
    get_where_clause_for_game,
    resolve_game_context,
    validate_parameter_name,
)

# Import the parent blueprint
from .. import api_bp

logger = logging.getLogger(__name__)


@lru_cache(maxsize=128)
def _get_game_id_from_gid(game_gid: int) -> Optional[int]:
    """Cached game_gid to game_id conversion using GameService"""
    game_service = GameService()
    game = game_service.get_game_by_gid(game_gid)
    return game.id if game else None


@lru_cache(maxsize=128)
def _get_game_gid_from_id(game_id: int) -> Optional[int]:
    """Cached game_id to game_gid conversion using GameService"""
    game_service = GameService()
    game = game_service.get_game_by_database_id(game_id)
    return game.gid if game else None


@api_bp.route("/api/parameters/all", methods=["GET"])
def api_get_all_parameters():
    """
    API: Get all unique parameters for a game (deduplicated by param_name)
    支持game_gid参数(推荐)或game_id参数(向后兼容)

    Architecture (V9.0.0):
    - Uses ParameterService.get_parameters_paginated() for data access
    - No direct database access (100% ERS architecture)

    Performance: Uses hierarchical caching with 5-minute TTL
    - L1 cache: 60s (hot data)
    - L2 cache: 300s (shared cache)
    - Target: <100ms response time (70% improvement from 267ms baseline)
    """
    try:
        # 使用helper函数解析游戏上下文
        game_id, game_gid, error = resolve_game_context()
        if error:
            return json_error_response(error, status_code=400)

        # 获取可选参数
        search = request.args.get("search", "")
        type_filter = request.args.get("type", "")
        page = request.args.get("page", 1, type=int)
        limit = min(request.args.get("limit", 50, type=int), 100)

        # Use ParameterService for paginated results
        service = ParameterService()
        result = service.get_parameters_paginated(
            game_gid=int(game_gid) if game_gid else None,
            search=search or None,
            type_filter=type_filter or None,
            page=page,
            page_size=limit,
        )

        return json_success_response(
            data=result,
            message="Parameters retrieved successfully",
        )

    except ValueError as e:
        logger.error(f"Validation error fetching parameters: {e}")
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error fetching parameters: {e}", exc_info=True)
        return json_error_response("Failed to fetch parameters", status_code=500)


@api_bp.route("/api/parameters/<path:param_name>/details", methods=["GET"])
def api_get_parameter_details(param_name):
    """
    API: Get parameter details with cross-event usage

    Args:
        param_name: Parameter name
    Query Parameters:
        - game_gid: Game GID (required)
    """
    try:
        game_gid = request.args.get("game_gid", type=str)

        if not game_gid:
            game_gid = session.get("current_game_gid")

        if not game_gid:
            return json_error_response("game_gid required", status_code=400)

        # Convert to int
        try:
            game_gid = int(game_gid)
        except (ValueError, TypeError):
            return json_error_response("Invalid game_gid format", status_code=400)

        # Use ParameterService
        service = ParameterService()
        param_info = service.get_parameter_details(param_name, game_gid)

        if not param_info:
            return json_error_response("Parameter not found", status_code=404)

        return json_success_response(data=param_info)

    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error fetching parameter details for {param_name}: {e}", exc_info=True)
        return json_error_response("Failed to fetch parameter details", status_code=500)


@api_bp.route("/api/parameters/stats", methods=["GET"])
def api_get_parameter_stats():
    """
    API: Get parameter statistics

    Query Parameters:
        - game_gid: Game GID (required)
    """
    try:
        game_gid = request.args.get("game_gid", type=str)

        if not game_gid:
            game_gid = session.get("current_game_gid")

        if not game_gid:
            return json_error_response("game_gid required", status_code=400)

        # Convert to int
        try:
            game_gid = int(game_gid)
        except (ValueError, TypeError):
            return json_error_response("Invalid game_gid format", status_code=400)

        # Use ParameterService
        service = ParameterService()
        stats = service.get_parameter_stats(game_gid)

        return json_success_response(data=stats)

    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error fetching parameter stats: {e}", exc_info=True)
        return json_error_response("Failed to fetch parameter statistics", status_code=500)


@api_bp.route("/api/parameters/<int:id>", methods=["PUT"])
def api_update_parameter(id):
    """
    API: Update parameter information

    Uses ParameterService for business logic and cache management.
    """
    is_valid, data, error = validate_json_request(["param_name"])
    if not is_valid:
        return json_error_response(error, status_code=400)

    try:
        service = ParameterService()

        # Map API field name to Entity field name
        update_data = {"name": data["param_name"]}

        # Add additional fields if provided
        if "param_name_cn" in data:
            update_data["param_name_cn"] = data["param_name_cn"]
        if "param_type" in data:
            update_data["param_type"] = data["param_type"]
        if "json_path" in data:
            update_data["json_path"] = data["json_path"]

        # Update parameter via service
        updated_param = service.update_parameter(id, update_data)

        logger.info(f"Parameter updated via service: {id} -> {data['param_name']}")
        return json_success_response(
            data=updated_param.model_dump(), message="Parameter updated successfully"
        )

    except ValueError as e:
        logger.error(f"Validation error updating parameter {id}: {e}")
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error updating parameter {id}: {e}", exc_info=True)
        return json_error_response("Failed to update parameter", status_code=500)


@api_bp.route("/api/parameters/search", methods=["POST"])
def api_search_parameters():
    """
    API: Search parameters

    Request Body:
        - game_gid: Game GID (required, recommended)
        - keyword: Search keyword (required)
        - data_type: Data type filter (optional)
    """
    is_valid, data, error = validate_json_request(["game_gid", "keyword"])
    if not is_valid:
        return json_error_response(error, status_code=400)

    try:
        game_gid = data["game_gid"]
        keyword = data["keyword"]
        data_type = data.get("data_type", "")

        # Use ParameterService
        service = ParameterService()
        parameters = service.search_parameters(keyword, game_gid, data_type)

        return json_success_response(data=parameters)

    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error searching parameters: {e}", exc_info=True)
        return json_error_response("Failed to search parameters", status_code=500)


@api_bp.route("/api/parameters/common", methods=["GET"])
def api_get_common_parameters():
    """
    API: Get common parameters list

    Query Parameters:
        - game_gid: Game GID (required)
    """
    try:
        game_gid = request.args.get("game_gid", type=str)

        if not game_gid:
            game_gid = session.get("current_game_gid")

        if not game_gid:
            return json_error_response("game_gid required", status_code=400)

        # Convert to int
        try:
            game_gid = int(game_gid)
        except (ValueError, TypeError):
            return json_error_response("Invalid game_gid format", status_code=400)

        # Use ParameterService
        service = ParameterService()
        common_params = service.get_common_parameters_by_game(game_gid)

        return json_success_response(data=common_params)

    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error fetching common parameters: {e}", exc_info=True)
        return json_error_response("Failed to fetch common parameters", status_code=500)


@api_bp.route("/api/parameters/validate", methods=["GET"])
def api_validate_parameter():
    """
    API: Validate parameter name

    Query Parameters:
        - game_gid: Game GID (required, recommended)
        - game_id: Game database ID (optional, for backward compatibility)
        - param_name: Parameter name (required)
    """
    try:
        # 使用helper函数解析游戏上下文
        game_id, game_gid, error = resolve_game_context()
        if error:
            return json_error_response(error, status_code=400)

        param_name = request.args.get("param_name", "").strip()

        if not param_name:
            return json_error_response("Parameter name is required", status_code=400)

        # 使用helper函数验证参数名格式
        is_valid, error_msg = validate_parameter_name(param_name)
        if not is_valid:
            return json_success_response(
                data={
                    "valid": False,
                    "reason": error_msg,
                }
            )

        # Use ParameterService to check if parameter exists
        if not game_gid:
            return json_success_response(data={"valid": True, "exists": False})

        service = ParameterService()
        result = service.validate_parameter_name(param_name, game_gid)

        return json_success_response(data=result)

    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error validating parameter {param_name}: {e}", exc_info=True)
        return json_error_response("Failed to validate parameter", status_code=500)


@api_bp.route("/api/parameters/<int:id>", methods=["GET"])
def api_get_parameter(id):
    """
    API: Get parameter by ID

    Uses ParameterService for data access.
    """
    try:
        service = ParameterService()
        param = service.get_parameter_by_id(id)

        if not param:
            return json_error_response("Parameter not found", status_code=404)

        return json_success_response(data=param.model_dump())

    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error getting parameter {id}: {e}", exc_info=True)
        return json_error_response("Failed to get parameter", status_code=500)


@api_bp.route("/api/param-library/check", methods=["GET"])
def api_check_param_library():
    """API: Check if parameter exists in library"""
    param_name = request.args.get("param_name")
    template_id = request.args.get("template_id", type=int)

    if not param_name or template_id is None:
        return json_error_response("Missing required parameters", status_code=400)

    try:
        service = ParameterService()
        library_param = service.check_param_library(param_name, template_id)

        exists = library_param is not None

        return json_success_response(data={"exists": exists, "library_param": library_param})

    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error checking param library: {e}", exc_info=True)
        return json_error_response("Failed to check param library", status_code=500)


@api_bp.route("/api/event-params/<int:param_id>/link-library", methods=["POST"])
def api_link_event_param_to_library(param_id):
    """API: Link event parameter to library parameter"""
    is_valid, data, error = validate_json_request(["library_id"])
    if not is_valid:
        return json_error_response(error, status_code=400)

    library_id = data.get("library_id")

    try:
        service = ParameterService()
        result = service.link_event_param_to_library(param_id, library_id)

        return json_success_response(data=result, message="参数已关联到库")

    except ValueError as e:
        return json_error_response(str(e), status_code=404)
    except Exception as e:
        logger.error(f"Error linking param to library: {e}", exc_info=True)
        return json_error_response("Failed to link param to library", status_code=500)


@api_bp.route("/api/param-library/batch-check", methods=["POST"])
def api_batch_check_param_library():
    """API: Batch check parameters against library"""
    is_valid, data, error = validate_json_request(["parameters"])
    if not is_valid:
        return json_error_response(error, status_code=400)

    parameters = data.get("parameters", [])

    try:
        service = ParameterService()
        result = service.batch_check_param_library(parameters)

        return json_success_response(data=result)

    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error batch checking param library: {e}", exc_info=True)
        return json_error_response("Failed to batch check param library", status_code=500)


@api_bp.route("/api/alter-table/<int:param_id>", methods=["GET"])
def api_get_alter_table_sql(param_id):
    """
    API: Get ALTER TABLE SQL for a common parameter

    Args:
        param_id: Common parameter ID

    Returns:
        Parameter details and generated ALTER TABLE HQL statement

    Example:
        GET /api/alter-table/1

        Response:
        {
            "success": true,
            "data": {
                "param": {
                    "id": 1,
                    "param_name": "zone_id",
                    "param_name_cn": "区域ID",
                    "param_type": "string",
                    "table_name": "dwd_common_params",
                    "game_name": "Game Name",
                    "gid": 10000147
                },
                "alter_sql": "-- ALTER TABLE Statement\\nALTER TABLE dwd_common_params ADD COLUMN IF NOT EXISTS zone_id STRING COMMENT '区域ID';"
            }
        }
    """
    try:
        service = ParameterService()
        result = service.get_alter_table_sql(param_id)

        if not result:
            return json_error_response("Parameter not found", status_code=404)

        logger.info(f"Generated ALTER TABLE SQL for param_id={param_id}")

        return json_success_response(data=result)

    except ValueError as e:
        return json_error_response(str(e), status_code=404)
    except Exception as e:
        logger.error(
            f"Error generating ALTER TABLE SQL for param_id={param_id}: {e}",
            exc_info=True,
        )
        return json_error_response("An internal error occurred", status_code=500)
