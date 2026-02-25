#!/usr/bin/env python3
"""
创建测试参数数据

为测试事件创建参数字段，用于测试 WHERE 构建器的参数字段选择功能
"""

import sys
import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "data" / "dwd_generator.db"

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def create_test_params():
    """创建测试参数数据"""

    # 定义测试参数
    test_params = {
        1965: [  # zm_pvp_watch_initial_score (观看初始分数界面)
            {'param_name': 'serverName', 'param_name_cn': '服务器名称', 'template_id': 1, 'param_description': '玩家所在服务器'},
            {'param_name': 'roleName', 'param_name_cn': '角色名称', 'template_id': 1, 'param_description': '玩家角色名'},
            {'param_name': 'score', 'param_name_cn': '分数', 'template_id': 2, 'param_description': '观战分数'},
            {'param_name': 'rank', 'param_name_cn': '排名', 'template_id': 2, 'param_description': '当前排名'},
        ],
        1966: [  # zm_pvp_claim_reward (领取观战奖励)
            {'param_name': 'serverName', 'param_name_cn': '服务器名称', 'template_id': 1, 'param_description': '玩家所在服务器'},
            {'param_name': 'rewardId', 'param_name_cn': '奖励ID', 'template_id': 2, 'param_description': '领取的奖励ID'},
            {'param_name': 'rewardCount', 'param_name_cn': '奖励数量', 'template_id': 2, 'param_description': '奖励数量'},
        ],
        1967: [  # login (登录)
            {'param_name': 'serverName', 'param_name_cn': '服务器名称', 'template_id': 1, 'param_description': '登录服务器'},
            {'param_name': 'deviceId', 'param_name_cn': '设备ID', 'template_id': 1, 'param_description': '设备唯一标识'},
            {'param_name': 'ip', 'param_name_cn': 'IP地址', 'template_id': 1, 'param_description': '客户端IP地址'},
            {'param_name': 'loginTime', 'param_name_cn': '登录时间', 'template_id': 3, 'param_description': '登录时间戳'},
        ],
    }

    try:
        total_created = 0

        for event_id, params in test_params.items():
            logger.info(f"\n为事件 ID {event_id} 创建参数...")

            for param_data in params:
                # 检查参数是否已存在
                conn = sqlite3.connect(str(DB_PATH))
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id FROM event_params WHERE event_id = ? AND param_name = ?",
                    (event_id, param_data['param_name'])
                )
                existing = cursor.fetchone()
                conn.close()

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

        # 验证创建的参数
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT le.event_name_cn, COUNT(ep.id) as param_count
            FROM log_events le
            LEFT JOIN event_params ep ON le.id = ep.event_id
            WHERE le.game_gid = 10000147
            GROUP BY le.id, le.event_name_cn
            ORDER BY le.id
        """)

        logger.info("\n✅ 测试参数创建完成！")
        logger.info("\n事件参数统计:")

        for row in cursor.fetchall():
            logger.info(f"  - {row['event_name_cn']}: {row['param_count']} 个参数")

        conn.close()

        return True

    except Exception as e:
        logger.error(f"❌ 创建测试参数失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = create_test_params()
    sys.exit(0 if success else 1)
