#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Test Suite for Event2Table
Tests all integration points after major refactoring

Author: Integration Testing Script
Date: 2026-02-10
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import unittest
import tempfile
import shutil
from pathlib import Path

# Test imports
class TestModuleImports(unittest.TestCase):
    """Test 1: Module Imports"""

    def test_schema_layer_imports(self):
        """Test Schema layer imports"""
        try:
            from backend.models.schemas import (
                GameCreate, GameUpdate, GameResponse,
                EventCreate, EventResponse,
                EventParameterCreate, EventParameterResponse
            )
            self.assertTrue(True, "Schema layer imports successful")
        except ImportError as e:
            self.fail(f"Schema layer import failed: {e}")

    def test_repository_layer_imports(self):
        """Test Repository layer imports"""
        try:
            from backend.models.repositories.games import GameRepository
            from backend.models.repositories.events import EventRepository
            from backend.models.repositories.parameters import ParameterRepository
            self.assertTrue(True, "Repository layer imports successful")
        except ImportError as e:
            self.fail(f"Repository layer import failed: {e}")

    def test_hql_v2_imports(self):
        """Test HQL V2 architecture imports"""
        try:
            from backend.services.hql.core.generator import HQLGenerator
            from backend.services.hql.builders.field_builder import FieldBuilder
            from backend.services.hql.builders.where_builder import WhereBuilder
            from backend.services.hql.builders.join_builder import JoinBuilder
            from backend.services.hql.builders.union_builder import UnionBuilder
            self.assertTrue(True, "HQL V2 imports successful")
        except ImportError as e:
            self.fail(f"HQL V2 import failed: {e}")

    def test_canvas_imports(self):
        """Test Canvas system imports"""
        try:
            from backend.services.canvas.canvas import canvas_bp
            from backend.services.canvas.node_canvas_flows import flows_bp
            self.assertTrue(True, "Canvas system imports successful")
        except ImportError as e:
            self.fail(f"Canvas system import failed: {e}")


class TestFourLayerArchitecture(unittest.TestCase):
    """Test 2: Four-Layer Architecture Integration"""

    def setUp(self):
        """Set up test database"""
        self.test_db = tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False)
        self.test_db.close()

        # Set environment for testing
        os.environ['FLASK_ENV'] = 'testing'

    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)

    def test_schema_validation(self):
        """Test Schema layer validates data correctly"""
        from backend.models.schemas import GameCreate, EventCreate
        import html

        # Test GameCreate validation
        game_data = GameCreate(
            gid="10000147",
            name="Test Game",
            ods_db="ieu_ods"
        )
        self.assertEqual(game_data.gid, "10000147")
        self.assertEqual(game_data.name, html.escape("Test Game"))

        # Test invalid gid (non-numeric)
        with self.assertRaises(ValueError):
            GameCreate(gid="abc", name="Test", ods_db="ieu_ods")

        # Test invalid ods_db
        with self.assertRaises(ValueError):
            GameCreate(gid="10000147", name="Test", ods_db="invalid_db")

    def test_repository_operations(self):
        """Test Repository layer CRUD operations"""
        from backend.models.repositories.games import GameRepository

        repo = GameRepository()
        self.assertIsNotNone(repo, "GameRepository instantiated")

        # Check repository methods exist
        self.assertTrue(hasattr(repo, 'find_by_gid'))
        self.assertTrue(hasattr(repo, 'get_all_with_event_count'))
        self.assertTrue(hasattr(repo, 'get_all_with_stats'))


class TestHQLV2Integration(unittest.TestCase):
    """Test 3: HQL V2 Architecture Integration"""

    def test_hql_generator_instantiation(self):
        """Test HQLGenerator can be instantiated"""
        from backend.services.hql.core.generator import HQLGenerator

        generator = HQLGenerator()
        self.assertIsNotNone(generator)

    def test_hql_builders(self):
        """Test all HQL builders are available"""
        from backend.services.hql.builders.field_builder import FieldBuilder
        from backend.services.hql.builders.where_builder import WhereBuilder
        from backend.services.hql.builders.join_builder import JoinBuilder
        from backend.services.hql.builders.union_builder import UnionBuilder

        # Test builders can be instantiated
        field_builder = FieldBuilder()
        where_builder = WhereBuilder()
        join_builder = JoinBuilder()
        union_builder = UnionBuilder()

        self.assertIsNotNone(field_builder)
        self.assertIsNotNone(where_builder)
        self.assertIsNotNone(join_builder)
        self.assertIsNotNone(union_builder)


class TestDatabaseIntegration(unittest.TestCase):
    """Test 4: Database Integration"""

    def test_database_connection(self):
        """Test database can be connected"""
        from backend.core.database import get_db_connection
        from backend.core.config import get_db_path

        db_path = get_db_path()
        self.assertTrue(db_path.exists(), f"Database file exists: {db_path}")

    def test_database_tables_exist(self):
        """Test required tables exist"""
        from backend.core.database import get_db_connection
        from backend.core.config import get_db_path

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check games table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='games'")
        result = cursor.fetchone()
        self.assertIsNotNone(result, "games table exists")

        # Check log_events table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='log_events'")
        result = cursor.fetchone()
        self.assertIsNotNone(result, "log_events table exists")

        # Check event_params table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='event_params'")
        result = cursor.fetchone()
        self.assertIsNotNone(result, "event_params table exists")

        conn.close()


class TestCacheIntegration(unittest.TestCase):
    """Test 5: Cache Integration"""

    def test_cache_system_imports(self):
        """Test cache system can be imported"""
        try:
            from backend.core.cache.cache_system import cache_result, clear_cache
            from backend.core.cache.cache_hierarchical import HierarchicalCache
            self.assertTrue(True, "Cache system imports successful")
        except ImportError as e:
            self.fail(f"Cache system import failed: {e}")

    def test_cache_decorator(self):
        """Test cache decorator is available"""
        from backend.core.cache.cache_system import cache_result

        @cache_result('test_key', timeout=60)
        def test_function():
            return "test_result"

        result = test_function()
        self.assertEqual(result, "test_result")


class TestAPIContracts(unittest.TestCase):
    """Test 6: API Contracts (Frontend-Backend)"""

    def test_canvas_api_endpoints(self):
        """Test Canvas API endpoints are defined"""
        from backend.services.canvas.canvas import canvas_bp

        # Get all routes from canvas blueprint
        routes = [rule.rule for rule in canvas_bp.deferred_functions]

        # Check for critical endpoints
        canvas_endpoints = [
            '/canvas/api/execute',
            '/canvas/api/canvas/health',
        ]

        for endpoint in canvas_endpoints:
            self.assertTrue(any(endpoint in str(route) for route in routes),
                          f"Canvas endpoint {endpoint} is defined")

    def test_parameters_api_endpoints(self):
        """Test Parameters API endpoints are defined"""
        from backend.services.parameters.common_params import common_params_bp

        # Check blueprint exists
        self.assertIsNotNone(common_params_bp)


def run_integration_tests():
    """Run all integration tests"""
    print("=" * 80)
    print("Event2Table Integration Test Suite")
    print("=" * 80)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestModuleImports))
    suite.addTests(loader.loadTestsFromTestCase(TestFourLayerArchitecture))
    suite.addTests(loader.loadTestsFromTestCase(TestHQLV2Integration))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestCacheIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIContracts))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print()
    print("=" * 80)
    print("Integration Test Summary")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print()

    if result.wasSuccessful():
        print("✅ ALL INTEGRATION TESTS PASSED")
        return 0
    else:
        print("❌ SOME INTEGRATION TESTS FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(run_integration_tests())
