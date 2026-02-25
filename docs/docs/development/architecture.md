# 架构设计文档

> **版本**: 8.0 | **最后更新**: 2026-02-23
>
> 本文档详细说明 Event2Table 项目的架构设计、模块职责和数据流向。
>
> **🆕 最新变更**: 技术负债与双轨制问题分析 (2026-02-23) - 新增技术负债章节

---

## 目录

- [架构概览](#架构概览)
- [分层架构说明](#分层架构说明)
- [模块职责](#模块职责)
- [Canvas系统设计](#canvas系统设计)
- [HQL生成器设计](#hql生成器设计)
- [数据流向](#数据流向)
- [技术栈说明](#技术栈说明)
- [技术负债与双轨制问题](#技术负债与双轨制问题)

---

## 架构概览

### 系统架构图

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (React)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ Event Builder│  │ Field Builder│  │ Canvas UI │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│              API Layer (Flask Routes)                │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ Games API    │  │ Events API   │  │ HQL API   │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│           Service Layer (Business Logic)             │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ Game Service │  │ Event Service│  │HQL Service│ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│         Repository Layer (Data Access)               │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ Game Repo    │  │ Event Repo   │  │Param Repo │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│           Schema Layer (Data Validation)             │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ Game Schema  │  │ Event Schema │  │HQL Schema │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                  Database (SQLite)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │    Games     │  │    Events    │  │ Parameters│ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────┘
```

### 架构设计原则

**1. 分层架构（Layered Architecture）**

项目采用严格的四层架构，每一层有明确的职责：

- **API层**: 处理HTTP请求和响应
- **Service层**: 实现业务逻辑
- **Repository层**: 封装数据访问
- **Schema层**: 数据验证和序列化

**2. 关注点分离（Separation of Concerns）**

每一层只关注自己的职责，不越界处理其他层的逻辑。

**3. 依赖倒置（Dependency Inversion）**

高层模块不依赖低层模块，两者都依赖抽象（Schema/Interface）。

**4. 单一职责（Single Responsibility）**

每个类、每个函数只有一个改变的理由。

---

## 分层架构说明

### Schema层（数据验证层）

**位置**: `backend/models/schemas.py`

**职责**：
- 定义数据传输对象（DTO）
- 验证输入数据
- 数据序列化/反序列化
- 提供API文档

**技术选型**：Pydantic

**示例**：

```python
from pydantic import BaseModel, Field, validator
from typing import Literal
import html

class GameCreate(BaseModel):
    """游戏创建Schema"""
    gid: str = Field(..., min_length=1, max_length=50, description="游戏业务ID")
    name: str = Field(..., min_length=1, max_length=100, description="游戏名称")
    ods_db: Literal["ieu_ods", "overseas_ods"] = Field(..., description="ODS数据库名称")

    @validator("name")
    def sanitize_name(cls, v):
        """防止XSS攻击：转义HTML字符"""
        if v:
            return html.escape(v.strip())
        return v

    @validator("gid")
    def validate_gid(cls, v):
        """验证gid格式"""
        v = v.strip()
        if not v.isdigit():
            raise ValueError("gid必须是数字")
        return v
```

**优势**：
- ✅ 自动验证输入数据
- ✅ 生成API文档
- ✅ 防止XSS攻击
- ✅ 类型安全

### Repository层（数据访问层）

**位置**: `backend/models/repositories/`

**职责**：
- 封装数据访问逻辑
- 提供CRUD操作
- 实现复杂查询
- 管理缓存策略

**技术选型**：基于GenericRepository

**示例**：

```python
from backend.core.data_access import GenericRepository
from backend.core.database.converters import fetch_one_as_dict, fetch_all_as_dict
from typing import Optional, List, Dict, Any

class GameRepository(GenericRepository):
    """游戏仓储类"""

    def __init__(self):
        """初始化游戏仓储，启用缓存"""
        super().__init__(
            table_name="games",
            primary_key="id",
            enable_cache=True,
            cache_timeout=120  # 2分钟缓存
        )

    def find_by_gid(self, gid: int) -> Optional[Dict[str, Any]]:
        """根据业务GID查询游戏"""
        query = "SELECT * FROM games WHERE gid = ?"
        return fetch_one_as_dict(query, (gid,))

    def get_all_with_event_count(self) -> List[Dict[str, Any]]:
        """获取所有游戏及其事件数量"""
        query = """
            SELECT
                g.*,
                COUNT(DISTINCT le.id) as event_count
            FROM games g
            LEFT JOIN log_events le ON g.id = le.game_id
            GROUP BY g.id
            ORDER BY g.name
        """
        return fetch_all_as_dict(query)
```

**优势**：
- ✅ 数据访问逻辑集中
- ✅ 易于测试（Mock Repository）
- ✅ 缓存策略统一
- ✅ 复用通用CRUD

### Service层（业务逻辑层）

**位置**: `backend/services/`

**职责**：
- 实现业务逻辑
- 协调多个Repository
- 管理事务
- 调用HQL生成器

**示例**：

```python
from backend.models.repositories.games import GameRepository
from backend.models.repositories.events import EventRepository
from backend.models.schemas import GameCreate, GameResponse
from typing import Dict, Any

class GameService:
    """游戏业务服务"""

    def __init__(self):
        """初始化服务，注入Repository"""
        self.game_repo = GameRepository()
        self.event_repo = EventRepository()

    def create_game(self, game_data: GameCreate) -> Dict[str, Any]:
        """
        创建游戏

        业务逻辑：
        1. 验证gid唯一性
        2. 创建游戏
        3. 初始化默认配置
        """
        # 1. 检查gid是否已存在
        existing = self.game_repo.find_by_gid(game_data.gid)
        if existing:
            raise ValueError(f"Game gid {game_data.gid} already exists")

        # 2. 创建游戏
        game_id = self.game_repo.create(game_data.dict())

        # 3. 返回创建的游戏
        return self.game_repo.find_by_id(game_id)

    def delete_game(self, game_gid: int) -> None:
        """
        删除游戏

        业务逻辑：
        1. 检查游戏是否存在
        2. 检查是否有关联事件
        3. 删除游戏（级联删除事件）
        """
        # 1. 检查游戏存在
        game = self.game_repo.find_by_gid(game_gid)
        if not game:
            raise ValueError(f"Game {game_gid} not found")

        # 2. 检查关联事件
        events = self.event_repo.find_by_game_gid(game_gid)
        if events:
            raise ValueError(f"Cannot delete game with {len(events)} events")

        # 3. 删除游戏
        self.game_repo.delete(game['id'])
```

**优势**：
- ✅ 业务逻辑集中
- ✅ 事务管理清晰
- ✅ 易于扩展
- ✅ 可复用性强

#### Service层改进 (2026-02-20优化)

**新增Service类**：

1. **GameService** (`backend/services/games/game_service.py`)
   - `create_game_with_validation()` - 带验证的游戏创建
   - `update_game_with_cache_invalidation()` - 带缓存失效的游戏更新
   - `delete_game_with_checks()` - 带检查的游戏删除
   - `get_game_statistics()` - 游戏统计信息

2. **EventService** (`backend/services/events/event_service.py`)
   - `create_event()` - 创建事件
   - `import_events()` - 批量导入事件
   - `get_events_by_game_gid()` - 根据game_gid获取事件
   - `delete_event()` - 删除事件

3. **HQLFacade** (`backend/services/hql/hql_facade.py`)
   - 简化HQL生成的门面类
   - `generate_single_event_hql()` - 单事件HQL生成
   - `generate_join_hql()` - JOIN模式HQL生成
   - `generate_union_hql()` - UNION模式HQL生成

**Service层最佳实践**：

```python
# ✅ 正确：Service层使用game_gid
class GameService:
    def get_game_by_gid(self, game_gid: int) -> Dict[str, Any]:
        """根据game_gid获取游戏"""
        game = self.game_repo.find_by_gid(game_gid)
        if not game:
            raise ValueError(f"Game {game_gid} not found")
        return game

# ✅ 正确：Service层清理缓存
def update_game(self, game_gid: int, data: Dict) -> Dict[str, Any]:
    """更新游戏并清理缓存"""
    game = self.game_repo.update_by_gid(game_gid, data)
    cache.delete_many(f'game:{game_gid}*')
    cache.delete('games:all')
    return game

# ✅ 正确：Service层使用Repository
class EventService:
    def __init__(self):
        self.event_repo = EventRepository()
        self.param_repo = EventParamRepository()

    def create_event_with_params(self, event_data: Dict, params: List[Dict]) -> Dict:
        """创建事件及其参数"""
        event = self.event_repo.create(event_data)
        for param in params:
            self.param_repo.create({
                'event_id': event['id'],
                'game_gid': event_data['game_gid'],  # 使用game_gid
                **param
            })
        return event
```

**关键改进** (2026-02-20):
- ✅ 完全切换到game_gid（不再使用game_id）
- ✅ 自动缓存失效管理
- ✅ 增强类型注解（mypy兼容）
- ✅ 统一错误处理模式
- ✅ N+1查询修复

### API层（HTTP端点层）

**位置**: `backend/api/routes/`

**职责**：
- 处理HTTP请求/响应
- 解析请求参数
- 调用Service层
- 返回JSON响应

**示例**：

```python
from flask import Blueprint, request, jsonify
from backend.services.games.game_service import GameService
from backend.models.schemas import GameCreate, GameResponse
from backend.core.utils import json_success_response, json_error_response
import logging

logger = logging.getLogger(__name__)
games_bp = Blueprint('games', __name__)

@games_bp.route('/api/games', methods=['POST'])
def create_game():
    """创建游戏API"""
    try:
        # 1. 解析和验证请求参数
        data = request.get_json()
        game_data = GameCreate(**data)  # Pydantic验证

        # 2. 调用Service层
        service = GameService()
        game = service.create_game(game_data)

        # 3. 返回响应
        return json_success_response(
            data=GameResponse(**game).dict(),
            message="Game created successfully"
        )

    except ValidationError as e:
        return json_error_response(f"Validation error: {e}", status_code=400)
    except ValueError as e:
        return json_error_response(str(e), status_code=409)
    except Exception as e:
        logger.error(f"Error creating game: {e}")
        return json_error_response("Failed to create game", status_code=500)

@games_bp.route('/api/games/<int:gid>', methods=['DELETE'])
def delete_game(gid: int):
    """删除游戏API"""
    try:
        service = GameService()
        service.delete_game(gid)

        return json_success_response(message=f"Game {gid} deleted successfully")

    except ValueError as e:
        return json_error_response(str(e), status_code=404)
    except Exception as e:
        logger.error(f"Error deleting game: {e}")
        return json_error_response("Failed to delete game", status_code=500)
```

**优势**：
- ✅ HTTP逻辑与业务逻辑分离
- ✅ 错误处理统一
- ✅ 响应格式标准化
- ✅ 易于测试

---

## 模块职责

### 各层的主要职责

| 层 | 职责 | 不应该做的事 |
|---|------|-------------|
| **API层** | - 处理HTTP请求<br>- 解析参数<br>- 返回JSON响应 | - 直接访问数据库<br>- 包含业务逻辑<br>- 处理事务 |
| **Service层** | - 实现业务逻辑<br>- 协调Repository<br>- 管理事务 | - 直接访问数据库<br>- 处理HTTP请求<br>- 返回HTML |
| **Repository层** | - 封装数据访问<br>- 提供CRUD操作<br>- 实现查询 | - 包含业务逻辑<br>- 处理HTTP请求<br>- 返回非标准格式 |
| **Schema层** | - 验证数据<br>- 定义类型<br>- 序列化/反序列化 | - 包含业务逻辑<br>- 访问数据库<br>- 处理HTTP |

### 依赖关系

```
API Layer
    ↓ depends on
Service Layer
    ↓ depends on
Repository Layer
    ↓ depends on
Schema Layer
```

**规则**：
- ✅ 上层可以调用下层
- ✅ 下层不能调用上层
- ❌ 同层之间不能直接调用（通过Service协调）
- ✅ 所有层都可以使用Schema

### 数据转换流程

```
HTTP Request (JSON)
    ↓
API Layer (request.get_json())
    ↓
Schema Layer (Pydantic validation)
    ↓
Service Layer (Business Logic)
    ↓
Repository Layer (SQL queries)
    ↓
Database (SQLite)
    ↓
Repository Layer (Dict)
    ↓
Service Layer (Business Logic)
    ↓
Schema Layer (Serialization)
    ↓
API Layer (jsonify)
    ↓
HTTP Response (JSON)
```

---

## Canvas系统设计

### 系统架构

```
Frontend Canvas UI
    ↓
Canvas API (backend/services/canvas/)
    ↓
Canvas Node Manager
    ↓
HQL Builder (backend/services/hql/)
    ↓
HQL Output
```

### 节点类型

**1. Table节点（数据源）**
```javascript
{
  type: "table",
  data: {
    tableName: "ieu_ods.ods_10000147_all_view",
    gameGid: 10000147
  }
}
```

**2. Join节点（关联）**
```javascript
{
  type: "join",
  data: {
    joinType: "INNER", // INNER, LEFT, RIGHT, FULL
    joinConditions: [
      {
        leftField: "role_id",
        rightField: "role_id",
        operator: "="
      }
    ]
  }
}
```

**3. Filter节点（过滤）**
```javascript
{
  type: "filter",
  data: {
    conditions: [
      {
        field: "ds",
        operator: "=",
        value: "${bizdate}"
      }
    ]
  }
}
```

**4. Union节点（合并）**
```javascript
{
  type: "union",
  data: {
    unionType: "ALL" // ALL, DISTINCT
  }
}
```

### 可视化流程配置

**前端React组件**：
- `CanvasBoard`: 画布容器
- `CanvasNode`: 节点组件
- `ConnectionLine`: 连接线
- `NodePropertiesPanel`: 属性面板

**后端API**：
- `POST /api/canvas/templates`: 保存模板
- `GET /api/canvas/templates`: 获取模板列表
- `POST /api/canvas/generate`: 生成HQL
- `GET /api/canvas/nodes`: 获取节点类型

### HQL生成流程

```python
# backend/services/canvas/canvas_service.py

class CanvasService:
    """Canvas业务服务"""

    def generate_hql_from_template(self, template_id: int) -> str:
        """
        从Canvas模板生成HQL

        流程：
        1. 加载模板
        2. 解析节点关系
        3. 构建执行计划
        4. 调用HQL生成器
        5. 返回HQL语句
        """
        # 1. 加载模板
        template = self.template_repo.find_by_id(template_id)

        # 2. 解析节点关系
        nodes = json.loads(template['nodes'])
        edges = json.loads(template['edges'])

        # 3. 构建执行计划
        execution_plan = self._build_execution_plan(nodes, edges)

        # 4. 调用HQL生成器
        generator = HQLGenerator()
        hql = generator.generate_from_execution_plan(execution_plan)

        # 5. 返回HQL
        return hql
```

---

## HQL生成器设计

### V2架构（模块化、解耦）

```
backend/services/hql/
├── core/              # 核心生成器
│   ├── generator.py          # 主生成器
│   ├── incremental_generator.py  # 增量生成器
│   └── cache.py              # 缓存管理
├── builders/          # Builder模式
│   ├── field_builder.py      # 字段构建器
│   ├── where_builder.py      # WHERE条件构建器
│   ├── join_builder.py       # JOIN构建器
│   └── union_builder.py      # UNION构建器
├── models/            # 数据模型
│   └── event.py              # 事件模型定义
├── validators/        # 验证器
│   ├── event_validator.py    # 事件验证
│   └── field_validator.py    # 字段验证
├── templates/         # 模板管理
│   ├── view_template.py      # VIEW模板
│   └── procedure_template.py # PROCEDURE模板
└── tests/             # 单元测试
```

### Builder模式

**1. FieldBuilder（字段构建器）**

```python
class FieldBuilder:
    """字段构建器"""

    def build_fields(self, fields: List[Field]) -> List[str]:
        """
        构建字段SQL列表

        支持的字段类型：
        - base: 基础字段（直接从表中选择）
        - param: 参数字段（使用get_json_object解析）
        - computed: 计算字段（使用SQL表达式）
        """
        field_sqls = []
        for field in fields:
            if field.type == "base":
                sql = field.name
            elif field.type == "param":
                sql = f"get_json_object(params, '{field.json_path}') AS {field.name}"
            elif field.type == "computed":
                sql = f"{field.expression} AS {field.name}"
            field_sqls.append(sql)
        return field_sqls
```

**2. WhereBuilder（条件构建器）**

```python
class WhereBuilder:
    """WHERE条件构建器"""

    def build(self, conditions: List[Condition], context: Dict) -> str:
        """
        构建WHERE子句

        支持的条件：
        - 简单条件: field = value
        - 范围条件: field BETWEEN a AND b
        - 复合条件: (condition1 AND condition2)
        """
        if not conditions:
            return "ds = '${bizdate}'"  # 默认分区过滤

        condition_sqls = []
        for condition in conditions:
            if condition.operator == "BETWEEN":
                sql = f"{condition.field} BETWEEN {condition.value1} AND {condition.value2}"
            else:
                sql = f"{condition.field} {condition.operator} {condition.value}"
            condition_sqls.append(sql)

        return " AND ".join(condition_sqls)
```

**3. JoinBuilder（关联构建器）**

```python
class JoinBuilder:
    """JOIN构建器"""

    def build_join(
        self,
        events: List[Event],
        join_conditions: List[JoinCondition],
        join_type: str,
        use_aliases: bool
    ) -> str:
        """
        构建JOIN SQL

        支持的JOIN类型：
        - INNER JOIN
        - LEFT JOIN
        - RIGHT JOIN
        - FULL OUTER JOIN
        """
        if not events or len(events) < 2:
            raise ValueError("JOIN requires at least 2 events")

        # 主表
        main_event = events[0]
        join_sql = f"FROM {main_event.table_name} AS t0"

        # 关联表
        for i, event in enumerate(events[1:], start=1):
            alias = f"t{i}" if use_aliases else ""
            join_sql += f"\n  {join_type} JOIN {event.table_name}"
            if alias:
                join_sql += f" AS {alias}"

            # ON条件
            on_conditions = [c for c in join_conditions if c.right_table == i]
            on_clause = " AND ".join([
                f"t{c.left_table}.{c.left_field} = t{c.right_table}.{c.right_field}"
                for c in on_conditions
            ])
            join_sql += f"\n    ON {on_clause}"

        return join_sql
```

**4. UnionBuilder（合并构建器）**

```python
class UnionBuilder:
    """UNION构建器"""

    def build_union(
        self,
        events: List[Event],
        fields: List[Field],
        union_type: str
    ) -> str:
        """
        构建UNION SQL

        支持的UNION类型：
        - UNION ALL: 保留所有行（包括重复）
        - UNION DISTINCT: 去重
        """
        select_sqls = []
        for event in events:
            # 为每个事件生成SELECT语句
            field_sqls = self.field_builder.build_fields(fields)
            fields_clause = ",\n  ".join(field_sqls)

            select_sql = f"""SELECT
  {fields_clause}
FROM {event.table_name}
WHERE ds = '${bizdate}'"""

            select_sqls.append(select_sql)

        separator = f"\nUNION {'ALL' if union_type == 'ALL' else 'DISTINCT'}\n"
        return separator.join(select_sqls)
```

### 生成器主流程

```python
class HQLGenerator:
    """核心HQL生成器"""

    def __init__(self):
        """初始化生成器"""
        self.field_builder = FieldBuilder()
        self.where_builder = WhereBuilder()
        self.join_builder = JoinBuilder()
        self.union_builder = UnionBuilder()

    def generate(
        self,
        events: List[Event],
        fields: List[Field],
        conditions: List[Condition],
        **options
    ) -> str:
        """
        生成HQL主入口

        支持的模式：
        - single: 单事件
        - join: 多事件JOIN
        - union: 多事件UNION
        """
        mode = options.get("mode", "single")

        if mode == "single":
            return self._generate_single_event(events, fields, conditions, options)
        elif mode == "join":
            return self._generate_join_events(events, fields, conditions, options)
        elif mode == "union":
            return self._generate_union_events(events, fields, conditions, options)
        else:
            raise ValueError(f"Unsupported mode: {mode}")
```

### 支持的模式

**1. Single模式（单事件）**

```sql
CREATE OR REPLACE VIEW dwd_event_login AS
SELECT
  ds,
  role_id,
  account_id,
  utdid,
  get_json_object(params, '$.zoneId') AS zone_id
FROM ieu_ods.ods_10000147_all_view
WHERE ds = '${bizdate}';
```

**2. Join模式（多事件JOIN）**

```sql
CREATE OR REPLACE VIEW dwd_event_joined AS
SELECT
  t0.ds,
  t0.role_id,
  t0.account_id,
  t1.device_id
FROM ieu_ods.ods_10000147_login_view AS t0
INNER JOIN ieu_ods.ods_10000147_logout_view AS t1
  ON t0.role_id = t1.role_id
  AND t0.ds = t1.ds
WHERE t0.ds = '${bizdate}';
```

**3. Union模式（多事件UNION）**

```sql
CREATE OR REPLACE VIEW dwd_event_union AS
SELECT
  ds,
  role_id,
  'login' AS event_type
FROM ieu_ods.ods_10000147_login_view
WHERE ds = '${bizdate}'
UNION ALL
SELECT
  ds,
  role_id,
  'logout' AS event_type
FROM ieu_ods.ods_10000147_logout_view
WHERE ds = '${bizdate}';
```

---

## 数据流向

### 完整请求流程

```
1. 用户操作（前端）
   ├─ 用户填写表单
   ├─ 点击"生成HQL"按钮
   └─ 前端收集数据

2. API调用（前端 → 后端）
   ├─ fetch('/api/hql/generate', {
   │    method: 'POST',
   │    body: JSON.stringify(requestData)
   │  })
   └─ 发送HTTP POST请求

3. Schema验证（后端）
   ├─ Pydantic解析请求体
   ├─ 验证必填字段
   ├─ 验证数据类型
   └─ 转义HTML字符（XSS防护）

4. Service处理（业务逻辑）
   ├─ 调用GameRepository获取游戏信息
   ├─ 调用EventRepository获取事件列表
   ├─ 协调业务逻辑
   └─ 准备HQL生成参数

5. HQL生成（生成器）
   ├─ 创建HQLGenerator实例
   ├─ 调用FieldBuilder构建字段
   ├─ 调用WhereBuilder构建条件
   ├─ 根据mode选择构建器
   └─ 返回HQL语句

6. 数据库访问（Repository）
   ├─ 执行SQL查询
   ├─ 使用参数化查询（防注入）
   ├─ 返回字典格式数据
   └─ 更新缓存

7. 响应返回（后端 → 前端）
   ├─ Service层返回HQL字符串
   ├─ API层包装为JSON响应
   ├─ 返回200 OK状态码
   └─ 前端接收响应

8. UI更新（前端）
   ├─ 解析JSON响应
   ├─ 显示HQL预览
   ├─ 提供复制按钮
   └─ 下载HQL文件
```

### 错误处理流程

```
异常发生
    ↓
Service层捕获异常
    ↓
记录详细日志（logger.error）
    ↓
返回用户友好的错误消息
    ↓
API层包装为JSON错误响应
    ↓
返回适当的HTTP状态码
    ├─ 400: 参数验证失败
    ├─ 404: 资源不存在
    ├─ 409: 资源冲突
    └─ 500: 服务器错误
    ↓
前端显示错误提示
```

---

## 技术栈说明

### 后端技术栈

**核心框架**：
- **Flask**: 轻量级Web框架
  - Blueprint模块化
  - 请求上下文
  - Session管理

**数据验证**：
- **Pydantic**: 数据验证和序列化
  - 自动类型转换
  - 字段验证
  - 文档生成

**数据库**：
- **SQLite**: 轻量级数据库
  - 零配置
  - 事务支持
  - Python内置支持

**测试**：
- **pytest**: 测试框架
  - fixture机制
  - 参数化测试
  - 覆盖率报告

### 前端技术栈

**核心框架**：
- **React 18**: UI框架
  - Hooks API
  - Context API
  - 组件化

**构建工具**：
- **Vite**: 快速构建工具
  - 热更新
  - 优化打包
  - TypeScript支持

**UI框架**：
- **Tailwind CSS**: 实用优先的CSS框架
  - 响应式设计
  - 深色模式
  - 组件库

**测试**：
- **Playwright**: E2E测试框架
  - 跨浏览器支持
  - 自动等待
  - 网络拦截

### 开发工具

**代码质量**：
- **Black**: Python代码格式化
- **isort**: Import排序
- **ESLint**: JavaScript/TypeScript检查
- **Prettier**: 代码格式化

**版本控制**：
- **Git**: 版本控制
- **GitHub**: 代码托管

**文档**：
- **Markdown**: 文档编写
- **JSDoc**: JavaScript文档
- **Pydoc**: Python文档

---

## 架构优势

### 1. 可维护性

**分层架构**：
- 每层职责清晰
- 易于定位问题
- 降低修改风险

**模块化设计**：
- 功能独立
- 低耦合
- 易于替换

### 2. 可测试性

**依赖注入**：
- Repository可Mock
- Service可单元测试
- API可集成测试

**测试覆盖**：
- 单元测试（Service/Repository）
- 集成测试（API）
- E2E测试（前端）

### 3. 可扩展性

**水平扩展**：
- 无状态设计
- 缓存分离
- 负载均衡

**垂直扩展**：
- 缓存优化
- 数据库索引
- 异步处理

### 4. 性能优化

**缓存策略**：
- Redis缓存
- 分层缓存（L1/L2）
- TTL优化

**数据库优化**：
- 索引优化
- 查询优化
- 连接池

---

## 技术负债与双轨制问题

> **重要**: 本章节记录项目中存在的技术负债和双轨制问题，需要逐步清理和统一。

### 1. API双轨制问题 (REST vs GraphQL)

#### 问题描述

项目同时存在REST API和GraphQL API两套体系，但这是**设计上的功能互补**，而非技术负债。

| API类型 | 位置 | 使用场景 | 状态 |
|---------|------|----------|------|
| **REST API** | `backend/api/routes/` | 标准CRUD操作、HQL生成 | ✅ 主要API |
| **GraphQL API** | `backend/gql_api/` | 复杂查询、数据聚合、示例演示 | ✅ 补充API |

#### 具体表现

**后端API架构**：

```
backend/
├── api/routes/           # REST API (23个路由文件)
│   ├── games.py          # 游戏CRUD
│   ├── events.py         # 事件CRUD
│   ├── parameters.py     # 参数管理
│   ├── hql_preview_v2.py # HQL生成
│   └── ...
│
└── gql_api/              # GraphQL API (实现中)
    ├── queries/          # 10个查询模块
    ├── mutations/        # 10个变更模块
    ├── types/            # 类型定义
    └── dataloaders/      # 数据加载器
```

**前端使用情况**：

```
frontend/src/
├── graphql/              # GraphQL客户端（示例/演示）
│   ├── client.ts         # Apollo Client配置
│   ├── queries.ts        # GraphQL查询
│   ├── mutations.ts      # GraphQL变更
│   ├── hooks.ts          # GraphQL Hooks
│   └── components/       # 示例组件
│       └── GamesGraphQL.tsx  # GraphQL示例组件
│
└── shared/api/           # REST API客户端（生产使用）
    ├── hqlApiV2.ts       # HQL REST API
    └── ...
```

**使用统计**：
- React Query (REST): **62处** - 生产代码主要使用
- Apollo Client (GraphQL): **12处** - 主要在示例组件和测试中

#### 影响分析

| 影响 | 说明 |
|------|------|
| **维护成本** | GraphQL是补充功能，维护压力不大 |
| **功能互补** | REST用于CRUD，GraphQL用于复杂查询 |
| **学习曲线** | GraphQL作为可选技术，不强制学习 |
| **测试复杂度** | GraphQL主要用于示例，测试覆盖有限 |

#### 解决方案

**推荐方案：保留双API，明确职责**

理由：
1. **REST API**: 作为主要生产API，处理所有CRUD操作
2. **GraphQL API**: 作为补充API，用于复杂查询和演示
3. **前端**: 生产代码使用REST，示例代码使用GraphQL

**职责划分**：

| 场景 | 推荐API | 说明 |
|------|---------|------|
| CRUD操作 | REST | games, events, parameters等 |
| HQL生成 | REST | `/hql-preview-v2/api/generate` |
| 复杂查询 | GraphQL | 多表关联、数据聚合 |
| 示例演示 | GraphQL | 展示GraphQL能力 |
| 单元测试 | REST | 测试主要业务逻辑 |

**维护建议**：

1. **保持REST API为生产API**
   - 继续完善REST API功能
   - 确保REST API覆盖所有业务需求
   - 前端生产代码优先使用REST

2. **GraphQL作为补充**
   - 用于复杂查询场景
   - 用于示例和演示
   - 不强制要求前端使用

3. **文档说明**
   - 在API文档中明确REST和GraphQL的使用场景
   - 推荐新功能优先实现REST API
   - GraphQL作为可选特性

---

### 2. game_id与game_gid双轨制问题

#### 问题描述

经过深入分析，这是一个**假阳性**问题。项目中已经正确使用了`game_gid`作为业务标识，`game_id`仅在极少数遗留代码中使用。

| 标识符 | 类型 | 含义 | 使用状态 |
|--------|------|------|----------|
| `id` (games表) | INTEGER | 数据库内部自增主键 | ✅ 正常使用 |
| `gid` (games表) | TEXT | 游戏业务ID | ✅ 标准业务标识 |
| `game_gid` (外键) | TEXT/INTEGER | 关联到games.gid | ✅ 标准外键 |
| `game_id` (遗留) | INTEGER | 旧的外键关联 | ⚠️ 仅在common_params表 |

#### 数据库现状分析

**主要表结构（已标准化）**：

```sql
-- games表：标准设计
CREATE TABLE games (
    id INTEGER PRIMARY KEY,      -- 内部主键
    gid TEXT UNIQUE NOT NULL,    -- 业务ID (game_gid)
    name TEXT NOT NULL,
    ods_db TEXT NOT NULL
);

-- log_events表：已使用game_gid
CREATE TABLE log_events (
    id INTEGER PRIMARY KEY,
    game_gid TEXT NOT NULL,      -- 外键关联games.gid
    event_name TEXT NOT NULL,
    FOREIGN KEY (game_gid) REFERENCES games(gid)
);

-- event_params表：通过event_id关联
CREATE TABLE event_params (
    id INTEGER PRIMARY KEY,
    event_id INTEGER NOT NULL,   -- 关联log_events.id
    param_name TEXT NOT NULL,
    FOREIGN KEY (event_id) REFERENCES log_events(id)
);
```

**遗留表（common_params）**：

```sql
-- common_params表：仍使用game_id（需要清理）
CREATE TABLE common_params (
    id INTEGER PRIMARY KEY,
    game_id INTEGER NOT NULL,    -- ⚠️ 遗留字段，应改为game_gid
    param_name TEXT NOT NULL,
    FOREIGN KEY (game_id) REFERENCES games(id)
);
```

#### 代码现状分析

**API层（已标准化）**：

```python
# ✅ 正确：使用game_gid
@api_bp.route('/api/games/<int:gid>')
def get_game(gid: int):
    game = game_repo.find_by_gid(gid)
    return json_success_response(data=game)

@api_bp.route('/api/events')
def list_events():
    game_gid = request.args.get('game_gid')  # ✅ 使用game_gid
    events = event_repo.find_by_game_gid(game_gid)
    return json_success_response(data=events)
```

**Repository层（已标准化）**：

```python
# ✅ 正确：使用game_gid
class GameRepository(GenericRepository):
    def find_by_gid(self, gid: int) -> Optional[Dict]:
        query = "SELECT * FROM games WHERE gid = ?"
        return fetch_one_as_dict(query, (gid,))

class EventRepository(GenericRepository):
    def find_by_game_gid(self, game_gid: int) -> List[Dict]:
        query = "SELECT * FROM log_events WHERE game_gid = ?"
        return fetch_all_as_dict(query, (game_gid,))
```

#### 影响分析

| 影响 | 严重程度 | 说明 |
|------|----------|------|
| **数据一致性** | 低 | 主流表已使用game_gid |
| **查询复杂度** | 低 | game_gid直接关联，无需JOIN |
| **API混乱** | 低 | API已统一使用game_gid |
| **遗留代码** | 中 | common_params表仍使用game_id |

#### 解决方案

**推荐方案：清理遗留的game_id**

理由：
1. 主流代码已使用game_gid
2. 仅common_params表需要清理
3. 不需要大规模重构

**清理步骤**：

1. **Phase 1**: 修改common_params表结构
   ```sql
   -- 添加game_gid列
   ALTER TABLE common_params ADD COLUMN game_gid TEXT;

   -- 迁移数据
   UPDATE common_params
   SET game_gid = (SELECT gid FROM games WHERE id = common_params.game_id);

   -- 创建新索引
   CREATE INDEX idx_common_params_game_gid ON common_params(game_gid);

   -- 创建新外键约束
   -- 注意：SQLite不支持直接添加外键约束，需要重建表
   ```

2. **Phase 2**: 更新代码
   ```python
   # backend/core/database/_constants.py
   COMMON_PARAMS_TABLE_SQL = """
       CREATE TABLE IF NOT EXISTS common_params (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           game_gid TEXT NOT NULL,  -- 改为game_gid
           param_name TEXT NOT NULL,
           ...
           FOREIGN KEY (game_gid) REFERENCES games(gid),
           UNIQUE(game_gid, param_name)
       )
   """
   ```

3. **Phase 3**: 清理旧代码
   - 搜索并删除所有`game_id`相关代码
   - 更新测试用例
   - 验证功能正常

**验证清单**：

- [ ] common_params表迁移完成
- [ ] 所有API使用game_gid
- [ ] 所有Repository使用game_gid
- [ ] 测试用例更新
- [ ] 文档更新

---

### 3. HQL生成器版本问题

#### 问题描述

HQL生成器存在V1和V2两个版本，但**V1已非活跃，V2是主要生产版本**。

| 版本 | 位置 | 状态 | 说明 |
|------|------|------|------|
| **V1** | `backend/api/routes/hql_generation.py` | ⚠️ 非活跃 | 简化实现，功能有限 |
| **V2** | `backend/api/routes/hql_preview_v2.py` | ✅ 主要版本 | 完整实现，生产使用 |
| **Adapter** | `backend/api/routes/v1_adapter.py` | ⚠️ 兼容层 | V1格式到V2的适配 |

#### 具体表现

**文件结构**：

```
backend/api/routes/
├── hql_generation.py      # V1 (9.5KB) - 简化实现
├── hql_preview_v2.py      # V2 (46KB) - 完整实现
└── v1_adapter.py          # Adapter (16KB) - 格式转换

backend/services/hql/
├── core/
│   ├── generator.py       # V2核心生成器
│   └── incremental_generator.py
├── builders/              # Builder模式
│   ├── field_builder.py
│   ├── where_builder.py
│   ├── join_builder.py
│   └── union_builder.py
├── adapters/              # 适配器
│   └── project_adapter.py
├── hql_facade.py          # 门面类
└── hql_service_cached.py  # 缓存版本
```

**API端点**：

```
# V1 API (非活跃)
POST /api/generate           # 简化实现，功能有限
GET  /api/hql/<int:id>       # 获取HQL内容

# V2 API (主要)
POST /hql-preview-v2/api/generate        # 完整HQL生成
POST /hql-preview-v2/api/generate-debug  # 调试模式
POST /hql-preview-v2/api/validate        # HQL验证
GET  /hql-preview-v2/api/recommend-fields # 字段推荐
GET  /hql-preview-v2/api/status          # API状态
GET  /hql-preview-v2/api/cache-stats     # 缓存统计
POST /hql-preview-v2/api/cache-clear     # 清空缓存

# V1 Adapter (兼容)
POST /api/v1-adapter/preview-hql         # V1格式预览
POST /api/v1-adapter/generate-with-debug # V1格式生成
```

**前端使用情况**：

```
frontend/src/
├── shared/api/
│   └── hqlApiV2.ts       # ✅ 使用V2 API
│
└── event-builder/
    └── components/
        └── HQLPreviewWrapper/
            └── HQLPreviewWrapper.tsx  # ✅ 使用V2 API
```

#### 影响分析

| 影响 | 严重程度 | 说明 |
|------|----------|------|
| **代码冗余** | 低 | V1代码很少，维护成本低 |
| **功能不一致** | 低 | 前端已统一使用V2 |
| **API混乱** | 低 | 文档明确说明使用V2 |
| **测试重复** | 低 | 主要测试V2 |

#### 详细统一方案

**推荐方案：保留V2，清理V1和Adapter**

理由：
1. V2架构清晰（Builder模式）
2. V2功能完善（调试、验证、缓存）
3. 前端已统一使用V2
4. V1和Adapter使用率低

**Phase 1: 验证V2功能完整性（1周）**

```python
# 验证清单
- [ ] V2支持单事件HQL生成
- [ ] V2支持JOIN模式
- [ ] V2支持UNION模式
- [ ] V2支持WHERE条件
- [ ] V2支持字段别名
- [ ] V2支持参数字段解析
- [ ] V2支持缓存
- [ ] V2支持调试模式
- [ ] V2支持HQL验证
```

**Phase 2: 前端确认（1天）**

```bash
# 搜索前端是否还有使用V1 API的地方
grep -r "/api/generate" frontend/src --exclude-dir=__tests__
grep -r "/api/v1-adapter" frontend/src --exclude-dir=__tests__
```

**Phase 3: 清理V1代码（2天）**

```python
# 1. 删除V1 API文件
rm backend/api/routes/hql_generation.py

# 2. 删除V1 Adapter文件
rm backend/api/routes/v1_adapter.py

# 3. 更新API蓝图注册
# backend/api/__init__.py
# 移除以下导入和注册：
# from .routes import hql_generation
# from .routes import v1_adapter
```

**Phase 4: 更新文档（1天）**

```markdown
# docs/development/architecture.md

更新HQL生成器章节：
- 移除V1相关说明
- 强调V2为主要版本
- 更新API端点列表
```

**Phase 5: 更新测试（2天）**

```python
# backend/test/integration/api/
# 删除V1相关测试
rm test_hql_generation.py
rm test_v1_adapter.py

# 保留V2测试
# test_hql_preview_v2.py
```

**迁移时间表**：

| 阶段 | 任务 | 时间 | 负责人 |
|------|------|------|--------|
| Phase 1 | 验证V2功能完整性 | 1周 | 后端 |
| Phase 2 | 前端确认 | 1天 | 前端 |
| Phase 3 | 清理V1代码 | 2天 | 后端 |
| Phase 4 | 更新文档 | 1天 | 文档 |
| Phase 5 | 更新测试 | 2天 | 测试 |
| **总计** | | **2周** | |

**风险控制**：

1. **备份V1代码**
   ```bash
   git mv backend/api/routes/hql_generation.py backup/
   git mv backend/api/routes/v1_adapter.py backup/
   ```

2. **灰度发布**
   - 先在测试环境验证
   - 确认无问题后再部署生产

3. **回滚计划**
   - 如果出现问题，快速恢复V1代码
   - 重新注册V1 API端点

---

### 4. 前端状态管理问题

#### 问题描述

前端使用多种状态管理方案，但这是**合理的设计模式**，职责划分清晰。

| 方案 | 用途 | 库 | 状态 | 使用场景 |
|------|------|-----|------|----------|
| **Zustand** | 客户端状态 | `zustand` | ✅ 推荐 | 当前选中游戏、UI状态 |
| **React Query** | 服务端状态 | `@tanstack/react-query` | ✅ 推荐 | 游戏列表、事件数据、HQL生成 |
| **Apollo Client** | GraphQL状态 | `@apollo/client` | ✅ 补充 | GraphQL示例组件 |

#### 具体表现

**状态管理架构**：

```
frontend/src/
├── stores/
│   └── gameStore.ts       # Zustand Store (客户端状态)
│       └── useGameStore() # 当前选中游戏、模态框状态
│
├── graphql/
│   ├── client.ts          # Apollo Client配置
│   ├── queries.ts         # GraphQL查询定义
│   ├── mutations.ts       # GraphQL变更定义
│   ├── hooks.ts           # GraphQL Hooks (28个)
│   └── components/
│       └── GamesGraphQL.tsx  # GraphQL示例组件
│
└── 各组件内部
    └── useQuery/useMutation  # React Query (服务端状态，62处)
```

**职责划分**：

```typescript
// ✅ Zustand - 客户端状态（用户交互、UI状态）
const { currentGame, setCurrentGame, isAddGameModalOpen } = useGameStore();

// ✅ React Query - 服务端状态（API数据）
const { data: games, isLoading } = useQuery({
  queryKey: ['games'],
  queryFn: fetchGames
});

const { mutate: createGame } = useMutation({
  mutationFn: createGameApi,
  onSuccess: () => {
    queryClient.invalidateQueries(['games']);
  }
});

// ✅ Apollo Client - GraphQL状态（示例演示）
const { data, loading } = useGames(20);  // 仅在GamesGraphQL组件中使用
```

#### 影响分析

| 影响 | 严重程度 | 说明 |
|------|----------|------|
| **状态同步** | 低 | 职责清晰，不会冲突 |
| **学习曲线** | 低 | Zustand和React Query是主流方案 |
| **包体积** | 低 | Apollo Client仅在示例中使用 |
| **维护成本** | 低 | 各方案独立维护 |

#### 解决方案

**推荐方案：保持现状，明确职责**

理由：
1. **Zustand**: 轻量级客户端状态管理，适合UI状态
2. **React Query**: 专业的服务端状态管理，自动缓存、重新获取
3. **Apollo Client**: 用于GraphQL示例，展示GraphQL能力

**职责划分规范**：

| 状态类型 | 管理方案 | 示例 | 原因 |
|----------|----------|------|------|
| **客户端状态** | Zustand | 当前选中游戏、模态框开关、侧边栏状态 | 轻量、简单 |
| **服务端状态** | React Query | 游戏列表、事件数据、HQL生成结果 | 自动缓存、重新获取 |
| **表单状态** | React Hook Form | 表单输入、验证 | 专业表单管理 |
| **GraphQL状态** | Apollo Client | GraphQL查询（示例） | GraphQL特性 |

**使用规范**：

1. **Zustand使用场景**
   ```typescript
   // ✅ 正确：UI状态、用户交互
   const { currentGame, setCurrentGame } = useGameStore();
   const { isModalOpen, openModal, closeModal } = useModalStore();

   // ❌ 错误：不要存储服务端数据
   const { games, setGames } = useGameStore();  // 应该用React Query
   ```

2. **React Query使用场景**
   ```typescript
   // ✅ 正确：API数据、服务端状态
   const { data: games } = useQuery(['games'], fetchGames);
   const { mutate: createGame } = useMutation(createGameApi);

   // ❌ 错误：不要存储UI状态
   const { data: isModalOpen } = useQuery(['modal'], fetchModal);  // 应该用Zustand
   ```

3. **Apollo Client使用场景**
   ```typescript
   // ✅ 正确：GraphQL示例、演示
   const { data } = useGames(20);  // 仅在GamesGraphQL.tsx中使用

   // ❌ 错误：生产代码不要使用
   const { data } = useQuery(GET_GAMES);  // 生产代码应使用React Query
   ```

**文档建议**：

在`docs/development/frontend-state-management.md`中明确说明：

```markdown
# 前端状态管理规范

## 状态类型划分

1. 客户端状态 → 使用Zustand
2. 服务端状态 → 使用React Query
3. 表单状态 → 使用React Hook Form
4. GraphQL状态 → 使用Apollo Client（仅示例）

## 使用示例

见上文"职责划分规范"
```

---

### 5. Legacy代码问题

#### 问题描述

项目中存在一些标记为legacy/deprecated的代码，需要逐步清理。

| 文件 | 状态 | 说明 | 优先级 |
|------|------|------|--------|
| `backend/api/routes/legacy_api.py` | ⚠️ DEPRECATED | 废弃API，有安全风险 | **P0** |
| `backend/core/utils_legacy.py` | ⚠️ Legacy | 旧工具函数，动态导入 | **P1** |
| `backend/api/routes/events_v2.py` | ⚠️ DDD版本 | 使用DDD架构的新版本 | **P2** |
| `backend/api/routes/games_v2.py` | ⚠️ DDD版本 | 使用DDD架构的新版本 | **P2** |

#### 具体表现

**1. legacy_api.py（P0 - 高风险）**

```python
"""
⚠️ DEPRECATED: 此API已废弃，不建议使用

废弃原因:
- 安全风险：多处未验证的用户输入
- 维护困难：代码结构混乱
- 功能重复：新API已替代

建议迁移到:
- events.py
- games.py
- parameters.py
"""
```

**2. utils_legacy.py（P1 - 中等风险）**

```python
# backend/core/utils/__init__.py
# 动态导入legacy模块
spec = importlib.util.spec_from_file_location("backend.core.utils_legacy", parent_module_path)
utils_legacy = importlib.util.module_from_spec(spec)
sys.modules["backend.core.utils_legacy"] = utils_legacy
spec.loader.exec_module(utils_legacy)

# 导出legacy函数（20+个函数）
execute_write = utils_legacy.execute_write
execute_transaction = utils_legacy.execute_transaction
batch_execute = utils_legacy.batch_execute
db_transaction = utils_legacy.db_transaction
# ... 更多函数
```

**3. events_v2.py / games_v2.py（P2 - 低风险）**

```python
"""
Events API Routes V2 - DDD Architecture

This module provides event-related API endpoints using the DDD architecture.
It uses the EventAppService from the application layer.

Migration Status: Phase 2 - DDD Migration
"""
```

#### 详细清理计划

**P0: 清理legacy_api.py（1周）**

**Step 1: 验证无使用（1天）**
```bash
# 搜索前端是否使用legacy API
grep -r "/api/hql\|/api/common-params" frontend/src --exclude-dir=__tests__

# 搜索后端是否调用legacy API
grep -r "legacy_api" backend --include="*.py" --exclude-dir=__pycache__
```

**Step 2: 删除文件（1天）**
```bash
# 备份
git mv backend/api/routes/legacy_api.py backup/

# 删除
rm backend/api/routes/legacy_api.py
```

**Step 3: 更新API注册（1天）**
```python
# backend/api/__init__.py
# 移除以下导入：
# from .routes import legacy_api
# api_bp.register_blueprint(legacy_api.legacy_bp)
```

**Step 4: 更新测试（1天）**
```python
# 删除legacy API测试
rm backend/test/integration/api/test_legacy_api.py
```

**Step 5: 更新文档（1天）**
```markdown
# docs/api/README.md
移除legacy API相关说明
```

---

**P1: 清理utils_legacy.py（2周）**

**Step 1: 分析函数使用（3天）**
```python
# 列出所有legacy函数
execute_write = utils_legacy.execute_write
execute_transaction = utils_legacy.execute_transaction
batch_execute = utils_legacy.batch_execute
db_transaction = utils_legacy.db_transaction
success_response = utils_legacy.success_response
error_response = utils_legacy.error_response
json_success_response = utils_legacy.json_success_response
json_error_response = utils_legacy.json_error_response
validate_json_request = utils_legacy.validate_json_request
handle_errors = utils_legacy.handle_errors
handle_api_errors = utils_legacy.handle_api_errors
get_game_gid_param = utils_legacy.get_game_gid_param
require_game_with_redirect = utils_legacy.require_game_with_redirect
get_ods_db_name = utils_legacy.get_ods_db_name
calculate_common_param_threshold = utils_legacy.calculate_common_param_threshold
get_event_with_game_info = utils_legacy.get_event_with_game_info
get_game_by_gid = utils_legacy.get_game_by_gid
get_active_parameters = utils_legacy.get_active_parameters
get_event_with_parameters = utils_legacy.get_event_with_parameters
get_games_with_event_counts = utils_legacy.get_games_with_event_counts
check_game_has_events = utils_legacy.check_game_has_events
get_categories_by_game = utils_legacy.get_categories_by_game
sanitize_html = utils_legacy.sanitize_html
sanitize_user_input = utils_legacy.sanitize_user_input
escape_output = utils_legacy.escape_output
find_column_by_keywords = utils_legacy.find_column_by_keywords
```

**Step 2: 迁移有用函数（1周）**
```python
# 创建新模块 backend/core/utils_v2.py

# 迁移数据库操作函数
def execute_write(query: str, params: tuple = None) -> int:
    """执行INSERT/UPDATE/DELETE操作"""
    # 实现代码...

def execute_transaction(queries: List[Tuple[str, tuple]]) -> bool:
    """执行事务"""
    # 实现代码...

# 迁移响应函数
def json_success_response(data: Any = None, message: str = None, status_code: int = 200):
    """返回成功JSON响应"""
    # 实现代码...

def json_error_response(error: str, status_code: int = 400):
    """返回错误JSON响应"""
    # 实现代码...

# 迁移验证函数
def validate_json_request() -> Tuple[bool, Any, str]:
    """验证JSON请求"""
    # 实现代码...
```

**Step 3: 更新所有引用（3天）**
```python
# 搜索所有引用
grep -r "from backend.core.utils import" backend --include="*.py"

# 更新导入
# from backend.core.utils import execute_write
# 改为：
# from backend.core.utils_v2 import execute_write
```

**Step 4: 删除legacy文件（1天）**
```bash
# 备份
git mv backend/core/utils_legacy.py backup/

# 删除
rm backend/core/utils_legacy.py

# 更新 backend/core/utils/__init__.py
# 移除动态导入代码
```

---

**P2: 处理events_v2.py / games_v2.py（3周）**

**分析**：
- `events_v2.py`和`games_v2.py`不是遗留代码，而是使用DDD架构的新版本
- 目前的`events.py`和`games.py`是旧版本
- 这是一个架构迁移过程

**方案**：
1. 保留V2版本（DDD架构）
2. 逐步将旧版本迁移到V2
3. 最终删除旧版本

**迁移步骤**：

**Phase 1: 对比功能差异（1周）**
```python
# 对比 events.py 和 events_v2.py 的功能
# 列出V2有但V1没有的功能
# 列出V1有但V2没有的功能
```

**Phase 2: 补全V2功能（1周）**
```python
# 在events_v2.py中添加缺失的功能
# 在games_v2.py中添加缺失的功能
```

**Phase 3: 更新前端调用（1周）**
```typescript
// 将 /api/events 改为 /api/v2/events
// 将 /api/games 改为 /api/v2/games
```

**Phase 4: 删除旧版本（1天）**
```bash
# 备份
git mv backend/api/routes/events.py backup/
git mv backend/api/routes/games.py backup/

# 重命名V2版本
git mv backend/api/routes/events_v2.py backend/api/routes/events.py
git mv backend/api/routes/games_v2.py backend/api/routes/games.py
```

---

### 6. 技术负债清理优先级（更新版）

| 优先级 | 问题 | 影响 | 工作量 | 建议时间 | 负责人 |
|--------|------|------|--------|----------|--------|
| **P0** | Legacy API清理 | 安全风险 | 1周 | 立即 | 后端 |
| **P0** | common_params表game_gid迁移 | 数据一致性 | 1周 | 1-2周 | 后端 |
| **P1** | utils_legacy清理 | 维护成本 | 2周 | 3-4周 | 后端 |
| **P1** | HQL生成器V1清理 | 代码冗余 | 2周 | 1个月后 | 后端 |
| **P2** | DDD架构迁移（events/games） | 架构优化 | 4周 | 2个月后 | 后端 |
| **P2** | 文档完善 | 开发体验 | 1周 | 持续 | 文档 |

**时间线**：

```
Week 1-2:  P0 - Legacy API清理
Week 3-4:  P0 - common_params表迁移
Week 5-8:  P1 - utils_legacy清理
Week 9-12: P1 - HQL生成器V1清理
Week 13-20:P2 - DDD架构迁移
持续:     P2 - 文档完善
```

---

## 未来规划

### 短期规划（1-3个月）

- [ ] 完善HQL生成器（支持更多模式）
- [ ] 优化Canvas系统（拖拽优化）
- [ ] 增加单元测试覆盖率（>90%）
- [ ] 完善API文档（Swagger）

### 中期规划（3-6个月）

- [ ] 支持多数据源（MySQL/PostgreSQL）
- [ ] 实现任务调度（定时生成HQL）
- [ ] 增加性能监控（APM）
- [ ] 优化前端性能（虚拟化）

### 长期规划（6-12个月）

- [ ] 微服务架构拆分
- [ ] 支持分布式部署
- [ ] 实现多租户支持
- [ ] 增加AI辅助功能

---

**文档版本**: 8.0
**最后更新**: 2026-02-23
**维护者**: Event2Table Development Team
