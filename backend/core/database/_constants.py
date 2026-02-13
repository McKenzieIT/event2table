#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database constants and configuration
"""

# SQLite PRAGMA settings
PRAGMA_SETTINGS = {
    "journal_mode": "WAL",
    "synchronous": "NORMAL",
}


# Table creation SQL constants
GAMES_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gid TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        ods_db TEXT NOT NULL DEFAULT 'ieu_ods',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""

LOG_EVENTS_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS log_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_gid TEXT NOT NULL,
        event_name TEXT NOT NULL,
        event_name_cn TEXT NOT NULL,
        category_id INTEGER,
        source_table TEXT NOT NULL,
        target_table TEXT NOT NULL,
        include_in_common_params INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES event_categories(id),
        FOREIGN KEY (game_gid) REFERENCES games(gid)
    )
"""

EVENT_PARAMS_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS event_params (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        param_name TEXT NOT NULL,
        param_name_cn TEXT,
        template_id INTEGER,
        param_description TEXT,
        is_active INTEGER DEFAULT 1,
        version INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (event_id) REFERENCES log_events(id) ON DELETE CASCADE,
        FOREIGN KEY (template_id) REFERENCES param_templates(id)
    )
"""

EVENT_CATEGORIES_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS event_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""

PARAM_TEMPLATES_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS param_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        template_name TEXT UNIQUE NOT NULL,
        display_name TEXT NOT NULL,
        base_type TEXT NOT NULL,
        json_path TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""

COMMON_PARAMS_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS common_params (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER NOT NULL,
        param_name TEXT NOT NULL,
        param_name_cn TEXT,
        param_type TEXT,
        param_description TEXT,
        table_name TEXT,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
        UNIQUE(game_id, param_name)
    )
"""

EVENT_COMMON_PARAMS_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS event_common_params (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        common_param_id INTEGER NOT NULL,
        include INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (event_id) REFERENCES log_events(id) ON DELETE CASCADE,
        FOREIGN KEY (common_param_id) REFERENCES common_params(id) ON DELETE CASCADE,
        UNIQUE(event_id, common_param_id)
    )
"""

EVENT_CATEGORY_RELATIONS_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS event_category_relations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (event_id) REFERENCES log_events(id) ON DELETE CASCADE,
        FOREIGN KEY (category_id) REFERENCES event_categories(id) ON DELETE CASCADE,
        UNIQUE(event_id, category_id)
    )
"""

PARAM_LIBRARY_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS param_library (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        param_name TEXT NOT NULL,
        param_name_cn TEXT,
        template_id INTEGER,
        param_description TEXT,
        usage_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (template_id) REFERENCES param_templates(id)
    )
"""

HQL_STATEMENTS_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS hql_statements (
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
"""

CANVAS_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS canvas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        nodes_json TEXT NOT NULL,
        edges_json TEXT NOT NULL,
        game_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
    )
"""

HQL_HISTORY_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS hql_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 0,
        session_id TEXT,
        events_json TEXT NOT NULL,
        fields_json TEXT NOT NULL,
        conditions_json TEXT,
        mode TEXT NOT NULL,
        hql TEXT NOT NULL,
        performance_score INTEGER,
        metadata_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""

JOIN_CONFIGS_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS join_configs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER NOT NULL,
        left_event_id INTEGER NOT NULL,
        right_event_id INTEGER NOT NULL,
        join_type TEXT DEFAULT 'inner',
        join_conditions TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
        FOREIGN KEY (left_event_id) REFERENCES log_events(id) ON DELETE CASCADE,
        FOREIGN KEY (right_event_id) REFERENCES log_events(id) ON DELETE CASCADE
    )
"""

# Index creation SQL
INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_log_events_game_gid ON log_events(game_gid)",
    "CREATE INDEX IF NOT EXISTS idx_log_events_event_name ON log_events(event_name)",
    "CREATE INDEX IF NOT EXISTS idx_event_params_event_id ON event_params(event_id)",
    "CREATE INDEX IF NOT EXISTS idx_event_params_param_name ON event_params(param_name)",
    "CREATE INDEX IF NOT EXISTS idx_common_params_game_id ON common_params(game_id)",
    "CREATE INDEX IF NOT EXISTS idx_common_params_param_name ON common_params(param_name)",
    "CREATE INDEX IF NOT EXISTS idx_hql_history_user_id ON hql_history(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_hql_history_session_id ON hql_history(session_id)",
    "CREATE INDEX IF NOT EXISTS idx_join_configs_game_id ON join_configs(game_id)",
]

# All table SQL statements in order
ALL_TABLES_SQL = [
    GAMES_TABLE_SQL,
    EVENT_CATEGORIES_TABLE_SQL,
    PARAM_TEMPLATES_TABLE_SQL,
    LOG_EVENTS_TABLE_SQL,
    EVENT_PARAMS_TABLE_SQL,
    COMMON_PARAMS_TABLE_SQL,
    EVENT_COMMON_PARAMS_TABLE_SQL,
    EVENT_CATEGORY_RELATIONS_TABLE_SQL,
    PARAM_LIBRARY_TABLE_SQL,
    HQL_STATEMENTS_TABLE_SQL,
    CANVAS_TABLE_SQL,
    HQL_HISTORY_TABLE_SQL,
    JOIN_CONFIGS_TABLE_SQL,
]
