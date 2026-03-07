"""
Parameter Mutations

Implements GraphQL mutation resolvers for Parameter entity.
"""

import graphene
from graphene import Field, Int, String, Boolean, List
import logging

logger = logging.getLogger(__name__)


class CreateParameter(graphene.Mutation):
    """Create a new parameter"""

    class Arguments:
        event_id = Int(required=True, description="事件ID")
        param_name = String(required=True, description="参数英文名")
        param_name_cn = String(description="参数中文名")
        template_id = Int(description="参数模板ID")
        json_path = String(description="JSON路径")
        is_active = Boolean(default_value=True, description="是否活跃")

    ok = Boolean(description="操作是否成功")
    parameter = Field(lambda: __import__('backend.gql_api.types.parameter_type', fromlist=['ParameterType']).ParameterType, description="创建的参数")
    errors = List(String, description="错误信息")

    def mutate(self, info, event_id: int, param_name: str, param_name_cn: str = None,
               template_id: int = None, json_path: str = None, is_active: bool = True):
        """Execute the mutation"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.core.cache.cache_system import hierarchical_cache  # ⚡ PERF: Phase 1.2 Fix
            from backend.gql_api.types.parameter_type import ParameterType

            # Validate event exists
            event = fetch_one_as_dict("SELECT * FROM log_events WHERE id = ?", (event_id,))
            if not event:
                return CreateParameter(ok=False, errors=[f"Event {event_id} not found"])

            game_gid = event['game_gid']

            # Create parameter
            param_id = execute_write(
                """INSERT INTO event_params
                   (event_id, param_name, param_name_cn, template_id, json_path, is_active, version)
                   VALUES (?, ?, ?, ?, ?, ?, 1)""",
                (event_id, param_name, param_name_cn, template_id, json_path, 1 if is_active else 0),
                return_last_id=True
            )

            # ⚡ PERF: Phase 1.2 Fix - Correct cache invalidation
            try:
                hierarchical_cache.delete("dashboard_statistics")
                logger.info(f"✅ 已失效缓存: dashboard_statistics (参数创建)")
            except Exception as e:
                logger.warning(f"⚠️ 失效dashboard_statistics失败: {e}")

            try:
                hierarchical_cache.delete(f"parameters:{event_id}")
                hierarchical_cache.delete(f"events:{game_gid}")
                logger.info(f"✅ 已失效缓存: parameters:{event_id}, events:{game_gid}")
            except Exception as e:
                logger.warning(f"⚠️ 失效parameters/events缓存失败: {e}")

            logger.info(f"Parameter created via GraphQL: {param_name} (ID: {param_id})")

            # Return created parameter
            parameter = fetch_one_as_dict(
                """
                SELECT ep.*, pt.name as template_name, pt.description
                FROM event_params ep
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                WHERE ep.id = ?
                """,
                (param_id,)
            )

            return CreateParameter(ok=True, parameter=ParameterType.from_dict(parameter) if parameter else None)

        except Exception as e:
            logger.error(f"Error creating parameter: {e}", exc_info=True)
            return CreateParameter(ok=False, errors=[str(e)])


class UpdateParameter(graphene.Mutation):
    """Update an existing parameter"""

    class Arguments:
        id = Int(required=True, description="参数ID")
        param_name_cn = String(description="参数中文名")
        template_id = Int(description="参数模板ID")
        json_path = String(description="JSON路径")
        is_active = Boolean(description="是否活跃")

    ok = Boolean(description="操作是否成功")
    parameter = Field(lambda: __import__('backend.gql_api.types.parameter_type', fromlist=['ParameterType']).ParameterType, description="更新的参数")
    errors = List(String, description="错误信息")

    def mutate(self, info, id: int, param_name_cn: str = None, template_id: int = None,
               json_path: str = None, is_active: bool = None):
        """Execute the mutation"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.core.cache.cache_system import hierarchical_cache  # ⚡ PERF: Phase 1.2 Fix

            # Check if parameter exists
            param = fetch_one_as_dict("SELECT * FROM event_params WHERE id = ?", (id,))
            if not param:
                return UpdateParameter(ok=False, errors=["Parameter not found"])

            # Build update query
            updates = []
            params = []

            if param_name_cn:
                updates.append("param_name_cn = ?")
                params.append(param_name_cn)

            if template_id:
                updates.append("template_id = ?")
                params.append(template_id)

            if json_path:
                updates.append("json_path = ?")
                params.append(json_path)

            if is_active is not None:
                updates.append("is_active = ?")
                params.append(1 if is_active else 0)

            if not updates:
                return UpdateParameter(ok=False, errors=["No fields to update"])

            # Increment version
            updates.append("version = version + 1")

            params.append(id)
            query = f"UPDATE event_params SET {', '.join(updates)} WHERE id = ?"

            execute_write(query, tuple(params))

            # Get event for cache invalidation
            event = fetch_one_as_dict("SELECT game_gid FROM log_events WHERE id = ?", (param['event_id'],))
            event_id = param['event_id']
            game_gid = event['game_gid'] if event else None

            # ⚡ PERF: Phase 1.2 Fix - Correct cache invalidation
            try:
                hierarchical_cache.delete("dashboard_statistics")
                logger.info(f"✅ 已失效缓存: dashboard_statistics (参数更新)")
            except Exception as e:
                logger.warning(f"⚠️ 失效dashboard_statistics失败: {e}")

            try:
                hierarchical_cache.delete(f"parameters:{event_id}")
                hierarchical_cache.delete(f"parameter:{id}")
                if game_gid:
                    hierarchical_cache.delete(f"events:{game_gid}")
                logger.info(f"✅ 已失效缓存: parameters:{event_id}, parameter:{id}")
            except Exception as e:
                logger.warning(f"⚠️ 失效parameters/parameter缓存失败: {e}")

            logger.info(f"Parameter updated via GraphQL: ID {id}")

            # Return updated parameter
            updated_param = fetch_one_as_dict(
                """
                SELECT ep.*, pt.name as template_name, pt.description
                FROM event_params ep
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                WHERE ep.id = ?
                """,
                (id,)
            )

            return UpdateParameter(ok=True, parameter=ParameterType.from_dict(updated_param) if updated_param else None)

        except Exception as e:
            logger.error(f"Error updating parameter: {e}", exc_info=True)
            return UpdateParameter(ok=False, errors=[str(e)])


class DeleteParameter(graphene.Mutation):
    """Delete a parameter (soft delete by setting is_active = 0)"""

    class Arguments:
        id = Int(required=True, description="参数ID")
        hard_delete = Boolean(default_value=False, description="是否硬删除")

    ok = Boolean(description="操作是否成功")
    message = String(description="操作消息")
    errors = List(String, description="错误信息")

    def mutate(self, info, id: int, hard_delete: bool = False):
        """Execute the mutation"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.core.cache.cache_system import hierarchical_cache  # ⚡ PERF: Phase 1.2 Fix

            # Check if parameter exists
            param = fetch_one_as_dict("SELECT * FROM event_params WHERE id = ?", (id,))
            if not param:
                return DeleteParameter(ok=False, errors=["Parameter not found"])

            event_id = param['event_id']

            if hard_delete:
                # Hard delete
                execute_write("DELETE FROM event_params WHERE id = ?", (id,))
                message = "Parameter deleted permanently"
            else:
                # Soft delete
                execute_write("UPDATE event_params SET is_active = 0 WHERE id = ?", (id,))
                message = "Parameter deactivated"

            # Get event for cache invalidation
            event = fetch_one_as_dict("SELECT game_gid FROM log_events WHERE id = ?", (event_id,))
            game_gid = event['game_gid'] if event else None

            # ⚡ PERF: Phase 1.2 Fix - Correct cache invalidation
            try:
                hierarchical_cache.delete("dashboard_statistics")
                logger.info(f"✅ 已失效缓存: dashboard_statistics (参数删除)")
            except Exception as e:
                logger.warning(f"⚠️ 失效dashboard_statistics失败: {e}")

            try:
                hierarchical_cache.delete(f"parameters:{event_id}")
                hierarchical_cache.delete(f"parameter:{id}")
                if game_gid:
                    hierarchical_cache.delete(f"events:{game_gid}")
                logger.info(f"✅ 已失效缓存: parameters:{event_id}, parameter:{id}")
            except Exception as e:
                logger.warning(f"⚠️ 失效parameters/parameter缓存失败: {e}")

            logger.info(f"Parameter deleted via GraphQL: ID {id} (hard_delete={hard_delete})")

            return DeleteParameter(ok=True, message=message)

        except Exception as e:
            logger.error(f"Error deleting parameter: {e}", exc_info=True)
            return DeleteParameter(ok=False, errors=[str(e)])


class ParameterMutations:
    """Container for parameter mutations"""
    CreateParameter = CreateParameter
    UpdateParameter = UpdateParameter
    DeleteParameter = DeleteParameter
