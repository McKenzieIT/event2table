#!/usr/bin/env python3
"""
清理数据库中无效的测试游戏数据

问题：数据库中存在不符合 GameEntity 验证规则的测试数据：
- gid 为字符串而不是整数
- ods_db 不是 'ieu_ods' 或 'overseas_ods'

解决方案：删除这些无效数据
"""

import sys
import os

# 导入必要的模块（使用完整路径）
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from backend.core.config.config import get_db_path
from backend.core.database.converters import get_db_connection

def cleanup_invalid_games():
    """清理无效的游戏数据"""

    db_path = get_db_path()
    print(f"📂 使用数据库: {db_path}")

    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # 查找无效数据
    print("\n🔍 查找无效游戏数据...")

    # 查找 gid 不是整数的游戏
    cursor.execute("""
        SELECT id, gid, name, ods_db
        FROM games
        WHERE NOT CAST(gid AS INTEGER) = gid
        OR ods_db NOT IN ('ieu_ods', 'overseas_ods')
    """)

    invalid_games = cursor.fetchall()

    if not invalid_games:
        print("✅ 没有找到无效数据")
        return

    print(f"\n❌ 找到 {len(invalid_games)} 条无效数据:")
    for game in invalid_games:
        print(f"  - ID: {game[0]}, GID: {game[1]}, Name: {game[2]}, ODS_DB: {game[3]}")

    # 删除无效数据
    print(f"\n🗑️  删除无效数据...")

    invalid_ids = [str(game[0]) for game in invalid_games]
    placeholders = ",".join(["?" for _ in invalid_ids])

    cursor.execute(f"DELETE FROM games WHERE id IN ({placeholders})", invalid_ids)
    conn.commit()

    deleted_count = cursor.rowcount
    print(f"✅ 成功删除 {deleted_count} 条无效数据")

    # 验证清理后的数据
    cursor.execute("SELECT COUNT(*) FROM games")
    total_games = cursor.fetchone()[0]
    print(f"📊 剩余游戏数量: {total_games}")

    conn.close()

if __name__ == "__main__":
    cleanup_invalid_games()
