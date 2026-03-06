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

### 相关经验文档

- [React最佳实践 - Hooks规则](./react-best-practices.md#react-hooks-规则) - React组件测试常见问题
- [调试技能](./debugging-skills.md) - 测试失败后的调试方法
- [API设计模式 - 错误处理](./api-design-patterns.md#错误处理) - API测试方法
