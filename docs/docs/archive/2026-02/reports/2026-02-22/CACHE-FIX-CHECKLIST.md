# 缓存一致性问题修复清单

**检查表版本**: 1.0
**最后更新**: 2026-02-22
**预计完成时间**: 2026-02-23

---

## 使用说明

- ✅ = 已完成
- ⏳ = 进行中
- ❌ = 待修复
- ⏭️ = 跳过（不需要修复）

---

## Phase 1: 紧急修复（P0）

### 1.1 前端缓存失效键修复

#### EventsList.jsx
- [ ] **文件**: `frontend/src/analytics/pages/EventsList.jsx`
- [ ] **第89行** - 删除mutation:
  ```javascript
  // 修改前
  queryClient.invalidateQueries(['events']);

  // 修改后
  queryClient.invalidateQueries({ queryKey: ['events', currentGame?.gid] });
  ```
- [ ] **第226行** - 手动刷新按钮:
  ```javascript
  // 修改前
  queryClient.invalidateQueries({ queryKey: ['events'] });

  // 修改后
  queryClient.invalidateQueries({ queryKey: ['events', currentGame?.gid] });
  ```
- [ ] **验证**: 删除事件后，列表立即更新

---

#### CategoriesList.jsx
- [ ] **文件**: `frontend/src/analytics/pages/CategoriesList.jsx`
- [ ] **第90行** - 删除mutation:
  ```javascript
  // 修改前
  queryClient.invalidateQueries({ queryKey: ['categories'] });

  // 修改后
  queryClient.invalidateQueries({ queryKey: ['categories', gameGid] });
  ```
- [ ] **第111行** - 批量删除mutation:
  ```javascript
  // 修改前
  queryClient.invalidateQueries({ queryKey: ['categories'] });

  // 修改后
  queryClient.invalidateQueries({ queryKey: ['categories', gameGid] });
  ```
- [ ] **验证**: 删除分类后，列表立即更新

---

#### CommonParamsList.jsx
- [ ] **文件**: `frontend/src/analytics/pages/CommonParamsList.jsx`
- [ ] **第60行** - 删除mutation:
  ```javascript
  // 修改前
  queryClient.invalidateQueries({ queryKey: ['common-params'] });

  // 修改后
  queryClient.invalidateQueries({ queryKey: ['common-params', gameGid] });
  ```
- [ ] **第77行** - 批量删除mutation:
  ```javascript
  // 修改前
  queryClient.invalidateQueries({ queryKey: ['common-params'] });

  // 修改后
  queryClient.invalidateQueries({ queryKey: ['common-params', gameGid] });
  ```
- [ ] **验证**: 删除公参后，列表立即更新

---

#### FlowsList.jsx
- [ ] **文件**: `frontend/src/analytics/pages/FlowsList.jsx`
- [ ] **第64行** - 删除mutation:
  ```javascript
  // 修改前
  queryClient.invalidateQueries(['flows']);

  // 修改后
  queryClient.invalidateQueries({ queryKey: ['flows', gameGid] });
  ```
- [ ] **验证**: 删除流程后，列表立即更新

---

#### CategoryManagementModal.jsx
- [ ] **文件**: `frontend/src/analytics/components/categories/CategoryManagementModal.jsx`
- [ ] **第55行** - 创建mutation:
  ```javascript
  // 修改前
  queryClient.invalidateQueries(['categories']);

  // 修改后
  queryClient.invalidateQueries({ queryKey: ['categories', gameGid] });
  ```
- [ ] **第77行** - 更新mutation:
  ```javascript
  // 修改前
  queryClient.invalidateQueries(['categories']);

  // 修改后
  queryClient.invalidateQueries({ queryKey: ['categories', gameGid] });
  ```
- [ ] **第97行** - 删除mutation:
  ```javascript
  // 修改前
  queryClient.invalidateQueries(['categories']);

  // 修改后
  queryClient.invalidateQueries({ queryKey: ['categories', gameGid] });
  ```
- [ ] **验证**: 所有分类操作后，列表立即更新

---

### 1.2 EventForm.jsx 添加缓存失效

- [ ] **文件**: `frontend/src/analytics/pages/EventForm.jsx`
- [ ] **第3行** - 添加 `useQueryClient` 到 imports:
  ```javascript
  // 修改前
  import { useQuery, useMutation } from '@tanstack/react-query';

  // 修改后
  import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
  ```
- [ ] **第27行后** - 添加 `queryClient` 初始化:
  ```javascript
  function EventForm() {
    const queryClient = useQueryClient();  // ← 添加这一行
    const { success, error: showError } = useToast();
  ```
- [ ] **第159行后** - 在 `handleSubmit` 中添加缓存失效:
  ```javascript
  success(isEdit ? '事件更新成功' : '事件创建成功');

  // 添加以下代码
  const gameGid = searchParams.get('game_gid') || currentGame?.gid;
  queryClient.invalidateQueries({
    queryKey: ['events', parseInt(gameGid)]
  });

  navigate('/events', { replace: true });
  ```
- [ ] **验证**:
  - 创建事件后，立即返回列表并显示新事件
  - 编辑事件后，立即返回列表并显示更新后的事件

---

### 1.3 后端缓存失效参数统一

- [ ] **文件**: `backend/core/cache/invalidator.py`
- [ ] **第168行**:
  ```python
  # 修改前
  event_count = self.invalidate_pattern('events.list', game_id=game_gid)

  # 修改后
  event_count = self.invalidate_pattern('events.list', game_gid=game_gid)
  ```
- [ ] **第227行**:
  ```python
  # 修改前
  event_count = self.invalidate_pattern('events.list', game_id=game_gid)

  # 修改后
  event_count = self.invalidate_pattern('events.list', game_gid=game_gid)
  ```
- [ ] **第283行**:
  ```python
  # 修改前
  event_count = self.invalidate_pattern('events.list', game_id=game_gid)

  # 修改后
  event_count = self.invalidate_pattern('events.list', game_gid=game_gid)
  ```
- [ ] **验证**: 检查后端日志，确认缓存失效成功

---

## Phase 2: 验证测试

### 2.1 功能验证（手动测试）

#### 游戏管理
- [ ] **测试1**: 编辑游戏名称
  - [ ] 操作：打开游戏管理 → 选择游戏 → 修改名称 → 点击保存
  - [ ] 预期：游戏列表立即显示新名称
  - [ ] 实际：□ 通过 □ 失败

- [ ] **测试2**: 删除游戏
  - [ ] 操作：打开游戏管理 → 选择游戏 → 点击删除
  - [ ] 预期：游戏列表立即移除该游戏
  - [ ] 实际：□ 通过 □ 失败

#### 事件管理
- [ ] **测试3**: 创建事件
  - [ ] 操作：打开事件列表 → 点击添加事件 → 填写表单 → 点击创建
  - [ ] 预期：返回列表后立即显示新事件
  - [ ] 实际：□ 通过 □ 失败

- [ ] **测试4**: 编辑事件
  - [ ] 操作：打开事件列表 → 点击编辑事件 → 修改表单 → 点击保存
  - [ ] 预期：返回列表后立即显示更新后的事件
  - [ ] 实际：□ 通过 □ 失败

- [ ] **测试5**: 删除事件
  - [ ] 操作：打开事件列表 → 选择事件 → 点击删除
  - [ ] 预期：事件列表立即移除该事件
  - [ ] 实际：□ 通过 □ 失败

#### 分类管理
- [ ] **测试6**: 删除分类
  - [ ] 操作：打开分类列表 → 选择分类 → 点击删除
  - [ ] 预期：分类列表立即移除该分类
  - [ ] 实际：□ 通过 □ 失败

#### 公参管理
- [ ] **测试7**: 删除公参
  - [ ] 操作：打开公参列表 → 选择公参 → 点击删除
  - [ ] 预期：公参列表立即移除该公参
  - [ ] 实际：□ 通过 □ 失败

- [ ] **测试8**: 同步公参
  - [ ] 操作：打开公参列表 → 点击同步公共参数
  - [ ] 预期：公参列表立即显示新公参
  - [ ] 实际：□ 通过 □ 失败

#### 流程管理
- [ ] **测试9**: 删除流程
  - [ ] 操作：打开流程列表 → 选择流程 → 点击删除
  - [ ] 预期：流程列表立即移除该流程
  - [ ] 实际：□ 通过 □ 失败

---

### 2.2 技术验证（代码审查）

- [ ] **检查1**: 所有 `invalidateQueries` 使用完整的缓存键
  - [ ] 方法：搜索 `invalidateQueries`，检查所有调用
  - [ ] 结果：□ 通过 □ 失败

- [ ] **检查2**: 所有 `queryKey` 使用数组形式（非字符串）
  - [ ] 方法：搜索 `queryKey:`，检查所有定义
  - [ ] 结果：□ 通过 □ 失败

- [ ] **检查3**: 所有 `queryKey` 包含所有依赖参数
  - [ ] 方法：对比 `useQuery` 和 `invalidateQueries` 的缓存键
  - [ ] 结果：□ 通过 □ 失败

- [ ] **检查4**: 后端缓存失效使用正确的参数名（`game_gid`）
  - [ ] 方法：搜索 `game_id=`，确认不存在
  - [ ] 结果：□ 通过 □ 失败

---

## Phase 3: 优化改进（可选）

### 3.1 后端API优化

#### games.py
- [ ] **第414行** - 返回更新后的游戏数据
  ```python
  # 修改前
  return json_success_response(message="Game updated successfully")

  # 修改后
  updated_game = fetch_one_as_dict('SELECT * FROM games WHERE gid = ?', (gid,))
  return json_success_response(data=updated_game, message="Game updated successfully")
  ```

#### events.py
- [ ] **第502行** - 删除事件后返回更新后的列表
- [ ] **第561行** - 更新事件后返回更新后的数据

---

### 3.2 文档和规范

- [ ] 创建 React Query 缓存管理规范文档
  - [ ] 缓存键命名规范
  - [ ] 缓存失效最佳实践
  - [ ] 代码审查检查清单

- [ ] 创建开发者指南
  - [ ] 如何正确使用 `useQuery` 和 `useMutation`
  - [ ] 如何实现乐观更新
  - [ ] 常见陷阱和解决方案

---

## 快速参考

### 自动修复脚本

```bash
# 运行自动修复
bash scripts/cache-fix/apply-cache-fixes.sh
```

### 回滚方法

```bash
# 回滚所有更改
cp .cache-fix-backup-*/EventsList.jsx.bak frontend/src/analytics/pages/EventsList.jsx
cp .cache-fix-backup-*/CategoriesList.jsx.bak frontend/src/analytics/pages/CategoriesList.jsx
# ... 其他文件
```

### 验证命令

```bash
# 启动后端
python web_app.py

# 启动前端（新终端）
cd frontend && npm run dev

# 访问应用
open http://localhost:5173
```

---

## 修复进度统计

**总任务数**: 30
**已完成**: 0
**进行中**: 0
**待修复**: 30

**完成度**: 0%

---

## 备注

- 所有修改都会自动备份到 `/.cache-fix-backup-YYYYMMDD_HHMMSS/`
- 建议先在测试环境验证，然后再应用到生产环境
- 遇到问题时，参考完整分析报告：`docs/reports/2026-02-22/REACT-QUERY-CACHE-ANALYSIS-REPORT.md`

---

**最后更新**: 2026-02-22
**负责人**: Event2Table 开发团队
**审查状态**: 待开始
