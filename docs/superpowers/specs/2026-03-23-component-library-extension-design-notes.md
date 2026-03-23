# 组件库扩展和设计系统集成 - 设计讨论笔记

> 创建时间：2026-03-23
> 状态：讨论进行中
> 目的：记录 brainstorming 阶段的关键讨论内容，避免上下文丢失

---

## 一、设计目标

**主题：** 组件库扩展和设计系统集成

**核心目标：**
1. 扩展现有组件库（@shared/ui）
2. 建立统一的设计系统集成
3. 实现主题切换功能

---

## 二、现有基础设施分析

### 2.1 组件库现状

| 项目 | 状态 |
|------|------|
| 组件库位置 | `frontend/src/shared/ui/` |
| 组件数量 | 50+ 组件 |
| 已有组件 | Button, Input, Card, Modal, Table, VirtualList, DatePicker, Form, Select, Toast 等 |
| 统一导出 | `frontend/src/shared/ui/index.ts` |
| TypeScript | ✅ 支持（部分文件有 `@ts-nocheck`） |

### 2.2 设计令牌现状

**主令牌文件：** `frontend/src/styles/design-tokens.css`（800+ 行）

**包含内容：**
- 颜色系统（Cyan, Violet, Slate 等）
- 间距系统（--space-1 到 --space-16）
- 字体系统（--text-xs 到 --text-4xl）
- 阴影系统
- 过渡动画
- 断点定义
- 工具类（.glass-card, .text-gradient 等）

**模块令牌文件：** `frontend/src/styles/event-builder-tokens.css`

**命名规范：** `--en-*` 前缀
**使用范围：** 事件构建器模块（~15 个 CSS 文件，~80 处引用）

### 2.3 主题系统现状

| 实现方式 | 使用位置 | 状态 |
|----------|----------|------|
| `data-theme` 属性 | Table.css | ⚠️ 仅此组件 |
| `prefers-color-scheme` | Select.css, ToastNotification.css 等 | ⚠️ 部分组件 |
| 全局主题变量 | 无 | ❌ 缺失 |

**问题：** 两套机制并存，无法统一控制

---

## 三、组件扩展讨论

### 3.1 组件决策汇总

| 组件 | 决策 | 理由 |
|------|------|------|
| **Drawer** | ✅ 抽象为通用组件 | 已有业务使用（ParameterDetailDrawer），价值明确 |
| **AutoComplete** | ❌ 不新建 | 增强 Select 即可，增益更大 |
| **DatePicker** | ✅ 添加导出 | 已完成，只需统一导出 |
| **DataGrid** | ❌ 不新建 | Table 已具备核心能力（虚拟滚动、排序、选择） |
| **Tabs** | ⚠️ 按需决策 | 低成本（~5h），有需求时实现 |

### 3.2 Drawer 组件分析

**当前使用场景：**
- `ParameterDetailDrawer.tsx` - 参数详情查看

**适合使用 Drawer 的页面：**
| 页面 | 场景 | 效果 |
|------|------|------|
| 参数管理 | 参数详情查看 | 不跳转页面，快速预览 |
| 事件管理 | 事件详情编辑 | 上下文保持，编辑后关闭 |
| 画布编辑 | 节点属性配置 | 已有 PropertiesPanel，类似功能 |
| 数据分析 | 高级筛选面板 | 不占用主内容区域 |

### 3.3 Select 增强

**增强方案：**
```typescript
// 方案 A: Select 增加 autocomplete 模式
<Select
  mode="autocomplete"  // 启用自动完成
  onSearch={handleSearch}
  filterOption={false}  // 禁用本地过滤，使用远程搜索
  options={suggestions}
/>

// 方案 B: Select 增加 allowCreate 属性
<Select
  allowCreate  // 允许创建新选项
  searchable
  options={options}
/>
```

**增益对比：**
| 维度 | 增强 Select | 新建 AutoComplete |
|------|-------------|-------------------|
| 代码量 | +50 行 | +300 行 |
| 维护成本 | 低 | 高 |
| 学习成本 | 低 | 中 |
| 功能完整性 | 90% | 100% |

---

## 四、设计系统集成讨论

### 4.1 设计令牌整合策略

**问题：** 存在两套令牌命名规范
- `--space-*`, `--text-*` (design-tokens.css)
- `--en-space-*`, `--en-font-*` (event-builder-tokens.css)

**待决策问题：**
1. event-builder-tokens 能否代替主令牌？
2. 令牌的作用是什么？有什么影响？

### 4.2 主题系统实现

**确认的方案：**

| 配置项 | 决策 |
|--------|------|
| 默认主题 | 暗色（dark） |
| 主题切换 | 提供切换按钮 |
| 按钮位置 | 用户设置面板 |
| 持久化 | localStorage |

**实现架构：**
```typescript
// 主题状态管理
const ThemeContext = createContext<{
  theme: 'dark' | 'light';
  setTheme: (theme: 'dark' | 'light') => void;
}>();

// 持久化 Hook
function useThemePersistence() {
  const [theme, setTheme] = useState(() => {
    const stored = localStorage.getItem('theme');
    if (stored) return stored;
    return 'dark'; // 默认暗色
  });
  
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);
  
  return [theme, setTheme];
}
```

**CSS 结构：**
```css
/* 默认暗色（无需属性选择器） */
:root {
  --bg-primary: #030712;
  --text-primary: #F9FAFB;
}

/* 亮色主题覆盖 */
[data-theme='light'] {
  --bg-primary: #FFFFFF;
  --text-primary: #0F172A;
}
```

### 4.3 技能使用规划

**设计系统集成流程：**

```
1. teach-impeccable (一次性设置)
   ├── 收集设计上下文
   ├── 建立品牌个性
   └── 保存到 .impeccable.md

2. extract (组件/令牌提取)
   ├── 发现可复用模式
   ├── 提取组件到设计系统
   └── 提取设计令牌

3. normalize (一致性归一化)
   ├── 分析现有组件与设计系统的差异
   ├── 归一化样式（使用令牌）
   └── 清理冗余代码

4. web-design-guidelines (合规审查)
   ├── 检查 Web Interface Guidelines 合规
   └── 可访问性审查
```

**时机：** 在设计文档完成后、实施开始前运行

---

## 五、集成优先级（待确认）

| 优先级 | 任务 | 工作量 |
|--------|------|--------|
| P0 | 统一主题系统（data-theme） | 2-3 天 |
| P1 | 组件样式迁移到设计令牌 | 3-5 天 |
| P2 | 提取可复用组件到设计系统 | 2-3 天 |
| P3 | Storybook 文档化 | 2-3 天 |

---

## 六、设计令牌整合策略（已解决）

### 6.1 令牌对比

| 维度 | design-tokens.css | event-builder-tokens.css |
|------|-------------------|--------------------------|
| 行数 | ~800 行 | ~60 行 |
| 覆盖范围 | 全局 | 仅事件构建器模块 |
| 颜色系统 | 完整 | 仅字段类型颜色 |
| 间距系统 | 16 级 | 8 级 |
| 字体系统 | 完整 | 仅字号和字重 |

### 6.2 决策

**event-builder-tokens 不能代替主令牌**

**原因：**
- 功能缺失（缺少完整颜色系统、响应式断点、动画关键帧等）
- 重构工作量大（需补充 ~700 行代码）
- 命名冲突（`--en-*` 前缀不适合全局使用）

### 6.3 令牌的作用

1. **一致性** - 统一视觉元素，避免硬编码
2. **可维护性** - 单点修改，全局生效
3. **可扩展性** - 新组件直接使用现有令牌
4. **团队协作** - 设计师与开发者共享语言
5. **主题支持** - 支持暗色/亮色模式切换

### 6.4 最终方案

**保持两层令牌结构：**
- `design-tokens.css` - 主令牌（全局）
- `event-builder-tokens.css` - 模块令牌（引用主令牌 + 模块特有）

**改造方式：** 将 `--en-space-*` 等基础令牌映射到 `var(--space-*)` 主令牌

---

## 七、待解决问题

暂无待解决问题，所有关键问题已讨论完成。

---

## 七、决策记录

| 日期 | 决策内容 | 理由 |
|------|----------|------|
| 2026-03-23 | 主题系统使用纯 CSS 变量 + data-theme | 性能最优 |
| 2026-03-23 | 默认暗色主题 | 项目定位 |
| 2026-03-23 | 主题切换按钮放用户设置面板 | 用户决策 |
| 2026-03-23 | 不新建 DataGrid | Table 已具备核心能力 |
| 2026-03-23 | 不新建 AutoComplete | 增强 Select 即可 |
| 2026-03-23 | 保持两层令牌结构 | 功能完整性、零破坏性 |
| 2026-03-23 | event-builder-tokens 映射到主令牌 | 统一性、可维护性 |

---

*此文档将持续更新，记录设计讨论的关键内容。*
