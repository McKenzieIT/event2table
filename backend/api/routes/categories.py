"""
Categories API Routes Module

This module contains all category-related API endpoints for managing
event categories.

Core endpoints:
- GET /api/categories - List all categories with event counts
- POST /api/categories - Create a new category
- GET /api/categories/<int:id> - Get category details
- PUT/PATCH /api/categories/<int:id> - Update a category
- DELETE /api/categories/<int:id> - Delete a category
- POST /api/categories/batch-delete - Batch delete categories

Architecture (V9.0.0):
- Uses CategoryService for business logic
- Uses GameService for game validation
- Uses EventCategoryEntity for data validation
- Automatic cache invalidation via service layer
- No direct database access (100% ERS architecture)
"""

import logging

from flask import request

# Import shared utilities
from backend.core.utils import (
    json_error_response,
    json_success_response,
    sanitize_and_validate_string,
    validate_json_request,
)

# Import Service layer
from backend.services.event_categories.category_service import CategoryService
from backend.services.games.game_service import GameService

# Import Entity for validation
from backend.models.entities import EventCategoryEntity

# Import the parent blueprint
from .. import api_bp

logger = logging.getLogger(__name__)


@api_bp.route("/api/categories", methods=["GET"])
def api_list_categories():
    """
    API: List categories filtered by game_gid

    Query Parameters:
        game_gid (int, required): Game GID to filter categories by

    Returns:
        List of categories with event counts for the specified game

    Error:
        400: If game_gid parameter is missing or invalid
        404: If game_gid does not exist
    """
    try:
        service = CategoryService()

        # Get and validate game_gid parameter (REQUIRED)
        game_gid = request.args.get("game_gid", type=int)

        # MANDATORY: game_gid must be provided
        if not game_gid:
            return json_error_response("game_gid is required", status_code=400)

        # Verify game exists using GameService
        game_service = GameService()
        game = game_service.get_game_by_gid(game_gid)
        if not game:
            return json_error_response(f"Game {game_gid} not found", status_code=404)

        # Use service to get categories with event counts
        categories = service.get_all_categories(game_gid=game_gid)

        # Convert Entity objects to dictionaries for JSON response
        return json_success_response(
            data=[category.model_dump() for category in categories]
        )
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        return json_error_response("Failed to fetch categories", status_code=500)


@api_bp.route("/api/categories/<int:id>", methods=["GET"])
def api_get_category(id):
    """API: Get a single category by ID"""
    try:
        service = CategoryService()
        category = service.get_category_by_id(id)

        if not category:
            return json_error_response("Category not found", status_code=404)

        return json_success_response(data=category.model_dump())
    except ValueError as e:
        logger.error(f"Validation error fetching category {id}: {e}")
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error fetching category {id}: {e}")
        return json_error_response("Failed to fetch category", status_code=500)


@api_bp.route("/api/categories", methods=["POST"])
def api_create_category():
    """API: Create a new category"""
    is_valid, data, error = validate_json_request(["name"])
    if not is_valid:
        return json_error_response(error, status_code=400)

    # 验证和清理分类名称
    is_valid, result = sanitize_and_validate_string(
        data.get("name"), max_length=200, field_name="name", allow_empty=False
    )
    if not is_valid:
        return json_error_response(result, status_code=400)
    name = result

    try:
        service = CategoryService()

        # Create Entity object (will be validated by Pydantic)
        category_data = EventCategoryEntity(name=name)

        # Use service to create category
        created_category = service.create_category(category_data)

        logger.info(f"Category created: {name}")
        return json_success_response(
            message="Category created successfully",
            data=created_category.model_dump()
        )
    except ValueError as e:
        # Handle duplicate name error
        if "already exists" in str(e):
            return json_error_response(str(e), status_code=409)
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error creating category: {e}")
        return json_error_response("Failed to create category", status_code=500)


@api_bp.route("/api/categories/<int:id>", methods=["PUT", "PATCH"])
def api_update_category(id):
    """API: Update an existing category"""
    is_valid, data, error = validate_json_request(["name"])
    if not is_valid:
        return json_error_response(error, status_code=400)

    # 验证和清理分类名称
    is_valid, result = sanitize_and_validate_string(
        data.get("name"), max_length=200, field_name="name", allow_empty=False
    )
    if not is_valid:
        return json_error_response(result, status_code=400)
    name = result

    try:
        service = CategoryService()

        # Use service to update category
        updated_category = service.update_category(id, {"name": name})

        logger.info(f"Category updated: {name} (ID: {id})")
        return json_success_response(
            message="Category updated successfully",
            data=updated_category.model_dump()
        )
    except ValueError as e:
        # Handle not found or duplicate name errors
        error_msg = str(e)
        if "not found" in error_msg:
            return json_error_response(error_msg, status_code=404)
        if "already exists" in error_msg:
            return json_error_response(error_msg, status_code=409)
        return json_error_response(error_msg, status_code=400)
    except Exception as e:
        logger.error(f"Error updating category {id}: {e}")
        return json_error_response("Failed to update category", status_code=500)


@api_bp.route("/api/categories/<int:id>", methods=["DELETE"])
def api_delete_category(id):
    """API: Delete a category"""
    try:
        service = CategoryService()

        # Get category for logging before deletion
        category = service.get_category_by_id(id)
        if not category:
            return json_error_response("Category not found", status_code=404)

        # Use service to delete category
        service.delete_category(id)

        logger.info(f"Category deleted: {category.name} (ID: {id})")
        return json_success_response(message="Category deleted successfully")
    except ValueError as e:
        # Handle not found error
        if "not found" in str(e):
            return json_error_response(str(e), status_code=404)
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error deleting category {id}: {e}")
        return json_error_response("Failed to delete category", status_code=500)


@api_bp.route("/api/categories/batch-delete", methods=["POST"])
def api_batch_delete_categories():
    """
    API: Batch delete categories

    Request body:
    {
        "category_ids": [1, 2, 3, 4, 5]
    }

    Returns:
    {
        "success": true,
        "data": {
            "deleted_count": 4,
            "failed_ids": [3],
            "failed_reasons": {3: "Category has 5 associated events"},
            "message": "Successfully deleted 4 out of 5 categories (1 failed)"
        }
    }
    """
    is_valid, data, error = validate_json_request(["category_ids"])
    if not is_valid:
        return json_error_response(error, status_code=400)

    if not data["category_ids"] or not isinstance(data["category_ids"], list):
        return json_error_response("Invalid category IDs", status_code=400)

    try:
        category_ids = data["category_ids"]

        # 验证数量限制
        if len(category_ids) > 100:
            return json_error_response(
                f"Too many IDs: {len(category_ids)} > 100", status_code=400
            )

        # 验证所有ID都是正整数
        if not all(isinstance(cid, int) and cid > 0 for cid in category_ids):
            return json_error_response(
                "All category IDs must be positive integers", status_code=400
            )

        service = CategoryService()

        # Use service to batch delete categories
        result = service.batch_delete_categories(category_ids)

        logger.info(
            f"Batch delete categories: {result['deleted_count']} deleted, "
            f"{len(result['failed_ids'])} failed"
        )

        return json_success_response(
            message=result["message"],
            data={
                "deleted_count": result["deleted_count"],
                "failed_ids": result["failed_ids"],
                "failed_reasons": result["failed_reasons"]
            },
        )
    except ValueError as e:
        # Handle validation errors
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error batch deleting categories: {e}")
        return json_error_response("Failed to delete categories", status_code=500)


@api_bp.route("/api/categories/batch-update", methods=["PUT"])
def api_batch_update_categories():
    """API: Batch update categories

    Example request body:
    {
        "ids": [1, 2, 3],
        "updates": {"name": "Updated Name"}
    }
    """
    is_valid, data, error = validate_json_request(["ids", "updates"])
    if not is_valid:
        return json_error_response(error, status_code=400)

    category_ids = data.get("ids", [])
    updates = data.get("updates", {})

    if not category_ids or not updates:
        return json_error_response("Invalid request data", status_code=400)

    try:
        # Validate and sanitize update fields
        if "name" in updates:
            is_valid, result = sanitize_and_validate_string(
                updates["name"], max_length=200, field_name="name", allow_empty=False
            )
            if not is_valid:
                return json_error_response(result, status_code=400)
            updates["name"] = result

        service = CategoryService()

        # Use service to batch update categories
        updated_count = service.batch_update_categories(category_ids, updates)

        logger.info(f"Batch updated {updated_count} categories")
        return json_success_response(
            message=f"Updated {updated_count} categories",
            data={"updated_count": updated_count},
        )
    except ValueError as e:
        # Handle validation errors
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error batch updating categories: {e}")
        return json_error_response("Failed to update categories", status_code=500)


@api_bp.route("/api/categories/stats", methods=["GET"])
def api_get_category_stats():
    """
    API: Get category statistics

    Query Parameters:
        game_gid (int, optional): Game GID to filter statistics by

    Returns:
        Statistics including:
        - total_categories: Total number of categories
        - active_categories: Number of active categories
        - categories_with_events: Number of categories with associated events
        - category_breakdown: Detailed breakdown of each category with event counts

    Example:
        # Get global statistics
        GET /api/categories/stats

        # Get game-specific statistics
        GET /api/categories/stats?game_gid=10000147
    """
    try:
        service = CategoryService()

        # Get optional game_gid parameter
        game_gid = request.args.get("game_gid", type=int)

        # If game_gid is provided, verify game exists using GameService
        if game_gid is not None:
            game_service = GameService()
            game = game_service.get_game_by_gid(game_gid)
            if not game:
                return json_error_response(f"Game {game_gid} not found", status_code=404)

        # Get statistics from service (with caching)
        stats = service.get_statistics(game_gid)

        logger.info(f"Category statistics retrieved (game_gid={game_gid})")
        return json_success_response(data=stats)

    except ValueError as e:
        logger.error(f"Validation error fetching category statistics: {e}")
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error fetching category statistics: {e}")
        return json_error_response("Failed to fetch category statistics", status_code=500)
