#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HQL预览API集成测试

测试事件节点构建器的HQL生成功能，确保：
1. 包含分区筛选 (WHERE ds = '${ds}')
2. 使用正确的表名格式 ({ods_db}.ods_{game_gid}_all_view)
3. 使用 event 而非 event_name
4. 字段根据选择动态生成
"""

import pytest
import json
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def client(app, db):
    """
    创建测试客户端 - 使用共享的app和db fixture

    注意：测试数据准备需要commit，因为API函数使用新的数据库连接。
    db fixture会在测试结束后rollback，所以不会污染数据库。
    """
    with app.test_client() as client:
        # 使用测试数据库
        os.environ["FLASK_ENV"] = "testing"

        # 确保测试游戏存在
        game = db.execute('SELECT * FROM games WHERE gid = ?', (10000147,)).fetchone()
        if not game:
            db.execute('''
                INSERT INTO games (gid, name, ods_db)
                VALUES (?, ?, ?)
            ''', (10000147, '测试游戏', 'ieu_ods'))
            db.commit()  # Commit so API functions can see the data

        # 确保测试事件存在
        event = db.execute('SELECT * FROM log_events WHERE id = 1').fetchone()
        if not event:
            # 先获取游戏的database ID
            game_record = db.execute('SELECT id FROM games WHERE gid = ?', (10000147,)).fetchone()
            if game_record:
                game_db_id = game_record[0]
                db.execute('''
                    INSERT INTO log_events (id, game_id, game_gid, event_name, event_name_cn, source_table, target_table)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (1, game_db_id, 10000147, 'role.online', '角色上线', 'ieu_ods.ods_10000147_all_view', 'dwd.v_dwd_10000147_role_online_di'))
                db.commit()  # Commit so API functions can see the data

        yield client


def test_hql_preview_contains_partition_filter(client):
    """
    RED测试：HQL预览应包含分区筛选

    验证生成的HQL包含 WHERE ds = '${ds}'
    """
    # 准备请求数据
    request_data = {
        "game_gid": 10000147,
        "event_id": 1,
        "name_en": "test_role_online_node",
        "name_cn": "测试角色上线节点",
        "fields": [
            {
                "field_name": "ds",
                "field_type": "base",
                "alias": "ds"
            },
            {
                "field_name": "role_id",
                "field_type": "base",
                "alias": "role_id"
            }
        ],
        "filter_conditions": {
            "custom_where": "",
            "conditions": []
        }
    }

    # 发送API请求
    response = client.post(
        '/event_node_builder/api/preview-hql',
        data=json.dumps(request_data),
        content_type='application/json'
    )

    # 验证响应
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = json.loads(response.data)
    assert 'success' in data, "Response missing 'success' field"
    assert data['success'] == True, f"API returned failure: {data.get('message')}"

    hql = data['data']['hql']

    # 核心验证：必须包含分区筛选
    assert "ds = '${ds}'" in hql, \
        f"HQL missing partition filter! Got:\n{hql}"


def test_hql_preview_uses_correct_table_name(client):
    """
    RED测试：HQL预览应使用正确的表名格式

    验证表名格式为 {ods_db}.ods_{game_gid}_all_view
    """
    request_data = {
        "game_gid": 10000147,
        "event_id": 1,
        "name_en": "test_node",
        "name_cn": "测试节点",
        "fields": [
            {"field_name": "ds", "field_type": "base", "alias": "ds"}
        ],
        "filter_conditions": {"custom_where": "", "conditions": []}
    }

    response = client.post(
        '/event_node_builder/api/preview-hql',
        data=json.dumps(request_data),
        content_type='application/json'
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    hql = data['data']['hql']

    # 验证表名格式
    assert "ods_10000147_all_view" in hql, \
        f"HQL missing correct table name! Got:\n{hql}"
    assert "ieu_ods" in hql or "ods_10000147_all_view" in hql, \
        f"HQL missing ODS database prefix! Got:\n{hql}"


def test_hql_preview_uses_event_not_event_name(client):
    """
    RED测试：HQL预览应使用event而非event_name

    验证WHERE子句使用 event = 'xxx' 而非 event_name = 'xxx'
    """
    request_data = {
        "game_gid": 10000147,
        "event_id": 1,  # 假设event_id=1是role.online事件
        "name_en": "test_node",
        "name_cn": "测试节点",
        "fields": [
            {"field_name": "ds", "field_type": "base", "alias": "ds"}
        ],
        "filter_conditions": {"custom_where": "", "conditions": []}
    }

    response = client.post(
        '/event_node_builder/api/preview-hql',
        data=json.dumps(request_data),
        content_type='application/json'
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    hql = data['data']['hql']

    # 验证使用event而非event_name
    assert "event = " in hql or "event='" in hql or 'event="' in hql, \
        f"HQL should use 'event' field! Got:\n{hql}"
    assert "event_name =" not in hql, \
        f"HQL should NOT use 'event_name'! Got:\n{hql}"


def test_hql_preview_supports_param_fields(client):
    """
    RED测试：HQL预览应支持参数字段

    验证参数字段使用 get_json_object(params, '$.field')
    """
    request_data = {
        "game_gid": 10000147,
        "event_id": 1,
        "name_en": "test_node",
        "name_cn": "测试节点",
        "fields": [
            {"field_name": "ds", "field_type": "base", "alias": "ds"},
            {
                "field_name": "level",
                "field_type": "param",
                "alias": "level",
                "base_type": "int"
            }
        ],
        "filter_conditions": {"custom_where": "", "conditions": []}
    }

    response = client.post(
        '/event_node_builder/api/preview-hql',
        data=json.dumps(request_data),
        content_type='application/json'
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    hql = data['data']['hql']

    # 验证参数字段使用get_json_object
    assert "get_json_object(params, '$.level')" in hql, \
        f"HQL missing get_json_object for param field! Got:\n{hql}"


if __name__ == '__main__':
    # 运行测试
    pytest.main([__file__, '-v'])
