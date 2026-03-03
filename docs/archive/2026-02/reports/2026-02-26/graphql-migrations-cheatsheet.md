# GraphQL API 架构迁移速查表

**日期**: 2026-02-26
**用途**: 快速参考 - 如何从旧 DDD 架构迁移到新架构

---

## 快速对照表

### 游戏相关操作

| 操作 | 旧架构 (DDD) | 新架构 (Entity + Service) |
|------|--------------|---------------------------|
| **导入** | `from backend.application.services.game_app_service_enhanced import get_game_app_service` | `from backend.services.games.game_service import GameService` |
| **创建游戏** | `dto = GameCreateDTO(...); service.create_game(dto)` | `entity = GameEntity(...); service.create_game(entity)` |
| **更新游戏** | `dto = GameUpdateDTO(...); service.update_game(gid, dto)` | `service.update_game(gid, {...})` |
| **删除游戏** | `service.delete_game(gid, force=True)` | `service.delete_game(gid)` |
| **批量删除** | `service.batch_delete_games(gids, force=True)` | `service.batch_delete_games(gids)` |
| **序列化** | `result.to_dict()` | `result.model_dump()` |

### HQL 相关操作

| 操作 | 旧架构 (DDD) | 新架构 (Entity + Service) |
|------|--------------|---------------------------|
| **导入** | `from backend.domain.services.hql_generation_service import HQLGenerationService` | `from backend.services.hql.hql_service_cached import HQLServiceCached` |
| **生成 HQL** | `service.generate_single_event_hql(event, options)` | `service.generate_hql(events, fields, conditions, mode)` |
| **验证 HQL** | `service.validate_events_for_generation(events)` | `service.validate_hql(hql)` |

---

## 代码示例

### 示例 1: 创建游戏

**旧代码**:
```python
from backend.application.services.game_app_service_enhanced import (
    get_game_app_service,
    GameCreateDTO
)

service = get_game_app_service()
dto = GameCreateDTO(gid=100001, name="My Game", ods_db="ieu_ods")
result = service.create_game(dto)
game_dict = result.to_dict()
```

**新代码**:
```python
from backend.services.games.game_service import GameService
from backend.models.entities import GameEntity

service = GameService()
entity = GameEntity(gid=100001, name="My Game", ods_db="ieu_ods")
result = service.create_game(entity)
game_dict = result.model_dump()
```

---

### 示例 2: 更新游戏

**旧代码**:
```python
from backend.application.services.game_app_service_enhanced import (
    get_game_app_service,
    GameUpdateDTO
)

service = get_game_app_service()
dto = GameUpdateDTO(name="Updated Name")
result = service.update_game(gid, dto)
```

**新代码**:
```python
from backend.services.games.game_service import GameService

service = GameService()
result = service.update_game(gid, {'name': 'Updated Name'})
```

---

### 示例 3: 删除游戏（带检查）

**旧代码**:
```python
from backend.application.services.game_app_service_enhanced import get_game_app_service

service = get_game_app_service()
impact = service.check_deletion_impact(gid)

if not confirm and impact['has_associated_data']:
    return error(f"Game has {impact['event_count']} events")

result = service.delete_game(gid, force=confirm)
```

**新代码**:
```python
from backend.services.games.game_service import GameService
from backend.core.utils.converters import fetch_one_as_dict

service = GameService()

# 手动检查事件数量
event_count_result = fetch_one_as_dict(
    "SELECT COUNT(*) as count FROM log_events WHERE game_gid = ?",
    (gid,)
)
event_count = event_count_result['count'] if event_count_result else 0

if not confirm and event_count > 0:
    return error(f"Game has {event_count} events")

service.delete_game(gid)
```

---

### 示例 4: 生成 HQL

**旧代码**:
```python
from backend.domain.services.hql_generation_service import HQLGenerationService

service = HQLGenerationService()
hql = service.generate_single_event_hql(event, options)
is_valid, errors = service.validate_events_for_generation(events)
```

**新代码**:
```python
from backend.services.hql.hql_service_cached import HQLServiceCached

service = HQLServiceCached()

# 准备字段
fields = [
    {'name': 'ds', 'type': 'base'},
    {'name': 'role_id', 'type': 'base'},
    {'name': 'zone_id', 'type': 'param', 'json_path': '$.zoneId'}
]

# 生成 HQL
hql = service.generate_hql(
    events=events,
    fields=fields,
    conditions=[],
    mode='single'
)

# 验证 HQL
validation = service.validate_hql(hql)
```

---

## GraphQL Mutation 模板

### 创建 Mutation 模板

```python
import graphene
from graphene import Field, Int, String, Boolean, List

class MyCustomMutation(graphene.Mutation):
    """自定义 mutation 使用新架构"""

    class Arguments:
        # 定义输入参数
        gid = Int(required=True)
        name = String(required=True)

    # 定义输出字段
    ok = Boolean()
    data = Field(lambda: MyType)
    errors = List(String)

    def mutate(self, info, gid: int, name: str):
        """执行 mutation"""
        try:
            # 导入服务层
            from backend.services.games.game_service import GameService
            from backend.models.entities import GameEntity

            # 获取服务实例
            service = GameService()

            # 创建 Entity (Pydantic 自动验证)
            entity = GameEntity(gid=gid, name=name)

            # 调用服务
            result = service.create_game(entity)

            # 序列化结果
            data_dict = result.model_dump()

            # 返回 GraphQL 类型
            return MyCustomMutation(
                ok=True,
                data=MyType.from_dict(data_dict)
            )

        except ValueError as e:
            # 业务逻辑错误
            return MyCustomMutation(ok=False, errors=[str(e)])

        except Exception as e:
            # 未知错误
            logger.error(f"Error: {e}", exc_info=True)
            return MyCustomMutation(ok=False, errors=[str(e)])
```

---

## 常见问题

### Q1: 如何处理导入错误？

**错误**: `ModuleNotFoundError: No module named 'backend.domain'`

**解决**:
```python
# 替换所有 backend.domain 导入
# 旧: from backend.domain.services.xxx import YyyService
# 新: from backend.services.xxx import yyy_service
```

### Q2: 如何处理 DTO？

**错误**: `NameError: name 'GameCreateDTO' is not defined`

**解决**:
```python
# 替换 DTO 为 Entity
# 旧: dto = GameCreateDTO(gid=..., name=...)
# 新: entity = GameEntity(gid=..., name=...)
```

### Q3: 如何序列化结果？

**错误**: `AttributeError: 'GameEntity' object has no attribute 'to_dict'`

**解决**:
```python
# 使用 Pydantic 的方法
# 旧: result.to_dict()
# 新: result.model_dump()
```

### Q4: 如何处理异常？

**错误**: `NameError: name 'DomainException' is not defined`

**解决**:
```python
# 使用标准 Python 异常
# 旧: except DomainException as e
# 新: except ValueError as e
```

---

## 验证清单

迁移完成后，请验证以下内容：

- [ ] 所有 `backend.domain.*` 导入已移除
- [ ] 所有 `backend.application.*` 导入已移除
- [ ] 所有 DTO 使用已替换为 Entity
- [ ] 所有 `to_dict()` 已替换为 `model_dump()`
- [ ] 所有异常使用标准 Python 类型
- [ ] mutations 可以正确导入
- [ ] GraphQL schema 正确注册
- [ ] 基本功能测试通过

---

## 相关文档

- [完整修复报告](./graphql-mutations-refactoring-summary.md)
- [Entity 架构文档](/Users/mckenzie/Documents/event2table/backend/models/entities.py)
- [Game Service 文档](/Users/mckenzie/Documents/event2table/backend/services/games/game_service.py)
- [HQL Service 文档](/Users/mckenzie/Documents/event2table/backend/services/hql/hql_service_cached.py)

---

**最后更新**: 2026-02-26
**维护者**: Event2Table Development Team
