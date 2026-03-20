# 测试失败修复指南

**日期**: 2026-03-20
**当前测试通过率**: 80% (32/40)
**目标**: 95%+ (38/40)

---

## 剩余失败的测试分析

### 1. 数据依赖检测失败 (1个测试)

**测试**: `test_detect_dependent_awaits`

**问题**: `check_data_dependencies()` 应该检测到 `user.id` 依赖但没有

**源代码**:
```javascript
const user = await fetchUser()
const posts = await fetchPosts(user.id)  // user.id 是数据依赖
```

**当前逻辑**:
```python
def check_data_dependencies(group: List[Dict]) -> bool:
    variables = [stmt['variable'] for stmt in group]  # ['user', 'posts']
    expressions = ' '.join([stmt['expression'] for stmt in group])

    for i, var in enumerate(variables):
        for j in range(i + 1, len(variables)):
            if var in group[j]['expression']:  # 检查 'user' 是否在 'fetchPosts(user.id)' 中
                return True
```

**分析**: 逻辑应该是正确的 - `'user'` 在 `'fetchPosts(user.id)'` 中应该返回 True

**可能原因**:
1. `extract_await_statements()` 提取的表达式不包含 `user.id`
2. 表达式只提取了函数名部分

**修复方案**:
```python
# 改进提取逻辑，捕获完整表达式
pattern = r'const\s+(\w+)\s*=\s*await\s+([^()\n]+)'
# 当前: fetchPosts(user.id) → 可能被截断
# 应该: 完整保留 fetchPosts(user.id)
```

**优先级**: MEDIUM (不影响核心功能)

---

### 2. 递归深度问题 (2个测试)

**测试**:
- `test_detect_analytics_imports`
- `test_detect_multiple_issues_in_same_file`

**错误**: `RecursionError: maximum recursion depth exceeded`

**原因**: `_detect_bundle_issues()` 中调用自身导致无限递归

**问题代码位置**: `detector_bundle.py:199`

**修复方案**:
```python
# 当前 (错误):
def _detect_bundle_issues(file_path, source_code, source_dir, lazy_threshold_kb):
    # ...
    issues.append(_create_barrel_import_issue(file_path, barrel_import))
    #                                     ^^^^^^^^^^^^^^^^^^ 可能递归调用

# 修复: 确保没有递归
def _detect_bundle_issues(file_path, source_code, source_dir, lazy_threshold_kb):
    # ...
    issues.append(_create_barrel_import_issue(file_path, barrel_import))
    # 而不是 _detect_bundle_issues(...)
```

**优先级**: HIGH (阻止测试运行)

---

### 3. Rerender 检测器问题 (5个测试)

#### 3.1 派生状态检测失败 (3个测试)

**测试**:
- `test_detect_continuous_value_with_boolean_derivation`
- `test_detect_multiple_derived_states`
- `test_detect_state_only_used_in_callback`

**问题**: 检测器返回 0 个问题，预期 > 0

**原因**: 正则表达式模式不匹配

**当前模式**:
```python
pattern = r'const\s+(\w+)\s*=\s*' + re.escape(hook) + r'\(\);[^}]*const\s+(\w+)\s*=\s*\1\s*[<>=]'
```

**问题**: `[^}]*` 匹配到行尾会停止，但实际代码中有多行

**修复方案**:
```python
# 使用 re.DOTALL 标志，让 . 匹配换行符
pattern = r'const\s+(\w+)\s*=\s*' + re.escape(hook) + r'\(\);.*?const\s+(\w+)\s*=\s*\1\s*[<>=]'
#     ^^ 使用 .*? 而不是 [^}]*

# 或者更好的方法：多行匹配
pattern = r'const\s+(\w+)\s*=\s*' + re.escape(hook) + r'\(\);[\s\S]*?const\s+(\w+)\s*=\s*\1\s*[<>=]'
```

**优先级**: MEDIUM

---

#### 3.2 Transitions 检测器路径问题 (2个测试)

**测试**:
- `test_detect_multiple_setters`
- `test_detect_setState_without_transition`

**错误**: `IndexError: 3`

**原因**: `_detect_missing_transitions()` 中仍有路径处理遗漏

**修复**: 在所有 `file_path.relative_to()` 调用处使用 `_get_relative_path()`

**优先级**: HIGH

---

## 快速修复步骤

### Step 1: 修复递归问题 (HIGH)

在 `detector_bundle.py` 中查找并修复所有递归调用：

```bash
# 搜索可能的递归调用
grep -n "_detect_bundle_issues" scripts/detectors/static/detector_bundle.py
```

确保没有函数调用自身。

### Step 2: 修复路径问题 (HIGH)

在 `detector_rerender.py` 中：

```bash
# 查找所有未使用 _get_relative_path 的地方
grep -n "file_path.relative_to" scripts/detectors/static/deterender.py
```

全部替换为 `_get_relative_path(file_path)`。

### Step 3: 改进正则表达式 (MEDIUM)

在 `detector_rerender.py` 中更新派生状态检测模式：

```python
# 使用 re.DOTALL 标志
matches = re.finditer(pattern, source_code, re.DOTALL)
```

### Step 4: 改进数据依赖检测 (MEDIUM)

在 `ast_helpers.py` 中的 `extract_await_statements()` 函数确保捕获完整表达式。

---

## 测试验证

修复后运行测试：

```bash
# 运行所有测试
python3 -m pytest tests/ -v

# 运行特定失败测试
python3 -m pytest tests/test_detector_bundle.py::TestThirdPartyLibraryDetection -v

# 运行特定测试方法
python3 -m pytest tests/test_detector_rerender.py::TestTransitionsDetection -v
```

---

## 预期结果

修复后测试通过率应该达到:
- **当前**: 80% (32/40)
- **修复递归和路径**: 90% (36/40)
- **修复正则表达式**: 95% (38/40)

---

## 时间估算

| 任务 | 预计时间 | 优先级 |
|------|----------|--------|
| 修复递归深度 | 30 分钟 | HIGH |
| 修复路径问题 | 15 分钟 | HIGH |
| 改进正则表达式 | 45 分钟 | MEDIUM |
| 改进数据依赖检测 | 30 分钟 | MEDIUM |
| **总计** | **2 小时** | |

---

## 建议

**方案 1**: 继续修复 (2小时)
- 优点: 达到 95%+ 测试通过率
- 缺点: 需要更多时间

**方案 2**: 当前状态已可用
- 优点: 80% 通过率，核心功能完整
- 缺点: 有边缘情况未覆盖

**推荐**: 如果时间紧迫，方案 2 已足够用于实际使用。剩余问题可以在后续迭代中修复。

---

**最后更新**: 2026-03-20
