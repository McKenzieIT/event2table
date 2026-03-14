# TDD RED阶段报告 - P0-9错误信息泄露

**日期**: 2026-03-08
**测试文件**: `backend/test/unit/security/test_error_message_leak.py`
**测试状态**: ❌ 4 FAILED（符合预期）
**TDD阶段**: RED - 测试失败，验证问题存在

---

## 测试结果摘要

```
========================= test session starts =========================
collected 7 items

test_create_parameter_does_not_leak_stack_trace SKIPPED (mutation not yet implemented)
test_create_event_does_not_leak_sensitive_info SKIPPED (mutation not yet implemented)
test_generic_error_messages_for_all_mutations PASSED
test_database_error_sanitization FAILED
test_file_path_not_leaked FAILED
test_internal_variable_names_not_leaked FAILED
test_stack_trace_not_leaked FAILED

============== 4 failed, 1 passed, 2 skipped in 20.82s ==============
```

---

## 失败测试详情

### 1. test_database_error_sanitization ❌

**失败原因**: 数据库错误消息包含敏感信息

```python
# 测试断言失败
assert "constraint" not in sanitized.lower()

# 实际错误消息
"IntegrityError: FOREIGN KEY constraint failed"

# 问题：暴露了
# - 数据库约束类型 (FOREIGN KEY)
# - 数据库内部错误 (IntegrityError)
```

**影响**:
- ⚠️ 攻击者可以了解数据库结构
- ⚠️ 攻击者可以推断表关系

---

### 2. test_file_path_not_leaked ❌

**失败原因**: 错误消息包含完整文件路径

```python
# 测试断言失败
assert "/Users/" not in sanitized

# 实际错误消息
"FileNotFoundError: [Errno 2] No such file or directory:
'/Users/mckenzie/Documents/event2table/backend/config/config.json'"

# 问题：暴露了
# - 用户名 (mckenzie)
# - 项目路径
# - 文件结构
# - 配置文件位置
```

**影响**:
- ⚠️ 攻击者可以了解服务器文件系统
- ⚠️ 攻击者可以尝试路径遍历攻击
- ⚠️ 泄露用户隐私信息

---

### 3. test_internal_variable_names_not_leaked ❌

**失败原因**: 错误消息包含内部变量名

```python
# 测试断言失败
assert "user_context" not in sanitized

# 实际错误消息
"NameError: name 'user_context' is not defined
in function create_event at line 42"

# 问题：暴露了
# - 内部变量名 (user_context)
# - 函数名 (create_event)
# - 代码行号 (line 42)
```

**影响**:
- ⚠️ 攻击者可以了解代码实现细节
- ⚠️ 攻击者可以推断业务逻辑
- ⚠️ 增加代码逆向工程难度

---

### 4. test_stack_trace_not_leaked ❌

**失败原因**: 错误消息包含完整堆栈跟踪

```python
# 测试断言失败
assert "Traceback" not in sanitized

# 实际错误消息
"""
Traceback (most recent call last):
  File "/Users/mckenzie/Documents/event2table/backend/api/routes/events.py", line 45, in create_event
    event_id = execute_insert(...)
  File "/Users/mckenzie/Documents/event2table/backend/core/database/converters.py", line 123, in execute_insert
    cursor.execute(query, params)
sqlite3.IntegrityError: UNIQUE constraint failed
"""

# 问题：暴露了
# - 完整调用栈
# - 所有文件路径
# - 所有代码行号
# - 数据库驱动 (sqlite3)
# - 具体错误类型
```

**影响**:
- ⚠️ **最严重的信息泄露**
- ⚠️ 攻击者可以完整了解系统架构
- ⚠️ 攻击者可以定位所有可攻击点
- ⚠️ 符合OWASP Top 10 - A01:2021 – Broken Access Control

---

## 安全风险分析

### 风险等级: 🔴 **P0 - 严重**

**CVSS评分**: 7.5 (High)
**CWE分类**: CWE-209 (Information Exposure Through Error Messages)

### 泄露的敏感信息类型

| 类型 | 风险 | 示例 |
|------|------|------|
| **文件路径** | 🔴 严重 | `/Users/mckenzie/Documents/event2table/backend/config/config.json` |
| **堆栈跟踪** | 🔴 严重 | 完整调用栈、文件路径、行号 |
| **数据库结构** | 🟠 中等 | 表名、列名、约束类型 |
| **内部变量** | 🟡 低-中等 | 变量名、函数名、代码逻辑 |
| **系统信息** | 🟡 低-中等 | Python版本、库版本、操作系统 |

### 攻击场景

**场景1: 路径遍历攻击**
```
1. 攻击者触发一个错误
2. 获得文件路径: /Users/mckenzie/Documents/event2table/backend/config/config.json
3. 尝试访问: https://api.example.com/../../config/config.json
4. 下载配置文件（如果Web服务器配置不当）
```

**场景2: SQL注入推断**
```
1. 攻击者触发数据库错误
2. 获得错误: "column 'invalid_col' does not exist in table 'log_events'"
3. 推断出表名: log_events
4. 构造SQL注入: ' UNION SELECT * FROM log_events--
```

**场景3: 架构侦察**
```
1. 攻击者触发多个错误
2. 分析所有堆栈跟踪
3. 绘制完整系统架构图:
   - 路由层: backend/api/routes/events.py
   - 数据层: backend/core/database/converters.py
   - 模型层: backend/models/repositories/events.py
4. 针对性攻击每一层
```

---

## 下一步行动（TDD GREEN阶段）

### 任务清单

- [ ] **P0-9.1**: 创建错误清理工具函数 (`backend/core/security/error_sanitizer.py`)
  - `sanitize_error_message()` - 清理错误消息
  - `is_safe_to_show_user()` - 检查错误是否安全
  - `remove_file_paths()` - 移除文件路径
  - `remove_stack_trace()` - 移除堆栈跟踪
  - `remove_sql_details()` - 移除SQL细节

- [ ] **P0-9.2**: 在所有GraphQL mutations中应用错误清理
  - `backend/gql_api/mutations/parameter_mutations.py`
  - `backend/gql_api/mutations/event_mutations.py`
  - `backend/gql_api/mutations/batch_mutations.py`
  - 所有其他mutations

- [ ] **P0-9.3**: 在REST API中应用错误清理
  - `backend/api/routes/` 下的所有路由
  - 统一错误处理中间件

- [ ] **P0-9.4**: 更新日志系统
  - 详细错误记录到日志（仅内部）
  - 通用错误返回给客户端

- [ ] **P0-9.5**: 验证所有测试通过（GREEN阶段）
  ```bash
  pytest backend/test/unit/security/test_error_message_leak.py -v
  # 预期: 7 passed
  ```

---

## 实施优先级

| 优先级 | 任务 | 预计时间 |
|--------|------|---------|
| **P0** | 创建错误清理工具 | 1小时 |
| **P0** | 修复GraphQL mutations | 2小时 |
| **P1** | 修复REST API路由 | 2小时 |
| **P1** | 更新日志系统 | 1小时 |
| **P2** | 添加单元测试覆盖率 | 1小时 |
| **P2** | 添加集成测试 | 1小时 |

**总计**: 约8小时

---

## 参考资料

- **OWASP**: [Error Handling and Logging](https://owasp.org/www-community/ vulnerabilities/Information_exposure_through_an_error_message)
- **CWE-209**: [Information Exposure Through Error Messages](https://cwe.mitre.org/data/definitions/209.html)
- **CWE-532**: [Insertion of Sensitive Information into Log File](https://cwe.mitre.org/data/definitions/532.html)
- **安全要点文档**: `/Users/mckenzie/Documents/event2table/docs/lessons-learned/security-essentials.md`

---

## 测试文件位置

```
/Users/mckenzie/Documents/event2table/backend/test/unit/security/test_error_message_leak.py
```

---

## 下一步

✅ **RED阶段完成** - 测试失败，验证问题存在

🔜 **GREEN阶段** - 实现最小代码使测试通过

```bash
# 开始GREEN阶段
# 创建错误清理工具函数
# 修改所有mutations使用清理后的错误消息
# 运行测试验证通过
```

---

**报告生成时间**: 2026-03-08
**TDD专家**: Claude (Sonnet 4.6)
**项目**: Event2Table - P0-9错误信息泄露修复
