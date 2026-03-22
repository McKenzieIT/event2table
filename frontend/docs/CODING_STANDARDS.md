# 前端编码规范

> **版本**: 1.0 | **最后更新**: 2026-03-22
>
> 本文档定义了 Event2Table 前端项目的编码规范，确保代码质量、可维护性和团队协作效率。

---

## 目录

- [命名规范](#命名规范)
- [目录结构规范](#目录结构规范)
- [导入导出规范](#导入导出规范)
- [组件开发规范](#组件开发规范)
- [TypeScript 使用规范](#typescript-使用规范)
- [React Hooks 规范](#react-hooks-规范)
- [性能优化最佳实践](#性能优化最佳实践)
- [错误处理规范](#错误处理规范)
- [测试规范](#测试规范)
- [代码格式化](#代码格式化)

---

## 命名规范

### 文件命名

**组件文件**：
```typescript
// ✅ 正确：使用 PascalCase
GameList.tsx
EventBuilder.tsx
CanvasFlow.tsx
Table.tsx

// ❌ 错误：不要使用小写或下划线
gameList.tsx
event_builder.tsx
canvas-flow.tsx
```

**Hook 文件**：
```typescript
// ✅ 正确：使用 use 前缀 + camelCase
useGameData.ts
useCanvasFlow.ts
useModal.ts

// ❌ 错误：不要使用其他前缀
gameData.ts
canvasFlow.ts
modal.ts
```

**工具函数文件**：
```typescript
// ✅ 正确：使用 camelCase
formatDate.ts
validateEmail.ts
generateHQL.ts

// ❌ 错误：不要使用大写
FormatDate.ts
ValidateEmail.ts
```

**类型定义文件**：
```typescript
// ✅ 正确：使用 .types.ts 后缀
game.types.ts
event.types.ts
form.types.ts

// ❌ 错误：不要使用其他后缀
gameTypes.ts
eventTypes.ts
```

**测试文件**：
```typescript
// ✅ 正确：使用 .spec.ts 或 .test.ts 后缀
GameList.spec.ts
useGameData.test.ts

// ❌ 错误：不要使用其他后缀
GameList.test.tsx
useGameData.spec.js
```

### 变量和函数命名

**变量**：
```typescript
// ✅ 正确：使用 camelCase
const userName = 'John';
const gameCount = 10;
const isLoading = false;

// ❌ 错误：不要使用下划线或大写
const user_name = 'John';
const GameCount = 10;
const IS_LOADING = false;  // 除非是常量
```

**常量**：
```typescript
// ✅ 正确：使用 UPPER_SNAKE_CASE
const MAX_RETRY_COUNT = 3;
const DEFAULT_PAGE_SIZE = 20;
const API_BASE_URL = 'https://api.example.com';

// ❌ 错误：不要使用小写
const maxRetryCount = 3;
const defaultPageSize = 20;
```

**函数**：
```typescript
// ✅ 正确：使用 camelCase，动词开头
function fetchGameData() { }
function validateEmail() { }
function generateHQL() { }

// ❌ 错误：不要使用名词开头
function gameData() { }
function emailValidation() { }
```

**类和接口**：
```typescript
// ✅ 正确：使用 PascalCase
class GameService { }
interface GameData { }
type EventStatus = 'active' | 'inactive';

// ❌ 错误：不要使用小写
class gameService { }
interface gameData { }
```

**枚举**：
```typescript
// ✅ 正确：使用 PascalCase
enum EventStatus {
  Active = 'active',
  Inactive = 'inactive',
  Pending = 'pending',
}

// ❌ 错误：不要使用小写
enum eventStatus {
  active = 'active',
  inactive = 'inactive',
}
```

### React 组件命名

**组件名称**：
```typescript
// ✅ 正确：使用 PascalCase
function GameList() { }
const EventBuilder = () => { }

// ❌ 错误：不要使用小写
function gameList() { }
const eventBuilder = () => { }
```

**Props 接口**：
```typescript
// ✅ 正确：使用组件名 + Props 后缀
interface GameListProps {
  games: Game[];
  loading: boolean;
}

interface EventBuilderProps {
  eventId: string;
  onSave: (event: Event) => void;
}

// ❌ 错误：不要使用其他后缀
interface GameListProps { }  // ✅ 正确
interface GameListInterface { }  // ❌ 错误
interface IGameList { }  // ❌ 错误
```

**事件处理器**：
```typescript
// ✅ 正确：使用 handle 前缀
const handleClick = () => { };
const handleSubmit = (data: FormData) => { };
const handleGameSelect = (game: Game) => { };

// ❌ 错误：不要使用其他前缀
const onClick = () => { };
const submit = (data: FormData) => { };
```

**回调函数**：
```typescript
// ✅ 正确：使用 on 前缀
interface GameListProps {
  onGameSelect: (game: Game) => void;
  onGameDelete: (gameId: string) => void;
}

// ❌ 错误：不要使用其他前缀
interface GameListProps {
  gameSelect: (game: Game) => void;
  deleteGame: (gameId: string) => void;
}
```

---

## 目录结构规范

### Feature 模块结构

每个功能模块应遵循以下结构：

```
features/
└── games/
    ├── components/           # 游戏相关组件
    │   ├── GameList.tsx
    │   ├── GameCard.tsx
    │   ├── GameForm.tsx
    │   └── index.ts         # 组件导出
    ├── hooks/               # 游戏相关 Hooks
    │   ├── useGameData.ts
    │   ├── useGameList.ts
    │   └── index.ts         # Hooks 导出
    ├── api/                 # API 调用
    │   ├── gamesApi.ts
    │   └── index.ts         # API 导出
    ├── types/               # 类型定义
    │   ├── game.types.ts
    │   └── index.ts         # 类型导出
    ├── utils/               # 工具函数
    │   ├── gameUtils.ts
    │   └── index.ts         # 工具导出
    └── index.ts             # 模块统一导出
```

### Shared UI 组件结构

```
shared/ui/
├── components/
│   ├── Button/
│   │   ├── Button.tsx       # 组件实现
│   │   ├── Button.types.ts  # 类型定义
│   │   ├── Button.test.tsx  # 测试文件
│   │   └── index.ts         # 组件导出
│   ├── Table/
│   │   ├── Table.tsx
│   │   ├── Table.types.ts
│   │   ├── Table.test.tsx
│   │   └── index.ts
│   └── index.ts             # 统一导出所有组件
└── hooks/
    ├── useModal/
    │   ├── useModal.ts
    │   ├── useModal.test.ts
    │   └── index.ts
    └── index.ts
```

### 模块导出规范

**组件导出**：
```typescript
// Button/index.ts
export { default as Button } from './Button';
export type { ButtonProps, ButtonVariant } from './Button.types';
```

**Feature 模块导出**：
```typescript
// features/games/index.ts
// 组件
export * from './components';

// Hooks
export * from './hooks';

// API
export * from './api';

// 类型
export * from './types';

// 工具
export * from './utils';
```

---

## 导入导出规范

### 导入顺序

导入应按以下顺序排列，每组之间用空行分隔：

```typescript
// 1. React 和核心库
import React, { useState, useEffect } from 'react';
import { BrowserRouter } from 'react-router-dom';

// 2. 第三方库
import { useQuery } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

// 3. 内部模块（按层级）
// 3.1 features
import { useGameData } from '@/features/games/hooks';
import { GameList } from '@/features/games/components';

// 3.2 shared
import { Button } from '@/shared/ui/components';
import { useModal } from '@/shared/ui/hooks';

// 3.3 stores
import { useGameStore } from '@/stores';

// 3.4 utils
import { formatDate } from '@/shared/utils';

// 4. 类型导入
import type { Game, GameData } from '@/features/games/types';
import type { ButtonProps } from '@/shared/ui/components';

// 5. 样式
import './GameList.styles.css';
```

### 导入路径别名

使用路径别名代替相对路径：

```typescript
// ✅ 正确：使用路径别名
import { Button } from '@/shared/ui/components';
import { useGameData } from '@/features/games/hooks';
import { formatDate } from '@/shared/utils';

// ❌ 错误：使用相对路径
import { Button } from '../../../shared/ui/components';
import { useGameData } from '../hooks';
import { formatDate } from '../../../shared/utils';
```

### 命名导出 vs 默认导出

**组件**：优先使用命名导出

```typescript
// ✅ 正确：命名导出
export function GameList() { }
export const GameList = () => { }

// ❌ 避免：默认导出（除非有特殊原因）
export default function GameList() { }
```

**工具函数**：使用命名导出

```typescript
// ✅ 正确：命名导出
export function formatDate(date: Date): string { }
export function validateEmail(email: string): boolean { }

// ❌ 避免：默认导出
export default function formatDate(date: Date): string { }
```

**类型**：使用命名导出

```typescript
// ✅ 正确：命名导出
export interface GameData { }
export type EventStatus = 'active' | 'inactive';

// ❌ 避免：默认导出
export default interface GameData { }
```

### 类型导入

使用 `type` 关键字导入类型：

```typescript
// ✅ 正确：使用 type 关键字
import type { Game, GameData } from '@/features/games/types';

// ❌ 错误：不使用 type 关键字
import { Game, GameData } from '@/features/games/types';
```

---

## 组件开发规范

### 组件结构

```typescript
/**
 * GameList 组件
 * 
 * 显示游戏列表，支持分页、筛选和搜索
 * 
 * @example
 * ```tsx
 * <GameList 
 *   games={games} 
 *   loading={loading}
 *   onGameSelect={handleGameSelect}
 * />
 * ```
 */

// 1. 导入
import React, { useState, useCallback } from 'react';
import type { GameListProps } from './GameList.types';

// 2. 组件定义
export function GameList({ games, loading, onGameSelect }: GameListProps) {
  // 3. Hooks
  const [searchTerm, setSearchTerm] = useState('');
  
  // 4. 计算属性
  const filteredGames = React.useMemo(
    () => games.filter(game => 
      game.name.toLowerCase().includes(searchTerm.toLowerCase())
    ),
    [games, searchTerm]
  );
  
  // 5. 事件处理器
  const handleSearch = useCallback((term: string) => {
    setSearchTerm(term);
  }, []);
  
  const handleGameClick = useCallback((game: Game) => {
    onGameSelect?.(game);
  }, [onGameSelect]);
  
  // 6. 渲染
  if (loading) {
    return <LoadingSpinner />;
  }
  
  return (
    <div className="game-list">
      <SearchBar onSearch={handleSearch} />
      <div className="game-list__items">
        {filteredGames.map(game => (
          <GameCard 
            key={game.id} 
            game={game} 
            onClick={handleGameClick}
          />
        ))}
      </div>
    </div>
  );
}

// 7. 默认导出（如果需要）
export default GameList;
```

### Props 接口定义

```typescript
/**
 * GameList 组件 Props
 */
export interface GameListProps {
  /** 游戏列表数据 */
  games: Game[];
  
  /** 是否正在加载 */
  loading?: boolean;
  
  /** 游戏选中回调 */
  onGameSelect?: (game: Game) => void;
  
  /** 自定义类名 */
  className?: string;
  
  /** 子元素 */
  children?: React.ReactNode;
}
```

### 组件注释规范

**文件头注释**：
```typescript
/**
 * GameList 组件
 * 
 * 功能描述：显示游戏列表，支持分页、筛选和搜索
 * 
 * @author Your Name
 * @created 2026-03-22
 */
```

**函数注释**：
```typescript
/**
 * 过滤游戏列表
 * 
 * @param games - 游戏列表
 * @param searchTerm - 搜索关键词
 * @returns 过滤后的游戏列表
 */
function filterGames(games: Game[], searchTerm: string): Game[] {
  // 实现
}
```

### 组件最佳实践

**1. 使用 TypeScript 类型安全**：
```typescript
// ✅ 正确：定义 Props 接口
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'danger';
  size: 'small' | 'medium' | 'large';
  disabled?: boolean;
  onClick?: () => void;
}

function Button({ variant, size, disabled, onClick }: ButtonProps) {
  // 实现
}

// ❌ 错误：不使用类型
function Button({ variant, size, disabled, onClick }) {
  // 实现
}
```

**2. 使用 React.memo 优化性能**：
```typescript
// ✅ 正确：使用 React.memo
export const GameCard = React.memo<GameCardProps>(({ game, onClick }) => {
  return (
    <div className="game-card" onClick={() => onClick(game)}>
      <h3>{game.name}</h3>
    </div>
  );
});

// ❌ 错误：不使用 memo
export const GameCard = ({ game, onClick }) => {
  return (
    <div className="game-card" onClick={() => onClick(game)}>
      <h3>{game.name}</h3>
    </div>
  );
};
```

**3. 解构 Props**：
```typescript
// ✅ 正确：解构 Props
function GameList({ games, loading, onGameSelect }: GameListProps) {
  // 实现
}

// ❌ 错误：不解构 Props
function GameList(props: GameListProps) {
  const { games, loading, onGameSelect } = props;
  // 实现
}
```

**4. 使用可选链和空值合并**：
```typescript
// ✅ 正确：使用可选链
const gameName = game?.name ?? 'Unknown';

// ❌ 错误：不使用可选链
const gameName = game && game.name ? game.name : 'Unknown';
```

---

## TypeScript 使用规范

### 类型定义

**接口 vs 类型**：
```typescript
// ✅ 使用接口定义对象结构
interface Game {
  id: string;
  name: string;
  description?: string;
}

// ✅ 使用类型定义联合类型、元组等
type EventStatus = 'active' | 'inactive' | 'pending';
type Coordinate = [number, number];
```

**泛型**：
```typescript
// ✅ 正确：使用泛型提供类型灵活性
interface ApiResponse<T> {
  data: T;
  message: string;
  success: boolean;
}

interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

// 使用示例
const response: ApiResponse<Game> = {
  data: { id: '1', name: 'Game 1' },
  message: 'Success',
  success: true,
};
```

**类型守卫**：
```typescript
// ✅ 正确：使用类型守卫
function isGame(obj: unknown): obj is Game {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'name' in obj
  );
}

// 使用示例
if (isGame(data)) {
  console.log(data.name); // TypeScript 知道这是 Game 类型
}
```

### 类型推断

**避免 any**：
```typescript
// ✅ 正确：使用具体类型
function processData(data: Game[]): Game[] {
  return data.map(game => ({
    ...game,
    processed: true,
  }));
}

// ❌ 错误：使用 any
function processData(data: any[]): any[] {
  return data.map(item => ({
    ...item,
    processed: true,
  }));
}
```

**使用 unknown 代替 any**：
```typescript
// ✅ 正确：使用 unknown
function parseJSON(json: string): unknown {
  return JSON.parse(json);
}

// ❌ 错误：使用 any
function parseJSON(json: string): any {
  return JSON.parse(json);
}
```

### 严格模式

确保 `tsconfig.json` 启用严格模式：

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true
  }
}
```

---

## React Hooks 规范

### Hooks 使用规则

**1. 只在顶层调用 Hooks**：
```typescript
// ✅ 正确
function GameList() {
  const [games, setGames] = useState([]);
  const { data } = useQuery(...);
  
  // ...
}

// ❌ 错误：在条件语句中使用
function GameList() {
  if (someCondition) {
    const [games, setGames] = useState([]); // 错误！
  }
}

// ❌ 错误：在循环中使用
function GameList() {
  games.forEach(game => {
    const [selected, setSelected] = useState(false); // 错误！
  });
}
```

**2. 只在 React 函数中调用 Hooks**：
```typescript
// ✅ 正确：在 React 组件中使用
function GameList() {
  const [games, setGames] = useState([]);
  // ...
}

// ✅ 正确：在自定义 Hook 中使用
function useGameData() {
  const [games, setGames] = useState([]);
  // ...
}

// ❌ 错误：在普通函数中使用
function processData() {
  const [data, setData] = useState([]); // 错误！
}
```

### 自定义 Hook 规范

**命名规范**：
```typescript
// ✅ 正确：使用 use 前缀
function useGameData() { }
function useModal() { }
function useDebounce() { }

// ❌ 错误：不使用 use 前缀
function gameData() { }
function modal() { }
```

**返回值**：
```typescript
// ✅ 正确：返回数组或对象
function useGameData(gameId: string) {
  const [data, setData] = useState<Game | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  
  // ...
  
  return { data, loading, error };
}

// ✅ 正确：返回数组（类似 useState）
function useToggle(initialValue: boolean = false) {
  const [value, setValue] = useState(initialValue);
  const toggle = useCallback(() => setValue(v => !v), []);
  return [value, toggle] as const;
}
```

**依赖数组**：
```typescript
// ✅ 正确：包含所有依赖
useEffect(() => {
  fetchData(gameId);
}, [gameId]); // gameId 是依赖

// ✅ 正确：使用 useCallback 缓存函数
const handleClick = useCallback(() => {
  console.log(gameId);
}, [gameId]);

useEffect(() => {
  handleClick();
}, [handleClick]); // handleClick 是依赖

// ❌ 错误：缺少依赖
useEffect(() => {
  fetchData(gameId);
}, []); // gameId 应该在依赖数组中
```

### 性能优化 Hooks

**useMemo**：
```typescript
// ✅ 正确：缓存计算结果
const filteredGames = useMemo(
  () => games.filter(game => 
    game.name.toLowerCase().includes(searchTerm.toLowerCase())
  ),
  [games, searchTerm]
);

// ❌ 错误：不使用 useMemo
const filteredGames = games.filter(game => 
  game.name.toLowerCase().includes(searchTerm.toLowerCase())
);
```

**useCallback**：
```typescript
// ✅ 正确：缓存函数
const handleGameClick = useCallback((game: Game) => {
  onGameSelect?.(game);
}, [onGameSelect]);

// ❌ 错误：不使用 useCallback
const handleGameClick = (game: Game) => {
  onGameSelect?.(game);
};
```

---

## 性能优化最佳实践

### 组件优化

**1. 使用 React.memo**：
```typescript
export const GameCard = React.memo<GameCardProps>(({ game, onClick }) => {
  return (
    <div className="game-card" onClick={() => onClick(game)}>
      <h3>{game.name}</h3>
    </div>
  );
}, (prevProps, nextProps) => {
  // 自定义比较函数
  return prevProps.game.id === nextProps.game.id;
});
```

**2. 虚拟滚动**：
```typescript
import { useVirtualizer } from '@tanstack/react-virtual';

function GameList({ games }: GameListProps) {
  const parentRef = useRef<HTMLDivElement>(null);
  
  const virtualizer = useVirtualizer({
    count: games.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 100,
  });
  
  return (
    <div ref={parentRef} style={{ height: '500px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px` }}>
        {virtualizer.getVirtualItems().map(virtualItem => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            <GameCard game={games[virtualItem.index]} />
          </div>
        ))}
      </div>
    </div>
  );
}
```

**3. 代码分割**：
```typescript
// ✅ 正确：使用 React.lazy
const GameList = React.lazy(() => import('@/features/games/components/GameList'));
const EventBuilder = React.lazy(() => import('@/features/events/components/EventBuilder'));

function App() {
  return (
    <React.Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/games" element={<GameList />} />
        <Route path="/events" element={<EventBuilder />} />
      </Routes>
    </React.Suspense>
  );
}
```

### 数据获取优化

**1. 使用 React Query 缓存**：
```typescript
// ✅ 正确：配置缓存
const { data } = useQuery({
  queryKey: ['games', gameId],
  queryFn: () => fetchGame(gameId),
  staleTime: 5 * 60 * 1000, // 5 分钟
  cacheTime: 10 * 60 * 1000, // 10 分钟
});

// ✅ 正确：预取数据
useQuery({
  queryKey: ['games'],
  queryFn: () => fetchGames(),
  onSuccess: (games) => {
    // 预取第一个游戏
    games[0] && queryClient.prefetchQuery({
      queryKey: ['games', games[0].id],
      queryFn: () => fetchGame(games[0].id),
    });
  },
});
```

**2. 防抖和节流**：
```typescript
import { useDebounce } from '@/shared/hooks';

function SearchBar() {
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearchTerm = useDebounce(searchTerm, 300);
  
  const { data } = useQuery({
    queryKey: ['search', debouncedSearchTerm],
    queryFn: () => searchGames(debouncedSearchTerm),
    enabled: debouncedSearchTerm.length > 2,
  });
  
  return (
    <input
      type="text"
      value={searchTerm}
      onChange={(e) => setSearchTerm(e.target.value)}
      placeholder="Search games..."
    />
  );
}
```

### 渲染优化

**1. 避免 inline 函数**：
```typescript
// ✅ 正确：使用 useCallback
const handleClick = useCallback(() => {
  console.log('Clicked');
}, []);

return <Button onClick={handleClick}>Click me</Button>;

// ❌ 错误：inline 函数
return <Button onClick={() => console.log('Clicked')}>Click me</Button>;
```

**2. 避免 inline 对象**：
```typescript
// ✅ 正确：使用 useMemo
const style = useMemo(() => ({
  padding: '16px',
  backgroundColor: 'white',
}), []);

return <div style={style}>Content</div>;

// ❌ 错误：inline 对象
return <div style={{ padding: '16px', backgroundColor: 'white' }}>Content</div>;
```

**3. 使用 key 优化列表**：
```typescript
// ✅ 正确：使用稳定的 key
{games.map(game => (
  <GameCard key={game.id} game={game} />
))}

// ❌ 错误：使用 index 作为 key
{games.map((game, index) => (
  <GameCard key={index} game={game} />
))}
```

---

## 错误处理规范

### 错误边界

```typescript
interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // 发送错误到日志服务
    logErrorToService(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="error-boundary">
          <h2>Something went wrong.</h2>
          <p>{this.state.error?.message}</p>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### API 错误处理

```typescript
// ✅ 正确：使用 React Query 的错误处理
const { data, error, isLoading } = useQuery({
  queryKey: ['games'],
  queryFn: async () => {
    try {
      const response = await fetch('/api/games');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    } catch (error) {
      console.error('Failed to fetch games:', error);
      throw error; // 重新抛出错误让 React Query 处理
    }
  },
  retry: 3,
  retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
});

if (error) {
  return <ErrorMessage error={error} />;
}
```

### 表单错误处理

```typescript
// ✅ 正确：使用 Zod 验证
const schema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

const form = useForm({
  resolver: zodResolver(schema),
});

return (
  <form onSubmit={form.handleSubmit(onSubmit)}>
    <FormField
      name="email"
      label="Email"
      error={form.formState.errors.email?.message}
    />
    <FormField
      name="password"
      label="Password"
      type="password"
      error={form.formState.errors.password?.message}
    />
    <Button type="submit" disabled={form.formState.isSubmitting}>
      {form.formState.isSubmitting ? 'Submitting...' : 'Submit'}
    </Button>
  </form>
);
```

---

## 测试规范

### 单元测试

**测试文件命名**：
```typescript
// 组件测试
GameList.test.tsx
useGameData.test.ts

// 工具函数测试
formatDate.test.ts
validateEmail.test.ts
```

**测试结构**：
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { GameList } from './GameList';

describe('GameList', () => {
  const mockGames = [
    { id: '1', name: 'Game 1' },
    { id: '2', name: 'Game 2' },
  ];

  it('should render game list', () => {
    render(<GameList games={mockGames} loading={false} />);
    
    expect(screen.getByText('Game 1')).toBeInTheDocument();
    expect(screen.getByText('Game 2')).toBeInTheDocument();
  });

  it('should show loading state', () => {
    render(<GameList games={[]} loading={true} />);
    
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  it('should call onGameSelect when game is clicked', async () => {
    const onGameSelect = vi.fn();
    render(
      <GameList 
        games={mockGames} 
        loading={false} 
        onGameSelect={onGameSelect} 
      />
    );
    
    fireEvent.click(screen.getByText('Game 1'));
    
    await waitFor(() => {
      expect(onGameSelect).toHaveBeenCalledWith(mockGames[0]);
    });
  });
});
```

### E2E 测试

**测试文件命名**：
```typescript
// E2E 测试
critical-journey.spec.ts
game-creation.spec.ts
event-builder.spec.ts
```

**测试结构**：
```typescript
import { test, expect } from '@playwright/test';

test.describe('Game Creation Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/games');
  });

  test('should create a new game', async ({ page }) => {
    // 点击创建按钮
    await page.click('[data-testid="create-game-button"]');
    
    // 填写表单
    await page.fill('[name="name"]', 'Test Game');
    await page.fill('[name="description"]', 'Test Description');
    
    // 提交表单
    await page.click('[type="submit"]');
    
    // 验证结果
    await expect(page.locator('text=Test Game')).toBeVisible();
  });

  test('should show validation error for empty name', async ({ page }) => {
    await page.click('[data-testid="create-game-button"]');
    await page.click('[type="submit"]');
    
    await expect(page.locator('text=Name is required')).toBeVisible();
  });
});
```

### 测试覆盖率

目标覆盖率：
- **语句覆盖率**: > 80%
- **分支覆盖率**: > 75%
- **函数覆盖率**: > 80%
- **行覆盖率**: > 80%

运行覆盖率测试：
```bash
npm run test:coverage
```

---

## 代码格式化

### ESLint 配置

项目使用 ESLint 进行代码检查：

```bash
# 运行检查
npm run lint

# 自动修复
npm run lint:fix
```

### Prettier 配置

项目使用 Prettier 进行代码格式化：

```bash
# 格式化代码
npm run format
```

### EditorConfig

项目根目录包含 `.editorconfig` 文件，确保不同编辑器的代码风格一致。

---

## 总结

遵循本规范可以确保：
- ✅ 代码一致性和可读性
- ✅ 更少的 bug 和错误
- ✅ 更容易的维护和重构
- ✅ 更好的团队协作
- ✅ 更高的代码质量

**如有疑问，请参考：**
- [贡献指南](CONTRIBUTING.md)
- [React 官方文档](https://react.dev/)
- [TypeScript 官方文档](https://www.typescriptlang.org/)

---

**文档版本**: 1.0
**最后更新**: 2026-03-22
**维护者**: Event2Table Frontend Team
