"""
测试参数库 API - Test Driven Development

按照 TDD 原则编写：
1. RED - 先写失败的测试
2. Verify RED - 确认测试失败
3. GREEN - 写最少的代码让测试通过
4. Verify GREEN - 确认测试通过
5. REFACTOR - 重构清理
"""

import pytest
import os
from backend.core.database import get_db_connection, init_db
from backend.core.config import TEST_DB_PATH
from web_app import app


@pytest.fixture
def client(app):
    """
    创建测试客户端

    注意：此 fixture 现在依赖 conftest.py 中的 app fixture，
    该 fixture 已经正确处理了测试数据库的初始化和迁移。
    不应该在这里删除或重建数据库，以避免破坏其他测试的数据库状态。
    """
    # 确保使用测试环境
    os.environ['FLASK_ENV'] = 'testing'
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


def test_check_param_library_existing_parameter(client):
    """
    RED #1: 测试检查参数库中已存在的参数

    Given: 数据库中存在 accountId 参数 (template_id=1)
    When: 调用 GET /api/param-library/check?param_name=accountId&template_id=1
    Then: 返回 exists=True，并包含库参数详情
    """
    # 创建测试数据
    from backend.core.utils import execute_write

    # 创建参数库参数
    execute_write("""
        INSERT INTO param_library (param_name, param_name_cn, template_id, category)
        VALUES ('accountId', '账户ID', 1, 'common')
    """)

    response = client.get('/api/param-library/check?param_name=accountId&template_id=1')

    assert response.status_code == 200
    data = response.get_json()

    assert data['success'] == True
    assert data['data']['exists'] == True
    assert data['data']['library_param'] is not None
    assert data['data']['library_param']['param_name'] == 'accountId'
    assert data['data']['library_param']['template_id'] == 1

    # 清理测试数据
    execute_write("DELETE FROM param_library WHERE param_name = 'accountId'")


def test_check_param_library_nonexistent_parameter(client):
    """
    RED #2: 测试检查参数库中不存在的参数

    Given: 数据库中不存在 nonexistent_param 参数
    When: 调用 GET /api/param-library/check?param_name=nonexistent_param&template_id=1
    Then: 返回 exists=False，library_param 为 None
    """
    response = client.get('/api/param-library/check?param_name=nonexistent_param&template_id=1')

    assert response.status_code == 200
    data = response.get_json()

    assert data['success'] == True
    assert data['data']['exists'] == False
    assert data['data']['library_param'] is None


def test_check_param_library_missing_params(client):
    """
    RED #3: 测试缺少必需参数时的验证

    Given: 请求缺少 param_name
    When: 调用 GET /api/param-library/check?template_id=1
    Then: 返回 400 错误
    """
    response = client.get('/api/param-library/check?template_id=1')

    assert response.status_code == 400
    data = response.get_json()

    assert 'error' in data or 'message' in data


def test_check_param_library_missing_template_id(client):
    """
    RED #4: 测试缺少 template_id 参数

    Given: 请求缺少 template_id
    When: 调用 GET /api/param-library/check?param_name=test
    Then: 返回 400 错误
    """
    response = client.get('/api/param-library/check?param_name=test')

    assert response.status_code == 400
    data = response.get_json()

    assert 'error' in data or 'message' in data


def test_link_to_library_success(client):
    """
    RED #5: 测试成功关联参数到库

    Given: 存在事件参数 ID 和参数库 ID
    When: 调用 POST /api/event-params/<id>/link-library with library_id
    Then: 参数成功关联，返回成功消息
    """
    import uuid
    # 先创建测试数据
    from backend.core.utils import execute_write, fetch_one_as_dict

    # 使用唯一的参数名避免冲突
    unique_param_name = f'test_param_link_{uuid.uuid4().hex[:8]}'

    # 创建测试事件参数
    execute_write("""
        INSERT INTO event_params (event_id, param_name, param_name_cn, template_id, is_active)
        VALUES (1, ?, '测试参数', 1, 1)
    """, (unique_param_name,))

    # 创建参数库参数
    execute_write("""
        INSERT INTO param_library (param_name, param_name_cn, template_id, category)
        VALUES (?, '测试参数', 1, 'test')
    """, (unique_param_name,))

    param_id = fetch_one_as_dict("SELECT id FROM event_params WHERE param_name = ?", (unique_param_name,))['id']
    library_id = fetch_one_as_dict("SELECT id FROM param_library WHERE param_name = ?", (unique_param_name,))['id']

    # 调用 API
    response = client.post(f'/api/event-params/{param_id}/link-library',
                        json={'library_id': library_id},
                        content_type='application/json')

    assert response.status_code == 200
    data = response.get_json()

    assert data['success'] == True
    assert data['data']['param_id'] == param_id
    assert data['data']['library_id'] == library_id

    # 清理测试数据
    execute_write("DELETE FROM event_params WHERE param_name = ?", (unique_param_name,))
    execute_write("DELETE FROM param_library WHERE param_name = ?", (unique_param_name,))


def test_batch_check_param_library(client):
    """
    RED #6: 测试批量检查参数库

    Given: 参数库中有 accountId (template_id=1) 和 roleId (template_id=2)
    When: 调用 POST /api/param-library/batch-check with 参数列表
    Then: 返回匹配的和不匹配的参数
    """
    # 创建测试数据
    from backend.core.utils import execute_write

    # 创建参数库参数
    execute_write("""
        INSERT INTO param_library (param_name, param_name_cn, template_id, category)
        VALUES ('accountId', '账户ID', 1, 'common')
    """)
    execute_write("""
        INSERT INTO param_library (param_name, param_name_cn, template_id, category)
        VALUES ('roleId', '角色ID', 2, 'common')
    """)

    response = client.post('/api/param-library/batch-check',
                        json={
                            'parameters': [
                                {'param_name': 'accountId', 'template_id': 1},
                                {'param_name': 'roleId', 'template_id': 2},
                                {'param_name': 'nonexistent', 'template_id': 1}
                            ]
                        },
                        content_type='application/json')

    assert response.status_code == 200
    data = response.get_json()

    assert data['success'] == True
    assert 'matched' in data['data']
    assert 'unmatched' in data['data']

    matched = data['data']['matched']
    unmatched = data['data']['unmatched']

    assert len(matched) == 2
    assert len(unmatched) == 1

    assert matched[0]['param_name'] == 'accountId'
    assert matched[1]['param_name'] == 'roleId'
    assert unmatched[0]['param_name'] == 'nonexistent'

    # 清理测试数据
    execute_write("DELETE FROM param_library WHERE param_name IN ('accountId', 'roleId')")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
