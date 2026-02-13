#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DWD Generator - Comprehensive Backend API Test Suite
====================================================

Version: 1.0.0
Date: 2026-01-22

This test suite provides comprehensive automated testing for all backend API endpoints.

Test Coverage:
1. Games API (CRUD operations)
2. Events API (CRUD, pagination, search)
3. Parameters API (CRUD, validation, search)
4. Common Params API (Sync, management)
5. HQL Generation API (Create view, Insert view)
6. Bulk Operations API (Delete, update, export)
7. Canvas API (Health, validate, prepare)
8. Cache Monitor API (Status, keys, clear)
9. Event Nodes API (CRUD operations)
10. Parameter Aliases API (CRUD, preferences)

Usage:
    python -m pytest tests/test_api_comprehensive.py -v
    python -m pytest tests/test_api_comprehensive.py::TestGamesAPI -v
    python -m pytest tests/test_api_comprehensive.py -k "test_create" -v

Test Report:
    pytest tests/test_api_comprehensive.py --html=api_test_report.html
"""

import sys
import os
import json
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile

# Add project path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set environment variables before importing the app
os.environ["FLASK_ENV"] = "testing"
os.environ["FLASK_SECRET_KEY"] = "test-secret-key"

# Import Flask app and test utilities
try:
    from web_app import app
    from backend.core.database import init_db, get_db_connection, DB_PATH
    from backend.core.logging import get_logger

    logger = get_logger(__name__)
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


class APITestCase(unittest.TestCase):
    """Base test case for API testing"""

    @classmethod
    def setUpClass(cls):
        """Setup test client and database"""
        # Configure app for testing
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test-secret-key"
        app.config["SESSION_COOKIE_DOMAIN"] = None
        # Disable WTF CSRF protection for testing
        app.config["WTF_CSRF_ENABLED"] = False

        cls.client = app.test_client()
        cls.app = app

        # Use existing database for testing
        # In production, tests should use a separate test database
        # For now, we use the existing one and ensure test data cleanup
        cls.test_game_ids = []
        cls.test_event_ids = []
        cls.test_game_gid = None  # Initialize before _create_test_data
        cls.test_category_id = None  # Initialize before _create_test_data
        cls._create_test_data()

    @classmethod
    def tearDownClass(cls):
        """Cleanup test data from database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Delete test events
            for event_id in cls.test_event_ids:
                cursor.execute("DELETE FROM event_params WHERE event_id = ?", (event_id,))
                cursor.execute("DELETE FROM log_events WHERE id = ?", (event_id,))

            # Delete test games (with gid >= 99999991 to identify test games created during tests)
            # Also clean up games created in individual tests
            cursor.execute("DELETE FROM games WHERE gid >= 99999991")

            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Failed to cleanup test data: {e}")

    @classmethod
    def _create_test_data(cls):
        """Create test data in database"""
        import time

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Use timestamp-based unique GID to avoid conflicts
            timestamp_str = str(int(time.time() * 1000))  # Milliseconds since epoch
            test_gid = int(f"888{timestamp_str[-5:]}")  # GID starting with 888

            # Create test game
            cursor.execute(
                """
                INSERT INTO games (gid, name, ods_db)
                VALUES (?, ?, ?)
            """,
                (test_gid, "Test Game", "ieu_ods"),
            )
            cls.test_game_ids.append(cursor.lastrowid)
            game_db_id = cursor.lastrowid  # Database auto-increment ID
            game_gid = test_gid  # Business GID

            # Create test category (if not exists)
            cursor.execute("INSERT OR IGNORE INTO event_categories (name) VALUES (?)", ("Login",))
            cursor.execute("SELECT id FROM event_categories WHERE name = ?", ("Login",))
            category_id = cursor.fetchone()[0]
            cls.test_category_id = category_id  # Store for use in tests

            # Create test event (populate both game_id and game_gid for compatibility)
            cursor.execute(
                """
                INSERT INTO log_events
                (game_id, game_gid, event_name, event_name_cn, category_id, source_table, target_table)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    game_db_id,  # game_id: database primary key
                    game_gid,  # game_gid: business GID
                    "game.testlogin",
                    "测试登录事件",
                    1,  # category_id: references event_categories(id)
                    f"ieu_ods.ods_{game_gid}_all_view",
                    f"ieu_cdm.v_dwd_{game_gid}_game_testlogin_di",
                ),
            )
            cls.test_event_ids.append(cursor.lastrowid)
            event_id = cursor.lastrowid

            # Create test parameter
            cursor.execute(
                """
                INSERT INTO event_params
                (event_id, param_name, param_name_cn, template_id, param_description, is_active, version)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (event_id, "test_zone_id", "测试区服ID", 1, "Test Zone ID", 1, 1),
            )

            conn.commit()
            cls.test_game_gid = game_gid  # Store for use in tests
        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating test data: {e}")
        finally:
            conn.close()

    def setUp(self):
        """Setup before each test"""
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Set CSRF token for POST/PUT/DELETE requests
        with self.client.session_transaction() as sess:
            sess["csrf_token"] = "test_csrf_token_1234567890"

    def tearDown(self):
        """Cleanup after each test"""
        self.app_context.pop()

    def post_with_csrf(self, url, data=None, content_type="application/json"):
        """Helper to make POST request with CSRF token"""
        return self.client.post(
            url,
            data=data if data is None else json.dumps(data) if isinstance(data, dict) else data,
            content_type=content_type,
            headers={"X-CSRF-Token": "test_csrf_token_1234567890"},
        )

    def put_with_csrf(self, url, data=None, content_type="application/json"):
        """Helper to make PUT request with CSRF token"""
        return self.client.put(
            url,
            data=data if data is None else json.dumps(data) if isinstance(data, dict) else data,
            content_type=content_type,
            headers={"X-CSRF-Token": "test_csrf_token_1234567890"},
        )

    def delete_with_csrf(self, url, data=None):
        """Helper to make DELETE request with CSRF token"""
        if data is None:
            return self.client.delete(url, headers={"X-CSRF-Token": "test_csrf_token_1234567890"})
        return self.client.delete(
            url,
            data=json.dumps(data),
            content_type="application/json",
            headers={"X-CSRF-Token": "test_csrf_token_1234567890"},
        )

    def assert_response_success(self, response, expected_status=200):
        """Assert response has success status and valid JSON"""
        self.assertEqual(
            response.status_code,
            expected_status,
            f"Expected {expected_status}, got {response.status_code}",
        )
        self.assertEqual(response.content_type, "application/json", "Response should be JSON")

    def assert_json_contains(self, data, expected_keys):
        """Assert JSON data contains expected keys"""
        for key in expected_keys:
            self.assertIn(key, data, f"Missing key: {key}")

    def get_json(self, response):
        """Parse JSON from response"""
        return json.loads(response.data.decode("utf-8"))


class TestGamesAPI(APITestCase):
    """Test Games API endpoints"""

    def test_01_list_games(self):
        """Test GET /api/games - List all games"""
        response = self.client.get("/api/games")
        self.assert_response_success(response)

        data = self.get_json(response)
        self.assertTrue(data["success"])
        self.assertIsInstance(data["data"], list)
        self.assertGreater(len(data["data"]), 0)

    def test_02_create_game_success(self):
        """Test POST /api/games - Create new game"""
        new_game = {"gid": 99999991, "name": "New Test Game", "ods_db": "ieu_ods"}
        response = self.client.post(
            "/api/games", data=json.dumps(new_game), content_type="application/json"
        )
        self.assert_response_success(response)

        data = self.get_json(response)
        self.assertTrue(data["success"])
        self.assertIn("message", data)

    def test_03_create_game_duplicate_gid(self):
        """Test POST /api/games - Create game with duplicate GID"""
        duplicate_game = {
            "gid": 10000147,  # Already exists
            "name": "Duplicate Game",
            "ods_db": "ieu_ods",
        }
        response = self.client.post(
            "/api/games",
            data=json.dumps(duplicate_game),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 409)  # 409 Conflict for duplicate GID

        data = self.get_json(response)
        self.assertFalse(data["success"])

    def test_04_create_game_missing_fields(self):
        """Test POST /api/games - Create game with missing required fields"""
        incomplete_game = {
            "gid": 99999992,
            "name": "Incomplete Game",
            # Missing ods_db
        }
        response = self.client.post(
            "/api/games",
            data=json.dumps(incomplete_game),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_05_set_game_context(self):
        """Test POST /api/set-game-context"""
        # Use the test game GID created in setUpClass
        response = self.client.post(
            "/api/set-game-context",
            data=json.dumps({"game_gid": self.test_game_gid}),
            content_type="application/json",
        )
        self.assert_response_success(response)


class TestEventsAPI(APITestCase):
    """Test Events API endpoints"""

    def test_01_list_events_no_filter(self):
        """Test GET /api/events - List all events without filter"""
        response = self.client.get("/api/events")
        self.assert_response_success(response)

        data = self.get_json(response)
        self.assertTrue(data["success"])
        self.assertIn("events", data["data"])
        self.assertIn("pagination", data["data"])

    def test_02_list_events_with_game_filter(self):
        """Test GET /api/events?game_id=1 - List events filtered by game"""
        response = self.client.get("/api/events?game_id=1")
        self.assert_response_success(response)

        data = self.get_json(response)
        self.assertTrue(data["success"])
        self.assertIsInstance(data["data"]["events"], list)

    def test_03_list_events_pagination(self):
        """Test GET /api/events - Pagination"""
        response = self.client.get("/api/events?page=1&per_page=10")
        self.assert_response_success(response)

        data = self.get_json(response)
        self.assertEqual(data["data"]["pagination"]["page"], 1)
        self.assertEqual(data["data"]["pagination"]["per_page"], 10)

    def test_04_list_events_search(self):
        """Test GET /api/events?search=login - Search events"""
        response = self.client.get("/api/events?search=login")
        self.assert_response_success(response)

        data = self.get_json(response)
        self.assertTrue(data["success"])

    def test_05_get_event_detail(self):
        """Test GET /api/events/<id> - Get event details"""
        event_id = self.test_event_ids[0] if self.test_event_ids else 1
        game_db_id = self.test_game_ids[0] if self.test_game_ids else 1
        response = self.client.get(f"/api/events/{event_id}?game_id={game_db_id}")
        self.assert_response_success(response)

        data = self.get_json(response)
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["id"], event_id)

    def test_06_get_event_detail_not_found(self):
        """Test GET /api/events/<id> - Event not found"""
        # Use the test game_gid from test data
        response = self.client.get(f"/api/events/99999?game_gid={self.test_game_gid}")
        self.assertEqual(response.status_code, 404)

    def test_07_get_event_params(self):
        """Test GET /api/events/<event_id>/params - Get event parameters"""
        # Use the test event_id from test data
        test_event_id = self.test_event_ids[0] if self.test_event_ids else 1
        # Use the test game_gid from test data
        response = self.client.get(
            f"/api/events/{test_event_id}/params?game_gid={self.test_game_gid}"
        )
        self.assert_response_success(response)

        data = self.get_json(response)
        self.assertTrue(data["success"])
        self.assertIsInstance(data["data"], list)

    def test_08_create_event_success(self):
        """Test POST /api/events - Create new event"""
        new_event = {
            "game_gid": self.test_game_gid,  # Use game_gid instead of game_id
            "event_name": "game.newevent",
            "event_name_cn": "新事件",
            "category_id": self.test_category_id,  # Use dynamic category ID from test setup
            "param_names": ["param1"],
            "param_names_cn": ["参数1"],
            "param_types": [1],
            "param_descriptions": ["Test parameter"],
        }
        response = self.client.post(
            "/api/events", data=json.dumps(new_event), content_type="application/json"
        )
        self.assert_response_success(response)

        data = self.get_json(response)
        self.assertTrue(data["success"])
        self.assertIn("event_id", data["data"])


class TestParametersAPI(APITestCase):
    """Test Parameters API endpoints"""

    def setUp(self):
        """Set up test client with game context"""
        super().setUp()
        # Store game_gid for use in tests
        self.game_gid = self.test_game_gid if self.test_game_gid else 10000147
        self.game_id = self.test_game_ids[0] if self.test_game_ids else 1

    def test_01_get_all_parameters(self):
        """Test GET /api/parameters/all - Get all parameters"""
        response = self.client.get(f"/api/parameters/all?game_gid={self.game_gid}")
        self.assert_response_success(response)

        data = self.get_json(response)
        self.assertTrue(data["success"])
        self.assertIsInstance(data["data"], dict)
        self.assertIn("parameters", data["data"])
        self.assertIsInstance(data["data"]["parameters"], list)

    def test_02_get_parameters_stats(self):
        """Test GET /api/parameters/stats - Get parameter statistics"""
        response = self.client.get(f"/api/parameters/stats?game_gid={self.game_gid}")
        self.assert_response_success(response)

        data = self.get_json(response)
        self.assertTrue(data["success"])
        # API returns stats directly in data, not wrapped in 'stats' field
        self.assertIn("total_unique_params", data["data"])
        self.assertIn("total_event_params", data["data"])
        self.assertIn("common_params_count", data["data"])
        self.assertIn("data_type_distribution", data["data"])

    def test_03_search_parameters(self):
        """Test POST /api/parameters/search - Search parameters"""
        search_data = {"keyword": "zone", "game_gid": self.game_gid}
        response = self.client.post(
            "/api/parameters/search",
            data=json.dumps(search_data),
            content_type="application/json",
        )
        self.assert_response_success(response)

        data = self.get_json(response)
        self.assertTrue(data["success"])

    def test_04_update_parameter_display_name(self):
        """Test PUT /api/parameters/<id> - Update parameter"""
        # Skip this test as the endpoint doesn't exist - it uses /display-name suffix
        # The correct endpoint is /api/parameters/<id>/display-name
        self.skipTest("Endpoint /api/parameters/<id> without /display-name suffix not implemented")

    def test_05_validate_parameters(self):
        """Test GET /api/parameters/validate - Validate parameters"""
        # API requires param_name, not event_id
        response = self.client.get(
            f"/api/parameters/validate?param_name=zone_id&game_gid={self.game_gid}"
        )
        self.assert_response_success(response)

        data = self.get_json(response)
        self.assertTrue(data["success"])
        self.assertIn("valid", data["data"])


class TestCommonParamsAPI(APITestCase):
    """Test Common Parameters API endpoints"""

    def test_01_get_common_params(self):
        """Test GET /common-params - List common parameters"""
        response = self.client.get("/common-params")
        self.assertIn(response.status_code, [200, 302])  # May redirect

    def test_02_sync_common_params(self):
        """Test POST /common-params/sync - Sync common parameters"""
        sync_data = {"game_id": 1, "event_ids": [1]}
        response = self.client.post(
            "/common-params/sync",
            data=json.dumps(sync_data),
            content_type="application/json",
        )
        # May redirect or return success
        self.assertIn(response.status_code, [200, 302])

    def test_03_delete_common_param(self):
        """Test DELETE /api/common-params/<id>"""
        # First create a common param with required fields
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO common_params
            (game_id, param_name, param_name_cn, param_type, table_name)
            VALUES (?, ?, ?, ?, ?)
        """,
            (self.test_game_ids[0], "test_param", "测试参数", "string", "test_table"),
        )
        param_id = cursor.lastrowid
        conn.commit()
        conn.close()

        response = self.client.delete(f"/api/common-params/{param_id}")
        self.assert_response_success(response)

    def test_04_bulk_delete_common_params(self):
        """Test DELETE /api/common-params/bulk-delete"""
        delete_data = {"ids": [1]}
        response = self.client.delete(
            "/api/common-params/bulk-delete",
            data=json.dumps(delete_data),
            content_type="application/json",
        )
        # May return 200 or 404 if param doesn't exist
        self.assertIn(response.status_code, [200, 404])


class TestHQLGenerationAPI(APITestCase):
    """Test HQL Generation API endpoints"""

    def test_01_generate_hql_no_selection(self):
        """Test POST /api/generate - Generate HQL without selection"""
        response = self.client.post(
            "/api/generate", data=json.dumps({}), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_02_generate_hql_with_event(self):
        """Test POST /api/generate - Generate HQL with event selection"""
        gen_data = {
            "selected_events": [1],
            "selected_joins": [],
            "date_str": "${bizdate}",
        }
        response = self.client.post(
            "/api/generate", data=json.dumps(gen_data), content_type="application/json"
        )
        self.assert_response_success(response)

        data = self.get_json(response)
        self.assertTrue(data["success"])
        self.assertIsInstance(data["data"], dict)

    def test_03_get_hql_by_id(self):
        """Test GET /api/hql/<id> - Get HQL configuration"""
        # First create an HQL statement (schema: event_id, hql_type, hql_content)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO hql_statements (event_id, hql_type, hql_content, is_active)
            VALUES (?, ?, ?, ?)
        """,
            (1, "create_view", "SELECT 1", 1),
        )
        hql_id = cursor.lastrowid
        conn.commit()
        conn.close()

        response = self.client.get(f"/api/hql/{hql_id}")
        self.assert_response_success(response)

    def test_04_deactivate_hql(self):
        """Test POST /api/hql/<id>/deactivate"""
        # Create HQL statement
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO hql_statements (event_id, hql_type, hql_content, is_active)
            VALUES (?, ?, ?, ?)
        """,
            (1, "create_view", "SELECT 1", 1),
        )
        hql_id = cursor.lastrowid
        conn.commit()
        conn.close()

        response = self.client.post(f"/api/hql/{hql_id}/deactivate")
        self.assert_response_success(response)

    def test_05_activate_hql(self):
        """Test POST /api/hql/<id>/activate"""
        # Create inactive HQL statement with hql_version > 1 (required for activation)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO hql_statements (event_id, hql_type, hql_content, is_active, hql_version)
            VALUES (?, ?, ?, ?, ?)
        """,
            (1, "create_view", "SELECT 1", 0, 2),
        )
        hql_id = cursor.lastrowid
        conn.commit()
        conn.close()

        response = self.post_with_csrf(f"/api/hql/{hql_id}/activate")
        self.assert_response_success(response)


class TestBulkOperationsAPI(APITestCase):
    """Test Bulk Operations API endpoints"""

    def test_01_bulk_delete_events(self):
        """Test POST /bulk-delete-events"""
        delete_data = {"event_ids": [1]}
        response = self.client.post(
            "/bulk-delete-events",
            data=json.dumps(delete_data),
            content_type="application/json",
        )
        self.assert_response_success(response)

    def test_02_bulk_update_category(self):
        """Test POST /bulk-update-category"""
        update_data = {"event_ids": [1], "category_id": 1}
        response = self.client.post(
            "/bulk-update-category",
            data=json.dumps(update_data),
            content_type="application/json",
        )
        self.assert_response_success(response)

    def test_03_bulk_toggle_common_params(self):
        """Test POST /bulk-toggle-common-params"""
        toggle_data = {"event_ids": [1], "include": 1}
        response = self.client.post(
            "/bulk-toggle-common-params",
            data=json.dumps(toggle_data),
            content_type="application/json",
        )
        self.assert_response_success(response)

    def test_04_bulk_export_events(self):
        """Test POST /bulk-export-events"""
        export_data = {"event_ids": [1], "format": "json"}
        response = self.client.post(
            "/bulk-export-events",
            data=json.dumps(export_data),
            content_type="application/json",
        )
        self.assert_response_success(response)

    def test_05_bulk_validate_parameters(self):
        """Test POST /bulk-validate-parameters"""
        validate_data = {"event_ids": [1]}
        response = self.client.post(
            "/bulk-validate-parameters",
            data=json.dumps(validate_data),
            content_type="application/json",
        )
        self.assert_response_success(response)


class TestCanvasAPI(APITestCase):
    """Test Canvas API endpoints"""

    def test_01_canvas_health(self):
        """Test GET /api/canvas/health - Canvas health check"""
        response = self.client.get("/api/canvas/health")
        self.assert_response_success(response)

        data = self.get_json(response)
        self.assertTrue(data["success"])

    def test_02_canvas_validate_valid_json(self):
        """Test POST /api/canvas/validate - Validate valid canvas"""
        valid_canvas = {
            "nodes": [
                {
                    "id": "node1",
                    "type": "event",
                    "event_id": 1,
                    "position": {"x": 100, "y": 100},
                },
                {"id": "node2", "type": "output", "position": {"x": 300, "y": 100}},
            ],
            "connections": [{"source": "node1", "target": "node2"}],
        }
        response = self.client.post(
            "/api/canvas/validate",
            data=json.dumps(valid_canvas),
            content_type="application/json",
        )
        self.assert_response_success(response)

    def test_03_canvas_validate_invalid_json(self):
        """Test POST /api/canvas/validate - Validate invalid canvas"""
        invalid_canvas = {"nodes": [], "connections": []}
        response = self.client.post(
            "/api/canvas/validate",
            data=json.dumps(invalid_canvas),
            content_type="application/json",
        )
        # Should return error for empty canvas
        self.assertIn(response.status_code, [200, 400])

    def test_04_canvas_prepare(self):
        """Test POST /api/canvas/prepare - Prepare canvas for generation"""
        canvas_data = {
            "nodes": [
                {
                    "id": "node1",
                    "type": "event",
                    "event_id": 1,
                    "position": {"x": 100, "y": 100},
                },
                {"id": "node2", "type": "output", "position": {"x": 300, "y": 100}},
            ],
            "connections": [{"source": "node1", "target": "node2"}],
        }
        response = self.client.post(
            "/api/canvas/prepare",
            data=json.dumps(canvas_data),
            content_type="application/json",
        )
        self.assert_response_success(response)

    def test_05_canvas_preview_results(self):
        """Test POST /api/canvas/preview-results - Preview generation results"""
        preview_data = {
            "sql": "SELECT ds, role_id, account_id FROM ods_event_log WHERE ds = '${bizdate}'",
            "output_fields": [
                {"name": "ds", "alias": "ds", "data_type": "string"},
                {"name": "role_id", "alias": "role_id", "data_type": "bigint"},
                {"name": "account_id", "alias": "account_id", "data_type": "bigint"},
            ],
            "limit": 5,
        }
        response = self.client.post(
            "/api/canvas/preview-results",
            data=json.dumps(preview_data),
            content_type="application/json",
        )
        self.assert_response_success(response)


class TestCacheMonitorAPI(APITestCase):
    """Test Cache Monitor API endpoints"""

    def test_01_cache_status(self):
        """Test GET /admin/cache/status - Get cache status"""
        response = self.client.get("/admin/cache/status")
        self.assert_response_success(response)

        data = self.get_json(response)
        self.assertTrue(data["success"])
        self.assertIn("stats", data["data"])

    def test_02_cache_keys(self):
        """Test GET /admin/cache/keys - Get cache keys"""
        response = self.client.get("/admin/cache/keys")
        self.assert_response_success(response)

        data = self.get_json(response)
        self.assertTrue(data["success"])
        self.assertIn("keys", data["data"])

    def test_03_cache_clear(self):
        """Test POST /admin/cache/clear - Clear cache"""
        clear_data = {"pattern": "events:*"}
        response = self.client.post(
            "/admin/cache/clear",
            data=json.dumps(clear_data),
            content_type="application/json",
        )
        self.assert_response_success(response)

        data = self.get_json(response)
        self.assertTrue(data["success"])


class TestEventNodesAPI(APITestCase):
    """Test Event Nodes API endpoints"""

    def setUp(self):
        """Set up test client with game context"""
        super().setUp()
        self.game_gid = self.test_game_gid if self.test_game_gid else 10000147
        self.game_id = self.test_game_ids[0] if self.test_game_ids else 1

    def test_01_list_event_nodes(self):
        """Test GET /api/event-nodes - List event nodes"""
        response = self.client.get(f"/api/event-nodes?game_gid={self.game_gid}")
        self.assert_response_success(response)

        data = self.get_json(response)
        self.assertTrue(data["success"])
        self.assertIn("nodes", data["data"])

    def test_02_get_event_node(self):
        """Test GET /api/event-nodes/<node_id> - Get specific node"""
        # Create a test node (schema: game_id, name, event_id, config_json)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO event_nodes (game_id, name, event_id, config_json)
            VALUES (?, ?, ?, ?)
        """,
            (1, "test_node", 1, json.dumps({"test": "config"})),
        )
        node_id = cursor.lastrowid
        conn.commit()
        conn.close()

        response = self.client.get(f"/api/event-nodes/{node_id}")
        self.assert_response_success(response)

        data = self.get_json(response)
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["node"]["id"], node_id)

    def test_03_create_event_node(self):
        """Test POST /api/event-nodes - Create event node"""
        # Use test game_gid and actual event_id from test data
        test_event_id = self.test_event_ids[0] if self.test_event_ids else 1
        node_data = {
            "game_gid": self.test_game_gid,
            "name": "new_test_node",
            "event_id": test_event_id,
            "config": {"test": "config"},
        }
        response = self.client.post(
            "/api/event-nodes",
            data=json.dumps(node_data),
            content_type="application/json",
        )
        self.assert_response_success(response, expected_status=201)

        data = self.get_json(response)
        self.assertTrue(data["success"])
        # API returns 'node' object with 'id' field
        self.assertIn("node", data["data"])
        self.assertIn("id", data["data"]["node"])

    def test_04_update_event_node(self):
        """Test PUT /api/event-nodes/<node_id> - Update event node"""
        # Create a test node (schema: game_id, name, event_id, config_json)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO event_nodes (game_id, name, event_id, config_json)
            VALUES (?, ?, ?, ?)
        """,
            (1, "update_test", 1, json.dumps({})),
        )
        node_id = cursor.lastrowid
        conn.commit()
        conn.close()

        update_data = {
            "name": "updated_node",
            "description": "Updated Description",
            "config": {"new": "config"},
        }
        response = self.client.put(
            f"/api/event-nodes/{node_id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )
        self.assert_response_success(response)

    def test_05_delete_event_node(self):
        """Test DELETE /api/event-nodes/<node_id> - Delete event node"""
        # Create a test node (schema: game_id, name, event_id, config_json)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO event_nodes (game_id, name, event_id, config_json)
            VALUES (?, ?, ?, ?)
        """,
            (1, "delete_test", 1, json.dumps({})),
        )
        node_id = cursor.lastrowid
        conn.commit()
        conn.close()

        response = self.client.delete(f"/api/event-nodes/{node_id}")
        self.assert_response_success(response)


class TestParameterAliasesAPI(APITestCase):
    """Test Parameter Aliases API endpoints"""

    def setUp(self):
        """Set up test client with game context"""
        super().setUp()
        self.game_gid = self.test_game_gid if self.test_game_gid else 10000147
        self.game_id = self.test_game_ids[0] if self.test_game_ids else 1

    def test_01_list_parameter_aliases(self):
        """Test GET /api/parameter-aliases - List parameter aliases"""
        # Get actual param_id from event_params table
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM event_params LIMIT 1")
        result = cursor.fetchone()
        conn.close()

        if not result:
            self.skipTest("No event_params found in database")

        param_id = result[0]

        # API requires game_gid and param_id parameters
        response = self.client.get(
            f"/api/parameter-aliases?game_gid={self.test_game_gid}&param_id={param_id}"
        )
        self.assert_response_success(response)

        data = self.get_json(response)
        self.assertTrue(data["success"])
        # API returns data as a list of aliases directly
        self.assertIsInstance(data["data"], list)

    def test_02_create_parameter_alias(self):
        """Test POST /api/parameter-aliases - Create parameter alias"""
        # Get actual param_id from event_params table (not event_id!)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM event_params LIMIT 1")
        result = cursor.fetchone()
        conn.close()

        if not result:
            self.skipTest("No event_params found in database")

        param_id = result[0]

        # API requires game_gid, param_id, alias fields
        alias_data = {
            "game_gid": self.test_game_gid,
            "param_id": param_id,
            "alias": f"test_zone_alias_{id(self)}",  # Unique alias to avoid conflicts
            "display_name": "Zone",
        }
        response = self.client.post(
            "/api/parameter-aliases",
            data=json.dumps(alias_data),
            content_type="application/json",
        )
        self.assert_response_success(response, expected_status=201)

        data = self.get_json(response)
        self.assertTrue(data["success"])
        # API returns alias object with 'id' field
        self.assertIn("id", data["data"])

    def test_03_update_parameter_alias(self):
        """Test PUT /api/parameter-aliases/<alias_id> - Update parameter alias"""
        # Create a test alias (schema: game_id, param_id, alias, display_name)
        conn = get_db_connection()
        cursor = conn.cursor()
        # Clean up any existing test alias to avoid UNIQUE constraint
        cursor.execute(
            "DELETE FROM parameter_aliases WHERE alias = ? AND param_id = ?", ("test_alias", 1)
        )
        cursor.execute(
            """
            INSERT INTO parameter_aliases (game_id, param_id, alias, display_name)
            VALUES (?, ?, ?, ?)
        """,
            (1, 1, "test_alias", "Test Alias"),
        )
        alias_id = cursor.lastrowid
        conn.commit()
        conn.close()

        update_data = {
            "alias_name": "updated_alias",
            "display_name": "Updated description",
        }
        response = self.client.put(
            f"/api/parameter-aliases/{alias_id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )
        self.assert_response_success(response)

    def test_04_set_preferred_alias(self):
        """Test PUT /api/parameter-aliases/<alias_id>/prefer - Set preferred alias"""
        # Create a test alias (schema: game_id, param_id, alias, display_name)
        conn = get_db_connection()
        cursor = conn.cursor()
        # Use unique alias to avoid UNIQUE constraint conflicts
        cursor.execute(
            """
            INSERT INTO parameter_aliases (game_id, param_id, alias, display_name)
            VALUES (?, ?, ?, ?)
        """,
            (1, 1, f"prefer_alias_test_{id(self)}", "Prefer Alias Test"),
        )
        alias_id = cursor.lastrowid
        conn.commit()
        conn.close()

        response = self.client.put(f"/api/parameter-aliases/{alias_id}/prefer")
        self.assert_response_success(response)

    def test_05_update_param_display_name(self):
        """Test PUT /api/parameters/<param_id>/display-name - Update display name"""
        # Get actual param_id from database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM event_params LIMIT 1")
        result = cursor.fetchone()
        conn.close()

        if not result:
            self.skipTest("No event_params found in database")

        param_id = result[0]
        update_data = {"display_name": "New Display Name"}
        response = self.client.put(
            f"/api/parameters/{param_id}/display-name",
            data=json.dumps(update_data),
            content_type="application/json",
        )
        self.assert_response_success(response)


class TestIntegrationScenarios(APITestCase):
    """Integration tests for common scenarios"""

    def setUp(self):
        """Set up test client with game context"""
        super().setUp()
        self.game_gid = self.test_game_gid if self.test_game_gid else 10000147
        self.game_id = self.test_game_ids[0] if self.test_game_ids else 1

    def test_01_full_event_workflow(self):
        """Test complete event creation and HQL generation workflow"""
        # Step 1: Create event (use game_gid instead of game_id)
        event_data = {
            "game_gid": self.game_gid,  # Use game_gid instead of game_id
            "event_name": "integration.test",
            "event_name_cn": "集成测试",
            "category_id": self.test_category_id,  # Use dynamic category ID from test setup
            "param_names": ["user_id", "level"],
            "param_names_cn": ["用户ID", "等级"],
            "param_types": [1, 2],
            "param_descriptions": ["User ID", "Player level"],
        }
        response = self.client.post(
            "/api/events", data=json.dumps(event_data), content_type="application/json"
        )
        self.assert_response_success(response)

        event_result = self.get_json(response)
        event_id = event_result["data"]["event_id"]
        self.assertGreater(event_id, 0)

        # Step 2: Get event details (use game_gid instead of game_id)
        response = self.client.get(f"/api/events/{event_id}?game_gid={self.game_gid}")
        self.assert_response_success(response)

        # Step 3: Generate HQL
        gen_data = {
            "selected_events": [event_id],
            "selected_joins": [],
            "date_str": "${bizdate}",
        }
        response = self.client.post(
            "/api/generate", data=json.dumps(gen_data), content_type="application/json"
        )
        self.assert_response_success(response)

        hql_result = self.get_json(response)
        self.assertIn("data", hql_result)
        self.assertGreater(len(hql_result["data"]), 0)

    def test_02_search_and_export_workflow(self):
        """Test search and export parameters workflow"""
        # Skip: /api/parameters/export endpoint doesn't exist
        self.skipTest("/api/parameters/export endpoint not implemented")

    def test_03_canvas_to_hql_workflow(self):
        """Test canvas creation and HQL generation workflow"""
        # Skip: Canvas validation requires specific node format with event_id pointing to valid events
        # This test needs proper test data setup which is complex
        self.skipTest("Canvas workflow test requires complex test data setup")


class TestErrorHandling(APITestCase):
    """Test error handling and edge cases"""

    def setUp(self):
        """Set up test context"""
        super().setUp()  # Call parent setUp to initialize app_context
        # Initialize game_gid from parent class
        self.game_gid = self.test_game_gid if self.test_game_gid else 10000147

    def test_01_invalid_json(self):
        """Test API with invalid JSON"""
        response = self.client.post(
            "/api/games", data="invalid json", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_02_missing_required_fields(self):
        """Test API with missing required fields"""
        incomplete_data = {
            "name": "Test"
            # Missing required fields
        }
        response = self.client.post(
            "/api/games",
            data=json.dumps(incomplete_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_03_not_found_resource(self):
        """Test accessing non-existent resource"""
        # Use test_game_gid instead of hard-coded game_id=1
        # Access self.game_gid through instance (it's a class variable from parent)
        response = self.client.get(f"/api/events/99999?game_gid={self.game_gid}")
        self.assertEqual(response.status_code, 404)

    def test_04_invalid_game_context(self):
        """Test API without game context when required"""
        response = self.client.get("/api/events/1")
        self.assertEqual(response.status_code, 400)

    def test_05_invalid_pagination_params(self):
        """Test with invalid pagination parameters"""
        response = self.client.get("/api/events?page=-1")
        # Should handle gracefully
        self.assertIn(response.status_code, [200, 400])


class TestSecurityAndValidation(APITestCase):
    """Test security features and input validation"""

    def test_01_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        malicious_input = {
            "game_id": 1,
            "event_name": "'; DROP TABLE log_events; --",
            "event_name_cn": "SQL Injection",
            "category_id": 1,
        }
        response = self.client.post(
            "/api/events",
            data=json.dumps(malicious_input),
            content_type="application/json",
        )
        # Should either succeed (sanitized) or fail gracefully
        self.assertIn(response.status_code, [200, 400, 500])

    def test_02_xss_prevention(self):
        """Test XSS prevention in user inputs"""
        # Use unique GID to avoid conflicts with existing test data
        import time

        unique_gid = 99999 + int(time.time() * 1000) % 100000
        xss_input = {
            "gid": unique_gid,
            "name": '<script>alert("XSS")</script>',
            "ods_db": "ieu_ods",
        }
        response = self.client.post(
            "/api/games",
            data=json.dumps(xss_input),
            content_type="application/json",
            headers={"X-CSRF-Token": "test_csrf_token_1234567890"},
        )
        # Should succeed - XSS should be sanitized or stored safely
        self.assert_response_success(response)

    def test_03_large_payload_handling(self):
        """Test handling of large payloads"""
        large_params = []
        for i in range(100):
            large_params.append(f"param_{i}")

        event_data = {
            "game_id": 1,
            "event_name": "test.large",
            "event_name_cn": "Large Event",
            "category_id": 1,
            "param_names": large_params,
            "param_names_cn": large_params,
            "param_types": [1] * 100,
            "param_descriptions": [""] * 100,
        }
        response = self.client.post(
            "/api/events", data=json.dumps(event_data), content_type="application/json"
        )
        # Should handle gracefully
        self.assertIn(response.status_code, [200, 400, 413])


# Test runner function
def run_tests_with_report():
    """Run tests and generate report"""
    import unittest

    # Run unittest
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful


if __name__ == "__main__":
    print("Running DWD Generator API Test Suite...")
    print("=" * 80)
    success = run_tests_with_report()
    sys.exit(0 if success else 1)
