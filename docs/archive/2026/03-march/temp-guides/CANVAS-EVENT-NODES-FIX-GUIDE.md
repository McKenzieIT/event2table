# Canvas和Event Nodes问题修复指南

**基于E2E测试结果**: [CANVAS-EVENT-NODES-E2E-TEST-REPORT.md](./CANVAS-EVENT-NODES-E2E-TEST-REPORT.md)

---

## 问题概述

**测试通过率**: 23% (7/30项测试通过)
**阻塞问题**: 6个
**失败问题**: 17个

---

## P0 - 立即修复（阻塞问题）

### 问题1: 路由配置问题 ⚠️ **极其严重**

**症状**:
- 直接访问 `http://localhost:5173/event-node-builder?game_gid=10000147` 显示首页或错误页面
- 所有3个页面（Event Node Builder、Event Nodes Management、Canvas）都无法通过URL直接访问

**根因**:
- 路由配置可能缺少`game_gid`参数处理
- 路由守卫可能阻止了直接访问
- 组件懒加载配置可能有问题

**修复步骤**:

#### 1. 检查路由配置

```typescript
// frontend/src/routes/routes.tsx

import { lazy } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

// ✅ 确保正确导入组件
const EventNodeBuilder = lazy(() => import('@event-builder/pages/EventNodeBuilder'));
const EventNodesManagement = lazy(() => import('@event-builder/pages/EventNodesManagement'));
const Canvas = lazy(() => import('@canvas/pages/Canvas'));

// ✅ 正确配置路由
<Routes>
  <Route path="/event-node-builder" element={<EventNodeBuilder />} />
  <Route path="/event-nodes" element={<EventNodesManagement />} />
  <Route path="/canvas" element={<Canvas />} />
</Routes>
```

#### 2. 添加路由参数处理

```typescript
// frontend/src/event-builder/pages/EventNodeBuilder.jsx
import { useSearchParams } from 'react-router-dom';

function EventNodeBuilder() {
  const [searchParams] = useSearchParams();
  const gameGid = searchParams.get('game_gid');

  // ✅ 验证game_gid参数
  if (!gameGid) {
    return <Navigate to="/" />;
  }

  // ✅ 使用gameGid获取数据
  useEffect(() => {
    fetchParameters(gameGid);
  }, [gameGid]);

  return <div>...</div>;
}
```

#### 3. 检查路由模式

```typescript
// 确保 BrowserRouter 使用正确模式
// 如果使用 HashRouter，URL 应该是:
// http://localhost:5173/#/event-node-builder?game_gid=10000147

// 如果使用 BrowserRouter，URL 应该是:
// http://localhost:5173/event-node-builder?game_gid=10000147
```

**验证**:
```bash
# 直接访问URL应该显示正确页面
curl http://localhost:5173/event-node-builder?game_gid=10000147
```

---

### 问题2: 后端API连接失败 ⚠️ **极其严重**

**症状**:
- Event Node Builder显示 "加载参数失败: INTERNAL SERVER ERROR"
- 参数API调用返回500错误

**根因**:
- 后端服务器未启动
- API端点不存在
- 数据库连接失败

**修复步骤**:

#### 1. 启动后端服务器

```bash
# 进入项目目录
cd /Users/mckenzie/Documents/event2table

# 激活虚拟环境
source backend/venv/bin/activate

# 启动Flask服务器
python3 web_app.py

# 验证服务器运行
curl http://127.0.0.1:5001/api/health
```

#### 2. 检查API端点是否存在

```bash
# 测试参数API
curl "http://127.0.0.1:5001/api/parameters?game_gid=10000147"

# 测试事件API
curl "http://127.0.0.1:5001/api/events?game_gid=10000147"

# 测试事件节点API
curl "http://127.0.0.1:5001/api/event-nodes?game_gid=10000147"
```

#### 3. 创建缺失的API端点

```python
# backend/api/routes/parameters.py

from flask import jsonify, request
from backend.core.utils import json_success_response, json_error_response

@parameters_bp.route('/api/parameters', methods=['GET'])
def get_parameters():
    """获取游戏参数列表"""
    try:
        game_gid = request.args.get('game_gid', type=int)

        if not game_gid:
            return json_error_response('game_gid parameter is required', status_code=400)

        # 查询参数
        from backend.core.database.converters import fetch_all_as_dict
        parameters = fetch_all_as_dict(
            'SELECT * FROM event_params WHERE game_gid = ?',
            (game_gid,)
        )

        return json_success_response(data=parameters)

    except Exception as e:
        logger.error(f"Error fetching parameters: {e}")
        return json_error_response('Failed to fetch parameters', status_code=500)
```

#### 4. 检查数据库连接

```python
# backend/core/config/config.py

import sqlite3

def get_db_connection():
    """获取数据库连接"""
    DB_PATH = BASE_DIR / "data" / "dwd_generator.db"

    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
```

**验证**:
```bash
# 所有API应该返回200状态码
curl -w "\nHTTP Status: %{http_code}\n" \
  "http://127.0.0.1:5001/api/parameters?game_gid=10000147"
```

---

### 问题3: 面包屑导航显示错误 ⚠️ **重要**

**症状**:
- Event Node Builder页面面包屑显示"参数管理"而非"事件节点构建器"

**根因**:
- 面包屑配置硬编码
- 面包屑未根据路由动态更新

**修复步骤**:

#### 1. 创建动态面包屑配置

```typescript
// frontend/src/shared/components/Breadcrumb/breadcrumbConfig.ts

interface BreadcrumbItem {
  label: string;
  path: string;
}

export const breadcrumbMap: Record<string, BreadcrumbItem[]> = {
  '/event-node-builder': [
    { label: '首页', path: '/' },
    { label: '事件节点构建器', path: '/event-node-builder' }
  ],
  '/event-nodes': [
    { label: '首页', path: '/' },
    { label: '事件节点管理', path: '/event-nodes' }
  ],
  '/canvas': [
    { label: '首页', path: '/' },
    { label: 'HQL画布', path: '/canvas' }
  ]
};
```

#### 2. 使用动态面包屑组件

```typescript
// frontend/src/shared/components/Breadcrumb/Breadcrumb.jsx

import { useLocation } from 'react-router-dom';
import { breadcrumbMap } from './breadcrumbConfig';

function Breadcrumb() {
  const location = useLocation();
  const currentPath = location.pathname;

  // ✅ 根据路径获取面包屑
  const breadcrumbs = breadcrumbMap[currentPath] || [
    { label: '首页', path: '/' }
  ];

  return (
    <nav className="breadcrumb">
      {breadcrumbs.map((crumb, index) => (
        <span key={index}>
          {index > 0 && ' > '}
          <a href={crumb.path}>{crumb.label}</a>
        </span>
      ))}
    </nav>
  );
}
```

**验证**:
- 访问 Event Node Builder，面包屑应显示: `首页 > 事件节点构建器`
- 访问 Canvas，面包屑应显示: `首页 > HQL画布`

---

## P1 - 尽快修复（重要问题）

### 问题4: Canvas页面显示首页内容

**症状**:
- 访问 `http://localhost:5173/canvas?game_gid=10000147` 显示首页而非Canvas应用

**根因**:
- Canvas组件未正确渲染
- 路由配置问题

**修复步骤**:

#### 1. 检查Canvas组件导入

```typescript
// frontend/src/routes/routes.tsx

// ✅ 确保正确导入
const Canvas = lazy(() => import('@canvas/pages/Canvas'));

// ✅ 添加Suspense
<Route
  path="/canvas"
  element={
    <Suspense fallback={<Loading />}>
      <Canvas />
    </Suspense>
  }
/>
```

#### 2. 检查Canvas组件导出

```typescript
// frontend/src/features/canvas/pages/Canvas.jsx

// ✅ 确保默认导出
export default function Canvas() {
  return (
    <div className="canvas-container">
      {/* Canvas内容 */}
    </div>
  );
}
```

---

### 问题5: 游戏上下文提示缺失

**症状**:
- 页面没有显示当前游戏GID（10000147）
- 用户不清楚当前操作的游戏

**修复步骤**:

#### 1. 创建游戏上下文组件

```typescript
// frontend/src/shared/components/GameContext/GameContextBar.jsx

import { useSearchParams } from 'react-router-dom';

function GameContextBar() {
  const [searchParams] = useSearchParams();
  const gameGid = searchParams.get('game_gid');

  if (!gameGid) return null;

  return (
    <div className="game-context-bar">
      <span className="game-context-text">
        当前游戏: Updated Name (GID: {gameGid})
      </span>
      <button
        className="game-context-switch"
        onClick={() => window.location.href = '/games'}
      >
        切换游戏
      </button>
    </div>
  );
}

export default GameContextBar;
```

#### 2. 在需要游戏上下文的页面使用

```typescript
// frontend/src/event-builder/pages/EventNodeBuilder.jsx

import GameContextBar from '@/shared/components/GameContext/GameContextBar';

function EventNodeBuilder() {
  return (
    <div>
      <GameContextBar />
      {/* 页面内容 */}
    </div>
  );
}
```

---

## P2 - 可选优化（用户体验改进）

### 改进1: 添加加载状态指示器

```typescript
function EventNodeBuilder() {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchParameters().finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return (
      <div className="loading-container">
        <Spinner />
        <p>正在加载参数...</p>
      </div>
    );
  }

  return <div>...</div>;
}
```

### 改进2: 添加空状态提示

```typescript
function EventNodesList({ nodes }) {
  if (nodes.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">📊</div>
        <h2>暂无事件节点</h2>
        <p>点击下方按钮创建第一个事件节点</p>
        <button onClick={() => setShowCreateModal(true)}>
          创建事件节点
        </button>
      </div>
    );
  }

  return <div>{nodes.map(node => ...)}</div>;
}
```

### 改进3: 改进错误提示

```typescript
function EventNodeBuilder() {
  const [error, setError] = useState(null);

  if (error) {
    return (
      <Alert type="error" dismissible onClose={() => setError(null)}>
        <h3>加载失败</h3>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>
          重新加载
        </button>
      </Alert>
    );
  }
}
```

---

## 测试验证清单

修复完成后，请验证以下项目：

### 路由配置
- [ ] 直接访问 `http://localhost:5173/event-node-builder?game_gid=10000147` 显示正确页面
- [ ] 直接访问 `http://localhost:5173/event-nodes?game_gid=10000147` 显示正确页面
- [ ] 直接访问 `http://localhost:5173/canvas?game_gid=10000147` 显示正确页面

### API连接
- [ ] 参数API返回200状态码
- [ ] 事件API返回200状态码
- [ ] 事件节点API返回200状态码

### 面包屑导航
- [ ] Event Node Builder面包屑显示 "首页 > 事件节点构建器"
- [ ] Event Nodes面包屑显示 "首页 > 事件节点管理"
- [ ] Canvas面包屑显示 "首页 > HQL画布"

### 游戏上下文
- [ ] 页面顶部显示当前游戏GID（10000147）
- [ ] 提供"切换游戏"按钮

### 错误处理
- [ ] API失败时显示友好的错误消息
- [ ] 提供"重新加载"按钮
- [ ] 不显示技术堆栈跟踪

---

## 相关文档

- **E2E测试报告**: [CANVAS-EVENT-NODES-E2E-TEST-REPORT.md](./CANVAS-EVENT-NODES-E2E-TEST-REPORT.md)
- **测试总结**: [CANVAS-EVENT-NODES-TEST-SUMMARY.md](./CANVAS-EVENT-NODES-TEST-SUMMARY.md)
- **测试截图**: `/docs/reports/2026-03-03/*.png`

---

**文档创建时间**: 2026-03-03
**基于测试版本**: E2E Test v1.0
