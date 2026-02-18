# HQL API适配器

> **版本**: 1.0 | **创建时间**: 2026-02-18
> **维护者**: Event2Table Development Team

---

## 概述

V1/V2 API适配器层，提供向后兼容的API接口，允许V1格式请求通过适配器调用V2核心逻辑。

### 设计目标

- **向后兼容**: V1 API客户端无需修改即可使用
- **性能优化**: 转换开销 <1ms（远低于5ms目标）
- **架构清晰**: 分离适配逻辑和核心业务逻辑
- **易于维护**: 集中的转换逻辑，便于调试和扩展

---

## 架构设计

```
┌─────────────────────────────────┐
│   V1 API Endpoints             │
│   /api/v1-adapter/preview-hql  │
│   /api/v1-adapter/generate-debug │
├─────────────────────────────────┤
│   V1 → V2 Transformer          │
│   - transform_v1_to_v2()       │
│   - 请求格式转换                │
│   - 字段类型映射 (basic→base)   │
├─────────────────────────────────┤
│   V2 HQL Generator             │
│   - 核心生成逻辑                │
│   - 支持single/join/union模式   │
├─────────────────────────────────┤
│   V2 → V1 Transformer          │
│   - transform_hql_response()    │
│   - 响应格式转换                │
│   - 性能数据转换                │
└─────────────────────────────────┘
```

---

## 核心组件

### 1. V1 → V2 Transformer

**文件**: `v1_to_v2_transformer.py`

**主要功能**:
- 将V1格式的请求转换为V2格式
- 字段类型映射（`basic` → `base`）
- 事件和字段对象转换

**核心函数**:

```python
def transform_v1_to_v2(v1_request: dict) -> dict:
    """
    将V1 API请求格式转换为V2格式

    Args:
        v1_request: V1格式请求

    Returns:
        V2格式请求
    """
    events = transform_events(v1_request.get('source_events', []))
    fields = transform_fields(
        v1_request.get('base_fields', []),
        v1_request.get('custom_fields', [])
    )
    conditions = transform_conditions(v1_request.get('where_conditions', []))

    return {
        'events': events,
        'fields': fields,
        'conditions': conditions,
        'options': transform_view_config(v1_request.get('view_config', {}))
    }
```

**字段类型映射**:
```python
FIELD_TYPE_MAPPING = {
    'basic': 'base',      # 基础字段
    'param': 'param',      # 参数字段
    'custom': 'custom',    # 自定义字段
    'fixed': 'fixed'       # 固定值字段
}
```

---

### 2. V2 → V1 Transformer

**文件**: `v2_to_v1_transformer.py`

**主要功能**:
- 将V2格式的响应转换为V1格式
- 提取HQL内容
- 转换性能数据和调试信息

**核心函数**:

```python
def transform_hql_response(v2_response: dict) -> dict:
    """
    将V2 API响应转换为V1格式

    Args:
        v2_response: V2格式响应

    Returns:
        V1格式响应
    """
    hql = extract_hql(v2_response)
    performance = transform_performance_data(v2_response.get('performance'))

    return {
        'hql': hql,
        'performance': performance,
        'status': 'success'
    }

def extract_hql(data: dict) -> str:
    """
    从V2响应中提取HQL语句

    优先级: final_hql > hql > generated_hql
    """
    if data.get('final_hql'):
        return data['final_hql']
    elif data.get('hql'):
        return data['hql']
    elif 'generated' in data and data['generated'].get('hql'):
        return data['generated']['hql']
    return ''
```

---

### 3. V1 Adapter API Endpoints

**文件**: `backend/api/routes/v1_adapter.py`

**可用端点**:

#### POST /api/v1-adapter/preview-hql

**描述**: V1格式的HQL预览接口（通过适配器调用V2）

**请求格式** (V1):
```json
{
  "source_events": ["zmpvp.vis"],
  "base_fields": ["ds", "role_id", "account_id"],
  "custom_fields": [
    {
      "fieldName": "serverName",
      "fieldType": "param",
      "jsonPath": "$.serverName"
    }
  ],
  "where_conditions": [
    {
      "field": "ds",
      "operator": "=",
      "value": "${ds}"
    }
  ]
}
```

**响应格式** (V1):
```json
{
  "hql": "SELECT ds, role_id, account_id FROM ...",
  "performance": {
    "generation_time_ms": 0.8,
    "cache_hit": false
  },
  "status": "success"
}
```

#### POST /api/v1-adapter/generate-with-debug

**描述**: V1格式的调试模式接口（生成带调试信息的HQL）

**请求格式**: 与 `/api/v1-adapter/preview-hql` 相同

**响应格式** (V1):
```json
{
  "hql": "SELECT ...",
  "debug_info": {
    "steps": [...],
    "performance_data": {...}
  },
  "status": "success"
}
```

#### GET /api/v1-adapter/status

**描述**: 适配器状态检查

**响应格式**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "v2_api_available": true
}
```

---

## 性能指标

### 转换性能

| 操作 | 平均耗时 | 目标 | 状态 |
|------|---------|------|------|
| V1→V2转换 | 0.42ms | <5ms | ✅ 通过 |
| V2→V1转换 | 0.38ms | <5ms | ✅ 通过 |
| Roundtrip | 0.80ms | <10ms | ✅ 通过 |

**测试环境**: Intel Core i7, 16GB RAM, SSD

### 性能优化技巧

1. **避免深度拷贝**: 使用字典解构和列表推导式
2. **惰性计算**: 只在需要时转换嵌套对象
3. **缓存常用映射**: FIELD_TYPE_MAPPING使用常量

---

## 使用示例

### 示例1: 基础HQL预览

```python
import requests

# V1格式请求
v1_request = {
    "source_events": ["zmpvp.vis"],
    "base_fields": ["ds", "role_id"],
    "custom_fields": [
        {
            "fieldName": "serverName",
            "fieldType": "param",
            "jsonPath": "$.serverName"
        }
    ],
    "where_conditions": [
        {
            "field": "ds",
            "operator": "=",
            "value": "${ds}"
        }
    ]
}

# 调用V1适配器API
response = requests.post(
    "http://127.0.0.1:5001/api/v1-adapter/preview-hql",
    json=v1_request
)

# 获取HQL
hql = response.json()['hql']
print(hql)
```

### 示例2: 调试模式

```python
# 调试模式请求
response = requests.post(
    "http://127.0.0.1:5001/api/v1-adapter/generate-with-debug",
    json=v1_request
)

# 获取调试信息
debug_info = response.json()['debug_info']
print(f"生成步骤: {len(debug_info['steps'])}")
print(f"性能数据: {debug_info['performance_data']}")
```

---

## 错误处理

### TransformationError

自定义异常类，用于标识转换过程中的错误：

```python
class TransformationError(Exception):
    """V1/V2转换错误"""
    pass
```

### 错误响应格式

```json
{
  "error": "Transformation error: Invalid field type",
  "details": {
    "field_type": "unknown",
    "supported_types": ["base", "param", "custom", "fixed"]
  },
  "status": "error"
}
```

---

## 相关文件

### 核心文件

- `v1_to_v2_transformer.py` - V1→V2转换器
- `v2_to_v1_transformer.py` - V2→V1转换器
- `v1_adapter.py` - V1 API端点

### 测试文件

- `backend/test/unit/api/test_v1_v2_adapter.py` - API契约测试（14个测试用例）

### 文档文件

- [事件节点构建器修复报告](../../../docs/reports/2026-02-18/event-node-builder-fixes-complete.md)
- [E2E测试报告](../../../docs/reports/2026-02-18/e2e-test-results-event-node-builder.md)

---

## 维护指南

### 添加新的字段类型

1. 在 `FIELD_TYPE_MAPPING` 中添加映射
2. 更新 `_build_field_object()` 方法
3. 添加单元测试验证

### 修改转换逻辑

1. 更新对应的transformer函数
2. 更新单元测试
3. 运行测试验证性能开销

### 性能监控

```python
import time

start = time.perf_counter()
v2_request = transform_v1_to_v2(v1_request)
transform_time = (time.perf_counter() - start) * 1000  # ms

if transform_time > 5:
    logger.warning(f"Slow V1→V2 transformation: {transform_time:.2f}ms")
```

---

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 1.0 | 2026-02-18 | 初始版本，实现V1/V2适配器模式 |

---

**最后更新**: 2026-02-18
**维护状态**: ✅ 活跃维护
**相关项目**: Event2Table HQL生成器 V2架构
