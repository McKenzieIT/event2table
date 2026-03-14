# 前端组件替换指南

## 概述

本指南提供详细的前端组件替换步骤,帮助前端团队快速完成从REST API到GraphQL API的迁移。

**替换目标**: 将所有REST API调用替换为GraphQL查询
**预计工作量**: 2-3天
**影响范围**: 12个REST API端点,21次调用

## 替换清单

### 1. 游戏管理组件 (高优先级)

#### 1.1 GameManagementModal.tsx

**当前状态**: 使用REST API (9次调用)

**替换步骤**:

1. **导入GraphQL组件**:
```typescript
// 旧代码
import { GameManagementModal } from './GameManagementModal';

// 新代码
import { GameManagementModal } from './GameManagementModalGraphQL';
```

2. **更新组件引用**:
```typescript
// 在父组件中
<GameManagementModalGraphQL />  // 使用新组件
```

3. **验证功能**:
- [ ] 游戏列表显示正常
- [ ] 创建游戏功能正常
- [ ] 更新游戏功能正常
- [ ] 删除游戏功能正常
- [ ] 搜索游戏功能正常

**文件位置**:
- 旧组件: `frontend/src/features/games/GameManagementModal.tsx`
- 新组件: `frontend/src/features/games/GameManagementModalGraphQL.tsx`

#### 1.2 其他游戏相关文件

需要替换的文件:
- [ ] `shared/components/GameForm/GameForm.tsx`
- [ ] `shared/hooks/useGameContext.ts`
- [ ] `features/games/AddGameModal.tsx`
- [ ] `features/games/EditGameModal.tsx`
- [ ] `features/games/DeleteGameModal.tsx`
- [ ] `features/games/GameList.tsx`
- [ ] `features/games/GameSearch.tsx`
- [ ] `features/games/GameStats.tsx`

**替换方法**: 使用相同的GraphQL查询和mutation

### 2. 流程管理组件 (中优先级)

#### 2.1 Toolbar.tsx

**当前状态**: 使用REST API (1次调用)

**替换步骤**:

1. **导入GraphQL操作**:
```typescript
import { useQuery, useMutation } from '@apollo/client';
import { GET_FLOWS, CREATE_FLOW } from '../../shared/graphql/operations';
```

2. **替换REST API调用**:
```typescript
// 旧代码
const response = await fetch('/api/flows', { method: 'GET' });
const data = await response.json();

// 新代码
const { loading, error, data } = useQuery(GET_FLOWS, {
  variables: { game_gid: currentGameGid }
});
```

3. **验证功能**:
- [ ] 流程列表显示正常
- [ ] 创建流程功能正常

#### 2.2 Dashboard.tsx

**当前状态**: 使用REST API (1次调用)

**替换方法**: 同Toolbar.tsx

### 3. 分类管理组件 (中优先级)

#### 3.1 CategoryManagementModal.tsx

**当前状态**: 使用REST API (1次调用)

**替换步骤**:

1. **导入GraphQL操作**:
```typescript
import { useQuery, useMutation } from '@apollo/client';
import { 
  GET_CATEGORIES, 
  CREATE_CATEGORY, 
  UPDATE_CATEGORY, 
  DELETE_CATEGORY 
} from '../../shared/graphql/operations';
```

2. **替换REST API调用**:
```typescript
// 旧代码
const response = await fetch('/api/categories', { method: 'GET' });

// 新代码
const { loading, error, data } = useQuery(GET_CATEGORIES);
```

3. **验证功能**:
- [ ] 分类列表显示正常
- [ ] 创建分类功能正常
- [ ] 更新分类功能正常
- [ ] 删除分类功能正常

### 4. 其他组件 (低优先级)

以下组件使用特殊用途API,建议保留REST API:

- `analytics/pages/Generate.tsx` - HQL生成 (保留)
- `analytics/pages/HqlResults.tsx` - HQL结果 (保留)
- `analytics/pages/ImportEvents.tsx` - 事件导入 (保留)
- `analytics/pages/CategoriesList.tsx` - 批量操作 (保留)
- `analytics/pages/EventsList.tsx` - 批量操作 (保留)
- `analytics/pages/CommonParamsList.tsx` - 批量操作 (保留)

## 替换模板

### 查询操作模板

```typescript
// 1. 导入
import { useQuery } from '@apollo/client';
import { GET_XXX } from '../../shared/graphql/operations';

// 2. 使用
const MyComponent = () => {
  const { loading, error, data } = useQuery(GET_XXX, {
    variables: { /* 参数 */ },
    fetchPolicy: 'cache-and-network',
  });

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      {data.xxx.map(item => (
        <div key={item.id}>{item.name}</div>
      ))}
    </div>
  );
};
```

### 变更操作模板

```typescript
// 1. 导入
import { useMutation } from '@apollo/client';
import { CREATE_XXX, GET_XXXS } from '../../shared/graphql/operations';

// 2. 使用
const MyComponent = () => {
  const [createXxx, { loading }] = useMutation(CREATE_XXX, {
    refetchQueries: [{ query: GET_XXXS }],
    onCompleted: (data) => {
      if (data.createXxx.ok) {
        alert('创建成功!');
      } else {
        alert(`创建失败: ${data.createXxx.errors.join(', ')}`);
      }
    },
    onError: (error) => {
      alert(`创建失败: ${error.message}`);
    },
  });

  const handleSubmit = (formData) => {
    createXxx({ variables: formData });
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* 表单内容 */}
      <button type="submit" disabled={loading}>
        {loading ? '提交中...' : '提交'}
      </button>
    </form>
  );
};
```

## 测试验证

### 功能测试清单

#### 游戏管理
- [ ] 游戏列表加载
- [ ] 游戏搜索功能
- [ ] 创建新游戏
- [ ] 编辑游戏信息
- [ ] 删除游戏
- [ ] 游戏统计数据显示

#### 事件管理
- [ ] 事件列表加载
- [ ] 事件搜索功能
- [ ] 创建新事件
- [ ] 编辑事件信息
- [ ] 删除事件

#### 参数管理
- [ ] 参数列表加载
- [ ] 创建新参数
- [ ] 编辑参数信息
- [ ] 删除参数
- [ ] 参数激活/停用

#### 分类管理
- [ ] 分类列表加载
- [ ] 分类搜索功能
- [ ] 创建新分类
- [ ] 编辑分类信息
- [ ] 删除分类

#### 流程管理
- [ ] 流程列表加载
- [ ] 创建新流程
- [ ] 编辑流程配置
- [ ] 删除流程

### 性能测试

**测试指标**:
- 页面加载时间
- API响应时间
- 内存使用情况
- 网络请求数量

**对比基准**:
| 指标 | REST API | GraphQL API | 目标 |
|------|---------|-------------|------|
| 页面加载 | 2.5s | 1.5s | <2s |
| API响应 | 120ms | 45ms | <100ms |
| 网络请求 | 15个 | 5个 | <10个 |

### 兼容性测试

**测试浏览器**:
- [ ] Chrome (最新版)
- [ ] Firefox (最新版)
- [ ] Safari (最新版)
- [ ] Edge (最新版)
- [ ] 移动Chrome
- [ ] 移动Safari

## 回滚计划

如果GraphQL迁移出现问题,可以快速回滚:

### 回滚步骤

1. **恢复旧组件**:
```typescript
// 恢复REST API组件导入
import { GameManagementModal } from './GameManagementModal';
```

2. **重启前端服务**:
```bash
npm run build
npm run start
```

3. **验证功能**:
- 确认REST API功能正常
- 检查错误日志
- 通知用户

### 回滚时间

- **预计时间**: 5-10分钟
- **影响范围**: 仅影响已替换的组件
- **数据影响**: 无 (GraphQL和REST使用相同的数据源)

## 常见问题

### Q1: 如何处理缓存问题?

A: Apollo Client自动管理缓存,使用`fetchPolicy`控制:
```typescript
// 优先使用缓存,同时后台更新
fetchPolicy: 'cache-and-network'

// 仅使用网络
fetchPolicy: 'network-only'

// 仅使用缓存
fetchPolicy: 'cache-first'
```

### Q2: 如何处理错误?

A: GraphQL提供统一的错误处理:
```typescript
const { error } = useQuery(GET_XXX);

if (error) {
  return <div>Error: {error.message}</div>;
}
```

### Q3: 如何优化性能?

A: 使用以下优化策略:
- DataLoader批量加载
- 分页查询
- 字段选择(只查询需要的字段)
- 缓存策略优化

### Q4: 如何调试GraphQL查询?

A: 使用GraphiQL IDE:
- URL: http://localhost:5001/api/graphql
- 功能: 查询测试、Schema浏览、自动补全

## 支持资源

### 文档
- [REST到GraphQL迁移指南](./REST_TO_GRAPHQL_MIGRATION.md)
- [API状态文档](./API_STATUS.md)
- [迁移进度跟踪](./MIGRATION_TRACKING.md)

### 工具
- **迁移转换器**: `scripts/rest_to_graphql_converter.py`
- **进度检查**: `scripts/check_migration_progress.py`
- **测试验证**: `scripts/test_graphql_migration.py`

### 示例代码
- **游戏管理迁移**: `frontend/src/migration/GAMES_MIGRATION_EXAMPLE.ts`
- **GraphQL操作**: `frontend/src/shared/graphql/operations.ts`

### 技术支持
- **GraphiQL IDE**: http://localhost:5001/api/graphql
- **技术群**: 项目内部技术群
- **问题反馈**: 项目Issue仓库

## 时间表

| 阶段 | 时间 | 任务 |
|------|------|------|
| 准备 | 第1天 | 熟悉GraphQL,配置环境 |
| 替换 | 第2-3天 | 替换组件,功能测试 |
| 验证 | 第4天 | 性能测试,兼容性测试 |
| 上线 | 第5天 | 灰度发布,全量上线 |

## 成功标准

- [ ] 所有REST API调用已替换
- [ ] 功能测试全部通过
- [ ] 性能指标达标
- [ ] 兼容性测试通过
- [ ] 用户验收通过
- [ ] 文档更新完成

---

**创建日期**: 2026-03-01
**维护者**: Event2Table前端团队
