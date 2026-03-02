# Games API

**游戏管理API**

**版本**: 8.0.0 (Phase 1-2)
**文件**: `backend/api/routes/games.py`
**架构**: GameService → GameRepository → GameEntity

---

## 概述

游戏API提供游戏信息的完整CRUD操作，支持统计查询和批量操作。

**核心特性**:
- ✅ 完整CRUD操作
- ✅ 统计信息查询
- ✅ 批量更新和删除
- ✅ 业务GID (game_gid) 作为主标识
- ✅ 自动缓存管理

**架构变更**:
- Phase 2: 统一使用game_gid而非game_id
- Phase 1: 基础CRUD实现

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
