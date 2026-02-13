# E2E Testing Quick Reference

> **快速参考**: 如何运行 Event2Table 的 E2E 测试

---

## 快速开始

### 1. 运行所有 E2E 测试

```bash
cd /Users/mckenzie/Documents/event2table/frontend
npx playwright test
```

### 2. 运行特定测试类型

```bash
# 响应式设计测试
npx playwright test responsive-design.spec.ts

# 冒烟测试
npx playwright test smoke-tests.spec.ts

# API 测试
npx playwright test api-tests.spec.ts

# 截图测试
npx playwright test screenshots.spec.ts
```

### 3. 运行特定项目

```bash
# 仅桌面浏览器
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit

# 仅移动浏览器
npx playwright test --project="Mobile Chrome"
npx playwright test --project="Mobile Safari"

# 响应式测试
npx playwright test --project=responsive-design
```

---

## 常用命令

### 基础命令

```bash
# 列出所有测试
npx playwright test --list

# 运行测试（详细模式）
npx playwright test --reporter=list

# 运行测试（HTML 报告）
npx playwright test --reporter=html

# 运行失败测试
npx playwright test --last-failed
```

### 调试命令

```bash
# UI 模式
npx playwright test --ui

# 调试模式
npx playwright test --debug

# 有头模式（显示浏览器）
npx playwright test --headed

# 慢动作模式（用于调试）
npx playwright test --slow-mo=1000
```

### 特定测试

```bash
# 按名称过滤
npx playwright test -g "should load homepage"
npx playwright test -g "Mobile Viewport"
npx playwright test -g "Tablet Viewport"

# 按文件名过滤
npx playwright test responsive
npx playwright test smoke

# 运行单个测试文件
npx playwright test tests/e2e/responsive-design.spec.ts
```

---

## 测试项目说明

| 项目 | 测试范围 | 设备模拟 | 用途 |
|-----|---------|---------|------|
| chromium | 所有 .spec.ts<br>**除了** responsive-design.spec.ts | Desktop Chrome | Chrome 浏览器测试 |
| firefox | 所有 .spec.ts<br>**除了** responsive-design.spec.ts | Desktop Firefox | Firefox 兼容性 |
| webkit | 所有 .spec.ts<br>**除了** responsive-design.spec.ts | Desktop Safari | Safari 兼容性 |
| Mobile Chrome | 所有 .spec.ts<br>**除了** responsive-design.spec.ts | Pixel 5 | Android 移动设备 |
| Mobile Safari | 所有 .spec.ts<br>**除了** responsive-design.spec.ts | iPhone 12 | iOS 移动设备 |
| responsive-design | **仅** responsive-design.spec.ts | 无（手动 viewport） | 响应式设计 |

---

## 故障排除

### 问题：连接被拒绝

```
Error: net::ERR_CONNECTION_REFUSED at http://localhost:5173/
```

**解决方案**：

选项 1：让 Playwright 自动启动（推荐）
```bash
# Playwright 会自动启动服务器（已配置 webServer）
npx playwright test
```

选项 2：手动启动服务器
```bash
# 终端 1：启动服务器
cd /Users/mckenzie/Documents/event2table/frontend
npm run dev

# 终端 2：运行测试
npx playwright test
```

### 问题：测试超时

```
Test timeout of 30000ms exceeded
```

**解决方案**：

```bash
# 增加超时时间
npx playwright test --timeout=60000

# 或在配置文件中修改
# playwright.config.ts: use: { actionTimeout: 30000 }
```

### 问题：浏览器未安装

```
Error: Executable doesn't exist at /path/to/chromium
```

**解决方案**：

```bash
# 安装 Playwright 浏览器
npx playwright install

# 安装所有浏览器
npx playwright install --with-deps
```

---

## 查看测试结果

### HTML 报告

```bash
# 自动打开 HTML 报告
npx playwright test --reporter=html

# 手动打开报告
npx playwright show-report
```

### JSON 报告

```bash
# 生成 JSON 报告
npx playwright test --reporter=json

# 报告位置
cat test-results.json
```

### 截图和视频

失败测试会自动生成：
- **截图**: `test-results/` 目录
- **视频**: `test-results/` 目录
- **Trace**: `test-results/` 目录

---

## 持续集成

### GitHub Actions

```yaml
- name: Run E2E tests
  run: npx playwright test

- name: Upload test results
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: playwright-report/
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

npx playwright test --project=responsive-design

if [ $? -ne 0 ]; then
  echo "❌ E2E tests failed. Commit aborted."
  exit 1
fi

echo "✅ E2E tests passed."
```

---

## 相关文档

- [E2E 测试指南](../../E2E_TESTING_GUIDE.md) - 完整的端到端测试指南
- [响应式测试指南](./RESPONSIVE_TESTING_GUIDE.md) - 响应式设计测试详解
- [测试修复报告](../docs/development/responsive-test-fix-report.md) - 响应式测试修复详情

---

## 常见任务

### 添加新测试

1. 在 `tests/e2e/` 创建 `your-test.spec.ts`
2. 编写测试用例
3. 运行测试验证
4. 提交代码

```bash
npx playwright test your-test.spec.ts
```

### 调试失败测试

```bash
# 1. 使用调试模式
npx playwright test your-test.spec.ts --debug

# 2. 使用 Playwright Inspector
# 调试模式会自动打开 Inspector

# 3. 查看 trace
npx playwright show-trace test-results/trace.zip
```

### 更新快照

```bash
# 1. 删除旧快照
rm -rf tests/e2e/__screenshots__

# 2. 重新生成快照
npx playwright test screenshots.spec.ts --update-snapshots
```

---

**最后更新**: 2026-02-12
**维护者**: Event2Table Development Team
