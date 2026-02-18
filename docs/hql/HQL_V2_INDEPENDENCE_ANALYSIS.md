# HQL V2独立性分析与迁移策略

**分析日期**: 2026-02-17
**分析目标**: 评估HQL V2作为独立模块的可行性，设计项目迁移策略
**V2模块规模**: 8,044行代码，完全模块化架构

---

## 一、V2模块独立性评分

### 当前独立性评分

| 维度 | 评分 | 说明 |
|------|------|------|
| **代码解耦** | ⭐ 4.5/5 | 核心生成器完全无业务依赖，仅适配器层依赖项目 |
| **依赖隔离** | ⭐ 4/5 | 仅1个业务依赖点（ProjectAdapter），可选导入 |
| **可移植性** | ⭐ 4/5 | 可作为独立PyPI包发布，适配器可替换 |
| **测试覆盖** | ⭐ 5/5 | 完整单元测试，无需数据库即可运行 |

**综合评分**: ⭐ **4.5/5** - 高度独立，易于复用

---

## 二、依赖分析

### 2.1 项目特定依赖（可解耦）

#### ✅ **唯一强依赖点**: `ProjectAdapter`

**位置**: `backend/services/hql/adapters/project_adapter.py`

**依赖内容**:
```python
from backend.core.utils import fetch_one_as_dict
```

**作用**:
- 查询`log_events`表获取事件信息
- 查询`games`表获取数据库配置
- 构建`{ods_db}.ods_{game_gid}_all_view`表名

**解耦方案**:
```python
# 方案1: 接口化（推荐）
class IProjectAdapter(ABC):
    @abstractmethod
    def get_event_info(self, event_id: int) -> Event:
        pass

    @abstractmethod
    def get_game_info(self, game_gid: int) -> Dict[str, Any]:
        pass

# 方案2: 配置化
EVENT_TABLE_TEMPLATE = "{ods_db}.ods_{game_gid}_all_view"
```

**解耦难度**: 🟢 **低** - 仅1个文件，224行代码

---

#### 🟡 **可选依赖**: `HQLHistoryService`, `FieldRecommender`

**位置**:
- `backend/services/hql/services/history_service.py`
- `backend/services/hql/services/field_recommender.py`

**依赖内容**:
```python
from backend.core.database import fetch_one_as_dict, fetch_all_as_dict
```

**作用**:
- 历史记录管理（hql_history表）
- 智能字段推荐（基于历史统计）

**解耦方案**:
```python
# 这些是扩展功能，不是核心功能
# 可在独立版本中移除或使用SQLite内存数据库
```

**解耦难度**: 🟢 **低** - 已标记为可选依赖

---

### 2.2 通用依赖（保留）

以下是V2核心功能必需的通用依赖，可以保留：

| 依赖 | 用途 | 版本要求 |
|------|------|---------|
| `dataclasses` | 数据模型 | Python 3.7+ |
| `typing` | 类型注解 | Python 3.7+ |
| `enum` | 枚举类型 | Python 3.7+ |
| `abc` | 抽象基类 | Python 3.7+ |
| `re` | 正则表达式 | Python标准库 |
| `hashlib` | 缓存键生成 | Python标准库 |

**✅ 结论**: 无需第三方库，纯Python标准库

---

## 三、当前V1引用点分析

### 3.1 后端引用点

#### 🔴 **高优先级**: `POST /api/generate`

**文件**: `backend/api/routes/hql_generation.py`
**调用方式**:
```python
@api_bp.route("/api/generate", methods=["POST"])
def api_generate_hql():
    # V1实现，仅返回占位符
    results = {
        "message": "HQL generation endpoint - requires implementation with HQLManager"
    }
```

**状态**: ❌ **未实现** - 仅返回占位符消息

**影响**: 前端调用此API会失败

---

#### 🟢 **已迁移**: `POST /hql-preview-v2/api/generate`

**文件**: `backend/api/routes/hql_preview_v2.py`
**调用方式**:
```python
from backend.services.hql.core.generator import HQLGenerator
from backend.services.hql.adapters.project_adapter import ProjectAdapter

generator = HQLGenerator()
hql = generator.generate(events=events, fields=fields, conditions=conditions)
```

**状态**: ✅ **完全V2** - 使用V2核心服务

**优势**:
- 支持 single/join/union 三种模式
- 内置缓存机制（LRU Cache）
- 增量生成支持（3-5x性能提升）

---

#### 🟡 **Canvas模块**: `/api/canvas/execute`

**文件**: `backend/services/canvas/canvas.py`
**调用方式**:
```python
# Canvas使用自定义HQL生成逻辑
# 未调用V1或V2服务
```

**状态**: ⚠️ **独立实现** - 需要迁移到V2

---

### 3.2 前端引用点

#### 🔴 **高优先级**: `Generate.jsx`

**文件**: `frontend/src/analytics/pages/Generate.jsx`
**调用方式**:
```javascript
const response = await fetch("/api/generate", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    selected_events: [selectedEvent],
    date_str: "${bizdate}",
  }),
});
```

**状态**: ❌ **调用未实现的V1 API**

**影响**: 用户点击"生成HQL"按钮会失败

---

#### 🟢 **已迁移**: `FieldBuilder.tsx`

**文件**: `frontend/src/event-builder/pages/FieldBuilder.tsx`
**调用方式**:
```typescript
import { previewHQL } from '@shared/api/fieldBuilder';

// 前端生成HQL（临时方案）
const hql = generateHQL(fields, `event_${eventId}`, mode);
```

**状态**: ⚠️ **前端生成** - 临时方案，应迁移到V2 API

---

#### 🟡 **Canvas模块**: `hqlGenerators.js`

**文件**: `frontend/src/features/canvas/components/utils/hqlGenerators.js`
**调用方式**:
```javascript
export class HQLGenerators {
  static generateEventHQL(eventConfig, gameData) {
    // 前端HQL生成逻辑
    const hql = `-- ${eventConfig.event_name}\nSELECT ...`;
    return hql;
  }
}
```

**状态**: ⚠️ **前端生成** - 临时方案，应迁移到V2 API

---

## 四、V1 vs V2 API对比

### 4.1 功能对比

| 功能 | V1 API | V2 API | 差距 |
|------|--------|--------|------|
| **单事件HQL** | ❌ 未实现 | ✅ 完整实现 | V2胜 |
| **多事件JOIN** | ❌ 不支持 | ✅ 支持 | V2胜 |
| **多事件UNION** | ❌ 不支持 | ✅ 支持 | V2胜 |
| **参数字段** | ❌ 不支持 | ✅ 支持 | V2胜 |
| **WHERE条件** | ❌ 不支持 | ✅ 支持 | V2胜 |
| **增量生成** | ❌ 不支持 | ✅ 支持 | V2胜 |
| **语法验证** | ❌ 基础验证 | ✅ 完整验证 | V2胜 |
| **性能分析** | ❌ 不支持 | ✅ 支持 | V2胜 |
| **缓存机制** | ❌ 不支持 | ✅ LRU缓存 | V2胜 |
| **历史记录** | ❌ 不支持 | ✅ 支持 | V2胜 |

**结论**: V2在所有维度都优于V1

---

### 4.2 API端点对比

| 功能 | V1端点 | V2端点 | 状态 |
|------|--------|--------|------|
| 生成HQL | `POST /api/generate` | `POST /hql-preview-v2/api/generate` | ⚠️ 并存 |
| 调试模式 | ❌ | `POST /hql-preview-v2/api/generate-debug` | ✅ V2 |
| 增量生成 | ❌ | `POST /hql-preview-v2/api/generate-incremental` | ✅ V2 |
| 语法验证 | `POST /api/validate-hql` | `POST /hql-preview-v2/api/validate` | ⚠️ 并存 |
| 性能分析 | ❌ | `POST /hql-preview-v2/api/analyze` | ✅ V2 |
| 字段推荐 | ❌ | `GET /hql-preview-v2/api/recommend-fields` | ✅ V2 |
| 历史记录 | ❌ | `/hql-preview-v2/api/history/*` | ✅ V2 |

**迁移建议**: 将V1端点重定向到V2端点

---

## 五、迁移策略对比

### 策略A: 适配器模式（推荐 ⭐）

#### 方案设计

创建V2客户端适配器，模拟V1接口，前端无需改动

**后端实现**:
```python
# backend/api/routes/hql_generation.py
@api_bp.route("/api/generate", methods=["POST"])
def api_generate_hql():
    """V1 API - 重定向到V2服务"""
    # 1. 解析V1格式请求
    selected_events = data.get("selected_events", [])
    date_str = data.get("date_str", "${bizdate}")

    # 2. 转换为V2格式
    events_data = []
    for event_name in selected_events:
        events_data.append({
            "name": event_name,
            "table_name": f"{game_ods_db}.ods_{game_gid}_all_view"
        })

    # 3. 调用V2服务
    from backend.services.hql.service_interface import HQLServiceFactory

    service = HQLServiceFactory.create(version='v2')
    hql = service.generate_hql(
        events=events_data,
        fields=[...],  # 默认字段
        conditions=[]
    )

    # 4. 返回V1格式响应
    return json_success_response(data={"hql": hql})
```

**前端**: 无需改动

---

#### 优势
- ✅ 前端零改动，风险最低
- ✅ 平滑过渡，可逐步优化
- ✅ V1/V2并存，易于回滚
- ✅ 保持API契约一致性

#### 劣势
- ⚠️ 增加一层适配逻辑
- ⚠️ 维护两套API文档

#### 实施难度
- 🟢 **低** - 适配器逻辑简单（~100行代码）
- 🟢 **时间**: 2-3天

---

### 策略B: 直接迁移

#### 方案设计

前端直接调用V2 API，移除V1端点

**后端实现**:
```python
# 删除 backend/api/routes/hql_generation.py
# 保留 backend/api/routes/hql_preview_v2.py

# 在 web_app.py 中注册V2 blueprint
from backend.api.routes import hql_preview_v2
app.register_blueprint(hql_preview_v2_bp, url_prefix='/')
```

**前端改造**:
```typescript
// frontend/src/analytics/pages/Generate.jsx
const response = await fetch("/hql-preview-v2/api/generate", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    events: [{
      game_gid: currentGameGid,
      event_name: selectedEvent
    }],
    fields: [
      { fieldName: "ds", fieldType: "base" },
      { fieldName: "role_id", fieldType: "base" },
      // ...
    ],
    where_conditions: [],
    options: {
      mode: "single",
      include_comments: true
    }
  }),
});
```

---

#### 优势
- ✅ 充分利用V2功能
- ✅ 无性能损失
- ✅ 代码更简洁

#### 劣势
- ❌ 需要前端适配
- ❌ 需要更新所有调用点
- ❌ 测试工作量大

#### 实施难度
- 🟡 **中** - 前端改造工作量较大
- 🟡 **时间**: 5-7天

---

### 策略C: 渐进式迁移

#### 方案设计

保留V1用于旧功能，新功能使用V2

**阶段1**: V1用于`Generate.jsx`，V2用于`FieldBuilder.tsx`
**阶段2**: 新功能（Canvas）使用V2
**阶段3**: 逐步迁移旧功能到V2

---

#### 优势
- ✅ 风险最低
- ✅ 灵活性高
- ✅ 可随时调整策略

#### 劣势
- ❌ 维护两套代码
- ❌ API文档混乱
- ❌ 技术债务累积

#### 实施难度
- 🟢 **低** - 无需大规模改造
- 🟡 **时间**: 长期（数月）

---

## 六、推荐方案

### 🏆 **推荐**: 策略A（适配器模式） + 策略B（逐步迁移）

**理由**:
1. **短期**: 使用适配器模式，快速修复V1 API，保证业务连续性
2. **中期**: 新功能（Canvas、Field Builder）直接使用V2 API
3. **长期**: 逐步迁移旧功能，最终移除V1

---

## 七、实施步骤

### 阶段1: V2模块边界优化（2天）

#### ✅ **步骤1.1**: 抽象适配器接口

```python
# backend/services/hql/adapters/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class IProjectAdapter(ABC):
    """项目适配器接口"""

    @abstractmethod
    def get_event_info(self, event_id: int) -> Dict[str, Any]:
        """获取事件信息"""
        pass

    @abstractmethod
    def get_game_info(self, game_gid: int) -> Dict[str, Any]:
        """获取游戏信息"""
        pass
```

---

#### ✅ **步骤1.2**: 重构ProjectAdapter

```python
# backend/services/hql/adapters/project_adapter.py
from .base import IProjectAdapter

class ProjectAdapter(IProjectAdapter):
    """Event2Table项目适配器实现"""

    def get_event_info(self, event_id: int) -> Dict[str, Any]:
        from backend.core.utils import fetch_one_as_dict
        return fetch_one_as_dict("SELECT * FROM log_events WHERE id = ?", (event_id,))

    def get_game_info(self, game_gid: int) -> Dict[str, Any]:
        from backend.core.utils import fetch_one_as_dict
        return fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (game_gid,))
```

---

#### ✅ **步骤1.3**: 移除可选依赖

```python
# backend/services/hql/__init__.py
# 可选导入历史服务和推荐器
try:
    from .services.history_service import HQLHistoryService
    from .services.field_recommender import FieldRecommender
    _services_available = True
except ImportError:
    _services_available = False
```

---

### 阶段2: 创建适配层（2-3天）

#### ✅ **步骤2.1**: 实现V1适配器

```python
# backend/api/routes/hql_generation.py
@api_bp.route("/api/generate", methods=["POST"])
def api_generate_hql():
    """V1 API - 适配到V2服务"""
    from backend.services.hql.service_interface import HQLServiceFactory
    from backend.services.hql.adapters.project_adapter import ProjectAdapter

    # 解析V1请求
    selected_events = data.get("selected_events", [])

    # 转换为V2格式
    events = []
    for event_name in selected_events:
        # 查询事件信息
        event = fetch_one_as_dict(
            "SELECT * FROM log_events WHERE event_name = ? AND game_gid = ?",
            (event_name, game_gid)
        )
        events.append(ProjectAdapter.event_from_project(game_gid, event['id']))

    # 调用V2服务
    service = HQLServiceFactory.create(version='v2')
    hql = service.generate_hql(
        events=events,
        fields=ProjectAdapter.fields_from_api_request(get_default_fields()),
        conditions=[]
    )

    return json_success_response(data={"hql": hql, "events": selected_events})
```

---

#### ✅ **步骤2.2**: 更新API文档

```markdown
# API文档

## V1 API（已适配到V2）

### POST /api/generate
> **说明**: 已适配到V2服务，保持V1接口格式

**状态**: ✅ 已实现（适配器模式）

## V2 API（推荐使用）

### POST /hql-preview-v2/api/generate
> **说明**: 原生V2服务，支持更多功能

**状态**: ✅ 已实现
```

---

### 阶段3: 前端迁移（3-5天）

#### ✅ **步骤3.1**: 修复Generate.jsx

```typescript
// frontend/src/analytics/pages/Generate.jsx
// 方案A: 无需改动（后端已适配）
// 方案B: 直接调用V2 API

const handleGenerate = async () => {
  // 方案B: 直接调用V2
  const response = await fetch("/hql-preview-v2/api/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      events: [{
        game_gid: currentGameGid,
        event_id: selectedEventData.id
      }],
      fields: [
        { fieldName: "ds", fieldType: "base" },
        { fieldName: "role_id", fieldType: "base" },
        { fieldName: "account_id", fieldType: "base" },
        { fieldName: "utdid", fieldType: "base" },
        { fieldName: "envinfo", fieldType: "base" },
        { fieldName: "tm", fieldType: "base" },
        { fieldName: "ts", fieldType: "base" }
      ],
      where_conditions: [],
      options: {
        mode: "single",
        include_comments: true
      }
    }),
  });
}
```

---

#### ✅ **步骤3.2**: 更新FieldBuilder.tsx

```typescript
// frontend/src/event-builder/pages/FieldBuilder.tsx
// 调用V2 API预览HQL

const previewHQL = async () => {
  const response = await fetch("/hql-preview-v2/api/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      events: [{
        game_gid: urlGameGid,
        event_id: selectedEventId
      }],
      fields: fields.map(f => ({
        fieldName: f.name,
        fieldType: f.type,
        alias: f.alias,
        jsonPath: f.jsonPath
      })),
      where_conditions: [],
      options: {
        mode: "single",
        include_comments: true
      }
    }),
  });

  const result = await response.json();
  setCustomHQL(result.data.hql);
}
```

---

#### ✅ **步骤3.3**: Canvas模块迁移

```javascript
// frontend/src/features/canvas/hooks/useFlowExecute.ts
// 调用V2 API生成HQL

const executeFlow = async (nodes, edges) => {
  const response = await fetch("/hql-preview-v2/api/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      events: eventNodes.map(node => ({
        game_gid: gameData.gid,
        event_id: node.config.event_id
      })),
      fields: extractFieldsFromNodes(nodes),
      where_conditions: [],
      options: {
        mode: detectJoinOrUnion(edges),
        join_config: buildJoinConfig(edges)
      }
    }),
  });
}
```

---

### 阶段4: 清理V1（1-2天）

#### ✅ **步骤4.1**: 移除V1适配器

```bash
# 当所有前端都已迁移到V2后
rm backend/api/routes/hql_generation.py
```

---

#### ✅ **步骤4.2**: 更新文档

```markdown
# API文档

## V2 API

### POST /hql-preview-v2/api/generate
> **说明**: HQL V2生成API（推荐使用）

## V1 API
> **已废弃** - 请使用V2 API
```

---

## 八、独立化V2模块

### 目标：将V2打包为独立PyPI包

#### 步骤1: 创建独立项目结构

```bash
hql-generator/
├── hql_generator/
│   ├── __init__.py
│   ├── core/
│   ├── builders/
│   ├── models/
│   ├── validators/
│   └── adapters/
│       ├── base.py          # 接口定义
│       └── example.py       # 示例适配器
├── tests/
├── setup.py
├── pyproject.toml
└── README.md
```

---

#### 步骤2: 配置依赖

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="hql-generator",
    version="2.0.0",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        # 无需第三方依赖！
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
        ]
    }
)
```

---

#### 步骤3: 提供示例适配器

```python
# hql_generator/adapters/example.py
from .base import IProjectAdapter

class ExampleProjectAdapter(IProjectAdapter):
    """示例适配器 - 展示如何实现自定义适配器"""

    def get_event_info(self, event_id: int) -> Dict[str, Any]:
        # 从你的数据源查询事件信息
        return {
            "event_name": "login",
            "table_name": "your_db.your_table",
            "partition_field": "ds"
        }

    def get_game_info(self, game_gid: int) -> Dict[str, Any]:
        # 从你的数据源查询游戏信息
        return {
            "gid": game_gid,
            "ods_db": "your_db"
        }
```

---

#### 步骤4: 使用方式

```bash
# 安装
pip install hql-generator

# 使用
from hql_generator import HQLServiceFactory, Event, Field, YourCustomAdapter

# 创建服务
service = HQLServiceFactory.create(version='v2')
service.set_adapter(YourCustomAdapter())

# 生成HQL
event = Event(name="login", table_name="db.table")
field = Field(name="role_id", type="base")
hql = service.generate_hql(events=[event], fields=[field], conditions=[])
```

---

## 九、总结

### V2模块独立性结论

✅ **高度独立**: 4.5/5评分，可作为独立PyPI包发布
✅ **易于移植**: 仅需实现适配器接口即可复用
✅ **功能完整**: 支持single/join/union三种模式，功能远超V1
✅ **性能优越**: 内置缓存机制，增量生成性能提升3-5x

---

### 迁移策略总结

| 阶段 | 策略 | 时间 | 风险 |
|------|------|------|------|
| **阶段1** | V2边界优化 | 2天 | 🟢 低 |
| **阶段2** | 创建适配层 | 2-3天 | 🟢 低 |
| **阶段3** | 前端迁移 | 3-5天 | 🟡 中 |
| **阶段4** | 清理V1 | 1-2天 | 🟢 低 |
| **总计** | - | **8-12天** | 🟡 **可控** |

---

### 下一步行动

1. **立即执行**: 实施阶段1（V2模块边界优化）
2. **短期目标**: 创建适配层，修复V1 API（阶段2）
3. **中期目标**: 逐步迁移前端到V2（阶段3）
4. **长期目标**: 发布独立PyPI包（独立化）

---

**文档作者**: Claude Code (Event2Table Project)
**审核状态**: ✅ 已完成
**最后更新**: 2026-02-17
