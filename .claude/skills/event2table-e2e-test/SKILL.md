---
name: event2table-e2e-test
description: Interactive E2E testing system for Event2Table using Chrome DevTools MCP. Focuses on REAL USER WORKFLOW testing - discovering functional obstacles through intelligent browser interaction. Uses Chrome DevTools Protocol for deep analysis: DOM inspection, console monitoring, network request tracking, and performance measurement. NOT an automated test runner - use for interactive problem diagnosis and exploration.
---

# Event2Table E2E Testing Skill

## 🎯 Core Philosophy

> **"测试不是验证页面能加载，而是验证用户能完成任务。"**

**核心能力**:
- 🔍 **交互式诊断** - 使用Chrome DevTools MCP实时分析页面
- 🎯 **问题发现** - 专注于发现功能障碍和用户体验问题
- 📊 **深度分析** - DOM + Console + Network + Performance
- 🧠 **智能判断** - 基于观察调整测试策略
- 📝 **详细报告** - 记录发现、根因和建议

**测试深度**:
- **Page Load (20%)** - 页面是否显示
- **User Interaction (60%)** ← **核心重点** - 按钮和表单是否工作
- **Workflow Completion (20%)** - 整个功能是否完成

**工具**: Chrome DevTools MCP (mcp__chrome-devtools__*)

**不使用**: Playwright自动化测试框架（用于独立场景）

---

## Quick Start

### ⚠️ MANDATORY: 全面测试要求

**每次调用 skill 必须测试所有页面的所有功能！**

**强制覆盖页面**（11个）:
1. Dashboard (首页)
2. Events List (事件列表)
3. Events Create (创建事件)
4. Parameters List (参数列表)
5. Parameters Dashboard (参数仪表板)
6. Event Node Builder (事件节点构建器)
7. Event Nodes Management (事件节点管理)
8. Canvas (HQL构建画布)
9. Flows Management (HQL流程管理)
10. Categories Management (分类管理)
11. Common Parameters (公参管理)

**注意**:
- 游戏管理功能通过 **游戏管理模态框** 和 **添加游戏模态框** 访问
- 游戏管理模态框: 在Dashboard点击"游戏管理"按钮打开
- 添加游戏模态框: 在游戏管理模态框中点击"添加游戏"打开

**强制测试功能**（每页）:
- ✅ 页面加载 + DOM 结构
- ✅ 控制台错误检查
- ✅ 所有按钮点击测试
- ✅ 所有表单填写和提交
- ✅ 搜索/过滤功能验证
- ✅ 模态框打开/关闭
- ✅ API 调用状态验证
- ✅ 统计数据显示验证
- ✅ 分页功能测试
- ✅ 性能测量

### 基本使用

```
"全面测试Event2Table所有页面功能"  ← 推荐：测试所有页面
"测试Dashboard和Games管理功能"      ← 指定模块
"诊断事件创建流程的问题"              ← 问题诊断
"检查Canvas拖拽功能的障碍"           ← 功能验证
```

### 高级用法

```
"全面测试所有11个页面，生成详细报告"
"深度分析参数管理页面的性能和数据问题"
"诊断Canvas拖拽功能和HQL生成的完整流程"
"验证事件导入Excel的所有交互步骤"
```

---

## Testing Anti-Patterns (What NOT to Do)

### ❌ Anti-Pattern #1: Shallow Testing

```javascript
// DON'T DO THIS
test('Page loads', async () => {
  await page.goto('/events')
  expect(await page.locator('button').isVisible()).toBe(true)
  // This doesn't test if button WORKS!
})
```

**Why it's wrong**: Button exists but clicking it does nothing = bug missed!

### ✅ Correct Pattern: Workflow Testing

使用Chrome DevTools MCP的完整流程：

```javascript
// DO THIS INSTEAD
1. navigate_page({ url: '/events' })
2. take_snapshot() - 验证页面结构
3. click('导入Excel按钮')
4. wait_for('.import-dialog')
5. upload_file('test.xlsx')
6. click('导入按钮')
7. verify('.toast-success', text='导入成功')
8. check_console_errors()
9. check_network_errors()
```

**Why it's right**: Tests complete user workflow, discovers real issues.

### ❌ Anti-Pattern #2: Generic Error Messages

```javascript
// DON'T DO THIS
throw new Error('Creation failed')
// Users don't know what went wrong!
```

### ✅ Correct Pattern: Actionable Errors

```javascript
// DO THIS INSTEAD
if (response.status === 409) {
  throw new Error(`Game GID ${data.gid} already exists. Please use another GID (suggested: 90000000+)`)
}
// Users know exactly what to do!
```

---

## Chrome DevTools MCP核心能力

### 1. 页面导航和快照

```javascript
// 导航到页面
mcp__chrome-devtools__navigate_page({
  type: "url",
  url: "http://localhost:5173/#/games"
})

// 获取页面快照（DOM结构）
mcp__chrome-devtools__take_snapshot()

// 截图
mcp__chrome-devtools__take_screenshot({
  filePath: "output/screenshots/games-page.png",
  fullPage: true
})
```

### 2. 交互操作

```javascript
// 点击元素
mcp__chrome-devtools__click({ uid: "element-uid" })

// 填写表单
mcp__chrome-devtools__fill({
  uid: "input-uid",
  value: "test value"
})

// 拖拽操作
mcp__chrome-devtools__drag({
  from_uid: "draggable-uid",
  to_uid: "dropzone-uid"
})
```

### 3. 控制台监控

```javascript
// 检查错误
mcp__chrome-devtools__list_console_messages({
  types: ["error", "warn"]
})

// 获取错误详情
mcp__chrome-devtools__get_console_message({
  msgid: error_id
})
```

### 4. 网络监控

```javascript
// 列出所有请求
mcp__chrome-devtools__list_network_requests({
  resourceTypes: ["xhr", "fetch"]
})

// 获取请求详情
mcp__chrome-devtools__get_network_request({
  reqid: request_id
})
```

### 5. 性能测量

```javascript
// 执行JavaScript获取性能指标
mcp__chrome-devtools__evaluate_script({
  function: `
    () => {
      const timing = performance.timing;
      return {
        pageLoadTime: timing.loadEventEnd - timing.navigationStart,
        domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart
      };
    }
  `
})
```

---

## 标准测试流程

### Phase 1: 页面加载验证

```
1. 导航到目标页面
   → navigate_page()

2. 等待页面稳定
   → wait_for_load_state()

3. 获取页面快照
   → take_snapshot()

4. ⭐ 检查关键元素可见性（NEW）
   → verify_element_visible()
   → 检查元素不仅在DOM中，而且在视口中可见
   → 使用 evaluate_script 检查 offsetTop、offsetHeight、getBoundingClientRect()

5. 检查控制台错误
   → list_console_messages({types: ["error"]})

6. ⭐ 截图验证（NEW）
   → take_screenshot() → 保存截图
   → 检查关键元素是否在截图中可见
   → 对比预期设计与实际渲染
```

### Phase 2: 用户交互测试

```
1. 识别交互元素
   → take_snapshot() → find buttons, forms, links

2. ⭐ 验证元素可见性（NEW）
   → evaluate_script() 检查元素是否在视口内
   → 检查元素尺寸（width/height > 0）
   → 检查元素不隐藏（display !== 'none', visibility !== 'hidden'）
   → 检查元素不透明（opacity !== 0）

3. 执行交互操作
   → click() / fill() / drag()

4. 等待响应
   → wait_for_element() / wait_for_text()

5. ⭐ 验证交互结果（NEW）
   → take_screenshot() → 截图记录交互后状态
   → take_snapshot() → 验证DOM状态变化
   → evaluate_script() → 验证数据更新
   → 对比交互前后截图，确认变化符合预期

6. 检查错误
   → list_console_messages()
   → list_network_requests()
```

### Phase 3: 工作流完成验证

```
1. 执行完整用户流程
   → Series of interactions

2. 验证每个步骤
   → Continuous verification

3. 检查API调用
   → list_network_requests()

4. 验证最终状态
   → take_snapshot() + evaluate_script()

5. 生成报告
   → Compile findings
```

---

## 错误分类和处理

### 1. 页面加载错误

**症状**:
- 页面白屏
- 无限loading
- 关键元素缺失

**诊断**:
```javascript
1. take_snapshot() - 检查DOM结构
2. list_console_messages() - 检查JavaScript错误
3. list_network_requests() - 检查API调用失败
```

**常见原因**:
- React Hooks错误
- Lazy loading超时
- API返回400/500

### 2. 交互失败

**症状**:
- 点击无响应
- 表单无法提交
- 拖拽不工作

**诊断**:
```javascript
1. take_snapshot() - 检查元素是否存在
2. evaluate_script() - 检查事件监听器
3. list_console_messages() - 检查点击错误
```

**常见原因**:
- 元素选择器错误
- 事件处理程序bug
- 状态管理问题

### 3. API错误

**症状**:
- 400 Bad Request
- 404 Not Found
- 500 Internal Server Error

**诊断**:
```javascript
1. list_network_requests() - 找到失败请求
2. get_network_request() - 获取详细信息
3. 检查request headers和body
```

**常见原因**:
- 缺少必需参数
- 参数类型错误
- 后端逻辑错误

---

## 测试数据隔离

### GID范围规范

```javascript
// ✅ 正确：使用测试GID
TEST_GID_START = 90000000
TEST_GID_END = 99999999

// ❌ 错误：使用生产GID
PROD_GID = 10000147 // STAR001 - 受保护！
```

### 测试数据生成

```javascript
// 生成唯一测试GID
const generateTestGid = () => {
  return Math.floor(Math.random() * 10000000) + 90000000;
}

// 生成测试游戏数据
const generateTestGame = () => ({
  gid: generateTestGid(),
  name: `E2E测试游戏_${Date.now()}`,
  ods_db: 'ieu_ods'
})
```

---

## 性能监控

### Core Web Vitals

```javascript
// 测量LCP (Largest Contentful Paint)
mcp__chrome-devtools__evaluate_script({
  function: `
    () => {
      return new Promise((resolve) => {
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          resolve(entries[entries.length - 1].startTime);
        }).observe({ entryTypes: ['largest-contentful-paint'] });
      });
    }
  `
})
```

### 性能预算

| 指标 | 目标 | 警告 |
|------|------|------|
| **Page Load** | <3s | >5s |
| **DOM Content Loaded** | <2s | >3s |
| **API Response** | <500ms | >1s |
| **LCP** | <2.5s | >4s |

---

## 报告模板

### 测试发现报告

```markdown
## [功能名称] 测试报告

### 测试环境
- 前端: http://localhost:5173
- 后端: http://127.0.0.1:5001
- 测试时间: YYYY-MM-DD HH:MM

### 测试步骤
1. 导航到 [URL]
2. 点击 [元素]
3. 填写 [表单]
4. 提交

### 预期结果
[描述期望的行为]

### 实际结果
[描述实际发生的行为]

### 问题分析
**SEVERITY**: CRITICAL/HIGH/MEDIUM
**IMPACT**: [用户影响]

### 根本原因
[Chrome DevTools MCP诊断过程]

### 建议修复
[具体的修复建议]

### 证据
- 截图: [path]
- Console错误: [log]
- 网络请求: [details]
```

---

## Phase 2经验总结

### 1. 用户工作流测试 > 页面加载测试

**发现**: 很多"通过"的测试实际有严重的功能障碍

**示例**:
- ✅ 页面加载通过
- ❌ 点击"导入Excel"按钮没反应
- ❌ 拖拽功能不工作

**教训**: 必须测试真实用户交互，不是页面可见性

### 2. 错误消息质量 = 用户体验

**发现**: 笼统的错误消息导致用户困惑

**坏示例**:
```
❌ "Creation failed"
❌ "Invalid input"
❌ "Error occurred"
```

**好示例**:
```
✅ "Game GID 10000147 already exists. Please use another GID (suggested: 90000000+)"
✅ "Field 'game_gid' is required. Please provide a valid game GID (e.g., 10000147)"
✅ "Event 'zmpvp.vis' not found. Please check the event name or select from the list"
```

### 3. 检查代码 before 实现修复

**发现**: 很多"新问题"已经被修复

**流程**:
1. 读取相关代码
2. 检查是否已修复
3. 避免重复工作

### 4. 验证修复的完整性

**检查清单**:
- [ ] 代码已修改
- [ ] 构建成功
- [ ] E2E测试通过
- [ ] 无回归
- [ ] 文档更新

---

## 快速参考

### Chrome DevTools MCP工具

| 工具 | 用途 | 示例 |
|------|------|------|
| `navigate_page` | 导航 | 打开页面、前进、后退 |
| `take_snapshot` | DOM分析 | 获取页面结构 |
| `take_screenshot` | 视觉记录 | 保存页面截图 |
| `click` | 点击操作 | 触发按钮、链接 |
| `fill` | 表单填写 | 输入文本 |
| `drag` | 拖拽 | Canvas拖拽 |
| `list_console_messages` | Console检查 | 发现JS错误 |
| `list_network_requests` | 网络监控 | API调用分析 |
| `evaluate_script` | 自定义脚本 | 性能测量 |
| `wait_for` | 等待条件 | 元素出现、文本匹配 |

### 常用选择器策略

| 优先级 | 选择器 | 稳定性 | 示例 |
|--------|--------|--------|------|
| 1 | `data-testid` | ⭐⭐⭐⭐⭐ | 最稳定 |
| 2 | `input[name="xxx"]` | ⭐⭐⭐⭐ | 语义化 |
| 3 | `text=xxx` | ⭐⭐⭐ | 可读性好 |
| 4 | `.css-class` | ⭐ | 最不稳定 |

### 测试命令

```bash
# 启动后端
python web_app.py

# 启动前端
cd frontend && npm run dev

# 验证服务器
curl http://127.0.0.1:5001
curl http://localhost:5173
```

---

## 附录

### Playwright自动化测试（独立文档）

如果需要自动化回归测试，请参考：
- `docs/testing/playwright-automation-guide.md`
- `frontend/playwright.config.js`
- `frontend/test/e2e/smoke/`

**注意**: Playwright是独立的自动化测试框架，不是Chrome DevTools MCP skill的一部分。

### 相关文档

- Phase 2经验: `docs/testing/phase2-lessons-learned.md`
- 测试指南: `docs/testing/e2e-testing-guide.md`
- 快速测试: `docs/testing/quick-test-guide.md`

---

## ⚠️ MANDATORY: 全面测试执行标准

**每次调用 skill 必须遵循以下标准**:

### 1. 页面覆盖要求

**必须测试所有11个页面**，不可跳过：
1. Dashboard (首页)
2. Events List (事件列表)
3. Events Create (创建事件)
4. Parameters List (参数列表)
5. Parameters Dashboard (参数仪表板)
6. Event Node Builder (事件节点构建器)
7. Event Nodes Management (事件节点管理)
8. Canvas (HQL构建画布)
9. Flows Management (HQL流程管理)
10. Categories Management (分类管理)
11. Common Parameters (公参管理)

**注意**: 游戏管理功能通过模态框访问,不在独立页面测试

### 2. 功能测试要求

**每个页面必须测试以下10项功能**：
- ✅ 页面加载 + DOM 结构验证
- ✅ 控制台错误检查（`list_console_messages`）
- ✅ 所有按钮点击测试
- ✅ 所有表单填写和提交
- ✅ 搜索/过滤功能验证
- ✅ 模态框打开/关闭
- ✅ API 调用状态验证（`list_network_requests`）
- ✅ 统计数据显示验证
- ✅ 分页功能测试
- ✅ 性能测量（`evaluate_script`）

### 3. 问题记录要求

**发现所有问题，按优先级分类**：
- **P0** - 阻塞性问题（页面崩溃、无响应）
- **P1** - 高优先级（功能不工作、数据错误）
- **P2** - 中优先级（UI问题、性能问题）
- **P3** - 低优先级（优化建议）

### 4. 报告生成要求

**生成完整测试报告**，包含：
- 所有11个页面的测试结果
- 每页10项功能的验证状态
- 所有发现的问题（P0-P3）
- API调用状态汇总
- 性能数据汇总
- 修复建议

### 5. 禁止行为

❌ **禁止**:
- 跳过任何页面
- 只测试页面加载，不测试交互
- 忽略控制台错误
- 不验证搜索功能
- 不检查统计数据
- 只报告通过的项目

### 6. 测试模板

使用以下模板生成报告：
- `.claude/skills/event2table-e2e-test/templates/comprehensive-test-report.md`

---

## ⚠️ 元素可见性验证规范 (CRITICAL)

> **🚨 基于用户反馈的测试方法改进**
>
> **用户问题**: "当前游戏管理页面的游戏卡牌card实际不可视，但是测试并没有发现问题"
>
> **根本原因**: `take_snapshot()` 只检查元素是否在DOM中存在，不检查元素是否在用户视口中实际可见

### 可见性验证三要素

**1. DOM存在性** - 元素在DOM树中
**2. CSS可见性** - 元素不被隐藏
**3. 视口位置** - 元素在用户可见区域内

### 标准可见性检查流程

```javascript
// 步骤1: 检查元素在DOM中存在
const snapshot = await mcp__chrome-devtools__take_snapshot();
const elementExists = snapshot.elements.some(el => el.text.includes('游戏名称'));

if (!elementExists) {
  // FAIL: 元素不存在
  return { status: 'fail', reason: 'Element not found in DOM' };
}

// 步骤2: 检查元素CSS可见性
const visibilityCheck = await mcp__chrome-devtools__evaluate_script({
  function: `
    (selector) => {
      const elements = document.querySelectorAll(selector);
      if (elements.length === 0) return { visible: false, reason: 'Element not found' };

      const element = elements[0];
      const styles = window.getComputedStyle(element);
      const rect = element.getBoundingClientRect();

      // 检查CSS隐藏
      if (styles.display === 'none') {
        return { visible: false, reason: 'display: none' };
      }
      if (styles.visibility === 'hidden') {
        return { visible: false, reason: 'visibility: hidden' };
      }
      if (styles.opacity === '0') {
        return { visible: false, reason: 'opacity: 0' };
      }

      // 检查元素尺寸
      if (rect.width === 0 || rect.height === 0) {
        return { visible: false, reason: 'Zero size', rect };
      }

      // 检查是否在视口内
      const inViewport = (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= window.innerHeight &&
        rect.right <= window.innerWidth
      );

      if (!inViewport) {
        return { visible: false, reason: 'Outside viewport', rect };
      }

      return {
        visible: true,
        reason: 'Fully visible',
        rect,
        styles: {
          display: styles.display,
          visibility: styles.visibility,
          opacity: styles.opacity
        }
      };
    }
  `,
  args: [{ selector: '.game-card' }]
});

// 步骤3: 截图验证
await mcp__chrome-devtools__take_screenshot({
  filePath: 'output/screenshots/games-list-visibility-check.png',
  fullPage: true
});

// 步骤4: 综合判断
if (!visibilityCheck.visible) {
  return {
    status: 'fail',
    reason: `Element not visible: ${visibilityCheck.reason}`,
    details: visibilityCheck
  };
}

return {
  status: 'pass',
  message: 'Element is visible and accessible to user',
  details: visibilityCheck
};
```

### 截图对比验证

**交互前截图** → **交互操作** → **交互后截图** → **对比验证**

```javascript
// 1. 交互前截图
await mcp__chrome_devtools__take_screenshot({
  filePath: 'output/screenshots/before-interaction.png',
  fullPage: false // 仅视口区域
});

// 2. 执行交互
await mcp__chrome_devtools__fill({
  uid: 'search-input',
  value: 'STAR'
});

// 3. 等待响应（重要：等待足够时间）
await new Promise(resolve => setTimeout(resolve, 500)); // 至少500ms

// 4. 交互后截图
await mcp__chrome_devtools__take_screenshot({
  filePath: 'output/screenshots/after-interaction.png',
  fullPage: false
});

// 5. 验证状态变化
const gameCountAfter = await mcp__chrome_devtools__evaluate_script({
  function: `
    () => document.querySelectorAll('.game-card').length
  `
});

if (gameCountAfter === 0) {
  return {
    status: 'fail',
    reason: 'Search returned 0 results - possible filtering bug',
    screenshot: 'output/screenshots/after-interaction.png'
  };
}
```

### 常见可见性问题

| 问题 | 症状 | 检测方法 |
|------|------|---------|
| **display: none** | 元素不渲染 | `getComputedStyle(el).display === 'none'` |
| **visibility: hidden** | 元素占位但不可见 | `getComputedStyle(el).visibility === 'hidden'` |
| **opacity: 0** | 元素完全透明 | `getComputedStyle(el).opacity === '0'` |
| **Zero size** | 元素尺寸为0 | `rect.width === 0 \|\| rect.height === 0` |
| **Outside viewport** | 元素在视口外 | `rect.bottom < 0 \|\| rect.top > window.innerHeight` |
| **Z-index buried** | 元素被遮挡 | 需要检查父元素z-index |
| **Overflow hidden** | 父元素裁剪 | 检查父元素 `overflow` 属性 |

### 测试检查清单

**每个关键元素必须验证**：
- [ ] 元素在DOM中存在 (`take_snapshot()`)
- [ ] 元素CSS可见 (`evaluate_script()` + `getComputedStyle()`)
- [ ] 元素尺寸 > 0 (`getBoundingClientRect()`)
- [ ] 元素在视口内 (`getBoundingClientRect()` + viewport check)
- [ ] 元素可交互 (可点击元素)
- [ ] 截图保存用于视觉验证
- [ ] 交互前后状态对比

---

## 🔬 补充测试经验 (2026-02-21)

### 基于实际测试的补充要求

**测试报告**: `docs/reports/2026-02-21/e2e-supplementary-test-report.md`

### 1. 按钮点击完整性测试标准

**必须测试的按钮类型**:
- ✅ **导航按钮** - Dashboard卡片、侧边栏链接
- ✅ **操作按钮** - 查看、编辑、删除
- ✅ **功能按钮** - 新增、导入、导出、批量操作
- ✅ **分页按钮** - 首页、末页、页码、每页显示
- ✅ **模态框按钮** - 打开、关闭、取消、保存

**测试方法**:
```javascript
// 1. 点击按钮
mcp__chrome-devtools__click({ uid: "button-uid" })

// 2. 验证响应（3种可能响应）
// A. 导航跳转
take_snapshot() → 检查URL变化

// B. 模态框打开
take_snapshot() → 检查dialog元素存在

// C. 页面状态更新
take_snapshot() → 检查数据变化
```

**通过标准**:
- 点击后有明确响应（导航、模态框、状态变化）
- 无控制台错误
- 响应时间<2秒

### 2. 模态框交互完整测试标准

**测试流程**:
```javascript
// 1. 打开模态框
click("打开按钮")
take_snapshot() → 验证dialog存在

// 2. 测试模态框内功能（如果适用）
click("模态框内按钮")
take_snapshot() → 验证内嵌dialog或状态变化

// 3. 测试表单验证
click("保存") // 不填必填字段
take_snapshot() → 验证模态框保持打开（验证生效）

// 4. 测试关闭功能
click("取消") 或 press_key("Escape")
take_snapshot() → 验证dialog关闭
```

**支持的模态框类型**:
- **单层模态框** - 游戏管理、分类管理
- **嵌套模态框** - 游戏管理 → 添加游戏（已验证支持）

### 3. 分页功能完整测试标准

**必须测试的分页场景**:
```javascript
// 1. 翻页测试
click("第2页")
take_snapshot() → 验证数据变化（显示第11-20条）

click("首页")
take_snapshot() → 验证返回第1页

// 2. 每页显示数量切换（如果支持）
click("每页显示下拉框")
select("20")
take_snapshot() → 验证每页显示20条

// 3. 分页信息验证
evaluate_script(() => document.querySelector('.pagination-info').textContent)
// 应显示: "显示第 X 到 Y 条， 共 Z 条"
```

**通过标准**:
- 翻页后数据正确更新
- 分页信息准确
- 页码按钮状态正确（当前页disabled）

### 4. 表单验证规则测试标准

**必须测试的验证场景**:
```javascript
// 场景1: 空字段提交
fill("必填字段", "")
click("保存")
→ 预期: 表单保持打开，显示验证错误

// 场景2: 无效数据格式
fill("GID", "abc") // 应该是数字
click("保存")
→ 预期: 显示格式错误提示

// 场景3: 重复数据
fill("GID", "10000147") // 已存在
click("保存")
→ 预期: 显示"游戏GID已存在"错误

// 场景4: 成功提交
fill("所有字段", "valid data")
click("保存")
→ 预期: 关闭模态框，显示成功提示，数据更新
```

**验证检查点**:
- [ ] 必填字段标记*可见
- [ ] placeholder提示文字正确
- [ ] 空字段提交被阻止
- [ ] 错误提示清晰可读
- [ ] 成功提交后数据更新

### 5. 统计数据准确性验证标准

**Dashboard统计验证**:
```javascript
// 获取Dashboard显示的统计数据
const stats = {
  games: parseInt(document.querySelector('.games-count').textContent),
  events: parseInt(document.querySelector('.events-count').textContent),
  parameters: parseInt(document.querySelector('.parameters-count').textContent)
}

// 导航到对应页面验证
navigate_to("/games")
const actualGames = countItems(".game-card")
assert(stats.games === actualGames, "游戏总数应匹配")
```

**验证方法**:
- **交叉验证** - Dashboard统计 vs 列表页实际数量
- **API验证** - 页面显示 vs API返回
- **实时性** - 创建/删除后统计是否更新

### 6. 错误处理测试标准

**必须测试的错误场景**:
```javascript
// 1. 网络错误
// (需要mock或断网测试)

// 2. 服务器错误500
// 检查控制台是否有API错误

// 3. 业务逻辑错误409
// 提交重复数据 → 应显示友好错误提示

// 4. 权限错误403
// 访问无权限资源 → 应显示权限错误
```

**错误提示质量标准**:
- ✅ **好**: "游戏GID 10000147已存在，请使用其他GID（建议90000000+）"
- ❌ **坏**: "创建失败"
- ❌ **坏**: "Invalid input"

**错误检查流程**:
```javascript
// 1. 执行可能出错的操作
click("删除按钮")

// 2. 检查确认对话框
take_snapshot() → 查找ConfirmDialog

// 3. 确认删除
click("确认")

// 4. 检查结果
list_console_messages() → 无新错误
list_network_requests() → API返回200或显示Toast
```

### 7. UX用户体验测试标准 ⚠️ **极其重要**

> **🚨 2026-02-21 新增**: 发现并修复游戏管理模态框UX问题
>
> **根本原因**: BaseModal的`size="full"`未正确应用，导致模态框宽度只有500px

**核心能力**：验证界面布局、视觉层次、可读性和交互体验

#### 7.1 模态框尺寸测试

**测试方法**:
```javascript
// 1. 打开模态框
click("游戏管理")

// 2. 测量模态框尺寸
const modal = document.querySelector('[role="dialog"]');
const rect = modal.getBoundingClientRect();
const style = window.getComputedStyle(modal);

// 3. 验证尺寸标准
const metrics = {
  modalWidth: rect.width,
  modalHeight: rect.height,
  maxWidth: style.maxWidth,
  minWidth: style.minWidth
};

// 4. 判断UX质量
if (metrics.modalWidth < 800) {
  return {
    status: 'FAIL',
    issue: '模态框太窄，内容拥挤',
    currentWidth: metrics.modalWidth,
    recommendedWidth: '1200-1400px'
  };
}
```

**通过标准**:
- 游戏管理模态框宽度 ≥ 1200px
- 列表页面板宽度 ≥ 400px
- 详情面板有足够空间显示所有字段
- 内容间距充足（padding ≥ 16px）

#### 7.2 内容可读性测试

**测试项**:
```javascript
// 1. 检查文字大小和行高
const gameItems = document.querySelectorAll('.game-list-item');
const firstItem = gameItems[0];
const itemStyle = window.getComputedStyle(firstItem);

return {
  fontSize: itemStyle.fontSize,
  lineHeight: itemStyle.lineHeight,
  padding: itemStyle.padding,
  minHeight: itemStyle.minHeight,
  // 建议值
  recommended: {
    fontSize: '14px+',
    lineHeight: '1.4-1.6',
    padding: '12px+',
    minHeight: '56px+'
  }
};
```

**通过标准**:
- 游戏列表项高度 ≥ 56px（易于点击）
- 文字大小 ≥ 13px
- 行高 ≥ 1.4（可读性好）
- 内边距 ≥ 12px（内容不拥挤）

#### 7.3 视觉层次测试

**测试项**:
```javascript
// 1. 检查颜色对比度
const panels = document.querySelectorAll('.game-list-panel, .game-detail-panel');
const backgrounds = Array.from(panels).map(panel => ({
  background: window.getComputedStyle(panel).backgroundColor,
  color: window.getComputedStyle(panel).color
}));

// 2. 检查边框和分隔
const hasBorders = Array.from(panels).some(panel => {
  const style = window.getComputedStyle(panel);
  return style.borderTop || style.borderBottom || style.borderRight;
});

// 3. 检查阴影效果
const hasShadows = document.querySelectorAll('.modal-content').length > 0;
```

**通过标准**:
- 面板之间有明确的视觉分隔（边框/间距）
- 使用一致的背景色方案
- 模态框有阴影效果（提升层次感）

#### 7.4 交互可用性测试

**测试项**:
```javascript
// 1. 测试列表项点击响应
const gameItems = document.querySelectorAll('.game-list-item');
gameItems.forEach((item, index) => {
  item.click();

  // 检查是否有选中状态
  const isActive = item.classList.contains('active');

  // 检查右侧详情是否更新
  const detailPanel = document.querySelector('.game-detail-panel');
  const hasContent = detailPanel.querySelector('.form-group');

  if (!isActive || !hasContent) {
    return {
      status: 'FAIL',
      issue: `游戏项 ${index} 点击无响应`,
      itemIndex: index
    };
  }
});
```

**通过标准**:
- 点击游戏项立即显示选中状态
- 右侧详情面板内容立即更新
- 无延迟或卡顿

#### 7.5 响应式布局测试

**测试方法**:
```javascript
// 1. 测试不同屏幕尺寸
const viewports = [
  { width: 1920, height: 1080 }, // 桌面
  { width: 1400, height: 900 },  // 小屏幕
  { width: 768, height: 1024 }   // 平板
];

for (const viewport of viewports) {
  // 调整浏览器窗口大小
  await mcp__chrome_devtools__emulate({
    viewport: { width: viewport.width, height: viewport.height }
  });

  // 检查布局是否正常
  const snapshot = await mcp__chrome_devtools__take_snapshot();
  // 验证无元素重叠或溢出
}
```

**通过标准**:
- 桌面、小屏幕、平板都能正常显示
- 移动端布局正确切换（flex-direction: column）
- 无水平滚动条

#### 7.6 滚动性能测试

**测试方法**:
```javascript
// 1. 测试列表滚动性能
const gameList = document.querySelector('.game-list');
const startTime = performance.now();

gameList.scrollTop = 1000; // 快速滚动
gameList.scrollTop = 0;     // 滚回顶部

const endTime = performance.now();
const scrollDuration = endTime - startTime;

// 2. 检查滚动是否流畅
if (scrollDuration > 100) {
  return {
    status: 'WARNING',
    issue: '滚动性能不佳',
    duration: scrollDuration,
    recommendation: '使用虚拟滚动优化'
  };
}
```

**通过标准**:
- 滚动响应时间 < 100ms
- 无明显卡顿或掉帧
- 86个游戏项流畅滚动

#### 7.7 空间利用率测试

**测试方法**:
```javascript
// 1. 检查空间利用效率
const modal = document.querySelector('[role="dialog"]');
const contentWidth = modal.getBoundingClientRect().width;
const usedWidth = Array.from(modal.querySelectorAll('.game-list-panel, .game-detail-panel'))
  .reduce((sum, panel) => sum + panel.getBoundingClientRect().width, 0);

const utilization = (usedWidth / contentWidth) * 100;

// 2. 检查是否有过大空白
const whitespace = 100 - utilization;

if (whitespace > 40) {
  return {
    status: 'WARNING',
    issue: '空间利用率低',
    utilization: `${utilization.toFixed(1)}%`,
    whitespace: `${whitespace.toFixed(1)}%`,
    recommendation: '增加面板宽度或添加更多功能'
  };
}
```

**通过标准**:
- 空间利用率 ≥ 70%
- 左右面板比例合理（列表:详情 = 1:2 到 1:3）
- 无过大的空白区域

#### 常见UX问题

| 问题 | 症状 | 检测方法 |
|------|------|---------|
| **模态框太窄** | 宽度<800px | 检查modal元素宽度 |
| **内容拥挤** | padding<12px | 检查元素padding |
| **列表项太小** | 高度<56px | 检查列表项minHeight |
| **文字太小** | font-size<13px | 检查文字大小 |
| **对比度不足** | 难以阅读 | 检查颜色对比度 |
| **滚动卡顿** | >100ms延迟 | 性能测量 |
| **响应式断裂** | 移动端布局错误 | 不同屏幕测试 |

#### UX测试检查清单

**每个模态框必须验证**：
- [ ] 尺寸适合内容（宽度≥800px for游戏管理）
- [ ] 内容间距充足（padding≥16px）
- [ ] 文字大小可读（≥13px）
- [ ] 列表项易于点击（高度≥56px）
- [ ] 视觉层次清晰（边框、背景、阴影）
- [ ] 滚动性能良好（<100ms响应）
- [ ] 响应式布局正常
- [ ] 空间利用合理（≥70%）

#### UX问题记录格式

```markdown
## UX问题：[问题名称]

**严重程度**: P1/P2/P3
**发现页面**: [页面名称]
**具体位置**: [组件或元素]

**问题描述**:
- **当前状态**: [描述当前问题]
- **影响用户**: [描述用户影响]
- **复现步骤**: [如何复现]

**测量数据**:
- 模态框宽度: [实际值] px
- 推荐宽度: [建议值] px
- 内容间距: [实际值] px
- 列表项高度: [实际值] px

**建议修复**:
1. [具体修复步骤1]
2. [具体修复步骤2]

**修复后验证**:
- [ ] 尺寸符合要求
- [ ] 内容可读性提升
- [ ] 用户满意度改善
```

---

## 📊 100%测试覆盖率要求

### 页面覆盖率: 13/13 (100%)

### 每页功能覆盖率: 10/10 (100%)

| 功能项 | Dashboard | Games | Events | Parameters | Others |
|--------|----------|-------|--------|-----------|--------|
| 1. 页面加载 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 2. 控制台错误 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 3. 按钮点击 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 4. 表单填写提交 | N/A | ✅ | ✅ | N/A | ⚠️ |
| 5. 搜索过滤 | N/A | ✅ | ✅ | ✅ | ⚠️ |
| 6. 模态框开关 | ⚠️ | ✅ | ⚠️ | ⚠️ | ⚠️ |
| 7. API调用 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 8. 统计数据 | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ |
| 9. 分页功能 | N/A | ✅ | ✅ | ✅ | N/A |
| 10. 性能测量 | ❌ | ❌ | ❌ | ❌ | ❌ |

**图例**: ✅已测试 | ⚠️部分测试 | ❌未测试 | N/A不适用

### 未完成测试项（需补充）

**P1 - 高优先级**:
1. **表单完整提交流程** - 填写所有字段并成功提交
2. **模态框关闭操作** - 取消/ESC/点击外部
3. **删除确认对话框** - 完整删除流程
4. **统计数据实时更新** - 创建后统计是否更新

**P2 - 中优先级**:
5. **每页显示数量切换** - 10/20/50/100
6. **搜索后翻页** - 搜索结果的分页
7. **编辑功能** - 完整编辑流程
8. **图片上传** - 如果有

**P3 - 低优先级**:
9. **性能基准测试** - Page Load、LCP等
10. **跨页面流程** - 完整用户工作流

---

## 测试执行检查清单

### 开始测试前
- [ ] 前端服务器运行 (`npm run dev`)
- [ ] 后端服务器运行 (`python web_app.py`)
- [ ] Chrome DevTools MCP可用
- [ ] 测试数据已准备 (GID 90000000+)

### 测试执行中
- [ ] 11个页面全部访问
- [ ] 每页10项功能全部测试
- [ ] 所有发现的错误记录
- [ ] 截图保存关键步骤

### 测试完成后
- [ ] 生成测试报告
- [ ] 问题按P0-P3分类
- [ ] 提供修复建议
- [ ] 验证修复后重新测试

---

**Skill Version**: 2.4 (100% Coverage Requirements)
**Last Updated**: 2026-02-21
**Status**: Production Ready
**Maintainer**: Event2Table Development Team
