"""
通用数据访问层 (Repository Pattern)

提供统一的CRUD操作接口，消除重复的SQL查询代码
支持可选的缓存集成以提升查询性能
"""

import logging
from typing import List, Dict, Any, Optional
from backend.core.utils.converters import fetch_one_as_dict, fetch_all_as_dict

# Import execute_write from backend.core.utils.utils (the original utils.py file)
# Using importlib to avoid circular import with the utils package
import importlib.util
import os

spec = importlib.util.spec_from_file_location(
    "backend.core.utils_utils", os.path.join(os.path.dirname(__file__), "utils.py")
)
utils_utils_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils_utils_module)
execute_write = utils_utils_module.execute_write

logger = logging.getLogger(__name__)


class GenericRepository:
    """
    通用仓储模式实现

    提供标准的数据访问方法，避免重复的SQL查询代码
    支持可选的缓存以提升性能
    """

    ALLOWED_TABLES: set = {
        "games",
        "log_events",
        "event_params",
        "event_categories",
        "flow_templates",
        "event_nodes",
        "parameter_aliases",
        "param_library",
        "common_params",
        "join_configs",
        "event_node_configs",
        "param_templates",
        "param_versions",
        "param_configs",
        "param_validation_rules",
        "batch_import_records",
        "batch_import_details",
        "param_dependencies",
        "hql_statements",
        "hql_history",
        "hql_generation_templates",
        "field_selection_presets",
        "node_templates",
        "async_tasks",
        "field_name_mappings",
        "field_name_history",
        "event_category_relations",
        "event_common_params",
        "sql_optimizations",
        "canvas",
        "parameters",
        "logs",
    }

    def __init__(
        self,
        table_name: str,
        primary_key: str = "id",
        enable_cache: bool = False,
        cache_timeout: int = 60,
    ):
        """
        初始化仓储

        Args:
            table_name: 表名
            primary_key: 主键字段名（默认为'id'）
            enable_cache: 是否启用缓存（默认False）
            cache_timeout: 缓存超时时间（秒，默认60）

        Raises:
            ValueError: 如果表名不在白名单中
        """
        from backend.core.security.sql_validator import SQLValidator

        SQLValidator.validate_table_name(table_name)
        if table_name not in self.ALLOWED_TABLES:
            raise ValueError(
                f"Invalid table name: '{table_name}'. "
                f"Allowed tables: {', '.join(sorted(self.ALLOWED_TABLES))}"
            )
        self.table_name = table_name
        self.primary_key = primary_key
        self.enable_cache = enable_cache
        self.cache_timeout = cache_timeout
        self._cache = None

        if enable_cache:
            try:
                from backend.core.cache.cache_system import cache

                self._cache = cache
            except ImportError:
                self.enable_cache = False

    def find_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """
        按ID查询单条记录

        取代所有: SELECT * FROM {table} WHERE id = ?

        Args:
            record_id: 记录ID

        Returns:
            记录字典，不存在返回None
        """
        # 尝试从缓存获取
        if self.enable_cache and self._cache:
            cache_key = f"{self.table_name}:id:{record_id}"
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cached

        # 从数据库查询
        query = f"SELECT * FROM {self.table_name} WHERE {self.primary_key} = ?"
        result = fetch_one_as_dict(query, (record_id,))

        # 存入缓存
        if self.enable_cache and self._cache and result:
            cache_key = f"{self.table_name}:id:{record_id}"
            self._cache.set(cache_key, result, timeout=self.cache_timeout)

        return result

    def find_by_field(self, field: str, value: Any) -> Optional[Dict[str, Any]]:
        """
        按字段查询单条记录

        用于: SELECT id FROM games WHERE gid = ?

        Args:
            field: 字段名
            value: 字段值

        Returns:
            记录字典，不存在返回None

        Raises:
            ValueError: 如果字段名无效
        """
        from backend.core.security.sql_validator import SQLValidator

        SQLValidator.validate_column_name(field)
        query = f"SELECT * FROM {self.table_name} WHERE {field} = ?"
        return fetch_one_as_dict(query, (value,))

    def find_where(
        self,
        conditions: Dict[str, Any],
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        按条件查询记录

        Args:
            conditions: 条件字典 {field: value}
            order_by: 排序字段
            limit: 限制数量

        Returns:
            记录列表

        Raises:
            ValueError: 如果字段名无效
        """
        from backend.core.security.sql_validator import SQLValidator

        for field in conditions.keys():
            SQLValidator.validate_column_name(field)
        where_clause = " AND ".join([f"{k} = ?" for k in conditions.keys()])
        query = f"SELECT * FROM {self.table_name}"

        if where_clause:
            query += f" WHERE {where_clause}"

        if order_by:
            query += f" ORDER BY {order_by}"

        if limit:
            query += f" LIMIT {limit}"

        return fetch_all_as_dict(query, tuple(conditions.values()))

    def find_first_where(self, conditions: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        按条件查询第一条记录

        Args:
            conditions: 条件字典

        Returns:
            记录或None
        """
        results = self.find_where(conditions, limit=1)
        return results[0] if results else None

    def find_all(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        查询所有记录

        Args:
            limit: 限制返回数量

        Returns:
            记录列表
        """
        query = f"SELECT * FROM {self.table_name}"
        if limit:
            query += f" LIMIT {limit}"

        return fetch_all_as_dict(query)

    def create(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a single record in the table.

        Args:
            data: Dictionary containing column names and values

        Returns:
            The created record as a dictionary, or None if creation fails

        Example:
            >>> repo = GameRepository()
            >>> game = repo.create({'gid': 'TEST_001', 'name': 'Test Game'})
        """
        # Reuse create_batch for consistency
        record_ids = self.create_batch([data])

        # Return the created record
        if record_ids and record_ids[0]:
            return self.find_by_id(record_ids[0])

        return None

    def update(self, record_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a single record by its primary key.

        Args:
            record_id: The primary key value of the record to update
            data: Dictionary containing column names and values to update

        Returns:
            The updated record as a dictionary, or None if update fails

        Example:
            >>> repo = GameRepository()
            >>> game = repo.update(1, {'name': 'Updated Name'})
        """
        if not self.primary_key:
            raise ValueError(
                f"Cannot update: no primary key defined for table '{self.table_name}'"
            )

        if not data:
            raise ValueError("Cannot update: no data provided for update")

        from backend.core.security.sql_validator import SQLValidator

        for field in data.keys():
            SQLValidator.validate_column_name(field)

        # Build UPDATE query
        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        query = f"""
            UPDATE {self.table_name}
            SET {set_clause}
            WHERE {self.primary_key} = ?
        """

        # Execute update
        values = list(data.values()) + [record_id]
        updated_count = execute_write(query, tuple(values))

        # Clear cache if update was successful
        if updated_count > 0 and self.enable_cache and self._cache:
            cache_key = f"{self.table_name}:id:{record_id}"
            self._cache.delete(cache_key)
            # Also clear the entire table cache pattern
            try:
                from backend.core.cache.cache_system import clear_cache_pattern

                clear_cache_pattern(f"{self.table_name}:*")
            except ImportError:
                pass

        # Return updated record
        return self.find_by_id(record_id)

    def delete(self, record_id: int) -> bool:
        """
        删除记录

        取代所有: DELETE FROM {table} WHERE id = ?

        Args:
            record_id: 记录ID

        Returns:
            是否成功
        """
        query = f"DELETE FROM {self.table_name} WHERE {self.primary_key} = ?"
        result = execute_write(query, (record_id,)) > 0

        # 删除成功时，清除相关缓存
        if result and self.enable_cache and self._cache:
            cache_key = f"{self.table_name}:id:{record_id}"
            self._cache.delete(cache_key)
            # 也清除整个表的缓存模式
            try:
                from backend.core.cache.cache_system import clear_cache_pattern

                clear_cache_pattern(f"{self.table_name}:*")
            except ImportError:
                pass

        return result

    def exists(self, record_id: int) -> bool:
        """
        检查记录是否存在

        Args:
            record_id: 记录ID

        Returns:
            是否存在
        """
        return self.find_by_id(record_id) is not None

    def find_by_ids(self, record_ids: List[int]) -> List[Dict[str, Any]]:
        """
        批量查询多个ID的记录

        取代所有: SELECT * FROM {table} WHERE id IN (?, ?, ?)

        Args:
            record_ids: 记录ID列表

        Returns:
            记录列表，不存在的ID会被忽略
        """
        if not record_ids:
            return []

        # 从缓存获取存在的记录
        cached_records = {}
        uncached_ids = []

        if self.enable_cache and self._cache:
            for record_id in record_ids:
                cache_key = f"{self.table_name}:id:{record_id}"
                cached = self._cache.get(cache_key)
                if cached is not None:
                    cached_records[record_id] = cached
                else:
                    uncached_ids.append(record_id)
        else:
            uncached_ids = record_ids

        # 查询未缓存的记录
        db_records = []
        if uncached_ids:
            placeholders = ",".join(["?" for _ in uncached_ids])
            query = f"SELECT * FROM {self.table_name} WHERE {self.primary_key} IN ({placeholders})"
            db_records = fetch_all_as_dict(query, tuple(uncached_ids))

            # 存入缓存
            if self.enable_cache and self._cache:
                for record in db_records:
                    cache_key = f"{self.table_name}:id:{record[self.primary_key]}"
                    self._cache.set(cache_key, record, timeout=self.cache_timeout)

        # 合并缓存和数据库查询结果
        all_records = list(cached_records.values()) + db_records

        # 按原始ID顺序排序
        id_to_record = {r[self.primary_key]: r for r in all_records}
        ordered_records = []
        for record_id in record_ids:
            if record_id in id_to_record:
                ordered_records.append(id_to_record[record_id])

        return ordered_records

    def delete_batch(self, record_ids: List[int]) -> int:
        """
        批量删除多个ID的记录

        取代所有: DELETE FROM {table} WHERE id IN (?, ?, ?)

        Args:
            record_ids: 记录ID列表

        Returns:
            实际删除的记录数
        """
        if not record_ids:
            return 0

        placeholders = ",".join(["?" for _ in record_ids])
        query = f"DELETE FROM {self.table_name} WHERE {self.primary_key} IN ({placeholders})"
        deleted_count = execute_write(query, tuple(record_ids))

        # 删除成功时，清除相关缓存
        if deleted_count > 0 and self.enable_cache and self._cache:
            for record_id in record_ids:
                cache_key = f"{self.table_name}:id:{record_id}"
                self._cache.delete(cache_key)
            # 也清除整个表的缓存模式
            try:
                from backend.core.cache.cache_system import clear_cache_pattern

                clear_cache_pattern(f"{self.table_name}:*")
            except ImportError:
                pass

        return deleted_count

    def update_batch(self, record_ids: List[int], updates: Dict[str, Any]) -> int:
        """
        批量更新多条记录的指定字段

        取代所有: UPDATE {table} SET field1=? WHERE id IN (?, ?, ?)

        Args:
            record_ids: 记录ID列表
            updates: 要更新的字段字典 {field_name: new_value}

        Returns:
            实际更新的记录数
        """
        if not record_ids or not updates:
            return 0

        from backend.core.security.sql_validator import SQLValidator

        for field in updates.keys():
            SQLValidator.validate_column_name(field)

        # 构建SET子句
        set_clause = ", ".join([f"{field} = ?" for field in updates.keys()])
        placeholders = ",".join(["?" for _ in record_ids])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE {self.primary_key} IN ({placeholders})"

        # 合并更新值和ID值
        values = list(updates.values()) + record_ids
        updated_count = execute_write(query, tuple(values))

        # 更新成功时，清除相关缓存
        if updated_count > 0 and self.enable_cache and self._cache:
            for record_id in record_ids:
                cache_key = f"{self.table_name}:id:{record_id}"
                self._cache.delete(cache_key)
            # 也清除整个表的缓存模式
            try:
                from backend.core.cache.cache_system import clear_cache_pattern

                clear_cache_pattern(f"{self.table_name}:*")
            except ImportError:
                pass

        return updated_count

    def create_batch(self, records: List[Dict[str, Any]]) -> List[int]:
        """
        批量创建多条记录

        取代所有: 多次单独调用 create()

        注意：由于SQLite的executemany()不返回lastrowid，此方法使用循环插入。
        但保持在单个事务中，仍然比多次单独调用create()更高效。

        Args:
            records: 要创建的记录列表，每个记录是一个字典

        Returns:
            插入记录的ID列表（按输入顺序）
        """
        if not records:
            return []

        # 获取数据库连接以支持事务
        from backend.core.database.database import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        inserted_ids = []

        try:
            # 获取所有字段名（从所有记录中）
            all_fields = set()
            for record in records:
                all_fields.update(record.keys())
            all_fields.discard("id")  # 移除id字段（自动生成）

            from backend.core.security.sql_validator import SQLValidator

            for field in all_fields:
                SQLValidator.validate_column_name(field)

            field_list = list(all_fields)
            field_names = ", ".join(field_list)
            placeholders = ", ".join(["?" for _ in field_list])

            # 构建单条插入SQL
            insert_sql = (
                f"INSERT INTO {self.table_name} ({field_names}) VALUES ({placeholders})"
            )

            # 在单个事务中循环插入所有记录
            for record in records:
                # 按字段顺序准备值
                values = [record.get(field) for field in field_list]
                cursor.execute(insert_sql, tuple(values))

                # 收集插入的ID
                inserted_ids.append(cursor.lastrowid)

            # 提交事务
            conn.commit()

            # 清除缓存
            if self.enable_cache and self._cache:
                for record_id in inserted_ids:
                    cache_key = f"{self.table_name}:id:{record_id}"
                    self._cache.delete(cache_key)
                try:
                    from backend.core.cache.cache_system import clear_cache_pattern

                    clear_cache_pattern(f"{self.table_name}:*")
                except ImportError:
                    pass

            return inserted_ids

        except Exception as e:
            # 回滚事务
            conn.rollback()
            logger.error(f"Error in create_batch for {self.table_name}: {e}")
            raise
        finally:
            conn.close()


class Repositories:
    """预定义的仓储实例，便于直接使用（无缓存）"""

    GAMES = GenericRepository("games", primary_key="id")
    FLOW_TEMPLATES = GenericRepository("flow_templates", primary_key="id")
    EVENT_NODE_CONFIGS = GenericRepository("event_node_configs", primary_key="id")
    JOIN_CONFIGS = GenericRepository("join_configs", primary_key="id")
    LOG_EVENTS = GenericRepository("log_events", primary_key="id")
    EVENT_CATEGORIES = GenericRepository("event_categories", primary_key="id")
    EVENT_PARAMS = GenericRepository("event_params", primary_key="id")
    LOGS = GenericRepository("logs", primary_key="id")
    COMMON_PARAMS = GenericRepository("common_params", primary_key="id")


class CachedRepositories:
    """启用缓存的仓储实例，适用于读多写少的场景"""

    GAMES = GenericRepository(
        "games", primary_key="id", enable_cache=True, cache_timeout=120
    )
    FLOW_TEMPLATES = GenericRepository(
        "flow_templates", primary_key="id", enable_cache=True, cache_timeout=120
    )
    EVENT_NODE_CONFIGS = GenericRepository(
        "event_node_configs", primary_key="id", enable_cache=True, cache_timeout=60
    )
    JOIN_CONFIGS = GenericRepository(
        "join_configs", primary_key="id", enable_cache=True, cache_timeout=60
    )
    LOG_EVENTS = GenericRepository(
        "log_events", primary_key="id", enable_cache=True, cache_timeout=30
    )  # 短缓存
    EVENT_CATEGORIES = GenericRepository(
        "event_categories", primary_key="id", enable_cache=True, cache_timeout=300
    )  # 长缓存
    EVENT_PARAMS = GenericRepository(
        "event_params", primary_key="id", enable_cache=True, cache_timeout=60
    )
    LOGS = GenericRepository(
        "logs", primary_key="id", enable_cache=True, cache_timeout=30
    )  # 短缓存
    COMMON_PARAMS = GenericRepository(
        "common_params", primary_key="id", enable_cache=True, cache_timeout=300
    )  # 长缓存
