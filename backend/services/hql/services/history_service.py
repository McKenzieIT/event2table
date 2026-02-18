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
from backend.core.database import get_db_connection
from backend.core.config import DB_PATH


def _fetch_all_as_dict(sql, params=None, db_path=None):
    """Helper function to fetch all rows as dictionaries"""
    if db_path is None:
        db_path = DB_PATH
    conn = get_db_connection(db_path)
    conn.row_factory = None  # Use default tuple factory
    cursor = conn.cursor()
    cursor.execute(sql, params or ())
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    conn.close()
    return [dict(zip(columns, row)) for row in rows]


def _fetch_one_as_dict(sql, params=None, db_path=None):
    """Helper function to fetch one row as dictionary"""
    if db_path is None:
        db_path = DB_PATH
    conn = get_db_connection(db_path)
    conn.row_factory = None
    cursor = conn.cursor()
    cursor.execute(sql, params or ())
    row = cursor.fetchone()
    if row:
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        return dict(zip(columns, row))
    conn.close()
    return None


class HQLHistoryService:
    """HQL历史版本管理服务"""

    def __init__(self, db_path: str = None):
        """
        初始化历史服务

        Args:
            db_path: 数据库路径，默认使用主数据库
        """
        self.db_path = db_path or DB_PATH

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
            int: 历史记录ID
        """
        events_json = json.dumps(events, ensure_ascii=False)
        fields_json = json.dumps(fields, ensure_ascii=False)
        conditions_json = json.dumps(conditions, ensure_ascii=False) if conditions else None
        metadata_json = json.dumps(metadata, ensure_ascii=False) if metadata else None

        # 对于canvas类型，hql字段存储JSON对象
        hql_content = hql
        if hql_type == "canvas":
            if isinstance(hql, dict):
                hql_content = json.dumps(hql, ensure_ascii=False)
            elif isinstance(hql, str):
                # 验证是否为有效的JSON字符串
                try:
                    json.loads(hql)
                    hql_content = hql
                except json.JSONDecodeError:
                    raise ValueError("canvas类型的hql必须是有效的JSON字符串")

        sql = """
            INSERT INTO hql_history (
                user_id, session_id, events_json, fields_json, conditions_json,
                mode, hql, performance_score, metadata_json, hql_type, game_gid, name_en, name_cn
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            sql,
            (
                user_id,
                session_id,
                events_json,
                fields_json,
                conditions_json,
                mode,
                hql_content,
                performance_score,
                metadata_json,
                hql_type,
                game_gid,
                name_en,
                name_cn,
            ),
        )
        conn.commit()
        lastrowid = cursor.lastrowid
        conn.close()

        return lastrowid

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

        return _fetch_all_as_dict(sql, params, db_path=self.db_path)

    def get_history_by_id(self, history_id: int) -> Optional[Dict]:
        """
        获取单个历史记录

        Args:
            history_id: 历史记录ID

        Returns:
            Optional[Dict]: 历史记录详情，不存在则返回None
        """
        sql = "SELECT * FROM hql_history WHERE id = ?"
        return _fetch_one_as_dict(sql, (history_id,), db_path=self.db_path)

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
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute(sql, (history_id,))
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount > 0

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
            for row in _fetch_all_as_dict(sql_keep, (user_id, keep_count), db_path=self.db_path)
        ]

        if not keep_ids:
            return 0

        # 删除不在保留列表中的记录
        placeholders = ",".join(["?" for _ in keep_ids])
        sql_delete = f"DELETE FROM hql_history WHERE user_id = ? AND id NOT IN ({placeholders})"
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute(sql_delete, [user_id] + keep_ids)
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()

        return rowcount

    def get_history_stats(self, user_id: int = 0) -> Dict:
        """
        获取历史统计信息

        Args:
            user_id: 用户ID

        Returns:
            Dict: 统计信息
        """
        sql_count = "SELECT COUNT(*) as count FROM hql_history WHERE user_id = ?"
        count_result = _fetch_one_as_dict(sql_count, (user_id,), db_path=self.db_path)

        sql_by_mode = """
            SELECT mode, COUNT(*) as count
            FROM hql_history
            WHERE user_id = ?
            GROUP BY mode
        """
        by_mode = _fetch_all_as_dict(sql_by_mode, (user_id,), db_path=self.db_path)

        sql_latest = """
            SELECT created_at FROM hql_history
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        """
        latest = _fetch_one_as_dict(sql_latest, (user_id,), db_path=self.db_path)

        return {
            "total_count": count_result["count"] if count_result else 0,
            "by_mode": {row["mode"]: row["count"] for row in by_mode},
            "latest_created_at": latest["created_at"] if latest else None,
        }

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
    ) -> List[Dict]:
        """
        搜索HQL历史记录（支持模糊搜索和多条件过滤）

        Args:
            keyword: 搜索关键词（模糊匹配hql_content, name_en, name_cn）
            hql_type: HQL类型过滤 (select/ddl/dml/canvas)
            game_gid: 游戏GID过滤
            user_id: 用户ID过滤
            date_from: 起始日期 (ISO 8601)
            date_to: 结束日期 (ISO 8601)
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            List[Dict]: 历史记录列表
        """
        # Build WHERE clause
        where_conditions = []
        params = []

        # Keyword search (fuzzy match)
        if keyword:
            where_conditions.append("""
                (hql LIKE ? OR name_en LIKE ? OR name_cn LIKE ?)
            """)
            keyword_pattern = f"%{keyword}%"
            params.extend([keyword_pattern, keyword_pattern, keyword_pattern])

        # HQL type filter
        if hql_type:
            where_conditions.append("hql_type = ?")
            params.append(hql_type)

        # Game GID filter
        if game_gid is not None:
            where_conditions.append("game_gid = ?")
            params.append(game_gid)

        # User ID filter
        if user_id is not None:
            where_conditions.append("user_id = ?")
            params.append(user_id)

        # Date range filter
        if date_from:
            where_conditions.append("created_at >= ?")
            params.append(date_from)

        if date_to:
            where_conditions.append("created_at <= ?")
            params.append(date_to)

        # Construct SQL
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

        sql = f"""
            SELECT * FROM hql_history
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """

        params.extend([limit, offset])

        return _fetch_all_as_dict(sql, tuple(params), db_path=self.db_path)

    def global_search_history(
        self,
        keyword: Optional[str] = None,
        hql_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict]:
        """
        全局搜索HQL历史记录（跨所有用户和会话）

        Args:
            keyword: 搜索关键词（模糊匹配hql_content, name_en, name_cn）
            hql_type: HQL类型过滤 (select/ddl/dml/canvas)
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            List[Dict]: 历史记录列表
        """
        # Build WHERE clause
        where_conditions = []
        params = []

        # Keyword search (fuzzy match)
        if keyword:
            where_conditions.append("""
                (hql LIKE ? OR name_en LIKE ? OR name_cn LIKE ?)
            """)
            keyword_pattern = f"%{keyword}%"
            params.extend([keyword_pattern, keyword_pattern, keyword_pattern])

        # HQL type filter
        if hql_type:
            where_conditions.append("hql_type = ?")
            params.append(hql_type)

        # Construct SQL
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

        sql = f"""
            SELECT
                id,
                user_id,
                session_id,
                mode,
                hql_type,
                game_gid,
                name_en,
                name_cn,
                hql,
                performance_score,
                created_at
            FROM hql_history
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """

        params.extend([limit, offset])

        return _fetch_all_as_dict(sql, tuple(params), db_path=self.db_path)
