# Phase 2 架构迁移实施计划

**生成时间**: 2026-03-02
**目标**: 架构一致性100%，消除API层直接数据库访问
**预计时间**: 8-10小时

---

## 📊 执行摘要

### 当前状态（V8.0.0）

| 维度 | 状态 | 违规数量 |
|------|------|----------|
| API层直接数据库访问 | 8个文件 | 37处 |
| 架构一致性 | 78% | - |
| Phase 1优化 | ✅ 完成 | 性能提升29.6% |

### Phase 2 目标（V9.0.0）

| 维度 | 目标 | 预期提升 |
|------|------|----------|
| API层直接数据库访问 | 0个文件 | -37处 (-100%) |
| 架构一致性 | 100% | +22% |
| 代码质量 | AAA | 消除技术债务 |

---

## 🔍 任务清单

### P0 - 核心API文件迁移（6个文件，6小时）

| # | 文件 | 直接访问 | 迁移方案 | 预计时间 |
|---|------|---------|----------|----------|
| 1 | `categories.py` | 2处 | GameService.get_game_by_gid() | 0.5小时 |
| 2 | `parameters.py` | 2处 | GameService.get_game_by_gid() | 0.5小时 |
| 3 | `flows.py` | 2处 | FlowService扩展 | 0.5小时 |
| 4 | `hql_generation.py` | 2处 | HQLService创建 | 1小时 |
| 5 | `event_parameters.py` | 0-2处 | ParameterService扩展 | 0.5小时 |
| 6 | `_param_helpers.py` | 1处 | 整合到GameService | 0.5小时 |

### P1 - 清理废弃文件（1个文件，0.5小时）

| # | 文件 | 操作 | 预计时间 |
|---|------|------|----------|
| 7 | `legacy_api.py` | 标记DEPRECATED | 0.5小时 |

### P2 - 测试验证（2小时）

| # | 任务 | 内容 | 预计时间 |
|---|------|------|----------|
| 8 | API契约测试 | 验证所有API端点 | 0.5小时 |
| 9 | 单元测试 | pytest backend/test/ | 0.5小时 |
| 10 | E2E测试 | playwright test | 1小时 |

---

## 🚀 实施步骤

### Task 1: 迁移 categories.py (0.5小时)

**文件**: `backend/api/routes/categories.py`

**当前问题**:
```python
# Line 72, 358
game = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (game_gid,))
if not game:
    return json_error_response(f"Game {game_gid} not found", status_code=404)
```

**修复方案**:
```python
# 导入GameService
from backend.services.games.game_service import GameService

# 替换为
service = GameService()
game = service.get_game_by_gid(game_gid)
if not game:
    return json_error_response(f"Game {game_gid} not found", status_code=404)
```

**检查清单**:
- [ ] 删除 `fetch_one_as_dict` 导入
- [ ] 添加 `GameService` 导入
- [ ] 替换所有游戏查询为Service调用
- [ ] 测试 `/api/categories` 端点

---

### Task 2: 迁移 parameters.py (0.5小时)

**文件**: `backend/api/routes/parameters.py`

**当前问题**:
```python
# Line 77, 84 - 在helper函数中
@lru_cache(maxsize=128)
def _get_game_id_from_gid(game_gid: int) -> Optional[int]:
    game = fetch_one_as_dict("SELECT id FROM games WHERE gid = ?", (game_gid,))
    return game["id"] if game else None

@lru_cache(maxsize=128)
def _get_game_gid_from_id(game_id: int) -> Optional[int]:
    game = fetch_one_as_dict("SELECT gid FROM games WHERE id = ?", (game_id,))
    return game["gid"] if game else None
```

**修复方案**:
```python
from backend.services.games.game_service import GameService

# GameService已经有这些方法，直接使用
@lru_cache(maxsize=128)
def _get_game_id_from_gid(game_gid: int) -> Optional[int]:
    service = GameService()
    game = service.get_game_by_gid(game_gid)
    return game.id if game else None

@lru_cache(maxsize=128)
def _get_game_gid_from_id(game_id: int) -> Optional[int]:
    service = GameService()
    game = service.get_game_by_id(game_id)
    return game.gid if game else None
```

**检查清单**:
- [ ] 修改helper函数使用GameService
- [ ] 测试 `/api/parameters/all` 端点

---

### Task 3: 迁移 flows.py (0.5小时)

**文件**: `backend/api/routes/flows.py`

**当前问题**:
```python
# Line 86 - 统计查询
total_result = fetch_one_as_dict(
    "SELECT COUNT(*) as total FROM flows WHERE game_gid = ?",
    (game_gid,)
)

# Line 92 - 列表查询
flows = fetch_all_as_dict(
    "SELECT * FROM flows WHERE game_gid = ? ORDER BY updated_at DESC",
    (game_gid,)
)
```

**修复方案**:
```python
# 扩展FlowService添加缺失方法
# backend/services/flows/flow_service.py

@cached(ttl=600)
def get_flows_count(self, game_gid: int) -> int:
    """获取指定游戏的Flow数量"""
    from backend.core.utils import fetch_one_as_dict
    result = fetch_one_as_dict(
        "SELECT COUNT(*) as total FROM flows WHERE game_gid = ?",
        (game_gid,)
    )
    return result["total"] if result else 0

# API层使用
from backend.services.flows.flow_service import FlowService

service = FlowService()
total = service.get_flows_count(game_gid)
flows = service.get_flows_by_game_gid(game_gid)
```

**检查清单**:
- [ ] 扩展FlowService添加 `get_flows_count()` 方法
- [ ] 更新API层使用FlowService
- [ ] 测试 `/api/flows` 端点

---

### Task 4: 迁移 hql_generation.py (1小时)

**文件**: `backend/api/routes/hql_generation.py`

**当前问题**:
```python
# Line 141, 306 - 需要检查具体使用情况
hql = fetch_one_as_dict(...)
current = fetch_one_as_dict(...)
```

**修复方案**:
```python
# 创建HQLService（如果不存在）或使用现有HQLHistoryService
# backend/services/hql/hql_service.py

from backend.services.hql.hql_history_service import HQLHistoryService

# API层使用
service = HQLHistoryService()
hql = service.get_hql_by_id(hql_id)
```

**检查清单**:
- [ ] 检查hql_generation.py中的具体查询
- [ ] 创建或扩展HQLService
- [ ] 更新API层使用Service
- [ ] 测试HQL生成端点

---

### Task 5: 迁移 event_parameters.py (0.5小时)

**文件**: `backend/api/routes/event_parameters.py`

**分析**:
- 已经使用ParameterService ✅
- 导入了`fetch_all_as_dict`, `fetch_one_as_dict`
- 需要验证是否实际使用

**检查清单**:
- [ ] 搜索文件中`fetch_*`的实际使用
- [ ] 如果有使用，替换为ParameterService方法
- [ ] 删除未使用的导入
- [ ] 测试 `/api/event-parameters` 端点

---

### Task 6: 整合 _param_helpers.py (0.5小时)

**文件**: `backend/api/routes/_param_helpers.py`

**分析**:
- 辅助函数文件，可能包含游戏上下文验证
- 需要整合到GameService或保留helper但使用Service

**修复方案**:
```python
# 保留helper但使用Service层
from backend.services.games.game_service import GameService

def resolve_game_context():
    """解析游戏上下文"""
    service = GameService()
    # ... 使用Service验证游戏
```

**检查清单**:
- [ ] 检查_param_helpers.py中的直接数据库访问
- [ ] 替换为Service调用
- [ ] 更新所有使用此helper的文件

---

### Task 7: 标记 legacy_api.py 为DEPRECATED (0.5小时)

**文件**: `backend/api/routes/legacy_api.py`

**操作**:
```python
"""
LEGACY API MODULE - DEPRECATED

This module is marked as DEPRECATED and will be removed in V10.0.0.
Please migrate to the new API endpoints:

旧端点 → 新端点:
- /api/legacy/games → /api/games
- /api/legacy/events → /api/events
- /api/legacy/parameters → /api/parameters

Deprecated: 2026-03-02
Removal: V10.0.0 (estimated 2026-04-01)
"""
```

**检查清单**:
- [ ] 添加DEPRECATED头部注释
- [ ] 更新文档说明迁移路径
- [ ] 在API响应中添加 `X-Deprecated: true` 头

---

## 📋 测试验证

### API契约测试
```bash
python scripts/test/api_contract_test.py
```

### 单元测试
```bash
pytest backend/test/unit/ -v
```

### E2E测试
```bash
cd frontend
npm run test:e2e
```

---

## 📊 成功指标

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| API层直接数据库访问 | 37处 | 0处 | -100% ✅ |
| 架构一致性 | 78% | 100% | +22% ✅ |
| 代码质量 | B | AAA | +2级 ✅ |

---

## 🎯 预期成果

### 架构一致性
- ✅ 所有API路由通过Service层访问数据
- ✅ 所有Service通过Repository层访问数据
- ✅ 统一的错误处理和缓存策略

### 代码质量
- ✅ 消除所有直接数据库访问
- ✅ 代码审查通过率100%
- ✅ 测试覆盖率保持>90%

### 性能
- ✅ API响应时间保持<100ms
- ✅ 缓存命中率>80%
- ✅ 无性能退化

---

**计划创建时间**: 2026-03-02
**预计完成**: 2026-03-02 (同日)
**总工作量**: 8-10小时
