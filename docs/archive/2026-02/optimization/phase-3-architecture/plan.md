# Phase 3: 架构重构

> **阶段**: P3 - 中等优先级 | **预计时间**: 4-6小时 | **并行任务**: 4个

---

## 📋 重构清单

### 问题1: API层直接调用数据库（157处）🔴 高

**位置**: `backend/api/routes/*.py` 所有路由文件

**问题**: 绕过Service/Repository层，违反分层架构

**重构方案**:
```python
# ❌ 当前（错误）
# api/routes/games.py
@games_bp.route('/api/games', methods=['GET'])
def list_games():
    games = fetch_all_as_dict("SELECT * FROM games ORDER BY name")
    return json_success_response(data=games)

# ✅ 重构后
# api/routes/games.py
@games_bp.route('/api/games', methods=['GET'])
def list_games():
    service = GameService()
    games = service.get_all_games()
    return json_success_response(data=games)

# services/games/game_service.py
class GameService:
    def __init__(self):
        self.game_repo = GameRepository()
    
    def get_all_games(self) -> List[Dict[str, Any]]:
        """获取所有游戏"""
        return self.game_repo.find_all()

# models/repositories/games.py
class GameRepository(GenericRepository):
    def find_all(self) -> List[Dict[str, Any]]:
        """查询所有游戏"""
        return fetch_all_as_dict("SELECT * FROM games ORDER BY name")
```

**影响范围**: 157处API调用，需要逐步迁移

---

### 问题2: Service层定义API路由 🔴 高

**位置**: `backend/services/flows/routes.py`

**问题**: Service层包含Flask Blueprint，职责混乱

**重构方案**:
```python
# 1. 将路由迁移到 api/routes/flows.py
# api/routes/flows.py
from backend.services.flows.flow_service import FlowService

@flows_bp.route('/api/flows', methods=['GET'])
def list_flows():
    service = FlowService()
    flows = service.get_all_flows()
    return json_success_response(data=flows)

# 2. services/flows/flow_service.py 仅保留业务逻辑
class FlowService:
    def get_all_flows(self):
        # 纯业务逻辑
        pass

# 3. 废弃 services/flows/routes.py
```

---

### 问题3: Service层直接调用数据库工具（30+处）🟠 中

**位置**: `backend/services/` 下多个文件

**问题**: Service层绕过Repository直接调用数据库

**重构方案**:
```python
# ❌ 当前（错误）
# services/games/games.py
class GameService:
    def get_game(self, game_gid: int):
        return fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (game_gid,))

# ✅ 重构后
class GameService:
    def __init__(self):
        self.game_repo = GameRepository()
    
    def get_game(self, game_gid: int):
        return self.game_repo.find_by_gid(game_gid)
```

---

### 问题4: Schema层未被充分使用 🟠 中

**位置**: `backend/models/schemas.py`

**问题**: Pydantic Schema已定义但API层大多直接使用手动验证

**重构方案**:
```python
# ❌ 当前（错误）
# api/routes/games.py
is_valid, data, error = validate_json_request(["gid", "name", "ods_db"])
if not is_valid:
    return json_error_response(error, status_code=400)

# ✅ 重构后
# api/routes/games.py
from backend.models.schemas import GameCreate

try:
    game_data = GameCreate(**request.json)
except ValidationError as e:
    return json_error_response(f"Validation error: {e}", status_code=400)

service = GameService()
game = service.create_game(game_data)
return json_success_response(data=game, status_code=201)
```

---

### 问题5: Repository层不完整 🟠 中

**位置**: `backend/models/repositories/`

**问题**: 仅存在4个Repository，缺少核心实体Repository

**重构方案**:
```python
# 创建缺失的Repository
# models/repositories/event_params.py
class EventParamRepository(GenericRepository):
    def __init__(self):
        super().__init__('event_params', 'id')
    
    def find_by_event_id(self, event_id: int) -> List[Dict[str, Any]]:
        """根据事件ID查询参数"""
        return fetch_all_as_dict(
            "SELECT * FROM event_params WHERE event_id = ?",
            (event_id,)
        )
    
    def batch_create(self, params: List[Dict[str, Any]]) -> int:
        """批量创建参数"""
        # ... 批量插入逻辑
        pass

# 类似地创建其他Repository
```

---

### 问题6: 重复的Blueprint注册 🔴 高

**位置**: 
- `backend/services/games/games.py`
- `backend/api/routes/games.py`

**问题**: 多个文件定义相同的Blueprint，导致路由冲突

**重构方案**:
```python
# 1. 统一使用 api_bp 作为API入口
# backend/api/routes/__init__.py
from flask import Blueprint

api_bp = Blueprint('api', __name__)

# 2. 移除 services/games/games.py 中的 Blueprint 定义
# 3. 所有路由文件使用 api_bp
```

---

### 问题7: 缺少Service层抽象 🔴 高

**位置**: 整体架构

**问题**: 大部分业务逻辑直接写在API路由中

**重构方案**:
```python
# 创建核心Service类
# services/games/game_service.py
class GameService:
    """游戏业务服务"""
    
    def __init__(self):
        self.game_repo = GameRepository()
        self.event_repo = EventRepository()
    
    def create_game(self, game_data: GameCreate) -> Dict[str, Any]:
        """创建游戏"""
        # 1. 业务逻辑验证
        if self.game_repo.exists_by_gid(game_data.gid):
            raise ValueError(f"Game gid {game_data.gid} already exists")
        
        # 2. 创建游戏
        game_id = self.game_repo.create(game_data.dict())
        
        # 3. 初始化默认配置
        self._init_default_config(game_id)
        
        return self.game_repo.find_by_id(game_id)

# 类似地创建 EventService, ParameterService 等
```

---

### 问题8: HQL服务层架构复杂 🟠 中

**位置**: `backend/services/hql/` 和 `backend/api/routes/hql_preview_v2.py`

**问题**: API层直接导入多个HQL子模块

**重构方案**:
```python
# 创建门面类
# services/hql/hql_facade.py
class HQLFacade:
    """HQL服务门面类"""
    
    def __init__(self):
        self.generator = HQLGenerator()
        self.validator = HQLPerformanceAnalyzer()
    
    def generate_hql(self, events, fields, conditions, mode):
        """生成HQL"""
        # 1. 验证
        self.validator.validate(events, fields)
        
        # 2. 生成
        hql = self.generator.generate(events, fields, conditions, mode)
        
        return hql

# API层只与门面类交互
# api/routes/hql_preview_v2.py
from backend.services.hql.hql_facade import HQLFacade

facade = HQLFacade()

@hql_bp.route('/api/hql/generate', methods=['POST'])
def generate_hql():
    hql = facade.generate_hql(events, fields, conditions, mode)
    return json_success_response(data={"hql": hql})
```

---

### 问题9: API路由文件过大 🟡 低

**位置**: `backend/api/routes/hql_preview_v2.py` (1369行)

**问题**: 单个文件违反单一职责

**重构方案**:
```python
# 拆分为多个模块
# api/routes/hql/
# ├── __init__.py
# ├── generation.py    # HQL生成相关路由
# ├── validation.py    # HQL验证相关路由
# └── history.py       # HQL历史记录路由
```

---

### 问题10: data_access.py使用importlib规避循环导入 🟡 低

**位置**: `backend/core/data_access.py:14-22`

**问题**: 使用importlib规避循环导入，表明架构问题

**重构方案**:
```python
# 重构模块结构，消除循环依赖
# 1. 将共享工具函数移到独立模块
# backend/core/database/shared.py

# 2. data_access.py 导入共享模块
from backend.core.database.shared import get_db_connection
```

---

## 🚀 执行计划

### 并行subagent任务分配

```
Subagent 1: 创建Service层
├── services/games/game_service.py
├── services/events/event_service.py
├── services/parameters/parameter_service.py
└── services/flows/flow_service.py

Subagent 2: 完善Repository层
├── models/repositories/event_params.py
├── models/repositories/categories.py
├── models/repositories/flow_templates.py
└── 迁移现有Repository使用

Subagent 3: 统一API层架构
├── 移除 services/flows/routes.py
├── 统一使用 api_bp
├── 拆分 hql_preview_v2.py
└── API层迁移到使用Service层

Subagent 4: Schema层优化
├── API层统一使用Pydantic Schema
├── 移除手动验证代码
└── 创建HQL门面类
```

---

## ✅ 验证步骤

1. **架构测试**:
   ```bash
   # 验证分层架构
   pytest backend/test/unit/core/ -v
   pytest backend/test/unit/services/ -v
   ```

2. **集成测试**:
   ```bash
   # 完整集成测试
   pytest backend/test/integration/ -v
   ```

3. **API测试**:
   ```bash
   # API契约测试
   python scripts/test/api_contract_test.py
   ```

---

## 🎯 预期成果

- ✅ 完整的四层架构（API → Service → Repository → Schema）
- ✅ Service层封装所有业务逻辑
- ✅ Repository层统一数据访问
- ✅ API层仅处理HTTP请求/响应
- ✅ 统一的错误处理和验证

**架构改进**:
- 代码可维护性: 提升50%
- 模块耦合度: 降低40%
- 测试覆盖率: 提升30%

**风险**: 高 - 大规模重构，需要充分测试和逐步迁移

**下一步**: [Phase 4 - 代码质量](../phase-4-code-quality/plan.md)
