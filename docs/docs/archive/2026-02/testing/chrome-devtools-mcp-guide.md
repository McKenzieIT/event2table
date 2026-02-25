# chrome-devtools-mcp使用指南

**项目**: Event2Table
**创建日期**: 2026-02-13
**目标**: 为Event2Table项目提供chrome-devtools-mcp自动化测试的完整指南

---

## 一、chrome-devtools-mcp概述

### 1.1 什么是chrome-devtools-mcp？

chrome-devtools-mcp是一个**Model Context Protocol (MCP)**服务器，允许AI助手与Chrome DevTools Protocol集成，实现：

- **自动化浏览器交互**: 导航、点击、填表、截图
- **性能分析**: 渲染性能、脚本执行时间、布局计数
- **网络请求监控**: API请求、响应时间、状态码
- **元素检查和调试**: DOM查询、CSS样式、可访问性
- **JavaScript执行和调试**: 控制台执行、表达式求值、错误捕获

### 1.2 为什么使用chrome-devtools-mcp？

1. **自动化E2E测试**: 无需手动点击浏览测试场景
2. **性能基准建立**: 精确测量优化前后的性能指标
3. **网络验证**: 验证API请求正确触发
4. **回归检测**: CI/CD集成自动测试
5. **调试辅助**: 快速重现和调试用户报告的问题

### 1.3 与Event2Table集成

chrome-devtools-mcp可以用于：

1. **Dashboard卡片E2E测试** - 验证所有快捷操作卡片可点击
2. **游戏管理模态框测试** - 验证游戏CRUD功能正常
3. **视觉一致性测试** - 验证青蓝色调主题在所有页面一致
4. **性能基准测试** - 测量React.memo优化效果

---

## 二、安装与配置

### 2.1 前提条件

在安装chrome-devtools-mcp之前，确保：

```bash
# 1. 验证Node.js和npm可用
which node    # 应输出: /usr/local/Cellar/node/25.6.0/bin/node
which npm     # 应输出: /usr/local/Cellar/node/25.6.0/bin/npm
which npx     # 应输出: /usr/local/Cellar/node/25.6.0/bin/npx

# 2. 验证版本
node --version    # 应显示: v25.6.0
npm --version     # 应显示: 10.x.x
npx --version     # 应显示: 10.x.x
```

### 2.2 安装方式

#### 方式A: 全局安装（推荐）

```bash
npm install -g chrome-devtools-mcp@latest
```

#### 方式B: 项目本地安装

```bash
cd /Users/mckenzie/Documents/event2table
npm install --save-dev chrome-devtools-mcp@latest
```

#### 方式C: 使用npm run脚本（推荐用于测试）

在`frontend/package.json`中配置：

```json
{
  "scripts": {
    "mcp:help": "npx chrome-devtools-mcp@latest --help",
    "mcp:test": "npx chrome-devtools-mcp@latest test",
    "mcp:screenshot": "npx chrome-devtools-mcp@latest screenshot"
  }
}
```

然后运行：
```bash
cd frontend
npm run mcp:help
npm run mcp:test
npm run mcp:screenshot
```

### 2.3 配置验证

安装后验证配置：

```bash
# 显示帮助信息
npx chrome-devtools-mcp@latest --help

# 列出可用工具
npx chrome-devtools-mcp@latest list-tools

# 测试导航功能（需要先启动开发服务器）
npx chrome-devtools-mcp@latest navigate http://localhost:5173

# 测试截图功能
npx chrome-devtools-mcp@latest screenshot screenshot.png

# 测试元素查询
npx chrome-devtools-mcp@latest query-selector ".game-management-btn"
```

---

## 三、核心API

### 3.1 导航控制

#### navigate(url, options?)

导航到指定URL。

```javascript
// 导航到Dashboard
await mcp.navigate('http://localhost:5173');

// 等待页面加载
await mcp.waitForLoadState('networkidle');

// 导航并等待特定元素
await mcp.navigate('http://localhost:5173/games');
await mcp.waitForSelector('.game-management-modal');
```

### 3.2 DOM操作

#### querySelector(selector)

查找页面元素。

```javascript
// 查找游戏管理按钮
const btn = await mcp.querySelector('.game-management-btn');

// 查找所有快捷操作卡片
const cards = await mcp.querySelectorAll('.action-card');

console.log(`找到 ${cards.length} 个快捷操作卡片`);
```

#### click(selector, options?)

模拟点击元素。

```javascript
// 点击游戏管理按钮
await mcp.click('.game-management-btn');

// 点击快捷操作卡片
await mcp.click('.action-card[href="/games"]');

// 点击并等待导航
await mcp.click('.action-card[href="/events"]');
await mcp.waitForLoadState('networkidle');
```

### 3.3 截图和验证

#### screenshot(filename, options?)

保存页面截图。

```javascript
// 整页截图
await mcp.screenshot('dashboard-full.png');

// 特定元素截图
await mcp.screenshot('game-modal.png', {
  selector: '.game-management-modal'
});

// 截图并隐藏光标
await mcp.screenshot('test-result.png', {
  hideCursor: true,
  fullPage: false
});
```

### 3.4 网络监控

#### getNetworkRequests(filter?)

获取API请求信息。

```javascript
// 获取所有API请求
const requests = await mcp.getNetworkRequests({
  filter: req => req.url.includes('/api/')
});

console.log(`捕获到 ${requests.length} 个API请求`);

// 验证请求
requests.forEach(req => {
  console.log(`  ${req.method} ${req.url}`);
  console.log(`    状态: ${req.status}`);
  console.log(`    时间: ${req.duration}ms`);
});
```

### 3.5 控制台监控

#### getConsoleLogs(filter?)

获取浏览器控制台日志。

```javascript
// 获取所有日志
const logs = await mcp.getConsoleLogs();

// 过滤错误
const errors = logs.filter(log => log.level === 'error');

console.log(`发现 ${errors.length} 个错误:`);
errors.forEach(err => {
  console.error(`  [${err.source}] ${err.message}`);
  if (err.stack) console.error(`    堆栈: ${err.stack}`);
});
```

---

## 四、E2E测试场景

### 4.1 Dashboard卡片测试

**目标**: 验证所有Dashboard快捷操作卡片可正常点击和导航。

#### 测试步骤

```javascript
// 1. 导航到Dashboard
await mcp.navigate('http://localhost:5173');
await mcp.waitForSelector('.dashboard-container');

// 2. 清空控制台日志
await mcp.clearConsoleLogs();

// 3. 查找所有快捷操作卡片
const cards = await mcp.querySelectorAll('.action-card');
console.log(`找到 ${cards.length} 个快捷操作卡片`);

// 4. 测试每个卡片
for (const card of cards) {
  const cardText = await mcp.getText(card);
  console.log(`\n测试卡片: ${cardText}`);

  // 点击卡片
  await mcp.click(card);

  // 等待导航
  await mcp.waitForLoadState('networkidle');
  await mcp.wait(1000);

  // 获取控制台日志
  const logs = await mcp.getConsoleLogs();
  const errors = logs.filter(log => log.level === 'error');

  if (errors.length > 0) {
    console.error(`  ❌ 发现${errors.length}个错误:`);
    errors.forEach(err => console.error(`    [${err.source}] ${err.message}`));
  } else {
    console.log(`  ✅ 导航成功，无错误`);
  }

  // 截图记录
  await mcp.screenshot(`test-${cardText.replace(/\s+/g, '-')}.png`);

  // 返回Dashboard
  await mcp.navigate('http://localhost:5173');
  await mcp.waitForSelector('.dashboard-container');
}
```

#### 验证标准

- [ ] 点击"管理游戏"卡片 → 导航到 `/games`
- [ ] 点击"管理事件"卡片 → 导航到 `/events`
- [ ] 点击"HQL画布"卡片 → 导航到 `/canvas`
- [ ] 点击"流程管理"卡片 → 导航到 `/flows`
- [ ] 所有导航无JavaScript错误
- [ ] 所有导航无React警告
- [ ] 测试截图保存成功

### 4.2 游戏管理模态框测试

**目标**: 验证游戏管理模态框的完整功能。

#### 测试步骤

```javascript
// 1. 导航到Dashboard
await mcp.navigate('http://localhost:5173');
await mcp.waitForSelector('.dashboard-container');

// 2. 点击"游戏管理"按钮
await mcp.click('.game-management-btn');

// 3. 验证模态框打开
await mcp.waitForSelector('.game-management-modal');
console.log('✅ 游戏管理模态框已打开');

// 4. 测试搜索功能
const searchInput = await mcp.querySelector('.game-search-input');
await mcp.type(searchInput, 'test-game');
await mcp.wait(500); // 等待搜索过滤

// 5. 测试添加游戏按钮
const addBtn = await mcp.querySelector('.add-game-btn');
await mcp.click(addBtn);

// 6. 验证添加游戏模态框
await mcp.waitForSelector('.add-game-modal');
console.log('✅ 添加游戏模态框已打开');

// 7. 关闭模态框
const closeBtn = await mcp.querySelector('.modal-close-btn');
await mcp.click(closeBtn);

// 8. 验证模态框关闭
await mcp.wait(300);
const modal = await mcp.querySelector('.game-management-modal');
if (!modal || modal.offsetParent === null) {
  console.log('✅ 模态框已关闭');
}

// 9. 截图记录
await mcp.screenshot('game-management-test.png');
```

#### 验证标准

- [ ] 点击"游戏管理"按钮打开模态框
- [ ] 搜索功能正常工作
- [ ] 添加游戏按钮打开嵌套模态框
- [ ] 关闭按钮正常工作
- [ ] 所有操作无JavaScript错误
- [ ] 测试截图保存成功

### 4.3 视觉一致性测试

**目标**: 验证青蓝色调Cyber风格在所有页面一致。

#### 测试步骤

```javascript
// 1. 导航到Dashboard
await mcp.navigate('http://localhost:5173');
await mcp.waitForSelector('.dashboard-container');

// 2. 检查背景色
const bodyBg = await mcp.getComputedStyle('body', 'background');
console.log('背景色:', bodyBg);

// 3. 检查Card组件hover效果
const cards = await mcp.querySelectorAll('.action-card');
for (const card of cards) {
  const hoverBg = await mcp.getComputedStyle(card, ':hover', 'background');
  console.log('Card hover背景:', hoverBg);
}

// 4. 截图记录视觉样式
await mcp.screenshot('visual-theme-test.png');
```

#### 验证标准

- [ ] 背景色为深青蓝渐变
- [ ] Card hover效果为青色边框
- [ ] 所有页面视觉风格一致
- [ ] 无CSS错误或警告

---

## 五、最佳实践

### 5.1 测试脚本编写

1. **模块化设计** - 每个测试场景独立文件
2. **错误处理** - 完善的try-catch和错误恢复
3. **日志记录** - 详细的console.log输出
4. **截图保存** - 每个关键步骤截图记录
5. **清理资源** - 测试结束后关闭浏览器和清理临时文件

### 5.2 性能测试技巧

1. **基准测试** - 优化前后使用相同测试脚本
2. **多次运行** - 每个测试运行3-5次取平均值
3. **独立测试** - 每个功能点单独测试避免干扰
4. **资源监控** - 测试过程中监控CPU和内存使用

### 5.3 调试技巧

1. **headless模式** - 开发时使用headless模式加快速度
2. **调试模式** - 使用`--debug`参数查看详细日志
3. **交互延迟** - 使用`wait()`而非`sleep()`确保元素就绪
4. **选择器优化** - 优先使用data-testid等稳定选择器

---

## 六、常见问题

### 6.1 安装和配置问题

#### Q: npx: command not found

**症状**:
```bash
$ npx chrome-devtools-mcp@latest --help
npx: command not found
```

**解决方案**:
1. 永久配置PATH（已在Phase 3完成）
2. 重新加载shell配置: `source ~/.zshrc`
3. 验证: `which npx` 应输出正确路径

#### Q: 端口已占用

**症状**:
```bash
Error: Port 9222 is already in use
```

**解决方案**:
1. 关闭其他Chrome实例
2. 使用`--remote-debugging-port`指定不同端口

### 6.2 测试执行问题

#### Q: 元素未找到

**症状**:
```javascript
Error: Element not found: .game-management-btn
```

**解决方案**:
1. 检查选择器语法正确
2. 使用`waitForSelector`等待元素加载
3. 检查是否在iframe中需要切换context

#### Q: 测试超时

**症状**:
```javascript
Error: Timeout waiting for selector
```

**解决方案**:
1. 增加超时时间
2. 检查网络连接
3. 验证开发服务器正在运行

### 6.3 性能问题

#### Q: 测试运行缓慢

**症状**: 测试脚本执行时间过长

**解决方案**:
1. 使用headless模式
2. 减少截图次数
3. 并行执行独立测试

---

## 七、快速参考

### 7.1 常用命令

```bash
# 安装
npm install -g chrome-devtools-mcp@latest

# 帮助
npx chrome-devtools-mcp@latest --help

# 导航
npx chrome-devtools-mcp@latest navigate http://localhost:5173

# 截图
npx chrome-devtools-mcp@latest screenshot test.png

# 查询元素
npx chrome-devtools-mcp@latest query-selector ".btn"
```

### 7.2 测试环境

```bash
# 终端1: 后端服务
python /Users/mckenzie/Documents/event2table/web_app.py

# 终端2: 前端服务
cd /Users/mckenzie/Documents/event2table/frontend
npm run dev

# 验证服务
# 后端: http://127.0.0.1:5001
# 前端: http://localhost:5173
```

### 7.3 Element选择器

| 元素 | 推荐选择器 | 备注 |
|------|------------|------|
| 游戏管理按钮 | `.game-management-btn` | 自定义类名 |
| 快捷操作卡片 | `.action-card[href="/games"]` | 属性选择器 |
| 模态框容器 | `.game-management-modal` | 自定义类名 |
| 搜索输入 | `.game-search-input` | 自定义类名 |
| 添加按钮 | `.add-game-btn` | 自定义类名 |

---

## 八、后续步骤

### 8.1 立即可用

1. **阅读本文档** - 理解chrome-devtools-mcp的基本使用
2. **安装MCP工具** - 按照第二章节完成安装
3. **验证配置** - 运行基础命令确认可用
4. **开发服务器** - 启动backend和frontend开发服务器

### 8.2 测试执行

1. **编写测试脚本** - 基于第四章节的场景编写JavaScript测试
2. **执行Dashboard测试** - 验证快捷操作卡片功能
3. **执行游戏管理测试** - 验证模态框功能
4. **收集测试结果** - 保存截图和日志
5. **生成测试报告** - 记录测试结果和发现的问题

### 8.3 持续改进

1. **CI/CD集成** - 将E2E测试集成到CI流程
2. **性能回归测试** - 建立性能基准防止退化
3. **测试覆盖率提升** - 逐步增加测试场景到80%+

---

**文档版本**: 1.0
**创建日期**: 2026-02-13
**最后更新**: 2026-02-13
**维护者**: Event2Table Development Team

---

## 附录A: 相关资源

### MCP官方文档
- https://modelcontextprotocol.io/
- https://chromedevtools.github.io/devtools-protocol/

### Event2Table项目文档
- [E2E测试指南](../testing/e2e-testing-guide.md)
- [快速测试指南](../testing/quick-test-guide.md)
- [开发规范](../../CLAUDE.md)

### 社区资源
- chrome-devtools-mcp GitHub仓库
- MCP社区示例和最佳实践
