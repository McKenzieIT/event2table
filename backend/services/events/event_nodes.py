#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Nodes Management Module
Handles event node CRUD operations
"""

import json
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    session,
)
from backend.core.logging import get_logger
from backend.core.utils import (
    fetch_all_as_dict,
    fetch_one_as_dict,
    execute_write,
    success_response,
    error_response,
    validate_game_exists,
    get_event_with_game_info,
    json_success_response,
    json_error_response,
)
from backend.core.cache.cache_system import clear_game_cache

logger = get_logger(__name__)

event_nodes_bp = Blueprint("event_nodes", __name__)


# NOTE: This route has been migrated to React (EventNodes.jsx)
# The React component at /event-nodes handles the UI rendering
# Only API routes are kept below
# @event_nodes_bp.route('/event-nodes')
# def list_event_nodes():
#     """
#     List all event nodes with pagination
#
#     **Game Context Required**: This page requires a game to be selected first.
#     """
#     # Get game_gid from query parameter or session
#     game_gid = request.args.get('game_gid', type=int) or session.get('current_game_gid')
#
#     # Pagination parameters
#     page = request.args.get('page', 1, type=int)
#     per_page = request.args.get('per_page', 20, type=int)
#
#     # Validate pagination parameters
#     if page < 1: page = 1
#     if per_page not in [10, 20, 50, 100]: per_page = 20
#
#     offset = (page - 1) * per_page
#
#     # Check if there are any games in database
#     result = fetch_one_as_dict('SELECT COUNT(*) as count FROM games')
#     games_exist = result['count'] > 0 if result else False
#
#     if not games_exist:
#         flash('请先创建游戏', 'error')
#         return redirect(url_for('games.list_games'))
#
#     # **游戏上下文强制验证**: 必须选择游戏后才能查看事件节点
#     if not game_gid:
#         flash('请先选择游戏', 'error')
#         return redirect(url_for('games.list_games'))
#
#     # Set session for game context
#     session['current_game_gid'] = game_gid
#
#     # Get total count for pagination
#     count_result = fetch_one_as_dict('''
#         SELECT COUNT(*) as total
#         FROM event_nodes
#         WHERE game_gid = ?
#     ''', (game_gid,))
#     total_nodes = count_result['total'] if count_result else 0
#     total_pages = max(1, (total_nodes + per_page - 1) // per_page)
#
#     # **游戏上下文过滤**: 只显示当前游戏的事件节点
#     nodes = fetch_all_as_dict('''
#         SELECT en.*, le.event_name, le.event_name_cn, g.name as game_name, g.gid
#         FROM event_nodes en
#         LEFT JOIN log_events le ON en.event_id = le.id
#         LEFT JOIN games g ON en.game_gid = g.id
#         WHERE en.game_gid = ?
#         ORDER BY en.id DESC
#         LIMIT ? OFFSET ?
#     ''', (game_gid, per_page, offset))
#
#     # Parse config_json for each node
#     for node in nodes:
#         try:
#             config = json.loads(node['config_json'])
#             node['field_count'] = len(config.get('fieldList', []))
#         except:
#             node['field_count'] = 0
#
#     # Get current game info
#     current_game = fetch_one_as_dict('SELECT id, name, gid FROM games WHERE id = ?', (game_gid,))
#
#     return render_template('event_nodes.html',
#                           nodes=nodes,
#                           selected_game_id=game_gid,
#                           current_game=current_game,
#                           page=page,
#                           per_page=per_page,
#                           total_pages=total_pages,
#                           total_nodes=total_nodes)
#
@event_nodes_bp.route("/api/event-nodes", methods=["GET"])
def get_event_nodes():
    """API: Get all event nodes for a game"""
    game_gid = request.args.get("game_gid", type=str)
    if not game_gid:
        return json_error_response("game_gid is required", status_code=400)

    # Validate game exists
    game = fetch_one_as_dict("SELECT gid FROM games WHERE gid = ?", (game_gid,))
    if not game:
        return json_error_response("Game not found", status_code=404)

    # Query using game_gid directly (no conversion needed)
    nodes = fetch_all_as_dict(
        """
        SELECT en.*, le.event_name, le.event_name_cn
        FROM event_nodes en
        LEFT JOIN log_events le ON en.event_id = le.id
        WHERE en.game_gid = ? AND en.is_active = 1
        ORDER BY en.created_at DESC
    """,
        (game_gid,),
    )

    # Parse config_json
    for node in nodes:
        try:
            node["config"] = json.loads(node["config_json"])
        except (json.JSONDecodeError, TypeError, ValueError):
            node["config"] = {}

    return json_success_response(data={"nodes": nodes}, message="Event nodes retrieved")


@event_nodes_bp.route("/api/event-nodes/<int:node_id>", methods=["GET"])
def get_event_node(node_id):
    """API: Get a single event node"""
    node = fetch_one_as_dict(
        """
        SELECT en.*, le.event_name, le.event_name_cn
        FROM event_nodes en
        LEFT JOIN log_events le ON en.event_id = le.id
        WHERE en.id = ?
    """,
        (node_id,),
    )

    if not node:
        return json_error_response("Event node not found", status_code=404)

    # Parse config_json
    try:
        node["config"] = json.loads(node["config_json"])
    except (json.JSONDecodeError, TypeError, ValueError):
        node["config"] = {}

    return json_success_response(data={"node": node}, message="Event node retrieved")


@event_nodes_bp.route("/api/event-nodes", methods=["POST"])
def create_event_node():
    """API: Create a new event node"""
    data = request.get_json()

    # Validate required fields
    required_fields = ["game_gid", "name", "event_id", "config"]
    for field in required_fields:
        if field not in data:
            return json_error_response(f"{field} is required", status_code=400)

    game_gid = data["game_gid"]
    name = data["name"]
    event_id = data["event_id"]
    config = data["config"]

    # Validate game exists
    game = fetch_one_as_dict("SELECT gid FROM games WHERE gid = ?", (game_gid,))
    if not game:
        return json_error_response("Game not found", status_code=404)

    # Validate event exists
    event = fetch_one_as_dict("SELECT * FROM log_events WHERE id = ?", (event_id,))
    if not event:
        return json_error_response("Event not found", status_code=404)

    # Check if node with same name exists for this game
    existing = fetch_one_as_dict(
        "SELECT * FROM event_nodes WHERE game_gid = ? AND name = ?", (game_gid, name)
    )
    if existing:
        return json_error_response(
            "Event node with this name already exists", status_code=400
        )

    # Create event node
    config_json = json.dumps(config, ensure_ascii=False)
    node_id = execute_write(
        """
        INSERT INTO event_nodes (game_gid, name, event_id, config_json)
        VALUES (?, ?, ?, ?)
    """,
        (game_gid, name, event_id, config_json),
    )

    # Save parameter aliases if provided
    if "fieldList" in config:
        save_parameter_aliases(game_gid, config["fieldList"])

    # Clear cache
    clear_game_cache(game_gid)

    node = fetch_one_as_dict("SELECT * FROM event_nodes WHERE id = ?", (node_id,))
    return json_success_response(
        data={"node": node}, message="Event node created", status_code=201
    )


@event_nodes_bp.route("/api/event-nodes/<int:node_id>", methods=["PUT"])
def update_event_node(node_id):
    """API: Update an event node"""
    data = request.get_json()

    # Get existing node
    node = fetch_one_as_dict("SELECT * FROM event_nodes WHERE id = ?", (node_id,))
    if not node:
        return json_error_response("Event node not found", status_code=404)

    # Get game_gid from node for cache clearing
    game_gid = node.get("game_gid")

    # Update fields
    update_fields = []
    update_values = []

    if "name" in data:
        update_fields.append("name = ?")
        update_values.append(data["name"])

    if "event_id" in data:
        update_fields.append("event_id = ?")
        update_values.append(data["event_id"])

    if "config" in data:
        config_json = json.dumps(data["config"], ensure_ascii=False)
        update_fields.append("config_json = ?")
        update_values.append(config_json)

        # Save parameter aliases if fieldList is provided
        if "fieldList" in data["config"] and game_gid:
            save_parameter_aliases(game_gid, data["config"]["fieldList"])

    if "is_active" in data:
        update_fields.append("is_active = ?")
        update_values.append(data["is_active"])

    if update_fields:
        update_values.append(node_id)
        execute_write(
            f"""
            UPDATE event_nodes
            SET {", ".join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """,
            update_values,
        )

        # Clear cache
        if game_gid:
            clear_game_cache(game_gid)

    updated_node = fetch_one_as_dict(
        "SELECT * FROM event_nodes WHERE id = ?", (node_id,)
    )
    return json_success_response(
        data={"node": updated_node}, message="Event node updated"
    )


@event_nodes_bp.route("/api/event-nodes/<int:node_id>", methods=["DELETE"])
def delete_event_node(node_id):
    """API: Delete an event node"""
    node = fetch_one_as_dict("SELECT * FROM event_nodes WHERE id = ?", (node_id,))
    if not node:
        return json_error_response("Event node not found", status_code=404)

    # Get game_gid from node for cache clearing
    game_gid = node.get("game_gid")

    # Delete node (soft delete by setting is_active = 0)
    execute_write("UPDATE event_nodes SET is_active = 0 WHERE id = ?", (node_id,))

    # Clear cache
    if game_gid:
        clear_game_cache(game_gid)

    return json_success_response(message="Event node deleted")


def save_parameter_aliases(game_gid, field_list):
    """
    Save parameter aliases from field list

    Args:
        game_gid: Game GID (business ID)
        field_list: List of field dictionaries
    """
    # Convert game_gid to game_id for database operations
    game = fetch_one_as_dict("SELECT id FROM games WHERE gid = ?", (game_gid,))
    if not game:
        logger.warning(
            f"Game not found for game_gid={game_gid}, skipping parameter aliases save"
        )
        return
    game_id = game["id"]

    for field in field_list:
        if field.get("source") == "parameter" and "paramId" in field:
            param_id = field["paramId"]
            alias = field.get("alias", "")
            display_name = field.get("displayName", "")

            if not alias:
                continue

            # Check if alias exists for this parameter
            existing = fetch_one_as_dict(
                """
                SELECT * FROM parameter_aliases
                WHERE game_id = ? AND param_id = ? AND alias = ?
            """,
                (game_id, param_id, alias),
            )

            if existing:
                # Update usage count and last_used_at
                execute_write(
                    """
                    UPDATE parameter_aliases
                    SET usage_count = usage_count + 1,
                        last_used_at = CURRENT_TIMESTAMP,
                        display_name = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """,
                    (display_name, existing["id"]),
                )
            else:
                # Create new alias
                execute_write(
                    """
                    INSERT INTO parameter_aliases (game_id, param_id, alias, display_name, usage_count, last_used_at)
                    VALUES (?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
                """,
                    (game_id, param_id, alias, display_name),
                )
