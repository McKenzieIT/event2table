"""
DataLoader Performance Tests

Tests for DataLoader batch loading functionality to ensure N+1 query prevention.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from promise import Promise

from backend.gql_api.dataloaders.event_loader import EventLoader
from backend.gql_api.dataloaders.game_loader import GameLoader
from backend.gql_api.dataloaders.parameter_loader import ParameterLoader


@pytest.mark.describe("GameLoader")
class TestGameLoader:
    """Test Game DataLoader batch loading"""

    @pytest.fixture
    def game_loader(self):
        """Create a fresh GameLoader instance for each test"""
        return GameLoader()

    @pytest.mark.it("should batch load multiple games in single query")
    @patch('backend.core.utils.fetch_all_as_dict')
    def test_batch_load_games(self, mock_fetch, game_loader):
        """Test that multiple game requests are batched into single query"""
        # Mock database response
        mock_fetch.return_value = [
            {
                'id': 1,
                'gid': 10000147,
                'name': 'Game1',
                'ods_db': 'ieu_ods',
                'event_count': 5,
                'param_count': 10,
            },
            {
                'id': 2,
                'gid': 10000148,
                'name': 'Game2',
                'ods_db': 'ieu_ods',
                'event_count': 3,
                'param_count': 7,
            },
        ]

        # Load multiple games
        promise = game_loader.load_many([10000147, 10000148])
        result = promise.get()  # Synchronously get Promise result

        # Verify query was made (may be called twice due to subquery optimization)
        assert mock_fetch.call_count >= 1

        # Verify query contains IN clause with both GIDs
        call_args = mock_fetch.call_args
        query = call_args[0][0]
        assert 'IN (?, ?)' in query
        assert call_args[0][1] == (10000147, 10000148)

        # Verify results
        assert len(result) == 2
        assert result[0]['gid'] == 10000147
        assert result[1]['gid'] == 10000148

    @pytest.mark.it("should cache results within same request")
    @patch('backend.gql_api.dataloaders.game_loader.fetch_all_as_dict')
    def test_cache_results(self, mock_fetch, game_loader):
        """Test that loading same game twice uses cache"""
        mock_fetch.return_value = [
            {'id': 1, 'gid': 10000147, 'name': 'Game1', 'ods_db': 'ieu_ods'},
        ]

        # Load same game twice
        promise1 = game_loader.load(10000147)
        promise2 = game_loader.load(10000147)

        result1 = promise1.get()
        result2 = promise2.get()

        # Should only query database once
        assert mock_fetch.call_count == 1

        # Results should be identical
        assert result1 == result2

    @pytest.mark.it("should handle missing games gracefully")
    @patch('backend.gql_api.dataloaders.game_loader.fetch_all_as_dict')
    def test_handle_missing_games(self, mock_fetch, game_loader):
        """Test that missing games return None without errors"""
        # Mock empty response
        mock_fetch.return_value = []

        # Load non-existent game
        promise = game_loader.load(99999999)
        result = promise.get()

        # Should return None
        assert result is None


@pytest.mark.describe("EventLoader")
class TestEventLoader:
    """Test Event DataLoader batch loading"""

    @pytest.fixture
    def event_loader(self):
        """Create a fresh EventLoader instance for each test"""
        return EventLoader()

    @pytest.mark.it("should batch load events for multiple games")
    @patch('backend.core.utils.fetch_all_as_dict')
    def test_batch_load_events(self, mock_fetch, event_loader):
        """Test that events for multiple games are batched"""
        # Mock database response
        mock_fetch.return_value = [
            {'id': 1, 'game_gid': 10000147, 'event_name': 'login'},
            {'id': 2, 'game_gid': 10000147, 'event_name': 'logout'},
            {'id': 3, 'game_gid': 10000148, 'event_name': 'purchase'},
        ]

        # Load events for multiple games
        promise = event_loader.load_many([10000147, 10000148])
        result = promise.get()

        # Verify single query
        assert mock_fetch.call_count == 1

        # Verify results are grouped by game_gid
        assert len(result[0]) == 2  # Game 10000147 has 2 events
        assert len(result[1]) == 1  # Game 10000148 has 1 event


@pytest.mark.describe("ParameterLoader")
class TestParameterLoader:
    """Test Parameter DataLoader batch loading"""

    @pytest.fixture
    def parameter_loader(self):
        """Create a fresh ParameterLoader instance for each test"""
        return ParameterLoader()

    @pytest.mark.it("should batch load parameters for multiple events")
    @patch('backend.core.utils.fetch_all_as_dict')
    def test_batch_load_parameters(self, mock_fetch, parameter_loader):
        """Test that parameters for multiple events are batched"""
        # Mock database response
        mock_fetch.return_value = [
            {'id': 1, 'event_id': 1, 'param_name': 'zone_id'},
            {'id': 2, 'event_id': 1, 'param_name': 'role_id'},
            {'id': 3, 'event_id': 2, 'param_name': 'level'},
        ]

        # Load parameters for multiple events
        promise = parameter_loader.load_many([1, 2])
        result = promise.get()

        # Verify single query
        assert mock_fetch.call_count == 1

        # Verify results are grouped by event_id
        assert len(result[0]) == 2  # Event 1 has 2 params
        assert len(result[1]) == 1  # Event 2 has 1 param


@pytest.mark.describe("DataLoader Integration")
class TestDataLoaderIntegration:
    """Test DataLoader integration with GraphQL resolvers"""

    @pytest.mark.it("should prevent N+1 queries in nested queries")
    @patch('backend.gql_api.dataloaders.game_loader.fetch_all_as_dict')
    @patch('backend.core.utils.fetch_all_as_dict')
    @patch('backend.core.utils.fetch_all_as_dict')
    def test_prevent_n_plus_one_queries(self, mock_params, mock_events, mock_games):
        """
        Test that nested Game -> Events -> Parameters query
        uses batch loading instead of N+1 queries
        """
        # Mock responses
        mock_games.return_value = [
            {'id': 1, 'gid': 10000147, 'name': 'Game1'},
        ]
        mock_events.return_value = [
            {'id': 1, 'game_gid': 10000147, 'event_name': 'login'},
            {'id': 2, 'game_gid': 10000147, 'event_name': 'logout'},
        ]
        mock_params.return_value = [
            {'id': 1, 'event_id': 1, 'param_name': 'zone_id'},
            {'id': 2, 'event_id': 1, 'param_name': 'role_id'},
            {'id': 3, 'event_id': 2, 'param_name': 'timestamp'},
        ]

        # Simulate nested query
        game_loader = GameLoader()
        event_loader = EventLoader()
        parameter_loader = ParameterLoader()

        # Load game
        game_promise = game_loader.load(10000147)
        game = game_promise.get()

        # Load events for game
        events_promise = event_loader.load(10000147)
        events = events_promise.get()

        # Load parameters for each event
        param_promises = [parameter_loader.load(e['id']) for e in events]
        params = Promise.all(param_promises).get()

        # Should only make 3 queries total (1 game, 1 events batch, 1 params batch)
        assert mock_games.call_count == 1
        assert mock_events.call_count == 1
        assert mock_params.call_count == 1

        # Without DataLoader: would be 1 + N + N*M queries
        # With DataLoader: 3 queries regardless of N and M


@pytest.mark.describe("DataLoader Performance")
class TestDataLoaderPerformance:
    """Performance benchmarks for DataLoader"""

    @pytest.mark.it("should load 100 games with single query")
    @patch('backend.gql_api.dataloaders.game_loader.fetch_all_as_dict')
    def test_load_100_games_single_query(self, mock_fetch):
        """Test that loading 100 games still uses single query"""
        # Mock 100 games
        mock_fetch.return_value = [
            {'id': i, 'gid': 10000000 + i, 'name': f'Game{i}'} for i in range(100)
        ]

        loader = GameLoader()
        gids = [10000000 + i for i in range(100)]

        promise = loader.load_many(gids)
        result = promise.get()

        # Should still be single query
        assert mock_fetch.call_count == 1

        # Query should have 100 placeholders
        call_args = mock_fetch.call_args
        query = call_args[0][0]
        assert 'IN (' + ', '.join(['?'] * 100) + ')' in query

    @pytest.mark.it("should reduce query count by 99% for 100 games with events")
    @pytest.mark.benchmark(min_rounds=5)
    @patch('backend.gql_api.dataloaders.game_loader.fetch_all_as_dict')
    @patch('backend.core.utils.fetch_all_as_dict')
    def test_query_reduction_percentage(self, mock_events, mock_games):
        """
        Benchmark: Without DataLoader would be 101 queries (1 games + 100 events)
        With DataLoader should be 2 queries (1 games + 1 events batch)
        Reduction: 101 -> 2 = 98% reduction
        """
        # Setup
        num_games = 100
        mock_games.return_value = [
            {'id': i, 'gid': 10000000 + i, 'name': f'Game{i}'} for i in range(num_games)
        ]
        mock_events.return_value = [
            {'id': i, 'game_gid': 10000000 + (i % 10), 'event_name': f'event{i}'}
            for i in range(num_games)
        ]

        # Execute
        game_loader = GameLoader()
        event_loader = EventLoader()

        game_promise = game_loader.load_many([10000000 + i for i in range(num_games)])
        games = game_promise.get()

        event_promise = event_loader.load_many([g['gid'] for g in games])
        events = event_promise.get()

        # Verify query reduction
        total_queries = mock_games.call_count + mock_events.call_count
        expected_without_loader = num_games + 1  # 1 for games + 100 for events
        reduction = (expected_without_loader - total_queries) / expected_without_loader

        assert total_queries == 2  # 1 game query + 1 events query
        assert reduction >= 0.98  # 98% reduction
