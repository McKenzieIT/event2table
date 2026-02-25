# 前端GraphQL集成指南

## 已完成工作

### 1. 安装依赖
```bash
npm install @apollo/client graphql
```

### 2. 创建的文件

```
frontend/src/graphql/
├── client.ts          # Apollo Client配置
├── queries.ts         # GraphQL查询定义
├── mutations.ts       # GraphQL变更定义
├── hooks.ts           # 自定义React Hooks
└── index.ts           # 导出文件

frontend/src/components/
└── GamesGraphQL.tsx   # 示例组件
```

## 使用方法

### 1. 在应用入口配置Apollo Provider

```tsx
// src/main.tsx 或 src/App.tsx
import { ApolloProvider } from '@apollo/client';
import { client } from './graphql';

function App() {
  return (
    <ApolloProvider client={client}>
      {/* Your app components */}
    </ApolloProvider>
  );
}
```

### 2. 在组件中使用GraphQL

#### 查询数据

```tsx
import { useGames } from './graphql';

function GamesList() {
  const { loading, error, data } = useGames(20);
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return (
    <ul>
      {data.games.map(game => (
        <li key={game.gid}>{game.name}</li>
      ))}
    </ul>
  );
}
```

#### 执行变更

```tsx
import { useCreateGame } from './graphql';

function CreateGameForm() {
  const [createGame, { loading, error }] = useCreateGame();
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const result = await createGame({
      variables: {
        gid: 99999999,
        name: 'Test Game',
        odsDb: 'ieu_ods',
      },
    });
    
    if (result.data?.createGame?.ok) {
      alert('Game created!');
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <button type="submit" disabled={loading}>
        Create Game
      </button>
    </form>
  );
}
```

## 可用的Hooks

### 查询Hooks

- `useGames(limit?, offset?)` - 获取游戏列表
- `useGame(gid)` - 获取单个游戏
- `useSearchGames(query)` - 搜索游戏
- `useEvents(gameGid, limit?, offset?)` - 获取事件列表
- `useEvent(id)` - 获取单个事件
- `useSearchEvents(query, gameGid?)` - 搜索事件

### 变更Hooks

- `useCreateGame()` - 创建游戏
- `useUpdateGame()` - 更新游戏
- `useDeleteGame()` - 删除游戏
- `useCreateEvent()` - 创建事件
- `useUpdateEvent()` - 更新事件
- `useDeleteEvent()` - 删除事件

## GraphQL vs REST对比

### REST API
```typescript
// 需要多次请求
const games = await fetch('/api/games');
const events = await fetch('/api/events?game_gid=10000147');
```

### GraphQL API
```typescript
// 一次请求获取所有数据
const { data } = useQuery(gql`
  query GetGamesWithEvents {
    games(limit: 10) {
      gid
      name
      events {
        id
        eventName
      }
    }
  }
`);
```

## 优势

1. **按需获取**: 只请求需要的字段
2. **减少请求**: 一次请求获取关联数据
3. **类型安全**: TypeScript类型推导
4. **缓存**: Apollo Client自动缓存
5. **实时更新**: 支持轮询和订阅

## 注意事项

1. GraphQL端点: `http://localhost:5001/api/graphql`
2. 确保后端服务已启动
3. 开发环境可访问GraphiQL IDE: `http://localhost:5001/api/graphql`
4. 生产环境需要配置正确的CORS

## 下一步

1. 在主应用中集成Apollo Provider
2. 逐步迁移REST API调用到GraphQL
3. 添加错误处理和加载状态
4. 优化缓存策略
5. 添加订阅功能实现实时更新
