#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Template Service
"""

import json
import unittest
from unittest.mock import MagicMock, patch

from backend.services.template_service import TemplateService


class TestTemplateService(unittest.TestCase):
    """Template Service Unit Tests"""

    def setUp(self):
        """Set up test fixtures"""
        self.service = TemplateService()

    @patch('backend.services.template_service.fetch_all_as_dict')
    def test_get_categories(self, mock_fetch):
        """Test getting template categories"""
        # Mock response
        mock_fetch.return_value = [
            {'category': '登录事件', 'template_count': 10, 'total_usage': 150},
            {'category': '充值付费', 'template_count': 5, 'total_usage': 80},
        ]

        # Call method
        result = self.service.get_categories()

        # Assertions
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['category'], '登录事件')
        self.assertEqual(result[0]['template_count'], 10)
        mock_fetch.assert_called_once()

    @patch('backend.services.template_service.fetch_all_as_dict')
    def test_get_subcategories(self, mock_fetch):
        """Test getting subcategories for a category"""
        # Mock response
        mock_fetch.return_value = [{'subcategory': '基础登录'}, {'subcategory': '设备登录'}]

        # Call method
        result = self.service.get_subcategories('登录事件')

        # Assertions
        self.assertEqual(len(result), 2)
        self.assertIn('基础登录', result)
        self.assertIn('设备登录', result)
        mock_fetch.assert_called_once()

    @patch('backend.services.template_service.fetch_all_as_dict')
    @patch('backend.services.template_service.fetch_one_as_dict')
    def test_search_templates(self, mock_fetch_one, mock_fetch_all):
        """Test searching templates"""
        # Mock responses
        mock_fetch_one.return_value = {'total': 5}
        mock_fetch_all.return_value = [
            {'id': 1, 'name': 'test_template', 'display_name': 'Test Template'}
        ]

        # Call method
        result = self.service.search_templates(keyword='test', limit=10, offset=0)

        # Assertions
        self.assertIn('templates', result)
        self.assertIn('total', result)
        self.assertEqual(result['total'], 5)
        self.assertEqual(len(result['templates']), 1)

    @patch('backend.services.template_service.fetch_all_as_dict')
    def test_get_popular_templates(self, mock_fetch):
        """Test getting popular templates"""
        # Mock response
        mock_fetch.return_value = [{'id': 1, 'name': 'popular_template', 'usage_count': 100}]

        # Call method
        result = self.service.get_popular_templates(limit=10)

        # Assertions
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['usage_count'], 100)
        mock_fetch.assert_called_once()

    @patch('backend.services.template_service.fetch_one_as_dict')
    def test_get_template_by_id(self, mock_fetch):
        """Test getting template by ID"""
        # Mock response
        mock_fetch.return_value = {
            'id': 1,
            'name': 'test_template',
            'display_name': 'Test Template',
        }

        # Call method
        result = self.service.get_template_by_id(1)

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], 1)
        self.assertEqual(result['name'], 'test_template')

    @patch('backend.services.template_service.execute_write')
    @patch('backend.services.template_service.fetch_one_as_dict')
    def test_increment_usage(self, mock_fetch, mock_execute):
        """Test incrementing template usage"""
        # Mock responses
        mock_execute.return_value = 1
        mock_fetch.return_value = {'id': 1, 'usage_count': 11}

        # Call method
        result = self.service.increment_usage(1)

        # Assertions
        self.assertTrue(result)
        mock_execute.assert_called_once()

    @patch('backend.services.template_service.execute_write')
    @patch('backend.services.template_service.fetch_one_as_dict')
    def test_create_template(self, mock_fetch, mock_execute):
        """Test creating a new template"""
        # Mock responses
        mock_execute.return_value = 1
        mock_fetch.return_value = {'id': 1, 'name': 'new_template', 'display_name': 'New Template'}

        # Test data
        template_data = {
            'name': 'new_template',
            'display_name': 'New Template',
            'category': '登录事件',
            'hql_content': 'SELECT * FROM table',
            'tags': ['test'],
            'variables': {'param1': 'value1'},
        }

        # Call method
        result = self.service.create_template(template_data)

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'new_template')
        mock_execute.assert_called_once()

    @patch('backend.services.template_service.execute_write')
    def test_update_template(self, mock_execute):
        """Test updating a template"""
        # Mock response
        mock_execute.return_value = 1

        # Test data
        update_data = {'display_name': 'Updated Template', 'description': 'Updated description'}

        # Call method
        result = self.service.update_template(1, update_data)

        # Assertions
        self.assertTrue(result)
        mock_execute.assert_called_once()

    @patch('backend.services.template_service.execute_write')
    @patch('backend.services.template_service.fetch_one_as_dict')
    def test_delete_template(self, mock_fetch, mock_execute):
        """Test deleting a template"""
        # Mock responses
        mock_fetch.return_value = {'id': 1, 'name': 'test_template', 'is_system': 0}
        mock_execute.return_value = 1

        # Call method
        result = self.service.delete_template(1)

        # Assertions
        self.assertTrue(result)
        mock_execute.assert_called_once()

    def test_delete_system_template_raises_error(self):
        """Test that deleting a system template raises an error"""
        # Mock response
        with patch('backend.services.template_service.fetch_one_as_dict') as mock_fetch:
            mock_fetch.return_value = {'id': 1, 'name': 'system_template', 'is_system': 1}

            # Call method and assert error
            with self.assertRaises(ValueError) as context:
                self.service.delete_template(1)

            self.assertIn('Cannot delete system template', str(context.exception))

    @patch('backend.services.template_service.fetch_one_as_dict')
    def test_export_template(self, mock_fetch):
        """Test exporting a template"""
        # Mock response
        mock_fetch.return_value = {
            'id': 1,
            'name': 'test_template',
            'display_name': 'Test Template',
            'category': '登录事件',
            'hql_content': 'SELECT * FROM table',
            'tags': json.dumps(['test']),
            'variables': json.dumps({'param1': 'value1'}),
            'created_at': '2024-01-01',
            'updated_at': '2024-01-01',
        }

        # Call method
        result = self.service.export_template(1)

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'test_template')
        self.assertIsInstance(result['tags'], list)
        self.assertIsInstance(result['variables'], dict)
        self.assertNotIn('created_at', result)
        self.assertNotIn('updated_at', result)

    @patch('backend.services.template_service.fetch_one_as_dict')
    @patch('backend.services.template_service.create_template')
    def test_import_template(self, mock_create, mock_fetch):
        """Test importing a template"""
        # Mock responses
        mock_fetch.return_value = None  # Template doesn't exist
        mock_create.return_value = {'id': 1, 'name': 'imported_template'}

        # Test data
        template_data = {
            'name': 'imported_template',
            'display_name': 'Imported Template',
            'category': '登录事件',
            'hql_content': 'SELECT * FROM table',
        }

        # Call method
        result = self.service.import_template(template_data)

        # Assertions
        self.assertIsNotNone(result)
        mock_create.assert_called_once()

    def test_import_template_missing_required_fields(self):
        """Test that importing a template with missing required fields raises an error"""
        # Test data with missing fields
        template_data = {
            'name': 'test_template'
            # Missing display_name, category, hql_content
        }

        # Call method and assert error
        with self.assertRaises(ValueError) as context:
            self.service.import_template(template_data)

        self.assertIn('Missing required field', str(context.exception))


if __name__ == '__main__':
    unittest.main()
