#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E2E Test Data Setup Script

为E2E测试创建必要的测试数据
- 创建游戏(GID=10000147)
- 创建测试事件(login, register, battle等)
- 创建测试参数(zone_id, level, role_id等)
- 幂等性设计: 可安全重复运行

Usage:
    python3 scripts/test/setup_e2e_test_data.py
    python3 scripts/test/setup_e2e_test_data.py --verbose
    python3 scripts/test/setup_e2e_test_data.py --dry-run
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


def setup_test_data(verbose=False, dry_run=False):
    """
    设置E2E测试数据

    Args:
        verbose: 是否显示详细信息
        dry_run: 是否为试运行模式(不实际写入数据库)
    """
    from backend.models.repositories.games import GameRepository
    from backend.models.repositories.events import EventRepository
    from backend.models.repositories.parameters import ParameterRepository
    from backend.models.entities import GameEntity, EventEntity
    from backend.core.utils.converters import get_db_connection, fetch_one_as_dict

    # 初始化Repository
    game_repo = GameRepository()
    event_repo = EventRepository()
    param_repo = ParameterRepository()

    # 统计信息
    stats = {
        "games_created": 0,
        "games_updated": 0,
        "events_created": 0,
        "events_updated": 0,
        "params_created": 0,
    }

    logger.info("=" * 60)
    logger.info("E2E Test Data Setup")
    logger.info("=" * 60)

    # ========================================
    # 1. 确保游戏STAR001存在
    # ========================================
    logger.info("\n[1/4] Setting up game STAR001 (GID=10000147)...")

    game = game_repo.find_by_gid(10000147)

    if not game:
        # 创建游戏
        game_data = GameEntity(
            gid=10000147,
            name="STAR001",
            ods_db="ieu_ods",  # ✅ 必须是ieu_ods或overseas_ods,不能是test_db
            description="E2E测试游戏",
            dwd_prefix="dwd"
        )

        if dry_run:
            logger.info(f"  [DRY-RUN] Would create game: {game_data.name} (GID={game_data.gid})")
        else:
            # 使用create方法创建游戏
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO games (gid, name, ods_db, description, dwd_prefix, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """, (game_data.gid, game_data.name, game_data.ods_db, game_data.description, game_data.dwd_prefix))
            conn.commit()
            conn.close()

            game = game_repo.find_by_gid(10000147)
            stats["games_created"] += 1
            logger.info(f"  ✓ Created game: {game.name} (GID={game.gid}, ODS_DB={game.ods_db})")
    else:
        # 验证ods_db是否正确
        if game.ods_db not in ["ieu_ods", "overseas_ods"]:
            logger.warning(f"  ⚠ Game has invalid ods_db '{game.ods_db}', updating to 'ieu_ods'...")
            if not dry_run:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE games SET ods_db = ? WHERE gid = ?", ("ieu_ods", game.gid))
                conn.commit()
                conn.close()
                stats["games_updated"] += 1
                logger.info(f"  ✓ Updated game ods_db: {game.gid} → ieu_ods")
        else:
            logger.info(f"  ✓ Game exists: {game.name} (GID={game.gid}, ODS_DB={game.ods_db})")

    # ========================================
    # 2. 创建测试事件
    # ========================================
    logger.info("\n[2/4] Setting up test events...")

    test_events = [
        {
            "event_name": "login",
            "event_name_cn": "登录",
            "category_id": None,  # 将使用默认类别
            "include_in_common_params": 1,
            "parameters": [
                {"param_name": "role_id", "param_name_cn": "角色ID", "param_type": "base"},
                {"param_name": "account_id", "param_name_cn": "账号ID", "param_type": "base"},
                {"param_name": "zone_id", "param_name_cn": "区域ID", "param_type": "base"},
                {"param_name": "level", "param_name_cn": "等级", "param_type": "param", "json_path": "$.level"},
            ]
        },
        {
            "event_name": "register",
            "event_name_cn": "注册",
            "category_id": None,
            "include_in_common_params": 1,
            "parameters": [
                {"param_name": "account_id", "param_name_cn": "账号ID", "param_type": "base"},
                {"param_name": "device_id", "param_name_cn": "设备ID", "param_type": "base"},
                {"param_name": "channel", "param_name_cn": "渠道", "param_type": "param", "json_path": "$.channel"},
            ]
        },
        {
            "event_name": "battle",
            "event_name_cn": "战斗",
            "category_id": None,
            "include_in_common_params": 1,
            "parameters": [
                {"param_name": "role_id", "param_name_cn": "角色ID", "param_type": "base"},
                {"param_name": "battle_id", "param_name_cn": "战斗ID", "param_type": "base"},
                {"param_name": "result", "param_name_cn": "战斗结果", "param_type": "param", "json_path": "$.result"},
                {"param_name": "duration", "param_name_cn": "战斗时长", "param_type": "param", "json_path": "$.duration"},
            ]
        },
        {
            "event_name": "recharge",
            "event_name_cn": "充值",
            "category_id": None,
            "include_in_common_params": 1,
            "parameters": [
                {"param_name": "role_id", "param_name_cn": "角色ID", "param_type": "base"},
                {"param_name": "amount", "param_name_cn": "充值金额", "param_type": "param", "json_path": "$.amount"},
                {"param_name": "currency", "param_name_cn": "货币类型", "param_type": "param", "json_path": "$.currency"},
            ]
        },
    ]

    # 获取或创建默认类别
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM event_categories WHERE name = ?", ("未分类",))
    category_row = cursor.fetchone()

    if not category_row:
        cursor.execute("INSERT INTO event_categories (name) VALUES (?)", ("未分类",))
        conn.commit()
        category_id = cursor.lastrowid
        logger.info(f"  ✓ Created default category: 未分类 (ID={category_id})")
    else:
        category_id = category_row[0]
    conn.close()

    for event_data in test_events:
        # 检查事件是否已存在
        existing = event_repo.find_by_name(event_data["event_name"], 10000147)

        if not existing:
            # 生成表名
            source_table = f"ieu_ods.ods_{10000147}_all_view"
            target_table = f"dwd.v_dwd_{10000147}_{event_data['event_name']}_di"

            if dry_run:
                logger.info(f"  [DRY-RUN] Would create event: {event_data['event_name']}")
                logger.info(f"    Parameters: {len(event_data['parameters'])}")
            else:
                # 创建事件
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO log_events (
                        game_gid, event_name, event_name_cn, category_id,
                        source_table, target_table, include_in_common_params,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                """, (
                    10000147,
                    event_data["event_name"],
                    event_data["event_name_cn"],
                    category_id,
                    source_table,
                    target_table,
                    event_data["include_in_common_params"]
                ))
                event_id = cursor.lastrowid
                conn.commit()
                conn.close()

                # 创建参数
                for param in event_data["parameters"]:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO event_params (
                            event_id, game_gid, param_name, param_name_cn,
                            param_type, json_path, template_id, is_active, version,
                            created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, 1, 1, 1, datetime('now'), datetime('now'))
                    """, (
                        event_id,
                        10000147,
                        param["param_name"],
                        param["param_name_cn"],
                        param["param_type"],
                        param.get("json_path")
                    ))
                    conn.commit()
                    conn.close()
                    stats["params_created"] += 1

                stats["events_created"] += 1
                logger.info(f"  ✓ Created event: {event_data['event_name']} (ID={event_id}, {len(event_data['parameters'])} params)")
        else:
            if verbose:
                logger.info(f"  ✓ Event exists: {event_data['event_name']} (ID={existing.id})")

    # ========================================
    # 3. 验证测试数据
    # ========================================
    logger.info("\n[3/4] Verifying test data...")

    # 验证游戏
    game = game_repo.find_by_gid(10000147)
    if game:
        logger.info(f"  ✓ Game: {game.name} (GID={game.gid}, ODS_DB={game.ods_db})")
    else:
        logger.error("  ✗ Game 10000147 not found!")

    # 验证事件
    expected_events = ["login", "register", "battle", "recharge"]
    for event_name in expected_events:
        event = event_repo.find_by_name(event_name, 10000147)
        if event:
            # 统计参数数量
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM event_params WHERE event_id = ? AND is_active = 1", (event.id,))
            param_count = cursor.fetchone()[0]
            conn.close()

            logger.info(f"  ✓ Event: {event.event_name} ({event.event_name_cn}) - {param_count} params")
        else:
            logger.warning(f"  ✗ Event not found: {event_name}")

    # ========================================
    # 4. 显示统计信息
    # ========================================
    logger.info("\n[4/4] Setup Summary:")
    logger.info("-" * 60)

    if dry_run:
        logger.info("  [DRY-RUN MODE] No data was actually modified")
    else:
        logger.info(f"  Games created: {stats['games_created']}")
        logger.info(f"  Games updated: {stats['games_updated']}")
        logger.info(f"  Events created: {stats['events_created']}")
        logger.info(f"  Parameters created: {stats['params_created']}")

    # 查询实际数据库统计
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM games WHERE gid = 10000147")
    game_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM log_events WHERE game_gid = 10000147")
    event_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM event_params WHERE game_gid = 10000147")
    param_count = cursor.fetchone()[0]

    conn.close()

    logger.info(f"\n  Database state:")
    logger.info(f"    Total games (GID=10000147): {game_count}")
    logger.info(f"    Total events (game_gid=10000147): {event_count}")
    logger.info(f"    Total parameters (game_gid=10000147): {param_count}")

    logger.info("\n" + "=" * 60)
    logger.info("E2E Test Data Setup Complete!")
    logger.info("=" * 60)

    return stats


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Setup E2E test data")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show verbose output")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Dry run mode (don't modify database)")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        setup_test_data(verbose=args.verbose, dry_run=args.dry_run)
        return 0
    except Exception as e:
        logger.error(f"\n❌ Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
