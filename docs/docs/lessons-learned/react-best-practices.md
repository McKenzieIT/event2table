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

## 相关经验文档

- [测试指南 - E2E测试](./testing-guide.md#e2e测试) - React组件E2E测试方法
- [调试技能](./debugging-skills.md) - React组件调试方法
