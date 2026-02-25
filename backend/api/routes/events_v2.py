#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEPRECATED - Legacy DDD Implementation

This file contains the legacy DDD-based API implementation.

Please use the main API routes instead:
- from backend.api.routes.events import events_bp

Migration Date: 2026-02-25
Planned Removal: Version 2.0
Reason: Architecture migration to simplified layered architecture

---
DEPRECATED - 遗留DDD实现

此文件包含基于DDD的遗留API实现。

请使用主API路由:
- from backend.api.routes.events import events_bp

迁移日期: 2026-02-25
计划移除: 版本 2.0
原因: 迁移到精简分层架构

---
Events API Routes V2 - DDD Architecture

This module provides event-related API endpoints using the DDD architecture.
It uses the EventAppService from the application layer.

Migration Status: Phase 2 - DDD Migration
"""

import logging
from typing import Any, Dict, Tuple

from flask import request, jsonify

from backend.api import api_bp
from backend.application.services.event_app_service import EventAppService
from backend.infrastructure.persistence.event_repository_impl import EventRepositoryImpl
from backend.domain.exceptions.domain_exceptions import (
    EventAlreadyExists,
    InvalidEventName,
    ParameterAlreadyExists,
)

logger = logging.getLogger(__name__)

# Dependency Injection - Create service instance
_event_repo = EventRepositoryImpl()
_event_service = EventAppService(_event_repo)


@api_bp.route("/api/v2/events", methods=["GET"])
def api_list_events_v2() -> Tuple[Dict[str, Any], int]:
    """
    API V2: List all events with pagination (DDD Architecture)

    Query Parameters:
        - game_gid: Filter by game GID (required)
        - category: Filter by category (optional)
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20)

    Returns:
        JSON response with events list and pagination info
    """
    try:
        game_gid = request.args.get("game_gid", type=int)
        if not game_gid:
            return jsonify({
                "success": False,
                "error": "game_gid is required"
            }), 400

        category = request.args.get("category")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)

        # Limit per_page to prevent excessive queries
        per_page = min(per_page, 100)

        result = _event_service.get_events_by_game(
            game_gid=game_gid,
            category=category,
            page=page,
            per_page=per_page
        )

        return jsonify({
            "success": True,
            "data": result
        }), 200

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error listing events: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@api_bp.route("/api/v2/events/<int:event_id>", methods=["GET"])
def api_get_event_v2(event_id: int) -> Tuple[Dict[str, Any], int]:
    """
    API V2: Get event by ID (DDD Architecture)

    Args:
        event_id: Event ID

    Returns:
        JSON response with event details
    """
    try:
        event = _event_service.get_event_by_id(event_id)

        if not event:
            return jsonify({
                "success": False,
                "error": f"Event not found: id={event_id}"
            }), 404

        return jsonify({
            "success": True,
            "data": event
        }), 200

    except Exception as e:
        logger.error(f"Error getting event: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@api_bp.route("/api/v2/events", methods=["POST"])
def api_create_event_v2() -> Tuple[Dict[str, Any], int]:
    """
    API V2: Create a new event (DDD Architecture)

    Request Body:
        {
            "game_gid": int,
            "event_name": str,
            "category": str,
            "description": str (optional)
        }

    Returns:
        JSON response with created event
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400

        game_gid = data.get("game_gid")
        event_name = data.get("event_name")
        category = data.get("category")
        description = data.get("description")

        if not game_gid or not event_name or not category:
            return jsonify({
                "success": False,
                "error": "game_gid, event_name, and category are required"
            }), 400

        event = _event_service.create_event(
            game_gid=game_gid,
            event_name=event_name,
            category=category,
            description=description
        )

        return jsonify({
            "success": True,
            "data": event
        }), 201

    except EventAlreadyExists as e:
        logger.warning(f"Event already exists: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 409
    except InvalidEventName as e:
        logger.warning(f"Invalid event name: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error creating event: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@api_bp.route("/api/v2/events/<int:event_id>", methods=["PUT"])
def api_update_event_v2(event_id: int) -> Tuple[Dict[str, Any], int]:
    """
    API V2: Update an event (DDD Architecture)

    Args:
        event_id: Event ID

    Request Body:
        {
            "name": str (optional),
            "category": str (optional),
            "description": str (optional)
        }

    Returns:
        JSON response with updated event
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400

        event = _event_service.update_event(
            event_id=event_id,
            name=data.get("name"),
            category=data.get("category"),
            description=data.get("description")
        )

        return jsonify({
            "success": True,
            "data": event
        }), 200

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error updating event: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@api_bp.route("/api/v2/events/<int:event_id>", methods=["DELETE"])
def api_delete_event_v2(event_id: int) -> Tuple[Dict[str, Any], int]:
    """
    API V2: Delete an event (DDD Architecture)

    Args:
        event_id: Event ID

    Returns:
        JSON response with success status
    """
    try:
        _event_service.delete_event(event_id)

        return jsonify({
            "success": True,
            "message": f"Event {event_id} deleted successfully"
        }), 200

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404
    except Exception as e:
        logger.error(f"Error deleting event: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@api_bp.route("/api/v2/events/<int:event_id>/parameters", methods=["POST"])
def api_add_parameter_v2(event_id: int) -> Tuple[Dict[str, Any], int]:
    """
    API V2: Add a parameter to an event (DDD Architecture)

    Args:
        event_id: Event ID

    Request Body:
        {
            "param_name": str,
            "param_type": str,
            "json_path": str,
            "description": str (optional)
        }

    Returns:
        JSON response with updated event
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400

        param_name = data.get("param_name")
        param_type = data.get("param_type")
        json_path = data.get("json_path")
        description = data.get("description")

        if not param_name or not param_type or not json_path:
            return jsonify({
                "success": False,
                "error": "param_name, param_type, and json_path are required"
            }), 400

        event = _event_service.add_parameter(
            event_id=event_id,
            param_name=param_name,
            param_type=param_type,
            json_path=json_path,
            description=description
        )

        return jsonify({
            "success": True,
            "data": event
        }), 200

    except ParameterAlreadyExists as e:
        logger.warning(f"Parameter already exists: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 409
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error adding parameter: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@api_bp.route("/api/v2/events/<int:event_id>/parameters/<param_name>", methods=["DELETE"])
def api_remove_parameter_v2(event_id: int, param_name: str) -> Tuple[Dict[str, Any], int]:
    """
    API V2: Remove a parameter from an event (DDD Architecture)

    Args:
        event_id: Event ID
        param_name: Parameter name

    Returns:
        JSON response with updated event
    """
    try:
        event = _event_service.remove_parameter(
            event_id=event_id,
            param_name=param_name
        )

        return jsonify({
            "success": True,
            "data": event
        }), 200

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error removing parameter: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@api_bp.route("/api/v2/events/search", methods=["GET"])
def api_search_events_v2() -> Tuple[Dict[str, Any], int]:
    """
    API V2: Search events (DDD Architecture)

    Query Parameters:
        - keyword: Search keyword (required)
        - game_gid: Filter by game GID (optional)

    Returns:
        JSON response with matching events
    """
    try:
        keyword = request.args.get("keyword")
        game_gid = request.args.get("game_gid", type=int)

        if not keyword:
            return jsonify({
                "success": False,
                "error": "keyword is required"
            }), 400

        events = _event_service.search_events(
            keyword=keyword,
            game_gid=game_gid
        )

        return jsonify({
            "success": True,
            "data": events
        }), 200

    except Exception as e:
        logger.error(f"Error searching events: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@api_bp.route("/api/v2/events/<int:event_id>/statistics", methods=["GET"])
def api_get_event_statistics_v2(event_id: int) -> Tuple[Dict[str, Any], int]:
    """
    API V2: Get event statistics (DDD Architecture)

    Args:
        event_id: Event ID

    Returns:
        JSON response with event statistics
    """
    try:
        stats = _event_service.get_event_statistics(event_id)

        if not stats:
            return jsonify({
                "success": False,
                "error": f"Event not found: id={event_id}"
            }), 404

        return jsonify({
            "success": True,
            "data": stats
        }), 200

    except Exception as e:
        logger.error(f"Error getting event statistics: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500
