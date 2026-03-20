"""
GraphQL Mutation Tests

Tests for GraphQL mutation operations.
"""

import pytest
from backend.gql_api.schema import schema


class TestGameMutations:
    """Test game-related mutations"""

    @pytest.mark.integration
    def test_create_game(self, client):
        """Test creating a game"""
        mutation = """
        mutation CreateGame($gid: Int!, $name: String!, $odsDb: String!) {
            createGame(gid: $gid, name: $name, odsDb: $odsDb) {
                ok
                game {
                    gid
                    name
                    odsDb
                }
                errors
            }
        }
        """

        # Use a test GID that won't conflict
        result = schema.execute(
            mutation, variables={"gid": 99999999, "name": "Test Game", "odsDb": "ieu_ods"}
        )

        # Check that mutation executes
        assert result.errors is None or len(result.errors) == 0

        # In integration tests, verify the game was created
        # and clean up afterwards

    @pytest.mark.integration
    def test_update_game(self, client):
        """Test updating a game"""
        mutation = """
        mutation UpdateGame($gid: Int!, $name: String) {
            updateGame(gid: $gid, name: $name) {
                ok
                game {
                    gid
                    name
                }
                errors
            }
        }
        """

        result = schema.execute(mutation, variables={"gid": 10000147, "name": "Updated Name"})

        # Check that mutation executes
        assert result.errors is None or len(result.errors) == 0


class TestEventMutations:
    """Test event-related mutations"""

    @pytest.mark.integration
    def test_create_event(self, client):
        """Test creating an event"""
        mutation = """
        mutation CreateEvent(
            $gameGid: Int!,
            $eventName: String!,
            $eventNameCn: String!,
            $categoryId: Int!
        ) {
            createEvent(
                gameGid: $gameGid,
                eventName: $eventName,
                eventNameCn: $eventNameCn,
                categoryId: $categoryId
            ) {
                ok
                event {
                    id
                    eventName
                    eventNameCn
                }
                errors
            }
        }
        """

        result = schema.execute(
            mutation,
            variables={
                "gameGid": 10000147,
                "eventName": "test_event",
                "eventNameCn": "测试事件",
                "categoryId": 1,
            },
        )

        # Check that mutation executes
        assert result.errors is None or len(result.errors) == 0
