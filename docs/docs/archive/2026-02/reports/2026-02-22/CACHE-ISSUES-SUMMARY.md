# React Query 缓存一致性问题摘要

**日期**: 2026-02-22
**严重程度**: 🔴 P0 - 严重
**状态**: 🔧 待修复

---

## 快速概览

### 问题
Event2Table 项目所有增删改操作后，前端界面**不会自动更新显示最新数据**，用户需要手动刷新页面。

### 根本原因
1. **前端缓存失效范围过窄**：`invalidateQueries` 使用了不完整的缓存键
2. **后端API不返回更新后的数据**：修改操作只返回成功消息
3. **缓存键设计不一致**：查询和失效使用了不同的缓存键结构

### 影响范围
- **8个核心功能模块**受影响
- **所有增删改操作**（100%）都不会立即更新界面
- **用户体验严重受损**

---

## 问题清单（按严重程度排序）

### 🔴 P0 - 严重问题（需要立即修复）

| # | 功能模块 | 文件 | 问题 | 影响 |
|---|---------|------|------|------|
| 1 | 游戏管理 | `GameManagementModal.jsx:110,216,245` | 后端未返回更新数据，依赖5秒staleTime | 更新游戏后看不到新名称 |
| 2 | 事件管理 | `EventsList.jsx:89,226` | 缓存键不匹配（6个参数 vs 1个参数） | 所有事件操作后看不到更新 |
| 3 | 事件表单 | `EventForm.jsx` | 完全没有缓存失效逻辑 | 创建/编辑事件后看不到新事件 |
| 4 | 分类管理 | `CategoriesList.jsx:90,111` | 缓存键缺少 `gameGid` 参数 | 删除分类后看不到更新 |
| 5 | 公参管理 | `CommonParamsList.jsx:60,77` | 缓存键缺少 `gameGid` 参数 | 删除公参后看不到更新 |
| 6 | 流程管理 | `FlowsList.jsx:64` | 缓存键缺少 `gameGid` 参数 | 删除流程后看不到更新 |
| 7 | 分类模态框 | `CategoryManagementModal.jsx:55,77,97` | 缓存键缺少 `gameGid` 参数 | 所有分类操作后看不到更新 |

### 🟡 P1 - 中等问题（建议下周修复）

| # | 功能模块 | 文件 | 问题 | 影响 |
|---|---------|------|------|------|
| 8 | 后端缓存 | `invalidator.py:168,227,283` | 使用 `game_id` 而非 `game_gid` | 缓存失效可能失败 |

### ✅ 正确实现（参考示例）

| # | 功能模块 | 文件 | 评价 |
|---|---------|------|------|
| 1 | 分类模态框 | `CategoryModal.jsx:107` | ✅ 正确使用 `['categories', gameGid]` |
| 2 | 公参同步 | `CommonParamsList.jsx:102` | ✅ 正确使用 `['common-params', gameGid]` |

---

## 修复方案

### 方案1：统一缓存失效键（推荐 - 立即执行）

**工作量**: 1-2小时
**影响**: 8个前端文件

**修复原则**:
```javascript
// ✅ 正确：查询时使用的缓存键
queryKey: ['events', currentPage, pageSize, selectedCategory, currentGame?.gid, searchTerm]

// ✅ 正确：失效时使用完全相同的缓存键
queryClient.invalidateQueries({
  queryKey: ['events', currentGame?.gid]  // 至少包含关键参数
});
```

**修复清单**:
1. `EventsList.jsx:89,226` - 使用 `['events', currentGame?.gid]`
2. `CategoriesList.jsx:90,111` - 使用 `['categories', gameGid]`
3. `CommonParamsList.jsx:60,77` - 使用 `['common-params', gameGid]`
4. `FlowsList.jsx:64` - 使用 `['flows', gameGid]`
5. `CategoryManagementModal.jsx:55,77,97` - 使用 `['categories', gameGid]`
6. `EventForm.jsx` - 添加 `queryClient.invalidateQueries`

### 方案2：后端API返回更新后的数据（优化 - 下周执行）

**工作量**: 2-3天
**影响**: 4-5个后端路由

**修复示例**:
```python
# ❌ 当前实现
return json_success_response(message="Game updated successfully")

# ✅ 推荐实现
updated_game = fetch_one_as_dict('SELECT * FROM games WHERE gid = ?', (gid,))
return json_success_response(data=updated_game, message="Game updated successfully")
```

---

## 自动修复脚本

为了加速修复，已创建自动修复脚本：

```bash
# 运行自动修复
bash scripts/cache-fix/apply-cache-fixes.sh
```

**脚本功能**:
- ✅ 自动修复6个文件的缓存失效键
- ✅ 创建备份（`/.cache-fix-backup-YYYYMMDD_HHMMSS/`）
- ⚠️ EventForm.jsx 需要手动编辑（脚本提供详细指导）
- ✅ 提供验证和回滚指令

---

## 验证清单

### 功能验证（手动测试）

- [ ] **游戏管理**
  - [ ] 编辑游戏名称后，列表立即显示新名称
  - [ ] 删除游戏后，列表立即移除该游戏

- [ ] **事件管理**
  - [ ] 创建事件后，列表立即显示新事件
  - [ ] 编辑事件后，列表立即显示更新后的事件
  - [ ] 删除事件后，列表立即移除该事件

- [ ] **分类管理**
  - [ ] 创建分类后，列表立即显示新分类
  - [ ] 删除分类后，列表立即移除该分类

- [ ] **公参管理**
  - [ ] 删除公参后，列表立即移除该公参
  - [ ] 同步公参后，列表立即显示新公参

- [ ] **流程管理**
  - [ ] 删除流程后，列表立即移除该流程

### 技术验证（代码审查）

- [ ] 所有 `invalidateQueries` 使用完整的缓存键
- [ ] 所有 `queryKey` 使用数组形式
- [ ] 所有 `queryKey` 包含所有依赖参数
- [ ] 后端缓存失效使用正确的参数名（`game_gid`）

---

## 时间表

| 阶段 | 任务 | 工作量 | 截止日期 | 负责人 |
|-----|------|--------|----------|--------|
| **Phase 1** | 统一缓存失效键 | 2小时 | 2026-02-23 | Frontend |
| **Phase 1** | EventForm 添加缓存失效 | 1小时 | 2026-02-23 | Frontend |
| **Phase 1** | E2E 测试验证 | 2小时 | 2026-02-24 | QA |
| **Phase 2** | 后端API返回更新数据 | 3天 | 2026-02-28 | Backend |
| **Phase 2** | 建立缓存键规范 | 1天 | 2026-02-26 | Tech Lead |

---

## 相关文档

- **完整分析报告**: `docs/reports/2026-02-22/REACT-QUERY-CACHE-ANALYSIS-REPORT.md`
- **自动修复脚本**: `scripts/cache-fix/apply-cache-fixes.sh`
- **React Query 最佳实践**: `docs/development/react-query-best-practices.md`（待创建）

---

## 关键代码示例

### ✅ 正确实现（CategoryModal.jsx - 参考）

```javascript
// 第 21 行：查询时使用完整的缓存键
const { data: categoriesData } = useQuery({
  queryKey: ['categories', gameGid],  // ✅ 包含 gameGid
  queryFn: async () => {
    // ...
  }
});

// 第 107 行：失效时使用完全相同的缓存键
onSuccess: (data) => {
  queryClient.invalidateQueries({
    queryKey: ['categories', gameGid]  // ✅ 与查询完全一致
  });
}
```

### ❌ 错误实现（EventsList.jsx - 需要修复）

```javascript
// 第 42 行：查询时使用复杂的缓存键
const { data } = useQuery({
  queryKey: ['events', currentPage, pageSize, selectedCategory, currentGame?.gid, searchTerm],
  // ❌ 6个参数
});

// 第 89 行：失效时使用简化的缓存键
onSuccess: (data) => {
  queryClient.invalidateQueries(['events']);  // ❌ 只有1个参数，不匹配
}
```

### ✅ 修复后（EventsList.jsx - 推荐）

```javascript
// 第 89 行：使用精确的缓存键
onSuccess: (data) => {
  queryClient.invalidateQueries({
    queryKey: ['events', currentGame?.gid]  // ✅ 至少包含关键参数
  });
}
```

---

## 联系信息

**问题发现**: Claude Code Agent
**报告生成**: 2026-02-22
**审查状态**: 待技术负责人审查
**下一步**: 运行自动修复脚本，然后进行手动测试验证

---

**附录**:
- 备份位置：运行脚本后自动创建 `/.cache-fix-backup-YYYYMMDD_HHMMSS/`
- 回滚方法：参考脚本输出中的回滚指令
- 验证方法：参考上述验证清单
