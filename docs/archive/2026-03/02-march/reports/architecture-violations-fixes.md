# 架构违规快速修复指南

本指南提供常见架构违规的快速修复方案，帮助开发人员快速修复代码。

## 目录

1. [Service层直接数据库访问](#1-service层直接数据库访问)
2. [缺少Entity验证](#2-缺少entity验证)
3. [错误处理不一致](#3-错误处理不一致)
4. [Repository层业务逻辑](#4-repository层业务逻辑)

---

## 1. Service层直接数据库访问

### 违规模式

```python
# ❌ 错误：Service层直接访问数据库
from backend.core.utils import fetch_one_as_dict, fetch_all_as_dict

class SomeService:
    def get_game(self, game_gid: int):
        game = fetch_one_as_dict(
            "SELECT * FROM games WHERE gid = ?",
            (game_gid,)
        )
        return game
```

### 修复方案

**步骤1**: 创建Repository方法（如果不存在）

```python
# backend/models/repositories/games.py
class GameRepository(GenericRepository):
    def find_by_gid(self, gid: int) -> Optional[GameEntity]:
        """根据业务GID查询游戏"""
        query = "SELECT * FROM games WHERE gid = ?"
        row = fetch_one_as_dict(query, (gid,))
        return GameEntity(**row) if row else None
```

**步骤2**: 在Service层使用Repository

```python
# ✅ 正确：Service层通过Repository访问数据
from backend.models.repositories.games import GameRepository
from backend.models.entities import GameEntity

class SomeService:
    def __init__(self):
        self.game_repo = GameRepository()

    def get_game(self, game_gid: int) -> Optional[GameEntity]:
        game = self.game_repo.find_by_gid(game_gid)
        return game
```

### 常见修复模式

#### 模式1: 单个记录查询

**错误**:
```python
game = fetch_one_as_dict("SELECT * FROM games WHERE id = ?", (game_id,))
```

**正确**:
```python
game = game_repo.find_by_id(game_id)
```

#### 模式2: 列表查询

**错误**:
```python
events = fetch_all_as_dict("SELECT * FROM log_events WHERE game_gid = ?", (game_gid,))
```

**正确**:
```python
events = event_repo.find_by_game_gid(game_gid)
```

#### 模式3: 统计查询

**错误**:
```python
count = fetch_one_as_dict(
    "SELECT COUNT(*) as count FROM games WHERE gid = ?",
    (game_gid,)
)
```

**正确**:
```python
count = game_repo.count_by_gid(game_gid)
```

### 检查清单

修复Service层数据库访问时，确保：
- [ ] 所有`fetch_one_as_dict`调用移到Repository层
- [ ] 所有`fetch_all_as_dict`调用移到Repository层
- [ ] 所有`execute_update`调用移到Repository层
- [ ] 所有`execute_insert`调用移到Repository层
- [ ] Service层只调用Repository方法
- [ ] Repository方法返回Entity对象

---

## 2. 缺少Entity验证

### 违规模式

```python
# ❌ 错误：手动验证输入
@api_bp.route("/api/events", methods=["POST"])
def api_create_event():
    is_valid, data, error = validate_json_request([
        "game_gid", "event_name", "event_name_cn"
    ])
    if not is_valid:
        return json_error_response(error, status_code=400)

    # 手动验证每个字段
    event_name = data.get("event_name", "").strip()
    if len(event_name) == 0:
        return json_error_response("event_name cannot be empty")
    if len(event_name) > 200:
        return json_error_response("event_name exceeds maximum length")

    # 手动XSS防护
    event_name = html.escape(event_name)

    # 调用Service层
    event = event_service.create_event(data)
    return json_success_response(data=event)
```

### 修复方案

```python
# ✅ 正确：使用Entity自动验证
from backend.models.entities import EventEntity
from pydantic import ValidationError

@api_bp.route("/api/events", methods=["POST"])
def api_create_event():
    try:
        # 自动验证和类型转换
        event_data = EventEntity(**request.get_json())

        # 调用Service层
        event = event_service.create_event(event_data)

        # 返回响应
        return json_success_response(data=event.model_dump())

    except ValidationError as e:
        # Pydantic自动提供详细错误信息
        return json_error_response(
            f"Validation error: {e}",
            status_code=400
        )
    except ValueError as e:
        # 业务逻辑错误
        return json_error_response(str(e), status_code=409)
    except Exception as e:
        # 系统错误
        logger.error(f"Error creating event: {e}", exc_info=True)
        return json_error_response(
            "Failed to create event",
            status_code=500
        )
```

### Entity验证优势

| 验证类型 | 手动验证 | Entity验证 |
|---------|---------|-----------|
| **必填字段** | 手动if判断 | `Field(...)` |
| **类型转换** | 手动int() | 自动 |
| **长度限制** | 手动len() | `Field(min_length=1, max_length=100)` |
| **范围限制** | 手动if | `Field(ge=0, le=100)` |
| **XSS防护** | 手动html.escape | `@field_validator`自动 |
| **格式验证** | 正则表达式 | `Field(pattern=r'^...')` |
| **错误消息** | 手动拼接 | 自动生成 |

### 常见Entity定义

#### GameEntity

```python
from backend.models.entities import GameEntity

# ✅ 自动验证
game_data = GameEntity(
    gid=10000147,
    name="STAR001",  # 自动XSS防护
    ods_db="ieu_ods",  # 自动验证范围
    description="测试游戏"
)

# ❌ 验证失败示例
try:
    game_data = GameEntity(
        gid=-1,  # ❌ ValidationError: gid必须是正整数
        name="",  # ❌ ValidationError: name至少1个字符
        ods_db="invalid_db"  # ❌ ValidationError: 只允许ieu_ods或overseas_ods
    )
except ValidationError as e:
    print(e)  # 详细错误信息
```

#### EventEntity

```python
from backend.models.entities import EventEntity

# ✅ 自动验证
event_data = EventEntity(
    game_gid=10000147,
    event_name="login",  # 自动XSS防护
    event_name_cn="登录"  # 可选
)

# ❌ 验证失败示例
try:
    event_data = EventEntity(
        game_gid=-1,  # ❌ ValidationError: game_gid必须>=0
        event_name="",  # ❌ ValidationError: event_name至少1个字符
        event_name_cn="X" * 101  # ❌ ValidationError: 最多100字符
    )
except ValidationError as e:
    print(e)
```

#### ParameterEntity

```python
from backend.models.entities import ParameterEntity

# ✅ 自动验证
param_data = ParameterEntity(
    event_id=1,
    game_gid=10000147,
    name="zone_id",
    param_type="param",  # 自动验证: base/param/common/calculate
    json_path="$.zoneId",  # 自动验证格式
    hive_type="INT"
)

# ❌ 验证失败示例
try:
    param_data = ParameterEntity(
        event_id=0,  # ❌ ValidationError: event_id必须>0
        game_gid=-1,  # ❌ ValidationError: game_gid必须>=0
        param_type="invalid",  # ❌ ValidationError: 只允许base/param/common/calculate
        json_path="invalid_format"  # ❌ ValidationError: 必须以'$.开头
    )
except ValidationError as e:
    print(e)
```

### 检查清单

添加Entity验证时，确保：
- [ ] POST请求使用Entity验证
- [ ] PUT请求使用Entity验证
- [ ] PATCH请求使用Entity验证
- [ ] 移除手动验证代码
- [ ] 处理ValidationError异常
- [ ] 返回友好的错误消息

---

## 3. 错误处理不一致

### 违规模式

#### 模式1: 缺少try-except

```python
# ❌ 错误：没有错误处理
@api_bp.route("/api/events/<int:event_id>", methods=["GET"])
def api_get_event(event_id):
    event = event_service.get_event_by_id(event_id)
    return json_success_response(data=event)
```

#### 模式2: 原始异常暴露

```python
# ❌ 错误：暴露原始异常信息
@api_bp.route("/api/events", methods=["POST"])
def api_create_event():
    try:
        event = event_service.create_event(data)
        return json_success_response(data=event)
    except Exception as e:
        logger.error(f"Error: {e}")
        return json_error_response(str(e), status_code=500)  # ❌ 可能暴露SQL、路径
```

### 修复方案

#### 标准错误处理模板

```python
# ✅ 正确：完整的错误处理
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

@api_bp.route("/api/events/<int:event_id>", methods=["GET"])
def api_get_event(event_id):
    try:
        # 业务逻辑
        event = event_service.get_event_by_id(event_id)

        if not event:
            return json_error_response(
                f"Event not found: {event_id}",
                status_code=404
            )

        return json_success_response(data=event.model_dump())

    except ValueError as e:
        # 业务逻辑错误（如验证失败）
        logger.warning(f"Invalid request: {e}")
        return json_error_response(str(e), status_code=400)

    except ValidationError as e:
        # Pydantic验证错误
        logger.warning(f"Validation error: {e}")
        return json_error_response(
            f"Validation error: {e}",
            status_code=400
        )

    except Exception as e:
        # 系统错误
        logger.error(f"Error getting event: {e}", exc_info=True)
        return json_error_response(
            "Failed to get event",
            status_code=500
        )
```

#### POST请求错误处理

```python
@api_bp.route("/api/events", methods=["POST"])
def api_create_event():
    try:
        # 1. 自动验证输入
        event_data = EventEntity(**request.get_json())

        # 2. 调用Service层
        event = event_service.create_event(event_data)

        # 3. 返回成功响应
        return json_success_response(
            data=event.model_dump(),
            message="Event created successfully"
        )

    except ValidationError as e:
        # 输入验证失败
        return json_error_response(
            f"Validation error: {e}",
            status_code=400
        )

    except ValueError as e:
        # 业务逻辑错误（如gid已存在）
        return json_error_response(str(e), status_code=409)

    except Exception as e:
        # 系统错误
        logger.error(f"Error creating event: {e}", exc_info=True)
        return json_error_response(
            "Failed to create event",
            status_code=500
        )
```

### 错误分类处理

| 错误类型 | 异常类 | HTTP状态码 | 错误消息 |
|---------|--------|-----------|---------|
| **输入验证失败** | `ValidationError` | 400 | 详细验证错误 |
| **业务逻辑错误** | `ValueError` | 409 | 业务规则错误（如"gid已存在"） |
| **资源不存在** | `ValueError` | 404 | "Event not found" |
| **系统错误** | `Exception` | 500 | 通用错误消息 |

### 日志记录最佳实践

```python
# ✅ 正确：详细的日志，通用的用户消息
try:
    event = event_service.create_event(event_data)
except Exception as e:
    # 详细日志（仅服务器可见）
    logger.error(
        f"Error creating event: {e}",
        exc_info=True,  # 包含堆栈跟踪
        extra={
            "game_gid": event_data.game_gid,
            "event_name": event_data.event_name
        }
    )

    # 通用用户消息（客户端可见）
    return json_error_response(
        "Failed to create event",
        status_code=500
    )
```

### 检查清单

添加错误处理时，确保：
- [ ] 所有路由函数有try-except
- [ ] 区分ValidationError、ValueError、Exception
- [ ] 使用正确的HTTP状态码
- [ ] 详细日志记录，通用用户消息
- [ ] 不暴露敏感信息（SQL、路径、堆栈）

---

## 4. Repository层业务逻辑

### 违规模式

```python
# ❌ 错误：Repository层包含业务逻辑
class GameRepository(GenericRepository):
    def create_game(self, game_data: dict):
        # ❌ 业务逻辑：检查gid范围
        gid = game_data.get("gid")
        if gid < 90000000:
            raise ValueError("gid must be >= 90000000")

        # ❌ 业务逻辑：检查唯一性
        existing = self.find_by_gid(gid)
        if existing:
            raise ValueError(f"Game gid {gid} already exists")

        # ✅ 数据库操作（Repository的职责）
        return self.create(game_data)
```

### 修复方案

**步骤1**: Repository层只负责数据访问

```python
# ✅ 正确：Repository层只包含数据访问
class GameRepository(GenericRepository):
    def find_by_gid(self, gid: int) -> Optional[GameEntity]:
        """根据GID查询游戏"""
        query = "SELECT * FROM games WHERE gid = ?"
        row = fetch_one_as_dict(query, (gid,))
        return GameEntity(**row) if row else None

    def create(self, game_data: dict) -> int:
        """创建游戏"""
        return execute_insert(
            "INSERT INTO games (gid, name, ods_db) VALUES (?, ?, ?)",
            (game_data["gid"], game_data["name"], game_data["ods_db"])
        )
```

**步骤2**: Service层包含业务逻辑

```python
# ✅ 正确：Service层包含业务逻辑
class GameService:
    def __init__(self):
        self.game_repo = GameRepository()

    def create_game(self, game_data: GameEntity) -> GameEntity:
        """
        创建游戏

        业务逻辑：
        1. 验证gid范围
        2. 检查唯一性
        3. 创建游戏
        """
        # ✅ 业务规则1: 检查gid范围
        if game_data.gid < 90000000:
            raise ValueError("gid must be >= 90000000")

        # ✅ 业务规则2: 检查唯一性
        existing = self.game_repo.find_by_gid(game_data.gid)
        if existing:
            raise ValueError(f"Game gid {game_data.gid} already exists")

        # ✅ 调用Repository层创建
        game_id = self.game_repo.create(game_data.model_dump())

        return self.game_repo.find_by_id(game_id)
```

### Repository vs Service职责

| 层级 | 职责 | 示例 |
|------|------|------|
| **Repository** | 数据访问 | `find_by_id()`, `find_all()`, `create()`, `update()`, `delete()` |
| **Service** | 业务逻辑 | 检查唯一性、应用业务规则、协调多个Repository、事务管理 |

### 允许的Repository方法

```python
# ✅ 允许：纯数据访问方法
class GameRepository(GenericRepository):
    # 查询方法
    def find_by_id(self, game_id: int) -> Optional[GameEntity]:
        """根据ID查询"""
        pass

    def find_by_gid(self, gid: int) -> Optional[GameEntity]:
        """根据GID查询"""
        pass

    def find_all(self) -> List[GameEntity]:
        """查询所有"""
        pass

    # 统计方法
    def count_by_gid(self, gid: int) -> int:
        """统计数量"""
        pass

    # 数据转换方法
    def _deserialize_json(self, row: dict) -> dict:
        """JSON反序列化"""
        pass
```

### 禁止的Repository方法

```python
# ❌ 禁止：业务逻辑方法
class GameRepository(GenericRepository):
    # ❌ 业务规则验证
    def validate_gid_range(self, gid: int):
        """验证GID范围"""
        if gid < 90000000:
            raise ValueError("gid must be >= 90000000")

    # ❌ 唯一性检查
    def is_gid_unique(self, gid: int) -> bool:
        """检查GID唯一性"""
        existing = self.find_by_gid(gid)
        return existing is None

    # ❌ 复杂计算
    def calculate_game_score(self, game_id: int) -> float:
        """计算游戏评分"""
        # 复杂计算逻辑...
        pass
```

### 检查清单

审查Repository方法时，确保：
- [ ] 方法只包含数据访问逻辑
- [ ] 不包含业务规则验证
- [ ] 不包含复杂计算
- [ ] 不调用外部服务
- [ ] 返回Entity对象（而非字典）

---

## 快速参考

### 错误修复优先级

| 违规类型 | 优先级 | 预计工作量 |
|---------|--------|-----------|
| Service层数据库访问 | P0 | 3-5天 |
| 错误处理不一致 | P0 | 2-3天 |
| 缺少Entity验证 | P0 | 2-3天 |
| Repository层业务逻辑 | P1 | 1天 |

### 修复模板

```python
# ✅ 完整的修复示例
from backend.models.entities import EventEntity
from backend.services.events.event_service import EventService
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

@api_bp.route("/api/events", methods=["POST"])
def api_create_event():
    """
    API: 创建新事件

    架构合规性检查：
    ✅ 使用Entity验证输入
    ✅ 完整的错误处理
    ✅ Service层业务逻辑
    ✅ Repository层数据访问
    """
    try:
        # 1. Entity验证（自动XSS防护、类型转换、长度限制）
        event_data = EventEntity(**request.get_json())

        # 2. 调用Service层（业务逻辑、Repository调用）
        event_service = EventService()
        event = event_service.create_event(event_data)

        # 3. 返回成功响应
        return json_success_response(
            data=event.model_dump(),
            message="Event created successfully"
        )

    except ValidationError as e:
        # 输入验证失败
        return json_error_response(f"Validation error: {e}", status_code=400)

    except ValueError as e:
        # 业务逻辑错误
        return json_error_response(str(e), status_code=409)

    except Exception as e:
        # 系统错误
        logger.error(f"Error creating event: {e}", exc_info=True)
        return json_error_response("Failed to create event", status_code=500)
```

---

**文档版本**: v1.0
**最后更新**: 2026-03-02
**维护者**: Event2Table Development Team
