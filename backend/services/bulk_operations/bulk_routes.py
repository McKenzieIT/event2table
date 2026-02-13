"""
Bulk Operations Routes

Provides endpoints for bulk operations on events, games, and parameters.
All endpoints use the GenericRepository pattern for batch operations.
"""

import logging
import json
from typing import Any, Dict, List

from flask import request
from backend.core.utils import (
    execute_write,
    fetch_all_as_dict,
    fetch_one_as_dict,
    json_error_response,
    json_success_response,
    validate_json_request,
)
from backend.core.data_access import Repositories

# Import the blueprint
from . import bulk_bp

logger = logging.getLogger(__name__)


@bulk_bp.route("/bulk-delete-events", methods=["POST"])
def api_bulk_delete_events():
    """
    API: Bulk delete events

    Request Body:
        {
            "event_ids": [1, 2, 3, ...]  # List of event IDs to delete
        }

    Returns:
        Success response with count of deleted events

    Example:
        POST /bulk-delete-events
        {
            "event_ids": [1, 2, 3]
        }
    """
    try:
        # Validate request
        is_valid, data, error = validate_json_request(["event_ids"])
        if not is_valid:
            return json_error_response(error, status_code=400)

        event_ids = data.get("event_ids", [])

        if not event_ids or not isinstance(event_ids, list):
            return json_error_response("event_ids must be a non-empty list", status_code=400)

        # Delete event parameters first (foreign key constraint)
        placeholders = ",".join(["?" for _ in event_ids])
        execute_write(
            f"DELETE FROM event_params WHERE event_id IN ({placeholders})",
            tuple(event_ids)
        )

        # Delete events
        deleted_count = Repositories.LOG_EVENTS.delete_batch(event_ids)

        # Clear cache
        try:
            from backend.core.cache.cache_system import clear_cache_pattern
            clear_cache_pattern("events:*")
            clear_cache_pattern("dashboard_statistics")
        except ImportError:
            pass

        logger.info(f"Bulk deleted {deleted_count} events: {event_ids}")
        return json_success_response(
            message=f"Deleted {deleted_count} events successfully",
            data={"deleted_count": deleted_count, "event_ids": event_ids}
        )

    except Exception as e:
        logger.error(f"Error in bulk delete events: {e}")
        return json_error_response(f"Failed to delete events: {str(e)}", status_code=500)


@bulk_bp.route("/bulk-update-category", methods=["POST"])
def api_bulk_update_category():
    """
    API: Bulk update category for multiple events

    Request Body:
        {
            "event_ids": [1, 2, 3, ...],  # List of event IDs
            "category_id": 5               # New category ID
        }

    Returns:
        Success response with count of updated events

    Example:
        POST /bulk-update-category
        {
            "event_ids": [1, 2, 3],
            "category_id": 5
        }
    """
    try:
        # Validate request
        is_valid, data, error = validate_json_request(["event_ids", "category_id"])
        if not is_valid:
            return json_error_response(error, status_code=400)

        event_ids = data.get("event_ids", [])
        category_id = data.get("category_id")

        if not event_ids or not isinstance(event_ids, list):
            return json_error_response("event_ids must be a non-empty list", status_code=400)

        if not isinstance(category_id, int) or category_id <= 0:
            return json_error_response("category_id must be a positive integer", status_code=400)

        # Verify category exists
        category = fetch_one_as_dict(
            "SELECT id FROM event_categories WHERE id = ?",
            (category_id,)
        )
        if not category:
            return json_error_response(f"Category with id {category_id} not found", status_code=404)

        # Update events using Repository batch update
        updates = {"category_id": category_id}
        updated_count = Repositories.LOG_EVENTS.update_batch(event_ids, updates)

        # Clear cache
        try:
            from backend.core.cache.cache_system import clear_cache_pattern
            clear_cache_pattern("events:*")
        except ImportError:
            pass

        logger.info(f"Bulk updated category for {updated_count} events to category {category_id}")
        return json_success_response(
            message=f"Updated {updated_count} events to category {category_id}",
            data={"updated_count": updated_count, "category_id": category_id, "event_ids": event_ids}
        )

    except Exception as e:
        logger.error(f"Error in bulk update category: {e}")
        return json_error_response(f"Failed to update category: {str(e)}", status_code=500)


@bulk_bp.route("/bulk-toggle-common-params", methods=["POST"])
def api_bulk_toggle_common_params():
    """
    API: Bulk toggle common params inclusion for events

    Request Body:
        {
            "event_ids": [1, 2, 3, ...],  # List of event IDs
            "include": 1                   # 1 to include, 0 to exclude
        }

    Returns:
        Success response with count of updated events

    Example:
        POST /bulk-toggle-common-params
        {
            "event_ids": [1, 2, 3],
            "include": 1
        }
    """
    try:
        # Validate request
        is_valid, data, error = validate_json_request(["event_ids", "include"])
        if not is_valid:
            return json_error_response(error, status_code=400)

        event_ids = data.get("event_ids", [])
        include = data.get("include")

        if not event_ids or not isinstance(event_ids, list):
            return json_error_response("event_ids must be a non-empty list", status_code=400)

        if include not in [0, 1]:
            return json_error_response("include must be 0 or 1", status_code=400)

        # Update events using Repository batch update
        updates = {"include_in_common_params": include}
        updated_count = Repositories.LOG_EVENTS.update_batch(event_ids, updates)

        # Clear cache
        try:
            from backend.core.cache.cache_system import clear_cache_pattern
            clear_cache_pattern("events:*")
            clear_cache_pattern("common_params:*")
        except ImportError:
            pass

        action = "included in" if include == 1 else "excluded from"
        logger.info(f"Bulk toggled common params: {updated_count} events {action} common params")
        return json_success_response(
            message=f"Updated {updated_count} events - {action} common params",
            data={"updated_count": updated_count, "include": include, "event_ids": event_ids}
        )

    except Exception as e:
        logger.error(f"Error in bulk toggle common params: {e}")
        return json_error_response(f"Failed to toggle common params: {str(e)}", status_code=500)


@bulk_bp.route("/bulk-export-events", methods=["POST"])
def api_bulk_export_events():
    """
    API: Bulk export events configuration

    Request Body:
        {
            "event_ids": [1, 2, 3, ...],  # List of event IDs to export
            "format": "json"               # Export format (currently only "json" supported)
        }

    Returns:
        Events configuration in specified format

    Example:
        POST /bulk-export-events
        {
            "event_ids": [1, 2, 3],
            "format": "json"
        }
    """
    try:
        # Validate request
        is_valid, data, error = validate_json_request(["event_ids"])
        if not is_valid:
            return json_error_response(error, status_code=400)

        event_ids = data.get("event_ids", [])
        format_type = data.get("format", "json")

        if not event_ids or not isinstance(event_ids, list):
            return json_error_response("event_ids must be a non-empty list", status_code=400)

        if format_type not in ["json"]:
            return json_error_response("format must be 'json'", status_code=400)

        # Fetch events with their parameters
        placeholders = ",".join(["?" for _ in event_ids])
        events = fetch_all_as_dict(
            f"""
            SELECT
                le.id,
                le.game_gid,
                le.event_name,
                le.event_name_cn,
                le.category_id,
                ec.name as category_name,
                le.source_table,
                le.target_table,
                le.include_in_common_params
            FROM log_events le
            LEFT JOIN event_categories ec ON le.category_id = ec.id
            WHERE le.id IN ({placeholders})
            ORDER BY le.id
            """,
            tuple(event_ids)
        )

        if not events:
            return json_error_response("No events found with the provided IDs", status_code=404)

        # Fetch parameters for each event
        for event in events:
            event_params = fetch_all_as_dict(
                """
                SELECT
                    ep.param_name,
                    ep.param_name_cn,
                    ep.template_id,
                    pt.template_name as param_type,
                    ep.param_description as description,
                    ep.is_active
                FROM event_params ep
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                WHERE ep.event_id = ? AND ep.is_active = 1
                ORDER BY ep.id
                """,
                (event["id"],)
            )
            event["parameters"] = event_params

        logger.info(f"Bulk exported {len(events)} events")
        return json_success_response(
            message=f"Exported {len(events)} events successfully",
            data={
                "events": events,
                "count": len(events),
                "format": format_type
            }
        )

    except Exception as e:
        logger.error(f"Error in bulk export events: {e}")
        return json_error_response(f"Failed to export events: {str(e)}", status_code=500)


@bulk_bp.route("/bulk-validate-parameters", methods=["POST"])
def api_bulk_validate_parameters():
    """
    API: Bulk validate parameters for multiple events

    Request Body:
        {
            "event_ids": [1, 2, 3, ...]  # List of event IDs to validate
        }

    Returns:
        Validation results for each event

    Example:
        POST /bulk-validate-parameters
        {
            "event_ids": [1, 2, 3]
        }

    Response:
        {
            "success": true,
            "data": {
                "results": [
                    {
                        "event_id": 1,
                        "event_name": "game.login",
                        "is_valid": true,
                        "warnings": [],
                        "errors": []
                    },
                    ...
                ]
            }
        }
    """
    try:
        # Validate request
        is_valid, data, error = validate_json_request(["event_ids"])
        if not is_valid:
            return json_error_response(error, status_code=400)

        event_ids = data.get("event_ids", [])

        if not event_ids or not isinstance(event_ids, list):
            return json_error_response("event_ids must be a non-empty list", status_code=400)

        results = []

        # Validate each event
        for event_id in event_ids:
            # Fetch event
            event = Repositories.LOG_EVENTS.find_by_id(event_id)

            if not event:
                results.append({
                    "event_id": event_id,
                    "is_valid": False,
                    "errors": ["Event not found"]
                })
                continue

            # Fetch event parameters
            params = fetch_all_as_dict(
                """
                SELECT
                    ep.param_name,
                    ep.param_name_cn,
                    ep.template_id,
                    ep.param_description,
                    pt.base_type,
                    pt.template_name
                FROM event_params ep
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                WHERE ep.event_id = ? AND ep.is_active = 1
                """,
                (event_id,)
            )

            # Perform validation checks
            errors = []
            warnings = []

            # Check 1: Event must have a name
            if not event.get("event_name"):
                errors.append("Event name is missing")

            # Check 2: Event must have a valid category
            if not event.get("category_id"):
                errors.append("Category is not assigned")

            # Check 3: Check for duplicate parameter names
            param_names = [p["param_name"] for p in params]
            duplicates = [name for name in set(param_names) if param_names.count(name) > 1]
            if duplicates:
                errors.append(f"Duplicate parameter names: {', '.join(duplicates)}")

            # Check 4: Parameters without Chinese names
            missing_cn = [p["param_name"] for p in params if not p.get("param_name_cn")]
            if missing_cn:
                warnings.append(f"Parameters missing Chinese names: {', '.join(missing_cn)}")

            # Check 5: Parameters without descriptions
            missing_desc = [p["param_name"] for p in params if not p.get("param_description")]
            if missing_desc:
                warnings.append(f"Parameters missing descriptions: {', '.join(missing_desc)}")

            # Check 6: Event has no parameters
            if not params:
                warnings.append("Event has no parameters defined")

            # Overall validation status
            is_valid = len(errors) == 0

            results.append({
                "event_id": event_id,
                "event_name": event.get("event_name", ""),
                "event_name_cn": event.get("event_name_cn", ""),
                "is_valid": is_valid,
                "param_count": len(params),
                "errors": errors,
                "warnings": warnings
            })

        logger.info(f"Bulk validated parameters for {len(event_ids)} events")
        return json_success_response(
            message=f"Validated {len(event_ids)} events",
            data={
                "results": results,
                "total_events": len(event_ids),
                "valid_events": sum(1 for r in results if r["is_valid"]),
                "invalid_events": sum(1 for r in results if not r["is_valid"])
            }
        )

    except Exception as e:
        logger.error(f"Error in bulk validate parameters: {e}")
        return json_error_response(f"Failed to validate parameters: {str(e)}", status_code=500)
