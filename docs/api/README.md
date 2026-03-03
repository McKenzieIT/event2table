# Event2Table API 文档

**V9.0.0架构** - Repository Pattern Migration

**版本**: 9.0.0
**最后更新**: 2026-03-03
**架构**: ERS (Entity-Repository-Service) + Repository Pattern
**API统计**: REST API 84端点 | GraphQL 78操作
**迁移状态**: 6/8核心模块已迁移到Repository模式 (75%)

---

## 快速开始

### 基础信息

- **Base URL**: `http://127.0.0.1:5001/api`
- **数据格式**: JSON
- **字符编码**: UTF-8
- **认证方式**: Session-based (via Flask session)

### 统一响应格式

所有API响应遵循统一格式：

```json
{
  "success": true/false,
  "data": {...},
  "message": "操作成功",
  "error": "错误信息（仅错误时）"
}
```

### HTTP状态码

| 状态码 | 描述 | 使用场景 |
|--------|------|----------|
| 200 | OK | 请求成功 |
| 400 | Bad Request | 请求参数错误 |
| 404 | Not Found | 资源未找到 |
| 409 | Conflict | 资源冲突（如重复创建） |
| 500 | Internal Server Error | 服务器错误 |

---

## 架构变更 (V8.0.0)

### 双API架构

**REST API + GraphQL**:
- ✅ **REST API**: 84个端点，传统HTTP接口
- ✅ **GraphQL API**: 78个操作，113次调用，灵活查询
- ✅ **统一架构**: 共享Entity-Repository-Service层
- ✅ **渐进迁移**: REST → GraphQL平滑过渡

### ERS架构 (Entity-Repository-Service)

**100% ERS架构覆盖**:

```
┌─────────────────────────────────────────────────────┐
│         API Layer (HTTP + GraphQL端点)               │
│  - RESTful API: backend/api/routes/                  │
│  - GraphQL API: backend/gql_api/ (V2)               │
│  - 处理HTTP请求/响应                                  │
│  - 参数解析和验证 (Pydantic Entity)                   │
│  - 调用Service层                                      │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│           Service Layer (业务逻辑)                   │
│  backend/services/                                   │
│  - 实现业务逻辑                                       │
│  - 协调多个Repository                                │
│  - 缓存管理 (@cached, @cache_invalidate)             │
│  - Bloom Filter集成                                  │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│        Repository Layer (数据访问)                   │
│  backend/models/repositories/                        │
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

**各层职责**:
- ✅ Entity层: Pydantic模型统一数据验证
- ✅ Repository层: 基于GenericRepository的数据访问抽象
- ✅ Service层: 业务逻辑封装和缓存管理
- ✅ API层: REST + GraphQL双端点

**关键优势**:
- 🎯 **类型安全**: Repository返回Entity对象而非字典
- 🚀 **性能优化**: 读写分离缓存策略（读用@cached，写用@cache_invalidate）
- 🧪 **易于测试**: Repository可Mock，Service可单元测试
- 📦 **代码复用**: GenericRepository提供通用CRUD操作

### 缓存系统

**缓存覆盖率100%**:
- L1缓存: 热数据60秒TTL
- L2缓存: 共享数据300秒TTL
- 自动失效: 写操作自动清理相关缓存
- 性能提升: 67% (267ms → 88ms)

**缓存装饰器**:
```python
# 读操作：使用缓存
@cached(ttl=1800)
def get_events(game_gid):
    return event_repo.find_by_game_gid(game_gid)

# 写操作：清理缓存
@cache_invalidate
def create_event(data):
    return event_repo.create(data)
```

### 零破坏性变更

- ✅ 所有旧API端点保持兼容
- ✅ 新增端点使用新架构
- ✅ 渐进式迁移策略

---

## API模块索引

### REST API (84个端点)

#### 核心业务模块

| 模块 | 文档 | 端点数 | 状态 |
|------|------|--------|------|
| **Categories** | [Categories API](CATEGORIES-API.md) | 8 | ✅ Phase 5增强 |
| **Events** | [Events API](EVENTS-API.md) | 9 | ✅ Phase 5完全迁移 |
| **Parameters** | [Parameters API](PARAMETERS-API.md) | 16 | ✅ Phase 5大幅扩展 |
| **Field Builder** | [Field Builder API](FIELD-BUILDER-API.md) | 6 | ✅ Phase 5新增 |

#### 支持模块

| 模块 | 文档 | 端点数 | 状态 |
|------|------|--------|------|
| **Games** | [Games API](GAMES-API.md) | 7 | ✅ Phase 1-2 |
| **Join Configs** | [Join Configs API](JOIN-CONFIGS-API.md) | 5 | ✅ Phase 3 |
| **Flows/Canvas** | [Flows API](FLOWS-API.md) | 11 | ✅ Phase 2-3 |
| **Cache** | [Cache API](CACHE-API.md) | 23 | ✅ 完整实现 |

### GraphQL API (78个操作)

| 文档 | 操作数 | 调用次数 | 状态 |
|------|--------|----------|------|
| **GraphQL API** | [GraphQL API](GRAPHQL_API.md) | 78 | 113 | ✅ 完整实现 |

**GraphQL优势**:
- ✅ 按需查询，避免over-fetching
- ✅ 单次请求获取多个资源
- ✅ 强类型Schema自动验证
- ✅ 实时订阅支持

---

## API版本管理

### 版本策略

**V8.0.0** (当前版本):
- ✅ **REST API**: 稳定版本，84个端点
- ✅ **GraphQL API**: 新一代API，78个操作
- ✅ **双API共存**: 平滑迁移路径

### API选择指南

**何时使用REST API**:
- ✅ 简单的CRUD操作
- ✅ 需要标准HTTP状态码
- ✅ 缓存策略明确
- ✅ 与现有系统集成

**何时使用GraphQL API**:
- ✅ 需要灵活的数据查询
- ✅ 复杂的关联数据获取
- ✅ 实时数据订阅
- ✅ 减少网络请求次数

### 迁移建议

**渐进式迁移路径**:
```
REST API → GraphQL混合 → 完全GraphQL
  ↓            ↓              ↓
 当前状态    推荐方案      未来目标
```

**迁移示例**:
```javascript
// REST API
const events = await fetch('/api/events?game_gid=10000147').then(r => r.json());

// GraphQL API (等效查询)
const query = gql`
  query GetEvents($gameGid: Int!) {
    events(gameGid: $gameGid) {
      id
      eventName
      eventNameCn
    }
  }
`;
const { data } = await client.query({ query, variables: { gameGid: 10000147 } });
```

### 版本兼容性

| API版本 | 状态 | 废弃计划 |
|---------|------|----------|
| REST API V8.0.0 | ✅ 稳定 | 无计划 |
| GraphQL API V1.0 | ✅ 稳定 | 无计划 |
| REST API V7.x | ⚠️ 维护模式 | 2027-01-01 |

---

## 快速参考

### 游戏上下文

**所有API需要游戏上下文** (`game_gid`):

```bash
# 推荐方式：使用业务GID
GET /api/events?game_gid=10000147

# 向后兼容：也支持game_id（将逐步废弃）
GET /api/events?game_id=1
```

### 分页参数

**支持分页的API**:

```bash
GET /api/events?page=1&per_page=20
```

- `page`: 页码（从1开始，默认1）
- `per_page`: 每页数量（默认20，最大100）

### 批量操作

**支持批量操作的API**:

```bash
# 批量删除
DELETE /api/events/batch
Body: {"ids": [1, 2, 3]}

# 批量更新
PUT /api/events/batch-update
Body: {"ids": [1, 2, 3], "updates": {...}}
```

---

## 安全性

### 输入验证

- ✅ **Pydantic Entity验证**: 自动类型检查和长度限制
- ✅ **XSS防护**: HTML实体转义
- ✅ **SQL注入防护**: 参数化查询
- ✅ **长度限制**: 防止DoS攻击

### 游戏保护

**STAR001保护规则**:
```python
# ✅ 正确：使用测试GID
TEST_GID_START = 90000000

# ❌ 错误：禁止删除生产数据
game_gid = 10000147  # STAR001 - 禁止删除
```

详见: [STAR001-GAME-PROTECTION.md](../development/STAR001-GAME-PROTECTION.md)

---

## 性能优化

### 缓存策略

**读操作**:
```python
@cached(ttl=1800)  # 30分钟缓存
def get_events(game_gid):
    ...
```

**写操作**:
```python
@cache_invalidate  # 自动清理缓存
def create_event(game_gid, data):
    ...
```

### 性能指标

| 操作 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 获取参数列表 | 267ms | 88ms | 67% |
| 获取游戏列表 | 120ms | 45ms | 63% |
| 创建事件 | 350ms | 150ms | 57% |

---

## 错误处理

### 标准错误响应

```json
{
  "success": false,
  "error": "错误描述",
  "message": "用户友好的错误消息"
}
```

### 常见错误

| 错误 | 状态码 | 解决方案 |
|------|--------|----------|
| `game_gid required` | 400 | 提供game_gid参数 |
| `Game not found` | 404 | 检查game_gid是否正确 |
| `Validation error` | 400 | 检查请求参数格式 |
| `Already exists` | 409 | 资源已存在，使用唯一标识 |

---

## Repository 模式架构

> **🆕 V8.0.0**: 100% ERS架构，所有模块使用Repository模式

### 核心组件

**1. GenericRepository 基类**

提供通用CRUD操作和安全验证：

```python
from backend.core.data_access import GenericRepository

class GameRepository(GenericRepository):
    """游戏仓储类"""

    def __init__(self):
        super().__init__(
            table_name="games",
            primary_key="id",
            enable_cache=True,
            cache_timeout=120
        )

    # 继承的方法：
    # - find_by_id(id)          # 按ID查询
    # - find_by_field(f, v)     # 按字段查询
    # - find_where(cond)        # 按条件查询
    # - find_all()              # 查询所有
    # - create(data)            # 创建记录
    # - update(id, data)        # 更新记录
    # - delete(id)              # 删除记录
```

**2. Entity 统一模型**

Pydantic Entity作为单一真相来源：

```python
from backend.models.entities import GameEntity

# Entity自动验证输入
game = GameEntity(
    gid="10000147",
    name="Game Name",
    ods_db="ieu_ods"
)

# API层使用Entity验证
game_data = GameEntity(**request.json)

# Repository返回Entity
game = game_repo.find_by_gid(10000147)  # 返回GameEntity

# API层响应使用Entity序列化
return json_success_response(data=game.model_dump())
```

**3. Service 层缓存**

使用装饰器简化缓存管理：

```python
from backend.core.cache.decorators import cached, cache_invalidate

class GameService:
    @cached(ttl=1800)  # 读操作：使用缓存
    def get_games(self):
        return self.game_repo.find_all()

    @cache_invalidate  # 写操作：清理缓存
    def create_game(self, data):
        return self.game_repo.create(data)
```

### 数据流向

**完整请求流程**：

```
1. HTTP Request (JSON)
   ↓
2. API Layer (request.get_json())
   ↓
3. Entity Validation (Pydantic)
   ↓
4. Service Layer (Business Logic + Cache)
   ↓
5. Repository Layer (SQL Query)
   ↓
6. Database (SQLite)
   ↓
7. Repository Layer (Entity)
   ↓
8. Service Layer (Entity)
   ↓
9. API Layer (Entity.model_dump())
   ↓
10. HTTP Response (JSON)
```

### 使用示例

**创建新API端点（Entity架构）**：

```python
from flask import Blueprint, request
from backend.models.entities import GameEntity
from backend.services.games.game_service import GameService
from backend.core.utils import json_success_response, json_error_response

games_bp = Blueprint('games', __name__)

@games_bp.route('/api/games', methods=['POST'])
def create_game():
    """创建游戏API - Entity架构"""
    try:
        # 1. 解析和验证请求参数（Entity自动验证）
        data = request.get_json()
        game_data = GameEntity(**data)  # ⭐ Entity自动验证类型、长度、格式

        # 2. 调用Service层（处理业务逻辑和缓存）
        service = GameService()
        game = service.create_game(game_data)

        # 3. 返回响应（Entity序列化为JSON）
        return json_success_response(
            data=game.model_dump(),  # ⭐ Entity.model_dump()序列化
            message="Game created successfully"
        )

    except ValidationError as e:
        # Pydantic自动捕获验证错误
        return json_error_response(f"Validation error: {e}", status_code=400)
    except ValueError as e:
        # Service层业务逻辑错误
        return json_error_response(str(e), status_code=409)
    except Exception as e:
        # 未知错误
        logger.error(f"Error creating game: {e}")
        return json_error_response("Failed to create game", status_code=500)
```

**Entity vs Dict对比**：

```python
# ❌ 旧架构（Dict-based） - 需要手动验证
def create_game_old(request):
    data = request.get_json()

    # 手动验证
    if not data.get('name'):
        return {'error': 'Name is required'}, 400
    if len(data.get('name', '')) > 100:
        return {'error': 'Name too long'}, 400

    # 直接使用字典（无类型检查）
    game_id = execute_insert(
        "INSERT INTO games (name, gid) VALUES (?, ?)",
        (data['name'], data['gid'])
    )

    # 返回字典（无自动序列化）
    return {'data': {'id': game_id, **data}}

# ✅ 新架构（Entity-based） - 自动验证和类型安全
def create_game_new(request):
    data = request.get_json()

    # Entity自动验证（类型、长度、格式）
    game_data = GameEntity(**data)

    # Service层处理业务逻辑
    service = GameService()
    game = service.create_game(game_data)

    # Entity自动序列化
    return json_success_response(
        data=game.model_dump(),  # 转换为字典
        message="Success"
    )
```

**创建自定义Repository**：

```python
from backend.core.data_access import GenericRepository
from backend.models.entities import GameEntity
from typing import Optional, List

class GameRepository(GenericRepository):
    """游戏仓储类"""

    def __init__(self):
        super().__init__(
            table_name="games",
            enable_cache=True,
            cache_timeout=120
        )

    def find_by_gid(self, gid: int) -> Optional[GameEntity]:
        """根据业务GID查询"""
        query = "SELECT * FROM games WHERE gid = ?"
        row = fetch_one_as_dict(query, (gid,))
        return GameEntity(**row) if row else None

    def get_all_with_stats(self) -> List[GameEntity]:
        """获取游戏及其统计信息"""
        query = """
            SELECT g.*, COUNT(e.id) as event_count
            FROM games g
            LEFT JOIN log_events e ON g.gid = e.game_gid
            GROUP BY g.id
        """
        rows = fetch_all_as_dict(query)
        return [GameEntity(**row) for row in rows]
```

### 完整文档

详细内容请参考：
- **[Repository Pattern Guide](../development/repository-pattern-guide.md)** - Repository模式完整指南 ⭐
- **[架构设计文档](../development/architecture.md)** - 分层架构详解
- **[Entity架构迁移指南](../development/ENTITY-ARCHITECTURE-MIGRATION-GUIDE.md)** - Entity架构说明

---

## Entity架构迁移指南 ⭐

> **从Dict-based迁移到Entity-based架构的完整指南**

### 迁移动机

**为什么需要迁移？**

| 方面 | 旧架构 (Dict) | 新架构 (Entity) | 收益 |
|------|--------------|----------------|------|
| **数据验证** | 手动验证每个字段 | Pydantic自动验证 | 减少80%验证代码 |
| **类型安全** | 无类型检查 | 完整类型注解 | IDE自动补全，减少bug |
| **序列化** | 手动dict操作 | Entity.model_dump() | 自动转换，避免遗漏字段 |
| **文档** | 手动编写API文档 | Pydantic自动生成文档 | 始终保持同步 |
| **维护性** | 3套模型 (Domain/Schema/Dict) | 1套Entity | 减少40%代码量 |

### 迁移步骤

#### Step 1: 定义Entity

**旧代码** (无Entity定义):
```python
# backend/api/routes/games.py
def create_game():
    data = request.get_json()
    # 直接使用字典，无验证
    game_id = execute_insert(
        "INSERT INTO games (name, gid) VALUES (?, ?)",
        (data['name'], data['gid'])
    )
    return {'id': game_id, **data}
```

**新代码** (Entity定义):
```python
# backend/models/entities.py
from pydantic import BaseModel, Field, field_validator
import html

class GameEntity(BaseModel):
    """游戏实体 - 单一真相来源"""
    id: Optional[int] = None
    gid: str = Field(..., min_length=1, max_length=50, description="游戏业务GID")
    name: str = Field(..., min_length=1, max_length=100, description="游戏名称")
    ods_db: str = Field(..., pattern=r'^(ieu_ods|overseas_ods)$')
    description: Optional[str] = None
    dwd_prefix: str = Field("dwd")

    model_config = {"from_attributes": True}

    @field_validator('name')
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """防止XSS攻击"""
        return html.escape(v.strip())
```

#### Step 2: 更新Repository返回Entity

**旧代码** (返回Dict):
```python
class GameRepository:
    def find_by_gid(self, gid: int) -> Optional[Dict]:
        query = "SELECT * FROM games WHERE gid = ?"
        return fetch_one_as_dict(query, (gid,))  # 返回字典
```

**新代码** (返回Entity):
```python
class GameRepository:
    def find_by_gid(self, gid: int) -> Optional[GameEntity]:
        query = "SELECT * FROM games WHERE gid = ?"
        row = fetch_one_as_dict(query, (gid,))
        return GameEntity(**row) if row else None  # ⭐ 返回Entity
```

#### Step 3: 更新Service使用Entity

**旧代码** (Dict处理):
```python
class GameService:
    def create_game(self, data: Dict) -> Dict:
        # 手动验证
        if not data.get('name'):
            raise ValueError("Name required")

        # 手动调用Repository
        game_id = self.game_repo.create(data)

        # 手动查询返回
        return self.game_repo.find_by_id(game_id)
```

**新代码** (Entity处理):
```python
class GameService:
    def create_game(self, game_data: GameEntity) -> GameEntity:
        # Entity已验证，直接使用
        existing = self.game_repo.find_by_gid(game_data.gid)
        if existing:
            raise ValueError(f"Game {game_data.gid} already exists")

        # 使用model_dump()转换为字典
        game_id = self.game_repo.create(game_data.model_dump())

        # 返回Entity对象
        return self.game_repo.find_by_id(game_id)
```

#### Step 4: 更新API层

**旧代码** (手动验证):
```python
@games_bp.route('/api/games', methods=['POST'])
def create_game():
    try:
        data = request.get_json()

        # 手动验证
        if not data.get('name'):
            return {'error': 'Name required'}, 400

        # 调用Service
        service = GameService()
        game = service.create_game(data)

        return jsonify({'success': True, 'data': game})
    except Exception as e:
        return {'error': str(e)}, 500
```

**新代码** (Entity自动验证):
```python
@games_bp.route('/api/games', methods=['POST'])
def create_game():
    try:
        data = request.get_json()

        # ⭐ Entity自动验证
        game_data = GameEntity(**data)

        # ⭐ Service处理
        service = GameService()
        game = service.create_game(game_data)

        # ⭐ Entity序列化
        return json_success_response(
            data=game.model_dump(),
            message="Game created successfully"
        )
    except ValidationError as e:
        # ⭐ Pydantic自动捕获验证错误
        return json_error_response(f"Validation error: {e}", status_code=400)
    except ValueError as e:
        # ⭐ Service层业务错误
        return json_error_response(str(e), status_code=409)
    except Exception as e:
        # ⭐ 未知错误
        logger.error(f"Error creating game: {e}")
        return json_error_response("Failed to create game", status_code=500)
```

### 迁移检查清单

**API层**:
- [ ] 使用Entity解析请求参数：`GameEntity(**request.get_json())`
- [ ] 捕获ValidationError异常
- [ ] 使用Entity.model_dump()序列化响应
- [ ] 返回统一的JSON格式

**Service层**:
- [ ] 方法参数使用Entity类型
- [ ] 返回Entity对象
- [ ] 使用Entity.model_dump()调用Repository
- [ ] 添加缓存装饰器

**Repository层**:
- [ ] 所有查询方法返回Entity对象
- [ ] 使用Entity(**row)构造对象
- [ ] 更新类型注解

**Entity定义**:
- [ ] 所有字段有类型注解
- [ ] 添加Field验证规则
- [ ] 添加field_validator进行复杂验证
- [ ] 设置model_config = {"from_attributes": True}

### 常见迁移问题

#### 问题1: Entity验证失败

**症状**:
```
ValidationError: 1 validation error for GameEntity
name
  Field required [type=missing, ...]
```

**原因**: 请求参数缺少必填字段

**解决方案**:
```python
# ✅ 前端发送完整参数
fetch('/api/games', {
  method: 'POST',
  body: JSON.stringify({
    gid: "10000147",
    name: "Game Name",
    ods_db: "ieu_ods"
    # ⭐ 所有必填字段都要提供
  })
})
```

#### 问题2: Entity.model_dump()丢失字段

**症状**: 响应数据不完整

**原因**: Entity定义中字段为Optional且数据库为NULL

**解决方案**:
```python
# ✅ 使用model_dump()时包含所有字段
data = game.model_dump(exclude_none=False)  # 保留None值
data = game.model_dump(mode='json')  # JSON序列化模式
```

#### 问题3: 字典无法转换为Entity

**症状**:
```
TypeError: Object of type int is not JSON serializable
```

**原因**: datetime等特殊类型未序列化

**解决方案**:
```python
# ✅ Entity配置JSON编码器
class GameEntity(BaseModel):
    created_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }
```

### 迁移前后对比

**代码量对比**:
```
旧架构 (Dict):     216行
新架构 (Entity):    130行
减少:              86行 (40%)
```

**验证代码对比**:
```
旧架构: 手动验证 20+ 行
新架构: Entity定义 5行
减少: 15行 (75%)
```

**错误处理对比**:
```
旧架构: 分散在各处
新架构: Pydantic统一处理
```

### 迁移验证

**单元测试**:
```python
def test_create_game_with_entity():
    # ⭐ 使用Entity测试
    game_data = GameEntity(
        gid="10000147",
        name="Test Game",
        ods_db="ieu_ods"
    )

    service = GameService()
    game = service.create_game(game_data)

    # ⭐ 断言Entity对象
    assert isinstance(game, GameEntity)
    assert game.gid == "10000147"
    assert game.name == "Test Game"
```

**API测试**:
```bash
# 测试Entity验证
curl -X POST http://127.0.0.1:5001/api/games \
  -H "Content-Type: application/json" \
  -d '{"name": "Test"}'  # ❌ 缺少gid字段

# 预期响应：
# {
#   "success": false,
#   "error": "Validation error: 1 validation error for GameEntity\n  gid\n    Field required [type=missing]"
# }
```

### 相关文档

- **[Entity架构迁移指南](../development/ENTITY-ARCHITECTURE-MIGRATION-GUIDE.md)** - 完整迁移步骤
- **[Repository Pattern Guide](../development/repository-pattern-guide.md)** - Repository使用指南
- **[Pydantic文档](https://docs.pydantic.dev/)** - Pydantic官方文档

---

## 开发指南

### 前端调用示例

```javascript
// 获取游戏列表
const games = await fetch('/api/games').then(r => r.json());

// 获取事件（带分页）
const events = await fetch('/api/events?game_gid=10000147&page=1&per_page=20')
  .then(r => r.json());

// 创建事件
const result = await fetch('/api/events', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    game_gid: 10000147,
    event_name: 'login',
    event_name_cn: '登录'
  })
}).then(r => r.json());
```

### cURL示例

```bash
# 获取游戏列表
curl http://127.0.0.1:5001/api/games

# 获取事件
curl http://127.0.0.1:5001/api/events?game_gid=10000147

# 创建事件
curl -X POST http://127.0.0.1:5001/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "game_gid": 10000147,
    "event_name": "login",
    "event_name_cn": "登录"
  }'
```

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 8.0.0 | 2026-03-02 | 双API架构：REST 84端点 + GraphQL 78操作 |
| 8.0.0 | 2026-03-01 | V8.0.0架构：100% ERS覆盖、缓存100%覆盖 |
| 7.8.0 | 2026-02-26 | Entity架构统一完成 |
| 7.6.0 | 2026-02-25 | 缓存系统文档完善 |
| 7.0.0 | 2026-02-10 | ERS架构引入 |

---

## 相关文档

### 架构与开发
- [架构设计](../development/architecture.md)
- [开发指南](../development/contributing.md)
- [API开发规范](../development/api-development.md)
- [缓存系统](../cache/README.md)

### API文档
- [GraphQL API](GRAPHQL_API.md) - GraphQL接口文档
- [REST到GraphQL迁移指南](REST_TO_GRAPHQL_MIGRATION.md) - 迁移最佳实践
- [迁移进度报告](MIGRATION_PROGRESS_REPORT.md) - 迁移状态跟踪
- [API状态](API_STATUS.md) - API健康状态

### 测试与验证
- [迁移测试报告](MIGRATION_TEST_REPORT.md) - 测试覆盖
- [REST API移除计划](REST_API_REMOVAL_PLAN.md) - 废弃路线图

---

## 联系方式

- **项目**: Event2Table
- **文档维护**: Event2Table Development Team
- **最后更新**: 2026-03-02

---

## API统计总览

| API类型 | 端点/操作数 | 调用次数 | 覆盖率 | 状态 |
|---------|-------------|----------|--------|------|
| **REST API** | 84个端点 | - | 100% | ✅ 稳定 |
| **GraphQL API** | 78个操作 | 113次调用 | 100% | ✅ 稳定 |
| **总计** | 162个 | - | 100% | ✅ 生产就绪 |

**模块分布**:
- 核心业务模块: 39个REST端点 + 45个GraphQL操作
- 支持模块: 45个REST端点 + 33个GraphQL操作
- 缓存系统: 23个REST端点（共享）
- Canvas/Flows: 11个REST端点（专用）
