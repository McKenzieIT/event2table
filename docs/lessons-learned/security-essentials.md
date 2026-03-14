# 安全要点

> **来源**: 整合了3个文档的安全相关经验 + 2026-03最新安全修复
> **最后更新**: 2026-03-09
> **维护**: 每次安全问题修复后立即更新

---

## SQL注入防护 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 3次 | **来源**: [OPTIMIZATION_LESSONS_LEARNED.md](../archive/2026-02/optimization/OPTIMIZATION_LESSONS_LEARNED.md), [FINAL_OPTIMIZATION_REPORT.md](../archive/2026-02/optimization/FINAL_OPTIMIZATION_REPORT.md), [sql-validator-guidelines.md](../development/sql-validator-guidelines.md)

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

- [XSS防护](#xss防护-⚠️-p0极其重要---2026-03-09新增) - 另一个重要的安全防护
- [输入验证](#输入验证) - Pydantic Schema验证
- [权限检查完整性](#权限检查完整性-⚠️-p0极其重要---2026-03-09新增) - 认证和授权装饰器

---

## XSS防护 ⚠️ **P0极其重要 - 2026-03-09新增**

**优先级**: P0 | **出现次数**: 1次 | **来源**: [XSS防护修复报告](../reports/2026-03-09/XSS-PROTECTION-FIX-SUMMARY.md), [P0-7权限检查报告](../reports/2026-03-09/P0-7-PERMISSION-CHECK-COMPLETE.md)

### 问题现象

**症状描述**:
- 事件名称和参数名称未进行HTML转义
- 允许恶意脚本注入：`<script>alert('xss')</script>`
- 存储到数据库后，前端显示时执行恶意代码

**攻击示例**:
```javascript
// 恶意输入
event_name = "<script>alert('XSS')</script>"

// 如果未转义，存储到数据库
// 前端显示时：<script>标签会执行
```

### 根本原因

**技术原因**:
1. **Pydantic Schema缺少输入清理步骤** - 未在验证层进行XSS防护
2. **用户输入直接存储** - 未经过任何HTML转义
3. **前端未进行输出编码** - 直接渲染未清理的用户输入

### 解决方案

**1. Pydantic Validator集成html.escape()**:
```python
# backend/models/schemas.py
import html
from pydantic import BaseModel, Field, field_validator

class EventBase(BaseModel):
    """事件基础Schema"""
    event_name: str = Field(..., min_length=1, max_length=100)

    @field_validator("event_name", mode="before")
    @classmethod
    def sanitize_event_name(cls, v):
        """验证并清理事件名，防止XSS攻击"""
        if isinstance(v, str):
            v = v.strip()
        if not v:
            raise ValueError("event_name不能为空")
        if " " in v:
            raise ValueError("event_name不能包含空格")
        # ✅ 转义HTML特殊字符，防止XSS攻击
        return html.escape(v) if isinstance(v, str) else v
```

**HTML转义规则**:
- `<` → `&lt;`
- `>` → `&gt;`
- `&` → `&amp;`
- `"` → `&quot;`
- `'` → `&#x27;`

**2. 所有用户输入字段添加XSS防护**:
```python
# 参数名称也需要XSS防护
class ParameterBase(BaseModel):
    param_name: str = Field(..., min_length=1, max_length=50)
    display_name: Optional[str] = Field(None, max_length=100)

    @field_validator("param_name", mode="before")
    @classmethod
    def sanitize_param_name(cls, v):
        """验证并清理参数名（snake_case），防止XSS攻击"""
        if isinstance(v, str):
            v = v.strip()
        if not v:
            raise ValueError("param_name不能为空")
        if " " in v:
            raise ValueError("param_name不能包含空格，请使用snake_case格式")
        return html.escape(v) if isinstance(v, str) else v
```

**3. 测试验证**:
```python
# backend/test/unit/security/test_xss_protection.py
def test_event_name_xss_payload_is_escaped():
    """测试XSS payload被转义"""
    from backend.models.schemas import EventCreate

    xss_payload = "<script>alert('xss')</script>"
    event_data = EventCreate(
        game_gid=90000001,
        event_name=xss_payload,
        event_name_cn="测试事件",
        source_table="ieu_ods.ods_90000001_all_view",
        target_table="dwd.v_dwd_90000001_test_di"
    )

    # 验证：XSS payload应被转义
    assert "&lt;script&gt;" in event_data.event_name
    assert "<script>" not in event_data.event_name
```

### 预防措施

**代码审查清单**:
- [ ] 所有用户输入字段都添加了`html.escape()`转义？
- [ ] 在Pydantic Schema层进行输入验证（最早防护层）？
- [ ] 使用`@field_validator(mode="before")`确保转义在其他验证之前执行？

**TDD测试流程**:
1. RED: 编写失败的测试（XSS payload应被转义）
2. GREEN: 实现html.escape()验证器
3. REFACTOR: 重构代码，保持测试通过

### 相关经验

- [输入验证](#输入验证) - Pydantic Schema验证
- [权限检查完整性](#权限检查完整性-⚠️-p0极其重要---2026-03-09新增) - 认证和授权装饰器

---

## 权限检查完整性 ⚠️ **P0极其重要 - 2026-03-09新增**

**优先级**: P0 | **出现次数**: 1次 | **来源**: [P0-11权限检查报告](../reports/2026-03-09/P0-11-PERMISSION-CHECK-COMPLETE.md), [权限检查设计文档](../../backend/core/security/authentication.py)

### 问题现象

**症状描述**:
- GraphQL mutations没有身份验证和授权检查
- 任何人都可以创建、修改、删除数据
- 存在严重安全风险

### 根本原因

**技术原因**:
1. **Mutations直接执行业务逻辑** - 没有验证用户身份
2. **缺少权限检查机制** - 没有认证和授权装饰器
3. **GraphQL Context未传递用户信息** - 无法进行权限验证

### 解决方案

**1. 认证装饰器（@authenticated）**:
```python
# backend/core/security/authentication.py
from functools import wraps

def authenticated(func):
    """
    Authentication decorator - verifies user is logged in

    Checks that the GraphQL context contains a valid user.
    """
    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        # Check if context exists
        if not hasattr(info, 'context'):
            raise Exception("Authentication required: No context found")

        # Check if user exists in context
        if info.context.user is None:
            raise Exception("Authentication required: Please log in")

        return func(root, info, *args, **kwargs)
    return wrapper
```

**2. 授权装饰器（@require_permission）**:
```python
def require_permission(permission: str):
    """
    Authorization decorator - verifies user has specific permission

    Checks that the authenticated user has the required permission.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(root, info, *args, **kwargs):
            # First check authentication
            if not hasattr(info, 'context') or info.context.user is None:
                raise Exception("Authentication required: Please log in")

            user = info.context.user

            # Check if user has permissions attribute
            if not hasattr(user, 'permissions'):
                raise Exception(f"Authorization failed: Permission '{permission}' required")

            # Check if user has the required permission
            if permission not in user.permissions:
                raise Exception(f"Authorization failed: Missing '{permission}' permission")

            return func(root, info, *args, **kwargs)
        return wrapper
    return decorator
```

**3. Mutation应用示例**:
```python
# backend/gql_api/mutations/game_mutations.py
class CreateGame(graphene.Mutation):
    """Create a new game"""

    class Arguments:
        gid = graphene.Int(required=True, description="游戏GID")
        name = graphene.String(required=True, description="游戏名称")
        ods_db = graphene.String(required=True, description="ODS数据库名称")

    ok = graphene.Boolean(description="操作是否成功")
    game = Field(GameType, description="创建的游戏")
    errors = graphene.List(graphene.String, description="错误信息")

    @authenticated
    @require_permission('game:write')
    def mutate(self, info, gid: int, name: str, ods_db: str):
        """Execute the mutation"""
        # Mutation logic here
        pass
```

**4. 权限体系设计**:

采用 `资源:操作` 格式的权限字符串：

- **事件权限**: `event:write`, `event:delete`
- **游戏权限**: `game:write`, `game:delete`
- **参数权限**: `parameter:write`, `parameter:delete`
- **批量操作权限**: `batch:create`, `batch:update`, `batch:delete`

### 预防措施

**代码审查清单**:
- [ ] 所有mutations必须添加`@authenticated`装饰器？
- [ ] 所有写操作必须添加`@require_permission`装饰器？
- [ ] 架构验证：自动化检查所有mutations都有认证装饰器？
- [ ] 每个mutation都有认证和授权测试？

**测试验证**:
```python
def test_create_event_requires_authentication():
    """未登录用户应无法创建事件"""
    # 模拟未登录用户
    info = Mock()
    info.context = Mock(user=None)

    mutation = CreateEvent()

    with pytest.raises(Exception) as exc_info:
        mutation.mutate(info, game_gid=90000001, event_name="Test")

    error_msg = str(exc_info.value).lower()
    assert any(keyword in error_msg for keyword in [
        "authentication", "unauthorized", "login"
    ]), f"Expected auth error, got: {exc_info.value}"
```

### 相关经验

- [XSS防护](#xss防护-⚠️-p0极其重要---2026-03-09新增) - XSS防护实施
- [输入验证](#输入验证) - Pydantic Schema验证

---

## 输入验证层次 ⚠️ **P0极其重要 - 2026-03-09新增**

**优先级**: P0 | **出现次数**: 1次 | **来源**: [P0-8验证器执行顺序报告](../reports/2026-03-09/P0-8-VALIDATOR-EXECUTION-ORDER-FIX.md)

### 问题现象

**症状描述**:
- 自定义验证器的错误消息不显示
- 输入`param_name=""`时期望错误：`"param_name不能为空"`
- 实际错误：`"String should have at least 1 character"` ❌

### 根本原因

**技术原因**:
1. **Field验证先执行** - Pydantic的Field验证（`min_length=1`）在自定义验证器之前执行
2. **自定义验证器没有机会执行** - Field验证失败后，自定义验证器被跳过

### 解决方案

**1. 使用mode="before"确保验证顺序**:
```python
# ❌ 错误：Field验证先执行
@validator("param_name")  # 默认mode="after"
def sanitize_param_name(cls, v):
    v = v.strip()
    if not v:
        raise ValueError("param_name不能为空")  # 永远不会执行
    return html.escape(v)

# ✅ 正确：自定义验证器先执行
@field_validator("param_name", mode="before")
@classmethod
def sanitize_param_name(cls, v):
    """验证并清理参数名（snake_case），防止XSS攻击"""
    if isinstance(v, str):
        v = v.strip()
    if not v:
        raise ValueError("param_name不能为空")  # ✅ 会执行
    if " " in v:
        raise ValueError("param_name不能包含空格，请使用snake_case格式")
    return html.escape(v) if isinstance(v, str) else v
```

**2. 验证器模式对比**:

| 模式 | 执行顺序 | 用途 | 示例 |
|------|---------|------|------|
| `mode="after"` (默认) | Field → 自定义验证器 | 对已验证的值进行后处理 | 数据转换、格式化 |
| `mode="before"` | 自定义验证器 → Field | 自定义验证逻辑优先执行 | XSS防护、空值检查 |

**3. Pydantic V1 vs V2迁移**:

```python
# Pydantic V1 (已废弃)
@validator("field_name", pre=True)
def validate_field(cls, v):
    return v

# Pydantic V2 (推荐)
@field_validator("field_name", mode="before")
@classmethod
def validate_field(cls, v):
    return v
```

### 预防措施

**代码审查清单**:
- [ ] 需要自定义验证逻辑时，优先使用`mode="before"`？
- [ ] 测试验证顺序，确保自定义验证器有机会执行？
- [ ] 从V1迁移到V2时，将`@validator(pre=True)`替换为`@field_validator(mode="before")`？
- [ ] 添加`@classmethod`装饰器（Pydantic V2规范）？

**测试验证**:
```python
def test_validator_execution_order():
    """测试验证器执行顺序"""
    # 测试mode="before"的验证器先执行
    # 测试自定义错误消息显示
    # 测试Field验证不会阻止自定义验证器
```

### 相关经验

- [XSS防护](#xss防护-⚠️-p0极其重要---2026-03-09新增) - XSS防护需要`mode="before"`
- [权限检查完整性](#权限检查完整性-⚠️-p0极其重要---2026-03-09新增) - 认证和授权装饰器

### 案例文档

- [后端优化Phase 1 - 安全加固](../archive/2026-02/optimization/FINAL_OPTIMIZATION_REPORT.md#phase-1-安全加固)
- [SQLValidator使用指南](../development/sql-validator-guidelines.md)

---

## XSS防护 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 3次 | **来源**: [OPTIMIZATION_LESSONS_LEARNED.md](../archive/2026-02/optimization/OPTIMIZATION_LESSONS_LEARNED.md), [FINAL_OPTIMIZATION_REPORT.md](../archive/2026-02/optimization/FINAL_OPTIMIZATION_REPORT.md)

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

**优先级**: P1 | **出现次数**: 2次 | **来源**: [OPTIMIZATION_LESSONS_LEARNED.md](../archive/2026-02/optimization/OPTIMIZATION_LESSONS_LEARNED.md)

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

**优先级**: P0 | **出现次数**: 2次 | **来源**: [FINAL_OPTIMIZATION_REPORT.md](../archive/2026-02/optimization/FINAL_OPTIMIZATION_REPORT.md)

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

**优先级**: P1 | **出现次数**: 1次 | **来源**: [FINAL_OPTIMIZATION_REPORT.md Phase 1](../archive/2026-02/optimization/FINAL_OPTIMIZATION_REPORT.md)

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

**优先级**: P1 | **出现次数**: 1次 | **来源**: [FINAL_OPTIMIZATION_REPORT.md Phase 0](../archive/2026-02/optimization/FINAL_OPTIMIZATION_REPORT.md)

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

**优先级**: P1 | **出现次数**: 1次 | **来源**: [FINAL_OPTIMIZATION_REPORT.md Phase 1](../archive/2026-02/optimization/FINAL_OPTIMIZATION_REPORT.md)

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

## SQL注入防护的层次化策略 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 多次 | **来源**: 多个安全相关报告

### 核心原则

**多层次防护体系**:
1. **参数化查询** - 所有SQL查询必须使用参数化
2. **SQLValidator** - 动态SQL标识符必须使用白名单验证
3. **输入验证** - 使用Pydantic Schema进行输入验证
4. **错误信息脱敏** - 避免暴露SQL查询细节

### 实现示例

**参数化查询**:
```python
# ✅ 安全：参数化查询
def get_events(game_gid: int):
    query = "SELECT * FROM log_events WHERE game_gid = ?"
    return fetch_all_as_dict(query, (game_gid,))

# ❌ 危险：字符串拼接
def get_events(game_gid: int):
    query = f"SELECT * FROM log_events WHERE game_gid = {game_gid}"  # SQL注入风险！
```

**SQLValidator验证**:
```python
from backend.core.security.sql_validator import SQLValidator

# ✅ 安全：验证动态表名
table_name = request.args.get("table")
validated_table = SQLValidator.validate_table_name(table_name)
query = f"SELECT * FROM {validated_table}"

# ✅ 安全：使用白名单验证
ALLOWED_FIELDS = {"name", "created_at", "id"}
SQLValidator.validate_field_whitelist(sort_by, ALLOWED_FIELDS)
```

### 代码审查清单

- [ ] 所有SQL查询是否使用参数化？
- [ ] 动态SQL标识符是否使用SQLValidator验证？
- [ ] 是否使用Pydantic Schema进行输入验证？
- [ ] 错误信息是否脱敏？

### 相关经验

- [SQL注入防护](#sql注入防护) - 基础SQL注入防护
- [XSS防护](#xss防护) - XSS防护策略

---

## XSS防护的自动化实现 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 多次 | **来源**: Entity相关报告

### Pydantic自动XSS防护

**字段验证器**:
```python
from pydantic import BaseModel, Field, field_validator
import html

class GameEntity(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

    @field_validator('name')
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """自动XSS防护"""
        return html.escape(v.strip())
```

**输出编码**:
```python
# JSON序列化自动处理特殊字符
from flask import jsonify

@app.route('/api/games')
def get_games():
    games = fetch_all_as_dict("SELECT * FROM games")
    return jsonify(games)  # ✅ 自动JSON编码，防止XSS
```

### 代码审查清单

- [ ] 用户输入是否使用@field_validator自动转义？
- [ ] JSON响应是否使用jsonify()而非手动拼接？
- [ ] 是否避免在HTML中直接插入用户输入？
- [ ] 是否使用textContent而非innerHTML？

### 相关经验

- [XSS防护](#xss防护) - 基础XSS防护
- [输入验证](#输入验证) - Pydantic Schema验证

---

## 相关经验文档

- [性能模式 - 缓存策略](./performance-patterns.md#缓存策略) - 缓存安全
- [数据库模式 - game_gid迁移](./database-patterns.md#game_gid迁移) - 数据库安全
