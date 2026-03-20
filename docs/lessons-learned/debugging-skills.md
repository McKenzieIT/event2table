# 调试技能

> **来源**: 整合了E2E测试和Subagent分析的调试经验
> **最后更新**: 2026-03-04（新增前端加载问题调试模式）
> **维护**: 每次调试问题后立即更新

---

## Chrome DevTools MCP调试法 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 2次 | **来源**: [E2E测试报告](../archive/2026-02/testing-reports/)

### 标准调试流程

**步骤1: 列出所有页面**
```javascript
mcp__chrome-devtools__list_pages()
```

**步骤2: 导航到测试页面**
```javascript
mcp__chrome-devtools__navigate_page({
  type: "url",
  url: "http://localhost:5173/parameter-dashboard?game_gid=10000147"
})
```

**步骤3: 获取页面快照**
```javascript
mcp__chrome-devtools__take_snapshot()
```

**步骤4: 检查控制台错误**
```javascript
mcp__chrome-devtools__list_console_messages({
  types: ["error", "warn"]
})
```

**步骤5: 截图记录**
```javascript
mcp__chrome-devtools__take_screenshot({
  filePath: "docs/reports/2026-02-23/bug-screenshot.png",
  fullPage: true
})
```

**步骤6: 点击交互元素**
```javascript
mcp__chrome-devtools__click({ uid: "clickable-element-uid" })
```

### 错误检测模式

**React Hooks错误**:
```
[error] React has detected a change in the order of Hooks called
[error] Uncaught Error: Rendered more hooks than during the previous render
```

**加载超时错误**:
```
页面状态：卡在"LOADING EVENT2TABLE..."超过30秒
控制台：无错误信息（但也不显示任何内容）
```

**API错误**:
```
[error] Failed to load resource: 400 (BAD REQUEST)
```

### 使用场景

**适用场景**:
- ✅ 探索性测试 - 快速验证假设
- ✅ 根因分析 - 深入理解问题
- ✅ 交互式调试 - 实时查看状态
- ✅ 截图记录 - 保存问题现场

**不适用场景**:
- ❌ 回归测试 - 应该使用Playwright
- ❌ 批量测试 - 应该使用自动化测试工具
- ❌ CI/CD集成 - 应该使用无头浏览器

### 2026-03-04 新增：前端加载问题调试模式 ⭐ **P0重要**

**问题现象**：
- 页面卡在 "Loading Event2Table..." 状态超过30秒
- 控制台显示模块导入错误
- CORS 错误阻止 GraphQL 请求
- React 应用无法完全挂载

### 错误检测模式

**Apollo Provider 导入错误**:
```
❌ Uncaught SyntaxError: The requested module
   '/node_modules/.vite/deps/@apollo_client.js?v=1744da38'
   does not provide an export named 'ApolloProvider'

❌ 错误根因：从 @apollo/client 导入 React 组件
   ✅ 修复：从 @apollo/client/react 导入
```

**CORS 策略阻止错误**:
```
❌ Access to fetch at 'http://127.0.0.1:5001/api/graphql' from origin 'http://localhost:5173'
   has been blocked by CORS policy: Response to preflight request doesn't pass access control check:
   No 'Access-Control-Allow-Origin' header is present on the requested resource.

❌ 错误根因：Flask 未配置 CORS
   ✅ 修复：添加 Flask-CORS 配置
```

**双重错误链分析**:
```
Layer 1: 代码层 - Apollo 导入路径错误
Layer 2: 配置层 - CORS 未配置
结果：页面卡住，无法加载
```

### 6步前端加载调试流程

**步骤1: 确认服务器状态**
```javascript
// 列出所有页面，确认前后端服务器运行
mcp__chrome-devtools__list_pages()
// 预期：应有前端和后端服务器页面
```

**步骤2: 导航到问题页面**
```javascript
mcp__chrome-devtools__navigate_page({
  type: "url",
  url: "http://localhost:5173"
})
// 预期：应显示 "Loading Event2Table..."
```

**步骤3: 获取页面快照**
```javascript
mcp__chrome-devtools__take_snapshot()
// 重点检查：
// - 是否卡在加载状态
// - 页面内容是否完整
// - 导航菜单是否显示
```

**步骤4: 检查控制台错误**
```javascript
mcp__chrome-devtools__list_console_messages({
  types: ["error", "warn"]
})
// 查找关键错误：
// - Apollo Provider 导入错误
// - CORS 错误
// - 模块解析失败
```

**步骤5: 分析错误链**
```javascript
// 错误链分析示例
// 错误1：Apollo Provider 模块不存在
// 错误2：CORS 策略阻止请求
// 根本原因：导入路径错误 + CORS 未配置
```

**步骤6: 验证修复效果**
```javascript
// 修复后重新测试
mcp__chrome-devtools__navigate_page({ type: "reload" })
mcp__chrome-devtools__take_snapshot()

// 成功标志：
// ✅ 页面标题正常显示
// ✅ 导航菜单完整
// ✅ 游戏列表正常
// ✅ 无控制台错误
```

### 相关经验

- [测试指南 - E2E测试](./testing-guide.md#e2e测试) - E2E测试方法论
- [React最佳实践 - Hooks规则](./react-best-practices.md#react-hooks-规则) - React Hooks调试

---

## Subagent并行分析法 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [测试指南 - E2E测试](./testing-guide.md#e2e测试)

### 根因分析策略

**步骤1: 识别问题模式**
- 问题是孤立事件还是重复模式？
- 多个页面有相同症状？

**步骤2: 并行深度分析**
```javascript
// 启动2个并行subagent
Task(subagent_type="general-purpose", prompt="分析React Hooks错误根因")
Task(subagent_type="general-purpose", prompt="分析加载超时模式")
```

**步骤3: 综合分析结果**
- 对比两个subagent的发现
- 识别共同点和差异
- 确定根本原因

**步骤4: 设计修复方案**
- 基于根因分析，而非症状
- 考虑长期预防措施
- 避免表面修复

### Subagent使用原则

**何时使用Subagent**:
- ✅ 复杂问题需要深度分析
- ✅ 需要探索多个假设
- ✅ 需要代码审查和模式识别
- ❌ 简单的显而易见的问题

**并行vs顺序**:
- **并行**: 多个独立分析任务（如分析不同方面的根因）
- **顺序**: 依赖前一个分析结果的任务

### Canvas组件调试 ⭐ (2026-03-04新增)

**优先级**: P0 | **出现次数**: 1次 | **来源**: [CANVAS-EVENT-NODES-FIX-GUIDE.md](../archive/2026/03-march/temp-guides/CANVAS-EVENT-NODES-FIX-GUIDE.md)

### 事件节点配置问题诊断

**常见症状**:
- ✅ 路由配置问题：直接访问URL显示首页或错误页面
- ✅ API连接失败：显示"加载参数失败: INTERNAL SERVER ERROR"
- ✅ 面包屑导航错误：显示不正确的页面标题
- ✅ 游戏上下文缺失：页面不显示当前游戏GID

**三步诊断法**:

#### 第1步：确认基础设施状态
```bash
# 1. 检查服务器运行状态
curl http://127.0.0.1:5001/api/health

# 2. 检查API端点可用性
curl "http://127.0.0.1:5001/api/parameters?game_gid=10000147"
curl "http://127.0.0.1:5001/api/events?game_gid=10000147"

# 3. 检查数据库连接
sqlite3 data/dwd_generator.db "SELECT COUNT(*) FROM games;"
```

#### 第2步：使用Chrome DevTools MCP深度分析
```javascript
// 1. 导航到问题页面
mcp__chrome-devtools__navigate_page({
  type: "url",
  url: "http://localhost:5173/event-node-builder?game_gid=10000147"
})

// 2. 获取页面快照，查看错误状态
mcp__chrome-devtools__take_snapshot()

// 3. 检查控制台错误
mcp__chrome-devtools__list_console_messages({
  types: ["error", "warn"]
})

// 4. 截图记录问题
mcp__chrome-devtools__take_screenshot({
  filePath: "debug/canvas-node-builder-error.png",
  fullPage: true
})
```

#### 第3步：并行Subagent分析策略
```javascript
// 启动2个并行subagent进行深度分析
Task(subagent_type="general-purpose", prompt="分析Canvas路由配置问题")
Task(subagent_type="general-purpose", prompt="分析React组件懒加载问题")

// 综合分析结果，识别根本原因
// - 路由参数处理缺失
// - 组件导入路径错误
// - Suspense配置不当
```

### 前后端集成验证

**4步验证流程**:

#### 步骤1：路由配置验证
```typescript
// ✅ 正确的路由配置示例
const routes = (
  <BrowserRouter>
    <Routes>
      <Route
        path="/event-node-builder"
        element={
          <Suspense fallback={<Loading />}>
            <EventNodeBuilder />
          </Suspense>
        }
      />
      <Route
        path="/canvas"
        element={
          <Suspense fallback={<Loading />}>
            <Canvas />
          </Suspense>
        }
      />
    </Routes>
  </BrowserRouter>
)
```

#### 步骤2：API连接验证
```bash
# 验证所有Canvas相关API
curl -w "\nStatus: %{http_code}\n" \
  "http://127.0.0.1:5001/api/parameters?game_gid=10000147"
curl -w "\nStatus: %{http_code}\n" \
  "http://127.0.0.1:5001/api/events?game_gid=10000147"
curl -w "\nStatus: %{http_code}\n" \
  "http://127.0.0.1:5001/api/event-nodes?game_gid=10000147"
```

#### 步骤3：组件渲染验证
```typescript
// ✅ 正确的组件参数处理
function EventNodeBuilder() {
  const [searchParams] = useSearchParams();
  const gameGid = searchParams.get('game_gid');

  // 验证必需参数
  if (!gameGid) {
    return <Navigate to="/" />;
  }

  // 使用参数获取数据
  useEffect(() => {
    fetchParameters(gameGid);
  }, [gameGid]);

  return <div>Event Node Builder</div>;
}
```

#### 步骤4：用户体验验证
```typescript
// ✅ 动态面包屑配置
const breadcrumbMap = {
  '/event-node-builder': [
    { label: '首页', path: '/' },
    { label: '事件节点构建器', path: '/event-node-builder' }
  ],
  '/canvas': [
    { label: '首页', path: '/' },
    { label: 'HQL画布', path: '/canvas' }
  ]
};

// ✅ 游戏上下文显示
function GameContextBar() {
  const [searchParams] = useSearchParams();
  const gameGid = searchParams.get('game_gid');

  return (
    <div className="game-context">
      当前游戏: {gameName} (GID: {gameGid})
    </div>
  );
}
```

### 调试工具集成

**Canvas专用调试组合**:
1. **Chrome DevTools MCP** - 页面导航和交互测试
2. **Subagent并行分析** - 根因深度分析
3. **curl API测试** - 后端接口验证
4. **路由配置检查** - React Router诊断

### 预防措施

**开发阶段的预防**:
- ✅ 所有路由必须支持 `game_gid` 参数
- ✅ 使用动态面包屑而非硬编码
- ✅ 在关键页面添加游戏上下文显示
- ✅ 实现 Error Boundary 捕获组件错误
- ✅ 配置适当的 Suspense fallback

**部署前的检查清单**:
- [ ] 直接访问所有Canvas相关URL
- [ ] 验证API端点响应
- [ ] 检查面包屑导航正确性
- [ ] 确认游戏上下文显示
- [ ] 测试错误处理机制

### 相关经验

- [测试指南 - Ralph Loop迭代测试法](./testing-guide.md#ralph-loop迭代测试法) - 完整的测试流程
- [重构检查清单 - Brainstorming](./refactoring-checklist.md#brainstorming) - 系统化问题解决

---

## 调试工具箱

### Chrome DevTools

**常用功能**:
- **Elements**: 检查DOM结构和样式
- **Console**: 查看日志和错误
- **Network**: 监控网络请求
- **Sources**: 调试JavaScript代码
- **Performance**: 分析性能瓶颈

**快捷键**:
- `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows) - 打开DevTools
- `Cmd+Option+C` (Mac) / `Ctrl+Shift+C` (Windows) - 检查元素
- `Cmd+Option+J` (Mac) / `Ctrl+Shift+J` (Windows) - 打开Console

### React DevTools

**安装**:
```bash
npm install --save-dev react-devtools
```

**使用**:
- **Components**: 查看React组件树
- **Profiler**: 分析React性能
- **Hooks**: 查看Hooks状态

### Playwright Inspector

**启动**:
```bash
npx playwright test --ui
```

**使用**:
- **Time Travel**: 查看测试每一步
- **Network**: 监控网络请求
- **Console**: 查看控制台输出
- **Snapshots**: 查看页面快照

---

## 并行开发策略 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 多次 | **来源**: 多个Phase报告

### 核心概念

**使用多个subagents并行处理，效率提升3-4倍**

### 并行模式

**任务分解**:
```
Phase 1: 紧急修复 (subagent A)
Phase 2: Service重构 (subagent B)
Phase 3: 模块迁移 (subagent C)
Phase 4: 全面清理 (subagent D)

同时进行 → 总体时间减少3-4倍
```

### 实施策略

**1. 任务分解原则**:
- 每个任务必须独立（无共享状态）
- 每个任务有明确的输入和输出
- 每个任务可独立验证

**2. 并行执行示例**:
```python
# 启动2个并行subagent
Task(subagent_type="general-purpose", prompt="分析React Hooks错误根因")
Task(subagent_type="general-purpose", prompt="分析加载超时模式")

# 同时进行，效率提升
```

**3. 集成测试**:
```bash
# 每个Phase完成后立即测试
pytest backend/test/unit/  # 单元测试
pytest backend/test/integration/  # 集成测试
npm run test:e2e  # E2E测试
```

### 性能数据

**Event2Table项目实际数据**:
- Phase 1-4并行开发：~4小时
- 如果串行开发：~12-16小时
- **效率提升：3-4倍**

### 代码审查清单

- [ ] 任务是否可独立执行？
- [ ] 是否有明确的输入和输出？
- [ ] 是否避免了共享状态？
- [ ] 每个任务完成后是否立即测试？

### 案例文档

- [后端架构优化报告](../archive/testing-reports/2026-03-01/2026-03-01/FINAL-ARCHITECTURE-OPTIMIZATION-REPORT.md)

---

### 相关经验

- [性能模式 - 数据库索引](./performance-patterns.md#数据库索引) - 性能分析工具
- [测试指南 - 测试工具选择](./testing-guide.md#测试工具选择) - 测试工具对比

### 来自 docs/cache/operations/monitoring.md (2026-03-18)

**关键主题**:
- 缓存系统监控和告警文档
- 📊 监控体系概览
- 三级监控架构
- 核心监控组件
- 🎯 核心监控指标

**重要经验**:
- logger.warning(f"⚠️ L2缓存读取失败: {e}")
- | **DEBUG** | 详细的缓存操作日志 | `✅ L1 HIT: dwd_gen:v3:events.list:game_id:1` |
- | **INFO** | 正常操作记录 | `✅ 缓存告警管理器初始化完成` |
- | **CRITICAL** | 严重问题 | `❌ L1缓存扩容失败: ...` |
- | **ERROR** | 错误异常 | `❌ 告警动作执行失败: ...` |


### 来自 docs/development/MIGRATION-GUIDE.md (2026-03-18)

**关键主题**:
- Event2Table 架构迁移指南
- 目录
- 1. 迁移概述
- 为什么迁移?
- 迁移收益

**重要经验**:
- | DDD代码清理 | **✅ 完成** (17个文件, 4132行) |
- - ✅ **精简分层架构**: API → Service → Repository → Entity
- - ✅ **统一Entity模型**: 单一真相来源,不可能不一致
- - ✅ **Pydantic v2**: 自动验证、类型安全、IDE支持
- - ✅ **Repository返回Entity**: 类型明确,自动验证


### 来自 docs/cache/operations/monitoring.md (2026-03-18)

**关键主题**:
- 缓存系统监控和告警文档
- 📊 监控体系概览
- 三级监控架构
- 核心监控组件
- 🎯 核心监控指标

**重要经验**:
- logger.warning(f"⚠️ L2缓存读取失败: {e}")
- | **DEBUG** | 详细的缓存操作日志 | `✅ L1 HIT: dwd_gen:v3:events.list:game_id:1` |
- | **INFO** | 正常操作记录 | `✅ 缓存告警管理器初始化完成` |
- | **CRITICAL** | 严重问题 | `❌ L1缓存扩容失败: ...` |
- | **ERROR** | 错误异常 | `❌ 告警动作执行失败: ...` |


### 来自 docs/plans/2026-03-06-PHASE-3-AGENT-QUICK-REFERENCE.md (2026-03-18)

**关键主题**:
- Phase 3 Agent Quick Reference Guide
- 🎯 Agent任务清单
- Agent 9: P0 表单输入组件（8个）
- 1. TypeScript类型检查
- 2. ESLint检查

**重要经验**:
- 1. ✅ `TextArea/TextArea.tsx`
- 2. ✅ `Select/Select.tsx`
- 3. ✅ `Checkbox/Checkbox.tsx`
- 4. ✅ `Switch/Switch.tsx`
- 5. ✅ `Radio/Radio.tsx`


### 来自 docs/development/MIGRATION-GUIDE.md (2026-03-18)

**关键主题**:
- Event2Table 架构迁移指南
- 目录
- 1. 迁移概述
- 为什么迁移?
- 迁移收益

**重要经验**:
- | DDD代码清理 | **✅ 完成** (17个文件, 4132行) |
- - ✅ **精简分层架构**: API → Service → Repository → Entity
- - ✅ **统一Entity模型**: 单一真相来源,不可能不一致
- - ✅ **Pydantic v2**: 自动验证、类型安全、IDE支持
- - ✅ **Repository返回Entity**: 类型明确,自动验证


### 来自 docs/hql/README.md (2026-03-18)

**关键主题**:
- HQL生成器文档
- 概述
- 文档索引
- 安全文档
- 架构文档

**重要经验**:
- - 操作符白名单的重要性
- -- ✅ HQL允许的占位符（调度系统替换）
- -- ❌ HIVE不支持参数化（Hive不支持）
- **关键区别**:
- # ✅ 正确：使用白名单


### 来自 docs/reports/2026-03-18/CLAUDE-MD-CONTENT-VERIFICATION.md (2026-03-18)

**关键主题**:
- CLAUDE.md 内容验证报告
- 📊 精简数据对比
- ✅ 完全保留的核心内容
- 1. **Critical Rules（P0强制执行规则）** - 100%保留
- 2. **快速开始指南** - 100%保留

**重要经验**:
- | **Critical Rules** | 10个（详细版） | 10个（简化版） | ✅ 保留 |
- | **经验文档链接** | 17个（重复列表） | 8个（核心列表） | ✅ 优化 |
- ## ✅ 完全保留的核心内容
- 1. ✅ STAR001 游戏保护规则
- 2. ✅ 完整实现原则


### 来自 docs/README.md (2026-03-19)

**关键主题**:
- Event2Table 文档中心
- 📚 快速导航
- 新用户入门
- 核心开发文档
- 经验文档系统 ⭐

**重要经验**:
- **正确示例** ✅:
- **错误示例** ❌:
- 1. ✅ 更新API文档（如果修改了API）
- 2. ✅ 更新架构文档（如果修改了架构）
- 3. ✅ 提取经验到经验文档


### 来自 docs/ci-cd/QUICKSTART.md (2026-03-19)

**关键主题**:
- CI/CD Quick Start Guide
- Quick Reference
- Run Tests Locally
- Backend tests
- Frontend tests

**重要经验**:
- - ✅ Tests must pass before merge
- - ✅ Auto-deploy only on main branch
- - ✅ Auto-rollback on failure
- - ✅ Monitor after deployment


### 来自 docs/README.md (2026-03-20)

**关键主题**:
- Event2Table 文档中心
- 📚 快速导航
- 新用户入门
- 核心开发文档
- 经验文档系统 ⭐

**重要经验**:
- **正确示例** ✅:
- **错误示例** ❌:
- 1. ✅ 更新API文档（如果修改了API）
- 2. ✅ 更新架构文档（如果修改了架构）
- 3. ✅ 提取经验到经验文档


### 来自 docs/ci-cd/QUICKSTART.md (2026-03-20)

**关键主题**:
- CI/CD Quick Start Guide
- Quick Reference
- Run Tests Locally
- Backend tests
- Frontend tests

**重要经验**:
- - ✅ Tests must pass before merge
- - ✅ Auto-deploy only on main branch
- - ✅ Auto-rollback on failure
- - ✅ Monitor after deployment


### 来自 docs/reports/2026-03/GAMES-MODULE-MIGRATION-REPORT.md (2026-03-20)

**关键主题**:
- Games Module Entity Architecture Migration - Final Report
- Executive Summary
- Migration Status
- ✅ Repository Layer (backend/models/repositories/games.py)
- Query methods (all return GameEntity)

**重要经验**:
- **Status**: ✅ **COMPLETE** - All validation standards met
- ### ✅ Repository Layer (backend/models/repositories/games.py)
- - ✅ All methods return `GameEntity` objects (not Dict)
- - ✅ Uses `@cached` decorator on query methods (30min TTL)
- - ✅ Type-safe operations with Pydantic Entity validation


### 来自 docs/reports/2026-03/BUG-FIX-REPORT-2026-03-14.md (2026-03-20)

**关键主题**:
- Event Node Builder Bug修复报告
- 执行摘要
- 修复结果
- 测试覆盖
- Bug #1: 重复React键导致组件崩溃（P0）

**重要经验**:
- **修复状态**: ✅ 所有Bug已修复并验证
- | #1 | P0 | 重复React键导致组件崩溃 | ✅ 已修复 | ✅ 验证成功 |
- | #2-3 | P0 | FieldConfigModal交互问题 | ✅ 已修复 | ✅ 验证成功 |
- | #4 | P1 | 删除确认显示错误字段名 | ✅ 已修复 | ✅ 验证成功 |
- - ✅ **39个字段成功添加**（32参数 + 7基础）

