# Chrome DevTools MCP增强指南

**版本**: 2.0 Enhanced
**日期**: 2026-02-21
**Skill**: event2table-e2e-test

---

## 增强功能概览

基于Phase 2的经验教训，我们为Chrome DevTools MCP增加了以下增强功能：

### 1. 测试计划系统

保存常用测试流程为"测试计划"，可重复执行并对比历史结果。

**示例测试计划**:
```json
{
  "name": "dashboard-smoke-test",
  "description": "Dashboard功能冒烟测试",
  "steps": [
    {
      "action": "navigate_page",
      "params": { "type": "url", "url": "http://localhost:5173/" }
    },
    {
      "action": "take_snapshot",
      "params": {}
    },
    {
      "action": "verify_element_exists",
      "params": { "selector": ".dashboard-container" }
    },
    {
      "action": "check_console_errors",
      "params": { "expected": 0 }
    },
    {
      "action": "check_network_errors",
      "params": { "expected": 0 }
    },
    {
      "action": "take_screenshot",
      "params": { "filePath": "output/screenshots/dashboard.png" }
    }
  ]
}
```

**执行测试计划**:
```javascript
const testPlan = loadTestPlan('dashboard-smoke-test.json');

for (const step of testPlan.steps) {
  switch (step.action) {
    case 'navigate_page':
      await mcp__chrome-devtools__navigate_page(step.params);
      break;
    case 'take_snapshot':
      await mcp__chrome-devtools__take_snapshot(step.params);
      break;
    // ... 其他步骤
  }
}
```

### 2. 智能选择器生成

自动生成稳定的选择器，避免脆弱的CSS选择器。

**选择器优先级**:
1. `data-testid` - 最稳定
2. `input[name="xxx"]` - 语义化
3. `text=xxx` - 可读性好
4. `.css-class` - 最不稳定

**自动生成**:
```javascript
function generateSelector(element) {
  // 优先使用data-testid
  if (element.attributes['data-testid']) {
    return `[data-testid="${element.attributes['data-testid']}"]`;
  }

  // 使用name属性（表单元素）
  if (element.attributes['name']) {
    return `[name="${element.attributes['name']}"]`;
  }

  // 使用text内容（按钮、链接）
  if (element.text) {
    return `text=${element.text}`;
  }

  // 最后使用class
  if (element.attributes['class']) {
    return `.${element.attributes['class'].split(' ')[0]}`;
  }
}
```

### 3. 性能基准对比

自动追踪性能指标，检测性能退化。

**基准存储** (`data/performance-baseline.json`):
```json
{
  "dashboard": {
    "pageLoadTime": 1800,
    "domContentLoaded": 1200,
    "lcp": 900
  },
  "timestamp": "2026-02-21T00:00:00Z"
}
```

**性能检测**:
```javascript
async function checkPerformance(testName, currentMetrics) {
  const baseline = loadBaseline(testName);

  const regression = [];
  for (const [metric, current] of Object.entries(currentMetrics)) {
    const baselineValue = baseline[metric];
    const threshold = baselineValue * 0.2; // 20%阈值

    if (current > baselineValue + threshold) {
      regression.push({
        metric,
        current,
        baseline: baselineValue,
        degradation: `${((current - baselineValue) / baselineValue * 100).toFixed(1)}%`
      });
    }
  }

  return regression;
}
```

### 4. API契约验证

自动检测前后端API契约不匹配。

**检查API调用**:
```javascript
async function verifyAPIContract() {
  const requests = await mcp__chrome-devtools__list_network_requests({
    resourceTypes: ['xhr', 'fetch']
  });

  const violations = [];

  for (const req of requests) {
    // 检查是否缺少必需参数
    if (req.status === 400) {
      const detail = await mcp__chrome-devtools__get_network_request({
        reqid: req.id
      });

      violations.push({
        url: req.url,
        error: detail.responseBody,
        suggestion: "检查是否缺少必需参数（如game_gid）"
      });
    }
  }

  return violations;
}
```

### 5. 错误模式识别

基于Phase 2经验，自动识别常见错误模式。

**错误模式库**:
```javascript
const errorPatterns = {
  "React Hooks错误": {
    signature: /Rendered more hooks than during the previous render/,
    cause: "Hook在条件返回后调用",
    fix: "将所有Hook移到条件返回之前"
  },

  "Lazy Loading超时": {
    signature: /Loading timeout|Page stuck on loading/,
    cause: "小型组件使用lazy loading",
    fix: "改用直接导入"
  },

  "API参数缺失": {
    signature: /Missing.*parameter|game_gid.*required/,
    cause: "前端未传递必需参数",
    fix: "添加game_gid参数到API调用"
  }
};
```

**自动识别**:
```javascript
function identifyErrorPattern(error) {
  for (const [name, pattern] of Object.entries(errorPatterns)) {
    if (pattern.signature.test(error)) {
      return {
        name,
        cause: pattern.cause,
        fix: pattern.fix
      };
    }
  }
  return null;
}
```

---

## 增强的测试流程

### Phase 1: 快速验证（30秒）

```
1. 导航到页面
2. take_snapshot() - 检查DOM结构
3. list_console_messages({types: ["error"]}) - 检查JS错误
4. 判断: 页面是否基本正常？
```

### Phase 2: 深度分析（2分钟）

```
1. list_network_requests() - 检查API调用
2. evaluate_script() - 获取性能指标
3. take_screenshot() - 视觉记录
4. verifyAPIContract() - 检查API契约
5. checkPerformance() - 检查性能退化
```

### Phase 3: 交互测试（5分钟）

```
1. 识别交互元素（按钮、表单、链接）
2. 执行用户操作（点击、填写、拖拽）
3. 验证响应（DOM变化、API调用、状态更新）
4. 检查错误（console + network）
5. 生成报告
```

---

## 自动报告生成

### 报告模板

```markdown
# [功能名] E2E测试报告

## 测试概要
- **测试时间**: YYYY-MM-DD HH:MM
- **测试人员**: [姓名]
- **测试范围**: [功能模块]

## 测试结果
- **状态**: ✅ 通过 / ⚠️ 部分通过 / ❌ 失败
- **通过率**: X%

## 发现的问题

### 问题1: [问题标题]
- **严重性**: CRITICAL/HIGH/MEDIUM
- **症状**: [描述症状]
- **根因**: [Chrome DevTools MCP诊断结果]
- **建议修复**: [具体修复建议]

### 问题2: [问题标题]
...

## 性能分析
- **Page Load**: Xms (目标: <3s)
- **API Response**: Xms (目标: <500ms)
- **LCP**: Xms (目标: <2.5s)

## 证据
- **截图**: [路径]
- **Console日志**: [关键错误]
- **网络请求**: [失败的API]
```

---

## 快速参考命令

### Chrome DevTools MCP常用工具

```javascript
// 页面导航
mcp__chrome-devtools__navigate_page({ type: "url", url: "..." })

// DOM分析
mcp__chrome-devtools__take_snapshot()

// 交互
mcp__chrome-devtools__click({ uid: "..." })
mcp__chrome-devtools__fill({ uid: "...", value: "..." })
mcp__chrome-devtools__drag({ from_uid: "...", to_uid: "..." })

// 监控
mcp__chrome-devtools__list_console_messages({ types: ["error"] })
mcp__chrome-devtools__list_network_requests({ resourceTypes: ["xhr", "fetch"] })

// 性能
mcp__chrome-devtools__evaluate_script({ function: "..." })

// 截图
mcp__chrome-devtools__take_screenshot({ filePath: "..." })
```

### 性能预算

| 指标 | 目标 | 警告 | 严重 |
|------|------|------|------|
| Page Load | <3s | >5s | >10s |
| DOM Content Loaded | <2s | >3s | >5s |
| API Response | <500ms | >1s | >2s |
| LCP | <2.5s | >4s | >6s |

---

## 最佳实践

### 1. 测试隔离

```javascript
// ✅ 使用测试GID范围
TEST_GID_START = 90000000
TEST_GID_END = 99999999

// ❌ 不要使用生产GID
PROD_GID = 10000147 // STAR001
```

### 2. 错误消息增强

```javascript
// ✅ 好的错误消息
`Game GID ${gid} already exists. Please use another GID (suggested: 90000000+)`

// ❌ 坏的错误消息
`Creation failed`
```

### 3. 选择器稳定性

```javascript
// ✅ 稳定选择器
[data-testid="submit-button"]
input[name="gid"]
text="保存"

// ❌ 不稳定选择器
.btn.submit
div > div > button
```

### 4. 性能监控

```javascript
// 每次测试都记录性能
const perf = await measurePerformance();
await saveToBaseline('dashboard', perf);
```

---

## 故障排除

### Chrome DevTools MCP无法连接

```bash
# 检查Chrome是否运行
ps aux | grep -i chrome

# 检查端口
lsof -i :9222
```

### 测试无法找到元素

```javascript
// 1. 检查快照
mcp__chrome-devtools__take_snapshot()

// 2. 查看实际DOM结构
// 3. 调整选择器
```

### API调用失败

```javascript
// 1. 检查网络请求
mcp__chrome-devtools__list_network_requests()

// 2. 获取详细错误
mcp__chrome-devtools__get_network_request({ reqid: ... })

// 3. 验证API契约
```

---

**版本**: 2.0 Enhanced
**最后更新**: 2026-02-21
**维护者**: Event2Table Development Team
