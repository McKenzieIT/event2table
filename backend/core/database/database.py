#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database initialization and connection management

This module provides database connection management and initialization
functions for the SQLite database used by the application.
"""

import sqlite3
from contextlib import contextmanager
from typing import Generator, Optional
from pathlib import Path

from backend.core.config import get_db_path
from backend.core.logging import get_logger
from backend.core.database._constants import ALL_TABLES_SQL, INDEXES_SQL
from backend.core.database._helpers import (
    _apply_pragma_settings,
    _create_table_if_not_exists,
    _create_index_if_not_exists,
    _execute_sql_file,
)

logger = get_logger(__name__)


def get_db_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """
    Get database connection with row factory and WAL mode

    Args:
        db_path: Optional database path. If not provided, uses get_db_path()

    Returns:
        SQLite connection with Row factory
    """
    if db_path is None:
        db_path = get_db_path()

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    _apply_pragma_settings(conn)

    return conn


@contextmanager
def get_db(db_path: Optional[Path] = None) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for database connections with WAL mode

    Args:
        db_path: Optional database path. If not provided, uses get_db_path()

    Yields:
        SQLite connection with Row factory
    """
    if db_path is None:
        db_path = get_db_path()

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    _apply_pragma_settings(conn)

    try:
        yield conn
    finally:
        conn.close()


def init_db(db_path: Optional[Path] = None):
    """
    Initialize database with all tables

    Args:
        db_path: Optional database path. If not provided, uses default database from config.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # Check if hql_statements table exists, if not create it
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='hql_statements'"
    )
    if not cursor.fetchone():
        logger.info("Creating hql_statements table...")
        cursor.execute("""
            CREATE TABLE hql_statements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                hql_type TEXT NOT NULL,
                hql_content TEXT NOT NULL,
                hql_version INTEGER DEFAULT 1,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES log_events(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
        logger.info("hql_statements table created successfully")
    else:
        logger.info("hql_statements table already exists")

    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gid TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            ods_db TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS log_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            event_name TEXT NOT NULL,
            event_name_cn TEXT NOT NULL,
            category_id INTEGER,
            source_table TEXT NOT NULL,
            target_table TEXT NOT NULL,
            include_in_common_params INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES event_categories(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parameters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            param_name TEXT NOT NULL,
            param_name_cn TEXT,
            param_type TEXT NOT NULL,
            param_description TEXT,
            is_common_param INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES log_events(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS common_params (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            param_name TEXT NOT NULL,
            param_name_cn TEXT,
            param_type TEXT NOT NULL,
            param_description TEXT,
            table_name TEXT NOT NULL,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_category_relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES log_events(id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES event_categories(id) ON DELETE CASCADE,
            UNIQUE(event_id, category_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_common_params (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            common_param_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES log_events(id) ON DELETE CASCADE,
            FOREIGN KEY (common_param_id) REFERENCES common_params(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS join_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            display_name TEXT NOT NULL,
            source_events TEXT NOT NULL,
            join_conditions TEXT,
            output_fields TEXT NOT NULL,
            output_table TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            event_id INTEGER NOT NULL,
            config_json TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
            FOREIGN KEY (event_id) REFERENCES log_events(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parameter_aliases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            param_id INTEGER NOT NULL,
            alias TEXT NOT NULL,
            display_name TEXT,
            usage_count INTEGER DEFAULT 0,
            last_used_at TIMESTAMP,
            is_preferred INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
            FOREIGN KEY (param_id) REFERENCES parameters(id) ON DELETE CASCADE,
            UNIQUE(game_id, param_id, alias)
        )
    """)

    # Create sql_optimizations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sql_optimizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_hql TEXT NOT NULL,
            optimized_hql TEXT NOT NULL,
            applied_rules TEXT,
            suggested_rules TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create index on sql_optimizations
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sql_optimizations_created_at
        ON sql_optimizations(created_at)
    """)

    # Seed default categories if table is empty
    _seed_default_categories(cursor)

    conn.commit()
    conn.close()


def _seed_default_categories(cursor: sqlite3.Cursor):
    """
    Seed default event categories if the table is empty

    Args:
        cursor: Database cursor
    """
    # Check if categories already exist
    cursor.execute("SELECT COUNT(*) FROM event_categories")
    count = cursor.fetchone()[0]

    if count > 0:
        logger.info(f"Categories already exist ({count} found), skipping seed")
        return

    logger.info("Seeding default event categories...")

    default_categories = [
        ("登录/认证", "Login"),
        ("游戏进度", "Progress"),
        ("经济/交易", "Economy"),
        ("社交/聊天", "Social"),
        ("战斗/PVP", "Battle"),
        ("系统", "System"),
        ("充值/付费", "Payment"),
        ("行为/点击", "Behavior"),
    ]

    for category_name in default_categories:
        cursor.execute(
            "INSERT INTO event_categories (name) VALUES (?)", (category_name[0],)
        )
        logger.info(f"  - Created category: {category_name[0]}")

    logger.info(f"Successfully seeded {len(default_categories)} default categories")


# ==================== Migration System ==================== #


class BaseMigration:
    """数据库迁移基类"""

    version: int = 0

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        """
        执行迁移

        Args:
            cursor: 数据库游标
            conn: 数据库连接
        """
        raise NotImplementedError("Subclasses must implement upgrade()")


class MigrationV1_AddCategoryId(BaseMigration):
    """迁移1：添加category_id列到log_events表"""

    version = 1

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        cursor.execute("PRAGMA table_info(log_events)")
        columns = [column[1] for column in cursor.fetchall()]

        if "category_id" not in columns:
            logger.info("Migration v1: Adding category_id column to log_events...")
            cursor.execute("ALTER TABLE log_events ADD COLUMN category_id INTEGER")

            # Create default category
            cursor.execute(
                'INSERT OR IGNORE INTO event_categories (name) VALUES ("默认分类")'
            )
            cursor.execute('SELECT id FROM event_categories WHERE name = "默认分类"')
            default_category = cursor.fetchone()

            if default_category:
                cursor.execute(
                    "UPDATE log_events SET category_id = ?", (default_category[0],)
                )

            logger.info(
                "Migration v1 completed: category_id column added to log_events"
            )


class MigrationV2_EventCategoryRelations(BaseMigration):
    """迁移2：创建event_category_relations表"""

    version = 2

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='event_category_relations'"
        )
        if not cursor.fetchone():
            logger.info("Migration v2: Adding event_category_relations table...")
            cursor.execute("""
                CREATE TABLE event_category_relations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER NOT NULL,
                    category_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (event_id) REFERENCES log_events(id) ON DELETE CASCADE,
                    FOREIGN KEY (category_id) REFERENCES event_categories(id) ON DELETE CASCADE,
                    UNIQUE(event_id, category_id)
                )
            """)
            logger.info("Migration v2 completed: event_category_relations table added")


class MigrationV3_IncludeInCommonParams(BaseMigration):
    """迁移3：添加include_in_common_params列到log_events表"""

    version = 3

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        cursor.execute("PRAGMA table_info(log_events)")
        columns = [column[1] for column in cursor.fetchall()]

        if "include_in_common_params" not in columns:
            logger.info(
                "Migration v3: Adding include_in_common_params column to log_events..."
            )
            cursor.execute(
                "ALTER TABLE log_events ADD COLUMN include_in_common_params INTEGER DEFAULT 1"
            )
            logger.info(
                "Migration v3 completed: include_in_common_params column added to log_events"
            )


class MigrationV4_IconPath(BaseMigration):
    """迁移4：添加icon_path列到games表"""

    version = 4

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        cursor.execute("PRAGMA table_info(games)")
        columns = [column[1] for column in cursor.fetchall()]

        if "icon_path" not in columns:
            logger.info("Migration v4: Adding icon_path column to games...")
            cursor.execute("ALTER TABLE games ADD COLUMN icon_path TEXT")
            logger.info("Migration v4 completed: icon_path column added to games")


class MigrationV5_EditTracking(BaseMigration):
    """迁移5：添加编辑追踪字段到hql_statements表"""

    version = 5

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        cursor.execute("PRAGMA table_info(hql_statements)")
        columns = [column[1] for column in cursor.fetchall()]

        if "is_user_edited" not in columns:
            logger.info("Migration v5: Adding is_user_edited column...")
            cursor.execute(
                "ALTER TABLE hql_statements ADD COLUMN is_user_edited INTEGER DEFAULT 0"
            )

        if "edit_notes" not in columns:
            logger.info("Migration v5: Adding edit_notes column...")
            cursor.execute("ALTER TABLE hql_statements ADD COLUMN edit_notes TEXT")

        if "original_content" not in columns:
            logger.info("Migration v5: Adding original_content column...")
            cursor.execute(
                "ALTER TABLE hql_statements ADD COLUMN original_content TEXT"
            )

        logger.info(
            "Migration v5 completed: edit tracking fields added to hql_statements"
        )


class MigrationV6_ParameterManagementRefactoring(BaseMigration):
    """迁移6：参数管理重构"""

    version = 6

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        logger.info("Migration v6: Starting parameter management refactoring...")

        # 1. Create param_templates table
        logger.info("Migration v6: Creating param_templates table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS param_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_name TEXT NOT NULL UNIQUE,
                display_name TEXT NOT NULL,
                base_type TEXT NOT NULL,
                element_type TEXT,
                nesting_level INTEGER DEFAULT 1,
                type_definition TEXT NOT NULL,
                hql_parse_template TEXT NOT NULL,
                description TEXT,
                is_system INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Insert predefined type templates
        templates_data = [
            (
                "string",
                "字符串",
                "string",
                None,
                1,
                '{"type": "primitive"}',
                "get_json_object(params, '$.{param_name}')",
                "基础字符串类型",
            ),
            (
                "int",
                "整数",
                "int",
                None,
                1,
                '{"type": "primitive"}',
                "CAST(get_json_object(params, '$.{param_name}') AS INT)",
                "基础整数类型",
            ),
            (
                "bigint",
                "长整数",
                "bigint",
                None,
                1,
                '{"type": "primitive"}',
                "CAST(get_json_object(params, '$.{param_name}') AS BIGINT)",
                "长整型",
            ),
            (
                "float",
                "浮点数",
                "float",
                None,
                1,
                '{"type": "primitive"}',
                "CAST(get_json_object(params, '$.{param_name}') AS FLOAT)",
                "浮点数类型",
            ),
            (
                "boolean",
                "布尔值",
                "boolean",
                None,
                1,
                '{"type": "primitive"}',
                "CAST(get_json_object(params, '$.{param_name}') AS BOOLEAN)",
                "布尔类型",
            ),
            (
                "array<string>",
                "字符串数组",
                "array",
                "string",
                1,
                '{"type": "array", "element_type": "string"}',
                "get_json_object(params, '$.{param_name}')",
                "字符串数组",
            ),
            (
                "array<int>",
                "整数数组",
                "array",
                "int",
                1,
                '{"type": "array", "element_type": "int"}',
                "get_json_object(params, '$.{param_name}')",
                "整数数组",
            ),
            (
                "array<float>",
                "浮点数组",
                "array",
                "float",
                1,
                '{"type": "array", "element_type": "float"}',
                "get_json_object(params, '$.{param_name}')",
                "浮点数数组",
            ),
            (
                "array<boolean>",
                "布尔数组",
                "array",
                "boolean",
                1,
                '{"type": "array", "element_type": "boolean"}',
                "get_json_object(params, '$.{param_name}')",
                "布尔数组",
            ),
            (
                "array<map>",
                "Map数组",
                "array",
                "map",
                2,
                '{"type": "array", "element_type": "map"}',
                "get_json_object(params, '$.{param_name}')",
                "包含Map的数组",
            ),
            (
                "map",
                "Map对象",
                "map",
                None,
                1,
                '{"type": "map"}',
                "get_json_object(params, '$.{param_name}')",
                "Map对象",
            ),
        ]

        cursor.executemany(
            """
            INSERT OR IGNORE INTO param_templates
            (template_name, display_name, base_type, element_type, nesting_level,
             type_definition, hql_parse_template, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            templates_data,
        )

        # 3. Create param_library table
        logger.info("Migration v6: Creating param_library table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS param_library (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                param_name TEXT NOT NULL,
                param_name_cn TEXT NOT NULL,
                template_id INTEGER NOT NULL,
                param_description TEXT,
                category TEXT,
                is_standard INTEGER DEFAULT 0,
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (template_id) REFERENCES param_templates(id),
                UNIQUE(param_name)
            )
        """)

        # 4. Create event_params table
        logger.info("Migration v6: Creating event_params table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_params (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                library_id INTEGER,
                param_name TEXT NOT NULL,
                param_name_cn TEXT,
                template_id INTEGER NOT NULL,
                param_description TEXT,
                hql_config TEXT,
                is_from_library INTEGER DEFAULT 0,
                version INTEGER DEFAULT 1,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES log_events(id) ON DELETE CASCADE,
                FOREIGN KEY (library_id) REFERENCES param_library(id) ON DELETE SET NULL,
                FOREIGN KEY (template_id) REFERENCES param_templates(id),
                UNIQUE(event_id, param_name, version)
            )
        """)

        # 5. Create param_versions table
        logger.info("Migration v6: Creating param_versions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS param_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_param_id INTEGER NOT NULL,
                version INTEGER NOT NULL,
                param_name TEXT NOT NULL,
                param_name_cn TEXT,
                template_id INTEGER NOT NULL,
                param_description TEXT,
                hql_config TEXT,
                change_reason TEXT,
                changed_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_param_id) REFERENCES event_params(id) ON DELETE CASCADE,
                FOREIGN KEY (template_id) REFERENCES param_templates(id)
            )
        """)

        # 6. Create param_configs table
        logger.info("Migration v6: Creating param_configs table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS param_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_param_id INTEGER NOT NULL UNIQUE,
                parse_mode TEXT DEFAULT 'json_extract',
                explode_config TEXT,
                array_element_delimiter TEXT DEFAULT ',',
                map_key_value_delimiter TEXT DEFAULT ':',
                custom_hql_template TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_param_id) REFERENCES event_params(id) ON DELETE CASCADE
            )
        """)

        # 7. Check if old parameters table exists and rename it
        logger.info("Migration v6: Checking for old parameters table...")
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='parameters'
        """)
        old_table_exists = cursor.fetchone() is not None

        if old_table_exists:
            # Migrate existing parameters to event_params
            logger.info(
                "Migration v6: Migrating existing parameters to event_params..."
            )
            cursor.execute(
                'SELECT id FROM param_templates WHERE template_name = "string" LIMIT 1'
            )
            default_template = cursor.fetchone()
            default_template_id = default_template[0] if default_template else None

            cursor.execute(
                """
                INSERT INTO event_params
                (event_id, param_name, param_name_cn, template_id, param_description,
                 is_from_library, version, is_active, created_at, updated_at)
                SELECT
                    p.event_id,
                    p.param_name,
                    p.param_name_cn,
                    COALESCE(
                        (SELECT id FROM param_templates WHERE template_name = p.param_type LIMIT 1),
                        ?
                    ),
                    p.param_description,
                    0,
                    1,
                    1,
                    p.created_at,
                    p.created_at
                FROM parameters p
                WHERE NOT EXISTS (
                    SELECT 1 FROM event_params ep
                    WHERE ep.event_id = p.event_id AND ep.param_name = p.param_name
                )
            """,
                (default_template_id,),
            )

            # Rename old table
            cursor.execute("ALTER TABLE parameters RENAME TO parameters_old_v5")
            logger.info(
                "Migration v6: renamed old parameters table to parameters_old_v5"
            )

        logger.info("Migration v6 completed: parameter management refactoring finished")


class MigrationV7_ParameterValidationAndBatchOperations(BaseMigration):
    """迁移7：参数验证规则和批量操作支持"""

    version = 7

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        logger.info(
            "Migration v7: Starting parameter validation and batch operations..."
        )

        # 1. Create param_validation_rules table
        logger.info("Migration v7: Creating param_validation_rules table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS param_validation_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_param_id INTEGER NOT NULL UNIQUE,
                rule_type TEXT NOT NULL,
                rule_config TEXT NOT NULL,
                error_message TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_param_id) REFERENCES event_params(id) ON DELETE CASCADE
            )
        """)

        # 2. Create batch_import_records table
        logger.info("Migration v7: Creating batch_import_records table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batch_import_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                import_name TEXT NOT NULL,
                import_type TEXT NOT NULL,
                total_rows INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                failed_count INTEGER DEFAULT 0,
                error_summary TEXT,
                file_path TEXT,
                status TEXT DEFAULT 'pending',
                created_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)

        # 3. Create batch_import_details table
        logger.info("Migration v7: Creating batch_import_details table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batch_import_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                import_id INTEGER NOT NULL,
                row_number INTEGER NOT NULL,
                data_type TEXT,
                action TEXT,
                entity_id INTEGER,
                status TEXT,
                error_message TEXT,
                FOREIGN KEY (import_id) REFERENCES batch_import_records(id) ON DELETE CASCADE
            )
        """)

        # 4. Create indexes for validation rules
        logger.info("Migration v7: Creating indexes for param_validation_rules...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_validation_rules_param_id
            ON param_validation_rules(event_param_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_validation_rules_type
            ON param_validation_rules(rule_type)
        """)

        # 5. Create indexes for batch imports
        logger.info("Migration v7: Creating indexes for batch_import tables...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_batch_import_records_status
            ON batch_import_records(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_batch_import_details_import_id
            ON batch_import_details(import_id)
        """)

        logger.info(
            "Migration v7 completed: validation rules and batch operations created"
        )


class MigrationV8_ParameterDependencies(BaseMigration):
    """迁移8：参数依赖关系支持"""

    version = 8

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        logger.info("Migration v8: Starting parameter dependencies...")

        # Create param_dependencies table
        logger.info("Migration v8: Creating param_dependencies table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS param_dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                dependent_param_id INTEGER NOT NULL,
                depends_on_param_id INTEGER NOT NULL,
                dependency_type TEXT NOT NULL,
                condition TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES log_events(id) ON DELETE CASCADE,
                FOREIGN KEY (dependent_param_id) REFERENCES event_params(id) ON DELETE CASCADE,
                FOREIGN KEY (depends_on_param_id) REFERENCES event_params(id) ON DELETE CASCADE,
                UNIQUE(event_id, dependent_param_id, depends_on_param_id)
            )
        """)

        # Create indexes
        logger.info("Migration v8: Creating indexes for param_dependencies...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_param_dependencies_event_id
            ON param_dependencies(event_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_param_dependencies_dependent
            ON param_dependencies(dependent_param_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_param_dependencies_depends_on
            ON param_dependencies(depends_on_param_id)
        """)

        logger.info("Migration v8 completed: parameter dependencies created")


class MigrationV9_EnhancedHQLGeneration(BaseMigration):
    """迁移9：增强的HQL生成功能"""

    version = 9

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        logger.info("Migration v9: Enhanced HQL generation features...")

        # Check if join_configs table exists and add new columns
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='join_configs'"
        )
        join_configs_exists = cursor.fetchone() is not None

        if join_configs_exists:
            logger.info("Migration v9: Adding new columns to join_configs...")
            cursor.execute("PRAGMA table_info(join_configs)")
            columns = [column[1] for column in cursor.fetchall()]

            if "join_type" not in columns:
                cursor.execute(
                    "ALTER TABLE join_configs ADD COLUMN join_type TEXT DEFAULT 'join'"
                )

            if "where_conditions" not in columns:
                cursor.execute(
                    "ALTER TABLE join_configs ADD COLUMN where_conditions TEXT"
                )

            if "field_mappings" not in columns:
                cursor.execute(
                    "ALTER TABLE join_configs ADD COLUMN field_mappings TEXT"
                )

            if "description" not in columns:
                cursor.execute("ALTER TABLE join_configs ADD COLUMN description TEXT")

            if "game_id" not in columns:
                cursor.execute("ALTER TABLE join_configs ADD COLUMN game_id INTEGER")

        # Create hql_generation_templates table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='hql_generation_templates'"
        )
        if not cursor.fetchone():
            logger.info("Migration v9: Creating hql_generation_templates table...")
            cursor.execute("""
                CREATE TABLE hql_generation_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_name TEXT NOT NULL UNIQUE,
                    display_name TEXT NOT NULL,
                    template_type TEXT NOT NULL,
                    template_content TEXT NOT NULL,
                    variables TEXT,
                    description TEXT,
                    is_system INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

        # Create field_selection_presets table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='field_selection_presets'"
        )
        if not cursor.fetchone():
            logger.info("Migration v9: Creating field_selection_presets table...")
            cursor.execute("""
                CREATE TABLE field_selection_presets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preset_name TEXT NOT NULL,
                    display_name TEXT NOT NULL,
                    game_id INTEGER,
                    field_list TEXT NOT NULL,
                    is_default INTEGER DEFAULT 0,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
                )
            """)

        logger.info("Migration v9 completed: Enhanced HQL generation features added")


class MigrationV10_ArrayParameterHierarchy(BaseMigration):
    """迁移10：Array参数层级结构支持"""

    version = 10

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        logger.info("Migration v10: Adding array parameter hierarchy support...")

        # Check if param_configs table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='param_configs'"
        )
        if cursor.fetchone():
            logger.info("Migration v10: Extending param_configs table...")
            cursor.execute("PRAGMA table_info(param_configs)")
            columns = [column[1] for column in cursor.fetchall()]

            if "child_params" not in columns:
                cursor.execute("ALTER TABLE param_configs ADD COLUMN child_params TEXT")

            if "array_element_structure" not in columns:
                cursor.execute(
                    "ALTER TABLE param_configs ADD COLUMN array_element_structure TEXT"
                )

        # Create index for parameter hierarchy
        logger.info("Migration v10: Creating indexes for parameter hierarchy...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_event_params_event_template
            ON event_params(event_id, template_id)
        """)

        logger.info("Migration v10 completed: array parameter hierarchy support added")


class MigrationV11_FieldBuilderSupport(BaseMigration):
    """迁移11：Field Builder支持"""

    version = 11

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        logger.info("Migration v11: Adding field builder support...")

        # Add field_mapping_v2 column to join_configs
        cursor.execute("PRAGMA table_info(join_configs)")
        columns = [column[1] for column in cursor.fetchall()]

        if "field_mapping_v2" not in columns:
            logger.info(
                "Migration v11: Adding field_mapping_v2 column to join_configs..."
            )
            cursor.execute("ALTER TABLE join_configs ADD COLUMN field_mapping_v2 TEXT")

        # Create node_templates table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='node_templates'"
        )
        if not cursor.fetchone():
            logger.info("Migration v11: Creating node_templates table...")
            cursor.execute("""
                CREATE TABLE node_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    node_name TEXT NOT NULL,
                    node_type TEXT NOT NULL,
                    node_config TEXT NOT NULL,
                    description TEXT,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

        # Create flow_templates table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='flow_templates'"
        )
        if not cursor.fetchone():
            logger.info("Migration v11: Creating flow_templates table...")
            cursor.execute("""
                CREATE TABLE flow_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    flow_name TEXT NOT NULL,
                    flow_graph TEXT NOT NULL,
                    variables TEXT,
                    description TEXT,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

        # Create indexes
        logger.info("Migration v11: Creating indexes for node and flow templates...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_node_templates_type
            ON node_templates(node_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flow_templates_created_by
            ON flow_templates(created_by)
        """)

        logger.info("Migration v11 completed: field builder support added")


class MigrationV12_FlowTemplates(BaseMigration):
    """迁移12：flow_templates表更新"""

    version = 12

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        logger.info("Migration v12: Updating flow_templates table...")

        # Check if table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='flow_templates'"
        )
        table_exists = cursor.fetchone() is not None

        if table_exists:
            logger.info(
                "Migration v12: flow_templates table exists, checking structure..."
            )
            cursor.execute("PRAGMA table_info(flow_templates)")
            columns = {column[1] for column in cursor.fetchall()}

            # Add missing columns
            if "game_id" not in columns:
                cursor.execute("ALTER TABLE flow_templates ADD COLUMN game_id INTEGER")
                cursor.execute(
                    "UPDATE flow_templates SET game_id = 1 WHERE game_id IS NULL"
                )

            if "is_active" not in columns:
                cursor.execute(
                    "ALTER TABLE flow_templates ADD COLUMN is_active INTEGER DEFAULT 1"
                )

            if "version" not in columns:
                cursor.execute(
                    "ALTER TABLE flow_templates ADD COLUMN version INTEGER DEFAULT 1"
                )

        else:
            # Table doesn't exist, create it
            logger.info("Migration v12: Creating flow_templates table...")
            cursor.execute("""
                CREATE TABLE flow_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    game_id INTEGER NOT NULL,
                    graph_data TEXT NOT NULL,
                    version INTEGER DEFAULT 1,
                    is_active INTEGER DEFAULT 1,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
                )
            """)

        # Create indexes
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_flow_templates_game_id
                ON flow_templates(game_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_flow_templates_updated_at
                ON flow_templates(updated_at)
            """)
        except Exception as e:
            logger.warning(f"Migration v12: Could not create indexes: {e}")

        logger.info("Migration v12 completed: flow templates support added")


class MigrationV13_EventNodesAndParameterAliases(BaseMigration):
    """迁移13：事件节点和参数别名支持"""

    version = 13

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        logger.info("Migration v13: Adding event_nodes and parameter_aliases tables...")

        # Create event_nodes table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='event_nodes'"
        )
        if not cursor.fetchone():
            logger.info("Migration v13: Creating event_nodes table...")
            cursor.execute("""
                CREATE TABLE event_nodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    event_id INTEGER NOT NULL,
                    config_json TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
                    FOREIGN KEY (event_id) REFERENCES log_events(id) ON DELETE CASCADE
                )
            """)

        # Create parameter_aliases table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='parameter_aliases'"
        )
        if not cursor.fetchone():
            logger.info("Migration v13: Creating parameter_aliases table...")
            cursor.execute("""
                CREATE TABLE parameter_aliases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id INTEGER NOT NULL,
                    param_id INTEGER NOT NULL,
                    alias TEXT NOT NULL,
                    display_name TEXT,
                    usage_count INTEGER DEFAULT 0,
                    last_used_at TIMESTAMP,
                    is_preferred INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
                    FOREIGN KEY (param_id) REFERENCES parameters(id) ON DELETE CASCADE,
                    UNIQUE(game_id, param_id, alias)
                )
            """)

        # Create indexes
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_event_nodes_game_id
                ON event_nodes(game_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_event_nodes_event_id
                ON event_nodes(event_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_parameter_aliases_game_id
                ON parameter_aliases(game_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_parameter_aliases_param_id
                ON parameter_aliases(param_id)
            """)
        except Exception as e:
            logger.warning(f"Migration v13: Could not create indexes: {e}")

        logger.info(
            "Migration v13 completed: event nodes and parameter aliases support added"
        )


class MigrationV14_FieldNameMappings(BaseMigration):
    """迁移14：字段名映射支持"""

    version = 14

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        logger.info("Migration v14: Adding field name mappings support...")

        # Create field_name_mappings table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='field_name_mappings'"
        )
        if not cursor.fetchone():
            logger.info("Migration v14: Creating field_name_mappings table...")
            cursor.execute("""
                CREATE TABLE field_name_mappings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id INTEGER NOT NULL,
                    param_name TEXT NOT NULL,
                    param_name_cn TEXT,
                    preferred_name TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(game_id, param_name),
                    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
                )
            """)

        # Create field_name_history table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='field_name_history'"
        )
        if not cursor.fetchone():
            logger.info("Migration v14: Creating field_name_history table...")
            cursor.execute("""
                CREATE TABLE field_name_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mapping_id INTEGER NOT NULL,
                    field_name TEXT NOT NULL,
                    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (mapping_id) REFERENCES field_name_mappings(id) ON DELETE CASCADE
                )
            """)

        # Create indexes
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_field_mappings_game_param
                ON field_name_mappings(game_id, param_name)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS field_name_history_mapping_id
                ON field_name_history(mapping_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS field_name_history_used_at
                ON field_name_history(used_at)
            """)
        except Exception as e:
            logger.warning(f"Migration v14: Could not create indexes: {e}")

        logger.info("Migration v14 completed: field name mappings support added")


class MigrationV15_EventNodeConfigs(BaseMigration):
    """迁移15：事件节点构建器配置"""

    version = 15

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        logger.info("Migration v15: Creating event_node_configs table...")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_node_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_gid INTEGER NOT NULL,
                name_en VARCHAR(200) NOT NULL,
                name_cn VARCHAR(200) NOT NULL,
                event_id INTEGER NOT NULL,
                base_fields TEXT,
                filter_conditions TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by VARCHAR(100),
                FOREIGN KEY (event_id) REFERENCES log_events(id)
            )
        """)

        # Create indexes for performance
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_event_node_game_gid
                ON event_node_configs(game_gid)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_event_node_name_en
                ON event_node_configs(name_en)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_event_node_event_id
                ON event_node_configs(event_id)
            """)
        except Exception as e:
            logger.warning(f"Migration v15: Could not create indexes: {e}")

        logger.info("Migration v15 completed: event node builder support added")


class MigrationV16_AsyncTasks(BaseMigration):
    """迁移16：异步任务系统"""

    version = 16

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        logger.info("Migration v16: Creating async_tasks table...")

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='async_tasks'"
        )
        if not cursor.fetchone():
            logger.info("Migration v16: Creating async_tasks table...")
            cursor.execute("""
                CREATE TABLE async_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT UNIQUE NOT NULL,
                    task_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    progress INTEGER DEFAULT 0,
                    result TEXT,
                    error_message TEXT,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)

            # Create indexes for async_tasks
            try:
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_async_tasks_task_id
                    ON async_tasks(task_id)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_async_tasks_status
                    ON async_tasks(status)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_async_tasks_created_at
                    ON async_tasks(created_at)
                """)
            except Exception as e:
                logger.warning(f"Migration v16: Could not create indexes: {e}")

        logger.info("Migration v16 completed: async task system support added")


class MigrationV17_CommonParamsDisplayName(BaseMigration):
    """迁移17：添加display_name列到common_params表"""

    version = 17

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        logger.info("Migration v17: Adding display_name column to common_params...")
        try:
            cursor.execute("PRAGMA table_info(common_params)")
            columns = [column[1] for column in cursor.fetchall()]

            if "display_name" not in columns:
                cursor.execute("ALTER TABLE common_params ADD COLUMN display_name TEXT")

                # Update existing records with default display names
                cursor.execute("""
                    UPDATE common_params
                    SET display_name = param_name_cn
                    WHERE display_name IS NULL
                """)
                logger.info("Migration v17: display_name column added")
            else:
                logger.info("Migration v17: display_name column already exists")
        except Exception as e:
            logger.warning(f"Migration v17: Could not add display_name column: {e}")

        logger.info("Migration v17 completed: common_params display_name support added")


class MigrationV18_AddGameGid(BaseMigration):
    """迁移18：添加game_gid列到log_events表并迁移数据"""

    version = 18

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        logger.info("Migration v18: Adding game_gid column to log_events...")

        try:
            cursor.execute("PRAGMA table_info(log_events)")
            columns = [column[1] for column in cursor.fetchall()]

            if "game_gid" not in columns:
                logger.info("Migration v18: Adding game_gid column to log_events...")
                cursor.execute("ALTER TABLE log_events ADD COLUMN game_gid INTEGER")

                # Migrate existing data: copy game_id to game_gid by joining with games table
                logger.info("Migration v18: Migrating existing data to game_gid...")
                cursor.execute("""
                    UPDATE log_events
                        SET game_gid = (
                            SELECT g.gid
                            FROM games g
                            WHERE g.id = log_events.game_id
                        )
                """)

                # Create index on game_gid
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_log_events_game_gid
                        ON log_events(game_gid)
                """)

                logger.info("Migration v18: game_gid column added and data migrated")
            else:
                logger.info("Migration v18: game_gid column already exists")

        except Exception as e:
            logger.warning(f"Migration v18: Could not add game_gid column: {e}")

        logger.info("Migration v18 completed: log_events game_gid support added")


# ... 其他迁移类可以类似方式添加 ...
# 为了简洁，这里只实现前3个迁移来满足测试


class MigrationRunner:
    """迁移运行器"""

    def __init__(self, db_path: str):
        """
        初始化迁移运行器

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.registry = get_migration_registry()

    def get_current_version(self) -> int:
        """
        获取当前数据库版本

        Returns:
            当前版本号
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA user_version")
        version = cursor.fetchone()[0]
        conn.close()

        return version

    def migrate_to_version(self, target_version: int):
        """
        迁移到指定版本

        Args:
            target_version: 目标版本号
        """
        current_version = self.get_current_version()

        if current_version >= target_version:
            logger.info(f"Database is already at version {current_version}")
            return

        logger.info(
            f"Migrating database from version {current_version} to {target_version}..."
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            for version in range(current_version + 1, target_version + 1):
                if version in self.registry:
                    migration = self.registry[version]
                    logger.info(f"Applying migration v{version}...")
                    migration.upgrade(cursor, conn)

                    # Update version (PRAGMA doesn't support parameters in SQLite)
                    cursor.execute(f"PRAGMA user_version = {version}")
                    conn.commit()
                    logger.info(f"Migration v{version} completed")

        finally:
            conn.close()


def get_migration_registry() -> dict:
    """
    获取迁移注册表

    Returns:
        版本号到迁移类的映射字典
    """
    return {
        1: MigrationV1_AddCategoryId(),
        2: MigrationV2_EventCategoryRelations(),
        3: MigrationV3_IncludeInCommonParams(),
        4: MigrationV4_IconPath(),
        5: MigrationV5_EditTracking(),
        6: MigrationV6_ParameterManagementRefactoring(),
        7: MigrationV7_ParameterValidationAndBatchOperations(),
        8: MigrationV8_ParameterDependencies(),
        9: MigrationV9_EnhancedHQLGeneration(),
        10: MigrationV10_ArrayParameterHierarchy(),
        11: MigrationV11_FieldBuilderSupport(),
        12: MigrationV12_FlowTemplates(),
        13: MigrationV13_EventNodesAndParameterAliases(),
        14: MigrationV14_FieldNameMappings(),
        15: MigrationV15_EventNodeConfigs(),
        16: MigrationV16_AsyncTasks(),
        17: MigrationV17_CommonParamsDisplayName(),
        18: MigrationV18_AddGameGid(),
    }


def migrate_db(db_path: Optional[Path] = None):
    """
    Migrate existing database to new schema

    Args:
        db_path: Optional database path. If not provided, uses get_db_path()
    """
    if db_path is None:
        db_path = get_db_path()

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # Check if database is empty (no tables)
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]

        # If database is empty, initialize it first
        if table_count == 0:
            logger.info("Database is empty, initializing...")
            # Initialize database with the provided db_path
            # Close current connection first as init_db() will create its own
            conn.close()
            init_db(db_path)
            # Reopen connection for migrations
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            # Re-query to get the actual table count after initialization
            cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            logger.info(f"Initialized database with {table_count} tables")

        # Get current database version
        cursor.execute("PRAGMA user_version")
        current_version = cursor.fetchone()[0]
        target_version = 20  # Increment this for each migration

        if current_version >= target_version:
            logger.info(f"Database is up to date (version {current_version})")
            conn.close()
            return

        logger.info(
            f"Migrating database from version {current_version} to {target_version}..."
        )

        # Migration 1: Add category_id column to log_events
        if current_version < 1:
            cursor.execute("PRAGMA table_info(log_events)")
            columns = [column[1] for column in cursor.fetchall()]

            if "category_id" not in columns:
                logger.info("Migration v1: Adding category_id column to log_events...")
                cursor.execute("ALTER TABLE log_events ADD COLUMN category_id INTEGER")

                # Create a default category if it doesn't exist
                cursor.execute(
                    'INSERT OR IGNORE INTO event_categories (name) VALUES ("默认分类")'
                )
                cursor.execute(
                    'SELECT id FROM event_categories WHERE name = "默认分类"'
                )
                default_category = cursor.fetchone()

                # Update existing records with default category
                if default_category:
                    cursor.execute(
                        "UPDATE log_events SET category_id = ?", (default_category[0],)
                    )

                logger.info(
                    "Migration v1 completed: category_id column added to log_events"
                )

        # Migration 2: Add event_category_relations table
        if current_version < 2:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='event_category_relations'"
            )
            if not cursor.fetchone():
                logger.info("Migration v2: Adding event_category_relations table...")
                cursor.execute("""
                    CREATE TABLE event_category_relations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_id INTEGER NOT NULL,
                        category_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (event_id) REFERENCES log_events(id) ON DELETE CASCADE,
                        FOREIGN KEY (category_id) REFERENCES event_categories(id) ON DELETE CASCADE,
                        UNIQUE(event_id, category_id)
                    )
                """)
                logger.info(
                    "Migration v2 completed: event_category_relations table added"
                )

        # Migration 3: Add include_in_common_params column to log_events
        if current_version < 3:
            cursor.execute("PRAGMA table_info(log_events)")
            columns = [column[1] for column in cursor.fetchall()]

            if "include_in_common_params" not in columns:
                logger.info(
                    "Migration v3: Adding include_in_common_params column to log_events..."
                )
                cursor.execute(
                    "ALTER TABLE log_events ADD COLUMN include_in_common_params INTEGER DEFAULT 1"
                )
                logger.info(
                    "Migration v3 completed: include_in_common_params column added to log_events"
                )

        # Migration 4: Add icon_path column to games table
        if current_version < 4:
            cursor.execute("PRAGMA table_info(games)")
            columns = [column[1] for column in cursor.fetchall()]

            if "icon_path" not in columns:
                logger.info("Migration v4: Adding icon_path column to games...")
                cursor.execute("ALTER TABLE games ADD COLUMN icon_path TEXT")
                logger.info("Migration v4 completed: icon_path column added to games")

        # Migration 5: Add edit tracking fields to hql_statements
        if current_version < 5:
            cursor.execute("PRAGMA table_info(hql_statements)")
            columns = [column[1] for column in cursor.fetchall()]

            # 添加编辑追踪字段
            if "is_user_edited" not in columns:
                logger.info("Migration v5: Adding is_user_edited column...")
                cursor.execute(
                    "ALTER TABLE hql_statements ADD COLUMN is_user_edited INTEGER DEFAULT 0"
                )

            if "edit_notes" not in columns:
                logger.info("Migration v5: Adding edit_notes column...")
                cursor.execute("ALTER TABLE hql_statements ADD COLUMN edit_notes TEXT")

            if "original_content" not in columns:
                logger.info("Migration v5: Adding original_content column...")
                cursor.execute(
                    "ALTER TABLE hql_statements ADD COLUMN original_content TEXT"
                )

            conn.commit()
            logger.info(
                "Migration v5 completed: edit tracking fields added to hql_statements"
            )

        # Migration 6: Parameter management refactoring
        if current_version < 6:
            logger.info("Migration v6: Starting parameter management refactoring...")

            # 1. Create param_templates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS param_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_name TEXT NOT NULL UNIQUE,
                    display_name TEXT NOT NULL,
                    base_type TEXT NOT NULL,
                    element_type TEXT,
                    nesting_level INTEGER DEFAULT 1,
                    type_definition TEXT NOT NULL,
                    hql_parse_template TEXT NOT NULL,
                    description TEXT,
                    is_system INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.info("Migration v6: param_templates table created")

            # 2. Insert predefined type templates
            templates_data = [
                (
                    "string",
                    "字符串",
                    "string",
                    None,
                    1,
                    '{"type": "primitive"}',
                    "get_json_object(params, '$.{param_name}')",
                    "基础字符串类型",
                ),
                (
                    "int",
                    "整数",
                    "int",
                    None,
                    1,
                    '{"type": "primitive"}',
                    "CAST(get_json_object(params, '$.{param_name}') AS INT)",
                    "基础整数类型",
                ),
                (
                    "bigint",
                    "长整数",
                    "bigint",
                    None,
                    1,
                    '{"type": "primitive"}',
                    "CAST(get_json_object(params, '$.{param_name}') AS BIGINT)",
                    "长整型",
                ),
                (
                    "float",
                    "浮点数",
                    "float",
                    None,
                    1,
                    '{"type": "primitive"}',
                    "CAST(get_json_object(params, '$.{param_name}') AS FLOAT)",
                    "浮点数类型",
                ),
                (
                    "boolean",
                    "布尔值",
                    "boolean",
                    None,
                    1,
                    '{"type": "primitive"}',
                    "CAST(get_json_object(params, '$.{param_name}') AS BOOLEAN)",
                    "布尔类型",
                ),
                (
                    "array<string>",
                    "字符串数组",
                    "array",
                    "string",
                    1,
                    '{"type": "array", "element_type": "string"}',
                    "get_json_object(params, '$.{param_name}')",
                    "字符串数组",
                ),
                (
                    "array<int>",
                    "整数数组",
                    "array",
                    "int",
                    1,
                    '{"type": "array", "element_type": "int"}',
                    "get_json_object(params, '$.{param_name}')",
                    "整数数组",
                ),
                (
                    "array<float>",
                    "浮点数组",
                    "array",
                    "float",
                    1,
                    '{"type": "array", "element_type": "float"}',
                    "get_json_object(params, '$.{param_name}')",
                    "浮点数数组",
                ),
                (
                    "array<map>",
                    "Map数组",
                    "array",
                    "map",
                    2,
                    '{"type": "array", "element_type": "map"}',
                    "get_json_object(params, '$.{param_name}')",
                    "包含Map的数组",
                ),
                (
                    "map",
                    "Map对象",
                    "map",
                    None,
                    1,
                    '{"type": "map"}',
                    "get_json_object(params, '$.{param_name}')",
                    "Map对象",
                ),
            ]

            cursor.executemany(
                """
                INSERT OR IGNORE INTO param_templates
                (template_name, display_name, base_type, element_type, nesting_level,
                 type_definition, hql_parse_template, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                templates_data,
            )
            logger.info("Migration v6: predefined type templates inserted")

            # 3. Create param_library table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS param_library (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    param_name TEXT NOT NULL,
                    param_name_cn TEXT NOT NULL,
                    template_id INTEGER NOT NULL,
                    param_description TEXT,
                    category TEXT,
                    is_standard INTEGER DEFAULT 0,
                    usage_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (template_id) REFERENCES param_templates(id),
                    UNIQUE(param_name)
                )
            """)
            logger.info("Migration v6: param_library table created")

            # 4. Create event_params table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS event_params (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER NOT NULL,
                    library_id INTEGER,
                    param_name TEXT NOT NULL,
                    param_name_cn TEXT,
                    template_id INTEGER NOT NULL,
                    param_description TEXT,
                    hql_config TEXT,
                    is_from_library INTEGER DEFAULT 0,
                    version INTEGER DEFAULT 1,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (event_id) REFERENCES log_events(id) ON DELETE CASCADE,
                    FOREIGN KEY (library_id) REFERENCES param_library(id) ON DELETE SET NULL,
                    FOREIGN KEY (template_id) REFERENCES param_templates(id),
                    UNIQUE(event_id, param_name, version)
                )
            """)
            logger.info("Migration v6: event_params table created")

            # 5. Create param_versions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS param_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_param_id INTEGER NOT NULL,
                    version INTEGER NOT NULL,
                    param_name TEXT NOT NULL,
                    param_name_cn TEXT,
                    template_id INTEGER NOT NULL,
                    param_description TEXT,
                    hql_config TEXT,
                    change_reason TEXT,
                    changed_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (event_param_id) REFERENCES event_params(id) ON DELETE CASCADE,
                    FOREIGN KEY (template_id) REFERENCES param_templates(id)
                )
            """)
            logger.info("Migration v6: param_versions table created")

            # 6. Create param_configs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS param_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_param_id INTEGER NOT NULL UNIQUE,
                    parse_mode TEXT DEFAULT 'json_extract',
                    explode_config TEXT,
                    array_element_delimiter TEXT DEFAULT ',',
                    map_key_value_delimiter TEXT DEFAULT ':',
                    custom_hql_template TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (event_param_id) REFERENCES event_params(id) ON DELETE CASCADE
                )
            """)
            logger.info("Migration v6: param_configs table created")

            # 7. Migrate existing parameters to event_params
            # First, get the default string template ID
            cursor.execute(
                'SELECT id FROM param_templates WHERE template_name = "string" LIMIT 1'
            )
            default_template = cursor.fetchone()
            default_template_id = default_template[0] if default_template else None

            # Migrate parameters, using default template for unknown types
            cursor.execute(
                """
                INSERT INTO event_params
                (event_id, param_name, param_name_cn, template_id, param_description,
                 is_from_library, version, is_active, created_at, updated_at)
                SELECT
                    p.event_id,
                    p.param_name,
                    p.param_name_cn,
                    COALESCE(
                        (SELECT id FROM param_templates WHERE template_name = p.param_type LIMIT 1),
                        ?
                    ),
                    p.param_description,
                    0,
                    1,
                    1,
                    p.created_at,
                    p.created_at
                FROM parameters p
                WHERE NOT EXISTS (
                    SELECT 1 FROM event_params ep
                    WHERE ep.event_id = p.event_id AND ep.param_name = p.param_name
                )
            """,
                (default_template_id,),
            )
            migrated_count = cursor.rowcount
            logger.info(
                f"Migration v6: migrated {migrated_count} parameters from parameters table"
            )

            # 8. Extract common parameters to param_library
            # Use INSERT OR IGNORE to skip duplicate param_name conflicts
            cursor.execute("""
                INSERT OR IGNORE INTO param_library
                (param_name, param_name_cn, template_id, param_description,
                 category, is_standard, usage_count)
                SELECT
                    param_name,
                    param_name_cn,
                    template_id,
                    param_description,
                    'auto_extracted',
                    0,
                    COUNT(*) as usage_count
                FROM event_params
                WHERE library_id IS NULL
                GROUP BY param_name, param_name_cn, template_id, param_description
                HAVING COUNT(*) >= 2
            """)
            extracted_count = cursor.rowcount
            logger.info(
                f"Migration v6: extracted {extracted_count} common parameters to library"
            )

            # 9. Mark parameters from library
            cursor.execute("""
                UPDATE event_params
                SET library_id = (
                    SELECT id FROM param_library
                    WHERE param_library.param_name = event_params.param_name
                    LIMIT 1
                ),
                is_from_library = 1
                WHERE EXISTS (
                    SELECT 1 FROM param_library
                    WHERE param_library.param_name = event_params.param_name
                )
            """)
            marked_count = cursor.rowcount
            logger.info(
                f"Migration v6: marked {marked_count} parameters as from library"
            )

            # 10. Rename old table (keep for rollback)
            # Check if old backup already exists to avoid conflicts
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='parameters_old_v5'
            """)
            old_backup_exists = cursor.fetchone() is not None

            if old_backup_exists:
                # Table already renamed, drop it to avoid conflicts
                cursor.execute("DROP TABLE IF EXISTS parameters_old_v5")
                logger.info("Migration v6: dropped existing parameters_old_v5 table")

            cursor.execute("""
                ALTER TABLE parameters RENAME TO parameters_old_v5
            """)
            logger.info(
                "Migration v6: renamed old parameters table to parameters_old_v5"
            )

            conn.commit()
            logger.info(
                "Migration v6 completed: parameter management refactoring finished"
            )

        # Migration v7: Parameter validation rules and batch operations
        if current_version < 7:
            logger.info(
                "Migration v7: Starting parameter validation and batch operations..."
            )

            # 1. Create param_validation_rules table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS param_validation_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_param_id INTEGER NOT NULL UNIQUE,
                    rule_type TEXT NOT NULL,
                    rule_config TEXT NOT NULL,
                    error_message TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (event_param_id) REFERENCES event_params(id) ON DELETE CASCADE
                )
            """)
            logger.info("Migration v7: created param_validation_rules table")

            # 2. Create batch_import_records table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS batch_import_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    import_name TEXT NOT NULL,
                    import_type TEXT NOT NULL,
                    total_rows INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    failed_count INTEGER DEFAULT 0,
                    error_summary TEXT,
                    file_path TEXT,
                    status TEXT DEFAULT 'pending',
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)
            logger.info("Migration v7: created batch_import_records table")

            # 3. Create batch_import_details table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS batch_import_details (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    import_id INTEGER NOT NULL,
                    row_number INTEGER NOT NULL,
                    data_type TEXT,
                    action TEXT,
                    entity_id INTEGER,
                    status TEXT,
                    error_message TEXT,
                    FOREIGN KEY (import_id) REFERENCES batch_import_records(id) ON DELETE CASCADE
                )
            """)
            logger.info("Migration v7: created batch_import_details table")

            # 4. Create indexes for validation rules
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_validation_rules_param_id
                ON param_validation_rules(event_param_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_validation_rules_type
                ON param_validation_rules(rule_type)
            """)
            logger.info("Migration v7: created indexes for param_validation_rules")

            # 5. Create indexes for batch imports
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_batch_import_records_status
                ON batch_import_records(status)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_batch_import_details_import_id
                ON batch_import_details(import_id)
            """)
            logger.info("Migration v7: created indexes for batch_import tables")

            conn.commit()
            logger.info(
                "Migration v7 completed: validation rules and batch operations created"
            )

        # Migration v8: Parameter dependencies
        if current_version < 8:
            logger.info("Migration v8: Starting parameter dependencies...")

            # Create param_dependencies table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS param_dependencies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER NOT NULL,
                    dependent_param_id INTEGER NOT NULL,
                    depends_on_param_id INTEGER NOT NULL,
                    dependency_type TEXT NOT NULL,
                    condition TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (event_id) REFERENCES log_events(id) ON DELETE CASCADE,
                    FOREIGN KEY (dependent_param_id) REFERENCES event_params(id) ON DELETE CASCADE,
                    FOREIGN KEY (depends_on_param_id) REFERENCES event_params(id) ON DELETE CASCADE,
                    UNIQUE(event_id, dependent_param_id, depends_on_param_id)
                )
            """)
            logger.info("Migration v8: created param_dependencies table")

            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_param_dependencies_event_id
                ON param_dependencies(event_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_param_dependencies_dependent
                ON param_dependencies(dependent_param_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_param_dependencies_depends_on
                ON param_dependencies(depends_on_param_id)
            """)
            logger.info("Migration v8: created indexes for param_dependencies")

            conn.commit()
            logger.info("Migration v8 completed: parameter dependencies created")

        # Migration 9: Enhanced HQL generation
        if current_version < 9:
            logger.info("Migration v9: Enhanced HQL generation features...")

            # 1. Add new columns to join_configs table
            cursor.execute("PRAGMA table_info(join_configs)")
            columns = [column[1] for column in cursor.fetchall()]

            if "join_type" not in columns:
                logger.info("Migration v9: Adding join_type column to join_configs...")
                cursor.execute(
                    "ALTER TABLE join_configs ADD COLUMN join_type TEXT DEFAULT 'join'"
                )

            if "where_conditions" not in columns:
                logger.info(
                    "Migration v9: Adding where_conditions column to join_configs..."
                )
                cursor.execute(
                    "ALTER TABLE join_configs ADD COLUMN where_conditions TEXT"
                )

            if "field_mappings" not in columns:
                logger.info(
                    "Migration v9: Adding field_mappings column to join_configs..."
                )
                cursor.execute(
                    "ALTER TABLE join_configs ADD COLUMN field_mappings TEXT"
                )

            if "description" not in columns:
                logger.info(
                    "Migration v9: Adding description column to join_configs..."
                )
                cursor.execute("ALTER TABLE join_configs ADD COLUMN description TEXT")

            if "game_id" not in columns:
                logger.info("Migration v9: Adding game_id column to join_configs...")
                cursor.execute("ALTER TABLE join_configs ADD COLUMN game_id INTEGER")

            # 2. Migrate existing join_configs to new format
            logger.info(
                "Migration v9: Migrating existing join_configs to new format..."
            )
            cursor.execute("""
                UPDATE join_configs
                SET join_type = 'join',
                    where_conditions = '{}',
                    field_mappings = '{}',
                    description = COALESCE(display_name, name),
                    game_id = (
                        SELECT game_id FROM log_events WHERE id = CAST(
                            json_extract(source_events, '$[0]') AS INTEGER
                        ) LIMIT 1
                    )
                WHERE join_type IS NULL
            """)
            affected_rows = cursor.rowcount
            logger.info(
                f"Migration v9: Migrated {affected_rows} existing join_configs to new format"
            )

            # 3. Create hql_generation_templates table
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='hql_generation_templates'"
            )
            if not cursor.fetchone():
                logger.info("Migration v9: Creating hql_generation_templates table...")
                cursor.execute("""
                    CREATE TABLE hql_generation_templates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        template_name TEXT NOT NULL UNIQUE,
                        display_name TEXT NOT NULL,
                        template_type TEXT NOT NULL,
                        template_content TEXT NOT NULL,
                        variables TEXT,
                        description TEXT,
                        is_system INTEGER DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Insert default templates
                cursor.executemany(
                    """
                    INSERT OR IGNORE INTO hql_generation_templates
                    (template_name, display_name, template_type, template_content, description, is_system)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    [
                        (
                            "union_all_basic",
                            "Basic UNION ALL",
                            "union_all",
                            "-- UNION ALL template for combining events",
                            "Basic UNION ALL template",
                            1,
                        ),
                        (
                            "join_inner",
                            "INNER JOIN",
                            "join",
                            "-- INNER JOIN template",
                            "Inner join template",
                            1,
                        ),
                        (
                            "join_left",
                            "LEFT JOIN",
                            "join",
                            "-- LEFT JOIN template",
                            "Left join template",
                            1,
                        ),
                        (
                            "where_in_filter",
                            "WHERE IN Filter",
                            "where_in",
                            "-- WHERE IN filter template",
                            "WHERE IN filter template",
                            1,
                        ),
                        (
                            "where_filter",
                            "WHERE Condition Builder",
                            "where",
                            "-- WHERE condition template",
                            "WHERE condition template",
                            1,
                        ),
                    ],
                )
                logger.info(
                    "Migration v9: hql_generation_templates table created with default templates"
                )

            # 4. Create field_selection_presets table
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='field_selection_presets'"
            )
            if not cursor.fetchone():
                logger.info("Migration v9: Creating field_selection_presets table...")
                cursor.execute("""
                    CREATE TABLE field_selection_presets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        preset_name TEXT NOT NULL,
                        display_name TEXT NOT NULL,
                        game_id INTEGER,
                        field_list TEXT NOT NULL,
                        is_default INTEGER DEFAULT 0,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
                    )
                """)
                logger.info("Migration v9: field_selection_presets table created")

            # 5. Create indexes for new columns
            logger.info("Migration v9: Creating indexes for enhanced HQL generation...")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_join_configs_join_type ON join_configs(join_type)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_join_configs_game_id ON join_configs(game_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_join_configs_description ON join_configs(description)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_field_presets_game_id ON field_selection_presets(game_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_field_presets_is_default ON field_selection_presets(is_default)"
            )
            logger.info("Migration v9: indexes created")

            conn.commit()
            logger.info(
                "Migration v9 completed: Enhanced HQL generation features added"
            )

        # Migration v10: Array参数层级结构优化
        if current_version < 10:
            logger.info("Migration v10: Adding array parameter hierarchy support...")

            # 1. 扩展param_configs表
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='param_configs'"
            )
            if cursor.fetchone():
                cursor.execute("PRAGMA table_info(param_configs)")
                columns = [column[1] for column in cursor.fetchall()]

                if "child_params" not in columns:
                    logger.info(
                        "Migration v10: Adding child_params column to param_configs..."
                    )
                    cursor.execute(
                        "ALTER TABLE param_configs ADD COLUMN child_params TEXT"
                    )

                if "array_element_structure" not in columns:
                    logger.info(
                        "Migration v10: Adding array_element_structure column to param_configs..."
                    )
                    cursor.execute(
                        "ALTER TABLE param_configs ADD COLUMN array_element_structure TEXT"
                    )

                logger.info(
                    "Migration v10: param_configs table extended with hierarchy fields"
                )

            # 2. 创建索引优化查询
            logger.info("Migration v10: Creating indexes for parameter hierarchy...")
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_event_params_event_template
                ON event_params(event_id, template_id)
            """)
            logger.info("Migration v10: index idx_event_params_event_template created")

            conn.commit()
            logger.info(
                "Migration v10 completed: array parameter hierarchy support added"
            )

        # Migration v11: Phase 1 - Field Builder Support
        if current_version < 11:
            logger.info("Migration v11: Adding field builder support...")

            # 1. 添加 field_mapping_v2 列到 join_configs 表
            cursor.execute("PRAGMA table_info(join_configs)")
            columns = [column[1] for column in cursor.fetchall()]

            if "field_mapping_v2" not in columns:
                logger.info(
                    "Migration v11: Adding field_mapping_v2 column to join_configs..."
                )
                cursor.execute(
                    "ALTER TABLE join_configs ADD COLUMN field_mapping_v2 TEXT"
                )
                logger.info("Migration v11: field_mapping_v2 column added")

            # 2. 创建 node_templates 表(为阶段2准备)
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='node_templates'"
            )
            if not cursor.fetchone():
                logger.info("Migration v11: Creating node_templates table...")
                cursor.execute("""
                    CREATE TABLE node_templates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        node_name TEXT NOT NULL,
                        node_type TEXT NOT NULL,
                        node_config TEXT NOT NULL,
                        description TEXT,
                        created_by TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                logger.info("Migration v11: node_templates table created")

            # 3. 创建 flow_templates 表(为阶段2准备)
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='flow_templates'"
            )
            if not cursor.fetchone():
                logger.info("Migration v11: Creating flow_templates table...")
                cursor.execute("""
                    CREATE TABLE flow_templates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        flow_name TEXT NOT NULL,
                        flow_graph TEXT NOT NULL,
                        variables TEXT,
                        description TEXT,
                        created_by TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                logger.info("Migration v11: flow_templates table created")

            # 4. 创建索引优化查询性能
            logger.info(
                "Migration v11: Creating indexes for node and flow templates..."
            )
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_node_templates_type
                ON node_templates(node_type)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_node_templates_created_by
                ON node_templates(created_by)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_flow_templates_created_by
                ON flow_templates(created_by)
            """)
            logger.info("Migration v11: indexes created")

            # 5. 创建 field_mapping_v2 索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_join_configs_field_mapping_v2
                ON join_configs(field_mapping_v2)
            """)
            logger.info("Migration v11: field_mapping_v2 index created")

            conn.commit()
            logger.info("Migration v11 completed: field builder support added")

        # Migration 12: Add flow_templates table for node canvas
        if current_version < 12:
            logger.info("Migration v12: Adding flow_templates table...")

            # Check if table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='flow_templates'"
            )
            table_exists = cursor.fetchone() is not None

            if table_exists:
                # Table exists, check if we need to add columns
                logger.info(
                    "Migration v12: flow_templates table exists, checking structure..."
                )
                cursor.execute("PRAGMA table_info(flow_templates)")
                columns = {column[1] for column in cursor.fetchall()}

                # Add missing columns if needed
                if "game_id" not in columns:
                    logger.info("Migration v12: Adding game_id column...")
                    cursor.execute(
                        "ALTER TABLE flow_templates ADD COLUMN game_id INTEGER"
                    )
                    # Set default game_id for existing records (use game 1 as default)
                    cursor.execute(
                        "UPDATE flow_templates SET game_id = 1 WHERE game_id IS NULL"
                    )
                    logger.info("Migration v12: game_id column added")

                if "is_active" not in columns:
                    logger.info("Migration v12: Adding is_active column...")
                    cursor.execute(
                        "ALTER TABLE flow_templates ADD COLUMN is_active INTEGER DEFAULT 1"
                    )
                    logger.info("Migration v12: is_active column added")

                if "version" not in columns:
                    logger.info("Migration v12: Adding version column...")
                    cursor.execute(
                        "ALTER TABLE flow_templates ADD COLUMN version INTEGER DEFAULT 1"
                    )
                    logger.info("Migration v12: version column added")

                # Rename flow_name to name if needed
                if "flow_name" in columns and "name" not in columns:
                    # SQLite doesn't support RENAME COLUMN directly, need to recreate table
                    # For now, we'll just add the name column
                    logger.info(
                        "Migration v12: Adding name column (alongside flow_name)..."
                    )
                    cursor.execute("ALTER TABLE flow_templates ADD COLUMN name TEXT")
                    cursor.execute(
                        "UPDATE flow_templates SET name = flow_name WHERE name IS NULL"
                    )
                    logger.info("Migration v12: name column added")

            else:
                # Table doesn't exist, create it
                logger.info("Migration v12: Creating flow_templates table...")
                cursor.execute("""
                    CREATE TABLE flow_templates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT,
                        game_id INTEGER NOT NULL,
                        graph_data TEXT NOT NULL,
                        version INTEGER DEFAULT 1,
                        is_active INTEGER DEFAULT 1,
                        created_by TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
                    )
                """)
                logger.info("Migration v12: flow_templates table created")

            # Create indexes (safe to run if they exist)
            try:
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_flow_templates_game_id
                    ON flow_templates(game_id)
                """)
                logger.info("Migration v12: game_id index created")
            except Exception as e:
                logger.warning(f"Migration v12: Could not create game_id index: {e}")

            try:
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_flow_templates_updated_at
                    ON flow_templates(updated_at)
                """)
                logger.info("Migration v12: updated_at index created")
            except Exception as e:
                logger.warning(f"Migration v12: Could not create updated_at index: {e}")

            conn.commit()
            logger.info("Migration v12 completed: flow templates support added")

        # Migration 13: Add event_nodes and parameter_aliases tables
        if current_version < 13:
            logger.info(
                "Migration v13: Adding event_nodes and parameter_aliases tables..."
            )

            # Create event_nodes table
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='event_nodes'"
            )
            if not cursor.fetchone():
                logger.info("Migration v13: Creating event_nodes table...")
                cursor.execute("""
                    CREATE TABLE event_nodes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        game_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        event_id INTEGER NOT NULL,
                        config_json TEXT NOT NULL,
                        is_active INTEGER DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
                        FOREIGN KEY (event_id) REFERENCES log_events(id) ON DELETE CASCADE
                    )
                """)
                logger.info("Migration v13: event_nodes table created")

            # Create parameter_aliases table
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='parameter_aliases'"
            )
            if not cursor.fetchone():
                logger.info("Migration v13: Creating parameter_aliases table...")
                cursor.execute("""
                    CREATE TABLE parameter_aliases (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        game_id INTEGER NOT NULL,
                        param_id INTEGER NOT NULL,
                        alias TEXT NOT NULL,
                        display_name TEXT,
                        usage_count INTEGER DEFAULT 0,
                        last_used_at TIMESTAMP,
                        is_preferred INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
                        FOREIGN KEY (param_id) REFERENCES parameters(id) ON DELETE CASCADE,
                        UNIQUE(game_id, param_id, alias)
                    )
                """)
                logger.info("Migration v13: parameter_aliases table created")

            # Create indexes
            try:
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_event_nodes_game_id
                    ON event_nodes(game_id)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_event_nodes_event_id
                    ON event_nodes(event_id)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_parameter_aliases_game_id
                    ON parameter_aliases(game_id)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_parameter_aliases_param_id
                    ON parameter_aliases(param_id)
                """)
                logger.info("Migration v13: indexes created")
            except Exception as e:
                logger.warning(f"Migration v13: Could not create indexes: {e}")

            conn.commit()
            logger.info(
                "Migration v13 completed: event nodes and parameter aliases support added"
            )

        # Migration 14: Add field_name_mappings and field_name_history tables
        if current_version < 14:
            logger.info("Migration v14: Adding field name mappings support...")

            # Create field_name_mappings table
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='field_name_mappings'"
            )
            if not cursor.fetchone():
                logger.info("Migration v14: Creating field_name_mappings table...")
                cursor.execute("""
                    CREATE TABLE field_name_mappings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        game_id INTEGER NOT NULL,
                        param_name TEXT NOT NULL,
                        param_name_cn TEXT,
                        preferred_name TEXT NOT NULL,
                        usage_count INTEGER DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(game_id, param_name),
                        FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
                    )
                """)
                logger.info("Migration v14: field_name_mappings table created")

            # Create field_name_history table
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='field_name_history'"
            )
            if not cursor.fetchone():
                logger.info("Migration v14: Creating field_name_history table...")
                cursor.execute("""
                    CREATE TABLE field_name_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        mapping_id INTEGER NOT NULL,
                        field_name TEXT NOT NULL,
                        used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (mapping_id) REFERENCES field_name_mappings(id) ON DELETE CASCADE
                    )
                """)
                logger.info("Migration v14: field_name_history table created")

            # Create indexes for field name mappings
            try:
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_field_mappings_game_param
                    ON field_name_mappings(game_id, param_name)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS field_name_history_mapping_id
                    ON field_name_history(mapping_id)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS field_name_history_used_at
                    ON field_name_history(used_at)
                """)
                logger.info("Migration v14: indexes created")
            except Exception as e:
                logger.warning(f"Migration v14: Could not create indexes: {e}")

            conn.commit()
            logger.info("Migration v14 completed: field name mappings support added")

        # Migration v15: Event node builder configurations
        if current_version < 15:
            logger.info("Migration v15: Creating event_node_configs table...")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS event_node_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_gid INTEGER NOT NULL,
                    name_en VARCHAR(200) NOT NULL,
                    name_cn VARCHAR(200) NOT NULL,
                    event_id INTEGER NOT NULL,
                    base_fields TEXT,
                    filter_conditions TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(100),
                    FOREIGN KEY (event_id) REFERENCES log_events(id)
                )
            """)
            logger.info("Migration v15: created event_node_configs table")

            # Create indexes for performance
            try:
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_event_node_game_gid
                    ON event_node_configs(game_gid)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_event_node_name_en
                    ON event_node_configs(name_en)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_event_node_event_id
                    ON event_node_configs(event_id)
                """)
                logger.info("Migration v15: indexes created")
            except Exception as e:
                logger.warning(f"Migration v15: Could not create indexes: {e}")

            conn.commit()
            logger.info("Migration v15 completed: event node builder support added")

        # Migration v16: 异步任务系统（事件节点复制优化）
        if current_version < 16:
            logger.info("Migration v16: Creating async_tasks table...")

            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='async_tasks'"
            )
            if not cursor.fetchone():
                logger.info("Migration v16: Creating async_tasks table...")
                cursor.execute("""
                    CREATE TABLE async_tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task_id TEXT UNIQUE NOT NULL,
                        task_type TEXT NOT NULL,
                        status TEXT NOT NULL,
                        progress INTEGER DEFAULT 0,
                        result TEXT,
                        error_message TEXT,
                        created_by TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        started_at TIMESTAMP,
                        completed_at TIMESTAMP
                    )
                """)
                logger.info("Migration v16: async_tasks table created")

            # Create indexes for async_tasks
            try:
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_async_tasks_task_id
                    ON async_tasks(task_id)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_async_tasks_status
                    ON async_tasks(status)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_async_tasks_created_at
                    ON async_tasks(created_at)
                """)
                logger.info("Migration v16: async_tasks indexes created")
            except Exception as e:
                logger.warning(f"Migration v16: Could not create indexes: {e}")

            conn.commit()
            logger.info("Migration v16 completed: async task system support added")

        # Migration 17: Add display_name column to common_params
        if current_version < 17:
            logger.info("Migration v17: Adding display_name column to common_params...")
            try:
                cursor.execute("PRAGMA table_info(common_params)")
                columns = [column[1] for column in cursor.fetchall()]

                if "display_name" not in columns:
                    cursor.execute(
                        "ALTER TABLE common_params ADD COLUMN display_name TEXT"
                    )

                    # Update existing records with default display names
                    cursor.execute("""
                        UPDATE common_params
                        SET display_name = param_name_cn
                        WHERE display_name IS NULL
                    """)
                    logger.info("Migration v17: display_name column added")
                else:
                    logger.info("Migration v17: display_name column already exists")
            except Exception as e:
                logger.warning(f"Migration v17: Could not add display_name column: {e}")

            conn.commit()
            logger.info(
                "Migration v17 completed: common_params display_name support added"
            )

        # Migration 18: Add game_gid column to log_events table
        if current_version < 18:
            logger.info("Migration v18: Adding game_gid column to log_events...")

            try:
                cursor.execute("PRAGMA table_info(log_events)")
                columns = [column[1] for column in cursor.fetchall()]

                if "game_gid" not in columns:
                    logger.info(
                        "Migration v18: Adding game_gid column to log_events..."
                    )
                    cursor.execute("ALTER TABLE log_events ADD COLUMN game_gid INTEGER")

                    # Migrate existing data: copy game_id to game_gid by joining with games table
                    logger.info("Migration v18: Migrating existing data to game_gid...")
                    cursor.execute("""
                        UPDATE log_events
                        SET game_gid = (
                            SELECT g.gid
                            FROM games g
                            WHERE g.id = log_events.game_id
                        )
                    """)

                    # Create index on game_gid
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_log_events_game_gid
                        ON log_events(game_gid)
                    """)

                    logger.info(
                        "Migration v18: game_gid column added and data migrated"
                    )
                else:
                    logger.info("Migration v18: game_gid column already exists")

            except Exception as e:
                logger.warning(f"Migration v18: Could not add game_gid column: {e}")

            conn.commit()
            logger.info("Migration v18 completed: log_events game_gid support added")

        # Migration 19: Add json_path column to event_params table
        if current_version < 19:
            logger.info("Migration v19: Adding json_path column to event_params...")

            try:
                cursor.execute("PRAGMA table_info(event_params)")
                columns = [column[1] for column in cursor.fetchall()]

                if "json_path" not in columns:
                    logger.info(
                        "Migration v19: Adding json_path column to event_params..."
                    )
                    cursor.execute("ALTER TABLE event_params ADD COLUMN json_path TEXT")

                    # Create index on json_path for better query performance
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_event_params_json_path
                        ON event_params(json_path)
                    """)

                    logger.info("Migration v19: json_path column added to event_params")
                else:
                    logger.info("Migration v19: json_path column already exists")

            except Exception as e:
                logger.warning(f"Migration v19: Could not add json_path column: {e}")

            conn.commit()
            logger.info("Migration v19 completed: event_params json_path support added")

        # Migration v20: Add game_gid to multiple tables (for game_gid migration)
        if current_version < 20:
            logger.info("Migration v20: Adding game_gid columns to tables...")

            tables_to_migrate = [
                "event_nodes",
                "parameter_aliases",
                "common_params",
                "flow_templates",
            ]

            for table_name in tables_to_migrate:
                try:
                    # Add game_gid column
                    cursor.execute(
                        f"SELECT name FROM pragma_table_info('{table_name}') WHERE name='game_gid'"
                    )
                    if not cursor.fetchone():
                        cursor.execute(
                            f"ALTER TABLE {table_name} ADD COLUMN game_gid INTEGER"
                        )
                        cursor.execute(
                            f"CREATE INDEX IF NOT EXISTS idx_{table_name}_game_gid ON {table_name}(game_gid)"
                        )
                        logger.info(
                            f"Migration v20: Added game_gid column to {table_name}"
                        )
                    else:
                        logger.info(f"Migration v20: {table_name} already has game_gid")

                    # Make game_id nullable (for migration from game_id to game_gid)
                    if table_name in [
                        "parameter_aliases",
                        "common_params",
                        "event_nodes",
                    ]:
                        cursor.execute(f"PRAGMA table_info({table_name})")
                        columns = {c[1]: c for c in cursor.fetchall()}
                        if (
                            "game_id" in columns and columns["game_id"][3] == 1
                        ):  # notnull = 1
                            # Recreate table with nullable game_id
                            logger.info(
                                f"Migration v20: Making game_id nullable in {table_name}"
                            )

                except Exception as e:
                    logger.warning(
                        f"Migration v20: Could not add game_gid to {table_name}: {e}"
                    )

            conn.commit()
            logger.info("Migration v20 completed: game_gid columns added to all tables")

        # Update database version (PRAGMA doesn't support parameters in SQLite)
        cursor.execute(f"PRAGMA user_version = {target_version}")
        conn.commit()
        logger.info(
            f"Database migration completed successfully. Version: {target_version}"
        )

    except Exception as e:
        conn.rollback()
        logger.error(f"Database migration failed: {e}")
        raise
    finally:
        conn.close()


def create_indexes():
    """Create database indexes for performance optimization"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Indexes for log_events table
    indexes = [
        # Games table
        "CREATE INDEX IF NOT EXISTS idx_games_gid ON games(gid)",
        # Log events table
        "CREATE INDEX IF NOT EXISTS idx_log_events_game_id ON log_events(game_id)",
        "CREATE INDEX IF NOT EXISTS idx_log_events_category_id ON log_events(category_id)",
        "CREATE INDEX IF NOT EXISTS idx_log_events_event_name ON log_events(event_name)",
        # Event params table (replaces 'parameters' table)
        "CREATE INDEX IF NOT EXISTS idx_event_params_event_id ON event_params(event_id)",
        "CREATE INDEX IF NOT EXISTS idx_event_params_param_name ON event_params(param_name)",
        # Common params table
        "CREATE INDEX IF NOT EXISTS idx_common_params_game_id ON common_params(game_id)",
        "CREATE INDEX IF NOT EXISTS idx_common_params_param_name ON common_params(param_name)",
        # HQL statements table
        "CREATE INDEX IF NOT EXISTS idx_hql_statements_event_id ON hql_statements(event_id)",
        "CREATE INDEX IF NOT EXISTS idx_hql_statements_hql_type ON hql_statements(hql_type)",
        "CREATE INDEX IF NOT EXISTS idx_hql_statements_is_active ON hql_statements(is_active)",
        # Event category relations
        "CREATE INDEX IF NOT EXISTS idx_event_category_relations_event_id ON event_category_relations(event_id)",
        "CREATE INDEX IF NOT EXISTS idx_event_category_relations_category_id ON event_category_relations(category_id)",
        # Event common params (removed common_param_id index as column doesn't exist)
        "CREATE INDEX IF NOT EXISTS idx_event_common_params_event_id ON event_common_params(event_id)",
        # New parameter management tables (v6)
        "CREATE INDEX IF NOT EXISTS idx_param_templates_base_type ON param_templates(base_type)",
        "CREATE INDEX IF NOT EXISTS idx_param_templates_nesting_level ON param_templates(nesting_level)",
        "CREATE INDEX IF NOT EXISTS idx_param_library_param_name ON param_library(param_name)",
        "CREATE INDEX IF NOT EXISTS idx_param_library_category ON param_library(category)",
        "CREATE INDEX IF NOT EXISTS idx_param_library_template_id ON param_library(template_id)",
        "CREATE INDEX IF NOT EXISTS idx_event_params_event_id ON event_params(event_id)",
        "CREATE INDEX IF NOT EXISTS idx_event_params_library_id ON event_params(library_id)",
        "CREATE INDEX IF NOT EXISTS idx_event_params_template_id ON event_params(template_id)",
        "CREATE INDEX IF NOT EXISTS idx_event_params_param_name ON event_params(param_name)",
        "CREATE INDEX IF NOT EXISTS idx_event_params_is_active ON event_params(is_active)",
        "CREATE INDEX IF NOT EXISTS idx_param_versions_event_param_id ON param_versions(event_param_id)",
        "CREATE INDEX IF NOT EXISTS idx_param_versions_version ON param_versions(event_param_id, version)",
        "CREATE INDEX IF NOT EXISTS idx_param_configs_event_param_id ON param_configs(event_param_id)",
        "CREATE INDEX IF NOT EXISTS idx_param_configs_parse_mode ON param_configs(parse_mode)",
        # Enhanced HQL generation (v9)
        "CREATE INDEX IF NOT EXISTS idx_join_configs_join_type ON join_configs(join_type)",
        "CREATE INDEX IF NOT EXISTS idx_join_configs_game_id ON join_configs(game_id)",
        "CREATE INDEX IF NOT EXISTS idx_join_configs_description ON join_configs(description)",
        # Field selection presets (v9)
        "CREATE INDEX IF NOT EXISTS idx_field_presets_game_id ON field_selection_presets(game_id)",
        "CREATE INDEX IF NOT EXISTS idx_field_presets_is_default ON field_selection_presets(is_default)",
        # Phase 1 - Field Builder indexes (v11)
        "CREATE INDEX IF NOT EXISTS idx_node_templates_type ON node_templates(node_type)",
        "CREATE INDEX IF NOT EXISTS idx_node_templates_created_by ON node_templates(created_by)",
        "CREATE INDEX IF NOT EXISTS idx_flow_templates_created_by ON flow_templates(created_by)",
        "CREATE INDEX IF NOT EXISTS idx_join_configs_field_mapping_v2 ON join_configs(field_mapping_v2)",
        # **性能优化**: Performance optimization indexes for parameter management (Ralph Loop v1)
        "CREATE INDEX IF NOT EXISTS idx_log_events_game_id_updated_at ON log_events(game_id, updated_at)",
        "CREATE INDEX IF NOT EXISTS idx_event_params_event_id_active ON event_params(event_id, is_active)",
        "CREATE INDEX IF NOT EXISTS idx_event_params_event_template_active ON event_params(event_id, template_id, is_active)",
        "CREATE INDEX IF NOT EXISTS idx_common_params_game_status ON common_params(game_id, status)",
        # **性能优化**: Event node copy optimization (2026-01-22)
        "CREATE INDEX IF NOT EXISTS idx_event_node_configs_game_gid_event_id ON event_node_configs(game_gid, event_id)",
        "CREATE INDEX IF NOT EXISTS idx_event_params_event_id_template ON event_params(event_id, template_id)",
    ]

    for index_sql in indexes:
        try:
            cursor.execute(index_sql)
            index_name = (
                index_sql.split("idx_")[1].split(" ")[0]
                if "idx_" in index_sql
                else "unknown"
            )
            logger.debug(f"Created index: {index_name}")
        except sqlite3.OperationalError as e:
            logger.warning(f"Index creation warning: {e}")

    conn.commit()
    conn.close()
    logger.info("Database indexes created/verified successfully")
