# HQL生成器文档

## 概述

Event2Table的HQL生成器用于构建Hadoop/Hive数据仓库的查询字符串。本目录包含HQL生成器的架构文档、安全指南和使用示例。

## 文档索引

### 安全文档

- **[HQL安全开发指南](./hql-security-guide.md)** ⭐ 必读
  - HQL vs SQL的区别
  - HQL注入风险说明
  - 安全的HQL生成模式
  - SQLValidator的使用方法
  - 操作符白名单的重要性
  - 占位符使用规范
  - 代码示例（安全vs不安全）
  - Do's and Don'ts清单

- **[HQL注入防护示例](./hql-injection-prevention.md)** ⭐ 必读
  - 常见的HQL注入模式
  - 如何验证用户输入
  - 如何安全地构建动态HQL
  - 实际案例（基于已修复的7个漏洞）

### 架构文档

- **[HQL生成器架构](../development/architecture.md#hql-v2架构设计)**
  - 模块化设计
  - Builder模式
  - 数据模型

## 快速开始

### 1. 理解HQL vs SQL

HQL（HiveQL）用于构建Hive查询字符串，与应用SQLite查询有本质区别：

```sql
-- ✅ HQL允许的占位符（调度系统替换）
WHERE ds = '${bizdate}'

-- ❌ HIVE不支持参数化（Hive不支持）
WHERE ds = ?
```

**关键区别**:
- SQLite SQL: 直接在数据库执行
- Hive HQL: 生成查询字符串，供调度系统使用

### 2. 使用SQLValidator验证

```python
from backend.core.security.sql_validator import SQLValidator

# 验证表名
validated_table = SQLValidator.validate_table_name("ieu_ods.ods_10000147_all_view")

# 验证列名
validated_column = SQLValidator.validate_column_name("role_id")

# 白名单验证
ALLOWED_FIELDS = {"role_id", "account_id", "zone_id"}
validated = SQLValidator.validate_field_whitelist("role_id", ALLOWED_FIELDS)
```

### 3. 使用操作符白名单

```python
# ✅ 正确：使用白名单
VALID_OPERATORS = ["=", "!=", "<", ">", "<=", ">=", "LIKE"]

if operator not in VALID_OPERATORS:
    raise ValueError(f"Invalid operator: {operator}")
```

### 4. 检测危险关键字

```python
DANGEROUS_KEYWORDS = ["DROP", "DELETE", "TRUNCATE", "--", ";"]

expr_upper = expression.upper()
for keyword in DANGEROUS_KEYWORDS:
    if keyword in expr_upper:
        raise ValueError(f"Dangerous keyword '{keyword}' found")
```

## 核心原则

### 1. 永远不要信任用户输入

所有用户输入必须验证：
- 表名、列名：使用`SQLValidator`
- 操作符：使用白名单
- 自定义表达式：检测危险关键字

### 2. 使用白名单而非黑名单

```python
# ❌ 黑名单（容易被绕过）
DANGEROUS_OPERATORS = ["OR", "AND", "--"]

# ✅ 白名单（安全）
ALLOWED_OPERATORS = ["=", "!=", "<", ">", "<=", ">="]
```

### 3. 检测多语句注入

```python
# ❌ 危险：允许分号
expression = "role_id; DROP TABLE users"

# ✅ 安全：检测分号
if ";" in expression:
    raise ValueError("Multiple statements detected")
```

### 4. 验证占位符值

```python
# ❌ 危险：用户输入直接作为占位符
user_value = "20260101' OR '1'='1"
hql = f"WHERE ds = '${user_value}'"

# ✅ 安全：验证占位符值格式
if not re.match(r'^\d{8}$', bizdate):
    raise ValueError(f"Invalid bizdate format: {bizdate}")
```

## 常见陷阱

### 陷阱1: 混淆SQL和HQL

**错误**: 使用Hive不支持的参数化（`?`占位符）

```python
# ❌ 错误：Hive不支持?
hql = "WHERE ds = ?"

# ✅ 正确：使用Hive占位符
hql = "WHERE ds = '${bizdate}'"
```

### 陷阱2: 忘记验证动态标识符

**错误**: 动态表名、列名未验证

```python
# ❌ 错误：未验证
hql = f"SELECT * FROM {user_table}"

# ✅ 正确：验证表名
validated_table = SQLValidator.validate_table_name(user_table)
hql = f"SELECT * FROM {validated_table}"
```

### 陷阱3: 使用黑名单过滤操作符

**错误**: 黑名单容易被绕过

```python
# ❌ 错误：黑名单
if operator in ["OR", "AND"]:
    raise ValueError("Dangerous operator")

# ✅ 正确：白名单
if operator not in ["=", "!=", "<", ">"]:
    raise ValueError("Invalid operator")
```

## 安全检查清单

在代码审查HQL生成器相关代码时，必须检查：

- [ ] 所有动态表名使用`validate_table_name()`验证
- [ ] 所有动态列名使用`validate_column_name()`验证
- [ ] 操作符使用白名单验证
- [ ] 自定义表达式通过危险关键字检测
- [ ] 占位符值经过格式验证
- [ ] 异常处理正确返回400错误
- [ ] 没有直接拼接用户输入到HQL

## 相关文档

- **[SQLValidator使用指南](../development/sql-validator-guidelines.md)** - SQL验证器详细文档
- **[安全要点](../lessons-learned/security-essentials.md)** - 项目安全最佳实践
- **[API设计模式](../lessons-learned/api-design-patterns.md)** - API层安全设计

## 贡献指南

如果你发现HQL生成器的安全问题，或者有改进建议：

1. **安全问题**: 立即报告给维护者
2. **文档改进**: 提交Pull Request
3. **代码改进**: 遵循TDD开发模式

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 1.0 | 2026-03-04 | 初始版本：创建HQL安全文档 |
