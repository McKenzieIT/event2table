"""
Nodes API Routes Module

This module contains all canvas node-related API endpoints for managing
canvas nodes.

Core endpoints:
- GET /api/nodes - List all nodes
- POST /api/nodes - Create a new node
- GET /api/nodes/<int:node_id> - Get node details
- PUT /api/nodes/<int:node_id> - Update a node
- DELETE /api/nodes/<int:node_id> - Delete a node

Event Node Builder API aliases (for frontend compatibility):
- GET /event_node_builder/api/list - List all nodes
- POST /event_node_builder/api/save - Create a new node
- GET /event_node_builder/api/load/<configId> - Get node details
- POST /event_node_builder/api/update/<configId> - Update a node
- DELETE /event_node_builder/api/delete/<configId> - Delete a node
- POST /event_node_builder/api/copy/<nodeId> - Copy a node
"""

import logging

from flask import request

# Import shared utilities
from backend.core.utils import (
    execute_write,
    fetch_all_as_dict,
    fetch_one_as_dict,
    json_error_response,
    json_success_response,
)

# Import Repository pattern for data access
from backend.core.data_access import Repositories

# Import the parent blueprint
from .. import api_bp

logger = logging.getLogger(__name__)


@api_bp.route("/api/nodes", methods=["GET"])
def api_list_nodes():
    """API: List all canvas nodes"""
    try:
        game_gid = request.args.get("game_gid", type=int)

        where_clauses = ["1=1"]
        params = []

        if game_gid:
            where_clauses.append("game_gid = ?")
            params.append(game_gid)

        where_sql = " AND ".join(where_clauses)

        nodes = fetch_all_as_dict(
            f"""
            SELECT * FROM event_node_configs
            WHERE {where_sql}
            ORDER BY updated_at DESC
        """,
            params,
        )

        return json_success_response(data=nodes)

    except Exception as e:
        logger.error(f"Error fetching nodes: {e}")
        return json_error_response("Failed to fetch nodes", status_code=500)


@api_bp.route("/api/nodes", methods=["POST"])
def api_create_node():
    """API: Create a new canvas node"""
    try:
        data = request.get_json()

        # Validate required fields
        if "game_gid" not in data or "node_name" not in data:
            return json_error_response(
                "Missing required fields: game_gid, node_name", status_code=400
            )

        # Validate game_gid exists using Repository
        game = Repositories.GAMES.find_by_field("gid", data["game_gid"])
        if not game:
            return json_error_response(
                f'Game with gid {data["game_gid"]} not found', status_code=404
            )

        node_id = execute_write(
            """INSERT INTO event_node_configs (game_gid, node_name, node_type, config_data)
               VALUES (?, ?, ?, ?)""",
            (
                data["game_gid"],
                data["node_name"],
                data.get("node_type", "basic"),
                data.get("config_data", "{}"),
            ),
            return_last_id=True,
        )

        logger.info(f"Node created: {data['node_name']} (ID: {node_id})")
        return json_success_response(data={"node_id": node_id}, message="Node created successfully")

    except Exception as e:
        logger.error(f"Error creating node: {e}")
        return json_error_response("Failed to create node", status_code=500)


@api_bp.route("/api/nodes/<int:node_id>", methods=["GET"])
def api_get_node(node_id):
    """API: Get node details"""
    try:
        node = Repositories.EVENT_NODE_CONFIGS.find_by_id(node_id)

        if not node:
            return json_error_response("Node not found", status_code=404)

        return json_success_response(data=node)

    except Exception as e:
        logger.error(f"Error getting node {node_id}: {e}")
        return json_error_response("Failed to get node", status_code=500)


@api_bp.route("/api/nodes/<int:node_id>", methods=["PUT"])
def api_update_node(node_id):
    """API: Update a node"""
    node = Repositories.EVENT_NODE_CONFIGS.find_by_id(node_id)
    if not node:
        return json_error_response("Node not found", status_code=404)

    try:
        data = request.get_json()

        execute_write(
            "UPDATE event_node_configs SET node_name = ?, node_type = ?, config_data = ? WHERE id = ?",
            (
                data.get("node_name", node["node_name"]),
                data.get("node_type", node["node_type"]),
                data.get("config_data", node["config_data"]),
                node_id,
            ),
        )

        logger.info(f"Node updated: {node_id}")
        return json_success_response(message="Node updated successfully")

    except Exception as e:
        logger.error(f"Error updating node {node_id}: {e}")
        return json_error_response("Failed to update node", status_code=500)


@api_bp.route("/api/nodes/<int:node_id>", methods=["DELETE"])
def api_delete_node(node_id):
    """API: Delete a node"""
    node = Repositories.EVENT_NODE_CONFIGS.find_by_id(node_id)
    if not node:
        return json_error_response("Node not found", status_code=404)

    try:
        Repositories.EVENT_NODE_CONFIGS.delete(node_id)

        logger.info(f"Node deleted: {node_id}")
        return json_success_response(message="Node deleted successfully")

    except Exception as e:
        logger.error(f"Error deleting node {node_id}: {e}")
        return json_error_response("Failed to delete node", status_code=500)


# ============================================================================
# Event Node Builder API Aliases (for frontend compatibility)
# ============================================================================
#
# NOTE: The following routes have been REMOVED to avoid conflicts with event_node_builder_bp
#
# The real implementations are in backend/services/node/event_node_builder.py
# which is registered with url_prefix='/event_node_builder'
#
# Removed routes (now handled by event_node_builder_bp):
# - /event_node_builder/api/list (line 665 in event_node_builder.py)
# - /event_node_builder/api/save (line 400 in event_node_builder.py)
# - /event_node_builder/api/load/<int:configId> (line 767 in event_node_builder.py)
# - /event_node_builder/api/update/<int:configId> (line 564 in event_node_builder.py)
# - /event_node_builder/api/delete/<int:configId> (line 1021 in event_node_builder.py)
# - /event_node_builder/api/copy/<int:nodeId> (line 1165 in event_node_builder.py)
#
# Frontend should call routes directly on event_node_builder_bp:
# - GET /event_node_builder/api/list
# - POST /event_node_builder/api/save
# - GET /event_node_builder/api/load/<configId>
# - POST /event_node_builder/api/update/<configId>
# - DELETE /event_node_builder/api/delete/<configId>
# - POST /event_node_builder/api/copy/<nodeId>
# ============================================================================
