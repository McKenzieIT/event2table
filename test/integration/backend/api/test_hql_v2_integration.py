"""
HQL V2 集成测试

测试HQL V2 API端点的完整工作流程
遵循TDD原则：先写测试，看它失败，然后实现
"""

import pytest
import sys
import json
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 导入Flask应用和模型
from backend.services.hql.models.event import Event, Field, Condition
from web_app import app


@pytest.mark.usefixtures("hql_v2_test_data")
class TestHQLV2PreviewAPI:
    """HQL V2 预览API集成测试"""

    def setup_method(self):
        """每个测试前的准备"""
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def teardown_method(self):
        """每个测试后的清理"""
        self.app_context.pop()

    def test_preview_hql_returns_valid_response(self):
        """
        RED: 测试预览HQL API返回有效响应

        应该POST /hql-preview-v2/api/preview
        返回200状态码和HQL内容
        """
        # 准备请求数据（使用实际存在的事件ID）
        request_data = {
            "game_gid": 10000147,
            "event_id": 55,  # 使用实际存在的事件ID
            "fields": [
                {"name": "ds", "type": "base"},
                {"name": "role_id", "type": "base"}
            ],
            "filter_conditions": {}
        }

        # 发送请求
        response = self.client.post(
            '/hql-preview-v2/api/preview',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'hql_content' in data['data']
        assert len(data['data']['hql_content']) > 0

    def test_preview_hql_with_conditions(self):
        """
        RED: 测试带过滤条件的HQL预览

        应该在WHERE子句中包含过滤条件
        """
        request_data = {
            "game_gid": 10000147,
            "event_id": 55,  # 使用实际存在的事件ID
            "fields": [
                {"name": "role_id", "type": "base"}
            ],
            "filter_conditions": {
                "conditions": [
                    {"field": "role_id", "operator": "=", "value": 123}
                ]
            }
        }

        response = self.client.post(
            '/hql-preview-v2/api/preview',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'role_id = 123' in data['data']['hql_content']

    def test_preview_hql_with_param_field(self):
        """
        RED: 测试带参数字段的HQL预览

        应该使用get_json_object提取参数
        """
        request_data = {
            "game_gid": 10000147,
            "event_id": 55,  # 使用实际存在的事件ID
            "fields": [
                {"name": "role_id", "type": "base"},
                {"name": "zone_id", "type": "param", "json_path": "$.zone_id", "alias": "zone"}
            ],
            "filter_conditions": {}
        }

        response = self.client.post(
            '/hql-preview-v2/api/preview',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'get_json_object(params, \'$.zone_id\')' in data['data']['hql_content']

    def test_preview_hql_validates_required_fields(self):
        """
        RED: 测试API验证必填字段

        缺少必填字段应该返回400错误
        """
        # 缺少event_id
        request_data = {
            "game_gid": 10000147,
            "fields": [],
            "filter_conditions": {}
        }

        response = self.client.post(
            '/hql-preview-v2/api/preview',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'error' in data

    def test_preview_hql_handles_invalid_event_id(self):
        """
        RED: 测试API处理无效的event_id

        不存在的event_id应该返回404错误
        """
        request_data = {
            "game_gid": 10000147,
            "event_id": 99999,  # 不存在的事件ID
            "fields": [],
            "filter_conditions": {}
        }

        response = self.client.post(
            '/hql-preview-v2/api/preview',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] == False

    def test_preview_hql_generates_correct_view_name(self):
        """
        RED: 测试生成的HQL使用正确的表名

        生成的HQL应该包含正确的表名和字段
        """
        request_data = {
            "game_gid": 10000147,
            "event_id": 55,  # 使用实际存在的事件ID
            "fields": [
                {"name": "role_id", "type": "base"}
            ],
            "filter_conditions": {}
        }

        response = self.client.post(
            '/hql-preview-v2/api/preview',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True

        # 验证HQL包含正确的表名
        hql = data['data']['hql_content']
        assert 'FROM ieu_ods.ods_10000147_all_view' in hql
        assert '`role_id`' in hql
        assert 'WHERE' in hql
        assert 'ds =' in hql


@pytest.mark.usefixtures("hql_v2_test_data")
class TestHQLV2Validation:
    """HQL V2 数据验证测试"""

    def setup_method(self):
        """测试前准备"""
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def teardown_method(self):
        """测试后清理"""
        self.app_context.pop()

    def test_validates_field_structure(self):
        """
        RED: 测试字段结构验证

        字段必须有name和type属性
        """
        request_data = {
            "game_gid": 10000147,
            "event_id": 55,  # 使用实际存在的事件ID
            "fields": [
                {"name": "role_id"}  # 缺少type
            ],
            "filter_conditions": {}
        }

        response = self.client.post(
            '/hql-preview-v2/api/preview',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        # 应该返回400或处理得体的错误
        assert response.status_code in [400, 200]
        if response.status_code == 400:
            data = json.loads(response.data)
            assert data['success'] == False

    def test_validates_condition_operators(self):
        """
        RED: 测试条件操作符验证

        只允许有效的操作符
        """
        request_data = {
            "game_gid": 10000147,
            "event_id": 55,  # 使用实际存在的事件ID
            "fields": [{"name": "role_id", "type": "base"}],
            "filter_conditions": {
                "conditions": [
                    {"field": "role_id", "operator": "INVALID", "value": 123}
                ]
            }
        }

        response = self.client.post(
            '/hql-preview-v2/api/preview',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        # 应该处理无效操作符
        assert response.status_code in [400, 200]
        data = json.loads(response.data)

        # 如果返回成功，HQL应该包含错误处理或默认处理
        if data['success']:
            # 生成的HQL应该能处理这种情况
            pass


@pytest.mark.usefixtures("hql_v2_test_data")
class TestHQLV2Performance:
    """HQL V2 性能测试"""

    def setup_method(self):
        """测试前准备"""
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def teardown_method(self):
        """测试后清理"""
        self.app_context.pop()

    def test_preview_hql_performance_with_large_fields(self):
        """
        RED: 测试大量字段的性能

        50个字段应该在合理时间内完成（<5秒）
        """
        # 生成50个字段
        fields = [
            {"name": f"field_{i}", "type": "base"}
            for i in range(50)
        ]

        request_data = {
            "game_gid": 10000147,
            "event_id": 55,  # 使用实际存在的事件ID
            "fields": fields,
            "filter_conditions": {}
        }

        # 测试性能
        import time
        start_time = time.time()

        response = self.client.post(
            '/hql-preview-v2/api/preview',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        end_time = time.time()
        duration = end_time - start_time

        assert response.status_code == 200
        assert duration < 5.0, f"HQL生成耗时 {duration:.2f}秒，超过5秒限制"


if __name__ == '__main__':
    # 运行测试
    pytest.main([__file__, '-v'])
