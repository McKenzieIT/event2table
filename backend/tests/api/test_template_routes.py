#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Template API Routes
"""

import unittest
import json
from unittest.mock import patch, MagicMock
from backend.api.routes.template import (
    api_get_template_categories,
    api_get_template_subcategories,
    api_search_templates,
    api_get_popular_templates,
    api_export_template,
    api_import_template,
    api_get_template,
    api_increment_template_usage
)
from flask import Flask


class TestTemplateRoutes(unittest.TestCase):
    """Template API Routes Unit Tests"""

    def setUp(self):
        """Set up test fixtures"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    @patch('backend.api.routes.template.TemplateService')
    def test_api_get_template_categories(self, mock_service_class):
        """Test GET /api/templates/categories endpoint"""
        # Mock service
        mock_service = MagicMock()
        mock_service.get_categories.return_value = [
            {'category': '登录事件', 'template_count': 10}
        ]
        mock_service_class.return_value = mock_service
        
        # Create test request context
        with self.app.test_request_context():
            response = api_get_template_categories()
            data = json.loads(response[0].get_data(as_text=True))
            
            # Assertions
            self.assertTrue(data['success'])
            self.assertEqual(len(data['data']), 1)

    @patch('backend.api.routes.template.TemplateService')
    def test_api_get_template_subcategories(self, mock_service_class):
        """Test GET /api/templates/categories/{category}/subcategories endpoint"""
        # Mock service
        mock_service = MagicMock()
        mock_service.get_subcategories.return_value = ['基础登录', '设备登录']
        mock_service_class.return_value = mock_service
        
        # Create test request context
        with self.app.test_request_context():
            response = api_get_template_subcategories('登录事件')
            data = json.loads(response[0].get_data(as_text=True))
            
            # Assertions
            self.assertTrue(data['success'])
            self.assertEqual(len(data['data']), 2)

    @patch('backend.api.routes.template.TemplateService')
    def test_api_search_templates(self, mock_service_class):
        """Test POST /api/templates/search endpoint"""
        # Mock service
        mock_service = MagicMock()
        mock_service.search_templates.return_value = {
            'templates': [{'id': 1, 'name': 'test'}],
            'total': 1,
            'limit': 50,
            'offset': 0
        }
        mock_service_class.return_value = mock_service
        
        # Create test request context
        with self.app.test_request_context(
            '/api/templates/search',
            method='POST',
            data=json.dumps({'keyword': 'test'}),
            content_type='application/json'
        ):
            response = api_search_templates()
            data = json.loads(response[0].get_data(as_text=True))
            
            # Assertions
            self.assertTrue(data['success'])
            self.assertIn('templates', data['data'])

    @patch('backend.api.routes.template.TemplateService')
    def test_api_get_popular_templates(self, mock_service_class):
        """Test GET /api/templates/popular endpoint"""
        # Mock service
        mock_service = MagicMock()
        mock_service.get_popular_templates.return_value = [
            {'id': 1, 'name': 'popular_template', 'usage_count': 100}
        ]
        mock_service_class.return_value = mock_service
        
        # Create test request context
        with self.app.test_request_context('/api/templates/popular?limit=10'):
            response = api_get_popular_templates()
            data = json.loads(response[0].get_data(as_text=True))
            
            # Assertions
            self.assertTrue(data['success'])
            self.assertEqual(len(data['data']), 1)

    @patch('backend.api.routes.template.TemplateService')
    def test_api_export_template(self, mock_service_class):
        """Test GET /api/templates/{id}/export endpoint"""
        # Mock service
        mock_service = MagicMock()
        mock_service.export_template.return_value = {
            'id': 1,
            'name': 'test_template',
            'hql_content': 'SELECT * FROM table'
        }
        mock_service_class.return_value = mock_service
        
        # Create test request context
        with self.app.test_request_context('/api/templates/1/export'):
            response = api_export_template(1)
            data = json.loads(response[0].get_data(as_text=True))
            
            # Assertions
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['id'], 1)

    @patch('backend.api.routes.template.TemplateService')
    def test_api_import_template(self, mock_service_class):
        """Test POST /api/templates/import endpoint"""
        # Mock service
        mock_service = MagicMock()
        mock_service.import_template.return_value = {
            'id': 1,
            'name': 'imported_template'
        }
        mock_service_class.return_value = mock_service
        
        # Test data
        import_data = {
            'name': 'imported_template',
            'display_name': 'Imported Template',
            'category': '登录事件',
            'hql_content': 'SELECT * FROM table'
        }
        
        # Create test request context
        with self.app.test_request_context(
            '/api/templates/import',
            method='POST',
            data=json.dumps(import_data),
            content_type='application/json'
        ):
            response = api_import_template()
            data = json.loads(response[0].get_data(as_text=True))
            
            # Assertions
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['name'], 'imported_template')

    @patch('backend.api.routes.template.TemplateService')
    def test_api_get_template(self, mock_service_class):
        """Test GET /api/templates/{id} endpoint"""
        # Mock service
        mock_service = MagicMock()
        mock_service.get_template_by_id.return_value = {
            'id': 1,
            'name': 'test_template'
        }
        mock_service_class.return_value = mock_service
        
        # Create test request context
        with self.app.test_request_context('/api/templates/1'):
            response = api_get_template(1)
            data = json.loads(response[0].get_data(as_text=True))
            
            # Assertions
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['id'], 1)

    @patch('backend.api.routes.template.TemplateService')
    def test_api_increment_template_usage(self, mock_service_class):
        """Test POST /api/templates/{id}/usage endpoint"""
        # Mock service
        mock_service = MagicMock()
        mock_service.increment_usage.return_value = True
        mock_service.get_template_by_id.return_value = {
            'id': 1,
            'usage_count': 11
        }
        mock_service_class.return_value = mock_service
        
        # Create test request context
        with self.app.test_request_context('/api/templates/1/usage', method='POST'):
            response = api_increment_template_usage(1)
            data = json.loads(response[0].get_data(as_text=True))
            
            # Assertions
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['usage_count'], 11)


if __name__ == '__main__':
    unittest.main()
