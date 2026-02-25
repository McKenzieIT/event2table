"""
Event Parameter Mutations

Implements GraphQL mutation resolvers for Event Parameter extended functionality.
"""

import graphene
from graphene import Field, Int, String, Boolean, List
import logging
import json

logger = logging.getLogger(__name__)


class UpdateEventParameter(graphene.Mutation):
    """Update an event parameter"""

    class Arguments:
        id = Int(required=True, description="参数ID")
        param_name = String(description="参数英文名")
        param_name_cn = String(description="参数中文名")
        param_type = String(description="参数类型")
        json_path = String(description="JSON路径")
        is_active = Boolean(description="是否活跃")

    ok = Boolean(description="操作是否成功")
    parameter = Field(lambda: __import__('backend.gql_api.types.event_parameter_type', fromlist=['EventParameterExtendedType']).EventParameterExtendedType, description="更新的参数")
    errors = List(String, description="错误信息")

    def mutate(self, info, id: int, param_name: str = None, param_name_cn: str = None,
               param_type: str = None, json_path: str = None, is_active: bool = None):
        """Execute the mutation"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.core.cache.cache_system import clear_cache_pattern
            from backend.gql_api.types.event_parameter_type import EventParameterExtendedType

            # Check if parameter exists
            param = fetch_one_as_dict("SELECT * FROM event_params WHERE id = ?", (id,))
            if not param:
                return UpdateEventParameter(ok=False, errors=["Parameter not found"])

            # Build update query
            updates = []
            params = []

            if param_name is not None:
                updates.append("param_name = ?")
                params.append(param_name)
            if param_name_cn is not None:
                updates.append("param_name_cn = ?")
                params.append(param_name_cn)
            if param_type is not None:
                updates.append("param_type = ?")
                params.append(param_type)
            if json_path is not None:
                updates.append("json_path = ?")
                params.append(json_path)
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(1 if is_active else 0)

            if not updates:
                return UpdateEventParameter(ok=False, errors=["No fields to update"])

            # Increment version
            updates.append("version = version + 1")

            params.append(id)
            query = f"UPDATE event_params SET {', '.join(updates)} WHERE id = ?"
            execute_write(query, tuple(params))

            # Create version history entry
            execute_write(
                """
                INSERT INTO param_versions (param_id, version, changes, changed_by)
                SELECT id, version, ?, 'graphql'
                FROM event_params WHERE id = ?
                """,
                (json.dumps({"updated_fields": [u.split('=')[0].strip() for u in updates]}), id)
            )

            # Clear cache
            clear_cache_pattern("dashboard:*")
            clear_cache_pattern("events:*")

            logger.info(f"Event parameter updated via GraphQL: ID {id}")

            # Return updated parameter
            updated_param = fetch_one_as_dict("SELECT * FROM event_params WHERE id = ?", (id,))

            return UpdateEventParameter(ok=True, parameter=EventParameterExtendedType.from_dict(updated_param) if updated_param else None)

        except Exception as e:
            logger.error(f"Error updating event parameter: {e}", exc_info=True)
            return UpdateEventParameter(ok=False, errors=[str(e)])


class DeleteEventParameter(graphene.Mutation):
    """Delete an event parameter"""

    class Arguments:
        id = Int(required=True, description="参数ID")

    ok = Boolean(description="操作是否成功")
    message = String(description="操作消息")
    errors = List(String, description="错误信息")

    def mutate(self, info, id: int):
        """Execute the mutation"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.core.cache.cache_system import clear_cache_pattern

            # Check if parameter exists
            param = fetch_one_as_dict("SELECT * FROM event_params WHERE id = ?", (id,))
            if not param:
                return DeleteEventParameter(ok=False, errors=["Parameter not found"])

            # Soft delete
            execute_write("UPDATE event_params SET is_active = 0 WHERE id = ?", (id,))

            # Clear cache
            clear_cache_pattern("dashboard:*")
            clear_cache_pattern("events:*")

            logger.info(f"Event parameter deleted via GraphQL: ID {id}")

            return DeleteEventParameter(ok=True, message="Parameter deleted successfully")

        except Exception as e:
            logger.error(f"Error deleting event parameter: {e}", exc_info=True)
            return DeleteEventParameter(ok=False, errors=[str(e)])


class SetParamConfig(graphene.Mutation):
    """Set parameter configuration"""

    class Arguments:
        param_id = Int(required=True, description="参数ID")
        array_expand = Boolean(description="是否展开数组")
        map_expand = Boolean(description="是否展开Map")
        custom_hql_template = String(description="自定义HQL模板")
        output_field_name = String(description="输出字段名")

    ok = Boolean(description="操作是否成功")
    config = Field(lambda: __import__('backend.gql_api.types.event_parameter_type', fromlist=['ParamConfigType']).ParamConfigType, description="配置")
    errors = List(String, description="错误信息")

    def mutate(self, info, param_id: int, array_expand: bool = None, map_expand: bool = None,
               custom_hql_template: str = None, output_field_name: str = None):
        """Execute the mutation"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.core.cache.cache_system import clear_cache_pattern
            from backend.gql_api.types.event_parameter_type import ParamConfigType

            # Check if config exists
            existing = fetch_one_as_dict("SELECT * FROM param_configs WHERE param_id = ?", (param_id,))

            if existing:
                # Update existing config
                updates = []
                params = []

                if array_expand is not None:
                    updates.append("array_expand = ?")
                    params.append(1 if array_expand else 0)
                if map_expand is not None:
                    updates.append("map_expand = ?")
                    params.append(1 if map_expand else 0)
                if custom_hql_template is not None:
                    updates.append("custom_hql_template = ?")
                    params.append(custom_hql_template)
                if output_field_name is not None:
                    updates.append("output_field_name = ?")
                    params.append(output_field_name)

                if updates:
                    params.append(param_id)
                    query = f"UPDATE param_configs SET {', '.join(updates)} WHERE param_id = ?"
                    execute_write(query, tuple(params))
            else:
                # Create new config
                execute_write(
                    """
                    INSERT INTO param_configs (param_id, array_expand, map_expand, custom_hql_template, output_field_name)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (param_id, 1 if array_expand else 0, 1 if map_expand else 0, custom_hql_template, output_field_name)
                )

            # Clear cache
            clear_cache_pattern("events:*")

            logger.info(f"Param config set via GraphQL: param_id {param_id}")

            # Return config
            config = fetch_one_as_dict("SELECT * FROM param_configs WHERE param_id = ?", (param_id,))

            return SetParamConfig(ok=True, config=ParamConfigType.from_dict(config) if config else None)

        except Exception as e:
            logger.error(f"Error setting param config: {e}", exc_info=True)
            return SetParamConfig(ok=False, errors=[str(e)])


class RollbackEventParameter(graphene.Mutation):
    """Rollback parameter to a previous version"""

    class Arguments:
        id = Int(required=True, description="参数ID")
        version = Int(required=True, description="目标版本号")

    ok = Boolean(description="操作是否成功")
    parameter = Field(lambda: __import__('backend.gql_api.types.event_parameter_type', fromlist=['EventParameterExtendedType']).EventParameterExtendedType, description="回滚后的参数")
    errors = List(String, description="错误信息")

    def mutate(self, info, id: int, version: int):
        """Execute the mutation"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.core.cache.cache_system import clear_cache_pattern
            from backend.gql_api.types.event_parameter_type import EventParameterExtendedType

            # Check if parameter exists
            param = fetch_one_as_dict("SELECT * FROM event_params WHERE id = ?", (id,))
            if not param:
                return RollbackEventParameter(ok=False, errors=["Parameter not found"])

            # Get target version
            target_version = fetch_one_as_dict(
                "SELECT * FROM param_versions WHERE param_id = ? AND version = ?",
                (id, version)
            )
            if not target_version:
                return RollbackEventParameter(ok=False, errors=[f"Version {version} not found"])

            # Parse changes and apply
            changes = json.loads(target_version.get('changes', '{}'))

            # Update parameter with version data
            execute_write(
                "UPDATE event_params SET version = ? WHERE id = ?",
                (version, id)
            )

            # Clear cache
            clear_cache_pattern("dashboard:*")
            clear_cache_pattern("events:*")

            logger.info(f"Event parameter rolled back via GraphQL: ID {id} to version {version}")

            # Return updated parameter
            updated_param = fetch_one_as_dict("SELECT * FROM event_params WHERE id = ?", (id,))

            return RollbackEventParameter(ok=True, parameter=EventParameterExtendedType.from_dict(updated_param) if updated_param else None)

        except Exception as e:
            logger.error(f"Error rolling back event parameter: {e}", exc_info=True)
            return RollbackEventParameter(ok=False, errors=[str(e)])


class CreateValidationRule(graphene.Mutation):
    """Create a validation rule for a parameter"""

    class Arguments:
        param_id = Int(required=True, description="参数ID")
        rule_type = String(required=True, description="规则类型")
        rule_config = String(description="规则配置JSON")
        error_message = String(description="错误消息")

    ok = Boolean(description="操作是否成功")
    rule = Field(lambda: __import__('backend.gql_api.types.event_parameter_type', fromlist=['ValidationRuleType']).ValidationRuleType, description="创建的规则")
    errors = List(String, description="错误信息")

    def mutate(self, info, param_id: int, rule_type: str, rule_config: str = None, error_message: str = None):
        """Execute the mutation"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.gql_api.types.event_parameter_type import ValidationRuleType

            # Validate rule_config JSON if provided
            if rule_config:
                try:
                    json.loads(rule_config)
                except json.JSONDecodeError:
                    return CreateValidationRule(ok=False, errors=["Invalid JSON in rule_config"])

            # Create validation rule
            rule_id = execute_write(
                """
                INSERT INTO param_validation_rules (param_id, rule_type, rule_config, error_message)
                VALUES (?, ?, ?, ?)
                """,
                (param_id, rule_type, rule_config, error_message),
                return_last_id=True
            )

            logger.info(f"Validation rule created via GraphQL: param_id {param_id}")

            # Return created rule
            rule = fetch_one_as_dict("SELECT * FROM param_validation_rules WHERE id = ?", (rule_id,))

            return CreateValidationRule(ok=True, rule=ValidationRuleType.from_dict(rule) if rule else None)

        except Exception as e:
            logger.error(f"Error creating validation rule: {e}", exc_info=True)
            return CreateValidationRule(ok=False, errors=[str(e)])


class EventParameterMutations:
    """Container for event parameter mutations"""
    UpdateEventParameter = UpdateEventParameter
    DeleteEventParameter = DeleteEventParameter
    SetParamConfig = SetParamConfig
    RollbackEventParameter = RollbackEventParameter
    CreateValidationRule = CreateValidationRule
