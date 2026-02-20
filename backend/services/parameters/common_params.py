#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Common Parameters Module
Handles common parameter CRUD operations
"""

from flask import Blueprint, request
from backend.core.logging import get_logger
from backend.core.utils import (
    fetch_all_as_dict,
    fetch_one_as_dict,
    execute_write,
    json_success_response,
    json_error_response,
)

logger = get_logger(__name__)

common_params_bp = Blueprint("common_params", __name__)


@common_params_bp.route("/api/common-params", methods=["GET"])
def list_common_params():
    """API: List common parameters for a specific game"""
    try:
        # Get game_gid from query parameters
        game_gid = request.args.get("game_gid", type=int)

        logger.info(f"[DEBUG] list_common_params called with game_gid={game_gid}")

        if not game_gid:
            return json_error_response("game_gid is required", status_code=400)

        # Validate game exists
        game = fetch_one_as_dict("SELECT gid FROM games WHERE gid = ?", (game_gid,))
        if not game:
            return json_error_response(f"Game {game_gid} not found", status_code=404)

        logger.info(f"[DEBUG] Using game_gid={game_gid}")

        # Fetch common params for this game only
        common_params = fetch_all_as_dict(
            """
            SELECT
                id,
                game_gid,
                param_name,
                param_name_cn,
                param_type,
                table_name,
                status,
                created_at,
                updated_at
            FROM common_params
            WHERE game_gid = ?
            ORDER BY created_at DESC
        """,
            (game_gid,),
        )

        # Map param_type to data_type for frontend compatibility
        for param in common_params:
            param["data_type"] = param.get("param_type", "string")
            param["key"] = param.get("param_name", "")
            param["name"] = param.get("param_name_cn", param.get("param_name", ""))
            param["description"] = param.get("param_description", "")

        return json_success_response(data=common_params)

    except Exception as e:
        logger.error(f"Error fetching common params: {e}")
        return json_error_response("Failed to fetch common params", status_code=500)


@common_params_bp.route("/api/common-params/sync", methods=["POST"])
def sync_common_params():
    """
    API: Sync common parameters for a game

    Analyzes all events for the specified game and identifies parameters
    that appear in 90% or more of events. These are automatically marked
    as common parameters.
    """
    data = request.get_json()

    if not data:
        return json_error_response("Request data is required", status_code=400)

    game_gid = data.get("game_gid") or data.get("game_id")

    if not game_gid:
        return json_error_response("game_gid is required", status_code=400)

    try:
        # Get all events for this game
        events = fetch_all_as_dict(
            "SELECT id, event_name FROM log_events WHERE game_gid = ?", (game_gid,)
        )

        if not events:
            return json_error_response("No events found for this game", status_code=404)

        total_events = len(events)
        threshold = 0.8  # 80% threshold (more practical)
        min_occurrences = int(total_events * threshold)

        logger.info(
            f"Analyzing {total_events} events for game_gid={game_gid}, threshold={min_occurrences}"
        )

        # Convert game_gid to database id for common_params table
        game_record = fetch_one_as_dict(
            "SELECT id FROM games WHERE gid = ?", (game_gid,)
        )
        if not game_record:
            return json_error_response(
                f"Game not found: gid={game_gid}", status_code=404
            )

        # Count parameter occurrences across all events
        param_counts = {}

        event_ids = [e["id"] for e in events]
        params_by_event = {}

        if event_ids:
            placeholders = ",".join(["?"] * len(event_ids))
            all_params = fetch_all_as_dict(
                f"""SELECT ep.event_id, ep.param_name, ep.param_name_cn
                    FROM event_params ep
                    WHERE ep.event_id IN ({placeholders}) AND ep.is_active = 1""",
                tuple(event_ids),
            )
            for param in all_params:
                eid = param["event_id"]
                if eid not in params_by_event:
                    params_by_event[eid] = []
                params_by_event[eid].append(param)

        for event in events:
            event_id = event["id"]
            params = params_by_event.get(event_id, []) if event_ids else []

            for param in params:
                param_key = param["param_name"]
                if param_key not in param_counts:
                    param_counts[param_key] = {
                        "count": 0,
                        "param_name_cn": param.get("param_name_cn", ""),
                    }
                param_counts[param_key]["count"] += 1

        # Identify common parameters (appear in >= 90% of events)
        common_params_to_add = []
        for param_name, data in param_counts.items():
            if data["count"] >= min_occurrences:
                # Check if already exists
                existing = fetch_one_as_dict(
                    "SELECT id FROM common_params WHERE game_gid = ? AND param_name = ?",
                    (game_gid, param_name),
                )

                if not existing:
                    common_params_to_add.append(
                        {
                            "param_name": param_name,
                            "param_name_cn": data["param_name_cn"],
                            "count": data["count"],
                        }
                    )

        # Insert new common parameters
        added_count = 0
        for param in common_params_to_add:
            try:
                # Determine data type (default to string for now)
                execute_write(
                    """
                    INSERT INTO common_params (
                        game_gid, param_name, param_name_cn, param_type,
                        table_name, status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, 'synced', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """,
                    (
                        game_gid,
                        param["param_name"],
                        param["param_name_cn"],
                        "string",
                        "common",
                    ),
                )
                added_count += 1
                logger.info(
                    f"Added common param: {param['param_name']} (appeared in {param['count']} events)"
                )
            except Exception as e:
                logger.error(f"Failed to add common param {param['param_name']}: {e}")

        return json_success_response(
            data={
                "total_events": total_events,
                "threshold": min_occurrences,
                "added": added_count,
                "analyzed": len(param_counts),
            },
            message=f"Synced {added_count} common parameters from {total_events} events",
        )

    except Exception as e:
        logger.error(f"Error syncing common params: {e}", exc_info=True)
        return json_error_response(
            f"Failed to sync common parameters: {str(e)}", status_code=500
        )


@common_params_bp.route("/api/common-params/<int:param_id>", methods=["DELETE"])
def delete_common_param(param_id):
    """API: Delete a common parameter"""
    # Check if param exists
    param = fetch_one_as_dict("SELECT * FROM common_params WHERE id = ?", (param_id,))

    if not param:
        return json_error_response("Common parameter not found", status_code=404)

    # Delete the param
    execute_write("DELETE FROM common_params WHERE id = ?", (param_id,))

    return json_success_response(message="Common parameter deleted")


@common_params_bp.route("/api/common-params/bulk-delete", methods=["DELETE", "POST"])
@common_params_bp.route(
    "/api/common-params/batch", methods=["DELETE"]
)  # Alias for frontend compatibility
def bulk_delete_common_params():
    """API: Bulk delete common parameters"""
    data = request.get_json() if request.data else {}

    ids = data.get("ids", [])

    if not ids:
        return json_error_response("ids list is required", status_code=400)

    if not isinstance(ids, list):
        return json_error_response("ids must be a list", status_code=400)

    # Delete params
    placeholders = ",".join(["?" for _ in ids])
    deleted_count = execute_write(
        f"DELETE FROM common_params WHERE id IN ({placeholders})", tuple(ids)
    )

    return json_success_response(
        data={"deleted": deleted_count},
        message=f"Deleted {deleted_count} common parameters",
    )
