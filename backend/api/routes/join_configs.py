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

Architecture: API Layer → Service Layer → Repository Layer
"""

import json
import logging

from flask import request, session

# Import shared utilities
from backend.core.utils import json_error_response, json_success_response, validate_json_request
from backend.models.entities import JoinConfigEntity

# Import Service Layer
from backend.services.join_configs.join_config_service import JoinConfigService

# Import the parent blueprint
from .. import api_bp

logger = logging.getLogger(__name__)


@api_bp.route("/api/join-configs", methods=["GET"])
def api_list_join_configs():
    """
    API: List all join configurations with optional filtering

    Query params:
    - game_gid: Filter by game GID (required)
    - join_type: Filter by join type (union_all|join|where_in)
    """
    game_gid = request.args.get("game_gid", type=int)

    if not game_gid:
        game_gid = session.get("current_game_gid")

    if not game_gid:
        return json_error_response("game_gid required", status_code=400)

    join_type = request.args.get("join_type")

    try:
        service = JoinConfigService()
        configs = service.list_join_configs(game_gid, join_type)

        # Convert Entity objects to dict
        configs_data = [config.model_dump() for config in configs]
        return json_success_response(data=configs_data)

    except ValueError as e:
        logger.error(f"Validation error listing join configs: {e}")
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error listing join configs: {e}")
        return json_error_response("Failed to fetch join configs", status_code=500)


@api_bp.route("/api/join-configs/<int:id>", methods=["GET"])
def api_get_join_config(id):
    """API: Get a single join configuration by ID"""
    try:
        service = JoinConfigService()
        config = service.get_join_config_by_id(id)

        if not config:
            return json_error_response("Join config not found", status_code=404)

        return json_success_response(data=config.model_dump())

    except ValueError as e:
        logger.error(f"Validation error fetching join config {id}: {e}")
        return json_error_response(str(e), status_code=400)
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
        "source_events": [1,2,3],  # JSON array (or string)
        "join_config": {},  # JSON for JOIN type (or join_condition)
        "output_fields": [],  # JSON array (or string)
        "output_table": "dwd_output_view",
        "join_type": "union_all|join|where_in",
        "where_conditions": {},  # optional
        "field_mappings": {},  # optional
        "description": "Description",
        "game_gid": 10000147
    }
    """
    is_valid, data, error = validate_json_request(
        [
            "name",
            "display_name",
            "source_events",
            "output_fields",
            "output_table",
            "game_gid",
        ]
    )
    if not is_valid:
        return json_error_response(error, status_code=400)

    try:
        service = JoinConfigService()

        # Parse JSON fields if they are strings
        def parse_json_field(value, field_name):
            """Parse JSON field if it's a string, otherwise return as-is"""
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON in {field_name}: {str(e)}")
            return value

        # Parse JSON fields
        source_events = parse_json_field(data["source_events"], "source_events")
        output_fields = parse_json_field(data["output_fields"], "output_fields")

        # Handle join_config (API may send join_condition)
        join_config = data.get("join_config") or data.get("join_condition", {})
        join_config = parse_json_field(join_config, "join_config")

        # Parse optional JSON fields
        where_conditions = data.get("where_conditions", {})
        field_mappings = data.get("field_mappings", {})

        # Validate join_type
        join_type = data.get("join_type", "join")
        if join_type not in ["union_all", "join", "where_in"]:
            return json_error_response(f"Invalid join_type: {join_type}", status_code=400)

        # Create JoinConfigEntity (Pydantic will validate)
        config_data = JoinConfigEntity(
            name=data["name"],
            display_name=data["display_name"],
            source_events=source_events,
            join_config=join_config,
            output_fields=output_fields,
            output_table=data["output_table"],
            join_type=join_type,
            where_conditions=where_conditions,
            field_mappings=field_mappings,
            description=data.get("description", data["display_name"]),
            game_gid=data["game_gid"],
        )

        # Create config via service
        created_config = service.create_join_config(config_data)

        return json_success_response(
            data={"config_id": created_config.id},
            message="Join configuration created successfully",
        )

    except ValueError as e:
        # Validation errors from service or Pydantic
        logger.error(f"Validation error creating join config: {e}")
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error creating join config: {e}")
        return json_error_response("Failed to create join config", status_code=500)


@api_bp.route("/api/join-configs/<int:id>", methods=["PUT", "PATCH"])
def api_update_join_config(id):
    """
    API: Update an existing join configuration

    Request body: Same as create (all fields optional)
    """
    is_valid, data, error = validate_json_request()
    if not is_valid:
        return json_error_response(error, status_code=400)

    if not data:
        return json_error_response("No fields to update", status_code=400)

    try:
        service = JoinConfigService()

        # Validate join_type if provided
        if "join_type" in data:
            if data["join_type"] not in ["union_all", "join", "where_in"]:
                return json_error_response(
                    f"Invalid join_type: {data['join_type']}", status_code=400
                )

        # Parse JSON fields if they are strings (service handles dict objects)
        json_fields = [
            "source_events",
            "join_config",
            "join_condition",
            "output_fields",
            "where_conditions",
            "field_mappings",
        ]
        for field in json_fields:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = json.loads(data[field])
                except json.JSONDecodeError:
                    return json_error_response(f"Invalid JSON in {field}", status_code=400)

        # Handle alias: join_condition → join_config
        if "join_condition" in data and "join_config" not in data:
            data["join_config"] = data.pop("join_condition")

        # Update config via service
        updated_config = service.update_join_config(id, data)

        return json_success_response(
            data=updated_config.model_dump(), message="Join configuration updated successfully"
        )

    except ValueError as e:
        # Validation errors from service
        logger.error(f"Validation error updating join config {id}: {e}")
        return json_error_response(
            str(e), status_code=404 if "not found" in str(e).lower() else 400
        )
    except Exception as e:
        logger.error(f"Error updating join config {id}: {e}")
        return json_error_response("Failed to update join config", status_code=500)


@api_bp.route("/api/join-configs/<int:id>", methods=["DELETE"])
def api_delete_join_config(id):
    """API: Delete a join configuration"""
    try:
        service = JoinConfigService()
        service.delete_join_config(id)

        return json_success_response(message="Join configuration deleted successfully")

    except ValueError as e:
        # Config not found
        logger.error(f"Validation error deleting join config {id}: {e}")
        return json_error_response(str(e), status_code=404)
    except Exception as e:
        logger.error(f"Error deleting join config {id}: {e}")
        return json_error_response("Failed to delete join config", status_code=500)
