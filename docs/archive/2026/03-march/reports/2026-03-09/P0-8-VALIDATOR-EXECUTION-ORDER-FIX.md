# P0-8 验证器执行顺序修复报告

**日期**: 2026-03-09
**优先级**: P0-8
**状态**: ✅ 已完成
**TDD阶段**: GREEN ✅

---

## 问题诊断

### 问题描述

Pydantic自定义验证器的错误消息没有显示，而是显示Field的默认错误消息。

**示例**:
- 输入: `param_name=""`
- 期望错误: `"param_name不能为空"`
- 实际错误: `"String should have at least 1 character"` ❌

### 根本原因

Pydantic的验证执行顺序：
1. **Field验证** (先执行): `min_length=1` → 检查字符串长度
2. **自定义验证器** (后执行): `@validator` → 业务逻辑验证

由于Field验证先执行，当输入为空字符串时，直接抛出`String should have at least 1 character`错误，自定义验证器根本没有机会执行。

**验证顺序问题**:
```
输入: param_name=""
  ↓
Field(min_length=1) 验证
  ↓ (失败，抛出错误)
❌ "String should have at least 1 character"
  ↓ (自定义验证器未执行)
```

---

## 修复方案

### 核心策略

使用`@field_validator(mode="before")`让自定义验证器在Field验证**之前**执行。

**修复后的验证顺序**:
```
输入: param_name=""
  ↓
@field_validator(mode="before") 验证 (优先执行)
  ↓ (检测到空字符串)
✅ "param_name不能为空" (自定义消息)
  ↓ (Field验证未执行)
```

### 代码修改

**文件**: `/Users/mckenzie/Documents/event2table/backend/models/schemas.py`

#### 1. 导入更新

```python
# 修改前
from pydantic import BaseModel, Field, validator

# 修改后
from pydantic import BaseModel, Field, field_validator, validator
```

#### 2. EventParameterBase.param_name 验证器

```python
# 修改前
@validator("param_name")
def sanitize_param_name(cls, v):
    """验证并清理参数名（snake_case），防止XSS攻击"""
    v = v.strip()
    if not v:
        raise ValueError("param_name不能为空")
    if " " in v:
        raise ValueError("param_name不能包含空格，请使用snake_case格式")
    return html.escape(v)

# 修改后
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

#### 3. EventBase.event_name 验证器

```python
# 修改前
@validator("event_name")
def sanitize_event_name(cls, v):
    """验证并清理事件名，防止XSS攻击"""
    v = v.strip()
    if not v:
        raise ValueError("event_name不能为空")
    if " " in v:
        raise ValueError("event_name不能包含空格")
    return html.escape(v)

# 修改后
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
    return html.escape(v) if isinstance(v, str) else v
```

### 关键改进点

1. **`mode="before"`**: 自定义验证器在Field验证之前执行
2. **`@classmethod`**: 符合Pydantic V2规范
3. **类型检查**: `isinstance(v, str)` 防止非字符串输入
4. **条件转义**: `html.escape(v) if isinstance(v, str) else v` 安全处理

---

## 测试验证

### 测试文件

`/Users/mckenzie/Documents/event2table/backend/test/unit/security/test_input_validation.py`

### 测试结果

```bash
$ pytest backend/test/unit/security/test_input_validation.py -v

============================= test session starts ==============================
collected 5 items

test_input_validation.py::test_parameter_create_requires_valid_name PASSED [ 20%]
test_input_validation.py::test_event_create_requires_valid_fields PASSED [ 40%]
test_input_validation.py::test_json_path_validation PASSED [ 60%]
test_input_validation.py::test_xss_prevention_in_parameter_name PASSED [ 80%]
test_input_validation.py::test_xss_prevention_in_event_name PASSED [100%]

======================= 5 passed, 22 warnings in 14.57s =====================
```

### 测试覆盖

| 测试用例 | 输入 | 期望错误 | 状态 |
|---------|------|---------|------|
| 空参数名 | `param_name=""` | `param_name不能为空` | ✅ |
| 包含空格 | `param_name="user name"` | `param_name不能包含空格` | ✅ |
| 仅空格 | `param_name="   "` | `param_name不能为空` | ✅ |
| 空事件名 | `event_name=""` | `event_name不能为空` | ✅ |
| 事件名含空格 | `event_name="test event"` | `event_name不能包含空格` | ✅ |
| JSON路径格式 | `json_path="invalid"` | `json_path必须以'$.'开头` | ✅ |
| XSS防护 | `param_name_cn="<script>"` | HTML转义 | ✅ |

---

## 技术要点

### Pydantic验证器模式

**`mode="after"` (默认)**:
- Field验证 → 自定义验证器
- 用于: 对已验证的值进行后处理

**`mode="before"` (本次使用)**:
- 自定义验证器 → Field验证
- 用于: 自定义验证逻辑优先执行

**`pre=True` (V1语法，已废弃)**:
- 等同于V2的`mode="before"`

### 验证器迁移指南

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

---

## 影响范围

### 修改文件

- ✅ `/Users/mckenzie/Documents/event2table/backend/models/schemas.py`

### 影响的Schema

1. **EventParameterBase**: `param_name` 验证器
2. **EventBase**: `event_name` 验证器

### 不影响的功能

- ✅ 其他验证器保持不变（继续使用`@validator`）
- ✅ Field约束继续有效（`min_length`, `max_length`等）
- ✅ 业务逻辑无变化
- ✅ API行为无变化（仅错误消息更清晰）

---

## 验证清单

- [x] 测试全部通过（5/5）
- [x] 自定义错误消息正确显示
- [x] 验证器执行顺序正确
- [x] 无破坏性变更
- [x] 代码符合Pydantic V2规范
- [x] XSS防护功能保留

---

## 经验总结

### 问题模式

**症状**: Pydantic自定义验证器不执行，显示Field默认错误消息

**原因**: Field验证在自定义验证器之前执行

**解决方案**: 使用`@field_validator(mode="before")`

### 预防措施

1. **优先使用`mode="before"`**: 当需要自定义验证逻辑时
2. **测试验证顺序**: 确保自定义验证器有机会执行
3. **清晰的错误消息**: 自定义消息比默认消息更有用
4. **Pydantic V2迁移**: 从`@validator(pre=True)`迁移到`@field_validator(mode="before")`

### 相关文档

- [Pydantic V2 迁移指南](https://errors.pydantic.dev/2.12/migration/)
- [Field Validators](https://docs.pydantic.dev/latest/concepts/validators/#field-validators)
- [项目CLAUDE.md - GraphQL类型同步规范](/Users/mckenzie/Documents/event2table/CLAUDE.md#graphql类型同步规范-⚠️-极其重要---2026-03-08新增)

---

## 下一步建议

### P0 - 立即执行

- [x] 修复P0-8验证器执行顺序问题 ✅

### P1 - 尽快执行

- [ ] 迁移所有`@validator(pre=True)`到`@field_validator(mode="before")`
- [ ] 更新项目文档，说明验证器最佳实践
- [ ] 添加验证器执行顺序测试

### P2 - 可选优化

- [ ] 统一所有验证器使用`@field_validator`（Pydantic V2规范）
- [ ] 移除V1风格的`@validator`导入
- [ ] 添加更多的自定义验证场景测试

---

**修复完成时间**: 2026-03-09
**修复验证**: ✅ 所有测试通过
**TDD状态**: ✅ RED → GREEN 完成
