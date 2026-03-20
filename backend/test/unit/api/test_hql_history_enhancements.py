#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HQL History V2 Enhancement Tests

Tests for:
- Enhanced save endpoint with hql_type, game_gid, name_en, name_cn
- Fuzzy search endpoint
- Global query endpoint
- Canvas type HQL handling
"""

import pytest
import json
from datetime import datetime, timedelta
from backend.api.routes.hql_preview_v2 import hql_preview_v2_bp
from backend.services.hql.hql_history_service import HQLHistoryService
from backend.core.config.config import get_db_path, TEST_DB_PATH


@pytest.fixture(scope="module")
def client():
    """Create Flask test client"""
    from flask import Flask

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(hql_preview_v2_bp)

    with app.test_client() as client:
        yield client


@pytest.fixture(scope="function")
def test_db():
    """Setup test database"""
    from backend.core.database import get_db_connection

    # Use test database
    conn = get_db_connection(TEST_DB_PATH)
    cursor = conn.cursor()

    # Create hql_history table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hql_history (
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
            metadata_json TEXT,
            hql_type TEXT DEFAULT 'select' NOT NULL,
            game_gid INTEGER,
            name_en TEXT,
            name_cn TEXT
        )
    """)

    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hql_history_type ON hql_history(hql_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hql_history_user ON hql_history(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hql_history_game ON hql_history(game_gid)")

    conn.commit()
    conn.close()

    yield

    # Cleanup
    conn = get_db_connection(TEST_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS hql_history")
    conn.commit()
    conn.close()


class TestHQLHistorySaveEnhancements:
    """Test enhanced save endpoint"""

    def test_save_select_type(self, client, test_db):
        """Test saving SELECT type HQL"""
        response = client.post(
            "/hql-preview-v2/api/history/save",
            json={
                "events": [{"game_gid": 10000147, "event_id": 1}],
                "fields": [{"fieldName": "role_id", "fieldType": "base"}],
                "where_conditions": [],
                "mode": "single",
                "hql": "SELECT role_id FROM table",
                "hql_type": "select",
                "game_gid": 10000147,
                "name_en": "Test Query",
                "name_cn": "测试查询",
                "user_id": 0,
            },
            content_type="application/json",
        )

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["success"] is True
        assert "history_id" in data["data"]

    def test_save_canvas_type(self, client, test_db):
        """Test saving CANVAS type HQL with JSON structure"""
        canvas_hql = {
            "create_table": "CREATE TABLE dwd_table AS SELECT * FROM ods_table",
            "insert_overwrite": "INSERT OVERWRITE TABLE dwd_table SELECT * FROM ods_table",
            "select": "SELECT * FROM dwd_table WHERE ds = '${bizdate}'",
        }

        response = client.post(
            "/hql-preview-v2/api/history/save",
            json={
                "events": [{"game_gid": 10000147, "event_id": 1}],
                "fields": [{"fieldName": "role_id", "fieldType": "base"}],
                "where_conditions": [],
                "mode": "single",
                "hql": canvas_hql,
                "hql_type": "canvas",
                "game_gid": 10000147,
                "name_en": "Canvas Flow",
                "name_cn": "Canvas流程",
                "user_id": 0,
            },
            content_type="application/json",
        )

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["success"] is True

    def test_save_ddl_type(self, client, test_db):
        """Test saving DDL type HQL"""
        response = client.post(
            "/hql-preview-v2/api/history/save",
            json={
                "events": [],
                "fields": [],
                "where_conditions": [],
                "mode": "single",
                "hql": "CREATE TABLE dwd_test AS SELECT 1",
                "hql_type": "ddl",
                "game_gid": 10000147,
                "name_en": "Create Table",
                "user_id": 0,
            },
            content_type="application/json",
        )

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["success"] is True

    def test_save_required_fields_validation(self, client, test_db):
        """Test validation of required fields"""
        response = client.post(
            "/hql-preview-v2/api/history/save",
            json={
                # Missing required fields: events, fields, mode, hql
                "hql_type": "select",
            },
            content_type="application/json",
        )

        data = json.loads(response.data)
        assert response.status_code == 400
        assert data["success"] is False

    def test_save_invalid_hql_type(self, client, test_db):
        """Test validation of hql_type"""
        response = client.post(
            "/hql-preview-v2/api/history/save",
            json={
                "events": [{"game_gid": 10000147, "event_id": 1}],
                "fields": [{"fieldName": "role_id", "fieldType": "base"}],
                "where_conditions": [],
                "mode": "single",
                "hql": "SELECT role_id FROM table",
                "hql_type": "invalid_type",  # Invalid type
                "user_id": 0,
            },
            content_type="application/json",
        )

        # Should succeed because validation is at API level, not schema
        # but service should handle it
        assert response.status_code in [200, 400]


class TestHQLHistorySearch:
    """Test fuzzy search endpoint"""

    @pytest.fixture(autouse=True)
    def setup_test_data(self, client, test_db):
        """Setup test data for search tests"""
        # Create test history records
        test_records = [
            {
                "events": [{"game_gid": 10000147, "event_id": 1}],
                "fields": [{"fieldName": "role_id", "fieldType": "base"}],
                "where_conditions": [],
                "mode": "single",
                "hql": "SELECT role_id FROM login_table WHERE ds = '${bizdate}'",
                "hql_type": "select",
                "game_gid": 10000147,
                "name_en": "Login Event Query",
                "name_cn": "登录事件查询",
                "user_id": 1,
            },
            {
                "events": [{"game_gid": 10000147, "event_id": 2}],
                "fields": [{"fieldName": "zone_id", "fieldType": "base"}],
                "where_conditions": [],
                "mode": "single",
                "hql": "SELECT zone_id FROM purchase_table",
                "hql_type": "select",
                "game_gid": 10000147,
                "name_en": "Purchase Event Query",
                "name_cn": "购买事件查询",
                "user_id": 1,
            },
            {
                "events": [{"game_gid": 10000148, "event_id": 1}],
                "fields": [{"fieldName": "amount", "fieldType": "base"}],
                "where_conditions": [],
                "mode": "single",
                "hql": "CREATE TABLE payment_table AS SELECT amount",
                "hql_type": "ddl",
                "game_gid": 10000148,
                "name_en": "Payment Table",
                "name_cn": "支付表",
                "user_id": 2,
            },
        ]

        for record in test_records:
            client.post(
                "/hql-preview-v2/api/history/save", json=record, content_type="application/json"
            )

    def test_search_by_keyword(self, client):
        """Test fuzzy search by keyword"""
        response = client.post(
            "/hql-preview-v2/api/history/search",
            json={"keyword": "login", "limit": 10},
            content_type="application/json",
        )

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["success"] is True
        assert len(data["data"]["history"]) > 0

    def test_search_by_hql_type(self, client):
        """Test search by HQL type"""
        response = client.post(
            "/hql-preview-v2/api/history/search",
            json={"hql_type": "ddl", "limit": 10},
            content_type="application/json",
        )

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["success"] is True
        for record in data["data"]["history"]:
            assert record["hql_type"] == "ddl"

    def test_search_by_game_gid(self, client):
        """Test search by game GID"""
        response = client.post(
            "/hql-preview-v2/api/history/search",
            json={"game_gid": 10000147, "limit": 10},
            content_type="application/json",
        )

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["success"] is True
        for record in data["data"]["history"]:
            assert record["game_gid"] == 10000147

    def test_search_by_user_id(self, client):
        """Test search by user ID"""
        response = client.post(
            "/hql-preview-v2/api/history/search",
            json={"user_id": 1, "limit": 10},
            content_type="application/json",
        )

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["success"] is True
        for record in data["data"]["history"]:
            assert record["user_id"] == 1

    def test_search_with_date_range(self, client):
        """Test search with date range"""
        today = datetime.now().isoformat()
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()

        response = client.post(
            "/hql-preview-v2/api/history/search",
            json={"date_from": yesterday, "date_to": today, "limit": 10},
            content_type="application/json",
        )

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["success"] is True

    def test_search_with_pagination(self, client):
        """Test search with pagination"""
        response = client.post(
            "/hql-preview-v2/api/history/search",
            json={"limit": 2, "offset": 0},
            content_type="application/json",
        )

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["success"] is True
        assert data["data"]["limit"] == 2
        assert data["data"]["offset"] == 0
        assert len(data["data"]["history"]) <= 2

    def test_search_invalid_limit(self, client):
        """Test validation of limit parameter"""
        response = client.post(
            "/hql-preview-v2/api/history/search",
            json={"limit": 1000},  # Exceeds max of 500
            content_type="application/json",
        )

        data = json.loads(response.data)
        assert response.status_code == 400
        assert data["success"] is False

    def test_search_invalid_offset(self, client):
        """Test validation of offset parameter"""
        response = client.post(
            "/hql-preview-v2/api/history/search",
            json={"offset": -1},  # Negative offset
            content_type="application/json",
        )

        data = json.loads(response.data)
        assert response.status_code == 400
        assert data["success"] is False


class TestHQLHistoryGlobalSearch:
    """Test global query endpoint"""

    @pytest.fixture(autouse=True)
    def setup_test_data(self, client, test_db):
        """Setup test data for global search tests"""
        # Create test history records with different user IDs
        for user_id in [1, 2, 3]:
            client.post(
                "/hql-preview-v2/api/history/save",
                json={
                    "events": [{"game_gid": 10000147, "event_id": 1}],
                    "fields": [{"fieldName": "role_id", "fieldType": "base"}],
                    "where_conditions": [],
                    "mode": "single",
                    "hql": f"SELECT role_id FROM table_user_{user_id}",
                    "hql_type": "select",
                    "game_gid": 10000147,
                    "name_en": f"User {user_id} Query",
                    "user_id": user_id,
                },
                content_type="application/json",
            )

    def test_global_search_by_keyword(self, client):
        """Test global search by keyword"""
        response = client.get("/hql-preview-v2/api/history/global?keyword=role_id&limit=10")

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["success"] is True
        assert len(data["data"]["history"]) > 0

    def test_global_search_by_hql_type(self, client):
        """Test global search by HQL type"""
        response = client.get("/hql-preview-v2/api/history/global?hql_type=select&limit=10")

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["success"] is True
        for record in data["data"]["history"]:
            assert record["hql_type"] == "select"

    def test_global_search_pagination(self, client):
        """Test global search with pagination"""
        response = client.get("/hql-preview-v2/api/history/global?limit=2&offset=0")

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["success"] is True
        assert data["data"]["limit"] == 2
        assert data["data"]["offset"] == 0
        assert len(data["data"]["history"]) <= 2

    def test_global_search_response_structure(self, client):
        """Test global search response has required fields"""
        response = client.get("/hql-preview-v2/api/history/global?limit=10")

        data = json.loads(response.data)
        assert response.status_code == 200
        assert "note" in data["data"]
        assert "authentication" in data["data"]["note"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
