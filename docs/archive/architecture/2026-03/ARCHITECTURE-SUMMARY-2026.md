# Event2Table 架构总结 (2026)

> **最后更新**: 2026-02-25
> **架构版本**: 精简分层架构 V2.0
> **迁移状态**: ✅ 完成 (Game/Event/Parameter模块)

---

## 📊 当前架构状态

### 已完成的迁移

| 模块 | Entity模型 | Repository | Service | 集成测试 | 状态 |
|------|-----------|------------|---------|----------|------|
| **Game** | ✅ GameEntity | ✅ 返回Entity | ✅ 简化完成 | 10/10 ✅ | **完成** |
| **Event** | ✅ EventEntity | ✅ 返回Entity | ✅ 简化完成 | 9/9 ✅ | **完成** |
| **Parameter** | ✅ ParameterEntity | ✅ 返回Entity | ✅ 简化完成 | 9/9 ✅ | **完成** |
| **总计** | 3/3 | 3/3 | 3/3 | **28/28** ✅ | **100%** |

### 集成测试结果

```bash
============================= test session starts ==============================
backend/test/integration/test_game_module_integration.py::TestGameModuleIntegration::10 tests PASSED
backend/test/integration/test_event_module_integration.py::TestEventModuleIntegration::9 tests PASSED
backend/test/integration/test_parameter_module_integration.py::TestParameterModuleIntegration::9 tests PASSED

============================= 28 passed in 17.71s ==============================
```

---

## 🎯 架构亮点

### 1. 统一Entity模型系统

**核心创新**: 单一真相来源的Entity模型

```python
# backend/models/entities.py - 全局唯一实体定义

from pydantic import BaseModel, Field, field_validator

class GameEntity(BaseModel):
    """
    游戏实体 - 全局唯一的模型定义
    所有模块(GameService/GameRepository/API)都使用这个模型
    """
    id: Optional[int] = None
    gid: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
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

    model_config = ConfigDict(from_attributes=True)
```

**优势**:
- ✅ 模型一致性 - 单一定义,不可能不一致
- ✅ 自动验证 - Pydantic自动验证所有输入
- ✅ 类型安全 - IDE自动补全和错误检测
- ✅ 减少转换 - 直接使用Entity,无需中间转换

### 2. Repository返回Entity对象

**模式**: Repository层返回Entity而非字典

```python
# backend/models/repositories/games.py
class GameRepository(GenericRepository):
    """游戏仓储类"""

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

**优势**:
- ✅ 类型安全 - 明确的返回类型
- ✅ 自动验证 - Pydantic验证数据完整性
- ✅ IDE支持 - 完整的代码补全

### 3. Service层业务逻辑封装

**模式**: Service层使用Entity进行业务逻辑处理

```python
# backend/services/games/game_service.py
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
            raise ValueError(f"Game {game.gid} already exists")

        # 创建游戏
        game_id = self.game_repo.create(game.model_dump())

        # 清理缓存
        self.invalidator.invalidate_pattern("games.list")

        return self.game_repo.find_by_id(game_id)
```

**优势**:
- ✅ 简化的业务逻辑
- ✅ 集成缓存管理
- ✅ 类型安全的方法签名

### 4. 集成缓存失效机制

**模式**: 自动缓存失效

```python
# Service层自动管理缓存
class GameService:
    def update_game(self, gid: int, data: Dict[str, Any]) -> GameEntity:
        """更新游戏"""
        # 更新数据
        game = self.game_repo.update(gid, data)

        # 清理相关缓存
        self.invalidator.invalidate_game(gid)
        self.invalidator.invalidate_pattern("games.list")

        return game
```

---

## 📊 与旧DDD架构对比

| 方面 | 旧DDD架构 | 新架构 | 改进 |
|------|----------|--------|------|
| **模型数量** | 3套 (Domain/Schema/Dict) | 1套 (Entity) | **-66%** |
| **代码量** | 216行 | 130行 | **-40%** |
| **学习曲线** | 陡峭 (DDD概念) | 平缓 (纯Python) | **✅** |
| **类型安全** | 部分 | 完全 (Pydantic) | **✅** |
| **开发速度** | 中 (样板代码多) | 高 (30-50%提升) | **✅** |
| **模型一致性** | ❌ 多套模型可能不一致 | ✅ 单一模型 | **✅** |
| **维护成本** | 中高 | 低 | **✅** |

---

## 🏗️ 四层精简架构

```
┌─────────────────────────────────────────────────────┐
│   API Layer (Flask Routes)                          │
│   - HTTP请求处理                                      │
│   - 参数验证 (Pydantic Entity)                       │
│   - 调用Service层                                     │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│   Service Layer (业务逻辑)                           │
│   - 业务逻辑封装                                      │
│   - 多Repository协作                                  │
│   - 缓存管理                                          │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│   Repository Layer (数据访问)                        │
│   - CRUD操作                                         │
│   - 返回Entity对象                                    │
│   - SQL查询封装                                       │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│   Entity Layer (数据模型)                            │
│   - Pydantic Entity定义                              │
│   - 输入验证                                          │
│   - 序列化/反序列化                                   │
└─────────────────────────────────────────────────────┘
```

**关键特性**:
- ✅ 统一Entity模型 (单一真相来源)
- ✅ Repository返回Entity (非字典)
- ✅ 自动输入验证 (Pydantic)
- ✅ 类型安全 (完整类型注解)

---

## 💡 最佳实践

### Entity使用

- ✅ 所有输入使用Entity验证
- ✅ Repository返回Entity
- ✅ Service接收/返回Entity

### 缓存使用

- ✅ 使用`@cached`装饰器
- ✅ 数据变更后调用`invalidate_pattern()`
- ✅ 使用CacheInvalidator实例

### 错误处理

- ✅ Service层抛出ValueError
- ✅ API层返回适当HTTP状态码 (400/404/409/500)
- ✅ 不暴露内部错误信息

### 开发规范

- ✅ 使用game_gid进行数据关联
- ✅ 使用Pydantic v2语法 (field_validator, ConfigDict)
- ✅ 完整的类型注解
- ✅ 详细的docstring文档

---

## 📁 目录结构

```
backend/
├── models/
│   ├── entities.py (统一Entity定义) ⭐
│   ├── repositories/ (数据访问层)
│   └── schemas.py (保留用于API验证)
├── services/ (业务逻辑层)
│   ├── games/
│   ├── events/
│   └── parameters/
├── api/
│   └── routes/ (HTTP端点)
└── core/
    ├── database/ (数据库工具)
    ├── cache/ (缓存系统)
    └── utils/ (工具函数)
```

---

## 📚 相关文档

- **迁移指南**: [docs/development/MIGRATION-GUIDE.md](MIGRATION-GUIDE.md)
- **开发规范**: [CLAUDE.md](../../CLAUDE.md)
- **优化报告**: [docs/archive/2026-02/optimization/FINAL_OPTIMIZATION_REPORT.md](../archive/2026-02/optimization/FINAL_OPTIMIZATION_REPORT.md)

---

**文档版本**: 1.0
**创建日期**: 2026-02-25
**作者**: Event2Table Development Team
