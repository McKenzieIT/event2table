#!/usr/bin/env python3
"""
Test Data Cleanup Script

Deletes all test games (GID >= 90000000) and their related data.
Protects production data (GID < 90000000) and specifically STAR001 (GID 10000147).

Safety features:
- Automatic database backup before cleanup
- Comprehensive analysis before deletion
- Protection of STAR001 (GID 10000147)
- Transaction-based cleanup (rollback on error)
- Detailed reporting

Usage:
    python scripts/tools/cleanup_test_data.py [--dry-run] [--force]

Arguments:
    --dry-run: Show what would be deleted without actually deleting
    --force: Skip confirmation prompt
"""

import sqlite3
import sys
import os
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Database path
DB_PATH = 'data/dwd_generator.db'

# Protection constants
STAR001_GID = '10000147'
TEST_GID_THRESHOLD = 90000000


def backup_database():
    """Create a timestamped backup of the database."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'{DB_PATH}.backup_{timestamp}'

    if os.path.exists(backup_path):
        print(f'⚠️  Backup already exists: {backup_path}')
        return backup_path

    print(f'📦 Creating backup: {backup_path}')
    import shutil
    shutil.copy2(DB_PATH, backup_path)
    print(f'✅ Backup created successfully')
    return backup_path


def analyze_database(conn):
    """Analyze database before cleanup."""
    cursor = conn.cursor()

    print('\n' + '=' * 70)
    print('DATABASE ANALYSIS - BEFORE CLEANUP')
    print('=' * 70)

    # Count all games
    cursor.execute('SELECT COUNT(*) FROM games')
    total_games = cursor.fetchone()[0]

    # Count test games (GID >= 90000000)
    cursor.execute('SELECT COUNT(*) FROM games WHERE CAST(gid AS INTEGER) >= ?', (TEST_GID_THRESHOLD,))
    test_games_count = cursor.fetchone()[0]

    # Count production games (GID < 90000000)
    cursor.execute('SELECT COUNT(*) FROM games WHERE CAST(gid AS INTEGER) < ?', (TEST_GID_THRESHOLD,))
    prod_games_count = cursor.fetchone()[0]

    # Check STAR001
    cursor.execute('SELECT id, gid, name FROM games WHERE gid = ?', (STAR001_GID,))
    star001 = cursor.fetchone()

    print(f'Total games: {total_games}')
    print(f'Test games (GID >= {TEST_GID_THRESHOLD}): {test_games_count}')
    print(f'Production games (GID < {TEST_GID_THRESHOLD}): {prod_games_count}')

    if star001:
        print(f'\n✅ STAR001 protected: id={star001[0]}, gid={star001[1]}, name={star001[2]}')
    else:
        print(f'\n⚠️  WARNING: STAR001 (GID {STAR001_GID}) not found!')

    # List test games
    print('\n' + '=' * 70)
    print(f'TEST GAMES TO BE DELETED (GID >= {TEST_GID_THRESHOLD}):')
    print('=' * 70)

    cursor.execute('''
        SELECT id, gid, name
        FROM games
        WHERE CAST(gid AS INTEGER) >= ?
        ORDER BY CAST(gid AS INTEGER)
    ''', (TEST_GID_THRESHOLD,))

    test_games = cursor.fetchall()
    test_game_ids = [str(g[0]) for g in test_games]
    test_game_gids = [g[1] for g in test_games]

    for game in test_games:
        print(f'  ID: {game[0]:<5} GID: {game[1]:<15} Name: {game[2]}')

    # Count related data
    if test_game_ids:
        # First check what columns exist in log_events
        cursor.execute('PRAGMA table_info(log_events)')
        columns = [col[1] for col in cursor.fetchall()]
        uses_game_gid = 'game_gid' in columns
        game_column = 'game_gid' if uses_game_gid else 'game_id'

        # Count events
        cursor.execute(f'''
            SELECT COUNT(*) FROM log_events
            WHERE {game_column} IN ({','.join(['?'] * len(test_game_ids if not uses_game_gid else test_game_gids))})
        ''', test_game_ids if not uses_game_gid else test_game_gids)
        events_count = cursor.fetchone()[0]

        # Count event_params (through log_events)
        cursor.execute(f'''
            SELECT COUNT(*) FROM event_params ep
            INNER JOIN log_events le ON ep.event_id = le.id
            WHERE le.{game_column} IN ({','.join(['?'] * len(test_game_ids if not uses_game_gid else test_game_gids))})
        ''', test_game_ids if not uses_game_gid else test_game_gids)
        params_count = cursor.fetchone()[0]

        # Count event_nodes
        cursor.execute(f'''
            SELECT COUNT(*) FROM event_nodes
            WHERE game_gid IN ({','.join(['?'] * len(test_game_gids))})
        ''', test_game_gids)
        nodes_count = cursor.fetchone()[0]

        print(f'\nRelated data to be deleted:')
        print(f'  Events: {events_count}')
        print(f'  Parameters: {params_count}')
        print(f'  Event Nodes: {nodes_count}')

    return test_games, test_game_ids, test_game_gids


def cleanup_test_data(conn, test_game_ids, test_game_gids, dry_run=False):
    """Delete test games and all related data."""
    cursor = conn.cursor()

    if dry_run:
        print('\n🔍 DRY RUN MODE - No changes will be made')
        return

    print('\n' + '=' * 70)
    print('STARTING CLEANUP (Transaction-based)')
    print('=' * 70)

    # Check what columns exist in log_events
    cursor.execute('PRAGMA table_info(log_events)')
    columns = [col[1] for col in cursor.fetchall()]
    uses_game_gid = 'game_gid' in columns
    game_column = 'game_gid' if uses_game_gid else 'game_id'
    game_ids_for_deletion = test_game_gids if uses_game_gid else test_game_ids

    try:
        # Begin transaction
        cursor.execute('BEGIN TRANSACTION')

        # Step 1: Delete event_params (through log_events)
        print('\n📝 Step 1: Deleting event_params...')
        cursor.execute(f'''
            DELETE FROM event_params
            WHERE event_id IN (
                SELECT id FROM log_events
                WHERE {game_column} IN ({','.join(['?'] * len(game_ids_for_deletion))})
            )
        ''', game_ids_for_deletion)
        params_deleted = cursor.rowcount
        print(f'   ✅ Deleted {params_deleted} event_params')

        # Step 2: Delete event_nodes
        print('\n📝 Step 2: Deleting event_nodes...')
        cursor.execute(f'''
            DELETE FROM event_nodes
            WHERE game_gid IN ({','.join(['?'] * len(test_game_gids))})
        ''', test_game_gids)
        nodes_deleted = cursor.rowcount
        print(f'   ✅ Deleted {nodes_deleted} event_nodes')

        # Step 3: Delete log_events
        print('\n📝 Step 3: Deleting log_events...')
        cursor.execute(f'''
            DELETE FROM log_events
            WHERE {game_column} IN ({','.join(['?'] * len(game_ids_for_deletion))})
        ''', game_ids_for_deletion)
        events_deleted = cursor.rowcount
        print(f'   ✅ Deleted {events_deleted} log_events')

        # Step 4: Delete games
        print('\n📝 Step 4: Deleting games...')
        cursor.execute(f'''
            DELETE FROM games
            WHERE id IN ({','.join(['?'] * len(test_game_ids))})
        ''', test_game_ids)
        games_deleted = cursor.rowcount
        print(f'   ✅ Deleted {games_deleted} games')

        # Commit transaction
        conn.commit()
        print('\n' + '=' * 70)
        print('✅ CLEANUP COMPLETED SUCCESSFULLY')
        print('=' * 70)

        return {
            'params_deleted': params_deleted,
            'nodes_deleted': nodes_deleted,
            'events_deleted': events_deleted,
            'games_deleted': games_deleted
        }

    except Exception as e:
        # Rollback on error
        conn.rollback()
        print(f'\n❌ ERROR during cleanup: {e}')
        print('🔄 Transaction rolled back - no changes made')
        raise


def verify_cleanup(conn):
    """Verify cleanup results."""
    cursor = conn.cursor()

    print('\n' + '=' * 70)
    print('VERIFICATION - AFTER CLEANUP')
    print('=' * 70)

    # Count remaining games
    cursor.execute('SELECT COUNT(*) FROM games')
    total_games = cursor.fetchone()[0]

    # Verify no test games remain
    cursor.execute('SELECT COUNT(*) FROM games WHERE CAST(gid AS INTEGER) >= ?', (TEST_GID_THRESHOLD,))
    remaining_test = cursor.fetchone()[0]

    # Count production games
    cursor.execute('SELECT COUNT(*) FROM games WHERE CAST(gid AS INTEGER) < ?', (TEST_GID_THRESHOLD,))
    prod_games = cursor.fetchone()[0]

    # Verify STAR001 still exists
    cursor.execute('SELECT id, gid, name FROM games WHERE gid = ?', (STAR001_GID,))
    star001 = cursor.fetchone()

    print(f'Total games remaining: {total_games}')
    print(f'Test games remaining: {remaining_test}')
    print(f'Production games remaining: {prod_games}')

    if star001:
        print(f'\n✅ STAR001 still exists: id={star001[0]}, gid={star001[1]}, name={star001[2]}')
    else:
        print(f'\n❌ CRITICAL: STAR001 (GID {STAR001_GID}) was deleted!')

    # List remaining games
    print('\n' + '=' * 70)
    print('REMAINING GAMES:')
    print('=' * 70)
    cursor.execute('SELECT id, gid, name FROM games ORDER BY CAST(gid AS INTEGER)')
    for game in cursor.fetchall():
        print(f'  ID: {game[0]:<5} GID: {game[1]:<15} Name: {game[2]}')

    success = (remaining_test == 0 and star001 is not None)
    return success


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description='Cleanup test data from database')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without actually deleting')
    parser.add_argument('--force', action='store_true', help='Skip confirmation prompt')
    args = parser.parse_args()

    print('=' * 70)
    print('TEST DATA CLEANUP SCRIPT')
    print('=' * 70)
    print(f'Database: {DB_PATH}')
    print(f'Test GID threshold: >= {TEST_GID_THRESHOLD}')
    print(f'Protected GID: {STAR001_GID} (STAR001)')

    if args.dry_run:
        print('🔍 DRY RUN MODE - No changes will be made')

    # Step 1: Backup
    if not args.dry_run:
        backup_path = backup_database()
        print(f'✅ Backup created: {backup_path}')
    else:
        print('\n🔍 DRY RUN: Skipping backup')

    # Step 2: Analyze
    conn = sqlite3.connect(DB_PATH)
    test_games, test_game_ids, test_game_gids = analyze_database(conn)

    if not test_games:
        print('\n✅ No test games found - nothing to clean up!')
        conn.close()
        return

    # Step 3: Confirm
    if not args.force and not args.dry_run:
        print('\n' + '=' * 70)
        response = input('⚠️  Do you want to proceed with cleanup? (yes/no): ')
        if response.lower() not in ['yes', 'y']:
            print('❌ Cleanup cancelled')
            conn.close()
            return

    # Step 4: Cleanup
    cleanup_test_data(conn, test_game_ids, test_game_gids, dry_run=args.dry_run)

    # Step 5: Verify
    if not args.dry_run:
        success = verify_cleanup(conn)
        if success:
            print('\n✅ All checks passed - cleanup successful!')
        else:
            print('\n⚠️  Some checks failed - please review')
    else:
        print('\n🔍 DRY RUN: Skipping verification')

    conn.close()


if __name__ == '__main__':
    main()
