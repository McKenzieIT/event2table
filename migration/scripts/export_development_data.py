#!/usr/bin/env python3
"""导出开发数据库数据"""
import sqlite3
import json
import sys
from pathlib import Path

def export_development_data(db_path: str, output_file: str):
    """导出开发环境数据（测试游戏和事件）"""
    if not Path(db_path).exists():
        print(f"⚠️  开发数据库不存在: {db_path}")
        print("   将跳过开发数据导出")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 导出测试游戏和事件
    data = {
        'games': cursor.execute("SELECT * FROM games WHERE name LIKE '%测试%' OR name LIKE '%test%'").fetchall(),
        'events': cursor.execute("""
            SELECT le.* FROM log_events le
            INNER JOIN games g ON le.game_gid = g.gid
            WHERE g.name LIKE '%测试%' OR g.name LIKE '%test%'
        """).fetchall(),
        'parameters': cursor.execute("""
            SELECT ep.* FROM event_params ep
            INNER JOIN log_events le ON ep.event_id = le.id
            INNER JOIN games g ON le.game_gid = g.gid
            WHERE g.name LIKE '%测试%' OR g.name LIKE '%test%' AND ep.is_active = 1
        """).fetchall(),
    }

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2, default=str)

    conn.close()
    print(f"✅ Development data exported to {output_file}")
    return True

if __name__ == '__main__':
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'dwd_generator_dev.db'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'migration/development_data.json'
    export_development_data(db_path, output_file)
