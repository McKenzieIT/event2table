#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for HQL Version Service

测试HQL版本管理服务的功能
"""

import pytest
from unittest.mock import MagicMock, patch

from backend.services.hql_version_service import HQLVersionService
from backend.models.repositories.hql_version_repository import HQLVersionRepository


class TestHQLVersionService:
    """测试HQLVersionService类"""

    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return HQLVersionService()

    @pytest.fixture
    def mock_repository(self):
        """模拟仓储"""
        with patch.object(HQLVersionService, '__init__', lambda self: None):
            service = HQLVersionService()
            service.repository = MagicMock(spec=HQLVersionRepository)
            service.invalidator = MagicMock()
            return service

    @pytest.fixture
    def sample_version(self):
        """示例版本数据"""
        return {
            "id": 1,
            "event_id": 123,
            "hql_content": "CREATE OR REPLACE VIEW test AS SELECT * FROM table",
            "version_number": 1,
            "change_description": "Initial version",
            "created_by": "user@example.com",
            "created_at": "2026-03-20 10:00:00"
        }

    def test_save_version_first_version(self, mock_repository):
        """测试保存第一个版本"""
        mock_repository.repository.get_latest_version.return_value = None
        mock_repository.repository.save_version.return_value = {
            "id": 1,
            "event_id": 123,
            "hql_content": "CREATE OR REPLACE VIEW test AS SELECT * FROM table",
            "version_number": 1,
            "change_description": "Initial version",
            "created_by": "user@example.com",
            "created_at": "2026-03-20 10:00:00"
        }

        result = mock_repository.save_version(
            event_id=123,
            hql_content="CREATE OR REPLACE VIEW test AS SELECT * FROM table",
            change_description="Initial version",
            created_by="user@example.com"
        )

        assert result is not None
        assert result["version_number"] == 1
        mock_repository.repository.save_version.assert_called_once()

    def test_save_version_second_version(self, mock_repository):
        """测试保存第二个版本"""
        mock_repository.repository.get_latest_version.return_value = {
            "version_number": 1
        }
        mock_repository.repository.save_version.return_value = {
            "id": 2,
            "event_id": 123,
            "hql_content": "CREATE OR REPLACE VIEW test AS SELECT id FROM table",
            "version_number": 2,
            "change_description": "Updated SELECT",
            "created_by": "user@example.com",
            "created_at": "2026-03-20 11:00:00"
        }

        result = mock_repository.save_version(
            event_id=123,
            hql_content="CREATE OR REPLACE VIEW test AS SELECT id FROM table",
            change_description="Updated SELECT",
            created_by="user@example.com"
        )

        assert result is not None
        assert result["version_number"] == 2

    def test_save_version_empty_content(self, mock_repository):
        """测试保存空内容 - 应抛出ValueError"""
        with pytest.raises(ValueError, match="HQL content cannot be empty"):
            mock_repository.save_version(
                event_id=123,
                hql_content="",
                change_description="Test",
                created_by="user@example.com"
            )

    def test_save_version_whitespace_content(self, mock_repository):
        """测试保存空白内容 - 应抛出ValueError"""
        with pytest.raises(ValueError, match="HQL content cannot be empty"):
            mock_repository.save_version(
                event_id=123,
                hql_content="   ",
                change_description="Test",
                created_by="user@example.com"
            )

    def test_compare_versions_success(self, mock_repository, sample_version):
        """测试成功比较两个版本"""
        version_1 = {**sample_version, "id": 1, "version_number": 1}
        version_2 = {**sample_version, "id": 2, "version_number": 2}

        mock_repository.repository.find_by_id.side_effect = [version_1, version_2]
        mock_repository.repository.compare_versions.return_value = {
            "version_1": {"id": 1, "version_number": 1},
            "version_2": {"id": 2, "version_number": 2},
            "diff": "- SELECT *\n+ SELECT id\n",
            "additions": 1,
            "deletions": 1,
            "changes": 0
        }

        result = mock_repository.compare_versions(1, 2)

        assert "version_1" in result
        assert "version_2" in result
        assert "diff" in result
        assert result["additions"] == 1
        assert result["deletions"] == 1

    def test_compare_versions_version_not_found(self, mock_repository):
        """测试比较不存在的版本 - 应抛出ValueError"""
        mock_repository.repository.find_by_id.return_value = None

        with pytest.raises(ValueError, match="Version 1 not found"):
            mock_repository.compare_versions(1, 2)

    def test_get_version_history(self, mock_repository, sample_version):
        """测试获取版本历史"""
        mock_repository.repository.find_by_event_id.return_value = [
            {**sample_version, "version_number": 2},
            {**sample_version, "version_number": 1}
        ]

        result = mock_repository.get_version_history(event_id=123)

        assert len(result) == 2
        assert result[0]["version_number"] == 2  # 应该降序排列

    def test_get_version_history_with_limit(self, mock_repository, sample_version):
        """测试获取版本历史带限制"""
        mock_repository.repository.find_by_event_id.return_value = [
            {**sample_version, "version_number": i} for i in range(1, 11)
        ]

        result = mock_repository.get_version_history(event_id=123, limit=5)

        assert len(result) == 5

    def test_get_version_history_invalid_event_id(self, mock_repository):
        """测试获取无效事件的版本历史 - 应抛出ValueError"""
        with pytest.raises(ValueError, match="Invalid event_id"):
            mock_repository.get_version_history(event_id=0)

        with pytest.raises(ValueError, match="Invalid event_id"):
            mock_repository.get_version_history(event_id=-1)

    def test_get_latest_version(self, mock_repository, sample_version):
        """测试获取最新版本"""
        mock_repository.repository.get_latest_version.return_value = sample_version

        result = mock_repository.get_latest_version(event_id=123)

        assert result is not None
        assert result["version_number"] == 1

    def test_get_latest_version_not_found(self, mock_repository):
        """测试获取不存在事件的最新版本"""
        mock_repository.repository.get_latest_version.return_value = None

        result = mock_repository.get_latest_version(event_id=999)

        assert result is None

    def test_rollback_to_version_success(self, mock_repository, sample_version):
        """测试成功回滚到指定版本"""
        target_version = {**sample_version, "id": 1, "version_number": 1}
        latest_version = {**sample_version, "id": 2, "version_number": 2}

        mock_repository.repository.find_by_id.return_value = target_version
        mock_repository.repository.get_latest_version.return_value = latest_version
        mock_repository.repository.rollback_to_version.return_value = {
            "id": 3,
            "event_id": 123,
            "hql_content": target_version["hql_content"],
            "version_number": 3,
            "change_description": "Rollback to version 1",
            "created_by": "user@example.com",
            "created_at": "2026-03-20 12:00:00"
        }

        result = mock_repository.rollback_to_version(
            event_id=123,
            target_version_id=1,
            rolled_back_by="user@example.com"
        )

        assert result is not None
        assert result["version_number"] == 3
        assert "Rollback to version 1" in result["change_description"]

    def test_rollback_to_version_target_not_found(self, mock_repository):
        """测试回滚到不存在的版本 - 应抛出ValueError"""
        mock_repository.repository.find_by_id.return_value = None

        with pytest.raises(ValueError, match="Target version 1 not found"):
            mock_repository.rollback_to_version(
                event_id=123,
                target_version_id=1,
                rolled_back_by="user@example.com"
            )

    def test_rollback_to_version_wrong_event(self, mock_repository, sample_version):
        """测试回滚到不属于指定事件的版本 - 应抛出ValueError"""
        target_version = {**sample_version, "id": 1, "event_id": 456}

        mock_repository.repository.find_by_id.return_value = target_version

        with pytest.raises(ValueError, match="does not belong to event 123"):
            mock_repository.rollback_to_version(
                event_id=123,
                target_version_id=1,
                rolled_back_by="user@example.com"
            )

    def test_get_version_count(self, mock_repository):
        """测试获取版本总数"""
        mock_repository.repository.get_version_count.return_value = 5

        result = mock_repository.get_version_count(event_id=123)

        assert result == 5

    def test_get_version_by_number(self, mock_repository, sample_version):
        """测试根据版本号获取版本"""
        mock_repository.repository.find_by_event_and_version.return_value = sample_version

        result = mock_repository.get_version_by_number(event_id=123, version_number=1)

        assert result is not None
        assert result["version_number"] == 1


class TestHQLVersionRepository:
    """测试HQLVersionRepository类"""

    @pytest.fixture
    def repository(self):
        """创建仓储实例"""
        return HQLVersionRepository()

    @pytest.fixture
    def sample_version(self):
        """示例版本数据"""
        return {
            "id": 1,
            "event_id": 123,
            "hql_content": "CREATE OR REPLACE VIEW test AS SELECT * FROM table",
            "version_number": 1,
            "change_description": "Initial version",
            "created_by": "user@example.com",
            "created_at": "2026-03-20 10:00:00"
        }

    def test_calculate_diff_identical_content(self, repository):
        """测试计算相同内容的差异"""
        content = "SELECT * FROM table"
        result = repository._calculate_diff(content, content)

        assert result["additions"] == 0
        assert result["deletions"] == 0
        assert result["changes"] == 0

    def test_calculate_diff_different_content(self, repository):
        """测试计算不同内容的差异"""
        content1 = "SELECT * FROM table"
        content2 = "SELECT id FROM table"

        result = repository._calculate_diff(content1, content2)

        assert result["additions"] > 0
        assert result["deletions"] > 0
        assert "diff_output" in result

    def test_calculate_diff_multiline(self, repository):
        """测试计算多行内容的差异"""
        content1 = """SELECT *
FROM table
WHERE id = 1"""

        content2 = """SELECT id, name
FROM table
WHERE id = 1 AND active = 1"""

        result = repository._calculate_diff(content1, content2)

        assert "diff_output" in result
        assert len(result["diff_output"]) > 0

    def test_compare_versions_both_exist(self, repository, sample_version):
        """测试比较两个存在的版本"""
        version_1 = {**sample_version, "id": 1, "hql_content": "SELECT * FROM table"}
        version_2 = {**sample_version, "id": 2, "hql_content": "SELECT id FROM table"}

        with patch.object(repository, 'find_by_id', side_effect=[version_1, version_2]):
            result = repository.compare_versions(1, 2)

            assert "version_1" in result
            assert "version_2" in result
            assert "diff" in result
            assert "additions" in result
            assert "deletions" in result

    def test_compare_versions_one_missing(self, repository, sample_version):
        """测试比较一个缺失的版本"""
        version_1 = {**sample_version, "id": 1, "hql_content": "SELECT * FROM table"}

        with patch.object(repository, 'find_by_id', side_effect=[version_1, None]):
            result = repository.compare_versions(1, 2)

            assert "error" in result
            assert "version_1" in result
            assert "version_2" is None

    def test_save_version_creates_record(self, repository):
        """测试保存版本创建记录"""
        with patch.object(repository, '_clear_event_cache'), \
             patch('backend.models.repositories.hql_version_repository.get_db_connection') as mock_get_conn:
            
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.lastrowid = 1
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            with patch.object(repository, 'find_by_id', return_value={
                "id": 1,
                "event_id": 123,
                "hql_content": "SELECT * FROM table",
                "version_number": 1,
                "change_description": "Test",
                "created_by": "user@example.com",
                "created_at": "2026-03-20 10:00:00"
            }):
                result = repository.save_version(
                    event_id=123,
                    hql_content="SELECT * FROM table",
                    version_number=1,
                    change_description="Test",
                    created_by="user@example.com"
                )

                assert result is not None
                assert result["id"] == 1
                mock_cursor.execute.assert_called_once()
                mock_conn.commit.assert_called_once()

    def test_rollback_to_version_creates_new_version(self, repository, sample_version):
        """测试回滚创建新版本"""
        target_version = {**sample_version, "id": 1, "version_number": 1}
        latest_version = {**sample_version, "id": 2, "version_number": 2}

        with patch.object(repository, 'find_by_id', return_value=target_version), \
             patch.object(repository, 'get_latest_version', return_value=latest_version), \
             patch.object(repository, 'save_version', return_value={
                 "id": 3,
                 "event_id": 123,
                 "hql_content": target_version["hql_content"],
                 "version_number": 3,
                 "change_description": "Rollback to version 1",
                 "created_by": "user@example.com",
                 "created_at": "2026-03-20 12:00:00"
             }) as mock_save:
            
            result = repository.rollback_to_version(
                event_id=123,
                target_version_id=1,
                rolled_back_by="user@example.com"
            )

            assert result is not None
            assert result["version_number"] == 3
            mock_save.assert_called_once()

    def test_rollback_to_version_target_not_found(self, repository):
        """测试回滚到不存在的目标版本"""
        with patch.object(repository, 'find_by_id', return_value=None):
            result = repository.rollback_to_version(
                event_id=123,
                target_version_id=1,
                rolled_back_by="user@example.com"
            )

            assert result is None

    def test_rollback_to_version_no_latest_version(self, repository, sample_version):
        """测试回滚但没有最新版本"""
        target_version = {**sample_version, "id": 1, "version_number": 1}

        with patch.object(repository, 'find_by_id', return_value=target_version), \
             patch.object(repository, 'get_latest_version', return_value=None):
            
            result = repository.rollback_to_version(
                event_id=123,
                target_version_id=1,
                rolled_back_by="user@example.com"
            )

            assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
