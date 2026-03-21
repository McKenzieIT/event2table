# React最佳实践

> **来源**: 整合了6个文档的React相关经验
> **最后更新**: 2026-03-04（新增前端加载问题修复经验）
> **维护**: 每次React相关问题修复后立即更新

---

## React Hooks规则 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 4次 | **来源**: [E2E测试指南](./testing-guide.md), [iteration-2修复报告](../archive/2026-02/e2e-test-reports/iteration-2/), [CLAUDE.md](../../CLAUDE.md)

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

- [E2E测试指南](./testing-guide.md) - 完整的E2E测试方法论

---

## Lazy Loading最佳实践 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 3次 | **来源**: [E2E测试指南](./testing-guide.md), [iteration-2修复报告](../archive/2026-02/e2e-test-reports/iteration-2/), [routes.jsx分析](../../frontend/src/routes/routes.jsx)

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

- [E2E测试指南](./testing-guide.md) - Lazy Loading决策标准和测试方法

---

## 性能优化技巧 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 2次 | **来源**: [CLAUDE.md](../../CLAUDE.md), [性能模式](./performance-patterns.md)

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

**优先级**: P1 | **出现次数**: 1次 | **来源**: [React组件规范](../../CLAUDE.md#react子组件定义顺序)

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

**优先级**: P1 | **出现次数**: 1次 | **来源**: [useEffect最佳实践](./testing-guide.md#usee xeffect依赖数组)

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

**优先级**: P1 | **出现次数**: 1次 | **来源**: [组件导出规范](../../CLAUDE.md#组件导出规范)

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

**优先级**: P1 | **出现次数**: 1次 | **来源**: [API响应处理](../../CLAUDE.md#api响应数据结构处理)

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

**优先级**: P1 | **出现次数**: 1次 | **来源**: [项目迁移指南](../../CLAUDE.md#typescript严格模式)

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

- [TypeScript开发规范](../../CLAUDE.md#typescript严格模式迁移) - TypeScript配置和类型系统设计

---

## Ralph Loop迭代测试方法论 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 9次迭代 | **来源**: [E2E测试指南](./testing-guide.md), [Ralph Testing方法](./testing-guide.md#ralph-loop迭代测试方法论)

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

- [E2E测试指南](./testing-guide.md) - 完整的E2E测试方法论
- [测试快速参考](../../CLAUDE.md#e2e测试关键学习成果) - E2E测试核心要点

### 相关经验

- [Chrome DevTools MCP调试法](#chrome-devtools-mcp工作流) - Chrome MCP详细使用
- [Subagent并行分析法](#subagent并行分析策略) - 并行分析策略

---

## Chrome DevTools MCP工作流 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 多次 | **来源**: [E2E测试指南](./testing-guide.md), [CLAUDE.md E2E测试关键学习](../../CLAUDE.md#e2e测试关键学习成果)

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

**优先级**: P1 | **出现次数**: 多次 | **来源**: [项目管理 - 并行开发策略](./project-management.md), [Ralph Loop迭代测试](#ralph-loop迭代测试方法论)

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

**优先级**: P1 | **出现次数**: 多次 | **来源**: [性能模式](./performance-patterns.md), [CLAUDE.md 性能优化](../../CLAUDE.md#性能优化)

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

## Vite与Apollo Client兼容性 ⚠️ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [前端加载问题修复报告](../reports/2026-03-04/FRONTEND-LOADING-FIX-REPORT.md)

### 问题现象

**症状描述**:
- 开发环境正常运行，无错误
- 生产构建出现模块解析错误
- 错误：`Cannot read property of undefined`
- Apollo Client某些子模块无法正确预构建

**影响范围**:
- 使用Vite 7.x + Apollo Client v4的项目
- GraphQL功能页面
- 生产环境构建

### 根本原因

**技术原因**:
1. **Vite 7.x改变了依赖预构建策略** - 与Apollo Client v4的某些子模块不兼容
2. **optimizeDeps配置不完整** - Apollo Client的某些子模块未被正确预构建
3. **模块解析失败** - 开发环境OK但生产构建失败

**版本兼容性问题**:
- Vite 7.x: 改变了依赖预构建策略
- Apollo Client 4.1.6: 某些子模块无法正确预构建
- 结果：运行时模块解析错误

### 解决方案

**方案1: 增强optimizeDeps配置（推荐）**

```typescript
// frontend/vite.config.ts
export default defineConfig({
  // ... 其他配置 ...

  optimizeDeps: {
    include: [
      'reactflow',
      // Apollo Client 核心包
      '@apollo/client',
      '@apollo/client/react',
      // Apollo Client 链（完整）
      '@apollo/client/link/context',
      '@apollo/client/link/error',
      '@apollo/client/link/retry',
      '@apollo/client/link/http',
      '@apollo/client/link/ws',
      // Apollo Client 工具
      '@apollo/client/utilities',
      // GraphQL（Apollo Client 的依赖）
      'graphql',
      'graphql/tag',
    ],
  },
});
```

**方案2: 排除某些包（不推荐，除非有特定问题）**

```typescript
optimizeDeps: {
  include: [
    'reactflow',
    '@apollo/client',
    '@apollo/client/react'
  ],
  exclude: [
    // ⚠️ 不推荐排除，除非有特定的兼容性问题
  ]
}
```

**方案3: 降级Vite版本（最后手段）**

```bash
# 如果方案1和2都失败，考虑降级Vite
npm install vite@^5.4.0 --save-dev

# 验证版本
npm list vite
# 应该显示: vite@5.4.x
```

### 版本兼容性矩阵

| Vite版本 | Apollo Client v4 | 兼容性 | 备注 |
|---------|-----------------|--------|------|
| Vite 5.x | 4.1.6 | ✅ 完全兼容 | 推荐配置，零问题 |
| Vite 6.x | 4.1.6 | ⚠️ 基本兼容 | 需要额外optimizeDeps配置 |
| Vite 7.x | 4.1.6 | ⚠️ 潜在问题 | 需要完整optimizeDeps，仍可能有风险 |

**当前项目状态**: Vite 7.3.1 + Apollo Client 4.1.6 → ⚠️ 中等风险

### 测试验证

**验证步骤1: 开发环境测试**

```bash
cd frontend

# 1. 清理Vite缓存
rm -rf node_modules/.vite

# 2. 启动开发服务器
npm run dev

# 3. 验证：检查控制台无模块解析错误
# 4. 验证：GraphQL页面正常加载
```

**验证步骤2: 生产构建测试**

```bash
# 1. 生产构建
npm run build

# 2. 检查构建输出
ls -lh dist/assets/js/

# 3. 验证：构建成功，无错误
# 4. 验证：生成的chunk包含Apollo Client代码
# 5. 验证：没有警告关于模块解析失败
```

**验证步骤3: GraphQL功能测试**

```bash
# 测试GraphQL页面
# 访问：http://localhost:5173/games-graphql
# 访问：http://localhost:5173/parameters-graphql
# 访问：http://localhost:5173/events-graphql

# 验证：
# ✅ 页面正常加载
# ✅ GraphQL查询成功执行
# ✅ 数据正确显示
# ✅ 控制台无错误
```

### 风险评估

**当前配置风险等级**: ⚠️ **中等**

**风险因素**:
1. Vite 7.x是较新版本，与Apollo Client v4的兼容性未充分验证
2. 当前optimizeDeps配置可能不完整
3. 生产构建可能出现意外的模块解析错误

**缓解措施**:
1. ✅ 实施推荐的optimizeDeps配置增强
2. ✅ 执行完整的测试验证步骤
3. ✅ 监控生产环境日志，检查模块解析错误
4. ⚠️ 如果问题持续，考虑降级到Vite 5.x

### 预防措施

**代码审查清单**:
- [ ] vite.config.ts中optimizeDeps配置是否完整？
- [ ] 是否包含所有Apollo Client子模块？
- [ ] 是否测试了开发环境和生产构建？
- [ ] 是否验证了GraphQL功能正常工作？

**监控检查**:
- [ ] 生产环境错误日志监控
- [ ] 用户反馈收集（GraphQL功能问题）
- [ ] 定期验证构建输出
- [ ] 关注Vite和Apollo Client的更新

### 后续建议

**短期（立即执行）**:
1. ✅ 实施推荐的optimizeDeps配置增强
2. ✅ 清理Vite缓存并重新启动开发服务器
3. ✅ 执行完整的GraphQL功能测试

**中期（1-2周内）**:
1. ✅ 监控生产环境错误日志
2. ✅ 收集用户反馈关于GraphQL功能的问题
3. ⚠️ 如果发现问题，考虑降级Vite版本

**长期（1-2个月内）**:
1. ✅ 关注Vite和Apollo Client的更新
2. ✅ 等待Vite 7.x与Apollo Client的兼容性改进
3. ✅ 评估是否需要升级到Apollo Client v5（如果发布）

### 常见错误和解决方案

**错误1: Cannot read property of undefined**

**错误信息**:
```
Uncaught TypeError: Cannot read property 'xxx' of undefined
```

**可能原因**:
- Apollo Client子模块未正确预构建
- Vite模块解析失败

**解决方案**:
1. 实施推荐的optimizeDeps配置
2. 清理Vite缓存：`rm -rf node_modules/.vite`
3. 重启开发服务器

**错误2: Module not found: Can't resolve '@apollo/client/react'**

**错误信息**:
```
Error: Module not found: Can't resolve '@apollo/client/react'
```

**可能原因**:
- Vite配置错误
- Node.js版本不兼容

**解决方案**:
1. 检查vite.config.ts中的optimizeDeps.include配置
2. 确认Node.js版本 >= 18.0.0
3. 重新安装依赖：`rm -rf node_modules && npm install`

**错误3: GraphQL query validation error**

**错误信息**:
```
GraphQL validation error: Cannot query field "xxx" on type "Query"
```

**可能原因**:
- GraphQL schema未正确加载
- Apollo Client缓存配置问题

**解决方案**:
1. 检查GraphQL schema定义
2. 验证Apollo Client的typePolicies配置
3. 清除Apollo Client缓存：`client.clearStore()`

## React 18+ defaultProps 已废弃 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 1次 | **来源**: [Event Node Builder错误修复](./event-node-builder-errors.md), [React 18发布日志](https://react.dev/blog/2022/03/29/react-v18)

### 问题现象

**症状描述**:
- React 18+ 控制台警告：`defaultProps: Support for defaultProps will be removed from function components in a future major release`
- 函数组件使用 `defaultProps` 被标记为废弃特性
- 官方文档推荐使用 ES6 默认参数替代

**影响范围**:
- 所有使用 `defaultProps` 的函数组件
- React 18.0+ 项目

### 根本原因

**技术原因**:
- React 团队决定在未来的 major 版本中移除函数组件的 `defaultProps`
- ES6 默认参数是更符合 JavaScript 标准的做法
- `defaultProps` 在函数组件中的行为与类组件不一致，容易混淆

**错误示例**:
```typescript
// ❌ 错误：使用已废弃的 defaultProps
interface EventNodeBuilderProps {
  availableEvents?: Event[];
}

function EventNodeBuilder({ availableEvents }: EventNodeBuilderProps) {
  // 组件逻辑
  return <div>{availableEvents.length} events</div>;
}

EventNodeBuilder.defaultProps = {
  availableEvents: []  // ⚠️ React 18+ 已废弃
};
```

### 解决方案

**方案1: 使用 ES6 默认参数（推荐）**

```typescript
// ✅ 正确：使用 ES6 默认参数
interface EventNodeBuilderProps {
  availableEvents?: Event[];
}

function EventNodeBuilder({
  availableEvents = []  // ✅ ES6 默认参数
}: EventNodeBuilderProps) {
  // 组件逻辑
  return <div>{availableEvents.length} events</div>;
}

// 不再需要 defaultProps
// EventNodeBuilder.defaultProps = { ... }  // ❌ 删除
```

**方案2: 使用 TypeScript 可选链和空值合并**

```typescript
// ✅ 正确：使用可选链和空值合并
interface EventNodeBuilderProps {
  availableEvents?: Event[];
}

function EventNodeBuilder({ availableEvents }: EventNodeBuilderProps) {
  const events = availableEvents ?? [];  // ✅ 空值合并

  return <div>{events.length} events</div>;
}
```

**方案3: 使用自定义 Hook 处理复杂默认值**

```typescript
// ✅ 正确：使用 Hook 处理复杂默认值
function useEventNodeBuilderProps(props: EventNodeBuilderProps) {
  return {
    availableEvents: props.availableEvents ?? [],
    selectedEvent: props.selectedEvent ?? null,
    // ... 其他默认值
  };
}

function EventNodeBuilder(props: EventNodeBuilderProps) {
  const { availableEvents, selectedEvent } = useEventNodeBuilderProps(props);

  return <div>{availableEvents.length} events</div>;
}
```

### 迁移指南

**步骤1: 识别所有使用 defaultProps 的组件**

```bash
# 搜索所有 defaultProps 使用
grep -r "defaultProps" frontend/src/
```

**步骤2: 逐个替换为 ES6 默认参数**

```typescript
// Before:
function Component({ prop1, prop2 }) {
  return <div>{prop1} {prop2}</div>;
}
Component.defaultProps = {
  prop1: 'default1',
  prop2: 'default2'
};

// After:
function Component({
  prop1 = 'default1',
  prop2 = 'default2'
}) {
  return <div>{prop1} {prop2}</div>;
}
```

**步骤3: 验证组件行为**

```bash
# 1. 启动开发服务器
npm run dev

# 2. 检查浏览器控制台
# 应该没有 defaultProps 警告

# 3. 测试组件功能
# 确认默认值正确应用
```

### ESLint 配置（强制检测）

**安装 ESLint 插件**:
```bash
npm install --save-dev eslint-plugin-react
```

**配置 ESLint 规则** (`.eslintrc.js`):
```javascript
module.exports = {
  plugins: ['react'],
  rules: {
    'react/no-default-props': 'error',  // 禁止使用 defaultProps
    'react/no-deprecated': 'error',     // 禁止使用废弃的 React API
    'react/function-component-definition': [
      'error',
      {
        namedComponents: 'arrow-function'  // 强制使用箭头函数
      }
    ]
  }
};
```

### 代码审查清单

- [ ] 函数组件是否避免使用 `defaultProps`？
- [ ] 是否使用 ES6 默认参数 `({ prop = default })`？
- [ ] 是否为可选 props 添加了合理的默认值？
- [ ] 是否使用 TypeScript 可选链 `??` 处理 null/undefined？
- [ ] 是否运行 ESLint 检查 defaultProps 使用？

### 性能对比

**defaultProps vs ES6 默认参数**:

| 方面 | defaultProps | ES6 默认参数 |
|------|--------------|--------------|
| **性能** | 每次渲染都检查 | 只在参数为 undefined 时使用 |
| **类型安全** | TypeScript 支持较弱 | TypeScript 原生支持 |
| **可读性** | 需要查看组件定义 | 参数定义中清晰可见 |
| **维护性** | 定义分散，易遗漏 | 集中在函数签名中 |
| **未来兼容** | ❌ 将被移除 | ✅ JavaScript 标准 |

### 最佳实践示例

**简单默认值**:
```typescript
// ✅ 简单默认值：使用 ES6 默认参数
interface ButtonProps {
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
}

function Button({
  variant = 'primary',
  size = 'md'
}: ButtonProps) {
  return <button className={`btn-${variant} btn-${size}`}>Click</button>;
}
```

**复杂默认值**:
```typescript
// ✅ 复杂默认值：使用 Hook
interface EventNodeBuilderProps {
  availableEvents?: Event[];
  selectedEvent?: Event | null;
  config?: NodeConfig;
}

function useDefaultProps(props: EventNodeBuilderProps) {
  return {
    availableEvents: props.availableEvents ?? [],
    selectedEvent: props.selectedEvent ?? null,
    config: props.config ?? {
      enableValidation: true,
      maxDepth: 5,
      allowCycles: false
    }
  };
}

function EventNodeBuilder(props: EventNodeBuilderProps) {
  const { availableEvents, selectedEvent, config } = useDefaultProps(props);

  // 组件逻辑
}
```

**数组/对象默认值**:
```typescript
// ✅ 数组/对象默认值：使用箭头函数或空值合并
interface ListProps {
  items?: Array<Item>;
  options?: ListOptions;
}

function List({ items, options }: ListProps) {
  // ✅ 使用空值合并
  const safeItems = items ?? [];
  const safeOptions = options ?? DEFAULT_OPTIONS;

  return <ul>{safeItems.map(item => <li key={item.id}>{item.name}</li>)}</ul>;
}

const DEFAULT_OPTIONS: ListOptions = {
  sortable: true,
  filterable: true,
  pageSize: 10
};
```

### 相关经验

- [React Hooks规则](#react-hooks规则) - React Hooks 使用规范
- [TypeScript严格模式迁移](#typescript严格模式迁移) - TypeScript 类型安全
- [组件导出规范](#组件导出规范) - 组件定义规范

### 案例文档

- [Event Node Builder错误修复](./event-node-builder-errors.md) - defaultProps 废弃问题完整案例
- [React 18发布日志](https://react.dev/blog/2022/03/29/react-v18) - 官方说明

---

## 2026-03-04 新增：前端加载问题修复经验 ⭐ **P0重要**

### Apollo Client v4 模块结构

**问题**：从 `@apollo/client` 导入 React 组件会导致语法错误
```typescript
// ❌ 错误：Apollo Provider 导入错误
import { ApolloProvider } from "@apollo/client"; // 语法错误：模块不提供 ApolloProvider

// ✅ 正确：React 组件从 @apollo/client/react 导入
import { ApolloProvider } from "@apollo/client/react"; // 正确路径
```

**根本原因**：
- Apollo Client v4 将 React 组件单独放在 `@apollo/client/react` 子模块中
- 直接从 `@apollo/client` 导入会导致模块解析失败
- 错误信息：`does not provide an export named 'ApolloProvider'`

**修复方法**：
```typescript
// 检查所有 Apollo 相关导入
import { ApolloProvider } from "@apollo/client/react";  // ✅
import { ApolloClient } from "@apollo/client";           // ✅
import { useQuery } from "@apollo/client/react";         // ✅
```

### Vite 依赖预优化配置 ⚠️ **P0极其重要**

**问题**：Vite 依赖预构建配置不完整，导致 Apollo Client 子模块未正确优化
```typescript
// ❌ 错误配置：缺少 Apollo Client 子模块
optimizeDeps: {
  include: ['@apollo/client']  // 只包含核心，缺少子模块
}

// ✅ 正确配置：包含所有 Apollo Client 子模块
optimizeDeps: {
  include: [
    'reactflow',
    // Apollo Client 核心包
    '@apollo/client',
    '@apollo/client/react',
    // Apollo Client 链
    '@apollo/client/link/context',
    '@apollo/client/link/error',
    '@apollo/client/link/retry',
    '@apollo/client/link/http',
    // Apollo Client 工具
    '@apollo/client/utilities',
    // GraphQL（Apollo Client 的依赖）
    'graphql'
  ],
  // 添加 GraphQL 文件扩展名支持
  assetsInclude: ['**/*.graphql']
}
```

**关键发现**：
- Vite 7.x 改变了依赖预构建策略
- 必须在 `optimizeDeps.include` 中明确指定所有子模块
- 缺少子模块会导致运行时模块解析错误

### 双重问题系统性诊断 ⚠️ **P0极其重要**

**问题层级**：
```
Layer 1: 代码层 - Apollo 导入路径错误（表面问题）
Layer 2: 配置层 - CORS 未配置（根本问题）
```

**诊断策略**：
```javascript
// 1. 检查浏览器控制台错误
// ❌ 错误1：模块导入错误
// ❌ 错误2：CORS 策略阻止请求

// 2. 确认错误链
// Apollo 导入错误 → GraphQL 请求失败 → 页面卡住

// 3. 修复所有层级
// 代码层：修复导入路径
// 配置层：启用 CORS
```

**教训**：
- 需要从浏览器控制台错误中找到根本原因
- 多层问题需要系统性诊断和修复
- 只修复表面问题会导致问题持续存在

### 预防措施

**代码审查清单**：
- [ ] Apollo Client 组件是否从 `@apollo/client/react` 导入？
- [ ] Vite 配置是否包含所有 Apollo Client 子模块？
- [ ] 是否启用了 Flask-CORS 配置？
- [ ] 是否验证了前端与后端的跨域通信？

### 相关经验

- [测试指南 - React挂载诊断](./testing-guide.md#react应用挂载问题诊断) - React应用启动问题诊断
- [API设计模式 - GraphQL实施](./api-design-patterns.md#graphql实施经验) - GraphQL最佳实践
- [调试技能](./debugging-skills.md) - 前端调试方法

---

## 17个组件优化案例 ⭐ **P1重要**

**优先级**: P1 | **最后更新**: 2026-03-09 | **来源**: [17个组件优化完整报告](../reports/2026-03-07/ALL-17-COMPONENTS-OPTIMIZATION-COMPLETE.md)

### 问题现象

**症状描述**:
- 17个React组件存在性能问题
- Dashboard参数更新延迟5分钟
- 用户交互时UI卡顿
- 不必要的重新渲染导致性能下降

**影响范围**:
- 所有Dashboard相关组件
- 参数管理组件
- 事件列表组件
- Canvas组件

### 根本原因

**技术原因**:
1. **缺少React.memo** - 组件频繁重新渲染，即使props相同
2. **缺少useCallback** - 回调函数每次渲染都重新创建
3. **缺少useMemo** - 昂贵计算每次渲染都重新执行
4. **大量列表渲染** - 未使用虚拟列表处理大量数据
5. **状态管理不当** - 不必要的状态更新导致级联重新渲染

### 解决方案

**17个组件优化清单**:

**1. DashboardGraphQL.tsx** - Dashboard性能优化
```typescript
// ❌ 优化前：每次渲染都重新创建回调
function DashboardGraphQL() {
  const handleGameSelect = (gameGid) => {
    // 处理游戏选择
  };

  return <GameSelector onSelect={handleGameSelect} />;
}

// ✅ 优化后：使用useCallback
function DashboardGraphQL() {
  const handleGameSelect = useCallback((gameGid: number) => {
    setCurrentGameGid(gameGid);
    refetchGames();
  }, []);

  const pollingInterval = usePollingInterval(10000, 60000);

  const { data: gamesData } = useGames(5, 0, {
    fetchPolicy: 'cache-first',
    refetchInterval: pollingInterval,  // 智能轮询
    nextFetchPolicy: 'cache-first',
  });

  return <GameSelector onSelect={handleGameSelect} />;
}
```

**2. GameCard.tsx** - 游戏卡片组件优化
```typescript
// ✅ 使用React.memo避免不必要的重新渲染
const GameCard = React.memo<GameCardProps>(({ game, onSelect, onDelete }) => {
  return (
    <div className="game-card">
      <h3>{game.name}</h3>
      <button onClick={() => onSelect(game.gid)}>选择</button>
      <button onClick={() => onDelete(game.gid)}>删除</button>
    </div>
  );
}, (prevProps, nextProps) => {
  // 自定义比较函数：只有game.id变化时才重新渲染
  return prevProps.game.id === nextProps.game.id;
});
```

**3. ParametersList.tsx** - 参数列表优化
```typescript
// ✅ 使用useMemo缓存过滤和排序结果
function ParametersList({ parameters, filter }) {
  const filteredParameters = useMemo(() => {
    return parameters
      .filter(param => param.name.includes(filter))
      .sort((a, b) => a.name.localeCompare(b.name));
  }, [parameters, filter]);

  return (
    <ul>
      {filteredParameters.map(param => <ParameterItem key={param.id} {...param} />)}
    </ul>
  );
}
```

**4. EventList.tsx** - 事件列表虚拟化
```typescript
// ✅ 使用react-window处理大量数据
import { FixedSizeList } from 'react-window';

function EventList({ events }) {
  const Row = ({ index, style }) => (
    <div style={style}>
      <EventItem {...events[index]} />
    </div>
  );

  return (
    <FixedSizeList
      height={600}
      itemCount={events.length}
      itemSize={80}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
}
```

**5-17. 其他组件优化**:
- **FieldSelectionModal.tsx** - 使用React.memo + useCallback
- **EventNodeBuilder.tsx** - 使用ES6默认参数（避免defaultProps）
- **HqlManage.tsx** - 所有Hook在条件返回前（React Hooks规则）
- **GameManagementModal.tsx** - 使用useCallback处理事件
- **ParameterDashboard.tsx** - 使用useMemo缓存统计数据
- **CategoriesList.tsx** - 使用React.memo优化列表项
- **BatchOperations.tsx** - 使用useCallback处理批量操作
- **AlterSqlBuilder.tsx** - 使用useMemo缓存SQL构建结果
- **ApiDocs.tsx** - 直接导入（不使用lazy loading）
- **ValidationRules.tsx** - 直接导入（不使用lazy loading）
- **ParameterNetwork.tsx** - 使用useMemo缓存图数据
- **ParameterHistory.tsx** - 使用useMemo缓存历史数据
- **ParameterUsage.tsx** - 使用React.memo优化使用卡片

### 性能提升数据

**优化前 vs 优化后**:

| 组件 | 优化前渲染次数 | 优化后渲染次数 | 性能提升 |
|------|--------------|--------------|---------|
| DashboardGraphQL | 120次/分钟 | 12次/分钟 | 90% ↓ |
| GameCard | 60次/分钟 | 8次/分钟 | 87% ↓ |
| ParametersList | 45次/分钟 | 6次/分钟 | 87% ↓ |
| EventList | 100次/分钟 | 5次/分钟 | 95% ↓ |
| FieldSelectionModal | 30次/分钟 | 2次/分钟 | 93% ↓ |

**Dashboard更新延迟**:
- 优化前：5分钟（300秒）
- 优化后：10秒
- **性能提升：96.7%**

### 代码审查清单

**React优化检查**:
- [ ] 组件是否使用React.memo包装？
- [ ] 回调函数是否使用useCallback？
- [ ] 昂贵计算是否使用useMemo？
- [ ] 大列表是否使用虚拟列表（react-window）？
- [ ] Hooks调用是否在条件返回之前？
- [ ] 是否避免使用defaultProps（React 18+）？

**性能验证**:
- [ ] 是否使用React DevTools Profiler分析渲染？
- [ ] 是否测试了优化前后的渲染次数对比？
- [ ] 是否验证了用户交互响应速度？

### 最佳实践总结

**1. React.memo使用原则**:
- ✅ 组件频繁重新渲染，但props相同
- ✅ 大型列表渲染
- ✅ 复杂组件渲染
- ❌ 简单组件（渲染成本< memo成本）

**2. useCallback使用原则**:
- ✅ 回调函数传递给优化过的子组件
- ✅ 回调函数作为其他Hook的依赖
- ❌ 回调函数只在本地使用（不传递给子组件）

**3. useMemo使用原则**:
- ✅ 昂贵计算（排序、过滤、大数据处理）
- ✅ 复杂对象创建
- ❌ 简单计算（成本< useMemo成本）

**4. 虚拟列表使用原则**:
- ✅ 列表项数>100
- ✅ 列表项渲染成本高
- ❌ 列表项数<50（直接渲染更简单）

### 业务价值

- Dashboard更新延迟从5分钟缩短到10秒（96.7%提升）
- 用户获得接近实时的工作体验
- 减少服务器负载和带宽消耗
- 提升用户体验满意度

### 案例文档

- [17个组件优化完整报告](../reports/2026-03-07/ALL-17-COMPONENTS-OPTIMIZATION-COMPLETE.md)
- [Dashboard实时优化报告](../reports/2026-03-07/DASHBOARD-REALTIME-OPTIMIZATION-REPORT.md)
- [React性能优化模式](./performance-patterns.md#react性能优化)

---

## 相关经验文档

- [测试指南 - E2E测试](./testing-guide.md#e2e测试) - React组件E2E测试方法
- [调试技能 - 并行开发](./debugging-skills.md#并行开发策略) - 并行开发具体方法
- [项目管理 - 并行开发策略](./project-management.md#并行开发策略) - 项目级并行开发
- [调试技能](./debugging-skills.md) - React组件调试方法
