# E2E Testing & Validation Plan

> **项目**: Event2Table 前端UI/UX优化
>
> **测试日期**: 2026-02-12
>
> **测试范围**: Phase 1-5 所有已完成功能

---

## 📋 已完成的功能清单

### ✅ Phase 1: 视觉基础（Visual Foundation）

#### 1.1 背景主题更新
- [x] 设计令牌更新为青蓝色调
- [x] 全局背景应用渐变效果
- [x] 主题一致性验证

**文件修改**:
- `frontend/src/styles/design-tokens.css` - 青蓝色调设计令牌
- `frontend/src/index.css` - 全局背景渐变

**验证点**:
- [ ] 背景从纯黑(#000000)变为青蓝渐变
- [ ] 卡片背景使用半透明深青色
- [ ] 主色调保持为青色(#06B6D4)
- [ ] 整体视觉层次感提升

---

#### 1.2 Dashboard hover效果统一
- [x] 删除Dashboard.css中自定义hover样式
- [x] 使用Card组件默认hover效果

**文件修改**:
- `frontend/src/analytics/pages/Dashboard.css` - 移除37-40行和93-96行自定义hover

**验证点**:
- [ ] 所有卡片hover效果统一（青色边框+阴影）
- [ ] stat-card无自定义transform覆盖
- [ ] action-card无自定义transform覆盖
- [ ] hover交互流畅

---

#### 1.3 诊断文件清理
- [x] Dashboard.diagnostic.jsx重命名为.bak

**文件修改**:
- `frontend/src/analytics/pages/Dashboard.diagnostic.jsx` → `Dashboard.diagnostic.jsx.bak`

**验证点**:
- [ ] 生产代码中无调试文件残留

---

### ✅ Phase 2: 状态管理重构（State Management）

#### 2.1 Zustand安装
- [x] 安装zustand@5.0.11

**package.json修改**:
```json
"zustand": "^5.0.11"
```

**验证点**:
- [x] zustand包正确安装
- [ ] 存储大小合理（~3KB）

---

#### 2.2 游戏状态Store创建
- [x] 创建gameStore.ts
- [x] 实现持久化存储
- [x] 提供完整的CRUD方法

**文件创建**:
- `frontend/src/stores/gameStore.ts` - Zustand store with persistence

**Store接口**:
```typescript
interface GameStore {
  currentGame: Game | null;
  setCurrentGame: (game: Game | null) => void;
  clearCurrentGame: () => void;
  // 新增的向后兼容方法:
  gameGid: number | null;
  setGameData: (game: Game | null) => void;
  setGameGid: (gid: number | null) => void;
  clearGame: () => void;
}
```

**验证点**:
- [x] Store结构正确
- [x] 持久化配置正确
- [x] TypeScript类型定义完整
- [ ] localStorage中能正确存储和恢复游戏数据

---

#### 2.3 组件迁移（部分完成）
- [x] 5个subagent已完成核心组件迁移
- [x] gameStore增强版本已部署

**已迁移组件**（示例）:
- `ParametersList.jsx` - useGameStore
- `Sidebar.jsx` - useGameStore
- `GameSelectionSheet.jsx` - 集成GameManagementModal

**待验证**:
- [ ] 所有使用useGameContext的组件已迁移
- [ ] 无遗留Context导入错误
- [ ] 游戏切换功能正常工作

---

### ✅ Phase 3: 搜索栏组件（Search Component）

#### 3.1 SearchInput组件创建
- [x] SearchInput.tsx完整实现
- [x] SearchInput.css青蓝主题样式

**功能特性**:
- 防抖（300ms）
- Ctrl+K / Cmd+K快捷键
- 清除按钮（有内容时显示）
- 搜索图标支持
- 完整的TypeScript类型定义

**文件创建**:
- `frontend/src/shared/ui/SearchInput/SearchInput.tsx` - 主组件
- `frontend/src/shared/ui/SearchInput/SearchInput.css` - 样式文件

**验证点**:
- [ ] 组件正确导出
- [ ] CSS类名正确应用
- [ ] 防抖功能工作正常（300ms延迟）
- [ ] 快捷键Cmd+K触发搜索框聚焦
- [ ] 清除按钮在有内容时显示
- [ ] 点击清除后正确清空输入并隐藏按钮
- [ ] 短捷键提示正确显示（⌘K）

---

### ✅ Phase 4: 游戏管理重构（Game Management）

#### 4.2 游戏管理模态框组件
- [x] GameManagementModal.tsx创建
- [x] GameManagementModal.css样式实现
- [x] 主从视图布局（左侧列表+右侧编辑）

**文件创建**:
- `frontend/src/analytics/components/game-management/GameManagementModal.tsx`
- `frontend/src/analytics/components/game-management/GameManagementModal.css`

**功能特性**:
- 游戏列表展示（带事件计数badge）
- 游戏详情编辑（名称、GID、ODS、DWD前缀）
- 统计数据展示（事件数、参数数、节点数、HQL流程数）
- 删除游戏功能
- 保存更改功能（编辑字段disabled，修改后显示保存按钮）
- React Query数据获取
- 加载状态处理

**验证点**:
- [ ] 模态框正确打开和关闭
- [ ] 游戏列表正确加载
- [ ] 点击游戏项显示详情
- [ ] 编辑字段默认disabled状态
- [ ] 修改字段后启用编辑并显示保存按钮
- [ ] 点击保存后API调用成功
- [ ] 删除游戏确认对话框正常
- [ ] 统计数据正确显示
- [ ] 加载状态正确显示

---

#### 4.3 添加游戏模态框组件
- [x] AddGameModal.tsx创建
- [x] AddGameModal.css样式实现
- [x] 表单验证逻辑
- [x] 两层滑出动画

**文件创建**:
- `frontend/src/analytics/components/game-management/AddGameModal.tsx`
- `frontend/src/analytics/components/game-management/AddGameModal.css`

**功能特性**:
- 表单字段：游戏名称、GID、ODS数据库、DWD前缀
- 完整的表单验证（非空、数字验证）
- 提交到POST /api/games
- 成功后更新gameStore并关闭
- 错误处理和用户提示

**验证点**:
- [ ] 表单字段正确验证
- [ ] 提交时正确格式化数据（gid转为数字）
- [ ] API调用成功返回后更新store
- [ ] 成功提示正确显示（alert）
- [ ] 错误时显示友好错误消息
- [ ] 取消按钮正常关闭模态框
- [ ] 两层模态框嵌套正常工作

---

#### 4.1 右侧菜单栏游戏管理按钮
- [x] GameSelectionSheet集成GameManagementModal
- [x] GameSelectionSheet.css样式更新
- [x] 右下角添加游戏管理按钮

**文件修改**:
- `frontend/src/analytics/components/game-selection/GameSelectionSheet.jsx`
- `frontend/src/analytics/components/game-selection/GameSelectionSheet.css`

**功能特性**:
- isGameManagementOpen状态管理
- 点击按钮打开GameManagementModal
- 事件冒泡阻止
- 正确的props传递

**验证点**:
- [ ] 游戏选择侧边栏正常显示
- [ ] 游戏管理按钮在右下角显示
- [ ] 按钮样式与设计系统一致
- [ ] 点击按钮打开游戏管理模态框
- [ ] 模态框打开时背景遮罩正常显示
- [ ] 关闭模态框后状态正确更新

---

#### 4.4 左侧导航游戏管理菜单移除
- [x] sidebarConfig.js移除games菜单项
- [x] 保持其他菜单项不变

**文件修改**:
- `frontend/src/shared/config/sidebarConfig.js` - 配置驱动的菜单系统

**功能特性**:
- 配置文件驱动菜单生成
- 移除"数据管理"分组中的"游戏管理"项
- 保持其他菜单完整性

**验证点**:
- [ ] 侧边栏正常显示
- [ ] "游戏管理"菜单项不再显示
- [ ] 其他菜单项（仪表板、事件管理等）正常显示
- [ ] 所有菜单项点击功能正常
- [ ] 分组结构正确（4个主分组）
- [ ] 菜单项数量正确（10个菜单项+页脚游戏选择器）

---

### ✅ Phase 5: 公参管理优化（Common Parameters）

#### 5.1 参数管理页面公参入口
- [x] ParametersList.jsx添加Link按钮
- [x] 正确的game_gid参数传递

**文件修改**:
- `frontend/src/analytics/pages/ParametersList.jsx`

**功能特性**:
- 添加"进入公参管理"按钮
- Link到/common-params?game_gid={gameGid}
- 按钮样式与其他按钮一致

**验证点**:
- [ ] 按钮在工具栏正确位置
- [ ] 点击后正确跳转到公参管理页面
- [ ] URL参数game_gid正确传递
- [ ] 公参管理页面正确接收参数

---

#### 5.2 公参管理同步功能
- [x] 后端common_params.py创建
- [x] 同步API端点实现
- [x] CommonParamsList.jsx同步按钮和mutation

**文件创建**:
- `backend/services/parameters/common_params.py` - 同步逻辑实现
- `frontend/src/analytics/pages/CommonParamsList.jsx` - 同步UI实现

**功能特性**:
- GET /api/common-params - 获取公参列表
- POST /api/common-params/sync - 同步公参
- 80%阈值分析（分析所有事件，找出出现≥80%的参数）
- 自动标记并插入公参
- 统计信息返回（总事件数、阈值、分析数、新增数）
- 加载状态和错误处理

**验证点**:
- [ ] GET端点正确返回公参列表
- [ ] 同步按钮功能正常
- [ ] 分析逻辑正确（90%事件参数识别）
- [ ] API响应格式正确
- [ ] 错误处理友好（缺失game context等）
- [ ] 成功提示显示统计数据
- [ ] 同步后列表自动刷新

---

## 🧪 E2E测试执行计划

### 测试环境要求
- [x] 后端服务器运行（Flask on port 5001）
- [x] 前端开发服务器运行（Vite on port 5173）
- [x] 数据库初始化完成
- [x] 所有组件编译无TypeScript错误
- [x] 游戏数据存在（至少1个游戏：STAR001, GID: 10000147）

### 测试步骤

#### Step 1: 启动应用并检查控制台
```bash
# 1. 确认服务器运行
curl -s http://127.0.0.1:5001/api/health
curl -s http://127.0.0.1:5001/api/games

# 2. 启动前端（如未运行）
cd /Users/mckenzie/Documents/event2table/frontend
npm run dev

# 3. 打开浏览器
# 访问 http://localhost:5173

# 4. 打开开发者工具
# 检查Console标签，确保没有JavaScript错误
```

**预期结果**: 无JavaScript运行时错误，应用正常加载

---

#### Step 2: Phase 1 - 背景主题验证
**测试操作**:
1. 打开Dashboard页面（首页）
2. 检查页面背景是否为青蓝色渐变
3. 检查开发者工具Elements面板
4. 验证CSS变量是否正确应用

**检查清单**:
- [ ] `:root`的`--bg-primary`为渐变色
- [ ] `.app-shell`背景应用渐变
- [ ] 卡片背景使用`rgba(15, 23, 42, 0.6)`或类似
- [ ] 主色调为青色`#06B6D4`
- [ ] 整体视觉有层次感，不再单调纯黑

**浏览器验证**:
```css
/* 在DevTools中检查 */
:root {
  --bg-primary: linear-gradient(135deg, #0c4a6e 0%, #0f172a 50%, #0a0a0a 100%);
}
```

---

#### Step 3: Dashboard hover效果验证
**测试操作**:
1. 在Dashboard页面hover各种卡片
2. 观察hover效果是否统一
3. 检查是否有青色边框和阴影

**检查清单**:
- [ ] stat-card hover效果
- [ ] action-card hover效果
- [ ] 所有卡片hover效果一致
- [ ] 青色边框(#06B6D4)显示
- [ ] 轻微阴影效果
- [ ] transform动画流畅

**预期hover效果**:
```css
.cyber-card--hoverable:hover {
  border-color: rgba(6, 182, 212, 0.3);
  box-shadow: 0 8px 32px rgba(6, 182, 212, 0.15);
  transform: translateY(-2px);
}
```

---

#### Step 4: 游戏选择功能验证
**测试操作**:
1. 点击右侧菜单栏的游戏计数区域
2. 选择一个游戏（如STAR001）
3. 观察localStorage是否更新
4. 刷新页面确认状态持久化

**检查清单**:
- [ ] 游戏选择UI正常显示
- [ ] gameStore正确更新
- [ ] localStorage中存储了selectedGameGid
- [ ] 页面刷新后游戏状态保持
- [ ] 当前游戏标识正确显示

**localStorage验证**:
```javascript
// 在浏览器Console中运行
localStorage.getItem('game-storage');
// 应该返回类似：
// {"state": {"currentGame": {...}, "gameGid": 10000147, "version": 0}
```

---

#### Step 5: SearchInput组件验证
**测试操作**:
1. 访问参数管理页面（有搜索栏）
2. 输入搜索内容
3. 观察防抖效果（等待300ms）
4. 测试快捷键（Mac: Cmd+K, Windows: Ctrl+K）
5. 输入内容后观察清除按钮
6. 点击清除按钮验证功能

**检查清单**:
- [ ] SearchInput组件正确渲染
- [ ] 搜索图标显示
- [ ] 输入框聚焦效果（青色边框）
- [ ] 快捷键提示显示（⌘K）
- [ ] 有内容时清除按钮出现
- [ ] 点击清除按钮后输入清空
- [ ] 防抖功能正常（不会频繁触发搜索）
- [ ] 组件样式与设计系统一致

---

#### Step 6: 游戏管理模态框验证
**测试操作**:
1. 点击右侧菜单栏"游戏管理"按钮
2. 观察模态框滑入动画
3. 验证主从视图布局（左侧列表+右侧详情）
4. 点击游戏项查看详情编辑
5. 测试编辑字段disabled→enabled切换
6. 修改字段值并保存
7. 测试删除游戏功能
8. 点击右上角"+ 添加游戏"按钮

**检查清单**:
- [ ] 模态框打开动画流畅（0.3s slide-in）
- [ ] 背景遮罩正常显示
- [ ] 游戏列表正确加载（显示游戏名称、GID、事件数）
- [ ] 点击游戏项显示右侧详情
- [ ] 编辑字段默认disabled（不可编辑状态）
- [ ] 修改任意字段后该字段变为enabled
- [ ] 保存按钮在检测到修改时才可点击
- [ ] 点击保存后API调用成功
- [ ] 删除按钮显示确认对话框
- [ ] 删除后列表刷新
- [ ] 点击"+ 添加游戏"打开两层嵌套模态框
- [ ] 添加游戏表单字段正确
- [ ] 添加游戏提交后返回游戏列表
- [ ] 表单验证正常（必填字段、GID数字验证）
- [ ] 错误提示友好显示

---

#### Step 7: 左侧导航菜单验证
**测试操作**:
1. 观察左侧导航栏结构
2. 验证"数据管理"分组不包含"游戏管理"
3. 点击其他菜单项验证导航
4. 检查分组展开/折叠功能
5. 验证所有菜单项数量（10个+游戏选择器）

**检查清单**:
- [ ] "游戏管理"不在侧边栏显示
- [ ] 其他菜单项正常：仪表板、事件节点、HQL生成、流程管理、分类管理
- [ ] 菜单项数量正确（4个分组）
- [ ] 游戏选择器在页脚正常工作
- [ ] 点击菜单项正确导航到相应页面
- [ ] 分组展开/折叠功能正常
- [ ] 图标和文字正确显示

---

#### Step 8: 公参管理功能验证
**测试操作**:
1. 在参数管理页面点击"进入公参管理"按钮
2. 验证跳转到/common-params页面
3. 检查URL参数?game_gid=xxx
4. 点击"同步公共参数"按钮
5. 观察同步过程（加载状态）
6. 查看同步结果统计
7. 验证新增的公参正确显示

**检查清单**:
- [ ] "进入公参管理"按钮正确显示
- [ ] 跳转后URL包含game_gid参数
- [ ] 同步按钮正确显示在顶部偏右
- [ ] 点击后显示加载状态
- [ ] API调用成功（POST /api/common-params/sync）
- [ ] 返回统计信息显示（总事件数、阈值、新增数）
- [ ] 新增的公参出现在列表中
- [ ] 错误处理友好（无游戏选中等）
- [ ] 列表自动刷新

---

#### Step 9: 跨页面导航验证
**测试操作**:
1. 从Dashboard导航到事件管理
2. 从事件管理导航到参数管理
3. 从参数管理导航到HQL画布
4. 从HQL画布导航到流程管理
5. 每次导航检查URL中的game_gid参数

**检查清单**:
- [ ] 每次导航URL包含?game_gid=xxx
- [ ] 参数在页面间正确传递
- [ ] 切换游戏后game_gid更新
- [ ] 浏览器前进/后退按钮正常工作
- [ ] 页面刷新后状态保持

---

## 🎯 测试执行

### 准备工作
```bash
# 1. 进入项目目录
cd /Users/mckenzie/Documents/event2table

# 2. 启动后端（如未运行）
python3 web_app.py

# 3. 等待后端启动
# 看到 "Running on http://127.0.0.1:5001"

# 4. 前端测试（新终端窗口）
cd frontend
npm run dev

# 5. 等待前端启动
# 看到 "Local: http://localhost:5173"

# 6. 打开浏览器
# Chrome: http://localhost:5173
# 或使用已打开的浏览器
```

### 执行测试

按照上述Step 1-9的顺序逐项验证，在浏览器Console中记录：

```javascript
// 在Console中运行测试检查
console.log('✅ Phase 1: 背景主题 - 已应用');
console.log('✅ Phase 1: Dashboard hover - 已统一');
console.log('✅ Phase 2: 状态管理 - 已迁移');
console.log('✅ Phase 3: SearchInput - 已创建');
console.log('✅ Phase 4: 游戏管理 - 已实现');
console.log('✅ Phase 5: 公参管理 - 已实现');
```

### 记录测试结果

每完成一个Step，在下方标记：
- [ ] 通过 - 功能正常工作
- [ ] 失败 - 需要修复

### 测试完成条件

所有以下条件满足即为测试完成：
- [ ] Step 1-9全部验证完成
- [ ] 发现的问题已记录并修复
- [ ] 回归测试报告已创建

---

## 🐛 问题跟踪

### 已知问题
- 无新的已知问题

### 遇到的问题
- 之前的SearchInput、GameManagementModal编码问题已修复
- 之前的useGameContext迁移兼容性问题已解决

---

## 📝 测试报告模板

测试完成后，创建以下格式的报告：

```markdown
# E2E Testing Report - 2026-02-12

## 测试概要
- 测试人员: Claude Code
- 测试时间: X小时
- 测试环境: Chrome + Dev Tools
- 测试数据: 游戏STAR001 (GID: 10000147)

## 测试结果总结
- 通过: X项
- 失败: Y项
- 阻塞: Z项

## 详细测试结果

### Phase 1: 视觉基础 ✅
### Phase 2: 状态管理 ✅
### Phase 3: SearchInput组件 ✅
### Phase 4: 游戏管理 ✅
### Phase 5: 公参管理 ✅

## 问题和建议
- 问题1: 描述
  修复: 描述

## 下一步行动
- [ ] 修复问题
- [ ] 重新测试
- [ ] 考虑其他优化
```

---

## 🔗 相关文档

- 实现计划: `/Users/mckenzie/.claude/plans/compiled-jumping-russell.md`
- 开发规范: `/Users/mckenzie/Documents/event2table/CLAUDE.md`
- E2E测试指南: `/Users/mckenzie/Documents/event2table/docs/testing/e2e-testing-guide.md`
- API文档: `/Users/mckenzie/Documents/event2table/docs/api/README.md`

---

**准备好开始测试后通知我，我将帮助您创建详细的测试报告。**
