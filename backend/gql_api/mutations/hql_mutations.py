"""
HQL Mutations

Implements GraphQL mutation resolvers for HQL generation.
"""

import graphene
from graphene import Field, Int, String, Boolean, List
import logging
import json

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

    def mutate(self, info, event_ids: list, mode: str = "single", options: str = None):
        """Execute the mutation"""
        try:
            from backend.domain.services.hql_generation_service import HQLGenerationService
            from backend.core.cache.invalidator import cache_invalidator_enhanced
            from backend.core.utils import fetch_one_as_dict, fetch_all_as_dict, execute_write
            
            # 验证参数
            if not event_ids:
                return GenerateHQL(ok=False, errors=["事件ID列表不能为空"])
            
            valid_modes = ['single', 'union_all', 'join', 'where_in']
            if mode not in valid_modes:
                return GenerateHQL(ok=False, errors=[f"无效的生成模式: {mode}，支持的模式: {', '.join(valid_modes)}"])
            
            # 解析选项
            options_dict = {}
            if options:
                try:
                    options_dict = json.loads(options)
                except json.JSONDecodeError as e:
                    return GenerateHQL(ok=False, errors=[f"选项JSON解析失败: {str(e)}"])
            
            # 获取事件数据
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
                    (event_id,)
                )
                
                if not event:
                    return GenerateHQL(ok=False, errors=[f"事件 {event_id} 不存在"])
                
                # 验证所有事件属于同一游戏
                if game_gid is None:
                    game_gid = event['game_gid']
                elif event['game_gid'] != game_gid:
                    return GenerateHQL(ok=False, errors=["所有事件必须属于同一游戏"])
                
                # 获取参数
                params = fetch_all_as_dict(
                    "SELECT * FROM event_params WHERE event_id = ? AND is_active = 1",
                    (event_id,)
                )
                
                events.append({
                    'id': event['id'],
                    'event_name': event['event_name'],
                    'game': {
                        'gid': event['game_gid'],
                        'name': event['game_name'],
                        'ods_db': event['ods_db']
                    },
                    'parameters': params
                })
            
            # 生成HQL
            service = HQLGenerationService()
            
            if mode == 'single':
                if len(events) != 1:
                    return GenerateHQL(ok=False, errors=["single模式只支持单个事件"])
                hql = service.generate_single_event_hql(events[0], options_dict)
            else:
                hql = service.generate_multi_event_hql(events, mode, options_dict)
            
            # 验证生成的HQL
            is_valid, validation_errors = service.validate_events_for_generation(events)
            if not is_valid:
                logger.warning(f"HQL验证警告: {validation_errors}")
            
            # 保存到历史记录
            try:
                execute_write(
                    """
                    INSERT INTO hql_history (game_gid, event_ids, hql_content, mode, options)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (game_gid, json.dumps(event_ids), hql, mode, options)
                )
            except Exception as e:
                logger.warning(f"保存HQL历史失败: {e}")
            
            logger.info(f"HQL generated via GraphQL: mode={mode}, events={len(events)}")
            
            return GenerateHQL(ok=True, hql=hql)
            
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

    def mutate(self, info, name: str, content: str, category: str = None, description: str = None):
        """Execute the mutation"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.core.cache.invalidator import cache_invalidator_enhanced
            
            # 创建模板
            template_id = execute_write(
                """
                INSERT INTO hql_templates (name, content, category, description)
                VALUES (?, ?, ?, ?)
                """,
                (name, content, category, description),
                return_last_id=True
            )
            
            # 失效缓存
            cache_invalidator_enhanced.invalidate_key('templates.list')
            
            logger.info(f"HQL template saved via GraphQL: {name}")
            
            return SaveHQLTemplate(ok=True, template_id=template_id)
            
        except Exception as e:
            logger.error(f"Error saving HQL template: {e}", exc_info=True)
            return SaveHQLTemplate(ok=False, errors=[str(e)])


class DeleteHQLTemplate(graphene.Mutation):
    """Delete an HQL template"""

    class Arguments:
        template_id = Int(required=True, description="模板ID")

    ok = Boolean(description="操作是否成功")
    errors = List(String, description="错误信息")

    def mutate(self, info, template_id: int):
        """Execute the mutation"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.core.cache.invalidator import cache_invalidator_enhanced
            
            # 检查模板是否存在
            template = fetch_one_as_dict(
                "SELECT * FROM hql_templates WHERE id = ?",
                (template_id,)
            )
            
            if not template:
                return DeleteHQLTemplate(ok=False, errors=["模板不存在"])
            
            # 软删除
            execute_write(
                "UPDATE hql_templates SET is_active = 0 WHERE id = ?",
                (template_id,)
            )
            
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
