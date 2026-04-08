"""
数据库迁移类 V1-V18
"""

import logging
import sqlite3

from .base import BaseMigration

logger = logging.getLogger(__name__)


class MigrationV1_AddCategoryId(BaseMigration):
    """迁移1: 添加category_id列到log_events表"""

    version = 1

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        cursor.execute("PRAGMA table_info(log_events)")
        columns = [column[1] for column in cursor.fetchall()]

        if "category_id" not in columns:
            logger.info("Migration v1: Adding category_id column to log_events...")
            cursor.execute("ALTER TABLE log_events ADD COLUMN category_id INTEGER")

            # Create default category
            cursor.execute('INSERT OR IGNORE INTO event_categories (name) VALUES ("默认分类")')
            cursor.execute('SELECT id FROM event_categories WHERE name = "默认分类"')
            default_category = cursor.fetchone()

            if default_category:
                cursor.execute("UPDATE log_events SET category_id = ?", (default_category[0],))

            logger.info("Migration v1 completed: category_id column added to log_events")


class MigrationV2_EventCategoryRelations(BaseMigration):
    """迁移2: 创建event_category_relations表"""

    version = 2

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='event_category_relations'"
        )
        if not cursor.fetchone():
            logger.info("Migration v2: Adding event_category_relations table...")
            cursor.execute(
                """
                CREATE TABLE event_category_relations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER NOT NULL,
                    category_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (event_id) REFERENCES log_events(id) ON DELETE CASCADE,
                    FOREIGN KEY (category_id) REFERENCES event_categories(id) ON DELETE CASCADE,
                    UNIQUE(event_id, category_id)
                )
            """
            )
            logger.info("Migration v2 completed: event_category_relations table added")


class MigrationV3_IncludeInCommonParams(BaseMigration):
    """迁移3: 添加include_in_common_params列到log_events表"""

    version = 3

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        cursor.execute("PRAGMA table_info(log_events)")
        columns = [column[1] for column in cursor.fetchall()]

        if "include_in_common_params" not in columns:
            logger.info("Migration v3: Adding include_in_common_params column to log_events...")
            cursor.execute(
                "ALTER TABLE log_events ADD COLUMN include_in_common_params INTEGER DEFAULT 1"
            )
            logger.info(
                "Migration v3 completed: include_in_common_params column added to log_events"
            )


class MigrationV4_IconPath(BaseMigration):
    """迁移4: 添加icon_path列到games表"""

    version = 4

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        cursor.execute("PRAGMA table_info(games)")
        columns = [column[1] for column in cursor.fetchall()]

        if "icon_path" not in columns:
            logger.info("Migration v4: Adding icon_path column to games...")
            cursor.execute("ALTER TABLE games ADD COLUMN icon_path TEXT")
            logger.info("Migration v4 completed: icon_path column added to games")


class MigrationV5_EditTracking(BaseMigration):
    """迁移5: 添加编辑追踪字段到hql_statements表"""

    version = 5

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        cursor.execute("PRAGMA table_info(hql_statements)")
        columns = [column[1] for column in cursor.fetchall()]

        if "is_user_edited" not in columns:
            logger.info("Migration v5: Adding is_user_edited column...")
            cursor.execute("ALTER TABLE hql_statements ADD COLUMN is_user_edited INTEGER DEFAULT 0")

        if "edit_notes" not in columns:
            logger.info("Migration v5: Adding edit_notes column...")
            cursor.execute("ALTER TABLE hql_statements ADD COLUMN edit_notes TEXT")

        if "original_content" not in columns:
            logger.info("Migration v5: Adding original_content column...")
            cursor.execute("ALTER TABLE hql_statements ADD COLUMN original_content TEXT")

        logger.info("Migration v5 completed: edit tracking fields added to hql_statements")


class MigrationV6_ParameterManagementRefactoring(BaseMigration):
    """迁移6: 参数管理重构"""

    version = 6

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        logger.info("Migration v6: Starting parameter management refactoring...")

        # 1. Create param_templates table
        logger.info("Migration v6: Creating param_templates table...")
        cursor.execute(
            """
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
        """
        )

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
        cursor.execute(
            """
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
        """
        )

        # 4. Create event_params table
        logger.info("Migration v6: Creating event_params table...")
        cursor.execute(
            """
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
        """
        )

        # 5. Create param_versions table
        logger.info("Migration v6: Creating param_versions table...")
        cursor.execute(
            """
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
        """
        )

        # 6. Create param_configs table
        logger.info("Migration v6: Creating param_configs table...")
        cursor.execute(
            """
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
        """
        )

        # 7. Check if old parameters table exists and rename it
        logger.info("Migration v6: Checking for old parameters table...")
        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='parameters'
        """
        )
        old_table_exists = cursor.fetchone() is not None

        if old_table_exists:
            # Migrate existing parameters to event_params
            logger.info("Migration v6: Migrating existing parameters to event_params...")
            cursor.execute('SELECT id FROM param_templates WHERE template_name = "string" LIMIT 1')
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
            logger.info("Migration v6: renamed old parameters table to parameters_old_v5")

        logger.info("Migration v6 completed: parameter management refactoring finished")


class MigrationV7_ParameterValidationAndBatchOperations(BaseMigration):
    """迁移7: 参数验证规则和批量操作支持"""

    version = 7

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        logger.info("Migration v7: Starting parameter validation and batch operations...")

        # 1. Create param_validation_rules table
        logger.info("Migration v7: Creating param_validation_rules table...")
        cursor.execute(
            """
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
        """
        )

        # 2. Create batch_import_records table
        logger.info("Migration v7: Creating batch_import_records table...")
        cursor.execute(
            """
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
        """
        )

        # 3. Create batch_import_details table
        logger.info("Migration v7: Creating batch_import_details table...")
        cursor.execute(
            """
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
        """
        )

        # 4. Create indexes for validation rules
        logger.info("Migration v7: Creating indexes for param_validation_rules...")
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_validation_rules_param_id
            ON param_validation_rules(event_param_id)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_validation_rules_type
            ON param_validation_rules(rule_type)
        """
        )

        # 5. Create indexes for batch imports
        logger.info("Migration v7: Creating indexes for batch_import tables...")
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_batch_import_records_status
            ON batch_import_records(status)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_batch_import_details_import_id
            ON batch_import_details(import_id)
        """
        )

        logger.info("Migration v7 completed: validation rules and batch operations created")


class MigrationV8_ParameterDependencies(BaseMigration):
    """迁移8: 参数依赖关系支持"""

    version = 8

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        logger.info("Migration v8: Starting parameter dependencies...")

        # Create param_dependencies table
        logger.info("Migration v8: Creating param_dependencies table...")
        cursor.execute(
            """
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
        """
        )

        # Create indexes
        logger.info("Migration v8: Creating indexes for param_dependencies...")
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_param_dependencies_event_id
            ON param_dependencies(event_id)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_param_dependencies_dependent
            ON param_dependencies(dependent_param_id)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_param_dependencies_depends_on
            ON param_dependencies(depends_on_param_id)
        """
        )

        logger.info("Migration v8 completed: parameter dependencies created")


class MigrationV9_EnhancedHQLGeneration(BaseMigration):
    """迁移9: 增强的HQL生成功能"""

    version = 9

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        logger.info("Migration v9: Enhanced HQL generation features...")

        # Check if join_configs table exists and add new columns
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='join_configs'")
        join_configs_exists = cursor.fetchone() is not None

        if join_configs_exists:
            logger.info("Migration v9: Adding new columns to join_configs...")
            cursor.execute("PRAGMA table_info(join_configs)")
            columns = [column[1] for column in cursor.fetchall()]

            if "join_type" not in columns:
                cursor.execute("ALTER TABLE join_configs ADD COLUMN join_type TEXT DEFAULT 'join'")

            if "where_conditions" not in columns:
                cursor.execute("ALTER TABLE join_configs ADD COLUMN where_conditions TEXT")

            if "field_mappings" not in columns:
                cursor.execute("ALTER TABLE join_configs ADD COLUMN field_mappings TEXT")

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
            cursor.execute(
                """
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
            """
            )

        # Create field_selection_presets table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='field_selection_presets'"
        )
        if not cursor.fetchone():
            logger.info("Migration v9: Creating field_selection_presets table...")
            cursor.execute(
                """
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
            """
            )

        logger.info("Migration v9 completed: Enhanced HQL generation features added")


class MigrationV10_ArrayParameterHierarchy(BaseMigration):
    """迁移10: Array参数层级结构支持"""

    version = 10

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        logger.info("Migration v10: Adding array parameter hierarchy support...")

        # Check if param_configs table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='param_configs'")
        if cursor.fetchone():
            logger.info("Migration v10: Extending param_configs table...")
            cursor.execute("PRAGMA table_info(param_configs)")
            columns = [column[1] for column in cursor.fetchall()]

            if "child_params" not in columns:
                cursor.execute("ALTER TABLE param_configs ADD COLUMN child_params TEXT")

            if "array_element_structure" not in columns:
                cursor.execute("ALTER TABLE param_configs ADD COLUMN array_element_structure TEXT")

        # Create index for parameter hierarchy
        logger.info("Migration v10: Creating indexes for parameter hierarchy...")
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_event_params_event_template
            ON event_params(event_id, template_id)
        """
        )

        logger.info("Migration v10 completed: array parameter hierarchy support added")


class MigrationV11_FieldBuilderSupport(BaseMigration):
    """迁移11: Field Builder支持"""

    version = 11

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        logger.info("Migration v11: Adding field builder support...")

        # Add field_mapping_v2 column to join_configs
        cursor.execute("PRAGMA table_info(join_configs)")
        columns = [column[1] for column in cursor.fetchall()]

        if "field_mapping_v2" not in columns:
            logger.info("Migration v11: Adding field_mapping_v2 column to join_configs...")
            cursor.execute("ALTER TABLE join_configs ADD COLUMN field_mapping_v2 TEXT")

        # Create node_templates table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='node_templates'"
        )
        if not cursor.fetchone():
            logger.info("Migration v11: Creating node_templates table...")
            cursor.execute(
                """
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
            """
            )

        # Create flow_templates table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='flow_templates'"
        )
        if not cursor.fetchone():
            logger.info("Migration v11: Creating flow_templates table...")
            cursor.execute(
                """
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
            """
            )

        # Create indexes
        logger.info("Migration v11: Creating indexes for node and flow templates...")
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_node_templates_type
            ON node_templates(node_type)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_flow_templates_created_by
            ON flow_templates(created_by)
        """
        )

        logger.info("Migration v11 completed: field builder support added")


class MigrationV12_FlowTemplates(BaseMigration):
    """迁移12: flow_templates表更新"""

    version = 12

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        logger.info("Migration v12: Updating flow_templates table...")

        # Check if table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='flow_templates'"
        )
        table_exists = cursor.fetchone() is not None

        if table_exists:
            logger.info("Migration v12: flow_templates table exists, checking structure...")
            cursor.execute("PRAGMA table_info(flow_templates)")
            columns = {column[1] for column in cursor.fetchall()}

            # Add missing columns
            if "game_id" not in columns:
                cursor.execute("ALTER TABLE flow_templates ADD COLUMN game_id INTEGER")
                cursor.execute("UPDATE flow_templates SET game_id = 1 WHERE game_id IS NULL")

            if "is_active" not in columns:
                cursor.execute("ALTER TABLE flow_templates ADD COLUMN is_active INTEGER DEFAULT 1")

            if "version" not in columns:
                cursor.execute("ALTER TABLE flow_templates ADD COLUMN version INTEGER DEFAULT 1")

        else:
            # Table doesn't exist, create it
            logger.info("Migration v12: Creating flow_templates table...")
            cursor.execute(
                """
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
            """
            )

        # Create indexes
        try:
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_flow_templates_game_id
                ON flow_templates(game_id)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_flow_templates_updated_at
                ON flow_templates(updated_at)
            """
            )
        except Exception as e:
            logger.warning(f"Migration v12: Could not create indexes: {e}")

        logger.info("Migration v12 completed: flow templates support added")


class MigrationV13_EventNodesAndParameterAliases(BaseMigration):
    """迁移13: 事件节点和参数别名支持"""

    version = 13

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        logger.info("Migration v13: Adding event_nodes and parameter_aliases tables...")

        # Create event_nodes table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='event_nodes'")
        if not cursor.fetchone():
            logger.info("Migration v13: Creating event_nodes table...")
            cursor.execute(
                """
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
            """
            )

        # Create parameter_aliases table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='parameter_aliases'"
        )
        if not cursor.fetchone():
            logger.info("Migration v13: Creating parameter_aliases table...")
            cursor.execute(
                """
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
            """
            )

        # Create indexes
        try:
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_event_nodes_game_id
                ON event_nodes(game_id)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_event_nodes_event_id
                ON event_nodes(event_id)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_parameter_aliases_game_id
                ON parameter_aliases(game_id)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_parameter_aliases_param_id
                ON parameter_aliases(param_id)
            """
            )
        except Exception as e:
            logger.warning(f"Migration v13: Could not create indexes: {e}")

        logger.info("Migration v13 completed: event nodes and parameter aliases support added")


class MigrationV14_FieldNameMappings(BaseMigration):
    """迁移14: 字段名映射支持"""

    version = 14

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        logger.info("Migration v14: Adding field name mappings support...")

        # Create field_name_mappings table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='field_name_mappings'"
        )
        if not cursor.fetchone():
            logger.info("Migration v14: Creating field_name_mappings table...")
            cursor.execute(
                """
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
            """
            )

        # Create field_name_history table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='field_name_history'"
        )
        if not cursor.fetchone():
            logger.info("Migration v14: Creating field_name_history table...")
            cursor.execute(
                """
                CREATE TABLE field_name_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mapping_id INTEGER NOT NULL,
                    field_name TEXT NOT NULL,
                    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (mapping_id) REFERENCES field_name_mappings(id) ON DELETE CASCADE
                )
            """
            )

        # Create indexes
        try:
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_field_mappings_game_param
                ON field_name_mappings(game_id, param_name)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS field_name_history_mapping_id
                ON field_name_history(mapping_id)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS field_name_history_used_at
                ON field_name_history(used_at)
            """
            )
        except Exception as e:
            logger.warning(f"Migration v14: Could not create indexes: {e}")

        logger.info("Migration v14 completed: field name mappings support added")


class MigrationV15_EventNodeConfigs(BaseMigration):
    """迁移15: 事件节点构建器配置"""

    version = 15

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        logger.info("Migration v15: Creating event_node_configs table...")

        cursor.execute(
            """
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
        """
        )

        # Create indexes for performance
        try:
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_event_node_game_gid
                ON event_node_configs(game_gid)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_event_node_name_en
                ON event_node_configs(name_en)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_event_node_event_id
                ON event_node_configs(event_id)
            """
            )
        except Exception as e:
            logger.warning(f"Migration v15: Could not create indexes: {e}")

        logger.info("Migration v15 completed: event node builder support added")


class MigrationV16_AsyncTasks(BaseMigration):
    """迁移16: 异步任务系统"""

    version = 16

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        logger.info("Migration v16: Creating async_tasks table...")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='async_tasks'")
        if not cursor.fetchone():
            logger.info("Migration v16: Creating async_tasks table...")
            cursor.execute(
                """
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
            """
            )

            # Create indexes for async_tasks
            try:
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_async_tasks_task_id
                    ON async_tasks(task_id)
                """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_async_tasks_status
                    ON async_tasks(status)
                """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_async_tasks_created_at
                    ON async_tasks(created_at)
                """
                )
            except Exception as e:
                logger.warning(f"Migration v16: Could not create indexes: {e}")

        logger.info("Migration v16 completed: async task system support added")


class MigrationV17_CommonParamsDisplayName(BaseMigration):
    """迁移17: 添加display_name列到common_params表"""

    version = 17

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        logger.info("Migration v17: Adding display_name column to common_params...")
        try:
            cursor.execute("PRAGMA table_info(common_params)")
            columns = [column[1] for column in cursor.fetchall()]

            if "display_name" not in columns:
                cursor.execute("ALTER TABLE common_params ADD COLUMN display_name TEXT")

                # Update existing records with default display names
                cursor.execute(
                    """
                    UPDATE common_params
                    SET display_name = param_name_cn
                    WHERE display_name IS NULL
                """
                )
                logger.info("Migration v17: display_name column added")
            else:
                logger.info("Migration v17: display_name column already exists")
        except Exception as e:
            logger.warning(f"Migration v17: Could not add display_name column: {e}")

        logger.info("Migration v17 completed: common_params display_name support added")


class MigrationV18_AddGameGid(BaseMigration):
    """迁移18: 添加game_gid列到log_events表并迁移数据"""

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
                cursor.execute(
                    """
                    UPDATE log_events
                        SET game_gid = (
                            SELECT g.gid
                            FROM games g
                            WHERE g.id = log_events.game_id
                        )
                """
                )

                # Create index on game_gid
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_log_events_game_gid
                        ON log_events(game_gid)
                """
                )

                logger.info("Migration v18: game_gid column added and data migrated")
            else:
                logger.info("Migration v18: game_gid column already exists")

        except Exception as e:
            logger.warning(f"Migration v18: Could not add game_gid column: {e}")

        logger.info("Migration v18 completed: log_events game_gid support added")
