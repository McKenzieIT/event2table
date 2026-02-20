#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Game GID Migration Analysis Script

This script analyzes the current database state and code to identify:
1. Tables using game_id vs game_gid
2. Foreign key constraints
3. Data migration requirements
4. Potential issues and risks
"""

import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.config import get_db_path
from backend.core.logging import get_logger

logger = get_logger(__name__)


class GameGidMigrationAnalyzer:
    """Analyze game_gid migration status and requirements"""

    def __init__(self, db_path: Path = None):
        self.db_path = db_path or get_db_path()
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def analyze_tables(self) -> Dict:
        """Analyze all tables for game_id/game_gid usage"""
        logger.info("📊 Analyzing database tables...")

        # Get all tables
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in self.cursor.fetchall()]

        analysis = {
            "tables_with_game_id": [],
            "tables_with_game_gid": [],
            "tables_with_both": [],
            "tables_without_game_ref": []
        }

        for table in tables:
            # Skip sqlite system tables
            if table.startswith("sqlite_"):
                continue

            # Get table schema
            self.cursor.execute(f"PRAGMA table_info({table})")
            columns = self.cursor.fetchall()

            has_game_id = any(col["name"] == "game_id" for col in columns)
            has_game_gid = any(col["name"] == "game_gid" for col in columns)

            # Get foreign keys
            self.cursor.execute(f"PRAGMA foreign_key_list({table})")
            foreign_keys = self.cursor.fetchall()

            fk_references_games = []
            for fk in foreign_keys:
                if fk["table"] == "games":
                    fk_references_games.append({
                        "from": fk["from"],
                        "to": fk["to"],
                        "on_delete": fk["on_delete"],
                        "on_update": fk["on_update"]
                    })

            table_info = {
                "name": table,
                "has_game_id": has_game_id,
                "has_game_gid": has_game_gid,
                "foreign_keys_to_games": fk_references_games
            }

            if has_game_id and has_game_gid:
                analysis["tables_with_both"].append(table_info)
                logger.info(f"  ✅ {table}: has BOTH game_id and game_gid")
            elif has_game_id:
                analysis["tables_with_game_id"].append(table_info)
                logger.info(f"  ⚠️  {table}: uses game_id (needs migration)")
            elif has_game_gid:
                analysis["tables_with_game_gid"].append(table_info)
                logger.info(f"  ✅ {table}: uses game_gid (migrated)")
            else:
                analysis["tables_without_game_ref"].append(table_info)

        return analysis

    def analyze_data_consistency(self) -> Dict:
        """Analyze data consistency between game_id and game_gid"""
        logger.info("\n🔍 Analyzing data consistency...")

        results = {}

        # Check tables with both columns
        tables_with_both = ["log_events", "event_nodes"]

        for table in tables_with_both:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            total_rows = self.cursor.fetchone()[0]

            self.cursor.execute(f"""
                SELECT COUNT(*) FROM {table}
                WHERE game_id IS NOT NULL AND game_gid IS NOT NULL
            """)
            both_filled = self.cursor.fetchone()[0]

            self.cursor.execute(f"""
                SELECT COUNT(*) FROM {table}
                WHERE game_id IS NULL OR game_gid IS NULL
            """)
            null_values = self.cursor.fetchone()[0]

            self.cursor.execute(f"""
                SELECT game_id, game_gid, COUNT(*) as cnt
                FROM {table}
                GROUP BY game_id, game_gid
                LIMIT 5
            """)
            sample_mapping = self.cursor.fetchall()

            results[table] = {
                "total_rows": total_rows,
                "both_filled": both_filled,
                "null_values": null_values,
                "sample_mapping": [dict(row) for row in sample_mapping]
            }

            logger.info(f"  📋 {table}:")
            logger.info(f"     - Total rows: {total_rows}")
            logger.info(f"     - Both filled: {both_filled}")
            logger.info(f"     - Null values: {null_values}")

        return results

    def check_foreign_key_integrity(self) -> Dict:
        """Check foreign key integrity"""
        logger.info("\n🔗 Checking foreign key integrity...")

        results = {}

        # Check log_events.game_id references
        self.cursor.execute("""
            SELECT COUNT(*) as orphaned
            FROM log_events le
            LEFT JOIN games g ON le.game_id = g.id
            WHERE le.game_id IS NOT NULL AND g.id IS NULL
        """)
        orphaned_game_id = self.cursor.fetchone()[0]

        # Check log_events.game_gid references
        self.cursor.execute("""
            SELECT COUNT(*) as orphaned
            FROM log_events le
            LEFT JOIN games g ON le.game_gid = CAST(g.gid AS INTEGER)
            WHERE le.game_gid IS NOT NULL AND g.gid IS NULL
        """)
        orphaned_game_gid = self.cursor.fetchone()[0]

        # Check event_nodes.game_id references
        self.cursor.execute("""
            SELECT COUNT(*) as orphaned
            FROM event_nodes en
            LEFT JOIN games g ON en.game_id = g.id
            WHERE en.game_id IS NOT NULL AND g.id IS NULL
        """)
        orphaned_event_nodes = self.cursor.fetchone()[0]

        results["orphaned_game_id_refs"] = {
            "log_events": orphaned_game_id,
            "event_nodes": orphaned_event_nodes
        }
        results["orphaned_game_gid_refs"] = {
            "log_events": orphaned_game_gid
        }

        logger.info(f"  Orphaned game_id references:")
        logger.info(f"    - log_events: {orphaned_game_id}")
        logger.info(f"    - event_nodes: {orphaned_event_nodes}")
        logger.info(f"  Orphaned game_gid references:")
        logger.info(f"    - log_events: {orphaned_game_gid}")

        return results

    def generate_migration_recommendations(self, analysis: Dict) -> List[str]:
        """Generate migration recommendations based on analysis"""
        logger.info("\n💡 Generating migration recommendations...")

        recommendations = []

        # Check if migration is already in progress
        tables_with_both = len(analysis["tables_with_both"])

        if tables_with_both > 0:
            recommendations.append(
                "✅ Migration is IN PROGRESS - some tables have both game_id and game_gid"
            )

        # Check tables that still use game_id
        tables_using_game_id = len(analysis["tables_with_game_id"])

        if tables_using_game_id > 0:
            recommendations.append(
                f"⚠️  {tables_using_game_id} tables still use game_id and need migration"
            )

        # Check critical tables
        critical_tables = ["common_params", "parameter_aliases", "join_configs", "flow_templates"]

        for table_info in analysis["tables_with_game_id"]:
            if table_info["name"] in critical_tables:
                recommendations.append(
                    f"🔴 CRITICAL: {table_info['name']} uses game_id - high priority migration"
                )

        # Check foreign keys
        for table_info in analysis["tables_with_game_id"]:
            if table_info["foreign_keys_to_games"]:
                for fk in table_info["foreign_keys_to_games"]:
                    if fk["from"] == "game_id":
                        recommendations.append(
                            f"🔴 {table_info['name']}: foreign key on game_id → must be migrated to game_gid"
                        )

        return recommendations

    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    """Main analysis function"""
    logger.info("🚀 Starting Game GID Migration Analysis...")

    analyzer = GameGidMigrationAnalyzer()

    try:
        # 1. Analyze tables
        table_analysis = analyzer.analyze_tables()

        # 2. Analyze data consistency
        data_analysis = analyzer.analyze_data_consistency()

        # 3. Check foreign key integrity
        fk_analysis = analyzer.check_foreign_key_integrity()

        # 4. Generate recommendations
        recommendations = analyzer.generate_migration_recommendations(table_analysis)

        # 5. Print summary
        logger.info("\n" + "="*80)
        logger.info("📊 ANALYSIS SUMMARY")
        logger.info("="*80)

        logger.info(f"\n✅ Tables using game_gid (migrated): {len(table_analysis['tables_with_game_gid'])}")
        for table in table_analysis["tables_with_game_gid"]:
            logger.info(f"  - {table['name']}")

        logger.info(f"\n⚠️  Tables using game_id (need migration): {len(table_analysis['tables_with_game_id'])}")
        for table in table_analysis["tables_with_game_id"]:
            logger.info(f"  - {table['name']}")
            if table["foreign_keys_to_games"]:
                for fk in table["foreign_keys_to_games"]:
                    logger.info(f"    FK: {fk['from']} → games.{fk['to']}")

        logger.info(f"\n🔄 Tables with BOTH (migration in progress): {len(table_analysis['tables_with_both'])}")
        for table in table_analysis["tables_with_both"]:
            logger.info(f"  - {table['name']}")

        logger.info(f"\n📋 Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            logger.info(f"  {i}. {rec}")

        logger.info("\n" + "="*80)
        logger.info("✅ Analysis complete!")
        logger.info("="*80)

    finally:
        analyzer.close()


if __name__ == "__main__":
    main()
