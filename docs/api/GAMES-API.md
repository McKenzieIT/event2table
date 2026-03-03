# Games API

**游戏管理API**

**版本**: 9.0.0 (Repository Pattern Migration)
**文件**: `backend/api/routes/games.py`
**架构**: API Layer → GameService → GameRepository → GameEntity

---

## 概述

游戏API提供游戏信息的完整CRUD操作，支持统计查询和批量操作。

**核心特性**:
- ✅ 完整CRUD操作
- ✅ 统计信息查询
- ✅ 批量更新和删除
- ✅ 业务GID (game_gid) 作为主标识
- ✅ 自动缓存管理
- ✅ Entity架构 (GameEntity) ⭐
- ✅ Repository模式 ⭐

**架构层次**:
```
API Layer (games.py)
    ↓
GameService (业务逻辑)
    ↓
GameRepository (数据访问)
    ↓
GameEntity (数据模型 + 验证)
    ↓
Database (SQLite)
```

**Entity架构优势** ⭐:
- 自动验证: Pydantic Entity自动验证输入
- 类型安全: 完整的类型注解和IDE支持
- 序列化: Entity.model_dump()自动转换为JSON
- 文档: 自动生成API文档和数据模型

---

## Repository Pattern ⭐

### 架构模式

所有数据访问都通过Repository层进行：

```python
# ✅ 正确：使用Service层
from backend.services.games.game_service import GameService

service = GameService()
games = service.get_games()

# ❌ 错误：直接数据库访问
games = fetch_all_as_dict('SELECT * FROM games')
```

### Repository层职责

**GameRepository** (`backend/models/repositories/games.py`):
- 封装所有game相关的SQL查询
- 返回Entity对象（而非字典）
- 提供CRUD操作
- 管理缓存策略

**示例**:
```python
class GameRepository(GenericRepository):
    """游戏仓储类"""

    def find_by_gid(self, gid: int) -> Optional[GameEntity]:
        """根据业务GID查询游戏"""
        query = "SELECT * FROM games WHERE gid = ?"
        row = fetch_one_as_dict(query, (gid,))
        return GameEntity(**row) if row else None  # ⭐ 返回Entity

    def get_all_with_event_count(self) -> List[GameEntity]:
        """获取所有游戏及其事件数量"""
        query = """
            SELECT g.*, COUNT(DISTINCT le.id) as event_count
            FROM games g
            LEFT JOIN log_events le ON g.id = le.game_id
            GROUP BY g.id
        """
        rows = fetch_all_as_dict(query)
        return [GameEntity(**row) for row in rows]  # ⭐ 返回Entity列表
```

### Entity对象访问 ⭐

API响应返回Entity对象，支持属性访问：

```python
# 旧方式：字典访问
game['name']
game['game_gid']

# 新方式：Entity属性访问 ⭐
game.name
game.gid
game.event_count  # 关联数据自动加载
```

### 缓存策略

**读取操作** (自动缓存):
- Games列表: 1800秒TTL
- Game详情: 900秒TTL
- 统计信息: 600秒TTL

**写入操作** (自动失效):
- CREATE: 自动清理所有游戏相关缓存
- UPDATE: 自动清理当前游戏缓存
- DELETE: 自动清理所有游戏相关缓存

```python
from backend.core.cache.decorators import cached, cache_invalidate

class GameService:
    @cached(ttl=1800)  # ⭐ 读取：使用缓存
    def get_games(self) -> List[GameEntity]:
        return self.game_repo.get_all()

    @cache_invalidate  # ⭐ 写入：清理缓存
    def create_game(self, game_data: GameEntity) -> GameEntity:
        return self.game_repo.create(game_data.model_dump())
```

---

## 端点列表

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/games` | 列出游戏 |
| GET | `/api/games/<game_gid>` | 获取游戏详情 |
| POST | `/api/games` | 创建游戏 |
| PUT/PATCH | `/api/games/<game_gid>` | 更新游戏 |
| DELETE | `/api/games/<game_gid>` | 删除游戏 |
| POST | `/api/games/batch-update` | 批量更新游戏 |
| DELETE | `/api/games/batch` | 批量删除游戏 |

---

## 端点详情

### GET /api/games

列出所有游戏。

**查询参数**:
| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| include_stats | bool | ❌ | false | 是否包含详细统计 |
| simple | bool | ❌ | false | 简单模式 |

**请求示例**:
```bash
# 简单列表
GET /api/games

# 包含统计信息
GET /api/games?include_stats=true

# 简单模式（仅Entity字段）
GET /api/games?simple=true
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "gid": "10000147",
      "name": "STAR001",
      "ods_db": "ieu_ods",
      "dwd_prefix": "dwd",
      "description": "测试游戏",
      "event_count": 150,
      "parameter_count": 450,
      "node_count": 25,
      "created_at": "2026-02-01T00:00:00",
      "updated_at": "2026-02-28T12:00:00"
    }
  ]
}
```

**Service层**: `GameService.get_games_with_detailed_stats()`
**缓存策略**: 1800秒TTL
**Entity架构**: ⭐ 响应数据由GameEntity自动序列化

---

## Entity架构详解 ⭐

### GameEntity定义

```python
# backend/models/entities.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import html

class GameEntity(BaseModel):
    """
    游戏实体 - 全局唯一的游戏数据模型

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

    # 关联数据（仅在查询时填充）
    event_count: Optional[int] = Field(0, description="事件数量统计")
    parameter_count: Optional[int] = Field(0, description="参数数量统计")
    node_count: Optional[int] = Field(0, description="节点数量统计")

    model_config = {"from_attributes": True}

    @field_validator('name')
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """防止XSS攻击：转义HTML字符"""
        return html.escape(v.strip())
```

### Entity自动验证

**请求验证** (自动):
```python
# ✅ 有效请求
{
  "gid": "10000147",
  "name": "Game Name",
  "ods_db": "ieu_ods"
}

# ❌ 无效请求 (Entity自动捕获)
{
  "gid": "10000147",
  "name": "",  # ❌ 最小长度1
  "ods_db": "invalid_db"  # ❌ 必须是ieu_ods或overseas_ods
}
```

**错误响应** (自动生成):
```json
{
  "success": false,
  "error": "Validation error: 2 validation errors for GameEntity\n  name\n    String should have at least 1 character [type=string_too_short, min_length=1]\n  ods_db\n    String should match pattern '^(ieu_ods|overseas_ods)$' [type=string_pattern_mismatch]"
}
```

### Entity序列化

**自动转换为JSON**:
```python
# Service层返回Entity
game = GameEntity(
    id=1,
    gid="10000147",
    name="Game Name",
    ods_db="ieu_ods"
)

# API层自动序列化
return json_success_response(
    data=game.model_dump(),  # ⭐ 自动转换为字典
    message="Success"
)

# 前端接收
{
  "success": true,
  "data": {
    "id": 1,
    "gid": "10000147",
    "name": "Game Name",
    "ods_db": "ieu_ods"
  }
}
```

---

---

### GET /api/games/<game_gid>

根据业务GID获取游戏详情。

**路径参数**:
| 参数 | 类型 | 描述 |
|------|------|------|
| game_gid | int | 游戏业务GID |

**请求示例**:
```bash
GET /api/games/10000147
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "gid": "10000147",
    "name": "STAR001",
    "ods_db": "ieu_ods",
    "dwd_prefix": "dwd",
    "description": "测试游戏",
    "event_count": 150,
    "parameter_count": 450,
    "node_count": 25,
    "created_at": "2026-02-01T00:00:00",
    "updated_at": "2026-02-28T12:00:00"
  }
}
```

**错误响应**:
| 状态码 | 描述 |
|--------|------|
| 404 | 游戏不存在 |

**Service层**: `GameService.get_game_by_gid(game_gid)`

---

### POST /api/games

创建新游戏。

**请求体**:
```json
{
  "gid": "10000148",
  "name": "STAR002",
  "ods_db": "ieu_ods",
  "dwd_prefix": "dwd",
  "description": "新游戏"
}
```

**字段验证**:
| 字段 | 类型 | 必填 | 验证规则 |
|------|------|------|----------|
| gid | string | ✅ | 唯一标识，长度1-50 |
| name | string | ✅ | 游戏名称，长度1-100 |
| ods_db | string | ✅ | ODS数据库（ieu_ods/overseas_ods） |
| dwd_prefix | string | ❌ | DWD表前缀（默认"dwd"） |
| description | string | ❌ | 描述，最大500字符 |

**请求示例**:
```bash
POST /api/games
Content-Type: application/json

{
  "gid": "90000001",
  "name": "测试游戏001",
  "ods_db": "ieu_ods",
  "description": "用于测试的游戏"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "Game created successfully",
  "data": {
    "id": 2,
    "gid": "90000001",
    "name": "测试游戏001",
    "ods_db": "ieu_ods",
    "dwd_prefix": "dwd",
    "description": "用于测试的游戏",
    "created_at": "2026-03-01T10:00:00",
    "updated_at": "2026-03-01T10:00:00"
  }
}
```

**错误响应**:
| 状态码 | 描述 |
|--------|------|
| 400 | 参数验证失败 |
| 409 | 游戏GID已存在 |

**Service层**: `GameService.create_game(game_data)`

---

### PUT/PATCH /api/games/<game_gid>

更新游戏信息。

**路径参数**:
| 参数 | 类型 | 描述 |
|------|------|------|
| game_gid | int | 游戏业务GID |

**请求体**:
```json
{
  "name": "STAR001更新",
  "description": "更新后的描述"
}
```

**请求示例**:
```bash
PUT /api/games/10000147
Content-Type: application/json

{
  "name": "STAR001",
  "description": "正式环境游戏"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "Game updated successfully",
  "data": {
    "id": 1,
    "gid": "10000147",
    "name": "STAR001",
    "description": "正式环境游戏",
    "updated_at": "2026-03-01T10:30:00"
  }
}
```

**错误响应**:
| 状态码 | 描述 |
|--------|------|
| 400 | 参数验证失败 |
| 404 | 游戏不存在 |

**Service层**: `GameService.update_game(game_gid, update_data)`

---

### DELETE /api/games/<game_gid>

删除游戏。

**路径参数**:
| 参数 | 类型 | 描述 |
|------|------|------|
| game_gid | int | 游戏业务GID |

**请求示例**:
```bash
DELETE /api/games/90000001
```

**响应示例**:
```json
{
  "success": true,
  "message": "Game deleted successfully"
}
```

**错误响应**:
| 状态码 | 描述 |
|--------|------|
| 404 | 游戏不存在 |

**注意事项**:
- ⚠️ 禁止删除 GID 10000147 (STAR001)
- 删除游戏会级联删除所有关联数据

**Service层**: `GameService.delete_game(game_gid)`

---

## 数据模型

### GameEntity

```python
class GameEntity(BaseModel):
    """游戏实体"""
    id: Optional[int] = None
    gid: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    ods_db: str = Field(..., pattern=r'^(ieu_ods|overseas_ods)$')
    description: Optional[str] = Field(None, max_length=500)
    dwd_prefix: str = Field("dwd", max_length=50)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # 统计字段（仅查询时返回）
    event_count: Optional[int] = 0
    parameter_count: Optional[int] = 0
    node_count: Optional[int] = 0
```

---

## 使用场景

### 1. 创建测试游戏

```javascript
// 创建测试游戏（使用90000000+范围的GID）
const game = await fetch('/api/games', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    gid: '90000001',
    name: '测试游戏001',
    ods_db: 'ieu_ods',
    description: '用于自动化测试'
  })
}).then(r => r.json());

console.log(`Game created: ${game.data.gid}`);
```

### 2. 获取游戏列表

```javascript
// 获取游戏列表（包含统计）
const games = await fetch('/api/games?include_stats=true')
  .then(r => r.json());

games.data.forEach(game => {
  console.log(`${game.name} (${game.gid})`);
  console.log(`  Events: ${game.event_count}`);
  console.log(`  Parameters: ${game.parameter_count}`);
});
```

---

## 相关文档

- [Events API](EVENTS-API.md) - 事件管理
- [Parameters API](PARAMETERS-API.md) - 参数管理
- [STAR001保护规则](../development/STAR001-GAME-PROTECTION.md)
