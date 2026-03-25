#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HQL Template Repository 单元测试
"""

import pytest

from backend.models.repositories.hql_template_repository import HQLTemplateRepository


@pytest.fixture(autouse=True)
def clean_test_data(db):
    """在每个测试前清理测试数据"""
    db.execute("DELETE FROM hql_generation_templates WHERE template_name LIKE 'TEST_%'")
    db.commit()
    yield


class TestHQLTemplateRepository:
    """HQL模板仓储测试类"""

    def setup_method(self):
        """设置测试环境"""
        self.repo = HQLTemplateRepository()

    def test_find_by_name(self, db):
        """测试根据名称查找模板"""
        # 创建测试模板
        template_id = self.repo.create_template(
            template_name="TEST_find_by_name",
            display_name="Test Find By Name",
            template_type="test",
            template_content="-- Test content",
        )

        # 查找模板
        template = self.repo.find_by_name("TEST_find_by_name")

        assert template is not None
        assert template["template_name"] == "TEST_find_by_name"
        assert template["display_name"] == "Test Find By Name"

    def test_find_by_type(self):
        """测试根据类型查找模板"""
        # 创建多个测试模板
        self.repo.create_template(
            template_name="TEST_type_1",
            display_name="Test Type 1",
            template_type="union",
            template_content="-- Union content",
        )
        self.repo.create_template(
            template_name="TEST_type_2",
            display_name="Test Type 2",
            template_type="union",
            template_content="-- Union content 2",
        )
        self.repo.create_template(
            template_name="TEST_type_3",
            display_name="Test Type 3",
            template_type="join",
            template_content="-- Join content",
        )

        # 查找union类型模板
        union_templates = self.repo.find_by_type("union")

        assert len(union_templates) >= 2
        assert all(t["template_type"] == "union" for t in union_templates)

    def test_find_system_templates(self):
        """测试查找系统模板"""
        # 创建系统模板和用户模板
        self.repo.create_template(
            template_name="TEST_system_1",
            display_name="Test System 1",
            template_type="test",
            template_content="-- System content",
            is_system=True,
        )
        self.repo.create_template(
            template_name="TEST_user_1",
            display_name="Test User 1",
            template_type="test",
            template_content="-- User content",
            is_system=False,
        )

        # 查找系统模板
        system_templates = self.repo.find_system_templates()

        assert len(system_templates) >= 1
        assert all(t["is_system"] == 1 for t in system_templates)

    def test_find_user_templates(self):
        """测试查找用户模板"""
        # 创建用户模板
        self.repo.create_template(
            template_name="TEST_user_template",
            display_name="Test User Template",
            template_type="test",
            template_content="-- User content",
            is_system=False,
        )

        # 查找用户模板
        user_templates = self.repo.find_user_templates()

        assert len(user_templates) >= 1
        assert all(t["is_system"] == 0 for t in user_templates)

    def test_search_by_name(self):
        """测试搜索模板"""
        # 创建测试模板
        self.repo.create_template(
            template_name="TEST_search_keyword",
            display_name="Search Keyword Test",
            template_type="test",
            template_content="-- Search content",
            description="Template for searching",
        )

        # 搜索关键词
        results = self.repo.search_by_name("keyword")

        assert len(results) >= 1
        assert any(
            "keyword" in t["template_name"].lower() or "keyword" in t["display_name"].lower()
            for t in results
        )

    def test_get_types(self):
        """测试获取所有模板类型"""
        # 创建不同类型的模板
        self.repo.create_template(
            template_name="TEST_type_union",
            display_name="Test Union",
            template_type="union",
            template_content="-- Union",
        )
        self.repo.create_template(
            template_name="TEST_type_join",
            display_name="Test Join",
            template_type="join",
            template_content="-- Join",
        )

        # 获取类型列表
        types = self.repo.get_types()

        assert isinstance(types, list)
        assert "union" in types
        assert "join" in types

    def test_create_template(self):
        """测试创建模板"""
        template_id = self.repo.create_template(
            template_name="TEST_create",
            display_name="Test Create",
            template_type="test",
            template_content="-- Test content",
            variables='{"var1": "value1"}',
            description="Test description",
            is_system=False,
        )

        assert template_id > 0

        # 验证模板已创建
        template = self.repo.find_by_id(template_id)
        assert template is not None
        assert template["template_name"] == "TEST_create"
        assert template["variables"] == '{"var1": "value1"}'

    def test_update_template(self):
        """测试更新模板"""
        # 创建模板
        template_id = self.repo.create_template(
            template_name="TEST_update",
            display_name="Test Update",
            template_type="test",
            template_content="-- Original content",
        )

        # 更新模板
        success = self.repo.update_template(
            template_id=template_id,
            display_name="Updated Display Name",
            template_content="-- Updated content",
            description="Updated description",
        )

        assert success is True

        # 验证更新
        template = self.repo.find_by_id(template_id)
        assert template["display_name"] == "Updated Display Name"
        assert template["template_content"] == "-- Updated content"
        assert template["description"] == "Updated description"

    def test_delete_template(self):
        """测试删除用户模板"""
        # 创建用户模板
        template_id = self.repo.create_template(
            template_name="TEST_delete",
            display_name="Test Delete",
            template_type="test",
            template_content="-- To be deleted",
            is_system=False,
        )

        # 确认模板已创建
        template_before = self.repo.find_by_id(template_id)
        assert template_before is not None, "Template should be created before deletion"

        # 删除模板
        success = self.repo.delete_template(template_id)

        assert success is True, "delete_template should return True"

        # 验证已删除 - delete_template returns True on successful deletion
        # The template should no longer exist
        template = self.repo.find_by_id(template_id)
        assert template is None, "Template should be deleted"

    def test_delete_system_template_forbidden(self):
        """测试禁止删除系统模板"""
        # 创建系统模板
        template_id = self.repo.create_template(
            template_name="TEST_system_delete",
            display_name="Test System Delete",
            template_type="test",
            template_content="-- System template",
            is_system=True,
        )

        # 尝试删除系统模板(应该失败)
        with pytest.raises(ValueError, match="Cannot delete system template"):
            self.repo.delete_template(template_id)

    def test_get_all(self):
        """测试获取所有模板"""
        # 创建多个模板
        self.repo.create_template(
            template_name="TEST_all_1",
            display_name="Test All 1",
            template_type="test",
            template_content="-- Test 1",
        )
        self.repo.create_template(
            template_name="TEST_all_2",
            display_name="Test All 2",
            template_type="test",
            template_content="-- Test 2",
        )

        # 获取所有模板
        all_templates = self.repo.find_all()

        assert len(all_templates) >= 2
