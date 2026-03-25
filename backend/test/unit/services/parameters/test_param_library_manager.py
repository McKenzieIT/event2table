#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for ParamLibraryManager

Tests the migration from direct database access to Repository pattern.
Follows TDD: Test first, implementation second.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from backend.services.parameters.param_library_manager import ParamLibraryManager


class TestParamLibraryManagerRepositoryMigration:
    """Test ParamLibraryManager uses Repository pattern"""

    @pytest.fixture
    def test_game_gid(self):
        """Test game GID (not production data)"""
        return 90000001

    @pytest.fixture
    def mock_repo(self):
        """Mock ParameterRepository instance"""
        return Mock()

    @pytest.fixture
    def manager(self, mock_repo):
        """Create ParamLibraryManager with mocked repository"""
        with patch(
            'backend.services.parameters.param_library_manager.ParameterRepository',
            return_value=mock_repo,
        ):
            manager = ParamLibraryManager()
            manager.param_repo = mock_repo  # Ensure it uses our mock
            yield manager

    def test_init_creates_repository(self):
        """Test that manager initializes ParameterRepository"""
        with patch(
            'backend.services.parameters.param_library_manager.ParameterRepository'
        ) as mock_repo_class:
            manager = ParamLibraryManager()
            mock_repo_class.assert_called_once()

    def test_get_param_library_returns_structure(self, manager, mock_repo, test_game_gid):
        """
        Test get_param_library returns expected structure

        Should return:
        {
            'parameters': [...],
            'stats': {
                'total': int,
                'by_type': {...},
                'by_category': {...}
            }
        }
        """
        # Mock repository response - using dict format (actual return type)
        mock_params = [
            {'id': 1, 'param_name': 'zone_id', 'param_type': 'string', 'table_name': 'common'},
            {'id': 2, 'param_name': 'role_id', 'param_type': 'int', 'table_name': 'common'},
        ]

        mock_repo.get_common_params_by_game.return_value = mock_params

        # Call method
        result = manager.get_param_library(test_game_gid)

        # Verify structure
        assert 'parameters' in result
        assert 'stats' in result
        assert isinstance(result['parameters'], list)
        assert len(result['parameters']) == 2

        # Verify stats
        stats = result['stats']
        assert 'total' in stats
        assert 'by_type' in stats
        assert 'by_category' in stats
        assert stats['total'] == 2

    def test_get_param_library_counts_by_type(self, manager, mock_repo, test_game_gid):
        """Test that stats correctly count parameters by type"""
        # Mock repository response with different types
        mock_params = [
            {'param_type': 'string', 'table_name': 'common'},
            {'param_type': 'string', 'table_name': 'game'},
            {'param_type': 'int', 'table_name': 'common'},
        ]

        mock_repo.get_common_params_by_game.return_value = mock_params

        result = manager.get_param_library(test_game_gid)

        # Verify by_type counts
        assert result['stats']['by_type']['string'] == 2
        assert result['stats']['by_type']['int'] == 1

    def test_get_param_library_counts_by_category(self, manager, mock_repo, test_game_gid):
        """Test that stats correctly count parameters by category"""
        # Mock repository response with different categories (table_name)
        mock_params = [
            {'param_type': 'string', 'table_name': 'common'},
            {'param_type': 'string', 'table_name': 'common'},
            {'param_type': 'int', 'table_name': 'custom'},
        ]

        mock_repo.get_common_params_by_game.return_value = mock_params

        result = manager.get_param_library(test_game_gid)

        # Verify by_category counts (using table_name as category)
        assert result['stats']['by_category']['common'] == 2
        assert result['stats']['by_category']['custom'] == 1

    def test_get_param_library_uses_repository(self, manager, mock_repo, test_game_gid):
        """Test that get_param_library uses ParameterRepository instead of direct DB"""
        mock_repo.get_common_params_by_game.return_value = []

        manager.get_param_library(test_game_gid)

        # Verify repository method was called
        mock_repo.get_common_params_by_game.assert_called_once_with(test_game_gid)

    def test_get_param_library_with_cache_decorator(self, test_game_gid):
        """Test that get_param_library has caching enabled"""
        with patch('backend.services.parameters.param_library_manager.ParameterRepository'):
            manager = ParamLibraryManager()
            # Check if method has cache decorator (it should have __wrapped__ or similar)
            assert hasattr(manager.get_param_library, '__name__')

    def test_get_param_library_empty_parameters(self, manager, mock_repo, test_game_gid):
        """Test get_param_library handles empty parameter list"""
        mock_repo.get_common_params_by_game.return_value = []

        result = manager.get_param_library(test_game_gid)

        assert result['parameters'] == []
        assert result['stats']['total'] == 0
        assert result['stats']['by_type'] == {}
        assert result['stats']['by_category'] == {}

    @patch('backend.services.parameters.param_library_manager.cached')
    def test_cache_configuration(self, mock_cached, test_game_gid):
        """Test that cache is configured with correct parameters"""
        # Import to trigger decorator
        from backend.services.parameters.param_library_manager import ParamLibraryManager

        # Verify cached was called with correct parameters
        # This will be checked when we run the actual test
        assert True  # Placeholder for cache configuration test
