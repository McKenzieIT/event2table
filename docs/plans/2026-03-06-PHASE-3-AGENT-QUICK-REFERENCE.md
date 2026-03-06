# Phase 3 Agent Quick Reference Guide

**日期**: 2026-03-06
**任务**: Phase 3 React性能优化 - Agent快速参考

---

## 🎯 Agent任务清单

### Agent 9: P0 表单输入组件（8个）

**工作目录**: `frontend/src/shared/ui/`
**预估时间**: 45分钟

**优化组件**:
1. ✅ `TextArea/TextArea.tsx`
2. ✅ `Select/Select.tsx`
3. ✅ `Checkbox/Checkbox.tsx`
4. ✅ `Switch/Switch.tsx`
5. ✅ `Radio/Radio.tsx`
6. ✅ `SearchInput/SearchInput.tsx`
7. ✅ `Pagination/Pagination.tsx`
8. ✅ `Card/Card.tsx`

**优化策略**:
```typescript
// 1. 使用 useCallback 稳定事件处理器
const handleChange = useCallback((value: string) => {
  onChange?.(value);
}, [onChange]);

// 2. 使用 useMemo 缓存CSS类名
const inputClass = useMemo(() => {
  return [
    'cyber-input',
    disabled && 'cyber-input--disabled',
    error && 'cyber-input--error'
  ].filter(Boolean).join(' ');
}, [disabled, error]);

// 3. 使用 React.memo + custom comparison
const MemoizedComponent = React.memo(Component, (prevProps, nextProps) => {
  return (
    prevProps.value === nextProps.value &&
    prevProps.disabled === nextProps.disabled &&
    prevProps.error === nextProps.error
  );
});
```

**验证步骤**:
```bash
# 1. TypeScript类型检查
npx tsc --noEmit

# 2. ESLint检查
npm run lint

# 3. 单元测试
npm run test:unit -- TextArea.test.tsx
npm run test:unit -- Select.test.tsx

# 4. 本地测试
npm run dev
# 访问 http://localhost:5173
# 测试表单输入组件
```

---

### Agent 10: P0 模态框组件（5个）

**工作目录**: `frontend/src/shared/ui/`
**预估时间**: 40分钟

**优化组件**:
1. ✅ `BaseModal/BaseModal.tsx`
2. ✅ `ConfirmDialog/ConfirmDialog.tsx`
3. ✅ `Toast/Toast.tsx`
4. ✅ `CanvasErrorBoundary.tsx`
5. ✅ `ErrorBoundary.tsx`

**优化策略**:
```typescript
// 1. 使用 useCallback 稳定关闭回调
const handleClose = useCallback(() => {
  onClose?.();
}, [onClose]);

// 2. useEffect 添加键盘监听
useEffect(() => {
  if (isOpen) {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') handleClose();
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }
}, [isOpen, handleClose]);

// 3. 使用 useMemo 缓存动画类
const modalClass = useMemo(() => {
  return [
    'modal',
    isOpen ? 'modal--open' : 'modal--closed'
  ].join(' ');
}, [isOpen]);

// 4. 条件渲染（不渲染hidden模态框）
if (!isOpen && !mountOnShow) return null;

// 5. 使用 React.memo
const MemoizedModal = React.memo(Modal, (prevProps, nextProps) => {
  return prevProps.isOpen === nextProps.isOpen;
});
```

**验证步骤**:
```bash
# 1. TypeScript类型检查
npx tsc --noEmit

# 2. ESLint检查
npm run lint

# 3. 单元测试
npm run test:unit -- ConfirmDialog.test.tsx
npm run test:unit -- Toast.test.tsx

# 4. 本地测试
npm run dev
# 访问 http://localhost:5173
# 测试模态框组件
```

---

### Agent 11: P0 Canvas核心组件（11个）

**工作目录**: `frontend/src/features/canvas/`
**预估时间**: 60分钟

**优化组件**:
- **P0**:
  1. ✅ `CanvasFlow.tsx` (644行)
  2. ✅ `PropertiesPanel.tsx` (466行)
  3. ✅ `Toolbar.tsx` (296行)
- **P1**:
  4. ✅ `NodeSelector.tsx` (192行)
  5. ✅ `JoinConfigModal.tsx` (265行)
  6. ✅ `DataPreviewModal.tsx` (277行)
  7. ✅ `NodeDetailModal.tsx` (152行)
  8. ✅ `ConnectionPromptModal.tsx` (212行)
  9. ✅ `nodes/EventNode.tsx`
  10. ✅ `nodes/JoinNode.tsx`
  11. ✅ `nodes/UnionAllNode.tsx`
  12. ✅ `nodes/OutputNode.tsx`

**优化策略**:
```typescript
// CanvasFlow.tsx 优化示例
const CanvasFlow: React.FC<CanvasFlowProps> = ({ flowId }) => {
  // 1. 使用 useCallback 稳定所有ReactFlow回调
  const onNodesChange = useCallback((changes: NodeChange[]) => {
    // 处理节点变化
  }, []);

  const onEdgesChange = useCallback((changes: EdgeChange[]) => {
    // 处理边变化
  }, []);

  const onConnect = useCallback((connection: Connection) => {
    // 处理连接
  }, []);

  // 2. 使用 useMemo 缓存节点类型
  const nodeTypes: NodeTypes = useMemo(() => ({
    eventNode: EventNode,
    joinNode: JoinNode,
    unionAllNode: UnionAllNode,
    outputNode: OutputNode,
  }), []);

  // 3. 使用 useMemo 缓存可用字段
  const availableFields = useMemo(() => {
    return calculateAvailableFields(nodes, edges);
  }, [nodes, edges]);

  return (
    <ReactFlow
      nodeTypes={nodeTypes}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
    >
      <Panel position="top-right">
        <Toolbar onSave={handleSave} onExecute={handleExecute} />
      </Panel>
    </ReactFlow>
  );
};

const MemoizedCanvasFlow = React.memo(CanvasFlow, (prevProps, nextProps) => {
  return prevProps.flowId === nextProps.flowId;
});
```

**验证步骤**:
```bash
# 1. TypeScript类型检查
npx tsc --noEmit

# 2. ESLint检查
npm run lint

# 3. 本地测试
npm run dev
# 访问 http://localhost:5173/canvas
# 测试Canvas交互
```

---

### Agent 12: P0 游戏管理组件（8个）

**工作目录**: `frontend/src/features/games/` + `frontend/src/features/events/`
**预估时间**: 50分钟

**优化组件**:
- **P0**:
  1. ✅ `games/GameManagementModal.tsx` (586行)
  2. ✅ `games/GameManagementModalGraphQL.tsx` (280行)
  3. ✅ `games/AddGameModalGraphQL.tsx` (148行)
- **P1**:
  4. ✅ `events/EventManagementModalGraphQL.tsx` (308行)
  5. ✅ `events/AddEventModalGraphQL.tsx` (204行)
  6. ✅ `games/AddGameModal.tsx`
  7. ✅ `canvas/pages/CanvasPage.tsx` (111行)
  8. ✅ `canvas/pages/FlowBuilder.tsx`

**优化策略**:
```typescript
// GameManagementModalGraphQL.tsx 优化示例
const GameManagementModal: React.FC<Props> = ({ isOpen, onClose }) => {
  // 1. GraphQL查询
  const { data, loading, error } = useGetGamesQuery();

  // 2. 使用 useCallback 稳定事件处理器
  const handleCreate = useCallback((input: GameInput) => {
    createGame({ variables: { input } });
  }, []);

  const handleUpdate = useCallback((gid: string, changes: GameInput) => {
    updateGame({ variables: { gid, changes } });
  }, []);

  const handleDelete = useCallback((gid: string) => {
    deleteGame({ variables: { gid } });
  }, []);

  // 3. 使用 useMemo 缓存过滤后的游戏列表
  const filteredGames = useMemo(() => {
    return data?.games.filter(game => {
      return game.name.toLowerCase().includes(searchTerm.toLowerCase());
    }) ?? [];
  }, [data?.games, searchTerm]);

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <GameList
        games={filteredGames}
        onCreate={handleCreate}
        onUpdate={handleUpdate}
        onDelete={handleDelete}
      />
    </Modal>
  );
};

const MemoizedGameManagementModal = React.memo(GameManagementModal);
```

**验证步骤**:
```bash
# 1. TypeScript类型检查
npx tsc --noEmit

# 2. ESLint检查
npm run lint

# 3. 单元测试
npm run test:unit -- GameManagementModal.test.tsx

# 4. 本地测试
npm run dev
# 访问 http://localhost:5173
# 测试游戏管理功能
```

---

### Agent 13: P1 + P2 剩余组件（21个）

**工作目录**: `frontend/src/shared/ui/` + `frontend/src/features/`
**预估时间**: 45分钟

**优化组件**:
- **P1**:
  1. ✅ `Badge/Badge.tsx`
  2. ✅ `Breadcrumb/Breadcrumb.tsx`
  3. ✅ `EmptyState/EmptyState.tsx`
  4. ✅ `ErrorState/ErrorState.tsx`
  5. ✅ `Skeleton/Skeleton.tsx`
  6. ✅ `Spinner/Spinner.tsx`
  7. ✅ `Loading.tsx`
  8. ✅ `PageLoader/PageLoader.tsx`
  9. ✅ `canvas/components/App.tsx`
  10. ✅ `canvas/components/SearchBar.tsx`
  11. ✅ `canvas/components/NodeContextMenu.tsx`
- **P2**:
  12. ✅ `CodeBlock/CodeBlock.tsx`
  13. ✅ `SelectGamePrompt.tsx`
  14. ✅ `PerformanceMonitor.tsx`
  15. ✅ 其他辅助文件

**优化策略**:
```typescript
// 简单展示组件优化示例
const Badge: React.FC<BadgeProps> = ({ variant = 'default', children }) => {
  return (
    <span className={`badge badge--${variant}`}>
      {children}
    </span>
  );
};

// 仅使用 React.memo 即可
const MemoizedBadge = React.memo(Badge);
```

**验证步骤**:
```bash
# 1. TypeScript类型检查
npx tsc --noEmit

# 2. ESLint检查
npm run lint

# 3. 单元测试
npm run test:unit -- Badge.test.tsx
npm run test:unit -- Spinner.test.tsx

# 4. 本地测试
npm run dev
# 访问 http://localhost:5173
# 测试UI组件
```

---

## 🔧 通用优化模式

### 模式1: 添加 React.memo

```typescript
// 优化前
export default Component;

// 优化后
const ComponentMemo = React.memo(Component);
ComponentMemo.displayName = 'ComponentMemo';
export default ComponentMemo;
```

### 模式2: 添加 useCallback

```typescript
// 优化前
const handleChange = (value: string) => {
  onChange?.(value);
};

// 优化后
const handleChange = useCallback((value: string) => {
  onChange?.(value);
}, [onChange]);
```

### 模式3: 添加 useMemo

```typescript
// 优化前
const filteredItems = items.filter(item => item.active);

// 优化后
const filteredItems = useMemo(() => {
  return items.filter(item => item.active);
}, [items]);
```

### 模式4: Custom Comparison

```typescript
// 仅用于性能关键组件
const MemoizedComponent = React.memo(Component, (prevProps, nextProps) => {
  return (
    prevProps.value === nextProps.value &&
    prevProps.disabled === nextProps.disabled
  );
});
```

---

## ✅ 验证清单

### 每个组件优化后

- [ ] 添加了 `React.memo`？
- [ ] 事件处理器使用了 `useCallback`？
- [ ] 复杂计算使用了 `useMemo`？
- [ ] 组件功能正常工作？
- [ ] 无TypeScript类型错误？
- [ ] 无ESLint错误？

### Agent完成后

- [ ] 所有组件已优化？
- [ ] TypeScript类型检查通过？
- [ ] ESLint检查通过？
- [ ] 单元测试通过？
- [ ] 本地测试通过？
- [ ] 性能有所提升？

---

## 🚨 常见错误

### ❌ 错误1: 忘记添加依赖项

```typescript
// ❌ 错误
const handleChange = useCallback((value: string) => {
  onChange?.(value);
}, []); // 缺少 onChange 依赖

// ✅ 正确
const handleChange = useCallback((value: string) => {
  onChange?.(value);
}, [onChange]);
```

### ❌ 错误2: 过度使用 useMemo

```typescript
// ❌ 错误
const className = useMemo(() => {
  return 'simple-class';
}, []); // 简单字符串不需要缓存

// ✅ 正确
const className = 'simple-class';
```

### ❌ 错误3: Custom Comparison 返回 false

```typescript
// ❌ 错误
const MemoizedComponent = React.memo(Component, (prevProps, nextProps) => {
  return false; // 总是返回false，组件永远不会更新
});

// ✅ 正确
const MemoizedComponent = React.memo(Component, (prevProps, nextProps) => {
  return prevProps.value === nextProps.value;
});
```

---

## 📊 性能验证

### 使用 Chrome DevTools React Profiler

1. **打开React DevTools**:
   - F12 打开开发者工具
   - Profiler 标签页

2. **录制性能**:
   - 点击录制按钮
   - 执行用户操作
   - 停止录制

3. **分析结果**:
   - 查看渲染次数
   - 查看渲染时间
   - 对比优化前后

### 成功标准

- 🚀 渲染次数减少 >20%
- 🚀 脚本执行时间缩短 >15%
- 🚀 用户感知性能提升明显

---

## 📚 参考文档

- **[Phase 3 优化方案](/Users/mckenzie/Documents/event2table/docs/plans/2026-03-06-PHASE-3-OPTIMIZATION-PLAN.md)** - 完整优化方案
- **[React最佳实践](/Users/mckenzie/Documents/event2table/docs/lessons-learned/react-best-practices.md)** - React Hooks规则
- **[性能模式](/Users/mckenzie/Documents/event2table/docs/lessons-learned/performance-patterns.md)** - 性能优化模式

---

**文档版本**: 1.0
**创建日期**: 2026-03-06
**作者**: Claude Code
**状态**: ✅ 已完成
