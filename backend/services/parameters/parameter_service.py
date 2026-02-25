#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameter Service - 业务逻辑层 (精简架构)

提供参数相关的业务逻辑服务
- 使用统一Entity模型 (ParameterEntity)
- 移除DDD抽象,简化业务逻辑
- 集成缓存防护和失效机制
"""

from typing import List, Optional, Dict, Any, Union
import logging
import sqlite3
from backend.models.entities import ParameterEntity, CommonParameterEntity
from backend.models.repositories.parameters import ParameterRepository
from backend.core.cache.cache_system import CacheInvalidator, cached
from backend.core.utils.converters import fetch_all_as_dict, fetch_one_as_dict

logger = logging.getLogger(__name__)


class ParameterService:
    """参数业务服务 (精简架构)"""

    def __init__(self):
        self.param_repo = ParameterRepository()
        from backend.core.cache.cache_system import HierarchicalCache
        self.cache = HierarchicalCache()
        self.invalidator = CacheInvalidator(self.cache)

    @cached("parameters.list", timeout=120)
    def get_all_parameters(self) -> List[ParameterEntity]:
        """
        获取所有参数 (带缓存)

        Returns:
            参数Entity列表

        Raises:
            DatabaseError: 数据库查询失败
        """
        # ParameterRepository现在直接返回ParameterEntity
        return self.param_repo.find_all()

    @cached("parameters.by_event", timeout=180)
    def get_parameters_by_event(
        self, event_id: int, include_inactive: bool = False
    ) -> List[ParameterEntity]:
        """
        根据事件ID获取参数列表 (带缓存)

        Args:
            event_id: 事件ID
            include_inactive: 是否包含非活跃参数

        Returns:
            参数Entity列表

        Raises:
            ValueError: event_id无效
        """
        if not event_id or event_id <= 0:
            raise ValueError(f"Invalid event_id: {event_id}")

        # ParameterRepository现在直接返回ParameterEntity
        return self.param_repo.get_all_by_event(event_id, include_inactive)

    @cached("parameters.by_id", timeout=300)
    def get_parameter_by_id(self, param_id: int) -> Optional[ParameterEntity]:
        """
        根据ID获取参数 (带缓存)

        Args:
            param_id: 参数ID

        Returns:
            ParameterEntity, 不存在返回None

        Raises:
            ValueError: param_id无效
        """
        if not param_id or param_id <= 0:
            raise ValueError(f"Invalid param_id: {param_id}")

        # ParameterRepository现在直接返回ParameterEntity
        return self.param_repo.find_by_id(param_id)

    @cached("parameters.by_game", timeout=180)
    def get_parameters_by_game(self, game_gid: int) -> List[ParameterEntity]:
        """
        根据游戏GID获取所有参数 (带缓存)

        Args:
            game_gid: 游戏业务GID

        Returns:
            参数Entity列表

        Raises:
            ValueError: game_gid无效
        """
        from backend.core.utils.business_helpers import validate_game_gid
        validate_game_gid(game_gid)

        query = """
            SELECT ep.*, le.game_gid
            FROM event_params ep
            INNER JOIN log_events le ON ep.event_id = le.id
            WHERE le.game_gid = ? AND ep.is_active = 1
            ORDER BY ep.id
        """
        params_dicts = fetch_all_as_dict(query, (game_gid,))
        return [self.param_repo._row_to_entity(p) for p in params_dicts]

    @cached("parameters.common", timeout=360)
    def get_common_parameters(
        self, game_gid: Optional[int] = None, threshold: float = 0.8
    ) -> List[CommonParameterEntity]:
        """
        获取公共参数列表 (带缓存)

        Args:
            game_gid: 可选的游戏GID过滤
            threshold: 公共参数阈值 (默认0.8)

        Returns:
            公共参数Entity列表
        """
        # 使用Repository的get_common_parameters方法
        # 注意：get_common_parameters返回字典列表（因为包含统计信息）
        common_params = self.param_repo.get_common_parameters(game_gid)

        # Filter by threshold if specified
        if threshold < 1.0:
            total_events = self._get_total_event_count(game_gid)
            common_params = [
                p
                for p in common_params
                if p.get("usage_count", 0) / total_events >= threshold
            ]

        # Convert to CommonParameterEntity
        return [CommonParameterEntity(**p) for p in common_params]

    def create_parameter(
        self,
        param_data: Union[Dict[str, Any], ParameterEntity],
        **kwargs
    ) -> ParameterEntity:
        """
        创建参数 (自动失效缓存)

        Args:
            param_data: 参数数据 (字典或ParameterEntity)

        Returns:
            创建的ParameterEntity

        Raises:
            ValueError: 参数验证失败
        """
        # 处理不同类型的输入
        if isinstance(param_data, ParameterEntity):
            param_entity = param_data
            data = param_entity.model_dump()
        elif isinstance(param_data, dict):
            # 创建Entity进行验证
            param_entity = ParameterEntity(**param_data)
            data = param_entity.model_dump()
        else:
            raise ValueError(f"param_data must be dict or ParameterEntity, got {type(param_data)}")

        # 验证输入
        event_id = data.get("event_id")
        if not event_id or event_id <= 0:
            raise ValueError(f"Invalid event_id: {event_id}")

        name = data.get("name")
        if not name or len(name.strip()) == 0:
            raise ValueError("Parameter name cannot be empty")

        param_type = data.get("param_type", "base")
        json_path = data.get("json_path")

        # 验证param_type
        valid_types = ["base", "param", "common", "calculate"]
        if param_type not in valid_types:
            raise ValueError(f"Invalid param_type: {param_type}. Must be one of {valid_types}")

        # 验证json_path格式
        if json_path and not json_path.startswith("$."):
            raise ValueError(f"JSON path must start with '$.', got: {json_path}")

        # 获取game_gid
        event = fetch_one_as_dict(
            "SELECT game_gid FROM log_events WHERE id = ?", (event_id,)
        )
        if not event:
            raise ValueError(f"Event not found: {event_id}")

        game_gid = event["game_gid"]

        # 确保data中有game_gid
        data["game_gid"] = game_gid

        # 创建参数 (使用Repository)
        try:
            result = self.param_repo.create(data)
            if result is None:
                raise ValueError("Failed to create parameter")
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError(f"Parameter '{name}' already exists for event_id={event_id}")
            raise

        # 失效缓存
        self._invalidate_parameter_cache(event_id, game_gid)
        logger.info(f"参数创建成功,已失效缓存: name={name}, event_id={event_id}")

        return result

    def update_parameter(
        self, param_id: int, updates: Dict[str, Any]
    ) -> ParameterEntity:
        """
        更新参数 (自动失效缓存)

        Args:
            param_id: 参数ID
            updates: 更新字段字典

        Returns:
            更新后的ParameterEntity

        Raises:
            ValueError: 参数不存在或验证失败
        """
        if not param_id or param_id <= 0:
            raise ValueError(f"Invalid param_id: {param_id}")

        # 获取原参数
        existing = self.param_repo.find_by_id(param_id)
        if not existing:
            raise ValueError(f"Parameter not found: {param_id}")

        # 验证更新
        if "name" in updates and not updates["name"]:
            raise ValueError("Parameter name cannot be empty")

        if "param_type" in updates:
            valid_types = ["base", "param", "common", "calculate"]
            if updates["param_type"] not in valid_types:
                raise ValueError(
                    f"Invalid param_type: {updates['param_type']}. Must be one of {valid_types}"
                )

        if "json_path" in updates and updates["json_path"]:
            if not updates["json_path"].startswith("$."):
                raise ValueError(
                    f"JSON path must start with '$.', got: {updates['json_path']}"
                )

        # 更新参数
        self.param_repo.update(param_id, updates)

        # 失效缓存
        self._invalidate_parameter_cache(
            existing.event_id, existing.game_gid
        )
        logger.info(f"参数更新成功,已失效缓存: param_id={param_id}")

        return self.get_parameter_by_id(param_id)

    def delete_parameter(self, param_id: int) -> None:
        """
        删除参数 (自动失效缓存)

        Args:
            param_id: 参数ID

        Raises:
            ValueError: 参数不存在
        """
        if not param_id or param_id <= 0:
            raise ValueError(f"Invalid param_id: {param_id}")

        # 获取参数信息
        existing = self.param_repo.find_by_id(param_id)
        if not existing:
            raise ValueError(f"Parameter not found: {param_id}")

        event_id = existing.event_id
        game_gid = existing.game_gid

        # 删除参数
        self.param_repo.delete(param_id)

        # 失效缓存
        self._invalidate_parameter_cache(event_id, game_gid)
        logger.info(f"参数删除成功,已失效缓存: param_id={param_id}")

    def batch_delete_parameters(self, param_ids: List[int]) -> int:
        """
        批量删除参数 (自动失效缓存)

        Args:
            param_ids: 参数ID列表

        Returns:
            删除的参数数量

        Raises:
            ValueError: param_id包含无效值
        """
        if not param_ids:
            return 0

        # 获取所有参数信息 (用于失效缓存)
        affected_events = set()
        affected_games = set()

        for pid in param_ids:
            param = self.param_repo.find_by_id(pid)
            if param:
                affected_events.add(param.get("event_id"))
                affected_games.add(param.get("game_gid"))

        # 批量删除 (use delete_batch from GenericRepository)
        deleted_count = self.param_repo.delete_batch(param_ids)

        # 失效缓存
        if deleted_count > 0:
            for event_id in affected_events:
                self.invalidator.invalidate_pattern(f"parameters.by_event:{event_id}")
            for game_gid in affected_games:
                self.invalidator.invalidate_pattern(f"parameters.by_game:{game_gid}")
                self.invalidator.invalidate_game(game_gid)

            logger.info(f"批量删除参数成功,已失效缓存: count={deleted_count}")

        return deleted_count

    # ========== 私有辅助方法 ==========

    def _invalidate_parameter_cache(
        self, event_id: Optional[int] = None, game_gid: Optional[int] = None
    ):
        """
        失效参数相关缓存

        Args:
            event_id: 事件ID
            game_gid: 游戏GID
        """
        if event_id:
            # 失效事件的参数缓存
            self.invalidator.invalidate_pattern(f"parameters.by_event:{event_id}")

        if game_gid:
            # 失效游戏的参数缓存
            self.invalidator.invalidate_pattern(f"parameters.by_game:{game_gid}")
            # 失效游戏相关的公共参数缓存
            self.invalidator.invalidate_game(game_gid)

        # 失效全局参数列表缓存
        self.invalidator.invalidate_pattern("parameters.list")

    def _get_total_event_count(self, game_gid: Optional[int]) -> int:
        """获取游戏的事件总数"""
        if game_gid:
            count = fetch_one_as_dict(
                "SELECT COUNT(*) as count FROM log_events WHERE game_gid = ?",
                (game_gid,),
            )
        else:
            count = fetch_one_as_dict("SELECT COUNT(*) as count FROM log_events")
        return count["count"] if count else 1
