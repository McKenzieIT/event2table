#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Tests Configuration

Shared fixtures for integration tests
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


@pytest.fixture(scope="session")
def integration_client():
    """
    Fixture for integration tests that need a Flask test client

    This fixture uses the production database schema but should use
    test data to avoid polluting production data.
    """
    from web_app import app

    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="function")
def sample_game(integration_client):
    """
    Fixture providing a sample game for testing

    Returns the first game from the database or creates a test game
    """
    response = integration_client.get('/api/games')
    data = response.get_json()

    if data.get('data') and len(data['data']) > 0:
        return data['data'][0]

    # If no games exist, create one
    response = integration_client.post('/api/games', json={
        'gid': 999999,
        'name': 'Integration Test Game',
        'ods_db': 'ieu_ods'
    })

    if response.status_code == 200:
        return response.get_json()['data']

    return None
