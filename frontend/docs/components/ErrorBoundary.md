# ErrorBoundary Component

## 概述

ErrorBoundary 组件是一个增强版的错误边界组件，用于捕获子组件树中的 JavaScript 错误，记录错误日志，并显示备用 UI。支持自定义回退 UI、错误回调、重置回调和基于依赖项的自动重置。

## Props

| 属性名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `fallback` | `ReactNode \| FallbackRenderFunction` | `undefined` | 自定义回退 UI 或渲染函数 |
| `onError` | `(error: Error, errorInfo: ErrorInfo) => void` | `undefined` | 错误回调函数 |
| `onReset` | `() => void` | `undefined` | 重置回调函数 |
| `resetKeys` | `unknown[]` | `undefined` | 依赖项数组，变化时自动重置 |
| `children` | `ReactNode` | - | 子组件 |

### 类型定义

```typescript
interface ErrorInfo {
  componentStack: string;
  errorBoundary: string;
}

interface FallbackProps {
  error: Error;
  errorInfo: ErrorInfo;
  resetErrorBoundary: () => void;
}

type FallbackRenderFunction = (props: FallbackProps) => ReactNode;

interface ErrorBoundaryProps {
  fallback?: ReactNode | FallbackRenderFunction;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  onReset?: () => void;
  resetKeys?: unknown[];
  children: ReactNode;
}
```

## 使用示例

### 基础用法（默认 UI）

```tsx
import { ErrorBoundary } from '@shared/ui';

function App() {
  return (
    <ErrorBoundary>
      <MyComponent />
    </ErrorBoundary>
  );
}
```

### 自定义回退 UI

```tsx
import { ErrorBoundary } from '@shared/ui';

function App() {
  return (
    <ErrorBoundary
      fallback={
        <div className="error-fallback">
          <h2>出错了</h2>
          <p>页面遇到了一个错误，请刷新页面重试</p>
          <button onClick={() => window.location.reload()}>刷新</button>
        </div>
      }
    >
      <MyComponent />
    </ErrorBoundary>
  );
}
```

### 使用渲染函数

```tsx
import { ErrorBoundary } from '@shared/ui';

function App() {
  return (
    <ErrorBoundary
      fallback={({ error, errorInfo, resetErrorBoundary }) => (
        <div className="error-fallback">
          <h2>出错了</h2>
          <p>{error.message}</p>
          <details>
            <summary>错误详情</summary>
            <pre>{errorInfo.componentStack}</pre>
          </details>
          <button onClick={resetErrorBoundary}>重试</button>
          <button onClick={() => window.location.reload()}>刷新页面</button>
        </div>
      )}
    >
      <MyComponent />
    </ErrorBoundary>
  );
}
```

### 错误回调

```tsx
import { ErrorBoundary } from '@shared/ui';

function App() {
  const handleError = (error: Error, errorInfo: ErrorInfo) => {
    // 发送错误到日志服务
    console.error('Error caught by boundary:', error);
    console.error('Component stack:', errorInfo.componentStack);
    
    // 发送到错误追踪服务
    // logErrorToService(error, errorInfo);
  };

  return (
    <ErrorBoundary onError={handleError}>
      <MyComponent />
    </ErrorBoundary>
  );
}
```

### 重置回调

```tsx
import { ErrorBoundary } from '@shared/ui';
import { useState } from 'react';

function App() {
  const [key, setKey] = useState(0);

  const handleReset = () => {
    // 清理状态
    setKey(prev => prev + 1);
  };

  return (
    <ErrorBoundary
      onReset={handleReset}
      resetKeys={[key]}
    >
      <MyComponent key={key} />
    </ErrorBoundary>
  );
}
```

### 基于路由的自动重置

```tsx
import { ErrorBoundary } from '@shared/ui';
import { useLocation } from 'react-router-dom';

function App() {
  const location = useLocation();

  return (
    <ErrorBoundary resetKeys={[location.pathname]}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </ErrorBoundary>
  );
}
```

### 多个 ErrorBoundary

```tsx
import { ErrorBoundary } from '@shared/ui';

function App() {
  return (
    <ErrorBoundary fallback={<div>应用级错误</div>}>
      <Header />
      <main>
        <ErrorBoundary fallback={<div>主要内容错误</div>}>
          <MainContent />
        </ErrorBoundary>
        <aside>
          <ErrorBoundary fallback={<div>侧边栏错误</div>}>
            <Sidebar />
          </ErrorBoundary>
        </aside>
      </main>
      <Footer />
    </ErrorBoundary>
  );
}
```

### 完整示例

```tsx
import { ErrorBoundary } from '@shared/ui';
import { useState } from 'react';

function UserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchUser(userId)
      .then(setUser)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [userId]);

  if (loading) return <Spinner />;
  if (error) throw error; // 会被 ErrorBoundary 捕获

  return <div>{user.name}</div>;
}

function App() {
  const [userId, setUserId] = useState('1');

  const handleError = (error: Error, errorInfo: ErrorInfo) => {
    // 发送错误到监控服务
    logError({
      error: error.message,
      stack: errorInfo.componentStack,
      userId,
    });
  };

  return (
    <div>
      <select value={userId} onChange={(e) => setUserId(e.target.value)}>
        <option value="1">用户 1</option>
        <option value="2">用户 2</option>
        <option value="3">用户 3</option>
      </select>

      <ErrorBoundary
        resetKeys={[userId]}
        onError={handleError}
        fallback={({ error, resetErrorBoundary }) => (
          <div className="error-container">
            <h2>加载用户失败</h2>
            <p>{error.message}</p>
            <button onClick={resetErrorBoundary}>重试</button>
          </div>
        )}
      >
        <UserProfile userId={userId} />
      </ErrorBoundary>
    </div>
  );
}
```

## 注意事项

1. **错误捕获范围**:
   - 只捕获子组件树中的错误
   - 不捕获事件处理器中的错误
   - 不捕获异步代码中的错误
   - 不捕获服务端渲染错误

2. **重置机制**:
   - `resetKeys` 变化时会自动重置错误状态
   - 使用浅比较判断 `resetKeys` 是否变化
   - 调用 `resetErrorBoundary()` 也可以手动重置

3. **性能优化**:
   - 使用 `React.memo` 进行优化
   - 避免在 `fallback` 中创建新的函数或组件

4. **错误处理**:
   - 错误会被记录到控制台
   - `onError` 回调可用于发送错误到日志服务
   - 错误信息包含组件堆栈

5. **最佳实践**:
   - 在应用顶层放置一个 ErrorBoundary
   - 在关键功能区域放置独立的 ErrorBoundary
   - 提供友好的错误提示和恢复选项
   - 记录错误信息用于调试

6. **局限性**:
   - 无法捕获以下错误:
     - 事件处理器（如 `onClick`）
     - 异步代码（如 `setTimeout`、`Promise`）
     - 服务端渲染
     - 错误边界本身的错误

7. **与其他错误处理结合**:
   - 事件处理器错误使用 `try-catch`
   - 异步错误使用 `Promise.catch()`
   - 全局错误使用 `window.onerror`

## 相关组件

- [`Modal`](./Modal.md) - 模态框组件（可用于显示错误详情）
- [`Button`](./Button.md) - 按钮组件
