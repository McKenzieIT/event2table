# Management Pages E2E Test - Fix Guide

**测试日期**: 2026-03-03
**问题数量**: 3个 (1个P0, 2个P1)
**修复优先级**: P0 - 立即修复

---

## 问题概览

| ID | 优先级 | 问题 | 状态 |
|----|--------|------|------|
| #1 | P0 | "新建流程"按钮导航错误 | 🔴 未修复 |
| #2 | P1 | Categories页面重定向到Dashboard | 🔴 未修复 |
| #3 | P1 | Common Params页面重定向到Dashboard | 🔴 未修复 |

---

## 问题 #1: "新建流程"按钮导航错误 (P0)

### 症状

点击"新建流程"按钮后，页面跳转到事件创建页面而非流程创建页面。

**导航历史**:
```
点击前: http://localhost:5173/#/flows?game_gid=10000147
点击后: http://localhost:5173/#/events/create?game_gid=10000147
```

### 根本原因

按钮的 `onClick` 处理器错误配置为导航到 `/events/create`。

### 修复步骤

#### 步骤1: 定位问题代码

**文件**: `frontend/src/analytics/pages/FlowsList.tsx`

**查找代码**:
```typescript
// ❌ 错误代码
<Button onClick={() => navigate('/events/create')}>
  新建流程
</Button>
```

#### 步骤2: 修复代码

**方案A: 使用模态框 (推荐)**

```typescript
// 1. 添加状态
const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

// 2. 修改按钮
<Button onClick={() => setIsModalOpen(true)}>
  新建流程
</Button>

// 3. 添加模态框
{isModalOpen && (
  <FlowCreateModal
    gameGid={gameGid}
    onClose={() => setIsModalOpen(false)}
    onSuccess={() => {
      setIsModalOpen(false);
      queryClient.invalidateQueries(['flows']);
    }}
  />
)}
```

**方案B: 导航到流程创建页面**

```typescript
// 修改按钮导航路径
<Button onClick={() => navigate('/flows/create?game_gid=' + gameGid)}>
  新建流程
</Button>
```

#### 步骤3: 创建FlowCreateModal组件 (如果使用方案A)

**文件**: `frontend/src/analytics/components/flows/FlowCreateModal.tsx`

```typescript
import { useState } from 'react';
import { Dialog } from '@shared/ui/Dialog/Dialog';
import { Input } from '@shared/ui/Input/Input';
import { Button } from '@shared/ui/Button/Button';

interface FlowCreateModalProps {
  gameGid: string;
  onClose: () => void;
  onSuccess: () => void;
}

export default function FlowCreateModal({
  gameGid,
  onClose,
  onSuccess
}: FlowCreateModalProps) {
  const [flowName, setFlowName] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = async () => {
    const response = await fetch('/api/flows', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        game_gid: gameGid,
        flow_name: flowName,
        description
      })
    });

    if (response.ok) {
      onSuccess();
    }
  };

  return (
    <Dialog open={true} onClose={onClose} title="新建流程">
      <Input
        label="流程名称"
        value={flowName}
        onChange={(e) => setFlowName(e.target.value)}
      />
      <Input
        label="描述"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />
      <Button onClick={handleSubmit}>创建</Button>
      <Button onClick={onClose}>取消</Button>
    </Dialog>
  );
}
```

#### 步骤4: 验证修复

1. 启动开发服务器: `cd frontend && npm run dev`
2. 导航到: `http://localhost:5173/#/flows?game_gid=10000147`
3. 点击"新建流程"按钮
4. 验证: 打开模态框或导航到流程创建页面 (而非事件创建)

### 预期结果

- ✅ 点击"新建流程"后打开流程创建界面
- ✅ 创建成功后刷新流程列表
- ✅ 不再跳转到事件创建页面

---

## 问题 #2 & #3: Categories和Common Params页面重定向 (P1)

### 症状

导航到Categories或Common Params页面后，页面短暂显示正确标题，然后重定向到Dashboard。

**现象**:
```
1. 导航到: #/categories?game_gid=10000147
2. 短暂显示: "分类管理"
3. hash变为空: window.location.hash = ""
4. 最终显示: Dashboard内容
```

### 根本原因分析

#### 可能原因1: 路由顺序问题

**文件**: `frontend/src/routes/routes.tsx`

**问题**: 通配符路由 `path: "*"` 可能捕获了所有路由

**检查**:
```typescript
// ❌ 错误: 通配符路由在前
{ path: "*", element: <NotFound /> },
{ path: "categories", element: <CategoriesList /> },

// ✅ 正确: 具体路由在前
{ path: "categories", element: <CategoriesList /> },
{ path: "common-params", element: <CommonParamsList /> },
{ path: "*", element: <NotFound /> }, // 放在最后
```

#### 可能原因2: 组件内部重定向

**文件**:
- `frontend/src/analytics/pages/CategoriesListGraphQL.tsx`
- `frontend/src/analytics/pages/CommonParamsList.tsx`

**检查**: 查找 `useEffect` 中的 `navigate` 调用

```typescript
// ❌ 错误: 不必要的重定向
useEffect(() => {
  if (!gameGid) {
    navigate('/'); // 这会导致重定向
  }
}, [gameGid, navigate]);

// ✅ 正确: 使用React Query的enabled
const { data } = useQuery({
  queryKey: ['categories', gameGid],
  queryFn: fetchCategories,
  enabled: !!gameGid // 不运行查询而非重定向
});
```

#### 可能原因3: MainLayout路由守卫

**文件**: `frontend/src/shared/components/layouts/MainLayout.tsx`

**检查**: 查找路由守卫或权限检查逻辑

```typescript
// ❌ 错误: 过度严格的权限检查
useEffect(() => {
  if (!hasAccess) {
    navigate('/');
  }
}, [hasAccess, navigate]);
```

### 修复步骤

#### 步骤1: 检查路由顺序

**文件**: `frontend/src/routes/routes.tsx`

**验证路由配置**:
```typescript
export const routes: RouteObject[] = [
  {
    element: <MainLayout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: "canvas", element: <CanvasPage /> },
      { path: "flows", element: <FlowsList /> },
      { path: "categories", element: <CategoriesList /> }, // ✅ 在通配符之前
      { path: "common-params", element: <CommonParamsList /> }, // ✅ 在通配符之前
      { path: "events", element: <EventsList /> },
      { path: "parameters", element: <ParametersList /> },
      // ... 其他具体路由
      { path: "*", element: <NotFound /> }, // ✅ 通配符放最后
    ],
  },
];
```

#### 步骤2: 检查组件内部重定向

**文件**: `frontend/src/analytics/pages/CategoriesListGraphQL.tsx`

**查找并移除不必要的重定向**:
```typescript
// ❌ 移除这样的代码
useEffect(() => {
  if (!gameGid) {
    navigate('/');
  }
}, [gameGid, navigate]);
```

**正确做法**:
```typescript
// ✅ 使用React Query的enabled
const { data, isLoading, error } = useCategories(
  100,
  0,
  !!gameGid // 仅当gameGid存在时才查询
);
```

#### 步骤3: 检查MainLayout

**文件**: `frontend/src/shared/components/layouts/MainLayout.tsx`

**查找并注释掉路由守卫** (如果存在):
```typescript
// ❌ 暂时注释掉以调试
// useEffect(() => {
//   if (!hasAccess) {
//     navigate('/');
//   }
// }, [hasAccess, navigate]);
```

#### 步骤4: 添加调试日志

**在CategoriesListGraphQL.tsx中添加**:
```typescript
useEffect(() => {
  console.log('[CategoriesListGraphQL] Mounted');
  console.log('[CategoriesListGraphQL] gameGid:', gameGid);
  console.log('[CategoriesListGraphQL] window.location.hash:', window.location.hash);

  return () => {
    console.log('[CategoriesListGraphQL] Unmounted');
  };
}, [gameGid]);
```

#### 步骤5: 验证修复

1. 启动开发服务器: `cd frontend && npm run dev`
2. 打开浏览器控制台
3. 导航到: `http://localhost:5173/#/categories?game_gid=10000147`
4. 观察控制台日志
5. 验证: 页面保持显示，不重定向到Dashboard

### 预期结果

- ✅ Categories页面正常显示，不重定向
- ✅ Common Params页面正常显示，不重定向
- ✅ 所有CRUD操作可用

---

## 验证清单

### 修复后验证

**问题 #1验证**:
- [ ] 导航到Flows页面
- [ ] 点击"新建流程"按钮
- [ ] 验证打开流程创建界面 (模态框或页面)
- [ ] 创建新流程成功
- [ ] 流程列表刷新显示新流程

**问题 #2 & #3验证**:
- [ ] 导航到Categories页面
- [ ] 验证页面正常显示，不重定向
- [ ] 测试创建分类功能
- [ ] 测试编辑分类功能
- [ ] 测试删除分类功能
- [ ] 导航到Common Params页面
- [ ] 验证页面正常显示，不重定向
- [ ] 测试添加公参功能
- [ ] 测试编辑公参功能
- [ ] 测试删除公参功能

---

## 修复优先级

### 立即修复 (今天)

1. **P0 - 问题 #1**: "新建流程"按钮导航错误
   - 修复时间: 30分钟
   - 影响: 用户无法创建新流程

### 高优先级 (本周)

2. **P1 - 问题 #2**: Categories页面重定向
   - 修复时间: 1小时
   - 影响: 用户无法管理分类

3. **P1 - 问题 #3**: Common Params页面重定向
   - 修复时间: 1小时 (与问题#2一起修复)
   - 影响: 用户无法管理公参

---

## 相关文档

- [完整测试报告](./MANAGEMENT-PAGES-E2E-TEST-REPORT.md)
- [路由配置指南](../../development/getting-started.md)
- [React Query使用指南](../../development/api-development.md)

---

**最后更新**: 2026-03-03
**修复负责人**: 待分配
**修复期限**: P0 - 今天, P1 - 本周
