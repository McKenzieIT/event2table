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
- DELETE /api/categories/batch - Batch delete categories
"""

import logging
import sqlite3

# Import cache functions
import sys

from flask import request

# Import shared utilities
from backend.core.utils import (
    execute_write,
    fetch_all_as_dict,
    fetch_one_as_dict,
    json_error_response,
    json_success_response,
    sanitize_and_validate_string,
    validate_json_request,
)

sys.path.append("..")
try:
    from backend.core.cache.cache_system import clear_cache_pattern
except ImportError:

    def clear_cache_pattern(pattern):
        """
        Clear cache entries matching a pattern (fallback implementation).

        This is a fallback function used when the cache_system module
        is not available. It does nothing but prevents ImportError.

        Args:
            pattern (str): Cache key pattern to match (unused in fallback)

        Returns:
            None
        """
        pass


# Import Repository pattern for data access
from backend.core.data_access import Repositories

# Import the parent blueprint
from .. import api_bp

logger = logging.getLogger(__name__)


@api_bp.route("/api/categories", methods=["GET"])
def api_list_categories():
    """API: List all categories with event counts"""
    try:
        categories = fetch_all_as_dict("""
            SELECT
                ec.id,
                ec.name,
                ec.created_at,
                COUNT(DISTINCT le.id) as event_count
            FROM event_categories ec
            LEFT JOIN log_events le ON ec.id = le.category_id
            GROUP BY ec.id
            ORDER BY ec.name
        """)
        return json_success_response(data=categories)
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        return json_error_response("Failed to fetch categories", status_code=500)


@api_bp.route("/api/categories/<int:id>", methods=["GET"])
def api_get_category(id):
    """API: Get a single category by ID"""
    try:
        category = Repositories.EVENT_CATEGORIES.find_by_id(id)

        if not category:
            return json_error_response("Category not found", status_code=404)

        return json_success_response(data=category)
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
        execute_write("INSERT INTO event_categories (name) VALUES (?)", (name,))
        clear_cache_pattern("categories")
        logger.info(f"Category created: {name}")
        return json_success_response(message="Category created successfully")
    except sqlite3.IntegrityError:
        return json_error_response("Category name already exists", status_code=409)
    except Exception as e:
        logger.error(f"Error creating category: {e}")
        return json_error_response("Failed to create category", status_code=500)


@api_bp.route("/api/categories/<int:id>", methods=["PUT", "PATCH"])
def api_update_category(id):
    """API: Update an existing category"""
    category = Repositories.EVENT_CATEGORIES.find_by_id(id)
    if not category:
        return json_error_response("Category not found", status_code=404)

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
        execute_write("UPDATE event_categories SET name = ? WHERE id = ?", (name, id))
        clear_cache_pattern("categories")
        logger.info(f"Category updated: {name} (ID: {id})")
        return json_success_response(message="Category updated successfully")
    except sqlite3.IntegrityError:
        return json_error_response("Category name already exists", status_code=409)
    except Exception as e:
        logger.error(f"Error updating category {id}: {e}")
        return json_error_response("Failed to update category", status_code=500)


@api_bp.route("/api/categories/<int:id>", methods=["DELETE"])
def api_delete_category(id):
    """API: Delete a category"""
    category = Repositories.EVENT_CATEGORIES.find_by_id(id)
    if not category:
        return json_error_response("Category not found", status_code=404)

    try:
        # Delete category relations first
        execute_write("DELETE FROM event_category_relations WHERE category_id = ?", (id,))
        # Delete category
        Repositories.EVENT_CATEGORIES.delete(id)

        clear_cache_pattern("categories")
        logger.info(f"Category deleted: {category['name']} (ID: {id})")
        return json_success_response(message="Category deleted successfully")
    except Exception as e:
        logger.error(f"Error deleting category {id}: {e}")
        return json_error_response("Failed to delete category", status_code=500)


@api_bp.route("/api/categories/batch", methods=["DELETE"])
def api_batch_delete_categories():
    """API: Batch delete categories"""
    is_valid, data, error = validate_json_request(["ids"])
    if not is_valid:
        return json_error_response(error, status_code=400)

    if not data["ids"] or not isinstance(data["ids"], list):
        return json_error_response("Invalid category IDs", status_code=400)

    try:
        # Delete category relations first
        execute_write(
            f'DELETE FROM event_category_relations WHERE category_id IN ({",".join(["?"] * len(data["ids"]))})',
            data["ids"],
        )
        # Delete categories using Repository batch delete
        deleted_count = Repositories.EVENT_CATEGORIES.delete_batch(data["ids"])

        clear_cache_pattern("categories")
        logger.info(f"Batch deleted {deleted_count} categories")
        return json_success_response(
            message=f"Deleted {deleted_count} categories", data={"deleted_count": deleted_count}
        )
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

        # Use Repository batch update
        updated_count = Repositories.EVENT_CATEGORIES.update_batch(category_ids, updates)

        clear_cache_pattern("categories")
        logger.info(f"Batch updated {updated_count} categories")
        return json_success_response(
            message=f"Updated {updated_count} categories", data={"updated_count": updated_count}
        )
    except Exception as e:
        logger.error(f"Error batch updating categories: {e}")
        return json_error_response("Failed to update categories", status_code=500)
