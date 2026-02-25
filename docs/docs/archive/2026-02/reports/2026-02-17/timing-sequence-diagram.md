# 批量删除时序问题可视化

## 完整时序图：正常删除流程

```
用户操作                    前端React Query           后端API                  数据库
────────────────────────────────────────────────────────────────────────────────────────
T0: 打开弹窗
   useQuery(['games'])
   ───────────────→   GET /api/games
                        (cache miss)          ──────────────────→   SELECT * FROM games
   ←──────────────                              ←──────────────────   返回[游戏A,B,C]
   缓存30秒 (staleTime)

T1: UI显示游戏列表
   ┌─────────────────┐
   │ ☑ 游戏A (GID:1) │  ← 从缓存读取
   │ ☑ 游戏B (GID:2) │
   │ ☑ 游戏C (GID:3) │
   └─────────────────┘

T2: 点击"批量删除"
   handleBatchDelete()
   ────────────────────────────────────────────────────────────────────────
   const gamesToDelete =
     games.filter(g =>
       selectedGames.includes(g.gid)
     )  // ⚠️ 从缓存的games过滤

T3: 显示确认对话框
   "确定要删除选中的3个游戏吗？"
   [确定] [取消]

T4: 用户确认删除
   setIsDeleting(true)

T5: 循环删除 - 第1次
   DELETE /api/games/1
   { confirm: true }    ─────────────────→  api_delete_game(gid=1)
                                                 execute_cascade_delete()
                                                 BEGIN TRANSACTION
                                                 DELETE FROM log_events...
                                                 DELETE FROM games...
                                                 COMMIT
   ←──────────────────  200 OK               clear_game_cache()
                                                 clear_cache_pattern(...)
                                                 ⚠️ 但没有清除 games:list:v1!

T6: 循环删除 - 第2次
   DELETE /api/games/2
   { confirm: true }    ─────────────────→  api_delete_game(gid=2)
                                                 (同上)
   ←──────────────────  200 OK

T7: 循环删除 - 第3次
   DELETE /api/games/3
   { confirm: true }    ─────────────────→  api_delete_game(gid=3)
                                                 (同上)
   ←──────────────────  200 OK

T8: 刷新列表
   queryClient.invalidateQueries(['games'])
   ───────────────→   GET /api/games
                        (staleTime未过)      ──────────────────→   (可能使用缓存)
   ←──────────────                              ←──────────────────   或返回空[]

T9: 显示结果
   success('批量删除成功：3 个游戏')
```

---

## 时序图：竞态条件场景（用户报告的问题）

```
标签页A                     标签页B                    前端React Query           后端API              数据库
───────────────────────────────────────────────────────────────────────────────────────────────────
T0: 打开弹窗                                      T0: 用户B打开弹窗
   useQuery(['games'])                              useQuery(['games'])
   ─────────────────→   GET /api/games                ─────────────────→   GET /api/games
   ←─────────────────   返回[游戏A,B,C]               ←─────────────────   返回[游戏A,B,C]
   缓存30秒                                          缓存30秒

   ┌─────────────────┐                                                    ┌──────────────┐
   │ ☑ 游戏A (GID:1) │                                                    │ 游戏A (GID:1) │
   │ ☑ 游戏B (GID:2) │                                                    │ 游戏B (GID:2) │
   │ ☑ 游戏C (GID:3) │                                                    │ 游戏C (GID:3) │
   └─────────────────┘                                                    └──────────────┘

T1: 用户A选中游戏A,B                                      T1: 用户B删除游戏B
   点击"批量删除"
   ─────────────────────────────────────────────────────────────────────────────────────────
   const gamesToDelete =
     games.filter(g =>
       selectedGames.includes(g.gid)
     )  // ⚠️ games来自缓存，包含游戏B

                            DELETE /api/games/2
                            { confirm: true }              ─────────────────→  api_delete_game(2)
   ←───────────────────────────────────────────────────────────────────────   DELETE FROM games
                                                                               WHERE gid=2
                                                                               ←────────────────
                                                                               200 OK

T2: 用户A确认删除
   setIsDeleting(true)

T3: 循环删除 - 第1次
   DELETE /api/games/1
   { confirm: true }    ──────────────────────────────────────────→  api_delete_game(1)
   ←────────────────────────────────────────────────────────────────  200 OK

T4: 循环删除 - 第2次  ⚠️
   DELETE /api/games/2
   { confirm: true }    ──────────────────────────────────────────→  api_delete_game(2)
                                                                      Repositories.GAMES
                                                                      .find_by_field("gid", 2)
                                                                      ←────────────────
   ←────────────────────────────────────────────────────────────────  ❌ 404 Not Found!
                                                                      "Game not found"

   console.error('Failed to delete game 游戏B (GID: 2):', {
     status: 404,
     statusText: 'Not Found',
     body: { error: 'Game not found' }
   })

T5: 循环删除 - 第3次
   DELETE /api/games/3
   { confirm: true }    ──────────────────────────────────────────→  api_delete_game(3)
   ←────────────────────────────────────────────────────────────────  200 OK

T6: 刷新列表
   queryClient.invalidateQueries(['games'])
   ─────────────────→   GET /api/games                          ─────────────────→  SELECT * FROM games
   ←─────────────────  返回[游戏A,C]                            ←─────────────────  返回[游戏A,C]

T7: 显示结果
   showError('批量删除部分失败：成功 2 个，失败 1 个')
   console.error('批量删除错误详情:
   - 游戏B (GID: 2): 404 - Game not found')
```

**关键问题**：
- 用户A的UI仍然显示游戏B（因为30秒缓存未过期）
- 用户B已经删除了游戏B
- 用户A尝试删除游戏B时，收到404错误

---

## 时序图：缓存不一致场景

```
时间轴                    前端React Query          后端Flask-Caching        数据库
──────────────────────────────────────────────────────────────────────────────────
T0: 首次加载
   GET /api/games
   ─────────────────→   cache.get("games:list:v1")
                         cache miss
                         ─────────────────→   SELECT * FROM games
                         ←─────────────────   返回[游戏A,B,C]
                         cache.set("games:list:v1", [...], timeout=3600)
   ←────────────────  返回[游戏A,B,C]
   缓存30秒

T1 (5秒后):
   UI显示游戏列表 (从缓存读取)

T2 (10秒后):
   外部事件删除游戏B
   (例如：另一个用户、定时任务、手动清理)
                          ─────────────────→   DELETE FROM games
                                               WHERE gid=2
                                               ←────────────────
                                               200 OK

T3 (15秒后):
   用户选中游戏B点击删除
   handleBatchDelete()
   const gamesToDelete =
     games.filter(...)  // ⚠️ games仍包含游戏B（缓存未过期）

   DELETE /api/games/2
   ─────────────────→  api_delete_game(2)
                        Repositories.GAMES.find_by_field("gid", 2)
                        ─────────────────→   SELECT * FROM games
                                             WHERE gid=2
                        ←─────────────────   ❌ NULL (游戏不存在)
   ←────────────────  ❌ 404 Not Found!

T4 (16秒后):
   queryClient.invalidateQueries(['games'])
   GET /api/games
   ─────────────────→  cache.get("games:list:v1")
                       ⚠️ Cache HIT! 返回旧数据[游戏A,B,C]
   ←────────────────  返回[游戏A,B,C] (过期的!)

T5 (36秒后):
   用户重新打开弹窗
   staleTime已过(>30秒)
   GET /api/games
   ─────────────────→  cache.get("games:list:v1")
                       ⚠️ 仍然HIT! (Flask-Caching 1小时TTL)
                       返回[游戏A,B,C] (更过期的!)
```

**关键问题**：
- 后端Flask-Caching的1小时TTL远长于前端的30秒
- 删除操作只清除 `clear_game_cache()`，不清除 `games:list:v1`
- 导致前端 `invalidateQueries` 后获取到的仍然是过期数据

---

## 优化后的时序图：乐观删除

```
用户操作                    前端React Query           后端API                  数据库
────────────────────────────────────────────────────────────────────────────────────────
T0: 打开弹窗
   useQuery(['games'])
   ───────────────→   GET /api/games
   ←──────────────  返回[游戏A,B,C]
   缓存30秒

T1: UI显示游戏列表
   ┌─────────────────┐
   │ ☑ 游戏A (GID:1) │
   │ ☑ 游戏B (GID:2) │
   │ ☑ 游戏C (GID:3) │
   └─────────────────┘

T2: 点击"批量删除"
   handleBatchDelete()

   ✅ 乐观更新：立即从UI移除
   queryClient.setQueryData(['games'], {
     ...apiResponse,
     data: games.filter(g => ![1,2,3].includes(g.gid))
   })

   ┌─────────────────┐
   │ (空列表)         │  ← UI立即更新
   └─────────────────┘

T3: 后台并发删除
   Promise.allSettled([
     DELETE /api/games/1,
     DELETE /api/games/2,
     DELETE /api/games/3
   ])
   ─────────────────→  (并发请求)
   ←─────────────────  全部200 OK

T4: 删除成功
   queryClient.invalidateQueries(['games'])
   ───────────────→   GET /api/games (验证一致性)
   ←──────────────  返回[]

T5: 显示结果
   success('批量删除成功：3 个游戏')
```

**优点**：
- UI立即响应，无延迟
- 减少竞态条件窗口
- 用户体验极佳

---

## 优化后的时序图：删除前检查

```
用户操作                    前端React Query           后端API                  数据库
────────────────────────────────────────────────────────────────────────────────────────
T0-T2: (同上) 打开弹窗、显示列表、点击批量删除

T3: ✅ 删除前检查
   queryClient.cancelQueries(['games'])
   queryClient.refetchQueries(['games'])
   ───────────────→   GET /api/games
                        (强制刷新)
   ←──────────────  返回[游戏A,C]  ← 游戏B已被删除

   const { exist, missing } = checkGamesExist([1,2,3])
   // exist = [1,3] (游戏A,C)
   // missing = [2] (游戏B)

   if (missing.length > 0) {
     showError('以下游戏已被删除：游戏B')
   }

T4: 仅删除存在的游戏
   for (const gid of [1,3]) {
     DELETE /api/games/${gid}
   }
   ─────────────────→  DELETE /api/games/1,3
   ←─────────────────  全部200 OK

T5: 显示结果
   success('批量删除完成：成功 2 个（1 个已被删除）')
```

**优点**：
- 避免404错误
- 清晰告知用户状态
- 只删除实际存在的游戏

---

## 缓存清除机制对比

### 当前实现（有缺陷）

```python
@api_bp.route("/api/games/<int:gid>", methods=["DELETE"])
def api_delete_game(gid):
    # ... 删除逻辑 ...

    # 清理缓存
    if status_code == 200:
        clear_game_cache()  # ❌ 不清除 games:list:v1
        clear_cache_pattern("dashboard_statistics")

    return result, status_code
```

**问题**：`clear_game_cache()` 只清除 `game:{id}` 的缓存，不清除列表缓存。

### 修复后的实现

```python
@api_bp.route("/api/games/<int:gid>", methods=["DELETE"])
def api_delete_game(gid):
    # ... 删除逻辑 ...

    # 清理缓存
    if status_code == 200:
        clear_game_cache()
        clear_cache_pattern("dashboard_statistics")

        # ✅ 显式清除Flask-Caching的列表缓存
        try:
            current_app.cache.delete("games:list:v1")
            logger.info("✅ Cleared games:list:v1 cache")
        except (AttributeError, RuntimeError) as e:
            logger.warning(f"Failed to clear games:list cache: {e}")

    return result, status_code
```

**优点**：确保删除后立即清除列表缓存，防止返回过期数据。

---

## 错误处理对比

### 当前实现（混淆404和错误）

```javascript
if (deleteResponse.ok) {
  successCount++;
} else {
  failCount++;  // ❌ 404被当作失败
  errors.push({
    status: deleteResponse.status,
    message: 'Unknown error'
  });
}

showError(`批量删除部分失败：成功 ${successCount} 个，失败 ${failCount} 个`);
```

### 修复后的实现

```javascript
if (deleteResponse.ok) {
  successCount++;
} else if (deleteResponse.status === 404) {
  // ✅ 404不是错误，游戏已被删除
  successCount++;
  alreadyDeletedCount++;
} else {
  failCount++;
  errors.push({...});
}

if (failCount === 0) {
  const message = alreadyDeletedCount > 0
    ? `批量删除完成：成功 ${successCount} 个（${alreadyDeletedCount} 个已被删除）`
    : `批量删除成功：${successCount} 个游戏`;
  success(message);
} else {
  showError(`批量删除部分失败：成功 ${successCount} 个，失败 ${failCount} 个`);
}
```

**优点**：准确区分"失败"、"已删除"、"成功"，提供清晰的用户反馈。

---

## 总结

### 问题根源

1. **后端缓存未清除**：`clear_game_cache()` 不清除 `games:list:v1`
2. **前端缓存时序**：30秒 `staleTime` 在删除期间可能过期
3. **错误处理不当**：404被当作失败而非"已删除"
4. **缺乏删除前检查**：不验证游戏是否仍然存在

### 优化策略

1. **紧急修复**：
   - 修复后端缓存清除逻辑
   - 改进404错误处理
   - 添加删除前检查

2. **体验优化**：
   - 实现乐观删除
   - 缩短缓存时间
   - 添加删除幂等性

3. **长期优化**：
   - WebSocket实时更新
   - 统一缓存管理
   - 改进E2E测试

---

**生成时间**: 2026-02-17
**工具**: Claude Code (Sonnet 4.5)
