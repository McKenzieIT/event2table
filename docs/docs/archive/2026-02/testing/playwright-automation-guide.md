# Playwright自动化测试指南

> **独立文档**: 这是Event2Table的Playwright自动化测试框架，与Chrome DevTools MCP skill分开使用。

**用途**: 自动化回归测试、CI/CD集成、多浏览器测试

**注意**: 如需交互式问题诊断，请使用 `/event2table-e2e-test` skill（Chrome DevTools MCP）

---

## 快速开始

### 安装和配置

```bash
cd frontend
npm install -D @playwright/test
npx playwright install
```

### 运行测试

```bash
# 所有smoke测试
npm run test:e2e:smoke

# UI模式（可视化调试）
npm run test:e2e:ui

# 调试模式
npm run test:e2e:debug

# 查看测试报告
npm run test:e2e:report
```

---

## 测试组织

### 目录结构

```
frontend/test/e2e/
├── smoke/           # 冒烟测试（快速验证）
├── regression/      # 回归测试（完整覆盖）
├── critical/        # 关键路径测试
├── fixtures/        # 测试数据
└── playwright.config.js
```

### 测试文件命名

- `*.smoke.spec.js` - 冒烟测试
- `*.regression.spec.js` - 回归测试
- `*.critical.spec.js` - 关键测试

---

## Playwright配置

```javascript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './test/e2e',
  fullyParallel: true,
  workers: 6,
  reporter: [
    ['html', { outputFolder: 'test/e2e/playwright-report' }],
    ['json', { outputFile: 'test/e2e/results.json' }]
  ],
  use: {
    baseURL: 'http://localhost:5173',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    { name: 'smoke', testMatch: /.*\.smoke\.spec\.js/ },
    { name: 'regression', testMatch: /.*\.regression\.spec\.js/ },
    { name: 'critical', testMatch: /.*\.critical\.spec\.js/ }
  ]
});
```

---

## 测试模板

### 冒烟测试

```javascript
import { test, expect } from '@playwright/test';

test.describe('Dashboard Smoke', () => {
  test('Dashboard loads and displays content', async ({ page }) => {
    await page.goto('/');

    // Wait for page to load
    await expect(page.locator('.dashboard-container')).toBeVisible();

    // Verify statistics cards
    await expect(page.locator('.stat-card')).toHaveCount({ min: 3 });

    // Check for console errors
    const errors = await page.evaluate(() => window.__errors || []);
    expect(errors).toHaveLength(0);
  });

  test('Dashboard loads within performance budget', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/');
    await expect(page.locator('.dashboard-container')).toBeVisible();
    const loadTime = Date.now() - startTime;

    expect(loadTime).toBeLessThan(5000); // 5秒预算
  });
});
```

### CRUD测试

```javascript
test.describe('Games CRUD', () => {
  test('User can create a new game', async ({ page }) => {
    await page.goto('/#/games/create');

    // Generate unique test GID
    const testGid = Math.floor(Math.random() * 10000000) + 90000000;

    // Fill form
    await page.fill('input[name="gid"]', String(testGid));
    await page.fill('input[name="name"]', 'E2E测试游戏');
    await page.selectOption('select[name="ods_db"]', 'ieu_ods');

    // Submit
    await page.click('button[type="submit"]');

    // Verify success
    await expect(page.locator('.toast-success')).toBeVisible();
    await expect(page.locator('.toast-success')).toContainText(/创建成功/i);
  });
});
```

---

## Pre-commit Hook

### 安装

```bash
cp scripts/git-hooks/pre-commit-enhanced .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### 使用

```bash
# 正常提交（会运行E2E测试）
git commit -m "message"

# 跳过E2E测试
SKIP_E2E_TESTS=true git commit -m "message"
```

---

## CI/CD集成

### GitHub Actions配置

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '25'

      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci

      - name: Install Playwright
        working-directory: ./frontend
        run: npx playwright install --with-deps

      - name: Run E2E tests
        working-directory: ./frontend
        run: npm run test:e2e:smoke

      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: frontend/test/e2e/playwright-report/
```

---

## 与Chrome DevTools MCP的区别

| 特性 | Chrome DevTools MCP | Playwright |
|------|-------------------|------------|
| **类型** | 交互式诊断工具 | 自动化测试框架 |
| **用途** | 问题诊断、探索性测试 | 回归测试、CI/CD |
| **能力** | 实时页面分析、网络监控 | 脚本化测试、多浏览器 |
| **优势** | 深度诊断、灵活调试 | 可重复、批量执行 |
| **输出** | 详细分析报告 | Pass/Fail结果 |

### 何时使用哪个？

**使用Chrome DevTools MCP (`/event2table-e2e-test`)**:
- 🔍 新功能测试
- 🎯 问题诊断
- 🔬 探索性测试
- 📊 性能分析
- 🐛 Bug调查

**使用Playwright (本指南)**:
- 🔄 回归测试
- 🚀 CI/CD集成
- 🧪 冒烟测试
- 🌐 多浏览器测试
- 📈 质量趋势分析

---

## 维护者

- **Skill维护者**: Event2Table Development Team
- **Playwright配置**: frontend/playwright.config.js
- **测试代码**: frontend/test/e2e/
- **文档**: docs/testing/playwright-automation-guide.md

---

**最后更新**: 2026-02-21
**版本**: 1.0
