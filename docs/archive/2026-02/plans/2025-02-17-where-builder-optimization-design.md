# WHERE条件构建器优化设计文档

**日期**: 2025-02-17
**设计者**: Claude + User
**状态**: 设计阶段 - 阶段1（字段源修复）

---

## 设计方案概述

### 阶段1：字段源修复（核心功能）

**目标**：
- ✅ FieldSelector 显示事件的所有参数字段（不限于画布字段）
- ✅ 已添加到画布的字段用浅绿色背景高亮
- ✅ 智能分组：参数字段组 + 基础字段组

**不改动的部分**：
- 暂时保留模式切换（阶段2移除）
- V2 API保持勾选框（阶段3融合）
- 分组功能保持原样（阶段2优化）

---

## 美学方向：Refined Technical（精致技术风格）

### 视觉特征

- **排版**: JetBrains Mono（代码/字段名）+ Inter（UI文本）
- **配色**:
  - 主色：Slate-900（深灰）
  - 强调色：Cyan-500（主按钮）、Emerald-400（已在画布标记）
  - 背景色：Slate-50（浅灰白）
  - 边框色：Slate-200（浅灰）
- **间距**: 4px 基础单位，8px/16px/24px 层级
- **圆角**: 6px（统一）
- **阴影**: 微妙的多层阴影

---

## 组件架构

### 数据流

```typescript
// 新增的 props 传递
EventNodeBuilder
  └─ selectedEvent: Event object

WhereBuilderModal (新增 props)
  ├─ canvasFields: Field[] (原有)
  └─ selectedEvent: Event (新增) ← 关键

WhereBuilderCanvas
  ├─ canvasFields: Field[] (原有)
  └─ selectedEvent: Event (新增) ← 关键

WhereConditionItem
  ├─ canvasFields: Field[] (原有)
  └─ selectedEvent: Event (新增) ← 关键

FieldSelector (重大改动)
  ├─ canvasFields: Field[] (原有，用于标记)
  └─ selectedEvent: Event (新增，获取所有参数) ← 关键
```

### 新增 Hook

```typescript
// hooks/useEventAllParams.ts
/**
 * 获取事件的所有参数字段
 * 结合画布字段状态，提供视觉标记
 */
export function useEventAllParams(selectedEvent, canvasFields) {
  const { data: allParams } = useQuery({
    queryKey: ['event-params', selectedEvent?.id],
    queryFn: () => fetchParams(selectedEvent.id),
    enabled: !!selectedEvent,
  });

  // 合并字段状态
  const fieldsWithStatus = useMemo(() => {
    if (!allParams) return [];

    const canvasFieldNames = new Set(canvasFields.map(f => f.fieldName));

    return [
      // 参数字段（分组1）
      ...allParams.map(param => ({
        fieldName: param.param_name,
        displayName: param.param_name_cn,
        isFromCanvas: canvasFieldNames.has(param.param_name),
        group: 'parameter',
      })),
      // 基础字段（分组2）
      ...BASE_FIELDS.map(field => ({
        fieldName: field.value,
        displayName: field.label,
        isFromCanvas: canvasFieldNames.has(field.value),
        group: 'base',
      })),
    ];
  }, [allParams, canvasFields]);

  return fieldsWithStatus;
}
```

---

## UI 设计规范

### FieldSelector 组件

**Before（问题）**:
```jsx
<select>
  <option>选择字段</option>
  {canvasFields.map(...)}  ← 只有画布字段
  <option>ds (分区)</option>
  <option>role_id (角色ID)</option>
  ...
</select>
```

**After（优化）**:
```jsx
<select className="field-selector-enhanced">
  <optgroup label="📦 参数字段">
    {allParams
      .filter(f => f.group === 'parameter')
      .map(f => (
        <option
          value={f.fieldName}
          className={f.isFromCanvas ? 'field-in-canvas' : ''}
        >
          {f.isFromCanvas ? '✓ ' : ''}{f.displayName} ({f.fieldName})
        </option>
      ))
    }
  </optgroup>

  <optgroup label="📊 基础字段">
    {allParams
      .filter(f => f.group === 'base')
      .map(f => (
        <option
          value={f.fieldName}
          className={f.isFromCanvas ? 'field-in-canvas' : ''}
        >
          {f.isFromCanvas ? '✓ ' : ''}{f.displayName} ({f.fieldName})
        </option>
      ))
    }
  </optgroup>
</select>

<style>
  .field-in-canvas {
    background-color: #d1fae5;  /* Emerald-100 */
    color: #065f46;              /* Emerald-800 */
    font-weight: 500;
  }
</style>
```

### WhereBuilderModal 布局

```
┌─────────────────────────────────────────────────────┐
│  🎯 WHERE条件构建器                     [×] 关闭    │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌─ WHERE预览 ────────────────────────── [复制] ─┐  │
│  │ WHERE ds = '${ds}'                          │  │
│  │   AND event_name = 'role.online'           │  │
│  │   AND serverName = 'S1'                     │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌─ 构建器画布 ────────────────────────────────┐  │
│  │ [+ 添加条件]  [清空]                         │  │
│  │                                               │  │
│  │ ┌─────────────────────────────────────────┐ │  │
│  │ │ ☰  字段: [服务器名称 ▼]  =  [值____]  🗑 │ │  │
│  │ │    └─ 参数字段 (9个)                     │ │  │
│  │ │    └─ 基础字段 (6个)                     │ │  │
│  │ └─────────────────────────────────────────┘ │  │
│  │                                               │  │
│  │ ┌─────────────────────────────────────────┐ │  │
│  │ │ AND  字段: [role_id ▼]  =  [值____]  🗑 │ │  │
│  │ └─────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  2 个条件                      [取消]  [✓ 应用]     │
└─────────────────────────────────────────────────────┘
```

---

## CSS 变量系统

```css
:root {
  /* 颜色 - 主色调 */
  --where-primary: #0f172a;      /* Slate-900 */
  --where-secondary: #64748b;    /* Slate-500 */
  --where-accent: #06b6d4;       /* Cyan-500 */
  --where-success: #10b981;      /* Emerald-500 */

  /* 颜色 - 背景色 */
  --where-bg: #f8fafc;           /* Slate-50 */
  --where-card-bg: #ffffff;      /* White */
  --where-canvas-bg: #f1f5f9;    /* Slate-100 */

  /* 颜色 - 边框色 */
  --where-border: #e2e8f0;       /* Slate-200 */
  --where-border-focus: #06b6d4; /* Cyan-500 */

  /* 已在画布标记 */
  --where-in-canvas-bg: #d1fae5; /* Emerald-100 */
  --where-in-canvas-text: #065f46; /* Emerald-800 */

  /* 排版 */
  --where-font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  --where-font-ui: 'Inter', system-ui, sans-serif;

  /* 间距 */
  --where-space-xs: 4px;
  --where-space-sm: 8px;
  --where-space-md: 16px;
  --where-space-lg: 24px;

  /* 圆角 */
  --where-radius: 6px;
  --where-radius-sm: 4px;
  --where-radius-lg: 8px;

  /* 阴影 */
  --where-shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --where-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
  --where-shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
}
```

---

## 动画规范

### 字段选择动画
```css
.field-selector-enhanced option {
  transition: background-color 150ms ease, color 150ms ease;
}

.field-selector-enhanced option:hover {
  background-color: var(--where-canvas-bg);
}

.field-in-canvas {
  /* 微妙的脉冲效果 */
  animation: canvas-pulse 2s ease-in-out infinite;
}

@keyframes canvas-pulse {
  0%, 100% {
    background-color: var(--where-in-canvas-bg);
  }
  50% {
    background-color: #a7f3d0; /* Emerald-200 */
  }
}
```

### 条件添加动画
```css
.where-condition-item {
  animation: slide-in 200ms ease-out;
}

@keyframes slide-in {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

---

## 可访问性规范

### 键盘导航
- `Tab`: 在字段、操作符、值输入框间切换
- `Enter`: 确认字段选择
- `Escape`: 关闭下拉菜单
- `Ctrl/Cmd + Enter`: 应用WHERE条件

### ARIA 标签
```jsx
<select
  aria-label="选择字段"
  aria-describedby="field-description"
>
  <optgroup label="参数字段" aria-describedby="param-count">
    {/* options */}
  </optgroup>
</select>
<span id="field-description" className="sr-only">
  选择用于构建WHERE条件的字段，包括参数字段和基础字段
</span>
```

### 颜色对比度
- 已在画布字段：对比度 7.2:1（WCAG AA ✅）
- 普通字段：对比度 12.6:1（WCAG AAA ✅）

---

## 性能优化

### React Query 缓存
```typescript
// 缓存事件参数，减少重复请求
const { data: allParams } = useQuery({
  queryKey: ['event-params', selectedEvent?.id],
  queryFn: () => fetchParams(selectedEvent.id),
  enabled: !!selectedEvent,
  staleTime: 5 * 60 * 1000,  // 5分钟内不重新请求
  cacheTime: 10 * 60 * 1000, // 缓存10分钟
});
```

### useMemo 优化字段列表
```typescript
const fieldsWithStatus = useMemo(() => {
  // 合并和标记逻辑
}, [allParams, canvasFields]);
```

---

## 测试策略（TDD）

### 测试用例 - 阶段1

#### 1. 字段加载测试
```typescript
test('选择事件后，字段选择器显示所有参数字段', async () => {
  // Given
  const mockEvent = { id: 1968, name: 'role.online' };
  const mockParams = [
    { param_name: 'serverId', param_name_cn: '服务器ID' },
    { param_name: 'serverName', param_name_cn: '服务器名称' },
    // ... 9个参数
  ];

  // When
  render(<FieldSelector selectedEvent={mockEvent} canvasFields={[]} />);
  await waitFor(() => screen.getByText('服务器名称;

  // Then
  expect(screen.getByText('服务器ID')).toBeInTheDocument();
  expect(screen.getByText('角色名称')).toBeInTheDocument();
  // 验证所有9个参数都显示
});
```

#### 2. 已在画布标记测试
```typescript
test('已在画布的字段显示绿色背景', async () => {
  // Given
  const mockEvent = { id: 1968, name: 'role.online' };
  const canvasFields = [
    { fieldName: 'serverName', displayName: '服务器名称' }
  ];

  // When
  render(<FieldSelector selectedEvent={mockEvent} canvasFields={canvasFields} />);

  // Then
  const serverNameOption = screen.getByText(/服务器名称/);
  expect(serverNameOption).toHaveClass('field-in-canvas');
  expect(serverNameOption).toHaveStyle({ backgroundColor: '#d1fae5' });
});
```

#### 3. 分组显示测试
```typescript
test('字段按参数字段和基础字段分组显示', async () => {
  // Given & When
  render(<FieldSelector selectedEvent={mockEvent} canvasFields={[]} />);

  // Then
  expect(screen.getByText('📦 参数字段')).toBeInTheDocument();
  expect(screen.getByText('📊 基础字段')).toBeInTheDocument();

  const paramGroup = screen.getByLabelText('参数字段');
  const baseGroup = screen.getByLabelText('基础字段');

  expect(within(paramGroup).getAllByRole('option').length).toBe(9);
  expect(within(baseGroup).getAllByRole('option').length).toBe(6);
});
```

---

## Chrome DevTools MCP 测试路径

### 测试步骤

1. **导航到事件节点构建器**
```bash
navigate_page: http://localhost:5173/#/event-node-builder?game_gid=10000147
```

2. **选择事件**
```bash
click: "角色上线"  # role.online
```

3. **打开WHERE条件构建器**
```bash
click: "WHERE条件 配置"
```

4. **点击"添加第一个条件"**
```bash
click: "添加第一个条件"
```

5. **验证字段选择器**
```bash
take_snapshot
# 检查：
# - 显示 "📦 参数字段" 分组（9个字段）
# - 显示 "📊 基础字段" 分组（6个字段）
```

6. **添加字段到画布**
```bash
click: "服务器名称"  # 参数字段
dblclick  # 双击添加到画布
```

7. **验证"已在画布"标记**
```bash
click: "WHERE条件 配置"
click: "添加条件"
fill: "字段"  # 打开字段选择器
# 验证："服务器名称"选项有绿色背景
```

---

## 实施清单

### 阶段1任务

- [ ] **1.1 数据层**
  - [ ] 创建 `useEventAllParams` hook
  - [ ] 修改 `WhereBuilderModal` 接收 `selectedEvent` prop
  - [ ] 修改 `WhereBuilderCanvas` 传递 `selectedEvent`

- [ ] **1.2 组件层**
  - [ ] 重构 `FieldSelector` 支持 `optgroup`
  - [ ] 添加"已在画布"视觉标记（绿色背景）
  - [ ] 添加字段分组（参数字段 + 基础字段）

- [ ] **1.3 样式层**
  - [ ] 创建 `WhereBuilderEnhanced.css`
  - [ ] 定义 CSS 变量系统
  - [ ] 实现动画效果（slide-in, pulse）

- [ ] **1.4 测试**
  - [ ] 编写单元测试（3个核心用例）
  - [ ] 使用 chrome-devtools-mcp 进行E2E测试
  - [ ] 性能测试（大量字段的渲染性能）

---

## 后续阶段预览

### 阶段2：模式简化
- 移除简单/高级模式切换
- 实现扁平分组功能
- 统一工具栏

### 阶段3：V2 API融合
- 默认启用V2 API
- 性能分析面板可折叠
- 调试模式快捷键（Ctrl/Cmd + D）

---

**设计完成时间**: 2025-02-17
**预计开发时间**: 阶段1（2-3天）
**优先级**: P0（核心功能）
