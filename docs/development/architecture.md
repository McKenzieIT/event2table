# 架构设计文档

> **版本**: 7.0 | **最后更新**: 2026-02-10
>
> 本文档详细说明 Event2Table 项目的架构设计、模块职责和数据流向。

---

## 目录

- [架构概览](#架构概览)
- [分层架构说明](#分层架构说明)
- [模块职责](#模块职责)
- [Canvas系统设计](#canvas系统设计)
- [HQL生成器设计](#hql生成器设计)
- [数据流向](#数据流向)
- [技术栈说明](#技术栈说明)

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

**文档版本**: 7.0
**最后更新**: 2026-02-10
**维护者**: Event2Table Development Team
