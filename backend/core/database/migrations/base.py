"""
数据库迁移基类
"""

import sqlite3


class BaseMigration:
    """数据库迁移基类"""

    version: int = 0

    def upgrade(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        """
        执行迁移

        Args:
            cursor: 数据库游标
            conn: 数据库连接
        """
        raise NotImplementedError("Subclasses must implement upgrade()")
