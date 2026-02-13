-- DWD Generator Database Schema
-- Generated: dwd_generator.db
-- Date: 1770720657.45038

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
                    );

CREATE TABLE batch_import_details (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    import_id INTEGER NOT NULL,
                    row_number INTEGER NOT NULL,
                    data_type TEXT,
                    action TEXT,
                    entity_id INTEGER,
                    status TEXT,
                    error_message TEXT,
                    FOREIGN KEY (import_id) REFERENCES batch_import_records(id) ON DELETE CASCADE
                );

CREATE TABLE batch_import_records (
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
                );

CREATE TABLE common_params (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            param_name TEXT NOT NULL,
            param_name_cn TEXT,
            param_type TEXT NOT NULL,
            param_description TEXT,
            table_name TEXT NOT NULL,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, display_name TEXT,
            FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
        );

CREATE TABLE event_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

CREATE TABLE event_category_relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES log_events(id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES event_categories(id) ON DELETE CASCADE,
            UNIQUE(event_id, category_id)
        );

CREATE TABLE event_common_params (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            common_param_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES log_events(id) ON DELETE CASCADE,
            FOREIGN KEY (common_param_id) REFERENCES common_params(id) ON DELETE CASCADE
        );

CREATE TABLE event_node_configs (
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
                );

CREATE TABLE event_nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            event_id INTEGER NOT NULL,
            config_json TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, game_gid INTEGER,
            FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
            FOREIGN KEY (event_id) REFERENCES log_events(id) ON DELETE CASCADE
        );

CREATE TABLE event_params (
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
                );

CREATE TABLE field_name_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        mapping_id INTEGER NOT NULL,
                        field_name TEXT NOT NULL,
                        used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (mapping_id) REFERENCES field_name_mappings(id) ON DELETE CASCADE
                    );

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
                    );

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
                    );

CREATE TABLE flow_templates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        flow_name TEXT NOT NULL,
                        flow_graph TEXT NOT NULL,
                        variables TEXT,
                        description TEXT,
                        created_by TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    , game_id INTEGER, is_active INTEGER DEFAULT 1, version INTEGER DEFAULT 1, name TEXT);

CREATE TABLE games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gid TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            ods_db TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        , icon_path TEXT);

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
                    );

CREATE TABLE hql_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 0,
            session_id TEXT,
            events_json TEXT NOT NULL,
            fields_json TEXT NOT NULL,
            conditions_json TEXT,
            mode TEXT NOT NULL DEFAULT 'single',
            hql TEXT NOT NULL,
            performance_score INTEGER,
            created_at TIMESTAMP NOT NULL DEFAULT (datetime('now', 'localtime')),
            metadata_json TEXT
        );

CREATE TABLE hql_statements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                hql_type TEXT NOT NULL,
                hql_content TEXT NOT NULL,
                hql_version INTEGER DEFAULT 1,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, is_user_edited INTEGER DEFAULT 0, edit_notes TEXT, original_content TEXT,
                FOREIGN KEY (event_id) REFERENCES log_events(id) ON DELETE CASCADE
            );

CREATE TABLE join_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            display_name TEXT NOT NULL,
            source_events TEXT NOT NULL,
            join_conditions TEXT,
            output_fields TEXT NOT NULL,
            output_table TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        , join_type TEXT DEFAULT 'join', where_conditions TEXT, field_mappings TEXT, description TEXT, game_id INTEGER, field_mapping_v2 TEXT);

CREATE TABLE log_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            event_name TEXT NOT NULL,
            event_name_cn TEXT NOT NULL,
            category_id INTEGER,
            source_table TEXT NOT NULL,
            target_table TEXT NOT NULL,
            include_in_common_params INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, game_gid INTEGER,
            FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES event_categories(id) ON DELETE CASCADE
        );

CREATE TABLE node_templates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        node_name TEXT NOT NULL,
                        node_type TEXT NOT NULL,
                        node_config TEXT NOT NULL,
                        description TEXT,
                        created_by TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

CREATE TABLE param_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_param_id INTEGER NOT NULL UNIQUE,
                    parse_mode TEXT DEFAULT 'json_extract',
                    explode_config TEXT,
                    array_element_delimiter TEXT DEFAULT ',',
                    map_key_value_delimiter TEXT DEFAULT ':',
                    custom_hql_template TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, child_params TEXT, array_element_structure TEXT,
                    FOREIGN KEY (event_param_id) REFERENCES event_params(id) ON DELETE CASCADE
                );

CREATE TABLE param_dependencies (
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
                );

CREATE TABLE param_library (
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
                );

CREATE TABLE param_templates (
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
                );

CREATE TABLE param_validation_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_param_id INTEGER NOT NULL UNIQUE,
                    rule_type TEXT NOT NULL,
                    rule_config TEXT NOT NULL,
                    error_message TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (event_param_id) REFERENCES event_params(id) ON DELETE CASCADE
                );

CREATE TABLE param_versions (
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
                );

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
            FOREIGN KEY (param_id) REFERENCES "parameters_old_v5"(id) ON DELETE CASCADE,
            UNIQUE(game_id, param_id, alias)
        );

CREATE TABLE parameters (
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
        );

CREATE TABLE "parameters_old_v5" (
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
        );

CREATE TABLE sql_optimizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_hql TEXT NOT NULL,
            optimized_hql TEXT NOT NULL,
            applied_rules TEXT,
            suggested_rules TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

CREATE TABLE sqlite_sequence(name,seq);

