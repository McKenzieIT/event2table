#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameter Aliases Management Module
Handles parameter alias CRUD operations
"""

import sqlite3
from flask import Blueprint, request, jsonify
from backend.core.logging import get_logger
from backend.core.utils import (
    fetch_all_as_dict,
    fetch_one_as_dict,
    execute_write,
    success_response,
    error_response,
    validate_game_exists,
    json_success_response,
    json_error_response,
)
from backend.core.database import get_db_connection

logger = get_logger(__name__)

parameter_aliases_bp = Blueprint("parameter_aliases", __name__)


@parameter_aliases_bp.route("/api/parameter-aliases", methods=["GET"])
def get_parameter_aliases():
    """API: Get all aliases for a parameter"""
    game_gid = request.args.get("game_gid", type=int)
    param_id = request.args.get("param_id", type=int)

    if not game_gid:
        return json_error_response("game_gid is required", status_code=400)

    if not param_id:
        return json_error_response("param_id is required", status_code=400)

    # Convert game_gid to game_id
    game = fetch_one_as_dict("SELECT id FROM games WHERE gid = ?", (game_gid,))
    if not game:
        return json_error_response("Game not found", status_code=404)
    game_id = game["id"]

    # Get aliases, ordered by is_preferred (preferred first), then usage_count
    # Note: param_id references event_params table (not the old 'parameters' table)
    aliases = fetch_all_as_dict(
        """
        SELECT pa.*, ep.param_name, ep.param_name_cn
        FROM parameter_aliases pa
        LEFT JOIN event_params ep ON pa.param_id = ep.id
        WHERE pa.game_id = ? AND pa.param_id = ?
        ORDER BY pa.is_preferred DESC, pa.usage_count DESC, pa.last_used_at DESC
    """,
        (game_id, param_id),
    )

    return json_success_response(data=aliases, message="Parameter aliases retrieved")


@parameter_aliases_bp.route("/api/parameter-aliases", methods=["POST"])
def create_parameter_alias():
    """API: Create a new parameter alias"""
    data = request.get_json()

    # Validate required fields
    required_fields = ["game_gid", "param_id", "alias"]
    for field in required_fields:
        if field not in data:
            return json_error_response(f"{field} is required", status_code=400)

    game_gid = data["game_gid"]
    param_id = data["param_id"]
    alias = data["alias"]
    display_name = data.get("display_name", "")
    is_preferred = data.get("is_preferred", 0)

    # Convert game_gid to game_id
    game = fetch_one_as_dict("SELECT id FROM games WHERE gid = ?", (game_gid,))
    if not game:
        return json_error_response("Game not found", status_code=404)
    game_id = game["id"]

    # Validate parameter exists (param_id references event_params table)
    param = fetch_one_as_dict("SELECT * FROM event_params WHERE id = ?", (param_id,))
    if not param:
        return json_error_response("Parameter not found", status_code=404)

    # Check if alias already exists
    existing = fetch_one_as_dict(
        """
        SELECT * FROM parameter_aliases
        WHERE game_id = ? AND param_id = ? AND alias = ?
    """,
        (game_id, param_id, alias),
    )

    if existing:
        return json_error_response("Alias already exists for this parameter", status_code=400)

    # If setting as preferred, unset other preferred aliases
    if is_preferred:
        execute_write(
            """
            UPDATE parameter_aliases
            SET is_preferred = 0
            WHERE game_id = ? AND param_id = ?
        """,
            (game_id, param_id),
        )

    # Create alias
    alias_id = execute_write(
        """
        INSERT INTO parameter_aliases (game_id, param_id, alias, display_name, is_preferred, usage_count, last_used_at)
        VALUES (?, ?, ?, ?, ?, 0, NULL)
    """,
        (game_id, param_id, alias, display_name, is_preferred),
        return_last_id=True,
    )

    alias = fetch_one_as_dict("SELECT * FROM parameter_aliases WHERE id = ?", (alias_id,))
    return json_success_response(data=alias, message="Parameter alias created", status_code=201)


@parameter_aliases_bp.route("/api/parameter-aliases/<int:alias_id>", methods=["PUT"])
def update_parameter_alias(alias_id):
    """API: Update a parameter alias"""
    data = request.get_json()

    # Get existing alias
    alias = fetch_one_as_dict("SELECT * FROM parameter_aliases WHERE id = ?", (alias_id,))
    if not alias:
        return json_error_response("Parameter alias not found", status_code=404)

    # Update fields
    update_fields = []
    update_values = []

    if "alias" in data:
        update_fields.append("alias = ?")
        update_values.append(data["alias"])

    if "display_name" in data:
        update_fields.append("display_name = ?")
        update_values.append(data["display_name"])

    if "is_preferred" in data:
        # If setting as preferred, unset other preferred aliases
        if data["is_preferred"]:
            execute_write(
                """
                UPDATE parameter_aliases
                SET is_preferred = 0
                WHERE game_id = ? AND param_id = ? AND id != ?
            """,
                (alias["game_id"], alias["param_id"], alias_id),
            )

        update_fields.append("is_preferred = ?")
        update_values.append(data["is_preferred"])

    if update_fields:
        update_values.append(alias_id)
        execute_write(
            f"""
            UPDATE parameter_aliases
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """,
            update_values,
        )

    updated_alias = fetch_one_as_dict("SELECT * FROM parameter_aliases WHERE id = ?", (alias_id,))
    return json_success_response(data=updated_alias, message="Parameter alias updated")


@parameter_aliases_bp.route("/api/parameter-aliases/<int:alias_id>/prefer", methods=["PUT"])
def set_preferred_alias(alias_id):
    """API: Set an alias as preferred"""
    # Get existing alias
    alias = fetch_one_as_dict("SELECT * FROM parameter_aliases WHERE id = ?", (alias_id,))
    if not alias:
        return json_error_response("Parameter alias not found", status_code=404)

    game_id = alias["game_id"]
    param_id = alias["param_id"]

    # Unset other preferred aliases
    execute_write(
        """
        UPDATE parameter_aliases
        SET is_preferred = 0
        WHERE game_id = ? AND param_id = ?
    """,
        (game_id, param_id),
    )

    # Set this alias as preferred
    execute_write(
        """
        UPDATE parameter_aliases
        SET is_preferred = 1, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """,
        (alias_id,),
    )

    updated_alias = fetch_one_as_dict("SELECT * FROM parameter_aliases WHERE id = ?", (alias_id,))
    return json_success_response(data=updated_alias, message="Preferred alias set")


@parameter_aliases_bp.route("/api/parameters/<int:param_id>/display-name", methods=["PUT"])
def update_parameter_display_name(param_id):
    """API: Update parameter's display name

    Note: This endpoint references event_params table (not the old 'parameters' table)
    """
    data = request.get_json()

    if "display_name" not in data:
        return json_error_response("display_name is required", status_code=400)

    display_name = data["display_name"]

    # Get existing parameter (param_id references event_params table)
    param = fetch_one_as_dict("SELECT * FROM event_params WHERE id = ?", (param_id,))
    if not param:
        return json_error_response("Parameter not found", status_code=404)

    # Update parameter
    execute_write(
        """
        UPDATE event_params
        SET param_name_cn = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """,
        (display_name, param_id),
    )

    updated_param = fetch_one_as_dict("SELECT * FROM event_params WHERE id = ?", (param_id,))
    return json_success_response(data=updated_param, message="Parameter display name updated")
