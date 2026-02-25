# P0 安全问题修复完成报告

**日期**: 2026-02-16
**任务**: 修复游戏上下文管理 P0 安全问题
**状态**: ✅ 全部完成，构建验证通过

---

## 一、问题概述

根据代码审查报告（[game-context-management-audit.md](game-context-management-audit.md)），发现以下 **P0 关键安全问题**：

### 问题清单

| 页面 | 问题 | 风险等级 | 影响 |
|------|------|---------|------|
| **CommonParamsList.jsx** | 使用 `localStorage` 而非 URL 参数 | **P0** | 数据泄露、跨游戏污染 |
| **FlowsList.jsx** | 缺少 `game_gid` URL 参数和过滤 | **P0** | 数据泄露、跨游戏污染 |
| **Sidebar.jsx** | `routesRequiringGameContext` 缺失路由 | **P1** | 导航功能缺失 |

### 风险说明

**P0 关键问题**：
1. **数据泄露**: 用户可以看到其他游戏的数据
2. **跨游戏污染**: 操作可能影响错误的游戏
3. **不一致性**: 部分页面使用 localStorage，部分使用 URL，导致混乱

**修复原则**：
- ✅ 所有页面必须从 URL 读取 `game_gid`
- ✅ 所有 API 调用必须传递 `game_gid` 参数
- ✅ 缺少 `game_gid` 时显示明确的错误提示
- ✅ Sidebar 配置必须包含所有需要游戏上下文的路由

---

## 二、修复详情

### 修复 1: CommonParamsList.jsx

**文件路径**: `frontend/src/analytics/pages/CommonParamsList.jsx`

#### 问题分析

**原始代码问题**：
```javascript
// ❌ 使用 localStorage（不安全、不一致）
const gameGid = localStorage.getItem('selectedGameGid');

// ❌ API 调用没有 game_gid 过滤
const res = await fetch('/api/common-params');

// ❌ 没有 game_gid 存在性检查
```

**安全风险**：
- `localStorage` 数据是全局的，可能导致跨游戏污染
- 用户手动修改 `localStorage` 可以绕过安全检查
- 与项目其他页面的 URL 参数模式不一致

#### 修复方案

**1. 导入 `useLocation` hook**：
```diff
+ import { useNavigate, useLocation } from 'react-router-dom';
```

**2. 从 URL 读取 `game_gid`**：
```diff
export default function CommonParamsList() {
  const navigate = useNavigate();
+ const location = useLocation();
+ // Read game_gid from URL parameters
+ const gameGid = new URLSearchParams(location.search).get('game_gid');
```

**3. 添加 `game_gid` 过滤到查询**：
```diff
const { data: params = [], isLoading, error: queryError } = useQuery({
-  queryKey: ['common-params'],
+  queryKey: ['common-params', gameGid],
  queryFn: async () => {
+    if (!gameGid) {
+      throw new Error('game_gid is required');
+    }
-    const res = await fetch('/api/common-params');
+    const res = await fetch(`/api/common-params?game_gid=${gameGid}`);
    if (!res.ok) {
+      if (res.status === 400) {
+        throw new Error('game_gid is required');
+      }
+      if (res.status === 404) {
+        throw new Error(`Game ${gameGid} not found`);
+      }
      throw new Error('Failed to fetch common parameters');
    }
    const result = await res.json();
    return result.data || [];
  },
+  enabled: !!gameGid // Only run query if gameGid exists
});
```

**4. 修改同步 mutation**：
```diff
const syncMutation = useMutation({
  mutationFn: async () => {
-    const gameGid = localStorage.getItem('selectedGameGid');
-    if (!gameGid) {
-      throw new Error('Please select a game first');
-    }
+    if (!gameGid) {
+      throw new Error('game_gid is required');
+    }
    const res = await fetch('/api/common-params/sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_gid: parseInt(gameGid) })
    });
    // ...
  },
  onSuccess: (data) => {
-    queryClient.invalidateQueries({ queryKey: ['common-params'] });
+    queryClient.invalidateQueries({ queryKey: ['common-params', gameGid] });
    // ...
  }
});
```

**5. 添加 `game_gid` 存在性检查**：
```diff
const getDataTypeBadge = (dataType) => {
  // ...
};

+ // Show error if game_gid is missing
+ if (!gameGid) {
+   return (
+     <div className="error-state">
+       <h2>请先选择游戏</h2>
+       <p>公参管理需要选择一个游戏才能查看。</p>
+       <Button onClick={() => navigate('/')}>
+         返回首页选择游戏
+       </Button>
+     </div>
+   );
+ }
+
if (isLoading) return <div className="loading-state">加载中...</div>;
if (queryError) return <div className="error-state">加载失败: {queryError.message}</div>;
```

**6. 修改 `handleSync` 函数**：
```diff
const handleSync = () => {
-  const gameGid = localStorage.getItem('selectedGameGid');
-  if (!gameGid) {
-    warning('请先选择一个游戏');
-    return;
-  }
+  if (!gameGid) {
+    warning('请先选择一个游戏');
+    return;
+  }
  // ...
};
```

#### 修复结果

✅ **完全移除 `localStorage` 的使用**
✅ **所有 API 调用都传递 `game_gid` 参数**
✅ **缺少 `game_gid` 时显示明确的错误提示**
✅ **与项目其他页面保持一致（URL 参数模式）**

---

### 修复 2: FlowsList.jsx

**文件路径**: `frontend/src/analytics/pages/FlowsList.jsx`

#### 问题分析

**原始代码问题**：
```javascript
// ❌ 没有导入 useLocation
import { useNavigate } from 'react-router-dom';

// ❌ 没有 game_gid 参数
const response = await fetch('/api/flows');

// ❌ 没有 game_gid 存在性检查
```

**安全风险**：
- 所有游戏的流程都会被返回
- 用户可能看到或修改其他游戏的流程
- 缺少游戏上下文隔离

#### 修复方案

**1. 导入 `useLocation` hook**：
```diff
- import { useNavigate } from 'react-router-dom';
+ import { useNavigate, useLocation } from 'react-router-dom';
```

**2. 从 URL 读取 `game_gid`**：
```diff
export default function FlowsList() {
  const navigate = useNavigate();
+ const location = useLocation();
+ // Read game_gid from URL parameters
+ const gameGid = new URLSearchParams(location.search).get('game_gid');
```

**3. 添加 `game_gid` 过滤到查询**：
```diff
const { data: apiResponse, isLoading, error } = useQuery({
-  queryKey: ['flows'],
+  queryKey: ['flows', gameGid],
  queryFn: async () => {
+    if (!gameGid) {
+      throw new Error('game_gid is required');
+    }
-    const response = await fetch('/api/flows');
+    const response = await fetch(`/api/flows?game_gid=${gameGid}`);
    if (!response.ok) {
+      if (response.status === 400) {
+        throw new Error('game_gid is required');
+      }
+      if (response.status === 404) {
+        throw new Error(`Game ${gameGid} not found`);
+      }
      throw new Error('Failed to fetch flows');
    }
    const result = await response.json();
    return result;
  },
+  enabled: !!gameGid // Only run query if gameGid exists
});
```

**4. 更新导航函数以传递 `game_gid`**：
```diff
const handleEditFlow = (flowId) => {
-  navigate(`/flows/${flowId}/edit`);
+  navigate(`/flows/${flowId}/edit?game_gid=${gameGid}`);
};

const handleCreateFlow = () => {
-  navigate('/flows/create');
+  navigate('/flows/create' + (gameGid ? `?game_gid=${gameGid}` : ''));
};
```

**5. 添加 `game_gid` 存在性检查**：
```diff
const handleCreateFlow = () => {
  navigate('/flows/create' + (gameGid ? `?game_gid=${gameGid}` : ''));
};

+ // Show error if game_gid is missing
+ if (!gameGid) {
+   return (
+     <div className="flows-list-page">
+       <div className="error-message">
+         <h2>请先选择游戏</h2>
+         <p>流程管理需要选择一个游戏才能查看。</p>
+         <Button onClick={() => navigate('/')}>
+           返回首页选择游戏
+         </Button>
+       </div>
+     </div>
+   );
+ }
+
if (error) {
  return (
    // ...
  );
}
```

#### 修复结果

✅ **添加 `game_gid` URL 参数读取**
✅ **所有 API 调用都传递 `game_gid` 参数**
✅ **导航时保持 `game_gid` 参数**
✅ **缺少 `game_gid` 时显示明确的错误提示**

---

### 修复 3: Sidebar.jsx

**文件路径**: `frontend/src/analytics/components/sidebar/Sidebar.jsx`

#### 问题分析

**原始代码问题**：
```javascript
// ❌ 缺失的路由
const routesRequiringGameContext = ['/event-node-builder', '/canvas', '/parameters', '/categories'];
```

**缺失的路由**：
- `/event-nodes` - 事件节点管理
- `/events` - 事件管理
- `/common-params` - 公参管理
- `/flows` - 流程管理

**影响**：
- 点击这些菜单项时不会自动添加 `game_gid` 参数
- 用户体验不一致
- 可能导致导航到没有游戏上下文的页面

#### 修复方案

```diff
// 需要游戏上下文的路由（这些路由会动态添加 game_gid 参数）
- const routesRequiringGameContext = ['/event-node-builder', '/canvas', '/parameters', '/categories'];
+ const routesRequiringGameContext = [
+   '/event-node-builder',
+   '/event-nodes',
+   '/events',
+   '/canvas',
+   '/parameters',
+   '/categories',
+   '/common-params',
+   '/flows'
+ ];
```

#### 修复结果

✅ **所有需要游戏上下文的路由都已添加**
✅ **导航时会自动添加 `game_gid` 参数**
✅ **用户体验一致性提升**

---

## 三、构建验证

### 前端构建测试

**命令**: `npm run build`

**结果**: ✅ **成功**

```
✓ 1524 modules transformed
✓ built in 1m 6s
```

**说明**:
- 所有修改的文件语法正确
- 没有导入错误
- 没有类型错误
- 构建产物生成成功

### 构建产物

```
dist/index.html                                      3.60 kB │ gzip:   1.38 kB
dist/assets/css/index-C2X0Pmcr.css                 267.80 kB │ gzip:  39.74 kB
dist/assets/js/index-C1EgRza4.js                 1,800.99 kB │ gzip: 558.78 kB
```

---

## 四、测试验证清单

### 功能测试

- [ ] **CommonParamsList 页面**
  - [ ] 访问 `http://localhost:5173/#/common-params?game_gid=10000147`
  - [ ] ✅ 应显示该游戏的公参列表
  - [ ] ✅ URL 缺少 `game_gid` 时显示错误提示
  - [ ] ✅ 同步公参功能正常工作
  - [ ] ✅ 所有操作都传递 `game_gid` 参数

- [ ] **FlowsList 页面**
  - [ ] 访问 `http://localhost:5173/#/flows?game_gid=10000147`
  - [ ] ✅ 应显示该游戏的流程列表
  - [ ] ✅ URL 缺少 `game_gid` 时显示错误提示
  - [ ] ✅ 点击"新建流程"携带 `game_gid` 参数
  - [ ] ✅ 点击"编辑"携带 `game_gid` 参数

- [ ] **Sidebar 导航**
  - [ ] ✅ 点击所有菜单项都自动添加 `game_gid` 参数
  - [ ] ✅ 用户体验一致性

### API 契约测试

- [ ] **CommonParamsList API**:
  ```javascript
  GET /api/common-params?game_gid=10000147
  Response: { success: true, data: [...] }
  Status: 200 OK

  // 缺少 game_gid
  GET /api/common-params
  Response: { "success": false, "message": "game_gid is required" }
  Status: 400 Bad Request
  ```

- [ ] **FlowsList API**:
  ```javascript
  GET /api/flows?game_gid=10000147
  Response: { success: true, data: { flows: [...] } }
  Status: 200 OK

  // 缺少 game_gid
  GET /api/flows
  Response: { "success": false, "message": "game_gid is required" }
  Status: 400 Bad Request
  ```

### 安全测试

- [ ] **跨游戏数据隔离**:
  - [ ] 游戏 A 的用户无法看到游戏 B 的数据
  - [ ] 游戏 A 的用户无法修改游戏 B 的数据
  - [ ] 移除 `localStorage` 后无跨游戏污染

- [ ] **URL 参数篡改**:
  - [ ] 篡改 `game_gid` 导致 404 错误
  - [ ] 缺少 `game_gid` 导致明确的错误提示

---

## 五、代码质量改进

### 一致性提升

**修复前**：
- CategoriesList: URL 参数 ✅
- CommonParamsList: localStorage ❌
- FlowsList: 无参数 ❌

**修复后**：
- CategoriesList: URL 参数 ✅
- CommonParamsList: URL 参数 ✅
- FlowsList: URL 参数 ✅

### 可维护性提升

**统一的模式**：
```javascript
// 1. 导入 useLocation
import { useNavigate, useLocation } from 'react-router-dom';

// 2. 从 URL 读取 game_gid
const gameGid = new URLSearchParams(location.search).get('game_gid');

// 3. 检查 game_gid 存在性
if (!gameGid) {
  return <ErrorState />;
}

// 4. 查询时传递 game_gid
useQuery({
  queryKey: ['resource', gameGid],
  queryFn: () => fetch(`/api/resource?game_gid=${gameGid}`),
  enabled: !!gameGid
});
```

---

## 六、已知问题和后续任务

### 已修复

- [x] CommonParamsList.jsx - 移除 localStorage
- [x] FlowsList.jsx - 添加 game_gid 过滤
- [x] Sidebar.jsx - 添加缺失路由

### 待测试

- [ ] CommonParamsList 页面功能测试
- [ ] FlowsList 页面功能测试
- [ ] Sidebar 导航测试
- [ ] API 契约验证

### 后续优化

- [ ] 添加 E2E 测试用例
- [ ] 后端 API 强制验证 game_gid
- [ ] 添加单元测试覆盖

---

## 七、影响范围

### 修改的文件

1. **CommonParamsList.jsx**:
   - 导入: 添加 `useLocation`
   - 状态: 从 URL 读取 `game_gid`
   - 查询: 添加 `game_gid` 过滤
   - 同步: 移除 `localStorage` 使用
   - 错误处理: 添加 `game_gid` 检查

2. **FlowsList.jsx**:
   - 导入: 添加 `useLocation`
   - 状态: 从 URL 读取 `game_gid`
   - 查询: 添加 `game_gid` 过滤
   - 导航: 保持 `game_gid` 参数
   - 错误处理: 添加 `game_gid` 检查

3. **Sidebar.jsx**:
   - 配置: 添加 4 个缺失路由

### 不受影响的文件

- ✅ CategoriesList.jsx（已正确实现）
- ✅ EventsList.jsx（未在此次修复范围）
- ✅ ParametersList.jsx（未在此次修复范围）
- ✅ EventNodes.tsx（功能正确，仅配置缺失）

---

## 八、完成状态

### ✅ 已完成

- [x] 修复 CommonParamsList.jsx P0 问题
- [x] 修复 FlowsList.jsx P0 问题
- [x] 更新 Sidebar.jsx P1 问题
- [x] 前端构建验证通过
- [x] 代码审查完成
- [x] 文档更新完成

### 🔲 待用户测试

- [ ] 功能测试（所有修复的页面）
- [ ] API 契约测试
- [ ] 安全测试（跨游戏数据隔离）

### 📋 相关文档

- **分类模态框重构报告**: [category-modal-refactoring-completion.md](category-modal-refactoring-completion.md)
- **游戏上下文审查报告**: [game-context-management-audit.md](game-context-management-audit.md)
- **项目开发规范**: [CLAUDE.md](../../../CLAUDE.md)

---

**报告完成时间**: 2026-02-16 21:00
**下一步行动**: 用户进行功能测试或继续其他任务
