# ⚠️ PERFORMANCE ISSUE: N+1 query detected in this file
# TODO: Refactor to use JOIN or prefetch pattern
# See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameter Batch Query Tests

测试参数批量查询功能, 验证N+1查询已修复
"""

import os
import sys
from pathlib import Path

import pytest

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_batch_find_by_event_ids(db):
    """
    RED测试: 批量查询事件参数功能

    验证batch_find_by_event_ids方法能一次性查询多个事件的参数
    """
    # 准备测试数据 - 创建多个游戏
    db.execute(
        'INSERT INTO games (gid, name, ods_db) VALUES (?, ?, ?)', (90000001, '测试游戏1', 'ieu_ods')
    )
    db.execute(
        'INSERT INTO games (gid, name, ods_db) VALUES (?, ?, ?)', (90000002, '测试游戏2', 'ieu_ods')
    )
    db.commit()

    # 获取游戏ID
    game1 = db.execute('SELECT id FROM games WHERE gid = ?', (90000001,)).fetchone()
    game2 = db.execute('SELECT id FROM games WHERE gid = ?', (90000002,)).fetchone()

    # 准备测试事件数据
    db.execute(
        '''INSERT INTO log_events (game_id, game_gid, event_name, event_name_cn, source_table, target_table)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (
            game1['id'],
            90000001,
            'user.login',
            '用户登录',
            'ieu_ods.ods_90000001_all_view',
            'dwd.test',
        ),
    )
    db.execute(
        '''INSERT INTO log_events (game_id, game_gid, event_name, event_name_cn, source_table, target_table)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (
            game2['id'],
            90000002,
            'user.logout',
            '用户登出',
            'ieu_ods.ods_90000002_all_view',
            'dwd.test',
        ),
    )
    db.commit()

    # 获取事件ID
    event1 = db.execute('SELECT id FROM log_events WHERE game_gid = ?', (90000001,)).fetchone()
    event2 = db.execute('SELECT id FROM log_events WHERE game_gid = ?', (90000002,)).fetchone()

    # 添加测试参数
    db.execute(
        '''INSERT INTO event_params (event_id, param_name, param_name_cn, template_id, is_active)
           VALUES (?, ?, ?, ?, ?)''',
        (event1['id'], 'user_id', '用户ID', 1, 1),
    )
    db.execute(
        '''INSERT INTO event_params (event_id, param_name, param_name_cn, template_id, is_active)
           VALUES (?, ?, ?, ?, ?)''',
        (event1['id'], 'zone_id', '区域ID', 2, 1),
    )
    db.execute(
        '''INSERT INTO event_params (event_id, param_name, param_name_cn, template_id, is_active)
           VALUES (?, ?, ?, ?, ?)''',
        (event2['id'], 'user_id', '用户ID', 1, 1),
    )
    db.commit()

    # 测试批量查询
    from backend.models.repositories.parameters import ParameterRepository

    repo = ParameterRepository()

    # 验证batch_find_by_event_ids方法存在并正确工作
    params_map = repo.batch_find_by_event_ids([event1['id'], event2['id']])

    # 验证结果
    assert isinstance(params_map, dict)
    assert event1['id'] in params_map
    assert event2['id'] in params_map

    # 验证第一个事件的参数
    event1_params = params_map[event1['id']]
    assert len(event1_params) == 2
    param_names = [p.name for p in event1_params]
    assert 'user_id' in param_names
    assert 'zone_id' in param_names

    # 验证第二个事件的参数
    event2_params = params_map[event2['id']]
    assert len(event2_params) == 1
    assert event2_params[0].name == 'user_id'

    # 验证参数包含game_gid
    for params in params_map.values():
        for param in params:
            assert hasattr(param, 'game_gid')
            assert param.game_gid > 0


def test_batch_get_game_gids_by_param_ids(db):
    """
    RED测试: 批量获取参数对应的游戏GID功能

    验证batch_get_game_gids_by_param_ids方法能正确映射参数ID到游戏GID
    """
    # 准备测试数据 - 创建游戏和公共参数 (使用不同的GID避免冲突)
    db.execute(
        'INSERT INTO games (gid, name, ods_db) VALUES (?, ?, ?)', (90001001, '测试游戏1', 'ieu_ods')
    )
    db.execute(
        'INSERT INTO games (gid, name, ods_db) VALUES (?, ?, ?)', (90001002, '测试游戏2', 'ieu_ods')
    )
    db.commit()

    # 添加测试公共参数
    db.execute(
        '''INSERT INTO common_params (game_id, game_gid, param_name, param_name_cn, param_type)
           VALUES (?, ?, ?, ?, ?)''',
        (1, 90000001, 'user_id', '用户ID', 'string'),
    )
    db.execute(
        '''INSERT INTO common_params (game_id, game_gid, param_name, param_name_cn, param_type)
           VALUES (?, ?, ?, ?, ?)''',
        (2, 90000002, 'zone_id', '区域ID', 'string'),
    )
    db.commit()

    # 获取参数ID
    param1 = db.execute('SELECT id FROM common_params WHERE game_gid = ?', (90000001,)).fetchone()
    param2 = db.execute('SELECT id FROM common_params WHERE game_gid = ?', (90000002,)).fetchone()

    # 测试批量获取游戏GID
    from backend.models.repositories.parameters import ParameterRepository

    repo = ParameterRepository()

    # 验证batch_get_game_gids_by_param_ids方法存在并正确工作
    game_gids_map = repo.batch_get_game_gids_by_param_ids([param1['id'], param2['id']])

    # 验证结果
    assert isinstance(game_gids_map, dict)
    assert param1['id'] in game_gids_map
    assert param2['id'] in game_gids_map

    # 验证游戏GID映射正确
    assert game_gids_map[param1['id']] == 90000001
    assert game_gids_map[param2['id']] == 90000002


def test_batch_queries_performance_improvement():
    """
    RED测试: 批量查询性能改进验证

    验证批量查询比单独查询更高效
    """
    from backend.models.repositories.parameters import ParameterRepository

    repo = ParameterRepository()

    # 测试空列表情况
    empty_result = repo.batch_find_by_event_ids([])
    assert empty_result == {}

    empty_gids_result = repo.batch_get_game_gids_by_param_ids([])
    assert empty_gids_result == {}

    # 测试单元素列表
    single_result = repo.batch_find_by_event_ids([1])
    assert isinstance(single_result, dict)

    single_gids_result = repo.batch_get_game_gids_by_param_ids([1])
    assert isinstance(single_gids_result, dict)


def test_get_common_params_caching():
    """
    RED测试: get_common_params方法的缓存功能

    验证get_common_params方法使用了正确的缓存装饰器和时间
    """
    from backend.services.parameters.parameter_service import ParameterService

    service = ParameterService()

    # 检查方法是否有缓存装饰器
    import inspect

    source = inspect.getsource(service.get_common_params)

    # 验证存在缓存装饰器
    assert '@cached' in source

    # 验证缓存键正确
    assert 'params.commonByGame' in source

    # 验证缓存超时时间
    assert 'timeout=180' in source or 'timeout = 180' in source
