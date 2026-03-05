# Python开发最佳实践

> **来源**: 整合了mypy类型安全相关经验
> **最后更新**: 2026-03-04
> **维护**: 每次Python类型问题修复后立即更新

---

## mypy --strict合规 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 10+次 | **来源**: [MYPY_STRICT_COMPLIANCE_REPORT](../archive/2026-03/03-march/reports/MYPY_STRICT_COMPLIANCE_REPORT.md)

### 常见问题与解决方案

#### 问题1: Missing Return Types

**优先级**: P0 | **出现次数**: 15+次

**错误信息**:
```
error: Function is missing a return type annotation
```

**错误示例**:
```python
# ❌ 错误：缺少返回类型
def get_event(event_id: int):
    return event_repo.find_by_id(event_id)

def create_game(name: str, ods_db: str):
    return game_repo.create({"name": name, "ods_db": ods_db})
```

**正确示例**:
```python
# ✅ 正确：添加返回类型
from typing import Optional, Dict, Any

def get_event(event_id: int) -> Optional[EventEntity]:
    return event_repo.find_by_id(event_id)

def create_game(name: str, ods_db: str) -> GameEntity:
    return game_repo.create({"name": name, "ods_db": ods_db})

def get_all_events(game_gid: int) -> List[EventEntity]:
    return event_repo.find_by_game_gid(game_gid)
```

**代码审查清单**:
- [ ] 所有函数都有返回类型注解？
- [ ] 返回类型准确反映实际返回值？
- [ ] Optional用于可能返回None的情况？

---

#### 问题2: Untyped Constructors

**优先级**: P0 | **出现次数**: 20+次

**错误信息**:
```
error: Call to untyped function "__init__" in typed context
```

**错误示例**:
```python
# ❌ 错误：__init__缺少返回类型
class EventService:
    def __init__(self):
        self.event_repo = EventRepository()
        self.cache = HierarchicalCache()  # type: ignore[no-untyped-call]
        self.invalidator = CacheInvalidator(self.cache)  # type: ignore[no-untyped-call]

class GameService:
    def __init__(self, cache):
        self.game_repo = GameRepository()
        self.cache = cache
```

**正确示例**:
```python
# ✅ 正确：添加-> None和参数类型
from typing import Optional
from backend.core.cache.cache_system import HierarchicalCache, CacheInvalidator

class EventService:
    def __init__(self) -> None:
        self.event_repo = EventRepository()
        self.cache: HierarchicalCache = HierarchicalCache()
        self.invalidator: CacheInvalidator = CacheInvalidator(self.cache)

class GameService:
    def __init__(self, cache: Optional[HierarchicalCache] = None) -> None:
        self.game_repo = GameRepository()
        self.cache = cache or HierarchicalCache()
```

**代码审查清单**:
- [ ] 所有`__init__`方法都有`-> None`返回类型？
- [ ] 所有参数都有类型注解？
- [ ] 所有实例变量都有类型注解？

---

#### 问题3: Optional Handling

**优先级**: P0 | **出现次数**: 10+次

**错误信息**:
```
error: Incompatible return value type (got "X | None", expected "X")
```

**错误示例**:
```python
# ❌ 错误：可能返回None但类型标注为非Optional
def get_filter(self) -> EnhancedBloomFilter:
    if self._filter is None:
        self._filter = create_filter()
    return self._filter  # mypy错误：可能是None

def get_event_name(event_id: int) -> str:
    event = fetch_one_as_dict("SELECT name FROM events WHERE id = ?", (event_id,))
    return event["name"]  # mypy错误：event可能是None
```

**正确示例 - 方案1: 类型断言**:
```python
# ✅ 正确：添加类型断言
def get_filter(self) -> EnhancedBloomFilter:
    if self._filter is None:
        self._filter = create_filter()
    assert self._filter is not None, "Filter should be initialized"
    return self._filter

def get_event_name(event_id: int) -> str:
    event = fetch_one_as_dict("SELECT name FROM events WHERE id = ?", (event_id,))
    if event is None:
        raise ValueError(f"Event {event_id} not found")
    return event["name"]
```

**正确示例 - 方案2: 改变返回类型为Optional**:
```python
# ✅ 正确：返回Optional类型
from typing import Optional

def get_filter(self) -> Optional[EnhancedBloomFilter]:
    return self._filter

def get_event_name(event_id: int) -> Optional[str]:
    event = fetch_one_as_dict("SELECT name FROM events WHERE id = ?", (event_id,))
    return event["name"] if event else None
```

**正确示例 - 方案3: 使用dict.get()方法**:
```python
# ✅ 正确：使用dict.get()并提供默认值
def get_event_name(event_id: int) -> str:
    event = fetch_one_as_dict("SELECT name FROM events WHERE id = ?", (event_id,))
    return event.get("name", "Unknown") if event else "Unknown"
```

**代码审查清单**:
- [ ] 所有可能返回None的函数都返回Optional类型？
- [ ] 使用assert或raise处理None情况？
- [ ] 使用dict.get()而不是直接访问dict[key]？

---

#### 问题4: Unused Type Ignores

**优先级**: P1 | **出现次数**: 8+次

**错误信息**:
```
error: Unused "type: ignore" comment
```

**错误示例**:
```python
# ❌ 错误：不再需要type: ignore
x = some_function()  # type: ignore[comment]

class EventRepository(GenericRepository):
    def __init__(self) -> None:  # type: ignore[override]
        super().__init__("log_events")
```

**正确示例**:
```python
# ✅ 正确：修复类型或移除注释
x: int = some_function()

class EventRepository(GenericRepository):
    def __init__(self) -> None:
        super().__init__("log_events")
```

**何时使用type: ignore**:
- ✅ 只有在确认mypy误报时使用
- ✅ 必须添加注释说明原因
- ❌ 不要用于掩盖真实类型错误
- ❌ 不要在修复类型后保留

```python
# ✅ 正确：带注释的type: ignore
def legacy_api_call(param):  # type: ignore[no-untyped-call]  # Legacy API, cannot modify
    return external_service.call(param)
```

**代码审查清单**:
- [ ] 所有`type: ignore`都有注释说明原因？
- [ ] 没有用于掩盖真实类型错误的`type: ignore`？
- [ ] 定期审查是否可以移除`type: ignore`？

---

### GenericRepository类型安全 ⚠️ **P1重要**

**优先级**: P1 | **出现次数**: 5+次 | **来源**: 同上

#### 问题: 子类覆盖方法返回类型不兼容

**错误信息**:
```
error: Return type "EventEntity | None" of "find_by_id" incompatible with return type "dict[str, Any] | None" in supertype "GenericRepository"
error: Return type "ParameterEntity | None" of "create" incompatible with return type "dict[str, Any] | None" in supertype "GenericRepository"
```

**错误示例**:
```python
# ❌ 错误：子类返回类型与父类冲突
class EventRepository(GenericRepository):
    def find_by_id(self, id: int) -> Optional[EventEntity]:  # ❌ 与父类冲突
        row = fetch_one_as_dict("SELECT * FROM log_events WHERE id = ?", (id,))
        return EventEntity(**row) if row else None

class ParameterRepository(GenericRepository):
    def create(self, data: Dict[str, Any]) -> Optional[ParameterEntity]:  # ❌ 与父类冲突
        id = execute_insert("INSERT INTO event_params ...", (...))
        return self.find_by_id(id)
```

#### 解决方案1: 使GenericRepository泛型化 (推荐)

**正确示例**:
```python
# ✅ 正确：使用泛型Repository
from typing import TypeVar, Generic, Optional

T = TypeVar('T')

class GenericRepository(Generic[T]):
    def __init__(self, table_name: str) -> None:
        self.table_name = table_name

    def find_by_id(self, id: int) -> Optional[T]:  # ✅ 泛型返回类型
        row = fetch_one_as_dict(f"SELECT * FROM {self.table_name} WHERE id = ?", (id,))
        return self._row_to_entity(row) if row else None

    def create(self, data: Dict[str, Any]) -> Optional[T]:  # ✅ 泛型返回类型
        id = execute_insert(f"INSERT INTO {self.table_name} ...", (...))
        return self.find_by_id(id)

    def _row_to_entity(self, row: Dict[str, Any]) -> T:
        # 由子类实现
        raise NotImplementedError

class EventRepository(GenericRepository[EventEntity]):
    def __init__(self) -> None:
        super().__init__("log_events")

    def _row_to_entity(self, row: Dict[str, Any]) -> EventEntity:
        return EventEntity(**row)  # ✅ 类型安全

class ParameterRepository(GenericRepository[ParameterEntity]):
    def __init__(self) -> None:
        super().__init__("event_params")

    def _row_to_entity(self, row: Dict[str, Any]) -> ParameterEntity:
        return ParameterEntity(**row)  # ✅ 类型安全
```

**优点**:
- ✅ 完全类型安全
- ✅ 不需要`type: ignore`
- ✅ 自动类型推断
- ✅ 重构友好

**缺点**:
- ⚠️ 需要修改GenericRepository基类（影响范围大）
- ⚠️ 需要修改所有Repository子类

**工作量**: 8-12小时

---

#### 解决方案2: 使用类型注释忽略 (临时方案)

**正确示例**:
```python
# ✅ 临时方案：使用type: ignore[override]
class EventRepository(GenericRepository):
    def find_by_id(self, id: int) -> Optional[EventEntity]:  # type: ignore[override]
        row = fetch_one_as_dict("SELECT * FROM log_events WHERE id = ?", (id,))
        return EventEntity(**row) if row else None

    def create(self, data: Dict[str, Any]) -> Optional[EventEntity]:  # type: ignore[override]
        id = execute_insert("INSERT INTO log_events ...", (...))
        return self.find_by_id(id)
```

**优点**:
- ✅ 快速实施（30分钟）
- ✅ 不需要修改基类

**缺点**:
- ❌ 失去类型安全
- ❌ 需要手动维护类型注解
- ❌ 容易出错

**何时使用**:
- ✅ 临时解决方案
- ✅ 等待GenericRepository泛型化重构
- ❌ 不应作为长期方案

---

### 代码审查清单

#### mypy --strict合规检查

**每个Python文件必须检查**:
- [ ] 所有函数都有返回类型注解？
- [ ] 所有`__init__`方法都有`-> None`返回类型？
- [ ] 所有参数都有类型注解？
- [ ] Optional用于可能返回None的情况？
- [ ] 没有未使用的`type: ignore`注释？
- [ ] GenericRepository子类类型安全？

#### 运行mypy检查

```bash
# 激活虚拟环境
source backend/venv/bin/activate

# 运行mypy严格模式检查
mypy backend --strict

# 检查特定文件
mypy backend/services/events/event_service.py --strict

# 统计错误数量
mypy backend --strict 2>&1 | grep "error:" | wc -l
```

---

### 常用类型注解

#### 基础类型

```python
from typing import List, Dict, Optional, Tuple, Set, Any

# 基础类型
def get_name() -> str:
    return "Event2Table"

def get_count() -> int:
    return 42

def get_enabled() -> bool:
    return True

# 集合类型
def get_events() -> List[EventEntity]:
    return [event1, event2]

def get_mapping() -> Dict[str, int]:
    return {"event1": 1, "event2": 2}

def get_optional() -> Optional[str]:
    return None  # 或 "value"

# 复杂类型
def get_data() -> Dict[str, Any]:
    return {"name": "test", "count": 42, "enabled": True}

def get_coordinates() -> Tuple[float, float]:
    return (37.7749, -122.4194)

def get_unique_ids() -> Set[int]:
    return {1, 2, 3, 4, 5}
```

#### 函数类型

```python
from typing import Callable, Optional

def apply_function(func: Callable[[int], int], value: int) -> int:
    return func(value)

def optional_callback(callback: Optional[Callable[[str], None]]) -> None:
    if callback:
        callback("Hello")
```

#### 类型别名

```python
from typing import Dict, List, Optional

# 类型别名
GameId = int
EventList = List[EventEntity]
OptionalEvent = Optional[EventEntity]
GameData = Dict[str, Any]

def get_game(game_id: GameId) -> OptionalEvent:
    return event_repo.find_by_id(game_id)

def get_events() -> EventList:
    return event_repo.find_all()
```

---

### 相关经验

- [React最佳实践 - TypeScript类型](./react-best-practices.md) - 前端TypeScript类型安全
- [API设计模式 - 分层架构](./api-design-patterns.md) - Repository层设计
- [重构检查清单 - TDD重构](./refactoring-checklist.md) - 类型安全重构流程
