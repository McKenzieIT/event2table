#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Game Module Integration Tests

集成测试验证Game模块的完整流程:
- API → Service → Repository → Entity → Database
- 缓存失效机制
- 错误处理
- 数据验证
"""

import os
import pytest
from datetime import datetime
from backend.models.entities import GameEntity
from backend.services.games.game_service import GameService
from backend.models.repositories.games import GameRepository
from backend.core.utils.converters import get_db_connection


class TestGameModuleIntegration:
    """Game模块集成测试"""

    @pytest.fixture(autouse=True)
    def setup_database(self):
        """测试前设置数据库"""
        # 设置测试环境
        os.environ["FLASK_ENV"] = "testing"

        # 确保测试数据库存在
        conn = get_db_connection()
        cursor = conn.cursor()

        # 创建测试用的游戏表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gid INTEGER UNIQUE NOT NULL,
                name TEXT NOT NULL,
                ods_db TEXT NOT NULL CHECK(ods_db IN ('ieu_ods', 'overseas_ods')),
                description TEXT,
                dwd_prefix TEXT DEFAULT 'dwd',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()
        yield

        # 清理测试数据
        cursor.execute("DELETE FROM games WHERE cast(gid as integer) >= 91000000")
        conn.commit()

    def test_create_game_flow(self):
        """测试完整的游戏创建流程"""
        # 1. 准备数据
        game_data = GameEntity(
            gid=91000001,
            name="Integration Test Game",
            ods_db="ieu_ods",
            description="Test game for integration testing",
        )

        # 2. 通过Service创建游戏
        service = GameService()
        created_game = service.create_game(game_data)

        # 3. 验证创建结果
        assert created_game is not None
        assert created_game.gid == 91000001
        assert created_game.name == "Integration Test Game"
        assert created_game.ods_db == "ieu_ods"

        # 4. 验证数据库记录
        repo = GameRepository()
        retrieved_game = repo.find_by_gid(91000001)
        assert retrieved_game is not None
        assert retrieved_game.gid == 91000001

    def test_get_game_by_gid(self):
        """测试通过GID获取游戏"""
        # 1. 创建测试游戏(使用Service以确保Bloom Filter更新)
        service = GameService()
        game_data = GameEntity(gid=91000002, name="Test Game", ods_db="ieu_ods")
        created_game = service.create_game(game_data)

        # 2. 通过Service获取游戏
        game = service.get_game_by_gid(91000002)

        # 3. 验证结果
        assert game is not None
        assert game.gid == 91000002
        assert game.name == "Test Game"

    def test_update_game_flow(self):
        """测试游戏更新流程"""
        # 1. 创建测试游戏
        service = GameService()
        game_data = GameEntity(gid=91000003, name="Original Name", ods_db="ieu_ods")
        service.create_game(game_data)

        # 2. 更新游戏
        updates = {"name": "Updated Name"}
        updated_game = service.update_game(91000003, updates)

        # 3. 验证更新结果
        assert updated_game.name == "Updated Name"

    def test_delete_game_flow(self):
        """测试游戏删除流程"""
        # 1. 创建测试游戏
        service = GameService()
        game_data = GameEntity(gid=91000004, name="To Be Deleted", ods_db="ieu_ods")
        service.create_game(game_data)

        # 2. 删除游戏
        service.delete_game(91000004)

        # 3. 验证删除结果
        game = service.get_game_by_gid(91000004)
        assert game is None

    def test_batch_delete_games(self):
        """测试批量删除游戏"""
        # 1. 创建多个测试游戏
        service = GameService()
        for i in range(5):
            game_data = GameEntity(gid=91000010 + i, name=f"Batch Test Game {i}", ods_db="ieu_ods")
            service.create_game(game_data)

        # 2. 批量删除
        game_gids = [91000010, 91000011, 91000012]
        deleted_count = service.batch_delete_games(game_gids)

        # 3. 验证删除结果
        assert deleted_count == 3
        assert service.get_game_by_gid(91000010) is None
        assert service.get_game_by_gid(91000011) is None
        assert service.get_game_by_gid(91000012) is None

    def test_game_validation(self):
        """测试游戏数据验证"""
        service = GameService()

        # 测试1: 创建重复GID的游戏
        game_data1 = GameEntity(gid=91000020, name="Game 1", ods_db="ieu_ods")
        service.create_game(game_data1)

        # 尝试创建相同GID的游戏
        game_data2 = GameEntity(gid=91000020, name="Game 2", ods_db="ieu_ods")
        with pytest.raises(ValueError) as exc_info:
            service.create_game(game_data2)
        assert "already exists" in str(exc_info.value)

        # 测试2: 无效的GID
        with pytest.raises(ValueError):
            service.get_game_by_gid(-1)

    def test_get_all_games_with_stats(self):
        """测试获取所有游戏及统计信息"""
        # 1. 创建多个测试游戏
        service = GameService()
        for i in range(3):
            game_data = GameEntity(gid=91000030 + i, name=f"Stats Test Game {i}", ods_db="ieu_ods")
            service.create_game(game_data)

        # 2. 获取所有游戏及统计
        games = service.get_all_games(include_stats=True)

        # 3. 验证结果
        assert len(games) >= 3
        # 检查是否有event_count字段
        test_games = [g for g in games if g.gid >= 91000030]
        assert len(test_games) == 3
        # 所有游戏都应该有event_count属性
        for game in test_games:
            assert hasattr(game, 'event_count')

    def test_entity_serialization(self):
        """测试Entity序列化"""
        # 1. 创建Entity
        game = GameEntity(
            id=1,
            gid=91000099,
            name="Serialization Test",
            ods_db="ieu_ods",
            created_at=datetime(2024, 1, 1, 12, 0, 0),
        )

        # 2. 序列化为字典
        data = game.model_dump()

        # 3. 验证序列化结果
        assert data["gid"] == 91000099
        assert data["name"] == "Serialization Test"
        assert data["ods_db"] == "ieu_ods"
        assert "id" in data
        assert "created_at" in data

        # 4. 反序列化
        restored_game = GameEntity(**data)
        assert restored_game.gid == game.gid
        assert restored_game.name == game.name

    def test_repository_returns_entities(self):
        """测试Repository返回Entity而非字典"""
        repo = GameRepository()

        # 1. 创建测试数据
        game_data = GameEntity(gid=91000050, name="Repository Test", ods_db="ieu_ods")
        repo.create(game_data.model_dump())

        # 2. 通过Repository查询
        game = repo.find_by_gid(91000050)

        # 3. 验证返回的是Entity类型
        assert game is not None
        assert isinstance(game, GameEntity)
        assert game.gid == 91000050
        assert hasattr(game, 'model_dump')  # Entity应该有model_dump方法

    def test_service_returns_entities(self):
        """测试Service返回Entity而非字典"""
        service = GameService()

        # 1. 创建测试数据
        game_data = GameEntity(gid=91000051, name="Service Test", ods_db="ieu_ods")
        service.create_game(game_data)

        # 2. 通过Service查询
        game = service.get_game_by_gid(91000051)

        # 3. 验证返回的是Entity类型
        assert game is not None
        assert isinstance(game, GameEntity)
        assert game.gid == 91000051
