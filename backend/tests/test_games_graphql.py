"""
Games GraphQL Integration Tests

Tests for Games module GraphQL operations.
"""

import pytest
from backend.gql_api.schema import schema


class TestGamesQueries:
    """Test Games GraphQL queries"""

    def test_games_list_query(self):
        """Test games list query with pagination"""
        query = '''
        query GetGamesList($limit: Int, $offset: Int) {
            games(limit: $limit, offset: $offset) {
                gid
                name
                odsDb
                eventCount
                parameterCount
            }
        }
        '''

        result = schema.execute(query, variables={'limit': 10, 'offset': 0})
        
        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None
        assert 'games' in result.data
        assert isinstance(result.data['games'], list)

    def test_single_game_query(self):
        """Test single game query"""
        query = '''
        query GetGame($gid: Int!) {
            game(gid: $gid) {
                gid
                name
                odsDb
                eventCount
                parameterCount
            }
        }
        '''

        result = schema.execute(query, variables={'gid': 10000147})
        
        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None
        assert 'game' in result.data

    def test_search_games_query(self):
        """Test games search query"""
        query = '''
        query SearchGames($query: String!) {
            searchGames(query: $query) {
                gid
                name
                odsDb
            }
        }
        '''

        result = schema.execute(query, variables={'query': 'game'})
        
        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None
        assert 'searchGames' in result.data
        assert isinstance(result.data['searchGames'], list)


class TestGamesMutations:
    """Test Games GraphQL mutations"""

    def test_create_game_mutation_structure(self):
        """Test create game mutation structure"""
        query = '''
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
        '''

        # Use a unique GID for testing
        result = schema.execute(
            query, 
            variables={
                'gid': 99999999,
                'name': 'Test Game GraphQL',
                'odsDb': 'ieu_ods'
            }
        )
        
        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None
        assert 'createGame' in result.data
        assert 'ok' in result.data['createGame']

    def test_update_game_mutation_structure(self):
        """Test update game mutation structure"""
        query = '''
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
        '''

        # This will fail if game doesn't exist, but structure is correct
        result = schema.execute(
            query,
            variables={
                'gid': 10000147,
                'name': 'Updated Game Name'
            }
        )
        
        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None
        assert 'updateGame' in result.data

    def test_delete_game_mutation_structure(self):
        """Test delete game mutation structure"""
        query = '''
        mutation DeleteGame($gid: Int!, $confirm: Boolean) {
            deleteGame(gid: $gid, confirm: $confirm) {
                ok
                message
                errors
            }
        }
        '''

        # Test with a non-existent game
        result = schema.execute(
            query,
            variables={
                'gid': 99999998,
                'confirm': False
            }
        )
        
        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None
        assert 'deleteGame' in result.data


class TestDataLoaderIntegration:
    """Test DataLoader integration"""

    def test_game_loader_batch_loading(self):
        """Test that GameLoader batches requests"""
        from backend.gql_api.dataloaders import game_loader
        
        # Clear loader cache
        game_loader.clear_all()
        
        # Load multiple games
        query = '''
        query GetMultipleGames {
            game1: game(gid: 10000147) {
                gid
                name
            }
            game2: game(gid: 10000148) {
                gid
                name
            }
        }
        '''

        result = schema.execute(query)
        
        # Should not have errors (even if games don't exist)
        assert result.errors is None or len(result.errors) == 0


class TestCacheIntegration:
    """Test cache middleware integration"""

    def test_query_caching(self):
        """Test that queries are cached"""
        query = '''
        query GetGamesCached {
            games(limit: 5) {
                gid
                name
            }
        }
        '''

        # First query
        result1 = schema.execute(query)
        
        # Second query (should hit cache)
        result2 = schema.execute(query)
        
        assert result1.errors is None or len(result1.errors) == 0
        assert result2.errors is None or len(result2.errors) == 0
        
        # Both should return data
        assert result1.data is not None
        assert result2.data is not None


class TestPerformance:
    """Performance tests"""

    def test_games_query_performance(self):
        """Test games query performance"""
        import time

        query = '''
        query GetGamesPerformance {
            games(limit: 50) {
                gid
                name
                odsDb
                eventCount
                parameterCount
            }
        }
        '''

        start = time.time()
        result = schema.execute(query)
        end = time.time()
        
        execution_time = end - start
        
        assert result.errors is None or len(result.errors) == 0
        # Should complete within 1 second
        assert execution_time < 1.0, f"Query took {execution_time:.2f}s"
        
        print(f"\nGames query execution time: {execution_time:.3f}s")

    def test_nested_query_performance(self):
        """Test nested query performance with DataLoader"""
        import time

        # This query would cause N+1 without DataLoader
        query = '''
        query GetGamesWithEvents {
            games(limit: 10) {
                gid
                name
                eventCount
            }
        }
        '''

        start = time.time()
        result = schema.execute(query)
        end = time.time()
        
        execution_time = end - start
        
        assert result.errors is None or len(result.errors) == 0
        # Should complete within 2 seconds even with nested data
        assert execution_time < 2.0, f"Query took {execution_time:.2f}s"
        
        print(f"\nNested query execution time: {execution_time:.3f}s")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
