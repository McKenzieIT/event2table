"""
Field Builder GraphQL Mutations

Mutation resolvers for field builder configuration management.
This module provides GraphQL mutations as a replacement for REST API endpoints.
"""

import graphene
from graphene import Mutation, String, Int, Boolean, Field, List, ObjectType
import logging
import json
import time

logger = logging.getLogger(__name__)


class SaveFieldBuilderConfig(Mutation):
    """
    Save field builder configuration

    Creates a new field builder configuration or updates an existing one.

    GraphQL equivalent of:
    - POST /api/field-builder/config
    - POST /api/field-builder/configs
    """
    class Arguments:
        config = String(required=True, description="Field mapping configuration as JSON string")
        viewName = String(required=True, description="View/table name")
        displayName = String(description="Display name for the configuration")
        id = Int(description="Configuration ID for update (optional)")

    ok = Boolean()
    fieldBuilderConfig = Field('backend.gql_api.types.field_builder_type.FieldBuilderConfigType')
    errors = List(String)
    message = String()

    def mutate(self, info, config, viewName, displayName=None, id=None):
        """Save field builder configuration"""
        try:
            from backend.core.data_access import Repositories
            from backend.core.cache.cache_system import clear_cache_pattern
            from backend.core.utils import execute_write

            # Parse config JSON
            try:
                config_data = json.loads(config) if isinstance(config, str) else config
            except json.JSONDecodeError as e:
                return SaveFieldBuilderConfig(
                    ok=False,
                    fieldBuilderConfig=None,
                    errors=[f"Invalid JSON in config: {str(e)}"],
                    message="Failed to parse configuration"
                )

            # Convert config to JSON string for storage
            config_json = json.dumps(config_data, ensure_ascii=False)

            # Retry logic for database lock errors
            max_retries = 3
            delay = 0.1

            for attempt in range(max_retries):
                try:
                    if id:
                        # Update existing configuration
                        affected = execute_write(
                            """
                            UPDATE join_configs
                            SET field_mapping_v2 = ?,
                                output_table = ?,
                                display_name = ?
                            WHERE id = ?
                            """,
                            (config_json, viewName, displayName, id),
                        )

                        if affected == 0:
                            return SaveFieldBuilderConfig(
                                ok=False,
                                fieldBuilderConfig=None,
                                errors=["Configuration not found"],
                                message="Update failed"
                            )
                    else:
                        # Create new configuration
                        name = viewName.replace("v_dwd_", "").replace("_", " ").strip().title()

                        id = execute_write(
                            """
                            INSERT INTO join_configs (
                                name,
                                source_events,
                                field_mapping_v2,
                                output_table,
                                display_name,
                                created_at
                            ) VALUES (?, '[]', ?, ?, ?, CURRENT_TIMESTAMP)
                            """,
                            (name, config_json, viewName, displayName),
                            return_last_id=True,
                        )

                    # Clear cache
                    clear_cache_pattern("field_builder")

                    logger.info(f"Field builder config saved: {id}")

                    # Fetch the saved configuration
                    repo = Repositories.join_configs()
                    saved_config = repo.get_by_id(id)

                    return SaveFieldBuilderConfig(
                        ok=True,
                        fieldBuilderConfig=saved_config,
                        errors=[],
                        message="Field builder configuration saved successfully"
                    )

                except Exception as e:
                    error_str = str(e).lower()
                    if "database is locked" in error_str and attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)
                        logger.warning(
                            f"Database locked, retry {attempt + 1}/{max_retries} after {wait_time}s"
                        )
                        time.sleep(wait_time)
                        continue
                    else:
                        raise

        except Exception as e:
            logger.error(f"Error saving field builder config: {e}", exc_info=True)
            return SaveFieldBuilderConfig(
                ok=False,
                fieldBuilderConfig=None,
                errors=[str(e)],
                message="An internal error occurred"
            )


class DeleteFieldBuilderConfig(Mutation):
    """
    Delete a field builder configuration

    GraphQL equivalent of:
    - DELETE /api/field-builder/config/<id>
    """
    class Arguments:
        id = Int(required=True, description="Configuration ID to delete")

    ok = Boolean()
    message = String()
    errors = List(String)

    def mutate(self, info, id):
        """Delete field builder configuration"""
        try:
            from backend.core.data_access import Repositories
            from backend.core.cache.cache_system import clear_cache_pattern

            repo = Repositories.join_configs()

            # Check if config exists
            config = repo.get_by_id(id)
            if not config:
                return DeleteFieldBuilderConfig(
                    ok=False,
                    message="Configuration not found",
                    errors=["Configuration not found"]
                )

            # Delete
            repo.delete(id)

            # Clear cache
            clear_cache_pattern("field_builder")

            logger.info(f"Field builder config deleted: {id}")

            return DeleteFieldBuilderConfig(
                ok=True,
                message="Configuration deleted successfully",
                errors=[]
            )

        except Exception as e:
            logger.error(f"Error deleting field builder config {id}: {e}", exc_info=True)
            return DeleteFieldBuilderConfig(
                ok=False,
                message="An internal error occurred",
                errors=[str(e)]
            )


class PreviewFieldBuilderHQL(Mutation):
    """
    Preview HQL from field builder configuration

    Generates HQL preview without saving the configuration.

    GraphQL equivalent of:
    - POST /api/field-builder/preview
    """
    class Arguments:
        config = String(required=True, description="Field mapping configuration as JSON string")
        sourceEvents = String(required=True, description="Source event IDs as JSON array")
        viewName = String(default_value="v_dwd_preview", description="View/table name")
        dateVar = String(default_value="${bizdate}", description="Date variable")

    ok = Boolean()
    hql = String()
    errors = List(String)
    message = String()

    def mutate(self, info, config, sourceEvents, viewName="v_dwd_preview", dateVar="${bizdate}"):
        """Preview HQL from field builder configuration"""
        try:
            # Parse JSON inputs
            try:
                config_data = json.loads(config) if isinstance(config, str) else config
                source_events = json.loads(sourceEvents) if isinstance(sourceEvents, str) else sourceEvents
            except json.JSONDecodeError as e:
                return PreviewFieldBuilderHQL(
                    ok=False,
                    hql=None,
                    errors=[f"Invalid JSON: {str(e)}"],
                    message="Failed to parse input"
                )

            if not config_data:
                return PreviewFieldBuilderHQL(
                    ok=False,
                    hql=None,
                    errors=["Missing configuration data"],
                    message="Preview failed"
                )

            if not source_events:
                return PreviewFieldBuilderHQL(
                    ok=False,
                    hql=None,
                    errors=["Missing source_events"],
                    message="Preview failed"
                )

            # Build join_config for v3 generator
            join_config = {
                "source_events": json.dumps(source_events),
                "field_mapping_v2": json.dumps(config_data),
                "output_table": viewName,
                "display_name": "Preview",
            }

            # Use v3 generator to create HQL
            from backend.services.hql.generator_v3 import hql_generator_v3

            hql = hql_generator_v3.generate_from_field_mapping_v2(join_config, dateVar)

            return PreviewFieldBuilderHQL(
                ok=True,
                hql=hql,
                errors=[],
                message="HQL preview generated successfully"
            )

        except Exception as e:
            logger.error(f"Error previewing HQL: {e}", exc_info=True)
            return PreviewFieldBuilderHQL(
                ok=False,
                hql=None,
                errors=[str(e)],
                message="An internal error occurred"
            )


class FieldBuilderMutations(ObjectType):
    """
    Field Builder Mutations

    GraphQL mutations for field builder configuration management.
    These mutations replace the legacy REST API endpoints.
    """
    save_field_builder_config = SaveFieldBuilderConfig.Field(
        description="Save field builder configuration (create or update)"
    )
    delete_field_builder_config = DeleteFieldBuilderConfig.Field(
        description="Delete a field builder configuration"
    )
    preview_field_builder_hql = PreviewFieldBuilderHQL.Field(
        description="Preview HQL from field builder configuration"
    )
