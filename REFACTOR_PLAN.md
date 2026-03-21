# 组件文件拆分重构计划

## 目标
将6个超标组件文件拆分为更小的模块，确保每个文件 < 500 行

## 当前状态
- Table.tsx: 854 行
- FieldCanvas.tsx: 795 行
- CanvasFlow.tsx: 648 行
- HQLResultModal.tsx: 576 行
- HQLPreviewModal.tsx: 540 行
- DatePicker.tsx: 519 行

## 拆分策略

### 1. Table.tsx (854行) → 目标 < 400行
**已创建文件:**
- useTableVirtualScroll.ts - 虚拟滚动逻辑
- useTableHandlers.ts - 事件处理器
- useTableRender.ts - 渲染辅助函数

**剩余操作:**
- 更新 Table.tsx 使用新的 hooks
- 提取 TableBody 和 TableHeader 渲染逻辑

### 2. FieldCanvas.tsx (795行) → 目标 < 400行
**拆分计划:**
- SortableFieldItem.tsx - 可排序字段项组件 (~200行)
- DropZone.tsx - 拖放区域组件 (~100行)
- EdgeToolbar.tsx - 边缘工具栏组件 (~150行)
- FieldContextMenu.tsx - 右键菜单组件 (~100行)
- CanvasStatsDisplay.tsx - 统计显示组件 (~80行)
- useFieldCanvas.ts - Canvas 逻辑 hooks (~150行)

### 3. CanvasFlow.tsx (648行) → 目标 < 350行
**拆分计划:**
- types.ts - 类型定义 (~100行)
- useCanvasFlow.ts - 主要逻辑 hooks (~200行)
- CanvasFlowToolbar.tsx - 工具栏组件 (~100行)
- CanvasFlow.tsx - 主组件 (~250行)

### 4. HQLResultModal.tsx (576行) → 目标 < 300行
**拆分计划:**
- hqlUtils.ts - HQL 工具函数 (~100行)
- HQLPreview.tsx - HQL 预览组件 (~150行)
- HQLEditor.tsx - HQL 编辑器组件 (~150行)
- HQLResultModal.tsx - 主组件 (~200行)

### 5. HQLPreviewModal.tsx (540行) → 目标 < 300行
**拆分计划:**
- hqlGenerators.ts - HQL 生成器函数 (~150行)
- TabSwitcher.tsx - Tab 切换组件 (~80行)
- HQLPreviewModal.tsx - 主组件 (~250行)

### 6. DatePicker.tsx (519行) → 目标 < 300行
**拆分计划:**
- dateUtils.ts - 日期工具函数 (~80行)
- CalendarGrid.tsx - 日历网格组件 (~200行)
- DatePicker.tsx - 主组件 (~200行)

## 执行顺序
1. ✅ 创建 Table hooks (已完成)
2. ⏳ 更新 Table.tsx
3. ⏳ 拆分 FieldCanvas.tsx
4. ⏳ 拆分 CanvasFlow.tsx
5. ⏳ 拆分 HQLResultModal.tsx
6. ⏳ 拆分 HQLPreviewModal.tsx
7. ⏳ 拆分 DatePicker.tsx
8. ⏳ 运行测试验证
9. ⏳ 提交更改
