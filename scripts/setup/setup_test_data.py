#!/usr/bin/env python3
"""
设置测试数据 - 简化版本

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

    # 连接两个数据库
    dev_conn = sqlite3.connect(str(DEV_DB))
    test_conn = sqlite3.connect(str(TEST_DB))

    try:
        # 1. 检查并复制游戏数据
        print("\n1. 检查游戏数据...")
        game = test_conn.execute("SELECT * FROM games WHERE gid = 10000147").fetchone()
        if not game:
            # 从开发数据库复制
            dev_game = dev_conn.execute("SELECT * FROM games WHERE gid = 10000147 LIMIT 1").fetchone()
            if dev_game:
                # 使用ID=1
                columns = [k for k in dev_game.keys() if k != 'id']
                placeholders = ', '.join(['?'] * len(columns))
                columns_str = ', '.join(columns)
                values = [dev_game[k] for k in columns]

                test_conn.execute(f"INSERT INTO games (id, {columns_str}) VALUES (1, {placeholders})", values)
                print(f"  ✅ 复制游戏: gid={dev_game['gid']}, name={dev_game['name']}")
                test_conn.commit()
                game = test_conn.execute("SELECT * FROM games WHERE gid = 10000147").fetchone()
            else:
                print("  ❌ 开发数据库中没有找到gid=10000147的游戏")
                return False
        else:
            print(f"  ✅ 游戏已存在: id={game[0]}, gid={game[1]}")

        game_id = game['id']

        # 2. 复制事件数据（使用真实的event结构）
        print("\n2. 复制事件数据...")

        # 从开发数据库获取两条事件记录
        dev_events = dev_conn.execute("SELECT * FROM log_events WHERE game_gid = 10000147 LIMIT 2").fetchall()

        if len(dev_events) < 2:
            print("  ⚠️  开发数据库中事件不足2条，使用现有数据")

        # 创建ID为1和2的事件（通过重新编号现有事件）
        existing_ids = set(e['id'] for e in test_conn.execute("SELECT id FROM log_events").fetchall())

        new_events = []
        target_ids = [1, 2]

        for i, target_id in enumerate(target_ids):
            if target_id not in existing_ids:
                if i < len(dev_events):
                    # 复制开发数据库的事件，修改ID
                    dev_event = dev_events[i]
                    # 排除auto-increment的id列
                    columns = [k for k in dev_event.keys() if k != 'id']
                    placeholders = ', '.join(['?'] * len(columns))
                    columns_str = ', '.join(columns)
                    values = [dev_event[k] for k in columns]
                    # 修改game_id为正确的值
                    if 'game_id' in columns:
                        idx = columns.index('game_id')
                        values[idx] = game_id

                    test_conn.execute(f"INSERT INTO log_events (id, {columns_str}) VALUES ({target_id}, {placeholders})", values)
                    print(f"  ✅ 插入事件: id={target_id}, name={dev_event['event_name']}")
                    new_events.append(target_id)
                else:
                    print(f"  ⚠️  警告: 没有足够的开发数据来创建事件{id}")
                    break

        test_conn.commit()

        # 3. 验证数据
        print("\n3. 验证测试数据...")
        count_games = test_conn.execute("SELECT COUNT(*) as count FROM games").fetchone()['count']
        count_events = test_conn.execute("SELECT COUNT(*) as count FROM log_events").fetchone()['count']

        print(f"  游戏数量: {count_games}")
        print(f"  事件数量: {count_events}")

        # 显示事件详情
        events = test_conn.execute("SELECT id, event_name, game_gid FROM log_events WHERE id IN (1, 2) ORDER BY id").fetchall()
        print("\n  测试事件:")
        for event in events:
            print(f"    - id={event['id']}, name={event['event_name']}, game_gid={event['game_gid']}")

        print("\n✅ 测试数据设置完成！")
        return True

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        dev_conn.close()
        test_conn.close()

if __name__ == '__main__':
    success = setup_test_data()
    sys.exit(0 if success else 1)
