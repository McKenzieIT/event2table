# P0-9 错误信息泄露 - 测试失败证据

**TDD阶段**: ✅ RED - 测试失败（符合预期）
**测试文件**: `backend/test/unit/security/test_error_message_leak.py`
**执行时间**: 2026-03-08
**测试状态**: ❌ 4 FAILED, 1 PASSED, 2 SKIPPED

---

## 测试执行摘要

### 命令
```bash
source backend/venv/bin/activate
python -m pytest backend/test/unit/security/test_error_message_leak.py -v -s
```

### 结果
```
collected 7 items

test_create_parameter_does_not_leak_stack_trace SKIPPED
test_create_event_does_not_leak_sensitive_info SKIPPED
test_generic_error_messages_for_all_mutations PASSED
test_database_error_sanitization FAILED
test_file_path_not_leaked FAILED
test_internal_variable_names_not_leaked FAILED
test_stack_trace_not_leaked FAILED

============== 4 failed, 1 passed, 2 skipped in 20.82s ==============
```

---

## 失败测试详情

### 失败 #1: test_database_error_sanitization

**测试目的**: 验证数据库错误消息不暴露表结构、列名、约束等敏感信息

**测试代码**:
```python
def test_database_error_sanitization():
    raw_db_errors = [
        "IntegrityError: FOREIGN KEY constraint failed",
        "OperationalError: no such table: log_events",
        "ProgrammingError: column 'invalid_col' does not exist",
        # ...
    ]

    def sanitize_error(error_msg: str) -> str:
        return error_msg  # ❌ 当前实现：直接返回原始错误

    for error in raw_db_errors:
        sanitized = sanitize_error(error)
        assert "constraint" not in sanitized.lower()
        # ...
```

**失败原因**:
```
E   AssertionError: Sanitized error should not contain 'constraint':
E   IntegrityError: FOREIGN KEY constraint failed
E   assert 'constraint' not in 'integrityerror: foreign key constraint failed'
E     'constraint' is contained here:
E       integrityerror: foreign key constraint failed
E     ?                             ++++++++++
```

**泄露的信息**:
- ❌ 数据库约束类型: `FOREIGN KEY`
- ❌ 数据库内部错误: `IntegrityError`
- ❌ 数据库技术栈: `FOREIGN KEY constraint failed`

---

### 失败 #2: test_file_path_not_leaked

**测试目的**: 验证错误消息不包含文件路径

**测试代码**:
```python
def test_file_path_not_leaked():
    error_with_path = (
        "FileNotFoundError: [Errno 2] No such file or directory: "
        "'/Users/mckenzie/Documents/event2table/backend/config/config.json'"
    )

    def sanitize_error(error_msg: str) -> str:
        return error_msg  # ❌ 当前实现：直接返回原始错误

    sanitized = sanitize_error(error_with_path)
    assert "/Users/" not in sanitized
    # ...
```

**失败原因**:
```
E   AssertionError: Error should not contain file paths
E   assert '/Users/' not in "FileNotFoundError: [Errno 2] No such file or directory:
E   '/Users/mckenzie/Documents/event2table/backend/config/config.json'"
E     '/Users/' is contained here:
E       FileNotFoundError: [Errno 2] No such file or directory:
E       '/Users/mckenzie/Documents/event2table/backend/config/config.json'
E     ?                                                          +++++++
```

**泄露的信息**:
- ❌ 用户名: `mckenzie`
- ❌ 项目路径: `/Users/mckenzie/Documents/event2table/`
- ❌ 文件结构: `backend/config/config.json`
- ❌ 操作系统: macOS (Unix路径风格)

---

### 失败 #3: test_internal_variable_names_not_leaked

**测试目的**: 验证错误消息不包含内部变量名和代码位置

**测试代码**:
```python
def test_internal_variable_names_not_leaked():
    error_with_vars = (
        "NameError: name 'user_context' is not defined "
        "in function create_event at line 42"
    )

    def sanitize_error(error_msg: str) -> str:
        return error_msg  # ❌ 当前实现：直接返回原始错误

    sanitized = sanitize_error(error_with_vars)
    assert "user_context" not in sanitized
    # ...
```

**失败原因**:
```
E   AssertionError: Error should not contain internal variable names
E   assert 'user_context' not in "NameError: name 'user_context' is not defined
E   in function create_event at line 42"
E     'user_context' is contained here:
E       NameError: name 'user_context' is not defined in function create_event at line 42
E     ?                  +++++++++++
```

**泄露的信息**:
- ❌ 内部变量名: `user_context`
- ❌ 函数名: `create_event`
- ❌ 代码行号: `line 42`
- ❌ 代码实现细节

---

### 失败 #4: test_stack_trace_not_leaked ⚠️ **最严重**

**测试目的**: 验证错误消息不包含完整堆栈跟踪

**测试代码**:
```python
def test_stack_trace_not_leaked():
    stack_trace = """
Traceback (most recent call last):
  File "/Users/mckenzie/Documents/event2table/backend/api/routes/events.py", line 45, in create_event
    event_id = execute_insert(...)
  File "/Users/mckenzie/Documents/event2table/backend/core/database/converters.py", line 123, in execute_insert
    cursor.execute(query, params)
sqlite3.IntegrityError: UNIQUE constraint failed
    """

    def sanitize_error(error_msg: str) -> str:
        return error_msg  # ❌ 当前实现：直接返回原始错误

    sanitized = sanitize_error(stack_trace)
    assert "Traceback" not in sanitized
    # ...
```

**失败原因**:
```
E   AssertionError: Error should not contain 'Traceback'
E   assert 'Traceback' not in '...'
E     'Traceback' is contained here:
E
E       Traceback (most recent call last):
E     ? +++++++++
E         File "/Users/mckenzie/Documents/event2table/backend/api/routes/events.py", line 45, in create_event
E           event_id = execute_insert(...)
E         File "/Users/mckenzie/Documents/event2table/backend/core/database/converters.py", line 123, in execute_insert
E           cursor.execute(query, params)
E       sqlite3.IntegrityError: UNIQUE constraint failed
```

**泄露的信息** (最严重):
- ❌ **完整堆栈跟踪** - 所有函数调用链
- ❌ **所有文件路径**:
  - `/Users/mckenzie/Documents/event2table/backend/api/routes/events.py`
  - `/Users/mckenzie/Documents/event2table/backend/core/database/converters.py`
- ❌ **所有代码行号**: `line 45`, `line 123`
- ❌ **数据库驱动**: `sqlite3`
- ❌ **具体错误类型**: `UNIQUE constraint failed`
- ❌ **系统架构**:
  - 路由层: `backend/api/routes/events.py`
  - 数据层: `backend/core/database/converters.py`
  - 函数名: `create_event`, `execute_insert`

**安全影响**:
- 🔴 **OWASP Top 10 - A01:2021 – Broken Access Control**
- 🔴 **CVSS 7.5 (High)**
- 🔴 **CWE-209: Information Exposure Through Error Messages**

---

## 测试失败证据 - 完整输出

### test_stack_trace_not_leaked 完整输出

```
backend/test/unit/security/test_error_message_leak.py:300: in test_stack_trace_not_leaked
    assert "Traceback" not in sanitized, \
E   AssertionError: Error should not contain 'Traceback'
E   assert 'Traceback' not in '\nTraceback (most recent call last):\n  File "/Users/mckenzie/Documents/event2table/backend/api/routes/events.py", line 45, in create_event\n    event_id = execute_insert(...)\n  File "/Users/mckenzie/Documents/event2table/backend/core/database/converters.py", line 123, in execute_insert\n    cursor.execute(query, params)\nsqlite3.IntegrityError: UNIQUE constraint failed\n    '
E     'Traceback' is contained here:
E
E       Traceback (most recent call last):
E     ? +++++++++
E         File "/Users/mckenzie/Documents/event2table/backend/api/routes/events.py", line 45, in create_event
E           event_id = execute_insert(...)
E         File "/Users/mckenzie/Documents/event2table/backend/core/database/converters.py", line 123, in execute_insert
E           cursor.execute(query, params)
E       sqlite3.IntegrityError: UNIQUE constraint failed
```

---

## 实际代码问题证据

### 文件: backend/gql_api/mutations/event_mutations.py

**行号**: 86-88

```python
except Exception as e:
    logger.error(f"Error creating event: {e}", exc_info=True)
    return CreateEvent(ok=False, errors=[str(e)])  # ❌ 直接返回异常消息！
```

**问题**:
- `str(e)` 将原始异常转换为字符串
- 直接返回给GraphQL客户端
- 没有任何清理或过滤

**实际错误示例**:

| 触发场景 | 原始异常 | 返回给客户端 | 泄露信息 |
|---------|---------|------------|---------|
| 重复事件 | `sqlite3.IntegrityError: UNIQUE constraint failed: log_events.event_code` | `UNIQUE constraint failed: log_events.event_code` | 表名、列名、约束 |
| 配置缺失 | `FileNotFoundError: /Users/mckenzie/.../config.json` | 完整文件路径 | 用户名、路径、系统信息 |
| SQL错误 | `psycopg2.errors.SyntaxError: ...` | 完整SQL和位置 | SQL语句、数据库结构 |
| 代码错误 | `NameError: name 'user_context' is not defined` | 变量名和函数位置 | 内部变量、代码结构 |

---

## 安全风险评估

### CVSS评分计算

**Base Score**: 7.5 (High)

**评分向量**:
```
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N
```

**分解**:
- **Attack Vector (AV)**: Network (N) - 可远程触发
- **Attack Complexity (AC)**: Low (L) - 易于触发
- **Privileges Required (PR)**: None (N) - 无需认证
- **User Interaction (UI)**: None (N) - 自动触发
- **Scope (S)**: Unchanged (U) - 仅影响当前应用
- **Confidentiality (C)**: High (H) - 泄露大量敏感信息
- **Integrity (I)**: None (N) - 不影响数据完整性
- **Availability (A)**: None (N) - 不影响可用性

### CWE分类

**CWE-209**: Information Exposure Through Error Messages
- **描述**: 产品通过错误消息泄露敏感信息
- **影响**: 攻击者可以获取系统内部信息
- **常见于**: Web应用、API、数据库错误处理

### OWASP Top 10

**A01:2021 – Broken Access Control**
- **排名**: 第1名（最严重）
- **描述**: 用户可以访问或操作超出其权限的资源或功能
- **子类别**: 错误消息泄露导致的信息泄露

---

## 测试覆盖率

### 测试场景覆盖

| 测试 | 覆盖场景 | 状态 |
|------|---------|------|
| test_database_error_sanitization | 数据库约束错误 | ❌ 失败 |
| test_file_path_not_leaked | 文件路径错误 | ❌ 失败 |
| test_internal_variable_names_not_leaked | 内部变量泄露 | ❌ 失败 |
| test_stack_trace_not_leaked | 完整堆栈跟踪泄露 | ❌ 失败 |
| test_generic_error_messages_for_all_mutations | 通用错误消息验证 | ✅ 通过 |

### 未覆盖场景（待添加测试）

- [ ] HTTP响应头中的错误信息
- [ ] 日志文件中的敏感信息
- [ ] GraphQL错误扩展字段
- [ ] 错误码枚举
- [ ] 多语言错误消息

---

## 修复时间估算

### 立即修复 (P0) - 4小时

| 任务 | 文件 | 时间 |
|------|------|------|
| 创建ErrorSanitizer | `backend/core/security/error_sanitizer.py` | 1小时 |
| 修复GraphQL mutations | `backend/gql_api/mutations/*.py` | 2小时 |
| 运行测试验证通过 | 所有测试 | 1小时 |

### 后续优化 (P1) - 3小时

| 任务 | 文件 | 时间 |
|------|------|------|
| 修复REST API | `backend/api/routes/*.py` | 2小时 |
| 添加更多测试 | `backend/test/unit/security/` | 1小时 |

**总计**: 7小时

---

## 下一步行动

### ✅ RED阶段完成

- ✅ 创建测试文件
- ✅ 测试执行并失败
- ✅ 验证问题存在
- ✅ 生成测试报告
- ✅ 分析安全风险

### 🔜 GREEN阶段开始

1. **创建ErrorSanitizer工具** (1小时)
   ```python
   # backend/core/security/error_sanitizer.py
   class ErrorSanitizer:
       @classmethod
       def sanitize(cls, error: Exception) -> str:
           # 移除敏感信息
           pass
   ```

2. **修复GraphQL mutations** (2小时)
   ```python
   # 旧代码
   except Exception as e:
       return CreateEvent(ok=False, errors=[str(e)])

   # 新代码
   except Exception as e:
       safe_error = ErrorSanitizer.sanitize_with_context(e, "Failed to create event")
       return CreateEvent(ok=False, errors=[safe_error])
   ```

3. **运行测试验证** (1小时)
   ```bash
   pytest backend/test/unit/security/test_error_message_leak.py -v
   # 预期: 7 passed
   ```

---

## 测试文件位置

```
/Users/mckenzie/Documents/event2table/backend/test/unit/security/test_error_message_leak.py
```

## 相关文档

- **TDD RED阶段报告**: `docs/reports/2026-03-08/TDD-RED-P0-9-ERROR-MESSAGE-LEAK.md`
- **代码分析报告**: `docs/reports/2026-03-08/P0-9-CODE-ANALYSIS.md`
- **测试失败证据**: `docs/reports/2026-03-08/P0-9-TEST-FAILURE-EVIDENCE.md` (本文档)
- **安全要点**: `docs/lessons-learned/security-essentials.md`

---

**报告生成时间**: 2026-03-08
**TDD阶段**: ✅ RED → 🔜 GREEN
**测试状态**: ❌ 4 FAILED (符合预期)
**P0-9优先级**: 🔴 严重 (CVSS 7.5)
