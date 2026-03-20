#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Tests: Events API Pagination

Tests the pagination functionality of the Events API endpoint:
- GET /api/events with pagination parameters
- Pagination metadata calculation
- Edge cases (empty pages, overflow)
- Search + pagination combination
"""

import pytest
from typing import List, Dict


class TestEventsPagination:
    """Test suite for Events API pagination"""

    def test_pagination_default_parameters(self, client, test_game, test_events):
        """
        Test pagination with default parameters

        Given: A game with multiple events
        When: Calling GET /api/events without pagination parameters
        Then: Should return first page with default page_size (20)
        """
        response = client.get(f"/api/events?game_gid={test_game['gid']}")

        assert response.status_code == 200
        data = response.get_json()

        assert "success" in data
        assert data["success"] is True
        assert "data" in data

        # Check pagination structure
        result = data["data"]
        assert "events" in result
        assert "pagination" in result

        pagination = result["pagination"]
        assert pagination["page"] == 1
        assert pagination["per_page"] == 20
        assert "total" in pagination
        assert "total_pages" in pagination
        assert pagination["total"] >= len(test_events)

    def test_pagination_custom_page_size(self, client, test_game, test_events):
        """
        Test pagination with custom page_size

        Given: A game with multiple events
        When: Calling GET /api/events with per_page=5
        Then: Should return at most 5 events
        """
        per_page = 5
        response = client.get(f"/api/events?game_gid={test_game['gid']}&per_page={per_page}")

        assert response.status_code == 200
        data = response.get_json()

        events = data["data"]["events"]
        pagination = data["data"]["pagination"]

        assert len(events) <= per_page
        assert pagination["per_page"] == per_page
        assert pagination["page"] == 1

    def test_pagination_page_navigation(self, client, test_game, test_events):
        """
        Test pagination page navigation

        Given: A game with multiple events (enough for multiple pages)
        When: Calling GET /api/events with page=1 and page=2
        Then: Should return different events for each page
        """
        per_page = 3

        # Get page 1
        response_page1 = client.get(
            f"/api/events?game_gid={test_game['gid']}&page=1&per_page={per_page}"
        )
        assert response_page1.status_code == 200
        data_page1 = response_page1.get_json()
        events_page1 = data_page1["data"]["events"]

        # Get page 2
        response_page2 = client.get(
            f"/api/events?game_gid={test_game['gid']}&page=2&per_page={per_page}"
        )
        assert response_page2.status_code == 200
        data_page2 = response_page2.get_json()
        events_page2 = data_page2["data"]["events"]

        # Verify different content (if there are enough events)
        if len(events_page1) == per_page and len(events_page2) > 0:
            # Extract event IDs
            ids_page1 = {e["id"] for e in events_page1}
            ids_page2 = {e["id"] for e in events_page2}
            # Pages should have different events
            assert ids_page1.isdisjoint(ids_page2), "Pages should contain different events"

    def test_pagination_total_pages_calculation(self, client, test_game, test_events):
        """
        Test total_pages calculation

        Given: A game with known number of events
        When: Calling GET /api/events with specific per_page
        Then: Should calculate total_pages correctly
        """
        per_page = 3

        response = client.get(f"/api/events?game_gid={test_game['gid']}&per_page={per_page}")
        assert response.status_code == 200

        data = response.get_json()
        pagination = data["data"]["pagination"]

        total = pagination["total"]
        total_pages = pagination["total_pages"]

        # Verify total_pages calculation: ceil(total / per_page)
        expected_total_pages = (total + per_page - 1) // per_page
        assert total_pages == expected_total_pages

    def test_pagination_beyond_last_page(self, client, test_game, test_events):
        """
        Test requesting page beyond available pages

        Given: A game with limited events
        When: Calling GET /api/events with page=999
        Then: Should return empty event list but valid pagination metadata
        """
        response = client.get(f"/api/events?game_gid={test_game['gid']}&page=999&per_page=10")

        assert response.status_code == 200
        data = response.get_json()

        events = data["data"]["events"]
        pagination = data["data"]["pagination"]

        # Should return empty list
        assert len(events) == 0
        # Pagination metadata should still be valid
        assert pagination["page"] == 999
        assert pagination["total"] > 0

    def test_pagination_with_search(self, client, test_game, test_events):
        """
        Test pagination combined with search

        Given: A game with multiple events
        When: Calling GET /api/events with search and pagination
        Then: Should return filtered results with correct pagination
        """
        # Create a search term that matches some events
        search_term = test_events[0]["event_name"][:3].lower()  # First 3 chars

        response = client.get(
            f"/api/events?game_gid={test_game['gid']}&search={search_term}&per_page=2"
        )

        assert response.status_code == 200
        data = response.get_json()

        events = data["data"]["events"]
        pagination = data["data"]["pagination"]

        # Verify all events match search term
        for event in events:
            assert (
                search_term in event["event_name"].lower()
                or search_term in event["event_name_cn"].lower()
            ), "All events should match search term"

        # Verify pagination
        assert len(events) <= 2
        assert pagination["per_page"] == 2

    def test_pagination_max_page_size_limit(self, client, test_game):
        """
        Test that per_page is capped at 100

        Given: A game with events
        When: Calling GET /api/events with per_page=200
        Then: Should cap per_page at 100
        """
        response = client.get(f"/api/events?game_gid={test_game['gid']}&per_page=200")

        assert response.status_code == 200
        data = response.get_json()

        pagination = data["data"]["pagination"]
        assert pagination["per_page"] == 100, "per_page should be capped at 100"

    def test_pagination_invalid_page_numbers(self, client, test_game):
        """
        Test pagination with invalid page numbers

        Given: A game with events
        When: Calling GET /api/events with page=0 or page=-1
        Then: Should default to page=1
        """
        # Test page=0
        response = client.get(f"/api/events?game_gid={test_game['gid']}&page=0")
        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["pagination"]["page"] == 1

        # Test page=-1
        response = client.get(f"/api/events?game_gid={test_game['gid']}&page=-1")
        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["pagination"]["page"] == 1

    def test_pagination_response_structure(self, client, test_game):
        """
        Test pagination response structure matches API contract

        Given: A game with events
        When: Calling GET /api/events
        Then: Response should match expected structure
        """
        response = client.get(f"/api/events?game_gid={test_game['gid']}")

        assert response.status_code == 200
        data = response.get_json()

        # Verify top-level structure
        assert "success" in data
        assert "data" in data
        assert data["success"] is True

        # Verify events structure
        events = data["data"]["events"]
        if events:  # If there are events
            event = events[0]
            required_fields = [
                "id",
                "game_gid",
                "event_name",
                "event_name_cn",
                "category_id",
                "created_at",
                "updated_at",
            ]
            for field in required_fields:
                assert field in event, f"Event should have field: {field}"

        # Verify pagination structure
        pagination = data["data"]["pagination"]
        required_pagination_fields = ["page", "per_page", "total", "total_pages"]
        for field in required_pagination_fields:
            assert field in pagination, f"Pagination should have field: {field}"

    def test_events_count_endpoint(self, client, test_game, test_events):
        """
        Test GET /api/events/count endpoint

        Given: A game with events
        When: Calling GET /api/events/count
        Then: Should return correct count
        """
        response = client.get(f"/api/events/count?game_gid={test_game['gid']}")

        assert response.status_code == 200
        data = response.get_json()

        assert "success" in data
        assert data["success"] is True
        assert "data" in data
        assert "total" in data["data"]
        assert data["data"]["total"] >= len(test_events)

    def test_events_count_with_search(self, client, test_game, test_events):
        """
        Test GET /api/events/count with search parameter

        Given: A game with events
        When: Calling GET /api/events/count with search
        Then: Should return filtered count
        """
        search_term = test_events[0]["event_name"][:3].lower()

        response = client.get(f"/api/events/count?game_gid={test_game['gid']}&search={search_term}")

        assert response.status_code == 200
        data = response.get_json()

        total = data["data"]["total"]
        # Total should be less than or equal to total events
        assert total <= len(test_events)

    def test_pagination_without_game_gid(self, client, test_events):
        """
        Test pagination without game_gid filter (returns all events)

        Given: Multiple games with events
        When: Calling GET /api/events without game_gid
        Then: Should return events from all games with pagination
        """
        response = client.get("/api/events?page=1&per_page=10")

        assert response.status_code == 200
        data = response.get_json()

        events = data["data"]["events"]
        pagination = data["data"]["pagination"]

        # Should return events
        assert len(events) >= 0
        # Pagination should be valid
        assert pagination["page"] == 1
        assert pagination["per_page"] == 10

    def test_pagination_with_both_filters(self, client, test_game, test_events):
        """
        Test pagination with both game_gid and search filters

        Given: A game with multiple events
        When: Calling GET /api/events with game_gid and search
        Then: Should return filtered and paginated results
        """
        search_term = "test"

        response = client.get(
            f"/api/events?game_gid={test_game['gid']}&search={search_term}&page=1&per_page=5"
        )

        assert response.status_code == 200
        data = response.get_json()

        events = data["data"]["events"]
        pagination = data["data"]["pagination"]

        # Verify filters applied
        for event in events:
            assert event["game_gid"] == test_game["gid"]
            assert (
                search_term in event["event_name"].lower()
                or search_term in event["event_name_cn"].lower()
            )

        # Verify pagination
        assert len(events) <= 5
        assert pagination["page"] == 1


@pytest.fixture
def test_game(client):
    """Create a test game"""
    response = client.post(
        "/api/games",
        json={
            "gid": "99999999",
            "name": "Test Game Pagination",
            "ods_db": "ieu_ods",
        },
    )
    assert response.status_code == 200
    return response.get_json()["data"]


@pytest.fixture
def test_events(client, test_game):
    """Create multiple test events for pagination testing"""
    events = []
    for i in range(10):
        response = client.post(
            "/api/events",
            json={
                "game_gid": test_game["gid"],
                "event_name": f"test_event_{i}",
                "event_name_cn": f"测试事件_{i}",
                "param_names": ["param1", "param2"],
                "param_names_cn": ["参数1", "参数2"],
                "param_types": [1, 1],
            },
        )
        assert response.status_code == 200
        events.append(response.get_json()["data"])

    return events
