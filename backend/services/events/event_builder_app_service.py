"""
Event Builder App Service

Provides business logic for event node builder operations.
This service handles batch field operations for the event builder canvas.

Author: Event2Table Development Team
Date: 2026-03-08
"""

import logging
from typing import Any, Dict, List

from backend.core.utils import fetch_all_as_dict, fetch_one_as_dict

logger = logging.getLogger(__name__)


class EventBuilderAppService:
    """
    Event Builder Application Service

    Handles batch field operations for event node builder.
    完整实现, 直接查询数据库, 正确分类字段类型.
    """

    def batch_add_fields(self, event_id: int, field_type: str) -> Dict[str, Any]:
        """
        批量添加字段到 Canvas

        Args:
            event_id: 事件ID
            field_type: 字段类型 ('all', 'param', 'non_common', 'common', 'base')

        Returns:
            包含 ok, fields, count 的字典（匹配前端期望格式）
        """
        try:
            # 1. 验证 event_id
            event = fetch_one_as_dict("SELECT * FROM log_events WHERE id = ?", (event_id,))

            if not event:
                return {
                    'ok': False,
                    'fields': [],
                    'count': 0,
                    'message': f'Event not found: {event_id}',
                }

            # 2. 根据 field_type 获取字段
            fields = self._get_fields_by_type(event, field_type)

            logger.info(
                f"Batch add fields: event_id={event_id}, "
                f"field_type={field_type}, count={len(fields)}"
            )

            # 3. 返回前端期望的格式
            return {
                'ok': True,
                'fields': fields,
                'count': len(fields),
                'message': f'成功添加 {len(fields)} 个字段',
            }

        except Exception as e:
            logger.error(f"Error in batch_add_fields: {e}", exc_info=True)
            return {'ok': False, 'fields': [], 'count': 0, 'message': f'批量添加字段失败: {str(e)}'}

    def _get_fields_by_type(self, event: Dict[str, Any], field_type: str) -> List[Dict[str, Any]]:
        """
        根据字段类型获取字段列表

        完整实现, 直接查询数据库, 正确分类字段类型.
        """
        # 基础字段(硬编码)
        base_fields = [
            {'name': 'ds', 'field_type': 'base', 'description': '日期分区', 'json_path': None},
            {'name': 'role_id', 'field_type': 'base', 'description': '角色ID', 'json_path': None},
            {
                'name': 'account_id',
                'field_type': 'base',
                'description': '账号ID',
                'json_path': None,
            },
            {
                'name': 'utdid',
                'field_type': 'base',
                'description': '设备唯一标识',
                'json_path': None,
            },
            {'name': 'envinfo', 'field_type': 'base', 'description': '环境信息', 'json_path': None},
            {
                'name': 'tm',
                'field_type': 'base',
                'description': '时间戳（毫秒）',
                'json_path': None,
            },
            {'name': 'ts', 'field_type': 'base', 'description': '时间戳（秒）', 'json_path': None},
        ]

        # 根据field_type返回对应的字段
        if field_type == 'base':
            return base_fields

        elif field_type == 'common':
            return self._get_common_fields(event)

        elif field_type == 'param':
            return self._get_param_fields(event)

        elif field_type == 'all':
            # 合并所有字段, 去重
            common_fields = self._get_common_fields(event)
            param_fields = self._get_param_fields(event)
            all_fields = base_fields + common_fields + param_fields

            # 去重(按字段名)
            unique_fields = {}
            for field in all_fields:
                name = field['name']
                if name not in unique_fields:
                    unique_fields[name] = field

            return list(unique_fields.values())

        elif field_type == 'non_common':
            # base + param(排除common)
            param_fields = self._get_param_fields(event)
            # 过滤掉公共参数
            param_fields_only = [
                p for p in param_fields if not self._is_common_parameter(p.get('name'))
            ]
            return base_fields + param_fields_only

        else:
            # 默认返回所有字段
            return base_fields + self._get_param_fields(event)

    def _get_common_fields(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取公共参数字段"""
        try:
            # 查询公共参数(include_in_common_params = 1)
            common_params = fetch_all_as_dict(
                """
                SELECT ep.id, ep.param_name, ep.param_name_cn, ep.json_path
                FROM event_params ep
                INNER JOIN log_events le ON ep.event_id = le.id
                WHERE le.game_gid = ?
                  AND ep.include_in_common_params = 1
                  AND ep.is_active = 1
                ORDER BY ep.param_name
                """,
                (event['game_gid'],),
            )

            return [
                {
                    'name': p['param_name'],
                    'field_type': 'common',
                    'description': p.get('param_name_cn', p['param_name']),
                    'json_path': p.get('json_path')
                    or f'$.{p["param_name"]}',  # Auto-generate json_path if None
                }
                for p in common_params
            ]

        except Exception as e:
            logger.error(f"Error getting common fields: {e}", exc_info=True)
            return []

    def _get_param_fields(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取事件特定参数字段"""
        try:
            # 查询事件特定参数
            params = fetch_all_as_dict(
                """
                SELECT ep.id, ep.param_name, ep.param_name_cn, ep.json_path, ep.template_id
                FROM event_params ep
                WHERE ep.event_id = ?
                  AND ep.is_active = 1
                ORDER BY ep.param_name
                """,
                (event['id'],),
            )

            return [
                {
                    'name': p['param_name'],
                    'field_type': 'param',
                    'description': p.get('param_name_cn', p['param_name']),
                    'json_path': p.get('json_path')
                    or f'$.{p["param_name"]}',  # Auto-generate json_path if None
                }
                for p in params
            ]

        except Exception as e:
            logger.error(f"Error getting param fields: {e}", exc_info=True)
            return []

    def _is_common_parameter(self, param_name: str) -> bool:
        """判断参数是否为公共参数"""
        try:
            # 查询参数是否为公共参数
            param = fetch_one_as_dict(
                """
                SELECT ep.include_in_common_params
                FROM event_params ep
                INNER JOIN log_events le ON ep.event_id = le.id
                WHERE ep.param_name = ?
                LIMIT 1
                """,
                (param_name,),
            )
            return param and param.get('include_in_common_params') == 1

        except Exception as e:
            logger.warning(f"Error checking common parameter: {e}")
            return False
