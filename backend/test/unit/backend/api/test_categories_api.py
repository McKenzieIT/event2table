"""
Unit Tests for Categories API

This test module verifies that the categories API enforces game_gid parameter
requirement and correctly filters categories by game.

TDD Phase: RED - Tests are written first to specify expected behavior
"""

import os
import sys

import pytest


def test_get_categories_requires_game_gid(client):
    """
    Test: GET /api/categories without game_gid should return 400 error

    Expected behavior:
    - API returns 400 status code
    - Error message indicates game_gid is required
    """
    response = client.get('/api/categories')

    # Should return 400 Bad Request
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    # Should have error message
    data = response.get_json()
    assert 'error' in data, "Response should contain 'error' field"
    assert 'game_gid' in data['error'].lower(), "Error message should mention 'game_gid'"


def test_get_categories_with_valid_game_gid(client, db):
    """
    Test: GET /api/categories?game_gid=10000147 returns game-specific categories

    Expected behavior:
    - API returns 200 status code
    - Only categories with events from game 10000147 are returned
    - Event counts only include events from game 10000147
    """
    # 准备测试数据
    game = db.execute('SELECT * FROM games WHERE gid = ?', (10000147,)).fetchone()
    if not game:
        cursor = db.execute(
            'INSERT INTO games (gid, name, ods_db) VALUES (?, ?, ?)',
            (10000147, '测试游戏', 'ieu_ods'),
        )
        db.commit()

    response = client.get('/api/categories?game_gid=10000147')

    # Should return 200 OK
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Should have data field
    data = response.get_json()
    assert 'data' in data, "Response should contain 'data' field"
    assert isinstance(data['data'], list), "Data should be a list"


def test_get_categories_with_nonexistent_game_gid(client):
    """
    Test: GET /api/categories?game_gid=99999999 for nonexistent game

    Expected behavior:
    - API returns 404 Not Found or 200 OK with empty list
    """
    response = client.get('/api/categories?game_gid=99999999')

    # Should return 404 or 200 with empty list
    assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}"

    if response.status_code == 200:
        data = response.get_json()
        assert 'data' in data
        assert isinstance(data['data'], list)


def test_get_categories_with_invalid_game_gid_format(client):
    """
    Test: GET /api/categories?game_gid=invalid with invalid format

    Expected behavior:
    - API returns 400 Bad Request
    - Error message indicates invalid format
    """
    response = client.get('/api/categories?game_gid=invalid')

    # Should return 400 Bad Request
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    data = response.get_json()
    assert 'error' in data, "Response should contain 'error' field"


def test_get_categories_event_counts_filtered_by_game(client, db):
    """
    Test: Categories event counts are filtered by game_gid

    Expected behavior:
    - Each category includes event_count field
    - event_count only includes events from the specified game
    """
    # 准备测试数据
    game = db.execute('SELECT * FROM games WHERE gid = ?', (10000147,)).fetchone()
    if not game:
        cursor = db.execute(
            'INSERT INTO games (gid, name, ods_db) VALUES (?, ?, ?)',
            (10000147, '测试游戏', 'ieu_ods'),
        )
        db.commit()

    response = client.get('/api/categories?game_gid=10000147')

    # Should return 200 OK
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.get_json()
    assert 'data' in data, "Response should contain 'data' field"

    # If categories exist, verify event_count field
    if data['data']:
        for category in data['data']:
            assert 'event_count' in category, "Each category should have 'event_count' field"
            assert isinstance(category['event_count'], int), "event_count should be an integer"
