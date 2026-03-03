# HQL V2迁移路线图

**版本**: 2.0
**更新日期**: 2026-02-17

---

## 架构对比图

### V1架构（旧）

```
┌──────────────────────────────────────────────────────┐
│                     前端层                            │
├──────────────────────────────────────────────────────┤
│  Generate.jsx          FieldBuilder.jsx   Canvas     │
│  ┌─────────────────┐   ┌──────────────┐             │
│  │ POST /api/      │   │ 前端生成HQL   │             │
│  │ generate        │   │ (临时方案)    │             │
│  └─────────────────┘   └──────────────┘             │
└──────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────┐
│                   后端API层                           │
├──────────────────────────────────────────────────────┤
│  POST /api/generate                                  │
│  ┌──────────────────────────────────────┐            │
│  │ ❌ 未实现！仅返回占位符               │            │
│  │ {"message": "requires implementation"}│            │
│  └──────────────────────────────────────┘            │
└──────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────┐
│                 服务层（空！）                         │
├──────────────────────────────────────────────────────┤
│  ❌ 无HQL生成服务                                     │
└──────────────────────────────────────────────────────┘
```

**问题**: V1 API未实现，前端调用失败

---

### V2架构（新）

```
┌──────────────────────────────────────────────────────┐
│                     前端层                            │
├──────────────────────────────────────────────────────┤
│  FieldBuilder.tsx       Canvas.tsx       (待迁移)     │
│  ┌──────────────────┐   ┌──────────────┐             │
│  │ POST /hql-       │   │ POST /hql-   │             │
│  │ preview-v2/api/  │   │ preview-v2/  │             │
│  │ generate         │   │ api/generate │             │
│  └──────────────────┘   └──────────────┘             │
└──────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────┐
│                   后端API层                           │
├──────────────────────────────────────────────────────┤
│  POST /hql-preview-v2/api/generate                   │
│  ┌──────────────────────────────────────┐            │
│  │ ✅ 完整实现                          │            │
│  │ - 支持 single/join/union             │            │
│  │ - 内置LRU缓存                        │            │
│  │ - 增量生成（3-5x性能提升）           │            │
│  └──────────────────────────────────────┘            │
│                         │                            │
│                         ▼                            │
│  ProjectAdapter（适配层）                            │
│  ┌──────────────────────────────────────┐            │
│  │ • events_from_api_request()           │            │
│  │ • fields_from_api_request()           │            │
│  │ • conditions_from_api_request()       │            │
│  └──────────────────────────────────────┘            │
└──────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────┐
│                 V2核心服务层                          │
├──────────────────────────────────────────────────────┤
│  ✅ 完全无业务依赖，可独立使用                         │
│                                                      │
│  HQLGenerator                                         │
│  ├── generate() - 主入口                             │
│  ├── _generate_single_event()                        │
│  ├── _generate_join_events()                         │
│  └── _generate_union_events()                        │
│                                                      │
│  Builders（构建器）                                   │
│  ├── FieldBuilder - 字段构建                         │
│  ├── WhereBuilder - WHERE条件                        │
│  ├── JoinBuilder - JOIN操作                          │
│  └── UnionBuilder - UNION操作                        │
│                                                      │
│  Validators（验证器）                                 │
│  ├── SyntaxValidator - 语法验证                      │
│  └── PerformanceAnalyzer - 性能分析                  │
│                                                      │
│  Cache（缓存）                                        │
│  └── LRUCache - 3-5x性能提升                         │
└──────────────────────────────────────────────────────┘
```

**优势**: V2完全实现，功能强大，性能优越

---

## 适配器模式（推荐方案）

### 架构图

```
┌──────────────────────────────────────────────────────┐
│                   前端层（不变）                      │
├──────────────────────────────────────────────────────┤
│  Generate.jsx                                        │
│  ┌──────────────────────────────────────┐            │
│  │ POST /api/generate                   │            │
│  │ (保持V1接口格式)                     │            │
│  └──────────────────────────────────────┘            │
└──────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────┐
│              V1适配层（新增）                         │
├──────────────────────────────────────────────────────┤
│  POST /api/generate（适配器实现）                     │
│  ┌──────────────────────────────────────┐            │
│  │ 1. 解析V1格式请求                    │            │
│  │    {selected_events: [...]}         │            │
│  │                                     │            │
│  │ 2. 转换为V2格式                     │            │
│  │    {events: [...], fields: [...]}  │            │
│  │                                     │            │
│  │ 3. 调用V2服务                       │            │
│  │    service.generate_hql(...)        │            │
│  │                                     │            │
│  │ 4. 返回V1格式响应                   │            │
│  └──────────────────────────────────────┘            │
└──────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────┐
│                 V2核心服务层                          │
├──────────────────────────────────────────────────────┤
│  HQLGenerationServiceV2                               │
│  └── generate_hql(events, fields, conditions)        │
└──────────────────────────────────────────────────────┘
```

**优势**:
- ✅ 前端无需改动
- ✅ 平滑过渡
- ✅ 易于回滚

---

## 迁移时间线

### Week 1: 基础准备

```
Day 1-2: V2模块边界优化
├── 抽象适配器接口（IProjectAdapter）
├── 重构ProjectAdapter
└── 移除可选依赖

Day 3-5: 创建适配层
├── 实现V1适配器
├── 更新API文档
└── 单元测试
```

---

### Week 2: 前端迁移

```
Day 1-2: 修复Generate.jsx
├── 方案A: 保持V1接口（后端适配）
└── 方案B: 直接调用V2 API

Day 3-4: 更新FieldBuilder.tsx
├── 调用V2 API预览HQL
└── 移除前端生成逻辑

Day 5: Canvas模块迁移
├── useFlowExecute调用V2 API
└── 移除前端HQL生成器
```

---

### Week 3: 清理与优化

```
Day 1-2: 清理V1
├── 移除V1适配器（如果前端已迁移）
└── 更新API文档

Day 3-5: 性能优化
├── 启用增量生成
├── 优化缓存策略
└── 性能测试
```

---

## API契约对比

### V1请求格式

```json
POST /api/generate
{
  "selected_events": ["login", "purchase"],
  "date_str": "${bizdate}"
}
```

**问题**:
- ❌ 无法指定字段
- ❌ 无法添加WHERE条件
- ❌ 不支持JOIN/UNION

---

### V2请求格式

```json
POST /hql-preview-v2/api/generate
{
  "events": [
    {
      "game_gid": 10000147,
      "event_id": 1
    }
  ],
  "fields": [
    {
      "fieldName": "role_id",
      "fieldType": "base"
    },
    {
      "fieldName": "zone_id",
      "fieldType": "param",
      "jsonPath": "$.zone_id"
    }
  ],
  "where_conditions": [
    {
      "field": "zone_id",
      "operator": "=",
      "value": 1,
      "logicalOp": "AND"
    }
  ],
  "options": {
    "mode": "single",
    "include_comments": true
  }
}
```

**优势**:
- ✅ 完整字段控制
- ✅ 灵活WHERE条件
- ✅ 支持JOIN/UNION

---

## 模块边界设计

### V2模块应该暴露什么接口？

```python
# 公共API（导出到__all__）
__all__ = [
    # 服务接口
    "IHQLGenerationService",
    "HQLGenerationServiceV2",
    "HQLServiceFactory",

    # 核心模型
    "Event",
    "Field",
    "Condition",
    "JoinConfig",

    # 生成器
    "HQLGenerator",
    "DebuggableHQLGenerator",

    # 构建器
    "FieldBuilder",
    "WhereBuilder",
    "JoinBuilder",
    "UnionBuilder",

    # 验证器
    "SyntaxValidator",
    "validate_hql",
    "quick_validate_hql",
]

# 不导出（内部使用）
# - ProjectAdapter（项目特定）
# - HQLHistoryService（可选依赖）
# - FieldRecommender（可选依赖）
```

---

### 项目特定逻辑应该在哪里？

```python
# 项目特定逻辑应放在适配器层
backend/services/hql/adapters/
├── base.py              # 接口定义
├── project_adapter.py   # Event2Table实现
└── example_adapter.py   # 示例实现

# 核心服务保持纯净
backend/services/hql/core/
├── generator.py         # 无业务依赖
├── builders/            # 无业务依赖
└── validators/          # 无业务依赖
```

---

### 如何保持V2可移植性？

**规则1**: 核心服务不导入项目模块
```python
# ✅ 正确：仅导入标准库
from typing import List, Dict, Any
from dataclasses import dataclass

# ❌ 错误：导入项目模块
from backend.core.utils import fetch_one_as_dict
from backend.models import Game
```

---

**规则2**: 依赖注入而非硬编码
```python
# ✅ 正确：依赖注入
class HQLGenerator:
    def __init__(self, adapter: IProjectAdapter = None):
        self.adapter = adapter

# ❌ 错误：硬编码依赖
class HQLGenerator:
    def __init__(self):
        self.adapter = ProjectAdapter()  # 硬编码
```

---

**规则3**: 可选依赖使用try-except
```python
# ✅ 正确：可选导入
try:
    from backend.services.hql.services.history_service import HQLHistoryService
    _history_available = True
except ImportError:
    _history_available = False

# 使用时检查
if _history_available:
    service = HQLHistoryService()
```

---

## 独立化检查清单

### ✅ 代码解耦检查

- [x] 核心生成器无业务依赖
- [x] 使用接口抽象适配器
- [x] 可选依赖使用try-except
- [ ] 移除所有`from backend.core`导入（核心服务）
- [ ] 使用依赖注入而非硬编码

---

### ✅ 可移植性检查

- [ ] 移除项目特定配置
- [ ] 提供示例适配器
- [ ] 编写独立使用文档
- [ ] 发布到PyPI

---

### ✅ 测试覆盖检查

- [ ] 核心服务单元测试（无需数据库）
- [ ] 适配器集成测试（需要数据库）
- [ ] E2E测试（完整流程）

---

## 下一步行动

### 立即执行（本周）

1. ✅ 创建`IProjectAdapter`接口
2. ✅ 重构`ProjectAdapter`实现接口
3. ✅ 实现V1适配器（`POST /api/generate`）
4. ✅ 更新API文档

---

### 短期目标（2周内）

1. 修复`Generate.jsx`调用V1 API失败问题
2. 更新`FieldBuilder.tsx`调用V2 API
3. Canvas模块迁移到V2 API
4. 完整E2E测试

---

### 中期目标（1个月内）

1. 移除前端HQL生成逻辑
2. 移除V1 API适配器
3. 性能优化（启用增量生成）
4. 独立化V2模块

---

### 长期目标（3个月内）

1. 发布独立PyPI包：`hql-generator`
2. 编写独立使用文档
3. 提供示例适配器
4. 社区推广

---

**文档作者**: Claude Code (Event2Table Project)
**状态**: ✅ 已完成
**最后更新**: 2026-02-17
