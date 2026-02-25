#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper functions for parameter API routes

This module provides reusable functions for handling game context
resolution in parameter-related endpoints, reducing code duplication.
"""

from typing import Tuple, Optional, Dict, Any
from flask import request, session
import logging

from backend.core.utils import fetch_one_as_dict, json_error_response

logger = logging.getLogger(__name__)


def resolve_game_context() -> Tuple[Optional[int], Optional[str], Optional[str]]:
    """
    Resolve game context from request parameters or session

    Supports both game_gid (business GID, recommended) and game_id (database ID)
    for backward compatibility.

    Returns:
        Tuple of (game_id, game_gid, error_message)
        - game_id: Database ID (for common_params table queries)
        - game_gid: Business GID (for log_events table queries)
        - error_message: Error message if resolution failed, None otherwise

    Examples:
        >>> game_id, game_gid, error = resolve_game_context()
        >>> if error:
        ...     return json_error_response(error, status_code=400)
        >>> # Use game_gid for event queries, game_id for common_params queries
    """
    game_gid = request.args.get("game_gid", type=str)

    if not game_gid:
        game_gid = session.get("current_game_gid")

    if not game_gid:
        return None, None, "game_gid required"

    # Convert game_gid to game_id for common_params table queries
    game = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (game_gid,))
    if not game:
        return None, None, f"Game not found: gid={game_gid}"
    game_id = game["id"]
    return game_id, game_gid, None


def get_where_clause_for_game(
    game_gid: Optional[str] = None, game_id: Optional[int] = None
) -> Tuple[str, Any]:
    """
    Get WHERE clause and query value for game filtering

    Args:
        game_gid: Business GID (preferred)
        game_id: Database ID (fallback)

    Returns:
        Tuple of (where_clause, query_value)

    Examples:
        >>> where, value = get_where_clause_for_game(game_gid="10000147")
        >>> # Returns: ("le.game_gid = ?", "10000147")
        >>> where, value = get_where_clause_for_game(game_id=1)
        >>> # Returns: ("le.game_id = ?", 1)
    """
    if game_gid:
        return "le.game_gid = ?", game_gid
    elif game_id:
        return "le.game_id = ?", game_id
    else:
        raise ValueError("Either game_gid or game_id must be provided")


def build_parameter_query(
    base_query: str,
    where_clause: str,
    params: list,
    search: Optional[str] = None,
    type_filter: Optional[str] = None,
) -> Tuple[str, list]:
    """
    Build parameter query with optional filters

    Args:
        base_query: Base SQL query with placeholder for WHERE clause
        where_clause: WHERE clause for game filtering
        params: Base query parameters (game_id or game_gid)
        search: Optional search keyword
        type_filter: Optional data type filter

    Returns:
        Tuple of (query_with_filters, params_with_filters)

    Examples:
        >>> query, params = build_parameter_query(
        ...     "SELECT * FROM event_params ep JOIN log_events le WHERE {where}",
        ...     "le.game_gid = ?",
        ...     ["10000147"],
        ...     search="zone",
        ...     type_filter="string"
        ... )
    """
    query = base_query.replace("{where}", where_clause)
    query_params = params.copy()

    if search:
        query += " AND (ep.param_name LIKE ? OR ep.param_name_cn LIKE ?)"
        query_params.extend([f"%{search}%", f"%{search}%"])

    if type_filter:
        query += " AND pt.base_type = ?"
        query_params.append(type_filter)

    return query, query_params


def validate_parameter_name(param_name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate parameter name format

    Args:
        param_name: Parameter name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    import re

    if not param_name:
        return False, "Parameter name is required"

    # snake_case format check
    if not re.match(r"^[a-z][a-z0-9_]*$", param_name):
        return False, (
            "Parameter name must be in snake_case format "
            "(lowercase letters, numbers, underscores)"
        )

    return True, None
