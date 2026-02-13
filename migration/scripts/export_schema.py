#!/usr/bin/env python3
"""导出数据库Schema到SQL文件"""
import sqlite3
import sys
from pathlib import Path

def export_schema(db_path: str, output_file: str):
    """导出数据库表结构到SQL文件"""
    if not Path(db_path).exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()

    with open(output_file, 'w') as f:
        f.write("-- DWD Generator Database Schema\n")
        f.write(f"-- Generated: {Path(db_path).name}\n")
        f.write(f"-- Date: {Path(__file__).stat().st_mtime}\n\n")

        for table in tables:
            table_name = table[0]
            # 获取建表语句
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            create_sql = cursor.fetchone()[0]
            if create_sql:
                f.write(f"{create_sql};\n\n")

    conn.close()
    print(f"✅ Schema exported to {output_file}")
    return True

if __name__ == '__main__':
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'dwd_generator.db'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'migration/schema.sql'
    export_schema(db_path, output_file)
