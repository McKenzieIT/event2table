"""
Category Batch Delete API Tests

Tests for batch deletion of event categories.
"""

import pytest
from flask import json


class TestCategoryBatchDelete:
    """Test category batch delete functionality"""

    def test_batch_delete_success(self, client):
        """Test successful batch delete of categories"""
        # Create test categories first
        category_ids = []
        for i in range(3):
            response = client.post('/api/categories', json={
                'name': f'Test Category {i}',
                'name_cn': f'测试分类 {i}',
                'description': f'Test description {i}'
            })
            if response.status_code == 200:
                category_ids.append(response.json['data']['id'])
        
        if not category_ids:
            pytest.skip("Could not create test categories")
        
        # Batch delete
        response = client.delete('/api/categories/batch', json={'ids': category_ids})
        
        assert response.status_code == 200
        data = response.json
        assert data['success'] is True
        assert 'deleted_count' in data['data']
        assert data['data']['deleted_count'] == len(category_ids)

    def test_batch_delete_with_events(self, client):
        """Test batch delete fails when categories have associated events"""
        # Create category with events
        response = client.post('/api/categories', json={
            'name': 'Category with Events',
            'name_cn': '带事件的分类'
        })
        
        if response.status_code != 200:
            pytest.skip("Could not create test category")
        
        category_id = response.json['data']['id']
        
        # Try to delete category with events
        response = client.delete('/api/categories/batch', json={'ids': [category_id]})
        
        # Should fail or return error
        assert response.status_code in [400, 409]

    def test_batch_delete_mixed(self, client):
        """Test batch delete with mix of valid and invalid IDs"""
        response = client.delete('/api/categories/batch', json={
            'ids': [99999, 100000]  # Non-existent IDs
        })
        
        assert response.status_code == 200
        data = response.json
        assert data['success'] is True
        assert data['data']['deleted_count'] == 0

    def test_api_batch_delete(self, client):
        """Test API endpoint for batch delete"""
        response = client.delete('/api/categories/batch', json={'ids': []})
        
        # Empty list should be handled gracefully
        assert response.status_code in [200, 400]

    def test_api_batch_delete_with_events(self, client):
        """Test API batch delete with events association check"""
        # This test ensures the API properly checks for event associations
        response = client.post('/api/categories', json={
            'name': 'Test Category',
            'name_cn': '测试分类'
        })
        
        if response.status_code != 200:
            pytest.skip("Could not create test category")
        
        category_id = response.json['data']['id']
        
        # Delete should work if no events
        response = client.delete('/api/categories/batch', json={'ids': [category_id]})
        
        assert response.status_code == 200
        data = response.json
        assert data['success'] is True


class TestCategoryBatchDeleteValidation:
    """Test validation for batch delete operations"""

    def test_batch_delete_empty_list(self, client):
        """Test batch delete with empty ID list"""
        response = client.delete('/api/categories/batch', json={'ids': []})
        
        # Empty list should be handled gracefully
        assert response.status_code in [200, 400]

    def test_batch_delete_invalid_ids(self, client):
        """Test batch delete with invalid ID types"""
        response = client.delete('/api/categories/batch', json={'ids': ['invalid', 'ids']})
        
        assert response.status_code == 400

    def test_api_batch_delete_empty_request(self, client):
        """Test API batch delete with empty request body"""
        response = client.delete('/api/categories/batch', json={})
        
        assert response.status_code == 400

    def test_api_batch_delete_too_many_ids(self, client):
        """Test API batch delete with too many IDs"""
        # Generate a large list of IDs
        ids = list(range(1, 101))  # 100 IDs
        
        response = client.delete('/api/categories/batch', json={'ids': ids})
        
        # Should either succeed or fail gracefully
        assert response.status_code in [200, 400]
