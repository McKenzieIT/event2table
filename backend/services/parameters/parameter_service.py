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
from backend.core.config.config import CacheConfig

logger = logging.getLogger(__name__)


class ParameterService:
    """参数业务服务 (精简架构)"""

    def __init__(self):
        self.param_repo = ParameterRepository()
        from backend.core.cache.cache_system import HierarchicalCache
        self.cache = HierarchicalCache()
        self.invalidator = CacheInvalidator(self.cache)

    @cached("parameters.list", timeout=CacheConfig.CACHE_TIMEOUT_PARAMS)
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

    @cached("parameters.paginated", timeout=CacheConfig.CACHE_TIMEOUT_PARAMS)
    def get_parameters_paginated(
        self,
        game_gid: Optional[int] = None,
        search: Optional[str] = None,
        type_filter: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        获取分页参数列表 (带缓存)

        Args:
            game_gid: 游戏GID (可选)
            search: 搜索关键字 (可选)
            type_filter: 类型过滤 (可选)
            page: 页码
            page_size: 每页大小

        Returns:
            Dict:
                parameters: 参数列表
                total: 总数
                page: 当前页
                has_more: 是否有更多

        Raises:
            ValueError: game_id转换失败
        """
        # Convert game_gid to game_id if provided
        game_id = None
        if game_gid:
            from backend.services.games.game_service import GameService
            game_service = GameService()
            game = game_service.get_game_by_gid(game_gid)
            if not game:
                raise ValueError(f"Game {game_gid} not found")
            game_id = game.id

        # Use Repository method
        return self.param_repo.get_parameters_paginated(
            game_id=game_id,
            search=search,
            type_filter=type_filter,
            page=page,
            page_size=page_size
        )

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

        # Use Repository method
        return self.param_repo.get_parameters_by_game(game_gid)

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
        game_gid = self.param_repo.get_event_game_gid(event_id)
        if not game_gid:
            raise ValueError(f"Event not found: {event_id}")

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
                affected_events.add(param.event_id)
                affected_games.add(param.game_gid)

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
        # Use Repository method
        return self.param_repo.get_total_event_count(game_gid)

    # ========== 新增方法: 参数类型管理 ==========

    def change_parameter_type(
        self, param_id: int, new_type: str
    ) -> ParameterEntity:
        """
        更改参数类型 (自动失效缓存)

        Args:
            param_id: 参数ID
            new_type: 新类型 (base/param/common/calculate)

        Returns:
            更新后的ParameterEntity

        Raises:
            ValueError: 参数不存在或类型无效
        """
        # 验证参数存在
        existing = self.get_parameter_by_id(param_id)
        if not existing:
            raise ValueError(f"Parameter not found: {param_id}")

        # 验证类型
        valid_types = ["base", "param", "common", "calculate"]
        if new_type not in valid_types:
            raise ValueError(
                f"Invalid param_type: {new_type}. Must be one of {valid_types}"
            )

        # 更新类型
        updated = self.update_parameter(param_id, {"param_type": new_type})
        logger.info(f"参数类型变更成功: {param_id} {existing.param_type} -> {new_type}")

        return updated

    # ========== 新增方法: 搜索和过滤 ==========

    @cached("parameters.search", timeout=120)
    def search_by_name(
        self,
        keyword: str,
        event_id: Optional[int] = None,
        game_gid: Optional[int] = None
    ) -> List[ParameterEntity]:
        """
        根据参数名搜索参数 (带缓存)

        Args:
            keyword: 搜索关键词
            event_id: 可选的事件ID过滤
            game_gid: 可选的游戏GID过滤

        Returns:
            参数Entity列表

        Raises:
            ValueError: keyword为空
        """
        if not keyword or len(keyword.strip()) == 0:
            raise ValueError("Search keyword cannot be empty")

        # 使用Repository的搜索方法
        params = self.param_repo.search_parameters(keyword, event_id)

        # 如果指定了game_gid,过滤结果
        if game_gid:
            params = [p for p in params if p.game_gid == game_gid]

        return params

    @cached("parameters.by_type", timeout=180)
    def find_by_type(
        self,
        param_type: str,
        game_gid: Optional[int] = None,
        event_id: Optional[int] = None
    ) -> List[ParameterEntity]:
        """
        根据参数类型查找参数 (带缓存)

        Args:
            param_type: 参数类型 (template_id)
            game_gid: 可选的游戏GID过滤
            event_id: 可选的事件ID过滤

        Returns:
            参数Entity列表

        Raises:
            ValueError: param_type无效
        """
        # param_type实际上是template_id
        try:
            template_id = int(param_type)
        except ValueError:
            raise ValueError(f"Invalid param_type: {param_type}. Must be an integer (template_id)")

        # 使用Repository的方法
        params = self.param_repo.get_parameters_by_type(template_id, event_id)

        # 如果指定了game_gid,过滤结果
        if game_gid:
            params = [p for p in params if p.game_gid == game_gid]

        return params

    @cached("parameters.by_template", timeout=180)
    def find_by_template(
        self,
        template_id: int,
        event_id: Optional[int] = None
    ) -> List[ParameterEntity]:
        """
        根据模板ID查找参数 (带缓存)

        Args:
            template_id: 模板ID
            event_id: 可选的事件ID过滤

        Returns:
            参数Entity列表

        Raises:
            ValueError: template_id无效
        """
        if not template_id or template_id <= 0:
            raise ValueError(f"Invalid template_id: {template_id}")

        # 使用Repository的find_by_template方法
        params = self.param_repo.find_by_template(template_id)

        # 如果指定了event_id,过滤结果
        if event_id:
            params = [p for p in params if p.event_id == event_id]

        return params

    # ========== 新增方法: 统计和分析 ==========

    @cached("parameters.count_by_game", timeout=300)
    def count_by_game(self, game_gid: int) -> Dict[str, int]:
        """
        统计游戏的参数数量 (按类型分组) (带缓存)

        Args:
            game_gid: 游戏GID

        Returns:
            统计字典: {"base": 10, "param": 5, "common": 2, "calculate": 0}

        Raises:
            ValueError: game_gid无效
        """
        from backend.core.utils.business_helpers import validate_game_gid
        validate_game_gid(game_gid)

        # Use Repository method
        return self.param_repo.count_by_game(game_gid)

    @cached("parameters.count_by_event", timeout=300)
    def count_by_event(self, event_id: int) -> Dict[str, int]:
        """
        统计事件的参数数量 (按类型分组) (带缓存)

        Args:
            event_id: 事件ID

        Returns:
            统计字典: {"base": 10, "param": 5, "common": 2, "calculate": 0}

        Raises:
            ValueError: event_id无效
        """
        if not event_id or event_id <= 0:
            raise ValueError(f"Invalid event_id: {event_id}")

        # Use Repository method
        return self.param_repo.count_by_event(event_id)

    @cached("parameters.usage_stats", timeout=360)
    def usage_stats(
        self,
        game_gid: Optional[int] = None,
        param_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取参数使用统计 (带缓存)

        Args:
            game_gid: 可选的游戏GID过滤
            param_name: 可选的参数名过滤

        Returns:
            统计字典,包含:
            - total_params: 总参数数
            - total_events: 总事件数
            - avg_params_per_event: 平均每事件参数数
            - most_common_params: 最常用参数列表
            - type_distribution: 类型分布
        """
        # Use Repository method
        return self.param_repo.get_usage_stats(game_gid, param_name)

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            缓存统计字典,包含:
            - total_keys: 总缓存键数
            - l1_size: L1缓存大小
            - l2_size: L2缓存大小
            - hit_rate: 命中率
        """
        return self.cache.get_stats()

    # ========== Common Params Service Methods ==========

    @cached("params.commonByGame", timeout=180)
    def get_common_params(self, game_gid: int) -> List[Dict[str, Any]]:
        """
        获取指定游戏的公共参数列表 (带缓存)

        Args:
            game_gid: 游戏GID

        Returns:
            公共参数字典列表

        Raises:
            ValueError: game_gid无效
        """
        if not game_gid or game_gid <= 0:
            raise ValueError(f"Invalid game_gid: {game_gid}")

        # Validate game exists using Repository
        game = self.param_repo.get_game_by_gid(game_gid)
        if not game:
            raise ValueError(f"Game not found: {game_gid}")

        # Get common params from repository
        common_params = self.param_repo.get_common_params_by_game(game_gid)

        # Map param_type to data_type for frontend compatibility
        for param in common_params:
            param["data_type"] = param.get("param_type", "string")
            param["key"] = param.get("param_name", "")
            param["name"] = param.get("param_name_cn", param.get("param_name", ""))
            param["description"] = param.get("param_description", "")

        return common_params

    def sync_common_params(self, game_gid: int, threshold: float = 0.8) -> Dict[str, Any]:
        """
        同步公共参数 - 分析所有事件并识别公共参数

        Args:
            game_gid: 游戏GID
            threshold: 公共参数阈值 (默认0.8, 即80%)

        Returns:
            同步结果字典 {
                'total_events': int,
                'threshold': int,
                'added': int,
                'analyzed': int
            }

        Raises:
            ValueError: game_gid无效
        """
        if not game_gid or game_gid <= 0:
            raise ValueError(f"Invalid game_gid: {game_gid}")

        # Validate game exists and get game_id using Repository
        game = self.param_repo.get_game_with_id(game_gid)
        if not game:
            raise ValueError(f"Game not found: {game_gid}")

        game_id = game["id"]

        # Get all events for this game using Repository
        events = self.param_repo.get_events_by_game(game_gid)

        if not events:
            return {
                "total_events": 0,
                "threshold": 0,
                "added": 0,
                "analyzed": 0,
                "message": "No events found for this game"
            }

        total_events = len(events)
        min_occurrences = int(total_events * threshold)

        logger.info(
            f"Analyzing {total_events} events for game_gid={game_gid}, threshold={min_occurrences}"
        )

        # Count parameter occurrences across all events (using batch query to fix N+1)
        param_counts = {}
        event_ids = [e["id"] for e in events]

        if event_ids:
            # Use batch query instead of N individual queries (N+1 fix)
            params_map = self.param_repo.batch_find_by_event_ids(event_ids)

            for event_id, params in params_map.items():
                for param in params:
                    param_key = param.name
                    if param_key not in param_counts:
                        param_counts[param_key] = {
                            "count": 0,
                            "param_name_cn": param.description if param.description else "",
                        }
                    param_counts[param_key]["count"] += 1

        # Identify common parameters
        common_params_to_add = []
        for param_name, data in param_counts.items():
            if data["count"] >= min_occurrences:
                # Check if already exists
                existing = self.param_repo.find_common_param_by_name(game_gid, param_name)
                if not existing:
                    common_params_to_add.append(
                        {
                            "param_name": param_name,
                            "param_name_cn": data["param_name_cn"],
                            "count": data["count"],
                        }
                    )

        # Insert new common parameters
        added_count = 0
        for param in common_params_to_add:
            try:
                self.param_repo.create_common_param({
                    "game_id": game_id,
                    "game_gid": game_gid,
                    "param_name": param["param_name"],
                    "param_name_cn": param["param_name_cn"],
                    "param_type": "string",
                    "table_name": "common"
                })
                added_count += 1
                logger.info(
                    f"Added common param: {param['param_name']} (appeared in {param['count']} events)"
                )
            except Exception as e:
                logger.error(f"Failed to add common param {param['param_name']}: {e}")

        # Invalidate cache
        self.invalidator.invalidate_pattern(f"common_params.list:{game_gid}")

        return {
            "total_events": total_events,
            "threshold": min_occurrences,
            "added": added_count,
            "analyzed": len(param_counts),
        }

    def delete_common_param(self, param_id: int) -> None:
        """
        删除公共参数 (自动失效缓存)

        Args:
            param_id: 公共参数ID

        Raises:
            ValueError: param_id无效或参数不存在
        """
        if not param_id or param_id <= 0:
            raise ValueError(f"Invalid param_id: {param_id}")

        # Get param info to determine game_gid for cache invalidation using Repository
        param = self.param_repo.get_common_param_with_game(param_id)
        if not param:
            raise ValueError(f"Common parameter not found: {param_id}")

        game_gid = param.get("game_gid")

        # Delete the param
        success = self.param_repo.delete_common_param(param_id)
        if not success:
            raise ValueError(f"Failed to delete common parameter: {param_id}")

        # Invalidate cache
        if game_gid:
            self.invalidator.invalidate_pattern(f"common_params.list:{game_gid}")

        logger.info(f"Common parameter deleted successfully: param_id={param_id}")

    def batch_delete_common_params(self, param_ids: List[int]) -> int:
        """
        批量删除公共参数 (自动失效缓存)

        Args:
            param_ids: 公共参数ID列表

        Returns:
            删除的参数数量

        Raises:
            ValueError: param_ids包含无效值
        """
        if not param_ids:
            return 0

        # Get affected games for cache invalidation (using batch query to fix N+1)
        param_id_to_game_gid_map = self.param_repo.batch_get_game_gids_by_param_ids(param_ids)
        affected_games = set(param_id_to_game_gid_map.values())

        # Batch delete
        deleted_count = self.param_repo.delete_common_params_batch(param_ids)

        # Invalidate cache for affected games
        if deleted_count > 0:
            for game_gid in affected_games:
                self.invalidator.invalidate_pattern(f"common_params.list:{game_gid}")

            logger.info(f"Batch deleted common params: count={deleted_count}")

        return deleted_count

    # ========== API Layer Helper Methods ==========

    @cached("parameters.details", timeout=180)
    def get_parameter_details(
        self, param_name: str, game_gid: int
    ) -> Optional[Dict[str, Any]]:
        """
        获取参数详细信息 (带缓存)

        Args:
            param_name: 参数名称
            game_gid: 游戏GID

        Returns:
            参数详细信息字典,包含:
            - param_name: 参数名
            - param_name_cn: 参数中文名
            - base_type: 数据类型
            - event_count: 使用该参数的事件数
            - events: 使用该参数的事件列表
            - is_common: 是否为公共参数

        Raises:
            ValueError: game_gid或param_name无效
        """
        if not param_name or len(param_name.strip()) == 0:
            raise ValueError("param_name cannot be empty")

        if not game_gid or game_gid <= 0:
            raise ValueError(f"Invalid game_gid: {game_gid}")

        # Use Repository method
        return self.param_repo.get_parameter_details(param_name, game_gid)

    @cached("parameters.stats", timeout=300)
    def get_parameter_stats(self, game_gid: int) -> Dict[str, Any]:
        """
        获取参数统计信息 (带缓存)

        Args:
            game_gid: 游戏GID

        Returns:
            统计信息字典,包含:
            - total_unique_params: 唯一参数总数
            - total_event_params: 事件参数总数
            - common_params_count: 公共参数数量
            - data_type_distribution: 数据类型分布

        Raises:
            ValueError: game_gid无效
        """
        if not game_gid or game_gid <= 0:
            raise ValueError(f"Invalid game_gid: {game_gid}")

        # Use Repository method
        return self.param_repo.get_parameter_stats(game_gid)

    @cached("parameters.search_full", timeout=120)
    def search_parameters(
        self,
        keyword: str,
        game_gid: int,
        data_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索参数 (带缓存)

        Args:
            keyword: 搜索关键词
            game_gid: 游戏GID
            data_type: 可选的数据类型过滤

        Returns:
            参数字典列表

        Raises:
            ValueError: keyword或game_gid无效
        """
        if not keyword or len(keyword.strip()) == 0:
            raise ValueError("Search keyword cannot be empty")

        if not game_gid or game_gid <= 0:
            raise ValueError(f"Invalid game_gid: {game_gid}")

        # Use Repository method
        return self.param_repo.search_parameters_advanced(keyword, game_gid, data_type)

    def validate_parameter_name(
        self, param_name: str, game_gid: int
    ) -> Dict[str, Any]:
        """
        验证参数名称

        Args:
            param_name: 参数名称
            game_gid: 游戏GID

        Returns:
            验证结果字典,包含:
            - valid: 是否有效
            - exists: 是否已存在

        Raises:
            ValueError: param_name或game_gid无效
        """
        if not param_name or len(param_name.strip()) == 0:
            raise ValueError("Parameter name cannot be empty")

        if not game_gid or game_gid <= 0:
            raise ValueError(f"Invalid game_gid: {game_gid}")

        # Use Repository method (note: parameter order is different)
        result = self.param_repo.validate_parameter_name(game_gid, param_name)
        # Ensure consistent return format
        return {"valid": result.get("valid", True), "exists": result.get("exists", False)}

    # ========== Param Library Management ==========

    @cached("param_library.check", timeout=300)
    def check_param_library(self, param_name: str, template_id: int) -> Optional[Dict[str, Any]]:
        """
        检查参数是否存在于库中 (带缓存)

        Args:
            param_name: 参数名称
            template_id: 模板ID

        Returns:
            库参数字典,不存在返回None

        Raises:
            ValueError: param_name或template_id无效
        """
        if not param_name or len(param_name.strip()) == 0:
            raise ValueError("param_name cannot be empty")

        if not template_id or template_id <= 0:
            raise ValueError(f"Invalid template_id: {template_id}")

        # Use Repository method
        return self.param_repo.check_param_library(param_name, template_id)

    def batch_check_param_library(
        self, parameters: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        批量检查参数库

        Args:
            parameters: 参数列表,每个参数包含param_name和template_id

        Returns:
            检查结果字典,包含:
            - matched: 匹配的参数列表
            - unmatched: 未匹配的参数列表

        Raises:
            ValueError: parameters为空或超过100个
        """
        if not parameters or len(parameters) > 100:
            raise ValueError("Invalid parameters count (max 100)")

        # Use Repository method
        return self.param_repo.batch_check_param_library(parameters)

    def link_event_param_to_library(
        self, param_id: int, library_id: int
    ) -> Dict[str, Any]:
        """
        关联事件参数到库参数

        Args:
            param_id: 事件参数ID
            library_id: 库参数ID

        Returns:
            关联结果字典

        Raises:
            ValueError: 参数不存在或库参数不存在
        """
        if not param_id or param_id <= 0:
            raise ValueError(f"Invalid param_id: {param_id}")

        if not library_id or library_id <= 0:
            raise ValueError(f"Invalid library_id: {library_id}")

        # Verify event parameter exists using Repository
        event_param = self.param_repo.get_event_param(param_id)
        if not event_param:
            raise ValueError(f"Event parameter not found: {param_id}")

        # Verify library parameter exists using Repository
        library_param = self.param_repo.get_library_param(library_id)
        if not library_param:
            raise ValueError(f"Library parameter not found: {library_id}")

        # Link event parameter to library using Repository
        self.param_repo.update_event_param_library_link(param_id, library_id)

        # Update usage count using Repository
        self.param_repo.update_library_usage_count(library_id)

        logger.info(f"Linked event param {param_id} to library param {library_id}")

        return {"param_id": param_id, "library_id": library_id}

    # ========== ALTER TABLE HQL Generation ==========

    def get_alter_table_sql(self, param_id: int) -> Optional[Dict[str, Any]]:
        """
        获取ALTER TABLE SQL语句

        Args:
            param_id: 公共参数ID

        Returns:
            包含参数和SQL的字典,不存在返回None

        Raises:
            ValueError: param_id无效
        """
        if not param_id or param_id <= 0:
            raise ValueError(f"Invalid param_id: {param_id}")

        # Use Repository method
        return self.param_repo.get_alter_table_sql(param_id)
