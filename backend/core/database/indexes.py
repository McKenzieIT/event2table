"""
数据库索引管理

提供数据库索引创建和管理功能。
"""

import sqlite3

from backend.core.logging import get_logger

from .connection import get_db_connection

logger = get_logger(__name__)


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
                index_sql.split("idx_")[1].split(" ")[0] if "idx_" in index_sql else "unknown"
            )
            logger.debug(f"Created index: {index_name}")
        except sqlite3.OperationalError as e:
            logger.warning(f"Index creation warning: {e}")

    conn.commit()
    conn.close()
    logger.info("Database indexes created/verified successfully")
