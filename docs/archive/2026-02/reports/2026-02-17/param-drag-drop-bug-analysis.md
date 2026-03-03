# 事件节点构建器 - 参数拖拽Bug根本原因分析

**日期**: 2026-02-17
**Bug描述**: 拖拽参数到画布后出现PropTypes警告和API 400错误

---

## 📋 问题概述

用户在事件节点构建器中拖拽参数到画布时遇到两个错误：

1. **React PropTypes警告**:
   ```
   Warning: Failed prop type: Invalid prop `fields[0].id` of type `number` supplied to `FieldCanvas`, expected `string`.
   Warning: Failed prop type: Invalid prop `fields[0].id` of type `number` supplied to `StatsPanel`, expected `string`.
   ```

2. **后端API错误**:
   ```
   POST /event_node_builder/api/preview-hql 400 (BAD REQUEST)
   Failed to preview HQL: BAD REQUEST
   ```

---

## 🔍 根本原因分析

### 问题1: PropTypes类型不匹配

#### 数据流追踪

**步骤1**: ParamSelector组件获取参数
```javascript
// /frontend/src/event-builder/components/ParamSelector.jsx:54
onAddField(
  "param",
  param.param_name,       // "zone_id"
  param.param_name_cn || param.param_name,  // "区服ID"
  param.id,               // ❌ 数字: 123 (来自数据库)
);
```

**步骤2**: useEventNodeBuilder hook创建字段对象
```javascript
// /frontend/src/shared/hooks/useEventNodeBuilder.js:52-64
const addFieldToCanvas = useCallback((fieldType, fieldName, displayName, paramId = null) => {
  setCanvasFields(prev => {
    const newField = {
      id: Date.now(),        // ❌ 数字: 1739792400000
      fieldType,
      fieldName,
      displayName,
      alias: fieldName,
      order: prev.length + 1,
      paramId,               // ❌ 数字: 123
    };
    return [...prev, newField];
  });
}, []);
```

**步骤3**: FieldCanvas组件接收字段
```javascript
// /frontend/src/event-builder/components/FieldCanvas.tsx:597-598
FieldCanvas.propTypes = {
  fields: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,  // ✅ 期望字符串
      // ...
    })
  ),
}
```

#### 类型不匹配位置

| 位置 | 代码 | 类型 | 期望类型 |
|------|------|------|----------|
| `addFieldToCanvas` | `id: Date.now()` | `number` | `string` |
| `addFieldToCanvas` | `paramId: param.id` | `number` | `number` ✅ |
| `FieldCanvas.propTypes` | `id: PropTypes.string` | N/A | `string` |

#### 结论

**根本原因**: `useEventNodeBuilder.js` 使用 `Date.now()` 生成ID时返回数字，但 `FieldCanvas.tsx` 的 PropTypes 定义要求 `id` 为字符串。

---

### 问题2: 后端API 400错误

#### 数据流追踪

**步骤1**: HQLPreviewContainer准备请求数据
```javascript
// /frontend/src/event-builder/components/HQLPreviewContainer.jsx:41-54
const requestData = {
  game_gid: parseInt(gameGid, 10),
  event_id: event.id,
  fields: (fields || []).map(f => ({
    param_id: f.paramId,        // ✅ 数字: 123
    field_name: f.fieldName,    // ✅ 字符串: "zone_id"
    field_type: f.fieldType,    // ✅ 字符串: "param"
    aggregate_func: f.aggregateFunc || '',
    is_primary: f.isPrimary || false,
    alias: f.alias              // ✅ 字符串: "zone_id"
  })),
  filter_conditions: filterConditionsDict,
  sql_mode: sqlMode
};
```

**步骤2**: ProjectAdapter.field_from_project验证字段
```python
# /backend/services/hql/adapters/project_adapter.py:94-137
def field_from_project(field_data: Dict[str, Any]) -> Field:
    field_name = field_data.get("fieldName") or field_data.get("field_name")
    field_type = field_data.get("fieldType") or field_data.get("field_type")

    if not field_name:
        raise ValueError("Field must have either 'fieldName' or 'field_name'")
    if not field_type:
        raise ValueError("Field must have either 'fieldType' or 'field_type'")

    return Field(
        name=field_name,
        type=field_type,
        alias=field_data.get("alias"),
        aggregate_func=field_data.get("aggregateFunc") or field_data.get("aggregate_func"),
        json_path=field_data.get("jsonPath") or field_data.get("json_path"),
        custom_expression=field_data.get("customExpression") or field_data.get("custom_expression"),
        fixed_value=field_data.get("fixedValue") or field_data.get("fixed_value"),
    )
```

**步骤3**: preview_hql API处理
```python
# /backend/services/event_node_builder/__init__.py:69-76
fields_v2 = []
for field in fields:
    try:
        field_obj = adapter.field_from_project(field)
        fields_v2.append(field_obj)
    except ValueError as e:
        return json_error_response(f"Invalid field: {str(e)}", status_code=400)
```

#### API 400错误的可能原因

经过代码分析，以下情况可能导致400错误：

1. **字段缺少必填字段**:
   - `field_name` 为空或undefined
   - `field_type` 为空或undefined

2. **后端Field模型验证失败**:
   ```python
   # backend/services/hql/models/event.py
   @dataclass
   class Field:
       name: str          # 必须为非空字符串
       type: str          # 必须为 'base' | 'param' | 'custom' | 'fixed'
       alias: Optional[str] = None
       # ...
   ```

3. **参数ID不匹配**:
   - 前端发送的 `param_id` 在数据库中不存在
   - 后端尝试查询参数信息时失败

#### 调试建议

在后端添加详细日志以确定具体错误原因：

```python
# /backend/services/event_node_builder/__init__.py:69
fields_v2 = []
for field in fields:
    try:
        logger.info(f"Processing field: {field}")  # 🔍 添加日志
        field_obj = adapter.field_from_project(field)
        fields_v2.append(field_obj)
    except ValueError as e:
        logger.error(f"Invalid field {field}: {str(e)}")  # 🔍 添加日志
        return json_error_response(f"Invalid field: {str(e)}", status_code=400)
```

---

## 🛠️ 修复方案

### 修复1: 统一ID类型为字符串

#### 选项A: 修改useEventNodeBuilder（推荐）

**文件**: `/frontend/src/shared/hooks/useEventNodeBuilder.js`

**修改位置**: 第52-64行

```javascript
const addFieldToCanvas = useCallback((fieldType, fieldName, displayName, paramId = null) => {
  setCanvasFields(prev => {
    const newField = {
      id: String(Date.now()),  // ✅ 转换为字符串
      fieldType,
      fieldName,
      displayName,
      alias: fieldName,
      order: prev.length + 1,
      paramId,  // 保持数字类型（符合PropTypes定义）
    };
    return [...prev, newField];
  });
}, []);
```

**同时更新PropTypes定义**:

```javascript
// /frontend/src/event-builder/components/FieldCanvas.tsx:597-604
FieldCanvas.propTypes = {
  fields: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,        // ✅ 字符串
      type: PropTypes.oneOf(['parameter', 'basic', 'custom', 'fixed']).isRequired,
      sourceId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),  // ✅ 兼容两种类型
      name: PropTypes.string.isRequired,
      alias: PropTypes.string,
      dataType: PropTypes.string.isRequired,
      isEditable: PropTypes.bool,
      paramId: PropTypes.number  // ✅ 保持数字类型
    })
  ),
  // ...
};
```

#### 选项B: 修改FieldCanvas PropTypes（不推荐）

如果确实需要 `id` 为数字类型，可以修改PropTypes：

```javascript
FieldCanvas.propTypes = {
  fields: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,  // 兼容两种类型
      // ...
    })
  ),
};
```

但这种方式会掩盖类型不一致的问题，不推荐。

---

### 修复2: 增强后端错误处理和日志

#### 文件: `/backend/services/event_node_builder/__init__.py`

**修改位置**: 第30-102行

```python
@event_node_builder_bp.route("/api/preview-hql", methods=["POST"])
def preview_hql():
    """
    API: 预览 HQL

    转发到现有的 HQL 生成逻辑
    """
    try:
        data = request.get_json()

        if not data:
            logger.error("Request body is required")
            return json_error_response("Request body is required", status_code=400)

        game_gid = data.get("game_gid")
        event_id = data.get("event_id")
        fields = data.get("fields", [])
        filter_conditions = data.get("filter_conditions", {})
        sql_mode = data.get("sql_mode", "view")

        if not game_gid or not event_id:
            logger.error(f"Missing required params: game_gid={game_gid}, event_id={event_id}")
            return json_error_response("game_gid and event_id are required", status_code=400)

        # 🔍 添加详细日志
        logger.info(f"Generating HQL for game_gid={game_gid}, event_id={event_id}")
        logger.info(f"Fields count: {len(fields)}, Filter conditions: {filter_conditions}")

        # 导入 HQL V2 生成器
        from backend.services.hql.core.generator import HQLGenerator
        from backend.services.hql.adapters.project_adapter import ProjectAdapter

        # 创建 HQL 生成器
        generator = HQLGenerator()
        adapter = ProjectAdapter()

        # 使用 ProjectAdapter 创建 Event 对象
        try:
            event_obj = adapter.event_from_project(game_gid, event_id)
        except ValueError as e:
            logger.error(f"Event not found: {str(e)}")
            return json_error_response(str(e), status_code=404)

        events_data = [event_obj]

        # 转换字段格式（使用 adapter）
        fields_v2 = []
        for idx, field in enumerate(fields):
            try:
                logger.debug(f"Processing field {idx}: {field}")  # 🔍 添加字段级别日志
                field_obj = adapter.field_from_project(field)
                fields_v2.append(field_obj)
            except ValueError as e:
                logger.error(f"Invalid field at index {idx}: {field}, error: {str(e)}")  # 🔍 详细错误信息
                return json_error_response(
                    f"Invalid field at index {idx}: {str(e)}",
                    status_code=400
                )

        # 转换 WHERE 条件格式（使用 adapter）
        where_conditions_v2 = []
        if filter_conditions:
            conditions = filter_conditions.get("conditions", [])
            for idx, cond in enumerate(conditions):
                try:
                    logger.debug(f"Processing condition {idx}: {cond}")  # 🔍 添加条件级别日志
                    condition_obj = adapter.condition_from_project(cond)
                    where_conditions_v2.append(condition_obj)
                except (KeyError, ValueError) as e:
                    logger.error(f"Invalid condition at index {idx}: {cond}, error: {str(e)}")
                    return json_error_response(
                        f"Invalid condition at index {idx}: {str(e)}",
                        status_code=400
                    )

        # 生成 HQL
        hql_result = generator.generate(
            events_data,
            fields_v2,
            where_conditions_v2,
            mode="single",
            sql_mode=sql_mode.upper(),
            include_comments=True
        )

        logger.info(f"HQL generated successfully")
        return json_success_response(data=hql_result, message="HQL preview generated")

    except Exception as e:
        logger.error(f"Error generating HQL preview: {e}", exc_info=True)
        return json_error_response(f"Failed to generate HQL preview: {str(e)}", status_code=500)
```

---

### 修复3: 前端API错误提示优化

#### 文件: `/frontend/src/event-builder/components/HQLPreviewContainer.jsx`

**修改位置**: 第68-74行

```javascript
} catch (err) {
  console.error('[HQLPreviewContainer] Failed to generate HQL:', err);
  setError(err.message);

  // 🔍 显示详细错误信息
  const errorMessage = err.response
    ? `服务器错误: ${err.response.status} - ${err.response.data?.message || err.message}`
    : `网络错误: ${err.message}`;

  setHqlContent(`-- 错误: ${errorMessage}`);
  setIsLoading(false);
}
```

---

## 📊 优化建议

### 1. 防止类型不匹配

#### 建议1.1: 使用类型检查工具

```javascript
// utils/typeHelpers.js
export const ensureString = (value) => {
  if (typeof value === 'string') return value;
  if (value === null || value === undefined) return '';
  return String(value);
};

export const ensureNumber = (value) => {
  if (typeof value === 'number') return value;
  const num = Number(value);
  return isNaN(num) ? 0 : num;
};
```

#### 建议1.2: 在addFieldToCanvas中使用类型检查

```javascript
const addFieldToCanvas = useCallback((fieldType, fieldName, displayName, paramId = null) => {
  setCanvasFields(prev => {
    const newField = {
      id: ensureString(Date.now()),
      fieldType: ensureString(fieldType),
      fieldName: ensureString(fieldName),
      displayName: ensureString(displayName),
      alias: ensureString(fieldName),
      order: prev.length + 1,
      paramId: ensureNumber(paramId),
    };
    return [...prev, newField];
  });
}, []);
```

### 2. 前端数据验证

#### 建议2.1: 在发送API请求前验证字段

```javascript
// utils/apiValidation.js
export const validateFieldForAPI = (field) => {
  const errors = [];

  if (!field.field_name || typeof field.field_name !== 'string') {
    errors.push('field_name must be a non-empty string');
  }

  if (!field.field_type || typeof field.field_type !== 'string') {
    errors.push('field_type must be a non-empty string');
  }

  if (!['base', 'param', 'custom', 'fixed'].includes(field.field_type)) {
    errors.push(`field_type must be one of: base, param, custom, fixed, got: ${field.field_type}`);
  }

  return {
    isValid: errors.length === 0,
    errors
  };
};

// 在HQLPreviewContainer.jsx中使用
const requestData = {
  // ...
  fields: (fields || []).map(f => {
    const fieldData = {
      param_id: f.paramId,
      field_name: f.fieldName,
      field_type: f.fieldType,
      aggregate_func: f.aggregateFunc || '',
      is_primary: f.isPrimary || false,
      alias: f.alias
    };

    // 验证字段
    const validation = validateFieldForAPI(fieldData);
    if (!validation.isValid) {
      console.error('[HQLPreviewContainer] Invalid field:', fieldData, validation.errors);
      throw new Error(`Invalid field: ${validation.errors.join(', ')}`);
    }

    return fieldData;
  }),
  // ...
};
```

### 3. 后端Schema验证

#### 建议3.1: 使用Pydantic进行请求验证

```python
# backend/models/schemas/event_node_builder.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any

class FieldPreviewRequest(BaseModel):
    """HQL预览字段请求"""
    param_id: Optional[int] = None
    field_name: str = Field(..., min_length=1)
    field_type: str = Field(..., regex='^(base|param|custom|fixed)$')
    aggregate_func: Optional[str] = None
    is_primary: bool = False
    alias: Optional[str] = None

    @validator('field_name')
    def field_name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('field_name must not be empty')
        return v.strip()

class HQLPreviewRequest(BaseModel):
    """HQL预览请求"""
    game_gid: int = Field(..., gt=0)
    event_id: int = Field(..., gt=0)
    fields: List[FieldPreviewRequest] = Field(..., min_items=0)
    filter_conditions: Optional[Dict[str, Any]] = None
    sql_mode: str = Field(default='view', regex='^(VIEW|TABLE)$')

    @validator('fields')
    def fields_must_not_be_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError('at least one field is required')
        return v

# 在API中使用
@event_node_builder_bp.route("/api/preview-hql", methods=["POST"])
def preview_hql():
    try:
        # 使用Pydantic验证请求
        request_data = HQLPreviewRequest(**request.get_json())

        # 继续处理...

    except ValidationError as e:
        return json_error_response(f"Validation error: {e}", status_code=400)
    except Exception as e:
        logger.error(f"Error generating HQL preview: {e}", exc_info=True)
        return json_error_response(f"Failed to generate HQL preview: {str(e)}", status_code=500)
```

### 4. 统一类型定义

#### 建议4.1: 使用TypeScript定义Field类型

```typescript
// types/eventBuilder.ts
export interface CanvasField {
  id: string;           // 必须为字符串
  fieldType: 'base' | 'param' | 'custom' | 'fixed';
  fieldName: string;
  displayName: string;
  alias: string;
  order: number;
  paramId?: number;     // 可选，数字类型
}

export interface APIFieldRequest {
  param_id?: number;
  field_name: string;
  field_type: 'base' | 'param' | 'custom' | 'fixed';
  aggregate_func?: string;
  is_primary?: boolean;
  alias?: string;
}

// 类型转换函数
export function canvasFieldToAPIRequest(field: CanvasField): APIFieldRequest {
  return {
    param_id: field.paramId,
    field_name: field.fieldName,
    field_type: field.fieldType,
    aggregate_func: field.aggregateFunc,
    is_primary: field.isPrimary,
    alias: field.alias,
  };
}
```

---

## 🧪 测试验证

### 测试用例1: 验证ID类型

```javascript
// test: ID应为字符串
const field = {
  id: String(Date.now()),
  fieldType: 'param',
  fieldName: 'zone_id',
  displayName: '区服ID',
  alias: 'zone_id',
  order: 1,
  paramId: 123,
};

console.log(typeof field.id);  // 应输出: "string"
```

### 测试用例2: 验证API请求

```javascript
// test: API请求字段格式
const apiRequest = {
  game_gid: 10000147,
  event_id: 1,
  fields: [{
    param_id: 123,
    field_name: 'zone_id',
    field_type: 'param',
    aggregate_func: '',
    is_primary: false,
    alias: 'zone_id',
  }],
  filter_conditions: {},
  sql_mode: 'view',
};

console.log(typeof apiRequest.fields[0].param_id);  // 应输出: "number"
console.log(typeof apiRequest.fields[0].field_name);  // 应输出: "string"
```

### 测试用例3: 端到端测试

1. 在事件节点构建器中选择事件
2. 从参数列表拖拽参数到画布
3. 验证：
   - ✅ 无PropTypes警告
   - ✅ 字段成功添加到画布
   - ✅ HQL预览成功生成
   - ✅ 无API 400错误

---

## 📝 总结

### 根本原因

1. **前端类型不一致**: `useEventNodeBuilder.js` 使用 `Date.now()` 生成数字ID，但 `FieldCanvas.tsx` 期望字符串ID
2. **后端验证不足**: 缺少详细的错误日志和请求验证

### 修复优先级

1. **高优先级**: 修复 `useEventNodeBuilder.js` 中的ID类型（修复1）
2. **中优先级**: 增强后端错误日志（修复2）
3. **低优先级**: 实施类型检查和数据验证（优化建议1-2）

### 预防措施

1. 使用TypeScript定义明确的类型
2. 在API调用前验证数据
3. 使用Pydantic进行后端请求验证
4. 添加详细的错误日志

---

**下一步**: 实施修复1和修复2，然后进行端到端测试验证。
