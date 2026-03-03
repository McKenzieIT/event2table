# React最佳实践

> **来源**: 整合了4个文档的React相关经验
> **最后更新**: 2026-02-24
> **维护**: 每次React相关问题修复后立即更新

---

## React Hooks规则 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 4次 | **来源**: [TESTING_LESSONS_LEARNED.md](../archive/2026-02/testing-reports/TESTING_LESSONS_LEARNED.md), [iteration-2修复报告](../archive/2026-02/e2e-test-reports/iteration-2/), [CLAUDE.md](../../CLAUDE.md)

### 问题现象

**症状描述**:
- React组件崩溃，出现 "Rendered more hooks than during the previous render" 错误
- 组件首次渲染正常，第二次渲染崩溃
- 控制台错误：`React has detected a change in the order of Hooks called`

**影响范围**:
- 所有使用Hooks的React组件
- 特别是有条件返回的组件

### 根本原因

**技术原因**:
1. **Hook在条件返回之后调用** - 违反React Hooks规则
2. **Hook调用顺序不一致** - 首次渲染和第二次渲染的Hook数量不同
3. **Hook在if/for/嵌套函数中调用** - 违反"只在顶层调用"规则

**错误示例**:
```javascript
// ❌ 错误：Hook在条件返回之后调用
function Component() {
  const data = useData();

  if (isLoading) return <Loading />; // ❌ 条件返回在中间

  const processed = useMemo(() => {}, [data]); // ❌ Hook在条件返回后
  return <View />;
}
```

**为什么崩溃**:
- 第1次渲染 (`isLoading=true`): 只调用1个Hook (`useData`)
- 第2次渲染 (`isLoading=false`): 调用2个Hook (`useData`, `useMemo`)
- **React检测到Hooks数量不一致** → 崩溃

### 解决方案

```javascript
// ✅ 正确：所有Hook在条件返回之前
function Component() {
  const data = useData();

  // ✅ 所有Hook在条件返回之前
  const processed = useMemo(() => {
    if (!data) return null;
    return data.filter(...);
  }, [data]);

  // ✅ 条件返回在所有Hook之后
  if (isLoading) return <Loading />;

  return <View />;
}
```

**关键规则**:
1. ✅ 只在顶层调用Hooks（不在if、for、嵌套函数中）
2. ✅ 没有在Hooks调用之间进行条件返回
3. ✅ 每次渲染时Hooks的调用顺序相同
4. ✅ 所有Hook都在组件最顶层调用

### 预防措施

**1. ESLint强制检测**:
```bash
npm install eslint-plugin-react-hooks --save-dev
```

```javascript
// .eslintrc.js
module.exports = {
  plugins: ['react-hooks'],
  rules: {
    'react-hooks/rules-of-hooks': 'error', // 强制规则
    'react-hooks/exhaustive-deps': 'warn', // 检测依赖项
  },
};
```

**2. 代码审查清单**:
- [ ] 所有Hooks都在组件最顶层调用？
- [ ] 没有任何Hook在条件语句、循环或嵌套函数中？
- [ ] 没有在Hooks调用之间进行条件返回？
- [ ] 每次渲染时Hooks的调用顺序相同？
- [ ] ESLint React Hooks规则已启用？

### 相关经验

- [Lazy Loading最佳实践](#lazy-loading) - 另一个React常见问题
- [性能优化技巧](#性能优化) - React.memo、useCallback优化

### 案例文档

- [E2E测试迭代2修复报告 - 案例1](../archive/2026-02/e2e-test-reports/iteration-2/FIX-REPORT.md#案例1-hooks规则修复)
- [HqlManage组件修复](../archive/2026-02/e2e-test-reports/iteration-2/SUMMARY.md)

---

## Lazy Loading最佳实践 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 3次 | **来源**: [TESTING_LESSONS_LEARNED.md](../archive/2026-02/testing-reports/TESTING_LESSONS_LEARNED.md), [iteration-2修复报告](../archive/2026-02/e2e-test-reports/iteration-2/), [routes.jsx分析](../../frontend/src/routes/routes.jsx)

### 问题现象

**症状描述**:
- 页面卡在 "LOADING EVENT2TABLE..." 状态，无法加载
- 控制台无错误信息
- 用户永远看不到实际加载内容或错误信息

**影响范围**:
- 使用React.lazy()和Suspense的页面
- 小型组件（<50行，<10KB）

### 根本原因

**技术原因**:
1. **双重Suspense嵌套** - 外层Suspense优先显示fallback，lazy组件永不resolve
2. **小型组件使用lazy loading** - 性能收益极小，但可能导致严重的加载问题
3. **lazy组件加载失败但错误被外层Suspense捕获** - 用户看不到错误信息

**错误架构**:
```javascript
// ❌ 错误：双重Suspense嵌套
// App.jsx
<Suspense fallback={<GlobalLoading text="Loading Event2Table..." />}>
  <MainLayout />
</Suspense>

// MainLayout.jsx
<Suspense fallback={<Loading text="加载中..." />}>
  <Outlet />
</Suspense>

// routes.jsx
const ApiDocs = lazy(() => import("@analytics/pages/ApiDocs"));

// 问题：lazy组件永不resolve → 永远显示"Loading Event2Table..."
```

### 解决方案

**1. 选择性使用Lazy Loading**:
```javascript
// ✅ 正确：小型组件直接导入
import ApiDocs from "@analytics/pages/ApiDocs";
import ValidationRules from "@analytics/pages/ValidationRules";
import ParameterDashboard from "@analytics/pages/ParameterDashboard";

// ❌ 错误：小型组件使用lazy loading
const ApiDocs = lazy(() => import("@analytics/pages/ApiDocs"));
```

**2. 仅在大型组件使用Lazy Loading**:
```javascript
// ✅ 正确：仅在大型组件（>10KB）使用lazy loading
const CanvasPage = lazy(() => import("./features/canvas/pages/CanvasPage"));
const EventNodeBuilder = lazy(() => import("./event-builder/pages/EventNodeBuilder"));

// ❌ 错误：小型文档页面使用lazy loading
const ApiDocs = lazy(() => import("@analytics/pages/ApiDocs")); // <50行
```

**使用原则**:
- ✅ 大型组件（>10KB） → 使用lazy loading
- ✅ 不常用的路由页面 → 使用lazy loading
- ✅ 复杂的数据可视化组件 → 使用lazy loading
- ❌ 简单的文档页面（<50行） → 直接导入
- ❌ 已经很快加载的小型组件 → 直接导入

### 预防措施

**1. 代码审查清单**:
- [ ] 组件大小是否>10KB？
- [ ] 是否是不常用页面？
- [ ] 是否有双重Suspense嵌套？
- [ ] 小型组件是否使用直接导入？

**2. 性能对比**:
- 修复前：3个lazy组件（~2KB）→ 加载超时 ❌
- 修复后：合并到主bundle（~1.8MB）→ 加载成功 ✅
- **结论**：对于小型组件，lazy loading的性能收益极小，但可能导致严重的加载问题

### 相关经验

- [React Hooks规则](#react-hooks规则) - React另一个常见问题
- [性能优化技巧](#性能优化) - 其他React性能优化方法

### 案例文档

- [E2E测试迭代2修复报告 - 案例2](../archive/2026-02/e2e-test-reports/iteration-2/FIX-REPORT.md#案例2-lazy-loading修复)
- [routes.jsx修复记录](../archive/2026-02/e2e-test-reports/iteration-2/SUMMARY.md)

---

## 性能优化技巧 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 2次 | **来源**: [CLAUDE.md](../../CLAUDE.md), [性能优化报告](../archive/2026-02/optimization-reports/)

### React.memo优化

**适用场景**:
- 组件频繁重新渲染，但props相同
- 大型列表渲染
- 复杂组件渲染

**示例**:
```javascript
// ✅ 使用React.memo避免不必要的重新渲染
const ExpensiveComponent = React.memo(({ data, onAction }) => {
  // ... 复杂渲染逻辑
}, (prevProps, nextProps) => {
  // 自定义比较函数
  return prevProps.data.id === nextProps.data.id;
});
```

### useCallback优化

**适用场景**:
- 回调函数传递给优化过的子组件
- 回调函数作为其他Hook的依赖

**示例**:
```javascript
// ✅ 使用useCallback避免回调函数重新创建
const handleClick = useCallback((id) => {
  // 处理点击
}, [/* 依赖 */]);
```

### 代码审查清单

- [ ] 是否有频繁重新渲染的组件？
- [ ] 是否可以使用React.memo优化？
- [ ] 是否可以使用useCallback优化回调函数？
- [ ] 是否可以使用useMemo优化计算结果？

---

## Input组件CSS布局规范 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 2次 | **来源**: [CLAUDE.md](../../CLAUDE.md#input组件使用规范), [Input组件源码](../../frontend/src/shared/ui/Input/)

### 问题现象

**症状描述**:
- Input组件尺寸不一致（cyber-input和wrapper长度不同）
- Input右侧出现152px空白间隙
- Modal CSS覆盖了Input组件的Grid架构

### 根本原因

**技术原因**:
1. **CSS命名混淆**: `.cyber-input`既用作Grid容器，又被当作input元素
2. **DOM结构错误**: Label在Input外部，导致Grid布局预留的label列空置
3. **外部CSS冲突**: Modal CSS覆盖了Input组件的Grid架构

**错误示例**:
```jsx
// ❌ 错误：Label在Input外部
<div className="form-group">
  <label>游戏名称</label>
  <Input ... />
</div>

/* ❌ 错误：外部CSS破坏Grid架构 */
.form-group .cyber-input {
  width: 100%;  /* 覆盖Grid容器 */
  padding: 0.625rem 0.75rem;
}
```

### 解决方案

**1. 核心原则：始终使用label prop**:
```jsx
// ✅ 正确：使用label prop
<Input
  label="游戏名称"
  type="text"
  value={gameName}
  onChange={(e) => setGameName(e.target.value)}
/>
```

**2. Input组件的DOM结构**:
```html
<div class="cyber-field cyber-input">              ← Grid容器（140px label列 + 1fr input列）
  <label class="cyber-field__label cyber-input__label">
    游戏名称 <span class="cyber-field__required">*</span>
  </label>
  <div class="cyber-field__wrapper cyber-input-wrapper">  ← Flex容器（占满第2列）
    <input class="cyber-field__input cyber-input"      ← 实际input元素（占满wrapper）
      type="text"
      value="..."
    />
  </div>
  <p class="cyber-field__helper cyber-input__helper">
    提示信息
  </p>
</div>
```

**3. 使用新的class名（避免混淆）**:
```css
/* ✅ 正确：只调整margin */
.cyber-field {
  margin-bottom: 1rem;
}

.cyber-field__input {
  border-color: #06b6d4;
}
```

### 预防措施

**代码审查清单**:
- [ ] 是否始终使用label prop而非外部label？
- [ ] Label是否在Input内部而非外部？
- [ ] 是否避免覆盖.cyber-field的Grid布局？
- [ ] 是否使用新的class名（cyber-field__*）？

### 相关经验

- [React Hooks规则](#react-hooks-规则) - React组件规范
- [性能优化技巧](#性能优化) - CSS性能优化

### 案例文档

- [Input组件架构重构报告](../../CLAUDE.md#2026-02-22-input组件架构重构与游戏编辑ux优化)

---

## React子组件定义顺序 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [iteration-6 FIX-REPORT-FLOW-BUILDER.md](../archive/2026-02/e2e-test-reports/iteration-6/)

### 问题现象

**症状描述**:
- 组件崩溃：`Element type is invalid: expected a string but got: undefined`
- Card子组件显示为undefined

### 根本原因

**技术原因**:
- 子组件赋值顺序错误：在使用时子组件还未定义
- React在JSX编译时找不到组件定义

**错误示例**:
```javascript
// ❌ 错误：子组件赋值早于定义
Card.Header = CardHeader;  // CardHeader还未定义！
Card.Body = CardBody;

const CardHeader = React.memo(function CardHeader() { ... });
const CardBody = React.memo(function CardBody() { ... });
```

### 解决方案

```javascript
// ✅ 正确顺序：先定义所有子组件
const CardHeader = React.memo(function CardHeader(...) { ... });
const CardBody = React.memo(function CardBody(...) { ... });

// ✅ 然后赋值给父组件
Card.Header = CardHeader;
Card.Body = CardBody;
```

### 预防措施

**代码审查清单**:
- [ ] 所有子组件是否在使用前已定义？
- [ ] 子组件定义是否在赋值之前？
- [ ] 是否避免循环依赖？

### 相关经验

- [React Hooks规则](#react-hooks-规则) - React组件规范
- [组件导出规范](#组件导出规范) - 组件导出最佳实践

---

## useEffect依赖数组最佳实践 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [event-node-builder-fixes-complete.md](../archive/2026-02/e2e-test-reports/iteration-8/)

### 问题现象

**症状描述**:
- `useCallback` + `useEffect` 组合导致React无法正确检测数组内容变化
- 字段添加后，HQL预览不更新

### 根本原因

**技术原因**:
- `useCallback`的记忆化函数引用不变，即使依赖数组内容变化
- `useEffect`依赖记忆化的函数，但函数内部的数组引用已过期

**错误示例**:
```javascript
// ❌ 反模式：useCallback + useEffect导致无法检测数组内容变化
const generateHQL = useCallback(async () => {
  // ... 使用fields数组
}, [deps]);

useEffect(() => {
  generateHQL();
}, [generateHQL]);
// 问题：fields变化时，generateHQL引用不变，useEffect不执行
```

### 解决方案

```javascript
// ✅ 正确：直接在useEffect中定义函数
useEffect(() => {
  const generateHQLInternal = async () => {
    // ... 使用fields数组
  };
  generateHQLInternal();
}, [fields]);
// 优势：fields变化时，useEffect能正确检测并执行
```

### 预防措施

**代码审查清单**:
- [ ] 是否避免在useCallback中引用会变化的数组？
- [ ] useEffect的依赖数组是否直接包含数据而非函数？
- [ ] 是否在useEffect内部定义使用数据的函数？

### 相关经验

- [React Hooks规则](#react-hooks-规则) - React Hooks规范
- [性能优化技巧](#性能优化) - useCallback正确使用

---

## 组件导出规范 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [iteration-7 COMPLETE-FIX-REPORT.md](../archive/2026-02/e2e-test-reports/iteration-7/)

### 问题现象

**症状描述**:
- 组件无法正确导入
- 导入时显示undefined

### 根本原因

**技术原因**:
- `shared/ui/index.ts`只导出别名，未导出原始组件名
- 导致某些导入方式失败

**错误示例**:
```javascript
// ❌ 错误：只导出别名
export { Input as CyberInput };  // 只有别名

// 导入时失败
import { CyberInput } from 'shared/ui';  // ✅ 可以
import { Input } from 'shared/ui';      // ❌ 失败
```

### 解决方案

```javascript
// ✅ 正确：同时导出原始组件名和别名
export { Input };
export { Input as CyberInput };

// 或者使用re-export
export * from './Input';
export * from './Button';
export * from './Modal';
```

### 预防措施

**代码审查清单**:
- [ ] index.ts是否同时导出原始组件名和别名？
- [ ] 是否使用export *来导出所有组件？
- [ ] 组件是否正确命名和导出？

### 相关经验

- [React子组件定义顺序](#react子组件定义顺序) - 组件定义顺序
- [性能优化技巧](#性能优化) - 组件导出优化

---

## API响应数据结构处理 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [iteration-7 COMPLETE-FIX-REPORT.md](../archive/2026-02/e2e-test-reports/iteration-7/)

### 问题现象

**症状描述**:
- 组件崩溃，无法读取undefined的属性
- 数据解析错误

### 根本原因

**技术原因**:
- API返回`{ data: { parameters: [...] } }`
- 但代码期望`result.data`是数组
- 未正确访问嵌套数据结构

**错误示例**:
```javascript
// ❌ 错误：直接访问result.data作为数组
const parameters = result.data.map(...);  // result.data是对象，不是数组！
```

### 解决方案

```javascript
// ✅ 正确：访问嵌套数据结构
const parameters = result.data.parameters.map(...);

// 或使用可选链
const parameters = result.data?.parameters || [];
```

### 预防措施

**代码审查清单**:
- [ ] 是否正确处理API响应的嵌套结构？
- [ ] 是否使用可选链（?.）避免undefined错误？
- [ ] 是否添加数据格式验证？

### 相关经验

- [API设计模式 - 错误处理](./api-design-patterns.md#错误处理) - API错误处理
- [调试技能](./debugging-skills.md) - 调试数据结构问题

---

## TypeScript严格模式迁移 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [FINAL-COMPREHENSIVE-REPORT.md](../../reports/2026-03-01/FINAL-COMPREHENSIVE-REPORT.md)

### 问题现象

**症状描述**:
- 项目中存在大量`any`类型
- 类型错误难以在开发时发现
- 运行时错误频发

### 根本原因

**技术原因**:
- TypeScript配置未启用严格模式
- 缺少类型检查规则
- 没有强制类型注解

### 解决方案

**分阶段启用严格模式**:
```json
// tsconfig.json
{
  "compilerOptions": {
    // 阶段1: noImplicitAny（已启用）
    "noImplicitAny": true,

    // 阶段2: strictNullChecks（计划中）
    "strictNullChecks": true,

    // 阶段3: 完整严格模式（最终目标）
    "strict": true
  }
}
```

**自动化类型检查**:
```bash
# ESLint强制检查
npm install --save-dev @typescript-eslint/parser @typescript-eslint/eslint-plugin
```

```javascript
// .eslintrc.js
module.exports = {
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint'],
  rules: {
    '@typescript-eslint/no-explicit-any': 'error',
    '@typescript-eslint/explicit-function-return-type': 'warn'
  }
};
```

**类型系统设计**:
```typescript
// 共享类型定义
export type Size = 'xs' | 'sm' | 'md' | 'lg' | 'xl';
export type Variant = 'primary' | 'secondary' | 'danger' | 'outline' | 'ghost';

// 组合模式
export interface LabeledComponentProps extends BaseComponentProps {
  label?: string;
  error?: string;
}
```

### 代码审查清单

- [ ] 是否启用了noImplicitAny？
- [ ] 是否避免使用any类型？
- [ ] 是否为函数添加返回类型注解？
- [ ] 是否使用共享类型定义？

### 案例文档

- [TypeScript完整迁移报告](../../reports/2026-03-01/FINAL-COMPREHENSIVE-REPORT.md)

---

## Ralph Loop迭代测试方法论 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 9次迭代 | **来源**: [Ralph Testing Final Report](../archive/ralph-testing/ralph/FINAL-REPORT.md), [迭代1-9报告](../archive/ralph-testing/ralph/)

### 核心概念

**发现问题 → Subagent深度分析 → 设计修复方案 → 实施修复 → Chrome MCP验证 → 记录结果**

### Ralph Loop方法论

**迭代测试流程**:
```
发现问题 → 根因分析 → 设计修复 → 实施修复 → E2E验证 → 记录经验
   ↑                                                        ↓
   └──────────────────── 下一次迭代 ──────────────────────────┘
```

**关键原则**:
1. **发现问题优先** - 通过E2E测试发现实际用户可见的问题
2. **根因分析深度** - 使用Subagent并行分析策略进行深度根因分析
3. **系统化修复** - 使用Brainstorming skill设计修复方案
4. **验证闭环** - 使用Chrome DevTools MCP进行端到端验证
5. **经验记录** - 将经验提取到经验文档系统

### 实施步骤

**步骤1: 发现问题（E2E测试）**
```bash
# 使用Chrome DevTools MCP进行E2E测试
1. 列出所有页面
mcp__chrome-devtools__list_pages()

2. 导航到测试页面
mcp__chrome-devtools__navigate_page({ type: "url", url: "..." })

3. 获取页面快照
mcp__chrome-devtools__take_snapshot()

4. 检查控制台错误
mcp__chrome-devtools__list_console_messages({ types: ["error", "warn"] })
```

**步骤2: 根因分析（Subagent并行）**
```python
# 启动2个并行subagent进行根因分析
Task(subagent_type="general-purpose", prompt="分析React Hooks错误根因")
Task(subagent_type="general-purpose", prompt="分析加载超时模式")

# 同时进行，效率提升
```

**步骤3: 设计修复方案（Brainstorming）**
```bash
# 使用brainstorming skill系统化设计修复方案
/superpowers:brainstorming

# 提示：设计React Hooks修复方案
# 1. 理解问题：Hook在条件返回后调用
# 2. 探索方案：2-3种修复策略
# 3. 选择最佳：重构Hook调用顺序
# 4. 分段验证：先验证Hook顺序，再验证功能
```

**步骤4: 实施修复**
```javascript
// 实施修复方案
function HqlManage() {
  const data = useData();
  const processed = useMemo(() => {}, [data]); // ✅ 所有Hook在条件返回前
  if (isLoading) return <Loading />;
  return <View />;
}
```

**步骤5: 验证修复（Chrome MCP）**
```bash
# 1. 刷新页面
mcp__chrome-devtools__navigate_page({ type: "reload" })

# 2. 获取页面快照
mcp__chrome-devtools__take_snapshot()

# 3. 检查控制台错误
mcp__chrome-devtools__list_console_messages({ types: ["error"] })

# 4. 截图记录
mcp__chrome-devtools__take_screenshot({ filePath: "fix-verification.png" })
```

**步骤6: 记录经验**
```markdown
# 更新经验文档
1. 提取经验点到经验文档
2. 更新CLAUDE.md中的记录
3. 将详细报告归档到archive/
```

### 性能数据

**Event2Table项目实际数据**:
- **测试覆盖**: 27+页面
- **发现问题**: 8个严重问题
- **修复成功率**: 100% (8/8)
- **迭代次数**: 9次
- **测试通过率**: 从63%提升到90%

### 代码审查清单

- [ ] 是否使用Chrome DevTools MCP进行E2E测试？
- [ ] 是否使用Subagent并行分析进行根因分析？
- [ ] 是否使用Brainstorming skill设计修复方案？
- [ ] 修复后是否进行E2E验证？
- [ ] 是否记录经验到经验文档？

### 案例文档

- [Ralph Testing Final Report](../archive/ralph-testing/ralph/FINAL-REPORT.md) - 完整测试报告
- [迭代2修复报告](../archive/ralph-testing/ralph/iteration-2/FIX-REPORT.md) - Hooks规则修复案例
- [迭代8修复报告](../archive/ralph-testing/ralph/iteration-8/EVENT-NODE-BUILDER-E2E-TEST-REPORT.md) - 事件节点构建器修复

### 相关经验

- [Chrome DevTools MCP调试法](#chrome-devtools-mcp工作流) - Chrome MCP详细使用
- [Subagent并行分析法](#subagent并行分析策略) - 并行分析策略

---

## Chrome DevTools MCP工作流 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 9次迭代 | **来源**: [Ralph Testing Final Report](../archive/ralph-testing/ralph/FINAL-REPORT.md), [CLAUDE.md E2E测试关键学习](../../CLAUDE.md#e2e测试关键学习成果)

### 核心工具

**Chrome DevTools MCP** - 通过MCP协议控制Chrome浏览器进行E2E测试

### 标准测试工作流

**1. 列出所有页面**
```javascript
// 查看所有打开的页面
mcp__chrome-devtools__list_pages()
// 返回: [{ pageId: 1, title: "Dashboard", url: "http://localhost:5173/" }, ...]
```

**2. 导航到测试页面**
```javascript
// 导航到指定URL
mcp__chrome-devtools__navigate_page({
  type: "url",
  url: "http://localhost:5173/parameter-dashboard?game_gid=10000147",
  timeout: 30000
})

// 或重新加载页面
mcp__chrome-devtools__navigate_page({
  type: "reload",
  ignoreCache: true
})
```

**3. 获取页面快照**
```javascript
// 获取可访问性树快照（推荐用于元素定位）
mcp__chrome-devtools__take_snapshot({
  verbose: false
})
// 返回: 页面元素列表，每个元素包含uid、角色、名称、属性
```

**4. 检查控制台错误**
```javascript
// 列出所有控制台消息
mcp__chrome-devtools__list_console_messages({
  types: ["error", "warn"],  // 只查看错误和警告
  pageSize: 50,
  includePreservedMessages: false
})

// 获取特定错误消息的详细信息
mcp__chrome-devtools__get_console_message({
  msgid: 123
})
```

**5. 截图记录**
```javascript
// 截取完整页面截图
mcp__chrome-devtools__take_screenshot({
  filePath: "docs/ralph/iteration-2/screenshots/fix-01.png",
  format: "png",
  fullPage: true
})

// 截取特定元素
mcp__chrome-devtools__take_screenshot({
  uid: "element-uid-from-snapshot",
  filePath: "element-screenshot.png"
})
```

**6. 点击交互元素**
```javascript
// 点击按钮/链接
mcp__chrome-devtools__click({
  uid: "submit-button",
  includeSnapshot: true  // 点击后获取新快照
})

// 双击
mcp__chrome-devtools__click({
  uid: "row-item",
  dblClick: true
})
```

**7. 填写表单**
```javascript
// 填写输入框
mcp__chrome-devtools__fill({
  uid: "game-name-input",
  value: "Test Game",
  includeSnapshot: true
})

// 批量填写多个表单元素
mcp__chrome-devtools__fill_form({
  elements: [
    { uid: "name-input", value: "Game Name" },
    { uid: "gid-input", value: "90000001" },
    { uid: "description-input", value: "Test Description" }
  ]
})
```

**8. 等待页面状态**
```javascript
// 等待特定文本出现
mcp__chrome-devtools__wait_for({
  text: ["数据加载完成", "Data loaded successfully"],
  timeout: 10000
})
```

### 错误检测模式

**React Hooks错误**:
```
[error] React has detected a change in the order of Hooks called
[error] Uncaught Error: Rendered more hooks than during the previous render
```

**加载超时错误**:
```
页面状态：卡在"LOADING EVENT2TABLE..."超过30秒
控制台：无错误信息（但也不显示任何内容）
```

**API错误**:
```
[error] Failed to load resource: 400 (BAD REQUEST)
[error] Failed to load resource: 404 (NOT FOUND)
[error] Failed to load resource: 500 (INTERNAL SERVER ERROR)
```

### 调试技巧

**技巧1: 使用快照快速定位元素**
```javascript
// 1. 获取快照
const snapshot = await mcp__chrome-devtools__take_snapshot();

// 2. 查找元素uid
const submitButton = snapshot.find(el => el.name === "提交");

// 3. 使用uid进行交互
await mcp__chrome-devtools__click({ uid: submitButton.uid });
```

**技巧2: 监控网络请求**
```javascript
// 列出所有网络请求
await mcp__chrome-devtools__list_network_requests({
  resourceTypes: ["xhr", "fetch"],
  pageSize: 100
})

// 获取特定请求的详细信息
await mcp__chrome-devtools__get_network_request({
  reqid: 12345,
  responseFilePath: "response.json"
})
```

**技巧3: 执行JavaScript**
```javascript
// 在页面上下文中执行JavaScript
await mcp__chrome-devtools__evaluate_script({
  function: `
    () => {
      return {
        gameGid: window.location.search.match(/game_gid=(\d+)/)?.[1],
        reactVersion: React.version,
        state: window.__STATE__
      }
    }
  `
})
```

### 代码审查清单

- [ ] 测试前是否列出所有页面确认环境？
- [ ] 是否使用take_snapshot()而非screenshot进行元素定位？
- [ ] 是否检查控制台错误和警告？
- [ ] 是否记录截图用于问题追踪？
- [ ] 测试失败时是否获取网络请求信息？

### 相关经验

- [Ralph Loop迭代测试方法论](#ralph-loop迭代测试方法论) - 完整测试流程
- [Subagent并行分析策略](#subagent并行分析策略) - 根因分析方法

---

## Subagent并行分析策略 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 多次 | **来源**: [CLAUDE.md 并行开发策略](../../CLAUDE.md#项目管理最佳实践), [Ralph Testing迭代2](../archive/ralph-testing/ralph/iteration-2/)

### 核心概念

**使用多个subagents并行处理独立任务，效率提升3-4倍**

### 并行分析模式

**根因分析策略**:
```python
# 步骤1: 识别问题模式
问题模式: React Hooks错误 + 加载超时

# 步骤2: 并行深度分析
Task(subagent_type="general-purpose", prompt="分析React Hooks错误根因")
Task(subagent_type="general-purpose", prompt="分析加载超时模式")

# 步骤3: 综合分析结果
对比两个subagent的发现，识别共同点和差异

# 步骤4: 确定根本原因
基于综合分析，确定最可能的根本原因
```

### 实施策略

**1. 任务分解原则**
```python
# ✅ 正确：任务独立，无共享状态
Task(subagent_type="general-purpose", prompt="分析React Hooks错误根因")
Task(subagent_type="general-purpose", prompt="分析加载超时模式")

# ❌ 错误：任务有依赖关系
Task(subagent_type="general-purpose", prompt="修复React Hooks错误")  # 需要先分析
Task(subagent_type="general-purpose", prompt="验证修复")  # 依赖修复完成
```

**2. 并行执行示例**
```python
# 同时启动2个并行subagent
agent1 = Task(subagent_type="general-purpose", prompt="分析React Hooks错误根因")
agent2 = Task(subagent_type="general-purpose", prompt="分析加载超时模式")

# 等待两个agent完成
result1 = agent1.result()
result2 = agent2.result()

# 综合分析
common_causes = find_common_causes(result1, result2)
```

**3. 集成测试**
```bash
# 每个分析完成后立即验证
pytest backend/test/unit/           # 单元测试
npm run test:e2e                     # E2E测试
```

### 性能数据

**Event2Table项目实际数据**:
- 并行分析：~30分钟
- 如果串行分析：~90-120分钟
- **效率提升：3-4倍**

### 代码审查清单

- [ ] 任务是否可独立执行？
- [ ] 是否有明确的输入和输出？
- [ ] 是否避免了共享状态？
- [ ] 每个任务完成后是否立即验证？

### 相关经验

- [项目管理 - 并行开发策略](./project-management.md#并行开发策略) - 项目级并行开发
- [Chrome DevTools MCP工作流](#chrome-devtools-mcp工作流) - MCP调试工具

---

## 性能分析模式 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 多次 | **来源**: [性能优化报告](../archive/2026-02/optimization-reports/), [CLAUDE.md 性能模式](../../CLAUDE.md#性能模式)

### React性能分析

**1. 使用React Profiler**
```javascript
import { Profiler } from 'react';

function onRenderCallback(
  id, phase, actualDuration, baseDuration,
  startTime, commitTime, interactions
) {
  console.log(`${id} (${phase}) took ${actualDuration}ms`);
}

<Profiler id="MyComponent" onRender={onRenderCallback}>
  <MyComponent />
</Profiler>
```

**2. 使用Chrome DevTools Performance**
```bash
# 1. 打开Chrome DevTools
# 2. 切换到Performance标签
# 3. 点击Record开始录制
# 4. 执行用户操作
# 5. 停止录制并分析
```

**3. 检测不必要的重新渲染**
```javascript
// 使用React DevTools Profiler
# 1. 打开React DevTools
# 2. 切换到Profiler标签
# 3. 点击Record开始录制
# 4. 执行用户操作
# 5. 查看每个组件的渲染次数
```

### 常见性能问题

**问题1: 大型列表渲染**
```javascript
// ❌ 问题：渲染所有项
{items.map(item => <Item key={item.id} {...item} />)}

// ✅ 解决：使用虚拟列表
import { FixedSizeList } from 'react-window';
<FixedSizeList
  height={600}
  itemCount={items.length}
  itemSize={50}
>
  {({ index, style }) => <Item style={style} {...items[index]} />}
</FixedSizeList>
```

**问题2: 频繁的状态更新**
```javascript
// ❌ 问题：每次更新都触发重新渲染
const [items, setItems] = useState([]);
const addItem = (item) => setItems([...items, item]);

// ✅ 解决：批量更新
const addItem = useCallback((item) => {
  setItems(prev => [...prev, item]);
}, []);
```

**问题3: 昂贵的计算**
```javascript
// ❌ 问题：每次渲染都重新计算
const sorted = items.sort((a, b) => a.value - b.value);

// ✅ 解决：使用useMemo
const sorted = useMemo(() =>
  items.sort((a, b) => a.value - b.value),
  [items]
);
```

### 性能优化清单

- [ ] 是否使用React.memo避免不必要的重新渲染？
- [ ] 是否使用useCallback和useMemo优化计算？
- [ ] 是否使用虚拟列表处理大型列表？
- [ ] 是否使用代码分割（lazy loading）减少初始加载？
- [ ] 是否使用React Profiler分析性能？

### 相关经验

- [性能优化技巧](#性能优化技巧) - React.memo、useCallback优化
- [项目管理 - 性能监控](./project-management.md) - 项目级性能监控

---

## 相关经验文档

- [测试指南 - E2E测试](./testing-guide.md#e2e测试) - React组件E2E测试方法
- [调试技能 - 并行开发](./debugging-skills.md#并行开发策略) - 并行开发具体方法
- [项目管理 - 并行开发策略](./project-management.md#并行开发策略) - 项目级并行开发
- [调试技能](./debugging-skills.md) - React组件调试方法
