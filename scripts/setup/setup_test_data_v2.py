#!/usr/bin/env python3
"""
设置测试数据 - 使用attach方法

从开发数据库复制必要的测试数据到测试数据库
"""

import sqlite3
import sys
from pathlib import Path

# 数据库路径
DEV_DB = Path(__file__).parent / "dwd_generator.db"
TEST_DB = Path(__file__).parent / "tests" / "test_database.db"

def setup_test_data():
    """设置测试数据"""
    print(f"开发数据库: {DEV_DB}")
    print(f"测试数据库: {TEST_DB}")

    # 连接测试数据库
    test_conn = sqlite3.connect(str(TEST_DB))

    try:
        # Attach开发数据库
        test_conn.execute(f"ATTACH DATABASE '{DEV_DB}' AS dev_db")

        # 1. 检查并复制游戏数据
        print("\n1. 检查游戏数据...")
        game = test_conn.execute("SELECT * FROM games WHERE gid = 10000147").fetchone()
        if not game:
            # 从开发数据库复制
            test_conn.execute("""
                INSERT INTO games (id, gid, name, ods_db)
                SELECT 1, gid, name, ods_db
                FROM dev_db.games
                WHERE gid = 10000147
                LIMIT 1
            """)
            test_conn.commit()
            print("  ✅ 复制游戏: gid=10000147")
        else:
            print(f"  ✅ 游戏已存在")

        # 获取游戏ID
        game = test_conn.execute("SELECT id FROM games WHERE gid = 10000147").fetchone()
        game_id = game[0]

        # 2. 创建ID为1和2的测试事件
        print("\n2. 创建测试事件...")

        # 删除已存在的ID 1和2的事件（如果有）
        test_conn.execute("DELETE FROM log_events WHERE id IN (1, 2)")
        test_conn.commit()

        # 从开发数据库复制两条事件并重新编号
        test_conn.execute(f"""
            INSERT INTO log_events (id, game_id, game_gid, event_name, event_name_cn, category_id, source_table, target_table)
            SELECT 1, {game_id}, game_gid, event_name, event_name_cn, category_id, source_table, target_table
            FROM dev_db.log_events
            WHERE game_gid = 10000147
            LIMIT 1
        """)

        test_conn.execute(f"""
            INSERT INTO log_events (id, game_id, game_gid, event_name, event_name_cn, category_id, source_table, target_table)
            SELECT 2, {game_id}, game_gid, event_name, event_name_cn, category_id, source_table, target_table
            FROM dev_db.log_events
            WHERE game_gid = 10000147
            LIMIT 1
            OFFSET 1
        """)

        test_conn.commit()
        print("  ✅ 创建事件: id=1, id=2")

        # 3. 验证数据
        print("\n3. 验证测试数据...")
        count_games = test_conn.execute("SELECT COUNT(*) FROM games").fetchone()[0]
        count_events = test_conn.execute("SELECT COUNT(*) FROM log_events").fetchone()[0]

        print(f"  游戏数量: {count_games}")
        print(f"  事件数量: {count_events}")

        # 显示事件详情
        events = test_conn.execute("SELECT id, event_name, game_gid FROM log_events WHERE id IN (1, 2) ORDER BY id").fetchall()
        print("\n  测试事件:")
        for event in events:
            print(f"    - id={event[0]}, name={event[1]}, game_gid={event[2]}")

        # Detach开发数据库
        test_conn.execute("DETACH DATABASE dev_db")

        print("\n✅ 测试数据设置完成！")
        return True

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        test_conn.close()

if __name__ == '__main__':
    success = setup_test_data()
    sys.exit(0 if success else 1)
