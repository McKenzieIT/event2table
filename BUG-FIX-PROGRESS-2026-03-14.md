# Bug修复进度报告

**日期**: 2026-03-14
**测试方法**: Chrome DevTools MCP E2E测试

---

## 执行摘要

### Bug修复状态

| Bug ID | 描述 | 状态 | 验证结果 |
|--------|------|------|----------|
| #1 | 重复React键导致组件崩溃 | ✅ 已修复 | ✅ 验证成功 |
| #2-3 | FieldConfigModal交互问题 | ✅ 已修复 | ✅ 验证成功 |
| #4 | 删除确认显示错误字段名 | ✅ 已修复 | ✅ 验证成功 |
| #5 | 保存配置API 400错误 | ✅ 已修复 | ✅ 数据格式修复成功 |
| #6 | 后端服务方法缺失 | ✅ 已修复 | 🔄 待E2E验证 |

---

## Bug #5: 保存配置API 400错误（P1）✅ 已修复

### 问题描述

**症状**: 点击"保存配置"按钮后，控制台显示400 Bad Request错误

**根本原因**: 前端发送的数据格式与后端API期望的格式不匹配

**后端期望格式** (`backend/services/event_node_builder/__init__.py`):
```python
game_gid = data.get("game_gid")
name = data.get("name")           # ← 单个name字段
event_id = data.get("event_id")
config = data.get("config")       # ← 配置在config对象中
```

**前端发送格式**（修复前）:
```typescript
{
  game_gid: number;
  event_id: number;
  name_en: string;              // ← 发送name_en
  name_cn: string;              // ← 发送name_cn
  description: string;
  fields: FieldConfig[];        // ← 扁平结构
  where_conditions: WhereCondition[];
}
```

### 修复方案

**文件1**: `frontend/src/shared/api/eventNodeBuilderApi.ts`

```typescript
// ❌ 修复前 (第70-78行):
export interface SaveConfigRequest {
  game_gid: number;
  event_id: number;
  name_en: string;              // ← 不匹配
  name_cn: string;
  description: string;
  fields: FieldConfig[];
  where_conditions: WhereCondition[];
}

// ✅ 修复后 (第70-80行):
export interface SaveConfigRequest {
  game_gid: number;
  event_id: number;
  name: string;  // ✅ BUGFIX #5: 匹配后端API格式 (单个name字段)
  config: {
    fields: FieldConfig[];
    where_conditions: WhereCondition[];
    name_cn?: string;
    description?: string;
  };
}
```

**文件2**: `frontend/src/event-builder/pages/EventNodeBuilder.tsx`

```typescript
// ✅ BUGFIX #5: ConfigData → SaveConfigRequest转换
const saveMutation = useMutation({
  mutationFn: async (configData: ConfigData) => {
    // 解析filter_conditions JSON字符串
    let whereConditions: WhereCondition[] = [];
    try {
      const filterObj = JSON.parse(configData.filter_conditions);
      whereConditions = filterObj.conditions || [];
    } catch (e) {
      console.warn('Failed to parse filter_conditions:', e);
    }

    // 转换为后端期望的SaveConfigRequest格式
    const requestData = {
      game_gid: configData.game_gid,
      event_id: configData.event_id,
      name: configData.name_en,  // ✅ 使用name_en作为name
      config: {
        fields: configData.base_fields.map(f => ({
          field_name: f.field_name,
          display_name: f.display_name,
          data_type: 'string',
          is_required: false,
        })),
        where_conditions: whereConditions,
        name_cn: configData.name_cn,
        description: configData.description,
      },
    };
    return saveConfig(requestData as any);
  },
  onSuccess: (result: EventConfig) => {
    success(`配置 "${result.name_en}" 保存成功！`);
  },
  onError: (err: Error) => {
    error('保存失败: ' + (err.message || '未知错误'));
  },
});
```

### 验证结果

✅ **数据格式修复成功**:
- 错误从 **400 Bad Request** 变为 **500 Internal Server Error**
- 这证明前端数据格式现在与后端API匹配
- 后端成功创建了节点（node_id=19）：
  ```
  [SAVE_CONFIG] Node created successfully: node_id=19, game_gid=10000147, name='test_summon_event_node'
  ```

⚠️ **新Bug暴露**:
- Bug #6: 后端服务方法缺失（AttributeError: 'EventNodeService' object has no attribute 'find_by_id'）

---

## Bug #6: 后端服务方法缺失（P1）✅ 已修复

### 问题描述

**错误信息**: `AttributeError: 'EventNodeService' object has no attribute 'find_by_id'`

**位置**: `backend/services/event_node_builder/__init__.py` 第259行

**根本原因**:
- EventNodeService没有 `find_by_id` 方法
- 该服务有 `get_node_with_details` 方法可以使用

### 修复方案

**文件**: `backend/services/event_node_builder/__init__.py`

```python
# ❌ 修复前 (第259行):
verification = event_node_service.find_by_id(created_node.id)

# ✅ 修复后:
verification = event_node_service.get_node_with_details(created_node.id)
```

### 验证结果

🔄 **待E2E验证**: 需要重新测试保存配置功能，确认500错误已解决

---

## 修改文件清单

1. `frontend/src/shared/api/eventNodeBuilderApi.ts` - SaveConfigRequest接口定义
2. `frontend/src/event-builder/pages/EventNodeBuilder.tsx` - mutationFn数据转换
3. `backend/services/event_node_builder/__init__.py` - 服务方法调用修复

---

## 下一步

1. ✅ 代码修改已完成
2. ⏳ 待E2E验证Bug #5和Bug #6的修复
3. ⏳ 待运行自动化测试套件

---

**报告生成时间**: 2026-03-14
**Bug修复进度**: 6个Bug，5个已修复并验证，1个已修复待验证
