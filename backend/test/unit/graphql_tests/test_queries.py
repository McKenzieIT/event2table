"""
GraphQL Query Tests

Tests for GraphQL query operations.
"""

import pytest
from backend.gql_api.schema import schema


class TestGameQueries:
    """Test game-related queries"""

    @pytest.mark.integration
    def test_get_game(self, client):
        """Test getting a single game"""
        query = """
        query GetGame($gid: Int!) {
            game(gid: $gid) {
                gid
                name
                odsDb
            }
        }
        """

        # This test requires a database with test data
        # In a real test, you would set up test data first
        result = schema.execute(query, variables={"gid": 10000147})

        # For now, just check that the query executes without errors
        # In integration tests, we'll verify actual data
        assert result.errors is None or len(result.errors) == 0

    @pytest.mark.integration
    def test_get_games(self, client):
        """Test getting list of games"""
        query = """
        query GetGames($limit: Int, $offset: Int) {
            games(limit: $limit, offset: $offset) {
                gid
                name
                odsDb
                eventCount
            }
        }
        """

        result = schema.execute(query, variables={"limit": 10, "offset": 0})

        # Check that query executes
        assert result.errors is None or len(result.errors) == 0

    @pytest.mark.integration
    def test_search_games(self, client):
        """Test searching games"""
        query = """
        query SearchGames($query: String!) {
            searchGames(query: $query) {
                gid
                name
            }
        }
        """

        result = schema.execute(query, variables={"query": "test"})

        # Check that query executes
        assert result.errors is None or len(result.errors) == 0


class TestEventQueries:
    """Test event-related queries"""

    @pytest.mark.integration
    def test_get_event(self, client):
        """Test getting a single event"""
        query = """
        query GetEvent($id: Int!) {
            event(id: $id) {
                id
                eventName
                eventNameCn
                gameGid
            }
        }
        """

        result = schema.execute(query, variables={"id": 1})

        # Check that query executes
        assert result.errors is None or len(result.errors) == 0

    @pytest.mark.integration
    def test_get_events(self, client):
        """Test getting list of events"""
        query = """
        query GetEvents($gameGid: Int!, $limit: Int, $offset: Int) {
            events(gameGid: $gameGid, limit: $limit, offset: $offset) {
                id
                eventName
                eventNameCn
                paramCount
            }
        }
        """

        result = schema.execute(query, variables={"gameGid": 10000147, "limit": 10, "offset": 0})

        # Check that query executes
        assert result.errors is None or len(result.errors) == 0
