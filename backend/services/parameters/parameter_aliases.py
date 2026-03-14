#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameter Aliases Management Module - REFACTORED
===============================================

Refactored to use Repository pattern instead of direct database access.

Migration Status: Repository Pattern Implementation (2026-03-03)
- Removed direct database access
- Added ParameterAliasRepository integration
- All methods now use Repository layer
- Maintained backward compatibility
"""

from flask import Blueprint, request

from backend.core.logging import get_logger
from backend.core.utils import json_error_response, json_success_response
from backend.models.repositories.games import GameRepository
from backend.models.repositories.parameter_alias_repository import ParameterAliasRepository
from backend.models.repositories.parameters import ParameterRepository

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

    # Use Repository
    alias_repo = ParameterAliasRepository()
    aliases = alias_repo.find_by_param_and_game(param_id, game_gid)

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

    # Use Repositories
    game_repo = GameRepository()
    game = game_repo.find_by_gid(game_gid)
    if not game:
        return json_error_response("Game not found", status_code=404)

    # Get game_id for legacy support
    game_id = game.id

    # Validate parameter exists (param_id references event_params table)
    param_repo = ParameterRepository()
    param = param_repo.find_by_id(param_id)
    if not param:
        return json_error_response("Parameter not found", status_code=404)

    # Check if alias already exists
    alias_repo = ParameterAliasRepository()
    existing = alias_repo.find_by_alias_and_game(alias, game_gid)

    if existing:
        return json_error_response("Alias already exists for this parameter", status_code=400)

    # Create alias
    alias_id = alias_repo.create_alias(
        game_id=game_id,
        game_gid=game_gid,
        param_id=param_id,
        alias=alias,
        display_name=display_name,
        is_preferred=bool(is_preferred),
    )

    created_alias = alias_repo.find_by_id(alias_id)
    return json_success_response(
        data=created_alias, message="Parameter alias created", status_code=201
    )


@parameter_aliases_bp.route("/api/parameter-aliases/<int:alias_id>", methods=["PUT"])
def update_parameter_alias(alias_id):
    """API: Update a parameter alias"""
    data = request.get_json()

    # Use Repository
    alias_repo = ParameterAliasRepository()
    alias = alias_repo.find_by_id(alias_id)

    if not alias:
        return json_error_response("Parameter alias not found", status_code=404)

    # Update alias
    success = alias_repo.update_alias(
        alias_id=alias_id,
        alias=data.get("alias"),
        display_name=data.get("display_name"),
        is_preferred=data.get("is_preferred"),
    )

    if not success:
        return json_error_response("Failed to update alias", status_code=500)

    updated_alias = alias_repo.find_by_id(alias_id)
    return json_success_response(data=updated_alias, message="Parameter alias updated")


@parameter_aliases_bp.route("/api/parameter-aliases/<int:alias_id>/prefer", methods=["PUT"])
def set_preferred_alias(alias_id):
    """API: Set an alias as preferred"""
    # Use Repository
    alias_repo = ParameterAliasRepository()
    alias = alias_repo.find_by_id(alias_id)

    if not alias:
        return json_error_response("Parameter alias not found", status_code=404)

    # Set as preferred
    success = alias_repo.set_preferred_alias(alias_id)

    if not success:
        return json_error_response("Failed to set preferred alias", status_code=500)

    updated_alias = alias_repo.find_by_id(alias_id)
    return json_success_response(data=updated_alias, message="Preferred alias set")


@parameter_aliases_bp.route("/api/parameters/<int:param_id>/display-name", methods=["PUT"])
def update_parameter_display_name(param_id):
    """API: Update parameter's display name

    Note: This endpoint references event_params table
    """
    data = request.get_json()

    if "display_name" not in data:
        return json_error_response("display_name is required", status_code=400)

    display_name = data["display_name"]

    # Use Repository
    param_repo = ParameterRepository()
    param = param_repo.find_by_id(param_id)

    if not param:
        return json_error_response("Parameter not found", status_code=404)

    # Update parameter display name
    updated_param = param_repo.update(param_id, {"name_cn": display_name})

    if not updated_param:
        return json_error_response("Failed to update parameter", status_code=500)

    # Convert to dict for response
    param_dict = (
        updated_param.model_dump() if hasattr(updated_param, 'model_dump') else updated_param
    )
    return json_success_response(data=param_dict, message="Parameter display name updated")
