"""
GraphQL Authentication Integration Tests (TDD Phase 1: RED - Real Test)

These tests use the actual GraphQL schema to reproduce the real error:
'Request' object has no attribute 'user'

This is the REAL failing test that will drive our TDD implementation.
"""

import os
import pytest
from unittest.mock import Mock

# Set development mode for all tests
os.environ['FLASK_ENV'] = 'development'


class TestGraphQLAuthIntegration:
    """
    Integration test for GraphQL authentication

    This test uses the actual GraphQL schema and should FAIL before the fix.
    """

    def test_create_game_mutation_without_auth(self, test_db):
        """
        REAL TDD TEST: CreateGame mutation without authentication

        Expected Error (BEFORE FIX - RED):
        - AttributeError: 'Request' object has no attribute 'user'
        - OR Exception: Authentication required

        Expected Behavior (AFTER FIX - GREEN):
        - Mutation succeeds in development mode
        - Returns CreateGame response with ok=True
        """
        # Import schema to test actual GraphQL execution
        from backend.gql_api.schema import schema

        # GraphQL mutation
        mutation = '''
            mutation CreateGame($gid: Int!, $name: String!, $odsDb: String!) {
                createGame(gid: $gid, name: $name, odsDb: $odsDb) {
                    ok
                    game { gid name odsDb }
                    errors
                }
            }
        '''

        variables = {'gid': 90099999, 'name': 'Test Auth Game', 'odsDb': 'ieu_ods'}

        # Execute WITHOUT user context (development mode)
        result = schema.execute(
            mutation, variables=variables, context_value=None  # No context = no user
        )

        # BEFORE FIX: This should have errors
        # AFTER FIX: This should succeed
        print(f"\n=== GraphQL Result ===")
        print(f"Errors: {result.errors}")
        print(f"Data: {result.data}")

        # Assert: AFTER FIX - Should succeed in development mode
        assert result.errors is None, f"Expected no errors, got: {result.errors}"
        assert result.data['createGame']['ok'] == True, "Expected mutation to succeed"
        assert result.data['createGame']['game']['gid'] == 90099999, "Expected correct game GID"

    def test_create_game_mutation_with_mock_auth(self, test_db):
        """
        Test: CreateGame mutation WITH mock authentication

        This should also fail before the fix because of how the
        @authenticated decorator accesses context.user
        """
        from backend.gql_api.schema import schema

        mutation = '''
            mutation CreateGame($gid: Int!, $name: String!, $odsDb: String!) {
                createGame(gid: $gid, name: $name, odsDb: $odsDb) {
                    ok
                    game { gid name odsDb }
                    errors
                }
            }
        '''

        variables = {'gid': 90099998, 'name': 'Test Game With User', 'odsDb': 'ieu_ods'}

        # Create mock context with user
        mock_context = Mock()
        mock_user = Mock()
        mock_user.permissions = ['game:write']
        mock_context.user = mock_user

        # Execute WITH mock user context
        result = schema.execute(mutation, variables=variables, context_value=mock_context)

        print(f"\n=== GraphQL Result (With Auth) ===")
        print(f"Errors: {result.errors}")
        print(f"Data: {result.data}")

        # This might also fail due to the way decorators access the context
        # We'll see what happens!


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
