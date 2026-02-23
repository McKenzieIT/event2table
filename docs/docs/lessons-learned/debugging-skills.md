# 调试技能

> **来源**: 整合了E2E测试和Subagent分析的调试经验
> **最后更新**: 2026-02-24
> **维护**: 每次调试问题后立即更新

---

## Chrome DevTools MCP调试法 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 2次 | **来源**: [TESTING_LESSONS_LEARNED.md](../archive/2026-02/testing-reports/TESTING_LESSONS_LEARNED.md), [E2E测试报告](../archive/2026-02/e2e-test-reports/)

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

### 相关经验

- [测试指南 - E2E测试](./testing-guide.md#e2e测试) - E2E测试方法论
- [React最佳实践 - Hooks规则](./react-best-practices.md#react-hooks-规则) - React Hooks调试

---

## Subagent并行分析法 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [Ralph Loop迭代测试法](../archive/2026-02/e2e-test-reports/)

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

### 相关经验

- [性能模式 - 数据库索引](./performance-patterns.md#数据库索引) - 性能分析工具
- [测试指南 - 测试工具选择](./testing-guide.md#测试工具选择) - 测试工具对比
