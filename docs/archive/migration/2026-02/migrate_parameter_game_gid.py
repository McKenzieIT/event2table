#!/usr/bin/env python3
"""
Parameter Tables game_gid Migration
Add game_gid field to parameter_aliases and common_params tables

Author: Event2Table Development Team
Date: 2026-02-20
"""

import sqlite3
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

DB_PATH = "data/dwd_generator.db"


def backup_database():
    """Backup database"""
    backup_path = f"data/dwd_generator.db.backup_params_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    import shutil

    shutil.copy2(DB_PATH, backup_path)
    logger.info(f"✅ Backup created: {backup_path}")
    return backup_path


def migrate_parameter_aliases(conn):
    """Migrate parameter_aliases table"""
    cursor = conn.cursor()

    logger.info("\n=== Migrating parameter_aliases ===")

    # Check current structure
    cursor.execute("PRAGMA table_info(parameter_aliases)")
    columns = [col[1] for col in cursor.fetchall()]
    logger.info(f"Current columns: {columns}")

    if "game_gid" in columns:
        logger.info("✅ game_gid column already exists")
        return

    # Add game_gid column
    cursor.execute("ALTER TABLE parameter_aliases ADD COLUMN game_gid INTEGER")
    logger.info("✅ Added game_gid column")

    # Populate game_gid from param_id -> event_params -> log_events
    cursor.execute("""
        UPDATE parameter_aliases
        SET game_gid = (
            SELECT le.game_gid
            FROM event_params ep
            JOIN log_events le ON ep.event_id = le.id
            WHERE ep.id = parameter_aliases.param_id
            LIMIT 1
        )
        WHERE EXISTS (
            SELECT 1 FROM event_params ep
            JOIN log_events le ON ep.event_id = le.id
            WHERE ep.id = parameter_aliases.param_id
        )
    """)

    logger.info(f"✅ Updated {cursor.rowcount} records with game_gid")

    # Check for NULL values
    cursor.execute("SELECT COUNT(*) FROM parameter_aliases WHERE game_gid IS NULL")
    null_count = cursor.fetchone()[0]
    if null_count > 0:
        logger.warning(f"⚠️ {null_count} records have NULL game_gid (orphaned param_id)")
    else:
        logger.info("✅ All records have valid game_gid")

    # Create index
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_parameter_aliases_game_gid ON parameter_aliases(game_gid)"
    )
    logger.info("✅ Created index on game_gid")


def migrate_common_params(conn):
    """Migrate common_params table"""
    cursor = conn.cursor()

    logger.info("\n=== Migrating common_params ===")

    # Check current structure
    cursor.execute("PRAGMA table_info(common_params)")
    columns = [col[1] for col in cursor.fetchall()]
    logger.info(f"Current columns: {columns}")

    if "game_gid" in columns:
        logger.info("✅ game_gid column already exists")
        return

    # Add game_gid column
    cursor.execute("ALTER TABLE common_params ADD COLUMN game_gid INTEGER")
    logger.info("✅ Added game_gid column")

    # Note: common_params doesn't have param_id, so we need another approach
    # Check if there's any way to link it to games
    cursor.execute("SELECT COUNT(*) FROM common_params")
    total = cursor.fetchone()[0]
    logger.info(f"Total records: {total}")

    # For now, common_params records need game_gid to be set via the API
    # when they are created. Existing records will have NULL game_gid.
    # This is acceptable because common_params are typically regenerated per game.

    # Create index
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_common_params_game_gid ON common_params(game_gid)"
    )
    logger.info("✅ Created index on game_gid")

    # Log distribution
    cursor.execute("SELECT game_gid, COUNT(*) FROM common_params GROUP BY game_gid")
    dist = cursor.fetchall()
    logger.info(f"Game GID distribution: {dist}")


def verify_migration(conn):
    """Verify migration results"""
    logger.info("\n=== Verification ===")

    cursor = conn.cursor()

    for table in ["parameter_aliases", "common_params"]:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]

        has_game_gid = "game_gid" in columns
        logger.info(f"{table}: game_gid={'✅' if has_game_gid else '❌'}")

        if has_game_gid:
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE game_gid IS NOT NULL")
            valid = cursor.fetchone()[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            total = cursor.fetchone()[0]
            logger.info(f"  Valid records: {valid}/{total}")


def main():
    logger.info("=" * 60)
    logger.info("Parameter Tables game_gid Migration")
    logger.info("=" * 60)

    backup_database()

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("BEGIN TRANSACTION")

        migrate_parameter_aliases(conn)
        migrate_common_params(conn)

        verify_migration(conn)

        conn.commit()
        logger.info("\n✅ Migration completed successfully!")

    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
