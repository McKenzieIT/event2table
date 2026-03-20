# 游戏删除功能测试指南

## 修复总结

### 1. 主要问题
- ❌ 错误使用 `game.id` (数据库自增ID) 而非 `game.gid` (业务GID)
- ❌ 调用不存在的批量删除端点 `/api/games/batch`
- ❌ 未实现两阶段确认流程
- ❌ 性能问题：handler执行时间1424ms

### 2. 修复内容

#### 文件1: `/frontend/src/analytics/components/game-management/GameManagementModal.jsx`

**修复点1：删除API使用game.gid**
```javascript
// ❌ 修复前
const response = await fetch(`/api/games/${game.id}`, {
  method: 'DELETE'
});

// ✅ 修复后
const response = await fetch(`/api/games/${game.gid}`, {
  method: 'DELETE',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ confirm: false })
});
```

**修复点2：实现两阶段确认流程**
```javascript
// 第一阶段：检查是否有关联数据
const response = await fetch(`/api/games/${game.gid}`, {
  method: 'DELETE',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ confirm: false })
});

if (response.status === 409) {
  const errorData = await response.json();

  // 显示详细的确认对话框
  const confirmMessage =
    `游戏"${game.name}"有关联数据，删除将清除以下内容：\n` +
    `• ${errorData.data?.event_count || 0} 个事件\n` +
    `• ${errorData.data?.param_count || 0} 个参数\n` +
    `• ${errorData.data?.node_config_count || 0} 个节点配置\n\n` +
    `确定要继续删除吗？此操作不可撤销！`;

  if (!confirm(confirmMessage)) {
    return; // 用户取消
  }

  // 第二阶段：用户确认后强制删除
  const deleteResponse = await fetch(`/api/games/${game.gid}`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ confirm: true })
  });
}
```

**修复点3：更新API使用game.gid**
```javascript
// ❌ 修复前
const response = await fetch(`/api/games/${game.id}`, {
  method: 'PUT',
  // ...
});

// ✅ 修复后
const response = await fetch(`/api/games/${game.gid}`, {
  method: 'PUT',
  // ...
});
```

**修复点4：优化性能**
```javascript
// ❌ 修复前：依赖项不完整
}, []);

// ✅ 修复后：包含所有依赖
}, [selectedGameGid, queryClient]);
```

#### 文件2: `/frontend/src/features/games/GameManagementModal.jsx`

**修复点：更新delete mutation支持两阶段确认**
```javascript
// ✅ 修复后：mutation支持confirm参数
const deleteMutation = useMutation({
  mutationFn: async ({ gid, confirm }) => {
    const response = await fetch(`/api/games/${gid}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ confirm })
    });

    // 处理409响应
    if (response.status === 409) {
      const result = await response.json();
      return { needsConfirmation: true, data: result.data };
    }

    // ...
  },
  onSuccess: (result, variables) => {
    // 需要确认，显示对话框
    if (result.needsConfirmation) {
      const confirmMessage = /* ... */;
      if (confirm(confirmMessage)) {
        deleteMutation.mutate({ gid: variables.gid, confirm: true });
      }
      return;
    }

    // 删除成功
    queryClient.invalidateQueries(['games']);
    success('游戏删除成功');
    // ...
  }
});
```

## 测试步骤

### 1. 启动应用
```bash
# 终端1：启动后端
cd /Users/mckenzie/Documents/event2table
python web_app.py

# 终端2：启动前端
cd /Users/mckenzie/Documents/event2table/frontend
npm run dev
```

### 2. 测试场景

#### 场景1：删除没有关联数据的游戏
1. 打开游戏管理模态框
2. 创建一个新游戏（确保没有事件和参数）
3. 点击"删除游戏"按钮
4. **预期结果**：直接删除成功，无额外确认

#### 场景2：删除有关联数据的游戏（两阶段确认）
1. 选择一个有事件/参数的游戏
2. 点击"删除游戏"按钮
3. **预期结果**：显示详细确认对话框
   ```
   游戏"XXX"有关联数据，删除将清除以下内容：
   • X 个事件
   • X 个参数
   • X 个节点配置

   确定要继续删除吗？此操作不可撤销！
   ```
4. 点击"取消" → 游戏不被删除
5. 再次点击删除，点击"确定" → 游戏被成功删除

#### 场景3：更新游戏信息
1. 选择一个游戏
2. 修改游戏名称或ODS数据库
3. 点击"保存更改"
4. **预期结果**：更新成功，无报错

### 3. 验证API调用

**检查浏览器Network标签**：
- ❌ 不应出现：`DELETE http://localhost:5173/api/games/batch`
- ✅ 应该看到：`DELETE /api/games/10000147`（使用业务GID）
- ✅ 应该看到：`PUT /api/games/10000147`（使用业务GID）

**检查请求体**：
- 第一次删除请求：`{ confirm: false }`
- 第二次删除请求（确认后）：`{ confirm: true }`

### 4. 性能验证

**检查Console**：
- ✅ 不应出现"click handler took XXXms"警告
- ✅ 删除操作响应时间 < 500ms

### 5. 后端日志验证

**检查后端终端输出**：
```
*** api_delete_game CALLED with gid=10000147, force_delete=False ***
*** api_delete_game CALLED with gid=10000147, force_delete=True ***
Cascade deleted game XXX (GID: 10000147): X events, X params, X node configs
```

## 常见问题排查

### 问题1：仍然出现404错误
**原因**：可能仍在使用 `game.id`
**解决**：检查代码，确保所有API调用都使用 `game.gid`

### 问题2：不显示确认对话框
**原因**：游戏没有关联数据（符合预期）
**验证**：删除一个有事件的测试游戏

### 问题3：确认后仍删除失败
**原因**：后端API可能不支持两阶段确认
**验证**：检查后端日志，确认 `api_delete_game` 函数被调用

### 问题4：性能仍然慢
**原因**：依赖项不正确导致不必要的重新渲染
**解决**：检查 `useCallback` 和 `useMemo` 的依赖项数组

## API规范

### DELETE /api/games/<gid>
**请求头**：
```
Content-Type: application/json
```

**请求体（第一阶段）**：
```json
{
  "confirm": false
}
```

**响应（409 Conflict）**：
```json
{
  "success": false,
  "error": "Game has X events, X parameters, X node configs. Set confirm=true to force delete.",
  "data": {
    "event_count": 10,
    "param_count": 50,
    "node_config_count": 5
  }
}
```

**请求体（第二阶段）**：
```json
{
  "confirm": true
}
```

**响应（200 OK）**：
```json
{
  "success": true,
  "message": "Game and all associated data deleted successfully",
  "data": {
    "deleted_event_count": 10,
    "deleted_param_count": 50,
    "deleted_node_config_count": 5
  }
}
```

## 总结

修复完成后：
- ✅ 使用正确的 `game.gid` 作为标识符
- ✅ 实现两阶段确认流程（409 → 确认 → 200）
- ✅ 优化性能，避免慢速handler
- ✅ 提供清晰的用户反馈
- ✅ 符合后端API规范
