"""
Category Mutations

Implements GraphQL mutation resolvers for Category entity.

Provides comprehensive business logic validation:
- Input validation (name, color format)
- Game context validation (game must exist)
- Uniqueness constraints (name within game)
- Business rule enforcement (category protection, event associations)
"""

import logging
import re
from datetime import datetime

import graphene
from graphene import Boolean, Field, Int, List, String

from backend.core.security.authentication import authenticated, require_permission

logger = logging.getLogger(__name__)


class CreateCategory(graphene.Mutation):
    """
    Create a new category

    Business Rules:
        - category_name cannot be empty
        - category_name must be unique (globally, not per-game in current schema)
        - color must be hex format (#RRGGBB) if provided
        - created_at and updated_at are automatically initialized

    Example:
        mutation {
            createCategory(name: "Combat Events", color: "#FF5733") {
                ok
                category { id name color }
                errors
            }
        }
    """

    class Arguments:
        name = String(required=True, description="分类名称（不能为空）")
        color = String(description="分类颜色（十六进制格式 #RRGGBB, 可选）")

    ok = Boolean(description="操作是否成功")
    category = Field(
        lambda: __import__(
            'backend.gql_api.types.category_type', fromlist=['CategoryType']
        ).CategoryType,
        description="创建的分类",
    )
    errors = List(String, description="错误信息")

    @authenticated
    @require_permission("write")
    def mutate(self, info, name: str, color: str | None = None):
        """
        Execute the mutation with comprehensive validation

        Validation Layers:
            1. Input Validation: name format, color format
            2. Uniqueness Check: category_name must be unique globally
            3. Timestamp Initialization: created_at, updated_at

        Returns:
            CreateCategory with ok=True if successful
            CreateCategory with ok=False and errors list if validation fails
        """
        try:
            from backend.core.cache.cache_system import hierarchical_cache  # ⚡ PERF: Phase 1.2 Fix
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.gql_api.types.category_type import CategoryType

            # ========================================
            # Layer 1: Input Validation
            # ========================================

            # 1.1 Validate category_name is not empty
            if not name or len(name.strip()) == 0:
                return CreateCategory(ok=False, errors=["Category name cannot be empty"])

            # Trim whitespace from name
            name = name.strip()

            # 1.2 Validate name length (reasonable limit)
            if len(name) > 50:
                return CreateCategory(
                    ok=False,
                    errors=[f"Category name too long (max 50 characters), got: {len(name)}"],
                )

            # 1.3 Validate color format (if provided)
            if color is not None:
                # Validate hex color format (#RRGGBB)
                if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
                    return CreateCategory(
                        ok=False,
                        errors=[f"Invalid color format: '{color}'. Must be hex format (#RRGGBB)"],
                    )

            # ========================================
            # Layer 2: Uniqueness Check
            # ========================================

            # 2.1 Check if category already exists (global uniqueness)
            existing = fetch_one_as_dict("SELECT * FROM event_categories WHERE name = ?", (name,))
            if existing:
                return CreateCategory(
                    ok=False, errors=[f"Category '{name}' already exists (ID: {existing['id']})"]
                )

            # ========================================
            # Layer 3: Timestamp Initialization
            # ========================================

            now = datetime.now()

            # ========================================
            # Create Category
            # ========================================

            # Build INSERT query dynamically based on provided fields
            if color:
                category_id = execute_write(
                    "INSERT INTO event_categories (name, color, created_at, updated_at) VALUES (?, ?, ?, ?)",
                    (name, color, now, now),
                    return_last_id=True,
                )
            else:
                category_id = execute_write(
                    "INSERT INTO event_categories (name, created_at, updated_at) VALUES (?, ?, ?)",
                    (name, now, now),
                    return_last_id=True,
                )

            # ⚡ PERF: Phase 1.2 Fix - Correct cache invalidation
            try:
                hierarchical_cache.delete("dashboard_statistics")
                hierarchical_cache.delete("categories")
                logger.info(f"✅ 已失效缓存: dashboard_statistics, categories (分类创建)")
            except Exception as e:
                logger.warning(f"⚠️ 失效缓存失败: {e}")

            logger.info(f"Category created via GraphQL: {name} (ID: {category_id})")

            # Return created category
            category = fetch_one_as_dict(
                """
                SELECT ec.id, ec.name, ec.color, ec.created_at, ec.updated_at,
                       COUNT(le.id) as event_count
                FROM event_categories ec
                LEFT JOIN log_events le ON le.category_id = ec.id
                WHERE ec.id = ?
                GROUP BY ec.id
                """,
                (category_id,),
            )

            return CreateCategory(
                ok=True, category=CategoryType.from_dict(category) if category else None
            )

        except Exception as e:
            logger.error(f"Error creating category: {e}", exc_info=True)
            return CreateCategory(ok=False, errors=[str(e)])


class UpdateCategory(graphene.Mutation):
    """
    Update an existing category

    Business Rules:
        - Category must exist (existence check)
        - name must be unique (if changing)
        - color must be hex format (#RRGGBB) if changing
        - updated_at is automatically updated

    Example:
        mutation {
            updateCategory(id: 1, name: "Combat Events Updated", color: "#FF5733") {
                ok
                category { id name color }
                errors
            }
        }
    """

    class Arguments:
        id = Int(required=True, description="分类ID")
        name = String(description="分类名称（如果提供, 必须唯一）")
        color = String(description="分类颜色（十六进制格式 #RRGGBB, 可选）")

    ok = Boolean(description="操作是否成功")
    category = Field(
        lambda: __import__(
            'backend.gql_api.types.category_type', fromlist=['CategoryType']
        ).CategoryType,
        description="更新的分类",
    )
    errors = List(String, description="错误信息")

    @authenticated
    @require_permission("write")
    def mutate(self, info, id: int, name: str | None = None, color: str | None = None):
        """
        Execute the mutation with comprehensive validation

        Validation Layers:
            1. Existence Check: Category must exist
            2. Input Validation: name format, color format
            3. Uniqueness Check: name must be unique (if changing)
            4. Timestamp Update: updated_at is automatically updated

        Returns:
            UpdateCategory with ok=True if successful
            UpdateCategory with ok=False and errors list if validation fails
        """
        try:
            from backend.core.cache.cache_system import hierarchical_cache  # ⚡ PERF: Phase 1.2 Fix
            from backend.core.utils import execute_write, fetch_one_as_dict

            # ========================================
            # Layer 1: Existence Check
            # ========================================

            # 1.1 Check if category exists
            category = fetch_one_as_dict("SELECT * FROM event_categories WHERE id = ?", (id,))
            if not category:
                return UpdateCategory(ok=False, errors=[f"Category with id {id} not found"])

            # ========================================
            # Layer 2: Build Update Query
            # ========================================

            updates = []
            params = []
            errors = []

            # 2.1 Validate and add name (if provided)
            if name is not None:
                # Trim whitespace
                name = name.strip()

                # Validate name is not empty
                if not name:
                    errors.append("Category name cannot be empty")

                # Validate name length
                elif len(name) > 50:
                    errors.append(f"Category name too long (max 50 characters), got: {len(name)}")

                # Check name uniqueness
                else:
                    existing = fetch_one_as_dict(
                        "SELECT * FROM event_categories WHERE name = ? AND id != ?", (name, id)
                    )
                    if existing:
                        errors.append(
                            f"Category name '{name}' already exists (ID: {existing['id']})"
                        )
                    else:
                        updates.append("name = ?")
                        params.append(name)

            # 2.2 Validate and add color (if provided)
            if color is not None:
                # Validate hex color format (#RRGGBB)
                if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
                    errors.append(f"Invalid color format: '{color}'. Must be hex format (#RRGGBB)")
                else:
                    updates.append("color = ?")
                    params.append(color)

            # ========================================
            # Layer 3: Validation Summary
            # ========================================

            # 3.1 Return errors if any validation failed
            if errors:
                return UpdateCategory(ok=False, errors=errors)

            # 3.2 Check if there are any fields to update
            if not updates:
                return UpdateCategory(
                    ok=False, errors=["No fields to update (all fields are None or unchanged)"]
                )

            # ========================================
            # Layer 4: Execute Update
            # ========================================

            # 4.1 Add updated_at timestamp
            updates.append("updated_at = ?")
            params.append(datetime.now())

            # 4.2 Add id to params (WHERE clause)
            params.append(id)

            # 4.3 Execute UPDATE query
            query = f"UPDATE event_categories SET {', '.join(updates)} WHERE id = ?"
            execute_write(query, tuple(params))

            # ⚡ PERF: Phase 1.2 Fix - Correct cache invalidation
            try:
                hierarchical_cache.delete("dashboard_statistics")
                hierarchical_cache.delete("categories")
                hierarchical_cache.delete(f"category:{id}")
                logger.info(f"✅ 已失效缓存: dashboard_statistics, categories (分类更新)")
            except Exception as e:
                logger.warning(f"⚠️ 失效缓存失败: {e}")

            logger.info(
                f"Category updated via GraphQL: ID {id} (fields: {', '.join([u.split()[0] for u in updates[:-1]])})"
            )

            # Return updated category
            updated_category = fetch_one_as_dict(
                """
                SELECT ec.id, ec.name, ec.color, ec.created_at, ec.updated_at,
                       COUNT(le.id) as event_count
                FROM event_categories ec
                LEFT JOIN log_events le ON le.category_id = ec.id
                WHERE ec.id = ?
                GROUP BY ec.id
                """,
                (id,),
            )

            return UpdateCategory(
                ok=True,
                category=CategoryType.from_dict(updated_category) if updated_category else None,
            )

        except Exception as e:
            logger.error(f"Error updating category: {e}", exc_info=True)
            return UpdateCategory(ok=False, errors=[str(e)])


class DeleteCategory(graphene.Mutation):
    """Delete a category"""

    class Arguments:
        id = Int(required=True, description="分类ID")

    ok = Boolean(description="操作是否成功")
    message = String(description="操作消息")
    errors = List(String, description="错误信息")

    @authenticated
    @require_permission("write")
    def mutate(self, info, id: int):
        """Execute the mutation"""
        try:
            from backend.core.cache.cache_system import hierarchical_cache  # ⚡ PERF: Phase 1.2 Fix
            from backend.core.utils import execute_write, fetch_one_as_dict

            # Check if category exists
            category = fetch_one_as_dict("SELECT * FROM event_categories WHERE id = ?", (id,))
            if not category:
                return DeleteCategory(ok=False, errors=["Category not found"])

            # Check for associated events
            event_count = fetch_one_as_dict(
                "SELECT COUNT(*) as count FROM log_events WHERE category_id = ?", (id,)
            )

            if event_count['count'] > 0:
                return DeleteCategory(
                    ok=False,
                    errors=[
                        f"Cannot delete category with {event_count['count']} associated events"
                    ],
                )

            # Delete category
            execute_write("DELETE FROM event_categories WHERE id = ?", (id,))

            # ⚡ PERF: Phase 1.2 Fix - Correct cache invalidation
            try:
                hierarchical_cache.delete("dashboard_statistics")
                hierarchical_cache.delete("categories")
                hierarchical_cache.delete(f"category:{id}")
                logger.info(f"✅ 已失效缓存: dashboard_statistics, categories (分类删除)")
            except Exception as e:
                logger.warning(f"⚠️ 失效缓存失败: {e}")

            logger.info(f"Category deleted via GraphQL: ID {id}")

            return DeleteCategory(ok=True, message="Category deleted successfully")

        except Exception as e:
            logger.error(f"Error deleting category: {e}", exc_info=True)
            return DeleteCategory(ok=False, errors=[str(e)])


class CategoryMutations:
    """Container for category mutations"""

    CreateCategory = CreateCategory
    UpdateCategory = UpdateCategory
    DeleteCategory = DeleteCategory
