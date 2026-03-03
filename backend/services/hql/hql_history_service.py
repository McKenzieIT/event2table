#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HQL History Service (HQL历史业务服务 - 精简架构)

提供HQL生成历史的业务逻辑处理
- 使用HQLHistoryEntity进行类型安全的数据传递
- 集成缓存管理
- 简化业务逻辑，移除DDD抽象
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from backend.services.base_service import BaseService
from backend.models.entities import HQLHistoryEntity
from backend.models.repositories.hql_history_repository import HQLHistoryRepository


class HQLHistoryService(BaseService):
    """
    HQL历史业务服务 (精简架构)

    职责:
    - HQL历史记录CRUD操作
    - 业务规则验证
    - 缓存管理
    """

    def __init__(self):
        """初始化服务"""
        super().__init__()
        self.history_repo = HQLHistoryRepository()

    def get_history_by_id(self, history_id: int) -> Optional[HQLHistoryEntity]:
        """
        根据ID获取HQL历史记录

        Args:
            history_id: 历史记录ID

        Returns:
            HQLHistoryEntity, 不存在返回None
        """
        return self.history_repo.find_by_id(history_id)

    def get_history_list(
        self,
        user_id: int = 0,
        session_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[HQLHistoryEntity]:
        """
        获取历史记录列表 (ERS架构)

        Args:
            user_id: 用户ID
            session_id: 会话ID（如果提供，优先按会话查询）
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            HQLHistoryEntity列表
        """
        # 优先按session_id查询 (使用Repository)
        if session_id:
            return self.history_repo.find_by_session_id(session_id, limit, offset)

        # 否则按user_id查询
        return self.history_repo.find_by_user_id(user_id, limit, offset)

    def save_history(
        self,
        events: List[Dict],
        fields: List[Dict],
        conditions: List[Dict],
        mode: str,
        hql: str,
        performance_score: Optional[int] = None,
        user_id: int = 0,
        session_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        hql_type: str = "select",
        game_gid: Optional[int] = None,
        name_en: Optional[str] = None,
        name_cn: Optional[str] = None,
    ) -> int:
        """
        保存HQL生成历史

        Args:
            events: 事件列表
            fields: 字段列表
            conditions: 条件列表
            mode: 生成模式 (single/join/union)
            hql: 生成的HQL
            performance_score: 性能评分
            user_id: 用户ID
            session_id: 会话ID
            metadata: 额外元数据
            hql_type: HQL类型 (select/ddl/dml/canvas)
            game_gid: 游戏GID
            name_en: 英文名称
            name_cn: 中文名称

        Returns:
            历史记录ID

        Raises:
            ValueError: 当hql_type为canvas但hql不是有效JSON时
        """
        # 验证canvas类型的hql格式
        if hql_type == "canvas":
            import json

            if isinstance(hql, dict):
                # 验证必需字段
                required_keys = ["create_table", "insert_overwrite", "select"]
                for key in required_keys:
                    if key not in hql:
                        raise ValueError(f"canvas类型的hql缺少{key}字段")
                hql_content = json.dumps(hql, ensure_ascii=False)
            elif isinstance(hql, str):
                # 验证是否为有效的JSON字符串
                try:
                    hql_obj = json.loads(hql)
                    if not isinstance(hql_obj, dict):
                        raise ValueError("canvas类型的hql必须是JSON对象")
                    required_keys = ["create_table", "insert_overwrite", "select"]
                    for key in required_keys:
                        if key not in hql_obj:
                            raise ValueError(f"canvas类型的hql缺少{key}字段")
                    hql_content = hql
                except json.JSONDecodeError:
                    raise ValueError("canvas类型的hql必须是有效的JSON字符串")
            else:
                hql_content = str(hql)
        else:
            hql_content = hql

        # 创建Entity
        history = HQLHistoryEntity(
            id=None,
            user_id=user_id,
            session_id=session_id,
            events_json=events,
            fields_json=fields,
            conditions_json=conditions or [],
            mode=mode,
            hql=hql_content,
            hql_type=hql_type,
            performance_score=performance_score,
            metadata_json=metadata,
            game_gid=game_gid,
            name_en=name_en,
            name_cn=name_cn,
            created_at=datetime.now(),
        )

        # 保存到数据库
        history_id = self.history_repo.create(history)

        # 清理缓存
        self.invalidate_pattern("hql_history:*")

        return history_id

    def restore_history(self, history_id: int) -> Optional[Dict[str, Any]]:
        """
        恢复历史版本（返回历史记录的详细配置）

        Args:
            history_id: 历史记录ID

        Returns:
            包含events, fields, conditions, mode的字典，不存在返回None
        """
        history = self.history_repo.find_by_id(history_id)
        if not history:
            return None

        return {
            "id": history.id,
            "events": history.events_json,
            "fields": history.fields_json,
            "conditions": history.conditions_json or [],
            "mode": history.mode,
            "hql": history.hql,
            "performance_score": history.performance_score,
            "created_at": history.created_at,
            "metadata": history.metadata_json,
        }

    def delete_history(self, history_id: int) -> bool:
        """
        删除历史记录

        Args:
            history_id: 历史记录ID

        Returns:
            是否删除成功

        Raises:
            ValueError: 当历史记录不存在时
        """
        # 验证历史记录存在
        history = self.history_repo.find_by_id(history_id)
        if not history:
            raise ValueError(f"HQL history {history_id} not found")

        # 删除记录
        success = self.history_repo.delete(history_id)

        # 清理缓存
        if success:
            self.invalidate_pattern("hql_history:*")

        return success

    def search_history(
        self,
        keyword: Optional[str] = None,
        hql_type: Optional[str] = None,
        game_gid: Optional[int] = None,
        user_id: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[HQLHistoryEntity]:
        """
        搜索HQL历史记录

        Args:
            keyword: 搜索关键词
            hql_type: HQL类型过滤
            game_gid: 游戏GID过滤
            user_id: 用户ID过滤
            date_from: 起始日期
            date_to: 结束日期
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            HQLHistoryEntity列表
        """
        # 如果有日期范围过滤，使用Repository的search_by_keyword
        # 并在后续添加日期过滤
        if keyword:
            results = self.history_repo.search_by_keyword(
                keyword=keyword,
                user_id=user_id,
                hql_type=hql_type,
                game_gid=game_gid,
                limit=limit * 2,  # 多获取一些以便日期过滤
                offset=offset,
            )

            # 应用日期过滤
            if date_from or date_to:
                filtered = []
                # Parse date strings to datetime objects if needed
                date_from_dt: Optional[datetime] = datetime.fromisoformat(date_from) if isinstance(date_from, str) else date_from
                date_to_dt: Optional[datetime] = datetime.fromisoformat(date_to) if isinstance(date_to, str) else date_to

                for item in results:
                    if date_from_dt and item.created_at and item.created_at < date_from_dt:
                        continue
                    if date_to_dt and item.created_at and item.created_at > date_to_dt:
                        continue
                    filtered.append(item)
                return filtered[:limit]

            return results[:limit]

        # 无关键词搜索时，直接使用Repository方法
        if user_id is not None:
            return self.history_repo.find_by_user_id(user_id, limit, offset)
        elif game_gid is not None:
            return self.history_repo.find_by_game_gid(game_gid, limit, offset)
        else:
            # 全局搜索
            return self.history_repo.search_by_keyword(
                keyword="",
                hql_type=hql_type,
                limit=limit,
                offset=offset,
            )

    def global_search_history(
        self,
        keyword: Optional[str] = None,
        hql_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[HQLHistoryEntity]:
        """
        全局搜索HQL历史记录（跨所有用户和会话）

        Args:
            keyword: 搜索关键词
            hql_type: HQL类型过滤
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            HQLHistoryEntity列表
        """
        return self.history_repo.search_by_keyword(
            keyword=keyword or "",
            hql_type=hql_type,
            limit=limit,
            offset=offset,
        )

    def cleanup_old_history(self, user_id: int = 0, keep_count: int = 100) -> int:
        """
        清理旧历史记录，只保留最近的N条

        Args:
            user_id: 用户ID
            keep_count: 保留记录数量

        Returns:
            删除的记录数
        """
        # 获取需要保留的记录
        keep_histories = self.history_repo.find_by_user_id(user_id, limit=keep_count, offset=0)
        keep_ids = [h.id for h in keep_histories if h.id]

        if not keep_ids:
            return 0

        # 查询所有记录
        all_histories = self.history_repo.find_by_user_id(user_id, limit=10000, offset=0)
        delete_ids = [h.id for h in all_histories if h.id not in keep_ids]

        # 删除不在保留列表中的记录
        deleted_count = 0
        for history_id in delete_ids:
            if history_id is not None:
                if self.history_repo.delete(history_id):
                    deleted_count += 1

        # 清理缓存
        if deleted_count > 0:
            self.invalidate_pattern("hql_history:*")

        return deleted_count

    def get_history_stats(self, user_id: int = 0) -> Dict[str, Any]:
        """
        获取历史统计信息

        Args:
            user_id: 用户ID

        Returns:
            统计信息字典
        """
        total_count = self.history_repo.count_by_user_id(user_id)

        # 获取最近的记录
        histories = self.history_repo.find_by_user_id(user_id, limit=1000, offset=0)

        # 按模式统计
        by_mode: Dict[str, int] = {}
        for h in histories:
            by_mode[h.mode] = by_mode.get(h.mode, 0) + 1

        # 获取最新创建时间
        latest_created_at = histories[0].created_at if histories else None

        return {
            "total_count": total_count,
            "by_mode": by_mode,
            "latest_created_at": latest_created_at,
        }
