#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HQL Version API Routes Module

This module contains all HQL version-related API endpoints for managing,
comparing, and rolling back HQL versions.

Core endpoints:
- POST /api/hql-versions/save - Save a new HQL version
- POST /api/hql-versions/compare - Compare two versions
- GET /api/hql-versions/history/<int:event_id> - Get version history
- POST /api/hql-versions/rollback - Rollback to a specific version

Architecture:
- Uses HQLVersionService for business logic
- Uses HQLVersionRepository for data access
- No direct database access (100% ERS architecture)
"""

import logging

from flask import request

from backend.api import api_bp
from backend.core.utils import json_error_response, json_success_response, validate_json_request
from backend.services.hql_version_service import HQLVersionService

logger = logging.getLogger(__name__)

# Initialize HQL version service
hql_version_service = HQLVersionService()


@api_bp.route("/api/hql-versions/save", methods=["POST"])
def api_save_hql_version():
    """
    API: Save a new HQL version

    Request body:
    {
        "event_id": 123,
        "hql_content": "CREATE OR REPLACE VIEW ...",
        "change_description": "Updated WHERE clause",
        "created_by": "user@example.com"
    }

    Response:
    {
        "success": true,
        "data": {
            "id": 456,
            "event_id": 123,
            "hql_content": "CREATE OR REPLACE VIEW ...",
            "version_number": 2,
            "change_description": "Updated WHERE clause",
            "created_by": "user@example.com",
            "created_at": "2026-03-20 10:30:00"
        },
        "message": "HQL version saved successfully"
    }
    """
    is_valid, data, error = validate_json_request(
        ["event_id", "hql_content", "change_description", "created_by"]
    )
    if not is_valid:
        return json_error_response(error)

    event_id = data["event_id"]
    hql_content = data["hql_content"]
    change_description = data["change_description"]
    created_by = data["created_by"]

    try:
        version = hql_version_service.save_version(
            event_id=event_id,
            hql_content=hql_content,
            change_description=change_description,
            created_by=created_by,
        )

        if version:
            return json_success_response(
                data=version, message=f"HQL version {version['version_number']} saved successfully"
            )
        return json_error_response("Failed to save HQL version", status_code=500)
    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error saving HQL version: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@api_bp.route("/api/hql-versions/compare", methods=["POST"])
def api_compare_hql_versions():
    """
    API: Compare two HQL versions

    Request body:
    {
        "version_id_1": 123,
        "version_id_2": 124
    }

    Response:
    {
        "success": true,
        "data": {
            "version_1": {
                "id": 123,
                "version_number": 1,
                "created_at": "2026-03-20 10:00:00",
                "created_by": "user@example.com"
            },
            "version_2": {
                "id": 124,
                "version_number": 2,
                "created_at": "2026-03-20 10:30:00",
                "created_by": "user@example.com"
            },
            "diff": "- SELECT *\n+ SELECT id, name\n",
            "additions": 1,
            "deletions": 1,
            "changes": 0
        },
        "message": "Versions compared successfully"
    }
    """
    is_valid, data, error = validate_json_request(["version_id_1", "version_id_2"])
    if not is_valid:
        return json_error_response(error)

    version_id_1 = data["version_id_1"]
    version_id_2 = data["version_id_2"]

    try:
        diff_result = hql_version_service.compare_versions(version_id_1, version_id_2)

        if "error" in diff_result:
            return json_error_response(diff_result["error"], status_code=404)

        return json_success_response(
            data=diff_result, message="Versions compared successfully"
        )
    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error comparing HQL versions: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@api_bp.route("/api/hql-versions/history/<int:event_id>", methods=["GET"])
def api_get_hql_version_history(event_id):
    """
    API: Get HQL version history for an event

    URL parameters:
    - event_id: Event ID

    Query parameters:
    - limit: Optional limit on number of versions to return

    Response:
    {
        "success": true,
        "data": [
            {
                "id": 124,
                "event_id": 123,
                "hql_content": "CREATE OR REPLACE VIEW ...",
                "version_number": 2,
                "change_description": "Updated WHERE clause",
                "created_by": "user@example.com",
                "created_at": "2026-03-20 10:30:00"
            },
            {
                "id": 123,
                "event_id": 123,
                "hql_content": "CREATE OR REPLACE VIEW ...",
                "version_number": 1,
                "change_description": "Initial version",
                "created_by": "user@example.com",
                "created_at": "2026-03-20 10:00:00"
            }
        ],
        "message": "Retrieved 2 versions"
    }
    """
    try:
        limit = request.args.get("limit", type=int)

        versions = hql_version_service.get_version_history(event_id, limit=limit)

        return json_success_response(
            data=versions, message=f"Retrieved {len(versions)} version(s)"
        )
    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error getting HQL version history: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@api_bp.route("/api/hql-versions/rollback", methods=["POST"])
def api_rollback_hql_version():
    """
    API: Rollback to a specific HQL version

    Request body:
    {
        "event_id": 123,
        "target_version_id": 123,
        "rolled_back_by": "user@example.com"
    }

    Response:
    {
        "success": true,
        "data": {
            "id": 125,
            "event_id": 123,
            "hql_content": "CREATE OR REPLACE VIEW ...",
            "version_number": 3,
            "change_description": "Rollback to version 1",
            "created_by": "user@example.com",
            "created_at": "2026-03-20 11:00:00"
        },
        "message": "Rolled back to version 1, created new version 3"
    }
    """
    is_valid, data, error = validate_json_request(
        ["event_id", "target_version_id", "rolled_back_by"]
    )
    if not is_valid:
        return json_error_response(error)

    event_id = data["event_id"]
    target_version_id = data["target_version_id"]
    rolled_back_by = data["rolled_back_by"]

    try:
        new_version = hql_version_service.rollback_to_version(
            event_id=event_id,
            target_version_id=target_version_id,
            rolled_back_by=rolled_back_by,
        )

        if new_version:
            return json_success_response(
                data=new_version,
                message=f"Rolled back to version {data.get('version_number', 'unknown')}, "
                f"created new version {new_version['version_number']}",
            )
        return json_error_response("Failed to rollback HQL version", status_code=500)
    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error rolling back HQL version: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@api_bp.route("/api/hql-versions/latest/<int:event_id>", methods=["GET"])
def api_get_latest_hql_version(event_id):
    """
    API: Get the latest HQL version for an event

    URL parameters:
    - event_id: Event ID

    Response:
    {
        "success": true,
        "data": {
            "id": 124,
            "event_id": 123,
            "hql_content": "CREATE OR REPLACE VIEW ...",
            "version_number": 2,
            "change_description": "Updated WHERE clause",
            "created_by": "user@example.com",
            "created_at": "2026-03-20 10:30:00"
        },
        "message": "Retrieved latest version"
    }
    """
    try:
        version = hql_version_service.get_latest_version(event_id)

        if version:
            return json_success_response(data=version, message="Retrieved latest version")
        return json_error_response("No versions found for this event", status_code=404)
    except Exception as e:
        logger.error(f"Error getting latest HQL version: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@api_bp.route("/api/hql-versions/<int:version_id>", methods=["GET"])
def api_get_hql_version(version_id):
    """
    API: Get a specific HQL version by ID

    URL parameters:
    - version_id: Version ID

    Response:
    {
        "success": true,
        "data": {
            "id": 123,
            "event_id": 123,
            "hql_content": "CREATE OR REPLACE VIEW ...",
            "version_number": 1,
            "change_description": "Initial version",
            "created_by": "user@example.com",
            "created_at": "2026-03-20 10:00:00"
        },
        "message": "Retrieved version successfully"
    }
    """
    try:
        from backend.models.repositories.hql_version_repository import HQLVersionRepository

        repo = HQLVersionRepository()
        version = repo.find_by_id(version_id)

        if version:
            return json_success_response(data=version, message="Retrieved version successfully")
        return json_error_response("Version not found", status_code=404)
    except Exception as e:
        logger.error(f"Error getting HQL version {version_id}: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)
