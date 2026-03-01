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

        query = """
            SELECT
                ep.template_id,
                COUNT(*) as count
            FROM event_params ep
            INNER JOIN log_events le ON ep.event_id = le.id
            WHERE le.game_gid = ? AND ep.is_active = 1
            GROUP BY ep.template_id
        """
        results = fetch_all_as_dict(query, (game_gid,))

        # 转换为{"base": X, "param": Y, ...}格式
        stats = {"base": 0, "param": 0, "common": 0, "calculate": 0}
        type_map = {1: "base", 2: "param", 3: "common", 4: "calculate"}

        for row in results:
            template_id = row.get("template_id", 1)
            param_type = type_map.get(template_id, "base")
            stats[param_type] = row.get("count", 0)

        return stats

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

        query = """
            SELECT
                ep.template_id,
                COUNT(*) as count
            FROM event_params ep
            WHERE ep.event_id = ? AND ep.is_active = 1
            GROUP BY ep.template_id
        """
        results = fetch_all_as_dict(query, (event_id,))

        # 转换为{"base": X, "param": Y, ...}格式
        stats = {"base": 0, "param": 0, "common": 0, "calculate": 0}
        type_map = {1: "base", 2: "param", 3: "common", 4: "calculate"}

        for row in results:
            template_id = row.get("template_id", 1)
            param_type = type_map.get(template_id, "base")
            stats[param_type] = row.get("count", 0)

        return stats

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
        # 构建查询条件
        where_conditions = ["ep.is_active = 1"]
        params = []

        if game_gid:
            where_conditions.append("le.game_gid = ?")
            params.append(game_gid)

        if param_name:
            where_conditions.append("ep.param_name = ?")
            params.append(param_name)

        where_clause = " AND ".join(where_conditions)

        # 总参数数
        total_params_query = f"""
            SELECT COUNT(*) as count
            FROM event_params ep
            INNER JOIN log_events le ON ep.event_id = le.id
            WHERE {where_clause}
        """
        total_params_result = fetch_one_as_dict(total_params_query, tuple(params))
        total_params = total_params_result.get("count", 0) if total_params_result else 0

        # 总事件数
        if game_gid:
            total_events_query = "SELECT COUNT(*) as count FROM log_events WHERE game_gid = ?"
            total_events_result = fetch_one_as_dict(total_events_query, (game_gid,))
        else:
            total_events_query = "SELECT COUNT(*) as count FROM log_events"
            total_events_result = fetch_one_as_dict(total_events_query)

        total_events = total_events_result.get("count", 0) if total_events_result else 0

        # 平均参数数
        avg_params = total_params / total_events if total_events > 0 else 0

        # 类型分布
        type_dist_query = f"""
            SELECT
                ep.template_id,
                COUNT(*) as count
            FROM event_params ep
            INNER JOIN log_events le ON ep.event_id = le.id
            WHERE {where_clause}
            GROUP BY ep.template_id
        """
        type_dist_results = fetch_all_as_dict(type_dist_query, tuple(params))

        type_map = {1: "base", 2: "param", 3: "common", 4: "calculate"}
        type_distribution = {}
        for row in type_dist_results:
            template_id = row.get("template_id", 1)
            param_type = type_map.get(template_id, "base")
            type_distribution[param_type] = row.get("count", 0)

        # 最常用参数 (Top 10)
        most_common_query = f"""
            SELECT
                ep.param_name,
                COUNT(DISTINCT ep.event_id) as usage_count
            FROM event_params ep
            INNER JOIN log_events le ON ep.event_id = le.id
            WHERE {where_clause}
            GROUP BY ep.param_name
            ORDER BY usage_count DESC
            LIMIT 10
        """
        most_common_params = fetch_all_as_dict(most_common_query, tuple(params))

        return {
            "total_params": total_params,
            "total_events": total_events,
            "avg_params_per_event": round(avg_params, 2),
            "type_distribution": type_distribution,
            "most_common_params": most_common_params,
        }

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

    @cached("common_params.list", timeout=180)
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

        # Validate game exists
        game = fetch_one_as_dict("SELECT gid FROM games WHERE gid = ?", (game_gid,))
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

        # Validate game exists and get game_id
        game = fetch_one_as_dict(
            "SELECT id, gid FROM games WHERE gid = ?", (game_gid,)
        )
        if not game:
            raise ValueError(f"Game not found: {game_gid}")

        game_id = game["id"]

        # Get all events for this game
        events = fetch_all_as_dict(
            "SELECT id, event_name FROM log_events WHERE game_gid = ?", (game_gid,)
        )

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

        # Count parameter occurrences across all events
        param_counts = {}
        event_ids = [e["id"] for e in events]

        if event_ids:
            placeholders = ",".join(["?"] * len(event_ids))
            all_params = fetch_all_as_dict(
                f"""SELECT ep.event_id, ep.param_name, ep.param_name_cn
                    FROM event_params ep
                    WHERE ep.event_id IN ({placeholders}) AND ep.is_active = 1""",
                tuple(event_ids),
            )

            params_by_event = {}
            for param in all_params:
                eid = param["event_id"]
                if eid not in params_by_event:
                    params_by_event[eid] = []
                params_by_event[eid].append(param)

            for event in events:
                event_id = event["id"]
                params = params_by_event.get(event_id, [])

                for param in params:
                    param_key = param["param_name"]
                    if param_key not in param_counts:
                        param_counts[param_key] = {
                            "count": 0,
                            "param_name_cn": param.get("param_name_cn", ""),
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

        # Get param info to determine game_gid for cache invalidation
        param = fetch_one_as_dict("SELECT * FROM common_params WHERE id = ?", (param_id,))
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

        # Get affected games for cache invalidation
        affected_games = set()
        for pid in param_ids:
            param = fetch_one_as_dict("SELECT game_gid FROM common_params WHERE id = ?", (pid,))
            if param:
                affected_games.add(param["game_gid"])

        # Batch delete
        deleted_count = self.param_repo.delete_common_params_batch(param_ids)

        # Invalidate cache for affected games
        if deleted_count > 0:
            for game_gid in affected_games:
                self.invalidator.invalidate_pattern(f"common_params.list:{game_gid}")

            logger.info(f"Batch deleted common params: count={deleted_count}")

        return deleted_count
