#!/usr/bin/env python3
"""
创建 role.online 事件

为 game_gid=10000147 创建 role.online 事件及其参数
"""

import sys
import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "data" / "dwd_generator.db"

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_one_as_dict(query, params=()):
    """Execute query and return single row as dict"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def fetch_all_as_dict(query, params=()):
    """Execute query and return all rows as list of dicts"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def execute_write(query, params=(), return_last_id=False):
    """Execute write query and optionally return last insert id"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        if return_last_id:
            return cursor.lastrowid
        return cursor.rowcount
    finally:
        conn.close()

def create_role_online_event():
    """创建 role.online 事件"""

    # 检查游戏是否存在
    game = fetch_one_as_dict(
        "SELECT id, gid, name, ods_db FROM games WHERE gid = 10000147"
    )

    if not game:
        logger.error("游戏 gid=10000147 不存在！")
        return False

    game_id = game['id']
    game_gid = game['gid']
    ods_db = game['ods_db']

    logger.info(f"找到游戏: {game['name']} (gid={game_gid}, ods_db={ods_db})")

    # 检查 role.online 事件是否已存在
    existing = fetch_one_as_dict(
        "SELECT id FROM log_events WHERE game_gid = ? AND event_name = ?",
        (game_gid, 'role.online')
    )

    if existing:
        logger.info(f"事件 role.online 已存在，ID: {existing['id']}")
        event_id = existing['id']
    else:
        # 创建 role.online 事件
        event_id = execute_write(
            """INSERT INTO log_events
               (game_id, game_gid, event_name, event_name_cn, category_id, source_table, target_table, include_in_common_params)
               VALUES (?, ?, ?, ?, ?, ?, ?, 1)""",
            (
                game_id,
                game_gid,
                'role.online',
                '角色上线',
                3,  # 假设分类ID 3 存在
                f'{ods_db}.ods_{game_gid}_all_view',
                f'dwd.v_dwd_{game_gid}_role_online_di',
            ),
            return_last_id=True,
        )

        logger.info(f"✅ 创建事件: role.online (角色上线) - ID: {event_id}")

    # 定义参数
    test_params = [
        {'param_name': 'serverId', 'param_name_cn': '服务器ID', 'template_id': 2, 'param_description': '服务器ID'},
        {'param_name': 'serverName', 'param_name_cn': '服务器名称', 'template_id': 1, 'param_description': '服务器名称'},
        {'param_name': 'roleId', 'param_name_cn': '角色ID', 'template_id': 2, 'param_description': '角色ID'},
        {'param_name': 'roleName', 'param_name_cn': '角色名称', 'template_id': 1, 'param_description': '角色名称'},
        {'param_name': 'level', 'param_name_cn': '等级', 'template_id': 2, 'param_description': '角色等级'},
        {'param_name': 'vipLevel', 'param_name_cn': 'VIP等级', 'template_id': 2, 'param_description': 'VIP等级'},
        {'param_name': 'loginTime', 'param_name_cn': '登录时间', 'template_id': 3, 'param_description': '登录时间戳'},
        {'param_name': 'ip', 'param_name_cn': 'IP地址', 'template_id': 1, 'param_description': '客户端IP地址'},
        {'param_name': 'deviceId', 'param_name_cn': '设备ID', 'template_id': 1, 'param_description': '设备唯一标识'},
    ]

    total_created = 0
    for param_data in test_params:
        # 检查参数是否已存在
        existing = fetch_one_as_dict(
            "SELECT id FROM event_params WHERE event_id = ? AND param_name = ?",
            (event_id, param_data['param_name'])
        )

        if existing:
            logger.info(f"  参数已存在: {param_data['param_name_cn']} ({param_data['param_name']})")
            continue

        # 插入新参数
        param_id = execute_write(
            """INSERT INTO event_params
               (event_id, param_name, param_name_cn, template_id, param_description, is_active, version)
               VALUES (?, ?, ?, ?, ?, 1, 1)""",
            (
                event_id,
                param_data['param_name'],
                param_data['param_name_cn'],
                param_data['template_id'],
                param_data['param_description'],
            ),
            return_last_id=True,
        )

        logger.info(f"  ✅ 创建参数: {param_data['param_name_cn']} ({param_data['param_name']}) - ID: {param_id}")
        total_created += 1

    logger.info(f"\n✅ role.online 事件创建完成！共创建 {total_created} 个参数")

    # 验证所有事件
    all_events = fetch_all_as_dict(
        "SELECT id, event_name, event_name_cn FROM log_events WHERE game_gid = ? ORDER BY id",
        (game_gid,)
    )

    logger.info(f"\n游戏 {game['name']} 的所有事件:")
    for event in all_events:
        logger.info(f"  - ID {event['id']}: {event['event_name_cn']} ({event['event_name']})")

    return True

if __name__ == '__main__':
    success = create_role_online_event()
    sys.exit(0 if success else 1)
