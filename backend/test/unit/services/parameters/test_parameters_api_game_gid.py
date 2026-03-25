#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参数API game_gid修复测试

测试所有参数API正确使用game_gid进行查询, 而非game_id
"""

import os
import sys
from pathlib import Path

import pytest

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_parameters_all_uses_game_gid(client, db):
    """
    RED测试: 参数列表API应使用game_gid查询

    验证使用game_gid参数能正确返回参数列表
    """
    # 准备测试数据
    game = db.execute('SELECT * FROM games WHERE gid = ?', (10000147,)).fetchone()
    if not game:
        cursor = db.execute(
            'INSERT INTO games (gid, name, ods_db) VALUES (?, ?, ?)',
            (10000147, '测试游戏', 'ieu_ods'),
        )
        game_id = cursor.lastrowid
        db.commit()
    else:
        game_id = game['id']

    # 准备测试事件数据
    event = db.execute(
        'SELECT * FROM log_events WHERE game_gid = ? LIMIT 1', (10000147,)
    ).fetchone()
    if not event:
        db.execute(
            '''INSERT INTO log_events (id, game_id, event_name, event_name_cn, source_table, target_table, game_gid)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (
                1,
                game_id,
                'test.event',
                '测试事件',
                'ieu_ods.ods_10000147_all_view',
                'dwd.test',
                10000147,
            ),
        )
        db.commit()

    response = client.get('/api/parameters/all?game_gid=10000147')

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    # 验证返回参数列表(可能为空, 但API应该工作)
    assert 'parameters' in data['data']


def test_parameter_details_uses_game_gid(client, db):
    """
    RED测试: 参数详情API应使用game_gid查询
    """
    # 准备测试数据
    game = db.execute('SELECT * FROM games WHERE gid = ?', (10000147,)).fetchone()
    if not game:
        cursor = db.execute(
            'INSERT INTO games (gid, name, ods_db) VALUES (?, ?, ?)',
            (10000147, '测试游戏', 'ieu_ods'),
        )
        game_id = cursor.lastrowid
        db.commit()
    else:
        game_id = game['id']

    # 先创建一个测试参数
    try:
        db.execute(
            '''INSERT INTO event_params (event_id, param_name, param_name_cn, template_id, is_active, version)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (1, 'test_param', '测试参数', 1, 1, 1),
        )
        db.commit()
    except Exception as e:
        # 参数可能已存在, 忽略
        pass

    response = client.get('/api/parameters/test_param/details?game_gid=10000147')

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True


def test_parameter_stats_uses_game_gid(client, db):
    """
    RED测试: 参数统计API应使用game_gid查询
    """
    # 准备测试数据
    game = db.execute('SELECT * FROM games WHERE gid = ?', (10000147,)).fetchone()
    if not game:
        cursor = db.execute(
            'INSERT INTO games (gid, name, ods_db) VALUES (?, ?, ?)',
            (10000147, '测试游戏', 'ieu_ods'),
        )
        db.commit()

    response = client.get('/api/parameters/stats?game_gid=10000147')

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'total_unique_params' in data['data']


def test_parameter_search_uses_game_gid(client, db):
    """
    RED测试: 参数搜索API应使用game_gid查询
    """
    # 准备测试数据
    game = db.execute('SELECT * FROM games WHERE gid = ?', (10000147,)).fetchone()
    if not game:
        cursor = db.execute(
            'INSERT INTO games (gid, name, ods_db) VALUES (?, ?, ?)',
            (10000147, '测试游戏', 'ieu_ods'),
        )
        db.commit()

    response = client.post(
        '/api/parameters/search', json={'game_gid': '10000147', 'keyword': 'test'}
    )

    # 期望API正常处理(可能返回404如果参数不存在, 但不应该500错误)
    assert response.status_code in [200, 404]


def test_common_parameters_uses_game_gid(client, db):
    """
    RED测试: 公共参数API应使用game_gid查询
    """
    # 准备测试数据
    game = db.execute('SELECT * FROM games WHERE gid = ?', (10000147,)).fetchone()
    if not game:
        cursor = db.execute(
            'INSERT INTO games (gid, name, ods_db) VALUES (?, ?, ?)',
            (10000147, '测试游戏', 'ieu_ods'),
        )
        db.commit()

    response = client.get('/api/parameters/common?game_gid=10000147')

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True


def test_parameter_validate_uses_game_gid(client, db):
    """
    RED测试: 参数验证API应使用game_gid查询
    """
    # 准备测试数据
    game = db.execute('SELECT * FROM games WHERE gid = ?', (10000147,)).fetchone()
    if not game:
        cursor = db.execute(
            'INSERT INTO games (gid, name, ods_db) VALUES (?, ?, ?)',
            (10000147, '测试游戏', 'ieu_ods'),
        )
        db.commit()

    response = client.get('/api/parameters/validate?game_gid=10000147&param_name=test_param')

    # 期望API正常处理
    assert response.status_code in [200, 404]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
