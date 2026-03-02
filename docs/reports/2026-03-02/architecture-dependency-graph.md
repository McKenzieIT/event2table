# Event2Table 架构依赖关系图

## 当前架构状态

### ✅ 正确的依赖方向

```
┌─────────────────────────────────────────────────────────────┐
│                     API Layer (HTTP端点)                      │
│  backend/api/routes/                                         │
│  - games.py, events.py, parameters.py, flows.py, etc.       │
│                                                               │
│  职责:                                                         │
│  ✓ 处理HTTP请求/响应                                          │
│  ✓ 参数解析和验证 (Pydantic Entity)                           │
│  ✓ 调用Service层                                              │
│  ✓ 统一错误处理 (json_error_response)                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
                            ↓ 调用
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Service Layer (业务逻辑)                     │
│  backend/services/                                           │
│  - games/game_service.py                                     │
│  - events/event_service.py                                   │
│  - parameters/parameter_service.py                           │
│  - canvas/canvas_service.py                                  │
│                                                               │
│  职责:                                                         │
│  ✓ 实现业务逻辑                                               │
│  ✓ 协调多个Repository                                        │
│  ✓ 缓存管理 (@cached, @cache_invalidate)                      │
│  ❌ ❗大量直接数据库访问 (178处违规) ❗                          │
│  ✓ Bloom Filter集成                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
                            ↓ 应该只调用Repository
                            ↓ ❌ 但实际大量直接调用数据库
                            ↓
┌─────────────────────────────────────────────────────────────┐
│               Repository Layer (数据访问)                     │
│  backend/models/repositories/                                │
│  - games.py (GameRepository)                                 │
│  - events.py (EventRepository)                               │
│  - parameters.py (ParameterRepository)                       │
│  - flows.py (FlowRepository)                                 │
│                                                               │
│  职责:                                                         │
│  ✓ 封装数据访问逻辑                                           │
│  ✓ CRUD操作                                                  │
│  ✓ 返回Entity对象 (而非字典)                                  │
│  ⚠️ 部分方法包含业务逻辑 (54处需审查)                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
                            ↓ 调用
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 Entity Layer (统一数据模型)                   │
│  backend/models/entities.py                                  │
│  - GameEntity, EventEntity, ParameterEntity                  │
│  - FlowEntity, JoinConfigEntity, etc.                        │
│                                                               │
│  职责:                                                         │
│  ✓ 单一真相来源 (Single Source of Truth)                     │
│  ✓ Pydantic自动输入验证                                       │
│  ✓ XSS防护 (html.escape)                                     │
│  ✓ 序列化/反序列化                                           │
│  ✓ 无业务逻辑 ✅                                              │
└─────────────────────────────────────────────────────────────┘
```

## 违规的依赖关系

### ❌ 违规1: Service层直接访问数据库

```
Service Layer
    ↓
    ↓ ❌ 绕过Repository
    ↓
fetch_one_as_dict()
fetch_all_as_dict()
execute_update()
    ↓
    ↓ 直接数据库操作
    ↓
SQLite Database
```

**影响**:
- 绕过Repository层的缓存机制
- 数据库查询逻辑分散在各处
- 难以进行单元测试（无法mock Repository）
- 代码重复（多个Service重复相同的查询）

**示例**:
```python
# backend/services/event_node_builder/__init__.py

# ❌ 错误：直接访问数据库
game = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (game_gid,))

# ✅ 正确：通过Repository层
game_repo = GameRepository()
game = game_repo.find_by_gid(game_gid)
```

### ❌ 违规2: API层缺少Entity验证

```
API Layer
    ↓
    ↓ ❌ 手动验证或无验证
    ↓
validate_json_request()
手动 if 判断
    ↓
    ↓ 进入Service层
    ↓
Service Layer
```

**影响**:
- 验证逻辑分散，易出错
- 缺少XSS防护
- 缺少SQL注入防护
- 错误消息不友好

**示例**:
```python
# backend/api/routes/events.py

# ❌ 错误：手动验证
@api_bp.route("/api/events", methods=["POST"])
def api_create_event():
    is_valid, data, error = validate_json_request([...])
    if not is_valid:
        return json_error_response(error, status_code=400)

    # 手动验证每个字段
    if len(event_name) > 200:
        return json_error_response("event_name exceeds maximum length")

# ✅ 正确：使用Entity验证
from backend.models.entities import EventEntity

@api_bp.route("/api/events", methods=["POST"])
def api_create_event():
    try:
        event_data = EventEntity(**request.get_json())  # 自动验证
        event = event_service.create_event(event_data)
        return json_success_response(data=event.model_dump())
    except ValidationError as e:
        return json_error_response(f"Validation error: {e}", status_code=400)
```

### ❌ 违规3: 错误处理不一致

```
API Layer
    ↓
    ↓ ❌ 没有try-except 或 直接暴露异常
    ↓
except Exception as e:
    return json_error_response(str(e))  # 暴露SQL、路径等
```

**影响**:
- 暴露敏感信息（SQL查询、文件路径）
- 用户体验差（错误信息不友好）
- 安全风险（信息泄露）

**示例**:
```python
# backend/api/routes/events.py

# ❌ 错误：暴露原始异常
except Exception as e:
    logger.error(f"Error creating event: {e}")
    return json_error_response(str(e), status_code=500)  # 可能暴露SQL

# ✅ 正确：使用通用错误消息
except Exception as e:
    logger.error(f"Error creating event: {e}", exc_info=True)  # 详细日志
    return json_error_response("Failed to create event", status_code=500)  # 通用消息
```

## 模块依赖关系

### 核心模块依赖图

```
┌──────────────────────────────────────────────────────────────┐
│                        API Routes                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  games   │  │  events  │  │params    │  │  flows   │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│       │             │             │             │            │
└───────┼─────────────┼─────────────┼─────────────┼────────────┘
        ↓             ↓             ↓             ↓
        └─────────────┴─────────────┴─────────────┘
                              ↓
                    ┌─────────────────┐
                    │  Service Layer  │
                    │  ┌───────────┐  │
                    │  │GameService│  │
                    │  └─────┬─────┘  │
                    │        │        │
                    │  ┌─────┴─────┐  │
                    │  │EventService│  │
                    │  └─────┬─────┘  │
                    │        │        │
                    │  ┌─────┴─────┐  │
                    │  │ParamService│  │
                    │  └─────┬─────┘  │
                    └────────┼────────┘
                             ↓
                    ┌─────────────────┐
                    │Repository Layer │
                    │  ┌───────────┐  │
                    │  │GameRepo   │  │
                    │  └─────┬─────┘  │
                    │        │        │
                    │  ┌─────┴─────┐  │
                    │  │EventRepo  │  │
                    │  └─────┬─────┘  │
                    │        │        │
                    │  ┌─────┴─────┐  │
                    │  │ParamRepo  │  │
                    │  └─────┬─────┘  │
                    └────────┼────────┘
                             ↓
                    ┌─────────────────┐
                    │  Entity Layer   │
                    │ GameEntity      │
                    │ EventEntity     │
                    │ ParameterEntity │
                    └─────────────────┘
```

### 跨层访问违规图

```
✅ 正确的依赖方向:
API → Service → Repository → Entity

❌ 违规的依赖方向:
Service → Database (绕过Repository)
API → Database (绕过Service和Repository)
```

## 数据流向图

### 正确的数据流向

```
┌─────────┐
│ Client  │
└────┬────┘
     │ HTTP Request
     ↓
┌─────────────────────────────────────────────────────────────┐
│ API Layer                                                    │
│                                                              │
│  1. 接收HTTP请求                                              │
│  2. 使用Entity验证输入                                        │
│     event_data = EventEntity(**request.get_json())          │
│  3. 调用Service层                                            │
│     event = event_service.create_event(event_data)          │
│  4. 返回JSON响应                                              │
│     return json_success_response(data=event.model_dump())   │
└─────────────────────────────────────────────────────────────┘
     │
     │ 调用
     ↓
┌─────────────────────────────────────────────────────────────┐
│ Service Layer                                                │
│                                                              │
│  1. 接收Entity对象                                            │
│  2. 执行业务逻辑                                              │
│     - 检查gid唯一性                                          │
│     - 应用业务规则                                           │
│  3. 调用Repository层                                         │
│     game_id = game_repo.create(game_data.model_dump())      │
│  4. 返回Entity对象                                            │
│     return GameEntity(**row)                                │
└─────────────────────────────────────────────────────────────┘
     │
     │ 调用
     ↓
┌─────────────────────────────────────────────────────────────┐
│ Repository Layer                                             │
│                                                              │
│  1. 接收查询参数                                              │
│  2. 执行数据库查询                                            │
│     row = fetch_one_as_dict("SELECT * FROM games WHERE...")  │
│  3. 返回Entity对象                                            │
│     return GameEntity(**row)                                │
└─────────────────────────────────────────────────────────────┘
     │
     │ 查询
     ↓
┌─────────────────────────────────────────────────────────────┐
│ Database (SQLite)                                            │
│                                                              │
│  - games 表                                                  │
│  - log_events 表                                             │
│  - event_params 表                                           │
└─────────────────────────────────────────────────────────────┘
```

### 违规的数据流向

```
┌─────────┐
│ Client  │
└────┬────┘
     │ HTTP Request
     ↓
┌─────────────────────────────────────────────────────────────┐
│ API Layer                                                    │
│                                                              │
│  1. 接收HTTP请求                                              │
│  2. ❌ 手动验证或无验证                                       │
│  3. 调用Service层                                            │
└─────────────────────────────────────────────────────────────┘
     │
     ↓
┌─────────────────────────────────────────────────────────────┐
│ Service Layer                                                │
│                                                              │
│  1. 接收请求参数                                              │
│  2. ❌ 直接访问数据库                                         │
│     game = fetch_one_as_dict("SELECT * FROM games WHERE...") │
│  3. ❌ 业务逻辑和数据访问混合                                  │
└─────────────────────────────────────────────────────────────┘
     │
     ↓
┌─────────────────────────────────────────────────────────────┐
│ Database (SQLite)                                            │
│  ❌ 绕过Repository层，缺少缓存管理                             │
└─────────────────────────────────────────────────────────────┘
```

## 架构改进建议

### 1. Service层重构

**当前状态**:
```
Service → fetch_one_as_dict() → Database
```

**目标状态**:
```
Service → Repository.find_by_id() → fetch_one_as_dict() → Database
```

**好处**:
- ✅ 统一数据访问逻辑
- ✅ 利用Repository缓存
- ✅ 便于单元测试
- ✅ 减少代码重复

### 2. API层验证重构

**当前状态**:
```
API → validate_json_request() → Service
```

**目标状态**:
```
API → Entity(**data) → Service
```

**好处**:
- ✅ 自动验证
- ✅ XSS防护
- ✅ 友好错误消息
- ✅ 减少代码量

### 3. 错误处理统一

**当前状态**:
```
API → try-except → str(e) → Client (可能暴露敏感信息)
```

**目标状态**:
```
API → try-except → logger.error(e) → "Failed to..." → Client
```

**好处**:
- ✅ 保护敏感信息
- ✅ 友好错误消息
- ✅ 详细日志记录

## 架构合规性检查工具

### 自动化检查脚本

```bash
# 运行架构合规性检查
python scripts/verify/architecture_compliance_check.py
```

**检查项**:
- ✅ 导入违规（跨层访问）
- ✅ Service层数据库访问
- ✅ Repository层业务逻辑
- ✅ 错误处理一致性
- ✅ 数据验证一致性

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
python scripts/verify/architecture_compliance_check.py
if [ $? -ne 0 ]; then
    echo "❌ 架构合规性检查失败，请修复后再提交"
    exit 1
fi
```

## 总结

### 当前架构合规率: 70.0%

**优势**:
- ✅ 依赖方向正确（无反向依赖）
- ✅ Entity层设计优秀
- ✅ Repository层职责基本清晰

**需要改进**:
- ❌ Service层大量直接数据库访问（178处）
- ❌ 错误处理不统一（98处）
- ❌ 数据验证不完整（57处）

### 目标架构合规率: 95.0%

**修复路径**:
1. **阶段1（1-2周）**: 修复P0问题 → 90%+
2. **阶段2（2-4周）**: 审查和优化 → 95%+
3. **阶段3（持续）**: 维持合规性 → 95%+

---

**文档版本**: v1.0
**最后更新**: 2026-03-02
**下次更新**: 2026-04-02
