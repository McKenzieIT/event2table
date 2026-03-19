#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Async Tasks API Routes

Provides REST API endpoints for managing asynchronous tasks.
"""

import logging

from flask import request

from backend.core.logging import get_logger
from backend.core.utils import json_error_response, json_success_response
from backend.services.async_tasks.async_task_service import AsyncTaskService

from .async_task_bp import async_task_bp

logger = get_logger(__name__)


@async_task_bp.route("/api/async-tasks", methods=["GET"])
def list_async_tasks():
    """
    API: List all async tasks

    Query Parameters:
        task_type (str, optional): Filter by task type
        status (str, optional): Filter by status ('pending', 'running', 'completed', 'failed')
        created_by (str, optional): Filter by creator
        limit (int, optional): Limit number of results (default: 100)

    Returns:
        List of tasks matching the filters
    """
    try:
        service = AsyncTaskService()

        # Build filters from query parameters
        filters = {}
        if request.args.get("task_type"):
            filters["task_type"] = request.args.get("task_type")
        if request.args.get("status"):
            filters["status"] = request.args.get("status")
        if request.args.get("created_by"):
            filters["created_by"] = request.args.get("created_by")

        # Get limit parameter
        limit = request.args.get("limit", type=int, default=100)

        # Validate limit
        if limit < 1 or limit > 1000:
            return json_error_response("limit must be between 1 and 1000", status_code=400)

        # Get tasks
        tasks = service.list_tasks(filters=filters, limit=limit)

        return json_success_response(data=tasks)

    except Exception as e:
        logger.error(f"Error listing async tasks: {e}")
        return json_error_response("Failed to list tasks", status_code=500)


@async_task_bp.route("/api/async-tasks/<task_id>", methods=["GET"])
def get_async_task(task_id):
    """
    API: Get a single async task by ID

    Args:
        task_id: Task UUID

    Returns:
        Task details or 404 if not found
    """
    try:
        service = AsyncTaskService()
        task = service.get_task(task_id)

        if not task:
            return json_error_response("Task not found", status_code=404)

        return json_success_response(data=task)

    except ValueError as e:
        logger.error(f"Validation error fetching task {task_id}: {e}")
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error fetching task {task_id}: {e}")
        return json_error_response("Failed to fetch task", status_code=500)


@async_task_bp.route("/api/async-tasks", methods=["POST"])
def create_async_task():
    """
    API: Create a new async task

    Request body:
    {
        "task_type": "string (required)",
        "payload": { ... } (optional),
        "created_by": "string (optional)"
    }

    Returns:
        Created task with task_id
    """
    try:
        data = request.get_json()

        if not data:
            return json_error_response("Request body is required", status_code=400)

        # Validate required fields
        task_type = data.get("task_type")
        if not task_type:
            return json_error_response("task_type is required", status_code=400)

        # Optional fields
        payload = data.get("payload")
        created_by = data.get("created_by")

        # Create task
        service = AsyncTaskService()
        task_id = service.create_task(
            task_type=task_type,
            payload=payload,
            created_by=created_by,
        )

        # Return created task
        task = service.get_task(task_id)

        logger.info(f"Async task created: task_id={task_id}, type={task_type}")
        return json_success_response(
            message="Task created successfully",
            data=task,
        )

    except ValueError as e:
        logger.error(f"Validation error creating task: {e}")
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return json_error_response("Failed to create task", status_code=500)


@async_task_bp.route("/api/async-tasks/<task_id>", methods=["PUT", "PATCH"])
def update_async_task(task_id):
    """
    API: Update an async task status

    Request body:
    {
        "status": "string (required): 'pending', 'running', 'completed', 'failed'",
        "progress": "number (optional, 0-100)",
        "result": { ... } (optional),
        "error": "string (optional)"
    }

    Returns:
        Updated task details
    """
    try:
        data = request.get_json()

        if not data:
            return json_error_response("Request body is required", status_code=400)

        # Validate required fields
        status = data.get("status")
        if not status:
            return json_error_response("status is required", status_code=400)

        # Validate status value
        valid_statuses = ["pending", "running", "completed", "failed"]
        if status not in valid_statuses:
            return json_error_response(
                f"status must be one of: {', '.join(valid_statuses)}",
                status_code=400,
            )

        # Optional fields
        progress = data.get("progress")
        result = data.get("result")
        error = data.get("error")

        # Update task
        service = AsyncTaskService()
        service.update_task_status(
            task_id=task_id,
            status=status,
            progress=progress,
            result=result,
            error=error,
        )

        # Return updated task
        task = service.get_task(task_id)

        logger.info(f"Async task updated: task_id={task_id}, status={status}")
        return json_success_response(
            message="Task updated successfully",
            data=task,
        )

    except ValueError as e:
        logger.error(f"Validation error updating task {task_id}: {e}")
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        return json_error_response("Failed to update task", status_code=500)


@async_task_bp.route("/api/async-tasks/<task_id>", methods=["DELETE"])
def delete_async_task(task_id):
    """
    API: Delete an async task

    Args:
        task_id: Task UUID

    Returns:
        Success message or 404 if not found
    """
    try:
        service = AsyncTaskService()
        task = service.get_task(task_id)

        if not task:
            return json_error_response("Task not found", status_code=404)

        # Delete task using repository
        service.task_repo.delete(task["id"])

        # Invalidate cache
        service.invalidate_pattern("async_tasks:*")

        logger.info(f"Async task deleted: task_id={task_id}")
        return json_success_response(message="Task deleted successfully")

    except ValueError as e:
        logger.error(f"Validation error deleting task {task_id}: {e}")
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        return json_error_response("Failed to delete task", status_code=500)


@async_task_bp.route("/api/async-tasks/cleanup", methods=["POST"])
def cleanup_old_async_tasks():
    """
    API: Clean up old completed/failed tasks

    Request body:
    {
        "days": "number (optional, default: 30)"
    }

    Returns:
        Number of tasks deleted
    """
    try:
        data = request.get_json() or {}
        days = data.get("days", 30)

        # Validate days
        if not isinstance(days, int) or days < 1:
            return json_error_response("days must be a positive integer", status_code=400)

        # Cleanup old tasks
        service = AsyncTaskService()
        deleted_count = service.cleanup_old_tasks(days=days)

        logger.info(f"Old async tasks cleaned up: {deleted_count} tasks deleted")
        return json_success_response(
            message=f"Cleaned up {deleted_count} old tasks",
            data={"deleted_count": deleted_count},
        )

    except Exception as e:
        logger.error(f"Error cleaning up old tasks: {e}")
        return json_error_response("Failed to clean up old tasks", status_code=500)


@async_task_bp.route("/api/async-tasks/statistics", methods=["GET"])
def get_async_task_statistics():
    """
    API: Get async task statistics

    Returns:
        Statistics including total tasks, tasks by status, and tasks by type
    """
    try:
        service = AsyncTaskService()
        stats = service.get_task_statistics()

        return json_success_response(data=stats)

    except Exception as e:
        logger.error(f"Error fetching task statistics: {e}")
        return json_error_response("Failed to fetch task statistics", status_code=500)
