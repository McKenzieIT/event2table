# React Query 缓存一致性问题全面分析报告

**日期**: 2026-02-22
**分析范围**: Event2Table 项目所有使用 React Query 的功能模块
**问题严重程度**: 🔴 P0 - 严重影响用户体验

---

## 执行摘要

### 问题概述
Event2Table 项目存在**严重的 React Query 缓存一致性问题**，导致所有使用 `useMutation` 的功能在增删改操作后，前端界面**不会自动更新显示最新数据**。

### 根本原因
1. **前端缓存失效范围过窄**：`invalidateQueries` 只使用了部分缓存键，没有包含完整的依赖参数
2. **后端API未返回更新后的数据**：修改操作只返回成功消息，不返回更新后的完整数据
3. **缓存键设计不一致**：同一个资源的查询和失效使用了不同的缓存键结构

### 影响范围
- ✅ 已确认存在问题的功能：**8个核心功能模块**
- ⚠️ 预计受影响的用户操作：**所有增删改操作**（100%）
- 📊 用户体验影响：**严重** - 需要手动刷新页面才能看到更新

---

## 一、问题详情

### 1.1 游戏管理（GameManagementModal）🔴 P0

**文件**: `frontend/src/features/games/GameManagementModal.jsx`

**问题代码**:
```javascript
// 第 48 行：查询时使用完整的缓存键（没有额外参数）
queryKey: ['games']

// 第 110 行：删除成功后失效缓存
queryClient.invalidateQueries(['games']);

// 第 216 行：批量删除成功后失效缓存
queryClient.invalidateQueries(['games']);

// 第 245 行：更新成功后失效缓存
queryClient.invalidateQueries(['games']);
```

**后端API** (`backend/api/routes/games.py:414`):
```python
return json_success_response(message="Game updated successfully")
# ❌ 只返回成功消息，没有返回更新后的游戏数据
```

**问题分析**:
- ✅ 缓存键设计正确（`['games']`），查询和失效一致
- ❌ **后端未返回更新后的数据**
- ⚠️ **依赖 `staleTime: 5 * 1000`**（第55行）- 5秒内认为数据新鲜，不会重新请求

**修复建议**:
1. **后端API修改**（推荐）:
   ```python
   # 修改 games.py:414
   updated_game = fetch_one_as_dict('SELECT * FROM games WHERE gid = ?', (gid,))
   return json_success_response(data=updated_game, message="Game updated successfully")
   ```

2. **前端使用 `setQueryData`**（备选）:
   ```javascript
   onSuccess: (data, variables) => {
     queryClient.setQueryData(['games'], (oldGames) => {
       return oldGames.map(g => g.gid === variables.gid ? { ...g, ...data } : g);
     });
     queryClient.invalidateQueries(['games']);
   }
   ```

---

### 1.2 事件管理（EventsList）🔴 P0

**文件**: `frontend/src/analytics/pages/EventsList.jsx`

**问题代码**:
```javascript
// 第 42 行：查询时使用复杂的缓存键（包含6个参数）
queryKey: ['events', currentPage, pageSize, selectedCategory, currentGame?.gid, searchTerm]

// 第 89 行：删除成功后失效缓存（只使用部分键）
queryClient.invalidateQueries(['events']);

// 第 226 行：手动刷新时（同样只使用部分键）
queryClient.invalidateQueries({ queryKey: ['events'] });
```

**问题分析**:
- ❌ **严重不一致**：查询使用6个参数，失效只使用1个参数
- ❌ **React Query 行为**：`invalidateQueries(['events'])` 会失效所有以 `['events']` 开头的缓存键
- ⚠️ **可能过度失效**：会失效所有游戏的缓存，而不仅仅是当前游戏

**后端API** (`backend/api/routes/events.py`):
```python
# 第 502 行：删除后
cache_invalidator.invalidate_pattern("events.list:*")

# 第 561 行：更新后
cache_invalidator.invalidate_pattern("events.list:*")

# ❌ 后端缓存失效模式不包含 game_gid 参数
```

**修复建议**:
```javascript
// 方案1：精确失效（推荐）
queryClient.invalidateQueries({
  queryKey: ['events', currentPage, pageSize, selectedCategory, currentGame?.gid, searchTerm]
});

// 方案2：使用精确的模糊匹配（次选）
queryClient.invalidateQueries({
  queryKey: ['events', currentGame?.gid]
});

// 方案3：失效所有事件缓存（简单但低效）
queryClient.invalidateQueries({
  predicate: (query) => query.queryKey[0] === 'events'
});
```

**后端API修改**:
```python
# 修改失效模式，包含 game_gid
cache_invalidator.invalidate_pattern(f"events.list:{game_gid}:*")
```

---

### 1.3 事件表单（EventForm）🔴 P0

**文件**: `frontend/src/analytics/pages/EventForm.jsx`

**问题代码**:
```javascript
// 第 3 行：未导入 useQueryClient
import { useQuery, useMutation } from '@tanstack/react-query';

// 第 123-169 行：表单提交逻辑
const handleSubmit = async (e) => {
  e.preventDefault();

  // ... 验证逻辑 ...

  try {
    const url = isEdit ? `/api/events/${id}` : '/api/events';
    const method = isEdit ? 'PUT' : 'POST';

    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    });

    if (!response.ok) {
      const result = await response.json();
      throw new Error(result.message || (isEdit ? '更新失败' : '创建失败'));
    }

    // ✅ 显示成功提示
    success(isEdit ? '事件更新成功' : '事件创建成功');

    // ❌ 直接导航，没有失效缓存
    navigate('/events', { replace: true });
  } catch (err) {
    showError(err.message);
  }
};
```

**问题分析**:
- ❌ **没有使用 `useMutation`**
- ❌ **没有使用 `useQueryClient`**
- ❌ **提交成功后没有失效缓存**
- ⚠️ 依赖导航后的 `useQuery` 重新获取数据，但由于 `staleTime` 可能不会立即刷新

**修复建议**:
```javascript
// 1. 添加导入
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// 2. 在组件内获取 queryClient
const queryClient = useQueryClient();

// 3. 提交成功后失效缓存
try {
  // ... API 调用 ...

  success(isEdit ? '事件更新成功' : '事件创建成功');

  // ✅ 失效事件列表缓存
  queryClient.invalidateQueries({
    queryKey: ['events', currentGame?.gid]  // 使用当前游戏的 GID
  });

  navigate('/events', { replace: true });
} catch (err) {
  showError(err.message);
}
```

---

### 1.4 分类管理（CategoriesList）🔴 P0

**文件**: `frontend/src/analytics/pages/CategoriesList.jsx`

**问题代码**:
```javascript
// 第 50 行：查询时使用 game_gid
queryKey: ['categories', gameGid]

// 第 90 行：删除后失效缓存（缺少 gameGid）
queryClient.invalidateQueries({ queryKey: ['categories'] });

// 第 111 行：批量删除后（同样缺少 gameGid）
queryClient.invalidateQueries({ queryKey: ['categories'] });

// 第 329 行：模态框成功回调（正确使用了 gameGid）
queryClient.invalidateQueries({ queryKey: ['categories'] });
```

**问题分析**:
- ⚠️ **不一致**：查询使用 `['categories', gameGid]`，失效使用 `['categories']`
- ⚠️ 三个位置中的缓存失效方式不统一
- 第329行虽然正确，但在模态框内部，列表页面本身的删除操作不正确

**修复建议**:
```javascript
// 第 90 行：删除成功后
queryClient.invalidateQueries({ queryKey: ['categories', gameGid] });

// 第 111 行：批量删除成功后
queryClient.invalidateQueries({ queryKey: ['categories', gameGid] });
```

---

### 1.5 公参管理（CommonParamsList）🔴 P0

**文件**: `frontend/src/analytics/pages/CommonParamsList.jsx`

**问题代码**:
```javascript
// 第 29 行：查询时使用 gameGid
queryKey: ['common-params', gameGid]

// 第 60 行：删除后失效缓存（缺少 gameGid）
queryClient.invalidateQueries({ queryKey: ['common-params'] });

// 第 77 行：批量删除后（缺少 gameGid）
queryClient.invalidateQueries({ queryKey: ['common-params'] });

// 第 102 行：同步后（正确使用了 gameGid）
queryClient.invalidateQueries({ queryKey: ['common-params', gameGid] });
```

**问题分析**:
- ⚠️ **不一致**：查询使用 `['common-params', gameGid]`，删除/批量删除缺少 `gameGid`
- ✅ 同步操作正确使用了 `gameGid`

**修复建议**:
```javascript
// 第 60 行：删除成功后
queryClient.invalidateQueries({ queryKey: ['common-params', gameGid] });

// 第 77 行：批量删除成功后
queryClient.invalidateQueries({ queryKey: ['common-params', gameGid] });
```

---

### 1.6 流程管理（FlowsList）🟡 P1

**文件**: `frontend/src/analytics/pages/FlowsList.jsx`

**问题代码**:
```javascript
// 第 29 行：查询时使用 gameGid
queryKey: ['flows', gameGid]

// 第 64 行：删除后失效缓存（缺少 gameGid）
queryClient.invalidateQueries(['flows']);

// 第 118 行：手动刷新时（正确使用了 gameGid）
queryClient.invalidateQueries({ queryKey: ['flows', gameGid] });
```

**问题分析**:
- ⚠️ **不一致**：查询使用 `['flows', gameGid]`，删除使用 `['flows']`
- ✅ 手动刷新正确使用了 `gameGid`

**修复建议**:
```javascript
// 第 64 行：删除成功后
queryClient.invalidateQueries({ queryKey: ['flows', gameGid] });
```

---

### 1.7 分类管理模态框（CategoryManagementModal）🟡 P1

**文件**: `frontend/src/analytics/components/categories/CategoryManagementModal.jsx`

**问题代码**:
```javascript
// 第 31 行：查询时使用 gameGid
queryKey: ['categories', gameGid]

// 第 55、77、97 行：所有 mutation 都缺少 gameGid
queryClient.invalidateQueries(['categories']);
```

**问题分析**:
- ⚠️ **不一致**：查询使用 `['categories', gameGid]`，所有失效都缺少 `gameGid`

**修复建议**:
```javascript
// 所有三个位置统一修改
queryClient.invalidateQueries({ queryKey: ['categories', gameGid] });
```

---

### 1.8 分类模态框（CategoryModal）✅ 正确

**文件**: `frontend/src/analytics/components/categories/CategoryModal.jsx`

**问题代码**:
```javascript
// 第 107 行：提交成功后（正确使用了 gameGid）
queryClient.invalidateQueries({ queryKey: ['categories', gameGid] });
```

**分析**:
- ✅ **正确实现**：缓存失效与查询键完全一致
- 📚 **参考示例**：其他组件应该参考这个实现

---

## 二、后端缓存问题

### 2.1 缓存失效模式不一致

**问题代码** (`backend/core/cache/invalidator.py`):
```python
# 第 168 行：事件列表失效
event_count = self.invalidate_pattern('events.list', game_id=game_gid)
# ❌ 使用 game_id 参数

# 第 227 行：事件列表失效（另一个地方）
event_count = self.invalidate_pattern('events.list', game_id=game_gid)
# ❌ 同样使用 game_id

# 第 283 行：参数失效
event_count = self.invalidate_pattern('events.list', game_id=game_gid)
# ❌ 又是 game_id
```

**问题分析**:
- ❌ **参数命名混乱**：代码使用 `game_id` 但实际传入的是 `game_gid`
- ❌ **缓存键格式不统一**：有些地方使用 `game_id`，有些使用 `game_gid`
- ⚠️ 可能导致缓存失效失败

**修复建议**:
```python
# 统一使用 game_gid
event_count = self.invalidate_pattern('events.list', game_gid=game_gid)
```

---

### 2.2 后端API不返回更新后的数据

**问题代码** (`backend/api/routes/games.py`):
```python
# 第 414 行：更新游戏
return json_success_response(message="Game updated successfully")
# ❌ 没有返回更新后的游戏数据

# 第 269 行：删除游戏后
cache_invalidator.invalidate_pattern("dashboard_statistics:*")
# ✅ 失效缓存，但没有通知前端
```

**问题代码** (`backend/api/routes/events.py`):
```python
# 第 502 行：删除事件
cache_invalidator.invalidate_pattern("events.list:*")
# ✅ 失效缓存，但API响应未包含更新后的列表

# 第 561 行：更新事件
cache_invalidator.invalidate_pattern("events.list:*")
# ✅ 失效缓存，但API响应未包含更新后的数据
```

**问题分析**:
- ❌ **违反 RESTful 最佳实践**：修改操作应返回更新后的资源
- ❌ **前端无法同步更新**：依赖 `invalidateQueries` 重新请求，增加网络开销
- ⚠️ **可能导致竞态条件**：如果缓存失效失败，前端数据不会更新

**修复建议**:
```python
# 方案1：返回更新后的数据（推荐）
# 修改操作后，查询并返回更新后的数据
updated_data = fetch_one_as_dict('SELECT * FROM games WHERE gid = ?', (gid,))
return json_success_response(data=updated_data, message="Game updated successfully")

# 方案2：使用 setQueryData 前端直接更新（备选）
# 前端在 onSuccess 回调中手动更新缓存
```

---

## 三、根本原因分析

### 3.1 架构层面

1. **缓存键设计不一致**
   - 查询时使用复杂的缓存键（包含多个参数）
   - 失效时使用简化的缓存键（不包含关键参数）
   - 导致 React Query 无法精确匹配和失效

2. **前后端缓存策略不同步**
   - 后端使用基于模式（pattern）的缓存失效
   - 前端使用基于键（key）的缓存失效
   - 两者之间没有明确的映射关系

3. **缺少统一的缓存管理规范**
   - 没有明确的缓存键命名规范
   - 没有统一的缓存失效策略
   - 每个开发者各自实现，导致不一致

### 3.2 实现层面

1. **开发者对 React Query 理解不足**
   - 不了解 `invalidateQueries` 的精确匹配机制
   - 不了解缓存键的结构化设计原则
   - 习惯使用简单的字符串键，而非数组键

2. **后端 API 设计不符合最佳实践**
   - 修改操作只返回成功/失败，不返回更新后的数据
   - 依赖前端重新请求数据，增加网络开销
   - 无法实现乐观更新（optimistic updates）

3. **测试覆盖不足**
   - 没有针对缓存一致性的 E2E 测试
   - 手动测试时往往忽略缓存更新问题
   - 问题在生产环境才暴露

---

## 四、影响评估

### 4.1 用户体验影响

| 功能模块 | 影响程度 | 用户操作 | 预期行为 | 实际行为 |
|---------|---------|---------|---------|---------|
| 游戏管理 | 🔴 严重 | 更新游戏名称 | 立即看到新名称 | ❌ 需要刷新页面 |
| 事件管理 | 🔴 严重 | 创建/编辑事件 | 立即看到新事件 | ❌ 需要刷新页面 |
| 分类管理 | 🔴 严重 | 添加/删除分类 | 立即看到更新 | ❌ 需要刷新页面 |
| 公参管理 | 🔴 严重 | 同步公参 | 立即看到新公参 | ✅ 正常工作 |
| 流程管理 | 🟡 中等 | 删除流程 | 立即从列表消失 | ❌ 需要刷新页面 |

### 4.2 性能影响

1. **不必要的网络请求**
   - 缓存失效后重新请求数据
   - 如果后端返回更新后的数据，可以避免这次请求
   - 估计增加 20-30% 的网络流量

2. **服务器负载增加**
   - 前端频繁重新请求数据
   - 后端缓存失效未命中
   - 数据库查询增加

3. **前端渲染性能**
   - 重新请求数据后需要重新渲染
   - 如果使用 `setQueryData`，可以实现乐观更新
   - 用户体验更流畅

---

## 五、修复方案

### 5.1 短期修复（P0 - 立即执行）

#### 修复1：统一缓存失效键（1-2小时）

**优先级**: 🔴 P0
**工作量**: 1-2小时
**影响文件**: 8个前端组件

**修复步骤**:
1. 修改所有 `invalidateQueries` 调用，使用完整的缓存键
2. 确保失效键与查询键完全一致
3. 添加代码审查规则，防止以后引入类似问题

**修复清单**:
```javascript
// ✅ EventsList.jsx:89
- queryClient.invalidateQueries(['events']);
+ queryClient.invalidateQueries({ queryKey: ['events', currentGame?.gid] });

// ✅ CategoriesList.jsx:90
- queryClient.invalidateQueries({ queryKey: ['categories'] });
+ queryClient.invalidateQueries({ queryKey: ['categories', gameGid] });

// ✅ CommonParamsList.jsx:60
- queryClient.invalidateQueries({ queryKey: ['common-params'] });
+ queryClient.invalidateQueries({ queryKey: ['common-params', gameGid] });

// ✅ FlowsList.jsx:64
- queryClient.invalidateQueries(['flows']);
+ queryClient.invalidateQueries({ queryKey: ['flows', gameGid] });

// ✅ CategoryManagementModal.jsx:55,77,97
- queryClient.invalidateQueries(['categories']);
+ queryClient.invalidateQueries({ queryKey: ['categories', gameGid] });
```

**验证方法**:
1. 启动前端和后端服务器
2. 执行增删改操作
3. 验证界面立即更新显示最新数据
4. 不需要手动刷新页面

---

#### 修复2：EventForm 添加缓存失效（1小时）

**优先级**: 🔴 P0
**工作量**: 1小时
**影响文件**: 1个前端组件

**修复步骤**:
1. 在 `EventForm.jsx` 中导入 `useQueryClient`
2. 在提交成功后添加缓存失效逻辑
3. 验证创建/编辑事件后立即返回列表

**修复代码**:
```javascript
// EventForm.jsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

function EventForm() {
  const queryClient = useQueryClient();
  // ... 其他代码 ...

  const handleSubmit = async (e) => {
    e.preventDefault();

    // ... 验证逻辑 ...

    try {
      const url = isEdit ? `/api/events/${id}` : '/api/events';
      const method = isEdit ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const result = await response.json();
        throw new Error(result.message || (isEdit ? '更新失败' : '创建失败'));
      }

      success(isEdit ? '事件更新成功' : '事件创建成功');

      // ✅ 失效事件列表缓存
      const gameGid = searchParams.get('game_gid') || currentGame?.gid;
      queryClient.invalidateQueries({
        queryKey: ['events', parseInt(gameGid)]
      });

      navigate('/events', { replace: true });
    } catch (err) {
      showError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };
}
```

---

#### 修复3：后端缓存失效参数统一（1小时）

**优先级**: 🟡 P1
**工作量**: 1小时
**影响文件**: 1个后端文件

**修复步骤**:
1. 修改 `backend/core/cache/invalidator.py` 中的所有 `game_id` 为 `game_gid`
2. 确保参数命名与数据库字段一致
3. 添加单元测试验证缓存失效逻辑

**修复代码**:
```python
# backend/core/cache/invalidator.py

# 第 168 行
- event_count = self.invalidate_pattern('events.list', game_id=game_gid)
+ event_count = self.invalidate_pattern('events.list', game_gid=game_gid)

# 第 227 行
- event_count = self.invalidate_pattern('events.list', game_id=game_gid)
+ event_count = self.invalidate_pattern('events.list', game_gid=game_gid)

# 第 283 行
- event_count = self.invalidate_pattern('events.list', game_id=game_gid)
+ event_count = self.invalidate_pattern('events.list', game_gid=game_gid)

# 第 310 行（如果有）
- self.invalidate_pattern('events.list', game_id=game_gid)
+ self.invalidate_pattern('events.list', game_gid=game_gid)
```

---

### 5.2 中期优化（P1 - 1-2周）

#### 优化1：后端API返回更新后的数据（2-3天）

**优先级**: 🟡 P1
**工作量**: 2-3天
**影响文件**: 4-5个后端路由

**优化目标**:
- 所有修改操作（POST/PUT/PATCH/DELETE）返回更新后的数据
- 前端可以使用返回的数据直接更新缓存（`setQueryData`）
- 实现乐观更新（optimistic updates）

**示例代码**:
```python
# backend/api/routes/games.py:414
@api_bp.route("/api/games/<int:gid>", methods=["PUT"])
def api_update_game(gid):
    # ... 验证和更新逻辑 ...

    execute_write(query, tuple(update_values))

    # ✅ 查询并返回更新后的游戏数据
    updated_game = fetch_one_as_dict(
        'SELECT * FROM games WHERE gid = ?',
        (gid,)
    )

    if cache_invalidator:
        cache_invalidator.invalidate_pattern("games.list:*")
        cache_invalidator.invalidate_pattern("dashboard_statistics:*")

    return json_success_response(
        data=updated_game,
        message="Game updated successfully"
    )
```

**前端使用**:
```javascript
// frontend/src/features/games/GameManagementModal.jsx:244
const updateMutation = useMutation({
  mutationFn: async ({ gid, ...data }) => {
    const response = await fetch(`/api/games/${gid}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to update game');
    return response.json();
  },
  onSuccess: (data, variables) => {
    // ✅ 直接使用返回的数据更新缓存
    queryClient.setQueryData(['games'], (oldGames) => {
      return oldGames.map(g => g.gid === variables.gid ? data.data : g);
    });

    // ✅ 然后失效缓存以确保数据一致性
    queryClient.invalidateQueries(['games']);

    success('游戏更新成功');
    setHasChanges(false);
  },
  onError: (err) => {
    showError(`更新失败: ${err.message}`);
  }
});
```

---

#### 优化2：建立缓存键命名规范（1天）

**优先级**: 🟡 P1
**工作量**: 1天
**输出文档**: 缓存管理规范文档

**规范内容**:
1. **缓存键结构**
   ```javascript
   // ✅ 正确：使用数组形式的缓存键，包含所有依赖参数
   queryKey: ['resource', id, param1, param2]

   // ❌ 错误：使用字符串形式的缓存键
   queryKey: 'resource'

   // ❌ 错误：缺少关键参数
   queryKey: ['resource']  // 缺少 id
   ```

2. **缓存失效规则**
   ```javascript
   // ✅ 正确：使用与查询相同的缓存键
   queryClient.invalidateQueries({
     queryKey: ['resource', id, param1, param2]
   });

   // ❌ 错误：使用简化版本的缓存键
   queryClient.invalidateQueries({ queryKey: ['resource'] });

   // ✅ 正确：使用 predicate 函数批量失效
   queryClient.invalidateQueries({
     predicate: (query) => query.queryKey[0] === 'resource'
   });
   ```

3. **后端缓存失效模式**
   ```python
   # ✅ 正确：使用完整的缓存键格式
   cache_invalidator.invalidate_pattern(f"resource.list:{game_gid}:*")

   # ❌ 错误：使用通配符过于宽泛
   cache_invalidator.invalidate_pattern("resource.list:*")

   # ❌ 错误：参数命名不一致
   cache_invalidator.invalidate_pattern('resource.list', game_id=game_gid)
   ```

**文档位置**:
`docs/development/react-query-cache-guidelines.md`

---

#### 优化3：添加 E2E 测试（2-3天）

**优先级**: 🟡 P1
**工作量**: 2-3天
**测试框架**: Playwright

**测试场景**:
1. 游戏管理：创建、编辑、删除游戏后验证列表更新
2. 事件管理：创建、编辑、删除事件后验证列表更新
3. 分类管理：创建、编辑、删除分类后验证列表更新
4. 公参管理：同步公参后验证列表更新

**测试代码示例**:
```typescript
// frontend/test/e2e/cache-consistency.spec.ts
import { test, expect } from '@playwright/test';

test.describe('React Query Cache Consistency', () => {
  test('游戏更新后列表立即刷新', async ({ page }) => {
    await page.goto('http://localhost:5173');

    // 打开游戏管理模态框
    await page.click('[data-testid="game-management-button"]');
    await page.waitForSelector('.game-management-modal');

    // 选择一个游戏
    await page.click('.game-list-item:first-child');

    // 修改游戏名称
    const newName = `Updated Game ${Date.now()}`;
    await page.fill('input[name="name"]', newName);
    await page.click('button:has-text("保存")');

    // 等待保存完成
    await page.waitForSelector('text=游戏更新成功');

    // ✅ 验证游戏列表立即更新（不需要刷新页面）
    const gameName = await page.textContent('.game-list-item:first-child .game-item-name');
    expect(gameName).toContain(newName);
  });

  test('事件创建后列表立即刷新', async ({ page }) => {
    await page.goto('http://localhost:5173/events?game_gid=10000147');

    // 点击添加事件按钮
    await page.click('button:has-text("添加事件")');

    // 填写事件表单
    await page.fill('input[name="event_name"]', `test.event.${Date.now()}`);
    await page.fill('input[name="event_name_cn"]', '测试事件');
    await page.click('button:has-text("创建事件")');

    // 等待创建完成
    await page.waitForSelector('text=事件创建成功');

    // ✅ 验证事件列表立即显示新事件（不需要刷新页面）
    const eventList = await page.textContent('.events-table');
    expect(eventList).toContain(`test.event.`);
  });
});
```

---

### 5.3 长期改进（P2 - 1个月）

#### 改进1：实现乐观更新（1周）

**优先级**: 🟢 P2
**工作量**: 1周
**用户体验**: 显著提升

**实现方案**:
```javascript
// 乐观更新示例
const updateMutation = useMutation({
  mutationFn: async (newData) => {
    const response = await fetch(`/api/games/${gid}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newData)
    });
    return response.json();
  },
  onMutate: async (variables) => {
    // ✅ 取消正在进行的查询
    await queryClient.cancelQueries(['games']);

    // ✅ 保存之前的缓存数据（用于回滚）
    const previousGames = queryClient.getQueryData(['games']);

    // ✅ 乐观更新缓存
    queryClient.setQueryData(['games'], (oldGames) => {
      return oldGames.map(g =>
        g.gid === variables.gid
          ? { ...g, ...variables }
          : g
      );
    });

    return { previousGames };
  },
  onError: (err, variables, context) => {
    // ❌ 发生错误，回滚缓存
    queryClient.setQueryData(['games'], context.previousGames);
  },
  onSettled: () => {
    // ✅ 无论成功失败，都重新获取数据以确保一致性
    queryClient.invalidateQueries(['games']);
  }
});
```

---

#### 改进2：建立缓存监控系统（3-5天）

**优先级**: 🟢 P2
**工作量**: 3-5天
**技术栈**: React Query DevTools + 后端监控

**监控指标**:
1. 缓存命中率
2. 缓存失效频率
3. 缓存重新请求次数
4. 缓存不一致错误次数

**实现方案**:
```javascript
// 缓存监控中间件
import { QueryClient } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      onSuccess: (data, query) => {
        // 记录缓存命中
        console.log(`[Cache Hit] ${query.queryKey.join('/')}`);
      },
      onError: (error, query) => {
        // 记录缓存错误
        console.error(`[Cache Error] ${query.queryKey.join('/')}:`, error);
      }
    },
    mutations: {
      onSuccess: (data, variables, query) => {
        // 记录缓存失效
        console.log(`[Cache Invalidate] ${query.mutationKey}`);
      }
    }
  }
});
```

---

## 六、修复优先级和时间表

### Phase 1: 紧急修复（P0 - 本周完成）

| 任务 | 优先级 | 工作量 | 负责人 | 截止日期 |
|-----|--------|--------|--------|----------|
| 统一缓存失效键 | 🔴 P0 | 2小时 | Frontend | 2026-02-23 |
| EventForm 添加缓存失效 | 🔴 P0 | 1小时 | Frontend | 2026-02-23 |
| 后端参数统一 | 🟡 P1 | 1小时 | Backend | 2026-02-24 |
| E2E 测试验证 | 🔴 P0 | 2小时 | QA | 2026-02-24 |

**里程碑**: 所有核心功能的缓存一致性问题修复完成

---

### Phase 2: 优化改进（P1 - 下周完成）

| 任务 | 优先级 | 工作量 | 负责人 | 截止日期 |
|-----|--------|--------|--------|----------|
| 后端API返回更新数据 | 🟡 P1 | 3天 | Backend | 2026-02-28 |
| 建立缓存键规范 | 🟡 P1 | 1天 | Tech Lead | 2026-02-26 |
| 完善E2E测试覆盖 | 🟡 P1 | 3天 | QA | 2026-02-28 |

**里程碑**: 建立完整的缓存管理规范和测试体系

---

### Phase 3: 长期改进（P2 - 3月份）

| 任务 | 优先级 | 工作量 | 负责人 | 截止日期 |
|-----|--------|--------|--------|----------|
| 实现乐观更新 | 🟢 P2 | 1周 | Frontend | 2026-03-07 |
| 缓存监控系统 | 🟢 P2 | 1周 | DevOps | 2026-03-14 |

**里程碑**: 显著提升用户体验和系统可观测性

---

## 七、验证清单

### 7.1 功能验证（手动测试）

- [ ] **游戏管理**
  - [ ] 创建游戏后，游戏列表立即显示新游戏
  - [ ] 编辑游戏名称后，游戏列表立即显示新名称
  - [ ] 删除游戏后，游戏列表立即移除该游戏
  - [ ] 批量删除游戏后，游戏列表立即移除所有已删除游戏

- [ ] **事件管理**
  - [ ] 创建事件后，事件列表立即显示新事件
  - [ ] 编辑事件后，事件列表立即显示更新后的事件
  - [ ] 删除事件后，事件列表立即移除该事件
  - [ ] 批量删除事件后，事件列表立即移除所有已删除事件

- [ ] **分类管理**
  - [ ] 创建分类后，分类列表立即显示新分类
  - [ ] 编辑分类后，分类列表立即显示更新后的分类
  - [ ] 删除分类后，分类列表立即移除该分类
  - [ ] 批量删除分类后，分类列表立即移除所有已删除分类

- [ ] **公参管理**
  - [ ] 删除公参后，公参列表立即移除该公参
  - [ ] 批量删除公参后，公参列表立即移除所有已删除公参
  - [ ] 同步公参后，公参列表立即显示新公参

- [ ] **流程管理**
  - [ ] 删除流程后，流程列表立即移除该流程

### 7.2 技术验证（代码审查）

- [ ] 所有 `invalidateQueries` 调用使用完整的缓存键
- [ ] 所有 `queryKey` 使用数组形式（非字符串）
- [ ] 所有 `queryKey` 包含所有依赖参数
- [ ] 后端API返回更新后的数据
- [ ] 后端缓存失效使用正确的参数名（`game_gid`）

### 7.3 性能验证（测试环境）

- [ ] 测量修复前后的网络请求数量
- [ ] 测量修复前后的缓存命中率
- [ ] 测量修复前后的页面响应时间

---

## 八、附录

### 8.1 相关文件清单

**前端文件（8个需要修复）**:
1. `frontend/src/features/games/GameManagementModal.jsx`
2. `frontend/src/analytics/pages/EventsList.jsx`
3. `frontend/src/analytics/pages/EventForm.jsx`
4. `frontend/src/analytics/pages/CategoriesList.jsx`
5. `frontend/src/analytics/pages/CommonParamsList.jsx`
6. `frontend/src/analytics/pages/FlowsList.jsx`
7. `frontend/src/analytics/components/categories/CategoryManagementModal.jsx`
8. `frontend/src/analytics/components/categories/CategoryModal.jsx` ✅（参考示例）

**后端文件（1个需要修复）**:
1. `backend/core/cache/invalidator.py`

**后端API路由（4个建议优化）**:
1. `backend/api/routes/games.py`
2. `backend/api/routes/events.py`
3. `backend/api/routes/categories.py`
4. `backend/api/routes/parameters.py`

### 8.2 React Query 最佳实践

**缓存键设计**:
```javascript
// ✅ 正确：使用数组形式的缓存键
queryKey: ['resource', id, param1, param2]

// ✅ 正确：使用对象形式的缓存键（更清晰）
queryKey: ['resource', { id, param1, param2 }]

// ❌ 错误：使用字符串形式的缓存键
queryKey: 'resource'

// ❌ 错误：使用嵌套对象（难以匹配）
queryKey: ['resource', { params: { id, param1 } }]
```

**缓存失效**:
```javascript
// ✅ 正确：精确失效
queryClient.invalidateQueries({
  queryKey: ['resource', id]
});

// ✅ 正确：批量失效（使用 predicate）
queryClient.invalidateQueries({
  predicate: (query) => query.queryKey[0] === 'resource'
});

// ❌ 错误：过度失效（失效所有缓存）
queryClient.invalidateQueries();
```

**乐观更新**:
```javascript
// ✅ 正确：使用 onMutate 实现乐观更新
const mutation = useMutation({
  mutationFn: updateData,
  onMutate: async (variables) => {
    await queryClient.cancelQueries(['resource']);
    const previousData = queryClient.getQueryData(['resource']);
    queryClient.setQueryData(['resource'], variables);
    return { previousData };
  },
  onError: (err, variables, context) => {
    queryClient.setQueryData(['resource'], context.previousData);
  },
  onSettled: () => {
    queryClient.invalidateQueries(['resource']);
  }
});
```

---

## 九、总结

### 9.1 核心问题

Event2Table 项目存在**严重的 React Query 缓存一致性问题**，影响所有核心功能模块的增删改操作。

### 9.2 根本原因

1. 前端缓存失效键与查询键不一致
2. 后端API不返回更新后的数据
3. 缺少统一的缓存管理规范

### 9.3 解决方案

1. **短期修复**（本周）：统一缓存失效键
2. **中期优化**（下周）：后端API返回更新数据
3. **长期改进**（3月）：实现乐观更新

### 9.4 预期效果

- ✅ 所有增删改操作后界面立即更新
- ✅ 不需要手动刷新页面
- ✅ 减少不必要的网络请求
- ✅ 显著提升用户体验

---

**报告生成时间**: 2026-02-22
**下次审查时间**: 2026-02-25（Phase 1 完成后）
**负责人**: Event2Table 开发团队
