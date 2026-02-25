"""
GraphQL Schema Tests

Tests for GraphQL schema and resolvers.
"""

import pytest
from backend.gql_api.schema import schema


class TestGraphQLSchema:
    """Test GraphQL schema structure"""

    def test_schema_loads(self):
        """Test that schema loads without errors"""
        assert schema is not None

    def test_query_type_exists(self):
        """Test that Query type exists"""
        query_type = schema.get_query_type()
        assert query_type is not None

    def test_mutation_type_exists(self):
        """Test that Mutation type exists"""
        mutation_type = schema.get_mutation_type()
        assert mutation_type is not None

    def test_query_fields(self):
        """Test that Query has expected fields"""
        query_type = schema.get_query_type()
        fields = query_type.fields

        # Game queries
        assert 'game' in fields
        assert 'games' in fields
        assert 'searchGames' in fields

        # Event queries
        assert 'event' in fields
        assert 'events' in fields
        assert 'searchEvents' in fields

        # Category queries
        assert 'category' in fields
        assert 'categories' in fields
        assert 'searchCategories' in fields

    def test_mutation_fields(self):
        """Test that Mutation has expected fields"""
        mutation_type = schema.get_mutation_type()
        fields = mutation_type.fields

        # Game mutations
        assert 'createGame' in fields
        assert 'updateGame' in fields
        assert 'deleteGame' in fields

        # Event mutations
        assert 'createEvent' in fields
        assert 'updateEvent' in fields
        assert 'deleteEvent' in fields


class TestGraphQLQueries:
    """Test GraphQL query execution"""

    def test_games_query(self):
        """Test games query"""
        query = '''
        query {
            games(limit: 5) {
                gid
                name
                odsDb
                eventCount
            }
        }
        '''

        result = schema.execute(query)
        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None

    def test_game_query(self):
        """Test single game query"""
        query = '''
        query($gid: Int!) {
            game(gid: $gid) {
                gid
                name
                odsDb
            }
        }
        '''

        result = schema.execute(query, variables={'gid': 10000147})
        # May return None if game doesn't exist
        assert result.data is not None

    def test_categories_query(self):
        """Test categories query"""
        query = '''
        query {
            categories(limit: 10) {
                id
                name
                eventCount
            }
        }
        '''

        result = schema.execute(query)
        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
