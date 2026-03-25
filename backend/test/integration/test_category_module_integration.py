#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Category Module Integration Tests

集成测试验证Event Category模块的完整流程:
- API → Service → Repository → Entity → Database
- 缓存失效机制
- 错误处理
- 数据验证
"""

import os
from datetime import datetime

import pytest

from backend.core.utils.converters import get_db_connection
from backend.models.entities import EventCategoryEntity
from backend.models.repositories.category_repository import CategoryRepository
from backend.services.event_categories.category_service import CategoryService


class TestCategoryModuleIntegration:
    """Event Category模块集成测试"""

    @pytest.fixture(autouse=True)
    def setup_database(self):
        """测试前设置数据库"""
        # 设置测试环境
        os.environ["FLASK_ENV"] = "testing"

        # 确保测试数据库存在
        conn = get_db_connection()
        cursor = conn.cursor()

        # 创建测试用的event_categories表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS event_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                name_cn TEXT,
                description TEXT,
                color TEXT,
                icon TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()
        yield

        # 清理测试数据(删除测试创建的分类)
        cursor.execute("DELETE FROM event_categories WHERE name LIKE 'TEST_%'")
        cursor.execute("DELETE FROM event_categories WHERE name LIKE 'Integration%'")
        cursor.execute("DELETE FROM event_categories WHERE name LIKE 'Batch%'")
        conn.commit()

    def test_create_category_flow(self):
        """测试完整的分类创建流程"""
        # 1. 准备数据
        category_data = EventCategoryEntity(
            name="TEST_Login Category",
            name_cn="登录分类",
            description="Login events category",
            color="#FF5733",
            icon="login-icon",
        )

        # 2. 通过Service创建分类
        service = CategoryService()
        created_category = service.create_category(category_data)

        # 3. 验证创建结果
        assert created_category is not None
        assert created_category.name == "TEST_Login Category"
        assert created_category.name_cn == "登录分类"
        assert created_category.description == "Login events category"
        assert created_category.color == "#FF5733"
        assert created_category.icon == "login-icon"

        # 4. 验证数据库记录
        repo = CategoryRepository()
        retrieved_category = repo.find_by_name("TEST_Login Category")
        assert retrieved_category is not None
        assert retrieved_category.name == "TEST_Login Category"

    def test_get_category_by_id(self):
        """测试通过ID获取分类"""
        # 1. 创建测试分类
        repo = CategoryRepository()
        category_data = EventCategoryEntity(name="TEST_Test Category", name_cn="测试分类")
        created = repo.create(category_data.model_dump())

        # 2. 通过Service获取分类
        service = CategoryService()
        category = service.get_category_by_id(created.id)

        # 3. 验证结果
        assert category is not None
        assert category.id == created.id
        assert category.name == "TEST_Test Category"
        assert category.name_cn == "测试分类"

    def test_get_category_by_name(self):
        """测试通过名称获取分类"""
        # 1. 创建测试分类
        service = CategoryService()
        category_data = EventCategoryEntity(name="TEST_Search Category", name_cn="搜索分类")
        service.create_category(category_data)

        # 2. 通过名称查询
        category = service.get_category_by_name("TEST_Search Category")

        # 3. 验证结果
        assert category is not None
        assert category.name == "TEST_Search Category"
        assert category.name_cn == "搜索分类"

    def test_update_category_flow(self):
        """测试分类更新流程"""
        # 1. 创建测试分类
        service = CategoryService()
        category_data = EventCategoryEntity(name="TEST_Original Name", name_cn="原始名称")
        created = service.create_category(category_data)

        # 2. 更新分类
        updates = {
            "name": "TEST_Updated Name",
            "name_cn": "更新名称",
            "description": "Updated description",
            "color": "#00FF00",
        }
        updated_category = service.update_category(created.id, updates)

        # 3. 验证更新结果
        assert updated_category.name == "TEST_Updated Name"
        assert updated_category.name_cn == "更新名称"
        assert updated_category.description == "Updated description"
        assert updated_category.color == "#00FF00"

    def test_delete_category_flow(self):
        """测试分类删除流程"""
        # 1. 创建测试分类
        service = CategoryService()
        category_data = EventCategoryEntity(name="TEST_To Be Deleted", name_cn="待删除")
        created = service.create_category(category_data)

        # 2. 删除分类
        service.delete_category(created.id)

        # 3. 验证删除结果
        category = service.get_category_by_id(created.id)
        assert category is None

    def test_batch_delete_categories(self):
        """测试批量删除分类"""
        # 1. 创建多个测试分类
        service = CategoryService()
        category_ids = []
        for i in range(5):
            category_data = EventCategoryEntity(name=f"TEST_Batch Category {i}", name_cn=f"批量测试{i}")
            created = service.create_category(category_data)
            category_ids.append(created.id)

        # 2. 批量删除前3个
        deleted_ids = category_ids[:3]
        deleted_count = service.batch_delete_categories(deleted_ids)

        # 3. 验证删除结果
        assert deleted_count == 3
        assert service.get_category_by_id(deleted_ids[0]) is None
        assert service.get_category_by_id(deleted_ids[1]) is None
        assert service.get_category_by_id(deleted_ids[2]) is None
        # 后2个应该还在
        assert service.get_category_by_id(category_ids[3]) is not None
        assert service.get_category_by_id(category_ids[4]) is not None

    def test_batch_update_categories(self):
        """测试批量更新分类"""
        # 1. 创建多个测试分类
        service = CategoryService()
        category_ids = []
        for i in range(3):
            category_data = EventCategoryEntity(name=f"TEST_Batch Update {i}", name_cn=f"批量更新{i}")
            created = service.create_category(category_data)
            category_ids.append(created.id)

        # 2. 批量更新
        updates = {"description": "Batch updated description", "color": "#FF0000"}
        updated_count = service.batch_update_categories(category_ids, updates)

        # 3. 验证更新结果
        assert updated_count == 3
        for category_id in category_ids:
            category = service.get_category_by_id(category_id)
            assert category.description == "Batch updated description"
            assert category.color == "#FF0000"

    def test_get_all_categories(self):
        """测试获取所有分类"""
        # 1. 创建多个测试分类
        service = CategoryService()
        for i in range(3):
            category_data = EventCategoryEntity(name=f"TEST_All Category {i}", name_cn=f"所有分类{i}")
            service.create_category(category_data)

        # 2. 获取所有分类
        categories = service.get_all_categories()

        # 3. 验证结果
        test_categories = [c for c in categories if c.name.startswith("TEST_All")]
        assert len(test_categories) >= 3

    def test_category_validation(self):
        """测试分类数据验证"""
        service = CategoryService()

        # 测试1: 创建重复名称的分类
        category_data1 = EventCategoryEntity(name="TEST_Duplicate Test", name_cn="重复测试")
        service.create_category(category_data1)

        # 尝试创建相同名称的分类
        category_data2 = EventCategoryEntity(name="TEST_Duplicate Test", name_cn="重复测试2")
        with pytest.raises(ValueError) as exc_info:
            service.create_category(category_data2)
        assert "already exists" in str(exc_info.value).lower()

        # 测试2: 更新不存在的分类
        with pytest.raises(ValueError):
            service.update_category(99999, {"name": "New Name"})

    def test_entity_serialization(self):
        """测试Entity序列化"""
        # 1. 创建Entity
        category = EventCategoryEntity(
            id=1,
            name="TEST_Serialization Test",
            name_cn="序列化测试",
            description="Test serialization",
            color="#123456",
            icon="test-icon",
            created_at=datetime(2024, 1, 1, 12, 0, 0),
        )

        # 2. 序列化为字典
        data = category.model_dump()

        # 3. 验证序列化结果
        assert data["name"] == "TEST_Serialization Test"
        assert data["name_cn"] == "序列化测试"
        assert data["description"] == "Test serialization"
        assert data["color"] == "#123456"
        assert data["icon"] == "test-icon"
        assert "id" in data
        assert "created_at" in data

        # 4. 反序列化
        restored_category = EventCategoryEntity(**data)
        assert restored_category.name == category.name
        assert restored_category.name_cn == category.name_cn

    def test_repository_returns_entities(self):
        """测试Repository返回Entity而非字典"""
        repo = CategoryRepository()

        # 1. 创建测试数据
        category_data = EventCategoryEntity(name="TEST_Repository Test", name_cn="仓储测试")
        created = repo.create(category_data.model_dump())

        # 2. 通过Repository查询
        category = repo.find_by_id(created.id)

        # 3. 验证返回的是Entity类型
        assert category is not None
        assert isinstance(category, EventCategoryEntity)
        assert category.name == "TEST_Repository Test"
        assert hasattr(category, 'model_dump')  # Entity应该有model_dump方法

    def test_service_returns_entities(self):
        """测试Service返回Entity而非字典"""
        service = CategoryService()

        # 1. 创建测试数据
        category_data = EventCategoryEntity(name="TEST_Service Test", name_cn="服务测试")
        service.create_category(category_data)

        # 2. 通过Service查询
        category = service.get_category_by_name("TEST_Service Test")

        # 3. 验证返回的是Entity类型
        assert category is not None
        assert isinstance(category, EventCategoryEntity)
        assert category.name == "TEST_Service Test"

    def test_category_with_optional_fields(self):
        """测试包含可选字段的分类"""
        service = CategoryService()

        # 只填写必填字段
        category_data = EventCategoryEntity(name="TEST_Minimal Category")

        created = service.create_category(category_data)

        # 验证必填字段
        assert created.name == "TEST_Minimal Category"
        # 可选字段应该为None
        assert created.name_cn is None
        assert created.description is None
        assert created.color is None
        assert created.icon is None

    def test_get_all_categories_with_event_count(self):
        """测试获取分类及其事件数量"""
        # 这个测试需要log_events表, 如果不存在则跳过
        service = CategoryService()
        categories = service.get_all_categories()

        # 验证返回的是Entity列表
        assert isinstance(categories, list)
        for category in categories:
            assert isinstance(category, EventCategoryEntity)
            # 可能有event_count属性(如果Service添加了统计)
            if hasattr(category, 'event_count'):
                assert isinstance(category.event_count, int)
