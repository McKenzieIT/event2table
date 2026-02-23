# API设计模式

> **来源**: 整合了多个报告的API设计相关经验
> **最后更新**: 2026-02-24
> **维护**: 每次API设计问题修复后立即更新

---

## 分层架构 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 2次 | **来源**: [架构设计文档](../development/architecture.md), [OPTIMIZATION_LESSONS_LEARNED.md](../archive/2026-02/optimization-reports/OPTIMIZATION_LESSONS_LEARNED.md)

### 四层架构设计

```
┌─────────────────────────────────────────────────────┐
│              API Layer (HTTP端点)                    │
│  backend/api/routes/                                 │
│  - 处理HTTP请求/响应                                  │
│  - 参数解析和验证                                     │
│  - 调用Service层                                      │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│           Service Layer (业务逻辑)                   │
│  backend/services/                                   │
│  - 实现业务逻辑                                       │
│  - 协调多个Repository                                │
│  - 事务管理                                           │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│        Repository Layer (数据访问)                   │
│  backend/models/repositories/                        │
│  - 封装数据访问逻辑                                   │
│  - CRUD操作                                          │
│  - 复杂查询                                           │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│           Schema Layer (数据验证)                    │
│  backend/models/schemas.py                           │
│  - Pydantic模型定义                                   │
│  - 输入验证                                           │
│  - 序列化/反序列化                                    │
└─────────────────────────────────────────────────────┘
```

### 各层职责

**1. Schema层（数据验证）**:
```python
# backend/models/schemas.py
from pydantic import BaseModel, Field

class GameCreate(BaseModel):
    """游戏创建Schema"""
    gid: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    ods_db: Literal["ieu_ods", "overseas_ods"]

    @validator("name")
    def sanitize_name(cls, v):
        """防止XSS攻击"""
        return html.escape(v.strip())
```

**2. Repository层（数据访问）**:
```python
# backend/models/repositories/games.py
class GameRepository(GenericRepository):
    """游戏仓储类"""

    def find_by_gid(self, gid: int) -> Optional[Dict[str, Any]]:
        """根据业务GID查询游戏"""
        query = "SELECT * FROM games WHERE gid = ?"
        return fetch_one_as_dict(query, (gid,))

    def get_all_with_event_count(self) -> List[Dict[str, Any]]:
        """获取所有游戏及其事件数量"""
        query = """
            SELECT g.*, COUNT(DISTINCT le.id) as event_count
            FROM games g
            LEFT JOIN log_events le ON g.id = le.game_id
            GROUP BY g.id
        """
        return fetch_all_as_dict(query)
```

**3. Service层（业务逻辑）**:
```python
# backend/services/games/game_service.py
class GameService:
    """游戏业务服务"""

    def __init__(self):
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
        # 检查gid是否已存在
        existing = self.game_repo.find_by_gid(game_data.gid)
        if existing:
            raise ValueError(f"Game gid {game_data.gid} already exists")

        # 创建游戏
        game_id = self.game_repo.create(game_data.dict())

        return self.game_repo.find_by_id(game_id)
```

**4. API层（HTTP端点）**:
```python
# backend/api/routes/dwd_generator/games.py
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
```

### 架构原则

**关注点分离**:
- ✅ API层只处理HTTP相关逻辑
- ✅ Service层只处理业务逻辑
- ✅ Repository层只处理数据访问
- ✅ Schema层只处理数据验证

**禁止跨越层调用**:
- ❌ API层直接访问数据库
- ❌ API层直接调用Repository
- ❌ Service层访问HTTP请求对象

### 代码审查清单

- [ ] API层是否只调用Service层？
- [ ] Service层是否只调用Repository层？
- [ ] 是否使用Pydantic Schema验证输入？
- [ ] 错误处理是否适当（400/404/409/500）？

### 相关经验

- [数据库模式 - game_gid迁移](./database-patterns.md#game_gid迁移) - 数据访问模式
- [安全要点 - 输入验证](./security-essentials.md#输入验证) - Schema验证

---

## 错误处理 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 2次 | **来源**: [phase2-lessons-learned.md](../archive/2026-02/testing-reports/phase2-lessons-learned.md)

### 错误处理模式

**提供具体可操作的错误消息**:
```python
# ❌ 错误：通用错误消息
return json_error_response("Failed to create game", status_code=500)

# ✅ 正确：具体可操作的错误消息
return json_error_response(
    "Game gid 10000147 already exists. Use a different gid or update the existing game.",
    status_code=409
)
```

**根据HTTP状态码提供针对性指导**:
```python
# 400 Bad Request - 输入验证失败
if not game_name:
    return json_error_response(
        "Game name is required. Must be 1-100 characters.",
        status_code=400
    )

# 404 Not Found - 资源不存在
game = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (game_gid,))
if not game:
    return json_error_response(
        f"Game {game_gid} not found. Check the gid or create the game first.",
        status_code=404
    )

# 409 Conflict - 资源冲突
existing = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (game_gid,))
if existing:
    return json_error_response(
        f"Game {game_gid} already exists. Use PUT to update or DELETE to remove.",
        status_code=409
    )

# 500 Internal Server Error - 服务器错误
try:
    # 业务逻辑
except Exception as e:
    logger.error(f"Error creating game: {e}")  # 详细日志
    return json_error_response(
        "Internal server error. Please try again later or contact support.",
        status_code=500
    )
```

### 用户友好错误消息

**错误消息分类**:
1. **验证错误** (400) - 告诉用户输入有什么问题
2. **未找到错误** (404) - 告诉用户资源不存在以及如何创建
3. **冲突错误** (409) - 告诉用户资源冲突以及如何解决
4. **服务器错误** (500) - 告诉用户这是服务器问题，建议重试

### 代码审查清单

- [ ] 错误消息是否具体可操作？
- [ ] 错误消息是否包含解决方案？
- [ ] HTTP状态码是否正确？
- [ ] 详细错误是否记录到日志？

### 相关经验

- [安全要点 - 异常信息脱敏](./security-essentials.md#异常信息脱敏) - 错误响应安全
- [测试指南 - E2E测试](./testing-guide.md#e2e测试) - API错误测试

---

## GraphQL实施经验 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [GraphQL实施报告](../archive/2026-02/optimization-reports/)

### GraphQL vs REST

**何时使用GraphQL**:
- ✅ 需要灵活的数据查询
- ✅ 客户端需要不同的数据组合
- ✅ 减少API请求次数

**何时使用REST**:
- ✅ 简单的CRUD操作
- ✅ 标准化的资源操作
- ✅ 缓存优先的场景

### GraphQL最佳实践

**Schema设计**:
```python
# backend/gql_api/schema.py
from graphene import ObjectType, Schema, String, Int, List

class Game(ObjectType):
    gid = String(required=True)
    name = String(required=True)
    ods_db = String(required=True)

class Query(ObjectType):
    all_games = List(Game)

    def resolve_all_games(root, info):
        return fetch_all_as_dict("SELECT * FROM games")
```

**Resolver优化**:
```python
# ✅ 使用DataLoader解决N+1问题
from promise.dataloader import DataLoader

def batch_load_games(keys):
    """批量加载游戏"""
    games = fetch_all_as_dict(
        f"SELECT * FROM games WHERE gid IN ({','.join(['?']*len(keys))})",
        keys
    )
    return games

game_loader = DataLoader(batch_load_games)

def resolve_event(root, info):
    # 使用DataLoader批量加载
    return game_loader.load(root.game_gid)
```

### 代码审查清单

- [ ] GraphQL Schema是否清晰？
- [ ] 是否使用DataLoader解决N+1问题？
- [ ] 是否有适当的错误处理？
- [ ] 是否有查询深度限制？

### 相关经验

- [分层架构](#分层架构) - GraphQL分层设计
- [性能模式 - N+1查询优化](./performance-patterns.md#n1查询优化) - DataLoader优化

---

## Service层缓存集成 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [FINAL_OPTIMIZATION_REPORT.md Section 2.1](../archive/2026-02/optimization-reports/FINAL_OPTIMIZATION_REPORT.md)

### 缓存装饰器使用

**使用@cached装饰器**:
```python
from backend.core.cache.decorators import cached

class GameService:
    @cached('games.list', timeout=120)
    def get_all_games(self, include_stats: bool = False):
        """获取所有游戏（带缓存）"""
        # 自动缓存结果
        pass

    @cached('games.detail', timeout=300)
    def get_game_by_gid(self, game_gid: int):
        """根据GID获取游戏（带缓存）"""
        # 自动缓存结果
        pass
```

### 缓存失效调用

```python
from backend.core.cache.invalidator import CacheInvalidator

def create_game(self, game_data):
    # 创建游戏
    game = self.game_repo.create(game_data)

    # ✅ 失效相关缓存
    CacheInvalidator.invalidate_key('games.list')
    logger.info(f"游戏创建成功，已失效缓存: gid={game['gid']}")

    return game
```

### 代码审查清单

- [ ] Service层是否使用@cached装饰器？
- [ ] 创建/更新/删除操作后是否清理缓存？
- [ ] 缓存失效是否记录日志？
- [ ] 缓存TTL是否合理（5-10分钟）？

---

## API缓存失效策略 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [FINAL_OPTIMIZATION_REPORT.md Section 2.2](../archive/2026-02/optimization-reports/FINAL_OPTIMIZATION_REPORT.md)

### Games API缓存失效

```python
# 创建游戏
execute_write("INSERT INTO games ...")
CacheInvalidator.invalidate_key("dashboard_statistics")

# 更新游戏
execute_write("UPDATE games ...")
CacheInvalidator.invalidate_key("games.list")
CacheInvalidator.invalidate_key("dashboard_statistics")

# 删除游戏
execute_cascade_delete(game, impact)
CacheInvalidator.invalidate_key("games.list")
CacheInvalidator.invalidate_key("dashboard_statistics")
```

### Events API缓存失效

```python
# 创建事件
execute_write("INSERT INTO log_events ...")
CacheInvalidator.invalidate_key("dashboard_statistics")

# 更新事件
execute_write("UPDATE log_events ...")
CacheInvalidator.invalidate_pattern("events.list:*")

# 删除事件
execute_write("DELETE FROM log_events ...")
CacheInvalidator.invalidate_pattern("events.list:*")
```

### 代码审查清单

- [ ] 所有修改数据的API是否清理缓存？
- [ ] 是否使用了正确的缓存失效方法？
- [ ] Dashboard统计缓存是否失效？
- [ ] 是否记录缓存失效日志？

---

---

## DDD架构实施 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [架构设计文档](../development/architecture.md), [OPTIMIZATION_LESSONS_LEARNED.md](../archive/2026-02/optimization-reports/OPTIMIZATION_LESSONS_LEARNED.md)

### 领域驱动设计（DDD）原则

**战略设计**:
- **领域** - 业务问题的范围
- **子域** - 领域的特定部分
- **限界上下文** - 特定模型的边界
- **上下文映射** - 不同限界上下文之间的关系

**战术设计**:
- **实体** - 有唯一标识的对象
- **值对象** - 无标识的对象
- **聚合** - 一组相关的实体和值对象
- **领域服务** - 不属于实体的业务逻辑
- **仓储** - 数据访问的抽象

### DDD分层架构

```
┌─────────────────────────────────────────────────────┐
│           User Interface (用户界面)                  │
│  React Components + API Routes                       │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│           Application Layer (应用层)                 │
│  Services (GameService, EventService)               │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│           Domain Layer (领域层)                      │
│  Domain Models + Business Logic                     │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│         Infrastructure Layer (基础设施层)            │
│  Repositories + Database + Cache                    │
└─────────────────────────────────────────────────────┘
```

### 实施经验

**1. 领域模型设计**:
```python
# backend/domain/models/game.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Game:
    """游戏领域模型"""
    gid: int
    name: str
    ods_db: str
    description: Optional[str] = None

    def get_table_name(self) -> str:
        """获取ODS表名"""
        return f"{self.ods_db}.ods_{self.gid}_all_view"

    def validate_gid(self) -> bool:
        """验证GID格式"""
        return 10000000 <= self.gid <= 99999999
```

**2. 领域服务**:
```python
# backend/domain/services/game_validation_service.py
class GameValidationService:
    """游戏验证领域服务"""

    def validate_unique_gid(self, game_gid: int) -> bool:
        """验证GID唯一性"""
        existing = fetch_one_as_dict(
            "SELECT gid FROM games WHERE gid = ?",
            (game_gid,)
        )
        return existing is None

    def validate_table_exists(self, table_name: str) -> bool:
        """验证ODS表是否存在"""
        # 验证逻辑
        pass
```

**3. 仓储接口**:
```python
# backend/domain/repositories/game_repository.py
from abc import ABC, abstractmethod

class IGameRepository(ABC):
    """游戏仓储接口"""

    @abstractmethod
    def find_by_gid(self, gid: int) -> Optional[Game]:
        """根据GID查找游戏"""
        pass

    @abstractmethod
    def save(self, game: Game) -> None:
        """保存游戏"""
        pass
```

### DDD实施优势

**优势**:
- ✅ 业务逻辑集中在领域层
- ✅ 代码结构清晰，易于维护
- ✅ 领域模型与持久化解耦
- ✅ 便于测试和重构

### 代码审查清单

- [ ] 是否定义了清晰的领域模型？
- [ ] 是否使用了仓储接口抽象数据访问？
- [ ] 业务逻辑是否集中在领域服务？
- [ ] 是否遵循了限界上下文边界？

### 相关经验

- [分层架构](#分层架构) - DDD分层实现
- [数据库模式 - game_gid迁移](./database-patterns.md#game_gid迁移) - 领域模型ID设计

---

## Canvas系统设计模式 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [Canvas系统文档](../archive/2026-02/), [HQL生成器文档](../archive/2026-02/)

### Canvas系统架构

**节点类型**:
- **Table节点** - ODS表数据源
- **Join节点** - 表连接操作
- **Union节点** - 表联合操作
- **Filter节点** - 数据过滤

### 设计模式

**1. Builder模式**:
```python
class CanvasNodeBuilder:
    """Canvas节点构建器"""

    def __init__(self):
        self.node = CanvasNode()

    def with_type(self, node_type: str):
        """设置节点类型"""
        self.node.type = node_type
        return self

    def with_config(self, config: dict):
        """设置节点配置"""
        self.node.config = config
        return self

    def build(self) -> CanvasNode:
        """构建节点"""
        return self.node

# 使用示例
table_node = (CanvasNodeBuilder()
    .with_type("table")
    .with_config({"table_name": "ods_10000147_all_view"})
    .build())
```

**2. Facade模式**:
```python
class CanvasFacade:
    """Canvas系统门面"""

    def __init__(self):
        self.hql_generator = HQLGenerator()
        self.validator = CanvasValidator()
        self.cache = CanvasCache()

    def generate_hql(self, canvas: Canvas) -> str:
        """生成HQL（简化接口）"""
        # 验证Canvas
        if not self.validator.validate(canvas):
            raise ValueError("Invalid canvas")

        # 生成HQL
        hql = self.hql_generator.generate(canvas)

        # 缓存结果
        self.cache.set(canvas.id, hql)

        return hql
```

**3. Strategy模式**:
```python
class NodeStrategy(ABC):
    """节点处理策略接口"""

    @abstractmethod
    def process(self, node: CanvasNode, context: dict) -> str:
        pass

class TableNodeStrategy(NodeStrategy):
    """Table节点处理策略"""

    def process(self, node: CanvasNode, context: dict) -> str:
        table_name = node.config["table_name"]
        return f"SELECT * FROM {table_name}"

class JoinNodeStrategy(NodeStrategy):
    """Join节点处理策略"""

    def process(self, node: CanvasNode, context: dict) -> str:
        # Join处理逻辑
        pass

# 使用策略
strategies = {
    "table": TableNodeStrategy(),
    "join": JoinNodeStrategy(),
    "union": UnionNodeStrategy(),
    "filter": FilterNodeStrategy()
}

strategy = strategies[node.type]
result = strategy.process(node, context)
```

### Canvas验证规则

**验证清单**:
- [ ] Canvas是否有至少一个Table节点？
- [ ] Join节点是否有2个输入？
- [ ] Union节点是否有2个以上输入？
- [ ] 是否存在循环依赖？
- [ ] 节点配置是否完整？

### 相关经验

- [API设计模式 - 分层架构](#分层架构) - Canvas系统分层
- [重构检查清单 - HQL生成器重构经验](#hql生成器重构经验) - Canvas重构

---

## HQL生成器重构经验 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [HQL生成器重构报告](../archive/2026-02/), [优化报告](../archive/2026-02/optimization-reports/)

### 重构前的问题

**V1架构问题**:
- ❌ 单个巨型函数生成所有HQL（1000+行）
- ❌ 硬编码的字符串拼接
- ❌ 难以测试和维护
- ❌ 无法复用代码

### 重构方案：模块化V2架构

**V2模块化架构**:
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
└── templates/         # 模板管理
```

### 重构步骤

**1. 提取Builder**:
```python
# 重构前（单个函数）
def generate_hql(event, fields, conditions, mode):
    # 1000+行代码
    pass

# 重构后（Builder模式）
class HQLGenerator:
    def __init__(self):
        self.field_builder = FieldBuilder()
        self.where_builder = WhereBuilder()
        self.join_builder = JoinBuilder()

    def generate(self, events: List[Event], mode: str) -> str:
        # 清晰的生成逻辑
        if mode == "single":
            return self._generate_single(events)
        elif mode == "join":
            return self._generate_join(events)
        elif mode == "union":
            return self._generate_union(events)
```

**2. 创建数据模型**:
```python
@dataclass
class Field:
    """字段模型"""
    name: str
    type: str  # base, param, json
    json_path: Optional[str] = None
    alias: Optional[str] = None

@dataclass
class Condition:
    """条件模型"""
    field: str
    operator: str
    value: Any
    logical_op: Optional[str] = None  # AND, OR

@dataclass
class Event:
    """事件模型"""
    name: str
    table_name: str
    fields: List[Field]
    conditions: List[Condition]
```

**3. 使用模板**:
```python
# templates/hql_templates.py
SINGLE_EVENT_TEMPLATE = """
CREATE OR REPLACE VIEW {view_name} AS
SELECT
    {fields}
FROM {table_name}
{where_clause}
"""

JOIN_TEMPLATE = """
CREATE OR REPLACE VIEW {view_name} AS
SELECT
    {fields}
FROM {table_names}
{joins}
{where_clause}
"""
```

### 重构成果

**代码量对比**:
- 重构前：1000+行单个函数
- 重构后：50-100行多个小函数

**测试覆盖率**:
- 重构前：0%（无法测试）
- 重构后：95%+（可独立测试每个模块）

**维护性**:
- 重构前：修改一处影响全局
- 重构后：模块独立，易于修改

### 代码审查清单

- [ ] 函数是否<100行？
- [ ] 是否使用Builder模式？
- [ ] 是否有清晰的数据模型？
- [ ] 是否使用模板而非字符串拼接？
- [ ] 是否有完整的测试覆盖？

### 相关经验

- [重构检查清单 - TDD重构流程](#tdd重构流程) - TDD重构方法
- [API设计模式 - DDD架构实施](#ddd架构实施) - 领域模型设计

---

## 相关经验文档

- [安全要点 - SQL注入防护](./security-essentials.md#sql注入防护) - API安全
- [测试指南 - TDD实践](./testing-guide.md#tdd实践) - API测试
