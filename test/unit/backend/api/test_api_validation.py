#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Parameter Validation Tests
===============================

Tests for parameter validation, type conversion, and edge cases.
Prevents issues like missing safe_int_convert validation.

Created: 2026-01-25
Purpose: Test parameter validation and edge cases for all API endpoints
"""

import sys
import json
from pathlib import Path

# Add project path
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
from web_app import app


class TestAPIParameterValidation(unittest.TestCase):
    """Test API parameter validation and type conversion"""

    @classmethod
    def setUpClass(cls):
        """Setup test client"""
        cls.client = app.test_client()

    def test_events_api_invalid_page_number(self):
        """Test GET /api/events with negative page number"""
        response = self.client.get("/api/events?page=-1")
        # Should handle gracefully (default to page 1 or return error)
        self.assertIn(response.status_code, [200, 400])

    def test_events_api_invalid_per_page(self):
        """Test GET /api/events with invalid per_page"""
        response = self.client.get("/api/events?per_page=abc")
        # Should handle gracefully (default to 20 or return error)
        self.assertIn(response.status_code, [200, 400])

    def test_events_api_per_page_too_large(self):
        """Test GET /api/events with per_page exceeding maximum"""
        response = self.client.get("/api/events?per_page=999")
        data = json.loads(response.data)

        if response.status_code == 200:
            # Should cap at maximum (100)
            self.assertLessEqual(data['data']['pagination']['per_page'], 100)

    def test_events_api_invalid_game_id(self):
        """Test GET /api/events with invalid game_id"""
        response = self.client.get("/api/events?game_id=abc")

        # Should handle gracefully (either filter by 0 or return error)
        self.assertIn(response.status_code, [200, 400])

        if response.status_code == 200:
            data = json.loads(response.data)
            # Should still return valid structure
            self.assertIn('events', data['data'])
            self.assertIn('pagination', data['data'])

    def test_events_api_sql_injection_attempt(self):
        """Test GET /api/events with SQL injection attempt in search"""
        response = self.client.get("/api/events?search=';DROP TABLE log_events;--")

        # Should handle safely (not execute SQL)
        self.assertIn(response.status_code, [200, 400])

        if response.status_code == 200:
            # Should treat as literal string search
            data = json.loads(response.data)
            self.assertTrue(data['success'])

    def test_create_event_missing_required_field(self):
        """Test POST /api/events with missing required field"""
        incomplete_event = {
            "game_id": 1,
            "event_name": "game.test",
            # Missing event_name_cn
            "category_id": 1,
        }

        response = self.client.post(
            "/api/events",
            data=json.dumps(incomplete_event),
            content_type="application/json"
        )

        # Should return 400 for missing required field
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertFalse(data['success'])

    def test_create_event_invalid_game_id(self):
        """Test POST /api/events with non-existent game_id"""
        invalid_event = {
            "game_id": 99999,  # Non-existent game
            "event_name": "game.test",
            "event_name_cn": "测试",
            "category_id": 1,
        }

        response = self.client.post(
            "/api/events",
            data=json.dumps(invalid_event),
            content_type="application/json"
        )

        # Should return 400 or 404 for invalid game
        self.assertIn(response.status_code, [400, 404])

        data = json.loads(response.data)
        self.assertFalse(data['success'])

    def test_create_event_invalid_json(self):
        """Test POST /api/events with malformed JSON"""
        response = self.client.post(
            "/api/events",
            data="{invalid json}",
            content_type="application/json"
        )

        # Should return 400 for malformed JSON
        self.assertEqual(response.status_code, 400)

    def test_games_api_pagination_edge_cases(self):
        """Test GET /api/games pagination edge cases"""
        # Test with page=0 (should default to 1)
        response = self.client.get("/api/games?page=0")
        self.assertIn(response.status_code, [200, 400])

        # Test with very large page number
        response = self.client.get("/api/games?page=999999")
        self.assertIn(response.status_code, [200, 404])  # 200 with empty list or 404

    def test_api_response_format_consistency(self):
        """Test that all API responses follow consistent format"""
        endpoints = [
            "/api/games",
            "/api/events",
            "/api/parameters/all",
        ]

        for endpoint in endpoints:
            response = self.client.get(endpoint)

            if response.status_code == 200:
                data = json.loads(response.data)

                # All successful responses should have 'success' and 'timestamp' keys
                self.assertIn('success', data, f"{endpoint} missing 'success' key")
                self.assertIn('timestamp', data, f"{endpoint} missing 'timestamp' key")

                # If successful, should have 'data' key
                if data['success']:
                    self.assertIn('data', data, f"{endpoint} missing 'data' key")


if __name__ == '__main__':
    unittest.main(verbosity=2)
