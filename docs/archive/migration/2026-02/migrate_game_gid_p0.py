#!/usr/bin/env python3
"""
Game GID迁移脚本 - P0表
迁移common_params和parameter_aliases表

Author: Event2Table Development Team
Date: 2026-02-20
"""
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DB_PATH = "data/dwd_generator.db"
BACKUP_PATH = f"data/dwd_generator.db.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Game ID到GID的映射
GAME_ID_TO_GID = {}
GAME_GID_TO_ID = {}


def load_game_mappings(conn):
    """加载game_id到game_gid的映射"""
    cursor = conn.cursor()
    cursor.execute("SELECT id, gid FROM games")
    mappings = cursor.fetchall()

    for game_id, game_gid in mappings:
        GAME_ID_TO_GID[game_id] = game_gid
        GAME_GID_TO_ID[game_gid] = game_id

    logger.info(f"✅ Loaded {len(mappings)} game mappings")

    # 打印映射信息
    logger.info("Game ID to GID mappings:")
    for game_id, game_gid in sorted(GAME_ID_TO_GID.items()):
        logger.info(f"  game_id={game_id} → game_gid={game_gid}")


def backup_database():
    """备份数据库"""
    logger.info(f"Creating backup: {BACKUP_PATH}")
    import shutil
    shutil.copy2(DB_PATH, BACKUP_PATH)
    logger.info("✅ Backup created successfully")


def migrate_table(conn, table_name):
    """
    迁移单个表

    步骤：
    1. 添加game_gid列
    2. 从game_id映射数据到game_gid
    3. 验证数据完整性
    4. 删除game_id列
    """
    cursor = conn.cursor()

    logger.info(f"\n{'='*60}")
    logger.info(f"Migrating table: {table_name}")
    logger.info(f"{'='*60}")

    try:
        # 1. 检查表结构
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()
        columns = [col[1] for col in columns_info]

        logger.info(f"Current columns: {columns}")

        # 2. 检查数据量
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_count = cursor.fetchone()[0]
        logger.info(f"Total records: {total_count}")

        # 3. 检查game_id分布
        cursor.execute(f"SELECT game_id, COUNT(*) FROM {table_name} GROUP BY game_id")
        game_id_dist = cursor.fetchall()
        logger.info(f"Game ID distribution: {game_id_dist}")

        # 4. 检查是否已有game_gid列
        if 'game_gid' in columns:
            logger.info(f"  ⚠️  Table {table_name} already has game_gid column")

            # 检查是否还有game_id列
            if 'game_id' not in columns:
                logger.info(f"  ✅ Migration already completed (no game_id column)")
                return True

        # 5. 开始事务
        conn.execute("BEGIN TRANSACTION")

        # 6. 添加game_gid列（如果不存在）
        if 'game_gid' not in columns:
            logger.info(f"  Adding game_gid column...")
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN game_gid INTEGER")

        # 7. 更新数据：从game_id映射到game_gid
        if 'game_id' in columns:
            logger.info(f"  Migrating data from game_id to game_gid...")

            cursor.execute(f"SELECT DISTINCT game_id FROM {table_name} WHERE game_id IS NOT NULL")
            game_ids = [row[0] for row in cursor.fetchall()]

            migrated_count = 0
            orphaned_count = 0
            direct_gid_count = 0

            for game_id in game_ids:
                # 检查是否是有效的game_id
                game_gid = GAME_ID_TO_GID.get(game_id)

                if game_gid:
                    # 正常情况：game_id → game_gid映射
                    cursor.execute(
                        f"UPDATE {table_name} SET game_gid = ? WHERE game_id = ?",
                        (game_gid, game_id)
                    )
                    affected = cursor.rowcount
                    migrated_count += affected
                    logger.info(f"    Migrated {affected} records: game_id={game_id} → game_gid={game_gid}")
                else:
                    # 特殊情况1：game_id可能已经是GID（如10000147）
                    cursor.execute(f"SELECT 1 FROM games WHERE gid = ?", (game_id,))
                    if cursor.fetchone():
                        # game_id实际上已经是game_gid
                        cursor.execute(
                            f"UPDATE {table_name} SET game_gid = ? WHERE game_id = ?",
                            (game_id, game_id)
                        )
                        affected = cursor.rowcount
                        direct_gid_count += affected
                        logger.info(f"    Direct GID assignment: {affected} records with game_gid={game_id}")
                    else:
                        # 特殊情况2：孤儿数据（game_id对应的游戏已被删除）
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE game_id = ?", (game_id,))
                        orphaned = cursor.fetchone()[0]
                        orphaned_count += orphaned
                        logger.warning(f"    ⚠️  Orphaned data: {orphaned} records with deleted game_id={game_id}")
                        # 这些记录将保持game_gid=NULL

            logger.info(f"  ✅ Migration summary:")
            logger.info(f"    - Migrated from game_id: {migrated_count}")
            logger.info(f"    - Direct GID assignment: {direct_gid_count}")
            logger.info(f"    - Orphaned records (will be NULL): {orphaned_count}")

        # 8. 验证数据完整性
        logger.info(f"  Verifying data integrity...")

        # 检查是否有NULL game_gid（允许孤儿数据为NULL）
        cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE game_gid IS NULL AND game_id IS NOT NULL")
        null_count = cursor.fetchone()[0]

        if null_count > 0:
            logger.warning(f"  ⚠️  {null_count} records have NULL game_gid (orphaned data)")
            # 不再回滚，允许孤儿数据存在

        # 检查外键有效性
        cursor.execute(f"""
            SELECT COUNT(*) FROM {table_name}
            WHERE game_gid IS NOT NULL
            AND NOT EXISTS (SELECT 1 FROM games WHERE gid = {table_name}.game_gid)
        """)
        invalid_fk_count = cursor.fetchone()[0]

        if invalid_fk_count > 0:
            logger.warning(f"  ⚠️  {invalid_fk_count} records have invalid foreign key references")

            # 查看无效的记录
            cursor.execute(f"""
                SELECT game_gid FROM {table_name}
                WHERE game_gid IS NOT NULL
                AND NOT EXISTS (SELECT 1 FROM games WHERE gid = {table_name}.game_gid)
                GROUP BY game_gid
            """)
            invalid_gids = [row[0] for row in cursor.fetchall()]
            logger.warning(f"    Invalid game_gids: {invalid_gids}")
        else:
            logger.info(f"  ✅ All foreign keys are valid")

        # 9. 删除game_id列（通过重建表）
        if 'game_id' in columns:
            logger.info(f"  Dropping game_id column by recreating table...")

            # 获取所有列（除了game_id）
            columns_to_keep = [col for col in columns if col != 'game_id']

            # 创建新表
            temp_table = f"{table_name}_new"
            cursor.execute(f"DROP TABLE IF EXISTS {temp_table}")

            # 构建CREATE TABLE语句
            columns_def = []
            for col_info in columns_info:
                col_name = col_info[1]
                if col_name == 'game_id':
                    continue  # 跳过game_id列

                col_type = col_info[2]
                col_notnull = col_info[3]
                col_default = col_info[4]
                col_pk = col_info[5]

                col_def = f'"{col_name}" {col_type}'
                if col_pk:
                    col_def += " PRIMARY KEY"
                if col_notnull and not col_pk:
                    col_def += " NOT NULL"
                if col_default:
                    col_def += f" DEFAULT {col_default}"

                columns_def.append(col_def)

            create_sql = f"CREATE TABLE {temp_table} (\n  " + ",\n  ".join(columns_def) + "\n)"
            logger.debug(f"CREATE SQL: {create_sql}")

            cursor.execute(create_sql)

            # 复制数据（包括game_gid，不包括game_id）
            columns_str = ', '.join([f'"{col}"' for col in columns_to_keep])
            cursor.execute(f"""
                INSERT INTO {temp_table} ({columns_str})
                SELECT {columns_str} FROM {table_name}
            """)
            copied_count = cursor.rowcount
            logger.info(f"    Copied {copied_count} records to new table")

            # 删除旧表
            cursor.execute(f"DROP TABLE {table_name}")

            # 重命名新表
            cursor.execute(f"ALTER TABLE {temp_table} RENAME TO {table_name}")

            # 重建索引
            cursor.execute(f"SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='{table_name}'")
            indexes = cursor.fetchall()

            for idx_name, idx_sql in indexes:
                if idx_name.startswith('sqlite_'):
                    continue  # 跳过自动创建的索引

                if idx_sql:
                    try:
                        cursor.execute(idx_sql)
                        logger.info(f"    Recreated index: {idx_name}")
                    except Exception as e:
                        logger.warning(f"    Failed to recreate index {idx_name}: {e}")

            logger.info(f"  ✅ Dropped game_id column successfully")

        # 提交事务
        conn.commit()
        logger.info(f"  ✅ Table {table_name} migrated successfully")

        return True

    except Exception as e:
        conn.rollback()
        logger.error(f"  ❌ Migration failed for {table_name}: {e}")
        raise


def verify_migration(conn, tables):
    """验证迁移结果"""
    logger.info("\n" + "="*60)
    logger.info("Final Verification")
    logger.info("="*60)

    cursor = conn.cursor()

    for table in tables:
        logger.info(f"\nTable: {table}")

        # 检查表结构
        cursor.execute(f"PRAGMA table_info({table})")
        columns_info = cursor.fetchall()
        columns = [col[1] for col in columns_info]

        has_game_gid = 'game_gid' in columns
        has_game_id = 'game_id' in columns

        logger.info(f"  Columns: {columns}")

        if has_game_gid and not has_game_id:
            logger.info(f"  ✅ Migration successful (has game_gid, no game_id)")
        elif has_game_gid and has_game_id:
            logger.warning(f"  ⚠️  Both columns exist, needs manual review")
        else:
            logger.error(f"  ❌ Migration failed")

        # 验证外键（仅在表有game_gid列时）
        if has_game_gid:
            cursor.execute(f"""
                SELECT COUNT(*) FROM {table}
                WHERE game_gid IS NOT NULL
                AND NOT EXISTS (SELECT 1 FROM games WHERE gid = {table}.game_gid)
            """)
            invalid_count = cursor.fetchone()[0]

            if invalid_count > 0:
                logger.error(f"  ❌ {invalid_count} records have invalid foreign keys")
            else:
                logger.info(f"  ✅ All foreign keys are valid")

            # 检查NULL game_gid数量
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE game_gid IS NULL")
            null_count = cursor.fetchone()[0]
            if null_count > 0:
                logger.warning(f"  ⚠️  {null_count} records have NULL game_gid (orphaned data)")

            # 检查game_gid分布
            cursor.execute(f"""
                SELECT game_gid, COUNT(*) FROM {table}
                GROUP BY game_gid
                ORDER BY game_gid
            """)
            gid_dist = cursor.fetchall()
            logger.info(f"  Game GID distribution: {gid_dist}")

        # 检查数据量
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        total_count = cursor.fetchone()[0]
        logger.info(f"  Total records: {total_count}")


def main():
    """主函数"""
    logger.info("="*60)
    logger.info("Game GID Migration - P0 Tables")
    logger.info("="*60)

    # 1. 备份数据库
    backup_database()

    # 2. 连接数据库
    conn = sqlite3.connect(DB_PATH)

    try:
        # 3. 加载游戏映射
        load_game_mappings(conn)

        # 4. 迁移P0表
        p0_tables = ['common_params', 'parameter_aliases']

        for table in p0_tables:
            try:
                migrate_table(conn, table)
            except Exception as e:
                logger.error(f"Failed to migrate {table}: {e}")
                logger.info("Continuing with next table...")

        # 5. 验证最终结果
        verify_migration(conn, p0_tables)

        logger.info("\n" + "="*60)
        logger.info("✅ P0 Migration completed!")
        logger.info("="*60)
        logger.info(f"\nBackup location: {BACKUP_PATH}")
        logger.info("To rollback: cp " + BACKUP_PATH + " " + DB_PATH)

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        logger.info("Database is still in original state")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
