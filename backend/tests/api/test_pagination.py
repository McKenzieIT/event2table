"""
Pagination API Tests

Tests for pagination functionality across different endpoints.
"""

import pytest


class TestEventsPagination:
    """Test events pagination functionality"""

    def test_pagination_default_parameters(self, client, test_game_with_events):
        """Test pagination with default parameters"""
        game_gid = test_game_with_events['game_gid']

        response = client.get(f'/api/events?game_gid={game_gid}')

        assert response.status_code == 200
        data = response.json
        assert 'data' in data
        assert 'pagination' in data['data']

        pagination = data['data']['pagination']
        assert 'page' in pagination
        assert 'per_page' in pagination
        assert 'total' in pagination
        assert 'total_pages' in pagination

    def test_pagination_custom_page_size(self, client, test_game_with_events):
        """Test pagination with custom page size"""
        game_gid = test_game_with_events['game_gid']

        response = client.get(f'/api/events?game_gid={game_gid}&per_page=10')

        assert response.status_code == 200
        data = response.json
        pagination = data['data']['pagination']

        assert pagination['per_page'] == 10

    def test_pagination_page_navigation(self, client, test_game_with_events):
        """Test pagination with page navigation"""
        game_gid = test_game_with_events['game_gid']

        # Get first page
        response1 = client.get(f'/api/events?game_gid={game_gid}&page=1')
        assert response1.status_code == 200

        # Get second page
        response2 = client.get(f'/api/events?game_gid={game_gid}&page=2')
        assert response2.status_code == 200

        data1 = response1.json['data']
        data2 = response2.json['data']

        assert data1['pagination']['page'] == 1
        assert data2['pagination']['page'] == 2

    def test_pagination_total_pages_calculation(self, client, test_game_with_events):
        """Test total pages calculation"""
        game_gid = test_game_with_events['game_gid']
        event_count = len(test_game_with_events['events'])

        response = client.get(f'/api/events?game_gid={game_gid}&per_page=2')

        assert response.status_code == 200
        data = response.json
        pagination = data['data']['pagination']

        expected_total_pages = (event_count + 1) // 2  # Ceiling division
        assert pagination['total_pages'] == expected_total_pages

    def test_pagination_beyond_last_page(self, client, test_game_with_events):
        """Test requesting page beyond available pages"""
        game_gid = test_game_with_events['game_gid']

        response = client.get(f'/api/events?game_gid={game_gid}&page=999')

        assert response.status_code == 200
        data = response.json
        pagination = data['data']['pagination']

        # Should return empty results
        assert len(data['data']['items']) == 0

    def test_pagination_with_search(self, client, test_game_with_events):
        """Test pagination combined with search"""
        game_gid = test_game_with_events['game_gid']

        response = client.get(f'/api/events?game_gid={game_gid}&search=test')

        assert response.status_code == 200
        data = response.json

        # Should have pagination info even with search
        assert 'pagination' in data['data']

    def test_pagination_max_page_size_limit(self, client, test_game_with_events):
        """Test that page size is capped at maximum limit"""
        game_gid = test_game_with_events['game_gid']

        # Request page size larger than maximum
        response = client.get(f'/api/events?game_gid={game_gid}&per_page=1000')

        assert response.status_code == 200
        data = response.json
        pagination = data['data']['pagination']

        # Should be capped at 100 (or configured max)
        assert pagination['per_page'] <= 100

    def test_pagination_invalid_page_numbers(self, client, test_game_with_events):
        """Test pagination with invalid page numbers"""
        game_gid = test_game_with_events['game_gid']

        # Test page 0
        response = client.get(f'/api/events?game_gid={game_gid}&page=0')
        assert response.status_code == 200

        # Test negative page
        response = client.get(f'/api/events?game_gid={game_gid}&page=-1')
        assert response.status_code == 200

    def test_pagination_response_structure(self, client, test_game_with_events):
        """Test pagination response structure"""
        game_gid = test_game_with_events['game_gid']

        response = client.get(f'/api/events?game_gid={game_gid}')

        assert response.status_code == 200
        data = response.json

        # Verify response structure
        assert 'success' in data
        assert 'data' in data
        assert 'items' in data['data']
        assert 'pagination' in data['data']

        pagination = data['data']['pagination']
        required_fields = ['page', 'per_page', 'total', 'total_pages', 'has_next', 'has_prev']
        for field in required_fields:
            assert field in pagination

    def test_events_count_endpoint(self, client, test_game_with_events):
        """Test events count endpoint"""
        game_gid = test_game_with_events['game_gid']
        expected_count = len(test_game_with_events['events'])

        response = client.get(f'/api/events/count?game_gid={game_gid}')

        assert response.status_code == 200
        data = response.json

        assert 'data' in data
        assert 'count' in data['data']
        assert data['data']['count'] == expected_count

    def test_events_count_with_search(self, client, test_game_with_events):
        """Test events count endpoint with search filter"""
        game_gid = test_game_with_events['game_gid']

        response = client.get(f'/api/events/count?game_gid={game_gid}&search=test')

        assert response.status_code == 200
        data = response.json

        assert 'data' in data
        assert 'count' in data['data']

    def test_pagination_without_game_gid(self, client):
        """Test pagination without game_gid (should fail or return empty)"""
        response = client.get('/api/events')

        # Should either fail or return empty results
        assert response.status_code in [200, 400, 404]

    def test_pagination_with_both_filters(self, client, test_game_with_events):
        """Test pagination with multiple filters combined"""
        game_gid = test_game_with_events['game_gid']

        response = client.get(f'/api/events?game_gid={game_gid}&search=test&page=1&per_page=5')

        assert response.status_code == 200
        data = response.json

        # Should have pagination info
        assert 'pagination' in data['data']

        # Should respect page size
        pagination = data['data']['pagination']
        assert pagination['per_page'] == 5


class TestPaginationEdgeCases:
    """Test pagination edge cases"""

    def test_pagination_empty_results(self, client):
        """Test pagination when no results exist"""
        # Use a non-existent game
        response = client.get('/api/events?game_gid=999999')

        assert response.status_code == 200
        data = response.json

        # Should return empty results with pagination info
        assert 'data' in data
        assert 'pagination' in data['data']
        assert len(data['data']['items']) == 0

    def test_pagination_single_result(self, client, test_game):
        """Test pagination with single result"""
        # Create a single event
        client.post(
            '/api/events',
            json={
                'game_gid': test_game,
                'name': 'Single Event',
                'name_cn': '单个事件',
                'ods_table': 'ods_single_event',
            },
        )

        response = client.get(f'/api/events?game_gid={test_game}')

        assert response.status_code == 200
        data = response.json

        assert len(data['data']['items']) >= 1
        assert data['data']['pagination']['total'] >= 1
