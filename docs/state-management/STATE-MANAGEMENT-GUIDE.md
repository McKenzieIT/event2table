# Event2Table 状态管理指南

## 概述

Event2Table 采用 **Zustand + React Query** 的混合状态管理架构，提供高性能、类型安全的状态管理方案。

### 架构原则

1. **Zustand** - 管理客户端状态
   - UI状态（主题、侧边栏、模态框）
   - 用户状态（认证、权限、角色）
   - 应用全局状态（配置、错误、通知）

2. **React Query** - 管理服务端状态
   - API数据获取和缓存
   - 数据同步和更新
   - 乐观更新和重试

## Store 结构

### 1. UI Store (`uiStore.ts`)

管理所有UI相关的全局状态。

#### 状态类型

```typescript
type ThemeMode = 'light' | 'dark' | 'auto';

interface UIStore {
  // 主题状态
  themeMode: ThemeMode;
  setThemeMode: (mode: ThemeMode) => void;

  // 侧边栏状态
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  
  sidebarGroupStates: Record<string, boolean>;
  toggleSidebarGroup: (groupId: string) => void;

  // 模态框状态
  modalStates: Record<string, boolean>;
  openModal: (modalId: string) => void;
  closeModal: (modalId: string) => void;

  // 全屏状态
  isFullscreen: boolean;
  toggleFullscreen: () => void;

  // 加载状态
  globalLoading: boolean;
  setGlobalLoading: (loading: boolean) => void;
}
```

#### 使用示例

```tsx
import { useUIStore } from '@stores/hooks';

function MyComponent() {
  const { themeMode, setThemeMode, sidebarCollapsed, toggleSidebar } = useUIStore();
  
  return (
    <div>
      <p>主题: {themeMode}</p>
      <button onClick={() => setThemeMode('dark')}>暗色主题</button>
      <button onClick={toggleSidebar}>切换侧边栏</button>
    </div>
  );
}
```

### 2. User Store (`userStore.ts`)

管理用户认证和授权信息。

#### 状态类型

```typescript
interface UserInfo {
  id: string;
  username: string;
  email?: string;
  displayName?: string;
  avatar?: string;
}

interface UserStore {
  user: UserInfo | null;
  isAuthenticated: boolean;
  permissions: Permission[];
  roles: Role[];
  
  login: (user: UserInfo, permissions?: Permission[], roles?: Role[]) => void;
  logout: () => void;
  hasPermission: (permission: Permission) => boolean;
  hasRole: (role: Role) => boolean;
}
```

#### 使用示例

```tsx
import { useUserStore } from '@stores/hooks';

function ProtectedComponent() {
  const { user, isAuthenticated, hasPermission } = useUserStore();
  
  if (!isAuthenticated) {
    return <Login />;
  }
  
  if (!hasPermission('event:write')) {
    return <AccessDenied />;
  }
  
  return <div>欢迎, {user?.username}</div>;
}
```

### 3. App Store (`appStore.ts`)

管理应用级别的全局状态。

#### 状态类型

```typescript
interface AppStore {
  isAppInitialized: boolean;
  appVersion: string;
  apiBaseUrl: string;
  environment: 'development' | 'staging' | 'production';
  
  globalError: Error | null;
  notifications: Notification[];
  isOnline: boolean;
  
  featureFlags: Record<string, boolean>;
  getFeatureFlag: (flag: string) => boolean;
}
```

#### 使用示例

```tsx
import { useAppStore } from '@stores/hooks';

function AppHeader() {
  const { appVersion, environment, isOnline } = useAppStore();
  
  return (
    <header>
      <span>v{appVersion}</span>
      <span>{environment}</span>
      <span>{isOnline ? '在线' : '离线'}</span>
    </header>
  );
}
```

### 4. Game Store (`gameStore.ts`)

管理游戏相关的状态（已存在）。

## Hooks 使用

### 基础 Hooks

```typescript
// 使用完整的store
const { themeMode, setThemeMode } = useUIStore();
const { user, login, logout } = useUserStore();
const { appVersion, environment } = useAppStore();

// 使用特定功能的hook
const { themeMode, setThemeMode } = useTheme();
const { collapsed, toggleCollapsed } = useSidebar();
const { isOpen, open, close } = useModal('myModal');
const { isAuthenticated, user } = useAuth();
const { hasPermission } = usePermissions();
const { isOnline } = useOnlineStatus();
```

### React Query Hooks

React Query 用于管理服务端状态，保持现有的使用方式不变。

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// 获取数据
const { data, isLoading, error } = useQuery({
  queryKey: ['games'],
  queryFn: fetchGames,
});

// 修改数据
const mutation = useMutation({
  mutationFn: createGame,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['games'] });
  },
});
```

## 最佳实践

### 1. 状态分类

- **客户端状态**: 使用 Zustand
  - UI交互状态
  - 用户认证状态
  - 应用配置状态

- **服务端状态**: 使用 React Query
  - API数据
  - 数据缓存
  - 数据同步

### 2. 状态持久化

Zustand stores 使用 `persist` 中间件自动持久化到 localStorage。

```typescript
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

### 3. 类型安全

所有 stores 和 hooks 都提供完整的 TypeScript 类型支持。

```typescript
import type { ThemeMode, UserInfo, Permission } from '@stores';

function setTheme(mode: ThemeMode) {
  // 类型安全
}

function checkPermission(permission: Permission) {
  // 类型安全
}
```

### 4. 性能优化

- 使用选择器避免不必要的重渲染
- 使用特定的 hooks 而不是完整的 store
- React Query 自动处理缓存和去重

```typescript
// ✅ 好 - 只订阅需要的状态
const themeMode = useUIStore(state => state.themeMode);

// ✅ 好 - 使用特定hook
const { themeMode } = useTheme();

// ⚠️ 避免 - 订阅整个store
const store = useUIStore();
```

### 5. 错误处理

```typescript
import { useAppStore } from '@stores/hooks';

function handleApiError(error: Error) {
  const { setGlobalError, addNotification } = useAppStore();
  
  setGlobalError(error);
  addNotification({
    type: 'error',
    message: error.message,
  });
}
```

## 迁移指南

### 从 Context API 迁移到 Zustand

#### 之前（Context API）

```tsx
// ThemeContext.tsx
const ThemeContext = createContext<ThemeContextValue | null>(null);

function ThemeProvider({ children }) {
  const [themeMode, setThemeMode] = useState('light');
  
  return (
    <ThemeContext.Provider value={{ themeMode, setThemeMode }}>
      {children}
    </ThemeContext.Provider>
  );
}

function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within ThemeProvider');
  return context;
}
```

#### 之后（Zustand）

```tsx
// uiStore.ts
export const useUIStore = create<UIStore>((set) => ({
  themeMode: 'light',
  setThemeMode: (mode) => set({ themeMode: mode }),
}));

// hooks/useUIStore.ts
export function useTheme() {
  const { themeMode, setThemeMode } = useUIStore();
  return { themeMode, setThemeMode };
}
```

### 从 useState 迁移到 Zustand

#### 之前（useState）

```tsx
function MyComponent() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  return (
    <>
      <button onClick={() => setIsModalOpen(true)}>打开</button>
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </>
  );
}
```

#### 之后（Zustand）

```tsx
function MyComponent() {
  const { isOpen, open, close } = useModal('myModal');
  
  return (
    <>
      <button onClick={open}>打开</button>
      <Modal isOpen={isOpen} onClose={close} />
    </>
  );
}
```

## 常见问题

### Q: 何时使用 Zustand vs React Query？

**A**: 
- 使用 Zustand 管理客户端状态（UI、用户、配置）
- 使用 React Query 管理服务端状态（API数据、缓存）

### Q: 如何在组件间共享状态？

**A**: Zustand stores 是全局的，可以在任何组件中使用对应的 hook 访问。

### Q: 如何调试状态？

**A**: 
1. 使用 Redux DevTools（Zustand 支持）
2. 在组件中 `console.log(useUIStore())`
3. 使用 React Query DevTools 查看服务端状态

### Q: 如何重置状态？

**A**: 每个 store 都提供 `reset` 方法。

```typescript
const { resetUIState } = useUIStore();
resetUIState();
```

## 相关文档

- [最佳实践文档](./BEST-PRACTICES.md)
- [迁移指南](./MIGRATION-GUIDE.md)
- [Zustand 官方文档](https://zustand-demo.pmnd.rs/)
- [React Query 官方文档](https://tanstack.com/query/latest)
