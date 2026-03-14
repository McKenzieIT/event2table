# 测试指南

> **来源**: 整合了9个文档的测试相关经验
> **最后更新**: 2026-03-04 ✨ 新增E2E测试完整流程章节
> **维护**: 每次测试相关问题修复后立即更新

---

## E2E测试方法论 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 2次 | **来源**: [TESTING_LESSONS_LEARNED.md](../archive/2026-02/testing/TESTING_LESSONS_LEARNED.md), [phase2-lessons-learned.md](../archive/2026-02/testing/phase2-lessons-learned.md), [FINAL-REPORT](../archive/ralph-testing/ralph/FINAL-REPORT.md)

### 核心测试哲学

**从浅层到深度的转变**:
- ❌ **旧方法**：页面加载测试（20%深度）
- ✅ **新方法**：用户工作流测试（60%深度）

**测试深度比例**:
- 页面加载测试：20%
- 用户交互测试：60%
- 工作流完成测试：20%

### Ralph Loop迭代测试法

**测试流程**:
```
发现问题 → Subagent深度分析 → 设计修复方案 → 实施修复 → Chrome MCP验证 → 记录结果
```

**具体步骤**:
1. **发现问题** - 执行E2E测试，记录错误
2. **Subagent深度分析** - 使用并行Subagent分析根因
3. **设计修复方案** - 使用Brainstorming skill系统化设计
4. **实施修复** - 编写代码修复问题
5. **Chrome MCP验证** - 使用Chrome DevTools MCP验证修复
6. **记录结果** - 更新经验文档

### Chrome DevTools MCP测试流程

**标准测试步骤**:
```javascript
// 1. 列出所有页面
mcp__chrome-devtools__list_pages()

// 2. 导航到测试页面
mcp__chrome-devtools__navigate_page({
  type: "url",
  url: "http://localhost:5173/parameter-dashboard?game_gid=10000147"
})

// 3. 获取页面快照
mcp__chrome-devtools__take_snapshot()

// 4. 检查控制台错误
mcp__chrome-devtools__list_console_messages({
  types: ["error", "warn"]
})

// 5. 截图记录
mcp__chrome-devtools__take_screenshot({
  filePath: "docs/reports/2026-02-23/verification-screenshot.png",
  fullPage: true
})

// 6. 点击交互元素
mcp__chrome-devtools__click({ uid: "clickable-element-uid" })
```

**错误检测模式**:

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

**React应用挂载错误**:
```
页面状态：React应用无法挂载到DOM
HTML结构：`#app-root`为空，`#initial-loader`一直显示
症状：页面卡在"Loading Event2Table..."状态
```

### React应用挂载问题诊断 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 1次 | **来源**: [E2E-TEST-P0-ISSUE](../archive/2026-03/03-march/reports/E2E-TEST-P0-ISSUE.md)

#### 问题现象

**症状描述**:
- React应用完全无法挂载到DOM
- `#app-root`元素保持空状态
- 初始加载器(`#initial-loader`)一直显示
- 页面停留在"Loading Event2Table..."状态
- 无任何交互元素（0个按钮、0个输入框）

**影响范围**:
- 所有前端页面
- 导致E2E测试无法进行

#### 根本原因

**技术原因**:
1. **JavaScript执行错误** - Apollo Client初始化失败
2. **查询客户端初始化失败** - QueryClient初始化错误
3. **依赖模块导入失败** - 某个依赖模块导入失败
4. **ErrorBoundary捕获渲染错误** - 组件渲染错误被ErrorBoundary捕获

**常见错误**:
- Apollo Client GraphQL端点URL错误
- React组件循环依赖
- TypeScript编译错误
- node_modules损坏或Vite缓存问题

#### 诊断流程

**步骤1: 检查HTML结构**
```bash
# 使用Chrome DevTools MCP
mcp__chrome-devtools__take_snapshot()

# 检查HTML
# ❌ 错误状态：
<div id="app-root"></div>  <!-- 空！ -->
<div id="initial-loader">
  <div class="spinner"></div>
  <div class="text">Loading Event2Table...</div>
</div>

# ✅ 正确状态：
<div id="app-root">
  <div class="dashboard-container">...</div>
</div>
```

**步骤2: 检查浏览器控制台（P0优先级）**
```bash
# 打开Chrome DevTools (F12)
# → Console标签页
# → 记录所有红色错误信息
```

**常见控制台错误**:
```javascript
// React Hooks错误
[error] React has detected a change in the order of Hooks called
[error] Uncaught Error: Rendered more hooks than during the previous render

// 模块解析错误
[error] Uncaught Error: Cannot find module 'xxx'
[error] Error: Cannot read property of undefined

// GraphQL错误
[error] GraphQL error: Network request failed
[error] Unable to reach GraphQL endpoint
```

**步骤3: 检查JavaScript加载**
```bash
# 检查main.tsx是否可访问
curl -I http://localhost:5173/src/main.tsx

# 检查Vite依赖解析
# → Network标签页
# → 查找失败的请求（红色）
# → 特别注意 .tsx, .ts, .jsx文件
```

**步骤4: 验证前端服务器**
```bash
# 检查Vite进程
ps aux | grep vite

# 检查端口
lsof -i :5173

# 检查HTTP响应
curl -I http://localhost:5173
```

#### 解决方案

**解决方案1: 重启前端服务器（首选）**
```bash
# 1. 停止当前Vite进程
kill <vite-pid>
# 或
lsof -ti:5173 | xargs kill -9

# 2. 清理Vite缓存
cd frontend
rm -rf node_modules/.vite

# 3. 重新启动
npm run dev

# 4. 验证服务器启动
curl -I http://localhost:5173
# 应该返回: HTTP/1.1 200 OK
```

**解决方案2: 检查依赖安装**
```bash
cd frontend

# 检查依赖是否完整
npm list

# 重新安装依赖
rm -rf node_modules package-lock.json
npm install

# 验证关键依赖
npm list react
npm list @apollo/client
npm list vite
```

**解决方案3: TypeScript编译检查**
```bash
cd frontend

# 检查类型错误
npx tsc --noEmit

# 查看错误列表
# 修复类型错误后重新启动服务器
```

**解决方案4: 检查Apollo Client配置**
```typescript
// frontend/src/shared/apollo/client.ts

// ✅ 正确：检查GraphQL端点URL
const httpLink = createHttpLink({
  uri: 'http://127.0.0.1:5001/graphql',  // ← 确认URL正确
});

// ✅ 正确：检查Apollo Client初始化
const client = new ApolloClient({
  link: httpLink,
  cache: new InMemoryCache(),
  connectToDevTools: true,  // 开发环境启用
});
```

#### 代码审查清单

**React应用检查**:
- [ ] main.tsx中的`#app-root`元素存在？
- [ ] ReactDOM.createRoot正确调用？
- [ ] ErrorBoundary正确配置？
- [ ] ApolloProvider正确配置？
- [ ] 所有依赖正确安装？

**Apollo Client检查**:
- [ ] GraphQL端点URL正确？
- [ ] HttpLink正确配置？
- [ ] InMemoryCache正确初始化？
- [ ] ApolloProvider包裹App组件？

#### 预防措施

**开发环境检查**:
```bash
# 每次开发前检查
npm run dev  # → 启动前端服务器
python3 web_app.py  # → 启动后端服务器
curl http://localhost:5173  # → 验证前端可访问
curl http://127.0.0.1:5001/api/health  # → 验证后端可访问
```

**CI/CD集成**:
```yaml
# .github/workflows/e2e-test.yml
- name: Start frontend server
  run: |
    cd frontend
    npm run dev &
    npm run wait-for-dev-server  # 等待服务器启动

- name: Start backend server
  run: |
    python3 web_app.py &

- name: Run health check
  run: |
    curl http://localhost:5173
    curl http://127.0.0.1:5001/api/health
```

### 测试工具选择

**Playwright vs Chrome DevTools MCP**:
- **Playwright**: 适合自动化测试、回归测试、CI/CD集成
- **Chrome DevTools MCP**: 适合探索性测试、根因分析、交互式调试

**选择原则**:
- 自动化测试 → Playwright
- 探索性测试 → Chrome DevTools MCP
- 回归测试 → Playwright
- Bug调试 → Chrome DevTools MCP

### 代码审查清单

**E2E测试检查**:
- [ ] 用户工作流是否完整测试？
- [ ] 是否测试了错误场景？
- [ ] 是否验证了控制台无错误？
- [ ] 是否截图记录测试结果？
- [ ] 是否测试了边界情况？

---

## TDD实践 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 1次 | **来源**: [CLAUDE.md](../../CLAUDE.md), [TESTING_LESSONS_LEARNED.md](../archive/2026-02/testing/TESTING_LESSONS_LEARNED.md)

### TDD铁律

**NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST**

**TDD流程（Red-Green-Refactor）**:
1. **Red** - 先写测试，看测试失败
2. **Green** - 编写最小代码使测试通过
3. **Refactor** - 重构优化，保持测试通过

### 为什么需要TDD？

**好处**:
- ✅ 测试先行确保代码满足需求（而非"实现后验证"）
- ✅ 失败的测试证明测试有效（通过的测试可能什么都没测）
- ✅ 快速反馈循环减少调试时间
- ✅ 测试即文档，展示代码的正确使用方式

**违反TDD的代价**:
- ❌ 看似"更快"实际更慢（调试时间 > TDD时间）
- ❌ 测试通过立即 = 测试无效 = 假安全感
- ❌ 技术债务累积 = 未来重构困难

### 强制检查清单

**开发前检查**:
- [ ] 调用 `/superpowers:test-driven-development` skill
- [ ] 阅读TDD铁律
- [ ] 确认已设置测试环境（pytest/npm test等）
- [ ] 准备好先写测试，再看测试失败

**禁止行为**:
- ❌ 代码存在先于测试
- ❌ 测试通过立即（未看到失败）
- ❌ 跳过测试直接实现功能

### 相关经验

- [E2E测试方法论](#e2e测试) - E2E测试具体方法
- [测试自动化](#测试自动化) - 减少重复工作的自动化策略

---

## 测试自动化 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 2次 | **来源**: [TESTING_LESSONS_LEARNED.md](../archive/2026-02/testing/TESTING_LESSONS_LEARNED.md)

### Pre-commit Hook强制测试

**安装pre-commit hook**:
```bash
# 复制pre-commit hook到.git/hooks/
cp scripts/git-hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Hook功能**:
- 每次提交前自动运行测试
- 测试失败则阻止提交
- 显示所有失败的测试

**npm scripts配置**:
```json
{
  "scripts": {
    "test": "playwright test",
    "test:unit": "vitest",
    "test:e2e": "playwright test tests/e2e",
    "test:watch": "vitest --watch"
  }
}
```

### 测试分类

**单元测试**:
- 测试单个函数、类、组件
- 快速执行（毫秒级）
- 使用Vitest（前端）、pytest（后端）

**集成测试**:
- 测试多个模块的交互
- 中等执行时间（秒级）
- 使用pytest（后端）、Vitest（前端）

**E2E测试**:
- 测试完整用户工作流
- 较慢执行（分钟级）
- 使用Playwright

### 测试覆盖率目标

**目标**:
- 单元测试覆盖率：>80%
- 集成测试覆盖率：>60%
- E2E测试覆盖率：关键路径100%

**验证命令**:
```bash
# 前端覆盖率
npm run test:coverage

# 后端覆盖率
pytest backend/test/ --cov=backend --cov-report=html
```

---

## 错误消息质量对用户体验的影响 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 2次 | **来源**: [phase2-lessons-learned.md](../archive/2026-02/testing/phase2-lessons-learned.md)

### 核心原则

**错误消息质量直接影响用户体验和支持成本**

### 错误消息改进示例

| 场景 | 修复前 | 修复后 | 改进效果 |
|------|--------|--------|----------|
| GID重复 | "Game GID already exists" | "游戏GID 10000147 已存在，请使用其他GID（建议使用90000000+范围）" | ⭐⭐⭐⭐⭐ |
| GID格式错误 | "Game GID must be a positive integer" | "游戏GID必须是有效的正整数（提示：GID必须是正整数，如90000001）" | ⭐⭐⭐⭐ |
| 权限不足 | "Permission denied" | "您没有权限删除系统类别（ID: 1），请联系管理员" | ⭐⭐⭐⭐⭐ |

### 最佳实践代码

```javascript
// ❌ 错误做法
throw new Error('创建失败');

// ✅ 正确做法：根据HTTP状态码提供具体指导
let errorMessage = result.message || '创建失败';
if (response.status === 409) {
  errorMessage = `游戏GID ${data.gid} 已存在，请使用其他GID（建议使用90000000+范围）`;
} else if (response.status === 400) {
  if (errorMessage.includes('GID')) {
    errorMessage += '（提示：GID必须是正整数，如90000001）';
  }
}
throw new Error(errorMessage);
```

### 预防措施

**代码审查清单**:
- [ ] 错误消息是否具体可操作？
- [ ] 是否包含解决方案或建议？
- [ ] 是否避免技术术语？
- [ ] 是否考虑不同技术水平的用户？

---

## 避免重复工作 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 2次 | **来源**: [phase2-lessons-learned.md](../archive/2026-02/testing/phase2-lessons-learned.md)

### 问题调查流程

```
1. 阅读相关代码（后端 + 前端）
2. 检查是否有现有实现
3. 检查注释和commit历史
4. 如果已实现 → 验证并文档化
5. 如果未实现 → 设计并实现修复
```

### 案例：事件创建分类问题

**Phase 1建议**: "修复事件创建分类问题"
**Phase 2发现**: 后端第29-39行已有自动创建逻辑
**结论**: 问题已解决，只需要验证

**教训**: 调查优先于实施，避免重复工作

### 预防措施

**开发前检查**:
- [ ] 是否已搜索代码库查找类似实现？
- [ ] 是否检查过相关文档和注释？
- [ ] 是否询问过团队成员？

---

## 测试方法论演进 ⭐ **P1重要**

**优先级**: P1 | **来源**: [phase2-lessons-learned.md](../archive/2026-02/testing/phase2-lessons-learned.md)

### Phase 1方法论（浅层测试）❌

```
1. 导航到页面
2. 检查页面是否加载
3. 检查控制台是否有错误
4. 截图
5. 报告：PASS ✅

问题：
- ❌ 没有测试用户交互
- ❌ 没有验证功能是否工作
- ❌ 错过了关键bug
```

### Phase 2方法论（深度测试）✅

```
1. 导航到页面
2. 识别关键用户交互点
3. 对每个交互点：
   a. 执行交互（点击/输入/拖拽）
   b. 等待响应（2-3秒）
   c. 检查结果（UI变化/网络请求/控制台）
   d. 验证期望结果
4. 记录问题（如有）
5. 截图
6. 报告：详细的PASS/FAIL信息

改进：
- ✅ 测试实际用户工作流
- ✅ 发现真实的用户阻碍问题
- ✅ 提供可操作的修复建议
```

### 测试深度比例

**分配**:
- 页面加载测试：20%
- 用户交互测试：60%
- 工作流完成测试：20%

**为什么60%用于用户交互**:
- 用户主要通过交互与应用程序交互
- 加载成功不等于功能可用
- 交互测试最能发现真实问题

---

## E2E健康检查机制 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 1次 | **来源**: 已归档 (2026-03-01)

### 问题现象

**症状描述**:
- E2E测试执行失败，超时60+秒
- 错误信息不明确：`connect ECONNREFUSED 127.0.0.1:5001`
- 测试失败后难以诊断问题

### 根本原因

**技术原因**:
- E2E测试前未验证后端可用性
- 后端服务未启动导致测试失败
- 缺少快速失败机制

### 解决方案

**前置健康检查**:
```typescript
// tests/e2e/helpers/backend-health.ts
export async function ensureBackendReady(
  maxRetries = 30,
  retryInterval = 1000
): Promise<boolean> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch('http://127.0.0.1:5001/api/health');
      if (response.ok) {
        console.log('✅ Backend is ready');
        return true;
      }
    } catch (error) {
      if (i < maxRetries - 1) {
        console.log(`⏳ Backend not ready, retry ${i + 1}/${maxRetries}...`);
        await new Promise(resolve => setTimeout(resolve, retryInterval));
      }
    }
  }

  console.error('❌ Backend failed to start after retries');
  console.error('🔧 Please start backend: python3 web_app.py');
  return false;
}
```

**E2E测试中使用**:
```typescript
// tests/e2e/dashboard.spec.ts
import { test, beforeAll } from '@playwright/test';
import { ensureBackendReady } from './helpers/backend-health';

beforeAll(async () => {
  // ✅ 前置健康检查
  const backendReady = await ensureBackendReady();
  if (!backendReady) {
    throw new Error('Backend is not available');
  }
});

test('Dashboard loads correctly', async ({ page }) => {
  // ... 测试逻辑
});
```

**实现架构**:
```
E2E测试
    ↓ (beforeAll)
ensureBackendReady()
    ↓ (polling)
/api/health 端点
    ↓ (success)
实际API测试
```

### 代码审查清单

- [ ] E2E测试是否添加了前置健康检查？
- [ ] 是否使用polling而非单次检查？
- [ ] 是否提供了清晰的启动后端的指令？
- [ ] 是否有重试机制（建议30次）？

### 案例文档

- [API连接健康检查报告](../archive/testing-reports/2026-03-01/2026-03-01/TRACK-5-API-CONNECTIVITY-HEALTH-CHECK.md) (已归档)

---

## E2E测试完整流程 ⭐ (2026-03-04新增)

### 测试执行模式（基于11/11页面100%覆盖）

**测试覆盖统计**:
- ✅ **完全正常**: 1/11 (9%) - Event Nodes Management
- ⚠️ **部分工作**: 3/11 (27%) - Dashboard, Event Node Builder, Canvas
- ❌ **完全失败**: 7/11 (64%) - Events, Parameters, Flows, Categories, Common Params

**健康度评分**:
- 🟢 100%: Event Nodes Management（唯一完全正常）
- 🟡 50%: 部分工作页面（基础加载正常，功能部分工作）
- 🔴 <20%: 完全失败（路由、API、配置问题）

### Ralph Loop迭代测试法

**核心流程**:
```
发现问题 → Subagent深度分析 → 设计修复方案 → 实施修复 → Chrome MCP验证 → 记录结果
```

**迭代周期**:
1. **发现问题** - 执行E2E测试，记录页面状态、控制台错误、功能缺失
2. **Subagent深度分析** - 使用并行Subagent分析根本原因（GraphQL配置、路由问题、API错误等）
3. **设计修复方案** - 使用Brainstorming skill系统化设计修复策略
4. **实施修复** - 代码修复（路由配置、API实现、错误处理等）
5. **Chrome MCP验证** - 使用Chrome DevTools MCP验证修复效果
6. **记录结果** - 更新测试报告和经验文档

### Chrome DevTools MCP测试流程（标准6步）

```javascript
// 1. 列出所有页面
mcp__chrome-devtools__list_pages()

// 2. 导航到测试页面
mcp__chrome-devtools__navigate_page({
  type: "url",
  url: "http://localhost:5173/parameter-dashboard?game_gid=10000147"
})

// 3. 获取页面快照
mcp__chrome-devtools__take_snapshot()

// 4. 检查控制台错误
mcp__chrome-devtools__list_console_messages({
  types: ["error", "warn"]
})

// 5. 截图记录
mcp__chrome-devtools__take_screenshot({
  filePath: "docs/reports/2026-03-03/e2e-test-screenshot.png",
  fullPage: true
})

// 6. 点击交互元素
mcp__chrome-devtools__click({ uid: "clickable-element-uid" })
```

### 测试失败诊断方法

**React应用挂载错误**:
```
症状: 页面卡在"Loading Event2Table..."状态
检查: #app-root为空，无JavaScript错误
原因: Apollo Client配置错误、依赖模块导入失败
```

**GraphQL API错误**:
```
症状: "加载失败 - Failed to fetch"
检查: 网络标签红色请求，/graphql端点返回HTML
原因: 后端GraphQL未启动或配置错误
```

**路由参数解析错误**:
```
症状: URL包含参数但页面未收到（/flows?game_gid=10000147）
检查: HashRouter是否正确解析查询参数
原因: 路由配置或组件参数获取逻辑错误
```

**API后端500错误**:
```
症状: "INTERNAL SERVER ERROR"
检查: 后端日志、数据库连接、SQL查询
原因: 代码异常、数据库错误、权限问题
```

### E2E测试报告模板（结构化）

**执行摘要**:
```markdown
| 页面分类 | 页面数 | 测试状态 | 通过率 |
|---------|-------|---------|--------|
| Dashboard | 1 | ⚠️ 部分问题 | 50% |
| 事件管理 | 2 | ❌ 失败 | 0% |
| 参数管理 | 3 | ❌ 失败 | 0% |
| 高级功能 | 3 | ⚠️ 部分工作 | 33% |
| 管理功能 | 3 | ❌ 失败 | 0% |
| 总计 | **11** | **❌ 整体失败** | **17%** |
```

**关键统计**:
- ✅ **完全正常**: 1/11 (9%)
- ⚠️ **部分工作**: 3/11 (27%)
- ❌ **完全失败**: 7/11 (64%)

**问题分类统计**:
| 优先级 | 问题数量 | 影响页面 |
|--------|---------|---------|
| **P0 (阻塞)** | 8个 | Events (2), Parameters (2), Flows, Categories, Common Params, GraphQL |
| **P1 (重要)** | 5个 | Dashboard (2), Event Node Builder, Canvas, Events Create |
| **P2 (一般)** | 3个 | Dashboard (1), Flows (1), Canvas (1) |

### 关键问题修复经验

**P0 - 立即修复问题**:

1. **React应用挂载问题**:
   - 根因: `routes.tsx`导入不存在的模块路径
   - 修复: 注释掉无效导入，验证所有导入路径

2. **GraphQL后端配置**:
   - 根因: 前端已迁移到GraphQL，后端未启动
   - 修复: 检查`web_app.py`中GraphQL路由，确保后端GraphQL服务运行

3. **路由参数解析**:
   - 根因: HashRouter查询参数解析失败
   - 修复: 验证路由配置和参数传递逻辑

4. **API端点错误**:
   - 根因: 后端500错误或404
   - 修复: 检查后端日志，定位具体错误代码

**P1 - 重要问题修复**:

1. **游戏上下文提示**:
   - 问题: 无游戏上下文时显示不明确
   - 修复: 创建`RequireGameContext`组件，提供清晰的选择游戏提示

2. **错误消息改进**:
   - 问题: "INTERNAL SERVER ERROR"对用户不友好
   - 修复: 实施统一错误处理，开发环境显示详细错误，生产环境使用友好消息

3. **路由守卫逻辑**:
   - 问题: 路由重定向逻辑混乱
   - 修复: 简化路由守卫，确保正确的重定向行为

### 测试工具对比

| 工具 | 适用场景 | 优势 | 劣势 |
|------|----------|------|------|
| **Chrome DevTools MCP** | 探索性测试、根因分析 | 交互式调试、实时监控 | 需要人工操作 |
| **Playwright** | 自动化测试、回归测试 | 可重复、CI/CD集成 | 编写脚本复杂 |
| **组合使用** | 完整测试策略 | 深度+广度覆盖 | 协调成本高 |

### 测试最佳实践

**测试前准备**:
```bash
# 1. 检查服务器状态
curl http://localhost:5173  # 前端
curl http://127.0.0.1:5001/api/health  # 后端

# 2. 启动测试服务器
cd frontend
npm run dev &

# 3. 准备测试数据
sqlite3 data/dwd_generator.db "SELECT COUNT(*) FROM games;"
```

**测试执行要求**:
- [ ] 测试所有11个页面（100%覆盖）
- [ ] 记录每个页面的健康度评分
- [ ] 检查控制台所有错误（error/warn）
- [ ] 截图记录关键问题
- [ ] 区分P0/P1/P2优先级

**修复验证流程**:
1. 修复代码
2. 重启服务（前端+后端）
3. 重新执行E2E测试
4. 验证问题已解决
5. 更新测试报告

### 问题分类和优先级

**P0 - 阻塞性问题**（影响基本功能）:
- React应用无法挂载
- GraphQL后端不可用
- 关键API路由失败
- 用户无法完成核心任务

**P1 - 重要问题**（影响用户体验）:
- 游戏上下文提示不明确
- 错误消息不友好
- 某些功能不可用
- 用户体验障碍

**P2 - 一般问题**（优化改进）:
- UI显示问题
- 性能问题
- 文档缺失
- 代码质量问题

### API契约测试 ⭐ **P0极其重要 - 2026-03-04新增**

**优先级**: P0 | **出现次数**: 1次 | **来源**: 已归档 (2026-03-03)

### 前端路由哈希模式测试

**核心测试场景**：
```javascript
// 浏览器控制台测试脚本
const routes = [
  { path: '/parameters', title: '参数管理' },
  { path: '/parameters/dashboard', title: '参数统计' },
  { path: '/parameters/compare', title: '参数对比' },
  { path: '/parameters/enhanced', title: 'Enhanced' },
  { path: '/parameter-dashboard', title: '参数统计' }
];

routes.forEach((route, index) => {
  setTimeout(() => {
    window.location.hash = route.path;
    console.log(`Testing: ${route.path} - Expected: ${route.title}`);
  }, index * 2000);
});
```

### 参数格式一致性验证

**参数设计规范**：
```javascript
// ✅ 正确：使用 gameGid 参数
const gameGid = gameData.gid;  // 10000147
fetch(`/api/events?game_gid=${gameGid}`)  // 参数名一致

// ❌ 错误：参数名不一致
fetch(`/api/events?game_id=${gameGid}`)  // 错误的参数名
```

### 路由验证工具

**自动化端点测试**：
```javascript
// 浏览器控制台 - 验证API端点
const testEndpoints = [
  { method: 'GET', url: 'http://127.0.0.1:5001/api/health' },
  { method: 'GET', url: 'http://127.0.0.1:5001/api/events?game_gid=10000147' },
  { method: 'GET', url: 'http://127.0.0.1:5001/api/games' }
];

testEndpoints.forEach(async (endpoint) => {
  try {
    const response = await fetch(endpoint.url);
    console.log(`${endpoint.method} ${endpoint.url}: ${response.status}`);
  } catch (error) {
    console.error(`${endpoint.method} ${endpoint.url}: FAIL - ${error.message}`);
  }
});
```

### 常见问题及解决方案

**问题1: 404路由错误**
```bash
# 检查路由定义
grep -A5 "path: \"parameters\"" frontend/src/routes/routes.tsx

# 预期输出
#   // More specific parameter routes must come before general "parameters" route
#   { path: "parameters/dashboard", element: <ParameterDashboard /> },
#   { path: "parameters/compare", element: <ParameterCompare /> },
#   { path: "parameters/enhanced", element: <ParametersEnhanced /> },
#   { path: "parameters", element: <ParametersList /> },
```

**问题2: API参数错误**
```javascript
// 检查前端API调用
// ✅ 正确
fetch(`/api/events?game_gid=${gameGid}`)

// ❌ 错误
fetch(`/api/events?game_id=${gameGid}`)
```

### 验证步骤清单

**完整验证流程**：
1. ✅ 打开浏览器 DevTools（F12）
2. ✅ 清除控制台（🚫 按钮）
3. ✅ 依次访问每个路由：
   - `http://localhost:5173/#/parameters`
   - `http://localhost:5173/#/parameters/dashboard`
   - `http://localhost:5173/#/parameters/compare`
   - `http://localhost:5173/#/parameters/enhanced`
   - `http://localhost:5173/#/parameter-dashboard`
4. ✅ 检查每个路由的页面标题和内容
5. ✅ 确保控制台无错误
6. ✅ 验证显示正确的页面（不是"Select Game"提示）

### 成功标准

**通过标准**：
- ✅ 所有5个路由加载无控制台错误
- ✅ 每个路由显示正确的页面标题
- ✅ 每个路由显示正确的页面内容
- ✅ 无"Select Game"提示（如果游戏已选择）
- ✅ 无无限加载旋转器
- ✅ 无404页面

### 测试文档生成标准

**必生成的文档**:
1. **E2E-TEST-REPORT.md** - 详细测试报告
2. **FIX-GUIDE.md** - 修复指南
3. **TEST-SUMMARY.md** - 测试总结

> **注意**: 以上文档模板已归档至 `docs/archive/2026/03-march/reports/`

**必生成的截图**:
- `/frontend/screenshots/e2e-*.png` - 所有页面截图
- `/tmp/*.png` - Agent生成截图

**必生成的日志**:
- Vite日志: `/tmp/vite-restart.log`
- Chrome DevTools MCP session: `~/Library/Caches/superpowers/browser/2026-03-03/session-*`

### 控制台错误检测的完整工作流 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 3次 | **来源**: [E2E最终综合报告](../reports/2026-03-07/E2E-FINAL-COMPREHENSIVE-REPORT.md), [控制台错误检测报告](../reports/2026-03-07/E2E-CONSOLE-ERROR-DETECTION-REPORT.md)

### 问题现象

**症状描述**:
- 在E2E测试中，单纯页面加载成功不代表功能正常
- 控制台错误（error/warn）可能被忽略，但实际影响用户体验
- 需要在页面加载、用户交互、API响应等全流程中捕获错误

**影响范围**:
- 所有E2E测试
- 前端JavaScript异步执行
- React组件渲染错误
- GraphQL API错误

### 根本原因

**技术原因**:
- 前端JavaScript异步执行可能产生延迟错误
- React组件渲染错误可能不中断页面加载
- GraphQL API错误可能在生产环境被错误处理
- 用户交互可能触发新的错误，需要对比分析

### 解决方案

**完整的E2E测试 + 控制台错误检测流程**:
```javascript
// 标准化E2E测试流程
async function comprehensivePageTest(url) {
  // 1. 导航到页面
  await mcp__chrome-devtools__navigate_page({
    type: "url",
    url: url
  })

  // 2. 等待页面稳定
  await mcp__chrome-devtools__wait_for({
    selector: "main",
    timeout: 5000
  })

  // 3. 获取基线错误
  const baselineErrors = await mcp__chrome-devtools__list_console_messages({
    types: ["error", "warn"]
  })

  // 4. 执行关键交互（如点击按钮）
  await mcp__chrome-devtools__click({
    uid: "action-button"
  })

  // 5. 等待响应
  await mcp__chrome-devtools__await_text({
    text: "Loading...",
    timeout: 3000
  })

  // 6. 获取交互后的新错误
  const afterErrors = await mcp__chrome-devtools__list_console_messages({
    types: ["error"],
    since: Date.now() - 5000
  })

  // 7. 对比分析
  const newErrors = afterErrors.messages.filter(
    err => !baselineErrors.messages.some(init => init.id === err.id)
  )

  return {
    baselineErrors,
    newErrors,
    success: newErrors.length === 0
  }
}
```

**Chrome DevTools MCP工作流**:
```javascript
// 标准测试步骤
// 1. 列出所有页面
mcp__chrome-devtools__list_pages()

// 2. 导航到测试页面
mcp__chrome-devtools__navigate_page({
  type: "url",
  url: "http://localhost:5173/parameter-dashboard?game_gid=10000147"
})

// 3. 获取页面快照
mcp__chrome-devtools__take_snapshot()

// 4. 检查控制台错误
mcp__chrome-devtools__list_console_messages({
  types: ["error", "warn"]
})

// 5. 截图记录
mcp__chrome-devtools__take_screenshot({
  filePath: "docs/reports/2026-03-08/verification-screenshot.png",
  fullPage: true
})

// 6. 点击交互元素
mcp__chrome-devtools__click({ uid: "clickable-element-uid" })
```

### 错误分类和优先级

**错误优先级标准**:
```typescript
enum ErrorPriority {
  P0 = 'BLOCKING',      // 阻塞性错误 - 功能完全不可用
  P1 = 'CRITICAL',      // 严重错误 - 核心功能受影响
  P2 = 'MAJOR',         // 主要错误 - 用户体验受损
  P3 = 'MINOR',         // 次要错误 - 可选功能问题
  P4 = 'INFO'           // 信息提示 - 不影响功能
}

// 错误分类规则
function classifyError(error: ConsoleError): ConsoleError {
  // React错误
  if (error.message.includes('React') || error.message.includes('hooks')) {
    error.category = 'REACT';
    error.priority = error.message.includes('change in the order')
      ? ErrorPriority.P0
      : ErrorPriority.P1;
  }

  // GraphQL错误
  if (error.message.includes('GraphQL') || error.message.includes('fetch')) {
    error.category = 'GRAPHQL';
    error.priority = ErrorPriority.P1;
  }

  // 网络错误
  if (error.message.includes('Failed to load') || error.message.includes('network')) {
    error.category = 'NETWORK';
    error.priority = ErrorPriority.P1;
  }

  return error;
}
```

### 预防措施

**代码审查清单**:
- [ ] 所有E2E测试必须包含控制台错误检测？
- [ ] 是否建立错误严重度分级（P0错误必须立即修复）？
- [ ] 是否使用自动化脚本对比交互前后的错误变化？
- [ ] 是否记录错误ID用于追踪同一问题的多次出现？

### 业务价值

- 测试覆盖率从"页面加载"提升到"全流程功能验证"
- 能发现隐藏的功能问题，避免用户遇到异常
- 减少生产环境故障率（提前发现潜在问题）

### 案例文档

- [E2E最终综合报告](../reports/2026-03-07/E2E-FINAL-COMPREHENSIVE-REPORT.md)
- [控制台错误检测报告](../reports/2026-03-07/E2E-CONSOLE-ERROR-DETECTION-REPORT.md)

---

## E2E测试中的代码修复验证流程 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 2次 | **来源**: [E2E测试报告](../reports/2026-03-07/E2E-FINAL-COMPREHENSIVE-REPORT.md)

### 问题现象

**症状描述**:
- 代码修复完成后，需要验证修复是否真正生效
- 浏览器缓存可能导致修复效果不体现
- 需要区分"代码修复"和"功能修复"两个阶段

### 解决方案

**完整的修复验证流程**:
```bash
# 完整的修复验证流程
function verifyFix() {
  echo "=== 开始修复验证 ==="

  # 1. 停止所有服务器
  echo "1. 停止前端和后端服务器"
  kill $(lsof -ti:5173) 2>/dev/null || true
  kill $(lsof -ti:5001) 2>/dev/null || true

  # 2. 清除缓存
  echo "2. 清除浏览器缓存"
  echo "请手动操作: Ctrl+Shift+Delete → 选择'缓存的图像和文件' → '全部时间'"
  read -p "清除缓存后按回车继续..."

  # 3. 重新启动服务器
  echo "3. 重新启动服务器"
  cd frontend && npm run dev &
  cd backend && nohup python web_app.py > ../logs/backend.log 2>&1 &

  # 4. 等待服务器启动
  echo "4. 等待服务器启动"
  sleep 5

  # 5. 验证服务可用性
  curl -s http://localhost:5173 > /dev/null
  curl -s http://127.0.0.1:5001/api/health > /dev/null

  # 6. 重新测试修复的功能
  echo "6. 重新测试修复的功能"
  echo "请手动测试: 打开浏览器 → 访问 http://localhost:5173 → 测试修复的功能"

  # 7. 检查控制台错误
  echo "7. 检查浏览器控制台 (F12 → Console)"
  echo "确保没有出现新的错误信息"
}
```

### 预防措施

**验证清单**:
- [ ] 代码修复后必须执行完整的验证流程？
- [ ] 浏览器缓存清除是必经步骤？
- [ ] 需要测试原始问题和新增功能？
- [ ] 是否记录验证结果，包括截图和错误日志？

### 业务价值

- 确保修复真正生效，避免"假修复"
- 防止缓存导致的问题被误判
- 建立可重复的验证标准

---

## 测试数据准备和验证 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 2次 | **来源**: [E2E测试报告](../reports/2026-03-07/E2E-FINAL-COMPREHENSIVE-REPORT.md)

### 问题现象

**症状描述**:
- 测试时数据库缺少必要的测试数据
- 测试数据与生产数据混合，影响测试结果
- 测试后数据清理不彻底

### 解决方案

**测试数据准备脚本**:
```bash
# 测试数据准备脚本
function prepareTestData() {
  echo "=== 准备测试数据 ==="

  # 1. 验证测试环境
  if [ "$FLASK_ENV" != "testing" ]; then
    echo "❌ 错误: 未在测试环境 (FLASK_ENV=testing)"
    exit 1
  fi

  # 2. 检查测试数据库
  if [ ! -f "data/test_database.db" ]; then
    echo "❌ 错误: 测试数据库不存在"
    exit 1
  fi

  # 3. 验证测试数据范围
  sqlite3 data/test_database.db "
    SELECT COUNT(*) FROM games WHERE gid >= 90000000;
    SELECT COUNT(*) FROM log_events WHERE game_gid >= 90000000;
    SELECT COUNT(*) FROM event_params WHERE game_gid >= 90000000;
  "

  # 4. 清理临时测试数据（保留基础数据）
  echo "4. 清理临时测试数据"
  # 执行清理脚本

  # 5. 验证数据一致性
  echo "5. 验证数据一致性"
  python scripts/test/verify_data_consistency.py
}
```

### 预防措施

**代码审查清单**:
- [ ] 必须在测试环境（FLASK_ENV=testing）执行测试？
- [ ] 测试数据GID必须使用90000000+范围？
- [ ] 测试前验证数据库存在且数据符合预期？
- [ ] 是否建立测试数据清理机制？

### 业务价值

- 确保测试环境的独立性和一致性
- 避免测试数据污染生产环境
- 提高测试的可重复性和可靠性

---

## Dashboard实时优化（WebSocket替代轮询） ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [Dashboard实时优化报告](../reports/2026-03-07/DASHBOARD-REALTIME-OPTIMIZATION-REPORT.md)

### 问题现象

**症状描述**:
- 用户抱怨Dashboard更新延迟（5分钟）
- 不必要的API调用浪费带宽（页面隐藏时仍在轮询）
- 缺乏实时性，创建游戏/事件后无法立即看到结果

### 根本原因

**技术原因**:
- 使用固定轮询间隔（5秒），没有考虑用户实际使用场景
- 缺少页面可见性检测，导致后台标签页仍频繁请求
- 缓存失效机制不工作，数据更新后无法及时反映

### 解决方案

**基于页面可见性的智能轮询**:
```typescript
// frontend/src/hooks/usePageVisibility.ts (新增)
export function usePageVisibility(): boolean {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const handleVisibilityChange = () => {
      setIsVisible(!document.hidden);
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  return isVisible;
}

// 智能轮询间隔Hook
export function usePollingInterval(
  visibleInterval: number = 10000,  // 10秒可见时
  hiddenInterval: number = 60000    // 60秒隐藏时
): number {
  const isVisible = usePageVisibility();
  return isVisible ? visibleInterval : hiddenInterval;
}
```

**在Dashboard中使用**:
```typescript
// frontend/src/analytics/pages/DashboardGraphQL.tsx (修改)
function DashboardGraphQL() {
  const pollingInterval = usePollingInterval(10000, 60000);

  const { data: gamesData } = useGames(5, 0, {
    fetchPolicy: 'cache-first',
    refetchInterval: pollingInterval,  // ⚡ 智能轮询
    nextFetchPolicy: 'cache-first',
  });
}
```

### 预防措施

**代码审查清单**:
- [ ] 新的轮询策略必须使用Page Visibility API？
- [ ] 隐藏时轮询间隔至少60秒，减少83%的API调用？
- [ ] 缓存失效必须与业务操作强关联？
- [ ] 是否建立性能基准测试，确保优化效果？

### 业务价值

- Dashboard更新延迟从5分钟缩短到10秒（96.7%提升）
- 用户获得接近实时的工作体验
- 减少服务器负载和带宽消耗

### 案例文档

- [Dashboard实时优化报告](../reports/2026-03-07/DASHBOARD-REALTIME-OPTIMIZATION-REPORT.md)

---

## 缓存失效装饰器的自动化实现 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [Dashboard实时优化报告](../reports/2026-03-07/DASHBOARD-REALTIME-OPTIMIZATION-REPORT.md)

### 问题现象

**症状描述**:
- Dashboard缓存5分钟不更新，用户看到过期数据
- 代码中手动清理缓存容易遗漏或出错
- 缓存键格式不统一，导致失效失败

### 解决方案

**自动缓存失效装饰器**:
```python
# backend/core/cache/decorators.py (新增)
def cache_invalidate(func: Callable) -> Callable:
    """自动缓存失效装饰器 - 根据函数名自动推断缓存键"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        # 根据函数名自动推断需要失效的缓存键
        func_name = func.__name__

        # 自动失效dashboard_statistics（所有数据变更都影响）
        try:
            _cache.delete("dashboard_statistics")
            logger.info(f"✅ 已失效缓存: dashboard_statistics (由 {func_name} 触发)")
        except Exception as e:
            logger.warning(f"⚠️ 失效dashboard_statistics失败: {e}")

        return result
    return wrapper

# 在Service方法中使用
class GameService:
    @cache_invalidate  # 自动失效相关缓存
    def create_game(self, game_data: GameEntity) -> GameEntity:
        # 创建游戏逻辑
        pass
```

### 预防措施

**代码审查清单**:
- [ ] 所有写操作（create/update/delete）必须添加`@cache_invalidate`？
- [ ] 是否建立缓存键命名规范（如：`{module}:{function}:statistics`）？
- [ ] 缓存失效操作必须有错误处理和日志记录？
- [ ] 是否定期验证缓存是否按预期失效？

### 业务价值

- 确保数据变更后仪表板能立即更新
- 减少手动缓存清理的工作量和错误
- 提高系统一致性和用户体验

---

## 模态框集成的完整模式 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [E2E最终综合报告](../reports/2026-03-07/E2E-FINAL-COMPREHENSIVE-REPORT.md)

### 问题现象

**症状描述**:
- Dashboard的"管理游戏"按钮点击无响应
- 模态框组件已导入但未渲染
- 状态管理不完整，缺少控制状态

### 解决方案

**完整的模态框集成模式**:
```tsx
// 1. 正确的导入
import BaseModal from '@shared/ui/BaseModal/BaseModal';
import GameManagementModal from '@/features/games/GameManagementModalGraphQL';

// 2. 完整的状态管理
const {
  openGameManagementModal,
  isGameManagementModalOpen,
  closeGameManagementModal
} = useGameStore();

// 3. 在JSX中添加模态框
<BaseModal
  isOpen={isGameManagementModalOpen}
  onClose={closeGameManagementModal}
  title="游戏管理"
  size="full"
>
  <GameManagementModal />
</BaseModal>
```

### 预防措施

**代码审查清单**:
- [ ] 模态框集成必须包含完整的导入和状态？
- [ ] 模态框组件必须放置在正确的位置？
- [ ] 状态管理需要包含打开、关闭、状态检查？
- [ ] 是否建立模态框集成检查清单？

### 业务价值

- 确保模态框功能完整可用
- 避免用户交互功能失效
- 统一的集成模式提高开发效率

---

## TDD Red阶段经验 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 1次 | **最后更新**: 2026-03-09 | **来源**: [TDD Red阶段总结](../reports/2026-03-08/TDD-RED-SUMMARY.md), [11个P0问题报告](../reports/2026-03-08/P0-ISSUES-COMPLETE.md)

### 问题现象

**症状描述**:
- TDD（测试驱动开发）Red阶段发现11个P0问题
- 测试用例设计不完整导致遗漏关键场景
- Red阶段（测试失败）未充分验证，直接跳到Green阶段

**影响范围**:
- 所有使用TDD开发的功能
- GraphQL mutations
- 权限检查
- 输入验证

### 根本原因

**技术原因**:
1. **测试用例覆盖不完整** - 只测试正常流程，未测试异常场景
2. **测试数据准备不足** - 缺少边界值和无效输入的测试
3. **Red阶段验证不充分** - 测试失败未详细分析直接编写代码
4. **测试独立性不足** - 测试之间有依赖，无法独立运行

### 解决方案

**完整的TDD Red-Green-Refactor流程**:

**Red阶段（先写测试，看测试失败）**:
```python
# backend/tests/unit/test_game_mutations.py (示例)

def test_create_game_with_duplicate_gid():
    """
    测试场景：创建重复GID的游戏应该失败
    预期结果：409 Conflict错误
    """
    # Arrange: 准备测试数据
    existing_game = GameEntity(gid="90000001", name="Test Game", ods_db="ieu_ods")
    game_service.create_game(existing_game)

    duplicate_game = GameEntity(gid="90000001", name="Duplicate", ods_db="ieu_ods")

    # Act + Assert: 执行并验证
    with pytest.raises(ValueError) as exc_info:
        game_service.create_game(duplicate_game)

    assert "already exists" in str(exc_info.value)

def test_create_game_with_invalid_gid_format():
    """
    测试场景：创建GID格式无效的游戏应该失败
    预期结果：400 Bad Request错误
    """
    # ❌ 错误的GID格式（包含字母）
    invalid_game = GameEntity(gid="ABC123", name="Invalid", ods_db="ieu_ods")

    # Act + Assert
    with pytest.raises(ValidationError) as exc_info:
        game_service.create_game(invalid_game)

    assert "GID must be numeric" in str(exc_info.value)
```

**Green阶段（编写最小代码使测试通过）**:
```python
# backend/services/games/game_service.py

def create_game(self, game_data: GameEntity) -> GameEntity:
    """
    创建游戏

    Green阶段实现：仅使测试通过的最小代码
    """
    # ✅ 检查GID唯一性（针对test_create_game_with_duplicate_gid）
    existing = self.game_repo.find_by_gid(game_data.gid)
    if existing:
        raise ValueError(f"Game GID {game_data.gid} already exists")

    # ✅ 验证GID格式（针对test_create_game_with_invalid_gid_format）
    if not game_data.gid.isdigit():
        raise ValidationError("GID must be numeric")

    # 创建游戏
    game_id = self.game_repo.create(game_data.model_dump())
    return self.game_repo.find_by_id(game_id)
```

**Refactor阶段（重构优化，保持测试通过）**:
```python
# 重构后的实现

def create_game(self, game_data: GameEntity) -> GameEntity:
    """
    创建游戏

    Refactor阶段：优化代码结构，但保持所有测试通过
    """
    # ✅ 提取验证逻辑到单独方法（重构）
    self._validate_game_gid(game_data.gid)

    # ✅ 检查唯一性
    if self.game_repo.find_by_gid(game_data.gid):
        raise ValueError(f"Game GID {game_data.gid} already exists")

    # 创建游戏并清理缓存
    game_id = self.game_repo.create(game_data.model_dump())
    return self.game_repo.find_by_id(game_id)

def _validate_game_gid(self, gid: str) -> None:
    """验证GID格式（重构后提取的方法）"""
    if not gid.isdigit():
        raise ValidationError("GID must be numeric")
    if len(gid) < 8 or len(gid) > 10:
        raise ValidationError("GID must be 8-10 digits")
```

### 11个P0问题清单（从TDD Red阶段发现）

1. **权限检查缺失** - GraphQL mutations缺少`@authenticated`装饰器
2. **GID重复验证不完整** - 未测试GID重复场景
3. **输入验证缺失** - 未测试特殊字符、SQL注入、XSS攻击
4. **枚举值大小写问题** - GraphQL枚举值与前端不匹配
5. **Pydantic字段缺失** - Service层访问未在Schema中定义的字段
6. **数据库事务未回滚** - 测试失败后未清理数据库
7. **并发处理缺失** - 未测试并发创建相同GID
8. **缓存一致性** - 未验证缓存失效后数据一致性
9. **错误消息不友好** - 未验证用户看到的错误消息质量
10. **性能测试缺失** - 未测试大量数据时的性能
11. **日志记录缺失** - 未验证关键操作是否有日志

### 代码审查清单

**TDD Red阶段检查**:
- [ ] 是否先编写测试用例？
- [ ] 测试用例是否包含正常流程和异常流程？
- [ ] 是否验证测试失败（看到失败的错误消息）？
- [ ] 是否使用边界值和无效输入进行测试？

**TDD Green阶段检查**:
- [ ] 是否只编写使测试通过的最小代码？
- [ ] 是否避免过度实现（添加不需要的功能）？
- [ ] 是否所有测试都通过？

**TDD Refactor阶段检查**:
- [ ] 是否重构代码结构但保持测试通过？
- [ ] 是否提取重复逻辑？
- [ ] 是否优化代码可读性？

### 预防措施

**开发前检查**:
- [ ] 调用 `/superpowers:test-driven-development` skill
- [ ] 准备完整的测试用例清单
- [ ] 设置测试环境（pytest/npm test等）
- [ ] 准备测试数据（使用90000000+范围）

**测试用例设计模板**:
```python
# 测试用例必须包含的场景
def test_feature():
    # 1. 正常流程（Happy Path）
    # 2. 边界值测试（最小值、最大值、空值）
    # 3. 异常输入（特殊字符、SQL注入、XSS）
    # 4. 并发测试（多用户同时操作）
    # 5. 性能测试（大数据量）
    # 6. 错误消息验证（用户友好性）
```

### 业务价值

- TDD Red阶段发现11个P0问题，避免生产环境故障
- 测试先行确保代码满足需求（而非"实现后验证"）
- 失败的测试证明测试有效（通过的测试可能什么都没测）
- 快速反馈循环减少调试时间

### 案例文档

- [TDD Red阶段总结](../reports/2026-03-08/TDD-RED-SUMMARY.md)
- [11个P0问题完整报告](../reports/2026-03-08/P0-ISSUES-COMPLETE.md)

---

## GraphQL 400错误诊断 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 3次 | **最后更新**: 2026-03-09 | **来源**: [GraphQL 400错误深度分析](../reports/2026-03-08/GRAPHQL-400-DEEP-DIVE.md), [GraphQL 400最终修复](../reports/2026-03-08/GRAPHQL-400-FINAL-FIX.md)

### 问题现象

**症状描述**:
- GraphQL mutation返回`400 BAD REQUEST`错误
- 错误消息不明确：`"Variable '$input' got invalid value"`或`"Enum 'HqlJoinType' cannot represent value"`
- 前端TypeScript枚举值与后端GraphQL schema不匹配
- FieldSelectionModal组件的batchAddFieldsToCanvas mutation持续失败

**影响范围**:
- 所有GraphQL mutations
- Event Node Builder功能
- Canvas配置保存

### 根本原因

**技术原因**:
1. **枚举值大小写不匹配** - 前端使用`LEFT-JOIN`（连字符），后端期望`LEFT_JOIN`（下划线）
2. **Pydantic字段缺失** - Service层访问未在Schema中定义的字段
3. **参数格式不一致** - 前端发送`game_id`，后端期望`game_gid`
4. **GraphQL schema未同步** - 后端修改枚举值但前端TypeScript类型未更新

### 诊断流程

**步骤1: 检查GraphQL错误消息**
```javascript
// 浏览器DevTools → Network标签 → GraphQL请求 → Response

// ❌ 错误示例1：枚举值格式错误
{
  "errors": [
    {
      "message": "Enum 'HqlJoinType' cannot represent value: \"LEFT-JOIN\"",
      "locations": [{"line": 2, "column": 3}]
    }
  ]
}

// ✅ 正确值：LEFT_JOIN（下划线而非连字符）
```

**步骤2: 对比前端TypeScript枚举和后端GraphQL schema**
```graphql
# 后端GraphQL Schema (backend/gql_api/schema.py)
enum HqlJoinType {
  LEFT_JOIN    # ✅ UPPER_SNAKE_CASE
  RIGHT_JOIN
  INNER_JOIN
  FULL_JOIN
}
```

```typescript
// ❌ 错误：前端使用连字符
export enum HqlJoinType {
  LEFT_JOIN = "LEFT-JOIN",      // 错误！GraphQL无法解析
  RIGHT_JOIN = "RIGHT-JOIN"
}

// ✅ 正确：前端使用下划线
export enum HqlJoinType {
  LEFT_JOIN = "LEFT_JOIN",      // 完全匹配GraphQL schema
  RIGHT_JOIN = "RIGHT_JOIN",
  INNER_JOIN = "INNER_JOIN",
  FULL_JOIN = "FULL_JOIN"
}
```

**步骤3: 检查Pydantic模型完整性**
```python
# backend/models/schemas.py

class EventNodeInput(BaseModel):
    """Event node creation/update input"""
    id: Optional[int] = None
    node_type: str
    # ❌ 错误：缺少event_type字段
    # table_name: Optional[str] = None  # ← 未定义

# Service层访问未定义字段会抛出AttributeError
def create_event_node(self, node_data: EventNodeInput):
    event_type = node_data.event_type  # ❌ AttributeError!
```

**步骤4: 验证GraphQL mutation**
```bash
# 使用curl测试GraphQL mutation
curl -X POST http://127.0.0.1:5001/api/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { batchAddFieldsToCanvas(input: {gameGid: 90000001, fieldIds: [1, 2, 3]}) { success } }"
  }'

# 检查响应
# ✅ 200 OK + data: 成功
# ❌ 400 BAD REQUEST + errors: GraphQL验证失败
```

### 解决方案

**解决方案1: 修复枚举值大小写**
```typescript
// frontend/src/graphql/mutations.ts

export enum HqlJoinType {
  // ✅ 修复：使用下划线而非连字符
  LEFT_JOIN = "LEFT_JOIN",
  RIGHT_JOIN = "RIGHT_JOIN",
  INNER_JOIN = "INNER_JOIN",
  FULL_JOIN = "FULL_JOIN"
}
```

**解决方案2: 补全Pydantic模型字段**
```python
# backend/models/schemas.py

class EventNodeInput(BaseModel):
    """Event node creation/update input"""
    id: Optional[int] = None
    node_type: str
    event_type: Optional[str] = None      # ✅ 添加缺失字段
    table_name: Optional[str] = None      # ✅ 添加缺失字段
    join_type: Optional[str] = None       # ✅ 添加缺失字段
```

**解决方案3: 使用graphql-codegen自动生成类型**
```bash
# 安装graphql-codegen
npm install --save-dev @graphql-codegen/cli
npm install --save-dev @graphql-codegen/typescript
npm install --save-dev @graphql-codegen/typescript-operations

# 配置文件：codegen.yml
cat > codegen.yml << 'EOF'
schema:
  - http://127.0.0.1:5001/api/graphql

documents:
  - "frontend/src/graphql/**/*.tsx"

generates:
  frontend/src/graphql/generated-types.ts:
    plugins:
      - typescript
      - typescript-operations
EOF

# 生成类型
npx graphql-codegen

# 添加到package.json scripts
cat >> frontend/package.json << 'EOF'
"scripts": {
  "generate:types": "graphql-codegen",
  "predev": "npm run generate:types"  # 开发前自动生成
}
EOF
```

**解决方案4: 更新前端使用生成的类型**
```typescript
// frontend/src/canvas/components/EventNodeBuilder.tsx
import { HqlJoinType } from '@/graphql/generated-types';

function EventNodeBuilder() {
  const [createNode] = useMutation(CREATE_EVENT_NODE);

  const handleCreate = async () => {
    // ✅ 类型安全：使用生成的枚举类型
    const result = await createNode({
      variables: {
        input: {
          nodeType: NodeType.Join,
          joinType: HqlJoinType.LeftJoin  // 枚举类型安全
        }
      }
    });
  };
}
```

### 常见错误模式

**错误1: 枚举值格式不匹配**
```typescript
// ❌ 错误：连字符 vs 下划线
joinType: "LEFT-JOIN"     // GraphQL无法解析

// ✅ 正确：使用下划线
joinType: "LEFT_JOIN"     // GraphQL标准格式
```

**错误2: Pydantic字段缺失**
```python
# ❌ 错误：Service层访问未定义的字段
class EventNodeInput(BaseModel):
    node_type: str
    # 缺少event_type字段

# Service层抛出AttributeError
event_type = node_data.event_type  # AttributeError: 'EventNodeInput' object has no attribute 'event_type'

# ✅ 正确：定义所有Service层访问的字段
class EventNodeInput(BaseModel):
    node_type: str
    event_type: Optional[str] = None
```

**错误3: 硬编码枚举字符串**
```typescript
// ❌ 错误：硬编码字符串，容易拼写错误
joinType: "LEFT_JION"  // 拼写错误

// ✅ 正确：使用graphql-codegen生成的枚举
import { HqlJoinType } from '@/graphql/generated-types';
joinType: HqlJoinType.LeftJoin  // 类型安全
```

### 代码审查清单

**GraphQL mutation检查**:
- [ ] TypeScript枚举是否完全匹配GraphQL schema（大小写敏感）？
- [ ] Pydantic模型是否包含所有Service层访问的字段？
- [ ] 是否使用graphql-codegen生成类型？
- [ ] 是否避免硬编码枚举字符串？

**集成检查**:
- [ ] 运行API契约测试：`python scripts/test/api_contract_test.py`
- [ ] 生成最新类型：`npm run generate:types`
- [ ] 测试GraphQL mutation（有效枚举值）
- [ ] 测试GraphQL mutation（无效枚举值，应失败）

### 预防措施

**自动化验证脚本**:
```bash
# scripts/test/graphql_type_sync.sh
#!/bin/bash

# 1. 生成最新类型
cd frontend
npm run generate:types

# 2. 检查TypeScript编译错误
npx tsc --noEmit

# 3. 运行GraphQL契约测试
cd ..
python scripts/test/api_contract_test.py --verify

# 4. 测试GraphQL mutations
pytest backend/tests/integration/graphql/test_mutations.py -v
```

**Pre-commit Hook**:
```bash
# .git/hooks/pre-commit
#!/bin/bash

# 检查GraphQL类型同步
cd frontend
npm run generate:types
npx tsc --noEmit
```

### 业务价值

- 避免GraphQL 400错误导致功能不可用
- 类型安全减少运行时错误
- 自动化类型生成提高开发效率
- 前后端类型一致性保证

### 案例文档

- [GraphQL 400错误深度分析](../reports/2026-03-08/GRAPHQL-400-DEEP-DIVE.md)
- [GraphQL 400最终修复报告](../reports/2026-03-08/GRAPHQL-400-FINAL-FIX.md)
- [Event Node Builder错误修复](./event-node-builder-errors.md)

---

## 自动化性能测试 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 1次 | **最后更新**: 2026-03-09 | **来源**: [性能优化完整报告](../reports/2026-03-05/PERFORMANCE-OPTIMIZATION-COMPLETE-FINAL-REPORT.md), [N+1查询优化实施](../reports/2026-03-05/P0-N+1-OPTIMIZATION-IMPLEMENTATION-REPORT.md)

### 问题现象

**症状描述**:
- 828个性能问题无法手动逐一测试和验证
- 性能优化后需要回归测试确保没有引入新问题
- 需要持续监控代码库性能指标

**影响范围**:
- 所有前端React组件
- 所有后端API端点
- 数据库查询性能

### 根本原因

**技术原因**:
1. **缺少自动化性能测试框架** - 无法自动检测性能回归
2. **AST深度分析能力不足** - 静态代码分析未覆盖所有性能问题
3. **性能基准缺失** - 没有建立性能基准线用于对比

### 解决方案

**自动化性能测试框架**:

**AST静态分析 + 运行时profiling**:
```python
# scripts/performance/automated_performance_test.py

import ast
from typing import List, Dict

class PerformanceProblemDetector(ast.NodeVisitor):
    """AST性能问题检测器"""

    def __init__(self):
        self.problems = []
        self.metrics = {
            "total_issues": 0,
            "p0_issues": 0,
            "p1_issues": 0,
            "p2_issues": 0
        }

    def detect_n_plus_1_queries(self, tree: ast.AST) -> List[Dict]:
        """检测N+1查询模式"""
        problems = []

        for node in ast.walk(tree):
            # 检测循环中的数据库查询
            if isinstance(node, ast.For):
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        func_name = self._get_function_name(child)
                        if func_name and 'fetch' in func_name.lower():
                            problems.append({
                                "type": "N+1 Query",
                                "priority": "P0",
                                "line": node.lineno,
                                "description": "Database query inside loop",
                                "suggestion": "Use JOIN or batch query"
                            })

        return problems

    def detect_missing_useCallback(self, tree: ast.AST) -> List[Dict]:
        """检测React组件中缺少useCallback的情况"""
        problems = []

        # ... 实现检测逻辑

        return problems

    def detect_missing_react_memo(self, tree: ast.AST) -> List[Dict]:
        """检测可以优化的React组件"""
        problems = []

        # ... 实现检测逻辑

        return problems

    def classify_problems(self, problems: List[Dict]) -> Dict:
        """分类和统计性能问题"""
        for problem in problems:
            self.metrics["total_issues"] += 1
            priority = problem["priority"]
            self.metrics[f"{priority.lower()}_issues"] += 1

        return self.metrics
```

**并行Worker执行模式**:
```python
# scripts/performance/parallel_performance_optimization.py

import concurrent.futures

def optimize_parallel():
    """并行性能优化 - 7个Worker同时执行"""

    # Worker任务包设计
    worker_tasks = {
        "worker_1_n_plus_1_p0": {
            "name": "P0 N+1 Query Fixes",
            "issues": 27,
            "priority": "P0",
            "strategy": "JOIN_PREFETCH"
        },
        "worker_2_n_plus_1_p1": {
            "name": "P1 N+1 Query Fixes",
            "issues": 156,
            "priority": "P1",
            "strategy": "BATCH_QUERY"
        },
        "worker_3_react_optimization": {
            "name": "React Component Optimization",
            "issues": 89,
            "priority": "P1",
            "strategy": "USE_CALLBACK_MEMO"
        },
        # ... 更多Worker
    }

    # 并行执行（7个Worker）
    with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
        futures = {
            executor.submit(optimize_worker, task_id, task_config): task_id
            for task_id, task_config in worker_tasks.items()
        }

        for future in concurrent.futures.as_completed(futures):
            task_id = futures[future]
            try:
                result = future.result()
                print(f"✅ {task_id} completed: {result}")
            except Exception as e:
                print(f"❌ {task_id} failed: {e}")

    return {
        "total_workers": 7,
        "total_issues_fixed": 828,
        "execution_time": "3.5 hours",  # vs 12 hours serial
        "improvement": "67% time reduction"
    }
```

**性能基准测试**:
```python
# scripts/performance/benchmark_test.py

import time
from functools import wraps

def benchmark(func):
    """性能基准测试装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()

        execution_time = end - start
        print(f"⏱️ {func.__name__} executed in {execution_time:.4f}s")

        # 性能基准阈值
        BENCHMARK_THRESHOLD = 1.0  # 1秒

        if execution_time > BENCHMARK_THRESHOLD:
            print(f"⚠️ WARNING: {func.__name__} exceeded threshold ({BENCHMARK_THRESHOLD}s)")
            # 记录到性能日志
            log_performance_regression(func.__name__, execution_time)

        return result
    return wrapper

@benchmark
def get_all_events_with_cache(game_gid: int) -> List[EventEntity]:
    """测试：带缓存的事件查询（目标<100ms）"""
    pass

@benchmark
def get_all_events_without_cache(game_gid: int) -> List[EventEntity]:
    """测试：不带缓存的事件查询（基准对比）"""
    pass
```

### 828个性能问题自动分类结果

**分类统计**:
```
总计: 828个性能问题
├── P0 (阻塞): 41个 (5.0%)
│   ├── N+1查询: 27个
│   ├── React性能: 8个
│   └── 数据库索引: 6个
├── P1 (重要): 503个 (60.7%)
│   ├── N+1查询: 156个
│   ├── React优化: 89个
│   ├── 批量操作: 97个
│   └── 其他优化: 161个
└── P2 (一般): 284个 (34.3%)
    ├── 代码质量: 125个
    ├── 类型注解: 89个
    └── 文档缺失: 70个
```

**并行Worker执行结果**:
```
Worker 1 (P0 N+1查询): 27个问题 → ✅ 100%成功率
Worker 2 (P1 N+1查询): 156个问题 → ✅ 100%成功率
Worker 3 (React优化): 89个问题 → ✅ 100%成功率
Worker 4 (批量操作): 97个问题 → ✅ 100%成功率
Worker 5 (代码质量): 125个问题 → ✅ 100%成功率
Worker 6 (类型注解): 89个问题 → ✅ 100%成功率
Worker 7 (文档缺失): 70个问题 → ✅ 100%成功率

总执行时间: 3.5小时（串行需要12小时）
性能提升: 67%
```

### 代码审查清单

**性能测试检查**:
- [ ] 是否运行AST静态分析检测性能问题？
- [ ] 是否使用并行Worker处理独立任务？
- [ ] 是否建立性能基准阈值？
- [ ] 是否监控性能回归？

**优化验证**:
- [ ] 所有P0问题是否已修复？
- [ ] 性能测试覆盖率是否>80%？
- [ ] 是否进行性能基准对比？
- [ ] 是否监控生产环境性能指标？

### 预防措施

**CI/CD集成**:
```yaml
# .github/workflows/performance-test.yml
name: Performance Tests

on: [pull_request]

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run AST Analysis
        run: |
          python scripts/performance/automated_performance_test.py

      - name: Run Benchmark Tests
        run: |
          pytest backend/test/performance/ --benchmark-only

      - name: Check Performance Regression
        run: |
          python scripts/performance/check_regression.py
```

### 业务价值

- 自动化检测828个性能问题（vs 手动检测≈0）
- 并行执行减少67%执行时间
- 持续监控避免性能回归
- 建立性能基准量化优化效果

### 案例文档

- [性能优化完整报告](../reports/2026-03-05/PERFORMANCE-OPTIMIZATION-COMPLETE-FINAL-REPORT.md)
- [N+1查询优化实施报告](../reports/2026-03-05/P0-N+1-OPTIMIZATION-IMPLEMENTATION-REPORT.md)
- [并行优化最终报告](../reports/2026-03-05/PARALLEL-OPTIMIZATION-FINAL-REPORT.md)

---

### 相关经验文档

- [React最佳实践 - Hooks规则](./react-best-practices.md#react-hooks-规则) - React组件测试常见问题
- [调试技能](./debugging-skills.md) - 测试失败后的调试方法
- [API设计模式 - 错误处理](./api-design-patterns.md#错误处理) - API测试方法
- [性能模式 - Dashboard实时优化](./performance-patterns.md#dashboard实时优化websocket替代轮询) - Dashboard轮询优化

---

## Chrome DevTools MCP测试流程 ⚠️ **P0极其重要 - 2026-03-13新增**

> **来源**: 9个E2E测试报告（2026-03-11至2026-03-13）
> **核心成果**: 84个E2E测试，100%功能覆盖率
> **优先级**: P0

### Chrome MCP标准测试流程

**优势**: Chrome MCP是React应用E2E测试的最佳工具
- ✅ 真实浏览器环境
- ✅ 可检测UI/UX问题
- ✅ 支持交互式调试
- ⚠️ 不触发React事件（需特殊处理）

### 标准测试流程

**步骤1: 导航到测试页面**
```javascript
// 1. 列出所有页面
mcp__chrome-devtools__list_pages()

// 2. 导航到测试页面
mcp__chrome-devtools__navigate_page({
  type: "url",
  url: "http://localhost:5173/event-node-builder?game_gid=10000147"
})
```

**步骤2: 获取页面快照**
```javascript
// 3. 获取页面快照（分析DOM结构）
mcp__chrome-devtools__take_snapshot()
```

**步骤3: 检查控制台错误**
```javascript
// 4. 检查控制台错误和警告
mcp__chrome-devtools__list_console_messages({
  types: ["error", "warn"]
})
```

**步骤4: 截图记录**
```javascript
// 5. 截图记录测试结果
mcp__chrome-devtools__take_screenshot({
  filePath: "test-output/event-node-builder-test.png",
  fullPage: true
})
```

**步骤5: 交互元素测试**
```javascript
// 6. 点击交互元素
mcp__chrome-devtools__click({ uid: "save-button" })

// 7. 填写表单（特殊处理，见下节）
```

### React与Chrome MCP兼容性处理 ⭐ **极其重要**

**问题**: Chrome MCP的`fill`操作不会触发React onChange事件
- **现象**: 使用`fill`后React state未更新
- **原因**: Chrome MCP直接设置DOM值，绕过React事件系统
- **影响**: 8个模态框组件（EventForm、AddEventModal等）

**解决方案: useEffect监听DOM值**
```typescript
import { useEffect, useRef } from 'react';

function EventForm({ initialData, onSave }) {
  const [formData, setFormData] = useState(initialData);
  const nameRef = useRef<HTMLInputElement>(null);

  // 监听DOM值变化，同步到React state
  useEffect(() => {
    if (!nameRef.current) return;

    const domValue = nameRef.current.value;
    if (domValue !== formData.name) {
      // Chrome MCP修改了DOM，同步到state
      setFormData(prev => ({ ...prev, name: domValue }));
    }
  }, [formData.name]); // 依赖formData.name，避免无限循环

  return (
    <form onSubmit={() => onSave(formData)}>
      <Input
        ref={nameRef}  // 传递ref
        label="事件名称"
        type="text"
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
      />
      <button type="submit">保存</button>
    </form>
  );
}
```

**修复模式总结**:
1. **添加refs**: 为需要Chrome MCP测试的Input组件添加ref
2. **监听DOM值**: 使用useEffect监听DOM值变化
3. **传递ref**: 将ref传递给Input组件
4. **同步state**: DOM值变化时同步到React state

**需要修复的组件**（8个）:
- EventForm（P0）
- AddEventModal（P0）
- GameManagementModal（P0）
- NodeConfigModal（P0）
- CategoryModal（P1）
- ParameterManagementModal（P1）
- TemplateSelector（P1）
- HQLPreviewModal（P1）

**不需要修复的组件**:
- 只读模态框（FieldSelectionModal、DeleteConfirmModal等）
- 确认提示模态框（ConnectionPromptModal）
- 判断标准: 是否有Input组件需要用户填写

**可复用Hook设计**:
```typescript
// frontend/src/shared/hooks/useChromeMCPFormSync.ts
export function useChromeMCPFormSync<T extends Record<string, any>>(
  formData: T,
  setFormData: (data: T) => void,
  fields: (keyof T)[]
) {
  const refs = useRef<Record<string, HTMLInputElement>>({});

  // 为每个字段创建ref
  fields.forEach(field => {
    refs.current[field as string] = useRef(null);

    useEffect(() => {
      const ref = refs.current[field as string].current;
      if (!ref) return;

      const domValue = ref.value;
      if (domValue !== formData[field]) {
        setFormData({ ...formData, [field]: domValue });
      }
    }, [formData[field]]);
  });

  return refs.current;
}

// 使用示例
function MyForm() {
  const [formData, setFormData] = useState({ name: '', email: '' });
  const refs = useChromeMCPFormSync(formData, setFormData, ['name', 'email']);

  return (
    <>
      <Input ref={refs.name} value={formData.name} />
      <Input ref={refs.email} value={formData.email} />
    </>
  );
}
```

### 100%测试覆盖率达成策略

**测试分层和优先级管理**

**测试分层**:
- **P0（48个测试）**: 核心功能，阻塞发布
  - 拖放功能: 15个测试
  - 保存/加载配置: 3个测试
  - 字段编辑/删除: 5个测试
- **P1（29个测试）**: 重要功能，影响用户体验
  - 事件切换: 5个测试
  - 字段类型: 8个测试
  - 错误处理: 6个测试
- **P2（7个测试）**: 质量保障
  - 性能测试: 3个测试
  - 安全测试: 2个测试

**功能模块覆盖**:
- 事件管理: 100%（15/15功能点）
- 字段管理: 100%（12/12功能点）
- WHERE构建器: 100%（8/8功能点）
- JOIN构建器: 100%（4/4功能点）

**测试数量统计**:
- 后端单元测试: 33个（pytest）
- E2E测试: 51个（Playwright）
- 总计: 84个测试（比之前增加180%）

### E2E测试分层策略

**按优先级分层**:

**P0测试（阻塞发布）**:
```typescript
// 拖放功能测试（15个）
describe('Event Node Builder - Drag and Drop', () => {
  test('should drag event node to canvas', async () => {
    // 1. 导航到页面
    await page.goto('http://localhost:5173/event-node-builder');

    // 2. 拖拽事件节点
    await page.dragAndDrop('#event-login', '#canvas-area');

    // 3. 验证节点已添加
    const node = await page.locator('.canvas-node[data-event-type="login"]');
    await expect(node).toBeVisible();
  });

  test('should save canvas configuration', async () => {
    // ... 实现测试
  });

  // ... 13 more tests
});
```

**P1测试（影响用户体验）**:
```typescript
// 事件切换测试（5个）
describe('Event Node Builder - Event Switching', () => {
  test('should switch between events', async () => {
    await page.selectOption('#event-select', 'login');
    await expect(page.locator('#fields-list')).toContainText('role_id');

    await page.selectOption('#event-select', 'logout');
    await expect(page.locator('#fields-list')).toContainText('logout_time');
  });

  // ... 4 more tests
});
```

**P2测试（质量保障）**:
```typescript
// 性能测试（3个）
describe('Event Node Builder - Performance', () => {
  test('should render within 2 seconds', async () => {
    const startTime = Date.now();
    await page.goto('http://localhost:5173/event-node-builder');
    const loadTime = Date.now() - startTime;

    expect(loadTime).toBeLessThan(2000);
  });

  // ... 2 more tests
});
```

### 测试遗漏分析方法

**问题**: 为什么测试没有发现滚动问题？

**根因分析**:
- ❌ 现有测试只验证元素可见性
- ❌ 没有测试滚动条是否存在
- ❌ 测试数据太少，未触发滚动条
- ❌ 只验证元素存在，不验证功能完整性

**改进: 新增滚动功能测试**:
```typescript
describe('Scrolling Functionality', () => {
  test('should show scrollbar when content exceeds height', async () => {
    // 添加大量数据触发滚动条
    await page.addScriptTag({
      content: `
        for (let i = 0; i < 100; i++) {
          addField({ name: 'field_' + i });
        }
      `
    });

    // 验证滚动条存在
    const scrollContainer = page.locator('.fields-list');
    const scrollHeight = await scrollContainer.evaluate(el => el.scrollHeight);
    const clientHeight = await scrollContainer.evaluate(el => el.clientHeight);

    expect(scrollHeight).toBeGreaterThan(clientHeight);
  });

  test('should scroll to bottom when clicking scroll-down button', async () => {
    // 点击向下滚动按钮
    await page.click('#scroll-down-button');

    // 验证已滚动到底部
    const scrollContainer = page.locator('.fields-list');
    const scrollTop = await scrollContainer.evaluate(el => el.scrollTop);
    const scrollHeight = await scrollContainer.evaluate(el => el.scrollHeight);
    const clientHeight = await scrollContainer.evaluate(el => el.clientHeight);

    expect(scrollTop + clientHeight).toBeGreaterThanOrEqual(scrollHeight - 10);
  });

  // ... 4 more tests
});
```

### 相关经验

- [TDD方法论](#tdd方法论-完整实践-⚠️-p0极其重要---2026-03-13新增) - TDD完整实践
- [React与Chrome MCP兼容性](./react-best-practices.md#chrome-mcp兼容性处理-2026-03-13新增) - React兼容性
- [测试覆盖率达成策略](./testing-guide.md#e2e测试覆盖率100达成策略-2026-03-13新增) - 覆盖率策略

---

## TDD方法论完整实践 ⚠️ **P0极其重要 - 2026-03-13新增**

> **来源**: 4个测试相关报告（TDD Red/Green Phase、测试覆盖率100%完成）
> **核心成果**: 100%功能覆盖率，84个测试
> **优先级**: P0

### Red-Green-Refactor循环

**TDD三阶段**:

**Phase 1: Red（编写失败测试）**
- **目标**: 明确需求和问题
- **原则**: 测试必须失败，证明测试有效
- **禁止**: 测试通过立即=测试无效

**Phase 2: Green（最小化修复）**
- **目标**: 最小代码使测试通过
- **原则**: 只写必要代码，不过度设计
- **禁止**: 简化实现、TODO、占位符

**Phase 3: Refactor（重构优化）**
- **目标**: 优化代码，保持测试通过
- **原则**: 保持测试100%通过
- **禁止**: 引入新功能，只重构结构

### TDD实践案例: 保存按钮禁用问题

**问题**: 节点配置模态框的保存按钮首次打开即为禁用

**Red Phase: 编写测试验证问题**
```typescript
// frontend/src/event-builder/components/modals/__tests__/NodeConfigModal.test.tsx
describe('NodeConfigModal - Save Button', () => {
  test('should enable save button when form is valid', async () => {
    render(
      <NodeConfigModal
        node={{ nodeType: 'EVENT', eventType: 'login' }}
        onSave={mockSave}
      />
    );

    const saveButton = screen.getByRole('button', { name: '保存' });

    // 期望按钮可点击
    await expect(saveButton).toBeEnabled();
  });
});
```

**测试结果**: ❌ 失败 - 按钮为禁用状态

**Green Phase: 最小化修复**
```typescript
// 问题代码
const isFormValid = () => {
  return formData.name && formData.eventType;  // ❌ name为空时返回false
};

// 最小修复：移除过早验证
const isFormValid = () => {
  // ✅ 只在提交时验证，不在首次渲染时验证
  return true;  // 简化：始终允许点击，提交时验证
};
```

**测试结果**: ✅ 通过

**Refactor Phase: 添加注释说明设计决策**
```typescript
/**
 * 表单验证策略
 *
 * 设计决策: 不在首次渲染时禁用保存按钮
 *
 * 原因:
 * 1. 用户可能只想查看配置，不修改任何字段
 * 2. 首次渲染禁用按钮会造成"无法保存"的误解
 * 3. 提交时验证比实时验证更友好
 *
 * 验证时机:
 * - ✅ 提交时验证（onSubmit）
 * - ❌ 首次渲染时验证（useEffect）
 * - ❌ 实时验证（onChange）
 */
const handleSave = () => {
  // 提交时验证
  if (!formData.name || !formData.eventType) {
    showError('请填写必填字段');
    return;
  }

  onSave(formData);
};
```

**代码量**: 1行修改，13行注释

### TDD关键原则

**1. 完整实现原则**:
> **"宁可少做，不可做半"** - 完整实现，不留TODO

```typescript
// ❌ 错误: 简化实现
function validateInput(data) {
  // TODO: 后续实现
  return true;
}

// ✅ 正确: 完整实现
function validateInput(data) {
  if (!data.name || data.name.trim() === '') {
    return { valid: false, error: 'Name is required' };
  }

  if (data.name.length > 100) {
    return { valid: false, error: 'Name too long' };
  }

  return { valid: true };
}
```

**2. 测试先行原则**:
> **NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST**

```bash
# 工作流程
1. 编写测试
2. 运行测试（必须失败）❌
3. 编写最小代码
4. 运行测试（必须通过）✅
5. 重构优化
6. 运行测试（必须保持通过）✅
```

**3. 快速反馈循环**:
```typescript
// 使用Jest watch模式
npm test -- --watch

// 修改代码后自动运行相关测试
// 快速反馈（<5秒）
```

### 测试驱动问题修复

**流程**:
1. **编写测试验证问题存在**（Red）
2. **最小化修复使测试通过**（Green）
3. **重构优化代码结构**（Refactor）

**案例: 事件节点保存后未更新**

**Red Phase**:
```typescript
test('should update node list after saving', async () => {
  const { result } = renderHook(() => useEventNodes());

  // 保存新节点
  act(() => {
    result.current.saveNode({ id: 1, name: 'New Node' });
  });

  // 验证列表已更新
  expect(result.current.nodes).toContainEqual(
    expect.objectContaining({ name: 'New Node' })
  );
});
```

**测试结果**: ❌ 失败 - 列表未更新

**Green Phase**:
```typescript
// 最小修复
const saveNode = (node) => {
  api.saveNode(node).then(saved => {
    setNodes(prev => [...prev, saved]);  // ✅ 更新列表
  });
};
```

**测试结果**: ✅ 通过

**Refactor Phase**:
```typescript
// 重构：提取为自定义Hook
function useEventNodes() {
  const [nodes, setNodes] = useState([]);

  const saveNode = useCallback((node) => {
    api.saveNode(node).then(saved => {
      setNodes(prev => [...prev, saved]);
    });
  }, []);

  return { nodes, saveNode };
}
```

### TDD检查清单

**测试编写前**:
- [ ] 明确测试目标
- [ ] 设计测试用例（正常、边界、异常）
- [ ] 准备测试数据

**测试编写**:
- [ ] 测试必须失败（Red Phase）
- [ ] 测试失败原因明确
- [ ] 测试独立可重复

**代码实现**:
- [ ] 最小代码使测试通过（Green Phase）
- [ ] 不添加额外功能
- [ ] 保持代码简单

**代码重构**:
- [ ] 测试保持100%通过
- [ ] 优化代码结构
- [ ] 不改变功能行为

### 相关经验

- [Chrome MCP测试流程](#chrome-devtools-mcp测试流程-⚠️-p0极其重要---2026-03-13新增) - E2E测试
- [测试覆盖率100%策略](#e2e测试覆盖率100达成策略-2026-03-13新增) - 覆盖率策略
- [项目管理 - 并行开发策略](./project-management.md#并行开发策略-⚠️-p0极其重要) - TDD+并行执行

---

**文档统计**:
- P0经验点：11个
- P1经验点：7个
- 总计：18个测试经验点
- 最后更新：2026-03-13 🆕 新增Chrome MCP测试流程、TDD方法论完整实践、100%测试覆盖率策略
