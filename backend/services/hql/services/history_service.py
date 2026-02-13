"""
HQL历史版本服务

提供HQL生成历史的管理功能:
- 保存历史记录
- 查询历史列表
- 获取单个历史记录
- 恢复历史版本
- 删除历史记录
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from backend.core.database import fetch_one_as_dict, fetch_all_as_dict, execute_update


class HQLHistoryService:
    """HQL历史版本管理服务"""

    def __init__(self, db_path: str = None):
        """
        初始化历史服务

        Args:
            db_path: 数据库路径，默认使用主数据库
        """
        self.db_path = db_path

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

        Returns:
            int: 历史记录ID
        """
        events_json = json.dumps(events, ensure_ascii=False)
        fields_json = json.dumps(fields, ensure_ascii=False)
        conditions_json = json.dumps(conditions, ensure_ascii=False) if conditions else None
        metadata_json = json.dumps(metadata, ensure_ascii=False) if metadata else None

        sql = """
            INSERT INTO hql_history (
                user_id, session_id, events_json, fields_json, conditions_json,
                mode, hql, performance_score, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor = execute_update(
            sql,
            (
                user_id,
                session_id,
                events_json,
                fields_json,
                conditions_json,
                mode,
                hql,
                performance_score,
                metadata_json,
            ),
            db_path=self.db_path,
        )

        return cursor.lastrowid

    def get_history_list(
        self, user_id: int = 0, session_id: Optional[str] = None, limit: int = 50, offset: int = 0
    ) -> List[Dict]:
        """
        获取历史记录列表

        Args:
            user_id: 用户ID
            session_id: 会话ID（如果提供，优先按会话查询）
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            List[Dict]: 历史记录列表
        """
        if session_id:
            sql = """
                SELECT * FROM hql_history
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            params = (session_id, limit, offset)
        else:
            sql = """
                SELECT * FROM hql_history
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            params = (user_id, limit, offset)

        return fetch_all_as_dict(sql, params, db_path=self.db_path)

    def get_history_by_id(self, history_id: int) -> Optional[Dict]:
        """
        获取单个历史记录

        Args:
            history_id: 历史记录ID

        Returns:
            Optional[Dict]: 历史记录详情，不存在则返回None
        """
        sql = "SELECT * FROM hql_history WHERE id = ?"
        return fetch_one_as_dict(sql, (history_id,), db_path=self.db_path)

    def restore_history(self, history_id: int) -> Optional[Dict]:
        """
        恢复历史版本（返回历史记录的详细配置）

        Args:
            history_id: 历史记录ID

        Returns:
            Optional[Dict]: 包含events, fields, conditions, mode的字典
        """
        history = self.get_history_by_id(history_id)
        if not history:
            return None

        return {
            "id": history["id"],
            "events": json.loads(history["events_json"]),
            "fields": json.loads(history["fields_json"]),
            "conditions": (
                json.loads(history["conditions_json"]) if history["conditions_json"] else []
            ),
            "mode": history["mode"],
            "hql": history["hql"],
            "performance_score": history["performance_score"],
            "created_at": history["created_at"],
            "metadata": json.loads(history["metadata_json"]) if history["metadata_json"] else None,
        }

    def delete_history(self, history_id: int) -> bool:
        """
        删除历史记录

        Args:
            history_id: 历史记录ID

        Returns:
            bool: 是否删除成功
        """
        sql = "DELETE FROM hql_history WHERE id = ?"
        cursor = execute_update(sql, (history_id,), db_path=self.db_path)
        return cursor.rowcount > 0

    def cleanup_old_history(self, user_id: int = 0, keep_count: int = 100) -> int:
        """
        清理旧历史记录，只保留最近的N条

        Args:
            user_id: 用户ID
            keep_count: 保留记录数量

        Returns:
            int: 删除的记录数
        """
        # 查询需要保留的记录ID
        sql_keep = """
            SELECT id FROM hql_history
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """
        keep_ids = [
            row["id"]
            for row in fetch_all_as_dict(sql_keep, (user_id, keep_count), db_path=self.db_path)
        ]

        if not keep_ids:
            return 0

        # 删除不在保留列表中的记录
        placeholders = ",".join(["?" for _ in keep_ids])
        sql_delete = f"DELETE FROM hql_history WHERE user_id = ? AND id NOT IN ({placeholders})"
        cursor = execute_update(sql_delete, [user_id] + keep_ids, db_path=self.db_path)

        return cursor.rowcount

    def get_history_stats(self, user_id: int = 0) -> Dict:
        """
        获取历史统计信息

        Args:
            user_id: 用户ID

        Returns:
            Dict: 统计信息
        """
        sql_count = "SELECT COUNT(*) as count FROM hql_history WHERE user_id = ?"
        count_result = fetch_one_as_dict(sql_count, (user_id,), db_path=self.db_path)

        sql_by_mode = """
            SELECT mode, COUNT(*) as count
            FROM hql_history
            WHERE user_id = ?
            GROUP BY mode
        """
        by_mode = fetch_all_as_dict(sql_by_mode, (user_id,), db_path=self.db_path)

        sql_latest = """
            SELECT created_at FROM hql_history
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        """
        latest = fetch_one_as_dict(sql_latest, (user_id,), db_path=self.db_path)

        return {
            "total_count": count_result["count"] if count_result else 0,
            "by_mode": {row["mode"]: row["count"] for row in by_mode},
            "latest_created_at": latest["created_at"] if latest else None,
        }
