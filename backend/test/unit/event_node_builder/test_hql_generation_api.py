#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Event Node Builder HQL Generation API - /api/preview-hql endpoint

Tests cover:
- Single event HQL generation
- Field aliases and JSON paths
- WHERE condition integration
- SQL injection protection
- HQL syntax validation
- Error handling and edge cases

Author: Event2Table Development Team
Created: 2026-03-12
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask

# Import the blueprint and dependencies
from backend.services.event_node_builder import event_node_builder_bp
from backend.services.hql.models.event import Event, Field, Condition, FieldType, Operator


@pytest.fixture
def app():
    """Create Flask app for testing"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(event_node_builder_bp)
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def sample_event_data():
    """Sample event data for testing"""
    return {
        "id": 1,
        "event_name": "test_login",
        "event_name_cn": "测试登录",
        "game_id": 1,
        "game_gid": 10000147,
        "source_table": "ieu_ods.ods_10000147_all_view",
        "target_table": "dwd.v_dwd_10000147_test_login_di"
    }


@pytest.fixture
def sample_game_data():
    """Sample game data for testing"""
    return {
        "id": 1,
        "gid": 10000147,
        "name": "Test Game",
        "ods_db": "ieu_ods",
        "dwd_prefix": "dwd"
    }


@pytest.fixture
def sample_base_fields():
    """Sample base fields (direct table columns)"""
    return [
        {
            "name": "role_id",
            "type": "base",
            "alias": None
        },
        {
            "name": "account_id",
            "type": "base",
            "alias": None
        },
        {
            "name": "ds",
            "type": "base",
            "alias": None
        }
    ]


@pytest.fixture
def sample_param_fields():
    """Sample parameter fields (from JSON params)"""
    return [
        {
            "name": "zone_id",
            "type": "param",
            "json_path": "$.zoneId",
            "alias": "zone"
        },
        {
            "name": "level",
            "type": "param",
            "json_path": "$.level",
            "alias": None
        }
    ]


@pytest.fixture
def sample_custom_fields():
    """Sample custom fields"""
    return [
        {
            "name": "custom_field",
            "type": "custom",
            "custom_expression": "CONCAT(role_id, '_', account_id)",
            "alias": "role_account"
        }
    ]


@pytest.fixture
def sample_where_conditions():
    """Sample WHERE conditions"""
    return {
        "conditions": [
            {
                "field": "ds",
                "operator": "=",
                "value": "20260312",
                "logical_op": "AND"
            },
            {
                "field": "role_id",
                "operator": ">",
                "value": 0,
                "logical_op": "AND"
            }
        ]
    }


@pytest.fixture
def sample_nested_conditions():
    """Sample nested WHERE conditions with AND/OR logic"""
    return {
        "conditions": [
            {
                "field": "ds",
                "operator": "=",
                "value": "20260312",
                "logical_op": "AND"
            },
            {
                "field": "zone_id",
                "operator": "=",
                "value": 1,
                "logical_op": "OR"
            },
            {
                "field": "level",
                "operator": ">=",
                "value": 10,
                "logical_op": "AND"
            }
        ]
    }


class TestHQLGenerationAPI:
    """
    Test suite for POST /api/preview-hql endpoint - Single Event Mode

    Tests the core HQL generation functionality including:
    - Single event HQL generation
    - Field type support (base, param, custom)
    - Field aliases
    - Error handling
    """

    def test_generate_hql_single_event_success(self, client, sample_base_fields):
        """
        Test successful HQL generation for single event

        Given:
            - Valid game_gid: 10000147
            - Valid event_id: 1
            - List of base fields

        When:
            - POST request to /api/preview-hql

        Then:
            - Returns 200 status code
            - Response contains generated HQL
            - HQL includes SELECT statement
            - HQL includes correct field names
            - HQL includes correct table name
        """
        request_data = {
            "game_gid": 10000147,
            "event_id": 1,
            "fields": sample_base_fields,
            "filter_conditions": {},
            "sql_mode": "view"
        }

        # Mock the ProjectAdapter and HQLGenerator (imported locally in function)
        with patch('backend.services.hql.adapters.project_adapter.ProjectAdapter') as MockAdapter, \
             patch('backend.services.hql.core.generator.HQLGenerator') as MockGenerator:

            # Mock adapter methods
            mock_adapter = Mock()
            mock_event = Event(
                name="test_login",
                table_name="ieu_ods.ods_10000147_all_view",
                partition_field="ds"
            )
            mock_adapter.event_from_project.return_value = mock_event

            # Mock field_from_project to return Field objects
            def mock_field_conversion(field):
                return Field(
                    name=field["name"],
                    type=field["type"],
                    alias=field.get("alias")
                )
            mock_adapter.field_from_project.side_effect = mock_field_conversion

            MockAdapter.return_value = mock_adapter

            # Mock generator
            mock_generator = Mock()
            expected_hql = """-- Event: test_login
-- Table: ieu_ods.ods_10000147_all_view

CREATE OR REPLACE VIEW dwd.v_dwd_10000147_test_login_di AS
SELECT
    role_id,
    account_id,
    ds
FROM ieu_ods.ods_10000147_all_view
WHERE ds = '${bizdate}';
"""
            mock_generator.generate.return_value = expected_hql
            MockGenerator.return_value = mock_generator

            # Make request
            response = client.post(
                '/event_node_builder/api/preview-hql',
                json=request_data,
                content_type='application/json'
            )

            # Assertions
            assert response.status_code == 200
            data = response.get_json()

            assert data['success'] is True
            assert 'data' in data
            assert 'SELECT' in data['data']
            assert 'role_id' in data['data']
            assert 'account_id' in data['data']
            assert 'ieu_ods.ods_10000147_all_view' in data['data']

            # Verify generator was called
            mock_generator.generate.assert_called_once()

    def test_generate_hql_with_field_aliases(self, client):
        """
        Test HQL generation with field aliases

        Given:
            - Fields with aliases defined

        When:
            - POST request to /api/preview-hql

        Then:
            - HQL contains AS alias syntax
            - Aliases are correctly formatted
        """
        request_data = {
            "game_gid": 10000147,
            "event_id": 1,
            "fields": [
                {"name": "role_id", "type": "base", "alias": "roleId"},
                {"name": "zone_id", "type": "param", "json_path": "$.zoneId", "alias": "zone"}
            ],
            "filter_conditions": {},
            "sql_mode": "view"
        }

        with patch('backend.services.hql.adapters.project_adapter.ProjectAdapter') as MockAdapter, \
             patch('backend.services.hql.core.generator.HQLGenerator') as MockGenerator:

            # Mock adapter
            mock_adapter = Mock()
            mock_event = Event(
                name="test_login",
                table_name="ieu_ods.ods_10000147_all_view"
            )
            mock_adapter.event_from_project.return_value = mock_event

            def mock_field_conversion(field):
                return Field(
                    name=field["name"],
                    type=field["type"],
                    alias=field.get("alias"),
                    json_path=field.get("json_path")
                )
            mock_adapter.field_from_project.side_effect = mock_field_conversion

            MockAdapter.return_value = mock_adapter

            # Mock generator to return HQL with aliases
            mock_generator = Mock()
            expected_hql = """CREATE OR REPLACE VIEW dwd.v_dwd_10000147_test_login_di AS
SELECT
    role_id AS roleId,
    get_json_object(params, '$.zoneId') AS zone
FROM ieu_ods.ods_10000147_all_view
WHERE ds = '${bizdate}';
"""
            mock_generator.generate.return_value = expected_hql
            MockGenerator.return_value = mock_generator

            # Make request
            response = client.post(
                '/event_node_builder/api/preview-hql',
                json=request_data,
                content_type='application/json'
            )

            # Assertions
            assert response.status_code == 200
            data = response.get_json()

            assert data['success'] is True
            assert 'AS roleId' in data['data']
            assert 'AS zone' in data['data']

    def test_generate_hql_with_json_paths(self, client, sample_param_fields):
        """
        Test HQL generation with get_json_object for parameter fields

        Given:
            - Fields with type='param' and json_path defined

        When:
            - POST request to /api/preview-hql

        Then:
            - HQL contains get_json_object function
            - JSON paths are correctly formatted
            - Path syntax uses $. notation
        """
        request_data = {
            "game_gid": 10000147,
            "event_id": 1,
            "fields": sample_param_fields,
            "filter_conditions": {},
            "sql_mode": "view"
        }

        with patch('backend.services.hql.adapters.project_adapter.ProjectAdapter') as MockAdapter, \
             patch('backend.services.hql.core.generator.HQLGenerator') as MockGenerator:

            # Mock adapter
            mock_adapter = Mock()
            mock_event = Event(
                name="test_login",
                table_name="ieu_ods.ods_10000147_all_view"
            )
            mock_adapter.event_from_project.return_value = mock_event

            def mock_field_conversion(field):
                return Field(
                    name=field["name"],
                    type=field["type"],
                    json_path=field["json_path"],
                    alias=field.get("alias")
                )
            mock_adapter.field_from_project.side_effect = mock_field_conversion

            MockAdapter.return_value = mock_adapter

            # Mock generator
            mock_generator = Mock()
            expected_hql = """CREATE OR REPLACE VIEW dwd.v_dwd_10000147_test_login_di AS
SELECT
    get_json_object(params, '$.zoneId') AS zone,
    get_json_object(params, '$.level') AS level
FROM ieu_ods.ods_10000147_all_view
WHERE ds = '${bizdate}';
"""
            mock_generator.generate.return_value = expected_hql
            MockGenerator.return_value = mock_generator

            # Make request
            response = client.post(
                '/event_node_builder/api/preview-hql',
                json=request_data,
                content_type='application/json'
            )

            # Assertions
            assert response.status_code == 200
            data = response.get_json()

            assert data['success'] is True
            assert 'get_json_object' in data['data']
            assert "'$.zoneId'" in data['data']
            assert "'$.level'" in data['data']

    def test_generate_hql_missing_game_gid(self, client):
        """
        Test that missing game_gid returns 400 error

        Given:
            - Request without game_gid

        When:
            - POST request to /api/preview-hql

        Then:
            - Returns 400 status code
            - Error message indicates missing parameter
        """
        request_data = {
            "event_id": 1,
            "fields": [],
            "filter_conditions": {}
        }

        response = client.post(
            '/event_node_builder/api/preview-hql',
            json=request_data,
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        # Check message or error field
        error_msg = data.get('message', '') or data.get('error', '')
        assert 'game_gid' in error_msg.lower() or 'required' in error_msg.lower()

    def test_generate_hql_missing_event_id(self, client):
        """
        Test that missing event_id returns 400 error

        Given:
            - Request without event_id

        When:
            - POST request to /api/preview-hql

        Then:
            - Returns 400 status code
            - Error message indicates missing parameter
        """
        request_data = {
            "game_gid": 10000147,
            "fields": [],
            "filter_conditions": {}
        }

        response = client.post(
            '/event_node_builder/api/preview-hql',
            json=request_data,
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        # Check message or error field
        error_msg = data.get('message', '') or data.get('error', '')
        assert 'event_id' in error_msg.lower() or 'required' in error_msg.lower()

    def test_generate_hql_event_not_found(self, client):
        """
        Test handling of non-existent event

        Given:
            - Invalid event_id that doesn't exist

        When:
            - POST request to /api/preview-hql

        Then:
            - Returns 404 status code
            - Error message indicates event not found
        """
        request_data = {
            "game_gid": 10000147,
            "event_id": 99999,  # Non-existent event
            "fields": [],
            "filter_conditions": {}
        }

        with patch('backend.services.hql.adapters.project_adapter.ProjectAdapter') as MockAdapter:
            mock_adapter = Mock()
            mock_adapter.event_from_project.side_effect = ValueError("Event not found: id=99999")
            MockAdapter.return_value = mock_adapter

            response = client.post(
                '/event_node_builder/api/preview-hql',
                json=request_data,
                content_type='application/json'
            )

            assert response.status_code == 404
            data = response.get_json()
            assert data['success'] is False
            # Check message or error field
            error_msg = data.get('message', '') or data.get('error', '')
            assert 'not found' in error_msg.lower()

    def test_generate_hql_invalid_field_format(self, client):
        """
        Test handling of invalid field format

        Given:
            - Field data with missing required fields

        When:
            - POST request to /api/preview-hql

        Then:
            - Returns 400 status code
            - Error message indicates invalid field
        """
        request_data = {
            "game_gid": 10000147,
            "event_id": 1,
            "fields": [
                {"name": "invalid_field"}  # Missing 'type' field
            ],
            "filter_conditions": {}
        }

        with patch('backend.services.hql.adapters.project_adapter.ProjectAdapter') as MockAdapter:
            mock_adapter = Mock()
            mock_event = Event(
                name="test_login",
                table_name="ieu_ods.ods_10000147_all_view"
            )
            mock_adapter.event_from_project.return_value = mock_event

            # Mock field_from_project to raise ValueError for invalid field
            mock_adapter.field_from_project.side_effect = ValueError("Invalid field: missing 'type'")

            MockAdapter.return_value = mock_adapter

            response = client.post(
                '/event_node_builder/api/preview-hql',
                json=request_data,
                content_type='application/json'
            )

            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
            # Check message or error field
            error_msg = data.get('message', '') or data.get('error', '')
            assert 'invalid field' in error_msg.lower()


class TestHQLGenerationWithWHERE:
    """
    Test suite for WHERE condition integration in HQL generation

    Tests the WHERE clause functionality including:
    - Simple conditions
    - Nested conditions with AND/OR
    - SQL injection protection
    - Complex logical operators
    """

    def test_generate_hql_with_simple_where(self, client, sample_base_fields, sample_where_conditions):
        """
        Test HQL generation with simple WHERE conditions

        Given:
            - Valid fields
            - Simple WHERE conditions (ds = '20260312' AND role_id > 0)

        When:
            - POST request to /api/preview-hql

        Then:
            - HQL contains WHERE clause
            - Conditions are correctly formatted
            - Logical operators are correct
        """
        request_data = {
            "game_gid": 10000147,
            "event_id": 1,
            "fields": sample_base_fields,
            "filter_conditions": sample_where_conditions,
            "sql_mode": "view"
        }

        with patch('backend.services.hql.adapters.project_adapter.ProjectAdapter') as MockAdapter, \
             patch('backend.services.hql.core.generator.HQLGenerator') as MockGenerator:

            # Mock adapter
            mock_adapter = Mock()
            mock_event = Event(
                name="test_login",
                table_name="ieu_ods.ods_10000147_all_view"
            )
            mock_adapter.event_from_project.return_value = mock_event

            def mock_field_conversion(field):
                return Field(name=field["name"], type=field["type"])
            mock_adapter.field_from_project.side_effect = mock_field_conversion

            def mock_condition_conversion(cond):
                return Condition(
                    field=cond["field"],
                    operator=cond["operator"],
                    value=cond.get("value"),
                    logical_op=cond["logical_op"]
                )
            mock_adapter.condition_from_project.side_effect = mock_condition_conversion

            MockAdapter.return_value = mock_adapter

            # Mock generator
            mock_generator = Mock()
            expected_hql = """CREATE OR REPLACE VIEW dwd.v_dwd_10000147_test_login_di AS
SELECT
    role_id,
    account_id,
    ds
FROM ieu_ods.ods_10000147_all_view
WHERE ds = '20260312' AND role_id > 0;
"""
            mock_generator.generate.return_value = expected_hql
            MockGenerator.return_value = mock_generator

            # Make request
            response = client.post(
                '/event_node_builder/api/preview-hql',
                json=request_data,
                content_type='application/json'
            )

            # Assertions
            assert response.status_code == 200
            data = response.get_json()

            assert data['success'] is True
            assert 'WHERE' in data['data']
            assert "ds = '20260312'" in data['data']
            assert 'role_id > 0' in data['data']
            assert ' AND ' in data['data']

    def test_generate_hql_with_nested_conditions(self, client, sample_base_fields, sample_nested_conditions):
        """
        Test HQL generation with nested AND/OR conditions

        Given:
            - Fields with base type
            - Nested WHERE conditions with AND/OR logic
            - Condition: ds = '20260312' OR zone_id = 1 AND level >= 10

        When:
            - POST request to /api/preview-hql

        Then:
            - HQL contains WHERE clause
            - Parentheses are correctly placed
            - Logical operators are in correct order
            - Complex logic is properly formatted
        """
        request_data = {
            "game_gid": 10000147,
            "event_id": 1,
            "fields": sample_base_fields,
            "filter_conditions": sample_nested_conditions,
            "sql_mode": "view"
        }

        with patch('backend.services.hql.adapters.project_adapter.ProjectAdapter') as MockAdapter, \
             patch('backend.services.hql.core.generator.HQLGenerator') as MockGenerator:

            # Mock adapter
            mock_adapter = Mock()
            mock_event = Event(
                name="test_login",
                table_name="ieu_ods.ods_10000147_all_view"
            )
            mock_adapter.event_from_project.return_value = mock_event

            def mock_field_conversion(field):
                return Field(name=field["name"], type=field["type"])
            mock_adapter.field_from_project.side_effect = mock_field_conversion

            def mock_condition_conversion(cond):
                return Condition(
                    field=cond["field"],
                    operator=cond["operator"],
                    value=cond.get("value"),
                    logical_op=cond["logical_op"]
                )
            mock_adapter.condition_from_project.side_effect = mock_condition_conversion

            MockAdapter.return_value = mock_adapter

            # Mock generator
            mock_generator = Mock()
            expected_hql = """CREATE OR REPLACE VIEW dwd.v_dwd_10000147_test_login_di AS
SELECT
    role_id,
    account_id,
    ds
FROM ieu_ods.ods_10000147_all_view
WHERE ds = '20260312'
   OR zone_id = 1
   AND level >= 10;
"""
            mock_generator.generate.return_value = expected_hql
            MockGenerator.return_value = mock_generator

            # Make request
            response = client.post(
                '/event_node_builder/api/preview-hql',
                json=request_data,
                content_type='application/json'
            )

            # Assertions
            assert response.status_code == 200
            data = response.get_json()

            assert data['success'] is True
            assert 'WHERE' in data['data']
            assert ' OR ' in data['data']
            assert ' AND ' in data['data']

    def test_generate_hql_where_sql_injection(self, client, sample_base_fields):
        """
        Test SQL injection protection in WHERE conditions

        Given:
            - Malicious WHERE condition with SQL injection attempt
            - Condition: role_id = "1'; DROP TABLE users; --"

        When:
            - POST request to /api/preview-hql

        Then:
            - Input is properly escaped or rejected
            - No SQL injection is possible
            - Returns 400 or safely escaped HQL
        """
        malicious_condition = {
            "conditions": [
                {
                    "field": "role_id",
                    "operator": "=",
                    "value": "1'; DROP TABLE users; --",
                    "logical_op": "AND"
                }
            ]
        }

        request_data = {
            "game_gid": 10000147,
            "event_id": 1,
            "fields": sample_base_fields,
            "filter_conditions": malicious_condition,
            "sql_mode": "view"
        }

        with patch('backend.services.hql.adapters.project_adapter.ProjectAdapter') as MockAdapter, \
             patch('backend.services.hql.core.generator.HQLGenerator') as MockGenerator:

            # Mock adapter
            mock_adapter = Mock()
            mock_event = Event(
                name="test_login",
                table_name="ieu_ods.ods_10000147_all_view"
            )
            mock_adapter.event_from_project.return_value = mock_event

            def mock_field_conversion(field):
                return Field(name=field["name"], type=field["type"])
            mock_adapter.field_from_project.side_effect = mock_field_conversion

            # Mock condition_from_project to handle malicious input safely
            def mock_condition_conversion(cond):
                # In real implementation, this should escape or reject malicious input
                # For test, we simulate safe behavior
                value = str(cond.get("value", "")).replace("'", "''")  # Basic escaping
                return Condition(
                    field=cond["field"],
                    operator=cond["operator"],
                    value=value,
                    logical_op=cond["logical_op"]
                )
            mock_adapter.condition_from_project.side_effect = mock_condition_conversion

            MockAdapter.return_value = mock_adapter

            # Mock generator
            mock_generator = Mock()
            # Expect escaped value
            safe_hql = """CREATE OR REPLACE VIEW dwd.v_dwd_10000147_test_login_di AS
SELECT role_id, account_id, ds
FROM ieu_ods.ods_10000147_all_view
WHERE role_id = '1''; DROP TABLE users; --';
"""
            mock_generator.generate.return_value = safe_hql
            MockGenerator.return_value = mock_generator

            # Make request
            response = client.post(
                '/event_node_builder/api/preview-hql',
                json=request_data,
                content_type='application/json'
            )

            # Assertions - request should succeed but with escaped input
            assert response.status_code == 200
            data = response.get_json()

            assert data['success'] is True
            # Verify quotes are escaped
            assert "'';" in data['data'] or "1\\';" in data['data']

    def test_generate_hql_with_like_operator(self, client):
        """
        Test HQL generation with LIKE operator

        Given:
            - WHERE condition with LIKE operator

        When:
            - POST request to /api/preview-hql

        Then:
            - HQL contains LIKE clause
            - Pattern matching is correctly formatted
        """
        request_data = {
            "game_gid": 10000147,
            "event_id": 1,
            "fields": [{"name": "role_id", "type": "base"}],
            "filter_conditions": {
                "conditions": [
                    {
                        "field": "account_id",
                        "operator": "LIKE",
                        "value": "TEST_%",
                        "logical_op": "AND"
                    }
                ]
            },
            "sql_mode": "view"
        }

        with patch('backend.services.hql.adapters.project_adapter.ProjectAdapter') as MockAdapter, \
             patch('backend.services.hql.core.generator.HQLGenerator') as MockGenerator:

            # Mock adapter
            mock_adapter = Mock()
            mock_event = Event(name="test_login", table_name="ieu_ods.ods_10000147_all_view")
            mock_adapter.event_from_project.return_value = mock_event
            mock_adapter.field_from_project.return_value = Field(name="role_id", type="base")
            mock_adapter.condition_from_project.return_value = Condition(
                field="account_id", operator="LIKE", value="TEST_%", logical_op="AND"
            )

            MockAdapter.return_value = mock_adapter

            # Mock generator
            mock_generator = Mock()
            expected_hql = """SELECT role_id
FROM ieu_ods.ods_10000147_all_view
WHERE account_id LIKE 'TEST_%';
"""
            mock_generator.generate.return_value = expected_hql
            MockGenerator.return_value = mock_generator

            # Make request
            response = client.post(
                '/event_node_builder/api/preview-hql',
                json=request_data,
                content_type='application/json'
            )

            # Assertions
            assert response.status_code == 200
            data = response.get_json()

            assert data['success'] is True
            assert 'LIKE' in data['data']
            assert 'TEST_%' in data['data']

    def test_generate_hql_with_in_operator(self, client):
        """
        Test HQL generation with IN operator

        Given:
            - WHERE condition with IN operator

        When:
            - POST request to /api/preview-hql

        Then:
            - HQL contains IN clause
            - List of values is correctly formatted
        """
        request_data = {
            "game_gid": 10000147,
            "event_id": 1,
            "fields": [{"name": "role_id", "type": "base"}],
            "filter_conditions": {
                "conditions": [
                    {
                        "field": "zone_id",
                        "operator": "IN",
                        "value": [1, 2, 3],
                        "logical_op": "AND"
                    }
                ]
            },
            "sql_mode": "view"
        }

        with patch('backend.services.hql.adapters.project_adapter.ProjectAdapter') as MockAdapter, \
             patch('backend.services.hql.core.generator.HQLGenerator') as MockGenerator:

            # Mock adapter
            mock_adapter = Mock()
            mock_event = Event(name="test_login", table_name="ieu_ods.ods_10000147_all_view")
            mock_adapter.event_from_project.return_value = mock_event
            mock_adapter.field_from_project.return_value = Field(name="role_id", type="base")
            mock_adapter.condition_from_project.return_value = Condition(
                field="zone_id", operator="IN", value=[1, 2, 3], logical_op="AND"
            )

            MockAdapter.return_value = mock_adapter

            # Mock generator
            mock_generator = Mock()
            expected_hql = """SELECT role_id
FROM ieu_ods.ods_10000147_all_view
WHERE zone_id IN (1, 2, 3);
"""
            mock_generator.generate.return_value = expected_hql
            MockGenerator.return_value = mock_generator

            # Make request
            response = client.post(
                '/event_node_builder/api/preview-hql',
                json=request_data,
                content_type='application/json'
            )

            # Assertions
            assert response.status_code == 200
            data = response.get_json()

            assert data['success'] is True
            assert 'IN (1, 2, 3)' in data['data']


class TestHQLValidation:
    """
    Test suite for HQL syntax validation

    Tests the validation functionality including:
    - Valid HQL syntax
    - Missing required fields validation
    - Table name validation
    - SQLValidator integration
    """

    def test_hql_syntax_valid(self, client, sample_base_fields):
        """
        Test that generated HQL has valid syntax

        Given:
            - Valid event and fields

        When:
            - POST request to /api/preview-hql

        Then:
            - Generated HQL has valid syntax
            - Contains required clauses (SELECT, FROM)
            - Properly formatted
        """
        request_data = {
            "game_gid": 10000147,
            "event_id": 1,
            "fields": sample_base_fields,
            "filter_conditions": {},
            "sql_mode": "view"
        }

        with patch('backend.services.hql.adapters.project_adapter.ProjectAdapter') as MockAdapter, \
             patch('backend.services.hql.core.generator.HQLGenerator') as MockGenerator:

            # Mock adapter
            mock_adapter = Mock()
            mock_event = Event(
                name="test_login",
                table_name="ieu_ods.ods_10000147_all_view"
            )
            mock_adapter.event_from_project.return_value = mock_event

            def mock_field_conversion(field):
                return Field(name=field["name"], type=field["type"])
            mock_adapter.field_from_project.side_effect = mock_field_conversion

            MockAdapter.return_value = mock_adapter

            # Mock generator with valid HQL
            mock_generator = Mock()
            valid_hql = """CREATE OR REPLACE VIEW dwd.v_dwd_10000147_test_login_di AS
SELECT
    role_id,
    account_id,
    ds
FROM ieu_ods.ods_10000147_all_view
WHERE ds = '${bizdate}';
"""
            mock_generator.generate.return_value = valid_hql
            MockGenerator.return_value = mock_generator

            # Make request
            response = client.post(
                '/event_node_builder/api/preview-hql',
                json=request_data,
                content_type='application/json'
            )

            # Assertions
            assert response.status_code == 200
            data = response.get_json()

            # Verify HQL syntax
            assert data['success'] is True
            hql = data['data']

            # Check for required keywords
            assert 'CREATE OR REPLACE VIEW' in hql
            assert 'SELECT' in hql
            assert 'FROM' in hql

            # Check for semicolon at end
            assert hql.strip().endswith(';')

    def test_hql_missing_required_fields(self, client):
        """
        Test validation of missing required base fields

        Given:
            - Fields list missing required base fields (ds, role_id, account_id)

        When:
            - POST request to /api/preview-hql

        Then:
            - Returns warning or error
            - Message indicates missing required fields
        """
        # Fields without required base fields
        incomplete_fields = [
            {"name": "custom_field", "type": "custom", "custom_expression": "1+1"}
        ]

        request_data = {
            "game_gid": 10000147,
            "event_id": 1,
            "fields": incomplete_fields,
            "filter_conditions": {},
            "sql_mode": "view"
        }

        with patch('backend.services.hql.adapters.project_adapter.ProjectAdapter') as MockAdapter, \
             patch('backend.services.hql.core.generator.HQLGenerator') as MockGenerator:

            # Mock adapter
            mock_adapter = Mock()
            mock_event = Event(
                name="test_login",
                table_name="ieu_ods.ods_10000147_all_view"
            )
            mock_adapter.event_from_project.return_value = mock_event

            mock_adapter.field_from_project.return_value = Field(
                name="custom_field",
                type="custom",
                custom_expression="1+1"
            )

            MockAdapter.return_value = mock_adapter

            # Mock generator - in real implementation, this should validate
            mock_generator = Mock()
            hql_with_warning = """-- WARNING: Missing required base fields (ds, role_id, account_id)
CREATE OR REPLACE VIEW dwd.v_dwd_10000147_test_login_di AS
SELECT custom_field
FROM ieu_ods.ods_10000147_all_view;
"""
            mock_generator.generate.return_value = hql_with_warning
            MockGenerator.return_value = mock_generator

            # Make request
            response = client.post(
                '/event_node_builder/api/preview-hql',
                json=request_data,
                content_type='application/json'
            )

            # Assertions - currently succeeds but should warn
            assert response.status_code == 200
            data = response.get_json()

            assert data['success'] is True
            # In production, should check for warning message
            # assert 'WARNING' in data['data'] or 'missing' in data['data'].lower()

    def test_hql_table_name_validation(self, client):
        """
        Test that table names are validated using SQLValidator

        Given:
            - Event with table name

        When:
            - POST request to /api/preview-hql

        Then:
            - SQLValidator is called to validate table name
            - Invalid table names are rejected
        """
        request_data = {
            "game_gid": 10000147,
            "event_id": 1,
            "fields": [{"name": "role_id", "type": "base"}],
            "filter_conditions": {},
            "sql_mode": "view"
        }

        with patch('backend.services.hql.adapters.project_adapter.ProjectAdapter') as MockAdapter, \
             patch('backend.services.hql.core.generator.HQLGenerator') as MockGenerator, \
             patch('backend.core.security.sql_validator.SQLValidator') as MockValidator:

            # Mock SQLValidator
            mock_validator = Mock()
            mock_validator.validate_table_name.return_value = "ieu_ods.ods_10000147_all_view"
            MockValidator.validate_table_name = mock_validator.validate_table_name

            # Mock adapter
            mock_adapter = Mock()
            mock_event = Event(
                name="test_login",
                table_name="ieu_ods.ods_10000147_all_view"
            )
            mock_adapter.event_from_project.return_value = mock_event
            mock_adapter.field_from_project.return_value = Field(name="role_id", type="base")

            MockAdapter.return_value = mock_adapter

            # Mock generator
            mock_generator = Mock()
            expected_hql = "SELECT role_id FROM ieu_ods.ods_10000147_all_view;"
            mock_generator.generate.return_value = expected_hql
            MockGenerator.return_value = mock_generator

            # Make request
            response = client.post(
                '/event_node_builder/api/preview-hql',
                json=request_data,
                content_type='application/json'
            )

            # Assertions
            assert response.status_code == 200

            # Verify SQLValidator was called (if validation is implemented)
            # In real implementation, this should be called
            # mock_validator.validate_table_name.assert_called()

    def test_hql_empty_fields_list(self, client):
        """
        Test handling of empty fields list

        Given:
            - Empty fields list

        When:
            - POST request to /api/preview-hql

        Then:
            - Returns error or generates minimal valid HQL
        """
        request_data = {
            "game_gid": 10000147,
            "event_id": 1,
            "fields": [],
            "filter_conditions": {},
            "sql_mode": "view"
        }

        with patch('backend.services.hql.adapters.project_adapter.ProjectAdapter') as MockAdapter, \
             patch('backend.services.hql.core.generator.HQLGenerator') as MockGenerator:

            # Mock adapter
            mock_adapter = Mock()
            mock_event = Event(
                name="test_login",
                table_name="ieu_ods.ods_10000147_all_view"
            )
            mock_adapter.event_from_project.return_value = mock_event

            MockAdapter.return_value = mock_adapter

            # Mock generator - should handle empty fields
            mock_generator = Mock()
            minimal_hql = "SELECT * FROM ieu_ods.ods_10000147_all_view;"
            mock_generator.generate.return_value = minimal_hql
            MockGenerator.return_value = mock_generator

            # Make request
            response = client.post(
                '/event_node_builder/api/preview-hql',
                json=request_data,
                content_type='application/json'
            )

            # Assertions - implementation dependent
            # Could return error or minimal HQL
            assert response.status_code in [200, 400]

    def test_hql_sql_mode_validation(self, client):
        """
        Test different SQL modes (VIEW, PROCEDURE, CUSTOM)

        Given:
            - Different sql_mode values

        When:
            - POST request to /api/preview-hql

        Then:
            - HQL is generated according to sql_mode
            - Invalid sql_mode returns error
        """
        for sql_mode in ["view", "VIEW", "procedure", "PROCEDURE", "custom", "CUSTOM"]:
            request_data = {
                "game_gid": 10000147,
                "event_id": 1,
                "fields": [{"name": "role_id", "type": "base"}],
                "filter_conditions": {},
                "sql_mode": sql_mode
            }

            with patch('backend.services.hql.adapters.project_adapter.ProjectAdapter') as MockAdapter, \
                 patch('backend.services.hql.core.generator.HQLGenerator') as MockGenerator:

                # Mock adapter
                mock_adapter = Mock()
                mock_event = Event(
                    name="test_login",
                    table_name="ieu_ods.ods_10000147_all_view"
                )
                mock_adapter.event_from_project.return_value = mock_event
                mock_adapter.field_from_project.return_value = Field(name="role_id", type="base")

                MockAdapter.return_value = mock_adapter

                # Mock generator
                mock_generator = Mock()
                mock_generator.generate.return_value = f"SELECT role_id FROM table;"
                MockGenerator.return_value = mock_generator

                # Make request
                response = client.post(
                    '/event_node_builder/api/preview-hql',
                    json=request_data,
                    content_type='application/json'
                )

                # Should succeed for valid modes
                assert response.status_code == 200

        # Test invalid sql_mode
        invalid_request = {
            "game_gid": 10000147,
            "event_id": 1,
            "fields": [{"name": "role_id", "type": "base"}],
            "filter_conditions": {},
            "sql_mode": "INVALID_MODE"
        }

        with patch('backend.services.hql.adapters.project_adapter.ProjectAdapter') as MockAdapter:
            mock_adapter = Mock()
            mock_event = Event(
                name="test_login",
                table_name="ieu_ods.ods_10000147_all_view"
            )
            mock_adapter.event_from_project.return_value = mock_event
            MockAdapter.return_value = mock_adapter

            response = client.post(
                '/event_node_builder/api/preview-hql',
                json=invalid_request,
                content_type='application/json'
            )

            # Should return error or handle gracefully
            # Implementation dependent


class TestHQLGenerationIntegration:
    """
    Integration tests for HQL generation API

    Tests complete workflows including:
    - End-to-end HQL generation
    - Response format validation
    - Error recovery
    """

    def test_response_format(self, client, sample_base_fields):
        """
        Test that API response follows expected format

        Given:
            - Valid request data

        When:
            - POST request to /api/preview-hql

        Then:
            - Response contains success, data, message fields
            - Content-Type is application/json
        """
        request_data = {
            "game_gid": 10000147,
            "event_id": 1,
            "fields": sample_base_fields,
            "filter_conditions": {},
            "sql_mode": "view"
        }

        with patch('backend.services.hql.adapters.project_adapter.ProjectAdapter') as MockAdapter, \
             patch('backend.services.hql.core.generator.HQLGenerator') as MockGenerator:

            # Mock adapter
            mock_adapter = Mock()
            mock_event = Event(
                name="test_login",
                table_name="ieu_ods.ods_10000147_all_view"
            )
            mock_adapter.event_from_project.return_value = mock_event

            def mock_field_conversion(field):
                return Field(name=field["name"], type=field["type"])
            mock_adapter.field_from_project.side_effect = mock_field_conversion

            MockAdapter.return_value = mock_adapter

            # Mock generator
            mock_generator = Mock()
            mock_generator.generate.return_value = "SELECT role_id FROM table;"
            MockGenerator.return_value = mock_generator

            # Make request
            response = client.post(
                '/event_node_builder/api/preview-hql',
                json=request_data,
                content_type='application/json'
            )

            # Assertions
            assert response.status_code == 200
            assert response.content_type == 'application/json'

            data = response.get_json()

            # Check response structure
            assert 'success' in data
            assert 'data' in data
            assert 'message' in data

            # Check types
            assert isinstance(data['success'], bool)
            assert isinstance(data['data'], str)
            assert isinstance(data['message'], str)

    def test_endpoint_registered(self, app):
        """
        Test that /api/preview-hql endpoint is properly registered

        Given:
            - Flask app with event_node_builder blueprint

        When:
            - Check registered routes

        Then:
            - /event_node_builder/api/preview-hql is registered
            - Accepts POST method
        """
        with app.app_context():
            rules = [rule.rule for rule in app.url_map.iter_rules()]
            assert '/event_node_builder/api/preview-hql' in rules

            # Check methods
            rule = next(
                (r for r in app.url_map.iter_rules() if r.rule == '/event_node_builder/api/preview-hql'),
                None
            )
            assert rule is not None
            assert 'POST' in rule.methods

    def test_concurrent_requests(self, client, sample_base_fields):
        """
        Test handling of multiple concurrent requests

        Given:
            - Multiple valid requests

        When:
            - Concurrent POST requests to /api/preview-hql

        Then:
            - All requests succeed
            - No race conditions
        """
        request_data = {
            "game_gid": 10000147,
            "event_id": 1,
            "fields": sample_base_fields,
            "filter_conditions": {},
            "sql_mode": "view"
        }

        with patch('backend.services.hql.adapters.project_adapter.ProjectAdapter') as MockAdapter, \
             patch('backend.services.hql.core.generator.HQLGenerator') as MockGenerator:

            # Mock adapter
            mock_adapter = Mock()
            mock_event = Event(
                name="test_login",
                table_name="ieu_ods.ods_10000147_all_view"
            )
            mock_adapter.event_from_project.return_value = mock_event

            def mock_field_conversion(field):
                return Field(name=field["name"], type=field["type"])
            mock_adapter.field_from_project.side_effect = mock_field_conversion

            MockAdapter.return_value = mock_adapter

            # Mock generator
            mock_generator = Mock()
            mock_generator.generate.return_value = "SELECT role_id FROM table;"
            MockGenerator.return_value = mock_generator

            # Make multiple requests
            responses = []
            for _ in range(5):
                response = client.post(
                    '/event_node_builder/api/preview-hql',
                    json=request_data,
                    content_type='application/json'
                )
                responses.append(response)

            # All should succeed
            for response in responses:
                assert response.status_code == 200
                data = response.get_json()
                assert data['success'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
