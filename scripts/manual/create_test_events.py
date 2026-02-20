#!/usr/bin/env python3
"""
创建测试事件数据

为 game_gid=10000147 创建测试事件，用于开发测试
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging

import sys
import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "data" / "dwd_generator.db"

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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_events():
    """创建测试事件数据"""

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

    # 定义测试事件
    test_events = [
        {
            'event_name': 'zm_pvp_watch_initial_score',
            'event_name_cn': '观看初始分数界面',
            'category_id': 1,  # 假设分类ID 1 存在
            'source_table': f'{ods_db}.ods_{game_gid}_all_view',
            'target_table': f'dwd.v_dwd_{game_gid}_zm_pvp_watch_initial_score_di',
        },
        {
            'event_name': 'zm_pvp_claim_reward',
            'event_name_cn': '领取观战奖励',
            'category_id': 1,
            'source_table': f'{ods_db}.ods_{game_gid}_all_view',
            'target_table': f'dwd.v_dwd_{game_gid}_zm_pvp_claim_reward_di',
        },
        {
            'event_name': 'login',
            'event_name_cn': '登录',
            'category_id': 2,
            'source_table': f'{ods_db}.ods_{game_gid}_all_view',
            'target_table': f'dwd.v_dwd_{game_gid}_login_di',
        },
    ]

    try:
        # 创建事件
        for event_data in test_events:
            # 检查事件是否已存在
            existing = fetch_one_as_dict(
                "SELECT id FROM log_events WHERE game_gid = ? AND event_name = ?",
                (game_gid, event_data['event_name'])
            )

            if existing:
                logger.info(f"事件已存在: {event_data['event_name_cn']} ({event_data['event_name']})")
                continue

            # 插入新事件
            event_id = execute_write(
                """INSERT INTO log_events
                   (game_id, game_gid, event_name, event_name_cn, category_id, source_table, target_table, include_in_common_params)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 1)""",
                (
                    game_id,
                    game_gid,
                    event_data['event_name'],
                    event_data['event_name_cn'],
                    event_data['category_id'],
                    event_data['source_table'],
                    event_data['target_table'],
                ),
                return_last_id=True,
            )

            logger.info(f"✅ 创建事件: {event_data['event_name_cn']} ({event_data['event_name']}) - ID: {event_id}")

        # 验证创建的事件
        events = fetch_one_as_dict(
            "SELECT COUNT(*) as count FROM log_events WHERE game_gid = ?",
            (game_gid,)
        )

        logger.info(f"\n✅ 测试事件创建完成！游戏 {game['name']} 现在有 {events['count']} 个事件")

        # 显示事件列表
        all_events = fetch_one_as_dict(
            "SELECT id, event_name, event_name_cn FROM log_events WHERE game_gid = ? ORDER BY id",
            (game_gid,)
        )

        # Convert to list if it's a single row
        if isinstance(all_events, dict):
            all_events = [all_events]
        elif not isinstance(all_events, list):
            # If fetch_one_as_dict returned something unexpected, fetch with fetch_all
            from backend.core.database.converters import fetch_all_as_dict
            all_events = fetch_all_as_dict(
                "SELECT id, event_name, event_name_cn FROM log_events WHERE game_gid = ? ORDER BY id",
                (game_gid,)
            )

        logger.info("\n事件列表:")
        for event in all_events:
            logger.info(f"  - ID {event['id']}: {event['event_name_cn']} ({event['event_name']})")

        return True

    except Exception as e:
        logger.error(f"❌ 创建测试事件失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = create_test_events()
    sys.exit(0 if success else 1)
