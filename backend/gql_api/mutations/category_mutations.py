"""
Category Mutations

Implements GraphQL mutation resolvers for Category entity.
"""

import graphene
from graphene import Field, Int, String, Boolean, List
import logging

logger = logging.getLogger(__name__)


class CreateCategory(graphene.Mutation):
    """Create a new category"""

    class Arguments:
        name = String(required=True, description="分类名称")

    ok = Boolean(description="操作是否成功")
    category = Field(lambda: __import__('backend.gql_api.types.category_type', fromlist=['CategoryType']).CategoryType, description="创建的分类")
    errors = List(String, description="错误信息")

    def mutate(self, info, name: str):
        """Execute the mutation"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.core.cache.cache_system import clear_cache_pattern
            from backend.gql_api.types.category_type import CategoryType

            # Check if category already exists
            existing = fetch_one_as_dict("SELECT * FROM event_categories WHERE name = ?", (name,))
            if existing:
                return CreateCategory(ok=False, errors=[f"Category '{name}' already exists"])

            # Create category
            category_id = execute_write(
                "INSERT INTO event_categories (name) VALUES (?)",
                (name,),
                return_last_id=True
            )

            # Clear cache
            clear_cache_pattern("categories:*")

            logger.info(f"Category created via GraphQL: {name} (ID: {category_id})")

            # Return created category
            category = fetch_one_as_dict(
                """
                SELECT ec.id, ec.name, ec.created_at, ec.updated_at,
                       COUNT(le.id) as event_count
                FROM event_categories ec
                LEFT JOIN log_events le ON le.category_id = ec.id
                WHERE ec.id = ?
                GROUP BY ec.id
                """,
                (category_id,)
            )

            return CreateCategory(ok=True, category=CategoryType.from_dict(category) if category else None)

        except Exception as e:
            logger.error(f"Error creating category: {e}", exc_info=True)
            return CreateCategory(ok=False, errors=[str(e)])


class UpdateCategory(graphene.Mutation):
    """Update an existing category"""

    class Arguments:
        id = Int(required=True, description="分类ID")
        name = String(required=True, description="分类名称")

    ok = Boolean(description="操作是否成功")
    category = Field(lambda: __import__('backend.gql_api.types.category_type', fromlist=['CategoryType']).CategoryType, description="更新的分类")
    errors = List(String, description="错误信息")

    def mutate(self, info, id: int, name: str):
        """Execute the mutation"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.core.cache.cache_system import clear_cache_pattern

            # Check if category exists
            category = fetch_one_as_dict("SELECT * FROM event_categories WHERE id = ?", (id,))
            if not category:
                return UpdateCategory(ok=False, errors=["Category not found"])

            # Check if new name already exists
            existing = fetch_one_as_dict(
                "SELECT * FROM event_categories WHERE name = ? AND id != ?",
                (name, id)
            )
            if existing:
                return UpdateCategory(ok=False, errors=[f"Category '{name}' already exists"])

            # Update category
            execute_write(
                "UPDATE event_categories SET name = ? WHERE id = ?",
                (name, id)
            )

            # Clear cache
            clear_cache_pattern("categories:*")
            clear_cache_pattern("events:*")

            logger.info(f"Category updated via GraphQL: ID {id}")

            # Return updated category
            updated_category = fetch_one_as_dict(
                """
                SELECT ec.id, ec.name, ec.created_at, ec.updated_at,
                       COUNT(le.id) as event_count
                FROM event_categories ec
                LEFT JOIN log_events le ON le.category_id = ec.id
                WHERE ec.id = ?
                GROUP BY ec.id
                """,
                (id,)
            )

            return UpdateCategory(ok=True, category=CategoryType.from_dict(updated_category) if updated_category else None)

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

    def mutate(self, info, id: int):
        """Execute the mutation"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.core.cache.cache_system import clear_cache_pattern

            # Check if category exists
            category = fetch_one_as_dict("SELECT * FROM event_categories WHERE id = ?", (id,))
            if not category:
                return DeleteCategory(ok=False, errors=["Category not found"])

            # Check for associated events
            event_count = fetch_one_as_dict(
                "SELECT COUNT(*) as count FROM log_events WHERE category_id = ?",
                (id,)
            )

            if event_count['count'] > 0:
                return DeleteCategory(
                    ok=False,
                    errors=[f"Cannot delete category with {event_count['count']} associated events"]
                )

            # Delete category
            execute_write("DELETE FROM event_categories WHERE id = ?", (id,))

            # Clear cache
            clear_cache_pattern("categories:*")

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
