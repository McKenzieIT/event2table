# Chrome DevTools MCP 控制台日志捕获完整指南

**文档版本**: 1.0
**创建日期**: 2026-03-07
**适用工具**: chrome-devtools-mcp
**MCP服务器**: chrome-devtools-mcp@latest

---

## 📋 概述

本文档详细说明如何使用Chrome DevTools MCP的`list_console_messages`功能来捕获浏览器控制台的所有错误、警告和信息。

---

## 🔧 MCP配置要求

### 1. 检查MCP服务器配置

**配置文件位置**: `.claude/config.json`

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "-y",
        "chrome-devtools-mcp@latest"
      ]
    }
  }
}
```

### 2. 验证MCP可用性

在Claude Code中测试工具是否可用：

```bash
# 测试基础工具
mcp__chrome-devtools__list_pages

# 预期结果：返回Chrome页面列表
# 如果报错：需要重新启动VSCode
```

### 3. 重新加载VSCode（如果MCP不可用）

```bash
# 1. 完全关闭VSCode
# 2. 重新打开项目
# 3. MCP服务器会自动加载
```

---

## 🎯 核心工具使用

### 工具1: list_console_messages

**功能**: 列出控制台的所有消息

**参数**:
```typescript
{
  types?: ("error" | "warn" | "info" | "log" | "debug")[],
  since?: number  // 时间戳，获取该时间之后的消息
}
```

**使用示例**:

```javascript
// 获取所有错误
mcp__chrome-devtools__list_console_messages({
  types: ["error"]
})

// 获取错误和警告
mcp__chrome-devtools__list_console_messages({
  types: ["error", "warn"]
})

// 获取所有类型的消息
mcp__chrome-devtools__list_console_messages({})

// 获取最近的消息（使用时间戳）
mcp__chrome-devtools__list_console_messages({
  types: ["error"],
  since: Date.now() - 5000  // 最近5秒
})
```

**返回格式**:
```typescript
{
  messages: Array<{
    id: string;           // 消息ID
    type: string;         // "error" | "warn" | "info" | "log"
    timestamp: number;    // 时间戳
    text: string;         // 消息文本
    url?: string;         // 来源URL
    line?: number;        // 行号
    column?: number;      // 列号
    stackTrace?: string;  // 堆栈跟踪（错误）
  }>
}
```

---

### 工具2: get_console_message

**功能**: 获取单个消息的详细信息

**参数**:
```typescript
{
  msgid: string;  // 消息ID
}
```

**使用示例**:

```javascript
// 假设从list_console_messages获取到消息ID为"msg-123"
const message = mcp__chrome-devtools__get_console_message({
  msgid: "msg-123"
})

// 返回详细信息，包括完整堆栈跟踪
```

---

## 📊 完整测试流程

### 标准E2E测试 + 控制台错误检测流程

```javascript
// 步骤1: 导航到页面
mcp__chrome-devtools__navigate_page({
  type: "url",
  url: "http://localhost:5173/#/events"
})

// 步骤2: 等待页面加载
// （根据页面复杂度等待2-5秒）

// 步骤3: 获取页面加载时的控制台错误
const initialErrors = mcp__chrome-devtools__list_console_messages({
  types: ["error", "warn"]
})

// 步骤4: 测试交互（如点击按钮）
mcp__chrome-devtools__click({ uid: "button-uid" })

// 步骤5: 等待响应
// （等待1-2秒）

// 步骤6: 获取交互后的新错误
const afterClickErrors = mcp__chrome-devtools__list_console_messages({
  types: ["error"],
  since: Date.now() - 3000  // 最近3秒
})

// 步骤7: 对比前后错误，识别交互引发的新错误
const newErrors = afterClickErrors.messages.filter(
  err => !initialErrors.messages.some(init => init.id === err.id)
)

// 步骤8: 获取错误详情
if (newErrors.length > 0) {
  for (const error of newErrors) {
    const details = mcp__chrome-devtools__get_console_message({
      msgid: error.id
    })
    console.log(`Error Details:`, details)
  }
}
```

---

## 🎯 11页面控制台测试脚本

### 完整的自动化测试脚本（伪代码）

```javascript
// 所有11个页面的路由
const pages = [
  { name: "Dashboard", url: "http://localhost:5173/" },
  { name: "Events List", url: "http://localhost:5173/#/events" },
  { name: "Events Create", url: "http://localhost:5173/#/events/create" },
  { name: "Parameters List", url: "http://localhost:5173/#/parameters" },
  { name: "Parameter Dashboard", url: "http://localhost:5173/#/parameter-dashboard" },
  { name: "Event Node Builder", url: "http://localhost:5173/#/event-node-builder" },
  { name: "Event Nodes Management", url: "http://localhost:5173/#/event-nodes" },
  { name: "Canvas", url: "http://localhost:5173/#/canvas" },
  { name: "Flows Management", url: "http://localhost:5173/#/flows" },
  { name: "Categories Management", url: "http://localhost:5173/#/categories" },
  { name: "Common Parameters", url: "http://localhost:5173/#/common-params" }
]

const allErrors = {}

// 对每个页面进行测试
for (const page of pages) {
  console.log(`Testing page: ${page.name}`)

  // 1. 导航到页面
  mcp__chrome-devtools__navigate_page({
    type: "url",
    url: page.url
  })

  // 2. 等待页面完全加载
  // （实际实现中需要根据页面复杂度调整等待时间）

  // 3. 获取控制台错误
  const errors = mcp__chrome-devtools__list_console_messages({
    types: ["error", "warn"]
  })

  // 4. 记录错误
  allErrors[page.name] = {
    url: page.url,
    errors: errors.messages || [],
    errorCount: (errors.messages || []).length
  }

  // 5. 如果有错误，获取详细信息
  if (errors.messages && errors.messages.length > 0) {
    for (const error of errors.messages) {
      const details = mcp__chrome-devtools__get_console_message({
        msgid: error.id
      })
      allErrors[page.name].details = allErrors[page.name].details || []
      allErrors[page.name].details.push(details)
    }
  }
}

// 6. 生成报告
console.log("=== Console Errors Report ===")
for (const [pageName, pageData] of Object.entries(allErrors)) {
  console.log(`\n${pageName} (${pageData.url}):`)
  console.log(`  Errors: ${pageData.errorCount}`)

  if (pageData.errorCount > 0) {
    pageData.details.forEach((detail, index) => {
      console.log(`  Error ${index + 1}:`)
      console.log(`    Type: ${detail.type}`)
      console.log(`    Text: ${detail.text}`)
      console.log(`    URL: ${detail.url}`)
      console.log(`    Line: ${detail.line}`)
      console.log(`    Stack: ${detail.stackTrace}`)
    })
  }
}
```

---

## 🔍 错误分类和分析

### 常见错误类型

#### 1. React Errors
```javascript
// 典型React错误
{
  type: "error",
  text: "Uncaught Error: Rendered more hooks than during the previous render",
  url: "http://localhost:5173/assets/index.js",
  line: 1234,
  stackTrace: "..."
}
```

#### 2. GraphQL Errors
```javascript
// GraphQL查询错误
{
  type: "error",
  text: "[GraphQL] Failed to fetch",
  url: "http://127.0.0.1:5001/graphql",
  stackTrace: null
}
```

#### 3. Network Errors
```javascript
// 网络请求失败
{
  type: "error",
  text: "Failed to load resource: the server responded with status 500",
  url: "http://127.0.0.1:5001/api/categories",
  stackTrace: null
}
```

#### 4. TypeScript/Build Errors
```javascript
// TypeScript类型错误
{
  type: "warn",
  text: "TS2345: Argument of type 'string' is not assignable to parameter of type 'number'",
  url: "http://localhost:5173/assets/index.js",
  line: 5678
}
```

### 错误严重程度分类

| 严重程度 | 类型 | 说明 |
|---------|------|------|
| **P0** | `error` | 导致功能失效的错误 |
| **P1** | `warn` | 可能导致问题的警告 |
| **P2** | `info` | 信息性提示 |
| **P3** | `log`, `debug` | 调试信息 |

---

## 💡 最佳实践

### 1. 页面加载等待策略

```javascript
// ❌ 错误：不等待页面加载
mcp__chrome-devtools__navigate_page({ type: "url", url: "..." })
const errors = mcp__chrome-devtools__list_console_messages({ types: ["error"] })
// 可能错过异步加载的错误

// ✅ 正确：等待页面稳定
mcp__chrome-devtools__navigate_page({ type: "url", url: "..." })

// 等待方法1: 使用wait_for
mcp__chrome-devtools__wait_for({
  selector: "main",
  timeout: 5000
})

// 等待方法2: 使用await_element
mcp__chrome-devtools__await_element({
  selector: "[data-testid='dashboard-container']",
  timeout: 5000
})

// 等待方法3: 使用evaluate_script检查React是否完成
mcp__chrome-devtools__evaluate_script({
  function: "() => document.readyState === 'complete'"
})

// 然后获取错误
const errors = mcp__chrome-devtools__list_console_messages({ types: ["error"] })
```

### 2. 交互后错误捕获

```javascript
// ✅ 完整的交互测试流程

// 记录交互前的错误基线
const baselineErrors = mcp__chrome-devtools__list_console_messages({
  types: ["error"]
})
const baselineErrorIds = new Set(baselineErrors.messages.map(e => e.id))

// 执行交互
mcp__chrome-devtools__click({ uid: "button-uid" })

// 等待响应
mcp__chrome-devtools__await_text({
  text: "操作成功",
  timeout: 3000
})

// 获取交互后的错误
const afterErrors = mcp__chrome-devtools__list_console_messages({
  types: ["error"]
})

// 识别新增的错误
const newErrors = afterErrors.messages.filter(
  err => !baselineErrorIds.has(err.id)
)

// 分析新错误
if (newErrors.length > 0) {
  console.log(`⚠️ Clicking button caused ${newErrors.length} new errors:`)
  newErrors.forEach(err => {
    console.log(`  - ${err.text}`)
  })
}
```

### 3. 性能监控与控制台错误结合

```javascript
// 同时监控性能和控制台错误

// 导航到页面
mcp__chrome-devtools__navigate_page({
  type: "url",
  url: "http://localhost:5173/#/events"
})

// 等待页面加载完成
mcp__chrome-devtools__wait_for({
  selector: "main",
  timeout: 5000
})

// 获取性能指标
const performance = mcp__chrome-devtools__evaluate_script({
  function: `
    () => {
      const timing = performance.timing;
      return {
        pageLoadTime: timing.loadEventEnd - timing.navigationStart,
        domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
        domComplete: timing.domComplete - timing.navigationStart
      };
    }
  `
})

// 获取控制台错误
const errors = mcp__chrome-devtools__list_console_messages({
  types: ["error", "warn"]
})

// 综合分析
console.log(`Page Performance:`)
console.log(`  Load Time: ${performance.pageLoadTime}ms`)
console.log(`  DOM Content Loaded: ${performance.domContentLoaded}ms`)
console.log(`  Console Errors: ${(errors.messages || []).length}`)

// 如果页面加载慢且有错误，可能有关联
if (performance.pageLoadTime > 3000 && (errors.messages || []).length > 0) {
  console.log(`⚠️ Slow page load (${performance.pageLoadTime}ms) with errors:`)
  errors.messages.forEach(err => console.log(`  - ${err.text}`))
}
```

---

## 📝 报告生成模板

### Markdown报告模板

```markdown
## 控制台错误测试报告

### 测试环境
- **日期**: YYYY-MM-DD
- **浏览器**: Chrome/Chromium
- **测试工具**: chrome-devtools-mcp
- **测试页面**: 11个

### 页面错误汇总

| 页面 | 错误数 | 警告数 | 状态 |
|------|--------|--------|------|
| Dashboard | X | Y | ⚠️ |
| Events List | X | Y | ✅ |
| ... | ... | ... | ... |

### 详细错误列表

#### Dashboard (/)

**错误1: [类型] 消息文本**
- **类型**: error/warn/info
- **文件**: URL
- **行号**: Line:Column
- **堆栈**:
  ```
  Stack trace here
  ```
- **修复建议**: [具体建议]

#### Events List (/events)

**无错误** ✅

### 错误分类统计

| 错误类型 | 数量 | 占比 |
|---------|------|------|
| React错误 | X | XX% |
| GraphQL错误 | X | XX% |
| Network错误 | X | XX% |
| TypeScript警告 | X | XX% |

### 修复建议优先级

**P0 - 立即修复**:
1. [具体错误和修复建议]

**P1 - 尽快修复**:
1. [具体错误和修复建议]
```

---

## 🚨 常见问题排查

### 问题1: list_console_messages 返回空数组

**可能原因**:
- 页面还未完全加载
- 控制台确实没有消息
- MCP服务器未正确连接

**解决方法**:
```javascript
// 1. 检查页面是否加载完成
const readyState = mcp__chrome-devtools__evaluate_script({
  function: "() => document.readyState"
})
console.log("Ready State:", readyState)

// 2. 延长等待时间
// 手动等待3-5秒后再获取错误

// 3. 检查MCP服务器状态
mcp__chrome-devtools__list_pages()
// 如果报错，MCP服务器未连接，需要重启VSCode
```

### 问题2: 获取不到错误详情

**可能原因**:
- 使用了错误的msgid
- 消息已过期

**解决方法**:
```javascript
// 1. 使用list_console_messages返回的msgid，不要自己构造
const errors = mcp__chrome-devtools__list_console_messages({ types: ["error"] })

// 2. 立即获取详情（不要等待太久）
if (errors.messages && errors.messages.length > 0) {
  const firstErrorId = errors.messages[0].id
  const details = mcp__chrome-devtools__get_console_message({
    msgid: firstErrorId
  })
  console.log("Error Details:", details)
}
```

### 问题3: 时间戳过滤不工作

**可能原因**:
- 时间戳格式不正确
- 时区问题

**解决方法**:
```javascript
// ✅ 正确：使用Date.now()获取当前时间戳
const timestamp = Date.now()
const recentErrors = mcp__chrome-devtools__list_console_messages({
  types: ["error"],
  since: timestamp
})

// ❌ 错误：使用字符串日期
const recentErrors = mcp__chrome-devtools__list_console_messages({
  types: ["error"],
  since: "2026-03-07"  // 错误！需要数字时间戳
})
```

---

## 📚 相关文档

- **Skill文档**: `.claude/skills/event2table-e2e-test/SKILL.md`
- **MCP配置**: `.claude/config.json`
- **Chrome DevTools Protocol**: https://chromedevtools.github.io/devtools-protocol/
- **chrome-devtools-mcp**: https://github.com/ChromeDevTools/chrome-devtools-mcp

---

**文档维护者**: Event2Table Development Team
**最后更新**: 2026-03-07
**版本**: 1.0
