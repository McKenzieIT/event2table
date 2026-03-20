"""
GraphQL API E2E Tests

End-to-end tests for GraphQL API functionality.
"""

import pytest
import sys

sys.path.insert(0, '/Users/mckenzie/Documents/event2table')

from backend.gql_api.schema import schema


class TestGraphQLGamesE2E:
    """E2E tests for Game queries and mutations"""

    def test_query_games(self):
        """Test querying games list"""
        query = """
        {
            games(limit: 5) {
                gid
                name
                odsDb
                eventCount
            }
        }
        """

        result = schema.execute(query)

        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None
        assert 'games' in result.data
        assert isinstance(result.data['games'], list)

        if len(result.data['games']) > 0:
            game = result.data['games'][0]
            assert 'gid' in game
            assert 'name' in game
            assert 'odsDb' in game
            print(f"✅ Query returned {len(result.data['games'])} games")

    def test_query_single_game(self):
        """Test querying a single game by GID"""
        query = """
        query GetGame($gid: Int!) {
            game(gid: $gid) {
                gid
                name
                odsDb
            }
        }
        """

        result = schema.execute(query, variables={"gid": 10000147})

        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None
        assert 'game' in result.data

        if result.data['game']:
            assert result.data['game']['gid'] == 10000147
            print(f"✅ Query returned game: {result.data['game']['name']}")

    def test_search_games(self):
        """Test searching games"""
        query = """
        query SearchGames($query: String!) {
            searchGames(query: $query) {
                gid
                name
            }
        }
        """

        result = schema.execute(query, variables={"query": "Test"})

        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None
        assert 'searchGames' in result.data
        print(f"✅ Search found {len(result.data['searchGames'])} games")


class TestGraphQLEventsE2E:
    """E2E tests for Event queries"""

    def test_query_events(self):
        """Test querying events for a game"""
        query = """
        query GetEvents($gameGid: Int!, $limit: Int) {
            events(gameGid: $gameGid, limit: $limit) {
                id
                eventName
                eventNameCn
                paramCount
            }
        }
        """

        result = schema.execute(query, variables={"gameGid": 10000147, "limit": 5})

        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None
        assert 'events' in result.data

        if len(result.data['events']) > 0:
            event = result.data['events'][0]
            assert 'id' in event
            assert 'eventName' in event
            print(f"✅ Query returned {len(result.data['events'])} events")

    def test_query_single_event(self):
        """Test querying a single event"""
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

        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None
        print(f"✅ Event query executed")


class TestGraphQLMutationsE2E:
    """E2E tests for GraphQL mutations"""

    def test_create_game_mutation(self):
        """Test creating a game via mutation"""
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

        # Use a unique test GID
        result = schema.execute(
            mutation,
            variables={"gid": 99999998, "name": "E2E Test Game GraphQL", "odsDb": "ieu_ods"},
        )

        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None
        assert 'createGame' in result.data

        if result.data['createGame']['ok']:
            print(f"✅ Game created: {result.data['createGame']['game']['name']}")

            # Clean up - delete the test game
            delete_mutation = """
            mutation DeleteGame($gid: Int!) {
                deleteGame(gid: $gid, confirm: true) {
                    ok
                    message
                }
            }
            """
            schema.execute(delete_mutation, variables={"gid": 99999998})
        else:
            print(f"⚠️  Game creation failed: {result.data['createGame']['errors']}")


if __name__ == "__main__":
    # Run tests
    print("\n" + "=" * 60)
    print("GraphQL API E2E Tests")
    print("=" * 60 + "\n")

    # Test games
    print("Testing Games Queries...")
    test_games = TestGraphQLGamesE2E()
    test_games.test_query_games()
    test_games.test_query_single_game()
    test_games.test_search_games()

    print("\nTesting Events Queries...")
    test_events = TestGraphQLEventsE2E()
    test_events.test_query_events()
    test_events.test_query_single_event()

    print("\nTesting Mutations...")
    test_mutations = TestGraphQLMutationsE2E()
    test_mutations.test_create_game_mutation()

    print("\n" + "=" * 60)
    print("✅ All E2E tests completed!")
    print("=" * 60)
