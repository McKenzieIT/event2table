#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Additional Utils 单元测试

测试 backend.core.utils 中的更多工具函数
"""

import pytest
from datetime import datetime
from backend.core.utils import (
    success_response,
    error_response,
)


class TestSuccessResponse:
    """测试success_response函数"""

    def test_success_response_basic(self):
        """测试基本成功响应"""
        response, status = success_response()

        assert status == 200
        assert response['success'] is True
        assert 'timestamp' in response

    def test_success_response_with_data(self):
        """测试带数据的成功响应"""
        response, status = success_response(data={'id': 123, 'name': 'test'})

        assert status == 200
        assert response['data']['id'] == 123
        assert response['data']['name'] == 'test'

    def test_success_response_with_message(self):
        """测试带消息的成功响应"""
        response, status = success_response(message='Operation successful')

        assert status == 200
        assert response['message'] == 'Operation successful'

    def test_success_response_with_status_code(self):
        """测试带自定义状态码的成功响应"""
        response, status = success_response(status_code=201)

        assert status == 201

    def test_success_response_with_extra_fields(self):
        """测试带额外字段的成功响应"""
        response, status = success_response(extra='value', count=5)

        assert status == 200
        assert response['extra'] == 'value'
        assert response['count'] == 5


class TestErrorResponse:
    """测试error_response函数"""

    def test_error_response_basic(self):
        """测试基本错误响应"""
        response, status = error_response('Something went wrong')

        assert status == 400
        assert response['success'] is False
        assert response['error'] == 'Something went wrong'
        assert 'timestamp' in response

    def test_error_response_with_status_code(self):
        """测试带自定义状态码的错误响应"""
        response, status = error_response('Not found', status_code=404)

        assert status == 404

    def test_error_response_with_extra_fields(self):
        """测试带额外字段的错误响应"""
        response, status = error_response('Validation failed', field='name')

        assert status == 400
        assert response['field'] == 'name'


@pytest.mark.unit
class TestUtilityFunctions:
    """测试其他工具函数"""

    def test_timestamp_format(self):
        """测试时间戳格式"""
        response, _ = success_response()
        timestamp = response.get('timestamp')

        assert timestamp is not None
        # ISO format should contain T and colon
        assert 'T' in timestamp or ':' in timestamp

    def test_response_structure(self):
        """测试响应结构一致性"""
        success_resp, _ = success_response()
        error_resp, _ = error_response('Test error')

        # Both should have timestamp
        assert 'timestamp' in success_resp
        assert 'timestamp' in error_resp

        # Both should have success boolean
        assert 'success' in success_resp
        assert 'success' in error_resp
        assert success_resp['success'] is True
        assert error_resp['success'] is False
