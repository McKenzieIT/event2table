#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flow Service (流程模板业务逻辑层)

提供流程模板的业务逻辑封装:
- 流程CRUD操作
- 流程验证
- 缓存管理
"""

from typing import List, Optional
from backend.models.entities import FlowEntity
from backend.models.repositories.flow_repository import FlowRepository
from backend.models.repositories.games import GameRepository
from backend.services.base_service import BaseService


class FlowService(BaseService):
    """
    流程模板业务服务 (精简架构)

    职责:
    - 流程业务逻辑封装
    - 多Repository协作
    - 缓存管理
    """

    def __init__(self):
        """初始化流程服务"""
        super().__init__()
        self.flow_repo = FlowRepository()
        self.game_repo = GameRepository()

    def create_flow(self, flow: FlowEntity) -> FlowEntity:
        """
        创建流程模板

        业务规则:
        1. 如果指定game_gid，游戏必须存在
        2. 流程名称不能为空
        3. 创建后清理缓存

        Args:
            flow: FlowEntity实例

        Returns:
            创建的FlowEntity

        Raises:
            ValueError: 游戏不存在或验证失败

        Examples:
            >>> service = FlowService()
            >>> flow = FlowEntity(
            ...     game_gid=10000147,
            ...     flow_name="Test Flow",
            ...     flow_graph={"nodes": [], "edges": []}
            ... )
            >>> created_flow = service.create_flow(flow)
        """
        # 验证游戏存在（如果指定）
        if flow.game_gid:
            game = self.game_repo.find_by_gid(flow.game_gid)
            if not game:
                raise ValueError(f"Game {flow.game_gid} not found")

        # 创建流程
        flow_id = self.flow_repo.create(flow)

        # 清理缓存
        if flow.game_gid:
            self.invalidate_game_cache(flow.game_gid)
        self.invalidate_pattern("flows.list:*")

        return self.flow_repo.find_by_id(flow_id)

    def get_flow_by_id(self, flow_id: int) -> Optional[FlowEntity]:
        """
        根据ID获取流程

        Args:
            flow_id: 流程ID

        Returns:
            FlowEntity，不存在返回None
        """
        return self.flow_repo.find_by_id(flow_id)

    def get_flows_by_game_gid(self, game_gid: int) -> List[FlowEntity]:
        """
        获取游戏的所有流程

        Args:
            game_gid: 游戏GID

        Returns:
            FlowEntity列表

        Raises:
            ValueError: 游戏不存在
        """
        # 验证游戏存在
        game = self.game_repo.find_by_gid(game_gid)
        if not game:
            raise ValueError(f"Game {game_gid} not found")

        return self.flow_repo.find_by_game_gid(game_gid)

    def update_flow(self, flow_id: int, flow: FlowEntity) -> FlowEntity:
        """
        更新流程

        业务规则:
        1. 流程必须存在
        2. 更新后清理缓存

        Args:
            flow_id: 流程ID
            flow: 更新的FlowEntity数据

        Returns:
            更新后的FlowEntity

        Raises:
            ValueError: 流程不存在

        Examples:
            >>> service = FlowService()
            >>> flow = FlowEntity(
            ...     flow_name="Updated Flow Name",
            ...     description="Updated description"
            ... )
            >>> updated_flow = service.update_flow(1, flow)
        """
        # 验证流程存在
        existing_flow = self.flow_repo.find_by_id(flow_id)
        if not existing_flow:
            raise ValueError(f"Flow {flow_id} not found")

        # 更新流程
        self.flow_repo.update(flow_id, flow)

        # 清理缓存
        if existing_flow.game_gid:
            self.invalidate_game_cache(existing_flow.game_gid)
        self.invalidate_pattern(f"flows:{flow_id}")

        return self.flow_repo.find_by_id(flow_id)

    def delete_flow(self, flow_id: int) -> bool:
        """
        删除流程（软删除）

        业务规则:
        1. 流程必须存在
        2. 删除后清理缓存

        Args:
            flow_id: 流程ID

        Returns:
            是否删除成功

        Raises:
            ValueError: 流程不存在

        Examples:
            >>> service = FlowService()
            >>> success = service.delete_flow(1)
        """
        # 验证流程存在
        flow = self.flow_repo.find_by_id(flow_id)
        if not flow:
            raise ValueError(f"Flow {flow_id} not found")

        # 软删除
        success = self.flow_repo.delete(flow_id)

        if success:
            # 清理缓存
            if flow.game_gid:
                self.invalidate_game_cache(flow.game_gid)
            self.invalidate_pattern(f"flows:{flow_id}")
            self.invalidate_pattern("flows.list:*")

        return success

    def hard_delete_flow(self, flow_id: int) -> bool:
        """
        硬删除流程（从数据库彻底删除）

        Args:
            flow_id: 流程ID

        Returns:
            是否删除成功

        Warning:
            此操作不可恢复，请谨慎使用
        """
        flow = self.flow_repo.find_by_id(flow_id)
        if not flow:
            raise ValueError(f"Flow {flow_id} not found")

        success = self.flow_repo.hard_delete(flow_id)

        if success:
            # 清理缓存
            if flow.game_gid:
                self.invalidate_game_cache(flow.game_gid)
            self.invalidate_pattern(f"flows:{flow_id}")
            self.invalidate_pattern("flows.list:*")

        return success

    def count_flows_by_game_gid(self, game_gid: int) -> int:
        """
        统计游戏的流程数量

        Args:
            game_gid: 游戏GID

        Returns:
            流程数量
        """
        return self.flow_repo.count_by_game_gid(game_gid)

    def get_all_active_flows(self) -> List[FlowEntity]:
        """
        获取所有激活的流程

        Returns:
            FlowEntity列表
        """
        return self.flow_repo.find_all_active()
