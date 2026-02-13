# GameManagementModal 组件

## 概述

游戏管理模态框组件，提供主从视图布局的游戏管理界面。

**文件路径**: `/Users/mckenzie/Documents/event2table/frontend/src/features/games/GameManagementModal.jsx`

## 功能特性

### 布局结构

- **左侧面板**: 游戏列表
  - 搜索功能（支持游戏名称和GID）
  - 多选功能（批量操作）
  - 显示游戏总数
  - 滚动列表支持

- **右侧面板**: 游戏详情
  - 基本信息编辑
  - 统计数据显示
  - 危险操作区域

### 交互逻辑

1. **默认状态**: 所有可编辑字段为 disabled
2. **编辑模式**: 检测 onChange 事件后：
   - 移除 disabled 属性
   - 显示"保存"和"取消"按钮
   - 启用字段编辑
3. **保存操作**:
   - 提交 API (PUT /api/games/<gid>)
   - 成功后恢复 disabled 状态
   - 刷新游戏列表数据

## 核心功能

### 游戏列表

- ✅ 搜索过滤（名称/GID）
- ✅ 多选批量操作
- ✅ 点击选择查看详情
- ✅ 实时统计显示

### 游戏编辑

- ✅ 游戏名称（可编辑）
- ✅ GID（只读）
- ✅ ODS数据库（可编辑，下拉选择）
- ❌ DWD前缀（数据库中不存在此字段）

### 批量操作

- ✅ 批量删除（需确认）
- ✅ 删除前检查关联事件
- ✅ 错误提示和成功提示

### API集成

```javascript
// GET /api/games
// 获取游戏列表（包含统计数据）
const { data } = useQuery({
  queryKey: ['games'],
  queryFn: async () => {
    const response = await fetch('/api/games');
    return response.json();
  }
});

// PUT /api/games/<gid>
// 更新游戏信息
const response = await fetch(`/api/games/${gid}`, {
  method: 'PUT',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name, ods_db })
});

// DELETE /api/games/<gid>
// 删除单个游戏
const response = await fetch(`/api/games/${gid}`, {
  method: 'DELETE'
});

// DELETE /api/games/batch
// 批量删除游戏
const response = await fetch('/api/games/batch', {
  method: 'DELETE',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ ids: [gid1, gid2, ...] })
});
```

## 使用方法

### 基础用法

```jsx
import React, { useState } from 'react';
import { Button } from '@shared/ui';
import GameManagementModal from '@/features/games/GameManagementModal';

function MyComponent() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <div>
      <Button onClick={() => setIsModalOpen(true)}>
        打开游戏管理
      </Button>

      <GameManagementModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </div>
  );
}
```

### 与游戏状态集成

```jsx
import { useGameStore } from '@/stores/gameStore';

function GameManager() {
  const { setCurrentGame, currentGame } = useGameStore();
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleClose = () => {
    setIsModalOpen(false);

    // 刷新当前游戏数据
    if (currentGame) {
      fetch(`/api/games/${currentGame.gid}`)
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            setCurrentGame(data.data);
          }
        });
    }
  };

  return (
    <>
      <Button onClick={() => setIsModalOpen(true)}>
        管理游戏
      </Button>

      <GameManagementModal
        isOpen={isModalOpen}
        onClose={handleClose}
      />
    </>
  );
}
```

## 技术实现

### 状态管理

- **React Query**: 数据获取和缓存管理
- **Zustand (gameStore)**: 全局游戏状态
- **Local State**: UI交互状态

### 性能优化

- `React.memo`: 防止不必要的重渲染
- `useMemo`: 优化过滤计算
- `useCallback`: 稳定事件处理函数

### 数据验证

- 输入验证: 后端API处理
- XSS防护: 使用 sanitize_and_validate_string
- SQL注入防护: 参数化查询

## 样式定制

组件使用独立的CSS文件: `GameManagementModal.css`

主要样式类:
- `.game-management-modal`: 模态框容器
- `.game-list-panel`: 左侧列表面板
- `.game-detail-panel`: 右侧详情面板
- `.game-list-item`: 列表项
- `.form-group`: 表单组
- `.stats-grid`: 统计数据网格

### 响应式设计

- **桌面** (>1024px): 左右并排布局
- **平板** (640px-1024px): 上下堆叠布局
- **移动** (<640px): 单列布局

## 数据库Schema

```sql
CREATE TABLE games (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  gid TEXT UNIQUE NOT NULL,        -- 业务GID
  name TEXT NOT NULL,              -- 游戏名称
  ods_db TEXT NOT NULL,            -- ODS数据库名
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  icon_path TEXT
);
```

**注意**:
- `gid`: 业务GID，用于API和业务逻辑
- `id`: 数据库自增ID，仅用于数据库操作
- 所有查询应使用 `gid` 而非 `id`

## 错误处理

### 删除失败

如果游戏有关联的事件，删除会失败：
```
错误: Cannot delete game 'XX' with N associated events.
     Delete events first.
```

### 更新失败

```javascript
{
  "success": false,
  "message": "Game not found"
}
```

### 批量删除失败

```javascript
{
  "success": false,
  "message": "Cannot delete game 'XX' with N associated events"
}
```

## 测试

### 手动测试清单

- [ ] 打开模态框，显示游戏列表
- [ ] 搜索游戏名称
- [ ] 搜索游戏GID
- [ ] 多选游戏
- [ ] 批量删除（无关联事件）
- [ ] 点击游戏查看详情
- [ ] 编辑游戏名称
- [ ] 编辑ODS数据库
- [ ] 点击保存
- [ ] 点击取消
- [ ] 删除单个游戏（无关联事件）
- [ ] 尝试删除有关联事件的游戏

### E2E测试

```javascript
// 示例测试代码
test('should display games list', async () => {
  render(<GameManagementModal isOpen={true} onClose={jest.fn()} />);

  await waitFor(() => {
    expect(screen.getByText('游戏管理')).toBeInTheDocument();
  });
});

test('should search games', async () => {
  // ... 测试搜索功能
});

test('should edit game', async () => {
  // ... 测试编辑功能
});
```

## 开发规范

### 游戏标识符规范

⚠️ **极其重要**: 使用 `game_gid` 而非 `game_id`

```javascript
// ✅ 正确
fetch(`/api/games/${gameGid}`);
const table = `${odsDb}.ods_${gameGid}_all_view`;

// ❌ 错误
fetch(`/api/games/${gameId}`);
const table = `${odsDb}.ods_${gameId}_all_view`;
```

### API调用规范

```javascript
// ✅ 正确: 使用gid
await fetch(`/api/games/${game.gid}`, {
  method: 'PUT',
  body: JSON.stringify({ name: 'New Name' })
});

// ❌ 错误: 使用id
await fetch(`/api/games/${game.id}`, {
  method: 'PUT',
  body: JSON.stringify({ name: 'New Name' })
});
```

## 未来改进

- [ ] 添加游戏图标上传
- [ ] 添加DWD前缀字段（需数据库迁移）
- [ ] 支持批量编辑
- [ ] 添加游戏导出功能
- [ ] 添加拖拽排序
- [ ] 添加键盘快捷键

## 相关文档

- [API文档](../../../docs/api/README.md)
- [游戏管理规范](../../CLAUDE.md#游戏标识符规范)
- [E2E测试指南](../../../docs/testing/e2e-testing-guide.md)

## 维护者

Event2Table Development Team

**版本**: 1.0.0
**最后更新**: 2026-02-13
