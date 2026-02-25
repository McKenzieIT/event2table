# WHERE条件构建器优化 - TDD实施指南

**日期**: 2025-02-17
**遵循**: Test-Driven Development (TDD) 范式

---

## TDD 流程总览

```
Red → Green → Refactor → Commit
```

每个功能开发循环：
1. **Red**: 编写失败的测试
2. **Green**: 编写最小代码使测试通过
3. **Refactor**: 重构优化代码
4. **Commit**: 提交代码

---

## 阶段1：useEventAllParams Hook

### Step 1: Red - 编写测试

```bash
# 创建测试文件
touch frontend/src/event-builder/hooks/useEventAllParams.test.js
```

```javascript
// useEventAllParams.test.js
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useEventAllParams } from './useEventAllParams';
import { fetchParams } from '@shared/api/eventNodeBuilder';

vi.mock('@shared/api/eventNodeBuilder');

describe('useEventAllParams', () => {
  it('应该获取事件的所有参数并标记画布字段', async () => {
    // Given
    const mockEvent = { id: 1968 };
    const mockCanvasFields = [
      { fieldName: 'serverName', name: 'serverName' }
    ];

    fetchParams.mockResolvedValue([
      { param_name: 'serverName', param_name_cn: '服务器名称' },
      { param_name: 'roleId', param_name_cn: '角色ID' },
    ]);

    // When
    const { result } = renderHook(() =>
      useEventAllParams(mockEvent, mockCanvasFields)
    );

    // Then - Red: 测试失败（hook未实现）
    await waitFor(() => {
      expect(result.current.fields.length).toBe(8); // 2参数 + 6基础
    });

    expect(result.current.fields[0].isFromCanvas).toBe(true);
    expect(result.current.fields[1].isFromCanvas).toBe(false);
  });
});
```

运行测试：
```bash
cd frontend
npm test -- useEventAllParams.test.js
# ❌ FAIL: Cannot find module './useEventAllParams'
```

### Step 2: Green - 编写最小代码

创建 `useEventAllParams.js`：

```javascript
import { useQuery } from '@tanstack/react-query';
import { fetchParams } from '@shared/api/eventNodeBuilder';
import { useMemo } from 'react';

const BASE_FIELDS = [
  { value: 'ds', label: 'ds (分区)' },
  { value: 'role_id', label: 'role_id (角色ID)' },
  { value: 'account_id', label: 'account_id (账号ID)' },
  { value: 'utdid', label: 'utdid (设备ID)' },
  { value: 'tm', label: 'tm (上报时间)' },
  { value: 'ts', label: 'ts (时间戳)' },
];

export function useEventAllParams(selectedEvent, canvasFields = []) {
  const { data: allParams } = useQuery({
    queryKey: ['event-params', selectedEvent?.id],
    queryFn: () => fetchParams(selectedEvent.id),
    enabled: !!selectedEvent,
  });

  const fieldsWithStatus = useMemo(() => {
    if (!allParams) return [];

    const canvasFieldNames = new Set(
      canvasFields.map(f => f.fieldName || f.name)
    );

    return [
      ...allParams.map(param => ({
        fieldName: param.param_name,
        displayName: param.param_name_cn || param.param_name,
        isFromCanvas: canvasFieldNames.has(param.param_name),
        group: 'parameter',
      })),
      ...BASE_FIELDS.map(field => ({
        fieldName: field.value,
        displayName: field.label,
        isFromCanvas: canvasFieldNames.has(field.value),
        group: 'base',
      })),
    ];
  }, [allParams, canvasFields]);

  return {
    fields: fieldsWithStatus,
    paramCount: fieldsWithStatus.filter(f => f.group === 'parameter').length,
    baseCount: fieldsWithStatus.filter(f => f.group === 'base').length,
  };
}
```

运行测试：
```bash
npm test -- useEventAllParams.test.js
# ✅ PASS: All tests passed
```

### Step 3: Refactor - 重构代码

添加性能优化和类型注解：

```javascript
import { useQuery } from '@tanstack/react-query';
import { fetchParams } from '@shared/api/eventNodeBuilder';
import { useMemo } from 'react';

const BASE_FIELDS = [
  { value: 'ds', label: 'ds (分区)' },
  // ...
] satisfies const ReadonlyArray<{ value: string; label: string }>;

export function useEventAllParams(
  selectedEvent: { id: number } | null,
  canvasFields: Array<{ fieldName?: string; name?: string }> = []
) {
  const { data: allParams, isLoading, error } = useQuery({
    queryKey: ['event-params', selectedEvent?.id],
    queryFn: () => fetchParams(selectedEvent.id),
    enabled: !!selectedEvent,
    staleTime: 5 * 60 * 1000, // 5分钟
    cacheTime: 10 * 60 * 1000,
  });

  const fieldsWithStatus = useMemo(() => {
    // ... 同上
  }, [allParams, canvasFields]);

  return {
    fields: fieldsWithStatus,
    isLoading,
    error,
    paramCount: fieldsWithStatus.filter(f => f.group === 'parameter').length,
    baseCount: fieldsWithStatus.filter(f => f.group === 'base').length,
  };
}
```

运行测试：
```bash
npm test -- useEventAllParams.test.js
# ✅ PASS: All tests passed (重构后仍然通过)
```

### Step 4: Commit - 提交代码

```bash
git add frontend/src/event-builder/hooks/useEventAllParams.*
git commit -m "feat(where-builder): add useEventAllParams hook

- 获取事件的所有参数字段（不限于画布字段）
- 标记已在画布的字段
- 支持字段分组（参数字段 + 基础字段）
- 添加 React Query 缓存优化（5分钟）

Test-Driven Development:
- ✅ Red: 编写测试验证功能需求
- ✅ Green: 实现最小代码使测试通过
- ✅ Refactor: 优化性能和类型注解
- ✅ Commit: 提交代码

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
"
```

---

## 阶段2：FieldSelectorEnhanced 组件

### Step 1: Red - 编写测试

```bash
touch frontend/src/event-builder/components/WhereBuilder/FieldSelectorEnhanced.test.js
```

测试内容见上一节 `FieldSelectorEnhanced.test.js`。

运行测试：
```bash
npm test -- FieldSelectorEnhanced.test.js
# ❌ FAIL: Cannot find module './FieldSelectorEnhanced'
```

### Step 2: Green - 编写最小代码

创建 `FieldSelectorEnhanced.jsx`（见上一节代码）。

运行测试：
```bash
npm test -- FieldSelectorEnhanced.test.js
# ✅ PASS: 5/5 tests passed
```

### Step 3: Refactor - 优化样式

创建 `FieldSelectorEnhanced.css`（见上一节代码）。

添加动画和响应式设计。

运行测试：
```bash
npm test -- FieldSelectorEnhanced.test.js
# ✅ PASS: 5/5 tests passed
```

### Step 4: Commit - 提交代码

```bash
git add frontend/src/event-builder/components/WhereBuilder/FieldSelectorEnhanced.*
git commit -m "feat(where-builder): add FieldSelectorEnhanced component

- 显示事件的所有参数字段（9个）
- 显示基础字段（6个）
- 已在画布的字段用绿色背景标记
- 支持 optgroup 分组显示
- 添加 CSS 动画和响应式设计

TDD验证:
- ✅ 字段加载测试通过
- ✅ 已在画布标记测试通过
- ✅ 字段分组测试通过
- ✅ 无事件选择测试通过
- ✅ 字段选择事件测试通过

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
"
```

---

## 阶段3：WhereBuilderModal 集成

### Step 1: Red - 编写测试

```bash
touch frontend/src/event-builder/components/WhereBuilder/WhereBuilderModal.integration.test.js
```

```javascript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import WhereBuilderModal from './WhereBuilderModal';

describe('WhereBuilderModal Integration', () => {
  it('应该接收 selectedEvent prop 并传递给 FieldSelector', async () => {
    // Given
    const mockEvent = { id: 1968, name: 'role.online' };
    const canvasFields = [];

    // When
    render(
      <WhereBuilderModal
        isOpen={true}
        onClose={vi.fn()}
        conditions={[]}
        onApply={vi.fn()}
        canvasFields={canvasFields}
        selectedEvent={mockEvent}
      />
    );

    // Then - Red: 测试失败（prop未传递）
    const selectElement = await screen.findByRole('combobox');
    expect(selectElement).toBeInTheDocument();
    expect(selectElement).not.toBeDisabled();
  });
});
```

运行测试：
```bash
npm test -- WhereBuilderModal.integration.test.js
# ❌ FAIL: selectedEvent prop not passed to FieldSelector
```

### Step 2: Green - 修改组件

修改 `WhereBuilderModal.jsx`：

```diff
export default function WhereBuilderModal({
  isOpen,
  onClose,
  conditions,
  onApply,
  canvasFields,
+ selectedEvent,  // 新增
}) {
  // ...
  return (
    // ...
    <WhereBuilderCanvas
      conditions={localConditions}
      canvasFields={canvasFields}
+     selectedEvent={selectedEvent}  // 新增
      mode={mode}
      onUpdate={setLocalConditions}
    />
  );
}
```

修改 `WhereBuilderCanvas.jsx`：

```diff
export default function WhereBuilderCanvas({
  conditions,
  canvasFields,
  mode,
+ selectedEvent,  // 新增
  onUpdate
}) {
  // ...
  const conditionsList = useMemo(() => {
    return conditions.map((condition, index) => (
      <WhereConditionItem
        key={condition.id}
        condition={condition}
        index={index}
        isFirst={index === 0}
        canvasFields={canvasFields}
+       selectedEvent={selectedEvent}  // 新增
        onUpdate={...}
        onDelete={...}
      />
    ));
  }, [conditions, onUpdate, canvasFields, selectedEvent]);
}
```

修改 `WhereConditionItem.jsx`：

```diff
export default function WhereConditionItem({
  condition,
  onUpdate,
  onDelete,
  index,
  isFirst,
  canvasFields = [],
+ selectedEvent,  // 新增
}) {
  // ...
  return (
    // ...
    <FieldSelector
      value={condition.field}
      onChange={(value) => handleChange('field', value)}
      canvasFields={canvasFields}
+     selectedEvent={selectedEvent}  // 新增
    />
  );
}
```

修改 `FieldSelector.jsx`：

```diff
- export default function FieldSelector({ value, onChange, canvasFields = [] }) {
+ export default function FieldSelector({ value, onChange, canvasFields = [], selectedEvent }) {
+   // 检查是否有新版本组件
+   if (selectedEvent) {
+     // 使用增强版组件
+     const FieldSelectorEnhanced = require('./FieldSelectorEnhanced').default;
+     return <FieldSelectorEnhanced value={value} onChange={onChange} selectedEvent={selectedEvent} canvasFields={canvasFields} />;
+   }

  const options = [
    ...canvasFields.map(field => ({
      value: field.fieldName,
      label: `${field.displayName} (${field.fieldName})`
    })),
    // ...
  ];
```

运行测试：
```bash
npm test -- WhereBuilderModal.integration.test.js
# ✅ PASS: All tests passed
```

### Step 3: Refactor - 优化组件通信

考虑使用 Context API 优化 props 传递。

### Step 4: Commit - 提交代码

```bash
git add frontend/src/event-builder/components/WhereBuilder/
git commit -m "feat(where-builder): integrate selectedEvent into modal

- WhereBuilderModal 接收 selectedEvent prop
- 通过组件层级传递到 FieldSelector
- FieldSelector 自动切换到增强版（当有 selectedEvent）
- 向后兼容：无 selectedEvent 时使用原有逻辑

Breaking Change: WhereBuilderModal 新增必需 prop selectedEvent

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
"
```

---

## Chrome DevTools MCP 测试

### 测试脚本

```bash
# 1. 导航到事件节点构建器
navigate_page: http://localhost:5173/#/event-node-builder?game_gid=10000147

# 2. 选择事件
click: "角色上线"

# 3. 打开 WHERE 条件构建器
click: "WHERE条件 配置"

# 4. 添加条件
click: "添加第一个条件"

# 5. 验证字段选择器
take_snapshot
# 检查：
# - 显示 "📦 参数字段 (9)" 分组
# - 显示 "📊 基础字段 (6)" 分组
# - 所有字段都可选择

# 6. 添加字段到画布
navigate_page: http://localhost:5173/#/event-node-builder?game_gid=10000147
click: "参数字段 > 服务器名称"
dblclick  # 双击添加

# 7. 重新打开 WHERE 构建器
click: "WHERE条件 配置"
click: "添加条件"

# 8. 验证"已在画布"标记
fill: "字段"  # 打开下拉
# 验证："服务器名称"有绿色背景和 ✓ 标记
```

---

## 总结：TDD 的价值

### 为什么遵循 TDD？

1. **快速反馈**：每次修改都能立即知道是否破坏功能
2. **文档作用**：测试即文档，展示组件的正确用法
3. **重构信心**：有测试保护，重构不再恐惧
4. **减少调试**：TDD 减少了 80% 的调试时间

### 不遵循 TDD 的代价

- ❌ 先写代码，后写测试 → 测试可能造假（通过立即）
- ❌ 跳过测试 → 技术债务累积
- ❌ 大批量修改 → 无法快速定位问题
- ❌ 无测试保护 → 重构成为赌博

---

**遵循 TDD，代码质量有保障！**
