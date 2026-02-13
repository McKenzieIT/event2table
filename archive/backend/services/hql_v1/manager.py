#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HQL Manager Module
Manages HQL statement generation, storage, and retrieval with REPLACE logic support
"""

import sqlite3
from datetime import datetime
from contextlib import contextmanager
from typing import Dict, List, Any, Optional
from functools import lru_cache
from backend.core.database import get_db
from backend.core.config import HQLConfig
from backend.core.logging import get_logger

logger = get_logger(__name__)


# Cached function for event info retrieval
@lru_cache(maxsize=128)
def get_event_info_cached(event_id: int) -> Optional[Dict[str, Any]]:
    """Get event and game info with caching (LRU cache)

    Args:
        event_id: Event ID

    Returns:
        Event info dict or None
    """
    from backend.core.utils import fetch_one_as_dict
    return fetch_one_as_dict('''
        SELECT e.id, e.event_name, e.event_name_cn, g.name, g.gid
        FROM log_events e
        JOIN games g ON e.game_gid = g.gid
        WHERE e.id = ?
    ''', (event_id,))


class HQLManager:
    """HQL Manager class for handling HQL generation and management"""

    HQL_TYPES = HQLConfig.HQL_TYPES

    def __init__(self):
        """Initialize HQL Manager"""
        pass

    def generate_field_definitions(self, event: Dict[str, Any], parameters: List[Dict[str, Any]]) -> str:
        """Generate field definitions for CREATE VIEW HQL

        根据日志文件格式规范，HQL字段应包含：
        - ds, role_id, account_id, utdid, tm, ts (基础字段)
        - envinfo (用户环境信息，保留JSON格式)
        - params中解析的参数字段
        """
        fields = []

        # 基础字段 - 根据日志文件格式规范
        base_fields = [
            {'name': 'ds', 'type': 'string', 'comment': '分区标识'},
            {'name': 'role_id', 'type': 'string', 'comment': '角色ID'},
            {'name': 'account_id', 'type': 'string', 'comment': '账号ID'},
            {'name': 'utdid', 'type': 'string', 'comment': '设备ID'},
            {'name': 'envinfo', 'type': 'string', 'comment': '上报用户信息参数(JSON格式)'},
            {'name': 'tm', 'type': 'string', 'comment': '上报时间(yyyy-mm-dd)'},
            {'name': 'ts', 'type': 'bigint', 'comment': '上报时间戳'}
        ]

        for field in base_fields:
            fields.append(f"    {field['name']} {field['type']} COMMENT '{field['comment']}'")

        # 添加从params中解析的参数字段
        for param in parameters:
            param_name_cn = param.get('param_name_cn', '')
            # 使用get_json_object从params中提取字段
            fields.append(f"    get_json_object(params, '$.{param['param_name']}') AS {param['param_name']} COMMENT '{param_name_cn}'")

        return ',\n'.join(fields)

    def generate_create_view_hql(self, event: Dict[str, Any],
                                  parameters: List[Dict[str, Any]],
                                  game: Dict[str, Any]) -> str:
        """Generate CREATE OR REPLACE VIEW HQL for DWD layer"""
        source_table = event['source_table']
        target_table = event['target_table']
        event_name = event['event_name']
        event_name_cn = event['event_name_cn']

        hql = f"""-- ========================================
-- DWD Layer View: {event_name_cn} ({event_name})
-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- Game: {game['name']} ({game['gid']})
-- ========================================

CREATE OR REPLACE VIEW {target_table} AS
SELECT
{self.generate_field_definitions(event, parameters)}
FROM {source_table}
WHERE ds = '${{ds}}';

-- ========================================
-- 说明
-- 1. 本视图基于ODS层数据创建，使用CREATE OR REPLACE VIEW语法
-- 2. 当事件参数发生变更时，重新执行此HQL即可自动更新视图
-- 3. 如需添加新字段，修改此HQL后重新执行即可
-- ========================================
"""
        return hql

    def generate_alter_table_hql(self, target_table: str, param_name: str,
                                  param_type: str, param_name_cn: str) -> str:
        """Generate ALTER TABLE HQL for adding new field"""
        hql = f"""-- ========================================
-- ALTER TABLE Statement
-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- ========================================

-- 为 {target_table} 表添加新字段
ALTER TABLE {target_table} ADD COLUMN IF NOT EXISTS {param_name} {param_type} COMMENT '{param_name_cn}';

-- 添加字段后需要刷新视图
-- DROP VIEW IF EXISTS {target_table};
-- CREATE VIEW {target_table} AS SELECT * FROM {target_table};

-- ========================================
"""
        return hql

    def save_hql_to_database(self, event_id: int, hql_type: str, hql_content: str) -> None:
        """Save HQL statement to database"""
        from backend.core.utils import fetch_one_as_dict, execute_write

        # Check if HQL already exists
        existing = fetch_one_as_dict('''
            SELECT id, hql_version FROM hql_statements
            WHERE event_id = ? AND hql_type = ?
            ORDER BY hql_version DESC
            LIMIT 1
        ''', (event_id, hql_type))

        if existing:
            execute_write('''
                UPDATE hql_statements
                SET hql_content = ?, hql_version = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (hql_content, existing['hql_version'] + 1, existing['id']))
            logger.info(f"Updated HQL for event_id={event_id}, hql_type={hql_type}, version={existing['hql_version'] + 1}")
        else:
            execute_write('''
                INSERT INTO hql_statements (event_id, hql_type, hql_content, hql_version, is_active, created_at, updated_at)
                VALUES (?, ?, ?, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (event_id, hql_type, hql_content))
            logger.info(f"Saved new HQL for event_id={event_id}, hql_type={hql_type}, version=1")

    def get_hql_statements(self, event_id: Optional[int] = None,
                           game_gid: Optional[int] = None,
                           hql_type: Optional[str] = None,
                           is_active: bool = True) -> List[Dict[str, Any]]:
        """Get HQL statements from database"""
        from backend.core.utils import fetch_all_as_dict, fetch_one_as_dict

        query = 'SELECT * FROM hql_statements WHERE 1=1'
        params = []

        if event_id:
            query += ' AND event_id = ?'
            params.append(event_id)

        if game_gid:
            query += ' AND event_id IN (SELECT id FROM log_events WHERE game_gid = ?)'
            params.append(game_gid)

        if hql_type:
            query += ' AND hql_type = ?'
            params.append(hql_type)

        if not is_active:
            query += ' AND is_active = ?'
            params.append(0)

        results = fetch_all_as_dict(query, tuple(params))

        # Get event and game info using batch loading (avoid N+1 query)
        # Collect all unique event IDs
        event_ids = list(set([r['event_id'] for r in results if r.get('event_id')]))

        # Batch fetch event info using cached function
        events_info = {}
        for event_id in event_ids:
            event_info = get_event_info_cached(event_id)
            if event_info:
                events_info[event_id] = event_info

        # Attach event info to results
        for result in results:
            if result.get('event_id') and result['event_id'] in events_info:
                info = events_info[result['event_id']]
                result['event_name'] = info['event_name']
                result['event_name_cn'] = info['event_name_cn']
                result['game_name'] = info['name']
                result['game_gid'] = info['gid']

        return results

    def get_hql_content(self, hql_id: int) -> Optional[Dict[str, Any]]:
        """Get HQL content by ID"""
        from backend.core.utils import fetch_one_as_dict
        return fetch_one_as_dict('SELECT * FROM hql_statements WHERE id = ?', (hql_id,))

    def deactivate_hql(self, hql_id: int) -> None:
        """Deactivate an HQL statement"""
        from backend.core.utils import execute_write
        execute_write('''
            UPDATE hql_statements
            SET is_active = 0, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (hql_id,))
        logger.info(f"Deactivated HQL statement id={hql_id}")

    def delete_hql(self, hql_id: int) -> None:
        """Delete an HQL statement"""
        from backend.core.utils import execute_write
        execute_write('DELETE FROM hql_statements WHERE id = ?', (hql_id,))
        logger.info(f"Deleted HQL statement id={hql_id}")

    def generate_all_for_event(self, event_id: int) -> Dict[str, Any]:
        """Generate all HQL types for an event and save to database"""
        from backend.core.utils import fetch_one_as_dict, fetch_all_as_dict

        # Get event data with game information
        event_data = fetch_one_as_dict('''
            SELECT e.*, g.name as game_name, g.gid, g.ods_db
            FROM log_events e
            JOIN games g ON e.game_gid = g.gid
            WHERE e.id = ?
        ''', (event_id,))

        if not event_data:
            raise ValueError(f"Event not found: {event_id}")

        # Get parameters
        parameters = fetch_all_as_dict('''
            SELECT * FROM event_params
            WHERE event_id = ? AND is_active = 1
            ORDER BY id
        ''', (event_id,))

        # Build game dict from event_data
        game_info = {
            'name': event_data['game_name'],
            'gid': event_data['gid'],
            'ods_db': event_data['ods_db']
        }

        # Convert to dict format
        event = {
            'id': event_data['id'],
            'game_gid': event_data['game_gid'],
            'event_name': event_data['event_name'],
            'event_name_cn': event_data['event_name_cn'],
            'category_id': event_data['category_id'],
            'source_table': event_data['source_table'],
            'target_table': event_data['target_table']
        }

        # Generate and save CREATE HQL
        create_hql = self.generate_create_view_hql(event, parameters, game_info)
        self.save_hql_to_database(event_id, 'create', create_hql)

        logger.info(f"Generated and saved HQL for event: {event['event_name_cn']} ({event['event_name']})")
        return {
            'create': create_hql,
            'event': event,
            'parameters': parameters
        }

    def update_hql_content(self, hql_id: int, new_content: str,
                           edit_notes: str = None) -> bool:
        """更新HQL内容并标记为用户编辑"""
        from backend.core.utils import fetch_one_as_dict, execute_write

        current = fetch_one_as_dict('SELECT hql_content, is_user_edited FROM hql_statements WHERE id = ?', (hql_id,))

        if not current:
            logger.error(f"HQL not found: {hql_id}")
            return False

        # 如果是首次编辑，保存原始内容
        if not current['is_user_edited']:
            execute_write('''
                UPDATE hql_statements
                SET original_content = ?, is_user_edited = 1
                WHERE id = ?
            ''', (current['hql_content'], hql_id))

        # 更新内容
        execute_write('''
            UPDATE hql_statements
            SET hql_content = ?, edit_notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (new_content, edit_notes, hql_id))

        logger.info(f"Updated HQL content: id={hql_id}, notes={edit_notes}")
        return True

    def compare_hql_versions(self, hql_id: int) -> Optional[Dict[str, Any]]:
        """对比当前版本与原始系统生成版本"""
        from backend.core.utils import fetch_one_as_dict

        result = fetch_one_as_dict('SELECT hql_content, original_content, is_user_edited FROM hql_statements WHERE id = ?', (hql_id,))

        if not result:
            return None

        return {
            'current': result['hql_content'],
            'original': result['original_content'] if result['is_user_edited'] else result['hql_content'],
            'is_edited': bool(result['is_user_edited'])
        }


# Singleton instance
hql_manager = HQLManager()
