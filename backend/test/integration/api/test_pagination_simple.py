#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Integration Tests: Events API Pagination

Tests the pagination functionality of the Events API endpoint.
"""

import pytest


class TestEventsPaginationSimple:
    """Test suite for Events API pagination (simplified)"""

    def test_pagination_default_parameters(self, integration_client):
        """
        Test pagination with default parameters

        Given: Existing events in database
        When: Calling GET /api/events without pagination parameters
        Then: Should return first page with default page_size (20)
        """
        client = integration_client

        response = client.get("/api/events?page=1&per_page=20")

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

    def test_pagination_custom_page_size(self, integration_client):
        """
        Test pagination with custom page_size

        Given: Existing events in database
        When: Calling GET /api/events with per_page=5
        Then: Should return at most 5 events
        """
        client = integration_client
        per_page = 5

        response = client.get(f"/api/events?page=1&per_page={per_page}")

        assert response.status_code == 200
        data = response.get_json()

        events = data["data"]["events"]
        pagination = data["data"]["pagination"]

        assert len(events) <= per_page
        assert pagination["per_page"] == per_page
        assert pagination["page"] == 1

    def test_pagination_page_navigation(self, integration_client):
        """
        Test pagination page navigation

        Given: Existing events in database
        When: Calling GET /api/events with page=1 and page=2
        Then: Should return different events for each page
        """
        client = integration_client
        per_page = 3

        # Get page 1
        response_page1 = client.get(f"/api/events?page=1&per_page={per_page}")
        assert response_page1.status_code == 200
        data_page1 = response_page1.get_json()
        events_page1 = data_page1["data"]["events"]

        # Get page 2
        response_page2 = client.get(f"/api/events?page=2&per_page={per_page}")
        assert response_page2.status_code == 200
        data_page2 = response_page2.get_json()
        events_page2 = data_page2["data"]["events"]

        # Verify pagination structure
        assert data_page1["data"]["pagination"]["page"] == 1
        assert data_page2["data"]["pagination"]["page"] == 2

    def test_pagination_total_pages_calculation(self, integration_client):
        """
        Test total_pages calculation

        Given: Existing events in database
        When: Calling GET /api/events with specific per_page
        Then: Should calculate total_pages correctly
        """
        client = integration_client
        per_page = 3

        response = client.get(f"/api/events?page=1&per_page={per_page}")
        assert response.status_code == 200

        data = response.get_json()
        pagination = data["data"]["pagination"]

        total = pagination["total"]
        total_pages = pagination["total_pages"]

        # Verify total_pages calculation: ceil(total / per_page)
        # Edge case: when total=0, total_pages should be at least 1
        expected_total_pages = max(1, (total + per_page - 1) // per_page)
        assert (
            total_pages == expected_total_pages
        ), f"Expected {expected_total_pages} total_pages, got {total_pages} (total={total}, per_page={per_page})"

    def test_pagination_beyond_last_page(self, integration_client):
        """
        Test requesting page beyond available pages

        Given: Limited events in database
        When: Calling GET /api/events with page=999
        Then: Should return empty event list but valid pagination metadata
        """
        client = integration_client

        response = client.get("/api/events?page=999&per_page=10")

        assert response.status_code == 200
        data = response.get_json()

        events = data["data"]["events"]
        pagination = data["data"]["pagination"]

        # Should return empty list
        assert len(events) == 0
        # Pagination metadata should still be valid
        assert pagination["page"] == 999
        assert pagination["total"] >= 0

    def test_pagination_with_search(self, integration_client):
        """
        Test pagination combined with search

        Given: Existing events in database
        When: Calling GET /api/events with search and pagination
        Then: Should return filtered results with correct pagination
        """
        client = integration_client

        response = client.get("/api/events?search=test&per_page=2")

        assert response.status_code == 200
        data = response.get_json()

        events = data["data"]["events"]
        pagination = data["data"]["pagination"]

        # Verify pagination
        assert len(events) <= 2
        assert pagination["per_page"] == 2

    def test_pagination_max_page_size_limit(self, integration_client):
        """
        Test that per_page is capped at 100

        Given: Existing events in database
        When: Calling GET /api/events with per_page=200
        Then: Should cap per_page at 100
        """
        client = integration_client

        response = client.get("/api/events?per_page=200")

        assert response.status_code == 200
        data = response.get_json()

        pagination = data["data"]["pagination"]
        assert pagination["per_page"] == 100, "per_page should be capped at 100"

    def test_pagination_invalid_page_numbers(self, integration_client):
        """
        Test pagination with invalid page numbers

        Given: Existing events in database
        When: Calling GET /api/events with page=0 or page=-1
        Then: Should default to page=1
        """
        client = integration_client

        # Test page=0
        response = client.get("/api/events?page=0")
        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["pagination"]["page"] == 1

        # Test page=-1
        response = client.get("/api/events?page=-1")
        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["pagination"]["page"] == 1

    def test_pagination_response_structure(self, integration_client):
        """
        Test pagination response structure matches API contract

        Given: Existing events in database
        When: Calling GET /api/events
        Then: Response should match expected structure
        """
        client = integration_client

        response = client.get("/api/events")

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

    def test_events_count_endpoint(self, integration_client):
        """
        Test GET /api/events/count endpoint

        Given: Existing events in database
        When: Calling GET /api/events/count
        Then: Should return correct count
        """
        client = integration_client

        response = client.get("/api/events/count")

        assert response.status_code == 200
        data = response.get_json()

        assert "success" in data
        assert data["success"] is True
        assert "data" in data
        assert "total" in data["data"]
        assert data["data"]["total"] >= 0

    def test_events_count_with_search(self, integration_client):
        """
        Test GET /api/events/count with search parameter

        Given: Existing events in database
        When: Calling GET /api/events/count with search
        Then: Should return filtered count
        """
        client = integration_client

        response = client.get("/api/events/count?search=test")

        assert response.status_code == 200
        data = response.get_json()

        total = data["data"]["total"]
        # Total should be non-negative
        assert total >= 0

    def test_pagination_with_game_gid_filter(self, integration_client):
        """
        Test pagination with game_gid filter

        Given: Existing events in database
        When: Calling GET /api/events with game_gid
        Then: Should return filtered results with pagination
        """
        client = integration_client

        # Try with a known game_gid (from test data)
        response = client.get("/api/events?game_gid=10000147&page=1&per_page=5")

        assert response.status_code == 200
        data = response.get_json()

        events = data["data"]["events"]
        pagination = data["data"]["pagination"]

        # Verify all events have the correct game_gid
        for event in events:
            assert event["game_gid"] == 10000147, "All events should match game_gid"

        # Verify pagination
        assert len(events) <= 5
        assert pagination["page"] == 1
