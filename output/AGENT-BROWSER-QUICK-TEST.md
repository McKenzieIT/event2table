# agent-browser 权限测试指南

## 已添加的权限

✅ `Bash(npx agent-browser:*)`
✅ `Bash(agent-browser:*)`
✅ `Bash(npx agent-browser eval:*)`
✅ `Bash(agent-browser eval:*)`
✅ `Edit(//Users/mckenzie/Documents/event2table/**)`

## 快速验证步骤

### 1. 基础命令测试

```bash
# 测试 agent-browser 是否可用
agent-browser --version

# 或者使用 npx
npx agent-browser --version
```

### 2. 简单浏览器测试

```bash
# 打开测试页面
agent-browser open https://example.com

# 等待加载
agent-browser wait --load networkidle

# 获取页面标题（测试 eval 权限）
agent-browser eval 'document.title'

# 截图
agent-browser screenshot /tmp/test.png
```

### 3. 本地开发服务器测试

```bash
# 启动前端开发服务器（如果未运行）
cd frontend && npm run dev

# 在另一个终端测试
agent-browser open http://localhost:5173
agent-browser wait --load interactive
agent-browser eval 'document.title'
agent-browser screenshot /tmp/event2table-home.png
```

### 4. JavaScript 执行测试（eval 权限）

```bash
# 简单表达式
agent-browser eval 'document.URL'
agent-browser eval 'document.querySelectorAll("*").length'

# 复杂脚本（使用 --stdin 避免引号问题）
agent-browser eval --stdin <<'EVALEOF'
const buttons = document.querySelectorAll('button');
console.log(`Found ${buttons.length} buttons`);
return buttons.length;
EVALEOF

# 使用 base64 编码（程序化生成）
echo 'document.querySelector("h1")?.textContent' | \
  base64 | \
  xargs -I {} agent-browser eval -b {}
```

## 常见问题

### Q: 仍然提示需要权限？
A: 权限在下次会话中生效。重启 Claude Code 或等待会话刷新。

### Q: agent-browser 命令未找到？
A: 需要先安装 agent-browser：
```bash
# 全局安装
npm install -g agent-browser

# 或使用 Homebrew
brew install agent-browser

# 首次使用需要下载 Chrome
agent-browser install
```

### Q: eval 命令报错？
A: 复杂 JavaScript 需要使用 `--stdin` 或 `-b` 参数：
```bash
# ✅ 正确：简单表达式
agent-browser eval 'document.title'

# ✅ 正确：复杂脚本使用 --stdin
agent-browser eval --stdin <<'EOF'
const data = { test: 'value' };
console.log(data);
EOF

# ❌ 错误：嵌套引号不转义
agent-browser eval 'document.querySelector("a").href'  # 可能失败
```

## Edit 工具测试

```python
# 测试 Edit 工具
Edit(
    file_path="/Users/mckenzie/Documents/event2table/output/test-edit.txt",
    old_string="old content",
    new_string="new content"
)
```

## 完整测试示例

```bash
# 1. 打开应用
agent-browser open http://localhost:5173

# 2. 等待加载
agent-browser wait --load networkidle

# 3. 获取快照
agent-browser snapshot -i

# 4. 执行 JavaScript 检查页面状态
agent-browser eval 'document.readyState'
agent-browser eval 'performance.timing.loadEventEnd - performance.timing.navigationStart'

# 5. 检查控制台错误
agent-browser eval 'window.errors || []'

# 6. 截图保存
agent-browser screenshot /tmp/e2e-test-$(date +%s).png

# 7. 关闭浏览器
agent-browser close
```

## 权限验证清单

- [ ] `agent-browser --version` 可执行
- [ ] `agent-browser open <url>` 可打开网页
- [ ] `agent-browser eval '<js>'` 可执行 JavaScript
- [ ] `agent-browser eval --stdin <<'EOF'` 可执行复杂脚本
- [ ] `agent-browser screenshot <path>` 可保存截图
- [ ] `Edit()` 工具可编辑文件

## 相关文档

- **agent-browser 完整文档**: `.claude/skills/agent-browser/`
- **eval 命令参考**: `.claude/skills/agent-browser/references/commands.md#javascript-evaluation-eval`
- **项目测试指南**: `docs/testing/e2e-testing-guide.md`
