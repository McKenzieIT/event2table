# Event2Table 架构迁移指南

> **版本**: 1.0
> **日期**: 2026-02-25
> **目标读者**: 开发团队成员、新加入的开发者

---

## 目录

1. [迁移概述](#1-迁移概述)
2. [架构对比](#2-架构对比)
3. [Entity模型使用指南](#3-entity模型使用指南)
4. [Repository层使用指南](#4-repository层使用指南)
5. [Service层使用指南](#5-service层使用指南)
6. [常见问题FAQ](#6-常见问题faq)

---

## 1. 迁移概述

### 为什么迁移?

Event2Table项目最初采用DDD(领域驱动设计)架构,但在实际开发中发现以下问题:

1. **过度设计**: DDD抽象层(聚合根、值对象、规约模式)对小规模项目过于复杂
2. **模型不一致**: 同一实体有3种表示(Domain模型/Pydantic Schema/字典),容易导致不一致
3. **开发速度慢**: 30-50%的代码用于架构而非业务逻辑
4. **学习曲线陡**: 新成员需要理解大量DDD概念

### 迁移收益

| 指标 | 改进 |
|------|------|
| 代码量 | **-40%** (216行 → 130行) |
| 模型数量 | **-66%** (3套 → 1套) |
| 开发速度 | **+30-50%** |
| 学习曲线 | **显著降低** |
| 模型一致性 | **100%保证** |

### 新架构特点

- ✅ **精简分层架构**: API → Service → Repository → Entity
- ✅ **统一Entity模型**: 单一真相来源,不可能不一致
- ✅ **Pydantic v2**: 自动验证、类型安全、IDE支持
- ✅ **Repository返回Entity**: 类型明确,自动验证
- ✅ **集成缓存管理**: 简化的缓存失效机制

---

## 2. 架构对比

### 旧DDD架构

```
┌─────────────────────────────────────────────┐
│   Presentation Layer (API Routes)           │
├─────────────────────────────────────────────┤
│   Application Layer (App Services)           │  ← DDD应用服务
├─────────────────────────────────────────────┤
│   Domain Layer (Domain Models)              │  ← DDD领域模型
│   - Aggregates (聚合根)                    │
│   - Value Objects (值对象)                 │
│   - Specifications (规约)                    │
├─────────────────────────────────────────────┤
│   Infrastructure Layer                        │
│   - Repository Implementations              │
└─────────────────────────────────────────────┘
```

**问题**:
- 3次模型转换(Domain ↔ Schema ↔ Dict)
- 字段可能不同步
- 无法利用Pydantic自动验证
- DDD概念学习成本高

### 新精简架构

```
┌─────────────────────────────────────────────┐
│   API Layer (Flask Routes)                   │
│   - HTTP请求处理                              │
│   - 参数验证 (Pydantic Entity)               │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│   Service Layer (业务逻辑)                   │
│   - 业务逻辑封装                              │
│   - 多Repository协作                          │
│   - 缓存管理                                  │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│   Repository Layer (数据访问)                │
│   - CRUD操作                                 │
│   - 返回Entity对象                            │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│   Entity Layer (数据模型)                    │
│   - Pydantic Entity定义                      │
│   - 输入验证                                  │
└─────────────────────────────────────────────┘
```

**优势**:
- 单一Entity模型
- 直接使用Pydantic验证
- 类型安全
- 简单易懂

---

## 3. Entity模型使用指南

### 定义Entity

Entity是全局唯一的模型定义,使用Pydantic v2 BaseModel:

```python
# backend/models/entities.py

from pydantic import BaseModel, Field, field_validator
from pydantic.config import ConfigDict
from typing import Optional

class GameEntity(BaseModel):
    """游戏实体"""

    # 主键
    id: Optional[int] = None

    # 业务字段
    gid: str = Field(..., min_length=1, max_length=50, description="游戏业务GID")
    name: str = Field(..., min_length=1, max_length=100, description="游戏名称")
    ods_db: str = Field(..., pattern=r'^(ieu_ods|overseas_ods)$')
    description: Optional[str] = None

    # 关联数据
    event_count: Optional[int] = Field(0, description="事件数量统计")

    @field_validator('name')
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """防止XSS攻击"""
        import html
        return html.escape(v.strip())

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True  # 允许使用alias或field name
    )
```

**关键特性**:
- `Field(...)` - 必填字段
- `Field(default)` - 可选字段
- `min_length/max_length` - 字符串长度验证
- `pattern` - 正则表达式验证
- `field_validator` - 自定义验证器
- `ConfigDict` - Pydantic v2配置方式

### 使用Entity验证

**API层**:
```python
from backend.models.entities import GameEntity

@games_bp.route('/api/games', methods=['POST'])
def create_game():
    # 自动验证请求参数
    game_data = GameEntity(**request.get_json())

    # 调用Service
    service = GameService()
    created_game = service.create_game(game_data)

    return json_success_response(data=created_game.model_dump())
```

**Service层**:
```python
class GameService:
    def create_game(self, game: GameEntity) -> GameEntity:
        # game已经通过Pydantic验证
        existing = self.game_repo.find_by_gid(game.gid)
        if existing:
            raise ValueError(f"Game {game.gid} already exists")

        game_id = self.game_repo.create(game.model_dump())
        return self.game_repo.find_by_id(game_id)
```

**序列化和反序列化**:
```python
# 字典 → Entity (反序列化)
game_dict = {"gid": "10000147", "name": "STAR001", "ods_db": "ieu_ods"}
game = GameEntity(**game_dict)  # 自动验证

# Entity → 字典 (序列化)
game_dict = game.model_dump()  # 转换为字典
game_json = game.model_dump_json()  # 转换为JSON字符串
```

### 字段别名和向后兼容

```python
class EventEntity(BaseModel):
    # 使用alias支持旧字段名
    event_name: str = Field(..., alias="name")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True  # 允许使用name或event_name
    )

# 可以使用两种方式创建
event1 = EventEntity(name="test")  # 使用alias
event2 = EventEntity(event_name="test")  # 使用field name
```

---

## 4. Repository层使用指南

### 创建Repository

所有Repository继承自`GenericRepository`:

```python
# backend/models/repositories/games.py

from backend.models.repositories import GenericRepository
from backend.models.entities import GameEntity
from backend.core.database.converters import fetch_one_as_dict, fetch_all_as_dict
from typing import Optional, List

class GameRepository(GenericRepository):
    """游戏仓储类"""

    def __init__(self):
        super().__init__(
            table_name="games",
            primary_key="id",
            enable_cache=True  # 启用缓存
        )

    def find_by_gid(self, gid: int) -> Optional[GameEntity]:
        """根据业务GID查询游戏"""
        query = "SELECT * FROM games WHERE gid = ?"
        row = fetch_one_as_dict(query, (gid,))
        return GameEntity(**row) if row else None

    def get_all_with_event_count(self) -> List[GameEntity]:
        """获取所有游戏及其事件数量"""
        query = """
            SELECT g.*, COUNT(DISTINCT le.id) as event_count
            FROM games g
            LEFT JOIN log_events le ON g.id = le.game_id
            GROUP BY g.id
        """
        rows = fetch_all_as_dict(query)
        return [GameEntity(**row) for row in rows]
```

**关键点**:
- ✅ 所有方法返回Entity,不返回字典
- ✅ 使用`GenericRepository`提供通用CRUD
- ✅ 支持缓存自动管理
- ✅ 类型安全的返回值

### 使用Repository缓存

```python
class GameRepository(GenericRepository):
    def __init__(self):
        super().__init__(
            table_name="games",
            primary_key="id",
            enable_cache=True,  # 启用缓存
            cache_ttl=3600    # 缓存1小时
        )

    @cached(ttl=60)  # 方法级缓存
    def get_popular_games(self) -> List[GameEntity]:
        """获取热门游戏(缓存60秒)"""
        query = """
            SELECT g.*, COUNT(e.id) as event_count
            FROM games g
            LEFT JOIN log_events e ON g.id = e.game_id
            GROUP BY g.id
            ORDER BY event_count DESC
            LIMIT 10
        """
        rows = fetch_all_as_dict(query)
        return [GameEntity(**row) for row in rows]
```

---

## 5. Service层使用指南

### 创建Service

Service层封装业务逻辑,协调多个Repository:

```python
# backend/services/games/game_service.py

from backend.models.repositories.games import GameRepository
from backend.models.entities import GameEntity
from backend.core.cache.cache_invalidator import CacheInvalidator

class GameService:
    """游戏业务服务"""

    def __init__(self):
        self.game_repo = GameRepository()
        self.invalidator = CacheInvalidator()

    def create_game(self, game: GameEntity) -> GameEntity:
        """
        创建游戏

        业务规则:
        1. gid必须唯一
        2. 创建后清理缓存
        """
        # 验证gid唯一性
        existing = self.game_repo.find_by_gid(game.gid)
        if existing:
            raise ValueError(f"Game GID {game.gid} already exists")

        # 创建游戏
        game_id = self.game_repo.create(game.model_dump())

        # 清理缓存
        self.invalidator.invalidate_game(game.gid)
        self.invalidator.invalidate_pattern("games.list")

        return self.game_repo.find_by_id(game_id)
```

**关键点**:
- ✅ Service接收Entity作为参数
- ✅ Service返回Entity
- ✅ 业务规则在Service层实现
- ✅ 数据变更后清理缓存

### 缓存管理

```python
class GameService:
    def __init__(self):
        self.game_repo = GameRepository()
        self.invalidator = CacheInvalidator()

    @cached(ttl=300)  # 缓存5分钟
    def get_all_games(self) -> List[GameEntity]:
        """获取所有游戏(带缓存)"""
        return self.game_repo.get_all_with_event_count()

    def update_game(self, gid: int, data: Dict[str, Any]) -> GameEntity:
        """更新游戏"""
        # 更新数据
        game = self.game_repo.update(gid, data)

        # 清理相关缓存
        self.invalidator.invalidate_game(gid)  # 清理特定游戏缓存
        self.invalidator.invalidate_pattern("games.list")  # 清理列表缓存
        self.invalidator.invalidate_pattern("games.stats")  # 清理统计缓存

        return game
```

### 错误处理

```python
class GameService:
    def delete_game(self, gid: int) -> bool:
        """删除游戏"""
        # 检查是否有关联事件
        from backend.models.repositories.events import EventRepository
        event_repo = EventRepository()
        events = event_repo.get_by_game(gid)

        if events:
            raise ValueError(f"Cannot delete game {gid}: has {len(events)} associated events")

        # 删除游戏
        success = self.game_repo.delete(gid)

        # 清理缓存
        self.invalidator.invalidate_game(gid)

        return success
```

---

## 6. 常见问题FAQ

### Q1: 如何添加新模块?

**A**: 按照以下步骤:

1. **定义Entity** (在`backend/models/entities.py`):
```python
class NewEntity(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=100)

    model_config = ConfigDict(from_attributes=True)
```

2. **创建Repository** (在`backend/models/repositories/`):
```python
class NewRepository(GenericRepository):
    def __init__(self):
        super().__init__(
            table_name="new_table",
            primary_key="id",
            enable_cache=True
        )

    def find_by_name(self, name: str) -> Optional[NewEntity]:
        query = "SELECT * FROM new_table WHERE name = ?"
        row = fetch_one_as_dict(query, (name,))
        return NewEntity(**row) if row else None
```

3. **创建Service** (在`backend/services/new/`):
```python
class NewService:
    def __init__(self):
        self.new_repo = NewRepository()

    def create_new(self, entity: NewEntity) -> NewEntity:
        # 业务逻辑
        return self.new_repo.create(entity.model_dump())
```

4. **创建API路由** (在`backend/api/routes/`):
```python
from backend.models.entities import NewEntity
from backend.services.new.new_service import NewService

@new_bp.route('/api/new', methods=['POST'])
def create_new():
    data = NewEntity(**request.get_json())
    service = NewService()
    result = service.create_new(data)
    return json_success_response(data=result.model_dump())
```

### Q2: 如何处理复杂查询?

**A**: 在Repository中添加自定义查询方法:

```python
class GameRepository(GenericRepository):
    def search_games(self, keyword: str) -> List[GameEntity]:
        """搜索游戏"""
        query = """
            SELECT * FROM games
            WHERE name LIKE ?
               OR gid LIKE ?
            ORDER BY name
        """
        pattern = f"%{keyword}%"
        rows = fetch_all_as_dict(query, (pattern, pattern))
        return [GameEntity(**row) for row in rows]
```

### Q3: 如何优化性能?

**A**: 使用以下策略:

1. **Repository级缓存**:
```python
class GameRepository(GenericRepository):
    def __init__(self):
        super().__init__(
            table_name="games",
            enable_cache=True,
            cache_ttl=3600  # 1小时
        )
```

2. **Service级缓存**:
```python
from functools import lru_cache

class GameService:
    @lru_cache(maxsize=100)
    def get_cached_game(self, gid: int) -> GameEntity:
        return self.game_repo.find_by_gid(gid)
```

3. **查询优化**:
```python
# ✅ 好: 使用JOIN一次获取所有数据
query = """
    SELECT g.*, COUNT(e.id) as event_count
    FROM games g
    LEFT JOIN events e ON g.id = e.game_id
    GROUP BY g.id
"""

# ❌ 差: N+1查询
games = fetch_all_as_dict("SELECT * FROM games")
for game in games:
    events = fetch_all_as_dict("SELECT * FROM events WHERE game_id = ?", (game['id'],))
```

### Q4: 迁移常见错误

**A**: 避免以下错误:

1. **忘记更新import路径**:
```python
# ❌ 错误
from backend.domain.models.game import Game

# ✅ 正确
from backend.models.entities import GameEntity
```

2. **Repository返回字典而非Entity**:
```python
# ❌ 错误
def find_by_gid(self, gid: int) -> Dict[str, Any]:
    return fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (gid,))

# ✅ 正确
def find_by_gid(self, gid: int) -> Optional[GameEntity]:
    row = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (gid,))
    return GameEntity(**row) if row else None
```

3. **Service层忘记缓存失效**:
```python
# ❌ 错误
def update_game(self, gid: int, data: Dict):
    return self.game_repo.update(gid, data)

# ✅ 正确
def update_game(self, gid: int, data: Dict):
    result = self.game_repo.update(gid, data)
    self.invalidator.invalidate_game(gid)  # 清理缓存
    return result
```

4. **使用`.dict()`而非`.model_dump()`**:
```python
# ❌ 错误 (Pydantic v1)
game_dict = game.dict()

# ✅ 正确 (Pydantic v2)
game_dict = game.model_dump()
```

### Q5: 如何处理字段名不匹配?

**A**: 使用field alias或@property:

```python
class EventEntity(BaseModel):
    # 方案1: 使用alias
    event_name: str = Field(..., alias="name")

    # 方案2: 使用@property
    @property
    def name(self) -> str:
        return self.event_name

    @name.setter
    def name(self, value: str):
        self.event_name = value

    model_config = ConfigDict(populate_by_name=True)
```

### Q6: 如何编写单元测试?

**A**: 使用pytest和Mock:

```python
# backend/test/unit/services/test_game_service.py

import pytest
from unittest.mock import Mock
from backend.services.games.game_service import GameService
from backend.models.entities import GameEntity

class TestGameService:
    @pytest.fixture
    def service(self):
        """创建测试Service实例"""
        # Mock Repository
        mock_repo = Mock()
        service = GameService()
        service.game_repo = mock_repo
        return service

    def test_create_game_success(self, service):
        """测试创建游戏成功"""
        # Arrange
        game = GameEntity(gid="90000001", name="Test Game", ods_db="ieu_ods")
        service.game_repo.find_by_gid.return_value = None
        service.game_repo.create.return_value = 1
        service.game_repo.find_by_id.return_value = game

        # Act
        result = service.create_game(game)

        # Assert
        assert result.name == "Test Game"
        service.game_repo.create.assert_called_once()
```

---

## 附录

### 相关文档

- **架构总结**: [docs/development/ARCHITECTURE-SUMMARY-2026.md](ARCHITECTURE-SUMMARY-2026.md)
- **开发规范**: [CLAUDE.md](../../CLAUDE.md)
- **优化报告**: [docs/optimization/FINAL_OPTIMIZATION_REPORT.md](../optimization/FINAL_OPTIMIZATION_REPORT.md)

### 代码示例

完整代码示例请参考:
- Entity定义: `backend/models/entities.py`
- Repository实现: `backend/models/repositories/`
- Service实现: `backend/services/`
- API路由: `backend/api/routes/`

---

**文档维护**: 如有问题或建议,请联系开发团队
**最后更新**: 2026-02-25
