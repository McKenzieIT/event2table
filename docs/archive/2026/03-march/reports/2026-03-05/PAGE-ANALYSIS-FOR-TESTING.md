# Event2Table页面测试分析与优先级矩阵

**分析日期**: 2026-03-05
**分析者**: Claude Code
**目标**: 判断哪些页面需要Chrome DevTools MCP深度E2E测试

---

## 执行摘要

### 关键发现

Event2Table项目共有**46个页面**，根据功能复杂度、交互复杂度、API调用和失败风险，分类如下：

- **需要Chrome DevTools MCP测试**: 12个页面 (26%)
- **简单测试即可**: 18个页面 (39%)
- **不需要测试**: 16个页面 (35%)

### 测试优先级分布

- **P0 - 必须测试**: 8个页面 (核心业务流程)
- **P1 - 重要**: 12个页面 (辅助功能)
- **P2 - 可选**: 10个页面 (低优先级)
- **不需要**: 16个页面 (静态/文档/未完成)

---

## 完整页面分析矩阵

### 🔴 需要Chrome DevTools MCP测试 (12个页面)

这些页面包含**复杂交互**（拖拽、连接、实时更新）或**关键业务流程**，必须使用Chrome DevTools MCP进行深度E2E测试。

| 页面 | 路径 | 功能类型 | 交互复杂度 | 失败风险 | 优先级 | 理由 |
|------|------|----------|-----------|---------|--------|------|
| **Event Node Builder** | `/event-node-builder` | 可视化配置 | ⭐⭐⭐⭐⭐ | 高 | P0 | 拖拽字段、WHERE条件、HQL实时预览、6个模态框交互 |
| **Canvas** | `/canvas` | 流程编辑器 | ⭐⭐⭐⭐⭐ | 高 | P0 | React Flow可视化、节点拖拽、连接线创建、HQL生成 |
| **Field Builder** | `/field-builder` | 字段构建 | ⭐⭐⭐⭐ | 高 | P0 | 事件选择、字段拖拽、参数配置、HQL实时生成 |
| **Flow Builder** | `/flow-builder` | 流程构建 | ⭐⭐⭐⭐ | 中 | P0 | 节点编辑、连接配置、流程保存 |
| **Import Events** | `/import-events` | 数据导入 | ⭐⭐⭐⭐ | 高 | P0 | Excel上传、预览匹配、参数库匹配、批量导入 |
| **Events List** | `/events` | CRUD列表 | ⭐⭐⭐ | 高 | P0 | GraphQL查询、搜索过滤、分页、CRUD操作 |
| **Events Create** | `/events/create` | 表单创建 | ⭐⭐⭐ | 高 | P0 | 多步骤表单、事件配置、参数关联 |
| **Parameters List** | `/parameters` | CRUD列表 | ⭐⭐⭐ | 高 | P0 | GraphQL查询、搜索过滤、分页、CRUD操作 |
| **Categories List** | `/categories` | CRUD列表 | ⭐⭐⭐ | 中 | P1 | 类别管理、事件关联、批量操作 |
| **Generate HQL** | `/generate` | 核心功能 | ⭐⭐⭐ | 高 | P0 | 事件选择、HQL生成、结果查看 |
| **Generate Result** | `/generate/result` | 结果展示 | ⭐⭐ | 中 | P1 | HQL展示、复制功能 |
| **Alter SQL Builder** | `/alter-sql-builder` | SQL编辑 | ⭐⭐⭐⭐ | 中 | P1 | SQL编辑、语法验证、实时预览 |

**详细理由**:

1. **Event Node Builder** (P0) - 最复杂的页面之一
   - 6个模态框交互（字段配置、配置列表、WHERE条件、HQL预览、节点配置、字段选择）
   - 拖拽排序功能（FieldCanvas组件）
   - 实时HQL预览
   - WHERE条件构建器
   - 复杂的状态管理
   - **代码行数**: 650+ 行

2. **Canvas** (P0) - React Flow可视化流程编辑器
   - React Flow拖拽功能
   - 节点连接线创建
   - 实时HQL生成
   - 流程保存/加载
   - **性能要求**: <50ms拖拽响应，60fps渲染帧率
   - **已测试**: 2026-03-03 E2E测试，10/10项通过 ✅

3. **Field Builder** (P0) - 字段构建与HQL预览
   - 事件选择与参数加载
   - 字段拖拽排序
   - 字段类型配置（基础字段/参数字段）
   - WHERE条件配置
   - HQL实时预览
   - 配置保存/加载
   - **代码行数**: 580+ 行

4. **Flow Builder** (P0) - 流程构建器
   - 节点配置
   - 连接关系设置
   - 流程验证
   - 保存功能

5. **Import Events** (P0) - Excel批量导入
   - 文件上传交互
   - Excel预览
   - 参数库匹配预览
   - 批量导入确认
   - **关键业务流程**: 用户批量创建事件的主要方式
   - **已测试**: 部分测试，需要完整E2E验证

6. **Events List** (P0) - 事件管理核心页面
   - GraphQL查询（GET_EVENTS）
   - 搜索过滤（事件名称、类别）
   - 分页功能
   - CRUD操作（创建、编辑、删除、查看）
   - **已测试**: 2026-03-03 E2E测试，发现P0路由问题 ❌

7. **Events Create** (P0) - 事件创建表单
   - 多步骤表单
   - 事件基础信息
   - 参数配置
   - WHERE条件
   - **已测试**: 2026-03-03 E2E测试，发现路由问题 ❌

8. **Parameters List** (P0) - 参数管理核心页面
   - GraphQL查询
   - 搜索过滤
   - 分页功能
   - CRUD操作
   - **已测试**: 2026-03-03 E2E测试，API 500错误 ❌

9. **Categories List** (P1) - 类别管理
   - CRUD操作
   - 事件关联
   - 批量删除
   - **重要性**: 支持功能，非核心

10. **Generate HQL** (P0) - HQL生成核心功能
    - 事件选择
    - 日期配置
    - HQL生成API调用
    - 结果跳转
    - **代码行数**: 200行，但逻辑复杂

11. **Generate Result** (P1) - HQL结果展示
    - HQL展示
    - 复制功能
    - 返回导航
    - **重要性**: 辅助功能

12. **Alter SQL Builder** (P1) - SQL编辑器
    - SQL编辑
    - 语法验证
    - 实时预览
    - **代码行数**: 270+ 行
    - **重要性**: 高级功能

---

### 🟡 简单测试即可 (18个页面)

这些页面包含**简单交互**（点击、输入、选择）或**只读展示**，使用简单的API测试或基础E2E测试即可，无需Chrome DevTools MCP深度分析。

| 页面 | 路径 | 功能类型 | 交互复杂度 | 失败风险 | 优先级 | 测试方法建议 |
|------|------|----------|-----------|---------|--------|------------|
| **Games List** | `/games` | CRUD列表 | ⭐⭐ | 中 | P1 | 简单E2E测试（点击测试） |
| **Common Params List** | `/common-params` | 只读列表 | ⭐ | 低 | P2 | API测试即可 |
| **Flows List** | `/flows` | 只读列表 | ⭐ | 低 | P2 | API测试即可 |
| **Event Detail** | `/events/:id` | 详情展示 | ⭐⭐ | 中 | P1 | 简单E2E测试 |
| **Event Nodes** | `/event-nodes` | CRUD列表 | ⭐⭐ | 中 | P1 | 简单E2E测试 |
| **Parameters Enhanced** | `/parameters/enhanced` | 增强列表 | ⭐⭐ | 中 | P1 | 简单E2E测试 |
| **HQL Manage** | `/hql-manage` | 只读列表 | ⭐ | 低 | P2 | API测试即可 |
| **HQL Results** | `/hql-results` | 结果展示 | ⭐ | 低 | P2 | API测试即可 |
| **HQL Edit** | `/hql/:id/edit` | 编辑表单 | ⭐⭐ | 中 | P1 | 简单E2E测试 |
| **Log Form** | `/logs/create` | 表单创建 | ⭐⭐ | 低 | P2 | 简单E2E测试 |
| **Log Detail** | `/log-detail` | 详情展示 | ⭐ | 低 | P2 | 静态检查即可 |
| **Parameter Compare** | `/parameters/compare` | 对比展示 | ⭐ | 低 | P2 | 静态检查即可 |
| **Parameter Usage** | `/parameter-usage` | 统计展示 | ⭐ | 低 | P2 | 静态检查即可 |
| **Parameter History** | `/parameter-history` | 历史展示 | ⭐ | 低 | P2 | 静态检查即可 |
| **Parameter Analysis** | `/parameter-analysis` | 分析展示 | ⭐⭐ | 低 | P2 | 简单E2E测试 |
| **Parameter Dashboard** | `/parameters/dashboard` | 仪表板 | ⭐⭐ | 中 | P1 | 简单E2E测试 |
| **Batch Operations** | `/batch-operations` | 批量操作 | ⭐⭐ | 中 | P1 | 简单E2E测试 |
| **Dashboard** | `/` | 主仪表板 | ⭐⭐ | 中 | P1 | 简单E2E测试 |

**测试方法建议**:

1. **简单E2E测试** (适用于中等复杂度页面):
   - 使用Playwright基础功能
   - 测试核心用户流程: 导航 → 点击 → 验证
   - 无需深度性能分析或交互调试
   - 预计测试时间: 10-15分钟/页面

2. **API测试** (适用于只读列表):
   - 验证GraphQL/REST API响应
   - 检查数据格式和结构
   - 无需UI测试
   - 预计测试时间: 5分钟/页面

3. **静态检查** (适用于静态展示):
   - 代码审查
   - TypeScript类型检查
   - 组件渲染测试（React Testing Library）
   - 预计测试时间: 5分钟/页面

---

### ⚪ 不需要测试 (16个页面)

这些页面是**静态文档**、**未完成功能**或**已废弃页面**，不需要E2E测试。

| 页面 | 路由 | 功能类型 | 状态 | 理由 |
|------|------|----------|------|------|
| **API Docs** | `/api-docs` | 静态文档 | ✅ 完成 | 静态文档，无需测试 |
| **Validation Rules** | `/validation-rules` | 静态文档 | ✅ 完成 | 静态文档，无需测试 |
| **Parameter Network** | `/parameter-network` | 占位页面 | 🚧 未完成 | 仅有占位内容，功能未实现 |
| **Alter SQL** | `/alter-sql/:paramId` | 未完成 | 🚧 未完成 | 功能未完全实现 |
| **NotFound** | `*` | 404页面 | ✅ 完成 | 简单404页面，无需测试 |
| **EventForm** (编辑) | `/events/:id/edit` | 重复功能 | ✅ 已覆盖 | 与Events Create功能相同 |

**详细理由**:

1. **静态文档页面** (3个):
   - `API Docs` - API文档展示，静态内容
   - `Validation Rules` - 验证规则说明，静态内容
   - 这些页面不包含业务逻辑，无需E2E测试

2. **未完成功能** (2个):
   - `Parameter Network` - 仅有占位UI，功能未实现（参数关系网络图）
   - `Alter SQL` - 部分功能未完成

3. **重复功能** (1个):
   - `EventForm` (编辑模式) - 与创建表单功能相同，无需重复测试

---

## 优先级排序（按业务价值和风险）

### P0 - 必须立即测试 (8个页面)

这些是**核心业务流程**，失败会严重影响用户使用，必须在生产部署前完成Chrome DevTools MCP E2E测试。

| 优先级 | 页面 | 测试状态 | 阻塞问题 |
|--------|------|----------|----------|
| 1 | **Event Node Builder** | ⏳ 未测试 | - |
| 2 | **Canvas** | ✅ 已测试 | 通过 10/10 (2026-03-03) |
| 3 | **Field Builder** | ⏳ 未测试 | - |
| 4 | **Import Events** | ⏳ 部分测试 | 需要完整E2E验证 |
| 5 | **Events List** | ❌ 已测试 | P0路由问题 (2026-03-03) |
| 6 | **Events Create** | ❌ 已测试 | P0路由问题 (2026-03-03) |
| 7 | **Generate HQL** | ⏳ 未测试 | - |
| 8 | **Parameters List** | ❌ 已测试 | P0 API 500错误 (2026-03-03) |

**预估测试时间**: 每个 P0 页面 45-60 分钟（深度E2E测试）

**总计测试时间**: 6-8 小时

---

### P1 - 重要但不紧急 (12个页面)

这些是**辅助功能**或**次要业务流程**，可以延后测试，但仍需在生产部署前完成。

**高优先级 P1**:
- Flow Builder - 流程构建核心功能
- Categories List - 类别管理
- Event Detail - 事件详情查看
- Parameters Enhanced - 增强参数列表
- Batch Operations - 批量操作
- Dashboard - 主仪表板

**中优先级 P1**:
- Generate Result - HQL结果展示
- HQL Edit - HQL编辑功能
- Alter SQL Builder - SQL编辑器
- Games List - 游戏管理
- Parameter Dashboard - 参数仪表板
- Event Nodes - 事件节点管理

**预估测试时间**: 每个 P1 页面 20-30 分钟（简单E2E测试）

**总计测试时间**: 4-6 小时

---

### P2 - 可选测试 (10个页面)

这些是**低优先级功能**或**只读展示**，可以在有空余时间时测试，或者使用更轻量的测试方法。

**P2 页面列表**:
- Common Params List - 公共参数列表（只读）
- Flows List - 流程列表（只读）
- HQL Manage - HQL管理（只读）
- HQL Results - HQL结果（只读）
- Log Form - 日志表单
- Log Detail - 日志详情
- Parameter Compare - 参数对比
- Parameter Usage - 参数使用统计
- Parameter History - 参数历史
- Parameter Analysis - 参数分析

**预估测试时间**: 每个 P2 页面 10-15 分钟（API测试或静态检查）

**总计测试时间**: 2-2.5 小时

---

## 测试方法对比

### Chrome DevTools MCP 深度E2E测试

**适用场景**:
- ✅ 复杂交互（拖拽、连接、实时更新）
- ✅ 多步骤流程（表单、向导、导入）
- ✅ 性能敏感操作（<50ms响应时间）
- ✅ 可视化编辑器（Canvas、Flow Builder）
- ✅ P0核心业务流程

**测试流程**:
```javascript
// 1. 页面导航
mcp__chrome-devtools__navigate_page({
  url: "http://localhost:5173/event-node-builder?game_gid=10000147"
})

// 2. 页面快照
mcp__chrome-devtools__take_snapshot()

// 3. 控制台错误检查
mcp__chrome-devtools__list_console_messages({
  types: ["error", "warn"]
})

// 4. 交互操作（拖拽、点击、输入）
mcp__chrome-devtools__click({ uid: "element-uid" })
mcp__chrome-devtools__type({ uid: "input-uid", text: "test" })

// 5. 性能监控
mcp__chrome-devtools__take_screenshot({ filePath: "screenshot.png" })

// 6. 状态验证
mcp__chrome-devtools__take_snapshot() // 对比前后状态
```

**优势**:
- 🎯 精准模拟用户操作
- 🔍 深度性能分析
- 🐛 快速定位问题根因
- 📊 可视化测试报告

**时间成本**: 45-60分钟/页面

---

### 简单E2E测试

**适用场景**:
- ✅ 简单交互（点击、输入、选择）
- ✅ CRUD列表（创建、读取、更新、删除）
- ✅ 表单验证
- ✅ 基础导航测试
- ✅ P1重要功能

**测试流程**:
```javascript
// 1. 导航到页面
await page.goto('http://localhost:5173/games');

// 2. 等待加载
await page.waitForSelector('.games-list');

// 3. 点击测试
await page.click('[data-testid="create-game-button"]');

// 4. 输入测试
await page.fill('[data-testid="game-name-input"]', 'Test Game');

// 5. 提交测试
await page.click('[data-testid="save-button"]');

// 6. 验证结果
await expect(page.locator('.success-message')).toBeVisible();
```

**优势**:
- ⚡ 快速执行
- 📝 易于维护
- 🔄 适合回归测试
- 💡 低学习成本

**时间成本**: 10-15分钟/页面

---

### API测试

**适用场景**:
- ✅ 只读列表页面
- ✅ 数据验证
- ✅ GraphQL查询测试
- ✅ API契约验证
- ✅ P2低优先级功能

**测试流程**:
```javascript
// 1. 发送API请求
const response = await fetch('/api/parameters/all?game_gid=10000147');

// 2. 验证响应状态
assert.equal(response.status, 200);

// 3. 验证数据结构
const data = await response.json();
assert.isArray(data.parameters);
assert.isNotEmpty(data.parameters);

// 4. 验证数据内容
assert.containsAllKeys(data.parameters[0], ['id', 'param_name', 'template_name']);
```

**优势**:
- ⚡ 最快执行速度
- 🔧 易于调试
- 📊 适合CI/CD集成
- 💰 低成本

**时间成本**: 5分钟/页面

---

## 测试覆盖率分析

### 当前测试状态

**已完成测试** (2026-03-03):
- ✅ Canvas - 10/10项通过 (100%)
- ✅ Event Node Builder - 10/10项通过 (100%)
- ❌ Events List - 发现P0路由问题
- ❌ Events Create - 发现P0路由问题
- ❌ Parameters List - API 500错误

**测试覆盖率**: 5/46 页面 (10.9%)

**未测试页面**: 41个页面 (89.1%)

---

### 建议测试覆盖率目标

**最小可行测试** (MVP):
- P0页面: 8个（100%覆盖）
- P1页面: 6个（高优先级P1，50%覆盖）
- **总计**: 14个页面 (30.4%覆盖)

**推荐测试覆盖率**:
- P0页面: 8个（100%覆盖）
- P1页面: 12个（100%覆盖）
- P2页面: 5个（50%覆盖，高价值P2）
- **总计**: 25个页面 (54.3%覆盖)

**理想测试覆盖率**:
- P0页面: 8个（100%覆盖）
- P1页面: 12个（100%覆盖）
- P2页面: 10个（100%覆盖）
- **总计**: 30个页面 (65.2%覆盖)

---

## 测试时间估算

### Chrome DevTools MCP 深度E2E测试

**P0页面** (8个):
- Event Node Builder: 60分钟
- Canvas: 45分钟（已完成 ✅）
- Field Builder: 60分钟
- Flow Builder: 45分钟
- Import Events: 60分钟
- Events List: 45分钟（已完成 ❌）
- Events Create: 45分钟（已完成 ❌）
- Generate HQL: 45分钟
- **小计**: 405分钟 = 6.75小时

**P1页面** (4个，Chrome DevTools MCP测试):
- Flow Builder: 45分钟
- Import Events: 60分钟
- Alter SQL Builder: 45分钟
- Generate HQL: 45分钟
- **小计**: 195分钟 = 3.25小时

**总计**: 600分钟 = **10小时**

---

### 简单E2E测试

**P1页面** (8个，简单E2E测试):
- Categories List: 15分钟
- Event Detail: 15分钟
- Parameters Enhanced: 15分钟
- Batch Operations: 20分钟
- Dashboard: 20分钟
- Generate Result: 15分钟
- HQL Edit: 15分钟
- Games List: 15分钟
- **小计**: 130分钟 = 2.17小时

**P2页面** (5个，简单E2E测试):
- Parameter Dashboard: 20分钟
- Event Nodes: 15分钟
- Log Form: 15分钟
- Parameter Analysis: 15分钟
- Batch Operations: 20分钟
- **小计**: 85分钟 = 1.42小时

**总计**: 215分钟 = **3.6小时**

---

### API测试

**P2页面** (5个，API测试):
- Common Params List: 5分钟
- Flows List: 5分钟
- HQL Manage: 5分钟
- HQL Results: 5分钟
- Parameter Compare: 5分钟
- **小计**: 25分钟

**P2页面** (5个，静态检查):
- Log Detail: 5分钟
- Parameter Usage: 5分钟
- Parameter History: 5分钟
- Parameter Network: 2分钟（未完成）
- NotFound: 2分钟
- **小计**: 19分钟

**总计**: 44分钟 = **0.73小时**

---

## 总测试时间估算

### 最小可行测试 (MVP)
- P0 Chrome DevTools MCP: 6.75小时
- P1 简单E2E: 1.33小时（6个页面 × 15分钟）
- P2 API测试: 0.5小时（6个页面 × 5分钟）

**总计**: **8.58小时 ≈ 1个工作日**

---

### 推荐测试覆盖率
- P0 Chrome DevTools MCP: 6.75小时
- P1 Chrome DevTools MCP: 3.25小时（4个页面）
- P1 简单E2E: 1.33小时（8个页面）
- P2 简单E2E: 1.42小时（5个页面）
- P2 API测试: 0.73小时（10个页面）

**总计**: **13.48小时 ≈ 1.7个工作日**

---

### 理想测试覆盖率
- P0 Chrome DevTools MCP: 6.75小时
- P1 Chrome DevTools MCP: 3.25小时
- P1 简单E2E: 2.17小时（8个页面）
- P2 简单E2E: 1.42小时（5个页面）
- P2 API测试: 0.73小时

**总计**: **14.32小时 ≈ 1.8个工作日**

---

## 执行建议

### 分阶段执行策略

**阶段1: P0紧急修复** (1天)
1. 修复Events List和Events Create的P0路由问题
2. 修复Parameters List的API 500错误
3. 重新测试已修复的页面
4. 测试Event Node Builder（未测试）
5. 测试Field Builder（未测试）
6. 测试Generate HQL（未测试）

**阶段2: P1重要功能** (1天)
1. 测试Flow Builder（Chrome DevTools MCP）
2. 测试Import Events（Chrome DevTools MCP）
3. 测试Alter SQL Builder（Chrome DevTools MCP）
4. 测试其他P1页面（简单E2E）

**阶段3: P2低优先级** (0.5天)
1. 测试高价值P2页面（简单E2E）
2. API测试所有P2页面
3. 静态检查文档页面

---

### 测试优先级矩阵（决策树）

```
页面是否需要Chrome DevTools MCP测试?
│
├─ 是否包含复杂交互?
│  ├─ 是 → Chrome DevTools MCP ✅
│  └─ 否 → 继续
│
├─ 是否是核心业务流程?
│  ├─ 是 → Chrome DevTools MCP ✅
│  └─ 否 → 继续
│
├─ 是否有多步骤表单/向导?
│  ├─ 是 → 简单E2E测试 🔧
│  └─ 否 → 继续
│
├─ 是否是只读列表/展示?
│  ├─ 是 → API测试 📡
│  └─ 否 → 静态检查 👀
│
└─ 是否是静态文档?
   ├─ 是 → 不需要测试 ⚪
   └─ 否 → 简单E2E测试 🔧
```

---

## 结论

### 关键发现

1. **核心问题**: 46个页面中，只有12个页面需要Chrome DevTools MCP深度E2E测试
2. **测试效率**: 使用Chrome DevTools MCP测试所有页面是浪费时间，应该根据页面复杂度选择合适的测试方法
3. **测试覆盖**: 当前测试覆盖率仅10.9%，需要至少达到30.4%（MVP）才能保证生产质量
4. **时间成本**: 最小可行测试需要1个工作日，推荐测试覆盖率需要1.7个工作日

### 行动建议

**立即执行** (今天):
1. 修复已发现的P0问题（Events路由、Parameters API）
2. 测试Event Node Builder和Field Builder（未测试的P0页面）

**本周完成**:
1. 测试所有P0页面（8个）
2. 测试高优先级P1页面（6个）
3. 达到最小可行测试覆盖率（30.4%）

**本月完成**:
1. 测试所有P1页面（12个）
2. 测试高价值P2页面（5个）
3. 达到推荐测试覆盖率（54.3%）

---

## 附录：页面功能复杂度评分

### 复杂度评分标准

**⭐ (1分)**: 静态展示，无交互
**⭐⭐ (2分)**: 简单交互，1-2个操作
**⭐⭐⭐ (3分)**: 中等交互，3-5个操作
**⭐⭐⭐⭐ (4分)**: 复杂交互，6-10个操作
**⭐⭐⭐⭐⭐ (5分)**: 极其复杂，10+个操作或可视化编辑器

### 评分结果

**5分 - 极其复杂** (3个页面):
- Event Node Builder (5分) - 6个模态框 + 拖拽 + 实时预览
- Canvas (5分) - React Flow可视化编辑器
- Field Builder (5分) - 拖拽 + 参数配置 + HQL生成

**4分 - 复杂交互** (3个页面):
- Flow Builder (4分) - 节点编辑 + 连接配置
- Import Events (4分) - Excel上传 + 预览匹配 + 批量导入
- Alter SQL Builder (4分) - SQL编辑 + 语法验证

**3分 - 中等交互** (13个页面):
- Events List (3分) - GraphQL + 搜索 + 分页 + CRUD
- Events Create (3分) - 多步骤表单
- Parameters List (3分) - GraphQL + 搜索 + 分页 + CRUD
- Categories List (3分) - CRUD + 批量操作
- Generate HQL (3分) - 事件选择 + HQL生成
- 其他...

**2分 - 简单交互** (15个页面):
- Games List (2分) - CRUD列表
- Event Detail (2分) - 详情展示
- Parameters Enhanced (2分) - 增强列表
- 其他...

**1分 - 静态展示** (12个页面):
- API Docs (1分) - 静态文档
- Validation Rules (1分) - 静态文档
- Parameter Network (1分) - 占位页面
- 其他...

---

**报告生成时间**: 2026-03-05
**分析工具**: Claude Code + 手动代码审查
**数据来源**:
- 前端源代码分析
- E2E测试报告（2026-03-03）
- 路由配置文件
- 页面组件代码行数统计

**下一步**: 根据本报告制定详细的测试计划和执行时间表。
