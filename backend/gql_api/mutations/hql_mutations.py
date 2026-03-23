# ⚠️ PERFORMANCE: N+1 query detected - needs refactor
# TODO: Replace loop queries with JOIN or prefetch

# ⚠️ PERFORMANCE: N+1 query - needs JOIN/prefetch refactor
# TODO: Replace loop queries with single JOIN query
# See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

# ⚠️ PERFORMANCE: N+1 query - needs JOIN/prefetch refactor
# ⚠️ PERFORMANCE: N+1 query - needs JOIN/prefetch refactor
"""
HQL Mutations

Implements GraphQL mutation resolvers for HQL generation.
"""

import json
import logging

import graphene
from graphene import Boolean, Field, Int, List, String

from backend.core.cache.cache_system import hierarchical_cache
from backend.core.security.authentication import authenticated, require_permission

logger = logging.getLogger(__name__)


class GenerateHQL(graphene.Mutation):
    """Generate HQL from events"""

    class Arguments:
        event_ids = List(Int, required=True, description="事件ID列表")
        mode = String(default_value="single", description="生成模式: single, union_all, join, where_in")
        options = String(description="JSON格式的选项")

    ok = Boolean(description="操作是否成功")
    hql = String(description="生成的HQL语句")
    errors = List(String, description="错误信息")

    @authenticated
    @require_permission("write")
    def mutate(self, info, event_ids: list, mode: str = "single", options: str = None):
        """
        Execute the mutation

        Business Rules (P1-22):
        1. ✅ Input validation:
           - event_ids cannot be empty
           - mode must be valid: 'single', 'union_all', 'join', 'where_in'
           - options must be valid JSON if provided
        2. ✅ Event validation:
           - All events must exist
           - All events must belong to the same game
        3. ✅ HQL validation:
           - Generated HQL must start with SELECT
           - Generated HQL must end with DI or VIEW
           - No dangerous keywords (DROP, DELETE, TRUNCATE, INSERT, UPDATE)
        4. ✅ Caching: Cache HQL generation results for identical inputs
        """
        try:
            from backend.core.cache.invalidator import cache_invalidator_enhanced
            from backend.core.security.sql_validator import SQLValidator
            from backend.core.utils import execute_write, fetch_all_as_dict, fetch_one_as_dict
            from backend.domain.services.hql_generation_service import HQLGenerationService

            # ========== P1-22: Input Validation ==========

            # 1. Validate event_ids
            if not event_ids:
                return GenerateHQL(ok=False, errors=["事件ID列表不能为空"])

            # 2. Validate mode
            valid_modes = ['single', 'union_all', 'join', 'where_in']
            if mode not in valid_modes:
                return GenerateHQL(
                    ok=False,
                    errors=[f"无效的生成模式: {mode}, 支持的模式: {', '.join(valid_modes)}"],
                )

            # 3. Parse and validate options JSON
            options_dict = {}
            if options:
                try:
                    options_dict = json.loads(options)
                except json.JSONDecodeError as e:
                    return GenerateHQL(ok=False, errors=[f"选项JSON解析失败: {str(e)}"])

            # 4. Cache key for HQL generation result
            import hashlib

            cache_key = f"hql:gen:{mode}:{hashlib.md5(json.dumps({'event_ids': sorted(event_ids), 'options': options_dict}).encode()).hexdigest()}"

            # 5. Try to get from cache
            cached_hql = hierarchical_cache.get(cache_key)
            if cached_hql:
                logger.info(f"✅ HQL cache hit: {cache_key}")
                return GenerateHQL(ok=True, hql=cached_hql)

            # ========== Event Data Validation ==========

            events = []
            game_gid = None

            for event_id in event_ids:
                event = fetch_one_as_dict(
                    """
                    SELECT le.*, g.ods_db, g.name as game_name
                    FROM log_events le
                    JOIN games g ON le.game_gid = g.gid
                    WHERE le.id = ?
                    """,
                    (event_id,),
                )

                if not event:
                    return GenerateHQL(ok=False, errors=[f"事件 {event_id} 不存在"])

                # Validate all events belong to the same game
                if game_gid is None:
                    game_gid = event['game_gid']
                elif event['game_gid'] != game_gid:
                    return GenerateHQL(ok=False, errors=["所有事件必须属于同一游戏"])

                # Get parameters
                params = fetch_all_as_dict(
                    "SELECT * FROM event_params WHERE event_id = ? AND is_active = 1", (event_id,)
                )

                events.append(
                    {
                        'id': event['id'],
                        'event_name': event['event_name'],
                        'game': {
                            'gid': event['game_gid'],
                            'name': event['game_name'],
                            'ods_db': event['ods_db'],
                        },
                        'parameters': params,
                    }
                )

            # ========== Generate HQL ==========
            service = HQLGenerationService()

            if mode == 'single':
                if len(events) != 1:
                    return GenerateHQL(ok=False, errors=["single模式只支持单个事件"])
                hql = service.generate_single_event_hql(events[0], options_dict)
            else:
                hql = service.generate_multi_event_hql(events, mode, options_dict)

            # ========== P1-22: HQL Validation ==========

            try:
                hql_stripped = hql.strip()

                # 1. Basic syntax check: Must start with SELECT
                if not hql_stripped.upper().startswith('SELECT'):
                    raise ValueError("Generated HQL must start with SELECT")

                # 2. Basic syntax check: Must end with DI or VIEW
                if not (
                    hql_stripped.upper().endswith('DI') or hql_stripped.upper().endswith('VIEW')
                ):
                    raise ValueError("Generated HQL must end with DI or VIEW")

                # 3. Check for dangerous keywords
                dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'INSERT', 'UPDATE']
                hql_upper = hql.upper()
                for keyword in dangerous_keywords:
                    if keyword in hql_upper:
                        raise ValueError(f"Generated HQL contains dangerous keyword: {keyword}")

            except ValueError as e:
                logger.error(f"HQL validation failed: {e}")
                return GenerateHQL(ok=False, errors=[f"HQL validation failed: {str(e)}"])

            # Validate events for generation
            is_valid, validation_errors = service.validate_events_for_generation(events)
            if not is_valid:
                logger.warning(f"HQL验证警告: {validation_errors}")

            # ========== Save to history ==========
            try:
                execute_write(
                    """
                    INSERT INTO hql_history (game_gid, event_ids, hql_content, mode, options)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (game_gid, json.dumps(event_ids), hql, mode, options),
                )

                # ⚡ PERF: Phase 1.2 Fix - Invalidate HQL history cache
                try:
                    hierarchical_cache.delete("dashboard_statistics")
                    hierarchical_cache.delete(f"hql_history:{game_gid}")
                    logger.info(f"✅ 已失效缓存: dashboard_statistics, hql_history:{game_gid}")
                except Exception as e:
                    logger.warning(f"⚠️ 失效HQL历史缓存失败: {e}")

            except Exception as e:
                logger.warning(f"保存HQL历史失败: {e}")

            # ========== Cache the result ==========
            try:
                hierarchical_cache.set(cache_key, hql, timeout=3600)
                logger.info(f"✅ Cached HQL generation result: {cache_key}")
            except Exception as e:
                logger.warning(f"Failed to cache HQL result: {e}")

            logger.info(f"HQL generated via GraphQL: mode={mode}, events={len(events)}")

            return GenerateHQL(ok=True, hql=hql)

        except ValueError as e:
            # Business logic validation errors
            logger.warning(f"Validation error generating HQL: {e}")
            return GenerateHQL(ok=False, errors=[str(e)])
        except Exception as e:
            logger.error(f"Error generating HQL: {e}", exc_info=True)
            return GenerateHQL(ok=False, errors=[str(e)])


class SaveHQLTemplate(graphene.Mutation):
    """Save HQL as a template"""

    class Arguments:
        name = String(required=True, description="模板名称")
        content = String(required=True, description="HQL内容")
        category = String(description="模板分类")
        description = String(description="模板描述")

    ok = Boolean(description="操作是否成功")
    template_id = Int(description="模板ID")
    errors = List(String, description="错误信息")

    @authenticated
    @require_permission("write")
    def mutate(self, info, name: str, content: str, category: str = None, description: str = None):
        """
        Execute the mutation

        Business Rules (P1-23):
        1. ✅ Name validation: Cannot be empty
        2. ✅ Content validation: Must be valid HQL
           - Must start with SELECT
           - Must end with DI or VIEW
           - No dangerous keywords
        3. ✅ Uniqueness: Template name must be unique
        """
        try:
            from backend.core.cache.invalidator import cache_invalidator_enhanced
            from backend.core.security.sql_validator import SQLValidator
            from backend.core.utils import execute_write, fetch_one_as_dict

            # ========== P1-23: Input Validation ==========

            # 1. Validate name
            if not name or not name.strip():
                return SaveHQLTemplate(ok=False, errors=["Template name cannot be empty"])

            name = name.strip()

            # 2. Validate content (HQL)
            if not content or not content.strip():
                return SaveHQLTemplate(ok=False, errors=["HQL content cannot be empty"])

            try:
                content_stripped = content.strip()

                # Basic syntax check: Must start with SELECT
                if not content_stripped.upper().startswith('SELECT'):
                    raise ValueError("HQL template must start with SELECT")

                # Basic syntax check: Must end with DI or VIEW
                if not (
                    content_stripped.upper().endswith('DI')
                    or content_stripped.upper().endswith('VIEW')
                ):
                    raise ValueError("HQL template must end with DI or VIEW")

                # Check for dangerous keywords
                dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'INSERT', 'UPDATE']
                content_upper = content.upper()
                for keyword in dangerous_keywords:
                    if keyword in content_upper:
                        raise ValueError(f"HQL template contains dangerous keyword: {keyword}")

            except ValueError as e:
                return SaveHQLTemplate(ok=False, errors=[f"HQL validation failed: {str(e)}"])

            # 3. Check for duplicate name
            existing = fetch_one_as_dict(
                "SELECT * FROM hql_templates WHERE name = ? AND is_active = 1", (name,)
            )

            if existing:
                return SaveHQLTemplate(ok=False, errors=[f"Template name '{name}' already exists"])

            # ========== Create Template ==========
            template_id = execute_write(
                """
                INSERT INTO hql_templates (name, content, category, description)
                VALUES (?, ?, ?, ?)
                """,
                (name, content, category, description),
                return_last_id=True,
            )

            # Invalidate cache
            cache_invalidator_enhanced.invalidate_key('templates.list')

            logger.info(f"HQL template saved via GraphQL: {name} (ID: {template_id})")

            return SaveHQLTemplate(ok=True, template_id=template_id)

        except ValueError as e:
            # Business logic validation errors
            logger.warning(f"Validation error saving HQL template: {e}")
            return SaveHQLTemplate(ok=False, errors=[str(e)])
        except Exception as e:
            logger.error(f"Error saving HQL template: {e}", exc_info=True)
            return SaveHQLTemplate(ok=False, errors=[str(e)])


class DeleteHQLTemplate(graphene.Mutation):
    """Delete an HQL template"""

    class Arguments:
        template_id = Int(required=True, description="模板ID")

    ok = Boolean(description="操作是否成功")
    errors = List(String, description="错误信息")

    @authenticated
    @require_permission("write")
    def mutate(self, info, template_id: int):
        """Execute the mutation"""
        try:
            from backend.core.cache.invalidator import cache_invalidator_enhanced
            from backend.core.utils import execute_write, fetch_one_as_dict

            # 检查模板是否存在
            template = fetch_one_as_dict("SELECT * FROM hql_templates WHERE id = ?", (template_id,))

            if not template:
                return DeleteHQLTemplate(ok=False, errors=["模板不存在"])

            # 软删除
            execute_write("UPDATE hql_templates SET is_active = 0 WHERE id = ?", (template_id,))

            # 失效缓存
            cache_invalidator_enhanced.invalidate_template_related(template_id)

            logger.info(f"HQL template deleted via GraphQL: {template_id}")

            return DeleteHQLTemplate(ok=True)

        except Exception as e:
            logger.error(f"Error deleting HQL template: {e}", exc_info=True)
            return DeleteHQLTemplate(ok=False, errors=[str(e)])


class HQLMutations:
    """Container for HQL mutations"""

    GenerateHQL = GenerateHQL
    SaveHQLTemplate = SaveHQLTemplate
    DeleteHQLTemplate = DeleteHQLTemplate
