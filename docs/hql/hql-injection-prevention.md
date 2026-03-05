# HQL注入防护示例

## 概述

本文档提供HQL注入防护的实际案例，基于Event2Table项目中已修复的安全漏洞。通过对比**不安全代码**和**安全代码**，帮助开发者理解如何防止HQL注入攻击。

## 常见的HQL注入模式

### 模式1: 标识符注入

**攻击原理**: 攻击者在字段名、表名中注入恶意SQL代码

**攻击示例**:
```python
# 用户输入
field_name = "role_id; DROP TABLE users; --"

# ❌ 不安全代码
hql = f"SELECT {field_name} FROM events"

# 生成的HQL
SELECT role_id; DROP TABLE users; -- FROM events
```

**实际后果**:
- 生成多个HQL语句（第二个语句删除表）
- 注释符`--`导致后续代码被忽略
- 数据丢失风险

**防护方法**:

```python
# ✅ 安全代码
from backend.core.security.sql_validator import SQLValidator

def build_select_field(field_name: str) -> str:
    # 验证字段名
    validated_field = SQLValidator.validate_column_name(field_name)

    # 使用验证后的字段名
    return f"SELECT {validated_field} FROM events"

# 验证通过
build_select_field("role_id")
# 输出: SELECT role_id FROM events

# 验证失败
build_select_field("role_id; DROP TABLE users; --")
# 抛出异常: ValueError: Invalid column_name: 'role_id; DROP TABLE users; --'

# ⚠️ 注意：HQL表名需要特殊处理（包含数据库前缀）
def validate_hql_table_name(table_name: str) -> str:
    """验证HQL表名（database.table格式）"""
    if '.' not in table_name:
        raise ValueError(f"HQL table name must contain database prefix: {table_name}")

    parts = table_name.split('.')
    if len(parts) != 2:
        raise ValueError(f"Invalid HQL table name format: {table_name}")

    database, table = parts
    validated_db = SQLValidator.validate_identifier(database, "database")
    validated_table = SQLValidator.validate_identifier(table, "table")

    return f"{validated_db}.{validated_table}"
```

### 模式2: 操作符注入

**攻击原理**: 攻击者篡改WHERE条件的操作符，绕过验证逻辑

**攻击示例**:
```python
# 用户输入
operator = "OR 1=1 --"

# ❌ 不安全代码
hql = f"WHERE role_id {operator} '{value}'"

# 生成的HQL
WHERE role_id OR 1=1 -- '{value}'
```

**实际后果**:
- 条件始终为真（`1=1`）
- 注释符导致后续验证失效
- 数据泄露风险

**防护方法**:

```python
# ✅ 安全代码
class WhereBuilder:
    # 操作符白名单
    VALID_OPERATORS = [
        "=", "!=", "<>", "<", ">", "<=", ">=",
        "LIKE", "NOT LIKE", "IN", "NOT IN",
        "IS NULL", "IS NOT NULL"
    ]

    def build_condition(self, field: str, operator: str, value: str) -> str:
        # 验证字段名
        validated_field = SQLValidator.validate_identifier(field, "field")

        # 验证操作符（白名单）
        if operator not in self.VALID_OPERATORS:
            raise ValueError(
                f"Invalid operator: '{operator}'. "
                f"Must be one of: {', '.join(self.VALID_OPERATORS)}"
            )

        return f"{validated_field} {operator} {value}"

# 验证通过
build_condition("role_id", "=", "123")
# 输出: role_id = 123

# 验证失败
build_condition("role_id", "OR 1=1 --", "123")
# 抛出异常: ValueError: Invalid operator: 'OR 1=1 --'
```

### 模式3: 注释注入

**攻击原理**: 使用SQL注释标记绕过后续验证

**攻击示例**:
```python
# 用户输入
value = "123' --"

# ❌ 不安全代码
hql = f"WHERE role_id = '{value}' AND valid = 1"

# 生成的HQL
WHERE role_id = '123' --' AND valid = 1
```

**实际后果**:
- `AND valid = 1`条件被注释掉
- 可能绕过业务逻辑验证

**防护方法**:

```python
# ✅ 安全代码
def validate_string_value(value: str) -> str:
    """
    验证字符串值
    """
    # 检查注释标记
    if "--" in value or "/*" in value:
        raise ValueError("SQL comments detected in value")

    # 转义单引号
    escaped = value.replace("'", "''")

    return escaped

def build_condition_safe(field: str, value: str) -> str:
    validated_field = SQLValidator.validate_identifier(field, "field")
    validated_value = validate_string_value(value)

    return f"{validated_field} = '{validated_value}'"

# 验证失败
build_condition_safe("role_id", "123' --")
# 抛出异常: ValueError: SQL comments detected in value
```

### 模式4: UNION注入

**攻击原理**: 通过UNION查询注入恶意数据

**攻击示例**:
```python
# 用户输入
field_name = "role_id UNION SELECT password FROM users --"

# ❌ 不安全代码
hql = f"SELECT {field_name} FROM events"

# 生成的HQL
SELECT role_id UNION SELECT password FROM users -- FROM events
```

**实际后果**:
- 泄露其他表的敏感数据（如：密码）
- 数据泄露风险

**防护方法**:

```python
# ✅ 安全代码
def build_select_fields(field_names: list) -> str:
    # 验证所有字段名
    validated_fields = []
    for field in field_names:
        validated = SQLValidator.validate_column_name(field)
        validated_fields.append(validated)

    # 检查UNION关键字
    fields_str = " ".join(validated_fields)
    if "UNION" in fields_str.upper():
        raise ValueError("UNION keyword detected in field names")

    return f"SELECT {', '.join(validated_fields)} FROM events"

# 验证失败
build_select_fields(["role_id UNION SELECT password FROM users --"])
# 抛出异常: ValueError: Invalid column_name: 'role_id UNION SELECT password FROM users --'
```

## 如何验证用户输入

### 1. 标识符验证（表名、列名）

**验证规则**:
- 只允许字母、数字、下划线
- 不能以数字开头
- 不允许特殊字符

**实现**:

```python
from backend.core.security.sql_validator import SQLValidator

# 验证表名
def validate_table_name(table_name: str) -> str:
    return SQLValidator.validate_table_name(table_name)

# 验证列名
def validate_column_name(column_name: str) -> str:
    return SQLValidator.validate_column_name(column_name)

# 验证任意标识符
def validate_identifier(identifier: str, name: str = "identifier") -> str:
    return SQLValidator.validate_identifier(identifier, name)
```

**测试用例**:

```python
# ✅ 有效标识符
assert validate_table_name("events") == "events"
assert validate_table_name("log_events") == "log_events"
assert validate_column_name("role_id") == "role_id"
assert validate_column_name("ds") == "ds"

# ❌ 无效标识符（抛出异常）
try:
    validate_table_name("events; DROP TABLE users;")
except ValueError as e:
    print(f"捕获到注入: {e}")

try:
    validate_column_name("role_id' OR '1'='1")
except ValueError as e:
    print(f"捕获到注入: {e}")
```

### 2. 操作符验证

**验证规则**:
- 使用预定义白名单
- 大小写敏感（或统一转换为大写）

**实现**:

```python
class HQLValidator:
    # 允许的比较操作符
    COMPARISON_OPERATORS = ["=", "!=", "<>", "<", ">", "<=", ">="]

    # 允许的逻辑操作符
    LOGICAL_OPERATORS = ["AND", "OR", "NOT"]

    # 允许的匹配操作符
    MATCH_OPERATORS = ["LIKE", "NOT LIKE", "IN", "NOT IN"]

    # 允许的NULL操作符
    NULL_OPERATORS = ["IS NULL", "IS NOT NULL"]

    # 所有允许的操作符
    VALID_OPERATORS = (
        COMPARISON_OPERATORS +
        LOGICAL_OPERATORS +
        MATCH_OPERATORS +
        NULL_OPERATORS
    )

    @classmethod
    def validate_operator(cls, operator: str) -> str:
        """验证操作符"""
        op_upper = operator.upper().strip()

        if op_upper not in cls.VALID_OPERATORS:
            raise ValueError(
                f"Invalid operator: '{operator}'. "
                f"Must be one of: {', '.join(cls.VALID_OPERATORS)}"
            )

        return op_upper
```

**测试用例**:

```python
# ✅ 有效操作符
assert HQLValidator.validate_operator("=") == "="
assert HQLValidator.validate_operator("!=") == "!="
assert HQLValidator.validate_operator("LIKE") == "LIKE"
assert HQLValidator.validate_operator("IS NULL") == "IS NULL"

# ❌ 无效操作符（抛出异常）
try:
    HQLValidator.validate_operator("OR 1=1")
except ValueError as e:
    print(f"捕获到注入: {e}")

try:
    HQLValidator.validate_operator("--")
except ValueError as e:
    print(f"捕获到注入: {e}")
```

### 3. JOIN类型验证

**验证规则**:
- 只允许标准JOIN类型

**实现**:

```python
class JoinBuilder:
    VALID_JOIN_TYPES = ["INNER", "LEFT", "RIGHT", "CROSS", "FULL"]

    def validate_join_type(self, join_type: str) -> str:
        """验证JOIN类型"""
        join_upper = join_type.upper().strip()

        if join_upper not in self.VALID_JOIN_TYPES:
            raise ValueError(
                f"Invalid join type: '{join_type}'. "
                f"Must be one of: {', '.join(self.VALID_JOIN_TYPES)}"
            )

        return join_upper
```

**测试用例**:

```python
# ✅ 有效JOIN类型
assert JoinBuilder().validate_join_type("INNER") == "INNER"
assert JoinBuilder().validate_join_type("LEFT") == "LEFT"

# ❌ 无效JOIN类型（抛出异常）
try:
    JoinBuilder().validate_join_type("INNER JOIN ON 1=1; DROP TABLE users;")
except ValueError as e:
    print(f"捕获到注入: {e}")
```

### 4. 值的验证

**验证规则**:
- 字符串值：转义单引号
- 日期值：验证格式
- 数值：验证类型

**实现**:

```python
import re
from typing import Union

def validate_value(value: Union[str, int, float]) -> str:
    """
    验证并转义值
    """
    if isinstance(value, str):
        # 转义单引号
        escaped = value.replace("'", "''")

        # 检查危险模式
        if "--" in escaped or "/*" in escaped:
            raise ValueError("SQL comments detected in value")

        return f"'{escaped}'"

    elif isinstance(value, (int, float)):
        return str(value)

    elif isinstance(value, bool):
        return "TRUE" if value else "FALSE"

    else:
        raise TypeError(f"Unsupported value type: {type(value)}")

def validate_date(date_str: str, format: str = "%Y%m%d") -> str:
    """
    验证日期格式
    """
    from datetime import datetime

    try:
        # 尝试解析日期
        datetime.strptime(date_str, format)

        # 检查是否为纯数字（防止SQL注入）
        if not re.match(r'^\d+$', date_str):
            raise ValueError("Date must contain only digits")

        return date_str

    except ValueError as e:
        raise ValueError(f"Invalid date format: {date_str}. Expected: {format}")
```

**测试用例**:

```python
# ✅ 有效值
assert validate_value("hello") == "'hello'"
assert validate_value("it's") == "'it''s'"  # 单引号被转义
assert validate_value(123) == "123"
assert validate_value(True) == "TRUE"

# ❌ 无效值（抛出异常）
try:
    validate_value("value' --")
except ValueError as e:
    print(f"捕获到注入: {e}")

# ✅ 有效日期
assert validate_date("20260101") == "20260101"

# ❌ 无效日期（抛出异常）
try:
    validate_date("2026-01-01")  # 错误格式
except ValueError as e:
    print(f"捕获到无效日期: {e}")

try:
    validate_date("20260101; DROP TABLE users;")  # 包含分号
except ValueError as e:
    print(f"捕获到注入: {e}")
```

## 如何安全地构建动态HQL

### 1. 构建SELECT语句

```python
# ✅ 安全实现
def build_select_clause(fields: list, table_name: str) -> str:
    """
    构建SELECT子句

    Args:
        fields: 字段列表
        table_name: 表名

    Returns:
        SELECT子句
    """
    # 验证表名
    validated_table = SQLValidator.validate_table_name(table_name)

    # 验证所有字段
    validated_fields = []
    for field in fields:
        validated = SQLValidator.validate_column_name(field)
        validated_fields.append(validated)

    fields_clause = ", ".join(validated_fields)

    return f"SELECT {fields_clause} FROM {validated_table}"

# 使用示例
hql = build_select_clause(
    fields=["role_id", "account_id", "zone_id"],
    table_name="ieu_ods.ods_10000147_all_view"
)
# 输出: SELECT role_id, account_id, zone_id FROM ieu_ods.ods_10000147_all_view
```

### 2. 构建WHERE条件

```python
# ✅ 安全实现
class SafeWhereBuilder:
    VALID_OPERATORS = [
        "=", "!=", "<>", "<", ">", "<=", ">=",
        "LIKE", "NOT LIKE", "IN", "NOT IN",
        "IS NULL", "IS NOT NULL"
    ]

    def build_where(self, conditions: list) -> str:
        """
        构建WHERE子句

        Args:
            conditions: 条件列表
                [{"field": "role_id", "operator": ">", "value": 0}]

        Returns:
            WHERE子句
        """
        if not conditions:
            return "1=1"  # 默认条件

        where_parts = []
        for cond in conditions:
            # 验证字段名
            field = SQLValidator.validate_identifier(
                cond.get("field", ""), "field"
            )

            # 验证操作符
            operator = cond.get("operator", "=")
            if operator not in self.VALID_OPERATORS:
                raise ValueError(f"Invalid operator: {operator}")

            # 处理值
            value = cond.get("value")

            if operator in ["IS NULL", "IS NOT NULL"]:
                # NULL操作符不需要值
                part = f"{field} {operator}"
            else:
                # 验证并转义值
                validated_value = validate_value(value)
                part = f"{field} {operator} {validated_value}"

            where_parts.append(part)

        return " AND ".join(where_parts)

# 使用示例
builder = SafeWhereBuilder()
hql = builder.build_where([
    {"field": "role_id", "operator": ">", "value": 0},
    {"field": "ds", "operator": "=", "value": "20260101"}
])
# 输出: role_id > 0 AND ds = '20260101'
```

### 3. 构建JOIN语句

```python
# ✅ 安全实现
class SafeJoinBuilder:
    VALID_JOIN_TYPES = ["INNER", "LEFT", "RIGHT", "CROSS"]

    def build_join(
        self,
        left_table: str,
        right_table: str,
        join_type: str,
        join_conditions: list
    ) -> str:
        """
        构建JOIN子句

        Args:
            left_table: 左表名
            right_table: 右表名
            join_type: JOIN类型
            join_conditions: JOIN条件列表
                [{"left": "role_id", "right": "role_id"}]

        Returns:
            JOIN子句
        """
        # 验证表名
        validated_left = SQLValidator.validate_table_name(left_table)
        validated_right = SQLValidator.validate_table_name(right_table)

        # 验证JOIN类型
        join_upper = join_type.upper()
        if join_upper not in self.VALID_JOIN_TYPES:
            raise ValueError(f"Invalid join type: {join_type}")

        # 构建JOIN类型
        join_clause = f"{join_upper} JOIN {validated_right}"

        # 构建ON条件
        if join_upper != "CROSS":
            on_parts = []
            for cond in join_conditions:
                left = SQLValidator.validate_identifier(
                    cond.get("left", ""), "left_field"
                )
                right = SQLValidator.validate_identifier(
                    cond.get("right", ""), "right_field"
                )
                on_parts.append(f"{validated_left}.{left} = {validated_right}.{right}")

            on_clause = " AND ".join(on_parts)
            join_clause += f" ON {on_clause}"

        return join_clause

# 使用示例
builder = SafeJoinBuilder()
hql = builder.build_join(
    left_table="events_login",
    right_table="events_purchase",
    join_type="INNER",
    join_conditions=[{"left": "role_id", "right": "role_id"}]
)
# 输出: INNER JOIN events_purchase ON events_login.role_id = events_purchase.role_id
```

### 4. 构建UNION语句

```python
# ✅ 安全实现
class SafeUnionBuilder:
    def build_union(self, select_queries: list, union_type: str = "UNION") -> str:
        """
        构建UNION子句

        Args:
            select_queries: SELECT查询列表
            union_type: UNION类型（UNION/UNION ALL）

        Returns:
            UNION查询
        """
        # 验证UNION类型
        union_upper = union_type.upper().strip()
        if union_upper not in ["UNION", "UNION ALL"]:
            raise ValueError(f"Invalid union type: {union_type}")

        # 验证所有SELECT查询（确保不包含UNION）
        validated_queries = []
        for query in select_queries:
            # 检查查询中是否包含UNION（防止嵌套UNION注入）
            if "UNION" in query.upper():
                raise ValueError("Nested UNION detected in query")

            validated_queries.append(query)

        # 组合UNION查询
        return f" {union_upper} ".join(validated_queries)

# 使用示例
builder = SafeUnionBuilder()
hql = builder.build_union([
    "SELECT role_id FROM events_login",
    "SELECT role_id FROM events_purchase"
])
# 输出: SELECT role_id FROM events_login UNION SELECT role_id FROM events_purchase
```

## 实际案例（基于已修复的7个漏洞）

### 案例1: 字段构建器 - 危险关键字检测

**漏洞描述**: `FieldBuilder._build_custom_field()`未验证自定义表达式

**修复前**:
```python
# ❌ 不安全代码
def _build_custom_field(self, field: Field) -> str:
    if not field.custom_expression:
        raise ValueError("custom field must have custom_expression")

    # 直接使用自定义表达式（未验证）
    sql = field.custom_expression

    if field.alias:
        alias = self._escape_identifier(field.alias)
        sql = f"{sql} AS {alias}"

    return sql
```

**攻击示例**:
```python
field = Field(
    name="custom",
    type="custom",
    custom_expression="role_id; DROP TABLE users; --"
)

# 生成的HQL
SELECT role_id; DROP TABLE users; -- AS custom FROM events
```

**修复后**:
```python
# ✅ 安全代码
def _validate_custom_expression(self, expression: str) -> bool:
    """
    验证自定义表达式是否安全

    防止SQL注入
    """
    if not expression:
        return False

    # 转换为大写进行检查
    expr_upper = expression.upper()

    # 检查危险关键字
    for keyword in self.DANGEROUS_KEYWORDS:
        if keyword in expr_upper:
            raise ValueError(
                f"Dangerous SQL keyword '{keyword}' found in custom expression. "
                f"This could be a SQL injection attempt."
            )

    # 检查多个语句（分号）
    if ";" in expression:
        raise ValueError(
            "Multiple statements detected in custom expression. "
            "Only single expressions are allowed."
        )

    # 检查注释标记
    if "--" in expression or "/*" in expression:
        raise ValueError(
            "SQL comments detected in custom expression. "
            "Comments are not allowed."
        )

    return True

def _build_custom_field(self, field: Field) -> str:
    if not field.custom_expression:
        raise ValueError("custom field must have custom_expression")

    # ✅ 验证自定义表达式
    self._validate_custom_expression(field.custom_expression)

    sql = field.custom_expression

    if field.alias:
        alias = self._escape_identifier(field.alias)
        sql = f"{sql} AS {alias}"

    return sql
```

**验证**:
```python
# ✅ 有效表达式
field = Field(
    name="custom",
    type="custom",
    custom_expression="COUNT(DISTINCT role_id)"
)
# 通过验证

# ❌ 恶意表达式
field = Field(
    name="custom",
    type="custom",
    custom_expression="role_id; DROP TABLE users; --"
)
# 抛出异常: ValueError: Dangerous SQL keyword 'DROP' found
```

### 案例2: JOIN构建器 - 操作符白名单

**漏洞描述**: `JoinBuilder.build_join_with_where()`未验证WHERE条件的操作符

**修复前**:
```python
# ❌ 不安全代码
def build_join_with_where(self, events, join_conditions, where_conditions, ...):
    # 构建WHERE条件
    where_parts = []
    for cond in where_conditions:
        field = cond["field"]
        operator = cond["operator"]
        value = cond.get("value", "")

        # 未验证操作符，直接拼接
        where_parts.append(f"{field} {operator} {value}")

    where_clause = " AND ".join(where_parts)
    return f"SELECT *\n{join_sql}\nWHERE {where_clause}"
```

**攻击示例**:
```python
where_conditions = [
    {
        "field": "role_id",
        "operator": "OR 1=1 --",
        "value": "123"
    }
]

# 生成的HQL
WHERE role_id OR 1=1 -- '123'
```

**修复后**:
```python
# ✅ 安全代码
class JoinBuilder:
    VALID_OPERATORS = ["=", "!=", "<>", "<", ">", "<=", ">=", "LIKE", "NOT LIKE", "IN", "NOT IN", "IS NULL", "IS NOT NULL"]

    def _validate_where_condition(self, cond: Dict[str, Any]) -> None:
        """
        验证WHERE条件的安全性

        Args:
            cond: WHERE条件字典

        Raises:
            ValueError: 如果条件不安全
        """
        if "field" not in cond:
            raise ValueError("WHERE condition must have 'field'")

        # 验证字段名（SQL标识符）
        field = cond["field"]
        SQLValidator.validate_identifier(field, "field")

        # ✅ 验证操作符
        operator = cond.get("operator", "=")
        if operator not in self.VALID_OPERATORS:
            raise ValueError(
                f"Invalid operator: '{operator}'. "
                f"Must be one of: {', '.join(self.VALID_OPERATORS)}"
            )

    def build_join_with_where(self, events, join_conditions, where_conditions, ...):
        # 构建WHERE条件（带安全验证）
        where_parts = []
        for cond in where_conditions:
            # ✅ 验证条件安全性
            self._validate_where_condition(cond)

            field = cond["field"]
            operator = cond["operator"]
            value = cond.get("value", "")

            where_parts.append(f"{field} {operator} {value}")

        where_clause = " AND ".join(where_parts)
        return f"SELECT *\n{join_sql}\nWHERE {where_clause}"
```

**验证**:
```python
# ✅ 有效条件
where_conditions = [
    {"field": "role_id", "operator": ">", "value": 0}
]
# 通过验证

# ❌ 恶意条件
where_conditions = [
    {"field": "role_id", "operator": "OR 1=1 --", "value": "123"}
]
# 抛出异常: ValueError: Invalid operator: 'OR 1=1 --'
```

### 案例3: 标识符验证 - 使用SQLValidator

**漏洞描述**: 动态表名、字段名未验证

**修复前**:
```python
# ❌ 不安全代码
def generate_hql(table_name: str, fields: list) -> str:
    # 直接使用用户输入
    fields_clause = ", ".join(fields)

    return f"SELECT {fields_clause} FROM {table_name}"

# 攻击
generate_hql(
    table_name="events; DROP TABLE users; --",
    fields=["role_id", "account_id"]
)
```

**修复后**:
```python
# ✅ 安全代码
from backend.core.security.sql_validator import SQLValidator

def generate_hql(table_name: str, fields: list) -> str:
    # 验证表名
    validated_table = SQLValidator.validate_table_name(table_name)

    # 验证所有字段
    validated_fields = []
    for field in fields:
        validated = SQLValidator.validate_column_name(field)
        validated_fields.append(validated)

    fields_clause = ", ".join(validated_fields)

    return f"SELECT {fields_clause} FROM {validated_table}"

# 验证通过
generate_hql(
    table_name="events_login",
    fields=["role_id", "account_id"]
)
# 输出: SELECT role_id, account_id FROM events_login

# 验证失败
generate_hql(
    table_name="events; DROP TABLE users; --",
    fields=["role_id"]
)
# 抛出异常: ValueError: Invalid table_name: 'events; DROP TABLE users; --'
```

## 相关文档

- **[HQL安全开发指南](./hql-security-guide.md)** - HQL安全开发规范
- **[SQLValidator使用指南](../development/sql-validator-guidelines.md)** - SQL验证器文档
- **[安全要点](../lessons-learned/security-essentials.md)** - 项目安全最佳实践

## 总结

### 关键要点

1. **永远不要信任用户输入**
   - 所有输入必须验证
   - 使用白名单而非黑名单

2. **使用SQLValidator**
   - 表名、列名必须验证
   - 操作符必须使用白名单

3. **检测危险关键字**
   - DROP、DELETE、TRUNCATE等
   - 注释标记（--、/* */）
   - 多语句（;）

4. **转义特殊字符**
   - 单引号（' → ''）
   - 反引号（` → ``）

5. **异常处理**
   - 验证失败时抛出ValueError
   - API层捕获并返回400错误

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 1.0 | 2026-03-04 | 初始版本 |
