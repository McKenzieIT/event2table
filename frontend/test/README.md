# Frontend测试套件

## 快速开始

```bash
cd frontend

# 安装依赖
npm install

# 运行所有单元测试
npm test

# 运行E2E测试
npx playwright test

# 运行Critical E2E测试（推荐）
npx playwright test e2e/critical/

# 运行Smoke测试（快速验证）
npx playwright test e2e/smoke/

# 调试模式
npx playwright test e2e/critical/01-dashboard.spec.ts --debug
```

## 测试分层架构

### 1. 单元测试 (70%)
快速、隔离的组件和函数测试。

```
frontend/test/unit/
├── components/       # React组件测试
├── hooks/           # 自定义Hooks测试
├── utils/           # 工具函数测试
└── api/             # API调用测试
```

### 2. 集成测试 (20%)
模块间交互测试。

```
frontend/test/integration/
├── api-integration/  # API集成测试
└── state-management/ # 状态管理测试
```

### 3. E2E测试 (10%)
完整用户流程测试。

```
frontend/test/e2e/
├── critical/         # 关键流程 (12个) ✅ 保留
├── smoke/           # 冒烟测试 (快速验证)
└── comprehensive/   # 全面回归 (可选)
```

## Critical E2E测试清单 (12个)

核心业务流程测试（必须通过）:

1. `01-dashboard.spec.ts` - Dashboard加载
2. `02-games-list.spec.ts` - 游戏列表
3. `game-management.spec.ts` - 游戏管理CRUD
4. `event-management.spec.ts` - 事件管理
5. `events-workflow.spec.ts` - 事件工作流
6. `canvas-complete-workflow.spec.ts` - Canvas完整工作流
7. `error-handling-boundary-conditions.spec.ts` - 错误处理
8. `error-recovery-scenarios.spec.ts` - 错误恢复
9. `hql-generation.spec.ts` - HQL生成
10. `hql-export-workflow.spec.ts` - HQL导出
11. `test-parameter-management.spec.ts` - 参数管理
12. `p0-bug-detection.spec.ts` - P0 Bug检测

## 命名规范

- **单元测试**: `<ComponentName>.test.tsx`
  - 示例: `FieldSelectionModal.test.tsx`

- **E2E测试**: `<序号>-<功能描述>.spec.ts`
  - 示例: `01-dashboard.spec.ts`, `02-games-list.spec.ts`

## 测试编写模板

### E2E测试

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Setup: 导航到页面
    await page.goto('/#/games');
    await page.evaluate(() => {
      localStorage.setItem('selectedGameGid', '10000147');
    });
  });

  test('should do something important', async ({ page }) => {
    // Arrange: 准备测试数据
    const gameName = 'Test Game';

    // Act: 执行操作
    await page.click('[data-testid="create-game-btn"]');
    await page.fill('[data-testid="game-name-input"]', gameName);
    await page.click('[data-testid="save-btn"]');

    // Assert: 验证结果
    await expect(page.locator(`text=${gameName}`)).toBeVisible();
  });
});
```

## Playwright配置

配置文件: `playwright.config.ts`

关键设置:
- **Base URL**: `http://localhost:5173`
- **Timeout**: 30s (默认)
- **Retries**: 2次 (CI环境)

## 测试数据

测试数据存储在:
- `frontend/test/fixtures/mock-data.ts` - Mock数据
- `frontend/test/e2e/helpers/test-data.js` - E2E测试数据

## 调试技巧

### 1. 使用调试模式
```bash
npx playwright test e2e/critical/01-dashboard.spec.ts --debug
```

### 2. 查看测试报告
```bash
npx playwright test --reporter=html
npx playwright show-report
```

### 3. 截图调试
```typescript
await page.screenshot({ path: 'debug-screenshot.png' });
```

### 4. 慢动作模式
```typescript
await page.click('button', { delay: 1000 }); // 慢动作
```

## 常见问题

### Q: 测试超时怎么办?
增加超时时间:
```typescript
test.setTimeout(60000); // 60秒
```

### Q: 如何等待元素?
```typescript
// 等待元素可见
await expect(page.locator('.my-element')).toBeVisible();

// 等待API响应
await page.waitForResponse('**/api/games');

// 等待固定时间（不推荐）
await page.waitForTimeout(1000);
```

### Q: 如何处理弹窗?
```typescript
// 接受弹窗
page.on('dialog', dialog => dialog.accept());

// 或在测试中
await page.click('button', { prompt: true }); // 自动接受prompt
```

## 测试清理历史

**2026-03-21**: 测试文件清理
- 删除临时验证测试: 6个文件
- 合并Canvas测试: 2→1个
- 合并Event Node Builder测试: ~20个文件
- 精简Critical测试: 35→12个
- 归档位置: `docs/archive/testing/2026/03-march/deprecated-frontend-tests/`

## 相关文档

- [Playwright官方文档](https://playwright.dev/)
- [项目测试文档](../README.md)
- [E2E测试指南](../../docs/testing/e2e-testing-guide.md)
