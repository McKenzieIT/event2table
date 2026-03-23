# Event2Table 状态管理最佳实践

## 目录

- [状态分类原则](#状态分类原则)
- [Store 设计原则](#store-设计原则)
- [Hooks 使用规范](#hooks-使用规范)
- [性能优化](#性能优化)
- [错误处理](#错误处理)
- [测试策略](#测试策略)
- [常见反模式](#常见反模式)

## 状态分类原则

### 客户端状态 vs 服务端状态

#### 客户端状态（使用 Zustand）

**特征**:
- 由客户端控制
- 不需要持久化到服务器
- 响应用户交互
- UI相关

**示例**:
```typescript
// ✅ 正确 - 客户端状态
const { themeMode, setThemeMode } = useTheme();
const { sidebarCollapsed, toggleSidebar } = useSidebar();
const { isAuthenticated, user } = useAuth();
const { isModalOpen, openModal } = useModal('editModal');
```

#### 服务端状态（使用 React Query）

**特征**:
- 来自服务器
- 需要缓存和同步
- 可能被其他用户修改
- 数据相关

**示例**:
```typescript
// ✅ 正确 - 服务端状态
const { data: games, isLoading } = useQuery({
  queryKey: ['games'],
  queryFn: fetchGames,
});

const mutation = useMutation({
  mutationFn: createGame,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['games'] });
  },
});
```

### 状态分类决策树

```
是否来自服务器？
├─ 是 → 服务端状态 → 使用 React Query
└─ 否 → 客户端状态
    ├─ 是否需要跨组件共享？
    │   ├─ 是 → 使用 Zustand
    │   └─ 否 → 使用 useState
    └─ 是否需要持久化？
        ├─ 是 → 使用 Zustand + persist
        └─ 否 → 使用 useState
```

## Store 设计原则

### 1. 单一职责原则

每个 store 只管理一个领域的状态。

```typescript
// ✅ 好 - 职责清晰
// uiStore.ts - 只管理UI状态
// userStore.ts - 只管理用户状态
// appStore.ts - 只管理应用状态

// ❌ 差 - 职责混乱
// store.ts - 包含所有状态
```

### 2. 最小化状态

只存储必要的状态，派生状态通过计算得到。

```typescript
// ✅ 好 - 只存储基础状态
interface UIStore {
  sidebarCollapsed: boolean;
  // 派生状态：isSidebarExpanded = !sidebarCollapsed
}

// ❌ 差 - 存储冗余状态
interface UIStore {
  sidebarCollapsed: boolean;
  sidebarExpanded: boolean; // 冗余
}
```

### 3. 不可变性

Zustand 自动处理不可变性，但要注意引用类型。

```typescript
// ✅ 好 - 创建新对象
setUser((user) => ({
  ...user,
  name: 'New Name',
}));

// ❌ 差 - 直接修改
const user = getUser();
user.name = 'New Name';
setUser(user);
```

### 4. 类型安全

为所有状态和操作定义明确的类型。

```typescript
// ✅ 好 - 完整类型定义
interface UserStore {
  user: UserInfo | null;
  login: (user: UserInfo, permissions?: Permission[]) => void;
  hasPermission: (permission: Permission) => boolean;
}

// ❌ 差 - 使用 any
interface UserStore {
  user: any;
  login: (user: any) => void;
  hasPermission: (permission: any) => boolean;
}
```

## Hooks 使用规范

### 1. 使用特定 Hooks

优先使用特定功能的 hooks 而不是完整的 store hook。

```typescript
// ✅ 好 - 使用特定hook
const { themeMode, setThemeMode } = useTheme();
const { collapsed, toggleCollapsed } = useSidebar();
const { isAuthenticated, user } = useAuth();

// ⚠️ 可接受 - 使用完整store
const { themeMode, setThemeMode, sidebarCollapsed } = useUIStore();

// ❌ 差 - 订阅整个store
const store = useUIStore();
```

### 2. 选择器模式

使用选择器避免不必要的重渲染。

```typescript
// ✅ 好 - 只订阅需要的状态
const themeMode = useUIStore(state => state.themeMode);

// ✅ 好 - 使用特定hook
const { themeMode } = useTheme();

// ⚠️ 避免 - 订阅整个store
const { themeMode, sidebarCollapsed, modalStates } = useUIStore();
```

### 3. Hooks 命名规范

```typescript
// ✅ 好 - 清晰的命名
useTheme, useSidebar, useModal, useAuth
usePermissions, useRoles, useUserInfo
useAppConfig, useNotifications, useFeatureFlags

// ❌ 差 - 模糊的命名
useStore, useData, useState
```

## 性能优化

### 1. 避免不必要的重渲染

```typescript
// ✅ 好 - 使用选择器
function ThemeButton() {
  const themeMode = useUIStore(state => state.themeMode);
  const setThemeMode = useUIStore(state => state.setThemeMode);
  
  return <button onClick={() => setThemeMode('dark')}>{themeMode}</button>;
}

// ✅ 好 - 使用特定hook
function ThemeButton() {
  const { themeMode, setThemeMode } = useTheme();
  return <button onClick={() => setThemeMode('dark')}>{themeMode}</button>;
}
```

### 2. React Query 优化

```typescript
// ✅ 好 - 配置缓存时间
useQuery({
  queryKey: ['games'],
  queryFn: fetchGames,
  staleTime: 5 * 60 * 1000, // 5分钟
  gcTime: 10 * 60 * 1000, // 10分钟
});

// ✅ 好 - 使用选择器
const games = useQuery({
  queryKey: ['games'],
  queryFn: fetchGames,
  select: (data) => data.filter(game => game.active),
});
```

### 3. 批量更新

```typescript
// ✅ 好 - 批量更新
set((state) => ({
  ...state,
  themeMode: 'dark',
  sidebarCollapsed: true,
  globalLoading: false,
}));

// ❌ 差 - 多次更新
set({ themeMode: 'dark' });
set({ sidebarCollapsed: true });
set({ globalLoading: false });
```

## 错误处理

### 1. 全局错误处理

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

### 2. React Query 错误处理

```typescript
const { data, error, isError } = useQuery({
  queryKey: ['games'],
  queryFn: fetchGames,
  retry: 3,
  retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  onError: (error) => {
    handleApiError(error);
  },
});
```

### 3. 用户友好的错误消息

```typescript
// ✅ 好 - 用户友好的错误消息
addNotification({
  type: 'error',
  message: '创建游戏失败，请稍后重试',
});

// ❌ 差 - 技术错误消息
addNotification({
  type: 'error',
  message: '500 Internal Server Error: Database connection failed',
});
```

## 测试策略

### 1. 测试 Store

```typescript
import { renderHook, act } from '@testing-library/react';
import { useUIStore } from '@stores/uiStore';

describe('useUIStore', () => {
  beforeEach(() => {
    // 重置store状态
    useUIStore.getState().resetUIState();
  });

  it('should toggle sidebar', () => {
    const { result } = renderHook(() => useUIStore());
    
    act(() => {
      result.current.toggleSidebar();
    });
    
    expect(result.current.sidebarCollapsed).toBe(true);
  });
});
```

### 2. 测试 Hooks

```typescript
import { renderHook, act } from '@testing-library/react';
import { useTheme } from '@stores/hooks';

describe('useTheme', () => {
  it('should set theme mode', () => {
    const { result } = renderHook(() => useTheme());
    
    act(() => {
      result.current.setThemeMode('dark');
    });
    
    expect(result.current.themeMode).toBe('dark');
  });
});
```

### 3. 测试 React Query

```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

describe('useGames', () => {
  it('should fetch games', async () => {
    const queryClient = new QueryClient();
    
    const { result } = renderHook(() => useGames(), {
      wrapper: ({ children }) => (
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      ),
    });
    
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toBeDefined();
  });
});
```

## 常见反模式

### 1. 过度使用 Zustand

```typescript
// ❌ 差 - 组件本地状态不需要 Zustand
const [isModalOpen, setIsModalOpen] = useState(false);

// ✅ 好 - 只在需要跨组件共享时使用 Zustand
const { isOpen, open, close } = useModal('myModal');
```

### 2. 混合状态管理

```typescript
// ❌ 差 - 混合使用 Context 和 Zustand
const theme = useContext(ThemeContext);
const { setThemeMode } = useUIStore();

// ✅ 好 - 统一使用 Zustand
const { themeMode, setThemeMode } = useTheme();
```

### 3. 直接修改状态

```typescript
// ❌ 差 - 直接修改状态
const store = useUIStore();
store.themeMode = 'dark';

// ✅ 好 - 使用提供的action
const { setThemeMode } = useUIStore();
setThemeMode('dark');
```

### 4. 忽略 TypeScript 类型

```typescript
// ❌ 差 - 使用 any
const user: any = getUser();

// ✅ 好 - 使用具体类型
const user: UserInfo = getUser();
```

## 总结

遵循这些最佳实践可以确保：

1. **清晰的代码结构** - 状态管理逻辑易于理解和维护
2. **高性能** - 避免不必要的重渲染和计算
3. **类型安全** - TypeScript 提供完整的类型检查
4. **可测试性** - 状态管理逻辑易于测试
5. **可扩展性** - 架构支持未来的功能扩展

## 相关文档

- [状态管理指南](./STATE-MANAGEMENT-GUIDE.md)
- [迁移指南](./MIGRATION-GUIDE.md)
- [Zustand 最佳实践](https://docs.pmnd.rs/zustand/guides/performance)
- [React Query 最佳实践](https://tanstack.com/query/latest/docs/react/guides/important-defaults)
