# 缓存系统模块依赖关系图

## 当前架构（存在问题）

```
┌─────────────────────────────────────────────────────────────────┐
│                      backend/core/cache/                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────┐        ┌──────────────────────┐      │
│  │  cache_system.py     │        │ cache_hierarchical.py│      │
│  │  (922 lines)         │        │  (585 lines)         │      │
│  ├──────────────────────┤        ├──────────────────────┤      │
│  │ - HierarchicalCache  │◄───────│ - HierarchicalCache  │      │
│  │ - CacheKeyBuilder    │ 重复   │ - _match_pattern()   │      │
│  │ - CacheInvalidator   │  60-70%│ - _set_l1()         │      │
│  │ - _match_pattern()   │        │ - get_stats()        │      │
│  └─────────┬────────────┘        └──────────┬───────────┘      │
│            │                                │                   │
│            │ imports                        │ imports           │
│            ▼                                ▼                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              子系统模块 (依赖混乱)                        │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │  decorators.py  → imports from cache_system             │   │
│  │  invalidator.py → imports from cache_system             │   │
│  │  statistics.py  → imports from cache_system             │   │
│  │  degradation.py → imports from cache_hierarchical       │   │
│  │  intelligent_warmer.py → imports from cache_hierarchical│   │
│  │  monitoring.py  → no direct dependency                  │   │
│  │  capacity_monitor.py → no direct dependency             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

问题：
1. ❌ 两个HierarchicalCache类重复（60-70%代码重复）
2. ❌ 循环依赖：cache_hierarchical → cache_system → cache_hierarchical
3. ❌ 导入混乱：有些从cache_system导入，有些从cache_hierarchical导入
```

---

## 目标架构（修复后）

```
┌─────────────────────────────────────────────────────────────────┐
│               backend/core/cache/ (重构后)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────┐                                       │
│  │   base.py (新增)     │  基础接口和工具                       │
│  ├──────────────────────┤                                       │
│  │ - ICache            │  缓存接口                              │
│  │ - IHierarchicalCache│  分层缓存接口                          │
│  │ - CacheKeyBuilder   │  键生成器（移到这里）                  │
│  │ - ICacheMonitor     │  监控接口                              │
│  └─────────┬───────────┘                                       │
│            │                                                 │
│            │ imports (所有模块从这里导入基础)                  │
│            ▼                                                 │
│  ┌──────────────────────┐                                       │
│  │  cache_system.py     │  核心实现（保留）                      │
│  ├──────────────────────┤                                       │
│  │ - HierarchicalCache  │  统一实现（合并两个版本）              │
│  │ - CacheInvalidator   │  失效器                                │
│  └─────────┬───────────┘                                       │
│            │                                                 │
│            │ 依赖注入（不使用全局实例）                        │
│            ▼                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           子系统模块 (清晰的依赖层次)                     │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │  Layer 1: 增强功能                                        │   │
│  │  ├─ consistency.py       (读写锁)                         │   │
│  │  ├─ bloom_filter_enhanced.py (布隆过滤器)                 │   │
│  │  └─ degradation.py       (降级策略)                       │   │
│  │                                                           │   │
│  │  Layer 2: 监控和管理                                      │   │
│  │  ├─ monitoring.py         (告警系统)                      │   │
│  │  ├─ capacity_monitor.py  (容量监控)                      │   │
│  │  └─ intelligent_warmer.py (智能预热)                     │   │
│  │                                                           │   │
│  │  Layer 3: 工具和装饰器                                    │   │
│  │  ├─ decorators.py         (装饰器)                        │   │
│  │  ├─ invalidator.py        (失效器)                        │   │
│  │  └─ statistics.py         (统计)                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────┐                                       │
│  │  container.py (新增)  │  依赖注入容器                        │
│  ├──────────────────────┤                                       │
│  │ - CacheContainer     │  管理所有组件                         │
│  │ - init_cache()       │  初始化函数                          │
│  │ - get_cache()        │  获取实例                            │
│  └──────────────────────┘                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

改进：
1. ✅ 单一HierarchicalCache实现（消除重复）
2. ✅ 清晰的依赖层次（无循环依赖）
3. ✅ 统一的基础接口（base.py）
4. ✅ 依赖注入（container.py）
```

---

## 循环依赖详情

### 问题1: cache_hierarchical ↔ cache_system

```
cache_hierarchical.py (line 24)
    ↓ imports
cache_system.py (CacheKeyBuilder, get_cache)
    ↓ global instance
hierarchical_cache = HierarchicalCache() (line 750)
    ↓ 实际使用时可能
cache_hierarchical.py (如果使用cache_system的实例)

循环路径：
cache_hierarchical → cache_system → (通过实例) → cache_hierarchical
```

### 问题2: 子系统间的混乱依赖

```
degradation.py (line 25)
    ↓ imports
cache_hierarchical.py (hierarchical_cache)
    ↓ imports
cache_system.py (CacheKeyBuilder, get_cache)
    ↓
degradation.py (间接依赖)

intelligent_warmer.py (line 27)
    ↓ imports
cache_hierarchical.py (hierarchical_cache)
    ↓ imports
cache_system.py (CacheKeyBuilder, get_cache)
    ↓
intelligent_warmer.py (间接依赖)
```

### 解决方案

```
方案1: 提取公共基础
base.py
  ↑
  ├─ cache_system.py (只依赖base)
  ├─ cache_hierarchical.py (只依赖base)
  └─ 所有子系统 (只依赖base)

方案2: 依赖注入反转
container.py
  ↓ 创建实例
cache_system.py
  ↓ 注入依赖
degradation.py, intelligent_warmer.py等
```

---

## 代码重复热力图

```
方法名                      cache_system  cache_hierarchical  重复率
─────────────────────────  ────────────  ──────────────────  ──────
__init__                     132行         103行              85%
get()                        71行          108行              80%
set()                        54行          63行               75%
_set_l1()                    22行          20行              95%
delete()/invalidate()        28行          24行              90%
invalidate_pattern()         24行          28行              95%
_match_pattern()             69行          69行             100%  ⚠️
get_stats()                  27行          25行              85%
clear_l1()                   6行           6行              100%  ⚠️
─────────────────────────  ────────────  ──────────────────  ──────
总计                         433行         446行             ~87%

完全相同的方法（100%重复）：
- _match_pattern() (69行) ⚠️ 最严重
- clear_l1() (6行)
```

---

## 修复路线图

### Phase 1: 紧急修复 (Week 1)

```
Day 1-2: 合并重复的HierarchicalCache
  ├─ 分析两个版本的差异
  ├─ 迁移cache_hierarchical的独有功能到cache_system
  ├─ 删除cache_hierarchical中的HierarchicalCache类
  └─ 运行测试验证

Day 3-4: 更新所有导入
  ├─ 统一从cache_system导入HierarchicalCache
  ├─ 更新degradation.py的导入
  ├─ 更新intelligent_warmer.py的导入
  └─ 更新其他模块的导入

Day 5: 解决循环依赖
  ├─ 创建base.py提取公共基础
  ├─ 重构导入关系
  └─ 验证无循环依赖
```

### Phase 2: 架构改进 (Week 2-3)

```
Week 2: 定义抽象和容器
  ├─ 创建interfaces.py定义所有接口
  ├─ 创建container.py实现依赖注入
  └─ 重构现有类实现接口

Week 3: 统一和优化
  ├─ 统一日志规范
  ├─ 统一监控方法
  └─ 增加测试覆盖
```

---

## 模块职责重新分配

### 当前问题：职责不清

```
HierarchicalCache (承担7种职责):
├─ 1. 缓存存储 (L1/L2操作)
├─ 2. 统计收集 (命中率、QPS)
├─ 3. 容量管理 (LRU淘汰、扩容)
├─ 4. 模式匹配 (通配符匹配)
├─ 5. 降级管理 (Redis故障降级)
├─ 6. 布隆过滤器集成
└─ 7. 读写锁集成
```

### 重构后：职责分离

```
HierarchicalCache (只负责存储)
└─ get(), set(), delete()

CacheStatisticsCollector (独立组件)
└─ record_l1_hit(), record_l2_hit(), get_stats()

CacheCapacityManager (独立组件)
└─ evict_l1(), expand_l1(), should_expand()

CachePatternMatcher (独立组件)
└─ match(key, pattern)

CacheDegradationManager (独立组件)
└─ get_with_fallback(), is_degraded()

EnhancedHierarchicalCache (门面)
└─ 组合以上所有组件，提供统一接口
```

---

## 风险矩阵

```
影响程度
    ^
高 │  ①代码重复     ②循环依赖
   │  [P0, 高风险]  [P0, 高风险]
   │
中 │  ③职责不清     ④缺乏抽象
   │  [P2, 中风险]  [P1, 中风险]
   │
低 │  ⑤日志不一致   ⑥类型注解
   │  [P3, 低风险]  [P3, 低风险]
   │
   └──────────────────────────────► 发生概率
     低    中    高

风险等级：
- P0 (紧急): 必须立即修复
- P1 (重要): 尽快修复
- P2 (一般): 计划修复
- P3 (建议): 有时间修复
```

---

**图表生成时间**: 2026-02-24
**工具**: 文本图示（ASCII Art）
