#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Test Suite for game_id → game_gid Migration
Tests all modified functionality to ensure no regressions
"""

import sys
import os
import requests
import json
from datetime import datetime

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from backend.core.database import get_db_connection, DB_PATH
from backend.core.utils import (
    validate_game_exists,
    validate_game_id,
    check_game_has_events,
    get_categories_by_game,
    get_games_with_event_counts,
    get_event_with_game_info
)

class MigrationTestSuite:
    """Test suite for game_gid migration"""

    def __init__(self):
        self.base_url = "http://127.0.0.1:5001"
        self.results = []
        self.test_start_time = datetime.now()

    def log_result(self, category, test_name, passed, message=""):
        """Log test result"""
        self.results.append({
            'category': category,
            'test': test_name,
            'passed': passed,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if message:
            print(f"    {message}")

    # ==================== #
    # Backend Database Tests #
    # ==================== #

    def test_database_schema(self):
        """Test database schema has game_gid columns"""
        print("\n" + "="*60)
        print("Category 1: Database Schema Tests")
        print("="*60)

        conn = get_db_connection()
        cursor = conn.cursor()

        tables = [
            'log_events',
            'common_params',
            'event_nodes',
            'parameter_aliases',
            'field_selection_presets',
            'flow_templates',
            'field_name_mappings',
            'event_node_configs',
        ]

        all_passed = True
        for table in tables:
            cursor.execute(f'''
                SELECT COUNT(*) FROM pragma_table_info('{table}')
                WHERE name = 'game_gid'
            ''')
            has_column = cursor.fetchone()[0] > 0

            if has_column:
                self.log_result("Database Schema", f"{table} has game_gid column", True)
            else:
                self.log_result("Database Schema", f"{table} has game_gid column", False, "Column missing")
                all_passed = False

        conn.close()
        return all_passed

    def test_database_data_integrity(self):
        """Test database data integrity - no NULL game_gid"""
        print("\n" + "="*60)
        print("Category 2: Data Integrity Tests")
        print("="*60)

        conn = get_db_connection()
        cursor = conn.cursor()

        tables_to_check = [
            'log_events',
            'common_params',
            'event_nodes',
            'parameter_aliases',
            'field_name_mappings',
            'flow_templates',
            'event_node_configs',
        ]

        all_passed = True
        for table in tables_to_check:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            total = cursor.fetchone()[0]

            cursor.execute(f'SELECT COUNT(*) FROM {table} WHERE game_gid IS NULL')
            nulls = cursor.fetchone()[0]

            if total == 0:
                self.log_result("Data Integrity", f"{table} (empty table)", True)
            elif nulls == 0:
                self.log_result("Data Integrity", f"{table} data integrity", True, f"{total} rows, all valid")
            else:
                self.log_result("Data Integrity", f"{table} data integrity", False, f"{nulls}/{total} NULL game_gid")
                all_passed = False

        conn.close()
        return all_passed

    def test_database_foreign_keys(self):
        """Test foreign key relationships work correctly"""
        print("\n" + "="*60)
        print("Category 3: Foreign Key Tests")
        print("="*60)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Test log_events → games relationship
        cursor.execute('''
            SELECT COUNT(*) FROM log_events le
            LEFT JOIN games g ON le.game_gid = g.gid
            WHERE g.gid IS NULL
        ''')
        orphaned_events = cursor.fetchone()[0]

        if orphaned_events == 0:
            self.log_result("Foreign Keys", "log_events → games", True)
        else:
            self.log_result("Foreign Keys", "log_events → games", False, f"{orphaned_events} orphaned events")

        # Test event_node_configs → games relationship
        cursor.execute('''
            SELECT COUNT(*) FROM event_node_configs enc
            LEFT JOIN games g ON enc.game_gid = g.gid
            WHERE g.gid IS NULL
        ''')
        orphaned_nodes = cursor.fetchone()[0]

        if orphaned_nodes == 0:
            self.log_result("Foreign Keys", "event_node_configs → games", True)
        else:
            self.log_result("Foreign Keys", "event_node_configs → games", False, f"{orphaned_nodes} orphaned nodes")

        conn.close()
        return orphaned_events == 0 and orphaned_nodes == 0

    # ==================== #
    # Backend Utils Tests #
    # ==================== #

    def test_util_functions(self):
        """Test utility functions"""
        print("\n" + "="*60)
        print("Category 4: Utility Functions Tests")
        print("="*60)

        all_passed = True

        # Test validate_game_exists
        try:
            exists, game, error = validate_game_exists(10000147)
            # GID is stored as string in database, compare as string or convert to int
            game_gid = str(game.get('gid', '')) if game else ''
            if exists and game and (game_gid == '10000147' or game_gid == 10000147):
                self.log_result("Utils", "validate_game_exists(10000147)", True)
            else:
                self.log_result("Utils", "validate_game_exists(10000147)", False,
                               f"exists={exists}, game_gid={game_gid}, error={error}")
                all_passed = False
        except Exception as e:
            self.log_result("Utils", "validate_game_exists(10000147)", False, str(e))
            all_passed = False

        # Test validate_game_id
        try:
            valid, error = validate_game_id(10000147)
            if valid:
                self.log_result("Utils", "validate_game_id(10000147)", True)
            else:
                self.log_result("Utils", "validate_game_id(10000147)", False, error)
                all_passed = False
        except Exception as e:
            self.log_result("Utils", "validate_game_id(10000147)", False, str(e))
            all_passed = False

        # Test check_game_has_events
        try:
            has_events = check_game_has_events(10000147)
            if has_events:
                self.log_result("Utils", "check_game_has_events(10000147)", True)
            else:
                self.log_result("Utils", "check_game_has_events(10000147)", False, "No events found")
                all_passed = False
        except Exception as e:
            self.log_result("Utils", "check_game_has_events(10000147)", False, str(e))
            all_passed = False

        # Test get_games_with_event_counts
        try:
            games = get_games_with_event_counts()
            if games and len(games) > 0:
                self.log_result("Utils", "get_games_with_event_counts()", True, f"{len(games)} games")
            else:
                self.log_result("Utils", "get_games_with_event_counts()", False, "No games found")
                all_passed = False
        except Exception as e:
            self.log_result("Utils", "get_games_with_event_counts()", False, str(e))
            all_passed = False

        # Test get_event_with_game_info
        try:
            event = get_event_with_game_info(1)
            if event and event.get('game_gid'):
                self.log_result("Utils", "get_event_with_game_info(1)", True, f"game_gid={event['game_gid']}")
            else:
                self.log_result("Utils", "get_event_with_game_info(1)", False, "Event not found or missing game_gid")
                all_passed = False
        except Exception as e:
            self.log_result("Utils", "get_event_with_game_info(1)", False, str(e))
            all_passed = False

        # Test get_categories_by_game
        try:
            categories = get_categories_by_game(10000147)
            if categories is not None:  # Can be empty list
                self.log_result("Utils", "get_categories_by_game(10000147)", True, f"{len(categories)} categories")
            else:
                self.log_result("Utils", "get_categories_by_game(10000147)", False, "Returned None")
                all_passed = False
        except Exception as e:
            self.log_result("Utils", "get_categories_by_game(10000147)", False, str(e))
            all_passed = False

        return all_passed

    # ==================== #
    # Backend API Tests #
    # ==================== #

    def test_api_endpoints(self):
        """Test all modified API endpoints"""
        print("\n" + "="*60)
        print("Category 5: API Endpoint Tests")
        print("="*60)

        all_passed = True

        # Test 1: /api/games
        try:
            response = requests.get(f"{self.base_url}/api/games", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    games = data.get('data', [])
                    if len(games) > 0:
                        # Check that games have event counts
                        total_events = sum(g.get('event_count', 0) for g in games)
                        self.log_result("API", "/api/games", True, f"{len(games)} games, {total_events} events")
                    else:
                        self.log_result("API", "/api/games", False, "No games returned")
                        all_passed = False
                else:
                    self.log_result("API", "/api/games", False, data.get('error', 'Unknown error'))
                    all_passed = False
            else:
                self.log_result("API", "/api/games", False, f"HTTP {response.status_code}")
                all_passed = False
        except Exception as e:
            self.log_result("API", "/api/games", False, str(e))
            all_passed = False

        # Test 2: /api/dashboard-statistics
        try:
            response = requests.get(f"{self.base_url}/api/dashboard-statistics", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    stats = data.get('data', {})
                    if stats.get('game_count', 0) > 0:
                        self.log_result("API", "/api/dashboard-statistics", True,
                                     f"{stats['game_count']} games, {stats['event_count']} events")
                    else:
                        self.log_result("API", "/api/dashboard-statistics", False, "No statistics")
                        all_passed = False
                else:
                    self.log_result("API", "/api/dashboard-statistics", False, data.get('error'))
                    all_passed = False
            else:
                self.log_result("API", "/api/dashboard-statistics", False, f"HTTP {response.status_code}")
                all_passed = False
        except Exception as e:
            self.log_result("API", "/api/dashboard-statistics", False, str(e))
            all_passed = False

        # Test 3: /event_node_builder/api/stats?game_gid=10000147
        try:
            response = requests.get(f"{self.base_url}/event_node_builder/api/stats?game_gid=10000147", timeout=10)
            if response.status_code == 200:
                self.log_result("API", "/event_node_builder/api/stats", True, "HTTP 200")
            else:
                self.log_result("API", "/event_node_builder/api/stats", False, f"HTTP {response.status_code}")
                all_passed = False
        except Exception as e:
            self.log_result("API", "/event_node_builder/api/stats", False, str(e))
            all_passed = False

        # Test 4: /event_node_builder/api/search?game_gid=10000147
        try:
            response = requests.get(f"{self.base_url}/event_node_builder/api/search?game_gid=10000147", timeout=10)
            if response.status_code == 200:
                data = response.json()
                nodes = data.get('data', {}).get('nodes', [])
                self.log_result("API", "/event_node_builder/api/search", True, f"{len(nodes)} nodes")
            else:
                self.log_result("API", "/event_node_builder/api/search", False, f"HTTP {response.status_code}")
                all_passed = False
        except Exception as e:
            self.log_result("API", "/event_node_builder/api/search", False, str(e))
            all_passed = False

        return all_passed

    # ==================== #
    # Frontend Tests #
    # ==================== #

    def test_frontend_pages(self):
        """Test frontend pages are accessible"""
        print("\n" + "="*60)
        print("Category 6: Frontend Accessibility Tests")
        print("="*60)

        all_passed = True

        pages = [
            ('/', 'Home page'),
            ('/dashboard', 'Dashboard'),
            ('/events', 'Events page'),
            ('/event_nodes', 'Event Nodes page'),
        ]

        for path, name in pages:
            try:
                response = requests.get(f"{self.base_url}{path}", timeout=10)
                if response.status_code == 200:
                    self.log_result("Frontend", f"{name} ({path})", True)
                else:
                    self.log_result("Frontend", f"{name} ({path})", False, f"HTTP {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_result("Frontend", f"{name} ({path})", False, str(e))
                all_passed = False

        return all_passed

    # ==================== #
    # Integration Tests #
    # ==================== #

    def test_end_to_end_scenarios(self):
        """Test end-to-end scenarios"""
        print("\n" + "="*60)
        print("Category 7: End-to-End Integration Tests")
        print("="*60)

        all_passed = True

        # Scenario 1: View game details and statistics
        try:
            # Step 1: Get games list
            response = requests.get(f"{self.base_url}/api/games", timeout=10)
            if response.status_code != 200:
                raise Exception(f"Failed to get games: HTTP {response.status_code}")

            games_data = response.json()
            if not games_data.get('success'):
                raise Exception("API returned failure")

            games = games_data.get('data', [])
            if not games:
                raise Exception("No games found")

            # Step 2: Get first game's GID
            game_gid = games[0]['gid']

            # Step 3: Get game statistics
            response = requests.get(f"{self.base_url}/event_node_builder/api/stats?game_gid={game_gid}", timeout=10)
            if response.status_code != 200:
                raise Exception(f"Failed to get game stats: HTTP {response.status_code}")

            self.log_result("Integration", "View game details scenario", True,
                          f"Game {game_gid}: {games[0]['name']}")
        except Exception as e:
            self.log_result("Integration", "View game details scenario", False, str(e))
            all_passed = False

        # Scenario 2: Check dashboard data consistency
        try:
            # Get dashboard statistics
            response = requests.get(f"{self.base_url}/api/dashboard-statistics", timeout=10)
            if response.status_code != 200:
                raise Exception(f"Failed to get dashboard stats: HTTP {response.status_code}")

            stats_data = response.json()
            if not stats_data.get('success'):
                raise Exception("Dashboard API returned failure")

            stats = stats_data.get('data', {})

            # Get games list and verify consistency
            response = requests.get(f"{self.base_url}/api/games", timeout=10)
            if response.status_code != 200:
                raise Exception(f"Failed to get games: HTTP {response.status_code}")

            games_data = response.json()
            games = games_data.get('data', [])

            # Verify game counts match
            if stats.get('game_count') == len(games):
                self.log_result("Integration", "Dashboard data consistency", True,
                              f"{stats['game_count']} games")
            else:
                self.log_result("Integration", "Dashboard data consistency", False,
                              f"Mismatch: dashboard={stats['game_count']}, games={len(games)}")
                all_passed = False
        except Exception as e:
            self.log_result("Integration", "Dashboard data consistency", False, str(e))
            all_passed = False

        return all_passed

    # ==================== #
    # Test Runner #
    # ==================== #

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*80)
        print(" "*20 + "GAME_ID → GAME_GID MIGRATION TEST SUITE")
        print("="*80)
        print(f"Started at: {self.test_start_time.isoformat()}")
        print(f"Target: {self.base_url}")

        categories = [
            ("Database Schema", self.test_database_schema),
            ("Data Integrity", self.test_database_data_integrity),
            ("Foreign Keys", self.test_database_foreign_keys),
            ("Utility Functions", self.test_util_functions),
            ("API Endpoints", self.test_api_endpoints),
            ("Frontend", self.test_frontend_pages),
            ("Integration", self.test_end_to_end_scenarios),
        ]

        category_results = {}
        for category_name, test_func in categories:
            try:
                passed = test_func()
                category_results[category_name] = passed
            except Exception as e:
                print(f"\n❌ ERROR in {category_name}: {e}")
                category_results[category_name] = False

        # Print summary
        self.print_summary(category_results)

        # Save results
        self.save_results()

        return all(category_results.values())

    def print_summary(self, category_results):
        """Print test summary"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)

        total_passed = sum(1 for r in self.results if r['passed'])
        total_failed = sum(1 for r in self.results if not r['passed'])
        total_tests = len(self.results)

        print(f"\nTotal Tests: {total_tests}")
        print(f"Passed: {total_passed} ({100*total_passed//total_tests}%)")
        print(f"Failed: {total_failed}")

        print("\nCategory Results:")
        for category, passed in category_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {category}: {status}")

        print("\nFailed Tests:")
        failed_tests = [r for r in self.results if not r['passed']]
        if failed_tests:
            for test in failed_tests:
                print(f"  - [{test['category']}] {test['test']}")
                if test['message']:
                    print(f"    {test['message']}")
        else:
            print("  None! All tests passed! 🎉")

        test_end_time = datetime.now()
        duration = (test_end_time - self.test_start_time).total_seconds()

        print("\n" + "="*80)
        print(f"Test Duration: {duration:.2f} seconds")
        print(f"Ended at: {test_end_time.isoformat()}")
        print("="*80)

    def save_results(self):
        """Save test results to file"""
        results_dir = os.path.join(os.path.dirname(__file__), '../../test-results')
        os.makedirs(results_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = os.path.join(results_dir, f'migration_test_results_{timestamp}.json')

        with open(results_file, 'w') as f:
            json.dump({
                'start_time': self.test_start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'results': self.results,
                'summary': {
                    'total': len(self.results),
                    'passed': sum(1 for r in self.results if r['passed']),
                    'failed': sum(1 for r in self.results if not r['passed']),
                }
            }, f, indent=2)

        print(f"\n📄 Results saved to: {results_file}")


if __name__ == '__main__':
    suite = MigrationTestSuite()
    all_passed = suite.run_all_tests()
    sys.exit(0 if all_passed else 1)
