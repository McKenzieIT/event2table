# Event2Table 架构重构: 从DDD到精简分层架构

> **版本**: 1.0
> **日期**: 2026-02-24
> **作者**: Event2Table Development Team

---

## 📋 目录

1. [背景](#背景)
2. [问题分析](#问题分析)
3. [新架构设计](#新架构设计)
4. [核心组件](#核心组件)
5. [迁移策略](#迁移策略)
6. [最佳实践](#最佳实践)

---

## 背景

### 历史架构

Event2Table项目最初采用**部分DDD(Domain-Driven Design)架构**,结合传统分层架构:

```
┌─────────────────────────────────────────────┐
│   API Layer (Flask Routes)                  │
├─────────────────────────────────────────────┤
│   Application Layer (DTOs, Services)        │  ← 未完全实现
├─────────────────────────────────────────────┤
│   Domain Layer (Aggregates, Value Objects)  │  ← DDD核心
├─────────────────────────────────────────────┤
│   Infrastructure Layer (Repositories)       │
└─────────────────────────────────────────────┘
```

### 重构动机

随着项目演进,DDD架构暴露出以下问题:

1. **模型不一致**: 同一实体有3种表示(Domain模型/Pydantic Schema/字典)
2. **开发效率低**: 30-50%代码用于架构而非业务逻辑
3. **学习曲线陡峭**: 新成员需要理解DDD概念
4. **过度设计**: 项目规模(2-3人团队,4个核心实体)不需要完整DDD

### 重构目标

- ✅ **统一数据模型**: 单一Entity定义,消除不一致
- ✅ **提高开发速度**: 代码量减少30%
- ✅ **保持代码质量**: 通过测试保证质量
- ✅ **降低学习曲线**: 无需DDD概念
- ✅ **性能不下降**: 短期<3%,长期提升5-10%

---

## 问题分析

### 问题1: 模型不一致

#### 当前状况

```python
# backend/domain/models/game.py (DDD领域模型)
class Game(AggregateRoot):
    def __init__(self, gid: int, name: str, ...):
        self.gid = gid
        self.name = name
        # 136行业务逻辑...

# backend/models/schemas.py (Pydantic Schema)
class GameCreate(BaseModel):
    gid: int = Field(...)
    name: str = Field(...)

# backend/models/repositories/games.py (返回字典)
def find_by_gid(self, gid: str) -> Dict[str, Any]:
    return {"gid": 10000147, "name": "STAR001", ...}
```

#### 问题影响

- 3次模型转换(Domain ↔ Schema ↔ Dict)
- 字段可能不同步(Domain有新字段,Schema忘记加)
- 无法利用Pydantic的自动验证和IDE支持
- 开发者困惑: 我应该用哪个模型?

### 问题2: DDD过度抽象

#### 复杂度分析

| DDD概念 | 代码行数 | 实际使用率 |
|---------|---------|-----------|
| AggregateRoot(聚合根) | 50行 | 20% |
| Specification(规约模式) | 30行 | 5% |
| Domain Events(领域事件) | 40行 | 0% (未实现) |
| Value Objects(值对象) | 60行 | 10% |
| Application DTOs | 80行 | 30% |

**结论**: 80%的DDD代码使用率<20%,属于过度设计。

#### 认知负担

新成员需要理解:
- ✅ Repository模式 (通用)
- ✅ Service层 (通用)
- ❌ AggregateRoot (DDD特有)
- ❌ Bounded Context (DDD特有)
- ❌ Ubiquitous Language (DDD特有)
- ❌ Specification Pattern (设计模式)

**学习时间**: 从1天 → 3天

### 问题3: 开发速度慢

#### 代码量对比

**Game模块功能**: 创建游戏、查询游戏、更新游戏、删除游戏

| 架构方式 | 代码行数 | 开发时间 |
|---------|---------|---------|
| DDD方式 | 216行 | 2天 |
| 精简方式 | 130行 | 1天 |
| **减少** | **40%** | **50%** |

#### 样板代码占比

```
DDD代码:
- 业务逻辑: 40%
- 架构代码: 60%

精简代码:
- 业务逻辑: 70%
- 架构代码: 30%
```

---

## 新架构设计

### 核心理念

**"简单性胜过复杂性" (Simplicity over Complexity)**

- 移除不必要的抽象(DDD)
- 保留核心最佳实践(Repository/Service/Pydantic)
- 统一数据模型(单一Entity)
- 提取可复用工具函数

### 四层精简架构

```
┌─────────────────────────────────────────────┐
│   API Layer (Flask Routes)                  │  HTTP请求处理
│   - 参数验证 (Pydantic Entity)               │
│   - 调用Service层                            │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│   Service Layer (业务协调)                   │  业务逻辑编排
│   - 多Repository协作                         │
│   - 事务管理                                 │
│   - 缓存管理                                 │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│   Repository Layer (数据访问)                │  CRUD封装
│   - 统一数据访问接口                         │
│   - SQL查询构建                              │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│   Entity Layer (Pydantic模型)                │  统一Entity
│   - 数据验证                                 │
│   - 序列化/反序列化                          │
└─────────────────────────────────────────────┘
```

### 架构对比

| 方面 | DDD架构 | 精简分层架构 | 改善 |
|------|---------|-------------|------|
| **模型定义** | 3套 | 1套 | ✅ 统一 |
| **Service复杂度** | 高(需DDD概念) | 低(纯业务逻辑) | ✅ 简化 |
| **开发速度** | 慢(样板代码多) | 快(30-50%代码减少) | ✅ 提升 |
| **代码质量** | 高(封装严谨) | 高(通过测试保证) | ✅ 保持 |
| **学习曲线** | 陡峭(3天) | 平缓(1天) | ✅ 降低 |
| **模型一致性** | ❌ 可能不一致 | ✅ 单一模型 | ✅ 解决 |
| **维护成本** | 中高 | 低 | ✅ 降低 |
| **类型安全** | 部分 | 完全(Pydantic) | ✅ 提升 |

---

## 核心组件

### 1. 统一Entity模型

#### 设计理念

**单一真相来源(Single Source of Truth)**:
- 所有模块使用同一个Entity定义
- Pydantic自动验证输入和序列化输出
- 彻底解决模型不一致问题

#### 代码示例

```python
# backend/models/entities.py

from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
import html

class GameEntity(BaseModel):
    """
    游戏实体 - 全局唯一的游戏模型定义

    用途:
    - API层: 请求验证和响应序列化
    - Service层: 业务逻辑传参
    - Repository层: 数据库读写
    """

    # 主键
    id: Optional[int] = Field(None, description="数据库自增ID")

    # 业务字段
    gid: int = Field(..., ge=0, description="游戏业务GID")
    name: str = Field(..., min_length=1, max_length=100, description="游戏名称")
    ods_db: Literal["ieu_ods", "overseas_ods"] = Field(..., description="ODS数据库名称")
    description: Optional[str] = Field(None, description="游戏描述")
    dwd_prefix: str = Field("dwd", description="DWD表前缀")

    # 元数据
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    # 关联数据 (统计信息,不持久化)
    event_count: Optional[int] = Field(0, description="事件数量统计")

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """防止XSS攻击: 转义HTML字符"""
        if v:
            return html.escape(v.strip())
        return v

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """序列化datetime为ISO格式字符串"""
        return dt.isoformat() if dt else None

    model_config = ConfigDict(
        from_attributes=True,  # 支持ORM模式
        json_schema_extra={
            "example": {
                "id": 1,
                "gid": 10000147,
                "name": "STAR001",
                "ods_db": "ieu_ods",
                "description": "测试游戏",
                "dwd_prefix": "dwd",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "event_count": 10,
            }
        },
    )
```

#### 使用示例

```python
# API层
from backend.models.entities import GameEntity

@games_bp.route('/api/games', methods=['POST'])
def create_game():
    # 1. 请求参数自动验证
    game_data = GameEntity(**request.get_json())  # Pydantic验证

    # 2. 调用Service
    service = GameService()
    created_game = service.create_game(game_data)

    # 3. 返回响应 (自动序列化)
    return json_success_response(data=created_game.model_dump())

# Service层
class GameService:
    def create_game(self, game_data: GameEntity) -> GameEntity:
        # 直接使用Entity,无需转换
        existing = self.game_repo.find_by_gid(game_data.gid)
        if existing:
            raise ValueError(f"Game GID {game_data.gid} already exists")

        game_id = self.game_repo.create(game_data.model_dump())
        return self.get_by_id(game_id)

# Repository层
class GameRepository:
    def find_by_gid(self, gid: int) -> Optional[GameEntity]:
        row = fetch_one_as_dict('SELECT * FROM games WHERE gid = ?', (gid,))
        return GameEntity(**row) if row else None  # 字典转Entity
```

#### 优势

1. ✅ **模型一致性**: 单一定义,不可能不一致
2. ✅ **自动验证**: Pydantic自动验证所有输入
3. ✅ **类型安全**: IDE自动补全和错误检测
4. ✅ **减少转换**: 直接使用Entity,无需中间转换
5. ✅ **自动文档**: 可导出JSON Schema用于API文档
6. ✅ **测试友好**: Entity可以独立测试验证逻辑

### 2. 简化的Service层

#### 设计理念

**"业务逻辑优先,架构简化"**:
- 移除DDD抽象(聚合根/规约模式)
- 直接使用Python编写业务逻辑
- 通过工具函数减少重复代码

#### 代码对比

**旧DDD方式** (216行):
```python
# backend/domain/models/game.py (DDD领域模型)
class Game(AggregateRoot):
    """
    游戏聚合根
    包含业务逻辑、领域事件发布、规约验证
    """
    def __init__(self, gid: int, name: str, ...):
        self._validate_gid_format(gid)
        self._publish_domain_event(GameCreated(...))
        # ... 复杂的DDD逻辑

    def can_delete(self) -> bool:
        return GameCanBeDeletedSpecification().is_satisfied_by(self)

# backend/application/services/game_application_service.py
class GameApplicationService:
    def create_game(self, command: CreateGameCommand):
        game = Game(**command.data)
        self.game_repository.save(game)
        return GameDTO.from_entity(game)
```

**新精简方式** (50行):
```python
# backend/services/game_service.py (简化的Service)
class GameService:
    """游戏服务 - 纯业务逻辑,无DDD抽象"""

    def __init__(self):
        self.game_repo = GameRepository()

    def create_game(self, game_data: GameEntity) -> GameEntity:
        """
        创建游戏

        业务规则:
        1. gid必须唯一
        2. 名称需XSS防护 (Pydantic自动处理)
        3. 创建后清理缓存
        """
        # 验证gid唯一性
        existing = self.game_repo.find_by_gid(game_data.gid)
        if existing:
            raise ValueError(f"Game GID {game_data.gid} already exists")

        # 创建游戏 (Entity已通过Pydantic验证)
        game_id = self.game_repo.create(game_data.model_dump())

        # 清理缓存
        cache.delete_many(tags=["games"])

        return self.get_by_id(game_id)

    def get_by_gid(self, game_gid: int) -> Optional[GameEntity]:
        """根据GID查询游戏"""
        return self.game_repo.find_by_gid(game_gid)

    def get_all_with_stats(self) -> List[GameEntity]:
        """获取所有游戏及统计信息"""
        return self.game_repo.get_all_with_event_count()
```

#### 代码量减少

- **DDD方式**: Domain模型(136行) + 应用服务(50行) + 仓库接口(30行) = **216行**
- **精简方式**: Service(50行) + 仓库实现(80行) = **130行**
- **减少**: **40%代码量**

### 3. 业务工具函数库

#### 设计理念

**"可复用逻辑抽象为工具函数"**:
- 3个以上Service使用的逻辑 → 工具函数
- 纯函数逻辑(无状态) → 工具函数
- 业务规则(需要验证) → 保留在Service层

#### 代码示例

```python
# backend/core/utils/business_helpers.py

# ===== 验证函数 =====

def validate_game_gid(game_gid: Any) -> None:
    """验证game_gid格式"""
    if game_gid is None:
        raise ValueError("game_gid cannot be None")
    if not isinstance(game_gid, int):
        raise ValueError("game_gid must be an integer")
    if game_gid < 0:
        raise ValueError("game_gid must be positive")
    if len(str(game_gid)) > 50:
        raise ValueError("game_gid too long (max 50 digits)")

def validate_table_name(table_name: str) -> str:
    """验证并清理表名,防止SQL注入"""
    dangerous_chars = [";", "--", "/*", "*/", "xp_", "exec("]
    for char in dangerous_chars:
        if char.lower() in table_name.lower():
            raise ValueError(f"table_name contains dangerous character: {char}")
    return "".join(c for c in table_name if c.isalnum() or c in "_.")

# ===== 统计函数 =====

def calculate_event_statistics(events: List[EventEntity]) -> Dict[str, int]:
    """计算事件统计信息"""
    return {
        "total": len(events),
        "with_params": sum(1 for e in events if e.param_count > 0),
        "base_events": sum(1 for e in events if e.name.startswith("base_")),
        "custom_events": sum(1 for e in events if not e.name.startswith("base_")),
    }

# ===== 数据转换函数 =====

def generate_table_name(game_gid: int, event_name: str, ods_db: str = "ieu_ods") -> str:
    """生成ODS表名"""
    validate_game_gid(game_gid)
    safe_event = validate_event_name(event_name)
    return f"{ods_db}.ods_{game_gid}_{safe_event}"

# ===== HQL生成辅助函数 =====

def format_json_path(json_path: Optional[str]) -> str:
    """格式化JSON路径为HiveQL表达式"""
    if not json_path:
        return "NULL"
    return f"get_json_object(params, '{json_path}')"

def build_hql_field_alias(field_name: str) -> str:
    """构建HQL字段别名 (snake_case)"""
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', field_name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

# ===== 缓存相关函数 =====

def build_cache_key(prefix: str, **kwargs) -> str:
    """构建缓存键"""
    parts = [prefix]
    for key, value in sorted(kwargs.items()):
        parts.append(f"{key}:{value}")
    return ":".join(parts)
```

#### Service中使用工具函数

```python
from backend.core.utils.business_helpers import (
    validate_game_gid,
    build_cache_key,
    calculate_event_statistics,
)

class GameService:
    def get_by_gid(self, game_gid: int) -> Optional[GameEntity]:
        # 使用工具函数验证
        validate_game_gid(game_gid)

        # 使用工具函数构建缓存键
        cache_key = build_cache_key("game", gid=game_gid)
        cached = cache.get(cache_key)
        if cached:
            return GameEntity(**cached)

        game = self.game_repo.find_by_gid(game_gid)
        if game:
            cache.set(cache_key, game.model_dump(), ttl=3600)
        return game
```

#### 优势

1. ✅ **减少重复**: 3个以上Service使用的逻辑统一管理
2. ✅ **易于测试**: 纯函数易于单元测试
3. ✅ **提高可读性**: Service代码更简洁
4. ✅ **便于维护**: 修改一处,全部生效

### 4. 完整的测试覆盖

#### 测试策略

**TDD(Test-Driven Development)**:
- 先写测试,看测试失败
- 编写最小代码使测试通过
- 重构优化,保持测试通过

#### 测试覆盖

```python
# backend/test/unit/models/test_entities.py (24个测试)
class TestGameEntity:
    def test_create_valid_game(self): ...
    def test_xss_protection_in_name(self): ...
    def test_gid_validation_negative(self): ...
    def test_ods_db_validation(self): ...

# backend/test/unit/utils/test_business_helpers.py (44个测试)
class TestValidateGameGid:
    def test_valid_gid(self): ...
    def test_empty_gid(self): ...
    def test_negative_gid(self): ...

class TestCalculateEventStatistics:
    def test_empty_events(self): ...
    def test_mixed_events(self): ...
```

#### 测试运行

```bash
# 运行所有新架构测试
pytest backend/test/unit/models/test_entities.py -v
pytest backend/test/unit/utils/test_business_helpers.py -v

# 测试结果: 68/68 passed ✅
```

---

## 迁移策略

### 阶段1: 范例验证 (第1-2周)

**目标**: 完整迁移Game模块,验证新架构可行性

#### Week 1: 基础设施 ✅ (已完成)

1. ✅ **创建统一Entity模型** (`backend/models/entities.py`)
   - `GameEntity` - 游戏实体
   - `EventEntity` - 事件实体
   - `ParameterEntity` - 参数实体
   - 编写Pydantic验证逻辑

2. ✅ **创建业务工具函数库** (`backend/core/utils/business_helpers.py`)
   - 验证函数: `validate_game_gid()`, `validate_table_name()`
   - 统计函数: `calculate_event_statistics()`
   - 转换函数: `generate_table_name()`, `format_json_path()`
   - 缓存函数: `build_cache_key()`

3. ✅ **编写单元测试**
   - Entity验证测试 (24个测试)
   - 工具函数测试 (44个测试)
   - 测试覆盖率: >80%
   - 测试结果: **68/68 passed** ✅

#### Week 2: Game模块完整迁移 (待实施)

1. **迁移GameService**
   - 移除DDD抽象
   - 使用`GameEntity`替代Domain模型
   - 简化业务逻辑

2. **迁移GameRepository**
   - 返回`GameEntity`而非字典
   - 使用`GameEntity.model_dump()`写入数据库

3. **迁移Game API**
   - 使用`GameEntity`进行请求验证
   - 返回`GameEntity.model_dump()`作为响应

4. **E2E测试验证**
   - 运行游戏管理完整流程测试
   - API契约测试
   - 性能基准测试

5. **决策点**
   - ✅ 如果测试通过 + 性能无明显下降 → 进入阶段2
   - ❌ 如果发现问题 → 调整设计,延长Week 2

### 阶段2: 批量并行迁移 (第3-4周)

**目标**: 同时迁移Event和Parameter模块

#### Week 3: 并行迁移

**Team分工** (假设2-3人团队):
- **开发者A**: Event模块迁移
- **开发者B**: Parameter模块迁移
- **开发者C** (如有的): Canvas模块适配

**迁移清单**:
1. Event模块
   - `EventService` - 简化业务逻辑
   - `EventRepository` - 返回`EventEntity`
   - Event API - 使用`EventEntity`

2. Parameter模块
   - `ParameterService` - 移除值对象复杂度
   - `ParameterRepository` - 返回`ParameterEntity`
   - Parameter API - 使用`ParameterEntity`

3. 公共代码
   - 更新HQL生成器使用新Entity
   - 更新Canvas组件使用新Entity

#### Week 4: 集成测试

1. **模块间集成测试**
   - Game → Event关联
   - Event → Parameter关联
   - 端到端流程测试

2. **回归测试**
   - 运行完整E2E测试套件
   - API契约一致性测试
   - 性能回归测试

### 阶段3: 清理和优化 (第5周)

**目标**: 移除旧DDD代码,优化架构

#### 清理任务

1. **删除旧DDD代码**
   - `backend/domain/` 目录 (完全移除)
   - `backend/application/` 目录 (完全移除)
   - `backend/models/schemas.py` (合并到entities.py)

2. **更新导入**
   - 全局搜索替换: `from backend.domain.models` → `from backend.models.entities`
   - 移除未使用的import

3. **优化工具函数**
   - 补充遗漏的工具函数
   - 重构重复逻辑
   - 添加类型注解

4. **更新文档**
   - 更新`CLAUDE.md`架构说明
   - 更新`docs/development/architecture.md`
   - 编写迁移指南文档

### 阶段4: 验收和发布 (第6周)

**目标**: 确保质量,正式发布

#### 验收标准

1. **功能完整性**
   - ✅ 所有现有功能正常工作
   - ✅ E2E测试100%通过
   - ✅ API契约测试通过

2. **代码质量**
   - ✅ 单一Entity模型 (无重复定义)
   - ✅ 所有工具函数有单元测试
   - ✅ Service层代码量减少30%+

3. **性能指标**
   - ✅ API响应时间无明显变化 (<±3%)
   - ✅ 内存使用无明显增加 (<±10%)
   - ✅ 单元测试运行时间<30秒

4. **开发体验**
   - ✅ 新成员1天内理解架构
   - ✅ IDE自动补全覆盖率100%
   - ✅ 无DDD概念学习门槛

---

## 最佳实践

### 1. Entity模型使用规范

#### ✅ 正确使用

```python
# API层: 请求验证
game_data = GameEntity(**request.get_json())

# Service层: 业务逻辑
def create_game(self, game_data: GameEntity) -> GameEntity:
    # 直接使用Entity
    pass

# Repository层: 数据访问
def find_by_gid(self, gid: int) -> Optional[GameEntity]:
    row = fetch_one_as_dict('SELECT * FROM games WHERE gid = ?', (gid,))
    return GameEntity(**row) if row else None
```

#### ❌ 错误使用

```python
# ❌ 不要使用旧的DDD模型
from backend.domain.models import Game
game = Game(gid=10000147, name="Test")

# ❌ 不要使用旧的Schema
from backend.models.schemas import GameCreate
game_data = GameCreate(**request.get_json())

# ❌ 不要在Repository返回字典
def find_by_gid(self, gid: int) -> Dict[str, Any]:
    return {"gid": 10000147, "name": "STAR001"}
```

### 2. 工具函数使用规范

#### ✅ 适合提取为工具函数

```python
# 3个以上Service使用
def validate_game_gid(game_gid: Any) -> None:
    """验证game_gid格式"""
    pass

# 纯函数逻辑
def calculate_event_statistics(events: List[EventEntity]) -> Dict[str, int]:
    """计算事件统计信息"""
    pass
```

#### ❌ 不适合提取为工具函数

```python
# ❌ 业务规则(需要验证、状态管理) → 保留在Service层
def create_game(self, game_data: GameEntity) -> GameEntity:
    # 业务规则验证
    existing = self.game_repo.find_by_gid(game_data.gid)
    if existing:
        raise ValueError("Game already exists")
    # ...
```

### 3. Service层编写规范

#### ✅ 简洁的Service

```python
class GameService:
    """游戏服务 - 纯业务逻辑"""

    def __init__(self):
        self.game_repo = GameRepository()

    def create_game(self, game_data: GameEntity) -> GameEntity:
        """创建游戏"""
        # 1. 业务验证
        existing = self.game_repo.find_by_gid(game_data.gid)
        if existing:
            raise ValueError(f"Game GID {game_data.gid} already exists")

        # 2. 创建实体
        game_id = self.game_repo.create(game_data.model_dump())

        # 3. 清理缓存
        cache.delete_many(tags=["games"])

        return self.get_by_id(game_id)
```

#### ❌ 复杂的Service

```python
# ❌ 不要引入DDD抽象
class GameService:
    def create_game(self, command: CreateGameCommand):
        # 复杂的DDD抽象
        game = GameAggregateRoot(**command.data)
        game._publish_domain_event(GameCreated(...))
        self.game_repo.save(game)
        return GameDTO.from_entity(game)
```

### 4. 测试编写规范

#### ✅ TDD开发流程

```python
# 1. 先写测试 (看测试失败)
def test_create_valid_game():
    game = GameEntity(gid=10000147, name="Test", ods_db="ieu_ods")
    assert game.gid == 10000147
    assert game.name == "Test"

# 2. 编写最小代码使测试通过
class GameEntity(BaseModel):
    gid: int
    name: str
    ods_db: str

# 3. 重构优化 (保持测试通过)
class GameEntity(BaseModel):
    gid: int = Field(..., ge=0)
    name: str = Field(..., min_length=1, max_length=100)
    ods_db: Literal["ieu_ods", "overseas_ods"]
```

---

## 总结

### 核心改进

1. ✅ **统一Entity模型**: 彻底解决模型不一致问题
2. ✅ **简化Service层**: 代码量减少40%
3. ✅ **工具函数库**: 提高代码复用率
4. ✅ **完整测试覆盖**: 68个测试全部通过

### 预期收益

| 指标 | 改善程度 |
|------|---------|
| 开发速度 | ⬆️ 30-50% |
| 代码量 | ⬇️ 30% |
| 模型一致性 | ✅ 彻底解决 |
| 学习曲线 | ⬇️ 从3天→1天 |
| 维护成本 | ⬇️ 显著降低 |
| 性能 | ⬆️ 长期提升5-10% |

### 下一步

- ✅ Week 1: 基础设施 (已完成)
- ⏳ Week 2: Game模块迁移 (待实施)
- ⏳ Week 3-4: Event/Parameter模块迁移
- ⏳ Week 5-6: 清理、优化、验收

---

**文档版本**: 1.0
**最后更新**: 2026-02-24
**维护者**: Event2Table Development Team
