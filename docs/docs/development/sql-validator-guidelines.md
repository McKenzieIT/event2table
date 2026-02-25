# SQLValidator使用指南

## 概述

SQLValidator是Event2Table的安全组件，用于防止SQL注入攻击。所有动态SQL标识符（表名、列名、字段名）必须使用SQLValidator进行验证。

## 强制使用场景

| 场景 | 验证方法 | 说明 |
|------|----------|------|
| 动态表名 | `validate_table_name()` | 必须验证 |
| 动态列名 | `validate_column_name()` | 必须验证 |
| 动态字段名（UPDATE/INSERT） | `validate_field_whitelist()` | 推荐使用白名单 |
| ORDER BY子句 | `validate_order_by()` | 必须验证 |
| PRAGMA键 | `validate_pragma_key()` | 必须验证白名单 |

## API参考

### 基础验证方法

```python
from backend.core.security.sql_validator import SQLValidator

# 验证表名
SQLValidator.validate_table_name("games")  # 通过
SQLValidator.validate_table_name("users; DROP TABLE")  # 抛出ValueError

# 验证列名
SQLValidator.validate_column_name("name")  # 通过
SQLValidator.validate_column_name("name; SELECT")  # 抛出ValueError
```

### 白名单验证

```python
# 验证字段是否在白名单中
ALLOWED_FIELDS = {"id", "name", "created_at", "updated_at"}

SQLValidator.validate_field_whitelist("name", ALLOWED_FIELDS)  # 通过
SQLValidator.validate_field_whitelist("dangerous", ALLOWED_FIELDS)  # 抛出ValueError
```

### ORDER BY验证

```python
ALLOWED_SORT_FIELDS = {"name", "created_at", "id"}

# 仅字段名
SQLValidator.sanitize_order_by("name", ALLOWED_SORT_FIELDS)  # 返回 "name"

# 字段名 + 方向
SQLValidator.sanitize_order_by("created_at DESC", ALLOWED_SORT_FIELDS)  # 返回 "created_at DESC"
```

### PRAGMA验证

```python
# 验证PRAGMA键是否在白名单中
SQLValidator.validate_pragma_key("user_version")  # 通过
SQLValidator.validate_pragma_key("dangerous_pragma")  # 抛出ValueError
```

## 禁止模式

### ❌ 禁止：直接拼接用户输入

```python
# 危险！
table_name = request.args.get("table")
query = f"SELECT * FROM {table_name} WHERE id = ?"
```

### ✅ 必须：使用SQLValidator

```python
# 安全
from backend.core.security.sql_validator import SQLValidator

table_name = request.args.get("table")
validated_table = SQLValidator.validate_table_name(table_name)
query = f"SELECT * FROM {validated_table} WHERE id = ?"
```

## 实际使用示例

### 在Repository中使用

```python
from backend.core.security.sql_validator import SQLValidator
from backend.core.database.converters import fetch_all_as_dict

class EventRepository:
    def get_events_by_table(self, table_name: str):
        # 验证表名
        validated_table = SQLValidator.validate_table_name(table_name)
        
        # 安全查询
        return fetch_all_as_dict(f"SELECT * FROM {validated_table}")
```

### 在Service中使用

```python
from backend.core.security.sql_validator import SQLValidator

class GameService:
    def get_sorted_games(self, sort_by: str, direction: str = "ASC"):
        ALLOWED_SORT_FIELDS = {"name", "gid", "created_at"}
        
        # 验证排序字段
        sort_clause = SQLValidator.sanitize_order_by(
            f"{sort_by} {direction}", 
            ALLOWED_SORT_FIELDS
        )
        
        # 使用验证后的排序子句
        return fetch_all_as_dict(f"SELECT * FROM games ORDER BY {sort_clause}")
```

## 异常处理

SQLValidator在验证失败时抛出`ValueError`。建议在API层统一处理：

```python
from backend.core.security.sql_validator import SQLValidator
from backend.core.utils import json_error_response

@api_bp.route("/api/data", methods=["GET"])
def get_data():
    try:
        table_name = request.args.get("table")
        validated = SQLValidator.validate_table_name(table_name)
        # ...
    except ValueError as e:
        return json_error_response(str(e), status_code=400)
```

## 代码审查检查清单

- [ ] 所有动态表名使用`validate_table_name()`验证
- [ ] 所有动态列名使用`validate_column_name()`验证
- [ ] ORDER BY子句使用`sanitize_order_by()`验证
- [ ] 用户输入没有直接拼接到SQL中
- [ ] 异常处理正确返回400状态码

## 相关文件

- 验证器实现：`backend/core/security/sql_validator.py`
- 使用示例：`backend/services/ddl_generator.py`
- 使用示例：`backend/services/hql/builders/field_builder.py`
