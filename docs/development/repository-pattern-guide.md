# Repository Pattern Guide

> **版本**: 1.0 | **最后更新**: 2026-03-03
>
> 本文档详细说明 Event2Table 项目中 Repository 模式的使用方法和最佳实践。

---

## 目录

- [概述](#概述)
- [GenericRepository 基类](#genericrepository-基类)
- [创建自定义 Repository](#创建自定义-repository)
- [Entity 架构集成](#entity-架构集成)
- [缓存策略](#缓存策略)
- [Service 层集成](#service-层集成)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)

---

## 概述

### 什么是 Repository 模式？

Repository 模式是一种数据访问设计模式，它将数据访问逻辑与业务逻辑分离。

**核心优势**：
- ✅ **数据访问集中化**：所有 SQL 查询在一个地方
- ✅ **易于测试**：可以 Mock Repository 进行单元测试
- ✅ **缓存策略统一**：在 Repository 层统一管理缓存
- ✅ **类型安全**：返回 Entity 对象而非字典

### 架构层级

```
┌─────────────────────────────────────────────────────┐
│         API Layer (HTTP + GraphQL端点)               │
│  - 处理HTTP请求/响应                                  │
│  - 参数解析和验证 (Pydantic Entity)                   │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│           Service Layer (业务逻辑)                   │
│  - 实现业务逻辑                                       │
│  - 协调多个Repository                                │
│  - 缓存管理 (@cached, @cache_invalidate)             │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│        Repository Layer (数据访问)                   │
│  - GenericRepository基类                             │
│  - 封装数据访问逻辑                                   │
│  - CRUD操作                                          │
│  - 返回Entity对象 (而非Dict) ⭐                       │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│      Entity Layer (统一数据模型) ⭐                    │
│  - Pydantic Entity: backend/models/entities.py       │
│  - 单一真相来源 (Schema + Domain Model)              │
│  - 自动输入验证                                       │
│  - 序列化/反序列化                                    │
└─────────────────────────────────────────────────────┘
```

---

## GenericRepository 基类

### 核心功能

`GenericRepository` 提供了通用的 CRUD 操作：

```python
from backend.core.data_access import GenericRepository

class GenericRepository:
    """通用仓储模式实现"""

    ALLOWED_TABLES: set = {
        "games", "log_events", "event_params",
        "event_categories", "flow_templates", "event_nodes",
        # ... 更多表
    }

    def __init__(
        self,
        table_name: str,
        primary_key: str = "id",
        enable_cache: bool = False,
        cache_timeout: int = 60,
    ):
        """
        初始化仓储

        Args:
            table_name: 表名（必须在 ALLOWED_TABLES 中）
            primary_key: 主键字段名（默认为'id'）
            enable_cache: 是否启用缓存（默认False）
            cache_timeout: 缓存超时时间（秒，默认60）
        """
```

### CRUD 操作

**1. 查询操作**

```python
# 按ID查询
record = repo.find_by_id(1)
# SELECT * FROM {table} WHERE id = ?

# 按字段查询
record = repo.find_by_field("gid", 10000147)
# SELECT * FROM {table} WHERE gid = ?

# 按条件查询
records = repo.find_where(
    conditions={"game_gid": 10000147, "status": "active"},
    order_by="created_at DESC",
    limit=10
)
# SELECT * FROM {table} WHERE game_gid = ? AND status = ? ORDER BY created_at DESC LIMIT 10

# 查询所有
records = repo.find_all()
# SELECT * FROM {table}

# 批量查询
records = repo.find_by_ids([1, 2, 3])
# SELECT * FROM {table} WHERE id IN (1, 2, 3)
```

**2. 创建操作**

```python
# 创建单条记录
record_id = repo.create({
    "gid": "10000147",
    "name": "Game Name",
    "ods_db": "ieu_ods"
})
# INSERT INTO {table} (gid, name, ods_db) VALUES (?, ?, ?)

# 批量创建
record_ids = repo.create_batch([
    {"gid": "10000147", "name": "Game 1"},
    {"gid": "10000148", "name": "Game 2"}
])
# INSERT INTO {table} (gid, name) VALUES (?, ?), (?, ?)
```

**3. 更新操作**

```python
# 按ID更新
updated = repo.update(1, {"name": "Updated Name"})
# UPDATE {table} SET name = ? WHERE id = ?

# 批量更新
count = repo.update_batch(
    ids=[1, 2, 3],
    updates={"status": "inactive"}
)
# UPDATE {table} SET status = ? WHERE id IN (1, 2, 3)
```

**4. 删除操作**

```python
# 按ID删除
deleted = repo.delete(1)
# DELETE FROM {table} WHERE id = ?

# 批量删除
count = repo.delete_batch([1, 2, 3])
# DELETE FROM {table} WHERE id IN (1, 2, 3)
```

### 统计操作

```python
# 计数
count = repo.count()
# SELECT COUNT(*) FROM {table}

count = repo.count_where({"game_gid": 10000147})
# SELECT COUNT(*) FROM {table} WHERE game_gid = ?

# 检查存在性
exists = repo.exists(1)
# SELECT 1 FROM {table} WHERE id = ? LIMIT 1

exists = repo.exists_where({"gid": "10000147"})
# SELECT 1 FROM {table} WHERE gid = ? LIMIT 1
```

---

## 创建自定义 Repository

### 基本结构

```python
from typing import Optional, List, Dict, Any
from backend.core.data_access import GenericRepository
from backend.core.utils.converters import fetch_one_as_dict, fetch_all_as_dict
from backend.models.entities import GameEntity

class GameRepository(GenericRepository):
    """
    游戏仓储类

    继承 GenericRepository 并添加游戏特定的查询方法
    返回 GameEntity 而非字典，确保类型安全
    """

    def __init__(self):
        """初始化游戏仓储，启用缓存"""
        super().__init__(
            table_name="games",
            primary_key="id",
            enable_cache=True,
            cache_timeout=120  # 2分钟缓存
        )

    def find_by_gid(self, gid: int) -> Optional[GameEntity]:
        """
        根据业务GID查询游戏

        Args:
            gid: 游戏业务GID

        Returns:
            GameEntity, 不存在返回None
        """
        query = "SELECT * FROM games WHERE gid = ?"
        row = fetch_one_as_dict(query, (gid,))
        return GameEntity(**row) if row else None

    def find_all(self) -> List[GameEntity]:
        """查询所有游戏"""
        query = "SELECT * FROM games ORDER BY name"
        rows = fetch_all_as_dict(query)
        return [GameEntity(**row) for row in rows]

    def get_all_with_event_count(self) -> List[GameEntity]:
        """
        获取所有游戏及其事件数量

        Returns:
            GameEntity列表，包含事件数量统计
        """
        query = """
            SELECT
                g.*,
                COUNT(DISTINCT le.id) as event_count
            FROM games g
            LEFT JOIN log_events le ON g.gid = le.game_gid
            GROUP BY g.id
            ORDER BY g.name
        """
        rows = fetch_all_as_dict(query)
        return [GameEntity(**row) for row in rows]
```

### 命名规范

**Repository 类名**：
- ✅ 单数形式：`GameRepository`, `EventRepository`
- ❌ 复数形式：`GamesRepository`（不推荐）

**方法名**：
- ✅ `find_by_*` - 查询单条：`find_by_gid()`, `find_by_name()`
- ✅ `find_all` - 查询所有
- ✅ `get_*_with_*` - 查询带关联数据：`get_all_with_event_count()`
- ✅ `exists_by_*` - 检查存在：`exists_by_gid()`

### 安全验证

所有 Repository 都自动继承安全验证：

```python
# ✅ 自动验证表名（白名单）
repo = GameRepository()  # "games" 在 ALLOWED_TABLES 中

# ❌ 会抛出异常
repo = GenericRepository("invalid_table")  # ValueError: Invalid table name

# ✅ 自动验证字段名
record = repo.find_by_field("gid", 10000147)  # "gid" 是有效字段

# ❌ 会抛出异常
record = repo.find_by_field("invalid_field", 100)  # ValueError: Invalid column name
```

---

## Entity 架构集成

### Entity 定义

```python
# backend/models/entities.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
import html

class GameEntity(BaseModel):
    """
    游戏实体 - 全局唯一的模型定义

    所有模块 (GameService/GameRepository/API) 都使用这个模型
    """
    # 主键
    id: Optional[int] = None  # 数据库自增ID

    # 业务字段
    gid: str = Field(..., min_length=1, max_length=50, description="游戏业务GID")
    name: str = Field(..., min_length=1, max_length=100, description="游戏名称")
    ods_db: str = Field(..., pattern=r'^(ieu_ods|overseas_ods)$', description="ODS数据库")
    description: Optional[str] = Field(None, description="游戏描述")
    dwd_prefix: str = Field("dwd", description="DWD表前缀")

    # 元数据
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # 关联数据
    event_count: Optional[int] = Field(0, description="事件数量统计")

    model_config = {"from_attributes": True}

    @field_validator('name')
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """防止XSS攻击"""
        return html.escape(v.strip())
```

### Repository 返回 Entity

```python
class GameRepository(GenericRepository):
    """游戏仓储类"""

    def find_by_gid(self, gid: int) -> Optional[GameEntity]:
        """返回 GameEntity 对象"""
        query = "SELECT * FROM games WHERE gid = ?"
        row = fetch_one_as_dict(query, (gid,))
        return GameEntity(**row) if row else None  # ⭐ 返回Entity

    def find_all(self) -> List[GameEntity]:
        """返回 GameEntity 列表"""
        query = "SELECT * FROM games ORDER BY name"
        rows = fetch_all_as_dict(query)
        return [GameEntity(**row) for row in rows]  # ⭐ 返回Entity列表
```

### Service 使用 Entity

```python
class GameService:
    """游戏业务服务"""

    def __init__(self):
        self.game_repo = GameRepository()

    @cached_service("game:{gid}", ttl_l1=60, ttl_l2=300, key_params=['gid'])
    def get_game_by_gid(self, gid: int) -> GameEntity:
        """
        获取游戏

        Returns:
            GameEntity 对象
        """
        return self.game_repo.find_by_gid(gid)  # ⭐ 直接使用Entity

    def create_game(self, game_data: GameEntity) -> GameEntity:
        """
        创建游戏

        Args:
            game_data: GameEntity 对象

        Returns:
            创建的 GameEntity 对象
        """
        # 检查gid唯一性
        existing = self.game_repo.find_by_gid(game_data.gid)
        if existing:
            raise ValueError(f"Game gid {game_data.gid} already exists")

        # 创建游戏 (使用 model_dump() 转换为字典)
        game_id = self.game_repo.create(game_data.model_dump())

        # 返回创建的Entity
        return self.game_repo.find_by_id(game_id)
```

### API 使用 Entity

```python
from backend.models.entities import GameEntity
from backend.services.games.game_service import GameService

@games_bp.route('/api/games', methods=['POST'])
def create_game():
    """创建游戏API"""
    try:
        # 1. 解析和验证请求参数
        data = request.get_json()
        game_data = GameEntity(**data)  # ⭐ 使用Entity验证

        # 2. 调用Service层
        service = GameService()
        game = service.create_game(game_data)

        # 3. 返回响应
        return json_success_response(
            data=game.model_dump(),  # ⭐ Entity.model_dump()
            message="Game created successfully"
        )

    except ValidationError as e:
        return json_error_response(f"Validation error: {e}", status_code=400)
```

### Entity 架构优势

| 方面 | 旧架构 (Dict) | 新架构 (Entity) |
|------|---------------|----------------|
| **模型数量** | 3套 (Domain/Schema/Dict) | 1套统一Entity ✅ |
| **Repository返回** | Dict[str, Any] | Entity对象 ✅ |
| **类型安全** | 部分 | 完全 (Pydantic) ✅ |
| **输入验证** | Schema单独验证 | Entity自动验证 ✅ |
| **代码量** | 216行 | 130行 (-40%) ✅ |

---

## 缓存策略

### Repository 层缓存

```python
class GameRepository(GenericRepository):
    def __init__(self):
        """启用Repository层缓存"""
        super().__init__(
            table_name="games",
            primary_key="id",
            enable_cache=True,      # ⭐ 启用缓存
            cache_timeout=120       # ⭐ 2分钟TTL
        )
```

**缓存行为**：
- `find_by_id()` - 自动缓存结果
- `find_by_field()` - 不缓存（自定义查询）
- `find_all()` - 不缓存（数据量大）

### Service 层缓存

```python
from backend.core.cache.decorators import cached_service, invalidate_cache

class GameService:
    """游戏业务服务"""

    @cached_service(
        "game:{gid}",              # ⭐ 缓存键模板
        ttl_l1=60,                 # ⭐ L1缓存60秒
        ttl_l2=300,                # ⭐ L2缓存5分钟
        key_params=['gid']         # ⭐ 从参数提取gid
    )
    def get_game_by_gid(self, gid: int) -> GameEntity:
        """获取游戏（带缓存）"""
        return self.game_repo.find_by_gid(gid)

    @invalidate_cache("game:{gid}", key_params=['gid'])
    @invalidate_cache("games:list")  # ⭐ 同时清理列表缓存
    def update_game(self, gid: int, data: dict) -> GameEntity:
        """更新游戏（自动清理缓存）"""
        game = self.game_repo.update_by_gid(gid, data)
        return game
```

### 缓存最佳实践

**读操作 - 使用缓存**：
```python
# ✅ 正确：读操作使用缓存
@cached_service("events:{game_gid}", ttl_l1=60, ttl_l2=300)
def get_events(self, game_gid: int):
    return self.event_repo.find_by_game_gid(game_gid)
```

**写操作 - 清理缓存**：
```python
# ✅ 正确：写操作清理缓存
@invalidate_cache("events:{game_gid}")
def create_event(self, game_gid: int, data: dict):
    return self.event_repo.create(data)
```

**TTL 设置建议**：
- 静态数据（系统配置）：3600-7200秒
- 中等变化（游戏列表）：1800秒
- 实时数据（在线用户）：60秒

---

## Service 层集成

### 完整示例

```python
from backend.models.repositories.games import GameRepository
from backend.models.repositories.events import EventRepository
from backend.models.entities import GameEntity, EventEntity
from backend.core.cache.decorators import cached_service, invalidate_cache
from typing import List

class GameService:
    """游戏业务服务"""

    def __init__(self):
        """初始化服务，注入Repository"""
        self.game_repo = GameRepository()
        self.event_repo = EventRepository()

    @cached_service("games:list", ttl_l1=120, ttl_l2=600)
    def get_all_games(self) -> List[GameEntity]:
        """获取所有游戏（带缓存）"""
        return self.game_repo.find_all()

    @cached_service("game:{gid}", ttl_l1=60, ttl_l2=300, key_params=['gid'])
    def get_game_by_gid(self, gid: int) -> GameEntity:
        """根据GID获取游戏"""
        game = self.game_repo.find_by_gid(gid)
        if not game:
            raise ValueError(f"Game {gid} not found")
        return game

    @invalidate_cache("games:list")
    @invalidate_cache("game:{gid}", key_params=['gid'])
    def create_game(self, game_data: GameEntity) -> GameEntity:
        """
        创建游戏

        业务逻辑：
        1. 验证gid唯一性
        2. 创建游戏
        3. 清理缓存
        """
        # 检查gid是否已存在
        existing = self.game_repo.find_by_gid(game_data.gid)
        if existing:
            raise ValueError(f"Game gid {game_data.gid} already exists")

        # 创建游戏
        game_id = self.game_repo.create(game_data.model_dump())

        # 返回创建的游戏
        return self.game_repo.find_by_id(game_id)

    @invalidate_cache("games:list")
    @invalidate_cache("game:{gid}", key_params=['gid'])
    def update_game(self, gid: int, data: dict) -> GameEntity:
        """更新游戏"""
        game = self.game_repo.update_by_gid(gid, data)
        if not game:
            raise ValueError(f"Game {gid} not found")
        return game

    @invalidate_cache("games:list")
    @invalidate_cache("game:{gid}", key_params=['gid'])
    def delete_game(self, gid: int) -> None:
        """删除游戏"""
        # 检查关联事件
        events = self.event_repo.find_by_game_gid(gid)
        if events:
            raise ValueError(f"Cannot delete game with {len(events)} events")

        # 删除游戏
        success = self.game_repo.delete_by_gid(gid)
        if not success:
            raise ValueError(f"Game {gid} not found")
```

---

## 最佳实践

### 1. Repository 设计原则

**单一职责**：
```python
# ✅ 正确：每个Repository只负责一个表
class GameRepository(GenericRepository):
    """游戏仓储"""
    pass

class EventRepository(GenericRepository):
    """事件仓储"""
    pass

# ❌ 错误：一个Repository负责多个表
class GameAndEventRepository(GenericRepository):
    """游戏和事件仓储"""
    pass
```

**返回Entity对象**：
```python
# ✅ 正确：返回Entity
def find_by_gid(self, gid: int) -> Optional[GameEntity]:
    row = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (gid,))
    return GameEntity(**row) if row else None

# ❌ 错误：返回字典
def find_by_gid(self, gid: int) -> Optional[Dict]:
    return fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (gid,))
```

### 2. 缓存策略

**读写分离**：
```python
# ✅ 读操作：使用缓存
@cached_service("game:{gid}")
def get_game(self, gid: int):
    return self.game_repo.find_by_gid(gid)

# ✅ 写操作：清理缓存
@invalidate_cache("game:{gid}")
def update_game(self, gid: int, data: dict):
    return self.game_repo.update_by_gid(gid, data)
```

**TTL 合理设置**：
```python
# ✅ 静态数据：长TTL
@cached_service("system:config", ttl_l1=3600, ttl_l2=7200)
def get_config(self):
    pass

# ✅ 中等变化：中TTL
@cached_service("games:list", ttl_l1=120, ttl_l2=600)
def get_games(self):
    pass

# ✅ 实时数据：短TTL
@cached_service("online:users", ttl_l1=30, ttl_l2=60)
def get_online_users(self):
    pass
```

### 3. 错误处理

```python
# ✅ 正确：Service层抛出有意义的异常
def get_game_by_gid(self, gid: int) -> GameEntity:
    game = self.game_repo.find_by_gid(gid)
    if not game:
        raise ValueError(f"Game {gid} not found")
    return game

# ✅ 正确：API层捕获异常并返回HTTP状态码
@games_bp.route('/api/games/<int:gid>')
def get_game(gid: int):
    try:
        service = GameService()
        game = service.get_game_by_gid(gid)
        return json_success_response(data=game.model_dump())
    except ValueError as e:
        return json_error_response(str(e), status_code=404)
```

### 4. 参数验证

```python
# ✅ 正确：使用Entity自动验证
def create_game(self, game_data: GameEntity) -> GameEntity:
    # Entity已经验证过，直接使用
    game_id = self.game_repo.create(game_data.model_dump())
    return self.game_repo.find_by_id(game_id)

# ❌ 错误：手动验证每个字段
def create_game(self, name: str, gid: str, ods_db: str):
    if not name or len(name) > 100:
        raise ValueError("Invalid name")
    if not gid or not gid.isdigit():
        raise ValueError("Invalid gid")
    # ... 更多验证
```

---

## 常见问题

### Q1: 什么时候需要创建自定义Repository？

**A**: 当你需要以下功能时：

1. **复杂查询**：涉及多表JOIN
2. **特定业务方法**：如 `get_all_with_event_count()`
3. **特殊缓存逻辑**：需要自定义缓存策略
4. **返回Entity对象**：而非字典

**示例**：
```python
# 需要自定义Repository的情况
class GameRepository(GenericRepository):
    def get_all_with_event_count(self) -> List[GameEntity]:
        """复杂查询：JOIN多表"""
        query = """
            SELECT g.*, COUNT(le.id) as event_count
            FROM games g
            LEFT JOIN log_events le ON g.gid = le.game_gid
            GROUP BY g.id
        """
        rows = fetch_all_as_dict(query)
        return [GameEntity(**row) for row in rows]
```

### Q2: Repository层缓存 vs Service层缓存？

**A**: 两者职责不同：

| 特性 | Repository层缓存 | Service层缓存 |
|------|------------------|---------------|
| **粒度** | 单条记录（按ID） | 业务对象（按GID） |
| **缓存键** | `table:id:1` | `game:{gid}` |
| **控制** | 自动缓存find_by_id | 手动装饰器控制 |
| **适用** | 简单CRUD | 复杂业务逻辑 |

**推荐策略**：
- Repository层：启用缓存用于简单的 `find_by_id()`
- Service层：使用装饰器用于复杂业务方法

### Q3: 如何处理事务？

**A**: 在Service层处理事务：

```python
def create_event_with_params(self, event_data: EventEntity, params: List[ParamEntity]):
    """创建事件及其参数（事务）"""
    conn = get_db_connection()

    try:
        conn.execute("BEGIN TRANSACTION")

        # 创建事件
        event_id = self.event_repo.create(event_data.model_dump())

        # 创建参数
        for param in params:
            param_data = param.model_dump()
            param_data['event_id'] = event_id
            self.param_repo.create(param_data)

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
```

### Q4: 如何优化查询性能？

**A**: 多层优化策略：

**1. 数据库层**：
```python
# 添加索引
CREATE INDEX idx_events_game_gid ON log_events(game_gid);
```

**2. Repository层**：
```python
# 使用批量查询
events = event_repo.find_by_ids([1, 2, 3])  # 一次查询

# 而非
for event_id in [1, 2, 3]:
    event = event_repo.find_by_id(event_id)  # 三次查询
```

**3. Service层**：
```python
# 使用缓存
@cached_service("events:{game_gid}", ttl_l1=60)
def get_events(self, game_gid: int):
    return self.event_repo.find_by_game_gid(game_gid)
```

**4. 避免N+1查询**：
```python
# ❌ 错误：N+1查询
def get_games_with_events(self):
    games = self.game_repo.find_all()
    for game in games:
        game['events'] = self.event_repo.find_by_game_gid(game['gid'])  # N次查询

# ✅ 正确：一次查询
def get_games_with_events(self):
    query = """
        SELECT g.*, COUNT(e.id) as event_count
        FROM games g
        LEFT JOIN log_events e ON g.gid = e.game_gid
        GROUP BY g.id
    """
    return fetch_all_as_dict(query)
```

---

## 相关文档

- **[架构设计文档](architecture.md)** - 分层架构设计
- **[API文档](../api/README.md)** - REST API和GraphQL API文档
- **[缓存系统文档](../cache/README.md)** - 缓存系统详解
- **[Entity架构迁移指南](ENTITY-ARCHITECTURE-MIGRATION-GUIDE.md)** - Entity架构说明

### API开发相关

- **游戏API**: [Games API](../api/GAMES-API.md)
- **事件API**: [Events API](../api/EVENTS-API.md)
- **参数API**: [Parameters API](../api/PARAMETERS-API.md)
- **GraphQL API**: [GraphQL API](../api/GRAPHQL_API.md)

### 经验文档

- **[API设计模式](../lessons-learned/api-design-patterns.md)** - 分层架构、错误处理
- **[性能模式](../lessons-learned/performance-patterns.md)** - 缓存、N+1查询优化

---

**文档版本**: 1.0
**最后更新**: 2026-03-03
**维护者**: Event2Table Development Team
