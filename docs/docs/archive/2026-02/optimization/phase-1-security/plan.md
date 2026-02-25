# Phase 1: 安全加固

> **阶段**: P1 - 高优先级 | **预计时间**: 2-3小时 | **并行任务**: 3个

---

## 📋 修复清单

### 问题1: 动态WHERE子句构建（3处）🟠 中

**位置**:
- `backend/api/routes/dashboard.py:122-219`
- `backend/api/routes/templates.py:97-110`
- `backend/api/routes/games.py:337`

**问题**: 使用f-string构建WHERE子句，存在潜在SQL注入风险

**修复方案**:
```python
# ✅ 使用SQLValidator或查询构建器
from backend.core.security.sql_validator import SQLValidator

# 示例：dashboard.py
def build_safe_where_clause(game_gid: Optional[int]) -> Tuple[str, Tuple]:
    if game_gid:
        SQLValidator.validate_column_name("gid")  # 验证列名
        return "WHERE g.gid = ?", (game_gid,)
    return "", ()
```

---

### 问题2: 动态UPDATE字段构建（2处）🟠 中

**位置**:
- `backend/api/routes/games.py:337`
- `backend/api/routes/join_configs.py:296`

**问题**: 动态构建UPDATE SET子句，字段名未验证

**修复方案**:
```python
# ✅ 使用字段白名单验证
ALLOWED_UPDATE_FIELDS = {
    'games': ['name', 'ods_db', 'description', 'is_active'],
    'join_configs': ['name', 'config', 'is_active']
}

def validate_update_fields(table: str, fields: List[str]) -> None:
    allowed = ALLOWED_UPDATE_FIELDS.get(table, [])
    for field in fields:
        if field not in allowed:
            raise ValueError(f"Invalid field for update: {field}")
```

---

### 问题3: LIKE查询未转义通配符（1处）🟡 低

**位置**: `backend/api/routes/templates.py:91-92`

**问题**: 搜索参数中的`%`和`_`未转义

**修复方案**:
```python
# ✅ 转义LIKE通配符
def escape_like_wildcards(search: str) -> str:
    """转义SQL LIKE通配符"""
    return search.replace("%", "\\%").replace("_", "\\_")

# 使用
escaped_search = escape_like_wildcards(search)
params.extend([f"%{escaped_search}%", f"%{escaped_search}%", f"%{escaped_search}%"])
```

---

### 问题4: 部分字段缺少XSS防护（5处）🟠 中

**位置**: `backend/models/schemas.py`

**未转义字段**:
- `EventBase.source_table` (Line 156)
- `EventBase.target_table` (Line 157)
- `FieldDefinition.field_name`
- `ConditionDefinition.field`
- `HQLGenerationRequest.hql`

**修复方案**:
```python
# ✅ 添加XSS防护验证器
from pydantic import validator
import html

class EventBase(BaseModel):
    source_table: str
    target_table: str
    
    @validator('source_table', 'target_table')
    def sanitize_table_names(cls, v):
        """转义表名中的特殊字符"""
        if v:
            return html.escape(v.strip())
        return v
```

---

### 问题5: SQLValidator未被广泛使用 🟡 中

**位置**: 整个backend目录

**问题**: `SQLValidator`仅在`ddl_generator.py`和`field_builder.py`中使用

**修复方案**:
1. 创建强制使用SQLValidator的中间件
2. 更新开发规范，要求所有动态SQL使用SQLValidator
3. 添加代码审查检查清单

---

### 问题6: 批量删除未验证ID列表（1处）🟠 中

**位置**: `backend/api/routes/categories.py:227`

**问题**: 批量删除时动态构建IN子句

**修复方案**:
```python
# ✅ 验证ID列表
def validate_id_list(ids: List[int], max_count: int = 100) -> List[int]:
    """验证ID列表"""
    if not ids:
        raise ValueError("ID list cannot be empty")
    if len(ids) > max_count:
        raise ValueError(f"Too many IDs: {len(ids)} > {max_count}")
    if not all(isinstance(id, int) and id > 0 for id in ids):
        raise ValueError("All IDs must be positive integers")
    return ids

# 使用
validated_ids = validate_id_list(data["ids"])
```

---

### 问题7: WHERE条件值转义不完整（1处）🟠 中

**位置**: `backend/services/hql/builders/where_builder.py:158-167`

**问题**: 仅对单引号进行转义

**修复方案**:
```python
# ✅ 使用参数化查询而非手动转义
def format_value_for_hql(value: Any) -> str:
    """格式化HQL条件值"""
    if value is None:
        return "NULL"
    elif isinstance(value, str):
        # 使用参数化查询，不手动转义
        return "?"  # 由调用方处理参数化
    elif isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    elif isinstance(value, (int, float)):
        return str(value)
    else:
        raise ValueError(f"Unsupported type: {type(value)}")
```

---

### 问题8: legacy_api.py多处安全风险 🔴 高

**位置**: `backend/api/routes/legacy_api.py`

**问题**:
- Line 227: 批量删除使用字符串拼接
- Line 49-50: 直接获取用户输入未验证
- Line 69,95: 直接返回异常信息

**修复方案**: 
- **建议废弃此API**，已在前端优化中移除使用
- 如需保留，需要完全重构

---

## 🚀 执行计划

### 并行subagent任务分配

```
Subagent 1: 修复动态SQL构建问题
├── api/routes/dashboard.py (WHERE子句)
├── api/routes/templates.py (WHERE子句 + LIKE转义)
├── api/routes/games.py (UPDATE字段 + WHERE子句)
└── api/routes/join_configs.py (UPDATE字段)

Subagent 2: 修复XSS防护和验证问题
├── models/schemas.py (5个字段XSS防护)
├── api/routes/categories.py (批量删除验证)
└── services/hql/builders/where_builder.py (转义改进)

Subagent 3: 改进SQLValidator使用和legacy API
├── 创建SQLValidator强制使用指南
├── 更新CLAUDE.md安全规范
└── 标记legacy_api.py为废弃
```

---

## ✅ 验证步骤

1. **安全测试**:
   ```bash
   # 测试SQL注入防护
   pytest backend/test/unit/core/security/ -v
   ```

2. **XSS测试**:
   ```bash
   # 测试XSS防护
   pytest backend/test/unit/models/ -k "sanitize" -v
   ```

3. **手动验证**:
   - 尝试SQL注入攻击（应被拦截）
   - 尝试XSS攻击（应被转义）
   - 验证LIKE搜索功能正常

---

## 🎯 预期成果

- ✅ 8个安全问题修复
- ✅ SQLValidator强制使用规范建立
- ✅ XSS防护覆盖所有用户输入字段
- ✅ legacy API标记为废弃

**风险**: 中 - 涉及多处SQL构建修改，需要充分测试

**下一步**: [Phase 2 - 性能优化](../phase-2-performance/plan.md)
