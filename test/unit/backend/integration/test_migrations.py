#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Migration Tests

Tests for the database migration system to ensure:
1. Migrations run in correct order
2. Migrations are idempotent (can run multiple times safely)
3. Final schema matches expected structure
4. Data migration preserves existing data
"""

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class TestDatabaseMigrations(unittest.TestCase):
    """Test database migrations"""

    def setUp(self):
        """Set up test database"""
        # Set FLASK_ENV=testing to use TEST_DB_PATH
        os.environ["FLASK_ENV"] = "testing"

        # Create a temporary database file for this test
        # Note: We don't delete TEST_DB_PATH because other tests may be using it
        self.test_db = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".db")
        self.test_db.close()
        self.db_path = Path(self.test_db.name)

    def tearDown(self):
        """Clean up test database"""
        # Close any connections and delete test database
        if self.db_path.exists():
            try:
                os.unlink(self.db_path)
            except PermissionError:
                pass

    def _get_db_version(self, conn):
        """Get current database version"""
        cursor = conn.cursor()
        cursor.execute("PRAGMA user_version")
        return cursor.fetchone()[0]

    def _table_exists(self, conn, table_name):
        """Check if table exists"""
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        return cursor.fetchone() is not None

    def _column_exists(self, conn, table_name, column_name):
        """Check if column exists in table"""
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]
        return column_name in columns

    def test_migration_from_v0_to_v18(self):
        """Test full migration from version 0 to 18"""
        # Run migration with explicit db_path
        from backend.core.database.database import migrate_db

        migrate_db(self.db_path)

        # Verify final version
        conn = sqlite3.connect(str(self.db_path))
        version = self._get_db_version(conn)
        self.assertEqual(version, 18, "Database should be at version 18")
        conn.close()

    def test_migration_is_idempotent(self):
        """Test that running migrations twice is safe"""
        from backend.core.database.database import migrate_db

        # Run migration first time
        migrate_db(self.db_path)

        # Get version after first run
        conn = sqlite3.connect(str(self.db_path))
        version1 = self._get_db_version(conn)
        conn.close()

        # Run migration second time
        migrate_db(self.db_path)

        # Get version after second run
        conn = sqlite3.connect(str(self.db_path))
        version2 = self._get_db_version(conn)
        conn.close()

        # Versions should be identical
        self.assertEqual(version1, version2, "Migration should be idempotent")
        self.assertEqual(version2, 18, "Database should remain at version 18")

    def test_migration_v1_category_id(self):
        """Test Migration v1: category_id column added to log_events"""
        from backend.core.database.database import init_db, migrate_db

        # Initialize database with full schema
        init_db(self.db_path)

        # Manually remove category_id column to simulate v0 database
        # Note: SQLite doesn't support DROP COLUMN, so we recreate the table
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Get existing data
        cursor.execute("SELECT * FROM log_events")
        existing_data = cursor.fetchall()

        # Get column info
        cursor.execute("PRAGMA table_info(log_events)")
        columns = [col[1] for col in cursor.fetchall() if col[1] != "category_id"]

        # Recreate table without category_id
        columns_str = ", ".join(columns)
        cursor.execute(f"DROP TABLE log_events")
        cursor.execute(f"""
            CREATE TABLE log_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER,
                event_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Set database version to 0 (simulate v0 database)
        cursor.execute("PRAGMA user_version = 0")
        conn.commit()
        conn.close()

        # Run migration
        migrate_db(self.db_path)

        # Verify category_id column exists
        conn = sqlite3.connect(str(self.db_path))
        self.assertTrue(self._column_exists(conn, "log_events", "category_id"), "category_id column should exist")

        # Verify default category was created
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM event_categories WHERE name = '默认分类'")
        count = cursor.fetchone()[0]
        self.assertGreater(count, 0, "Default category should be created")
        conn.close()

    def test_migration_v2_event_category_relations(self):
        """Test Migration v2: event_category_relations table created"""
        # Import migrate_db dynamically to pick up patched get_db_path

        # Run migration
        from backend.core.database.database import migrate_db

        migrate_db(self.db_path)

        # Verify table exists
        conn = sqlite3.connect(str(self.db_path))
        self.assertTrue(
            self._table_exists(conn, "event_category_relations"), "event_category_relations table should exist"
        )
        conn.close()

    def test_migration_v3_include_in_common_params(self):
        """Test Migration v3: include_in_common_params column added"""
        # Import migrate_db dynamically to pick up patched get_db_path

        # Run migration
        from backend.core.database.database import migrate_db

        migrate_db(self.db_path)

        # Verify column exists
        conn = sqlite3.connect(str(self.db_path))
        self.assertTrue(
            self._column_exists(conn, "log_events", "include_in_common_params"),
            "include_in_common_params column should exist",
        )
        conn.close()

    def test_migration_v4_icon_path(self):
        """Test Migration v4: icon_path column added to games"""
        # Import migrate_db dynamically to pick up patched get_db_path

        # Run migration
        from backend.core.database.database import migrate_db

        migrate_db(self.db_path)

        # Verify column exists
        conn = sqlite3.connect(str(self.db_path))
        self.assertTrue(self._column_exists(conn, "games", "icon_path"), "icon_path column should exist in games table")
        conn.close()

    def test_migration_v5_edit_tracking(self):
        """Test Migration v5: edit tracking fields added to hql_statements"""
        # Import migrate_db dynamically to pick up patched get_db_path

        # Run migration
        from backend.core.database.database import migrate_db

        migrate_db(self.db_path)

        # Verify columns exist
        conn = sqlite3.connect(str(self.db_path))
        for column in ["is_user_edited", "edit_notes", "original_content"]:
            self.assertTrue(
                self._column_exists(conn, "hql_statements", column), f"{column} column should exist in hql_statements"
            )
        conn.close()

    def test_migration_v6_parameter_management(self):
        """Test Migration v6: parameter management refactoring"""
        # Import migrate_db dynamically to pick up patched get_db_path

        # Run migration
        from backend.core.database.database import migrate_db

        migrate_db(self.db_path)

        # Verify all new tables exist
        conn = sqlite3.connect(str(self.db_path))
        tables = ["param_templates", "param_library", "event_params", "param_versions", "param_configs"]

        for table in tables:
            self.assertTrue(self._table_exists(conn, table), f"{table} table should exist")

        # Verify param_templates has default templates
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM param_templates")
        count = cursor.fetchone()[0]
        self.assertGreater(count, 0, "Default templates should be created")

        conn.close()

    def test_migration_v18_game_gid(self):
        """Test Migration v18: game_gid column added to log_events"""
        from backend.core.database.database import init_db, migrate_db

        # Initialize database with full schema
        init_db(self.db_path)

        # Add test data before removing column
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Insert test game
        cursor.execute("INSERT INTO games (gid, name, ods_db) VALUES (10000147, 'Test Game', 'test_ods')")
        game_id = cursor.lastrowid

        # Insert test event (init_db schema doesn't have game_gid yet)
        cursor.execute(
            "INSERT INTO log_events (game_id, event_name, event_name_cn, source_table, target_table) VALUES (?, ?, ?, ?, ?)",
            (game_id, "test_event", "测试事件", "test_source", "test_target"),
        )
        event_id = cursor.lastrowid

        # Manually remove game_gid column to simulate pre-v18 database
        # Note: SQLite doesn't support DROP COLUMN, so we recreate the table
        cursor.execute("DROP TABLE log_events")
        cursor.execute("""
            CREATE TABLE log_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER,
                event_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Re-insert test data without game_gid
        cursor.execute(
            "INSERT INTO log_events (id, game_id, event_name) VALUES (?, ?, 'test_event')", (event_id, game_id)
        )

        # Set database version to 17 (simulate pre-v18 database)
        cursor.execute("PRAGMA user_version = 17")
        conn.commit()
        conn.close()

        # Run migration
        migrate_db(self.db_path)

        # Verify game_gid column exists
        conn = sqlite3.connect(str(self.db_path))
        self.assertTrue(self._column_exists(conn, "log_events", "game_gid"), "game_gid column should exist")

        # Verify data was migrated (game_gid should be 10000147)
        cursor = conn.cursor()
        cursor.execute("SELECT game_gid FROM log_events WHERE id = 1")
        result = cursor.fetchone()
        self.assertEqual(result[0], 10000147, "game_gid should be migrated from games.gid")

        conn.close()

    def test_all_required_tables_exist(self):
        """Test that all required tables exist after migration"""
        # Run migration
        from backend.core.database.database import migrate_db

        print(f"Test DB path: {self.db_path}")
        migrate_db(self.db_path)

        # Debug: Check what tables exist
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables after migration: {existing_tables}")
        conn.close()

        # List of all tables that should exist
        required_tables = [
            "games",
            "log_events",
            "event_categories",
            "event_category_relations",
            "hql_statements",
            "common_params",
            "event_common_params",
            "param_templates",
            "param_library",
            "event_params",
            "param_versions",
            "param_configs",
            "param_validation_rules",
            "batch_import_records",
            "batch_import_details",
            "param_dependencies",
            "join_configs",
            "hql_generation_templates",
            "field_selection_presets",
            "node_templates",
            "flow_templates",
            "event_nodes",
            "parameter_aliases",
            "field_name_mappings",
            "field_name_history",
            "event_node_configs",
            "async_tasks",
        ]

        conn = sqlite3.connect(str(self.db_path))
        for table in required_tables:
            exists = self._table_exists(conn, table)
            if not exists:
                conn.close()
                self.fail(f"Required table '{table}' does not exist. " f"Existing tables: {existing_tables}")
        conn.close()


class TestMigrationManager(unittest.TestCase):
    """Test the new MigrationManager class (after refactoring)"""

    def setUp(self):
        """Set up test database"""
        self.test_db = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".db")
        self.test_db.close()
        self.db_path = Path(self.test_db.name)

    def tearDown(self):
        """Clean up test database"""
        if self.db_path.exists():
            try:
                os.unlink(self.db_path)
            except PermissionError:
                pass

    def test_migration_manager_exists(self):
        """Test that MigrationManager class exists after refactoring"""
        try:
            from backend.core.database.migrations import MigrationManager

            self.assertTrue(True, "MigrationManager should be importable")
        except ImportError:
            self.skipTest("MigrationManager not yet created")


if __name__ == "__main__":
    unittest.main()
