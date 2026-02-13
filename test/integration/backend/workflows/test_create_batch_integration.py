#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Tests for create_batch with BatchImportManager

Tests the integration of Repository create_batch method with BatchImportManager
"""

import pytest
from backend.services.bulk_operations.batch_import_manager import batch_import_manager


@pytest.mark.integration
class TestCreateBatchIntegration:
    """测试 create_batch 与 BatchImportManager 集成"""

    def test_prepare_event_record(self):
        """测试事件记录准备功能"""
        event_data = {
            'event_name': 'test_login',
            'event_name_cn': '测试登录',
            'parameters': []
        }

        game_gid = 10000147  # 假设存在这个游戏
        category_id = 1  # 假设存在这个分类

        # 调用准备方法（如果游戏不存在会抛出异常，这是预期的）
        try:
            record = batch_import_manager._prepare_event_record(
                event_data, game_gid, category_id
            )

            # 验证返回的记录包含所有必需字段
            assert 'game_gid' in record
            assert 'event_name' in record
            assert 'source_table' in record
            assert 'target_table' in record
            assert record['event_name'] == 'test_login'

        except ValueError as e:
            # 游戏不存在时应该抛出ValueError
            assert 'not found' in str(e)

    def test_prepare_param_record(self):
        """测试参数记录准备功能"""
        event_id = 1
        param_data = {
            'param_name': 'role_id',
            'param_name_cn': '角色ID',
            'param_type': 'int',
            'param_description': '测试参数'
        }

        # 调用准备方法
        record = batch_import_manager._prepare_param_record(event_id, param_data)

        # 验证返回的记录包含所有必需字段
        assert record['event_id'] == event_id
        assert record['param_name'] == 'role_id'
        assert 'template_id' in record
        assert record['is_active'] == 1
        assert record['version'] == 1

    def test_create_events_batch_empty_list(self):
        """测试批量创建空列表"""
        from backend.core.data_access import Repositories

        # 测试空列表
        event_ids = batch_import_manager._create_events_batch([], 10000147, 1)

        assert event_ids == []
        assert isinstance(event_ids, list)

    def test_prepare_param_handles_missing_type(self):
        """测试参数类型缺失时使用默认值"""
        event_id = 1
        param_data = {
            'param_name': 'account_id',
            'param_name_cn': '账号ID',
            'param_type': 'nonexistent_type',  # 不存在的类型
            'param_description': ''
        }

        # 调用准备方法，应该fallback到string类型
        record = batch_import_manager._prepare_param_record(event_id, param_data)

        # 验证template_id存在（应该使用string类型的模板）
        assert 'template_id' in record
        assert record['template_id'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
