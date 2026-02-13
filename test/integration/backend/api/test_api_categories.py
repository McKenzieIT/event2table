#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Categories API Routes Tests

Tests the backend/api/routes/categories.py endpoints
"""

import pytest


@pytest.mark.integration
@pytest.mark.api
class TestCategoriesAPIList:
    """测试 GET /api/categories 端点"""

    def test_list_categories_success(self, client):
        """测试成功获取分类列表"""
        response = client.get('/api/categories')

        assert response.status_code == 200
        data = response.get_json()

        assert 'success' in data
        assert 'data' in data
        assert isinstance(data['data'], list)


@pytest.mark.integration
@pytest.mark.api
class TestCategoriesAPICreate:
    """测试 POST /api/categories 端点"""

    def test_create_category_missing_name(self, client):
        """测试创建分类缺少名称"""
        response = client.post('/api/categories', json={})

        # Should return error for missing name
        assert response.status_code in [400, 409]


@pytest.mark.integration
@pytest.mark.api
class TestCategoriesAPIGet:
    """测试 GET /api/categories/<id> 端点"""

    def test_get_category_not_found(self, client):
        """测试获取不存在的分类"""
        response = client.get('/api/categories/999999')

        assert response.status_code in [200, 404]  # May return empty list or 404
