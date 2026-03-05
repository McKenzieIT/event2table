# HQL安全开发指南

## 概述

本文档提供HQL（HiveQL）生成器的安全开发指南。HQL用于构建Hadoop/Hive数据仓库的查询字符串，与应用SQLite查询有本质区别。

**⚠️ 重要提示**: HQL生成器用于构建**Hive查询字符串**，而非直接执行SQL。安全重点在于防止用户输入破坏HQL语法结构。

## HQL vs SQL的区别

| 特性 | SQLite SQL | Hive HQL |
|------|------------|----------|
| **执行方式** | 直接在数据库执行 | 生成查询字符串，供调度系统使用 |
| **参数化** | 支持`?`占位符 | 使用`${variable}`占位符 |
| **注入风险** | 数据注入 | 语法破坏、恶意代码注入 |
| **验证重点** | 值的验证 | 标识符和表达式的验证 |
| **典型场景** | 实时查询 | ETL任务、数据仓库 |

### HQL特殊场景

```sql
-- ✅ HQL允许的占位符（调度系统替换）
WHERE ds = '${bizdate}'
WHERE ds BETWEEN '${start_date}' AND '${end_date}'

-- ✅ HQL使用的函数
get_json_object(params, '$.zone_id')

-- ❌ 不支持的参数化（Hive不支持）
WHERE ds = ?  -- Hive不支持
```

## HQL注入风险说明

### 风险1: 标识符注入

**攻击示例**:
```python
# ❌ 危险：用户输入直接拼接到表名
table_name = "ieu_ods.ods_10000147_all_view; DROP TABLE users;"
hql = f"SELECT * FROM {table_name}"

# 结果：生成的HQL包含恶意语句
# SELECT * FROM ieu_ods.ods_10000147_all_view; DROP TABLE users;
```

**防护**: 使用`SQLValidator.validate_table_name()`

### 风险2: 操作符注入

**攻击示例**:
```python
# ❌ 危险：用户输入操作符
operator = "OR 1=1 --"
hql = f"WHERE role_id {operator} '{value}'"

# 结果：始终为真的条件
# WHERE role_id OR 1=1 -- '{value}'
```

**防护**: 使用操作符白名单

### 风险3: 自定义表达式注入

**攻击示例**:
```python
# ❌ 危险：自定义表达式包含危险关键字
custom_expr = "role_id; DELETE FROM users WHERE 1=1"
hql = f"SELECT {custom_expr} AS role_id"

# 结果：多语句注入
# SELECT role_id; DELETE FROM users WHERE 1=1 AS role_id
```

**防护**: 使用`FieldBuilder._validate_custom_expression()`

### 风险4: 注释注入

**攻击示例**:
```python
# ❌ 危险：注释标记导致SQL后续部分被忽略
field_name = "role_id' --"
hql = f"WHERE {field_name} = '{value}'"

# 结果：条件被绕过
# WHERE role_id' -- = '{value}'
```

**防护**: 禁止注释标记`--`和`/* */`

## 安全的HQL生成模式

### 模式1: 使用SQLValidator验证标识符

```python
from backend.core.security.sql_validator import SQLValidator

# ✅ 正确：验证HQL表名（包含数据库前缀）
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

user_table = request.args.get("table")
validated_table = validate_hql_table_name(user_table)
hql = f"SELECT * FROM {validated_table}"

# ✅ 正确：验证字段名
user_field = request.args.get("field")
validated_field = SQLValidator.validate_identifier(user_field, "field")
hql = f"SELECT {validated_field} FROM events"

# ✅ 正确：项目适配器（推荐）
# 在Event2Table项目中，表名由ProjectAdapter构建
# table_name = f"{game.ods_db}.ods_{game.gid}_all_view"
# game数据来自数据库查询（非用户输入），因此安全
```

**验证规则**:
- 只允许字母、数字、下划线
- 不能以数字开头
- 不允许特殊字符（包括`;`, `'`, `"`, `--`等）

### 模式2: 操作符白名单

```python
# ✅ 正确：使用白名单验证操作符
VALID_OPERATORS = ["=", "!=", "<>", "<", ">", "<=", ">=", "LIKE", "NOT LIKE", "IN", "NOT IN"]

def build_condition(field: str, operator: str, value: str) -> str:
    # 验证操作符
    if operator not in VALID_OPERATORS:
        raise ValueError(f"Invalid operator: {operator}")

    # 验证字段名
    validated_field = SQLValidator.validate_identifier(field, "field")

    return f"{validated_field} {operator} {value}"
```

### 模式3: 危险关键字检测

```python
# ✅ 正确：检测危险关键字
DANGEROUS_KEYWORDS = [
    "DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE",
    "INSERT", "UPDATE", "EXEC", "EXECUTE", "SCRIPT",
    "--", "/*", "*/", ";", "xp_", "sp_"
]

def validate_custom_expression(expression: str) -> bool:
    expr_upper = expression.upper()

    for keyword in DANGEROUS_KEYWORDS:
        if keyword in expr_upper:
            raise ValueError(f"Dangerous keyword '{keyword}' found")

    # 检查多语句
    if ";" in expression:
        raise ValueError("Multiple statements detected")

    # 检查注释
    if "--" in expression or "/*" in expression:
        raise ValueError("SQL comments detected")

    return True
```

### 模式4: 占位符安全使用

```python
# ✅ 正确：使用Hive占位符
def build_partition_filter(bizdate: str) -> str:
    """
    构建分区过滤条件

    Args:
        bizdate: 业务日期（格式：YYYYMMDD）
    """
    # 验证日期格式
    if not re.match(r'^\d{8}$', bizdate):
        raise ValueError(f"Invalid bizdate format: {bizdate}")

    # 使用Hive占位符
    return f"ds = '${bizdate}'"

# ✅ 正确：在HQL模板中使用
hql_template = """
SELECT
    role_id,
    zone_id
FROM {table}
WHERE ds = '${bizdate}'
AND role_id > 0
"""

# 安全替换（table已通过SQLValidator验证）
table = SQLValidator.validate_table_name(user_input)
hql = hql_template.format(table=table, bizdate="20260101")
```

**⚠️ 禁止**: 将用户输入直接作为占位符值

```python
# ❌ 危险：用户输入直接作为占位符
user_value = "20260101' OR '1'='1"
hql = f"WHERE ds = '${user_value}'"

# 结果：ds = '20260101' OR '1'='1'
```

## SQLValidator的使用方法

### 导入

```python
from backend.core.security.sql_validator import SQLValidator
```

### 验证表名

**⚠️ 注意**: HQL表名通常包含数据库前缀（如：`ieu_ods.ods_10000147_all_view`），需要特殊处理。

```python
# ✅ 方式1: 分离验证（推荐）
def validate_hql_table_name(table_name: str) -> str:
    """
    验证HQL表名（包含数据库前缀）

    格式：database.table
    例如：ieu_ods.ods_10000147_all_view
    """
    if '.' not in table_name:
        raise ValueError(f"HQL table name must contain database prefix: {table_name}")

    # 分离数据库名和表名
    parts = table_name.split('.')
    if len(parts) != 2:
        raise ValueError(f"Invalid HQL table name format: {table_name}")

    database, table = parts

    # 分别验证数据库名和表名
    validated_db = SQLValidator.validate_identifier(database, "database")
    validated_table = SQLValidator.validate_identifier(table, "table")

    return f"{validated_db}.{validated_table}"

# 测试
validate_hql_table_name("ieu_ods.ods_10000147_all_view")  # ✅ 通过
validate_hql_table_name("table; DROP TABLE users")  # ❌ 失败

# ✅ 方式2: 项目适配器（实际使用）
# 在Event2Table项目中，表名通过ProjectAdapter从数据库查询构建
# 表名格式：f"{game.ods_db}.ods_{game.gid}_all_view"
# ods_db来自games表（数据库查询），不是用户输入
# 因此无需额外验证（已在数据库查询时验证）
```

### 验证字段名

```python
# ✅ 验证通过
validated = SQLValidator.validate_column_name("role_id")

# ❌ 验证失败（包含特殊字符）
validated = SQLValidator.validate_column_name("role_id' OR '1'='1")
# ValueError: Invalid column_name: 'role_id' OR '1'='1'
```

### 白名单验证

```python
ALLOWED_FIELDS = {"role_id", "account_id", "zone_id", "ds"}

# ✅ 验证通过
validated = SQLValidator.validate_field_whitelist("role_id", ALLOWED_FIELDS)

# ❌ 验证失败（字段不在白名单）
validated = SQLValidator.validate_field_whitelist("dangerous_field", ALLOWED_FIELDS)
# ValueError: Field 'dangerous_field' is not allowed.
#            Allowed fields: account_id, role_id, zone_id, ds
```

### ORDER BY验证

```python
ALLOWED_SORT_FIELDS = {"name", "created_at", "gid"}

# ✅ 验证通过
validated = SQLValidator.sanitize_order_by("name DESC", ALLOWED_SORT_FIELDS)

# ❌ 验证失败（方向无效）
validated = SQLValidator.sanitize_order_by("name INVALID", ALLOWED_SORT_FIELDS)
# ValueError: Invalid sort direction: INVALID. Must be ASC or DESC
```

## 操作符白名单的重要性

### HQL支持的操作符

```python
# ✅ 允许的比较操作符
COMPARISON_OPERATORS = ["=", "!=", "<>", "<", ">", "<=", ">="]

# ✅ 允许的逻辑操作符
LOGICAL_OPERATORS = ["AND", "OR"]

# ✅ 允许的匹配操作符
MATCH_OPERATORS = ["LIKE", "NOT LIKE", "IN", "NOT IN"]

# ✅ 允许的NULL操作符
NULL_OPERATORS = ["IS NULL", "IS NOT NULL"]
```

### 白名单验证示例

```python
class JoinBuilder:
    VALID_OPERATORS = [
        "=", "!=", "<>", "<", ">", "<=", ">=",
        "LIKE", "NOT LIKE", "IN", "NOT IN",
        "IS NULL", "IS NOT NULL"
    ]

    def _validate_operator(self, operator: str) -> None:
        """验证操作符是否在白名单中"""
        if operator not in self.VALID_OPERATORS:
            raise ValueError(
                f"Invalid operator: '{operator}'. "
                f"Must be one of: {', '.join(self.VALID_OPERATORS)}"
            )
```

### 为什么需要白名单？

**黑名单的问题**:
```python
# ❌ 使用黑名单（不推荐）
DANGEROUS_OPERATORS = ["OR", "AND", "--"]

if user_operator in DANGEROUS_OPERATORS:
    raise ValueError("Dangerous operator")

# 问题：攻击者可以使用未列入黑名单的操作符
# 例如：'||'（字符串拼接）可能绕过黑名单
```

**白名单的优势**:
```python
# ✅ 使用白名单（推荐）
ALLOWED_OPERATORS = ["=", "!=", "<", ">", "<=", ">="]

if user_operator not in ALLOWED_OPERATORS:
    raise ValueError("Invalid operator")

# 优势：只允许已知的、安全的操作符
```

## 占位符使用规范

### Hive占位符语法

```sql
-- ✅ 正确：使用${}占位符
WHERE ds = '${bizdate}'
WHERE ds BETWEEN '${start_date}' AND '${end_date}'

-- ✅ 正确：在表名中使用（需要验证）
INSERT OVERWRITE TABLE ${target_table} SELECT ...
```

### 占位符验证流程

```python
def validate_placeholder_value(key: str, value: str) -> str:
    """
    验证占位符的值

    Args:
        key: 占位符键名（如：bizdate）
        value: 占位符值

    Returns:
        验证后的值
    """
    # 验证键名
    validated_key = SQLValidator.validate_identifier(key, "placeholder_key")

    # 根据键名验证值的格式
    if validated_key == "bizdate":
        # 日期格式：YYYYMMDD
        if not re.match(r'^\d{8}$', value):
            raise ValueError(f"Invalid bizdate format: {value}")

    elif validated_key in ["start_date", "end_date"]:
        # 日期格式：YYYYMMDD
        if not re.match(r'^\d{8}$', value):
            raise ValueError(f"Invalid date format: {value}")

    return value
```

### HQL模板生成示例

```python
class HQLTemplateGenerator:
    """安全的HQL模板生成器"""

    # HQL模板（使用占位符）
    TEMPLATE = """
CREATE OR REPLACE VIEW {view_name} AS
SELECT
    {fields}
FROM {source_table}
WHERE ds = '${bizdate}'
{extra_conditions}
"""

    def generate(self, view_name: str, source_table: str, fields: list, bizdate: str) -> str:
        """
        生成HQL

        Args:
            view_name: 视图名称（需验证）
            source_table: 源表名（需验证）
            fields: 字段列表（需验证）
            bizdate: 业务日期（需验证）
        """
        # 验证标识符
        validated_view = SQLValidator.validate_table_name(view_name)
        validated_table = SQLValidator.validate_table_name(source_table)

        # 验证字段
        validated_fields = []
        for field in fields:
            validated_fields.append(SQLValidator.validate_column_name(field))

        # 验证日期
        if not re.match(r'^\d{8}$', bizdate):
            raise ValueError(f"Invalid bizdate: {bizdate}")

        # 替换占位符
        fields_clause = ",\n    ".join(validated_fields)
        hql = self.TEMPLATE.format(
            view_name=validated_view,
            source_table=validated_table,
            fields=fields_clause,
            bizdate=bizdate,
            extra_conditions=""
        )

        return hql
```

## 代码示例（安全vs不安全）

### 示例1: 构建字段列表

```python
# ❌ 不安全：直接拼接用户输入
def build_fields_unsafe(user_fields: list) -> str:
    fields_clause = ", ".join(user_fields)
    return f"SELECT {fields_clause} FROM events"

# 攻击：user_fields = ["role_id", "account_id; DROP TABLE users"]
# 结果：SELECT role_id, account_id; DROP TABLE users FROM events


# ✅ 安全：验证每个字段
def build_fields_safe(user_fields: list) -> str:
    validated_fields = []
    for field in user_fields:
        validated = SQLValidator.validate_column_name(field)
        validated_fields.append(validated)

    fields_clause = ", ".join(validated_fields)
    return f"SELECT {fields_clause} FROM events"

# 验证通过：user_fields = ["role_id", "account_id"]
# 结果：SELECT role_id, account_id FROM events

# 验证失败：user_fields = ["role_id", "account_id; DROP TABLE users"]
# 结果：ValueError: Invalid column_name: 'account_id; DROP TABLE users'
```

### 示例2: 构建WHERE条件

```python
# ❌ 不安全：直接拼接操作符
def build_condition_unsafe(field: str, operator: str, value: str) -> str:
    return f"{field} {operator} '{value}'"

# 攻击：operator = "OR '1'='1"
# 结果：role_id OR '1'='1' 'value'


# ✅ 安全：验证操作符和字段
def build_condition_safe(field: str, operator: str, value: str) -> str:
    # 验证字段名
    validated_field = SQLValidator.validate_identifier(field, "field")

    # 验证操作符
    ALLOWED_OPERATORS = ["=", "!=", "<", ">", "<=", ">=", "LIKE"]
    if operator not in ALLOWED_OPERATORS:
        raise ValueError(f"Invalid operator: {operator}")

    # 转义值中的单引号
    escaped_value = value.replace("'", "''")

    return f"{validated_field} {operator} '{escaped_value}'"
```

### 示例3: 构建JOIN条件

```python
# ❌ 不安全：未验证JOIN类型
def build_join_unsafe(left_table: str, right_table: str, join_type: str) -> str:
    return f"SELECT * FROM {left_table} {join_type} JOIN {right_table}"

# 攻击：join_type = "INNER JOIN ON 1=1; DROP TABLE users; --"
# 结果：SELECT * FROM table1 INNER JOIN ON 1=1; DROP TABLE users; -- table2


# ✅ 安全：验证所有标识符和JOIN类型
def build_join_safe(left_table: str, right_table: str, join_type: str) -> str:
    # 验证表名
    validated_left = SQLValidator.validate_table_name(left_table)
    validated_right = SQLValidator.validate_table_name(right_table)

    # 验证JOIN类型
    ALLOWED_JOIN_TYPES = ["INNER", "LEFT", "RIGHT", "CROSS"]
    if join_type not in ALLOWED_JOIN_TYPES:
        raise ValueError(f"Invalid join type: {join_type}")

    return f"SELECT * FROM {validated_left} {join_type} JOIN {validated_right}"
```

### 示例4: 自定义表达式

```python
# ❌ 不安全：直接使用自定义表达式
def add_custom_field_unsafe(expression: str) -> str:
    return f"SELECT {expression} AS custom_field FROM events"

# 攻击：expression = "role_id; DELETE FROM users WHERE 1=1"
# 结果：SELECT role_id; DELETE FROM users WHERE 1=1 AS custom_field FROM events


# ✅ 安全：验证自定义表达式
def add_custom_field_safe(expression: str) -> str:
    # 检查危险关键字
    DANGEROUS_KEYWORDS = ["DROP", "DELETE", "TRUNCATE", "--", ";"]

    expr_upper = expression.upper()
    for keyword in DANGEROUS_KEYWORDS:
        if keyword in expr_upper:
            raise ValueError(f"Dangerous keyword '{keyword}' found")

    # 检查多语句
    if ";" in expression:
        raise ValueError("Multiple statements detected")

    # 检查注释
    if "--" in expression or "/*" in expression:
        raise ValueError("SQL comments detected")

    return f"SELECT {expression} AS custom_field FROM events"
```

## Do's and Don'ts清单

### ✅ Do's（推荐做法）

- [x] 使用`SQLValidator.validate_table_name()`验证表名
- [x] 使用`SQLValidator.validate_column_name()`验证列名
- [x] 使用操作符白名单（`VALID_OPERATORS`）
- [x] 检查自定义表达式中的危险关键字
- [x] 验证占位符值的格式（如：日期格式）
- [x] 转义用户输入中的特殊字符（如：单引号）
- [x] 使用反引号转义标识符（``` `identifier` ```）
- [x] 在API层捕获`ValueError`并返回400错误

### ❌ Don'ts（禁止做法）

- [x] 不要直接拼接用户输入到HQL
- [x] 不要使用黑名单过滤操作符
- [x] 不要允许自定义表达式包含`;`、`--`、`/* */`
- [x] 不要将用户输入直接作为占位符值
- [x] 不要在HQL中使用多个语句（`;`分隔）
- [x] 不要忽略验证失败异常
- [x] 不要在日志中输出未验证的用户输入
- [x] 不要使用Hive不支持的参数化（`?`占位符）

## 相关文档

- **[SQLValidator使用指南](../development/sql-validator-guidelines.md)** - SQL验证器详细文档
- **[HQL注入防护示例](./hql-injection-prevention.md)** - 实际漏洞案例
- **[HQL生成器架构](../development/architecture.md)** - HQL生成器设计

## 代码审查检查清单

在代码审查HQL生成器相关代码时，必须检查：

- [ ] 所有动态表名使用`validate_table_name()`验证
- [ ] 所有动态列名使用`validate_column_name()`验证
- [ ] 操作符使用白名单验证
- [ ] 自定义表达式通过危险关键字检测
- [ ] 占位符值经过格式验证
- [ ] 异常处理正确返回400错误
- [ ] 没有直接拼接用户输入到HQL

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 1.0 | 2026-03-04 | 初始版本 |
