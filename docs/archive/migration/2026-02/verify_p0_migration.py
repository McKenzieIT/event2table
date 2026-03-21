#!/usr/bin/env python3
"""
验证P0表迁移结果

检查项：
1. 表结构是否正确（game_gid存在，game_id不存在）
2. 外键是否有效（game_gid都指向有效的games.gid）
3. 数据完整性（无孤儿记录）
4. 数据量是否正确

Author: Event2Table Development Team
Date: 2026-02-20
"""
import sqlite3
import sys
from pathlib import Path


def check_table_structure(conn, table_name):
    """检查表结构"""
    print(f"\n{'='*60}")
    print(f"Checking table: {table_name}")
    print(f"{'='*60}")

    cursor = conn.cursor()

    # 获取表结构
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_info = cursor.fetchall()
    columns = [col[1] for col in columns_info]

    print(f"\n📋 Table Structure:")
    for col_info in columns_info:
        col_name = col_info[1]
        col_type = col_info[2]
        col_notnull = col_info[3]
        col_pk = col_info[5]

        pk_marker = " 🗝️ PRIMARY KEY" if col_pk else ""
        null_marker = " NOT NULL" if col_notnull and not col_pk else ""
        print(f"  - {col_name}: {col_type}{null_marker}{pk_marker}")

    # 检查game_gid和game_id列
    has_game_gid = 'game_gid' in columns
    has_game_id = 'game_id' in columns

    print(f"\n✅ Migration Status:")
    if has_game_gid and not has_game_id:
        print(f"  ✅ PASS: Table has game_gid column, game_id column removed")
        return True
    elif has_game_gid and has_game_id:
        print(f"  ⚠️  WARN: Both game_gid and game_id columns exist")
        print(f"  ⚠️  ACTION: Manual review required")
        return False
    elif not has_game_gid and has_game_id:
        print(f"  ❌ FAIL: Table still uses game_id, migration not started")
        return False
    else:
        print(f"  ❌ FAIL: Neither game_gid nor game_id found")
        return False


def check_foreign_keys(conn, table_name):
    """检查外键有效性"""
    cursor = conn.cursor()

    print(f"\n🔗 Foreign Key Validation:")

    # 检查无效的外键
    cursor.execute(f"""
        SELECT COUNT(*)
        FROM {table_name}
        WHERE game_gid IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM games
            WHERE games.gid = {table_name}.game_gid
        )
    """)
    invalid_count = cursor.fetchone()[0]

    if invalid_count > 0:
        print(f"  ❌ FAIL: {invalid_count} records have invalid foreign keys")

        # 获取无效的game_gid列表
        cursor.execute(f"""
            SELECT DISTINCT game_gid
            FROM {table_name}
            WHERE game_gid IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM games
                WHERE games.gid = {table_name}.game_gid
            )
        """)
        invalid_gids = [row[0] for row in cursor.fetchall()]
        print(f"  Invalid game_gids: {invalid_gids}")

        return False
    else:
        print(f"  ✅ PASS: All foreign keys are valid")
        return True


def check_data_integrity(conn, table_name):
    """检查数据完整性"""
    cursor = conn.cursor()

    print(f"\n📊 Data Integrity:")

    # 检查数据量
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    total_count = cursor.fetchone()[0]
    print(f"  Total records: {total_count}")

    # 检查NULL game_gid
    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE game_gid IS NULL")
    null_count = cursor.fetchone()[0]

    if null_count > 0:
        print(f"  ❌ FAIL: {null_count} records have NULL game_gid")
        return False
    else:
        print(f"  ✅ PASS: No NULL game_gid values")

    # 检查game_gid分布
    cursor.execute(f"""
        SELECT
            game_gid,
            COUNT(*) as count,
            MIN(created_at) as first_created,
            MAX(created_at) as last_created
        FROM {table_name}
        GROUP BY game_gid
        ORDER BY count DESC
    """)
    gid_dist = cursor.fetchall()

    print(f"\n  Game GID Distribution:")
    for game_gid, count, first_created, last_created in gid_dist:
        print(f"    - game_gid={game_gid}: {count} records")
        print(f"      Created: {first_created} to {last_created}")

    return True


def check_indexes(conn, table_name):
    """检查索引"""
    cursor = conn.cursor()

    print(f"\n📇 Indexes:")

    cursor.execute(f"""
        SELECT name, sql
        FROM sqlite_master
        WHERE type='index'
        AND tbl_name='{table_name}'
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    indexes = cursor.fetchall()

    if indexes:
        for idx_name, idx_sql in indexes:
            print(f"  - {idx_name}")
            if idx_sql:
                print(f"    {idx_sql}")
    else:
        print(f"  ℹ️  No custom indexes found")

    return True


def verify_migration():
    """验证迁移结果"""
    print("="*60)
    print("P0 Migration Verification")
    print("="*60)

    DB_PATH = "data/dwd_generator.db"

    if not Path(DB_PATH).exists():
        print(f"❌ Database not found: {DB_PATH}")
        return False

    conn = sqlite3.connect(DB_PATH)

    try:
        p0_tables = ['common_params', 'parameter_aliases']
        results = {}

        for table in p0_tables:
            print(f"\n{'#'*60}")
            print(f"# Verifying: {table}")
            print(f"{'#'*60}")

            # 1. 检查表结构
            structure_ok = check_table_structure(conn, table)

            # 2. 检查外键
            fk_ok = check_foreign_keys(conn, table)

            # 3. 检查数据完整性
            integrity_ok = check_data_integrity(conn, table)

            # 4. 检查索引
            check_indexes(conn, table)

            # 汇总结果
            results[table] = {
                'structure': structure_ok,
                'foreign_keys': fk_ok,
                'integrity': integrity_ok,
            }

        # 最终报告
        print(f"\n{'='*60}")
        print("VERIFICATION SUMMARY")
        print(f"{'='*60}")

        all_passed = True
        for table, checks in results.items():
            table_status = "✅ PASS" if all(checks.values()) else "❌ FAIL"
            print(f"\n{table}: {table_status}")

            for check_name, check_result in checks.items():
                status = "✅" if check_result else "❌"
                print(f"  {status} {check_name}")

            if not all(checks.values()):
                all_passed = False

        print(f"\n{'='*60}")
        if all_passed:
            print("✅ ALL CHECKS PASSED")
            print(f"{'='*60}")
            return True
        else:
            print("❌ SOME CHECKS FAILED")
            print(f"{'='*60}")
            print("\nPlease review the failed checks above.")
            return False

    except Exception as e:
        print(f"\n❌ Verification failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    success = verify_migration()
    sys.exit(0 if success else 1)
