# GraphQL DataLoader 快速参考

**版本**: 1.0 | **最后更新**: 2026-03-07

---

## 🚀 快速开始

### 在 Resolver 中使用 DataLoader

```python
# ✅ 正确：使用 DataLoader 批量加载
from backend.gql_api.dataloaders.parameter_loader_enhanced import get_parameter_loader_enhanced

def resolve_parameters(root, info, event_id: int):
    loader = get_parameter_loader_enhanced()
    params = loader.load_by_event(event_id)
    return [ParameterType.from_dict(p) for p in params]

# ❌ 错误：直接查询数据库（N+1 问题）
def resolve_parameters(root, info, event_id: int):
    return fetch_all_as_dict(
        "SELECT * FROM event_params WHERE event_id = ?",
        (event_id,)
    )
```

---

## 📦 可用的 DataLoader

| DataLoader | 用途 | 导入路径 |
|------------|------|----------|
| **EventLoader** | 批量加载游戏的事件 | `optimized_loaders.get_event_loader()` |
| **ParameterLoader** | 批量加载事件的参数 | `optimized_loaders.get_parameter_loader()` |
| **GameLoader** | 批量加载游戏数据 | `optimized_loaders.get_game_loader()` |
| **ParameterLoaderEnhanced** | 增强的参数加载器（含模板） | `parameter_loader_enhanced.get_parameter_loader_enhanced()` |

---

## 🎯 使用场景

### 场景 1: 事件列表 + 参数数量

```graphql
query {
  events(game_gid: 10000147, limit: 100) {
    id
    event_name
    param_count  # ✅ DataLoader 批量加载
  }
}
```

**查询次数**: 2 次（1 次事件 + 1 次批量参数）

---

### 场景 2: 多个事件的参数

```graphql
query {
  event1: event(id: 1) {
    parameters { id param_name }
  }
  event2: event(id: 2) {
    parameters { id param_name }
  }
  event3: event(id: 3) {
    parameters { id param_name }
  }
}
```

**查询次数**: 4 次（3 次事件 + 1 次批量参数）

---

### 场景 3: 参数过滤

```python
def resolve_parameters(root, info, event_id: int, active_only: bool = True):
    loader = get_parameter_loader_enhanced()
    params = loader.load_by_event(event_id)

    # 过滤活跃参数
    if active_only and params:
        params = [p for p in params if p.get('is_active', 0) == 1]

    return [ParameterType.from_dict(p) for p in params]
```

---

## 🔧 自定义 DataLoader

### 创建自定义 DataLoader

```python
from promise.dataloader import DataLoader
from promise import Promise
from typing import List, Dict

class MyCustomLoader(DataLoader):
    def __init__(self):
        super().__init__(load_fn=self._batch_load)

    def _batch_load(self, keys: List[int]) -> Promise:
        # 批量查询数据库
        placeholders = ','.join('?' * len(keys))
        results = fetch_all_as_dict(
            f"SELECT * FROM my_table WHERE id IN ({placeholders})",
            tuple(keys)
        )

        # 按键分组
        results_map = {r['id']: r for r in results}

        # 按请求顺序返回
        return Promise.resolve([results_map.get(k) for k in keys])

# 使用全局函数访问
_my_custom_loader = None

def get_my_custom_loader() -> MyCustomLoader:
    global _my_custom_loader
    if _my_custom_loader is None:
        _my_custom_loader = MyCustomLoader()
    return _my_custom_loader
```

---

## 📊 性能对比

### 优化前 vs 优化后

| 场景 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 100 个事件 + param_count | 101 次查询 | 2 次查询 | 98% ↓ |
| 10 个事件的参数 | 10 次查询 | 1 次查询 | 90% ↓ |
| 100 个字段的 usage | 200 次查询 | 0 次查询 | 100% ↓ |

---

## ⚠️ 常见错误

### 错误 1: 在循环中使用 DataLoader

```python
# ❌ 错误：循环中使用 DataLoader（无法批量）
for event_id in event_ids:
    loader = get_parameter_loader_enhanced()
    params = loader.load_by_event(event_id)  # 每次单独查询

# ✅ 正确：批量加载
loader = get_parameter_loader_enhanced()
params_list = loader.load_by_events(event_ids)  # 一次批量查询
```

### 错误 2: 直接返回 Promise

```python
# ❌ 错误：直接返回 Promise 对象
def resolve_parameters(root, info, event_id: int):
    loader = get_parameter_loader_enhanced()
    return loader.load(event_id)  # 返回 Promise

# ✅ 正确：GraphQL 自动解析 Promise
def resolve_parameters(root, info, event_id: int):
    loader = get_parameter_loader_enhanced()
    params = loader.load(event_id)
    return [ParameterType.from_dict(p) for p in params]
```

### 错误 3: 忽略缓存

```python
# ❌ 错误：每次创建新实例（无缓存）
def resolve_parameters(root, info, event_id: int):
    loader = ParameterLoaderEnhanced()  # 新实例，无缓存
    return loader.load_by_event(event_id)

# ✅ 正确：使用全局函数（有缓存）
def resolve_parameters(root, info, event_id: int):
    loader = get_parameter_loader_enhanced()  # 单例，有缓存
    return loader.load_by_event(event_id)
```

---

## 🔍 调试技巧

### 启用 SQL 查询日志

```python
# 在 web_app.py 中添加
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### 验证 DataLoader 批量加载

```python
# 在 DataLoader 中添加日志
class ParameterLoaderEnhanced(DataLoader):
    def _batch_load_parameters(self, event_ids: List[int]) -> Promise:
        logger.info(f"DataLoader: 批量加载 {len(event_ids)} 个事件的参数")
        # ... 批量查询逻辑
```

### 检查缓存命中率

```python
# 在 CachedDataLoader 中添加日志
def _batch_load_with_cache(self, keys, batch_load_fn, ...):
    cached_count = len([k for k in keys if cache.get(k)])
    logger.info(f"DataLoader: 缓存命中 {cached_count}/{len(keys)}")
    # ... 缓存逻辑
```

---

## 📚 相关文档

- **详细优化报告**: [GRAPHQL-DATALOADER-OPTIMIZATION-REPORT.md](GRAPHQL-DATALOADER-OPTIMIZATION-REPORT.md)
- **测试指南**: [GRAPHQL-DATALOADER-TEST-GUIDE.md](GRAPHQL-DATALOADER-TEST-GUIDE.md)
- **执行总结**: [GRAPHQL-DATALOADER-OPTIMIZATION-SUMMARY.md](GRAPHQL-DATALOADER-OPTIMIZATION-SUMMARY.md)

---

## 🎓 最佳实践

### 何时使用 DataLoader

✅ **推荐使用**:
- GraphQL 查询中的一对多关系
- 批量加载同类对象
- 存在 N+1 查询问题

❌ **不推荐使用**:
- 查询单个对象
- 数据量很小（< 10 条）
- 已经用 JOIN 优化的查询

### 缓存策略

**L1 缓存（60s）**: 单个请求内快速访问
**L2 缓存（300s）**: 跨请求共享

### 性能目标

- **事件列表查询**: < 500ms
- **参数批量查询**: < 300ms
- **游戏列表查询**: < 200ms

---

**快速参考版本**: 1.0
**最后更新**: 2026-03-07
