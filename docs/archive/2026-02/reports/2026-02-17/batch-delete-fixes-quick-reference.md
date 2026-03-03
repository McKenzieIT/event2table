# 批量删除404错误修复快速参考

> **日期**: 2026-02-17
> **优先级**: P0 - 紧急修复
> **预计工作量**: 2-4小时

---

## 问题概述

用户在批量删除游戏时遇到404错误，但实际上这些游戏已经被成功删除。

**根本原因**：
1. 后端 `clear_game_cache()` 不清除 `games:list:v1` 缓存
2. 前端30秒缓存期内，UI显示的游戏列表可能与数据库不一致
3. 404错误被错误地当作"失败"而非"已删除"

---

## 快速修复方案

### 修复1：后端缓存清除（5分钟）

**文件**: `backend/api/routes/games.py`

**位置**: 第532-537行（`api_delete_game` 函数末尾）

**修改前**：
```python
# 清理缓存
if status_code == 200:
    clear_game_cache()
    clear_cache_pattern("dashboard_statistics")

return result, status_code
```

**修改后**：
```python
# 清理缓存
if status_code == 200:
    clear_game_cache()
    clear_cache_pattern("dashboard_statistics")

    # ✅ 显式清除Flask-Caching的列表缓存
    try:
        current_app.cache.delete("games:list:v1")
        logger.info("✅ Cleared games:list:v1 cache after deletion")
    except (AttributeError, RuntimeError) as e:
        logger.warning(f"Failed to clear games:list cache: {e}")

return result, status_code
```

**同样修改**: `api_batch_delete_games` 函数（第584行之前）

---

### 修复2：前端404错误处理（10分钟）

**文件**: `frontend/src/features/games/GameManagementModal.jsx`

**位置**: 第176-192行（`handleBatchDelete` 循环内）

**修改前**：
```javascript
if (deleteResponse.ok) {
  successCount++;
} else {
  failCount++;
  const errorResult = await deleteResponse.json().catch(() => ({}));
  console.error(`Failed to delete game ${game.gid}:`, {
    status: deleteResponse.status,
    statusText: deleteResponse.statusText,
    body: errorResult
  });
  errors.push({
    game: game.name,
    gid: game.gid,
    status: deleteResponse.status,
    message: errorResult.message || errorResult.error || 'Unknown error'
  });
}
```

**修改后**：
```javascript
if (deleteResponse.ok) {
  successCount++;
} else if (deleteResponse.status === 404) {
  // ✅ 404不是错误，游戏已被删除
  successCount++;
  alreadyDeletedCount++;
  logger.info(`Game ${game.name} (GID: ${game.gid}) already deleted`);
} else {
  failCount++;
  const errorResult = await deleteResponse.json().catch(() => ({}));
  console.error(`Failed to delete game ${game.gid}:`, {
    status: deleteResponse.status,
    statusText: deleteResponse.statusText,
    body: errorResult
  });
  errors.push({
    game: game.name,
    gid: game.gid,
    status: deleteResponse.status,
    message: errorResult.message || errorResult.error || 'Unknown error'
  });
}
```

**同时修改**：第158-220行，添加 `alreadyDeletedCount` 变量

**修改后**：
```javascript
let successCount = 0;
let alreadyDeletedCount = 0;  // ✅ 新增
let failCount = 0;
const errors = [];

for (const game of gamesToDelete) {
  try {
    const deleteResponse = await fetch(`/api/games/${game.gid}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ confirm: true })
    });

    if (deleteResponse.ok) {
      successCount++;
    } else if (deleteResponse.status === 404) {
      successCount++;
      alreadyDeletedCount++;
    } else {
      failCount++;
      // ... 错误处理 ...
    }
  } catch (err) {
    failCount++;
    // ... 错误处理 ...
  }
}

// 显示结果
if (failCount === 0) {
  const message = alreadyDeletedCount > 0
    ? `批量删除完成：成功 ${successCount} 个（${alreadyDeletedCount} 个已被删除）`
    : `批量删除成功：${successCount} 个游戏`;
  success(message);
} else {
  // ... 错误处理 ...
}
```

---

### 修复3：缩短前端缓存时间（2分钟）

**文件**: `frontend/src/features/games/GameManagementModal.jsx`

**位置**: 第38-47行（`useQuery` 配置）

**修改前**：
```javascript
const { data: apiResponse, isLoading, error } = useQuery({
  queryKey: ['games'],
  queryFn: async () => {
    const response = await fetch('/api/games');
    if (!response.ok) throw new Error('Failed to fetch games');
    return response.json();
  },
  enabled: isOpen,
  staleTime: 30 * 1000,  // ⚠️ 30秒
});
```

**修改后**：
```javascript
const { data: apiResponse, isLoading, error } = useQuery({
  queryKey: ['games'],
  queryFn: async () => {
    const response = await fetch('/api/games');
    if (!response.ok) throw new Error('Failed to fetch games');
    return response.json();
  },
  enabled: isOpen,
  staleTime: 5 * 1000,  // ✅ 减少到5秒
  refetchOnWindowFocus: true,  // ✅ 窗口聚焦时刷新
});
```

---

### 修复4：添加删除前检查（15分钟）

**文件**: `frontend/src/features/games/GameManagementModal.jsx`

**位置**: `handleBatchDelete` 函数开头（第114行之后）

**新增代码**：
```javascript
const handleBatchDelete = useCallback(async () => {
  if (selectedGames.length === 0) return;

  // ✅ 1. 删除前刷新游戏列表，确保数据最新
  queryClient.cancelQueries(['games']);
  await queryClient.refetchQueries(['games']);

  // ✅ 2. 获取最新数据
  const freshGames = queryClient.getQueryData(['games'])?.data || [];
  const existingGids = new Set(freshGames.map(g => g.gid));

  // ✅ 3. 过滤掉不存在的游戏
  const gamesToDelete = [];
  const missingGames = [];

  for (const gid of selectedGames) {
    if (existingGids.has(gid)) {
      const game = freshGames.find(g => g.gid === gid);
      if (game) gamesToDelete.push(game);
    } else {
      const game = games.find(g => g.gid === gid);
      missingGames.push(game ? game.name : `GID:${gid}`);
    }
  }

  if (gamesToDelete.length === 0) {
    showError('选中的游戏已被删除');
    setSelectedGames([]);
    return;
  }

  if (missingGames.length > 0) {
    showError(`以下游戏已被删除：${missingGames.join(', ')}`);
  }

  // ... 继续原有的删除逻辑 ...
}, [selectedGames, games, queryClient, success, showError]);
```

---

## 测试验证

### 1. 单元测试

```bash
# 后端测试
cd /Users/mckenzie/Documents/event2table
pytest backend/test/unit/api/test_games_cache_clearing.py -v
```

**测试用例**：
```python
def test_delete_game_clears_list_cache():
    """测试删除游戏后清除列表缓存"""
    # 创建游戏
    game = create_test_game(name="Test Game", gid=90009999)

    # 获取列表（建立缓存）
    response1 = client.get('/api/games')
    assert response1.status_code == 200
    assert len(response1.json['data']) >= 1

    # 删除游戏
    response2 = client.delete(f'/api/games/{game["gid"]}',
                             json={'confirm': True})
    assert response2.status_code == 200

    # 验证缓存被清除
    response3 = client.get('/api/games')
    assert response3.status_code == 200
    # ✅ 应该不包含已删除的游戏
    deleted_game = [g for g in response3.json['data'] if g['gid'] == game['gid']]
    assert len(deleted_game) == 0
```

### 2. 集成测试

```bash
# 前端E2E测试
cd /Users/mckenzie/Documents/event2table/frontend
npm run test:e2e -- batch-delete-caching
```

**测试场景**：
1. 创建3个测试游戏
2. 在两个标签页中打开游戏管理
3. 在标签页B中删除游戏A
4. 在标签页A中选中所有游戏并删除
5. 验证：标签页A应显示"2个成功（1个已被删除）"

### 3. 手动测试

**步骤**：
1. 启动应用：`python web_app.py`
2. 打开浏览器：`http://localhost:5001`
3. 打开游戏管理弹窗
4. 创建3个测试游戏
5. 在另一个标签页删除其中一个游戏
6. 在第一个标签页选中所有游戏并删除
7. **预期结果**：显示"批量删除完成：成功 2 个（1 个已被删除）"

---

## 部署清单

### 开发环境

- [ ] 修改 `backend/api/routes/games.py`（2处）
- [ ] 修改 `frontend/src/features/games/GameManagementModal.jsx`（3处）
- [ ] 运行后端单元测试：`pytest backend/test/unit/api/test_games_cache_clearing.py`
- [ ] 运行前端E2E测试：`npm run test:e2e -- batch-delete`
- [ ] 手动测试验证

### 生产环境

- [ ] 代码审查
- [ ] 合并到主分支
- [ ] 部署到生产环境
- [ ] 验证生产环境缓存清除：
  ```bash
  # 检查日志
  tail -f logs/app.log | grep "Cleared games:list:v1"
  ```
- [ ] 监控404错误率：
  ```bash
  # 检查错误日志
  grep "404" logs/app.log | wc -l
  ```

---

## 回滚方案

如果修复引入新问题，立即回滚：

```bash
# 回滚到修复前的版本
git revert <commit-hash>

# 或手动恢复文件
git checkout HEAD~1 backend/api/routes/games.py
git checkout HEAD~1 frontend/src/features/games/GameManagementModal.jsx
```

---

## 监控指标

### 关键指标

1. **404错误率**：应接近0%
   ```bash
   grep "404.*Game not found" logs/app.log | wc -l
   ```

2. **缓存清除成功率**：应 > 95%
   ```bash
   grep "Cleared games:list:v1" logs/app.log | wc -l
   grep "Failed to clear games:list" logs/app.log | wc -l
   ```

3. **删除操作响应时间**：应 < 500ms
   ```bash
   grep "DELETE /api/games" logs/app.log | tail -100
   ```

### 告警规则

- 如果404错误率 > 5%，触发告警
- 如果缓存清除失败率 > 10%，触发告警
- 如果删除操作响应时间 > 1s，触发告警

---

## 常见问题

### Q1: 为什么不能直接修改 `clear_game_cache()` 函数？

**A**: `clear_game_cache()` 是缓存系统的底层函数，修改它可能影响其他模块。直接在 `api_delete_game` 中调用 `current_app.cache.delete()` 更安全。

### Q2: 缩短 `staleTime` 会不会影响性能？

**A**: 影响很小。游戏列表查询经过优化，单次查询 < 50ms。从30秒减少到5秒，最多增加每2分钟1次请求（可忽略）。

### Q3: 为什么不使用乐观删除？

**A**: 乐观删除需要更多的错误处理逻辑（回滚、重试），作为紧急修复，我们优先选择最简单的方案。后续优化可以实现乐观删除。

### Q4: 如果 `current_app.cache.delete()` 失败怎么办？

**A**: 使用 `try-except` 捕获异常，记录警告日志，不影响删除操作本身。前端会通过 `invalidateQueries` 强制刷新，确保数据一致性。

### Q5: 404错误完全消失了吗？

**A**: 不完全。404错误仍然可能发生（例如真正的删除失败），但会被正确处理为"已删除"而非"失败"。

---

## 后续优化

### 短期（1周内）

1. 实现乐观删除
2. 添加WebSocket实时更新
3. 改进E2E测试覆盖

### 中期（1月内）

1. 统一缓存管理（Flask-Caching + CacheInvalidator）
2. 实现删除幂等性（`already_deleted` 标志）
3. 添加删除前确认对话框（显示影响范围）

### 长期（3月内）

1. 实现分布式缓存（Redis）
2. 添加删除审计日志
3. 实现软删除（标记删除而非物理删除）

---

## 相关文档

- **根因分析**: `/docs/reports/2026-02-17/batch-delete-404-root-cause-analysis.md`
- **时序图**: `/docs/reports/2026-02-17/timing-sequence-diagram.md`
- **API文档**: `/docs/api/README.md`
- **测试指南**: `/docs/testing/e2e-testing-guide.md`

---

**更新时间**: 2026-02-17
**负责人**: Claude Code (Sonnet 4.5)
**审查者**: 待定
**状态**: 待实施
