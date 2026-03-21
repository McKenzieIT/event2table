#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HQL History Enhancement Migration Script

Migrate hql_history table to support:
- hql_type: select, ddl, dml, canvas
- game_gid: game filtering
- name_en, name_cn: searchability
- Performance indexes
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from backend.core.database import get_db_connection
from backend.core.config import DB_PATH


def migrate_database(db_path=None):
    """
    Run migration to enhance hql_history table

    Args:
        db_path: Database path (default: use config)

    Returns:
        bool: Migration success
    """
    if db_path is None:
        db_path = DB_PATH

    print(f"Running migration on: {db_path}")

    # Read SQL migration script
    script_dir = os.path.dirname(__file__)
    migration_sql_path = os.path.join(script_dir, "add_hql_history_enhancements.sql")

    if not os.path.exists(migration_sql_path):
        print(f"❌ Migration script not found: {migration_sql_path}")
        return False

    with open(migration_sql_path, "r", encoding="utf-8") as f:
        migration_sql = f.read()

    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()

        # Split and execute each statement
        statements = [s.strip() for s in migration_sql.split(";") if s.strip()]

        for i, statement in enumerate(statements, 1):
            # Skip comments and verification queries
            if statement.startswith("--") or statement.startswith("/*"):
                continue
            if statement.startswith("SELECT") or statement.startswith("PRAGMA"):
                continue

            if statement:
                print(f"Executing statement {i}/{len(statements)}...")
                try:
                    cursor.execute(statement)
                except Exception as e:
                    # Ignore "duplicate column name" errors
                    if "duplicate column" in str(e).lower():
                        print(f"  ⚠️  Column already exists, skipping...")
                    else:
                        raise

        conn.commit()
        conn.close()

        print("✅ Migration completed successfully!")

        # Verify migration
        print("\n📊 Verification:")
        conn = get_db_connection(db_path)
        cursor = conn.cursor()

        # Check columns
        cursor.execute("PRAGMA table_info(hql_history)")
        columns = cursor.fetchall()
        print(f"  ✓ Table has {len(columns)} columns")

        # Check indexes
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='hql_history' ORDER BY name"
        )
        indexes = cursor.fetchall()
        print(f"  ✓ Table has {len(indexes)} indexes")

        conn.close()

        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate HQL history table")
    parser.add_argument("--db", help="Database path (default: use config)")
    parser.add_argument("--dry-run", action="store_true", help="Show SQL without executing")

    args = parser.parse_args()

    if args.dry_run:
        script_dir = os.path.dirname(__file__)
        migration_sql_path = os.path.join(script_dir, "add_hql_history_enhancements.sql")

        with open(migration_sql_path, "r", encoding="utf-8") as f:
            print(f.read())

        print("\n[DRY RUN] No changes made")
        return 0

    success = migrate_database(args.db)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
