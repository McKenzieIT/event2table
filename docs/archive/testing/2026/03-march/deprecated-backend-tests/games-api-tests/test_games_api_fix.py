"""
Test for Games API 500 error bug fix

This test verifies that GET /api/games returns 200 status code
and a valid list of games, not a 500 error.

Bug: GET /api/games currently returns 500 error
Expected: GET /api/games should return 200 with games list
"""

import pytest
from web_app import app


class TestGamesAPIBugFix:
    """Test suite for Games API 500 error bug fix"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        app.config['TESTING'] = True
        return app.test_client()

    def test_get_games_should_return_200_not_500(self, client):
        """
        RED: This test should fail because GET /api/games returns 500

        Expected behavior:
        - Status code should be 200, not 500
        - Response should contain "success": true
        - Response should contain a data array with games
        """
        response = client.get('/api/games')

        # This should fail because API returns 500
        assert response.status_code == 200, f"Expected status 200, got {response.status_code}"

        json_data = response.get_json()

        # This should fail because API returns error
        assert (
            json_data.get('success') is True
        ), f"Expected success=true, got {json_data.get('success')}"

        # This should fail because API returns error message
        assert (
            'data' in json_data
        ), f"Expected 'data' key in response, got keys: {list(json_data.keys())}"

        # Verify data is a list
        assert isinstance(
            json_data['data'], list
        ), f"Expected data to be list, got {type(json_data['data'])}"

    def test_get_games_should_contain_valid_game_data(self, client):
        """
        RED: This test should fail because API returns error

        Expected behavior:
        - Games list should contain valid game objects
        - Each game should have required fields (gid, name, ods_db)
        """
        response = client.get('/api/games')

        # This will fail at status code check
        assert response.status_code == 200

        json_data = response.get_json()
        games = json_data.get('data', [])

        # If we have games, verify structure
        if len(games) > 0:
            first_game = games[0]

            # Required fields
            assert 'gid' in first_game, "Game should have 'gid' field"
            assert 'name' in first_game, "Game should have 'name' field"
            assert 'ods_db' in first_game, "Game should have 'ods_db' field"

            # Verify field types
            assert isinstance(first_game['gid'], int), "gid should be int"
            assert isinstance(first_game['name'], str), "name should be str"
            assert isinstance(first_game['ods_db'], str), "ods_db should be str"
