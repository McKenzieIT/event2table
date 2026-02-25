# 缓存系统架构图

## 修复前（循环依赖）

```mermaid
graph TD
    A[cache_hierarchical.py] -->|imports| B[cache_system.py]
    B -.->|implicit dependency| A

    style A fill:#ffcccc
    style B fill:#ffcccc

    classDef bad fill:#ffcccc,stroke:#ff0000,stroke-width:2px
    class A,B bad
```

**问题**: 两个模块相互依赖，导致初始化顺序敏感

## 修复后（清晰分层）

```mermaid
graph TD
    A[cache_hierarchical.py] -->|imports| C[base.py]
    B[cache_system.py] -->|imports| C[base.py]

    style C fill:#ccffcc
    style A fill:#ccccff
    style B fill:#ccccff

    classDef base fill:#ccffcc,stroke:#00cc00,stroke-width:2px
    classDef impl fill:#ccccff,stroke:#0000cc,stroke-width:2px
    class C base
    class A,B impl
```

**优势**:
- 清晰的依赖方向（高层→低层）
- 无循环依赖
- 符合依赖倒置原则

## 模块职责

### Level 0: base.py (基础层)

```mermaid
classDiagram
    class CacheInterface {
        <<abstract>>
        +get(key) Optional~Any~
        +set(key, value, ttl) bool
        +delete(key) bool
        +clear() bool
        +get_stats() Dict
    }

    class BaseCache {
        <<abstract>>
        -name: str
        -_stats: Dict
        +get_stats() Dict
        +_record_hit()
        +_record_miss()
        +_record_set()
        +_record_delete()
    }

    class CacheKeyBuilder {
        <<utility>>
        +PREFIX: str
        +build(pattern, **kwargs) str
        +build_pattern(pattern, **kwargs) str
    }

    class CacheException {
        <<exception>>
    }

    CacheInterface <|-- BaseCache
    CacheException <|-- CacheKeyError
    CacheException <|-- CacheValueError
    CacheException <|-- CacheConnectionError
```

### Level 1: cache_system.py (实现层)

```mermaid
classDiagram
    class HierarchicalCache {
        -l1_cache: Dict
        -l2_cache: Redis
        +get(pattern, **kwargs)
        +set(pattern, data, ttl, **kwargs)
        +delete(pattern, **kwargs)
        +invalidate_pattern(pattern, **kwargs)
    }

    class CacheInvalidator {
        -cache: HierarchicalCache
        +invalidate(pattern, **kwargs)
        +invalidate_pattern(pattern, **kwargs)
        +invalidate_batch(patterns)
    }

    BaseCache <|-- HierarchicalCache
    CacheInvalidator --> HierarchicalCache
```

### Level 2: cache_hierarchical.py (高级实现层)

```mermaid
classDiagram
    class HierarchicalCache {
        -l1_cache: Dict
        -l2_cache: Redis
        -_rw_lock: ReadWriteLock
        -_bloom_filter: BloomFilter
        -_degradation_manager: DegradationManager
        +get(pattern, **kwargs)
        +set(pattern, data, **kwargs)
        +invalidate(pattern, **kwargs)
        +invalidate_pattern(pattern, **kwargs)
    }

    BaseCache <|-- HierarchicalCache
```

## 依赖关系图

```mermaid
graph LR
    subgraph "应用层"
        APP[API Routes / Services]
    end

    subgraph "缓存实现层"
        CS[cache_system.py]
        CH[cache_hierarchical.py]
    end

    subgraph "基础层"
        BASE[base.py]
    end

    APP --> CS
    APP --> CH
    CS --> BASE
    CH --> BASE

    style APP fill:#ffffcc
    style BASE fill:#ccffcc
```

## 导入示例

### 推荐方式（从base导入）

```python
# ✅ 推荐：从base.py导入工具类
from backend.core.cache.base import CacheKeyBuilder, get_cache

# ✅ 推荐：从具体模块导入实现
from backend.core.cache.cache_system import HierarchicalCache
from backend.core.cache.cache_hierarchical import cached_hierarchical

# ✅ 推荐：从包导入（使用__init__.py）
from backend.core.cache import (
    CacheKeyBuilder,
    HierarchicalCache,
    cached_hierarchical,
    get_cache,
)
```

### 不推荐方式（跨模块导入）

```python
# ❌ 不推荐：从cache_system导入（可能造成混淆）
from backend.core.cache.cache_system import CacheKeyBuilder

# ❌ 禁止：cache_system和cache_hierarchical互相导入
# from backend.core.cache.cache_hierarchical import XXX  # 在cache_system.py中
```

## 类继承关系

```mermaid
classDiagram
    class CacheInterface {
        <<interface>>
    }

    class BaseCache {
        <<abstract>>
    }

    class HierarchicalCache_System {
        -l1_cache: Dict
        -l2_cache: Redis
    }

    class HierarchicalCache_V2 {
        -l1_cache: Dict
        -l2_cache: Redis
        -_rw_lock
        -_bloom_filter
    }

    CacheInterface <|-- BaseCache
    BaseCache <|-- HierarchicalCache_System
    BaseCache <|-- HierarchicalCache_V2
```

## 模块大小对比

| 模块 | 行数 | 类数量 | 函数数量 | 职责 |
|------|------|--------|----------|------|
| base.py | ~150 | 5 | 2 | 基础类和工具 |
| cache_system.py | ~850 | 2 | 8 | 标准实现 |
| cache_hierarchical.py | ~585 | 2 | 6 | 高级实现 |

## 扩展指南

### 添加新的缓存实现

```python
# 1. 创建新文件 backend/core/cache/my_cache.py
from backend.core.cache.base import BaseCache

class MyCustomCache(BaseCache):
    def __init__(self, name: str):
        super().__init__(name)
        # 自定义初始化

    def get(self, key: str):
        self._record_hit()
        # 实现获取逻辑

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        self._record_set()
        # 实现设置逻辑

    # ... 实现其他抽象方法

# 2. 更新 __init__.py
from .my_cache import MyCustomCache

__all__ = [..., 'MyCustomCache']
```

### 添加新的工具函数

```python
# 在 base.py 中添加
def validate_cache_key(key: str) -> bool:
    """验证缓存键是否合法"""
    if not key:
        return False
    if len(key) > 250:
        return False
    return True

# 导出
__all__ = [..., 'validate_cache_key']
```

---

**文档版本**: 1.0.0
**最后更新**: 2026-02-24
**维护者**: Event2Table Development Team
