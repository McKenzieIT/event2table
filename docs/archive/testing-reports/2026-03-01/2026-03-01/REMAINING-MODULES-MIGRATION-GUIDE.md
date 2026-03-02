# 剩余模块迁移指南 - 方案 A（100% 完成）

**目标**: 完成剩余 25% 模块的 ERS 架构迁移
**预计工作量**: 18-21 小时
**执行方式**: 手动迁移（按照本指南逐步执行）

---

## 📋 迁移清单

### P0 - 必须完成（前端使用中）

- [ ] **完善 events.py** (3-4小时)
  - [ ] 分析 9 处直接数据库访问
  - [ ] 扩展 EventService（添加 5-6 个方法）
  - [ ] 重构 API 使用 Service
  - [ ] 测试验证

- [ ] **完善 parameters.py** (4-5小时)
  - [ ] 分析 23 处直接数据库访问
  - [ ] 扩展 ParameterService（添加 10-12 个方法）
  - [ ] 重构 API 使用 Service
  - [ ] 测试验证

- [ ] **迁移 Field Builder** (2小时)
  - [ ] 创建 FieldBuilderService
  - [ ] 重构 field_builder.py API
  - [ ] 测试验证

### P1 - 可选（已被 GraphQL 替代）

- [ ] **迁移 Dashboard** (5小时) 或直接移除
- [ ] **迁移 Templates** (2-3小时) 或直接移除
- [ ] **迁移 Nodes** (2小时) 或直接移除

---

## 🔧 任务 1: 完善 events.py 迁移

### 当前状态

**文件**: `backend/api/routes/events.py` (569行)
**Service**: `backend/services/events/event_service.py`
**问题**: 9 处直接数据库访问

### 直接数据库访问位置

根据 grep 结果，以下行有直接数据库访问：
- Line 153: `fetch_one_as_dict` - 获取总数
- Line 157: `fetch_all_as_dict` - 获取事件列表
- Line 198: `fetch_one_as_dict` - 获取分类
- Line 208: `fetch_one_as_dict` - 获取默认分类
- Line 215: `execute_write` - 插入事件
- Line 249: `fetch_one_as_dict` - 获取游戏
- Line 266: `execute_write` - 更新事件
- Line 336: `fetch_one_as_dict` - 获取事件详情
- Line 400: `execute_write` - 删除事件

### 需要添加到 EventService 的方法

#### 1. get_events_count

```python
@cached("events.count", timeout=120)
def get_events_count(self, game_gid: Optional[int] = None, search: Optional[str] = None) -> int:
    """
    获取事件数量

    Args:
        game_gid: 可选的游戏GID过滤
        search: 可选的搜索关键词

    Returns:
        事件数量
    """
    if search:
        return self.event_repo.count_by_search(search, game_gid)
    elif game_gid:
        return self.event_repo.count_by_game_gid(game_gid)
    else:
        return self.event_repo.count_all()
```

#### 2. get_events_by_category

```python
@cached("events.by_category", timeout=180)
def get_events_by_category(self, category_id: Optional[int]) -> List[EventEntity]:
    """
    根据分类ID获取事件

    Args:
        category_id: 分类ID

    Returns:
        事件Entity列表
    """
    if category_id:
        return self.event_repo.find_by_category(category_id)
    return []
```

#### 3. get_default_category

```python
@cached("events.default_category", timeout=600)
def get_default_category(self) -> Optional[Dict[str, Any]]:
    """
    获取默认分类

    Returns:
        分类信息字典
    """
    return self.event_repo.get_default_category()
```

#### 4. search_events

```python
@cached("events.search", timeout=120)
def search_events(self, keyword: str, game_gid: Optional[int] = None) -> List[EventEntity]:
    """
    搜索事件

    Args:
        keyword: 搜索关键词
        game_gid: 可选的游戏GID过滤

    Returns:
        匹配的事件Entity列表
    """
    return self.event_repo.search_by_name(keyword, game_gid)
```

### 重构 events.py API

**重构前** (Line 150-165):
```python
# 构建查询
count_query = "SELECT COUNT(*) as total FROM log_events WHERE 1=1"
query = """
    SELECT le.* FROM log_events le
    WHERE 1=1
"""
params = []

# 添加过滤条件
if game_gid is not None:
    count_query += " AND game_gid = ?"
    query += " AND game_gid = ?"
    params.append(game_gid)

if search:
    count_query += " AND event_name LIKE ?"
    query += " AND event_name LIKE ?"
    params.append(f"%{search}%")

# 执行查询
total_result = fetch_one_as_dict(count_query, tuple(params))
events = fetch_all_as_dict(query, tuple(params + [per_page, offset]))
```

**重构后**:
```python
service = EventService()

# 获取事件数量
total = service.get_events_count(game_gid, search)

# 获取事件列表
events_data = service.get_events_by_game(game_gid, page, per_page, search)
events = events_data.get("events", [])
```

### 执行步骤

1. **打开** `backend/services/events/event_service.py`
2. **添加** 上述缺失的方法到 EventService
3. **打开** `backend/api/routes/events.py`
4. **替换** 每处直接数据库访问为 Service 调用
5. **测试** 验证所有 API 端点正常工作

---

## 🔧 任务 2: 完善 parameters.py 迁移

### 当前状态

**文件**: `backend/api/routes/parameters.py` (864行)
**Service**: `backend/services/parameters/parameter_service.py`
**问题**: 23 处直接数据库访问

### 直接数据库访问位置

根据 grep 结果，关键位置包括：
- Line 78, 85: `fetch_one_as_dict` - game_gid 转换
- Line 176, 196: `fetch_all_as_dict`, `fetch_one_as_dict` - 获取参数
- Line 281, 305, 322, 377, 390: `fetch_one_as_dict`, `fetch_all_as_dict` - 各种查询
- Line 405, 510, 546: `fetch_all_as_dict` - 公共参数
- Line 609, 657, 682, 689: `fetch_one_as_dict` - 详细信息
- Line 698, 704: `execute_write` - 更新操作
- Line 748: `fetch_all_as_dict` - 库参数
- Line 822: `fetch_one_as_dict` - 事件参数

### 需要添加到 ParameterService 的方法

#### 1. get_parameter_details

```python
@cached("parameters.details", timeout=300)
def get_parameter_details(self, param_name: str, game_gid: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    获取参数详细信息

    Args:
        param_name: 参数名称
        game_gid: 可选的游戏GID

    Returns:
        参数详细信息字典
    """
    return self.param_repo.get_details(param_name, game_gid)
```

#### 2. get_parameter_stats

```python
@cached("parameters.stats", timeout=600)
def get_parameter_stats(self, game_gid: Optional[int] = None) -> Dict[str, Any]:
    """
    获取参数统计信息

    Args:
        game_gid: 可选的游戏GID

    Returns:
        统计信息字典
    """
    return self.param_repo.get_statistics(game_gid)
```

#### 3. search_parameters

```python
@cached("parameters.search", timeout=180)
def search_parameters(self, keyword: str, game_gid: Optional[int] = None) -> List[ParameterEntity]:
    """
    搜索参数

    Args:
        keyword: 搜索关键词
        game_gid: 可选的游戏GID

    Returns:
        匹配的参数Entity列表
    """
    return self.param_repo.search_by_name(keyword, game_gid)
```

#### 4. get_parameter_usage

```python
@cached("parameters.usage", timeout=300)
def get_parameter_usage(self, param_name: str, game_gid: Optional[int] = None) -> Dict[str, Any]:
    """
    获取参数使用情况

    Args:
        param_name: 参数名称
        game_gid: 可选的游戏GID

    Returns:
        使用情况字典
    """
    return self.param_repo.get_usage(param_name, game_gid)
```

#### 5. export_parameters

```python
@cached("parameters.export", timeout=600)
def export_parameters(self, game_gid: int, format: str = "json") -> Dict[str, Any]:
    """
    导出参数

    Args:
        game_gid: 游戏GID
        format: 导出格式 (json/csv)

    Returns:
        导出的数据字典
    """
    if format == "json":
        params = self.get_parameters_by_game(game_gid)
        return {"format": "json", "data": [p.model_dump() for p in params]}
    # 添加其他格式支持
```

### 重构 parameters.py API

**重构前** (Line 78-85):
```python
@lru_cache(maxsize=128)
def _get_game_id_from_gid(game_gid: int) -> Optional[int]:
    """Cached game_gid to game_id conversion"""
    game = fetch_one_as_dict("SELECT id FROM games WHERE gid = ?", (game_gid,))
    return game["id"] if game else None
```

**重构后**:
```python
# 使用 GameService
from backend.services.games.game_service import GameService

def _get_game_id_from_gid(game_gid: int) -> Optional[int]:
    """Cached game_gid to game_id conversion"""
    game_service = GameService()
    game = game_service.get_game_by_gid(game_gid)
    return game.id if game else None
```

**重构前** (Line 176-196):
```python
if event_id:
    query = """
        SELECT ep.*, le.event_name, le.game_gid
        FROM event_params ep
        INNER JOIN log_events le ON ep.event_id = le.id
        WHERE ep.event_id = ? AND ep.is_active = 1
        ORDER BY ep.id
    """
    parameters = fetch_all_as_dict(query, (event_id,))
else:
    # ... 其他逻辑
```

**重构后**:
```python
service = ParameterService()
if event_id:
    parameters = service.get_parameters_by_event(event_id)
else:
    parameters = service.get_all_parameters()
```

### 执行步骤

1. **打开** `backend/services/parameters/parameter_service.py`
2. **添加** 上述缺失的方法到 ParameterService
3. **打开** `backend/api/routes/parameters.py`
4. **替换** 每处直接数据库访问为 Service 调用
5. **测试** 验证所有 API 端点正常工作

---

## 🔧 任务 3: 迁移 Field Builder 模块

### 创建 FieldBuilderService

**文件**: `backend/services/field_builder/field_builder_service.py` (新建)

```python
from typing import Dict, Any, List, Optional
from backend.core.cache.decorators import cached, cache_invalidate
from backend.core.utils.converters import fetch_all_as_dict
import logging

logger = logging.getLogger(__name__)

class FieldBuilderService:
    """Field Builder 业务服务"""

    def __init__(self):
        pass

    @cached(ttl=1800, key_prefix="field_builder.base_fields")
    def get_base_fields(self, game_gid: int) -> List[Dict[str, Any]]:
        """获取基础字段列表"""
        query = """
            SELECT
                ep.id,
                ep.param_name,
                ep.param_type,
                pt.template_name,
                pt.display_name as type_display_name
            FROM event_params ep
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE ep.param_type = 'base'
            ORDER BY ep.param_name
        """
        return fetch_all_as_dict(query)

    @cached(ttl=1800, key_prefix="field_builder.custom_fields")
    def get_custom_fields(self, game_gid: int) -> List[Dict[str, Any]]:
        """获取自定义字段列表"""
        query = """
            SELECT
                ep.id,
                ep.param_name,
                ep.param_type,
                ep.json_path,
                pt.template_name,
                pt.display_name as type_display_name
            FROM event_params ep
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE ep.param_type = 'param'
            ORDER BY ep.param_name
        """
        return fetch_all_as_dict(query)

    @cached(ttl=1800, key_prefix="field_builder.all_fields")
    def get_all_fields(self, game_gid: int) -> Dict[str, Any]:
        """获取所有字段（基础+自定义）"""
        base_fields = self.get_base_fields(game_gid)
        custom_fields = self.get_custom_fields(game_gid)

        return {
            "base_fields": base_fields,
            "custom_fields": custom_fields,
            "total_fields": len(base_fields) + len(custom_fields)
        }
```

### 重构 field_builder.py API

**文件**: `backend/api/routes/field_builder.py`

**重构后**:
```python
from backend.services.field_builder.field_builder_service import FieldBuilderService

@api_bp.route("/api/field-builder/fields", methods=["GET"])
def api_get_fields():
    """API: 获取所有字段"""
    try:
        game_gid = request.args.get("game_gid", type=int)

        service = FieldBuilderService()
        fields = service.get_all_fields(game_gid)

        return json_success_response(data=fields)
    except Exception as e:
        logger.error(f"Error fetching fields: {e}")
        return json_error_response("Failed to fetch fields", status_code=500)
```

---

## 🎯 执行建议

### 策略 1: 分批完成（推荐）

**第一批**: events.py + parameters.py (7-9小时)
- 最关键，前端使用中
- 完成后核心功能100% ERS架构

**第二批**: Field Builder (2小时)
- 特殊用途，需要保留

**第三批**: Dashboard/Templates/Nodes (9-10小时 或 直接移除)
- 已被 GraphQL 替代
- 可考虑直接移除

### 策略 2: 优先完成 P0

只完成 P0 优先级任务（events.py + parameters.py + Field Builder），达到 95% ERS 架构覆盖。

**工作量**: 约 9-11 小时
**覆盖率**: 6/8 核心模块 → 7/8 (87.5%)

### 策略 3: 混合策略（最快）

1. 移除废弃 API（Dashboard, Templates, Nodes）- 1小时
2. 完善 events.py + parameters.py - 7-9小时
3. 迁移 Field Builder - 2小时

**总工作量**: 约 10-12 小时
**覆盖率**: 实际 100%（废弃模块已移除）

---

## ✅ 验证清单

完成迁移后，验证以下项目：

- [ ] 所有 API 端点返回正确响应
- [ ] 无直接数据库访问代码残留
- [ ] 所有查询方法使用 `@cached`
- [ ] 所有更新方法使用 `@cache_invalidate`
- [ ] 单元测试通过率 ≥ 95%
- [ ] API 契约测试通过
- [ ] 性能测试通过（响应时间 < 100ms）

---

## 📞 需要帮助？

如果在迁移过程中遇到问题：

1. **查看示例代码**: 参考已完成的模块（Games, Join Configs, Event Categories）
2. **查看文档**:
   - [FINAL-ARCHITECTURE-OPTIMIZATION-REPORT.md](FINAL-ARCHITECTURE-OPTIMIZATION-REPORT.md)
   - [QUICK-REFERENCE-CARD.md](QUICK-REFERENCE-CARD.md)
3. **运行测试**: `pytest backend/test/unit/services/ -v`

---

**指南生成时间**: 2026-03-01
**预计完成时间**: 10-21 小时（根据选择的策略）
**架构版本**: V7.8.0 → V8.0.0（目标）
