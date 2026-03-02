#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Node Service (事件节点业务服务 - 精简架构)

提供事件节点的业务逻辑处理
- 使用EventNodeEntity进行类型安全的数据传递
- 集成缓存管理
- 简化业务逻辑，移除DDD抽象
"""

from typing import List, Optional, Dict, Any
from backend.services.base_service import BaseService
from backend.models.entities import EventNodeEntity
from backend.models.repositories.event_node_repository import EventNodeRepository
from backend.models.repositories.games import GameRepository
from backend.models.repositories.events import EventRepository
from backend.core.cache.decorators import cached


class EventNodeService(BaseService):
    """
    事件节点业务服务 (精简架构)

    职责:
    - 事件节点CRUD操作
    - 业务规则验证
    - 缓存管理
    """

    def __init__(self):
        """初始化服务"""
        super().__init__()
        self.node_repo = EventNodeRepository()
        self.game_repo = GameRepository()
        self.event_repo = EventRepository()

    @cached("event_nodes.byId", timeout=120)
    def get_node_by_id(self, node_id: int) -> Optional[EventNodeEntity]:
        """
        根据ID获取事件节点 (带缓存)

        Args:
            node_id: 节点ID

        Returns:
            EventNodeEntity, 不存在返回None
        """
        return self.node_repo.find_by_id(node_id)

    @cached("event_nodes.byGame", timeout=120)
    def get_nodes_by_game_gid(self, game_gid: int) -> List[EventNodeEntity]:
        """
        获取指定游戏的所有事件节点 (带缓存)

        Args:
            game_gid: 游戏GID

        Returns:
            EventNodeEntity列表
        """
        return self.node_repo.find_by_game_gid(game_gid)

    @cached("event_nodes.byEvent", timeout=120)
    def get_nodes_by_event_id(self, event_id: int) -> List[EventNodeEntity]:
        """
        获取指定事件的所有节点 (带缓存)

        Args:
            event_id: 事件ID

        Returns:
            EventNodeEntity列表
        """
        return self.node_repo.find_by_event_id(event_id)

    def create_node(self, node: EventNodeEntity) -> EventNodeEntity:
        """
        创建事件节点

        Args:
            node: EventNodeEntity实例

        Returns:
            创建的EventNodeEntity

        Raises:
            ValueError: 当游戏或事件不存在时

        Example:
            >>> service = EventNodeService()
            >>> node = EventNodeEntity(
            ...     game_gid=10000147,
            ...     name="Login Node",
            ...     event_id=1,
            ...     config_json={"fields": [], "mode": "single"}
            ... )
            >>> created = service.create_node(node)
        """
        # 验证游戏存在
        game = self.game_repo.find_by_gid(node.game_gid)
        if not game:
            raise ValueError(f"Game {node.game_gid} not found")

        # 验证事件存在
        event = self.event_repo.find_by_id(node.event_id)
        if not event:
            raise ValueError(f"Event {node.event_id} not found")

        # 验证事件属于指定游戏
        if event.game_gid != node.game_gid:
            raise ValueError(
                f"Event {node.event_id} does not belong to game {node.game_gid}"
            )

        # 创建节点
        node_id = self.node_repo.create(node)

        # 清理缓存
        self.invalidate_game_cache(node.game_gid)
        self.invalidate_pattern(f"event_nodes.game:{node.game_gid}:*")

        return self.node_repo.find_by_id(node_id)

    def update_node(self, node_id: int, node: EventNodeEntity) -> EventNodeEntity:
        """
        更新事件节点

        Args:
            node_id: 节点ID
            node: EventNodeEntity实例

        Returns:
            更新后的EventNodeEntity

        Raises:
            ValueError: 当节点不存在或game_gid/event_id验证失败时
        """
        # 验证节点存在
        existing = self.node_repo.find_by_id(node_id)
        if not existing:
            raise ValueError(f"Event node {node_id} not found")

        # 如果更新game_gid或event_id，需要验证
        if node.game_gid != existing.game_gid or node.event_id != existing.event_id:
            # 验证游戏存在
            game = self.game_repo.find_by_gid(node.game_gid)
            if not game:
                raise ValueError(f"Game {node.game_gid} not found")

            # 验证事件存在
            event = self.event_repo.find_by_id(node.event_id)
            if not event:
                raise ValueError(f"Event {node.event_id} not found")

            # 验证事件属于指定游戏
            if event.game_gid != node.game_gid:
                raise ValueError(
                    f"Event {node.event_id} does not belong to game {node.game_gid}"
                )

        # 更新节点
        self.node_repo.update(node_id, node)

        # 清理缓存
        self.invalidate_game_cache(existing.game_gid)
        if node.game_gid != existing.game_gid:
            self.invalidate_game_cache(node.game_gid)

        return self.node_repo.find_by_id(node_id)

    def delete_node(self, node_id: int) -> bool:
        """
        删除事件节点（软删除）

        Args:
            node_id: 节点ID

        Returns:
            是否删除成功

        Raises:
            ValueError: 当节点不存在时
        """
        # 验证节点存在
        node = self.node_repo.find_by_id(node_id)
        if not node:
            raise ValueError(f"Event node {node_id} not found")

        # 删除节点
        success = self.node_repo.delete(node_id)

        # 清理缓存
        if success:
            self.invalidate_game_cache(node.game_gid)
            self.invalidate_pattern(f"event_nodes.game:{node.game_gid}:*")

        return success

    def hard_delete_node(self, node_id: int) -> bool:
        """
        硬删除事件节点（从数据库中彻底删除）

        Args:
            node_id: 节点ID

        Returns:
            是否删除成功

        Warning:
            此操作不可恢复，请谨慎使用
        """
        # 验证节点存在
        node = self.node_repo.find_by_id(node_id)
        if not node:
            raise ValueError(f"Event node {node_id} not found")

        # 硬删除
        success = self.node_repo.hard_delete(node_id)

        # 清理缓存
        if success:
            self.invalidate_game_cache(node.game_gid)
            self.invalidate_pattern(f"event_nodes.game:{node.game_gid}:*")

        return success

    @cached("event_nodes.countByGame", timeout=300)
    def count_nodes_by_game_gid(self, game_gid: int) -> int:
        """
        统计指定游戏的事件节点数量 (带缓存)

        Args:
            game_gid: 游戏GID

        Returns:
            节点数量
        """
        return self.node_repo.count_by_game_gid(game_gid)

    @cached("event_nodes.withDetails", timeout=180)
    def get_node_with_details(self, node_id: int) -> Optional[Dict[str, Any]]:
        """
        获取事件节点及其关联的游戏和事件信息 (带缓存)

        Args:
            node_id: 节点ID

        Returns:
            包含节点、游戏、事件信息的字典，不存在返回None
        """
        node = self.node_repo.find_by_id(node_id)
        if not node:
            return None

        # 获取关联的游戏和事件
        game = self.game_repo.find_by_gid(node.game_gid)
        event = self.event_repo.find_by_id(node.event_id)

        # 构造返回数据
        result = node.model_dump()
        if game:
            result["game_name"] = game.name
        if event:
            result["event_name"] = event.event_name
            result["event_name_cn"] = event.event_name_cn

        return result
