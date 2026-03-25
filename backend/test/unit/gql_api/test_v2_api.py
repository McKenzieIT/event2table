"""
V2 GraphQL API Test

Tests for V2 GraphQL queries and mutations.
"""

import os
import sys

import pytest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from backend.gql_api.schema import schema


class TestGameV2Queries:
    """Test Game V2 queries"""

    def test_games_v2_query(self):
        """Test games V2 list query"""
        query = """
        query {
            gamesV2 {
                id
                gid
                name
                odsDb
                isActive
                eventCount
            }
        }
        """

        result = schema.execute(query)

        # Check for errors
        assert result.errors is None or len(result.errors) == 0

        # Check data
        if result.data:
            games = result.data.get('gamesV2', [])
            assert isinstance(games, list)

            # If games exist, check structure
            if games:
                game = games[0]
                assert 'id' in game
                assert 'gid' in game
                assert 'name' in game
                assert 'odsDb' in game
                assert 'isActive' in game

    def test_game_v2_query(self):
        """Test single game V2 query"""
        # First get a list of games to find a valid GID
        list_query = """
        query {
            gamesV2 {
                gid
            }
        }
        """

        list_result = schema.execute(list_query)

        if list_result.data and list_result.data.get('gamesV2'):
            games = list_result.data['gamesV2']
            if games:
                gid = games[0]['gid']

                # Query single game
                query = f"""
                query {{
                    gameV2(gid: {gid}) {{
                        id
                        gid
                        name
                        odsDb
                        isActive
                        eventCount
                    }}
                }}
                """

                result = schema.execute(query)

                # Check for errors
                assert result.errors is None or len(result.errors) == 0

                # Check data
                if result.data:
                    game = result.data.get('gameV2')
                    if game:
                        assert game['gid'] == gid


class TestEventV2Queries:
    """Test Event V2 queries"""

    def test_events_v2_query(self):
        """Test events V2 list query with pagination"""
        # First get a game GID
        games_query = """
        query {
            gamesV2 {
                gid
            }
        }
        """

        games_result = schema.execute(games_query)

        if games_result.data and games_result.data.get('gamesV2'):
            games = games_result.data['gamesV2']
            if games:
                game_gid = games[0]['gid']

                # Query events with pagination
                query = f"""
                query {{
                    eventsV2(gameGid: {game_gid}, page: 1, perPage: 10) {{
                        data {{
                            id
                            eventName
                            eventNameCn
                            isActive
                            gameGid
                        }}
                        pagination {{
                            total
                            page
                            perPage
                            totalPages
                        }}
                    }}
                }}
                """

                result = schema.execute(query)

                # Check for errors
                assert result.errors is None or len(result.errors) == 0

                # Check data
                if result.data:
                    events_data = result.data.get('eventsV2')
                    if events_data:
                        assert 'data' in events_data
                        assert 'pagination' in events_data

                        # Check pagination structure
                        pagination = events_data['pagination']
                        assert 'total' in pagination
                        assert 'page' in pagination
                        assert 'perPage' in pagination
                        assert 'totalPages' in pagination


class TestGameV2Mutations:
    """Test Game V2 mutations"""

    def test_create_game_v2_mutation(self):
        """Test create game V2 mutation"""
        # Use a test GID (90000000+ range)
        test_gid = 90000001

        mutation = f"""
        mutation {{
            createGameV2(input: {{
                gid: {test_gid},
                name: "Test Game V2",
                odsDb: "ieu_ods",
                description: "Test game for V2 API"
            }}) {{
                success
                message
                game {{
                    id
                    gid
                    name
                    odsDb
                }}
                errors
            }}
        }}
        """

        result = v2_schema.execute(mutation)

        # Check for errors
        if result.errors:
            print(f"GraphQL Errors: {result.errors}")

        # Check data
        if result.data:
            create_result = result.data.get('createGameV2')
            if create_result:
                assert 'success' in create_result
                assert 'message' in create_result

                # If successful, check game data
                if create_result['success']:
                    game = create_result.get('game')
                    if game:
                        assert game['gid'] == test_gid
                        assert game['name'] == "Test Game V2"

    def test_batch_delete_games_v2_mutation(self):
        """Test batch delete games V2 mutation"""
        # Use test GIDs (90000000+ range)
        test_gids = [90000002, 90000003]

        mutation = f"""
        mutation {{
            batchDeleteGamesV2(gids: {test_gids}) {{
                success
                message
                deletedCount
                failedCount
                errors
            }}
        }}
        """

        result = v2_schema.execute(mutation)

        # Check for errors
        if result.errors:
            print(f"GraphQL Errors: {result.errors}")

        # Check data
        if result.data:
            delete_result = result.data.get('batchDeleteGamesV2')
            if delete_result:
                assert 'success' in delete_result
                assert 'message' in delete_result
                assert 'deletedCount' in delete_result
                assert 'failedCount' in delete_result


class TestEventV2Mutations:
    """Test Event V2 mutations"""

    def test_create_event_v2_mutation(self):
        """Test create event V2 mutation"""
        # First get a game GID
        games_query = """
        query {
            gamesV2 {
                gid
            }
        }
        """

        games_result = schema.execute(games_query)

        if games_result.data and games_result.data.get('gamesV2'):
            games = games_result.data['gamesV2']
            if games:
                game_gid = games[0]['gid']

                # Create event
                mutation = f"""
                mutation {{
                    createEventV2(input: {{
                        gameGid: {game_gid},
                        eventName: "test_event_v2",
                        eventNameCn: "测试事件V2",
                        description: "Test event for V2 API"
                    }}) {{
                        success
                        message
                        event {{
                            id
                            eventName
                            eventNameCn
                            gameGid
                        }}
                        errors
                    }}
                }}
                """

                result = v2_schema.execute(mutation)

                # Check for errors
                if result.errors:
                    print(f"GraphQL Errors: {result.errors}")

                # Check data
                if result.data:
                    create_result = result.data.get('createEventV2')
                    if create_result:
                        assert 'success' in create_result
                        assert 'message' in create_result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
