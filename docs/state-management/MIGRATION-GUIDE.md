# Event2Table 状态管理迁移指南

## 概述

本指南帮助您将现有的状态管理代码迁移到统一的 **Zustand + React Query** 架构。

## 迁移范围

### 需要迁移的代码

1. **Context API** - 迁移到 Zustand
2. **全局 useState** - 迁移到 Zustand
3. **自定义 hooks** - 重构为使用 Zustand

### 不需要迁移的代码

1. **React Query** - 保持现有使用方式
2. **组件本地 useState** - 保持不变
3. **表单状态** - 继续使用 useState 或表单库

## 迁移步骤

### 步骤 1: 识别需要迁移的代码

搜索以下模式：

```bash
# Context API
grep -r "createContext" frontend/src
grep -r "useContext" frontend/src

# 全局 useState
grep -r "useState.*theme" frontend/src
grep -r "useState.*sidebar" frontend/src
grep -r "useState.*modal" frontend/src
```

### 步骤 2: 迁移 Context API

#### 示例 1: ThemeContext 迁移

**之前（Context API）**:

```tsx
// ThemeContext.tsx
import React, { createContext, useContext, useState } from 'react';

type ThemeMode = 'light' | 'dark' | 'auto';

interface ThemeContextValue {
  themeMode: ThemeMode;
  setThemeMode: (mode: ThemeMode) => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [themeMode, setThemeMode] = useState<ThemeMode>('auto');
  
  return (
    <ThemeContext.Provider value={{ themeMode, setThemeMode }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}

// App.tsx
function App() {
  return (
    <ThemeProvider>
      <MainApp />
    </ThemeProvider>
  );
}
```

**之后（Zustand）**:

```tsx
// uiStore.ts (已创建)
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type ThemeMode = 'light' | 'dark' | 'auto';

interface UIStore {
  themeMode: ThemeMode;
  setThemeMode: (mode: ThemeMode) => void;
}

export const useUIStore = create<UIStore>()(
  persist(
    (set) => ({
      themeMode: 'auto',
      setThemeMode: (mode) => set({ themeMode: mode }),
    }),
    { name: 'ui-storage' }
  )
);

// hooks/useUIStore.ts (已创建)
export function useTheme() {
  const { themeMode, setThemeMode } = useUIStore();
  return { themeMode, setThemeMode };
}

// App.tsx
function App() {
  // 不需要 Provider
  return <MainApp />;
}
```

**组件迁移**:

```tsx
// 之前
function MyComponent() {
  const { themeMode, setThemeMode } = useTheme();
  return <button onClick={() => setThemeMode('dark')}>{themeMode}</button>;
}

// 之后 - 组件代码不变！
function MyComponent() {
  const { themeMode, setThemeMode } = useTheme();
  return <button onClick={() => setThemeMode('dark')}>{themeMode}</button>;
}
```

#### 示例 2: PopupContext 迁移

**之前（Context API）**:

```tsx
// PopupProvider.tsx
import React, { createContext, useContext, useState } from 'react';

interface PopupContextValue {
  isOpen: boolean;
  open: () => void;
  close: () => void;
}

const PopupContext = createContext<PopupContextValue | null>(null);

export function PopupProvider({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  
  const open = () => setIsOpen(true);
  const close = () => setIsOpen(false);
  
  return (
    <PopupContext.Provider value={{ isOpen, open, close }}>
      {children}
    </PopupContext.Provider>
  );
}

export function usePopup() {
  const context = useContext(PopupContext);
  if (!context) throw new Error('usePopup must be used within PopupProvider');
  return context;
}
```

**之后（Zustand）**:

```tsx
// 使用 uiStore 中的模态框状态
import { useModal } from '@stores/hooks';

function MyComponent() {
  const { isOpen, open, close } = useModal('myPopup');
  
  return (
    <>
      <button onClick={open}>打开</button>
      <Modal isOpen={isOpen} onClose={close} />
    </>
  );
}
```

### 步骤 3: 迁移全局 useState

#### 示例 1: 侧边栏状态

**之前（useState）**:

```tsx
// Sidebar.tsx
import React, { useState, useEffect } from 'react';

function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  
  useEffect(() => {
    const saved = localStorage.getItem('sidebarCollapsed');
    if (saved) setCollapsed(JSON.parse(saved));
  }, []);
  
  const toggle = () => {
    const newState = !collapsed;
    setCollapsed(newState);
    localStorage.setItem('sidebarCollapsed', JSON.stringify(newState));
  };
  
  return (
    <div className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <button onClick={toggle}>Toggle</button>
    </div>
  );
}
```

**之后（Zustand）**:

```tsx
// Sidebar.tsx
import { useSidebar } from '@stores/hooks';

function Sidebar() {
  const { collapsed, toggleCollapsed } = useSidebar();
  
  return (
    <div className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <button onClick={toggleCollapsed}>Toggle</button>
    </div>
  );
}
```

#### 示例 2: 用户认证状态

**之前（useState）**:

```tsx
// AuthContext.tsx
import React, { createContext, useContext, useState } from 'react';

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  login: (user: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  
  const login = (user: User) => setUser(user);
  const logout = () => setUser(null);
  
  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
```

**之后（Zustand）**:

```tsx
// 使用 userStore
import { useAuth } from '@stores/hooks';

function LoginButton() {
  const { isAuthenticated, user, login, logout } = useAuth();
  
  if (isAuthenticated) {
    return <button onClick={logout}>Logout ({user?.username})</button>;
  }
  
  return <button onClick={() => login({ id: '1', username: 'test' })}>Login</button>;
}
```

### 步骤 4: 迁移自定义 Hooks

#### 示例: useSidebar Hook

**之前（自定义 Hook）**:

```tsx
// hooks/useSidebar.ts
import { useState, useEffect } from 'react';

export function useSidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const [groupStates, setGroupStates] = useState<Record<string, boolean>>({});
  
  useEffect(() => {
    const savedCollapsed = localStorage.getItem('sidebarCollapsed');
    if (savedCollapsed) setCollapsed(JSON.parse(saved));
    
    const savedGroups = localStorage.getItem('sidebarGroupStates');
    if (savedGroups) setGroupStates(JSON.parse(savedGroups));
  }, []);
  
  const toggleCollapsed = () => {
    const newState = !collapsed;
    setCollapsed(newState);
    localStorage.setItem('sidebarCollapsed', JSON.stringify(newState));
  };
  
  const toggleGroup = (groupId: string) => {
    setGroupStates(prev => ({
      ...prev,
      [groupId]: !prev[groupId]
    }));
  };
  
  return {
    collapsed,
    groupStates,
    toggleCollapsed,
    toggleGroup,
  };
}
```

**之后（Zustand）**:

```tsx
// hooks/useUIStore.ts (已创建)
export function useSidebar() {
  const {
    sidebarCollapsed,
    toggleSidebar,
    setSidebarCollapsed,
    sidebarGroupStates,
    toggleSidebarGroup,
  } = useUIStore();
  
  return {
    collapsed: sidebarCollapsed,
    toggleCollapsed: toggleSidebar,
    setCollapsed: setSidebarCollapsed,
    groupStates: sidebarGroupStates,
    toggleGroup: toggleSidebarGroup,
  };
}
```

## 迁移检查清单

### Context API 迁移

- [ ] 识别所有 Context Provider
- [ ] 创建对应的 Zustand store
- [ ] 创建对应的 hook
- [ ] 移除 Context Provider 包裹
- [ ] 更新组件导入
- [ ] 测试功能正常

### useState 迁移

- [ ] 识别全局 useState
- [ ] 确定应该迁移到哪个 store
- [ ] 使用对应的 Zustand hook
- [ ] 移除 localStorage 手动管理
- [ ] 测试功能正常

### 自定义 Hooks 迁移

- [ ] 识别需要迁移的自定义 hooks
- [ ] 重构为使用 Zustand
- [ ] 保持 API 兼容性（如果可能）
- [ ] 更新所有使用该 hook 的组件
- [ ] 测试功能正常

## 常见问题和解决方案

### Q1: 如何处理多个模态框？

**A**: 使用 `useModal` hook 并传入不同的 modalId。

```tsx
const editModal = useModal('editModal');
const deleteModal = useModal('deleteModal');
const settingsModal = useModal('settingsModal');
```

### Q2: 如何处理复杂的权限逻辑？

**A**: 使用 `usePermissions` hook 提供的权限检查方法。

```tsx
const { hasPermission, hasAnyPermission, hasAllPermissions } = usePermissions();

if (hasPermission('event:write')) {
  // 显示编辑按钮
}

if (hasAnyPermission(['event:write', 'event:admin'])) {
  // 显示管理按钮
}
```

### Q3: 如何处理状态持久化？

**A**: Zustand stores 已配置 `persist` 中间件，自动持久化到 localStorage。

```typescript
// uiStore.ts
export const useUIStore = create<UIStore>()(
  persist(
    (set) => ({ /* ... */ }),
    {
      name: 'ui-storage',
      partialize: (state) => ({
        themeMode: state.themeMode,
        sidebarCollapsed: state.sidebarCollapsed,
      }),
    }
  )
);
```

### Q4: 如何处理 React Query 和 Zustand 的交互？

**A**: 保持它们独立，在需要时通过组件连接。

```tsx
function GameList() {
  // React Query - 服务端状态
  const { data: games, isLoading } = useQuery({
    queryKey: ['games'],
    queryFn: fetchGames,
  });
  
  // Zustand - UI状态
  const { sidebarCollapsed } = useSidebar();
  
  return (
    <div className={sidebarCollapsed ? 'collapsed' : ''}>
      {isLoading ? <Loading /> : <List games={games} />}
    </div>
  );
}
```

## 迁移示例

### 完整示例: 游戏管理页面

**之前（混合状态管理）**:

```tsx
// GameManagementPage.tsx
import React, { useState } from 'react';
import { useTheme } from './contexts/ThemeContext';
import { useAuth } from './contexts/AuthContext';
import { useSidebar } from './hooks/useSidebar';

function GameManagementPage() {
  const { themeMode, setThemeMode } = useTheme();
  const { user, isAuthenticated } = useAuth();
  const { collapsed, toggleCollapsed } = useSidebar();
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  if (!isAuthenticated) return <Login />;
  
  return (
    <div className={`page ${collapsed ? 'collapsed' : ''}`}>
      <header>
        <button onClick={toggleCollapsed}>Toggle Sidebar</button>
        <select value={themeMode} onChange={(e) => setThemeMode(e.target.value)}>
          <option value="light">Light</option>
          <option value="dark">Dark</option>
        </select>
      </header>
      <main>
        <button onClick={() => setIsModalOpen(true)}>Add Game</button>
        <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
      </main>
    </div>
  );
}
```

**之后（统一状态管理）**:

```tsx
// GameManagementPage.tsx
import React from 'react';
import { useTheme } from '@stores/hooks';
import { useAuth } from '@stores/hooks';
import { useSidebar } from '@stores/hooks';
import { useModal } from '@stores/hooks';

function GameManagementPage() {
  const { themeMode, setThemeMode } = useTheme();
  const { user, isAuthenticated } = useAuth();
  const { collapsed, toggleCollapsed } = useSidebar();
  const { isOpen, open, close } = useModal('addGameModal');
  
  if (!isAuthenticated) return <Login />;
  
  return (
    <div className={`page ${collapsed ? 'collapsed' : ''}`}>
      <header>
        <button onClick={toggleCollapsed}>Toggle Sidebar</button>
        <select value={themeMode} onChange={(e) => setThemeMode(e.target.value)}>
          <option value="light">Light</option>
          <option value="dark">Dark</option>
        </select>
      </header>
      <main>
        <button onClick={open}>Add Game</button>
        <Modal isOpen={isOpen} onClose={close} />
      </main>
    </div>
  );
}
```

## 验证迁移

### 功能验证

1. **状态持久化** - 刷新页面后状态是否保持
2. **跨组件共享** - 状态在不同组件间是否同步
3. **性能** - 是否有不必要的重渲染
4. **类型检查** - TypeScript 是否报错

### 测试

```typescript
// 测试主题切换
import { renderHook, act } from '@testing-library/react';
import { useTheme } from '@stores/hooks';

describe('Theme Migration', () => {
  it('should toggle theme', () => {
    const { result } = renderHook(() => useTheme());
    
    act(() => {
      result.current.setThemeMode('dark');
    });
    
    expect(result.current.themeMode).toBe('dark');
  });
});
```

## 回滚计划

如果迁移出现问题，可以回滚到之前的实现：

1. 保留旧的 Context API 代码（注释掉）
2. 保留旧的 useState 实现（注释掉）
3. 使用 Git 分支管理迁移过程
4. 逐步迁移，而不是一次性全部迁移

## 总结

迁移到 Zustand + React Query 架构可以带来以下好处：

1. **更简洁的代码** - 不需要 Provider 包裹
2. **更好的性能** - 更少的重渲染
3. **更强的类型安全** - 完整的 TypeScript 支持
4. **更好的开发体验** - 更简单的 API
5. **自动持久化** - 不需要手动管理 localStorage

## 相关文档

- [状态管理指南](./STATE-MANAGEMENT-GUIDE.md)
- [最佳实践](./BEST-PRACTICES.md)
- [Zustand 文档](https://zustand-demo.pmnd.rs/)
- [React Query 文档](https://tanstack.com/query/latest)
