"""
DEPRECATED - Legacy DDD Implementation

This file contains the legacy DDD-based API implementation.

Please use the main API routes instead:
- from backend.api.routes.games import games_bp

Migration Date: 2026-02-25
Planned Removal: Version 2.0
Reason: Architecture migration to simplified layered architecture

---
DEPRECATED - 遗留DDD实现

此文件包含基于DDD的遗留API实现。

请使用主API路由:
- from backend.api.routes.games import games_bp

迁移日期: 2026-02-25
计划移除: 版本 2.0
原因: 迁移到精简分层架构

---
Games API Routes Module (DDD Architecture)

This module contains all game-related API endpoints using the DDD architecture:
- GET /api/v2/games - List all games
- POST /api/v2/games - Create a new game
- GET /api/v2/games/<gid> - Get a single game by business GID
- PUT/PATCH /api/v2/games/<gid> - Update a game by business GID
- DELETE /api/v2/games/<gid> - Delete a game by business GID
- DELETE /api/v2/games/batch - Batch delete games
- PUT /api/v2/games/batch-update - Batch update games

This module uses:
- DDD Application Service Layer
- Unit of Work for transaction management
- Domain events for side effects
- DTOs for input/output

NOTE: All game queries use business GID (e.g., 10000147), not database ID.
"""

import logging
from typing import Any, Dict, Tuple

from flask import request, Response

from backend.api import api_bp
from backend.core.utils import (
    json_error_response,
    json_success_response,
    validate_json_request,
    sanitize_and_validate_string,
)
from backend.application.services.game_app_service_enhanced import (
    GameAppServiceEnhanced,
    GameCreateDTO,
    GameUpdateDTO,
    get_game_app_service
)
from backend.domain.exceptions import (
    DomainException,
    GameNotFound,
    CannotDeleteGameWithEvents,
    InvalidGameGID
)

logger = logging.getLogger(__name__)

# Allowed fields for dynamic UPDATE
ALLOWED_UPDATE_FIELDS = {"name", "ods_db"}


@api_bp.route("/api/v2/games", methods=["GET"])
def api_list_games_v2() -> Tuple[Dict[str, Any], int]:
    """
    API: List all games with statistics (DDD Architecture)
    
    Uses the DDD application service layer for data access.
    
    Returns:
        Tuple containing response dictionary and HTTP status code
    """
    try:
        service = get_game_app_service()
        games = service.get_all_games()
        
        # Convert DTOs to dicts
        games_data = [g.to_dict() for g in games]
        
        return json_success_response(data=games_data)
    
    except Exception as e:
        logger.error(f"Error listing games: {e}", exc_info=True)
        return json_error_response("Failed to list games", status_code=500)


@api_bp.route("/api/v2/games", methods=["POST"])
def api_create_game_v2() -> Tuple[Dict[str, Any], int]:
    """
    API: Create a new game (DDD Architecture)
    
    Request Body:
        {
            "gid": int,           # Business GID (required)
            "name": str,          # Game name (required)
            "ods_db": str         # ODS database name (required)
        }
    
    Returns:
        Tuple containing response dictionary and HTTP status code
    """
    # Validate required fields
    is_valid, data, error = validate_json_request(["gid", "name", "ods_db"])
    if not is_valid:
        logger.warning(f"Game creation failed: {error}")
        return json_error_response(error, status_code=400)
    
    # Validate and convert GID
    gid_value = data.get("gid")
    try:
        if isinstance(gid_value, str):
            gid_value = int(gid_value)
        elif not isinstance(gid_value, int):
            raise ValueError(f"Invalid GID type: {type(gid_value)}")
    except (ValueError, TypeError) as e:
        logger.warning(f"Game creation failed: Invalid GID format - {e}")
        return json_error_response(
            f"Game GID must be a valid integer, received: {gid_value}",
            status_code=400
        )
    
    if gid_value <= 0:
        return json_error_response(
            "Game GID must be a positive integer",
            status_code=400
        )
    
    # Validate and sanitize name
    is_valid, name = sanitize_and_validate_string(
        data.get("name"), max_length=200, field_name="name", allow_empty=False
    )
    if not is_valid:
        return json_error_response(name, status_code=400)
    
    # Validate and sanitize ods_db
    is_valid, ods_db = sanitize_and_validate_string(
        data.get("ods_db", ""), max_length=100, field_name="ods_db", allow_empty=False
    )
    if not is_valid:
        return json_error_response(ods_db, status_code=400)
    
    # Validate ods_db value
    if ods_db not in ['ieu_ods', 'overseas_ods']:
        return json_error_response(
            f"Invalid ods_db: {ods_db}. Must be 'ieu_ods' or 'overseas_ods'",
            status_code=400
        )
    
    try:
        service = get_game_app_service()
        
        # Create DTO
        dto = GameCreateDTO(gid=gid_value, name=name, ods_db=ods_db)
        
        # Call application service
        result = service.create_game(dto)
        
        logger.info(f"Game created successfully: {name} (GID: {gid_value})")
        
        return json_success_response(
            message="Game created successfully",
            data=result.to_dict()
        )
    
    except ValueError as e:
        # Game already exists
        logger.warning(f"Game creation failed: {e}")
        return json_error_response(str(e), status_code=409)
    
    except DomainException as e:
        logger.error(f"Domain error creating game: {e}")
        return json_error_response(str(e), status_code=400)
    
    except Exception as e:
        logger.error(f"Error creating game: {e}", exc_info=True)
        return json_error_response("Failed to create game", status_code=500)


@api_bp.route("/api/v2/games/<int:gid>", methods=["GET"])
def api_get_game_v2(gid: int) -> Tuple[Dict[str, Any], int]:
    """
    API: Get a single game by business GID (DDD Architecture)
    
    Args:
        gid: Business GID of the game
    
    Returns:
        Tuple containing response dictionary with game data and HTTP status code
    """
    try:
        service = get_game_app_service()
        game = service.get_game(gid)
        
        if not game:
            return json_error_response("Game not found", status_code=404)
        
        return json_success_response(data=game.to_dict())
    
    except Exception as e:
        logger.error(f"Error getting game {gid}: {e}", exc_info=True)
        return json_error_response("Failed to get game", status_code=500)


@api_bp.route("/api/v2/games/<int:gid>", methods=["PUT", "PATCH"])
def api_update_game_v2(gid: int) -> Tuple[Dict[str, Any], int]:
    """
    API: Update an existing game by business GID (DDD Architecture)
    
    Supports partial updates - only provide fields you want to update.
    Valid fields: name, ods_db
    """
    # Validate JSON format
    if not request.is_json:
        return json_error_response("Request must be JSON", status_code=400)
    
    data = request.get_json()
    if data is None:
        return json_error_response("Invalid JSON data", status_code=400)
    
    # Validate input fields against whitelist
    provided_fields = set(data.keys())
    invalid_fields = provided_fields - ALLOWED_UPDATE_FIELDS
    if invalid_fields:
        return json_error_response(
            f"Invalid fields: {', '.join(sorted(invalid_fields))}. "
            f"Allowed fields: {', '.join(sorted(ALLOWED_UPDATE_FIELDS))}",
            status_code=400,
        )
    
    # Validate and sanitize name if provided
    name = None
    if "name" in data:
        is_valid, name = sanitize_and_validate_string(
            data.get("name"), max_length=200, field_name="name", allow_empty=False
        )
        if not is_valid:
            return json_error_response(name, status_code=400)
    
    # Validate and sanitize ods_db if provided
    ods_db = None
    if "ods_db" in data:
        is_valid, ods_db = sanitize_and_validate_string(
            data.get("ods_db"), max_length=100, field_name="ods_db", allow_empty=False
        )
        if not is_valid:
            return json_error_response(ods_db, status_code=400)
        
        if ods_db not in ['ieu_ods', 'overseas_ods']:
            return json_error_response(
                f"Invalid ods_db: {ods_db}. Must be 'ieu_ods' or 'overseas_ods'",
                status_code=400
            )
    
    # Check if at least one field is being updated
    if name is None and ods_db is None:
        return json_error_response(
            "No valid fields to update. Provide 'name' and/or 'ods_db'",
            status_code=400
        )
    
    try:
        service = get_game_app_service()
        
        # Create DTO
        dto = GameUpdateDTO(name=name, ods_db=ods_db)
        
        # Call application service
        result = service.update_game(gid, dto)
        
        logger.info(f"Game updated: GID {gid}")
        
        return json_success_response(
            data=result.to_dict(),
            message="Game updated successfully"
        )
    
    except GameNotFound as e:
        return json_error_response(str(e), status_code=404)
    
    except DomainException as e:
        logger.error(f"Domain error updating game: {e}")
        return json_error_response(str(e), status_code=400)
    
    except Exception as e:
        logger.error(f"Error updating game: {e}", exc_info=True)
        return json_error_response("Failed to update game", status_code=500)


@api_bp.route("/api/v2/games/<int:gid>", methods=["DELETE"])
def api_delete_game_v2(gid: int) -> Tuple[Dict[str, Any], int]:
    """
    API: Delete a game by business GID (DDD Architecture)
    
    Query Parameters:
        confirm: bool - Set to true to force delete even if game has events
    """
    # Get confirmation flag
    data = request.get_json() or {}
    force_delete = data.get("confirm", False)
    
    try:
        service = get_game_app_service()
        
        # Check deletion impact first
        impact = service.check_deletion_impact(gid)
        
        # If no confirmation and has associated data, return impact
        if not force_delete and impact['has_associated_data']:
            return json_error_response(
                f"Game has {impact['event_count']} events, "
                f"{impact['param_count']} parameters, "
                f"{impact['node_config_count']} node configs. "
                f"Set confirm=true to force delete.",
                status_code=409,
                data={
                    "event_count": impact['event_count'],
                    "param_count": impact['param_count'],
                    "node_config_count": impact['node_config_count'],
                },
            )
        
        # Delete the game
        result = service.delete_game(gid, force=force_delete)
        
        logger.info(f"Game deleted: GID {gid}")
        
        return json_success_response(
            message="Game deleted successfully",
            data=result
        )
    
    except GameNotFound as e:
        return json_error_response(str(e), status_code=404)
    
    except CannotDeleteGameWithEvents as e:
        return json_error_response(str(e), status_code=409)
    
    except DomainException as e:
        logger.error(f"Domain error deleting game: {e}")
        return json_error_response(str(e), status_code=400)
    
    except Exception as e:
        logger.error(f"Error deleting game: {e}", exc_info=True)
        return json_error_response("Failed to delete game", status_code=500)


@api_bp.route("/api/v2/games/<int:gid>/impact", methods=["GET"])
def api_check_game_impact_v2(gid: int) -> Tuple[Dict[str, Any], int]:
    """
    API: Check the impact of deleting a game (DDD Architecture)
    
    Returns statistics about associated data that would be affected by deletion.
    """
    try:
        service = get_game_app_service()
        impact = service.check_deletion_impact(gid)
        
        return json_success_response(data=impact)
    
    except GameNotFound as e:
        return json_error_response(str(e), status_code=404)
    
    except Exception as e:
        logger.error(f"Error checking game impact: {e}", exc_info=True)
        return json_error_response("Failed to check game impact", status_code=500)


@api_bp.route("/api/v2/games/batch", methods=["DELETE"])
def api_batch_delete_games_v2() -> Tuple[Dict[str, Any], int]:
    """
    API: Batch delete games (DDD Architecture)
    
    Request Body:
        {
            "ids": [int],         # List of game GIDs
            "confirm": bool       # Force delete even if games have events
        }
    """
    is_valid, data, error = validate_json_request(["ids"])
    if not is_valid:
        return json_error_response(error, status_code=400)
    
    gids = data.get("ids", [])
    force_delete = data.get("confirm", False)
    
    if not gids or not isinstance(gids, list):
        return json_error_response("Invalid game IDs", status_code=400)
    
    try:
        service = get_game_app_service()
        result = service.batch_delete_games(gids, force=force_delete)
        
        logger.info(f"Batch deleted {result['success_count']} games")
        
        return json_success_response(
            message=f"Deleted {result['success_count']} games",
            data=result
        )
    
    except Exception as e:
        logger.error(f"Error batch deleting games: {e}", exc_info=True)
        return json_error_response("Failed to delete games", status_code=500)


@api_bp.route("/api/v2/games/batch-update", methods=["PUT"])
def api_batch_update_games_v2() -> Tuple[Dict[str, Any], int]:
    """
    API: Batch update games (DDD Architecture)
    
    Request Body:
        {
            "ids": [int],         # List of game GIDs
            "updates": {
                "name": str,      # Optional: new name
                "ods_db": str     # Optional: new ods_db
            }
        }
    """
    is_valid, data, error = validate_json_request(["ids", "updates"])
    if not is_valid:
        return json_error_response(error, status_code=400)
    
    gids = data.get("ids", [])
    updates = data.get("updates", {})
    
    if not gids or not updates:
        return json_error_response("Invalid request data", status_code=400)
    
    # Validate and sanitize update fields
    name = None
    ods_db = None
    
    if "name" in updates:
        is_valid, name = sanitize_and_validate_string(
            updates["name"], max_length=200, field_name="name", allow_empty=False
        )
        if not is_valid:
            return json_error_response(name, status_code=400)
    
    if "ods_db" in updates:
        is_valid, ods_db = sanitize_and_validate_string(
            updates["ods_db"], max_length=100, field_name="ods_db", allow_empty=False
        )
        if not is_valid:
            return json_error_response(ods_db, status_code=400)
        
        if ods_db not in ['ieu_ods', 'overseas_ods']:
            return json_error_response(
                f"Invalid ods_db: {ods_db}",
                status_code=400
            )
    
    try:
        service = get_game_app_service()
        
        # Create DTO
        dto = GameUpdateDTO(name=name, ods_db=ods_db)
        
        # Call application service
        result = service.batch_update_games(gids, dto)
        
        logger.info(f"Batch updated {result['updated_count']} games")
        
        return json_success_response(
            message=f"Updated {result['updated_count']} games",
            data=result
        )
    
    except Exception as e:
        logger.error(f"Error batch updating games: {e}", exc_info=True)
        return json_error_response("Failed to update games", status_code=500)
