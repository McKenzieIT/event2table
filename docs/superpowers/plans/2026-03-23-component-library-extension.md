# 组件库扩展和设计系统集成 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 扩展现有组件库(@shared/ui)，添加 Drawer 组件，增强 Select 组件，建立统一的设计系统集成，实现主题切换功能（暗色默认，支持亮色切换）

**Architecture:** 采用渐进式集成策略，保留现有两层设计令牌结构，通过 CSS 变量 + data-theme 属性实现主题切换。使用 3 Subagent 并行执行轮次 2 的独立任务（设计令牌整合、主题系统实现、Drawer 组件抽象）。

**Tech Stack:** React 18, TypeScript, CSS Variables, lodash.debounce, Jest, React Testing Library

**Spec Document:** `docs/superpowers/specs/2026-03-23-component-library-extension-design.md`

---

## 文件结构

### 新建文件
| 文件路径 | 职责 |
|----------|------|
| `frontend/src/shared/ui/Drawer/Drawer.tsx` | Drawer 组件实现 |
| `frontend/src/shared/ui/Drawer/Drawer.css` | Drawer 样式 |
| `frontend/src/shared/ui/Drawer/index.ts` | Drawer 导出 |
| `frontend/src/shared/ui/Theme/ThemeProvider.tsx` | 主题 Context Provider |
| `frontend/src/shared/ui/Theme/ThemeToggle.tsx` | 主题切换组件 |
| `frontend/src/shared/ui/Theme/index.ts` | Theme 模块导出 |
| `frontend/src/shared/ui/Select/Select.css` | Select 增强样式 |
| `frontend/src/shared/ui/__tests__/ThemeProvider.test.tsx` | ThemeProvider 单元测试 |
| `frontend/src/shared/ui/__tests__/Drawer.test.tsx` | Drawer 单元测试 |
| `frontend/src/shared/ui/__tests__/Select.test.tsx` | Select 单元测试 |

### 修改文件
| 文件路径 | 修改内容 |
|----------|----------|
| `frontend/src/styles/design-tokens.css` | 添加亮色主题变量，修改暗色为默认 |
| `frontend/src/styles/event-builder-tokens.css` | 建立到主令牌的映射 |
| `frontend/src/shared/ui/Select/Select.tsx` | 添加 autocomplete 模式和 allowCreate |
| `frontend/src/shared/ui/index.ts` | 导出新组件 |
| `frontend/src/app/App.tsx` | 包装 ThemeProvider |
| `frontend/src/analytics/components/parameters/ParameterDetailDrawer.tsx` | 迁移到通用 Drawer |
| `frontend/src/shared/ui/Modal/Modal.css` | 迁移 prefers-color-scheme |
| `frontend/src/shared/ui/Card/Card.css` | 迁移 prefers-color-scheme |

---

## 轮次 1: teach-impeccable（设计上下文收集）

### Task 1.1: 运行 teach-impeccable

**Files:**
- Create: `.impeccable.md`
- Modify: `.github/copilot-instructions.md`（可选）

- [ ] **Step 1: 运行 teach-impeccable skill**

执行 skill: `teach-impeccable`

按照 skill 流程：
1. 探索代码库（README、package.json、现有组件、设计令牌）
2. 提出 UX 聚焦问题（用户、品牌、审美、无障碍）
3. 编写设计上下文到 `.impeccable.md`

- [ ] **Step 2: 验证设计上下文文件**

Run: `cat .impeccable.md`
Expected: 包含 Users、Brand Personality、Aesthetic Direction、Design Principles 四个部分

- [ ] **Step 3: 提交**

```bash
git add .impeccable.md
git commit -m "docs: add design context via teach-impeccable"
git tag v-round-1-complete
```

---

## 轮次 2: 3 Subagent 并行执行

> **注意：** 此轮次使用 3 个独立的 Subagent 并行执行，每个 Subagent 负责一个独立任务。

### Task 2.1: 设计令牌整合（Subagent A）

**Files:**
- Modify: `frontend/src/styles/design-tokens.css`
- Modify: `frontend/src/styles/event-builder-tokens.css`

- [ ] **Step 1: 扩展 design-tokens.css 亮色主题**

```css
/* frontend/src/styles/design-tokens.css */

/* 暗色主题（默认） */
:root {
  /* 颜色 */
  --color-bg-primary: #0f172a;
  --color-bg-secondary: #1e293b;
  --color-bg-tertiary: #334155;
  --color-text-primary: #f8fafc;
  --color-text-secondary: #cbd5e1;
  --color-text-muted: #94a3b8;
  --color-border-default: #334155;
  --color-border-focus: #3b82f6;
  
  /* 间距 */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  --space-xl: 2rem;
  
  /* 字体 */
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  
  /* 圆角 */
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
  
  /* 阴影 */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.3);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.3);
  
  /* 过渡 */
  --transition-fast: 150ms ease;
  --transition-normal: 250ms ease;
  --transition-slow: 350ms ease;
  
  /* z-index */
  --z-dropdown: 100;
  --z-modal: 200;
  --z-drawer: 250;
  --z-toast: 300;
}

/* 亮色主题 */
[data-theme='light'] {
  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f8fafc;
  --color-bg-tertiary: #f1f5f9;
  --color-text-primary: #0f172a;
  --color-text-secondary: #475569;
  --color-text-muted: #94a3b8;
  --color-border-default: #e2e8f0;
  --color-border-focus: #3b82f6;
  
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
}
```

- [ ] **Step 2: 建立 event-builder-tokens.css 映射**

```css
/* frontend/src/styles/event-builder-tokens.css */

/* 映射到主令牌 */
:root {
  /* 间距映射 */
  --en-space-xs: var(--space-xs);
  --en-space-sm: var(--space-sm);
  --en-space-md: var(--space-md);
  --en-space-lg: var(--space-lg);
  
  /* 字段类型颜色（保留语义化，不映射） */
  --en-field-base: #06B6D4;
  --en-field-param: #8B5CF6;
  --en-field-event: #10B981;
  --en-field-output: #F59E0B;
}
```

- [ ] **Step 3: 验证 CSS 变量**

Run: `grep -c "var(--" frontend/src/styles/design-tokens.css`
Expected: 输出变量数量 > 20

- [ ] **Step 4: 提交**

```bash
git add frontend/src/styles/design-tokens.css frontend/src/styles/event-builder-tokens.css
git commit -m "feat(tokens): add light theme variables and token mapping"
```

---

### Task 2.2: 主题系统实现（Subagent B）

**Files:**
- Create: `frontend/src/shared/ui/Theme/ThemeProvider.tsx`
- Create: `frontend/src/shared/ui/Theme/ThemeToggle.tsx`
- Create: `frontend/src/shared/ui/Theme/index.ts`
- Create: `frontend/src/shared/ui/__tests__/ThemeProvider.test.tsx`

- [ ] **Step 1: 编写 ThemeProvider 测试**

```typescript
// frontend/src/shared/ui/__tests__/ThemeProvider.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, useTheme } from '../Theme/ThemeProvider';

const TestComponent = () => {
  const { theme, setTheme } = useTheme();
  return (
    <div>
      <span data-testid="theme">{theme}</span>
      <button onClick={() => setTheme('light')}>Light</button>
      <button onClick={() => setTheme('dark')}>Dark</button>
    </div>
  );
};

describe('ThemeProvider', () => {
  it('should default to dark theme', () => {
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );
    expect(screen.getByTestId('theme').textContent).toBe('dark');
  });

  it('should toggle theme', () => {
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );
    fireEvent.click(screen.getByText('Light'));
    expect(screen.getByTestId('theme').textContent).toBe('light');
  });

  it('should persist theme to localStorage', () => {
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );
    fireEvent.click(screen.getByText('Light'));
    expect(localStorage.getItem('theme')).toBe('light');
  });
});
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd frontend && npm test -- --testPathPattern="ThemeProvider" --passWithNoTests`
Expected: FAIL - Cannot find module '../Theme/ThemeProvider'

- [ ] **Step 3: 实现 ThemeProvider**

```typescript
// frontend/src/shared/ui/Theme/ThemeProvider.tsx
import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';

type Theme = 'dark' | 'light';

interface ThemeContextValue {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
  defaultTheme?: Theme;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ 
  children, 
  defaultTheme = 'dark' 
}) => {
  const [theme, setThemeState] = useState<Theme>(() => {
    if (typeof window === 'undefined') return defaultTheme;
    const stored = localStorage.getItem('theme');
    if (stored === 'light' || stored === 'dark') return stored;
    return defaultTheme;
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextValue => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
```

- [ ] **Step 4: 实现 ThemeToggle**

```typescript
// frontend/src/shared/ui/Theme/ThemeToggle.tsx
import React from 'react';
import { useTheme } from './ThemeProvider';
import './ThemeToggle.css';

export const ThemeToggle: React.FC = () => {
  const { theme, setTheme } = useTheme();

  const handleToggle = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  return (
    <button 
      className="theme-toggle" 
      onClick={handleToggle}
      aria-label={`切换到${theme === 'dark' ? '亮色' : '暗色'}主题`}
    >
      <span className="theme-toggle__icon">
        {theme === 'dark' ? '☀️' : '🌙'}
      </span>
      <span className="theme-toggle__label">
        {theme === 'dark' ? '亮色模式' : '暗色模式'}
      </span>
    </button>
  );
};
```

```css
/* frontend/src/shared/ui/Theme/ThemeToggle.css */

.theme-toggle {
  display: flex;
  align-items: center;
  gap: var(--space-sm, 0.5rem);
  padding: var(--space-sm, 0.5rem) var(--space-md, 1rem);
  background: var(--color-bg-secondary, #1e293b);
  border: 1px solid var(--color-border-default, #334155);
  border-radius: var(--radius-md, 6px);
  color: var(--color-text-primary, #f8fafc);
  cursor: pointer;
  transition: all var(--transition-fast, 150ms);
}

.theme-toggle:hover {
  background: var(--color-bg-tertiary, #334155);
  border-color: var(--color-border-focus, #3b82f6);
}

.theme-toggle__icon {
  font-size: 1.25rem;
}

.theme-toggle__label {
  font-size: var(--font-size-sm, 0.875rem);
}
```

- [ ] **Step 5: 创建 index.ts 导出**

```typescript
// frontend/src/shared/ui/Theme/index.ts
export { ThemeProvider, useTheme } from './ThemeProvider';
export { ThemeToggle } from './ThemeToggle';
```

- [ ] **Step 6: 运行测试确认通过**

Run: `cd frontend && npm test -- --testPathPattern="ThemeProvider" --passWithNoTests`
Expected: PASS - 3 tests passed

- [ ] **Step 7: 提交**

```bash
git add frontend/src/shared/ui/Theme/ frontend/src/shared/ui/__tests__/ThemeProvider.test.tsx
git commit -m "feat(theme): implement ThemeProvider and ThemeToggle"
```

---

### Task 2.3: Drawer 组件抽象（Subagent C）

**Files:**
- Create: `frontend/src/shared/ui/Drawer/Drawer.tsx`
- Create: `frontend/src/shared/ui/Drawer/Drawer.css`
- Create: `frontend/src/shared/ui/Drawer/index.ts`
- Create: `frontend/src/shared/ui/__tests__/Drawer.test.tsx`

- [ ] **Step 1: 编写 Drawer 测试**

```typescript
// frontend/src/shared/ui/__tests__/Drawer.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Drawer } from '../Drawer/Drawer';

describe('Drawer', () => {
  it('should not be visible when closed', () => {
    render(
      <Drawer isOpen={false} onClose={() => {}}>
        <div>Content</div>
      </Drawer>
    );
    expect(screen.queryByText('Content')).not.toBeVisible();
  });

  it('should be visible when open', () => {
    render(
      <Drawer isOpen={true} onClose={() => {}}>
        <div>Content</div>
      </Drawer>
    );
    expect(screen.getByText('Content')).toBeVisible();
  });

  it('should call onClose when overlay clicked', () => {
    const onClose = jest.fn();
    render(
      <Drawer isOpen={true} onClose={onClose}>
        <div>Content</div>
      </Drawer>
    );
    fireEvent.click(screen.getByTestId('drawer-overlay'));
    expect(onClose).toHaveBeenCalled();
  });

  it('should call onClose when Escape pressed', () => {
    const onClose = jest.fn();
    render(
      <Drawer isOpen={true} onClose={onClose}>
        <div>Content</div>
      </Drawer>
    );
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(onClose).toHaveBeenCalled();
  });
});
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd frontend && npm test -- --testPathPattern="Drawer" --passWithNoTests`
Expected: FAIL - Cannot find module '../Drawer/Drawer'

- [ ] **Step 3: 实现 Drawer 组件**

```typescript
// frontend/src/shared/ui/Drawer/Drawer.tsx
import React, { useEffect, useCallback, ReactNode } from 'react';
import './Drawer.css';

type DrawerPlacement = 'left' | 'right' | 'top' | 'bottom';

interface DrawerProps {
  /** 是否打开 */
  isOpen: boolean;
  /** 关闭回调 */
  onClose: () => void;
  /** 子元素 */
  children: ReactNode;
  /** 标题 */
  title?: string;
  /** 位置 */
  placement?: DrawerPlacement;
  /** 宽度（left/right） */
  width?: string;
  /** 高度（top/bottom） */
  height?: string;
  /** 是否显示遮罩 */
  mask?: boolean;
  /** 点击遮罩是否关闭 */
  maskClosable?: boolean;
  /** 自定义类名 */
  className?: string;
}

export const Drawer: React.FC<DrawerProps> = ({
  isOpen,
  onClose,
  children,
  title,
  placement = 'right',
  width = '400px',
  height = '300px',
  mask = true,
  maskClosable = true,
  className,
}) => {
  // ESC 键关闭
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    },
    [isOpen, onClose]
  );

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  // 打开时禁止 body 滚动
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  const handleMaskClick = () => {
    if (maskClosable) {
      onClose();
    }
  };

  const drawerStyle: React.CSSProperties = {
    width: placement === 'left' || placement === 'right' ? width : undefined,
    height: placement === 'top' || placement === 'bottom' ? height : undefined,
  };

  return (
    <div
      className={`drawer ${isOpen ? 'drawer--open' : ''} ${className || ''}`}
      role="dialog"
      aria-modal="true"
    >
      {/* 遮罩 */}
      {mask && (
        <div
          data-testid="drawer-overlay"
          className="drawer__mask"
          onClick={handleMaskClick}
        />
      )}

      {/* 抽屉内容 */}
      <div
        className={`drawer__content drawer__content--${placement}`}
        style={drawerStyle}
      >
        {/* 头部 */}
        {title && (
          <div className="drawer__header">
            <h3 className="drawer__title">{title}</h3>
            <button
              className="drawer__close"
              onClick={onClose}
              aria-label="关闭"
            >
              ✕
            </button>
          </div>
        )}

        {/* 内容 */}
        <div className="drawer__body">{children}</div>
      </div>
    </div>
  );
};
```

```css
/* frontend/src/shared/ui/Drawer/Drawer.css */

.drawer {
  position: fixed;
  inset: 0;
  z-index: var(--z-drawer, 250);
  pointer-events: none;
  opacity: 0;
  transition: opacity var(--transition-normal, 250ms);
}

.drawer--open {
  pointer-events: auto;
  opacity: 1;
}

.drawer__mask {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
}

.drawer__content {
  position: absolute;
  background: var(--color-bg-secondary, #1e293b);
  box-shadow: var(--shadow-lg);
  transition: transform var(--transition-normal, 250ms);
}

/* 位置变体 */
.drawer__content--left {
  top: 0;
  left: 0;
  height: 100%;
  transform: translateX(-100%);
}

.drawer__content--right {
  top: 0;
  right: 0;
  height: 100%;
  transform: translateX(100%);
}

.drawer__content--top {
  top: 0;
  left: 0;
  width: 100%;
  transform: translateY(-100%);
}

.drawer__content--bottom {
  bottom: 0;
  left: 0;
  width: 100%;
  transform: translateY(100%);
}

.drawer--open .drawer__content {
  transform: translateX(0) translateY(0);
}

.drawer__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-md, 1rem);
  border-bottom: 1px solid var(--color-border-default, #334155);
}

.drawer__title {
  margin: 0;
  font-size: var(--font-size-lg, 1.125rem);
  font-weight: 600;
  color: var(--color-text-primary, #f8fafc);
}

.drawer__close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm, 4px);
  color: var(--color-text-muted, #94a3b8);
  cursor: pointer;
  transition: all var(--transition-fast, 150ms);
}

.drawer__close:hover {
  background: var(--color-bg-tertiary, #334155);
  color: var(--color-text-primary, #f8fafc);
}

.drawer__body {
  padding: var(--space-md, 1rem);
  overflow-y: auto;
}
```

- [ ] **Step 4: 创建 index.ts 导出**

```typescript
// frontend/src/shared/ui/Drawer/index.ts
export { Drawer } from './Drawer';
```

- [ ] **Step 5: 运行测试确认通过**

Run: `cd frontend && npm test -- --testPathPattern="Drawer" --passWithNoTests`
Expected: PASS - 4 tests passed

- [ ] **Step 6: 提交**

```bash
git add frontend/src/shared/ui/Drawer/ frontend/src/shared/ui/__tests__/Drawer.test.tsx
git commit -m "feat(ui): implement Drawer component"
```

---

## 轮次 3: 组件样式迁移

### Task 3.1: 迁移 design-tokens.css prefers-color-scheme

**Files:**
- Modify: `frontend/src/styles/design-tokens.css`

- [ ] **Step 1: 查找所有 prefers-color-scheme 使用**

Run: `grep -rn "prefers-color-scheme" frontend/src --include="*.css"`
Expected: 列出所有使用位置

- [ ] **Step 2: 替换 design-tokens.css 中的 prefers-color-scheme**

将 `@media (prefers-color-scheme: dark)` 替换为 `:root`（暗色默认）
将 `@media (prefers-color-scheme: light)` 替换为 `[data-theme='light']`

- [ ] **Step 3: 迁移 Modal.css**

```css
/* frontend/src/shared/ui/Modal/Modal.css */
/* 替换前 */
@media (prefers-color-scheme: dark) { ... }

/* 替换后 */
.modal { /* 使用 CSS 变量 */ }
```

- [ ] **Step 4: 迁移 Card.css**

```css
/* frontend/src/shared/ui/Card/Card.css */
/* 替换前 */
@media (prefers-color-scheme: dark) { ... }

/* 替换后 */
.card { /* 使用 CSS 变量 */ }
```

- [ ] **Step 5: 验证迁移完成**

Run: `grep -rn "prefers-color-scheme" frontend/src --include="*.css"`
Expected: 无输出

- [ ] **Step 6: 提交**

```bash
git add frontend/src/styles/design-tokens.css frontend/src/shared/ui/Modal/Modal.css frontend/src/shared/ui/Card/Card.css
git commit -m "refactor(styles): migrate prefers-color-scheme to data-theme"
git tag v-round-3-complete
```

---

## 轮次 4: Select 增强

### Task 4.1: 增强 Select 组件

**Files:**
- Modify: `frontend/src/shared/ui/Select/Select.tsx`
- Create: `frontend/src/shared/ui/Select/Select.css`
- Create: `frontend/src/shared/ui/__tests__/Select.test.tsx`

- [ ] **Step 1: 安装 lodash.debounce 依赖**

Run: `cd frontend && npm install lodash.debounce && npm install -D @types/lodash.debounce`
Expected: 安装成功

- [ ] **Step 2: 编写 Select 增强测试**

```typescript
// frontend/src/shared/ui/__tests__/Select.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Select } from '../Select/Select';

describe('Select enhanced features', () => {
  const mockOptions = [
    { value: '1', label: 'Option 1' },
    { value: '2', label: 'Option 2' },
  ];

  it('should filter options in default mode', () => {
    render(
      <Select options={mockOptions} placeholder="Select..." />
    );
    fireEvent.click(screen.getByText('Select...'));
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'Option 1' } });
    expect(screen.getByText('Option 1')).toBeVisible();
    expect(screen.queryByText('Option 2')).not.toBeInTheDocument();
  });

  it('should call onSearch with debounce in autocomplete mode', async () => {
    jest.useFakeTimers();
    const onSearch = jest.fn();
    render(
      <Select 
        options={mockOptions} 
        mode="autocomplete" 
        onSearch={onSearch}
        searchDebounce={300}
      />
    );
    fireEvent.click(screen.getByRole('textbox'));
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'test' } });
    jest.advanceTimersByTime(300);
    expect(onSearch).toHaveBeenCalledWith('test');
    jest.useRealTimers();
  });

  it('should show create option when allowCreate is true', () => {
    render(
      <Select 
        options={mockOptions} 
        allowCreate 
        onCreate={() => {}}
      />
    );
    fireEvent.click(screen.getByText('请选择'));
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'New Option' } });
    expect(screen.getByText(/创建 "New Option"/)).toBeVisible();
  });

  it('should support keyboard navigation', () => {
    render(
      <Select options={mockOptions} />
    );
    fireEvent.click(screen.getByText('请选择'));
    fireEvent.keyDown(screen.getByRole('textbox'), { key: 'ArrowDown' });
    fireEvent.keyDown(screen.getByRole('textbox'), { key: 'Enter' });
    expect(screen.getByText('Option 1')).toBeVisible();
  });
});
```

- [ ] **Step 3: 运行测试确认失败**

Run: `cd frontend && npm test -- --testPathPattern="Select" --passWithNoTests`
Expected: FAIL - 新测试用例失败

- [ ] **Step 4: 实现 Select 增强**

参考设计文档 5.3 节的完整实现，添加：
- `mode` 属性（'default' | 'autocomplete'）
- `allowCreate` 属性
- `onSearch` 回调
- `loading` 状态
- `searchDebounce` 防抖
- 键盘导航

- [ ] **Step 5: 创建 Select.css**

参考设计文档 5.3 节的 CSS 实现。

- [ ] **Step 6: 运行测试确认通过**

Run: `cd frontend && npm test -- --testPathPattern="Select" --passWithNoTests`
Expected: PASS - 所有测试通过

- [ ] **Step 7: 提交**

```bash
git add frontend/src/shared/ui/Select/ frontend/src/shared/ui/__tests__/Select.test.tsx
git commit -m "feat(Select): add autocomplete mode and allowCreate"
git tag v-round-4-complete
```

---

## 轮次 5: 质量保证

### Task 5.1: 集成到 App.tsx

**Files:**
- Modify: `frontend/src/app/App.tsx`
- Modify: `frontend/src/shared/ui/index.ts`

- [ ] **Step 1: 导出新组件**

```typescript
// frontend/src/shared/ui/index.ts
// 添加导出
export { Drawer } from './Drawer';
export { ThemeProvider, useTheme, ThemeToggle } from './Theme';
export { Select } from './Select';
```

- [ ] **Step 2: 包装 ThemeProvider**

```typescript
// frontend/src/app/App.tsx
import { ThemeProvider } from '@shared/ui';

function App() {
  return (
    <ThemeProvider>
      {/* existing content */}
    </ThemeProvider>
  );
}
```

- [ ] **Step 3: 验证类型检查**

Run: `cd frontend && npm run type-check`
Expected: 无错误

- [ ] **Step 4: 提交**

```bash
git add frontend/src/app/App.tsx frontend/src/shared/ui/index.ts
git commit -m "feat: integrate ThemeProvider into App"
```

---

### Task 5.2: 运行 extract skill

- [ ] **Step 1: 运行 extract skill**

执行 skill: `extract`

目标：提取可复用模式到设计系统。

- [ ] **Step 2: 提交提取结果**

```bash
git add .
git commit -m "refactor: extract reusable patterns via extract skill"
```

---

### Task 5.3: 运行 normalize skill

- [ ] **Step 1: 运行 normalize skill**

执行 skill: `normalize`

目标：归一化组件样式一致性。

- [ ] **Step 2: 提交归一化结果**

```bash
git add .
git commit -m "style: normalize component styles via normalize skill"
```

---

### Task 5.4: 运行 web-design-guidelines 审查

- [ ] **Step 1: 运行 web-design-guidelines skill**

执行 skill: `web-design-guidelines`

目标：Web Interface Guidelines 合规审查。

- [ ] **Step 2: 修复审查发现的问题**

根据审查报告修复问题。

- [ ] **Step 3: 提交修复**

```bash
git add .
git commit -m "fix: resolve web-design-guidelines issues"
git tag v-round-5-complete
```

---

## 轮次 6: 集成测试与回归验证

### Task 6.1: 运行单元测试

- [ ] **Step 1: 运行所有单元测试**

Run: `cd frontend && npm test -- --passWithNoTests`
Expected: 所有测试通过

---

### Task 6.2: 运行 E2E 测试

- [ ] **Step 1: 运行 event2table-universal-test**

执行 skill: `event2table-universal-test`

目标：验证主题切换功能和回归测试。

- [ ] **Step 2: 修复测试失败**

如有测试失败，修复并重新运行。

---

### Task 6.3: 最终提交

- [ ] **Step 1: 创建最终标签**

```bash
git tag v-component-library-extension-complete
git push origin --tags
```

- [ ] **Step 2: 总结**

验证成功标准：
- [ ] 主题切换延迟 < 100ms
- [ ] localStorage 持久化正常
- [ ] Drawer/Select 功能完整
- [ ] WCAG AA 无障碍合规
- [ ] 回归测试 100% 通过

---

## 执行选项

**计划完成并保存到 `docs/superpowers/plans/2026-03-23-component-library-extension.md`。**

**两种执行选项：**

**1. Subagent-Driven（推荐）** - 我派遣一个全新的 subagent 来执行每个任务，任务之间进行审查，快速迭代

**2. Inline Execution** - 在此会话中使用 executing-plans 执行，批量执行并设置检查点进行审查

**选择哪种方式？**
