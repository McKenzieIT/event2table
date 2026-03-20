"""
Unit Tests for GraphQL Authentication (TDD Complete)

Tests the authentication decorators without Flask dependencies.
This is a complete TDD cycle: RED → GREEN → REFACTOR
"""

import os
import pytest
from unittest.mock import Mock

# Set development mode
os.environ['FLASK_ENV'] = 'development'

from backend.core.security.authentication import (
    authenticated,
    require_permission,
    is_development_mode,
    is_production_mode,
    check_auth_context,
    check_user_permission
)


class TestEnvironmentDetection:
    """Test environment detection functions"""

    def test_is_development_mode(self):
        """Test: Development mode detection"""
        os.environ['FLASK_ENV'] = 'development'
        assert is_development_mode() == True
        assert is_production_mode() == False

    def test_is_production_mode(self):
        """Test: Production mode detection"""
        os.environ['FLASK_ENV'] = 'production'
        assert is_development_mode() == False
        assert is_production_mode() == True

    def test_default_is_development(self):
        """Test: Default to development mode when FLASK_ENV not set"""
        del os.environ['FLASK_ENV']
        # Re-import to test default behavior
        import importlib
        import backend.core.security.authentication
        importlib.reload(backend.core.security.authentication)

        assert is_development_mode() == True


class TestAuthenticatedDecorator:
    """Test @authenticated decorator"""

    def test_authenticated_with_none_context_development(self):
        """
        Test: @authenticated with None context in development mode

        Expected: Allow mutation (development mode)
        """
        os.environ['FLASK_ENV'] = 'development'

        @authenticated
        def mock_mutation(root, info, *args, **kwargs):
            return "SUCCESS"

        # Create mock info with None context
        info = Mock()
        info.context = None

        # Should NOT raise exception in development mode
        result = mock_mutation(None, info)
        assert result == "SUCCESS"

    def test_authenticated_with_none_context_production(self):
        """
        Test: @authenticated with None context in production mode

        Expected: Raise Exception (production mode)
        """
        os.environ['FLASK_ENV'] = 'production'

        @authenticated
        def mock_mutation(root, info, *args, **kwargs):
            return "SUCCESS"

        # Create mock info with None context
        info = Mock()
        info.context = None

        # Should raise exception in production mode
        with pytest.raises(Exception) as exc_info:
            mock_mutation(None, info)

        assert "Authentication required" in str(exc_info.value)

    def test_authenticated_with_none_user_development(self):
        """
        Test: @authenticated with None user in development mode

        Expected: Allow mutation (development mode)
        """
        os.environ['FLASK_ENV'] = 'development'

        @authenticated
        def mock_mutation(root, info, *args, **kwargs):
            return "SUCCESS"

        # Create mock info with context but None user
        info = Mock()
        info.context.user = None

        # Should NOT raise exception in development mode
        result = mock_mutation(None, info)
        assert result == "SUCCESS"

    def test_authenticated_with_valid_user(self):
        """
        Test: @authenticated with valid user

        Expected: Allow mutation
        """
        @authenticated
        def mock_mutation(root, info, *args, **kwargs):
            return "SUCCESS"

        # Create mock info with valid user
        info = Mock()
        user = Mock()
        info.context.user = user

        # Should succeed
        result = mock_mutation(None, info)
        assert result == "SUCCESS"


class TestRequirePermissionDecorator:
    """Test @require_permission decorator"""

    def test_require_permission_with_none_context_development(self):
        """
        Test: @require_permission with None context in development mode

        Expected: Allow mutation (development mode)
        """
        os.environ['FLASK_ENV'] = 'development'

        @require_permission('game:write')
        def mock_mutation(root, info, *args, **kwargs):
            return "SUCCESS"

        # Create mock info with None context
        info = Mock()
        info.context = None

        # Should NOT raise exception in development mode
        result = mock_mutation(None, info)
        assert result == "SUCCESS"

    def test_require_permission_with_valid_user_permission(self):
        """
        Test: @require_permission with valid user and permission

        Expected: Allow mutation
        """
        @require_permission('game:write')
        def mock_mutation(root, info, *args, **kwargs):
            return "SUCCESS"

        # Create mock info with valid user and permission
        info = Mock()
        user = Mock()
        user.permissions = ['game:write', 'game:read']
        info.context.user = user

        # Should succeed
        result = mock_mutation(None, info)
        assert result == "SUCCESS"

    def test_require_permission_with_missing_permission(self):
        """
        Test: @require_permission with missing permission

        Expected: Raise Exception (missing permission)
        """
        @require_permission('game:delete')
        def mock_mutation(root, info, *args, **kwargs):
            return "SUCCESS"

        # Create mock info with user but missing permission
        info = Mock()
        user = Mock()
        user.permissions = ['game:write', 'game:read']
        info.context.user = user

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            mock_mutation(None, info)

        assert "Missing 'game:delete' permission" in str(exc_info.value)


class TestHelperFunctions:
    """Test helper functions"""

    def test_check_auth_context_development(self):
        """
        Test: check_auth_context in development mode

        Expected: No exception (development mode)
        """
        os.environ['FLASK_ENV'] = 'development'

        info = Mock()
        info.context = None

        # Should NOT raise exception in development mode
        check_auth_context(info)

    def test_check_auth_context_production(self):
        """
        Test: check_auth_context in production mode

        Expected: Raise Exception (production mode)
        """
        os.environ['FLASK_ENV'] = 'production'

        info = Mock()
        info.context = None

        # Should raise exception in production mode
        with pytest.raises(Exception) as exc_info:
            check_auth_context(info)

        assert "Authentication required" in str(exc_info.value)

    def test_check_user_permission_development(self):
        """
        Test: check_user_permission in development mode

        Expected: No exception (development mode)
        """
        os.environ['FLASK_ENV'] = 'development'

        info = Mock()
        info.context = None

        # Should NOT raise exception in development mode
        check_user_permission(info, 'game:write')


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v', '-s'])
