# E2E测试套件快速开始指南

## 🚀 5分钟快速开始

### 前置条件

```bash
# 1. 启动后端服务器
cd backend
source venv/bin/activate
python web_app.py

# 2. 启动前端开发服务器（新终端）
cd frontend
npm run dev

# 3. 确认服务器运行
curl http://127.0.0.1:5001/api/games  # 后端
curl http://localhost:5173           # 前端
```

### 运行测试

```bash
# 方式1: 使用测试脚本（推荐）
cd frontend/test/e2e
./run-critical-tests.sh

# 方式2: 直接使用Playwright
cd frontend
npx playwright test critical/

# 方式3: 带UI模式
npx playwright test critical/ --ui

# 方式4: 调试模式
npx playwright test critical/ --debug
```

### 查看结果

```bash
# HTML报告
npx playwright show-report

# 覆盖率报告
open frontend/test/e2e/test-coverage-report.html
```

---

## 📁 文件结构

```
frontend/test/e2e/
├── helpers/
│   └── test-utils.ts              # 公共测试工具（400行）
├── critical/
│   ├── 01-dashboard.spec.ts       # ✅ Dashboard测试（12个测试）
│   ├── 02-games-list.spec.ts      # ✅ Games List测试（14个测试）
│   ├── 03-games-modal.spec.ts     # 📋 待创建
│   ├── 04-events-list.spec.ts     # 📋 现有测试
│   ├── ...                        # 其他9个页面
│   └── README.md                  # 测试文档
├── run-critical-tests.sh          # 测试运行脚本
├── generate-test-report.sh        # 报告生成脚本
└── test-coverage-report.html      # HTML覆盖率报告
```

---

## 🛠️ 测试工具函数

### 页面导航

```typescript
// 导航到页面
await navigateToPage(page, '/games', TEST_GAME_GID);

// 等待页面就绪
await waitForPageReady(page, 3000);

// 等待React挂载
await waitForReactMount(page, 5000);
```

### 控制台检查

```typescript
// 断言无控制台错误
await assertNoConsoleErrors(page, 2000);

// 监控控制台错误
const getErrors = monitorConsoleErrors(page);
// ... 执行操作
const errors = getErrors();
```

### 性能测量

```typescript
// 测量页面性能
const metrics = await measurePagePerformance(page);
console.log(metrics.pageLoadTime);

// 断言性能标准
await assertPagePerformance(page, 5000);
```

### 测试数据生成

```typescript
// 生成测试GID
const testGid = generateTestGid(); // 90000000+

// 生成测试游戏名
const testName = generateTestGameName(); // "E2E Test Game 1234567890"

// 生成测试事件名
const eventName = generateTestEventName(); // "e2e_test_event_1234567890"
```

### API请求监控

```typescript
// 监控API请求
const { getRequests } = monitorApiRequests(page);

// 等待特定API请求
const apiCall = await waitForApiRequest(page, /\/api\/games/);

// 获取所有请求
const requests = getRequests();
```

### 元素交互

```typescript
// 点击所有按钮
const clickCount = await clickAllButtons(page);

// 填充所有输入
const fillCount = await fillAllInputs(page, 'test value');

// 处理确认对话框
await acceptDialog(page);
```

### 断言辅助

```typescript
// 断言页面包含文本
await assertPageContainsText(page, /游戏/);

// 断言元素可见
await assertElementVisible(page, '.game-card');

// 断言元素不可见
await assertElementNotVisible(page, '.modal');
```

---

## 📋 测试模板

```typescript
import { test, expect } from '@playwright/test';
import {
  navigateToPage,
  assertNoConsoleErrors,
  measurePagePerformance,
  generateTestGid,
  BASE_URL,
  TEST_GAME_GID
} from '../helpers/test-utils';

test.describe('Page Name', () => {

  test('1. should load page', async ({ page }) => {
    await navigateToPage(page, '/page-url', TEST_GAME_GID);
    await expect(page).toHaveTitle(/Page Title/);
  });

  test('2. should have no console errors', async ({ page }) => {
    await navigateToPage(page, '/page-url', TEST_GAME_GID);
    await assertNoConsoleErrors(page, 2000);
  });

  test('3. should meet performance criteria', async ({ page }) => {
    await navigateToPage(page, '/page-url', TEST_GAME_GID);
    const metrics = await measurePagePerformance(page);
    expect(metrics.pageLoadTime).toBeLessThan(10000);
  });

  // ... 更多测试
});
```

---

## 🎯 10项核心功能测试清单

每个页面测试应包含：

- [ ] 1. 页面加载 + DOM结构验证
- [ ] 2. 控制台错误检查
- [ ] 3. 所有按钮点击测试
- [ ] 4. 表单填写和提交
- [ ] 5. 搜索/过滤功能验证
- [ ] 6. 模态框打开/关闭
- [ ] 7. API调用状态验证
- [ ] 8. 统计数据显示验证
- [ ] 9. 分页功能测试
- [ ] 10. 性能测量

---

## 📊 测试数据

### 生产测试游戏
```typescript
const TEST_GAME_GID = 10000147; // STAR001
```

### 测试GID范围
```typescript
const TEST_GID_START = 90000000; // 测试GID起始值
```

### 测试数据库
```bash
# 生产数据库
data/dwd_generator.db

# 测试数据库
data/test_database.db

# 环境变量
FLASK_ENV=testing
```

---

## ⚡ 性能基准

### 页面加载时间
- **优秀**: < 3秒
- **可接受**: 3-5秒
- **需优化**: > 5秒

### API响应时间
- **优秀**: < 500ms
- **可接受**: 500ms-1s
- **需优化**: > 1s

---

## 🐛 故障排除

### 测试失败：Target closed

**原因**: 后端服务器未运行

**解决**:
```bash
cd backend
source venv/bin/activate
python web_app.py
```

### 测试超时

**原因**: 页面加载太慢

**解决**:
1. 检查浏览器控制台错误
2. 增加超时时间
3. 检查网络请求

### API调用失败

**原因**: 后端未响应

**解决**:
1. 检查后端日志
2. 重启后端服务器
3. 检查数据库连接

### 数据库错误

**原因**: 测试数据库未初始化

**解决**:
```bash
cd backend
python scripts/setup/init_db.py
```

---

## 📚 相关文档

- [完整测试报告](../../../output/E2E-TEST-SUITE-COMPLETION-REPORT.md)
- [测试目录README](./critical/README.md)
- [Playwright文档](https://playwright.dev/)
- [项目CLAUDE.md](../../../CLAUDE.md)

---

## 🎓 最佳实践

### 1. 测试隔离

每个测试应该独立运行，不依赖其他测试：

```typescript
test.beforeEach(async ({ page }) => {
  // 每个测试前都重新导航
  await navigateToPage(page, '/games', TEST_GAME_GID);
});

test.afterEach(async ({ page }) => {
  // 每个测试后清理数据
  await cleanupTestData(page, createdGids);
});
```

### 2. 使用data-testid

优先使用`data-testid`而非CSS选择器：

```typescript
// ✅ 好
await page.click('[data-testid="add-game-button"]');

// ❌ 避免
await page.click('.btn-primary');
```

### 3. 等待策略

使用适当的等待策略：

```typescript
// ✅ 好：等待特定元素
await expect(page.locator('.game-card')).toBeVisible();

// ❌ 避免：固定等待
await page.waitForTimeout(5000);
```

### 4. 错误处理

捕获并记录错误：

```typescript
try {
  await page.click('[data-testid="delete-button"]');
} catch (error) {
  console.error('Failed to click delete button:', error);
  throw error;
}
```

### 5. 测试数据清理

测试后清理数据：

```typescript
test.afterAll(async ({ page }) => {
  await cleanupTestData(page, createdGameGids);
});
```

---

## 🚀 CI/CD集成

### GitHub Actions示例

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
          node-version: '18'
      - name: Install dependencies
        run: cd frontend && npm install
      - name: Install Playwright
        run: cd frontend && npx playwright install --with-deps
      - name: Run E2E tests
        run: cd frontend && npx playwright test critical/
      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: frontend/test/e2e/playwright-report/
```

---

## 📞 获取帮助

- 查看完整报告：`output/E2E-TEST-SUITE-COMPLETION-REPORT.md`
- 查看测试文档：`frontend/test/e2e/critical/README.md`
- 查看项目规范：`CLAUDE.md`
- 查看Playwright文档：https://playwright.dev/

---

**更新日期**: 2026-03-17
**版本**: 1.0.0
