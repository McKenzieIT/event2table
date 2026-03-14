# API设计模式

> **来源**: 整合了多个报告的API设计相关经验 + 2026-03最新优化经验
> **最后更新**: 2026-03-09
> **维护**: 每次API设计问题修复后立即更新

---

## 分层架构 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 2次 | **来源**: [架构设计文档](../development/architecture.md), [CLAUDE.md](../../CLAUDE.md)

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

**优先级**: P0 | **出现次数**: 2次 | **来源**: [测试指南](./testing-guide.md), [错误处理最佳实践](../../CLAUDE.md#api安全规范)

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

**优先级**: P1 | **出现次数**: 1次 | **来源**: [GraphQL API文档](../api/GRAPHQL-API.md), [CLAUDE.md GraphQL规范](../../CLAUDE.md#graphql实施经验)

### GraphQL vs REST

**何时使用GraphQL**:
- ✅ 需要灵活的数据查询
- ✅ 客户端需要不同的数据组合
- ✅ 减少API请求次数（Dashboard加载：5次 → 1次，↓80%）
- ✅ 需要实时更新（Subscriptions）
- ✅ 复杂的关联数据查询

**何时使用REST**:
- ✅ 简单的CRUD操作
- ✅ 标准化的资源操作
- ✅ 缓存优先的场景
- ✅ 文件上传/下载

### 性能提升数据

**Event2Table项目实际数据**:
- 响应时间：↓29-49%
- 数据传输量：↓35-46%
- API调用次数：↓50-80%
- DataLoader查询优化：↓82-98%

### GraphQL Schema设计模式

**1. 类型系统设计**:
```python
# backend/gql_api/schema.py
from graphene import ObjectType, Schema, String, Int, List, Field, Float
from graphene_sqlalchemy import SQLAlchemyObjectType

class Game(SQLAlchemyObjectType):
    """游戏类型"""
    class Meta:
        model = GameModel
        only_fields = ("id", "gid", "name", "name_cn", "is_active")

    # 自定义字段
    event_count = Field(Int, description="事件数量")
    ods_table_name = Field(String, description="ODS表名")

    def resolve_event_count(root, info):
        """解析事件数量"""
        return count_events_for_game(root.gid)

    def resolve_ods_table_name(root, info):
        """解析ODS表名"""
        return f"{root.ods_db}.ods_{root.gid}_all_view"
```

**2. 查询设计**:
```python
class Query(ObjectType):
    # 列表查询
    games = List(Game, limit=Int(default_value=10), offset=Int(default_value=0))
    game_by_gid = Field(Game, gid=Int(required=True))

    # 关联查询
    events = List(Event, game_gid=Int(required=True), limit=Int(default_value=20))

    def resolve_games(root, info, limit=10, offset=0):
        """解析游戏列表"""
        query = GameModel.query.limit(limit).offset(offset)
        return query.all()

    def resolve_game_by_gid(root, info, gid):
        """根据GID查询游戏"""
        return GameModel.query.filter_by(gid=gid).first()
```

**3. 变更设计**:
```python
class CreateGame(graphene.Mutation):
    """创建游戏变更"""
    class Arguments:
        gid = graphene.Int(required=True)
        name = graphene.String(required=True)
        ods_db = graphene.String(required=True)

    game = Field(Game)

    def mutate(root, info, gid, name, ods_db):
        # 验证输入
        existing = GameModel.query.filter_by(gid=gid).first()
        if existing:
            raise ValueError(f"Game {gid} already exists")

        # 创建游戏
        game = GameModel(gid=gid, name=name, ods_db=ods_db)
        db.session.add(game)
        db.session.commit()

        return CreateGame(game=game)

class Mutation(ObjectType):
    create_game = CreateGame.Field()
    update_game = UpdateGame.Field()
    delete_game = DeleteGame.Field()
```

### DataLoader优化模式

**解决N+1查询问题**:
```python
# backend/gql_api/dataloaders/extended_loaders.py
from promise.dataloader import DataLoader
from functools import lru_cache

class EventLoader(DataLoader):
    """事件批量加载器"""

    def batch_load_fn(self, keys):
        """批量加载事件"""
        # 一次性查询所有事件
        events = fetch_all_as_dict(
            f"SELECT * FROM log_events WHERE game_gid IN ({','.join(['?']*len(keys))})",
            keys
        )

        # 按game_gid分组
        result = {key: [] for key in keys}
        for event in events:
            result[event['game_gid']].append(event)

        # 返回Promise
        return Promise.all([result.get(key, []) for key in keys])

# 在Resolver中使用
@lru_cache(maxsize=1)
def get_event_loader(info):
    """获取EventLoader实例（缓存到请求）"""
    return info.context.get('event_loader') or EventLoader()

def resolve_game_events(root, info):
    """解析游戏的事件"""
    loader = get_event_loader(info)
    return loader.load(root.gid)
```

**DataLoader性能对比**:
| DataLoader | 优化前查询次数 | 优化后查询次数 | 改进 |
|-----------|--------------|--------------|------|
| EventLoader | 11次（10游戏） | 2次 | ↓82% |
| ParameterLoader | 101次（100事件） | 2次 | ↓98% |
| CategoryLoader | 101次（100事件） | 2次 | ↓98% |
| GameStatsLoader | 31次（10游戏） | 4次 | ↓87% |

### GraphQL Subscriptions实现

**实时更新订阅**:
```python
# backend/gql_api/subscriptions.py
import graphene
from graphene import Subscription

class EventSubscription(Subscription):
    """事件订阅"""
    class Arguments:
        game_gid = graphene.Int(required=True)

    event = Field(Event)
    action = Field(graphene.String)  # CREATED, UPDATED, DELETED

    def subscribe(root, info, game_gid):
        """订阅事件变更"""
        # 返回异步迭代器
        return event_stream_generator(game_gid)

    def publish(root, info, game_gid):
        """发布事件变更"""
        event = yield
        return EventSubscription(event=event, action="CREATED")

class Subscription(graphene.ObjectType):
    event_subscription = EventSubscription.Field()
    parameter_subscription = ParameterSubscription.Field()
    dashboard_subscription = DashboardSubscription.Field()
```

**前端Subscription使用**:
```javascript
// frontend/src/graphql/subscriptions.ts
import { gql, useSubscription } from '@apollo/client';

const EVENT_SUBSCRIPTION = gql`
  subscription OnEventChange($gameGid: Int!) {
    eventSubscription(gameGid: $gameGid) {
      event {
        id
        name
        gameGid
      }
      action
    }
  }
`;

function EventList({ gameGid }) {
  const { data, loading } = useSubscription(EVENT_SUBSCRIPTION, {
    variables: { gameGid }
  });

  if (loading) return <p>Loading...</p>;

  return (
    <div>
      <h3>Real-time Events</h3>
      {data && <EventItem event={data.eventSubscription} />}
    </div>
  );
}
```

### 性能监控中间件

**查询性能监控**:
```python
# backend/gql_api/middleware/performance_monitor.py
class PerformanceMonitorMiddleware:
    """性能监控中间件"""

    def resolve(self, next, root, info, **args):
        start_time = time.time()

        result = next(root, info, **args)

        duration = time.time() - start_time

        # 记录慢查询
        if duration > 0.5:  # 500ms
            logger.warning(
                f"Slow GraphQL query: {info.field_name} "
                f"took {duration:.3f}s"
            )

        # 收集指标
        metricscollector.record_query(info.field_name, duration)

        return result
```

**DataLoader命中率监控**:
```python
class DataLoaderMonitorMiddleware:
    """DataLoader监控中间件"""

    def __init__(self):
        self.loader_stats = {}

    def record_loader_hit(self, loader_name, batch_size, cache_hits):
        """记录DataLoader命中率"""
        if loader_name not in self.loader_stats:
            self.loader_stats[loader_name] = {
                'total_requests': 0,
                'total_batches': 0,
                'cache_hits': 0
            }

        stats = self.loader_stats[loader_name]
        stats['total_requests'] += batch_size
        stats['total_batches'] += 1
        stats['cache_hits'] += cache_hits

    def get_hit_rate(self, loader_name):
        """获取命中率"""
        stats = self.loader_stats.get(loader_name, {})
        if stats['total_requests'] == 0:
            return 0
        return stats['cache_hits'] / stats['total_requests']
```

### 迁移最佳实践

**分阶段迁移策略**:
```
Phase 1: 基础设施准备
  ├─ GraphQL Code Generator配置
  ├─ TypeScript类型定义生成
  └─ GraphQL查询和变更定义

Phase 2: 页面迁移
  ├─ Dashboard → DashboardGraphQL
  ├─ EventsList → EventsListGraphQL
  └─ ParametersList → ParametersListGraphQL

Phase 3: 性能优化
  ├─ DataLoader扩展
  ├─ GraphQL Subscriptions
  └─ 性能监控中间件
```

**前端迁移模式**:
```javascript
// 迁移前（REST）
import { useQuery } from 'react-query';

function Dashboard() {
  const { data } = useQuery(['games'], () =>
    fetch('/api/games').then(r => r.json())
  );
}

// 迁移后（GraphQL）
import { useQuery, gql } from '@apollo/client';

const GET_GAMES = gql`
  query GetGames($limit: Int) {
    games(limit: $limit) {
      id
      gid
      name
      isActive
    }
  }
`;

function DashboardGraphQL() {
  const { loading, error, data } = useQuery(GET_GAMES, {
    variables: { limit: 10 }
  });
}
```

### 代码审查清单

- [ ] GraphQL Schema是否清晰且类型安全？
- [ ] 是否使用DataLoader解决N+1问题？
- [ ] DataLoader命中率是否>85%？
- [ ] 是否有适当的查询深度限制？
- [ ] 是否有性能监控中间件？
- [ ] Subscriptions是否正确实现？
- [ ] 是否有查询复杂度限制？

### 相关经验

- [分层架构](#分层架构) - GraphQL分层设计
- [性能模式 - N+1查询优化](./performance-patterns.md#n1查询优化) - DataLoader优化
- [性能模式 - 缓存策略](./performance-patterns.md#缓存策略) - GraphQL缓存

### 案例文档

- [GraphQL API文档](../api/GRAPHQL-API.md) - GraphQL Schema设计和查询指南
- [缓存系统开发规范](../../CLAUDE.md#缓存系统开发规范) - GraphQL缓存策略

---

## Service层缓存集成 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [缓存系统文档](../cache/README.md), [CLAUDE.md缓存规范](../../CLAUDE.md#缓存系统开发规范)

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

**优先级**: P1 | **出现次数**: 1次 | **来源**: [缓存系统文档](../cache/README.md), [API缓存失效策略](../../CLAUDE.md#缓存失效分析)

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

**优先级**: P1 | **出现次数**: 1次 | **来源**: [架构设计文档](../development/architecture.md), [Entity架构迁移](../../CLAUDE.md#entity架构迁移完成)

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

**优先级**: P1 | **出现次数**: 1次 | **来源**: [Canvas API文档](../api/CANVAS-API.md), [HQL生成器文档](../hql/README.md)

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

**优先级**: P1 | **出现次数**: 1次 | **来源**: [HQL生成器文档](../hql/README.md), [重构检查清单](./refactoring-checklist.md)

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

## 路由参数设计规范 ⭐ **P0极其重要 - 2026-03-04新增**

**优先级**: P0 | **出现次数**: 1次 | **来源**: [路由参数验证](../../CLAUDE.md#游戏标识符规范), [API契约测试](../../CLAUDE.md#api契约测试规范)

### 游戏标识符规范

**核心原则**：
```javascript
// ✅ 正确：使用 gameData.gid
const gameGid = gameData.gid;  // 10000147
const odsDb = gameData.ods_db;  // ieu_ods
const tableName = `${odsDb}.ods_${gameGid}_all_view`;

// ✅ 正确：API调用
fetch(`/api/events?game_gid=${gameGid}`)
fetch(`/api/parameters/all?game_gid=${gameGid}`)

// ❌ 错误：不要使用 gameId
const tableName = `ods_${gameId}_all_view`;  // 错误！
fetch(`/api/events?game_id=${gameId}`)  // 错误！
```

### 表名生成规范

**使用 game_gid 生成表名**：
```python
# ✅ 正确：游戏查询
game = fetch_one_as_dict('SELECT * FROM games WHERE gid = ?', (game_gid,))

# ✅ 正确：事件查询
events = fetch_all_as_dict('SELECT * FROM log_events WHERE game_gid = ?', (game_gid,))

# ✅ 正确：表名生成
source_table = f'{game["ods_db"]}.ods_{game["gid"]}_all_view'  # ieu_ods.ods_10000147_all_view
target_table = f'dwd.v_dwd_{game["gid"]}_{event}_di'  # dwd.v_dwd_10000147_login_di

# ❌ 错误：不要使用 game_id
source_table = f'{ods_db}.ods_{game_id}_all_view'  # 错误！
```

### 路由参数设计模式

**前端路由哈希模式**：
```javascript
// ✅ 正确：使用哈希路由（避免刷新）
const routes = [
  { path: '/parameters', title: '参数管理' },
  { path: '/parameters/dashboard', title: '参数统计' },
  { path: '/parameters/compare', title: '参数对比' },
  { path: '/parameters/enhanced', title: 'Enhanced' },
  { path: '/parameter-dashboard', title: '参数统计' }
];

// ✅ 正确：路由顺序（具体路由优先）
// routes.tsx 中必须按从具体到一般的顺序定义
{ path: "parameters/dashboard", element: <ParameterDashboard /> },  // 必须先定义
{ path: "parameters", element: <ParametersList /> }                   // 后定义
```

**后端路由参数**：
```python
# ✅ 正确：路由参数设计
@events_bp.route('/api/events', methods=['GET'])
def get_events():
    game_gid = request.args.get('game_gid', type=int)
    # 使用 game_gid 进行查询

# ✅ 正确：参数验证
from flask import request

def validate_game_gid(game_gid):
    if not game_gid:
        return json_error_response('Game context required', status_code=400)
    return game_gid
```

### API契约一致性验证

**端点存在性检查**：
```bash
# 验证后端端点是否存在
curl -X GET http://127.0.0.1:5001/api/health

# 验证前端路由是否正确映射
grep -A10 "path: \"parameters\"" frontend/src/routes/routes.tsx
```

**参数格式一致性**：
```javascript
// ✅ 前端和后端使用相同的参数名
// 前端
fetch(`/api/events?game_gid=${gameGid}`)

// 后端
@events_bp.route('/api/events', methods=['GET'])
def get_events():
    game_gid = request.args.get('game_gid', type=int)  // ✅ 一致
    # return events...
```

### 路由验证工具

**自动化测试脚本**：
```javascript
// 浏览器控制台测试脚本
const routes = [
  { path: '/parameters', title: '参数管理' },
  { path: '/parameters/dashboard', title: '参数统计' },
  { path: '/parameters/compare', title: '参数对比' },
  { path: '/parameters/enhanced', title: 'Enhanced' },
  { path: '/parameter-dashboard', title: '参数统计' }
];

routes.forEach((route, index) => {
  setTimeout(() => {
    window.location.hash = route.path;
    console.log(`Testing: ${route.path} - Expected: ${route.title}`);
  }, index * 2000);
});
```

**预期输出**：
```
Testing: /parameters - Expected: 参数管理
Testing: /parameters/dashboard - Expected: 参数统计
Testing: /parameters/compare - Expected: 参数对比
Testing: /parameters/enhanced - Expected: Enhanced
Testing: /parameter-dashboard - Expected: 参数统计
```

### 成功验证标准

**完整路由测试清单**：
- ✅ 所有5个路由加载无控制台错误
- ✅ 每个路由显示正确的页面标题
- ✅ 每个路由显示正确的页面内容
- ✅ 无"Select Game"提示（如果游戏已选择）
- ✅ 无无限加载旋转器
- ✅ 无404页面

### 代码审查清单

**路由参数检查**：
- [ ] 是否使用 game_gid 而非 game_id？
- [ ] 表名生成是否使用 game["gid"] 而非 game["id"]？
- [ ] API调用是否使用 game_gid 参数？
- [ ] 路由顺序是否从具体到一般？
- [ ] 前后端参数名是否一致？

---

## API契约测试的重要性 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 1次 | **来源**: [API契约测试规范](../../CLAUDE.md#api契约测试规范), [测试指南](./testing-guide.md)

### 核心原则

**前端调用的每个API必须后端实现**

### API契约一致性测试

**运行API契约测试**:
```bash
# 运行API契约测试
python scripts/test/api_contract_test.py

# 自动修复API契约问题
python scripts/test/api_contract_test.py --fix

# 验证修复后的代码
python scripts/test/api_contract_test.py --verify
```

### 必填检查项

- ✅ 前端调用的API端点必须后端存在
- ✅ HTTP方法必须匹配（GET/POST/PUT/DELETE等）
- ✅ 参数格式必须一致（game_gid vs game_id）
- ✅ 错误状态码必须定义（404/409/500）

### 开发工作流

**新增API时**:
```python
# 1. 先在前端实现API调用
fetch('/api/games/${gameGid}', { method: 'DELETE' })

# 2. 运行契约测试
python scripts/test/api_contract_test.py

# 3. 测试会报告缺失的路由
❌ DELETE /api/games/<int:id>
   前端: GamesList.jsx:44
   后端: 路由未定义

# 4. 运行自动修复
python scripts/test/api_contract_test.py --fix

# 5. 验证修复
python scripts/test/api_contract_test.py
```

### Pre-commit Hook

```bash
# 每次提交前自动运行API契约测试
git commit  # 会自动运行契约测试

# 如果测试失败，提交被阻止
❌ API契约测试失败，提交被阻止

# 修复后重新提交
python scripts/test/api_contract_test.py --fix
git commit
```

### 代码审查清单

- [ ] 前端调用的API是否后端存在？
- [ ] HTTP方法是否匹配？
- [ ] 参数格式是否一致？
- [ ] 错误状态码是否定义？

---

## GraphQL DataLoader实施清单 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 3次 | **来源**: [GraphQL DataLoader优化报告](../reports/2026-03-07/GRAPHQL-DATALOADER-OPTIMIZATION-REPORT.md), [性能优化Phase 1-4](../reports/2026-03-07/COMPLETE-PERFORMANCE-OPTIMIZATION-REPORT-PHASE-1-4.md)

### 问题现象

**症状描述**:
- N+1查询导致数据库负载过重（查询100个事件需要101次查询）
- GraphQL响应时间慢（500ms以上）
- 数据库连接数激增

**影响范围**:
- GraphQL API的关联查询
- 事件参数批量加载
- 游戏统计查询

### 五步集成流程

**步骤1: 创建增强的DataLoader类**
```python
class ParameterLoaderEnhanced(DataLoader):
    """增强的参数批量加载器"""

    def load_by_event(self, event_id: int):
        """加载单个事件的参数"""
        return self.load(event_id)

    def load_by_events(self, event_ids: List[int]):
        """批量加载多个事件的参数"""
        return self.load_many(event_ids)

    def _batch_load_parameters(self, event_ids: List[int]) -> Promise:
        """批量加载参数（包含模板信息）"""
        placeholders = ','.join(['?'] * len(event_ids))
        cursor.execute(f"""
            SELECT
                ep.*,
                pt.name as template_name,
                pt.description as template_description
            FROM event_params ep
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE ep.event_id IN ({placeholders})
            ORDER BY ep.event_id, ep.id
        """, event_ids)

        rows = cursor.fetchall()
        # 按event_id分组返回
        result = {event_id: [] for event_id in event_ids}
        for row in rows:
            result[row['event_id']].append(row)

        return Promise.resolve([result.get(event_id, []) for event_id in event_ids])
```

**步骤2: 在Resolver中使用DataLoader**
```python
def resolve_parameters(root, info, event_id: int, active_only: bool = True):
    """使用DataLoader批量加载参数"""
    from backend.gql_api.dataloaders.optimized_loaders import get_parameter_loader

    loader = get_parameter_loader()
    params = loader.load_by_event(event_id)

    if active_only and params:
        params = [p for p in params if p.get('is_active', 0) == 1]

    return [ParameterType.from_dict(param) for param in params]
```

**步骤3: 移除主查询中的子查询**
```python
# ❌ 错误：包含子查询
event = fetch_one_as_dict("""
    SELECT
        le.*,
        (SELECT COUNT(*) FROM event_params WHERE event_id = le.id) as param_count
    FROM log_events le
    WHERE le.id = ?
""", (id,))

# ✅ 正确：移除子查询，使用DataLoader
event = fetch_one_as_dict("""
    SELECT
        le.*,
        g.gid, g.name as game_name, g.ods_db,
        ec.name as category_name
    FROM log_events le
    LEFT JOIN games g ON le.game_gid = g.gid
    LEFT JOIN event_categories ec ON le.category_id = ec.id
    WHERE le.id = ?
""", (id,))
```

**步骤4: 添加DataLoader字段解析器**
```python
def resolve_param_count(self, info):
    """使用DataLoader解析参数数量"""
    from backend.gql_api.dataloaders.optimized_loaders import get_parameter_loader

    loader = get_parameter_loader()
    params = loader.load(self.id)

    if params:
        return len(params)
    return 0
```

**步骤5: 配置缓存策略**
```python
class CachedDataLoader:
    def _batch_load_with_cache(
        self,
        keys: List[Any],
        batch_load_fn: callable,
        ttl_l1: int = 60,   # L1缓存: 60秒
        ttl_l2: int = 300   # L2缓存: 300秒
    ):
        """先从缓存获取，批量加载未缓存数据"""
        # L1缓存检查
        cache_results = {}
        missing_keys = []

        for key in keys:
            cached = cache_result.get(f"loader:{self.__class__.__name__}:{key}")
            if cached:
                cache_results[key] = cached
            else:
                missing_keys.append(key)

        # 批量加载缺失的数据
        if missing_keys:
            loaded = batch_load_fn(missing_keys)
            # 写入缓存
            for key, value in zip(missing_keys, loaded):
                cache_result.set(
                    f"loader:{self.__class__.__name__}:{key}",
                    value,
                    ttl=ttl_l1
                )
                cache_results[key] = value

        return Promise.resolve([cache_results.get(key) for key in keys])
```

### 性能提升

**优化前**:
- 事件列表查询：101次（100个事件 + 1次主查询）
- API响应时间：~500ms
- 数据库负载：高

**优化后**:
- 事件列表查询：2次（1次主查询 + 1次批量参数查询）
- API响应时间：~50ms（90%提升）
- 数据库负载：降低70-90%

**查询减少率**: 70-99%

### 代码审查清单

- [ ] DataLoader类是否继承自`DataLoader`基类？
- [ ] 批量加载函数是否返回`Promise`对象？
- [ ] 每个 GraphQL 请求是否创建新的 DataLoader 实例？
- [ ] 是否使用`@cache_invalidate`装饰器自动清理缓存？
- [ ] 在Schema中是否定义正确的字段解析器？

### 相关经验

- [性能模式 - DataLoader批量查询优化](./performance-patterns.md#dataloader批量查询优化) - 性能优化详情
- [性能模式 - 批量查询优化](./performance-patterns.md#批量查询优化) - 批量查询模式

### 案例文档

- [GraphQL DataLoader优化报告](../reports/2026-03-07/GRAPHQL-DATALOADER-OPTIMIZATION-REPORT.md)
- [DataLoader快速参考](../reports/2026-03-07/GRAPHQL-DATALOADER-QUICK-REFERENCE.md)
- [DataLoader测试指南](../reports/2026-03-07/GRAPHQL-DATALOADER-TEST-GUIDE.md)

---

## GraphQL 400错误诊断 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 2次 | **来源**: [GraphQL 400错误深入分析](../reports/2026-03-07/GRAPHQL-400-ERROR-DEEP-DIVE.md)

### 问题现象

**症状描述**:
- GraphQL查询返回400错误但信息不明确
- 难以定位具体的参数错误
- 用户无法理解错误原因

### 解决方案

**GraphQL参数验证中间件**
```python
class GraphQLValidationMiddleware:
    """GraphQL参数验证中间件"""

    def resolve(self, next, root, info, **args):
        """解析前验证参数"""
        # 获取字段定义
        field_name = info.field_name
        field_def = info.schema.get_type(info.parent_type).fields[field_name]

        # 验证必需参数
        for arg in field_def.args.values():
            if arg.required and arg.name not in args:
                raise ValidationError(
                    f"Missing required argument '{arg.name}' "
                    f"for field '{field_name}'"
                )

            # 类型验证
            if arg.name in args:
                value = args[arg.name]
                expected_type = arg.type

                # GraphQL类型到Python类型的映射
                type_map = {
                    'Int': int,
                    'String': str,
                    'Boolean': bool,
                    'Float': float
                }

                if expected_type.name in type_map:
                    expected_python_type = type_map[expected_type.name]
                    if not isinstance(value, expected_python_type):
                        raise ValidationError(
                            f"Argument '{arg.name}' expects type '{expected_type.name}', "
                            f"got '{type(value).__name__}'"
                        )

        return next(root, info, **args)
```

**增强的错误处理**
```python
class GraphQLErrorHandler:
    """GraphQL错误处理器"""

    @staticmethod
    def format_validation_error(error) -> dict:
        """格式化验证错误"""
        return {
            'message': str(error),
            'extensions': {
                'code': 'GRAPHQL_VALIDATION_ERROR',
                'locations': error.locations,
                'path': error.path,
                'details': {
                    'field': error.locations[0].line if error.locations else None,
                    'argument': getattr(error, 'argument_name', None)
                }
            }
        }
```

### 代码审查清单

- [ ] 为每个GraphQL参数定义验证规则？
- [ ] 提供清晰的错误消息和位置信息？
- [ ] 使用适当的错误码（VALIDATION_ERROR, EXECUTION_ERROR等）？
- [ ] 记录详细的错误日志便于调试？
- [ ] 在测试中验证所有参数组合？

### 业务价值

- 错误定位准确率提升90%
- 用户可读的错误消息
- 减少技术支持请求

### 案例文档

- [GraphQL 400错误深入分析](../reports/2026-03-07/GRAPHQL-400-ERROR-DEEP-DIVE.md)

---

## DataLoader缓存键设计规范 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 1次 | **来源**: [GraphQL DataLoader优化报告](../reports/2026-03-07/GRAPHQL-DATALOADER-OPTIMIZATION-REPORT.md)

### 问题现象

**症状描述**:
- 缓存键冲突导致数据不一致
- 缓存命中率低
- 无法精确控制缓存失效

### 解决方案

**分层缓存键设计**
```python
# ✅ 分层缓存键设计
CACHE_KEY_PREFIXES = {
    'events': 'event_loader',
    'parameters': 'parameter_loader',
    'games': 'game_loader',
    'categories': 'category_loader'
}

class DataLoaderCacheManager:
    """DataLoader缓存管理器"""

    @staticmethod
    def generate_cache_key(loader_type: str, key: Any, **kwargs) -> str:
        """生成分层缓存键"""
        # 基础键
        base_key = f"{CACHE_KEY_PREFIXES[loader_type]}:{key}"

        # 根据参数添加后缀
        if kwargs:
            param_suffix = ':'.join([f"{k}={v}" for k, v in sorted(kwargs.items())])
            return f"{base_key}:{param_suffix}"

        return base_key
```

**增强的DataLoader带缓存**
```python
class CachedDataLoader(DataLoader):
    """带缓存机制的DataLoader"""

    def load(self, key: Any) -> Promise:
        """加载单个键的数据（带缓存）"""
        cache_key = DataLoaderCacheManager.generate_cache_key(
            self.__class__.__name__.lower().replace('loader', ''),
            key
        )

        # 尝试从L1缓存获取
        cached_data = cache_result.get(cache_key)
        if cached_data is not None:
            return Promise.resolve(cached_data)

        # 从数据源加载
        return self._batch_load_fn([key]).then(
            lambda results: Promise.resolve(results[0])
        ).then(
            lambda data: (
                cache_result.set(cache_key, data, ttl=self.cache_ttl_l1),
                data
            )
        )
```

### 代码审查清单

- [ ] 是否使用分层缓存键（类型:ID:参数）？
- [ ] 是否区分L1（内存）和L2（Redis）缓存？
- [ ] 缓存统计监控命中率？
- [ ] 数据变更时精确失效相关缓存？
- [ ] 避免缓存大对象（单个对象<1MB）？

### 相关经验

- [性能模式 - 多级缓存架构](./performance-patterns.md#多级缓存架构) - 缓存层级设计

---

## DataLoader生命周期管理 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [GraphQL DataLoader优化报告](../reports/2026-03-07/GRAPHQL-DATALOADER-OPTIMIZATION-REPORT.md)

### 问题现象

**症状描述**:
- DataLoader实例在多个请求间共享导致数据污染
- 内存泄漏
- 缓存数据过期未及时失效

### 解决方案

**上下文DataLoader管理器**
```python
class DataLoaderContextManager:
    """DataLoader上下文管理器"""

    def __init__(self):
        self._context_data = {}
        self._request_id = None

    def set_request_id(self, request_id: str):
        """设置请求ID"""
        self._request_id = request_id
        # 创建新的DataLoader实例
        self._context_data[request_id] = {}

    def get_loader(self, loader_class: type, **kwargs):
        """获取当前请求的DataLoader实例"""
        if self._request_id not in self._context_data:
            raise RuntimeError("No active request context")

        # 检查是否已存在
        if loader_class.__name__ not in self._context_data[self._request_id]:
            self._context_data[self._request_id][loader_class.__name__] = (
                loader_class(**kwargs)
            )

        return self._context_data[self._request_id][loader_class.__name__]

    def cleanup(self):
        """清理当前请求的DataLoader"""
        if self._request_id in self._context_data:
            # 清理缓存
            for loader in self._context_data[self._request_id].values():
                if hasattr(loader, 'cleanup_cache'):
                    loader.cleanup_cache()

            # 删除上下文
            del self._context_data[self._request_id]
```

### 代码审查清单

- [ ] 每个GraphQL请求创建独立的DataLoader实例？
- [ ] 请求结束时清理DataLoader缓存？
- [ ] 避免DataLoader实例跨请求共享？
- [ ] 监控DataLoader内存使用情况？
- [ ] 实现请求级别的缓存统计？

### 相关经验

- [性能模式 - Bloom Filter在数据库防护中的应用](./performance-patterns.md#bloom-filter在数据库防护中的应用) - 内存管理

---

## DataLoader性能监控 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [GraphQL DataLoader优化报告](../reports/2026-03-07/GRAPHQL-DATALOADER-OPTIMIZATION-REPORT.md)

### 问题现象

**症状描述**:
- 无法量化DataLoader的实际效果
- 慢查询难以定位
- 缓存命中率未知

### 解决方案

**DataLoader性能监控器**
```python
class DataLoaderPerformanceMonitor:
    """DataLoader性能监控器"""

    def __init__(self):
        self.metrics = {
            'loader_stats': {},  # 按加载器分类的统计
            'query_performance': [],  # 查询性能记录
            'cache_metrics': {},  # 缓存指标
            'error_rates': {}  # 错误率
        }
        self._start_time = time.time()

    def record_load(self, loader_name: str, key: Any, duration: float,
                   from_cache: bool = False):
        """记录加载操作"""
        if loader_name not in self.metrics['loader_stats']:
            self.metrics['loader_stats'][loader_name] = {
                'total_loads': 0,
                'cache_hits': 0,
                'total_duration': 0,
                'avg_duration': 0,
                'max_duration': 0,
                'keys_processed': set()
            }

        stats = self.metrics['loader_stats'][loader_name]

        # 更新统计
        stats['total_loads'] += 1
        if from_cache:
            stats['cache_hits'] += 1
        stats['total_duration'] += duration
        stats['avg_duration'] = stats['total_duration'] / stats['total_loads']
        stats['max_duration'] = max(stats['max_duration'], duration)
        stats['keys_processed'].add(key)

    def get_report(self) -> dict:
        """生成性能报告"""
        uptime = time.time() - self._start_time

        return {
            'uptime_seconds': uptime,
            'total_loaders': len(self.metrics['loader_stats']),
            'cache_performance': self.get_cache_performance(),
            'slow_queries': self.metrics['query_performance'][-10:],
            'error_summary': self.metrics['error_rates']
        }
```

### 代码审查清单

- [ ] 记录每个DataLoader操作的执行时间？
- [ ] 监控缓存命中率和慢查询？
- [ ] 收集错误率和错误类型？
- [ ] 定期生成性能报告？
- [ ] 设置性能告警阈值？

### 相关经验

- [性能模式 - 性能监控装饰器](./performance-patterns.md#性能监控装饰器) - 性能监控通用模式

---

## DataLoader测试策略 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [DataLoader测试指南](../reports/2026-03-07/GRAPHQL-DATALOADER-TEST-GUIDE.md)

### 问题现象

**症状描述**:
- DataLoader难以进行单元测试
- 批量加载逻辑复杂，测试覆盖率低
- 缓存行为难以验证

### 解决方案

**DataLoader测试工具类**
```python
class DataLoaderTestHelper:
    """DataLoader测试助手"""

    @staticmethod
    def create_mock_data_loader(batch_fn):
        """创建模拟的DataLoader"""
        class MockDataLoader(DataLoader):
            def __init__(self):
                super().__init__()
                self.call_log = []

            def batch_load_fn(self, keys):
                """记录调用并返回结果"""
                self.call_log.append({
                    'keys': keys,
                    'timestamp': time.time()
                })
                return batch_fn(keys)

        return MockDataLoader()

    @staticmethod
    def assert_batch_performance(loader, test_keys, max_duration: float = 0.1):
        """ assert 批量加载性能"""
        start_time = time.time()

        # 执行批量加载
        result = loader.load_many(test_keys)

        duration = time.time() - start_time

        # 断言性能
        assert duration < max_duration, f"Batch load took {duration}s, expected <{max_duration}s"

        return result
```

**DataLoader单元测试**
```python
class TestEventLoader(unittest.TestCase):
    """EventLoader单元测试"""

    def test_batch_load(self):
        """测试批量加载"""
        result = self.loader.load_many([1, 2, 3])

        # 验证结果
        self.assertEqual(len(result), 3)
        result_ids = [r['id'] for r in result]
        self.assertEqual(sorted(result_ids), [1, 2, 3])

        # 验证调用日志
        self.assertEqual(len(self.loader.call_log), 1)
        self.assertEqual(sorted(self.loader.call_log[0]['keys']), [1, 2, 3])

    def test_cache_performance(self):
        """测试缓存性能"""
        # 第一次加载
        result1 = self.loader.load(1)
        self.assertEqual(len(self.loader.call_log), 1)

        # 第二次加载（应命中缓存）
        result2 = self.loader.load(1)
        self.assertEqual(len(self.loader.call_log), 1)  # 没有新的数据库调用

        # 验证缓存命中
        self.assertEqual(result1, result2)
```

### 代码审查清单

- [ ] 为每个DataLoader编写单元测试？
- [ ] 测试批量加载vs单独加载的性能差异？
- [ ] 验证缓存命中和失效行为？
- [ ] 进行集成测试验证GraphQL集成？
- [ ] 进行性能测试确保大数据量下性能？

### 相关经验

- [测试指南 - E2E测试方法论](./testing-guide.md#e2e测试方法论) - E2E测试方法

---

## GraphQL类型同步规范 ⚠️ **P0极其重要 - 2026-03-09新增**

**优先级**: P0 | **出现次数**: 3次 | **来源**: [GraphQL类型同步规范](../../CLAUDE.md#graphql类型同步规范-⚠️-极其重要---2026-03-08新增), [GraphQL 400错误修复](../reports/2026-03-08/GRAPHQL-400-FINAL-FIX.md), [TDD Red阶段报告](../reports/2026-03-08/TDD-RED-SUMMARY.md)

### 问题现象

**症状描述**:
- 前端TypeScript枚举和后端GraphQL schema不一致
- GraphQL 400 Bad Request错误
- 枚举值大小写或格式不一致

**错误示例**:
```typescript
// 前端TypeScript
FieldType.PARAM = "param"        // ✅ 正确
FieldType.NON_COMMON = "non_common"  // ✅ 正确

// 后端GraphQL Schema
FieldTypeEnum.PARAMS = "params"     // ❌ 错误：多了s
FieldTypeEnum.NON_COMMON = "non-common"  // ❌ 错误：使用了连字符
```

### 根本原因

**技术原因**:
1. **枚举值不匹配** - 前后端枚举值大小写或格式不一致
2. **Pydantic模型完整性** - Service层访问的字段未在Pydantic模型中定义
3. **GraphQL枚举命名不规范** - 未使用UPPER_SNAKE_CASE标准

### 解决方案

**1. GraphQL枚举命名规范**:

**后端GraphQL Schema**:
```graphql
# ✅ 正确：UPPER_SNAKE_CASE（GraphQL标准）
enum HqlJoinType {
  LEFT_JOIN
  RIGHT_JOIN
  INNER_JOIN
  FULL_JOIN
}

enum NodeType {
  EVENT
  JOIN
  UNION
  FILTER
}
```

**前端TypeScript**:
```typescript
// ✅ 正确：完全匹配GraphQL schema（大小写、格式）
export enum HqlJoinType {
  LEFT_JOIN = "LEFT_JOIN",
  RIGHT_JOIN = "RIGHT_JOIN",
  INNER_JOIN = "INNER_JOIN",
  FULL_JOIN = "FULL_JOIN"
}

// ❌ 错误：使用连字符导致400错误
export enum HqlJoinType {
  LEFT_JOIN = "LEFT-JOIN",      // GraphQL无法解析
  RIGHT_JOIN = "RIGHT-JOIN"     // GraphQL无法解析
}
```

**2. 使用graphql-codegen自动生成类型**:

```bash
# 安装graphql-codegen
npm install --save-dev @graphql-codegen/cli
npm install --save-dev @graphql-codegen/typescript
npm install --save-dev @graphql-codegen/typescript-operations

# 配置文件：codegen.yml
schema:
  - http://127.0.0.1:5001/api/graphql

documents:
  - "frontend/src/graphql/**/*.tsx"

generates:
  frontend/src/graphql/generated-types.ts:
    plugins:
      - typescript
      - typescript-operations
```

**生成类型**:
```bash
# 从GraphQL schema自动生成TypeScript类型
npx graphql-codegen

# 添加到package.json scripts
"scripts": {
  "generate:types": "graphql-codegen",
  "predev": "npm run generate:types"  # 开发前自动生成
}
```

**使用生成的类型**:
```typescript
// frontend/src/canvas/components/EventNodeBuilder.tsx
import { CreateEventNodeMutation, HqlJoinType } from '@/graphql/generated-types';

function EventNodeBuilder() {
  const [createNode] = useMutation(CREATE_EVENT_NODE);

  const handleCreate = async () => {
    // ✅ 类型安全：所有类型从GraphQL schema生成
    const result = await createNode({
      variables: {
        input: {
          nodeType: NodeType.Join,
          joinType: HqlJoinType.LeftJoin  // 枚举类型安全
        }
      }
    });
  };
}
```

**3. Pydantic模型完整性**:

```python
# backend/models/schemas.py
from pydantic import BaseModel, Field
from typing import Optional

class EventNodeInput(BaseModel):
    """Event node creation/update input"""

    # ✅ 所有字段必须在Pydantic模型中定义
    id: Optional[int] = Field(None, description="Node ID")
    node_type: str = Field(..., description="Node type")
    event_type: Optional[str] = Field(None, description="Event type")  # ← 必须定义
    table_name: Optional[str] = Field(None, description="Table name")
    join_type: Optional[str] = Field(None, description="Join type")
```

**Service层安全访问**:
```python
def create_event_node(self, node_data: EventNodeInput):
    # ✅ 安全：所有字段已在Pydantic模型中定义
    event_type = node_data.event_type  # 字段存在，无AttributeError
```

### 预防措施

**代码审查检查清单**:
- [ ] TypeScript枚举是否完全匹配GraphQL schema（大小写敏感）？
- [ ] 是否使用graphql-codegen生成类型？
- [ ] 是否避免硬编码枚举字符串？
- [ ] 是否使用生成的枚举类型而非字符串字面量？

**自动化工具**:
```bash
# 运行API契约测试
python scripts/test/api_contract_test.py

# 生成最新类型
npm run generate:types

# 测试GraphQL mutation（有效枚举值）
npm run test
```

### 相关经验

- [Pydantic模型完整性](#pydantic模型完整性-⚠️-p0极其重要---2026-03-09新增) - 后端模型完整性
- [GraphQL 400错误诊断](#graphql-400错误诊断-⚠️-p0极其重要---2026-03-09新增) - 400错误诊断方法

---

## GraphQL 400错误诊断 ⚠️ **P0极其重要 - 2026-03-09新增**

**优先级**: P0 | **出现次数**: 2次 | **来源**: [GraphQL 400错误修复](../reports/2026-03-08/GRAPHQL-400-FINAL-FIX.md), [Dashboard优化报告](../reports/2026-03-07/DASHBOARD-REALTIME-OPTIMIZATION-REPORT.md)

### 问题现象

**症状描述**:
- GraphQL mutation返回400 Bad Request
- 错误信息：`Enum 'FieldTypeEnum' cannot represent value: 'param'`
- 前端无法诊断问题原因

### 根本原因

**技术原因**:
1. **枚举值格式不匹配** - 连字符vs下划线
2. **大小写不一致** - 后端UPPER_SNAKE_CASE vs 前端camelCase
3. **Apollo Client缓存** - 旧mutation定义仍在缓存中

### 解决方案

**1. 浏览器DevTools Network标签**:
```bash
# 1. 打开浏览器DevTools (F12)
# 2. 切换到Network标签
# 3. 查找GraphQL请求（红色=失败，黄色=等待）
# 4. 点击请求，查看Status Code和Response
```

**2. GraphiQL IDE测试**:
```bash
# 启动GraphiQL IDE
cd backend
python web_app.py

# 访问 http://127.0.0.1:5001/api/graphql?ide

# 测试mutation
mutation {
  createEvent(gameGid: 90000001, eventName: "test") {
    ok
    game {
      gid
      name
    }
  }
}
```

**3. Apollo Client缓存清理**:
```javascript
// 在浏览器Console执行
localStorage.clear();
sessionStorage.clear();

// 或者更彻底
if (window.__APOLLO_CLIENT__) {
  window.__APOLLO_CLIENT__.clearStore();
  console.log('✅ Apollo Client缓存已清除');
}

location.reload(true);
```

**4. 开发环境禁用缓存**:
```typescript
// frontend/src/graphql/client.ts
import { ApolloClient, InMemoryCache } from '@apollo/client';

const isDev = import.meta.env.DEV;

export const apolloClient = new ApolloClient({
  uri: '/api/graphql',
  cache: new InMemoryCache({ addTypename: true }),
  // 🆕 开发环境：禁用缓存持久化
  defaultOptions: isDev ? {
    watchQuery: {
      fetchPolicy: 'network-only',  // 强制网络请求
      errorPolicy: 'all'
    },
    query: {
      fetchPolicy: 'network-only',  // 强制网络请求
      errorPolicy: 'all'
    },
    mutate: {
      errorPolicy: 'all'
    }
  } : undefined
});
```

### 预防措施

**诊断流程**:
1. ✅ Network标签查看GraphQL请求
2. ✅ GraphiQL IDE测试mutation
3. ✅ 检查枚举值大小写和格式
4. ✅ 清理Apollo Client缓存
5. ✅ 开发环境禁用缓存

**清理脚本**:
```javascript
// frontend/scripts/clear-cache.js
const fs = require('fs');

console.log('🧹 清理Vite缓存...');
fs.rmSync('node_modules/.vite', { recursive: true, force: true });

console.log('✨ 清理完成！');
console.log('📌 接下来请：');
console.log('1. 打开浏览器DevTools (F12)');
console.log('2. 执行: localStorage.clear(); sessionStorage.clear();');
console.log('3. 硬刷新: Cmd+Shift+R');
```

**package.json配置**:
```json
{
  "scripts": {
    "clear-cache": "node frontend/scripts/clear-cache.js",
    "dev:fresh": "npm run clear-cache && npm run dev"
  }
}
```

### 相关经验

- [GraphQL类型同步规范](#graphql类型同步规范-⚠️-p0极其重要---2026-03-09新增) - 类型同步
- [Pydantic模型完整性](#pydantic模型完整性-⚠️-p0极其重要---2026-03-09新增) - 模型完整性

---

## GraphQL迁移策略 ⚠️ **P0极其重要 - 2026-03-13新增**

> **来源**: 12个GraphQL迁移报告（2026-02-25至2026-03-13）
> **核心成果**: GraphQL覆盖率95%+，性能提升显著
> **优先级**: P0

### 并行迁移策略 ⭐ **极其重要**

**核心洞察**: GraphQL迁移成功的关键在于识别任务依赖关系并实施并行处理

**依赖分组**:
- **组1（无依赖，可并行）**: 路由配置、性能监控、批量操作、文档
- **组2（依赖组1）**: 查询优化、订阅功能
- **组3（依赖组2）**: 剩余页面迁移、REST API移除

**执行成果**:
- ✅ 8个核心任务完成
- ✅ 进度75%
- ✅ 性能提升显著

### GraphQL性能监控体系 🆕

**建立完整的性能监控工具对比GraphQL和REST API**

**性能改善指标**:
| 指标 | REST API | GraphQL | 改善 |
|------|----------|---------|------|
| 请求数 | 15次 | 5次 | ↓ 66% |
| 响应时间 | 450ms | 280ms | ↓ 38% |
| 数据传输 | 120KB | 75KB | ↓ 37% |
| 缓存命中率 | 0% | 45% | ↑ 45% |

**监控实现**:
- **代码量**: 250+行监控代码
- **监控方法**: 15个
- **覆盖**: 查询、变更、订阅全流程

**监控指标**:
```python
# backend/core/monitoring/performance_monitor.py
class GraphQLPerformanceMonitor:
    """GraphQL性能监控"""

    def track_query(self, query: str, variables: dict):
        """跟踪查询性能"""
        start_time = time.time()

        # 执行查询
        result = execute_query(query, variables)

        # 记录指标
        duration = time.time() - start_time
        self.metrics.record({
            'query': query,
            'duration': duration,
            'result_size': len(result),
            'cache_hit': self.cache_checker.check()
        })

        return result
```

### 批量操作Mutations设计 ⭐

**经验**: GraphQL批量操作减少网络请求，提高效率

**批量Mutations**:
```graphql
# 批量删除事件
mutation BATCH_DELETE_EVENTS($event_ids: [Int!]!) {
  batchDeleteEvents(eventIds: $event_ids) {
    success
    deletedCount
    errors {
      id
      message
    }
  }
}

# 批量更新事件
mutation BATCH_UPDATE_EVENTS($updates: [EventUpdateInput!]!) {
  batchUpdateEvents(updates: $updates) {
    success
    updatedCount
    events {
      id
      name
      eventType
    }
  }
}
```

**实现要点**:
- ✅ 支持事务性操作
- ✅ 减少前端-后端往返次数
- ✅ 返回详细的错误信息
- ✅ 6个批量mutations：BATCH_DELETE_EVENTS、BATCH_UPDATE_EVENTS等

### GraphQL订阅实时推送 🆕

**WebSocket实现实时数据更新**

**订阅类型**:
```graphql
# 事件更新订阅
subscription ON_EVENT_UPDATED($game_gid: Int!) {
  onEventUpdated(gameGid: $game_gid) {
    id
    name
    eventType
    updatedAt
  }
}

# 参数更新订阅
subscription ON_PARAMETER_UPDATED($game_gid: Int!) {
  onParameterUpdated(gameGid: $game_gid) {
    id
    paramName
    paramType
    updatedAt
  }
}
```

**订阅特性**:
- ✅ 6个订阅类型：ON_EVENT_UPDATED、ON_PARAMETER_UPDATED等
- ✅ 自动重连机制
- ✅ 适合Dashboard、Canvas等实时场景

**前端使用**:
```typescript
import { useSubscription } from '@apollo/client';

const EVENT_UPDATED_SUBSCRIPTION = gql`
  subscription ON_EVENT_UPDATED($game_gid: Int!) {
    onEventUpdated(gameGid: $game_gid) {
      id
      name
      eventType
      updatedAt
    }
  }
`;

function EventList({ gameGid }) {
  const { data, loading } = useSubscription(
    EVENT_UPDATED_SUBSCRIPTION,
    { variables: { game_gid: gameGid } }
  );

  // 实时更新事件列表
  useEffect(() => {
    if (data?.onEventUpdated) {
      // 更新本地状态
      updateEvent(data.onEventUpdated);
    }
  }, [data]);

  return <div>{/* 渲染事件列表 */}</div>;
}
```

### GraphQL迁移最佳实践

**1. 渐进式迁移**:
- ✅ 先迁移查询（Query）
- ✅ 再迁移变更（Mutation）
- ✅ 最后迁移订阅（Subscription）
- ✅ 保持REST和GraphQL并行运行

**2. 性能优化**:
- ✅ 使用DataLoader批量查询
- ✅ 实现查询缓存
- ✅ 添加字段级权限控制
- ✅ 监控慢查询

**3. 错误处理**:
```python
# backend/gql_api/middleware/error_handling.py
class GraphQLErrorHandler:
    """GraphQL错误处理中间件"""

    @staticmethod
    def handle_format_error(error):
        """处理GraphQL格式错误"""
        logger.error(f"GraphQL Format Error: {error}")
        return {
            'message': 'GraphQL查询格式错误',
            'code': 'GRAPHQL_FORMAT_ERROR',
            'details': str(error)
        }

    @staticmethod
    def handle_validation_error(error):
        """处理GraphQL验证错误"""
        logger.error(f"GraphQL Validation Error: {error}")
        return {
            'message': 'GraphQL查询验证失败',
            'code': 'GRAPHQL_VALIDATION_ERROR',
            'details': error.message
        }
```

**4. 类型安全**:
```typescript
// 使用graphql-codegen生成类型
// frontend/src/graphql/generated-types.ts
export interface Event {
  id: number;
  name: string;
  eventType: string;
  gameGid: number;
}

export interface GetEventsQueryVariables {
  gameGid: number;
}

export interface GetEventsQuery {
  events: Event[];
}
```

### 迁移检查清单

**迁移前**:
- [ ] 识别所有REST API端点
- [ ] 分析依赖关系
- [ ] 制定并行迁移计划
- [ ] 设置性能监控

**迁移中**:
- [ ] 保持REST和GraphQL并行
- [ ] 逐个端点迁移
- [ ] 对比性能指标
- [ ] 验证功能完整性

**迁移后**:
- [ ] 性能测试
- [ ] E2E测试
- [ ] 废弃REST API
- [ ] 更新文档

### 相关经验

- [GraphQL类型同步规范](#graphql类型同步规范-⚠️-p0极其重要---2026-03-09新增) - 类型同步
- [DataLoader实施清单](#graphql-dataloader实施清单-2026-03-09新增) - DataLoader优化
- [批量查询优化模式](#批量查询优化模式-2026-03-09新增) - 批量查询
- [性能模式 - 并行优化策略](./performance-patterns.md#并行优化策略) - 并行执行

---

## 相关经验文档

- [安全要点 - SQL注入防护](./security-essentials.md#sql注入防护) - API安全
- [安全要点 - XSS防护](./security-essentials.md#xss防护-⚠️-p0极其重要---2026-03-09新增) - XSS防护
- [测试指南 - API契约测试](./testing-guide.md#api契约测试) - API契约测试方法
- [性能模式 - DataLoader批量查询优化](./performance-patterns.md#dataloader批量查询优化) - DataLoader性能优化
- [性能模式 - 并行优化策略](./performance-patterns.md#并行优化策略) - 并行开发优化
- [性能模式 - 缓存失效装饰器](./performance-patterns.md#缓存失效装饰器的自动化实现-2026-03-09新增) - 缓存失效自动化
- [测试指南 - TDD Red阶段经验](./testing-guide.md#tdd-red阶段经验-2026-03-09新增) - TDD实施经验

---

**文档统计**:
- P0经验点：6个
- P1经验点：4个
- 总计：10个API设计模式经验点
- 最后更新：2026-03-09 🆕 新增GraphQL类型同步、400错误诊断、缓存失效装饰器、TDD Red阶段经验