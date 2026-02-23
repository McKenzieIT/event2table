# Phase 0: 紧急修复

> **阶段**: P0 - 紧急 | **预计时间**: 1-2小时 | **并行任务**: 4个

---

## 📋 修复清单

### 问题1: 异常信息泄露（56处）🔴 严重

**影响**: 可能暴露内部路径、SQL、堆栈信息给用户

**受影响文件**（11个）:
- `backend/api/routes/events.py:344`
- `backend/api/routes/templates.py:262`
- `backend/api/routes/flows.py:277,299,371`
- `backend/services/flows/routes.py:60,101,129,179,215,248,278`
- `backend/api/routes/hql_preview_v2.py:276,356,720,866,963,1079,1274`
- `backend/api/routes/field_builder.py:155,201,256,299,326`
- `backend/services/canvas/canvas.py:153,186,238`
- `backend/services/cache_monitor/cache_monitor.py:149,214,305,349`
- `backend/api/routes/hql_generation.py:58,91,204,223,256`
- `backend/api/routes/event_parameters.py:64,82,96,110,128,151,165,191,194`
- `backend/api/routes/legacy_api.py:69,95,227`

**修复方案**:
```python
# ❌ 当前（错误）
except Exception as e:
    logger.error(f"Error: {e}")
    return json_error_response(str(e), status_code=500)

# ✅ 修复后
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)  # 完整堆栈记录到日志
    return json_error_response("An internal error occurred", status_code=500)
```

---

### 问题2: GenericRepository SQL构建安全问题 🔴 高

**位置**: `backend/core/data_access.py:86-110`

**问题**: 使用f-string构建SQL，表名和字段名未验证

**当前代码**:
```python
# ❌ 危险：表名/字段名未验证
query = f"SELECT * FROM {self.table_name} WHERE {self.primary_key} = ?"
query = f"SELECT * FROM {self.table_name} WHERE {field} = ?"
```

**修复方案**:
```python
# ✅ 添加验证
from backend.core.security.sql_validator import SQLValidator

class GenericRepository:
    ALLOWED_TABLES = {
        'games', 'log_events', 'event_params', 'categories',
        'flow_templates', 'event_nodes', 'parameter_aliases'
    }
    
    def __init__(self, table_name: str, primary_key: str = 'id'):
        # 验证表名
        if table_name not in self.ALLOWED_TABLES:
            raise ValueError(f"Invalid table name: {table_name}")
        self.table_name = table_name
        self.primary_key = primary_key
    
    def find_by_field(self, field: str, value: Any) -> Optional[Dict]:
        # 验证字段名
        SQLValidator.validate_column_name(field)
        query = f"SELECT * FROM {self.table_name} WHERE {field} = ?"
        return fetch_one_as_dict(query, (value,))
```

---

### 问题3: 缺少导入（2处）🔴 高

**位置1**: `backend/api/routes/field_builder.py:170, 314`

**错误**: 缺少 `get_db_connection` 和 `Repositories` 导入

**修复方案**:
```python
# 添加到文件顶部的导入
from backend.core.database.database import get_db_connection
from backend.core.data_access import Repositories
```

**位置2**: `backend/api/routes/flows.py:377, 410`

**错误**: 缺少 `validate_json_request` 导入

**修复方案**:
```python
# 添加到文件顶部的导入
from backend.core.utils import validate_json_request
```

---

### 问题4: Session设置错误 🔴 严重

**位置**: `backend/services/games/games.py:62, 66`

**当前代码**:
```python
# ❌ 错误：session中设置的是id而非gid
session["current_game_gid"] = game["id"]
```

**修复方案**:
```python
# ✅ 正确：使用gid
session["current_game_gid"] = game["gid"]
```

---

## 🚀 执行计划

### 并行subagent任务分配

```
Subagent 1: 修复异常信息泄露（56处）
├── api/routes/events.py (1处)
├── api/routes/templates.py (1处)
├── api/routes/flows.py (3处)
├── api/routes/hql_preview_v2.py (7处)
├── api/routes/field_builder.py (5处)
├── api/routes/hql_generation.py (5处)
├── api/routes/event_parameters.py (9处)
└── api/routes/legacy_api.py (3处)

Subagent 2: 修复GenericRepository SQL构建
└── core/data_access.py (1处，影响所有Repository)

Subagent 3: 修复缺少的导入
├── api/routes/field_builder.py (2处)
└── api/routes/flows.py (1处)

Subagent 4: 修复Session设置错误
└── services/games/games.py (1处)
```

---

## ✅ 验证步骤

完成修复后执行：

1. **单元测试**:
   ```bash
   pytest backend/test/unit/ -v
   ```

2. **集成测试**:
   ```bash
   pytest backend/test/integration/ -v
   ```

3. **API契约测试**:
   ```bash
   python scripts/test/api_contract_test.py
   ```

4. **手动验证**:
   - 触发异常场景，确认不再返回详细错误信息
   - 验证GenericRepository仍然正常工作
   - 验证field_builder和flows功能正常
   - 验证Session中的game_gid值正确

---

## 📝 执行日志

| 时间 | Subagent | 任务 | 状态 | 备注 |
|------|----------|------|------|------|
| - | - | - | ⏳ 待开始 | - |

---

## 🎯 预期成果

- ✅ 56处异常信息泄露修复，提升安全性
- ✅ GenericRepository添加输入验证，防止SQL注入
- ✅ 3处缺少的导入修复，消除运行时错误
- ✅ Session设置修复，避免游戏上下文错误

**风险**: 低 - 修改范围明确，影响可控

**下一步**: [Phase 1 - 安全加固](../phase-1-security/plan.md)
