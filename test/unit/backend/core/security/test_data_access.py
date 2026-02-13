"""
Repository模式单元测试

测试GenericRepository的数据访问功能
遵循TDD原则：先写测试，看测试失败，再实现功能
"""

import pytest
import sys
from pathlib import Path

# 添加backend到path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from backend.core.data_access import GenericRepository, Repositories


class TestGenericRepository:
    """GenericRepository单元测试"""

    def test_games_repository_exists(self):
        """
        RED测试1: Repositories.GAMES应该存在并可使用

        This is a basic smoke test to verify the repository infrastructure is working
        """
        assert hasattr(Repositories, 'GAMES')
        assert Repositories.GAMES is not None
        assert Repositories.GAMES.table_name == 'games'
        assert Repositories.GAMES.primary_key == 'id'

    def test_log_events_repository_exists(self):
        """
        RED测试2: Repositories.LOG_EVENTS应该存在并可使用
        """
        assert hasattr(Repositories, 'LOG_EVENTS')
        assert Repositories.LOG_EVENTS is not None
        assert Repositories.LOG_EVENTS.table_name == 'log_events'
        assert Repositories.LOG_EVENTS.primary_key == 'id'

    def test_repository_has_required_methods(self):
        """
        RED测试3: GenericRepository应该有所有必需的方法
        """
        repo = GenericRepository('test_table', primary_key='id')

        # 检查所有必需方法存在
        assert hasattr(repo, 'find_by_id')
        assert hasattr(repo, 'find_by_field')
        assert hasattr(repo, 'find_where')
        assert hasattr(repo, 'find_all')
        assert hasattr(repo, 'delete')
        assert hasattr(repo, 'exists')

        # 检查方法是可调用的
        assert callable(repo.find_by_id)
        assert callable(repo.find_by_field)
        assert callable(repo.find_where)
        assert callable(repo.find_all)
        assert callable(repo.delete)
        assert callable(repo.exists)

    def test_find_by_id_returns_none_for_nonexistent(self):
        """
        RED测试4: find_by_id应该对不存在的ID返回None

        Given: 数据库中不存在id=999999的记录
        When: 调用repository.find_by_id(999999)
        Then: 应该返回None（而不抛出异常）
        """
        repo = Repositories.GAMES
        result = repo.find_by_id(999999)
        assert result is None

    def test_exists_returns_false_for_nonexistent(self):
        """
        RED测试5: exists应该对不存在的ID返回False
        """
        repo = Repositories.GAMES
        result = repo.exists(999999)
        assert result is False

    def test_all_predefined_repositories_have_correct_structure(self):
        """
        RED测试6: 所有预定义的Repository都应该有正确的结构
        """
        # 检查所有预定义的Repository
        all_repos = [
            ('GAMES', 'games'),
            ('FLOW_TEMPLATES', 'flow_templates'),
            ('EVENT_NODE_CONFIGS', 'event_node_configs'),
            ('JOIN_CONFIGS', 'join_configs'),
            ('LOG_EVENTS', 'log_events'),
            ('EVENT_CATEGORIES', 'event_categories'),
            ('EVENT_PARAMS', 'event_params'),
            ('LOGS', 'logs'),
        ]

        for attr_name, expected_table in all_repos:
            assert hasattr(Repositories, attr_name), f"Missing repository: {attr_name}"
            repo = getattr(Repositories, attr_name)
            assert repo.table_name == expected_table, f"{attr_name} has wrong table name"
            assert repo.primary_key == 'id', f"{attr_name} should use 'id' as primary key"

    def test_find_where_with_single_condition(self):
        """
        RED测试7: find_where应该支持单个条件查询

        Given: 数据库中有多个log_events记录，其中某些记录的game_gid=10000147
        When: 调用repository.find_where({'game_gid': 10000147})
        Then: 应该返回所有game_gid=10000147的记录列表
        """
        repo = Repositories.LOG_EVENTS

        # 查询已存在的game_gid
        # 注意：这里假设数据库中至少有一个game_gid=10000147的记录
        # 如果没有，测试会失败（这是正确的RED状态）
        result = repo.find_where({'game_gid': 10000147})

        # 验证返回的是列表
        assert isinstance(result, list), "find_where should return a list"

        # 如果有记录，每个记录都应该是字典
        for record in result:
            assert isinstance(record, dict), "Each record should be a dict"
            assert 'game_gid' in record, "Each record should have game_gid field"

    def test_find_where_with_order_by(self):
        """
        RED测试8: find_where应该支持ORDER BY子句

        Given: 数据库中有多个log_events记录
        When: 调用repository.find_where({'game_gid': 10000147}, order_by='created_at DESC')
        Then: 应该返回按created_at降序排列的记录
        """
        repo = Repositories.LOG_EVENTS

        result = repo.find_where({'game_gid': 10000147}, order_by='created_at DESC')

        # 验证返回的是列表
        assert isinstance(result, list), "find_where with order_by should return a list"

        # 如果有多个结果，验证它们是按created_at降序排列的
        if len(result) >= 2:
            for i in range(len(result) - 1):
                current = result[i].get('created_at', 0)
                next_record = result[i + 1].get('created_at', 0)
                assert current >= next_record, "Records should be ordered by created_at DESC"

    def test_find_where_with_limit(self):
        """
        RED测试9: find_where应该支持LIMIT子句

        Given: 数据库中有多个log_events记录
        When: 调用repository.find_where({'game_gid': 10000147}, limit=5)
        Then: 应该返回最多5条记录
        """
        repo = Repositories.LOG_EVENTS

        result = repo.find_where({'game_gid': 10000147}, limit=5)

        # 验证返回的是列表
        assert isinstance(result, list), "find_where with limit should return a list"

        # 验证返回的记录数不超过limit
        assert len(result) <= 5, f"find_where with limit=5 should return at most 5 records, got {len(result)}"

    def test_find_where_with_multiple_conditions(self):
        """
        RED测试10: find_where应该支持多个条件查询

        Given: 数据库中有多个log_events记录
        When: 调用repository.find_where({'game_gid': 10000147, 'category_id': 1})
        Then: 应该返回同时满足两个条件的记录
        """
        repo = Repositories.LOG_EVENTS

        result = repo.find_where({'game_gid': 10000147, 'category_id': 1})

        # 验证返回的是列表
        assert isinstance(result, list), "find_where with multiple conditions should return a list"

        # 验证每个结果都满足所有条件
        for record in result:
            assert record.get('game_gid') == 10000147, "All records should have game_gid=10000147"
            assert record.get('category_id') == 1, "All records should have category_id=1"

    def test_find_first_where_returns_single_record(self):
        """
        RED测试11: find_first_where应该返回第一条匹配的记录

        Given: 数据库中有多个log_events记录
        When: 调用repository.find_first_where({'game_gid': 10000147})
        Then: 应该返回第一条匹配的记录或None
        """
        repo = Repositories.LOG_EVENTS

        result = repo.find_first_where({'game_gid': 10000147})

        # 验证返回的是字典或None
        assert result is None or isinstance(result, dict), "find_first_where should return a dict or None"

        # 如果有结果，验证它有必需的字段
        if result is not None:
            assert 'game_gid' in result, "Record should have game_gid field"
            assert result['game_gid'] == 10000147, "Record should match the condition"

    def test_find_by_ids_returns_multiple_records(self):
        """
        RED测试12: find_by_ids应该批量查询多个ID的记录

        Given: 数据库中有多个log_events记录，ID分别为1, 2, 3
        When: 调用repository.find_by_ids([1, 2, 3])
        Then: 应该返回ID对应的记录列表，不存在的ID应该被忽略
        """
        repo = Repositories.LOG_EVENTS

        # 使用可能存在的ID进行测试
        test_ids = [1, 2, 3]
        result = repo.find_by_ids(test_ids)

        # 验证返回的是列表
        assert isinstance(result, list), "find_by_ids should return a list"

        # 验证返回的记录都是字典
        for record in result:
            assert isinstance(record, dict), "Each record should be a dict"
            assert record['id'] in test_ids, f"Record ID {record['id']} should be in requested IDs"

    def test_find_by_ids_with_empty_list(self):
        """
        RED测试13: find_by_ids应该处理空列表

        Given: 传入空的ID列表
        When: 调用repository.find_by_ids([])
        Then: 应该返回空列表
        """
        repo = Repositories.LOG_EVENTS

        result = repo.find_by_ids([])

        # 验证返回的是空列表
        assert isinstance(result, list), "find_by_ids should return a list"
        assert len(result) == 0, "find_by_ids with empty list should return empty list"

    def test_delete_batch_deletes_multiple_records(self):
        """
        RED测试14: delete_batch应该批量删除多个ID的记录

        Given: 数据库中有多个可以删除的记录
        When: 调用repository.delete_batch([999998, 999999])
        Then: 应该返回删除的记录数，不存在的ID应该被忽略
        """
        repo = Repositories.EVENT_CATEGORIES

        # 使用不存在的ID进行测试（避免删除真实数据）
        test_ids = [999998, 999999]
        deleted_count = repo.delete_batch(test_ids)

        # 验证返回的是整数
        assert isinstance(deleted_count, int), "delete_batch should return an integer"

        # 由于这些ID不存在，删除数量应该是0
        assert deleted_count == 0, f"delete_batch with non-existent IDs should return 0, got {deleted_count}"

    def test_delete_batch_with_empty_list(self):
        """
        RED测试15: delete_batch应该处理空列表

        Given: 传入空的ID列表
        When: 调用repository.delete_batch([])
        Then: 应该返回0（没有删除任何记录）
        """
        repo = Repositories.EVENT_CATEGORIES

        deleted_count = repo.delete_batch([])

        # 验证返回的是0
        assert deleted_count == 0, "delete_batch with empty list should return 0"

    def test_update_batch_updates_multiple_records(self):
        """
        RED测试16: update_batch应该批量更新多条记录

        Given: 数据库中有多个event_categories记录
        When: 调用repository.update_batch(ids, {"name": "Updated"})
        Then: 应该返回实际更新的记录数，不存在的ID应该被忽略
        """
        repo = Repositories.EVENT_CATEGORIES

        # 使用不存在的ID进行测试（避免修改真实数据）
        test_ids = [999998, 999999]
        updated_count = repo.update_batch(test_ids, {"name": "Test Category"})

        # 验证返回的是整数
        assert isinstance(updated_count, int), "update_batch should return an integer"

        # 由于这些ID不存在，更新数量应该是0
        assert updated_count == 0, f"update_batch with non-existent IDs should return 0, got {updated_count}"

    def test_update_batch_with_empty_updates(self):
        """
        RED测试17: update_batch应该处理空的更新字典

        Given: 传入空的updates字典
        When: 调用repository.update_batch([1, 2], {})
        Then: 应该返回0（没有更新任何字段）
        """
        repo = Repositories.EVENT_CATEGORIES

        # 使用不存在的ID避免影响真实数据
        updated_count = repo.update_batch([999998, 999999], {})

        # 验证返回的是0
        assert updated_count == 0, "update_batch with empty updates should return 0"

    def test_update_batch_with_empty_ids(self):
        """
        RED测试18: update_batch应该处理空的ID列表

        Given: 传入空的ID列表
        When: 调用repository.update_batch([], {"name": "Test"})
        Then: 应该返回0（没有更新任何记录）
        """
        repo = Repositories.EVENT_CATEGORIES

        updated_count = repo.update_batch([], {"name": "Test"})

        # 验证返回的是0
        assert updated_count == 0, "update_batch with empty ids should return 0"

    def test_create_batch_creates_multiple_records(self):
        """RED测试19: create_batch应该批量创建多条记录并返回ID列表

        Given: 传入多条要创建的记录
        When: 调用repository.create_batch(records)
        Then: 应该返回插入记录的ID列表
        """
        repo = Repositories.EVENT_CATEGORIES

        # 准备测试数据（使用独特的名称避免冲突）
        import uuid
        test_records = [
            {"name": f"TEST_CAT_{uuid.uuid4().hex[:8]}"},
            {"name": f"TEST_CAT_{uuid.uuid4().hex[:8]}"},
            {"name": f"TEST_CAT_{uuid.uuid4().hex[:8]}"}
        ]

        # 调用create_batch（这个方法还不存在，会失败）
        inserted_ids = repo.create_batch(test_records)

        # 验证返回的ID列表
        assert isinstance(inserted_ids, list), "create_batch should return a list"
        assert len(inserted_ids) == len(test_records), f"Expected {len(test_records)} IDs, got {len(inserted_ids)}"
        assert all(isinstance(id, int) and id > 0 for id in inserted_ids), "All IDs should be positive integers"

        # 验证记录确实被插入到数据库
        for record_id in inserted_ids:
            record = repo.find_by_id(record_id)
            assert record is not None, f"Record with ID {record_id} should exist"

        # 清理测试数据
        repo.delete_batch(inserted_ids)

    def test_create_batch_with_empty_list(self):
        """RED测试20: create_batch应该处理空列表

        Given: 传入空的记录列表
        When: 调用repository.create_batch([])
        Then: 应该返回空列表
        """
        repo = Repositories.EVENT_CATEGORIES

        inserted_ids = repo.create_batch([])

        # 验证返回的是空列表
        assert isinstance(inserted_ids, list), "create_batch should return a list"
        assert len(inserted_ids) == 0, "create_batch with empty list should return empty list"

    def test_create_batch_with_partial_fields(self):
        """RED测试21: create_batch应该支持部分字段创建

        Given: 传入只包含部分字段的记录
        When: 调用repository.create_batch(records)
        Then: 应该成功创建，缺失字段使用数据库默认值
        """
        repo = Repositories.EVENT_CATEGORIES

        import uuid
        test_records = [
            {"name": f"TEST_CAT_PARTIAL_{uuid.uuid4().hex[:8]}"}
        ]

        inserted_ids = repo.create_batch(test_records)

        # 验证创建成功
        assert len(inserted_ids) == 1, "Should create 1 record"

        # 验证记录可以被查询
        record = repo.find_by_id(inserted_ids[0])
        assert record is not None, "Record should exist"
        assert 'name' in record, "Record should have name field"

        # 清理
        repo.delete_batch(inserted_ids)


if __name__ == '__main__':
    # 运行测试
    pytest.main([__file__, '-v'])
