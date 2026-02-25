# PRD架构更新说明

> **文档**: PRD架构更新章节
> **版本**: 1.0 | **日期**: 2026-02-24
> **更新原因**: 从DDD架构迁移到精简分层架构

---

## 架构变更概述

### 变更原因

Event2Table项目原采用部分DDD(Domain-Driven Design)架构,在实际使用中发现:
1. **模型不一致**: 同一实体有3种表示(Domain模型/Pydantic Schema/字典)
2. **开发效率低**: 30-50%代码用于架构而非业务逻辑
3. **学习曲线陡峭**: 新成员需要理解DDD概念(聚合根/规约模式等)
4. **过度设计**: 项目规模(2-3人团队,4个核心实体)不需要完整DDD

### 新架构

采用**精简分层架构 + 统一Entity模型**:
- 移除DDD的过度抽象(领域层/规约模式/应用层DTOs)
- 保留核心最佳实践(Repository/Service/Pydantic验证)
- 建立单一真相来源的统一Entity模型
- 提取可复用的业务工具函数

**预期收益**:
- 开发速度提升30-50%
- 代码量减少30%
- 模型一致性问题彻底解决
- 学习曲线显著降低(从3天→1天)

---

## 技术架构变更

### 旧架构: DDD + 分层架构

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

**问题**:
- 3套模型定义(Domain/Schema/Dict)
- 复杂的DDD抽象(聚合根/规约模式)
- Application层未完成实现

### 新架构: 精简分层架构

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

**优势**:
- 单一Entity模型(统一数据定义)
- 简化的Service层(纯业务逻辑)
- 业务工具函数库(可复用逻辑)
- 完整测试覆盖(68个测试)

---

## 核心组件变更

### 1. 统一Entity模型 ⭐

#### 旧方式(DDD)

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

**问题**: 3套模型,容易不一致

#### 新方式(统一Entity)

```python
# backend/models/entities.py (统一Entity定义)

from pydantic import BaseModel, Field, field_validator

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
        import html
        if v:
            return html.escape(v.strip())
        return v

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

**优势**:
- ✅ 单一定义,不可能不一致
- ✅ Pydantic自动验证
- ✅ IDE自动补全和类型检查
- ✅ 减少模型转换开销

### 2. 简化的Service层

#### 旧方式(DDD)

```python
# 复杂的DDD抽象
class GameAggregateRoot(AggregateRoot):
    def __init__(self, gid: int, name: str, ...):
        self._validate_gid_format(gid)
        self._publish_domain_event(GameCreated(...))
        # ... 复杂的DDD逻辑

    def can_delete(self) -> bool:
        return GameCanBeDeletedSpecification().is_satisfied_by(self)

# 代码量: 216行 (Domain模型 + 应用服务 + 仓库接口)
```

#### 新方式(精简Service)

```python
# backend/services/game_service.py

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

# 代码量: 50行 (减少40%)
```

**优势**:
- ✅ 代码量减少40%
- ✅ 无需DDD概念
- ✅ 业务逻辑清晰直观

### 3. 业务工具函数库

#### 新增组件

```python
# backend/core/utils/business_helpers.py

"""
业务逻辑辅助函数 - 可复用的跨Service逻辑

原则:
1. 纯函数 (无状态)
2. 广泛复用 (3+处使用)
3. 业务相关 (非技术工具)
"""

# ===== 验证函数 =====
def validate_game_gid(game_gid: Any) -> None:
    """验证game_gid格式"""
    if game_gid is None:
        raise ValueError("game_gid cannot be None")
    if not isinstance(game_gid, int):
        raise ValueError("game_gid must be an integer")
    if game_gid < 0:
        raise ValueError("game_gid must be positive")

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
```

**优势**:
- ✅ 减少重复代码
- ✅ 易于单元测试
- ✅ 提高可维护性

---

## 迁移进度

### 阶段1: 范例验证 ✅ (已完成)

**目标**: 完整迁移Game模块,验证新架构可行性

#### Week 1: 基础设施 ✅

- ✅ 创建统一Entity模型 (`backend/models/entities.py`)
  - `GameEntity` - 游戏实体
  - `EventEntity` - 事件实体
  - `ParameterEntity` - 参数实体

- ✅ 创建业务工具函数库 (`backend/core/utils/business_helpers.py`)
  - 验证函数: `validate_game_gid()`, `validate_table_name()`
  - 统计函数: `calculate_event_statistics()`
  - 转换函数: `generate_table_name()`, `format_json_path()`
  - 缓存函数: `build_cache_key()`

- ✅ 编写单元测试
  - Entity验证测试 (24个测试)
  - 工具函数测试 (44个测试)
  - **测试结果: 68/68 passed** ✅

#### Week 2: Game模块迁移 (进行中)

- ⏳ 迁移GameService
- ⏳ 迁移GameRepository
- ⏳ 迁移Game API
- ⏳ E2E测试验证
- ⏳ 性能基准测试

### 阶段2-4: 后续计划

- ⏳ Week 3-4: Event/Parameter模块批量迁移
- ⏳ Week 5: 清理旧DDD代码
- ⏳ Week 6: 验收和发布

---

## 影响评估

### 对现有功能的影响

#### 无影响 (主要功能)

- ✅ **API接口**: 保持不变,前端无需修改
- ✅ **数据库Schema**: 无变更
- ✅ **业务逻辑**: 功能一致,仅重构代码结构
- ✅ **性能**: 目标无明显下降(<±3%)

#### 有影响 (内部实现)

- ⚠️ **导入路径**:
  - 旧: `from backend.domain.models import Game`
  - 新: `from backend.models.entities import GameEntity`

- ⚠️ **模型类型**:
  - 旧: `Game` (DDD领域模型), `GameCreate` (Pydantic Schema)
  - 新: `GameEntity` (统一Entity)

### 对开发流程的影响

#### 简化开发流程

**旧流程(DDD)**:
1. 创建DDD领域模型
2. 创建Pydantic Schema
3. 创建Application Service
4. 创建Repository
5. 编写集成测试

**新流程(精简)**:
1. 创建Entity (兼Domain + Schema功能)
2. 创建Service (简化业务逻辑)
3. 创建Repository
4. 编写单元测试

**时间**: 从2天 → 1天 (减少50%)

#### 降低学习曲线

**旧架构(DDD)**:
- 需要理解: AggregateRoot, Value Object, Specification, Domain Events
- 学习时间: 3天

**新架构(精简)**:
- 需要理解: Entity, Service, Repository, Pydantic
- 学习时间: 1天

---

## 术语对照表

### DDD术语 → 新架构术语

| DDD术语 | 新架构术语 | 说明 |
|---------|-----------|------|
| Aggregate Root(聚合根) | Entity(实体) | 简化为Pydantic模型 |
| Value Object(值对象) | Entity(实体) | 合并到Entity |
| Specification(规约) | 工具函数 | 简化为纯函数 |
| Domain Event(领域事件) | (未使用) | 当前不需要 |
| Application Service | Service | 保留但简化 |
| DTO | Entity | 统一为Entity |
| Repository | Repository | 保持不变 |

---

## 相关文档

- **完整架构文档**: [docs/development/architecture-refactoring.md](../development/architecture-refactoring.md)
- **详细实施计划**: [用户讨论记录](../../.claude/plans/rustling-marinating-rainbow.md)
- **迁移进度**: 查看`CHANGELOG.md`和Git提交记录

---

**文档版本**: 1.0
**创建日期**: 2026-02-24
**作者**: Event2Table Development Team
**审核**: 待团队审核
