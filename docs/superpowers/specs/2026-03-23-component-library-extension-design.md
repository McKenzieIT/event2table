# 组件库扩展与设计系统集成设计规格

> **文档版本**: 1.0  
> **创建日期**: 2026-03-23  
> **作者**: Aone Copilot  
> **状态**: 待审查

## 1. 概述

### 1.1 目标

扩展现有组件库（`@shared/ui`），建立统一的设计系统集成，实现主题切换功能，将工期从 6-8 天缩短到 1.5 天。

### 1.2 范围

- 设计令牌整合与统一
- 主题系统实现（暗色默认，支持亮色切换）
- Drawer 组件抽象
- Select 组件增强（autocomplete 模式）
- 3 Subagent 并行执行策略

### 1.3 预期成果

- 统一的设计令牌系统
- 可切换的暗色/亮色主题
- 可复用的 Drawer 组件
- 支持远程搜索的 Select 组件
- 预计工期：1.5 天

---

## 2. 架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                     应用层                               │
│  (Pages, Features, Business Components)                 │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                   组件库层                               │
│  @shared/ui (Drawer, Select, Toast, Modal, etc.)       │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                   主题系统层                             │
│  ThemeProvider, useTheme, ThemeToggle                   │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                   设计令牌层                             │
│  design-tokens.css, event-builder-tokens.css           │
└─────────────────────────────────────────────────────────┘
```

### 2.2 文件结构

```
frontend/src/
├── styles/
│   ├── design-tokens.css          # 主设计令牌（扩展亮色主题）
│   └── event-builder-tokens.css   # 模块令牌（映射到主令牌）
├── shared/
│   ├── ui/
│   │   ├── Drawer/                # 新增 Drawer 组件
│   │   │   ├── Drawer.tsx
│   │   │   ├── Drawer.css
│   │   │   └── index.ts
│   │   ├── Select/                # 增强 Select 组件
│   │   │   ├── Select.tsx
│   │   │   ├── Select.css
│   │   │   └── index.ts
│   │   └── index.ts               # 统一导出
│   └── theme/
│       ├── ThemeProvider.tsx      # 主题上下文
│       ├── ThemeToggle.tsx        # 主题切换组件
│       └── index.ts
└── app/
    └── App.tsx                    # 集成 ThemeProvider
```

---

## 3. 主题系统设计

### 3.1 ThemeProvider 实现

```typescript
// frontend/src/shared/theme/ThemeProvider.tsx
import React, { createContext, useContext, useState, useEffect, React.ReactNode } from 'react';

interface ThemeContextValue {
  theme: 'dark' | 'light';
  setTheme: (theme: 'dark' | 'light') => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

interface ThemeProviderProps {
  children: React.ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    // 优先级：localStorage > 默认暗色
    const stored = localStorage.getItem('theme');
    if (stored === 'light' || stored === 'dark') return stored;
    return 'dark';
  });

  useEffect(() => {
    // 设置 data-theme 属性
    document.documentElement.setAttribute('data-theme', theme);
    // 持久化到 localStorage
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(t => t === 'dark' ? 'light' : 'dark');

  return (
    <ThemeContext.Provider value={{ theme, setTheme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};
```

### 3.2 CSS 主题变量

```css
/* frontend/src/styles/design-tokens.css */

/* 默认暗色（无需属性选择器） */
:root {
  /* 背景色 */
  --bg-primary: #030712;
  --bg-secondary: #0F172A;
  --bg-tertiary: #1E293B;
  --bg-overlay: rgba(0, 0, 0, 0.5);
  
  /* 文字色 */
  --text-primary: #F9FAFB;
  --text-secondary: #D1D5DB;
  --text-muted: #9CA3AF;
  --text-inverse: #0F172A;
  
  /* 边框色 */
  --border-default: #374151;
  --border-muted: #1F2937;
  --border-focus: #3B82F6;
  
  /* 交互色 */
  --interactive-primary: #3B82F6;
  --interactive-secondary: #6366F1;
  --interactive-success: #10B981;
  --interactive-warning: #F59E0B;
  --interactive-error: #EF4444;
  
  /* 阴影 */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.4);
}

/* 亮色主题覆盖 */
[data-theme='light'] {
  --bg-primary: #FFFFFF;
  --bg-secondary: #F9FAFB;
  --bg-tertiary: #F3F4F6;
  --bg-overlay: rgba(0, 0, 0, 0.3);
  
  --text-primary: #0F172A;
  --text-secondary: #374151;
  --text-muted: #6B7280;
  --text-inverse: #F9FAFB;
  
  --border-default: #E5E7EB;
  --border-muted: #F3F4F6;
  --border-focus: #3B82F6;
  
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.15);
}
```

### 3.3 ThemeToggle 组件

```typescript
// frontend/src/shared/theme/ThemeToggle.tsx
import React from 'react';
import { useTheme } from './ThemeProvider';
import './ThemeToggle.css';

export const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="theme-toggle">
      <span className="theme-toggle__label">主题模式</span>
      <button 
        className="theme-toggle__button"
        onClick={toggleTheme}
        aria-label={`切换到${theme === 'dark' ? '亮色' : '暗色'}模式`}
      >
        {theme === 'dark' ? (
          <>
            <SunIcon className="theme-toggle__icon" />
            <span>亮色模式</span>
          </>
        ) : (
          <>
            <MoonIcon className="theme-toggle__icon" />
            <span>暗色模式</span>
          </>
        )}
      </button>
    </div>
  );
};

// 简单的图标组件
const SunIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="5" />
    <line x1="12" y1="1" x2="12" y2="3" />
    <line x1="12" y1="21" x2="12" y2="23" />
    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
    <line x1="1" y1="12" x2="3" y2="12" />
    <line x1="21" y1="12" x2="23" y2="12" />
    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
  </svg>
);

const MoonIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
  </svg>
);
```

---

## 4. Drawer 组件设计

### 4.1 组件 API

```typescript
// frontend/src/shared/ui/Drawer/Drawer.tsx
import React, { ReactNode, useEffect, useCallback } from 'react';
import './Drawer.css';

interface DrawerProps {
  /** 是否打开 */
  open: boolean;
  /** 关闭回调 */
  onClose: () => void;
  /** 抽屉位置 */
  position?: 'left' | 'right' | 'top' | 'bottom';
  /** 抽屉尺寸 */
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  /** 标题 */
  title?: ReactNode;
  /** 底部内容 */
  footer?: ReactNode;
  /** 点击遮罩层是否关闭 */
  closeOnOverlayClick?: boolean;
  /** 按 ESC 键是否关闭 */
  closeOnEscape?: boolean;
  /** 子元素 */
  children: ReactNode;
  /** 自定义类名 */
  className?: string;
}

export const Drawer: React.FC<DrawerProps> = ({
  open,
  onClose,
  position = 'right',
  size = 'md',
  title,
  footer,
  closeOnOverlayClick = true,
  closeOnEscape = true,
  children,
  className,
}) => {
  // ESC 键关闭
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (event.key === 'Escape' && closeOnEscape) {
      onClose();
    }
  }, [closeOnEscape, onClose]);

  useEffect(() => {
    if (open) {
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [open, handleKeyDown]);

  const handleOverlayClick = () => {
    if (closeOnOverlayClick) {
      onClose();
    }
  };

  return (
    <div className={`drawer-container ${open ? 'drawer-container--open' : ''}`}>
      {/* 遮罩层 */}
      <div 
        className={`drawer-overlay ${open ? 'drawer-overlay--open' : ''}`}
        onClick={handleOverlayClick}
        aria-hidden="true"
      />
      
      {/* 抽屉主体 */}
      <div
        className={`
          drawer 
          drawer--${position} 
          drawer--${size}
          ${open ? 'drawer--open' : ''}
          ${className || ''}
        `}
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? 'drawer-title' : undefined}
      >
        {/* 头部 */}
        {title && (
          <div className="drawer__header">
            <h2 id="drawer-title" className="drawer__title">{title}</h2>
            <button 
              className="drawer__close" 
              onClick={onClose}
              aria-label="关闭"
            >
              <CloseIcon />
            </button>
          </div>
        )}
        
        {/* 内容 */}
        <div className="drawer__body">
          {children}
        </div>
        
        {/* 底部 */}
        {footer && (
          <div className="drawer__footer">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
};

const CloseIcon: React.FC = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <line x1="18" y1="6" x2="6" y2="18" />
    <line x1="6" y1="6" x2="18" y2="18" />
  </svg>
);
```

### 4.2 尺寸定义

| Size | Width (left/right) | Height (top/bottom) |
|------|-------------------|---------------------|
| sm | 320px | 240px |
| md | 480px | 360px |
| lg | 640px | 480px |
| xl | 800px | 600px |
| full | 100% | 100% |

### 4.3 样式实现

```css
/* frontend/src/shared/ui/Drawer/Drawer.css */

.drawer-container {
  position: fixed;
  inset: 0;
  z-index: var(--z-modal, 1000);
  pointer-events: none;
  visibility: hidden;
}

.drawer-container--open {
  pointer-events: auto;
  visibility: visible;
}

/* 遮罩层 */
.drawer-overlay {
  position: absolute;
  inset: 0;
  background: var(--bg-overlay);
  opacity: 0;
  transition: opacity var(--transition-base, 200ms) var(--ease-out, ease-out);
}

.drawer-overlay--open {
  opacity: 1;
}

/* 抽屉主体 */
.drawer {
  position: absolute;
  background: var(--bg-secondary);
  box-shadow: var(--shadow-xl);
  transition: transform var(--transition-base, 200ms) var(--ease-out, ease-out);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 位置变体 */
.drawer--right {
  top: 0;
  right: 0;
  height: 100vh;
  transform: translateX(100%);
}

.drawer--left {
  top: 0;
  left: 0;
  height: 100vh;
  transform: translateX(-100%);
}

.drawer--top {
  left: 0;
  top: 0;
  width: 100vw;
  transform: translateY(-100%);
}

.drawer--bottom {
  left: 0;
  bottom: 0;
  width: 100vw;
  transform: translateY(100%);
}

/* 打开状态 */
.drawer--open.drawer--right,
.drawer--open.drawer--left {
  transform: translateX(0);
}

.drawer--open.drawer--top,
.drawer--open.drawer--bottom {
  transform: translateY(0);
}

/* 尺寸变体 - left/right */
.drawer--right.drawer--sm,
.drawer--left.drawer--sm { width: 320px; }
.drawer--right.drawer--md,
.drawer--left.drawer--md { width: 480px; }
.drawer--right.drawer--lg,
.drawer--left.drawer--lg { width: 640px; }
.drawer--right.drawer--xl,
.drawer--left.drawer--xl { width: 800px; }
.drawer--right.drawer--full,
.drawer--left.drawer--full { width: 100%; }

/* 尺寸变体 - top/bottom */
.drawer--top.drawer--sm,
.drawer--bottom.drawer--sm { height: 240px; }
.drawer--top.drawer--md,
.drawer--bottom.drawer--md { height: 360px; }
.drawer--top.drawer--lg,
.drawer--bottom.drawer--lg { height: 480px; }
.drawer--top.drawer--xl,
.drawer--bottom.drawer--xl { height: 600px; }
.drawer--top.drawer--full,
.drawer--bottom.drawer--full { height: 100%; }

/* 头部 */
.drawer__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-md, 1rem);
  border-bottom: 1px solid var(--border-muted);
}

.drawer__title {
  margin: 0;
  font-size: var(--text-lg, 1.125rem);
  font-weight: var(--font-semibold, 600);
  color: var(--text-primary);
}

.drawer__close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: var(--radius-sm, 4px);
  transition: color var(--transition-fast, 150ms), background var(--transition-fast, 150ms);
}

.drawer__close:hover {
  color: var(--text-primary);
  background: var(--bg-tertiary);
}

.drawer__close svg {
  width: 20px;
  height: 20px;
}

/* 内容 */
.drawer__body {
  flex: 1;
  padding: var(--space-md, 1rem);
  overflow-y: auto;
}

/* 底部 */
.drawer__footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--space-sm, 0.5rem);
  padding: var(--space-md, 1rem);
  border-top: 1px solid var(--border-muted);
}
```

### 4.4 迁移示例

```typescript
// 迁移前：ParameterDetailDrawer.tsx
const ParameterDetailDrawer = ({ open, onClose, paramId }) => {
  return (
    <div className="custom-drawer">
      <div className="custom-drawer__header">参数详情</div>
      <div className="custom-drawer__body">
        {/* 自定义实现 */}
      </div>
    </div>
  );
};

// 迁移后
import { Drawer } from '@shared/ui';

const ParameterDetailDrawer = ({ open, onClose, paramId }) => {
  return (
    <Drawer
      open={open}
      onClose={onClose}
      title="参数详情"
      size="lg"
    >
      <ParameterContent paramId={paramId} />
    </Drawer>
  );
};
```

---

## 5. Select 增强设计

### 5.1 增强 API

```typescript
// frontend/src/shared/ui/Select/Select.tsx
interface SelectProps {
  // 现有属性...
  
  /** 选择模式 */
  mode?: 'default' | 'autocomplete';
  
  /** 是否允许创建新选项 */
  allowCreate?: boolean;
  
  /** 远程搜索回调 */
  onSearch?: (value: string) => void;
  
  /** 是否正在加载 */
  loading?: boolean;
  
  /** 搜索防抖延迟（毫秒） */
  searchDebounce?: number;
  
  /** 无匹配选项时的提示 */
  noOptionsMessage?: string;
}
```

### 5.2 使用示例

```typescript
// 场景 1：远程搜索
<Select
  mode="autocomplete"
  onSearch={handleSearch}
  loading={isSearching}
  options={suggestions}
  placeholder="搜索事件名称..."
/>

// 场景 2：允许创建新选项
<Select
  allowCreate
  searchable
  options={existingOptions}
  placeholder="选择或创建标签..."
  onChange={handleTagChange}
/>
```

### 5.3 实现要点

```typescript
// 核心逻辑片段
const Select: React.FC<SelectProps> = ({
  mode = 'default',
  allowCreate = false,
  onSearch,
  searchDebounce = 300,
  loading = false,
  noOptionsMessage = '无匹配选项',
  // ...
}) => {
  const [searchValue, setSearchValue] = useState('');
  
  // 防抖搜索
  const debouncedSearch = useMemo(
    () => debounce((value: string) => onSearch?.(value), searchDebounce),
    [onSearch, searchDebounce]
  );

  const handleInputChange = (value: string) => {
    setSearchValue(value);
    if (mode === 'autocomplete') {
      debouncedSearch(value);
    }
  };

  // 是否显示"创建新选项"
  const showCreateOption = allowCreate && 
    searchValue && 
    !options.some(opt => opt.label === searchValue);

  return (
    <div className="select">
      {/* 输入框 */}
      <input
        value={searchValue}
        onChange={(e) => handleInputChange(e.target.value)}
        placeholder={placeholder}
      />
      
      {/* 加载指示器 */}
      {loading && <LoadingSpinner />}
      
      {/* 下拉选项 */}
      <ul className="select__options">
        {options.map(opt => (
          <li key={opt.value} onClick={() => handleSelect(opt)}>
            {opt.label}
          </li>
        ))}
        
        {/* 创建新选项 */}
        {showCreateOption && (
          <li className="select__create" onClick={handleCreate}>
            创建 "{searchValue}"
          </li>
        )}
        
        {/* 无选项提示 */}
        {!loading && options.length === 0 && (
          <li className="select__empty">{noOptionsMessage}</li>
        )}
      </ul>
    </div>
  );
};
```

---

## 6. 设计令牌整合

### 6.1 两层结构

保持现有两层结构，建立映射关系：

```css
/* frontend/src/styles/event-builder-tokens.css */

/* 映射到主令牌 */
:root {
  /* 间距映射 */
  --en-space-xs: var(--space-xs);
  --en-space-sm: var(--space-sm);
  --en-space-md: var(--space-md);
  --en-space-lg: var(--space-lg);
  
  /* 字段类型颜色（保留语义化） */
  --en-field-base: #06B6D4;
  --en-field-param: #8B5CF6;
  --en-field-event: #10B981;
  --en-field-output: #F59E0B;
}
```

### 6.2 迁移策略

1. **保留模块令牌文件**：`event-builder-tokens.css`
2. **建立映射关系**：模块令牌映射到主令牌
3. **渐进式迁移**：新组件直接使用主令牌
4. **向后兼容**：现有代码无需立即修改

---

## 7. 实施计划

### 7.1 执行时间线

```
┌─────────────────────────────────────────────────────────────┐
│ 轮次 │ 时间    │ 任务                          │ 执行方式   │
├──────┼─────────┼────────────────────────────────┼────────────┤
│ 1    │ 0-0.5h  │ teach-impeccable              │ 串行       │
│      │         │ 收集设计上下文                 │            │
├──────┼─────────┼────────────────────────────────┼────────────┤
│ 2    │ 0.5h-4h │ 设计令牌整合                   │ 3 Subagent │
│      │         │ 主题系统实现                   │ 并行       │
│      │         │ Drawer 组件抽象                │            │
├──────┼─────────┼────────────────────────────────┼────────────┤
│ 3    │ 4h-8h   │ 组件样式迁移                   │ 串行       │
│      │         │ prefers-color-scheme → data-theme │        │
├──────┼─────────┼────────────────────────────────┼────────────┤
│ 4    │ 8h-10h  │ Select 增强                   │ 串行       │
│      │         │ autocomplete 模式              │            │
├──────┼─────────┼────────────────────────────────┼────────────┤
│ 5    │ 10h-12h │ 质量保证                      │ 串行       │
│      │         │ extract → normalize → audit   │            │
└─────────────────────────────────────────────────────────────┘

总工期：约 1.5 天
```

### 7.2 技能使用时机

| 技能 | 时机 | 目的 |
|------|------|------|
| `teach-impeccable` | 轮次 1 | 收集设计上下文，建立品牌个性 |
| `extract` | 轮次 5 | 提取可复用模式到设计系统 |
| `normalize` | 轮次 5 | 归一化组件样式一致性 |
| `web-design-guidelines` | 轮次 5 | Web Interface Guidelines 合规审查 |

### 7.3 测试策略

| 测试类型 | 覆盖范围 | 工具 |
|----------|----------|------|
| 单元测试 | ThemeProvider, Drawer, Select | Jest + React Testing Library |
| 集成测试 | 主题切换流程 | Jest |
| E2E 测试 | 用户设置面板主题切换 | event2table-universal-test |
| 视觉回归 | 暗色/亮色主题对比 | agent-browser |

---

## 8. 风险与缓解

| 风险 | 概率 | 缓解措施 |
|------|------|----------|
| 组件样式迁移遗漏 | 中 | 使用 grep 全局搜索 `prefers-color-scheme` |
| 主题切换闪烁 | 低 | 在 `<html>` 上设置 `data-theme` 属性 |
| Drawer 动画性能 | 低 | 使用 `transform` 而非 `left/right` |
| Select 搜索防抖 | 低 | 使用成熟的 debounce 实现 |

---

## 9. 决策记录

### 9.1 为什么选择方案 A（渐进式集成）？

- **风险低**：不破坏现有功能
- **可增量**：逐步迁移，不影响开发进度
- **可验证**：每个阶段都可独立测试
- **工期短**：3 Subagent 并行加速

### 9.2 为什么选择纯 CSS 变量 + data-theme？

- **简单**：无需额外依赖
- **性能好**：CSS 变量切换无运行时开销
- **兼容性好**：现代浏览器全面支持
- **可调试**：DevTools 直接可见

### 9.3 为什么主题切换放在设置面板？

- **不干扰**：不占用导航栏空间
- **符合预期**：用户习惯在设置中找主题选项
- **可扩展**：未来可添加更多主题选项

---

## 10. 附录

### 10.1 相关文件

- 备份文档：`docs/superpowers/specs/2026-03-23-component-library-extension-design-notes.md`
- 设计令牌：`frontend/src/styles/design-tokens.css`
- 组件库：`frontend/src/shared/ui/index.ts`

### 10.2 参考资料

- [Web Interface Guidelines](https://github.com/vercel-labs/web-interface-guidelines)
- [React Context API](https://react.dev/reference/react/createContext)
- [CSS Custom Properties](https://developer.mozilla.org/en-US/docs/Web/CSS/--*)

---

**文档结束**
