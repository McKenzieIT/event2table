"""
Join Configs API Routes Module

This module contains all join configuration-related API endpoints for managing
multi-event join configurations.

Core endpoints:
- GET /api/join-configs - List all join configurations
- POST /api/join-configs - Create a new join configuration
- GET /api/join-configs/<int:id> - Get a single join configuration
- PUT /api/join-configs/<int:id> - Update a join configuration
- DELETE /api/join-configs/<int:id> - Delete a join configuration
"""

import logging
import sqlite3

# Import cache functions
import sys

from flask import request

# Import shared utilities
from backend.core.utils import (
    execute_write,
    fetch_all_as_dict,
    fetch_one_as_dict,
    json_error_response,
    json_success_response,
    validate_json_request,
)

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


# Import Repository pattern for data access
from backend.core.data_access import Repositories

# Import the parent blueprint
from .. import api_bp

logger = logging.getLogger(__name__)


@api_bp.route("/api/join-configs", methods=["GET"])
def api_list_join_configs():
    """
    API: List all join configurations with optional filtering

    Query params:
    - game_gid: Filter by game GID (recommended)
    - game_id: Filter by game database ID (deprecated, for backward compatibility)
    - join_type: Filter by join type (union_all|join|where_in)
    """
    # Support both game_gid (new) and game_id (legacy) parameters
    game_gid = request.args.get("game_gid", type=int)
    game_id = request.args.get("game_id", type=int)

    join_type = request.args.get("join_type")

    query = "SELECT * FROM join_configs WHERE 1=1"
    params = []

    # Use game_gid if provided, otherwise convert game_id to game_gid
    filter_column = "game_gid"
    filter_value = None

    if game_gid:
        filter_value = game_gid
    elif game_id:
        # Convert game_id to game_gid for backward compatibility
        game = Repositories.GAMES.find_by_id(game_id)
        if game:
            filter_value = game["gid"]
        else:
            return json_error_response("Game not found", status_code=404)

    if filter_value:
        query += f" AND {filter_column} = ?"
        params.append(filter_value)

    if join_type:
        query += " AND join_type = ?"
        params.append(join_type)

    query += " ORDER BY created_at DESC"

    try:
        configs = fetch_all_as_dict(query, tuple(params))
        return json_success_response(data=configs)
    except Exception as e:
        logger.error(f"Error listing join configs: {e}")
        return json_error_response("Failed to fetch join configs", status_code=500)


@api_bp.route("/api/join-configs/<int:id>", methods=["GET"])
def api_get_join_config(id):
    """API: Get a single join configuration by ID"""
    try:
        config = Repositories.JOIN_CONFIGS.find_by_id(id)

        if not config:
            return json_error_response("Join config not found", status_code=404)

        return json_success_response(data=config)
    except Exception as e:
        logger.error(f"Error fetching join config {id}: {e}")
        return json_error_response("Failed to fetch join config", status_code=500)


@api_bp.route("/api/join-configs", methods=["POST"])
def api_create_join_config():
    """
    API: Create a new join configuration

    Request body:
    {
        "name": "config_name",
        "display_name": "Display Name",
        "source_events": "[1,2,3]",  # JSON array
        "join_conditions": "{}",  # JSON for JOIN type
        "output_fields": "[]",  # JSON array
        "output_table": "dwd_output_view",
        "join_type": "union_all|join|where_in",
        "where_conditions": "{}",  # optional
        "field_mappings": "{}",  # optional
        "description": "Description",
        "game_gid": 10000147
    }
    """
    is_valid, data, error = validate_json_request(
        ["name", "display_name", "source_events", "output_fields", "output_table", "game_gid"]
    )
    if not is_valid:
        return json_error_response(error, status_code=400)

    try:
        # Validate JSON fields
        import json

        try:
            source_events_list = json.loads(data["source_events"])
            output_fields_list = json.loads(data["output_fields"])
        except json.JSONDecodeError as e:
            return json_error_response(
                f"Invalid JSON in source_events or output_fields: {str(e)}", status_code=400
            )

        # Validate join_type
        join_type = data.get("join_type", "join")
        if join_type not in ["union_all", "join", "where_in"]:
            return json_error_response(f"Invalid join_type: {join_type}", status_code=400)

        # Prepare join_condition based on type
        join_condition = data.get("join_condition", "{}")
        if join_type == "join" and not join_condition:
            return json_error_response("join_condition required for JOIN type", status_code=400)

        # Convert game_gid to game_id for database storage (if needed)
        game_gid = data["game_gid"]
        game = Repositories.GAMES.find_by_field("gid", game_gid)
        if not game:
            return json_error_response(f"Game with GID {game_gid} not found", status_code=404)

        # Insert join config (store game_id internally for foreign key)
        config_id = execute_write(
            """
            INSERT INTO join_configs (
                name, display_name, source_events, join_condition,
                output_fields, output_table, join_type,
                where_conditions, field_mappings, description, game_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                data["name"],
                data["display_name"],
                data["source_events"],
                join_condition,
                data["output_fields"],
                data["output_table"],
                join_type,
                data.get("where_conditions", "{}"),
                data.get("field_mappings", "{}"),
                data.get("description", data["display_name"]),
                game["id"],  # Store database ID for foreign key
            ),
            return_last_id=True,
        )

        clear_cache_pattern("join_configs")
        logger.info(f"Created join config {config_id}: {data['name']}")

        return json_success_response(
            data={"config_id": config_id}, message="Join configuration created successfully"
        )

    except sqlite3.IntegrityError:
        return json_error_response("Join config name already exists", status_code=400)
    except Exception as e:
        logger.error(f"Error creating join config: {e}")
        return json_error_response("Failed to create join config", status_code=500)


@api_bp.route("/api/join-configs/<int:id>", methods=["PUT", "PATCH"])
def api_update_join_config(id):
    """
    API: Update an existing join configuration

    Request body: Same as create
    """
    join_config = Repositories.JOIN_CONFIGS.find_by_id(id)
    if not join_config:
        return json_error_response("Join config not found", status_code=404)

    is_valid, data, error = validate_json_request()
    if not is_valid:
        return json_error_response(error, status_code=400)

    try:
        import json

        # Validate JSON fields if provided
        if "source_events" in data:
            try:
                json.loads(data["source_events"])
            except json.JSONDecodeError:
                return json_error_response("Invalid JSON in source_events", status_code=400)

        if "output_fields" in data:
            try:
                json.loads(data["output_fields"])
            except json.JSONDecodeError:
                return json_error_response("Invalid JSON in output_fields", status_code=400)

        # Validate join_type if provided
        if "join_type" in data:
            if data["join_type"] not in ["union_all", "join", "where_in"]:
                return json_error_response(
                    f'Invalid join_type: {data["join_type"]}', status_code=400
                )

        # Handle game_gid conversion to game_id for database storage
        if "game_gid" in data:
            game_gid = data["game_gid"]
            game = Repositories.GAMES.find_by_field("gid", game_gid)
            if not game:
                return json_error_response(f"Game with GID {game_gid} not found", status_code=404)
            # Store game_id internally for foreign key
            data["game_id"] = game["id"]
            # Remove game_gid from data as it's not a database column
            del data["game_gid"]

        # Build UPDATE query dynamically
        update_fields = []
        update_values = []

        for field in [
            "name",
            "display_name",
            "source_events",
            "join_condition",
            "output_fields",
            "output_table",
            "join_type",
            "where_conditions",
            "field_mappings",
            "description",
            "game_id",
        ]:
            if field in data:
                update_fields.append(f"{field} = ?")
                update_values.append(data[field])

        if not update_fields:
            return json_error_response("No fields to update", status_code=400)

        update_values.append(id)
        update_query = f"UPDATE join_configs SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"

        execute_write(update_query, tuple(update_values))

        clear_cache_pattern("join_configs")
        logger.info(f"Updated join config {id}")

        return json_success_response(message="Join configuration updated successfully")

    except Exception as e:
        logger.error(f"Error updating join config {id}: {e}")
        return json_error_response("Failed to update join config", status_code=500)


@api_bp.route("/api/join-configs/<int:id>", methods=["DELETE"])
def api_delete_join_config(id):
    """API: Delete a join configuration"""
    join_config = Repositories.JOIN_CONFIGS.find_by_id(id)
    if not join_config:
        return json_error_response("Join config not found", status_code=404)

    try:
        Repositories.JOIN_CONFIGS.delete(id)

        clear_cache_pattern("join_configs")
        logger.info(f"Deleted join config {id}: {join_config['name']}")

        return json_success_response(message="Join configuration deleted successfully")
    except Exception as e:
        logger.error(f"Error deleting join config {id}: {e}")
        return json_error_response("Failed to delete join config", status_code=500)
