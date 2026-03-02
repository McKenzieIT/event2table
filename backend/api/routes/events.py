"""
Events API Routes Module

This module contains all event-related API endpoints for managing
log events and their configurations.

Core endpoints:
- GET /api/events - List all events with pagination
- GET /api/events/count - Get events count
- POST /api/events - Create a new event
- GET /api/events/<int:id> - Get event details
- PUT/PATCH /api/events/<int:id> - Update an event
- GET /api/events/<int:id>/parameters - Get event parameters
- GET /api/events/<int:event_id>/params - Get event params (alias)

================================================================================
SCHEMA USAGE RECOMMENDATION (Phase 3)
================================================================================
This module currently uses manual validation via validate_json_request().
For better type safety and automatic validation, consider using Pydantic Schemas.

Available Schemas in backend/models/schemas.py:
- EventCreate: For creating new events
- EventUpdate: For updating existing events
- EventResponse: For API responses
================================================================================
"""

import html
import logging
from typing import Any, Dict, Tuple

from flask import request, session

# Import shared utilities
from backend.core.utils import (
    json_error_response,
    json_success_response,
    safe_int_convert,
    validate_game_gid,
    validate_json_request,
)

# Import EventService for business logic (ERS Architecture)
from backend.services.events.event_service import EventService

# Import the parent blueprint
from .. import api_bp

logger = logging.getLogger(__name__)

# Initialize EventService
event_service = EventService()


@api_bp.route("/api/events", methods=["GET"])
def api_list_events() -> Tuple[Dict[str, Any], int]:
    """
    API: List all events with pagination support and search

    Query Parameters:
        - game_gid: Filter by game GID (optional)
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20, max: 100)
        - search: Search keyword for event names (optional)

    Returns:
        Tuple containing response dictionary and HTTP status code

    Response Format:
        {
            "success": true,
            "data": {
                "events": [...],
                "pagination": {
                    "page": 1,
                    "per_page": 20,
                    "total": 100,
                    "total_pages": 5
                }
            }
        }
    """
    game_gid_str = request.args.get("game_gid")
    game_gid = safe_int_convert(game_gid_str) if game_gid_str else None

    logger.info(
        f"API: game_gid_str={game_gid_str}, game_gid={game_gid}, type={type(game_gid)}"
    )

    page = safe_int_convert(request.args.get("page"), 1, 1)
    per_page = safe_int_convert(request.args.get("per_page"), 20, 1)
    search = request.args.get("search", "").strip()

    # Validate pagination parameters
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 20
    if per_page > 100:
        per_page = 100

    try:
        # Use EventService for paginated list with caching
        result = event_service.get_events_paginated(
            game_gid=game_gid,
            page=page,
            per_page=per_page,
            search=search if search else None
        )

        return json_success_response(data=result)

    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error listing events: {e}")
        return json_error_response("Failed to list events", status_code=500)


@api_bp.route("/api/events", methods=["POST"])
def api_create_event():
    """API: Create a new event"""
    try:
        is_valid, data, error = validate_json_request(
            ["game_gid", "event_name", "event_name_cn"]
        )
        if not is_valid:
            return json_error_response(error, status_code=400)

        # 验证游戏GID
        is_valid_game, game_error = validate_game_gid(data["game_gid"])
        if not is_valid_game:
            return json_error_response(game_error, status_code=400)

        # Validate input lengths to prevent database errors and DoS attacks
        event_name = data.get("event_name", "").strip()
        event_name_cn = data.get("event_name_cn", "").strip()

        if len(event_name) == 0:
            return json_error_response("event_name cannot be empty", status_code=400)
        if len(event_name) > 200:
            return json_error_response(
                "event_name exceeds maximum length of 200 characters", status_code=400
            )
        if len(event_name_cn) > 200:
            return json_error_response(
                "event_name_cn exceeds maximum length of 200 characters",
                status_code=400,
            )

        # Sanitize input to prevent XSS attacks
        event_name = html.escape(event_name)
        event_name_cn = html.escape(event_name_cn)

        # Handle category_id
        category_id = data.get("category_id")
        if not category_id or (isinstance(category_id, str) and category_id.strip() == ""):
            category_id = None

        # Validate or create default category
        if category_id:
            if not event_service.validate_category_exists(category_id):
                return json_error_response(
                    f"Category with id {category_id} not found", status_code=400
                )
        else:
            category_id = event_service.get_or_create_default_category()

        # Prepare parameters list
        param_names = data.get("param_names", [])
        param_names_cn = data.get("param_names_cn", [])
        param_types = data.get("param_types", [])
        param_descriptions = data.get("param_descriptions", [])

        parameters = []
        for i, name in enumerate(param_names):
            if name:
                parameters.append({
                    "param_name": name,
                    "param_name_cn": param_names_cn[i] if i < len(param_names_cn) else "",
                    "template_id": param_types[i] if i < len(param_types) else 1,
                    "param_description": param_descriptions[i] if i < len(param_descriptions) else "",
                })

        # Create EventEntity
        from backend.models.entities import EventEntity
        event_data = EventEntity(
            game_gid=data["game_gid"],
            name=event_name,
            name_cn=event_name_cn,
            category_id=category_id,
            include_in_common_params=data.get("include_in_common_params", 1)
        )

        # Use EventService to create event with parameters
        event = event_service.create_event_with_parameters(event_data, parameters)

        logger.info(f"Event created: {event_name} (ID: {event.id})")
        return json_success_response(
            data={"event_id": event.id}, message="Event created successfully"
        )

    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        if "Bad Request" in str(e) or type(e).__name__ == "BadRequest":
            return json_error_response("Invalid request format", status_code=400)
        logger.error(f"Error creating event: {e}")
        return json_error_response("Failed to create event", status_code=500)


@api_bp.route("/api/events/<int:id>", methods=["GET"])
def api_get_event_detail(id):
    """
    API: Get detailed information for a single event

    Query params:
        - game_gid: Game GID (required)
    """
    game_gid = request.args.get("game_gid", type=int)

    if not game_gid:
        game_gid = session.get("current_game_gid")

    if not game_gid:
        return json_error_response("game_gid required", status_code=400)

    try:
        # Use EventService to get event detail with caching
        event = event_service.get_event_detail_with_game(id, game_gid)

        if not event:
            return json_error_response("Event not found", status_code=404)

        return json_success_response(data=event)

    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error getting event detail for {id}: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@api_bp.route("/api/events/<int:id>", methods=["PUT", "PATCH"])
def api_update_event(id):
    """API: Update an existing event"""
    is_valid, data, error = validate_json_request(
        ["event_name", "event_name_cn", "category_id"]
    )
    if not is_valid:
        return json_error_response(error, status_code=400)

    # Validate input lengths to prevent database errors and DoS attacks
    event_name = data.get("event_name", "").strip()
    event_name_cn = data.get("event_name_cn", "").strip()

    if len(event_name) == 0:
        return json_error_response("event_name cannot be empty", status_code=400)
    if len(event_name) > 200:
        return json_error_response(
            "event_name exceeds maximum length of 200 characters", status_code=400
        )
    if len(event_name_cn) > 200:
        return json_error_response(
            "event_name_cn exceeds maximum length of 200 characters", status_code=400
        )

    # Sanitize input to prevent XSS attacks
    event_name = html.escape(event_name)
    event_name_cn = html.escape(event_name_cn)

    try:
        # Use EventService to update event with cache invalidation
        event = event_service.update_event_with_invalidation(
            event_id=id,
            event_name=event_name,
            event_name_cn=event_name_cn,
            category_id=data.get("category_id"),
            include_in_common_params=data.get("include_in_common_params", 1)
        )

        if not event:
            return json_error_response("Event not found", status_code=404)

        logger.info(f"Event updated: {event_name} (ID: {id})")
        return json_success_response(message="Event updated successfully")

    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error updating event: {e}")
        return json_error_response("Failed to update event", status_code=500)


@api_bp.route("/api/events/<int:id>/parameters", methods=["GET"])
def api_get_event_parameters(id):
    """
    API: Get parameters for a specific event

    Returns list of parameters with id, param_name, param_name_cn,
    param_type, description, etc.
    """
    try:
        # Use EventService to get event parameters with caching
        parameters = event_service.get_event_parameters(id)

        return json_success_response(data=parameters)

    except Exception as e:
        logger.error(f"Error fetching parameters for event {id}: {e}")
        return json_error_response("Failed to fetch event parameters", status_code=500)


@api_bp.route("/api/events/<int:event_id>/params", methods=["GET"])
def api_get_event_params(event_id):
    """API: Get parameters for an event (alias for /parameters)"""
    # Call the main parameters endpoint
    return api_get_event_parameters(event_id)


# Event Node Builder API aliases are handled in events.py
# The actual implementation is provided in the earlier sections of this file

# Event Node Builder API aliases are handled in events.py
# The actual implementation is provided in the earlier sections of this file


# ============================================================================
# Event Node Builder API Aliases (for frontend compatibility)
# ============================================================================

# NOTE: Event Node Builder API routes are handled by event_node_builder_bp
# The following routes are intentionally disabled to avoid conflicts:
# - /event_node_builder/api/events (handled by event_node_builder_bp)
# - /event_node_builder/api/params (handled by event_node_builder_bp)
# - /event_node_builder/api/preview-hql (handled by event_node_builder_bp)
#
# The real implementation is in backend/services/node/event_node_builder.py
# which is registered as event_node_builder_bp with url_prefix='/event_node_builder'


@api_bp.route("/api/events/batch", methods=["DELETE"])
def api_batch_delete_events():
    """API: Batch delete events"""
    is_valid, data, error = validate_json_request(["ids"])
    if not is_valid:
        return json_error_response(error, status_code=400)

    event_ids = data.get("ids", [])

    if not event_ids or not isinstance(event_ids, list):
        return json_error_response("Invalid event IDs", status_code=400)

    try:
        # Use EventService for batch delete with cache invalidation
        deleted_count = event_service.batch_delete_events(event_ids)

        logger.info(f"Batch deleted {deleted_count} events")
        return json_success_response(
            message=f"Deleted {deleted_count} events",
            data={"deleted_count": deleted_count},
        )
    except Exception as e:
        logger.error(f"Error batch deleting events: {e}")
        return json_error_response("Failed to delete events", status_code=500)


@api_bp.route("/api/events/count", methods=["GET"])
def api_get_events_count():
    """
    API: Get events count

    Query Parameters:
        - game_gid: Filter by game GID (optional)
        - search: Search keyword for event names (optional)

    Returns:
        Tuple containing response dictionary and HTTP status code

    Response Format:
        {
            "success": true,
            "data": {
                "total": 123
            }
        }
    """
    try:
        # Get query parameters
        game_gid_str = request.args.get("game_gid")
        game_gid = safe_int_convert(game_gid_str) if game_gid_str else None
        search = request.args.get("search", "").strip()

        # Get events count from service
        total = event_service.get_events_count(
            game_gid=game_gid,
            search=search if search else None
        )

        return json_success_response(data={"total": total})

    except Exception as e:
        logger.error(f"Error getting events count: {e}")
        return json_error_response("Failed to get events count", status_code=500)


@api_bp.route("/api/events/batch-update", methods=["PUT"])
def api_batch_update_events():
    """API: Batch update events

    Example request body:
    {
        "ids": [1, 2, 3],
        "updates": {"event_name": "Updated Name", "category_id": 5}
    }
    """
    is_valid, data, error = validate_json_request(["ids", "updates"])
    if not is_valid:
        return json_error_response(error, status_code=400)

    event_ids = data.get("ids", [])
    updates = data.get("updates", {})

    if not event_ids or not updates:
        return json_error_response("Invalid request data", status_code=400)

    try:
        # Validate and sanitize update fields
        if "event_name" in updates:
            event_name = updates["event_name"].strip()
            if len(event_name) == 0:
                return json_error_response(
                    "event_name cannot be empty", status_code=400
                )
            if len(event_name) > 200:
                return json_error_response(
                    "event_name exceeds maximum length of 200 characters",
                    status_code=400,
                )
            updates["event_name"] = html.escape(event_name)

        if "event_name_cn" in updates:
            event_name_cn = updates["event_name_cn"].strip()
            if len(event_name_cn) > 200:
                return json_error_response(
                    "event_name_cn exceeds maximum length of 200 characters",
                    status_code=400,
                )
            updates["event_name_cn"] = html.escape(event_name_cn)

        # Use EventService for batch update with cache invalidation
        updated_count = event_service.batch_update_events(event_ids, updates)

        logger.info(f"Batch updated {updated_count} events")
        return json_success_response(
            message=f"Updated {updated_count} events",
            data={"updated_count": updated_count},
        )
    except Exception as e:
        logger.error(f"Error batch updating events: {e}")
        return json_error_response("Failed to update events", status_code=500)
