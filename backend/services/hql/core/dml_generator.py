"""
DML生成器 - Data Manipulation Language Generator

负责生成INSERT OVERWRITE等DML语句
完全独立、无业务依赖的DML生成器
"""

import re
from typing import Optional, List, Dict, Any
from datetime import datetime


class DMLGenerator:
    """
    DML生成器

    专门负责生成INSERT OVERWRITE TABLE等DML语句
    与DDL生成器配合使用，完成完整的ETL流程

    Examples:
        >>> from backend.services.hql.core.dml_generator import DMLGenerator
        >>>
        >>> generator = DMLGenerator()
        >>>
        >>> # 生成INSERT OVERWRITE语句
        >>> dml = generator.generate_insert_overwrite(
        ...     target_table="dwd.v_dwd_10000147_login_di",
        ...     source_query="SELECT role_id, account_id FROM ods_table",
        ...     partition_ds="20260217"
        ... )
        >>> print(dml)
    """

    # 危险的SQL关键字（用于表名验证）
    DANGEROUS_KEYWORDS = [
        "DROP",
        "DELETE",
        "TRUNCATE",
        "ALTER",
        "CREATE",
        "UPDATE",
        "EXEC",
        "EXECUTE",
        "SCRIPT",
        "--",
        "/*",
        "*/",
        ";",
        "xp_",
        "sp_",
    ]

    def __init__(self):
        """初始化DML生成器"""
        pass

    def generate_insert_overwrite(
        self,
        target_table: str,
        source_query: str,
        partition_ds: str,
        **options
    ) -> str:
        """
        生成INSERT OVERWRITE语句

        这是Hive数据仓库中最常用的DML操作，用于覆盖写入分区数据

        Args:
            target_table: 目标表名（格式: database.table）
                示例: dwd.v_dwd_10000147_login_di
            source_query: 源查询语句（SELECT语句）
                示例: "SELECT role_id, account_id FROM ods_table WHERE ds = '${bizdate}'"
            partition_ds: 分区日期值
                格式: YYYYMMDD (如: 20260217)
                支持动态变量: '${bizdate}', '${ds}'
            **options: 额外选项
                - include_if_not_exist: 是否添加IF NOT EXISTS（默认False）
                - include_comments: 是否包含注释（默认True）
                - overwrite_table: 是否覆盖整个表（默认False，仅覆盖分区）

        Returns:
            str: 完整的INSERT OVERWRITE语句

        Raises:
            ValueError: 当参数验证失败时

        Examples:
            >>> generator = DMLGenerator()
            >>> dml = generator.generate_insert_overwrite(
            ...     target_table="dwd.v_dwd_10000147_login_di",
            ...     source_query="SELECT role_id, account_id FROM ods_table",
            ...     partition_ds="20260217"
            ... )
            >>> print(dml)
            INSERT OVERWRITE TABLE dwd.v_dwd_10000147_login_di
            PARTITION (ds='20260217')
            SELECT role_id, account_id FROM ods_table

            >>> # 使用动态分区变量
            >>> dml = generator.generate_insert_overwrite(
            ...     target_table="dwd.v_dwd_10000147_login_di",
            ...     source_query="SELECT * FROM staging_table",
            ...     partition_ds="${bizdate}"
            ... )
        """
        # 验证参数
        self._validate_target_table(target_table)
        self._validate_source_query(source_query)
        self._validate_partition_ds(partition_ds)

        # 获取选项
        include_comments = options.get("include_comments", True)

        # 构建INSERT OVERWRITE语句
        dml_parts = []

        # 添加注释
        if include_comments:
            comments = self._build_comments(target_table, partition_ds)
            dml_parts.append(comments)

        # 构建主语句
        insert_statement = self._build_insert_overwrite(
            target_table=target_table,
            source_query=source_query,
            partition_ds=partition_ds,
            **options
        )
        dml_parts.append(insert_statement)

        return "\n".join(dml_parts)

    def generate_insert_overwrite_directory(
        self,
        target_directory: str,
        source_query: str,
        **options
    ) -> str:
        """
        生成INSERT OVERWRITE DIRECTORY语句（导出到文件系统）

        Args:
            target_directory: 目标目录路径（HDFS路径）
                示例: hdfs:///data/export/20260217
            source_query: 源查询语句
            **options: 额外选项
                - file_format: 文件格式（默认: TEXTFILE）
                    支持: TEXTFILE, PARQUET, ORC, AVRO
                - field_delim: 字段分隔符（默认: \\t）
                - line_delim: 行分隔符（默认: \\n）
                - include_comments: 是否包含注释（默认True）

        Returns:
            str: INSERT OVERWRITE DIRECTORY语句

        Examples:
            >>> generator = DMLGenerator()
            >>> dml = generator.generate_insert_overwrite_directory(
            ...     target_directory="hdfs:///data/export/20260217",
            ...     source_query="SELECT * FROM dwd_table"
            ... )
        """
        # 验证参数
        if not target_directory or not target_directory.strip():
            raise ValueError("target_directory cannot be empty")

        self._validate_source_query(source_query)

        # 获取选项
        file_format = options.get("file_format", "TEXTFILE")
        field_delim = options.get("field_delim", "\\t")
        line_delim = options.get("line_delim", "\\n")
        include_comments = options.get("include_comments", True)

        # 构建语句
        dml_parts = []

        if include_comments:
            dml_parts.append(f"-- Export to directory: {target_directory}")

        # INSERT OVERWRITE DIRECTORY
        dml_parts.append(f"INSERT OVERWRITE DIRECTORY '{target_directory}'")
        dml_parts.append(f"ROW FORMAT DELIMITED")
        dml_parts.append(f"FIELDS TERMINATED BY '{field_delim}'")
        dml_parts.append(f"LINES TERMINATED BY '{line_delim}'")
        dml_parts.append(f"STORED AS {file_format}")
        dml_parts.append(source_query)

        return "\n".join(dml_parts)

    def _build_insert_overwrite(
        self,
        target_table: str,
        source_query: str,
        partition_ds: str,
        **options
    ) -> str:
        """
        构建INSERT OVERWRITE核心语句

        Args:
            target_table: 目标表名
            source_query: 源查询
            partition_ds: 分区日期
            **options: 额外选项

        Returns:
            str: INSERT OVERWRITE语句
        """
        # 格式化源查询（去除多余的空白行）
        formatted_query = self._format_query(source_query)

        # 构建语句
        dml = f"""INSERT OVERWRITE TABLE {target_table}
PARTITION (ds='{partition_ds}')
{formatted_query}"""

        return dml

    def _build_comments(self, target_table: str, partition_ds: str) -> str:
        """
        构建注释信息

        Args:
            target_table: 目标表名
            partition_ds: 分区日期

        Returns:
            str: 注释文本
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        comments = [
            f"-- Generated by Event2Table DML Generator",
            f"-- Timestamp: {timestamp}",
            f"-- Target Table: {target_table}",
            f"-- Partition: ds='{partition_ds}'",
            f"-- Description: INSERT OVERWRITE for partition loading"
        ]

        return "\n".join(comments)

    def _format_query(self, query: str) -> str:
        """
        格式化查询语句

        去除多余的空白行，保持基本格式

        Args:
            query: 原始查询

        Returns:
            str: 格式化后的查询
        """
        # 去除首尾空白
        query = query.strip()

        # 压缩多个连续空行为单行
        query = re.sub(r'\n\s*\n\s*\n+', '\n\n', query)

        return query

    def _validate_target_table(self, table_name: str) -> None:
        """
        验证目标表名

        Args:
            table_name: 表名

        Raises:
            ValueError: 当表名无效时
        """
        if not table_name or not table_name.strip():
            raise ValueError("target_table cannot be empty")

        # 基本格式验证（应该包含database.table）
        if "." not in table_name:
            raise ValueError(
                f"target_table must be in format 'database.table', got: {table_name}"
            )

        # 检查危险关键字
        table_upper = table_name.upper()
        for keyword in self.DANGEROUS_KEYWORDS:
            if keyword in table_upper:
                raise ValueError(
                    f"Dangerous SQL keyword '{keyword}' found in target_table. "
                    f"This could be a SQL injection attempt."
                )

    def _validate_source_query(self, query: str) -> None:
        """
        验证源查询语句

        Args:
            query: 查询语句

        Raises:
            ValueError: 当查询无效时
        """
        if not query or not query.strip():
            raise ValueError("source_query cannot be empty")

        # 检查危险操作
        query_upper = query.upper()
        dangerous_operations = [
            "DROP TABLE",
            "DELETE FROM",
            "TRUNCATE",
            "ALTER TABLE",
            "CREATE TABLE",
            "UPDATE",
            "INSERT",
        ]

        for operation in dangerous_operations:
            if operation in query_upper:
                raise ValueError(
                    f"Dangerous operation '{operation}' found in source_query. "
                    f"source_query should be a SELECT statement only."
                )

        # 检查是否以SELECT开头（允许注释）
        stripped = query.lstrip()
        if not stripped.upper().startswith("SELECT") and not stripped.startswith("--"):
            raise ValueError(
                f"source_query must be a SELECT statement, got: {stripped[:50]}..."
            )

    def _validate_partition_ds(self, partition_ds: str) -> None:
        """
        验证分区日期格式

        Args:
            partition_ds: 分区日期

        Raises:
            ValueError: 当日期格式无效时
        """
        if not partition_ds or not partition_ds.strip():
            raise ValueError("partition_ds cannot be empty")

        # 支持动态变量（Hive变量）
        if partition_ds.startswith("${") and partition_ds.endswith("}"):
            return

        # 验证日期格式：YYYYMMDD
        if not re.match(r'^\d{8}$', partition_ds):
            raise ValueError(
                f"partition_ds must be in format YYYYMMDD (e.g., 20260217), "
                f"got: {partition_ds}"
            )

        # 验证日期有效性
        try:
            datetime.strptime(partition_ds, "%Y%m%d")
        except ValueError:
            raise ValueError(
                f"partition_ds contains invalid date: {partition_ds}"
            )


class DMLBuilderFactory:
    """
    DML构建器工厂

    提供便捷的构建方法
    """

    @staticmethod
    def create_etl_dml(
        dwd_prefix: str,
        game_gid: int,
        event_name: str,
        source_query: str,
        partition_ds: str
    ) -> str:
        """
        创建标准ETL DML语句

        按照项目约定生成目标表名和DML语句

        Args:
            dwd_prefix: DWD层数据库前缀（如: dwd）
            game_gid: 游戏业务GID（如: 10000147）
            event_name: 事件名称（如: login）
            source_query: 源查询
            partition_ds: 分区日期

        Returns:
            str: INSERT OVERWRITE语句

        Examples:
            >>> dml = DMLBuilderFactory.create_etl_dml(
            ...     dwd_prefix="dwd",
            ...     game_gid=10000147,
            ...     event_name="login",
            ...     source_query="SELECT * FROM ods_table",
            ...     partition_ds="20260217"
            ... )
        """
        generator = DMLGenerator()

        # 按照项目约定生成目标表名
        target_table = f"{dwd_prefix}.v_dwd_{game_gid}_{event_name}_di"

        return generator.generate_insert_overwrite(
            target_table=target_table,
            source_query=source_query,
            partition_ds=partition_ds
        )

    @staticmethod
    def create_batch_insert(
        target_table: str,
        source_queries: List[str],
        partition_ds: str
    ) -> str:
        """
        创建批量插入语句（使用UNION ALL）

        Args:
            target_table: 目标表
            source_queries: 源查询列表
            partition_ds: 分区日期

        Returns:
            str: 批量INSERT OVERWRITE语句
        """
        if not source_queries:
            raise ValueError("source_queries cannot be empty")

        if len(source_queries) == 1:
            generator = DMLGenerator()
            return generator.generate_insert_overwrite(
                target_table=target_table,
                source_query=source_queries[0],
                partition_ds=partition_ds
            )

        # 多个查询使用UNION ALL合并
        union_query = "UNION ALL\n".join(source_queries)

        generator = DMLGenerator()
        return generator.generate_insert_overwrite(
            target_table=target_table,
            source_query=union_query,
            partition_ds=partition_ds
        )


# 便捷函数
def generate_insert_overwrite(
    target_table: str,
    source_query: str,
    partition_ds: str,
    **options
) -> str:
    """
    生成INSERT OVERWRITE语句（便捷函数）

    Args:
        target_table: 目标表名
        source_query: 源查询
        partition_ds: 分区日期
        **options: 额外选项

    Returns:
        str: INSERT OVERWRITE语句

    Examples:
        >>> dml = generate_insert_overwrite(
        ...     target_table="dwd.v_dwd_10000147_login_di",
        ...     source_query="SELECT role_id FROM ods_table",
        ...     partition_ds="20260217"
        ... )
    """
    generator = DMLGenerator()
    return generator.generate_insert_overwrite(
        target_table=target_table,
        source_query=source_query,
        partition_ds=partition_ds,
        **options
    )
