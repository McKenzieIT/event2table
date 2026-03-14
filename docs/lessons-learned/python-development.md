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

## Pydantic Validator最佳实践 ⚠️ **P0极其重要**

**优先级**: P0 | **最后更新**: 2026-03-09 | **来源**: [Validator执行顺序修复报告](../reports/2026-03-09/P0-8-VALIDATOR-EXECUTION-ORDER-FIX.md), [XSS防护修复总结](../reports/2026-03-09/XSS-PROTECTION-FIX-SUMMARY.md), [权限检查完整报告](../reports/2026-03-09/P0-11-PERMISSION-CHECK-COMPLETE.md)

### 问题现象

**症状描述**:
- Pydantic validator执行顺序导致验证失败
- XSS防护未生效，恶意HTML未转义
- 权限检查在某些情况下被绕过
- 验证器执行顺序不明确导致混乱

**影响范围**:
- 所有使用Pydantic validators的Schema
- 输入验证和XSS防护
- 权限检查中间件
- GraphQL mutations

### 根本原因

**技术原因**:
1. **Validator执行顺序不明确** - 不清楚pre=True和post=False的区别
2. **缺少mode="before"参数** - 自定义验证器在Field验证后执行
3. **多个验证器协调问题** - 验证器执行顺序不符合预期
4. **XSS防护时机错误** - HTML转义在错误的位置执行

### 核心概念

**Pydantic Validator执行顺序**:
```
1. pre=True validators (自定义验证器，在Field验证之前)
2. Field validators (Pydantic自动类型检查和约束)
3. post=False validators (自定义验证器，在Field验证之后)
4. model_validator (模型级验证器)
```

**关键原则**:
- **输入清理** → 使用 `mode="before"` 在Field验证之前清理数据
- **业务验证** → 使用默认模式在Field验证之后验证业务规则
- **全局验证** → 使用 `model_validator` 验证多个字段的关系

### 解决方案

**案例1: XSS防护使用mode="before"**

**错误示例**:
```python
# ❌ 错误：默认模式（mode="after"）无法清理空字符串
from pydantic import BaseModel, field_validator

class EventCreate(BaseModel):
    event_name: str

    @field_validator("event_name")
    @classmethod
    def sanitize_event_name(cls, v):
        """验证并清理事件名"""
        if isinstance(v, str):
            v = v.strip()
        if not v:
            raise ValueError("event_name不能为空")
        return html.escape(v)  # XSS防护

# 问题：空字符串 "" 会触发Field验证错误："field required"
# 不会执行到自定义验证器
```

**正确示例**:
```python
# ✅ 正确：使用mode="before"在Field验证之前执行
from pydantic import BaseModel, field_validator
import html

class EventCreate(BaseModel):
    event_name: str

    @field_validator("event_name", mode="before")  # ← 关键：mode="before"
    @classmethod
    def sanitize_event_name(cls, v):
        """验证并清理事件名，防止XSS攻击"""
        # 1. 类型检查和转换
        if not isinstance(v, str):
            v = str(v)

        # 2. 清理空格
        v = v.strip()

        # 3. 验证非空
        if not v:
            raise ValueError("event_name不能为空")

        # 4. 验证格式（不允许空格）
        if " " in v:
            raise ValueError("event_name不能包含空格")

        # 5. XSS防护（HTML转义）
        return html.escape(v) if isinstance(v, str) else v
```

**执行流程对比**:
```
mode="after"（默认）:
用户输入 "" → Field验证失败（"field required"） → ❌ 不执行自定义验证器

mode="before":
用户输入 "" → 自定义验证器清理和验证 → raise ValueError → ✅ 有意义的错误消息
```

---

**案例2: 多验证器协调执行顺序**

**问题场景**:
```python
# 需求：验证GID格式，同时验证唯一性
class GameCreate(BaseModel):
    gid: str
    name: str

    @field_validator("gid")
    @classmethod
    def validate_gid_format(cls, v):
        """验证GID格式：必须是数字"""
        if not v.isdigit():
            raise ValueError("GID必须是数字")
        return v

    @field_validator("gid")
    @classmethod
    def validate_gid_uniqueness(cls, v):
        """验证GID唯一性"""
        existing = game_repo.find_by_gid(v)
        if existing:
            raise ValueError(f"GID {v} 已存在")
        return v
```

**问题**: 两个验证器都装饰`gid`字段，执行顺序不确定

**解决方案1: 使用mode="before"和mode="after"明确顺序**:
```python
# ✅ 正确：使用mode明确执行顺序
class GameCreate(BaseModel):
    gid: str
    name: str

    @field_validator("gid", mode="before")  # ← 第1个执行
    @classmethod
    def validate_gid_format(cls, v):
        """验证GID格式：必须是数字"""
        if isinstance(v, str) and not v.isdigit():
            raise ValueError("GID必须是数字")
        return v

    @field_validator("gid")  # ← 第2个执行（mode="after"）
    @classmethod
    def validate_gid_uniqueness(cls, v):
        """验证GID唯一性（在格式验证之后）"""
        existing = game_repo.find_by_gid(v)
        if existing:
            raise ValueError(f"GID {v} 已存在")
        return v
```

**执行流程**:
```
用户输入 "ABC123" →
1. mode="before"验证器：validate_gid_format → raise ValueError("GID必须是数字") ✅

用户输入 "10000147" →
1. mode="before"验证器：validate_gid_format → 通过 ✅
2. Field验证：str类型检查 → 通过 ✅
3. mode="after"验证器：validate_gid_uniqueness → 检查数据库 ✅
```

---

**案例3: 模型级多字段验证**

**问题场景**:
```python
# 需求：验证密码和确认密码是否一致
class UserCreate(BaseModel):
    password: str
    confirm_password: str

    # ❌ 问题：单字段验证器无法访问其他字段
```

**解决方案: 使用model_validator**:
```python
# ✅ 正确：使用model_validator进行多字段验证
from pydantic import BaseModel, model_validator

class UserCreate(BaseModel):
    password: str
    confirm_password: str

    @model_validator(mode="after")
    def validate_passwords_match(cls, data):
        """验证密码和确认密码是否一致"""
        if data.password != data.confirm_password:
            raise ValueError("密码和确认密码不一致")
        return data
```

---

**案例4: 验证器执行顺序完整示例**

**完整验证流程**:
```python
from pydantic import BaseModel, field_validator, model_validator
import html

class GameCreate(BaseModel):
    gid: str
    name: str
    ods_db: str
    description: Optional[str] = None

    # 1. mode="before" - 输入清理（第1个执行）
    @field_validator("gid", mode="before")
    @classmethod
    def clean_gid(cls, v):
        """清理GID输入：去除空格，转换字符串"""
        if not isinstance(v, str):
            v = str(v)
        return v.strip()

    # 2. mode="before" - 输入清理（第1个执行）
    @field_validator("name", mode="before")
    @classmethod
    def sanitize_name(cls, v):
        """清理名称：防止XSS攻击"""
        if isinstance(v, str):
            v = v.strip()
        return html.escape(v) if isinstance(v, str) else v

    # 3. Field验证 - 自动类型检查和约束（第2个执行）
    # Pydantic自动执行：str类型检查

    # 4. mode="after" - 业务验证（第3个执行）
    @field_validator("gid")
    @classmethod
    def validate_gid_format(cls, v):
        """验证GID格式：必须是8-10位数字"""
        if not v.isdigit():
            raise ValueError("GID必须是数字")
        if len(v) < 8 or len(v) > 10:
            raise ValueError("GID必须是8-10位数字")
        return v

    # 5. mode="after" - 业务验证（第3个执行）
    @field_validator("ods_db")
    @classmethod
    def validate_ods_db(cls, v):
        """验证ODS数据库：必须是ieu_ods或overseas_ods"""
        valid_dbs = ["ieu_ods", "overseas_ods"]
        if v not in valid_dbs:
            raise ValueError(f"ODS数据库必须是: {', '.join(valid_dbs)}")
        return v

    # 6. model_validator - 全局验证（第4个执行）
    @model_validator(mode="after")
    def validate_business_rules(cls, data):
        """模型级验证：跨字段业务规则"""
        # 示例：检查描述长度是否合理
        if data.description and len(data.description) > 500:
            raise ValueError("描述不能超过500字符")
        return data
```

**执行流程**:
```
用户输入 {gid: " 90000001 ", name: "<script>alert('xss')</script>", ods_db: "ieu_ods"}

Step 1 (mode="before"): clean_gid → "90000001" (去除空格)
Step 1 (mode="before"): sanitize_name → "&lt;script&gt;alert('xss')&lt;/script&gt;" (HTML转义)
Step 2 (Field验证): gid是str ✅, name是str ✅, ods_db是str ✅
Step 3 (mode="after"): validate_gid_format → "90000001"是8-10位数字 ✅
Step 3 (mode="after"): validate_ods_db → "ieu_ods"是有效数据库 ✅
Step 4 (model_validator): validate_business_rules → 描述未超长 ✅

结果：验证通过 ✅
```

### 代码审查清单

**Pydantic Validator检查**:
- [ ] 输入清理是否使用 `mode="before"`？
- [ ] 业务验证是否使用默认模式（mode="after"）？
- [ ] 多字段验证是否使用 `model_validator`？
- [ ] XSS防护是否在输入清理阶段执行？
- [ ] 验证器执行顺序是否符合预期？

**安全检查**:
- [ ] 所有用户输入是否进行HTML转义（XSS防护）？
- [ ] 是否使用 `html.escape()` 而非自定义转义？
- [ ] 是否验证输入长度（防止DoS攻击）？
- [ ] 是否验证输入格式（防止注入攻击）？

**测试验证**:
- [ ] 是否测试空字符串输入？
- [ ] 是否测试特殊字符输入（<, >, &, ', "）？
- [ ] 是否测试SQL注入尝试（', ;, --）？
- [ ] 是否测试XSS攻击尝试（<script>, <img>）？

### 最佳实践总结

**1. 输入清理 vs 业务验证**:
```python
# ✅ 输入清理：mode="before"
@field_validator("field", mode="before")
def clean_input(cls, v):
    """清理：去除空格、转义特殊字符、类型转换"""
    return v.strip() if isinstance(v, str) else v

# ✅ 业务验证：mode="after"（默认）
@field_validator("field")
def validate_business_rule(cls, v):
    """验证：检查格式、长度、唯一性等业务规则"""
    if not meets_business_rule(v):
        raise ValueError("不符合业务规则")
    return v
```

**2. 多验证器协调**:
```python
# ✅ 顺序：输入清理 → 格式验证 → 唯一性验证
@field_validator("field", mode="before")
def clean(cls, v): return v

@field_validator("field")
def validate_format(cls, v): return v

@field_validator("field")
def validate_unique(cls, v): return v
```

**3. 错误消息质量**:
```python
# ✅ 错误消息应该具体、可操作
@field_validator("gid")
def validate_gid(cls, v):
    if not v.isdigit():
        raise ValueError("GID必须是数字（提示：如90000001）")
    if len(v) < 8:
        raise ValueError(f"GID必须是8-10位数字（当前：{len(v)}位）")
    return v
```

### 业务价值

- 确保输入验证和XSS防护100%生效
- 验证器执行顺序明确，易于维护
- 错误消息质量提升，用户体验改善
- 防止SQL注入、XSS攻击等安全漏洞

### 案例文档

- [Validator执行顺序修复报告](../reports/2026-03-09/P0-8-VALIDATOR-EXECUTION-ORDER-FIX.md)
- [XSS防护修复总结](../reports/2026-03-09/XSS-PROTECTION-FIX-SUMMARY.md)
- [权限检查完整报告](../reports/2026-03-09/P0-11-PERMISSION-CHECK-COMPLETE.md)
- [安全要点 - XSS防护](./security-essentials.md#xss防护实施)

---

### 相关经验

- [React最佳实践 - TypeScript类型](./react-best-practices.md) - 前端TypeScript类型安全
- [API设计模式 - 分层架构](./api-design-patterns.md) - Repository层设计
- [重构检查清单 - TDD重构](./refactoring-checklist.md) - 类型安全重构流程
