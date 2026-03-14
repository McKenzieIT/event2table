# P0-9 错误信息泄露 - 代码分析报告

**日期**: 2026-03-08
**严重程度**: 🔴 P0 - 严重 (CVSS 7.5)
**CWE**: CWE-209 (Information Exposure Through Error Messages)

---

## 问题确认

### ❌ 实际代码中的错误信息泄露

**文件**: `backend/gql_api/mutations/event_mutations.py`
**行号**: 86-88

```python
except Exception as e:
    logger.error(f"Error creating event: {e}", exc_info=True)
    return CreateEvent(ok=False, errors=[str(e)])  # ❌ 直接返回异常消息！
```

**问题**:
- `str(e)` 直接将原始异常消息返回给客户端
- 如果是数据库错误，会暴露表结构、列名、约束等
- 如果是文件错误，会暴露完整文件路径
- `exc_info=True` 会记录完整堆栈跟踪到日志（虽然不会返回客户端，但日志需要保护）

---

## 典型错误场景示例

### 场景1: 数据库约束错误

**触发代码**:
```python
# 用户尝试创建重复事件
resolve_create_event(info, game_gid=10000147, event_code="login")
# 但 "login" 事件已存在
```

**实际数据库错误**:
```python
sqlite3.IntegrityError: UNIQUE constraint failed: log_events.event_code
```

**返回给客户端的错误**:
```json
{
  "ok": false,
  "errors": ["UNIQUE constraint failed: log_events.event_code"]
}
```

**泄露的信息**:
- ❌ 表名: `log_events`
- ❌ 列名: `event_code`
- ❌ 约束类型: `UNIQUE constraint`
- ❌ 数据库类型: `sqlite3`

**应该返回的错误**:
```json
{
  "ok": false,
  "errors": ["Failed to create event. Event code may already exist."]
}
```

---

### 场景2: 文件路径错误

**触发代码**:
```python
# 配置文件缺失或路径错误
resolve_create_event(info, game_gid=10000147, ...)
```

**实际文件错误**:
```python
FileNotFoundError: [Errno 2] No such file or directory:
'/Users/mckenzie/Documents/event2table/backend/config/database.json'
```

**返回给客户端的错误**:
```json
{
  "ok": false,
  "errors": [
    "[Errno 2] No such file or directory: '/Users/mckenzie/Documents/event2table/backend/config/database.json'"
  ]
}
```

**泄露的信息**:
- ❌ 用户名: `mckenzie`
- ❌ 项目路径: `/Users/mckenzie/Documents/event2table/`
- ❌ 文件结构: `backend/config/database.json`
- ❌ 操作系统: macOS (Unix路径)

**应该返回的错误**:
```json
{
  "ok": false,
  "errors": ["Configuration error. Please contact system administrator."]
}
```

---

### 场景3: SQL语法错误

**触发代码**:
```python
# 某个内部查询有SQL语法错误
# (虽然不应该发生，但如果发生...)
```

**实际SQL错误**:
```python
psycopg2.errors.SyntaxError: syntax error at or near "WHRE"
LINE 3:     WHRE game_gid = 10000147
            ^
```

**返回给客户端的错误**:
```json
{
  "ok": false,
  "errors": [
    "syntax error at or near \"WHRE\"\nLINE 3:     WHRE game_gid = 10000147\n            ^"
  ]
}
```

**泄露的信息**:
- ❌ SQL语句片段: `WHRE game_gid = 10000147`
- ❌ 表名/列名: `game_gid`
- ❌ 数据库驱动: `psycopg2` (PostgreSQL)

**应该返回的错误**:
```json
{
  "ok": false,
  "errors": ["Database error occurred. Please try again later."]
}
```

---

## 影响范围分析

### 受影响的文件

通过grep分析，以下文件存在类似问题：

#### GraphQL Mutations

| 文件 | 问题行数 | 风险等级 |
|------|---------|---------|
| `backend/gql_api/mutations/event_mutations.py` | 88, 158 | 🔴 严重 |
| `backend/gql_api/mutations/parameter_mutations.py` | 待检查 | 🔴 严重 |
| `backend/gql_api/mutations/batch_mutations.py` | 待检查 | 🔴 严重 |

#### REST API Routes

| 目录 | 预估数量 | 风险等级 |
|------|---------|---------|
| `backend/api/routes/dwd_generator/` | ~10个文件 | 🟠 中等 |
| `backend/api/routes/canvas/` | ~5个文件 | 🟠 中等 |

---

## TDD测试失败详情

### 测试执行时间
```
Time: 20.82 seconds
```

### 失败测试列表

#### 1. test_database_error_sanitization
```
FAILED
AssertionError: Sanitized error should not contain 'constraint':
IntegrityError: FOREIGN KEY constraint failed

assert 'constraint' not in 'integrityerror: foreign key constraint failed'
```

**问题**: 数据库约束错误直接返回给客户端

#### 2. test_file_path_not_leaked
```
FAILED
AssertionError: Error should not contain file paths
assert '/Users/' not in "FileNotFoundError: [Errno 2] No such file or directory:
'/Users/mckenzie/Documents/event2table/backend/config/config.json'"
```

**问题**: 文件路径完全暴露

#### 3. test_internal_variable_names_not_leaked
```
FAILED
AssertionError: Error should not contain internal variable names
assert 'user_context' not in "NameError: name 'user_context' is not defined
in function create_event at line 42"
```

**问题**: 内部变量名和代码位置泄露

#### 4. test_stack_trace_not_leaked
```
FAILED
AssertionError: Error should not contain 'Traceback'
assert 'Traceback' not in '...'
```

**问题**: 完整堆栈跟踪泄露（最严重）

---

## 修复方案设计

### 方案1: 创建错误清理工具函数 (推荐)

**新文件**: `backend/core/security/error_sanitizer.py`

```python
from typing import Optional
import re
import os

class ErrorSanitizer:
    """错误消息清理工具"""

    # 敏感信息模式
    SENSITIVE_PATTERNS = [
        r'/[/a-zA-Z0-9_\-\.]+/',  # 文件路径
        r'\.py:',                  # Python文件路径
        r'\.pyc',                  # Python字节码
        r'Traceback',              # 堆栈跟踪
        r'File ".+", line \d+',    # 文件和行号
        r'sqlite3\.',              # 数据库驱动
        r'psycopg2\.',             # PostgreSQL驱动
        r'pymysql\.',              # MySQL驱动
        r'constraint',             # 数据库约束
        r'integrity',              # 完整性错误
        r'UNIQUE',                 # 唯一约束
        r'FOREIGN KEY',            # 外键约束
        r'PRIMARY KEY',            # 主键约束
        r'table \w+',              # 表名
        r'column \w+',             # 列名
        r'SELECT .* FROM',         # SQL语句
        r'INSERT INTO',            # SQL语句
        r'UPDATE .* SET',          # SQL语句
        r'DELETE FROM',            # SQL语句
    ]

    @classmethod
    def sanitize(cls, error: Exception) -> str:
        """
        清理异常消息，移除敏感信息

        Args:
            error: 原始异常

        Returns:
            清理后的安全错误消息
        """
        error_msg = str(error)

        # 移除敏感信息
        for pattern in cls.SENSITIVE_PATTERNS:
            error_msg = re.sub(pattern, '[REDACTED]', error_msg, flags=re.IGNORECASE)

        # 如果清理后为空或太短，返回通用消息
        if len(error_msg) < 20:
            return "An error occurred. Please try again later."

        return error_msg

    @classmethod
    def sanitize_with_context(cls, error: Exception, context: str) -> str:
        """
        清理异常消息并添加上下文

        Args:
            error: 原始异常
            context: 上下文信息（如"Failed to create event"）

        Returns:
            带上下文的安全错误消息
        """
        return f"{context}: {cls.sanitize(error)}"
```

**使用方法**:

```python
from backend.core.security.error_sanitizer import ErrorSanitizer

# 旧代码（不安全）
except Exception as e:
    return CreateEvent(ok=False, errors=[str(e)])

# 新代码（安全）
except Exception as e:
    safe_error = ErrorSanitizer.sanitize_with_context(
        e,
        "Failed to create event"
    )
    return CreateEvent(ok=False, errors=[safe_error])
```

---

### 方案2: 统一异常处理中间件

**新文件**: `backend/core/error_handling.py`

```python
from functools import wraps
from typing import Callable
from backend.core.security.error_sanitizer import ErrorSanitizer

def handle_errors(context: str):
    """
    统一异常处理装饰器

    Args:
        context: 上下文信息
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 记录详细错误到日志
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error in {context}: {e}", exc_info=True)

                # 返回安全错误给客户端
                safe_error = ErrorSanitizer.sanitize_with_context(e, context)
                return CreateEvent(ok=False, errors=[safe_error])

        return wrapper
    return decorator
```

**使用方法**:

```python
from backend.core.error_handling import handle_errors

@handle_errors("Failed to create event")
def resolve_create_event(info, game_gid, event_name, ...):
    # 业务逻辑
    pass
```

---

## 修复优先级和时间估算

### P0 - 立即修复 (4小时)

| 任务 | 文件 | 时间 | 优先级 |
|------|------|------|--------|
| 创建ErrorSanitizer工具 | `backend/core/security/error_sanitizer.py` | 1小时 | P0 |
| 修复event_mutations.py | `backend/gql_api/mutations/event_mutations.py` | 1小时 | P0 |
| 修复parameter_mutations.py | `backend/gql_api/mutations/parameter_mutations.py` | 1小时 | P0 |
| 修复batch_mutations.py | `backend/gql_api/mutations/batch_mutations.py` | 1小时 | P0 |

### P1 - 后续修复 (3小时)

| 任务 | 文件 | 时间 | 优先级 |
|------|------|------|--------|
| 修复REST API路由 | `backend/api/routes/` | 2小时 | P1 |
| 添加集成测试 | `backend/test/integration/` | 1小时 | P1 |

---

## 验证计划

### 单元测试验证

```bash
# 运行P0-9测试套件
pytest backend/test/unit/security/test_error_message_leak.py -v

# 预期结果
# 7 passed (目前是4 failed)
```

### 手动验证

使用Postman或curl测试实际API端点：

```bash
# 测试1: 触发数据库约束错误
curl -X POST http://127.0.0.1:5001/api/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { createEvent(gameGid: 10000147, eventName: \"Test\", eventCode: \"login\") { ok errors } }"
  }'

# 预期响应（修复后）
{
  "data": {
    "createEvent": {
      "ok": false,
      "errors": ["Failed to create event: An error occurred. Please try again later."]
    }
  }
}

# ❌ 当前响应（错误）
{
  "data": {
    "createEvent": {
      "ok": false,
      "errors": ["UNIQUE constraint failed: log_events.event_code"]
    }
  }
}
```

---

## 安全检查清单

修复完成后，使用以下清单验证：

- [ ] 所有异常都使用ErrorSanitizer清理
- [ ] 错误消息不包含文件路径
- [ ] 错误消息不包含堆栈跟踪
- [ ] 错误消息不包含SQL语句
- [ ] 错误消息不包含表名/列名
- [ ] 错误消息不包含数据库约束
- [ ] 详细错误记录到日志（仅内部）
- [ ] 客户端只接收通用错误消息
- [ ] 所有7个单元测试通过
- [ ] 手动测试验证

---

## 参考资料

### 安全标准
- [OWASP Error Handling](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/06.3-Testing_for_Improper_Error_Handling)
- [CWE-209: Information Exposure Through Error Messages](https://cwe.mitre.org/data/definitions/209.html)

### 项目文档
- [安全要点文档](/Users/mckenzie/Documents/event2table/docs/lessons-learned/security-essentials.md)
- [API安全规范](/Users/mckenzie/Documents/event2table/CLAUDE.md#api安全规范)

---

## 下一步行动

✅ **RED阶段完成** - 测试失败，问题确认

🔜 **GREEN阶段开始** - 实施修复

```bash
# 1. 创建ErrorSanitizer工具
# 2. 修复所有GraphQL mutations
# 3. 运行测试验证通过
# 4. 手动测试验证
```

---

**报告生成时间**: 2026-03-08
**TDD阶段**: RED → GREEN
**测试文件**: `/Users/mckenzie/Documents/event2table/backend/test/unit/security/test_error_message_leak.py`
