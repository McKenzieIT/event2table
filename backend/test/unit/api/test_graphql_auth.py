"""
GraphQL Authentication Tests (TDD Phase 1: RED)

Tests the authentication behavior in GraphQL mutations.
This test file follows TDD principles: write failing test first, then fix.

Issue: 'Request' object has no attribute 'user' error in GraphQL mutations
Root Cause: @authenticated decorator expects info.context.user, but it may not exist
"""

from unittest.mock import Mock

import pytest

# Import GraphQL mutations
from backend.gql_api.mutations.game_mutations import CreateGame


class TestGraphQLAuthentication:
    """
    Test GraphQL authentication behavior

    TDD Workflow:
    1. RED: Write failing test (current state)
    2. GREEN: Write minimal code to pass
    3. REFACTOR: Improve code quality
    """

    def test_create_game_without_user_context(self):
        """
        Test: CreateGame mutation without user context (development mode)

        Expected Behavior (After Fix):
        - Should NOT raise AttributeError: 'Request' object has no attribute 'user'
        - Should allow mutation in development environment (no authentication required)
        - Should return successful response with created game

        Current Behavior (Before Fix - RED):
        - Raises: AttributeError or Exception about missing user
        """
        # Arrange: Create mock info object WITHOUT user context
        info = Mock()
        info.context = Mock()
        info.context.user = None  # Simulate no user (development mode)

        # Act: Try to create game
        mutation = CreateGame()

        # This should raise an error in current implementation
        # After fix, this should succeed
        with pytest.raises(Exception) as exc_info:
            result = mutation.mutate(info, gid=90099999, name='Test Auth Game', ods_db='ieu_ods')

        # Assert: Should fail with authentication error (current state)
        assert 'Authentication required' in str(exc_info.value)

    def test_create_game_with_user_context(self):
        """
        Test: CreateGame mutation WITH user context

        Expected Behavior:
        - Should succeed with proper user context
        - Should return CreateGame response with ok=True
        """
        # Arrange: Create mock info object WITH user context
        info = Mock()
        info.context = Mock()

        # Create mock user with permissions
        user = Mock()
        user.permissions = ['game:write']
        info.context.user = user

        # Act: Try to create game
        mutation = CreateGame()

        # This should succeed (after we fix the authentication issue)
        result = mutation.mutate(info, gid=90099998, name='Test Game With User', ods_db='ieu_ods')

        # Assert: Should succeed
        assert result is not None
        # After fix, we expect: assert result.ok == True

    def test_create_game_without_context_object(self):
        """
        Test: CreateGame mutation without context object at all

        Expected Behavior (After Fix):
        - Should handle missing context gracefully
        - Should not crash with AttributeError

        Current Behavior (Before Fix - RED):
        - Raises: AttributeError about missing context
        """
        # Arrange: Create mock info object WITHOUT context
        info = Mock()
        info.context = None

        # Act: Try to create game
        mutation = CreateGame()

        # This should raise an error in current implementation
        with pytest.raises(Exception) as exc_info:
            result = mutation.mutate(info, gid=90099997, name='Test No Context', ods_db='ieu_ods')

        # Assert: Should fail with context error (current state)
        assert 'context' in str(exc_info.value).lower()


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v', '-s'])
