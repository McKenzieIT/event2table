"""
Events API Routes Module

This module contains all event-related API endpoints for managing
log events and their configurations.

Core endpoints:
- GET /api/events - List all events with pagination
- POST /api/events - Create a new event
- GET /api/events/<int:id> - Get event details
- PUT/PATCH /api/events/<int:id> - Update an event
- GET /api/events/<int:id>/parameters - Get event parameters
- GET /api/events/<int:event_id>/params - Get event params (alias)
"""

import html
import logging
import sqlite3
from typing import Any, Dict, Tuple

# Import cache functions
import sys

from flask import request, session, Response

# Import shared utilities
from backend.core.utils import (
    execute_write,
    fetch_all_as_dict,
    fetch_one_as_dict,
    json_error_response,
    json_success_response,
    safe_int_convert,
    validate_game_gid,
    validate_json_request,
)

# Import Repository pattern for data access
from backend.core.data_access import Repositories

sys.path.append("..")
try:
    from backend.core.cache.cache_system import clear_cache_pattern
except ImportError:

    def clear_cache_pattern(pattern):
        """
        Clear cache entries matching a pattern (fallback implementation).

        This is a fallback function used when the cache_system module
        is not available. It does nothing but prevents ImportError.

        Args:
            pattern (str): Cache key pattern to match (unused in fallback)

        Returns:
            None
        """
        pass


# Import the parent blueprint
from .. import api_bp

logger = logging.getLogger(__name__)


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
    offset = (page - 1) * per_page

    # Build base query
    query = """
        SELECT
            le.*,
            g.gid, g.name as game_name, g.ods_db,
            ec.name as category_name,
            (SELECT COUNT(*) FROM event_params ep
             WHERE ep.event_id = le.id AND ep.is_active = 1) as param_count
        FROM log_events le
        LEFT JOIN games g ON le.game_gid = g.gid
        LEFT JOIN event_categories ec ON le.category_id = ec.id
    """

    # Build WHERE clauses and parameters
    where_clauses = []
    params = []

    # Game filter
    if game_gid:
        where_clauses.append("le.game_gid = ?")
        params.append(game_gid)

    # Search filter
    if search:
        where_clauses.append("(le.event_name LIKE ? OR le.event_name_cn LIKE ? OR ec.name LIKE ?)")
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern, search_pattern])

    # Construct WHERE clause
    if where_clauses:
        where_sql = " WHERE " + " AND ".join(where_clauses)
        query += where_sql

    # Get total count with filters
    count_query = "SELECT COUNT(*) as total FROM log_events le LEFT JOIN event_categories ec ON le.category_id = ec.id"
    if where_clauses:
        count_query += where_sql
    total_result = fetch_one_as_dict(count_query, tuple(params))

    # Add ORDER BY and pagination
    query += " ORDER BY le.id DESC LIMIT ? OFFSET ?"
    events = fetch_all_as_dict(query, tuple(params + [per_page, offset]))

    total_events = total_result["total"] if total_result else 0
    total_pages = max(1, (total_events + per_page - 1) // per_page)

    return json_success_response(
        data={
            "events": events,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total_events,
                "total_pages": total_pages,
            },
        }
    )


@api_bp.route("/api/events", methods=["POST"])
def api_create_event():
    """API: Create a new event"""
    try:
        is_valid, data, error = validate_json_request(
            ["game_gid", "event_name", "event_name_cn", "category_id"]
        )
        if not is_valid:
            return json_error_response(error, status_code=400)

        # 验证游戏GID
        is_valid_game, game_error = validate_game_gid(data["game_gid"])
        if not is_valid_game:
            return json_error_response(game_error, status_code=400)

        # 验证category_id
        if not data.get("category_id"):
            return json_error_response("category_id is required", status_code=400)

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

        # Update data with sanitized values
        data["event_name"] = event_name
        data["event_name_cn"] = event_name_cn

        # 获取category名称
        category = fetch_one_as_dict(
            "SELECT name FROM event_categories WHERE id = ?", (data["category_id"],)
        )
        if not category:
            return json_error_response(
                f'Category with id {data["category_id"]} not found', status_code=400
            )
        event_category = category["name"]

        # 验证game_gid存在
        game = fetch_one_as_dict(
            "SELECT id, gid, ods_db FROM games WHERE gid = ?", (data["game_gid"],)
        )
        if not game:
            return json_error_response(
                f'Game with gid {data["game_gid"]} not found', status_code=400
            )

        # Get database game_id and game_gid
        db_game_id = game["id"]
        game_gid = data["game_gid"]
        ods_db = game["ods_db"]

        # Generate source_table and target_table names
        source_table = f"{ods_db}.ods_{game_gid}_all_view"
        target_table = f'dwd.v_dwd_{game_gid}_{data["event_name"]}_di'

        event_id = execute_write(
            """INSERT INTO log_events (game_id, game_gid, event_name, event_name_cn, category_id, source_table, target_table, include_in_common_params)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                db_game_id,
                game_gid,
                data["event_name"],
                data.get("event_name_cn", ""),
                data.get("category_id", ""),
                source_table,
                target_table,
                data.get("include_in_common_params", 1),
            ),
            return_last_id=True,
        )

        # Parse parameters
        param_names = data.get("param_names", [])
        param_names_cn = data.get("param_names_cn", [])
        param_types = data.get("param_types", [])
        param_descriptions = data.get("param_descriptions", [])

        for i, name in enumerate(param_names):
            if name:
                execute_write(
                    """INSERT INTO event_params
                           (event_id, param_name, param_name_cn, template_id, param_description, is_active, version)
                           VALUES (?, ?, ?, ?, ?, 1, 1)""",
                    (
                        event_id,
                        name,
                        param_names_cn[i] if i < len(param_names_cn) else "",
                        param_types[i] if i < len(param_types) else 1,
                        param_descriptions[i] if i < len(param_descriptions) else "",
                    ),
                )

        clear_cache_pattern("dashboard_statistics")
        logger.info(f"Event created: {data['event_name']} (ID: {event_id})")
        return json_success_response(
            data={"event_id": event_id}, message="Event created successfully"
        )

    except sqlite3.IntegrityError as e:
        return json_error_response("Integrity constraint violation", status_code=400)
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
        - game_gid: Game GID (optional, falls back to session)
        - game_id: Legacy parameter for backward compatibility (deprecated)
    """
    # Try game_gid first, then fall back to game_id for backward compatibility
    game_gid = request.args.get("game_gid", type=int)
    if not game_gid:
        game_id = request.args.get("game_id", type=int)
        if game_id:
            # Convert game_id to game_gid
            game = Repositories.GAMES.find_by_id(game_id)
            if game:
                game_gid = game["gid"]

    if not game_gid:
        game_gid = session.get("current_game_gid")

    if not game_gid:
        return json_error_response("Game context required", status_code=400)

    try:
        event = fetch_one_as_dict(
            """
            SELECT
                le.*,
                g.gid,
                g.name as game_name,
                g.ods_db,
                ec.name as category_name
            FROM log_events le
            LEFT JOIN games g ON le.game_gid = g.gid
            LEFT JOIN event_categories ec ON le.category_id = ec.id
            WHERE le.id = ? AND le.game_gid = ?
        """,
            (id, game_gid),
        )

        if not event:
            return json_error_response("Event not found", status_code=404)

        return json_success_response(data=event)

    except Exception as e:
        logger.error(f"Error getting event detail for {id}: {e}")
        return json_error_response(str(e), status_code=500)


@api_bp.route("/api/events/<int:id>", methods=["PUT", "PATCH"])
def api_update_event(id):
    """API: Update an existing event"""
    # 使用Repository模式替代重复的SQL查询
    event = Repositories.LOG_EVENTS.find_by_id(id)
    if not event:
        return json_error_response("Event not found", status_code=404)

    is_valid, data, error = validate_json_request(["event_name", "event_name_cn", "category_id"])
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

    # Update data with sanitized values
    data["event_name"] = event_name
    data["event_name_cn"] = event_name_cn

    try:
        execute_write(
            "UPDATE log_events SET event_name = ?, event_name_cn = ?, category_id = ?, include_in_common_params = ? WHERE id = ?",
            (
                data["event_name"],
                data["event_name_cn"],
                data["category_id"],
                data.get("include_in_common_params", 1),
                id,
            ),
        )
        logger.info(f"Event updated: {data['event_name']} (ID: {id})")
        return json_success_response(message="Event updated successfully")
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
    # 使用Repository模式替代重复的SQL查询
    event = Repositories.LOG_EVENTS.find_by_id(id)
    if not event:
        return json_error_response("Event not found", status_code=404)

    try:
        parameters = fetch_all_as_dict(
            """
            SELECT
                ep.id,
                ep.param_name,
                ep.param_name_cn,
                pt.template_name as param_type,
                ep.param_description as description,
                ep.is_active,
                ep.created_at,
                ep.updated_at
            FROM event_params ep
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE ep.event_id = ? AND ep.is_active = 1
            ORDER BY ep.id
        """,
            (id,),
        )

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
        # Delete events using Repository batch delete
        deleted_count = Repositories.LOG_EVENTS.delete_batch(event_ids)

        clear_cache_pattern("events")  # Clear cache after delete
        logger.info(f"Batch deleted {deleted_count} events")
        return json_success_response(
            message=f"Deleted {deleted_count} events", data={"deleted_count": deleted_count}
        )
    except Exception as e:
        logger.error(f"Error batch deleting events: {e}")
        return json_error_response("Failed to delete events", status_code=500)


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
                return json_error_response("event_name cannot be empty", status_code=400)
            if len(event_name) > 200:
                return json_error_response(
                    "event_name exceeds maximum length of 200 characters", status_code=400
                )
            updates["event_name"] = html.escape(event_name)

        if "event_name_cn" in updates:
            event_name_cn = updates["event_name_cn"].strip()
            if len(event_name_cn) > 200:
                return json_error_response(
                    "event_name_cn exceeds maximum length of 200 characters", status_code=400
                )
            updates["event_name_cn"] = html.escape(event_name_cn)

        # Use Repository batch update
        updated_count = Repositories.LOG_EVENTS.update_batch(event_ids, updates)

        clear_cache_pattern("events")  # Clear cache after update
        logger.info(f"Batch updated {updated_count} events")
        return json_success_response(
            message=f"Updated {updated_count} events", data={"updated_count": updated_count}
        )
    except Exception as e:
        logger.error(f"Error batch updating events: {e}")
        return json_error_response("Failed to update events", status_code=500)
