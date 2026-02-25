# 安全要点

> **来源**: 整合了3个文档的安全相关经验
> **最后更新**: 2026-02-24
> **维护**: 每次安全问题修复后立即更新

---

## SQL注入防护 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 3次 | **来源**: [OPTIMIZATION_LESSONS_LEARNED.md](../archive/2026-02/optimization-reports/OPTIMIZATION_LESSONS_LEARNED.md), [FINAL_OPTIMIZATION_REPORT.md](../archive/2026-02/optimization-reports/FINAL_OPTIMIZATION_REPORT.md), [sql-validator-guidelines.md](../development/sql-validator-guidelines.md)

### 问题现象

**症状描述**:
- 攻击者可以通过输入字段操纵数据库查询
- 可能导致数据泄露、数据篡改、数据库被删除

**影响范围**:
- 所有使用动态SQL的API
- 所有接受用户输入的查询

### 根本原因

**技术原因**:
1. **字符串拼接SQL查询** - 直接将用户输入拼接到SQL语句中
2. **未验证的动态标识符** - 表名、列名等SQL标识符未经验证
3. **缺少参数化查询** - 没有使用占位符和参数绑定

**错误示例**:
```python
# ❌ 错误：字符串拼接SQL查询
query = f"SELECT * FROM games WHERE name = '{name}'"
# 攻击输入：name = "'; DROP TABLE games; --"
# 结果：SELECT * FROM games WHERE name = ''; DROP TABLE games; --'
```

### 解决方案

**1. 参数化查询（必须使用）**:
```python
# ✅ 正确：使用参数化查询
from backend.core.database.converters import fetch_one_as_dict

game = fetch_one_as_dict(
    "SELECT * FROM games WHERE name = ?",
    (name,)
)
```

**2. SQLValidator强制使用**:
```python
from backend.core.security.sql_validator import SQLValidator

# ✅ 正确：验证动态表名
table_name = request.args.get("table")
validated_table = SQLValidator.validate_table_name(table_name)
query = f"SELECT * FROM {validated_table}"

# ✅ 正确：验证动态列名
column = request.args.get("column")
validated_column = SQLValidator.validate_column_name(column)

# ✅ 正确：使用白名单验证
ALLOWED_FIELDS = {"name", "created_at", "id"}
SQLValidator.validate_field_whitelist(sort_by, ALLOWED_FIELDS)
```

**3. Pydantic Schema验证**:
```python
from backend.models.schemas import GameCreate

# ✅ Pydantic自动进行输入验证
game_data = GameCreate(**request.json)
```

### 预防措施

**代码审查清单**:
- [ ] 所有SQL查询是否使用参数化查询？
- [ ] 所有动态SQL标识符是否使用SQLValidator验证？
- [ ] 所有用户输入是否使用Pydantic Schema验证？
- [ ] 是否没有字符串拼接SQL查询？

**安全检查**:
```python
# ❌ 禁止：动态标识符未验证
query = f"SELECT * FROM {table_name} WHERE {column} = ?"

# ✅ 正确：使用SQLValidator验证
validated_table = SQLValidator.validate_table_name(table_name)
validated_column = SQLValidator.validate_column_name(column)
query = f"SELECT * FROM {validated_table} WHERE {validated_column} = ?"
```

### 相关经验

- [XSS防护](#xss防护) - 另一个重要的安全防护
- [输入验证](#输入验证) - Pydantic Schema验证

### 案例文档

- [后端优化Phase 1 - 安全加固](../archive/2026-02/optimization-reports/FINAL_OPTIMIZATION_REPORT.md#phase-1-安全加固)
- [SQLValidator使用指南](../development/sql-validator-guidelines.md)

---

## XSS防护 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 3次 | **来源**: [OPTIMIZATION_LESSONS_LEARNED.md](../archive/2026-02/optimization-reports/OPTIMIZATION_LESSONS_LEARNED.md), [FINAL_OPTIMIZATION_REPORT.md](../archive/2026-02/optimization-reports/FINAL_OPTIMIZATION_REPORT.md)

### 问题现象

**症状描述**:
- 攻击者可以通过输入字段注入恶意JavaScript代码
- 可能导致Cookie窃取、会话劫持、恶意重定向

**影响范围**:
- 所有接受用户输入并显示的页面
- 所有用户可编辑的内容

### 根本原因

**技术原因**:
1. **未转义的用户输入** - 直接显示用户输入的内容
2. **DOM操作使用innerHTML** - 直接插入未验证的HTML
3. **缺少CSP策略** - 没有内容安全策略防护

### 解决方案

**1. HTML转义（Schema层实现）**:
```python
from pydantic import validator
import html

class GameCreate(BaseModel):
    name: str

    @validator("name")
    def sanitize_name(cls, v):
        """防止XSS攻击"""
        return html.escape(v.strip())
```

**2. React自动转义（前端默认防护）**:
```javascript
// ✅ React自动转义，XSS安全
<div>{userInput}</div>

// ❌ 危险：直接使用innerHTML
<div dangerouslySetInnerHTML={{ __html: userInput }} />
```

**3. 内容安全策略（CSP）**:
```html
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self'; script-src 'self'">
```

### 预防措施

**代码审查清单**:
- [ ] 所有用户输入是否在Schema层进行XSS防护？
- [ ] 是否避免使用dangerouslySetInnerHTML？
- [ ] 是否配置了CSP策略？
- [ ] 是否对富文本内容进行sanitize？

### 相关经验

- [SQL注入防护](#sql注入防护) - SQL注入防护
- [输入验证](#输入验证) - Pydantic Schema验证

---

## 输入验证 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 2次 | **来源**: [OPTIMIZATION_LESSONS_LEARNED.md](../archive/2026-02/optimization-reports/OPTIMIZATION_LESSONS_LEARNED.md)

### Pydantic Schema验证

**为什么使用Pydantic**:
- ✅ 自动类型验证
- ✅ 自动XSS防护（通过validator）
- ✅ 清晰的错误消息
- ✅ 自动文档生成

**示例**:
```python
from pydantic import BaseModel, Field, validator

class GameCreate(BaseModel):
    """游戏创建Schema"""
    gid: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    ods_db: Literal["ieu_ods", "overseas_ods"]

    @validator("name")
    def sanitize_name(cls, v):
        """防止XSS攻击"""
        return html.escape(v.strip())

# 使用
game_data = GameCreate(**request.json)
```

### 验证规则

**必填检查项**:
- [ ] 输入验证（必填字段、数据类型、长度限制）
- [ ] XSS防护（HTML转义用户输入）
- [ ] SQL注入防护（参数化查询）
- [ ] 输出编码（JSON响应，不暴露内部信息）

### 相关经验

- [SQL注入防护](#sql注入防护) - SQL注入防护
- [XSS防护](#xss防护) - XSS防护
- [API设计模式 - 错误处理](./api-design-patterns.md#错误处理) - 错误响应不暴露敏感信息

---

## 异常信息脱敏 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 2次 | **来源**: [FINAL_OPTIMIZATION_REPORT.md](../archive/2026-02/optimization-reports/FINAL_OPTIMIZATION_REPORT.md)

### 问题现象

**症状描述**:
- API错误响应暴露堆栈跟踪、SQL查询、文件路径
- 可能被攻击者利用获取系统信息

### 解决方案

**错误处理模式**:
```python
# ✅ 正确：通用错误消息
try:
    # 业务逻辑
except Exception as e:
    logger.error(f"Error creating game: {e}")  # 详细日志
    return json_error_response("Failed to create game", status_code=500)  # 通用消息

# ❌ 错误：暴露内部错误
except Exception as e:
    return jsonify({"error": str(e)}), 500  # 可能暴露路径、SQL等
```

### 预防措施

**代码审查清单**:
- [ ] 所有异常是否捕获并记录详细日志？
- [ ] 用户是否只看到通用错误消息？
- [ ] 错误响应是否不暴露堆栈跟踪？
- [ ] 错误响应是否不暴露SQL查询？
- [ ] 错误响应是否不暴露文件路径？

### 相关经验

- [API设计模式 - 错误处理](./api-design-patterns.md#错误处理) - API错误处理最佳实践

---

## Legacy API废弃管理 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [FINAL_OPTIMIZATION_REPORT.md Phase 1](../archive/2026-02/optimization-reports/FINAL_OPTIMIZATION_REPORT.md)

### 安全风险

**问题症状**:
- 废弃API可能存在未修复的安全漏洞
- 维护两套API增加安全审计难度
- 开发者可能误用废弃API

### 解决方案

**1. 标记废弃API**:
```python
from backend.core.utils.decorators import deprecated

@api_bp.route('/api/legacy/games', methods=['GET'])
@deprecated("Use /api/games instead", deprecation_date="2026-02-20")
def list_games_legacy():
    """废弃API：使用 /api/games 替代"""
    warnings.warn("This API is deprecated. Use /api/games instead.")
    # ...
```

**2. 设置API版本 sunset date**:
```python
"""
**Deprecated**: This API will be removed on 2026-05-20.
**Migration Guide**: Use /api/games with game_gid parameter.
"""
```

**3. 监控废弃API使用**:
```python
from backend.core.monitoring.deprecation_monitor import log_deprecated_api_call

@log_deprecated_api_call
def list_games_legacy():
    """自动记录废弃API调用"""
    pass
```

### 代码审查清单

- [ ] 废弃API是否标记@deprecated装饰器？
- [ ] 是否提供迁移指南？
- [ ] 是否设置sunset date？
- [ ] 是否监控废弃API使用情况？

---

## GenericRepository安全验证 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [FINAL_OPTIMIZATION_REPORT.md Phase 0](../archive/2026-02/optimization-reports/FINAL_OPTIMIZATION_REPORT.md)

### 问题现象

**症状描述**:
- GenericRepository使用动态表名和字段名
- 未验证的标识符可能导致SQL注入

### 解决方案

**GenericRepository自动验证**:
```python
from backend.core.security.sql_validator import SQLValidator

class GenericRepository:
    def __init__(self, table_name: str, primary_key: str):
        # ✅ 自动验证表名
        validated_table = SQLValidator.validate_table_name(table_name)
        self.table_name = validated_table

        # ✅ 自动验证主键
        validated_key = SQLValidator.validate_column_name(primary_key)
        self.primary_key = validated_key

    def find_by_field(self, field_name: str, value: Any):
        # ✅ 验证字段名
        validated_field = SQLValidator.validate_column_name(field_name)
        query = f"SELECT * FROM {self.table_name} WHERE {validated_field} = ?"
        return fetch_one_as_dict(query, (value,))
```

### 使用示例

```python
# ✅ 安全：GenericRepository自动验证
game_repo = GenericRepository("games", "id")  # 自动验证表名和主键
game = game_repo.find_by_field("gid", 10000147)  # 自动验证字段名
```

---

## 批量删除验证 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [FINAL_OPTIMIZATION_REPORT.md Phase 1](../archive/2026-02/optimization-reports/FINAL_OPTIMIZATION_REPORT.md)

### 问题现象

**症状描述**:
- 批量操作可能导致大量数据删除
- 缺少验证可能导致误删重要数据

### 解决方案

**批量删除验证示例**:
```python
@app.route('/api/categories/batch-delete', methods=['POST'])
def batch_delete_categories():
    category_ids = request.json.get('ids', [])

    # ✅ 验证输入
    if not category_ids:
        return json_error_response("No categories provided", status_code=400)

    if len(category_ids) > 100:
        return json_error_response("Cannot delete more than 100 categories at once", status_code=400)

    # ✅ 验证权限（不能删除系统类别）
    system_categories = fetch_all_as_dict(
        "SELECT id FROM event_categories WHERE is_system = 1 AND id IN ({})".format(
            ','.join('?' * len(category_ids))
        ),
        category_ids
    )
    if system_categories:
        return json_error_response("Cannot delete system categories", status_code=403)
```

### 代码审查清单

- [ ] 是否验证输入非空？
- [ ] 是否限制批量操作数量？
- [ ] 是否验证权限（不能删除系统数据）？
- [ ] 是否有事务保护？

---

## 相关经验文档

- [性能模式 - 缓存策略](./performance-patterns.md#缓存策略) - 缓存安全
- [数据库模式 - game_gid迁移](./database-patterns.md#game_gid迁移) - 数据库安全
