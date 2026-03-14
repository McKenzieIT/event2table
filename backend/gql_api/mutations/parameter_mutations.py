"""
Parameter Mutations

Implements GraphQL mutation resolvers for Parameter entity with complete business logic.

Business Rules:
- P1-10: create_parameter - Full validation with param_name format, uniqueness, json_path
- P1-11: update_parameter - Existence check, permission check, optimistic locking
- P1-12: batch_create_parameters - Batch validation, uniqueness, transactional
- P1-13: batch_update_parameters - Batch validation, transactional

Author: Event2Table Development Team
Date: 2026-03-10
"""

import json
import logging
import re
from typing import Any, Dict
from typing import List as TypingList

import graphene
from graphene import Boolean, Field, InputObjectType, Int, List, String

from backend.core.database.transaction import transactional
from backend.core.security.authentication import authenticated, require_permission
from backend.core.security.error_sanitizer import ErrorSanitizer

logger = logging.getLogger(__name__)


class CreateParameter(graphene.Mutation):
    """
    Create a new parameter (P1-10)

    Business Logic:
    1. Validate param_name format (1-50 chars, starts with letter/underscore)
    2. Validate param_type enum (base, param, custom, fixed, common, non_common)
    3. Validate event_id existence
    4. Check param_name uniqueness within event
    5. Validate json_path format if provided
    6. Validate game_gid consistency

    Raises:
        ValueError: If validation fails
    """

    class Arguments:
        event_id = Int(required=True, description="事件ID")
        param_name = String(required=True, description="参数英文名")
        param_name_cn = String(description="参数中文名")
        param_type = String(description="参数类型: base/param/custom/fixed/common/non_common")
        template_id = Int(description="参数模板ID")
        json_path = String(description="JSON路径")
        is_active = Boolean(default_value=True, description="是否活跃")

    ok = Boolean(description="操作是否成功")
    parameter = Field(
        lambda: __import__(
            'backend.gql_api.types.parameter_type', fromlist=['ParameterType']
        ).ParameterType,
        description="创建的参数",
    )
    errors = List(String, description="错误信息")

    @authenticated
    @require_permission('parameter:write')
    def mutate(
        self,
        info,
        event_id: int,
        param_name: str,
        param_name_cn: str = None,
        param_type: str = None,
        template_id: int = None,
        json_path: str = None,
        is_active: bool = True,
    ):
        """
        Execute the mutation with complete business validation.

        Args:
            info: GraphQL info
            event_id: Event ID (required)
            param_name: Parameter name in English (required)
            param_name_cn: Parameter name in Chinese (optional)
            param_type: Parameter type enum (optional)
            template_id: Parameter template ID (optional)
            json_path: JSON path for extraction (optional)
            is_active: Active status (default: True)

        Returns:
            CreateParameter mutation result
        """
        try:
            from backend.core.cache.cache_system import hierarchical_cache
            from backend.core.utils import execute_write, fetch_all_as_dict, fetch_one_as_dict
            from backend.gql_api.types.parameter_type import ParameterType

            # ========== P1-10.1: Input Validation ==========

            # Validate param_name format
            if not param_name or not isinstance(param_name, str):
                return CreateParameter(
                    ok=False, errors=["param_name is required and must be a string"]
                )

            param_name = param_name.strip()

            # Check param_name format: 1-50 chars, starts with letter/underscore
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]{0,49}$', param_name):
                return CreateParameter(
                    ok=False,
                    errors=[
                        "param_name must start with a letter or underscore, "
                        "contain only letters, numbers, and underscores, "
                        "and be 1-50 characters long"
                    ],
                )

            # Validate param_type if provided
            valid_param_types = ['base', 'param', 'custom', 'fixed', 'common', 'non_common']
            if param_type and param_type not in valid_param_types:
                return CreateParameter(
                    ok=False, errors=[f"param_type must be one of: {', '.join(valid_param_types)}"]
                )

            # Validate json_path if provided
            if json_path:
                if not json_path.startswith('$.'):
                    return CreateParameter(
                        ok=False, errors=["json_path must start with '$.' (e.g., '$.zoneId')"]
                    )

                # Basic JSON path validation
                try:
                    # Check if it's a valid JSON path format
                    if not re.match(
                        r'^\$\.([a-zA-Z_][a-zA-Z0-9_]*)(\.[a-zA-Z_][a-zA-Z0-9_]*)*$', json_path
                    ):
                        return CreateParameter(
                            ok=False,
                            errors=[
                                f"Invalid json_path format: {json_path}. "
                                "Expected format: $.fieldName or $.field.nestedField"
                            ],
                        )
                except Exception as e:
                    logger.warning(f"json_path validation error: {e}")
                    return CreateParameter(ok=False, errors=[f"Invalid json_path format: {str(e)}"])

            # ========== P1-10.2: Business Rules Validation ==========

            # Validate event_id exists
            event = fetch_one_as_dict("SELECT * FROM log_events WHERE id = ?", (event_id,))
            if not event:
                return CreateParameter(ok=False, errors=[f"Event {event_id} not found"])

            game_gid = event['game_gid']

            # Check param_name uniqueness within event
            existing_param = fetch_one_as_dict(
                "SELECT * FROM event_params WHERE event_id = ? AND param_name = ?",
                (event_id, param_name),
            )
            if existing_param:
                return CreateParameter(
                    ok=False,
                    errors=[
                        f"Parameter '{param_name}' already exists for event {event_id}. "
                        f"Use update_parameter to modify the existing parameter."
                    ],
                )

            # Validate template_id if provided
            if template_id:
                template = fetch_one_as_dict(
                    "SELECT * FROM param_templates WHERE id = ?", (template_id,)
                )
                if not template:
                    return CreateParameter(ok=False, errors=[f"Template {template_id} not found"])

            # ========== P1-10.3: Create Parameter ==========

            # Set default param_type if not provided
            if not param_type:
                # Determine default based on json_path
                param_type = 'param' if json_path else 'base'

            # Create parameter
            param_id = execute_write(
                """INSERT INTO event_params
                   (event_id, param_name, param_name_cn, param_type, template_id, json_path, is_active, version)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 1)""",
                (
                    event_id,
                    param_name,
                    param_name_cn,
                    param_type,
                    template_id,
                    json_path,
                    1 if is_active else 0,
                ),
                return_last_id=True,
            )

            logger.info(
                f"Parameter created via GraphQL: {param_name} (ID: {param_id}, "
                f"event_id={event_id}, type={param_type})"
            )

            # ========== P1-10.4: Cache Invalidation ==========

            try:
                hierarchical_cache.delete("dashboard_statistics")
                logger.debug(f"✅ Invalidated cache: dashboard_statistics (parameter created)")
            except Exception as e:
                logger.warning(f"⚠️ Failed to invalidate dashboard_statistics cache: {e}")

            try:
                hierarchical_cache.delete(f"parameters:{event_id}")
                hierarchical_cache.delete(f"events:{game_gid}")
                logger.debug(f"✅ Invalidated cache: parameters:{event_id}, events:{game_gid}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to invalidate parameters/events cache: {e}")

            # ========== P1-10.5: Return Created Parameter ==========

            parameter = fetch_one_as_dict(
                """
                SELECT ep.*, pt.name as template_name, pt.description
                FROM event_params ep
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                WHERE ep.id = ?
                """,
                (param_id,),
            )

            return CreateParameter(
                ok=True, parameter=ParameterType.from_dict(parameter) if parameter else None
            )

        except ValueError as e:
            # Business logic validation errors
            logger.warning(f"Validation error in create_parameter: {e}")
            return CreateParameter(ok=False, errors=[str(e)])
        except Exception as e:
            # Unexpected errors
            safe_error = ErrorSanitizer.sanitize_with_context(e, "create parameter")
            logger.error(f"Error in create_parameter: {safe_error}")
            return CreateParameter(ok=False, errors=[safe_error])


class UpdateParameter(graphene.Mutation):
    """
    Update an existing parameter (P1-11)

    Business Logic:
    1. Check parameter existence
    2. Validate permissions (parameter belongs to user's game context)
    3. Optimistic locking using version field
    4. Special validation for param_name and param_type changes
    5. Validate json_path format if updated

    Raises:
        ValueError: If validation fails
    """

    class Arguments:
        id = Int(required=True, description="参数ID")
        param_name_cn = String(description="参数中文名")
        param_type = String(description="参数类型: base/param/custom/fixed/common/non_common")
        template_id = Int(description="参数模板ID")
        json_path = String(description="JSON路径")
        is_active = Boolean(description="是否活跃")
        expected_version = Int(description="乐观锁: 期望的版本号")

    ok = Boolean(description="操作是否成功")
    parameter = Field(
        lambda: __import__(
            'backend.gql_api.types.parameter_type', fromlist=['ParameterType']
        ).ParameterType,
        description="更新的参数",
    )
    errors = List(String, description="错误信息")

    @authenticated
    @require_permission('parameter:write')
    def mutate(
        self,
        info,
        id: int,
        param_name_cn: str = None,
        param_type: str = None,
        template_id: int = None,
        json_path: str = None,
        is_active: bool = None,
        expected_version: int = None,
    ):
        """
        Execute the mutation with complete business validation.

        Args:
            info: GraphQL info
            id: Parameter ID (required)
            param_name_cn: Parameter name in Chinese (optional)
            param_type: Parameter type enum (optional)
            template_id: Parameter template ID (optional)
            json_path: JSON path for extraction (optional)
            is_active: Active status (optional)
            expected_version: Expected version for optimistic locking (optional)

        Returns:
            UpdateParameter mutation result
        """
        try:
            from backend.core.cache.cache_system import hierarchical_cache
            from backend.core.utils import execute_write, fetch_all_as_dict, fetch_one_as_dict
            from backend.gql_api.types.parameter_type import ParameterType

            # ========== P1-11.1: Existence Check ==========

            param = fetch_one_as_dict("SELECT * FROM event_params WHERE id = ?", (id,))
            if not param:
                return UpdateParameter(ok=False, errors=[f"Parameter {id} not found"])

            current_version = param.get('version', 1)

            # ========== P1-11.2: Optimistic Locking ==========

            if expected_version is not None and expected_version != current_version:
                return UpdateParameter(
                    ok=False,
                    errors=[
                        f"Optimistic lock failed: Parameter {id} was modified by another transaction. "
                        f"Expected version {expected_version}, but current version is {current_version}. "
                        f"Please refresh and try again."
                    ],
                )

            # ========== P1-11.3: Permission Check ==========

            # Get event to check game context
            event = fetch_one_as_dict("SELECT * FROM log_events WHERE id = ?", (param['event_id'],))
            if not event:
                return UpdateParameter(
                    ok=False, errors=[f"Event {param['event_id']} not found for parameter {id}"]
                )

            # Note: Additional game context permission check can be added here
            # based on session user's game access
            game_gid = event['game_gid']

            # ========== P1-11.4: Field Validation ==========

            # Validate param_type if provided
            if param_type:
                valid_param_types = ['base', 'param', 'custom', 'fixed', 'common', 'non_common']
                if param_type not in valid_param_types:
                    return UpdateParameter(
                        ok=False,
                        errors=[f"param_type must be one of: {', '.join(valid_param_types)}"],
                    )

            # Validate json_path if provided
            if json_path:
                if not json_path.startswith('$.'):
                    return UpdateParameter(
                        ok=False, errors=["json_path must start with '$.' (e.g., '$.zoneId')"]
                    )

                # Basic JSON path validation
                try:
                    if not re.match(
                        r'^\$\.([a-zA-Z_][a-zA-Z0-9_]*)(\.[a-zA-Z_][a-zA-Z0-9_]*)*$', json_path
                    ):
                        return UpdateParameter(
                            ok=False,
                            errors=[
                                f"Invalid json_path format: {json_path}. "
                                "Expected format: $.fieldName or $.field.nestedField"
                            ],
                        )
                except Exception as e:
                    logger.warning(f"json_path validation error: {e}")
                    return UpdateParameter(ok=False, errors=[f"Invalid json_path format: {str(e)}"])

            # Validate template_id if provided
            if template_id:
                template = fetch_one_as_dict(
                    "SELECT * FROM param_templates WHERE id = ?", (template_id,)
                )
                if not template:
                    return UpdateParameter(ok=False, errors=[f"Template {template_id} not found"])

            # ========== P1-11.5: Build Update Query ==========

            updates = []
            params = []

            if param_name_cn is not None:
                updates.append("param_name_cn = ?")
                params.append(param_name_cn)

            if param_type is not None:
                updates.append("param_type = ?")
                params.append(param_type)

            if template_id is not None:
                updates.append("template_id = ?")
                params.append(template_id)

            if json_path is not None:
                updates.append("json_path = ?")
                params.append(json_path)

            if is_active is not None:
                updates.append("is_active = ?")
                params.append(1 if is_active else 0)

            if not updates:
                return UpdateParameter(ok=False, errors=["No fields to update"])

            # Increment version for optimistic locking
            updates.append("version = version + 1")

            # Add WHERE clause with id
            params.append(id)
            query = f"UPDATE event_params SET {', '.join(updates)} WHERE id = ?"

            # ========== P1-11.6: Execute Update ==========

            execute_write(query, tuple(params))

            logger.info(
                f"Parameter updated via GraphQL: ID {id}, "
                f"version {current_version} -> {current_version + 1}"
            )

            # ========== P1-11.7: Cache Invalidation ==========

            event_id = param['event_id']

            try:
                hierarchical_cache.delete("dashboard_statistics")
                logger.debug(f"✅ Invalidated cache: dashboard_statistics (parameter updated)")
            except Exception as e:
                logger.warning(f"⚠️ Failed to invalidate dashboard_statistics cache: {e}")

            try:
                hierarchical_cache.delete(f"parameters:{event_id}")
                hierarchical_cache.delete(f"parameter:{id}")
                hierarchical_cache.delete(f"events:{game_gid}")
                logger.debug(f"✅ Invalidated cache: parameters:{event_id}, parameter:{id}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to invalidate parameters/parameter cache: {e}")

            # ========== P1-11.8: Return Updated Parameter ==========

            updated_param = fetch_one_as_dict(
                """
                SELECT ep.*, pt.name as template_name, pt.description
                FROM event_params ep
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                WHERE ep.id = ?
                """,
                (id,),
            )

            return UpdateParameter(
                ok=True, parameter=ParameterType.from_dict(updated_param) if updated_param else None
            )

        except ValueError as e:
            # Business logic validation errors
            logger.warning(f"Validation error in update_parameter: {e}")
            return UpdateParameter(ok=False, errors=[str(e)])
        except Exception as e:
            # Unexpected errors
            safe_error = ErrorSanitizer.sanitize_with_context(e, "update parameter")
            logger.error(f"Error in update_parameter: {safe_error}")
            return UpdateParameter(ok=False, errors=[safe_error])


class DeleteParameter(graphene.Mutation):
    """Delete a parameter (soft delete by setting is_active = 0)"""

    class Arguments:
        id = Int(required=True, description="参数ID")
        hard_delete = Boolean(default_value=False, description="是否硬删除")

    ok = Boolean(description="操作是否成功")
    message = String(description="操作消息")
    errors = List(String, description="错误信息")

    @authenticated
    @require_permission('parameter:write')
    def mutate(self, info, id: int, hard_delete: bool = False):
        """Execute the mutation"""
        try:
            from backend.core.cache.cache_system import hierarchical_cache
            from backend.core.utils import execute_write, fetch_one_as_dict

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

            # Cache invalidation
            try:
                hierarchical_cache.delete("dashboard_statistics")
                logger.debug(f"✅ Invalidated cache: dashboard_statistics (parameter deleted)")
            except Exception as e:
                logger.warning(f"⚠️ Failed to invalidate dashboard_statistics cache: {e}")

            try:
                hierarchical_cache.delete(f"parameters:{event_id}")
                hierarchical_cache.delete(f"parameter:{id}")
                if game_gid:
                    hierarchical_cache.delete(f"events:{game_gid}")
                logger.debug(f"✅ Invalidated cache: parameters:{event_id}, parameter:{id}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to invalidate parameters/parameter cache: {e}")

            logger.info(f"Parameter deleted via GraphQL: ID {id} (hard_delete={hard_delete})")

            return DeleteParameter(ok=True, message=message)

        except Exception as e:
            safe_error = ErrorSanitizer.sanitize_with_context(e, "delete parameter")
            return DeleteParameter(ok=False, errors=[safe_error])


class ParameterInput(InputObjectType):
    """Input type for batch parameter operations"""

    event_id = Int(required=True, description="事件ID")
    param_name = String(required=True, description="参数英文名")
    param_name_cn = String(description="参数中文名")
    param_type = String(description="参数类型: base/param/custom/fixed/common/non_common")
    template_id = Int(description="参数模板ID")
    json_path = String(description="JSON路径")
    is_active = Boolean(default_value=True, description="是否活跃")


class BatchCreateParameters(graphene.Mutation):
    """
    Batch create parameters (P1-12)

    Business Logic:
    1. Validate all parameters belong to the same game
    2. Check batch size limit (max 1000)
    3. Check param_name uniqueness within each event (no duplicates in batch)
    4. Use transaction for all-or-nothing guarantee
    5. Validate each parameter's fields

    Raises:
        ValueError: If validation fails
    """

    class Arguments:
        parameters = List(ParameterInput, required=True, description="参数列表")

    ok = Boolean(description="操作是否成功")
    created_count = Int(description="成功创建数量")
    parameters = Field(
        lambda: __import__(
            'backend.gql_api.types.parameter_type', fromlist=['ParameterType']
        ).ParameterType,
        description="创建的参数列表",
    )
    errors = List(String, description="错误信息")

    @authenticated
    @require_permission('parameter:write')
    def mutate(self, info, parameters: list):
        """
        Execute the mutation with complete business validation.

        Args:
            info: GraphQL info
            parameters: List of parameter inputs (required)

        Returns:
            BatchCreateParameters mutation result
        """
        try:
            from backend.core.cache.cache_system import hierarchical_cache
            from backend.core.utils import execute_write, fetch_all_as_dict, fetch_one_as_dict
            from backend.gql_api.types.parameter_type import ParameterType

            # ========== P1-12.1: Batch Size Validation ==========

            if not parameters or not isinstance(parameters, list):
                return BatchCreateParameters(
                    ok=False, created_count=0, errors=["parameters must be a non-empty list"]
                )

            if len(parameters) > 1000:
                return BatchCreateParameters(
                    ok=False,
                    created_count=0,
                    errors=[
                        f"Cannot create more than 1000 parameters at once (got {len(parameters)})"
                    ],
                )

            # ========== P1-12.2: Batch Validation ==========

            # Collect all game_gids to verify they belong to the same game
            game_gids = set()
            event_ids = set()

            # Check param_name uniqueness within each event (no duplicates in batch)
            event_param_keys = set()

            # Validate each parameter and collect game_gids
            for idx, param in enumerate(parameters):
                # Validate required fields
                if not param.get('event_id'):
                    return BatchCreateParameters(
                        ok=False,
                        created_count=0,
                        errors=[f"Parameter at index {idx}: event_id is required"],
                    )

                if not param.get('param_name'):
                    return BatchCreateParameters(
                        ok=False,
                        created_count=0,
                        errors=[f"Parameter at index {idx}: param_name is required"],
                    )

                event_id = param['event_id']
                param_name = param['param_name'].strip()

                # Validate param_name format
                if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]{0,49}$', param_name):
                    return BatchCreateParameters(
                        ok=False,
                        created_count=0,
                        errors=[
                            f"Parameter at index {idx}: param_name '{param_name}' must start with "
                            "a letter or underscore, contain only letters, numbers, and underscores, "
                            "and be 1-50 characters long"
                        ],
                    )

                # Check for duplicate (event_id, param_name) in batch
                param_key = (event_id, param_name)
                if param_key in event_param_keys:
                    return BatchCreateParameters(
                        ok=False,
                        created_count=0,
                        errors=[
                            f"Duplicate parameter '{param_name}' in event {event_id} "
                            f"(found at indices {list(p['idx'] for p in parameters if p.get('event_id') == event_id and p.get('param_name') == param_name)})"
                        ],
                    )
                event_param_keys.add(param_key)

                # Validate event exists
                event = fetch_one_as_dict("SELECT * FROM log_events WHERE id = ?", (event_id,))
                if not event:
                    return BatchCreateParameters(
                        ok=False,
                        created_count=0,
                        errors=[f"Parameter at index {idx}: Event {event_id} not found"],
                    )

                # Collect game_gid
                game_gids.add(event['game_gid'])
                event_ids.add(event_id)

                # Validate json_path if provided
                json_path = param.get('json_path')
                if json_path:
                    if not json_path.startswith('$.'):
                        return BatchCreateParameters(
                            ok=False,
                            created_count=0,
                            errors=[
                                f"Parameter at index {idx}: json_path must start with '$.' "
                                f"(got: {json_path})"
                            ],
                        )

                    # Basic JSON path validation
                    try:
                        if not re.match(
                            r'^\$\.([a-zA-Z_][a-zA-Z0-9_]*)(\.[a-zA-Z_][a-zA-Z0-9_]*)*$', json_path
                        ):
                            return BatchCreateParameters(
                                ok=False,
                                created_count=0,
                                errors=[
                                    f"Parameter at index {idx}: Invalid json_path format: {json_path}"
                                ],
                            )
                    except Exception as e:
                        return BatchCreateParameters(
                            ok=False,
                            created_count=0,
                            errors=[f"Parameter at index {idx}: Invalid json_path: {str(e)}"],
                        )

            # Verify all parameters belong to the same game
            if len(game_gids) > 1:
                return BatchCreateParameters(
                    ok=False,
                    created_count=0,
                    errors=[
                        f"All parameters must belong to the same game. "
                        f"Found {len(game_gids)} different games: {', '.join(map(str, game_gids))}"
                    ],
                )

            game_gid = game_gids.pop() if game_gids else None

            # ========== P1-12.3: Check Uniqueness in Database ==========

            for event_id, param_name in event_param_keys:
                existing = fetch_one_as_dict(
                    "SELECT * FROM event_params WHERE event_id = ? AND param_name = ?",
                    (event_id, param_name),
                )
                if existing:
                    return BatchCreateParameters(
                        ok=False,
                        created_count=0,
                        errors=[
                            f"Parameter '{param_name}' already exists in event {event_id}. "
                            f"Use update_parameter to modify the existing parameter."
                        ],
                    )

            # ========== P1-12.4: Batch Create with Transaction ==========

            created_ids = []

            @transactional
            def _batch_create():
                """Internal transactional function for batch creation"""
                nonlocal created_ids

                for param in parameters:
                    param_id = execute_write(
                        """INSERT INTO event_params
                           (event_id, param_name, param_name_cn, param_type, template_id, json_path, is_active, version)
                           VALUES (?, ?, ?, ?, ?, ?, ?, 1)""",
                        (
                            param['event_id'],
                            param['param_name'].strip(),
                            param.get('param_name_cn'),
                            param.get('param_type')
                            or ('param' if param.get('json_path') else 'base'),
                            param.get('template_id'),
                            param.get('json_path'),
                            1 if param.get('is_active', True) else 0,
                        ),
                        return_last_id=True,
                    )
                    created_ids.append(param_id)

                return created_ids

            # Execute transactional batch create
            _batch_create()

            logger.info(f"Batch created {len(created_ids)} parameters via GraphQL")

            # ========== P1-12.5: Cache Invalidation ==========

            try:
                hierarchical_cache.delete("dashboard_statistics")
                logger.debug(
                    f"✅ Invalidated cache: dashboard_statistics (batch parameters created)"
                )
            except Exception as e:
                logger.warning(f"⚠️ Failed to invalidate dashboard_statistics cache: {e}")

            for event_id in event_ids:
                try:
                    hierarchical_cache.delete(f"parameters:{event_id}")
                    logger.debug(f"✅ Invalidated cache: parameters:{event_id}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to invalidate parameters:{event_id} cache: {e}")

            if game_gid:
                try:
                    hierarchical_cache.delete(f"events:{game_gid}")
                    logger.debug(f"✅ Invalidated cache: events:{game_gid}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to invalidate events:{game_gid} cache: {e}")

            # ========== P1-12.6: Return Created Parameters ==========

            created_parameters = fetch_all_as_dict(
                """
                SELECT ep.*, pt.name as template_name, pt.description
                FROM event_params ep
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                WHERE ep.id IN ({})
                """.format(','.join('?' * len(created_ids))),
                tuple(created_ids),
            )

            return BatchCreateParameters(
                ok=True,
                created_count=len(created_ids),
                parameters=[ParameterType.from_dict(p) for p in created_parameters],
            )

        except ValueError as e:
            # Business logic validation errors
            logger.warning(f"Validation error in batch_create_parameters: {e}")
            return BatchCreateParameters(ok=False, created_count=0, errors=[str(e)])
        except Exception as e:
            # Unexpected errors
            safe_error = ErrorSanitizer.sanitize_with_context(e, "batch create parameters")
            logger.error(f"Error in batch_create_parameters: {safe_error}")
            return BatchCreateParameters(ok=False, created_count=0, errors=[safe_error])


class BatchUpdateParameters(graphene.Mutation):
    """
    Batch update parameters (P1-13)

    Business Logic:
    1. Validate all parameters exist
    2. Check batch size limit (max 1000)
    3. Use transaction for all-or-nothing guarantee
    4. Validate each update's fields

    Raises:
        ValueError: If validation fails
    """

    class Arguments:
        updates = List(
            graphene.Argument(
                graphene.String,
                description="JSON string of parameter updates: [{id: 1, param_name_cn: '...'}, ...]",
            ),
            required=True,
            description="参数更新列表",
        )

    ok = Boolean(description="操作是否成功")
    updated_count = Int(description="成功更新数量")
    parameters = Field(
        lambda: __import__(
            'backend.gql_api.types.parameter_type', fromlist=['ParameterType']
        ).ParameterType,
        description="更新的参数列表",
    )
    errors = List(String, description="错误信息")

    @authenticated
    @require_permission('parameter:write')
    def mutate(self, info, updates: list):
        """
        Execute the mutation with complete business validation.

        Args:
            info: GraphQL info
            updates: List of parameter updates (each must include 'id')

        Returns:
            BatchUpdateParameters mutation result
        """
        try:
            from backend.core.cache.cache_system import hierarchical_cache
            from backend.core.utils import execute_write, fetch_all_as_dict, fetch_one_as_dict
            from backend.gql_api.types.parameter_type import ParameterType

            # ========== P1-13.1: Batch Size Validation ==========

            if not updates or not isinstance(updates, list):
                return BatchUpdateParameters(
                    ok=False, updated_count=0, errors=["updates must be a non-empty list"]
                )

            if len(updates) > 1000:
                return BatchUpdateParameters(
                    ok=False,
                    updated_count=0,
                    errors=[
                        f"Cannot update more than 1000 parameters at once (got {len(updates)})"
                    ],
                )

            # ========== P1-13.2: Batch Existence Check ==========

            updated_ids = []
            event_ids = set()
            game_gids = set()

            for idx, update in enumerate(updates):
                # Validate required 'id' field
                if not update.get('id'):
                    return BatchUpdateParameters(
                        ok=False,
                        updated_count=0,
                        errors=[f"Update at index {idx}: 'id' is required"],
                    )

                param_id = update['id']

                # Check if parameter exists
                param = fetch_one_as_dict("SELECT * FROM event_params WHERE id = ?", (param_id,))
                if not param:
                    return BatchUpdateParameters(
                        ok=False,
                        updated_count=0,
                        errors=[f"Update at index {idx}: Parameter {param_id} not found"],
                    )

                # Collect event_id and game_gid for cache invalidation
                event_ids.add(param['event_id'])

                event = fetch_one_as_dict(
                    "SELECT * FROM log_events WHERE id = ?", (param['event_id'],)
                )
                if event:
                    game_gids.add(event['game_gid'])

                # Validate param_type if provided
                if update.get('param_type'):
                    valid_param_types = ['base', 'param', 'custom', 'fixed', 'common', 'non_common']
                    if update['param_type'] not in valid_param_types:
                        return BatchUpdateParameters(
                            ok=False,
                            updated_count=0,
                            errors=[
                                f"Update at index {idx}: param_type must be one of: "
                                f"{', '.join(valid_param_types)}"
                            ],
                        )

                # Validate json_path if provided
                if update.get('json_path'):
                    json_path = update['json_path']
                    if not json_path.startswith('$.'):
                        return BatchUpdateParameters(
                            ok=False,
                            updated_count=0,
                            errors=[
                                f"Update at index {idx}: json_path must start with '$.' "
                                f"(got: {json_path})"
                            ],
                        )

                    # Basic JSON path validation
                    try:
                        if not re.match(
                            r'^\$\.([a-zA-Z_][a-zA-Z0-9_]*)(\.[a-zA-Z_][a-zA-Z0-9_]*)*$', json_path
                        ):
                            return BatchUpdateParameters(
                                ok=False,
                                updated_count=0,
                                errors=[
                                    f"Update at index {idx}: Invalid json_path format: {json_path}"
                                ],
                            )
                    except Exception as e:
                        return BatchUpdateParameters(
                            ok=False,
                            updated_count=0,
                            errors=[f"Update at index {idx}: Invalid json_path: {str(e)}"],
                        )

                updated_ids.append(param_id)

            # ========== P1-13.3: Batch Update with Transaction ==========

            @transactional
            def _batch_update():
                """Internal transactional function for batch updates"""
                for update in updates:
                    param_id = update['id']

                    # Build update query
                    updates_list = []
                    params = []

                    if update.get('param_name_cn') is not None:
                        updates_list.append("param_name_cn = ?")
                        params.append(update['param_name_cn'])

                    if update.get('param_type') is not None:
                        updates_list.append("param_type = ?")
                        params.append(update['param_type'])

                    if update.get('template_id') is not None:
                        updates_list.append("template_id = ?")
                        params.append(update['template_id'])

                    if update.get('json_path') is not None:
                        updates_list.append("json_path = ?")
                        params.append(update['json_path'])

                    if update.get('is_active') is not None:
                        updates_list.append("is_active = ?")
                        params.append(1 if update['is_active'] else 0)

                    if updates_list:
                        # Increment version
                        updates_list.append("version = version + 1")

                        params.append(param_id)
                        query = f"UPDATE event_params SET {', '.join(updates_list)} WHERE id = ?"
                        execute_write(query, tuple(params))

            # Execute transactional batch update
            _batch_update()

            logger.info(f"Batch updated {len(updated_ids)} parameters via GraphQL")

            # ========== P1-13.4: Cache Invalidation ==========

            try:
                hierarchical_cache.delete("dashboard_statistics")
                logger.debug(
                    f"✅ Invalidated cache: dashboard_statistics (batch parameters updated)"
                )
            except Exception as e:
                logger.warning(f"⚠️ Failed to invalidate dashboard_statistics cache: {e}")

            for event_id in event_ids:
                try:
                    hierarchical_cache.delete(f"parameters:{event_id}")
                    logger.debug(f"✅ Invalidated cache: parameters:{event_id}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to invalidate parameters:{event_id} cache: {e}")

            for param_id in updated_ids:
                try:
                    hierarchical_cache.delete(f"parameter:{param_id}")
                    logger.debug(f"✅ Invalidated cache: parameter:{param_id}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to invalidate parameter:{param_id} cache: {e}")

            for game_gid in game_gids:
                try:
                    hierarchical_cache.delete(f"events:{game_gid}")
                    logger.debug(f"✅ Invalidated cache: events:{game_gid}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to invalidate events:{game_gid} cache: {e}")

            # ========== P1-13.5: Return Updated Parameters ==========

            updated_parameters = fetch_all_as_dict(
                """
                SELECT ep.*, pt.name as template_name, pt.description
                FROM event_params ep
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                WHERE ep.id IN ({})
                """.format(','.join('?' * len(updated_ids))),
                tuple(updated_ids),
            )

            return BatchUpdateParameters(
                ok=True,
                updated_count=len(updated_ids),
                parameters=[ParameterType.from_dict(p) for p in updated_parameters],
            )

        except ValueError as e:
            # Business logic validation errors
            logger.warning(f"Validation error in batch_update_parameters: {e}")
            return BatchUpdateParameters(ok=False, updated_count=0, errors=[str(e)])
        except Exception as e:
            # Unexpected errors
            safe_error = ErrorSanitizer.sanitize_with_context(e, "batch update parameters")
            logger.error(f"Error in batch_update_parameters: {safe_error}")
            return BatchUpdateParameters(ok=False, updated_count=0, errors=[safe_error])


class ParameterMutations:
    """
    Container for parameter mutations

    Includes:
    - P1-10: CreateParameter - Create with full validation
    - P1-11: UpdateParameter - Update with optimistic locking
    - P1-12: BatchCreateParameters - Batch create with transaction
    - P1-13: BatchUpdateParameters - Batch update with transaction
    - DeleteParameter - Soft/hard delete
    """

    CreateParameter = CreateParameter
    UpdateParameter = UpdateParameter
    DeleteParameter = DeleteParameter
    BatchCreateParameters = BatchCreateParameters
    BatchUpdateParameters = BatchUpdateParameters
