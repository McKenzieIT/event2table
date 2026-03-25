"""
GraphQL Schema Tests

Tests for GraphQL schema definition and types.
"""

import pytest

from backend.gql_api.schema import schema


class TestGraphQLSchema:
    """Test GraphQL schema structure"""

    def test_schema_has_query_type(self):
        """Test that schema has Query type"""
        assert schema.query_type is not None
        assert schema.query_type.name == "Query"

    def test_schema_has_mutation_type(self):
        """Test that schema has Mutation type"""
        assert schema.mutation_type is not None
        assert schema.mutation_type.name == "Mutation"

    def test_query_has_game_field(self):
        """Test that Query type has game field"""
        fields = schema.query_type.fields
        assert 'game' in fields
        assert 'games' in fields
        assert 'searchGames' in fields

    def test_query_has_event_field(self):
        """Test that Query type has event field"""
        fields = schema.query_type.fields
        assert 'event' in fields
        assert 'events' in fields
        assert 'searchEvents' in fields

    def test_mutation_has_game_operations(self):
        """Test that Mutation type has game operations"""
        fields = schema.mutation_type.fields
        assert 'createGame' in fields
        assert 'updateGame' in fields
        assert 'deleteGame' in fields

    def test_mutation_has_event_operations(self):
        """Test that Mutation type has event operations"""
        fields = schema.mutation_type.fields
        assert 'createEvent' in fields
        assert 'updateEvent' in fields
        assert 'deleteEvent' in fields
