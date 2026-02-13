#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Canvas Processing Module
Tests for backend/services/canvas/canvas.py module

Following TDD principle: Write tests first, watch them fail, then implement.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, session

# We need to test the blueprint routes
from backend.services.canvas.canvas import (
    canvas_bp,
    generate_mock_results,
)


class TestGenerateMockResults:
    """Test generate_mock_results function"""

    def test_generate_mock_results_with_string_field(self):
        """Test generating mock results with string field"""
        output_fields = [
            {"name": "ds", "alias": "ds", "data_type": "string"}
        ]
        limit = 3

        result = generate_mock_results(output_fields, limit)

        assert result['row_count'] == 3
        assert len(result['rows']) == 3
        assert result['columns'] == ['ds']
        assert 'execution_time_ms' in result

    def test_generate_mock_results_with_multiple_fields(self):
        """Test generating mock results with multiple field types"""
        output_fields = [
            {"name": "ds", "alias": "ds", "data_type": "string"},
            {"name": "role_id", "alias": "role_id", "data_type": "bigint"},
            {"name": "level", "alias": "level", "data_type": "int"}
        ]
        limit = 2

        result = generate_mock_results(output_fields, limit)

        assert result['row_count'] == 2
        assert len(result['rows']) == 2
        assert len(result['columns']) == 3
        # Check that rows have correct number of columns
        assert all(len(row) == 3 for row in result['rows'])

    def test_generate_mock_results_default_limit(self):
        """Test generating mock results with default limit"""
        output_fields = [
            {"name": "ds", "alias": "ds", "data_type": "string"}
        ]

        result = generate_mock_results(output_fields)

        assert result['row_count'] == 5  # Default limit

    def test_generate_mock_results_empty_fields(self):
        """Test generating mock results with no fields"""
        output_fields = []
        limit = 3

        result = generate_mock_results(output_fields, limit)

        assert result['row_count'] == 0
        assert len(result['rows']) == 0
        assert result['columns'] == []

    def test_generate_mock_results_includes_execution_time(self):
        """Test that execution time is included in response"""
        output_fields = [
            {"name": "ds", "alias": "ds", "data_type": "string"}
        ]

        result = generate_mock_results(output_fields, 1)

        assert 'execution_time_ms' in result
        assert isinstance(result['execution_time_ms'], int)
        assert result['execution_time_ms'] >= 0


class TestCanvasHealthCheck:
    """Test canvas health check endpoint"""

    def test_health_check_returns_healthy_status(self):
        """Test that health check returns healthy status"""
        from flask import Flask
        from backend.services.canvas.canvas import health_check

        with Flask(__name__).test_request_context():
            response = health_check()

            # Verify response is a tuple (response, status_code)
            assert isinstance(response, tuple)
            assert len(response) == 2
            assert response[1] == 200  # Status code

            # Verify response JSON contains healthy status
            import json
            response_data = json.loads(response[0].get_data(as_text=True))
            assert response_data.get('success') == True
            assert response_data.get('data', {}).get('status') == 'healthy'


class TestCanvasValidationEndpoint:
    """Test canvas validation endpoint"""

    @patch('backend.services.node.canvas.validate_flow_graph')
    @patch('backend.services.node.canvas.json_success_response')
    def test_validate_flow_success(self, mock_json_response, mock_validate):
        """Test successful flow validation"""
        mock_validate.return_value = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'execution_order': ['node1', 'node2'],
            'validation_details': {}
        }
        mock_json_response.return_value = {"success": True}

        from backend.services.canvas.canvas import validate_flow

        with Flask(__name__).test_request_context(json={
            'nodes': [{'id': 'node1', 'type': 'event'}],
            'edges': []
        }):
            response = validate_flow()

        mock_validate.assert_called_once()
        call_args = mock_validate.call_args
        assert len(call_args[0][0]) == 1  # nodes
        assert len(call_args[0][1]) == 0  # edges

    @patch('backend.services.node.canvas.validate_flow_graph')
    @patch('backend.services.node.canvas.json_success_response')
    def test_validate_flow_with_connections(self, mock_json_response, mock_validate):
        """Test validation with 'connections' instead of 'edges'"""
        mock_validate.return_value = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        mock_json_response.return_value = {"success": True}

        from backend.services.canvas.canvas import validate_flow

        with Flask(__name__).test_request_context(json={
            'nodes': [{'id': 'node1'}],
            'connections': [{'from': 'node1', 'to': 'node2'}]
        }):
            response = validate_flow()

        mock_validate.assert_called_once()
        call_args = mock_validate.call_args
        # Should convert connections to edges
        assert len(call_args[0][1]) == 1  # edges

    @patch('backend.services.node.canvas.json_error_response')
    def test_validate_flow_missing_body(self, mock_json_error):
        """Test validation with missing request body"""
        mock_json_error.return_value = {"error": "Missing request body or invalid Content-Type"}

        from backend.services.canvas.canvas import validate_flow

        with Flask(__name__).test_request_context(json=None):
            response = validate_flow()

        mock_json_error.assert_called_once_with('Missing request body or invalid Content-Type', status_code=400)

    @patch('backend.services.node.canvas.validate_flow_graph')
    @patch('backend.services.node.canvas.json_success_response')
    def test_validate_flow_with_errors(self, mock_json_response, mock_validate):
        """Test validation that returns errors"""
        mock_validate.return_value = {
            'valid': False,
            'errors': ['Missing required field'],
            'warnings': []
        }
        mock_json_response.return_value = {"success": True}

        from backend.services.canvas.canvas import validate_flow

        with Flask(__name__).test_request_context(json={
            'nodes': [{'id': 'node1'}],
            'edges': []
        }):
            response = validate_flow()

        # Should still call validate and return result
        mock_validate.assert_called_once()

    @patch('backend.services.node.canvas.validate_flow_graph')
    def test_validate_flow_exception_handling(self, mock_validate):
        """Test validation exception handling"""
        mock_validate.side_effect = Exception("Validation error")

        from backend.services.canvas.canvas import validate_flow

        with Flask(__name__).test_request_context(json={
            'nodes': [{'id': 'node1'}],
            'edges': []
        }):
            response = validate_flow()

        # Should return 500 error
        assert response[1] == 500


class TestCanvasPrepareGeneration:
    """Test canvas prepare generation endpoint"""

    @patch('backend.services.node.canvas.node_canvas_flows')
    @patch('backend.services.node.canvas.json_success_response')
    def test_prepare_generation_success(self, mock_json_response, mock_flows):
        """Test successful flow preparation"""
        mock_flows.prepare_flow_for_generation.return_value = {
            'success': True,
            'prepared_graph': {}
        }
        mock_json_response.return_value = {"success": True}

        from backend.services.canvas.canvas import prepare_generation

        with Flask(__name__).test_request_context(json={
            'nodes': [{'id': 'node1'}],
            'connections': []
        }):
            response = prepare_generation()

        mock_flows.prepare_flow_for_generation.assert_called_once()

    @patch('backend.services.node.canvas.json_error_response')
    def test_prepare_generation_missing_body(self, mock_json_error):
        """Test prepare generation with missing body"""
        mock_json_error.return_value = {"error": "Missing request body or invalid Content-Type"}

        from backend.services.canvas.canvas import prepare_generation

        with Flask(__name__).test_request_context(json=None):
            response = prepare_generation()

        mock_json_error.assert_called_once_with('Missing request body or invalid Content-Type', status_code=400)

    @patch('backend.services.node.canvas.node_canvas_flows')
    @patch('backend.services.node.canvas.json_error_response')
    def test_prepare_generation_failure(self, mock_json_error, mock_flows):
        """Test prepare generation with failure"""
        mock_flows.prepare_flow_for_generation.return_value = {
            'success': False,
            'error': 'Invalid graph structure'
        }
        mock_json_error.return_value = {"error": "Invalid graph structure"}

        from backend.services.canvas.canvas import prepare_generation

        with Flask(__name__).test_request_context(json={
            'nodes': [],
            'connections': []
        }):
            response = prepare_generation()

        mock_json_error.assert_called_once()

    @patch('backend.services.node.canvas.node_canvas_flows')
    def test_prepare_generation_exception_handling(self, mock_flows):
        """Test prepare generation exception handling"""
        mock_flows.prepare_flow_for_generation.side_effect = Exception("Prepare error")

        from backend.services.canvas.canvas import prepare_generation

        with Flask(__name__).test_request_context(json={
            'nodes': [{'id': 'node1'}],
            'connections': []
        }):
            response = prepare_generation()

        # Should return 500 error
        assert response[1] == 500


class TestCanvasPreviewResults:
    """Test canvas preview results endpoint"""

    @patch('backend.services.node.canvas.json_success_response')
    def test_preview_results_success(self, mock_json_response):
        """Test successful SQL preview results generation"""
        mock_json_response.return_value = {"success": True}

        from backend.services.canvas.canvas import preview_sql_results

        with Flask(__name__).test_request_context(json={
            'sql': 'SELECT ds, role_id FROM table',
            'output_fields': [
                {"name": "ds", "alias": "ds", "data_type": "string"},
                {"name": "role_id", "alias": "role_id", "data_type": "bigint"}
            ],
            'limit': 3
        }):
            response = preview_sql_results()

        mock_json_response.assert_called_once()
        call_args = mock_json_response.call_args
        result_data = call_args[1]['data']

        assert 'rows' in result_data
        assert 'columns' in result_data
        assert 'row_count' in result_data

    @patch('backend.services.node.canvas.json_error_response')
    def test_preview_results_missing_body(self, mock_json_error):
        """Test preview results with missing body"""
        mock_json_error.return_value = {"error": "Missing request body or invalid Content-Type"}

        from backend.services.canvas.canvas import preview_sql_results

        with Flask(__name__).test_request_context(json=None):
            response = preview_sql_results()

        mock_json_error.assert_called_once_with('Missing request body or invalid Content-Type', status_code=400)

    @patch('backend.services.node.canvas.json_error_response')
    def test_preview_results_empty_sql(self, mock_json_error):
        """Test preview results with empty SQL"""
        mock_json_error.return_value = {"error": "SQL is empty"}

        from backend.services.canvas.canvas import preview_sql_results

        with Flask(__name__).test_request_context(json={
            'sql': '   ',
            'output_fields': []
        }):
            response = preview_sql_results()

        mock_json_error.assert_called_once_with('SQL is empty', status_code=400)

    def test_preview_results_default_limit(self):
        """Test preview results with default limit"""
        from backend.services.canvas.canvas import preview_sql_results

        with Flask(__name__).test_request_context(json={
            'sql': 'SELECT * FROM table',
            'output_fields': [
                {"name": "ds", "alias": "ds", "data_type": "string"}
            ]
        }):
            # Should use default limit of 5
            # We can't easily test this without mocking, but we can verify it doesn't crash
            try:
                response = preview_sql_results()
                assert response is not None
            except Exception as e:
                pytest.fail(f"Should not raise exception: {e}")

    @patch('backend.services.node.canvas.generate_mock_results')
    @patch('backend.services.node.canvas.json_success_response')
    def test_preview_results_custom_limit(self, mock_json_response, mock_generate):
        """Test preview results with custom limit"""
        mock_generate.return_value = {
            'columns': ['ds'],
            'rows': [['2026-01-18']],
            'row_count': 1,
            'execution_time_ms': 100
        }
        mock_json_response.return_value = {"success": True}

        from backend.services.canvas.canvas import preview_sql_results

        with Flask(__name__).test_request_context(json={
            'sql': 'SELECT ds FROM table',
            'output_fields': [{"name": "ds", "alias": "ds", "data_type": "string"}],
            'limit': 10
        }):
            response = preview_sql_results()

        mock_generate.assert_called_once()
        call_args = mock_generate.call_args
        assert call_args[0][1] == 10  # limit parameter

    @patch('backend.services.node.canvas.generate_mock_results')
    def test_preview_results_exception_handling(self, mock_generate):
        """Test preview results exception handling"""
        mock_generate.side_effect = Exception("Generation error")

        from backend.services.canvas.canvas import preview_sql_results

        with Flask(__name__).test_request_context(json={
            'sql': 'SELECT ds FROM table',
            'output_fields': [{"name": "ds", "alias": "ds", "data_type": "string"}]
        }):
            response = preview_sql_results()

        # Should return 500 error
        assert response[1] == 500


class TestCanvasNodeCanvasRoute:
    """Test canvas node_canvas route"""

    @patch('backend.services.node.canvas.fetch_one_as_dict')
    @patch('backend.services.node.canvas.render_template')
    def test_node_canvas_with_game_gid(self, mock_render, mock_fetch):
        """Test node_canvas route with game_gid parameter"""
        mock_fetch.return_value = {
            'id': 1,
            'gid': 10000147,
            'name': 'Test Game'
        }
        mock_render.return_value = 'rendered_html'

        from backend.services.canvas.canvas import node_canvas

        # Create Flask app with SECRET_KEY for session support
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'

        with app.test_request_context('/canvas/node_canvas?game_gid=10000147'):
            response = node_canvas()

        mock_fetch.assert_called_once_with('SELECT * FROM games WHERE gid = ?', (10000147,))
        mock_render.assert_called_once()

    @patch('backend.services.node.canvas.url_for')
    @patch('backend.services.node.canvas.fetch_one_as_dict')
    @patch('backend.services.node.canvas.redirect')
    def test_node_canvas_without_game_gid(self, mock_redirect, mock_fetch, mock_url_for):
        """Test node_canvas route without game_gid parameter"""
        mock_url_for.return_value = '/games'

        from backend.services.canvas.canvas import node_canvas

        # Create Flask app with SECRET_KEY for session support
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'

        with app.test_request_context('/canvas/node_canvas'):
            response = node_canvas()

        # Should redirect to games list
        mock_redirect.assert_called_once()

    @patch('backend.services.node.canvas.url_for')
    @patch('backend.services.node.canvas.fetch_one_as_dict')
    @patch('backend.services.node.canvas.redirect')
    def test_node_canvas_with_invalid_game_gid(self, mock_redirect, mock_fetch, mock_url_for):
        """Test node_canvas route with invalid game_gid"""
        mock_fetch.return_value = None
        mock_url_for.return_value = '/games'

        from backend.services.canvas.canvas import node_canvas

        # Create Flask app with SECRET_KEY for session support
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'

        with app.test_request_context('/canvas/node_canvas?game_gid=999999'):
            response = node_canvas()

        # Should redirect to games list
        mock_redirect.assert_called_once()

    @patch('backend.services.node.canvas.fetch_one_as_dict')
    @patch('backend.services.node.canvas.render_template')
    def test_node_canvas_sets_session(self, mock_render, mock_fetch):
        """Test that node_canvas sets session variables"""
        mock_fetch.return_value = {
            'id': 1,
            'gid': 10000147,
            'name': 'Test Game'
        }
        mock_render.return_value = 'rendered_html'

        from backend.services.canvas.canvas import node_canvas

        # Create Flask app with SECRET_KEY for session support
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'

        with app.test_request_context('/canvas/node_canvas?game_gid=10000147'):
            response = node_canvas()

            # Verify session was set within request context
            assert session.get('current_game_gid') == 10000147

        mock_render.assert_called_once()


class TestCanvasBackwardCompatibility:
    """Test backward compatibility features"""

    @patch('backend.services.node.canvas.url_for')
    @patch('backend.services.node.canvas.fetch_one_as_dict')
    @patch('backend.services.node.canvas.redirect')
    def test_game_id_to_game_gid_redirect(self, mock_redirect, mock_fetch, mock_url_for):
        """Test that game_id is converted to game_gid and redirects"""
        mock_fetch.return_value = {
            'gid': 10000147
        }
        mock_url_for.return_value = '/canvas/node_canvas?game_gid=10000147'

        from backend.services.canvas.canvas import node_canvas

        # Create Flask app with SECRET_KEY for session support
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'

        with app.test_request_context('/canvas/node_canvas?game_id=1'):
            response = node_canvas()

        # Should redirect with game_gid
        mock_redirect.assert_called_once()

    @patch('backend.services.node.canvas.validate_flow_graph')
    @patch('backend.services.node.canvas.json_success_response')
    def test_validate_flow_accepts_connections(self, mock_json_response, mock_validate):
        """Test that validate_flow accepts both 'edges' and 'connections'"""
        mock_validate.return_value = {'valid': True, 'errors': [], 'warnings': []}
        mock_json_response.return_value = {"success": True}

        from backend.services.canvas.canvas import validate_flow

        # Test with 'connections' instead of 'edges'
        with Flask(__name__).test_request_context(json={
            'nodes': [{'id': 'node1'}],
            'connections': [{'from': 'node1', 'to': 'node2'}]
        }):
            response = validate_flow()

        # Should convert connections to edges and validate
        mock_validate.assert_called_once()
        call_args = mock_validate.call_args
        assert len(call_args[0][1]) == 1  # Should have 1 edge
