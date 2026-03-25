"""
End-to-End Test: GraphQL Mutations Work Without Authentication

This test verifies that the TDD fix works end-to-end:
- GraphQL mutations can be executed without authentication in development mode
- No 'NoneType' object has no attribute 'user' errors
"""

import os

import pytest

# Set development mode
os.environ['FLASK_ENV'] = 'development'


class TestGraphQLMutationE2E:
    """End-to-end test for GraphQL mutations"""

    def test_create_game_mutation_works(self):
        """
        E2E Test: CreateGame mutation works in development mode

        This is the REAL test that proves the bug is fixed:
        - Before fix: 'NoneType' object has no attribute 'user' error
        - After fix: Mutation succeeds, game is created
        """
        from unittest.mock import Mock

        from backend.gql_api.mutations.game_mutations import CreateGame

        # Arrange: Create mock info object (simulating GraphQL context)
        info = Mock()
        info.context = None  # No user context (development mode)

        # Act: Execute mutation
        mutation = CreateGame()

        # This should NOT raise 'NoneType' object has no attribute 'user' error
        result = mutation.mutate(
            info, gid=90099999, name='TDD Test Game', ods_db='ieu_ods'  # Test GID (safe range)
        )

        # Assert: Mutation should succeed
        assert result is not None, "Mutation should return a result"
        assert result.ok == True, f"Mutation should succeed, got errors: {result.errors}"
        assert result.game is not None, "Game should be created"

        # Verify game data
        assert result.game.gid == 90099999
        assert result.game.name == 'TDD Test Game'
        assert result.game.ods_db == 'ieu_ods'

        print(f"\n✅ SUCCESS: Game created without authentication")
        print(f"   GID: {result.game.gid}")
        print(f"   Name: {result.game.name}")
        print(f"   ODS DB: {result.game.ods_db}")

    def test_update_game_mutation_works(self):
        """
        E2E Test: UpdateGame mutation works in development mode
        """
        from unittest.mock import Mock

        from backend.gql_api.mutations.game_mutations import UpdateGame

        # Arrange: Create mock info object
        info = Mock()
        info.context = None

        # Act: Execute mutation
        mutation = UpdateGame()

        # Use the game created in previous test
        result = mutation.mutate(
            info, gid=90099999, name='TDD Test Game Updated', description='Updated via TDD test'
        )

        # Assert: Mutation should succeed
        assert result is not None
        assert result.ok == True, f"Update failed: {result.errors}"
        assert result.game is not None

        # Verify updated data
        assert result.game.name == 'TDD Test Game Updated'
        assert result.game.description == 'Updated via TDD test'

        print(f"\n✅ SUCCESS: Game updated without authentication")
        print(f"   New Name: {result.game.name}")
        print(f"   Description: {result.game.description}")

    def test_delete_game_mutation_works(self):
        """
        E2E Test: DeleteGame mutation works in development mode
        """
        from unittest.mock import Mock

        from backend.gql_api.mutations.game_mutations import DeleteGame

        # Arrange: Create mock info object
        info = Mock()
        info.context = None

        # Act: Execute mutation
        mutation = DeleteGame()

        # Use the game created in previous tests
        result = mutation.mutate(info, gid=90099999, confirm=True)  # Force delete

        # Assert: Mutation should succeed
        assert result is not None
        assert result.ok == True, f"Delete failed: {result.errors}"
        assert result.message is not None

        print(f"\n✅ SUCCESS: Game deleted without authentication")
        print(f"   Message: {result.message}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
