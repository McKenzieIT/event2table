"""
HQL语法校验器

使用sqlparse库验证Hive SQL语法
提供详细的错误位置和修复建议
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

# 尝试导入sqlparse，如果没有安装则提供基本功能
try:
    import sqlparse
    from sqlparse.sql import Identifier, IdentifierList, Comparison
    from sqlparse.tokens import Token, Error

    SQLPARSE_AVAILABLE = True
except ImportError:
    SQLPARSE_AVAILABLE = False


@dataclass
class SyntaxError:
    """语法错误"""

    line: int
    column: int
    message: str
    error_type: str  # 'error' | 'warning'
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """验证结果"""

    is_valid: bool
    errors: List[SyntaxError] = field(default_factory=list)
    warnings: List[SyntaxError] = field(default_factory=list)
    parse_tree: Optional[Any] = None


class SyntaxValidator:
    """
    HQL语法校验器

    使用sqlparse库进行Hive SQL语法解析
    """

    # Hive关键字
    HIVE_KEYWORDS = {
        "SELECT",
        "FROM",
        "WHERE",
        "JOIN",
        "INNER",
        "LEFT",
        "RIGHT",
        "FULL",
        "OUTER",
        "ON",
        "AND",
        "OR",
        "NOT",
        "IN",
        "EXISTS",
        "BETWEEN",
        "LIKE",
        "RLIKE",
        "GROUP",
        "BY",
        "HAVING",
        "ORDER",
        "LIMIT",
        "OFFSET",
        "UNION",
        "UNION ALL",
        "INTERSECT",
        "MINUS",
        "INSERT",
        "UPDATE",
        "DELETE",
        "CREATE",
        "DROP",
        "ALTER",
        "TRUNCATE",
        "TABLE",
        "VIEW",
        "INDEX",
        "DATABASE",
        "SCHEMA",
        "PARTITIONED",
        "CLUSTERED",
        "SORTED",
        "LATERAL VIEW",
        "EXPLODE",
        "SPLIT",
    }

    # Hive函数
    HIVE_FUNCTIONS = {
        "get_json_object",
        "json_tuple",
        "parse_url",
        "regexp_extract",
        "regexp_replace",
        "split",
        "explode",
        "posexplode",
        "count",
        "sum",
        "avg",
        "min",
        "max",
        "stddev",
        "rank",
        "row_number",
        "dense_rank",
        "ntile",
        "lead",
        "lag",
        "first_value",
        "last_value",
        "cast",
        "convert",
        "coalesce",
        "nullif",
        "isnull",
        "nvl",
    }

    # 常见错误模式
    ERROR_PATTERNS = {
        "SELECT_STAR": {
            "pattern": r"SELECT\s+\*\s+FROM",
            "message": "避免使用SELECT *，明确列出所需字段",
            "suggestion": "明确列出所有需要的字段名",
        },
        "MISSING_WHERE": {
            "pattern": r"CREATE\s+(OR\s+REPLACE\s+)?VIEW.*?WHERE\s+\'\$\{",
            "message": "WHERE子句缺少分区过滤",
            "suggestion": "添加分区过滤条件，如: WHERE ds = '${bizdate}'",
        },
        "MISSING_QUOTES": {
            "pattern": r'=\s*[\'"][^\'"]*[\'"]\s+',
            "message": "字符串值未加引号",
            "suggestion": "给字符串值加上单引号，如: value = 'value'",
        },
        "UNION_WITHOUT_ALL": {
            "pattern": r"UNION\s+(?!ALL)",
            "message": "UNION后应该加ALL以保留去重",
            "suggestion": "使用UNION ALL代替UNION",
        },
    }

    def validate(self, hql: str) -> ValidationResult:
        """
        验证HQL语法

        Args:
            hql: HQL语句

        Returns:
            ValidationResult: 验证结果
        """
        errors = []
        warnings = []

        # 1. 基础格式检查
        format_errors = self._check_format(hql)
        errors.extend(format_errors)

        # 2. 尝试解析HQL（如果sqlparse可用）
        parse_tree = None
        if SQLPARSE_AVAILABLE:
            try:
                parse_tree = sqlparse.parse(hql)

                # 3. 语义检查
                semantic_errors = self._check_semantics(hql, parse_tree)
                errors.extend(semantic_errors)

            except Exception as e:
                # 解析失败
                errors.append(
                    SyntaxError(
                        line=0,
                        column=0,
                        message=f"语法解析失败: {str(e)}",
                        error_type="error",
                        suggestion="请检查HQL语法是否正确",
                    )
                )
        else:
            # 如果sqlparse不可用，添加警告
            warnings.append(
                SyntaxError(
                    line=0,
                    column=0,
                    message="sqlparse未安装，跳过高级语法检查",
                    error_type="warning",
                    suggestion="安装sqlparse以获得完整的语法验证: pip install sqlparse",
                )
            )

        # 4. 最佳实践检查
        practice_warnings = self._check_best_practices(hql)
        warnings.extend(practice_warnings)

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid, errors=errors, warnings=warnings, parse_tree=parse_tree
        )

    def _check_format(self, hql: str) -> List[SyntaxError]:
        """检查基础格式"""
        errors = []

        # 检查1: 必须包含CREATE VIEW或SELECT
        hql_upper = hql.upper()
        if "CREATE VIEW" not in hql_upper and "SELECT" not in hql_upper:
            errors.append(
                SyntaxError(
                    line=0,
                    column=0,
                    message="HQL必须包含CREATE VIEW或SELECT",
                    error_type="error",
                    suggestion="添加CREATE VIEW或SELECT语句",
                )
            )

        # 检查2: 必须包含FROM
        if "CREATE VIEW" in hql_upper or "SELECT" in hql_upper:
            if " FROM " not in hql_upper:
                errors.append(
                    SyntaxError(
                        line=0,
                        column=0,
                        message="缺少FROM子句",
                        error_type="error",
                        suggestion="添加FROM子句指定数据源",
                    )
                )

        # 检查3: 必须包含WHERE（分区过滤）
        if "WHERE" not in hql_upper:
            errors.append(
                SyntaxError(
                    line=0,
                    column=0,
                    message="缺少WHERE子句（分区过滤要求）",
                    error_type="error",
                    suggestion="添加WHERE子句，如: WHERE ds = '${bizdate}'",
                )
            )

        return errors

    def _check_semantics(self, hql: str, parse_tree) -> List[SyntaxError]:
        """检查语义"""
        errors = []

        # 检查1: 引号匹配
        errors.extend(self._check_quotes(hql))

        # 检查2: 括号匹配
        errors.extend(self._check_parentheses(hql))

        # 检查3: JOIN条件
        errors.extend(self._check_joins(hql, parse_tree))

        return errors

    def _check_quotes(self, hql: str) -> List[SyntaxError]:
        """检查引号匹配"""
        errors = []

        # 检查单引号
        single_quotes = hql.count("'")
        if single_quotes % 2 != 0:
            errors.append(
                SyntaxError(
                    line=0,
                    column=0,
                    message="单引号不匹配",
                    error_type="error",
                    suggestion="检查所有字符串值是否正确闭合",
                )
            )

        # 检查双引号（Hive中双引号需要转义）
        double_quotes = hql.count('"')
        if double_quotes > 0:
            errors.append(
                SyntaxError(
                    line=0,
                    column=0,
                    message="Hive中应避免使用双引号",
                    error_type="warning",
                    suggestion='使用单引号代替双引号，或转义双引号为\\"',
                )
            )

        return errors

    def _check_parentheses(self, hql: str) -> List[SyntaxError]:
        """检查括号匹配"""
        errors = []
        stack = []
        lines = hql.split("\n")

        for line_num, line in enumerate(lines, start=1):
            for col_num, char in enumerate(line, start=1):
                if char == "(":
                    stack.append(("(", line_num, col_num))
                elif char == ")":
                    if not stack:
                        errors.append(
                            SyntaxError(
                                line=line_num,
                                column=col_num,
                                message="右括号没有匹配的左括号",
                                error_type="error",
                                suggestion="检查括号配对",
                            )
                        )
                    elif stack[-1][0] == "(":
                        stack.pop()
                    else:
                        errors.append(
                            SyntaxError(
                                line=line_num,
                                column=col_num,
                                message=f"右括号匹配了{stack[-1][0]}",
                                error_type="error",
                                suggestion="检查括号类型",
                            )
                        )

        # 检查未闭合的左括号
        while stack:
            bracket_type, line_num, col_num = stack.pop()
            errors.append(
                SyntaxError(
                    line=line_num,
                    column=col_num,
                    message=f"未闭合的{bracket_type}括号",
                    error_type="error",
                    suggestion="添加闭合括号",
                )
            )

        return errors

    def _check_joins(self, hql: str, parse_tree) -> List[SyntaxError]:
        """检查JOIN语法"""
        errors = []

        # 检查JOIN是否包含ON条件
        join_pattern = r"(?:INNER|LEFT|RIGHT|FULL|CROSS)?\s+JOIN\s+(\w+)"
        joins = re.finditer(join_pattern, hql, re.IGNORECASE)

        for match in joins:
            join_text = hql[match.start() : match.start() + 50]  # 获取JOIN后50个字符
            if " ON " not in join_text[:100]:
                errors.append(
                    SyntaxError(
                        line=0,
                        column=0,
                        message=f"JOIN缺少ON条件",
                        error_type="error",
                        suggestion=f"为JOIN添加ON条件，如: {match.group(0)} {match.group(1)} ON t1.id = t2.id",
                    )
                )

        return errors

    def _check_best_practices(self, hql: str) -> List[SyntaxError]:
        """检查最佳实践"""
        warnings = []

        # 检查1: SELECT *
        if re.search(r"SELECT\s+\*\s+FROM", hql, re.IGNORECASE):
            warnings.append(
                SyntaxError(
                    line=0,
                    column=0,
                    message="避免使用SELECT *",
                    error_type="warning",
                    suggestion="明确列出所需字段名，避免查询大量不需要的数据",
                )
            )

        # 检查2: UNION没有ALL
        if re.search(r"UNION\s+(?!ALL)", hql):
            warnings.append(
                SyntaxError(
                    line=0,
                    column=0,
                    message="UNION后建议加ALL",
                    error_type="warning",
                    suggestion="使用UNION ALL保留所有记录，避免去重开销",
                )
            )

        # 检查3: 缺少分区字段过滤
        if "WHERE" in hql.upper():
            # 提取WHERE子句
            where_match = re.search(r"WHERE\s+([^;]+)", hql, re.IGNORECASE | re.DOTALL)
            if where_match:
                where_clause = where_match.group(1)
                # 检查是否包含常见分区字段
                partition_fields = ["ds", "dt", "day", "date"]
                has_partition_filter = any(
                    re.search(rf"\b{field}\b\s*=", where_clause, re.IGNORECASE)
                    for field in partition_fields
                )
                if not has_partition_filter:
                    warnings.append(
                        SyntaxError(
                            line=0,
                            column=0,
                            message="WHERE子句缺少分区字段过滤",
                            error_type="warning",
                            suggestion="添加分区字段过滤，如: WHERE ds = '${bizdate}'",
                        )
                    )

        # 检查4: 子查询性能
        subquery_count = hql.count("(") - hql.count(")")  # 简化估计
        if subquery_count > 3:
            warnings.append(
                SyntaxError(
                    line=0,
                    column=0,
                    message=f"检测到可能的嵌套子查询（{subquery_count}层）",
                    error_type="warning",
                    suggestion="考虑使用CTE或临时表简化复杂查询",
                )
            )

        return warnings

    def quick_validate(self, hql: str) -> Tuple[bool, List[str]]:
        """
        快速验证（简化版）

        Returns:
            Tuple[is_valid, error_messages]
        """
        result = self.validate(hql)
        error_messages = [f"{err.error_type}: {err.message}" for err in result.errors]
        return result.is_valid, error_messages


# 便捷函数
def validate_hql(hql: str) -> ValidationResult:
    """
    验证HQL语法（便捷函数）

    Args:
        hql: HQL语句

    Returns:
        ValidationResult: 验证结果
    """
    validator = SyntaxValidator()
    return validator.validate(hql)


def quick_validate_hql(hql: str) -> Tuple[bool, List[str]]:
    """
    快速验证HQL（便捷函数）

    Args:
        hql: HQL语句

    Returns:
        Tuple[is_valid, error_messages]
    """
    validator = SyntaxValidator()
    return validator.quick_validate(hql)


# 导出
__all__ = [
    "SyntaxValidator",
    "SyntaxError",
    "ValidationResult",
    "validate_hql",
    "quick_validate_hql",
]
