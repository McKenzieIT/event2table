#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Join Config Service - 业务逻辑层 (精简架构)

提供Join Config相关的业务逻辑服务
- 使用统一Entity模型 (JoinConfigEntity)
- 移除DDD抽象,简化业务逻辑
- 集成缓存防护和失效机制
"""

from typing import List, Optional
import logging
from backend.models.entities import JoinConfigEntity
from backend.models.repositories.join_config_repository import JoinConfigRepository
from backend.core.cache.cache_system import CacheInvalidator, cached
from backend.core.utils.business_helpers import validate_game_gid

logger = logging.getLogger(__name__)


class JoinConfigService:
    """Join Config业务服务 (精简架构)"""

    def __init__(self):
        self.config_repo = JoinConfigRepository()
        from backend.core.cache.cache_system import HierarchicalCache
        self.cache = HierarchicalCache()
        self.invalidator = CacheInvalidator(self.cache)
        logger.info("✅ JoinConfigService initialized")

    @cached("join_configs.list", timeout=120)
    def list_join_configs(self, game_gid: int, join_type: Optional[str] = None) -> List[JoinConfigEntity]:
        """
        获取游戏的Join配置列表 (带缓存)

        Args:
            game_gid: 游戏业务GID
            join_type: 可选, 按join_type过滤

        Returns:
            JoinConfigEntity列表

        Raises:
            ValueError: game_gid格式不正确
            DatabaseError: 数据库查询失败
        """
        validate_game_gid(game_gid)
        return self.config_repo.find_by_game_gid(game_gid, join_type)

    @cached("join_configs.detail", timeout=300)
    def get_join_config_by_id(self, config_id: int) -> Optional[JoinConfigEntity]:
        """
        根据ID获取Join配置 (带缓存)

        Args:
            config_id: 配置ID

        Returns:
            JoinConfigEntity, 不存在返回None

        Raises:
            ValueError: config_id格式不正确
        """
        if config_id <= 0:
            raise ValueError(f"config_id must be positive, got: {config_id}")

        return self.config_repo.find_by_id(config_id)

    def create_join_config(self, config_data: JoinConfigEntity) -> JoinConfigEntity:
        """
        创建Join配置 (自动失效缓存)

        Args:
            config_data: JoinConfigEntity (已通过Pydantic验证)

        Returns:
            创建的JoinConfigEntity

        Raises:
            ValueError: 名称已存在或验证失败
            ValidationError: 数据验证失败
        """
        # 验证名称唯一性
        existing = self.config_repo.find_by_name(config_data.name)
        if existing:
            raise ValueError(f"Join Config name '{config_data.name}' already exists")

        # 验证join_type和join_config的配合
        if config_data.join_type == "join" and not config_data.join_config:
            raise ValueError("join_type 'join' requires join_config to be provided")

        # 验证source_events不为空
        if not config_data.source_events:
            raise ValueError("source_events cannot be empty")

        # 验证output_fields不为空
        if not config_data.output_fields:
            raise ValueError("output_fields cannot be empty")

        # 创建配置 (Entity已通过Pydantic验证)
        result = self.config_repo.create(config_data.model_dump())
        if result is None:
            raise ValueError("Failed to create join config")

        # 失效缓存
        self.invalidator.invalidate_pattern("join_configs.list")

        logger.info(f"Join Config创建成功,已失效缓存: name={config_data.name}, game_gid={config_data.game_gid}")

        return result

    def update_join_config(self, config_id: int, updates: dict) -> JoinConfigEntity:
        """
        更新Join配置 (自动失效缓存)

        Args:
            config_id: 配置ID
            updates: 更新字段字典

        Returns:
            更新后的JoinConfigEntity

        Raises:
            ValueError: 配置不存在或验证失败
        """
        if config_id <= 0:
            raise ValueError(f"config_id must be positive, got: {config_id}")

        # 验证配置存在
        existing = self.config_repo.find_by_id(config_id)
        if not existing:
            raise ValueError(f"Join Config ID {config_id} not found")

        # 如果更新join_type,验证join_config
        if 'join_type' in updates and updates['join_type'] == 'join':
            if not updates.get('join_config') and not existing.join_config:
                raise ValueError("join_type 'join' requires join_config to be provided")

        # 序列化JSON字段（Repository期望字典）
        json_fields = ['source_events', 'join_config', 'output_fields', 'where_conditions', 'field_mappings']
        for field in json_fields:
            if field in updates:
                # 如果是字符串,尝试解析为JSON
                import json
                if isinstance(updates[field], str):
                    try:
                        updates[field] = json.loads(updates[field])
                    except json.JSONDecodeError:
                        raise ValueError(f"Invalid JSON in field '{field}'")

        # 更新配置
        success = self.config_repo.update(config_id, updates)
        if not success:
            raise ValueError("Failed to update join config")

        # 失效缓存
        self.invalidator.invalidate_pattern("join_configs.list")
        self.invalidator.invalidate_pattern(f"join_configs.detail:{config_id}")
        logger.info(f"Join Config更新成功,已失效缓存: id={config_id}")

        return self.get_join_config_by_id(config_id)

    def delete_join_config(self, config_id: int) -> None:
        """
        删除Join配置 (自动失效缓存)

        Args:
            config_id: 配置ID

        Raises:
            ValueError: 配置不存在
        """
        if config_id <= 0:
            raise ValueError(f"config_id must be positive, got: {config_id}")

        # 验证配置存在
        existing = self.config_repo.find_by_id(config_id)
        if not existing:
            raise ValueError(f"Join Config ID {config_id} not found")

        # 删除配置
        success = self.config_repo.delete(config_id)
        if not success:
            raise ValueError("Failed to delete join config")

        # 失效缓存
        self.invalidator.invalidate_pattern("join_configs.list")
        self.invalidator.invalidate_pattern(f"join_configs.detail:{config_id}")
        logger.info(f"Join Config删除成功,已失效缓存: id={config_id}, name={existing.name}")

    def delete_join_configs_by_game(self, game_gid: int) -> int:
        """
        删除游戏的所有Join配置 (自动失效缓存)

        Args:
            game_gid: 游戏业务GID

        Returns:
            删除的配置数量

        Raises:
            ValueError: game_gid格式不正确
        """
        validate_game_gid(game_gid)

        # 批量删除
        deleted_count = self.config_repo.delete_by_game_gid(game_gid)

        # 失效缓存
        if deleted_count > 0:
            self.invalidator.invalidate_pattern("join_configs.list")
            logger.info(f"批量删除Join Config成功,已失效缓存: game_gid={game_gid}, count={deleted_count}")

        return deleted_count

    def get_join_config_by_name(self, name: str) -> Optional[JoinConfigEntity]:
        """
        根据名称获取Join配置

        Args:
            name: 配置名称

        Returns:
            JoinConfigEntity, 不存在返回None
        """
        return self.config_repo.find_by_name(name)

    def validate_join_config(self, config_data: JoinConfigEntity) -> List[str]:
        """
        验证Join配置数据

        Args:
            config_data: Join配置Entity

        Returns:
            错误消息列表, 空列表表示验证通过
        """
        errors = []

        # 验证join_type和join_config的配合
        if config_data.join_type == "join" and not config_data.join_config:
            errors.append("join_type 'join' requires join_config to be provided")

        # 验证source_events不为空
        if not config_data.source_events:
            errors.append("source_events cannot be empty")

        # 验证output_fields不为空
        if not config_data.output_fields:
            errors.append("output_fields cannot be empty")

        # 验证output_table格式
        if not config_data.output_table or '.' not in config_data.output_table:
            errors.append("output_table must be in format 'database.table'")

        return errors
