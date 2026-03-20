#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test batch delete categories endpoint

Tests:
1. Batch delete multiple existing categories
2. Batch delete with non-existent IDs
3. Batch delete with empty list
4. Batch delete categories with events (foreign key constraint)
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from backend.core.utils import execute_write
from backend.core.utils.converters import fetch_all_as_dict, fetch_one_as_dict


@pytest.fixture
def client():
    """Create Flask test client"""
    from web_app import app

    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


@pytest.fixture(scope="module")
def db():
    """Setup test database"""
    from backend.core.config.config import TEST_DB_PATH, init_db

    # Initialize test database
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    init_db(TEST_DB_PATH)

    yield

    # Cleanup
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest.fixture
def test_categories(db):
    """Create test categories"""
    # Create 5 test categories
    category_ids = []
    for i in range(1, 6):
        result = execute_write(
            "INSERT INTO event_categories (name) VALUES (?)", (f"Test Category {i}",)
        )
        category_ids.append(result)

    # Create some events linked to category 3
    execute_write(
        """INSERT INTO log_events (name, game_gid, category_id)
           VALUES (?, ?, ?)""",
        ("Test Event", 90000001, 3),
    )

    yield category_ids

    # Cleanup
    execute_write("DELETE FROM log_events WHERE name = 'Test Event'")
    execute_write(f"DELETE FROM event_categories WHERE id IN ({','.join(map(str, category_ids))})")


def test_batch_delete_success(test_categories):
    """Test batch delete multiple categories"""
    from backend.services.event_categories.category_service import CategoryService

    service = CategoryService()

    # Delete categories 1, 2, 4, 5 (skip 3 which has events)
    result = service.batch_delete_categories([1, 2, 4, 5])

    assert result["deleted_count"] == 4
    assert len(result["failed_ids"]) == 0
    assert "Successfully deleted all 4 categories" in result["message"]


def test_batch_delete_with_events(test_categories):
    """Test batch delete with foreign key constraint"""
    from backend.services.event_categories.category_service import CategoryService

    service = CategoryService()

    # Try to delete category 3 (has events)
    result = service.batch_delete_categories([3])

    assert result["deleted_count"] == 0
    assert len(result["failed_ids"]) == 1
    assert 3 in result["failed_ids"]
    assert "associated events" in result["failed_reasons"][3]


def test_batch_delete_mixed(test_categories):
    """Test batch delete with mixed valid and invalid IDs"""
    from backend.services.event_categories.category_service import CategoryService

    service = CategoryService()

    # Mix of valid and invalid IDs
    result = service.batch_delete_categories([1, 2, 3, 999, 1000])

    # 1, 2 should succeed, 3 should fail (has events), 999, 1000 not found
    assert result["deleted_count"] == 2
    assert len(result["failed_ids"]) == 3
    assert 3 in result["failed_ids"]
    assert 999 in result["failed_ids"]
    assert 1000 in result["failed_ids"]
    assert "Category not found" in result["failed_reasons"][999]


def test_batch_delete_empty_list():
    """Test batch delete with empty list"""
    from backend.services.event_categories.category_service import CategoryService

    service = CategoryService()

    result = service.batch_delete_categories([])

    assert result["deleted_count"] == 0
    assert len(result["failed_ids"]) == 0


def test_batch_delete_invalid_ids():
    """Test batch delete with invalid IDs"""
    from backend.services.event_categories.category_service import CategoryService

    service = CategoryService()

    with pytest.raises(ValueError, match="Invalid category_id"):
        service.batch_delete_categories([-1, 0, 999])


def test_api_batch_delete(test_categories, client):
    """Test API endpoint"""
    response = client.post(
        '/api/categories/batch-delete',
        json={"category_ids": [1, 2, 4, 5]},
        content_type='application/json',
    )

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    assert data["data"]["deleted_count"] == 4
    assert len(data["data"]["failed_ids"]) == 0


def test_api_batch_delete_with_events(test_categories, client):
    """Test API endpoint with foreign key constraint"""
    response = client.post(
        '/api/categories/batch-delete', json={"category_ids": [3]}, content_type='application/json'
    )

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    assert data["data"]["deleted_count"] == 0
    assert len(data["data"]["failed_ids"]) == 1
    assert 3 in data["data"]["failed_ids"]
    assert "associated events" in data["data"]["failed_reasons"][3]


def test_api_batch_delete_empty_request(client):
    """Test API endpoint with empty request"""
    response = client.post('/api/categories/batch-delete', json={}, content_type='application/json')

    assert response.status_code == 400


def test_api_batch_delete_too_many_ids(client):
    """Test API endpoint with too many IDs"""
    ids = list(range(1, 102))  # 101 IDs
    response = client.post(
        '/api/categories/batch-delete', json={"category_ids": ids}, content_type='application/json'
    )

    assert response.status_code == 400
    assert "Too many IDs" in response.get_json()["error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
