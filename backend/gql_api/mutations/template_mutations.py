"""
Template Mutations

Implements GraphQL mutation resolvers for Template entity.
"""

import graphene
from graphene import Field, Int, String, Boolean, List
import logging
import json

logger = logging.getLogger(__name__)


class CreateTemplate(graphene.Mutation):
    """Create a new template"""

    class Arguments:
        name = String(required=True, description="模板名称")
        description = String(description="模板描述")
        category = String(description="模板分类")
        game_gid = Int(description="关联游戏GID")
        config = String(description="模板配置JSON")

    ok = Boolean(description="操作是否成功")
    template = Field(lambda: __import__('backend.gql_api.types.template_type', fromlist=['TemplateType']).TemplateType, description="创建的模板")
    errors = List(String, description="错误信息")

    def mutate(self, info, name: str, description: str = None, category: str = None,
               game_gid: int = None, config: str = None):
        """Execute the mutation"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.core.cache.cache_system import clear_cache_pattern
            from backend.gql_api.types.template_type import TemplateType

            # Validate config JSON if provided
            if config:
                try:
                    json.loads(config)
                except json.JSONDecodeError:
                    return CreateTemplate(ok=False, errors=["Invalid JSON in config"])

            # Create template
            template_id = execute_write(
                """
                INSERT INTO canvas_templates (name, description, category, game_gid, config)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name, description, category, game_gid, config),
                return_last_id=True
            )

            # Clear cache
            clear_cache_pattern("templates:*")

            logger.info(f"Template created via GraphQL: {name} (ID: {template_id})")

            # Return created template
            template = fetch_one_as_dict(
                "SELECT * FROM canvas_templates WHERE id = ?",
                (template_id,)
            )

            return CreateTemplate(ok=True, template=TemplateType.from_dict(template) if template else None)

        except Exception as e:
            logger.error(f"Error creating template: {e}", exc_info=True)
            return CreateTemplate(ok=False, errors=[str(e)])


class UpdateTemplate(graphene.Mutation):
    """Update an existing template"""

    class Arguments:
        id = Int(required=True, description="模板ID")
        name = String(description="模板名称")
        description = String(description="模板描述")
        category = String(description="模板分类")
        game_gid = Int(description="关联游戏GID")
        config = String(description="模板配置JSON")
        is_active = Boolean(description="是否活跃")

    ok = Boolean(description="操作是否成功")
    template = Field(lambda: __import__('backend.gql_api.types.template_type', fromlist=['TemplateType']).TemplateType, description="更新的模板")
    errors = List(String, description="错误信息")

    def mutate(self, info, id: int, name: str = None, description: str = None,
               category: str = None, game_gid: int = None, config: str = None,
               is_active: bool = None):
        """Execute the mutation"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.core.cache.cache_system import clear_cache_pattern
            from backend.gql_api.types.template_type import TemplateType

            # Check if template exists
            template = fetch_one_as_dict("SELECT * FROM canvas_templates WHERE id = ?", (id,))
            if not template:
                return UpdateTemplate(ok=False, errors=["Template not found"])

            # Validate config JSON if provided
            if config:
                try:
                    json.loads(config)
                except json.JSONDecodeError:
                    return UpdateTemplate(ok=False, errors=["Invalid JSON in config"])

            # Build update query
            updates = []
            params = []

            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            if category is not None:
                updates.append("category = ?")
                params.append(category)
            if game_gid is not None:
                updates.append("game_gid = ?")
                params.append(game_gid)
            if config is not None:
                updates.append("config = ?")
                params.append(config)
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(1 if is_active else 0)

            if not updates:
                return UpdateTemplate(ok=False, errors=["No fields to update"])

            params.append(id)
            query = f"UPDATE canvas_templates SET {', '.join(updates)} WHERE id = ?"
            execute_write(query, tuple(params))

            # Clear cache
            clear_cache_pattern("templates:*")

            logger.info(f"Template updated via GraphQL: ID {id}")

            # Return updated template
            updated_template = fetch_one_as_dict(
                "SELECT * FROM canvas_templates WHERE id = ?",
                (id,)
            )

            return UpdateTemplate(ok=True, template=TemplateType.from_dict(updated_template) if updated_template else None)

        except Exception as e:
            logger.error(f"Error updating template: {e}", exc_info=True)
            return UpdateTemplate(ok=False, errors=[str(e)])


class DeleteTemplate(graphene.Mutation):
    """Delete a template"""

    class Arguments:
        id = Int(required=True, description="模板ID")

    ok = Boolean(description="操作是否成功")
    message = String(description="操作消息")
    errors = List(String, description="错误信息")

    def mutate(self, info, id: int):
        """Execute the mutation"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.core.cache.cache_system import clear_cache_pattern

            # Check if template exists
            template = fetch_one_as_dict("SELECT * FROM canvas_templates WHERE id = ?", (id,))
            if not template:
                return DeleteTemplate(ok=False, errors=["Template not found"])

            # Soft delete by setting is_active = 0
            execute_write("UPDATE canvas_templates SET is_active = 0 WHERE id = ?", (id,))

            # Clear cache
            clear_cache_pattern("templates:*")

            logger.info(f"Template deleted via GraphQL: ID {id}")

            return DeleteTemplate(ok=True, message="Template deleted successfully")

        except Exception as e:
            logger.error(f"Error deleting template: {e}", exc_info=True)
            return DeleteTemplate(ok=False, errors=[str(e)])


class TemplateMutations:
    """Container for template mutations"""
    CreateTemplate = CreateTemplate
    UpdateTemplate = UpdateTemplate
    DeleteTemplate = DeleteTemplate
