# GraphQL DataLoader 优化测试指南

**日期**: 2026-03-07
**目的**: 验证 DataLoader 优化的正确性和性能提升

---

## 测试环境准备

### 1. 启动后端服务器

```bash
# 激活虚拟环境
source backend/venv/bin/activate

# 启动 Flask 服务器
python web_app.py
```

**预期输出**:
```
 * Running on http://127.0.0.1:5001
 * Restarting with stat
 * Debugger is active!
```

### 2. 启用 SQL 查询日志

**编辑 `web_app.py`**:
```python
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

这将显示所有 SQL 查询，便于验证优化效果。

### 3. 准备测试数据

确保数据库中有足够的测试数据：
- 至少 10 个游戏
- 每个游戏至少 20 个事件
- 每个事件至少 5 个参数

```bash
# 验证数据量
sqlite3 data/dwd_generator.db "
SELECT
    (SELECT COUNT(*) FROM games) as game_count,
    (SELECT COUNT(*) FROM log_events) as event_count,
    (SELECT COUNT(*) FROM event_params) as param_count;
"
```

---

## 测试场景

### 测试 1: 事件列表查询（无 N+1）

**目标**: 验证查询事件列表时不会触发 N+1 查询

**GraphQL 查询**:
```graphql
query TestEventListNoN1 {
  events(game_gid: 10000147, limit: 50) {
    id
    event_name
    event_name_cn
    category_name
    param_count
  }
}
```

**预期结果**:
- ✅ 返回 50 个事件
- ✅ 每个事件包含正确的 `param_count`
- ✅ SQL 日志显示 **只有 2 次查询**:
  1. 查询事件列表
  2. 批量查询所有事件的参数

**验证 SQL 日志**:
```sql
-- 查询 1: 获取事件列表
SELECT le.*, g.gid, g.name, ec.name
FROM log_events le
LEFT JOIN games g ON le.game_gid = g.gid
LEFT JOIN event_categories ec ON le.category_id = ec.id
WHERE le.game_gid = ? LIMIT 50;

-- 查询 2: 批量加载参数
SELECT ep.*
FROM event_params ep
WHERE ep.event_id IN (?, ?, ..., ?)  -- 50 个 event_id
ORDER BY ep.event_id, ep.id;
```

**性能指标**:
- 查询时间: < 500ms
- SQL 查询次数: 2 次

**❌ 如果失败**:
- SQL 日志显示 51+ 次查询
- 查询时间 > 2 秒

---

### 测试 2: 参数批量加载

**目标**: 验证查询多个事件的参数时使用批量加载

**GraphQL 查询**:
```graphql
query TestParameterBatchLoading {
  event1: event(id: 1) {
    id
    event_name
    parameters {
      id
      param_name
      param_type
    }
  }
  event2: event(id: 2) {
    id
    event_name
    parameters {
      id
      param_name
      param_type
    }
  }
  event3: event(id: 3) {
    id
    event_name
    parameters {
      id
      param_name
      param_type
    }
  }
}
```

**预期结果**:
- ✅ 返回 3 个事件及其参数
- ✅ SQL 日志显示 **只有 1 次批量参数查询**

**验证 SQL 日志**:
```sql
-- 查询 1: 获取事件（3 次，可接受）
SELECT ... FROM log_events WHERE id = ?;
SELECT ... FROM log_events WHERE id = ?;
SELECT ... FROM log_events WHERE id = ?;

-- 查询 2: 批量加载所有参数
SELECT ep.*, pt.name, pt.description
FROM event_params ep
LEFT JOIN param_templates pt ON ep.template_id = pt.id
WHERE ep.event_id IN (1, 2, 3)
ORDER BY ep.event_id, ep.id;
```

**性能指标**:
- 查询时间: < 300ms
- SQL 查询次数: 4 次（3 次事件 + 1 次批量参数）

**❌ 如果失败**:
- SQL 日志显示 6+ 次查询（每个事件单独查询参数）

---

### 测试 3: 游戏列表查询（已优化）

**目标**: 验证游戏列表查询使用 JOIN 优化（无需 DataLoader）

**GraphQL 查询**:
```graphql
query TestGameListOptimized {
  games(limit: 10) {
    gid
    name
    event_count
    parameter_count
  }
}
```

**预期结果**:
- ✅ 返回 10 个游戏
- ✅ 每个游戏包含正确的 `event_count` 和 `parameter_count`
- ✅ SQL 日志显示 **只有 1 次查询**（使用 JOIN）

**验证 SQL 日志**:
```sql
-- 查询 1: 单次查询，使用 JOIN
SELECT
    g.*,
    COUNT(DISTINCT le.id) as event_count,
    COUNT(DISTINCT CASE WHEN ep.is_active = 1 THEN ep.id END) as param_count
FROM games g
LEFT JOIN log_events le ON le.game_gid = g.gid
LEFT JOIN event_params ep ON ep.event_id = le.id
GROUP BY g.id
LIMIT 10;
```

**性能指标**:
- 查询时间: < 200ms
- SQL 查询次数: 1 次

**❌ 如果失败**:
- SQL 日志显示 11+ 次查询
- `event_count` 或 `parameter_count` 值为 0 或不正确

---

### 测试 4: 参数过滤查询

**目标**: 验证 `active_only` 过滤功能正常工作

**GraphQL 查询**:
```graphql
query TestParameterFiltering {
  parameters_active: parameters(event_id: 1, active_only: true) {
    id
    param_name
    is_active
  }
  parameters_all: parameters(event_id: 1, active_only: false) {
    id
    param_name
    is_active
  }
}
```

**预期结果**:
- ✅ `parameters_active` 只返回 `is_active=1` 的参数
- ✅ `parameters_all` 返回所有参数
- ✅ SQL 日志显示 **只有 1 次批量查询**（DataLoader 缓存）

**验证点**:
```python
# 伪代码验证
assert len(parameters_active) <= len(parameters_all)
assert all(p.is_active for p in parameters_active)
```

---

### 测试 5: DataLoader 缓存验证

**目标**: 验证 DataLoader 缓存正常工作

**GraphQL 查询**:
```graphql
query TestDataLoaderCache {
  # 第一次查询：从数据库加载
  events1: events(game_gid: 10000147, limit: 10) {
    id
    param_count
  }

  # 第二次查询：从缓存加载（同一请求内）
  events2: events(game_gid: 10000147, limit: 10) {
    id
    param_count
  }
}
```

**预期结果**:
- ✅ 两次查询返回相同结果
- ✅ SQL 日志显示 **只有 2 次查询**（第二次使用缓存）

**验证点**:
```python
# 伪代码验证
assert events1 == events2
# SQL 日志应该只有 2 次查询，而不是 4 次
```

---

### 测试 6: 并发查询验证

**目标**: 验证 DataLoader 在并发查询场景下的正确性

**GraphQL 查询**:
```graphql
query TestConcurrentQueries {
  game1: game(gid: 10000147) {
    gid
    name
  }
  game2: game(gid: 10000148) {
    gid
    name
  }
  events1: events(game_gid: 10000147, limit: 10) {
    id
    event_name
  }
  events2: events(game_gid: 10000148, limit: 10) {
    id
    event_name
  }
}
```

**预期结果**:
- ✅ 所有查询返回正确结果
- ✅ 无 GraphQL 错误
- ✅ 查询时间 < 1 秒

---

## 性能基准测试

### 基准测试脚本

**创建 `test_graphql_performance.py`**:
```python
import requests
import time
from typing import Dict, List

GRAPHQL_URL = "http://127.0.0.1:5001/api/graphql"

def execute_graphql_query(query: str, variables: Dict = None) -> Dict:
    """执行 GraphQL 查询"""
    start_time = time.time()

    response = requests.post(
        GRAPHQL_URL,
        json={"query": query, "variables": variables},
        headers={"Content-Type": "application/json"}
    )

    end_time = time.time()

    return {
        "data": response.json(),
        "duration_ms": (end_time - start_time) * 1000,
        "status_code": response.status_code
    }

def benchmark_event_list_query(limit: int = 100) -> Dict:
    """基准测试：事件列表查询"""
    query = f"""
    query {{
      events(game_gid: 10000147, limit: {limit}) {{
        id
        event_name
        param_count
      }}
    }}
    """

    result = execute_graphql_query(query)
    event_count = len(result["data"].get("data", {}).get("events", []))

    return {
        "test_name": f"Event List Query ({limit} events)",
        "event_count": event_count,
        "duration_ms": result["duration_ms"],
        "status_code": result["status_code"]
    }

def benchmark_parameter_batch_query(event_ids: List[int]) -> Dict:
    """基准测试：参数批量查询"""
    fields = "\n    ".join([
        f"event{i}: event(id: {eid}) {{ id parameters {{ id param_name }} }}"
        for i, eid in enumerate(event_ids)
    ])

    query = f"""
    query {{
      {fields}
    }}
    """

    result = execute_graphql_query(query)

    return {
        "test_name": f"Parameter Batch Query ({len(event_ids)} events)",
        "event_count": len(event_ids),
        "duration_ms": result["duration_ms"],
        "status_code": result["status_code"]
    }

if __name__ == "__main__":
    print("=" * 60)
    print("GraphQL DataLoader 性能基准测试")
    print("=" * 60)

    # 测试 1: 事件列表查询
    print("\n测试 1: 事件列表查询")
    result1 = benchmark_event_list_query(limit=100)
    print(f"  - 查询时间: {result1['duration_ms']:.2f} ms")
    print(f"  - 返回事件数: {result1['event_count']}")
    print(f"  - 状态: {'✅ PASS' if result1['duration_ms'] < 500 else '❌ FAIL'}")

    # 测试 2: 参数批量查询
    print("\n测试 2: 参数批量查询")
    result2 = benchmark_parameter_batch_query(event_ids=[1, 2, 3, 4, 5])
    print(f"  - 查询时间: {result2['duration_ms']:.2f} ms")
    print(f"  - 查询事件数: {result2['event_count']}")
    print(f"  - 状态: {'✅ PASS' if result2['duration_ms'] < 300 else '❌ FAIL'}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
```

**运行测试**:
```bash
python test_graphql_performance.py
```

**预期输出**:
```
====================================================
GraphQL DataLoader 性能基准测试
====================================================

测试 1: 事件列表查询
  - 查询时间: 234.56 ms
  - 返回事件数: 100
  - 状态: ✅ PASS

测试 2: 参数批量查询
  - 查询时间: 123.45 ms
  - 查询事件数: 5
  - 状态: ✅ PASS

====================================================
测试完成
====================================================
```

---

## 回归测试

### 功能完整性检查

**验证所有 GraphQL 查询仍然正常工作**:

```graphql
# 1. 游戏查询
query {
  game(gid: 10000147) {
    gid
    name
    event_count
  }
}

# 2. 事件查询
query {
  event(id: 1) {
    id
    event_name
    param_count
  }
}

# 3. 参数查询
query {
  parameters(event_id: 1, active_only: true) {
    id
    param_name
    param_type
  }
}

# 4. 搜索功能
query {
  search_events(query: "login", game_gid: 10000147) {
    id
    event_name
  }
}
```

**验证点**:
- ✅ 所有查询返回正确数据
- ✅ 无 GraphQL 错误
- ✅ 无 Python 异常

---

## 故障排查

### 问题 1: DataLoader 未生效

**症状**: SQL 日志仍显示 N+1 查询

**检查**:
```python
# 1. 确认 DataLoader 已导入
from backend.gql_api.dataloaders.parameter_loader_enhanced import get_parameter_loader_enhanced

# 2. 确认 resolver 使用了 DataLoader
def resolve_parameters(root, info, event_id: int):
    loader = get_parameter_loader_enhanced()  # ✅ 使用 DataLoader
    return loader.load_by_event(event_id)
```

**解决方案**:
- 确保 resolver 使用 `get_parameter_loader_enhanced()`
- 检查导入路径是否正确

### 问题 2: Promise 对象未解析

**症状**: GraphQL 返回 `Promise` 对象而非实际数据

**检查**:
```python
# ❌ 错误：直接返回 Promise
def resolve_parameters(root, info, event_id: int):
    loader = get_parameter_loader_enhanced()
    return loader.load(event_id)  # 返回 Promise 对象

# ✅ 正确：GraphQL 会自动解析 Promise
def resolve_parameters(root, info, event_id: int):
    loader = get_parameter_loader_enhanced()
    params = loader.load(event_id)
    return [ParameterType.from_dict(p) for p in params]
```

### 问题 3: 缓存未生效

**症状**: 同一请求内多次查询相同数据，缓存未命中

**检查**:
```python
# 确认使用同一个 DataLoader 实例
loader1 = get_parameter_loader_enhanced()
loader2 = get_parameter_loader_enhanced()

assert loader1 is loader2  # 应该是同一个实例
```

---

## 测试检查清单

### 必须通过的测试

- [ ] **测试 1**: 事件列表查询（无 N+1）
  - [ ] 返回正确数据
  - [ ] SQL 查询次数 = 2
  - [ ] 查询时间 < 500ms

- [ ] **测试 2**: 参数批量加载
  - [ ] 返回正确数据
  - [ ] SQL 查询次数 = 4（3 次事件 + 1 次批量参数）
  - [ ] 查询时间 < 300ms

- [ ] **测试 3**: 游戏列表查询（已优化）
  - [ ] 返回正确数据
  - [ ] SQL 查询次数 = 1
  - [ ] 查询时间 < 200ms

- [ ] **测试 4**: 参数过滤查询
  - [ ] `active_only=true` 只返回活跃参数
  - [ ] `active_only=false` 返回所有参数
  - [ ] 缓存正常工作

- [ ] **测试 5**: DataLoader 缓存验证
  - [ ] 同一请求内复用缓存
  - [ ] 缓存命中日志显示

- [ ] **测试 6**: 并发查询验证
  - [ ] 所有查询返回正确数据
  - [ ] 无 GraphQL 错误
  - [ ] 查询时间 < 1 秒

### 可选的性能测试

- [ ] **基准测试**: 事件列表查询（100 个事件）
  - [ ] 查询时间 < 500ms
  - [ ] 性能提升 > 80%

- [ ] **基准测试**: 参数批量查询（10 个事件）
  - [ ] 查询时间 < 300ms
  - [ ] 性能提升 > 90%

---

## 测试报告模板

**测试日期**: YYYY-MM-DD
**测试人员**: [Your Name]
**测试环境**: [Development/Staging/Production]

### 测试结果摘要

| 测试项 | 状态 | 查询次数 | 查询时间 | 备注 |
|--------|------|----------|----------|------|
| 事件列表查询 | ✅/❌ | 2 | 234ms | - |
| 参数批量加载 | ✅/❌ | 4 | 123ms | - |
| 游戏列表查询 | ✅/❌ | 1 | 89ms | - |
| 参数过滤查询 | ✅/❌ | 1 | 45ms | - |
| DataLoader 缓存 | ✅/❌ | - | - | - |
| 并发查询 | ✅/❌ | - | 567ms | - |

### 发现的问题

1. [问题描述]
   - 复现步骤: ...
   - 预期结果: ...
   - 实际结果: ...
   - 严重程度: P0/P1/P2

### 建议和改进

1. [建议内容]
   - 优先级: P0/P1/P2
   - 预期收益: ...

---

**测试指南版本**: 1.0
**最后更新**: 2026-03-07
