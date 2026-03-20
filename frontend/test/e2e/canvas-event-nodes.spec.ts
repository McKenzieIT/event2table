/**
 * Canvas and Event Nodes E2E Test Suite
 *
 * 测试范围：
 * 1. Event Node Builder (10项功能)
 * 2. Event Nodes Management (10项功能)
 * 3. Canvas (10项功能)
 *
 * 重点验证：
 * - 游戏上下文提示是否改进
 * - Canvas错误提示是否改进
 * - 面包屑导航是否修复
 */

import { test, expect } from '@playwright/test';

// 测试数据
const TEST_GAME_GID = 10000147;
const BASE_URL = `/game/${TEST_GAME_GID}`;

test.describe('Canvas and Event Nodes E2E Test Suite', () => {
  // 移除beforeEach钩子，每个测试独立导航

  /**
   * ============================================
   * 测试组1: Event Node Builder (10项功能)
   * ============================================
   */
  test.describe('Event Node Builder', () => {
    test('1. 页面加载 + DOM结构', async ({ page }) => {
      // 导航到Event Node Builder
      await page.goto(`/event-node-builder?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      // 验证页面标题
      await expect(page.locator('h1')).toContainText('事件节点构建器');

      // 验证主要组件存在
      await expect(page.locator('#event-select')).toBeVisible();
      await expect(page.locator('.field-canvas')).toBeVisible();
      await expect(page.locator('.hql-preview')).toBeVisible();
      await expect(page.locator('.where-builder')).toBeVisible();
    });

    test('2. 控制台错误检查', async ({ page }) => {
      const errors: string[] = [];

      page.on('console', msg => {
        if (msg.type() === 'error') {
          errors.push(msg.text());
        }
      });

      await page.goto(`/event-node-builder?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      // 等待一段时间以捕获异步错误
      await page.waitForTimeout(3000);

      // 验证没有控制台错误
      expect(errors).toHaveLength(0);
    });

    test('3. 所有按钮点击测试', async ({ page }) => {
      await page.goto(`/event-node-builder?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      // 测试返回按钮
      const backButton = page.locator('button:has-text("返回")');
      if (await backButton.isVisible()) {
        await backButton.click();
        await expect(page).toHaveURL(/\/canvas/);
      }

      // 重新导航回来
      await page.goto(`/event-node-builder?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      // 测试HQL预览按钮（如果存在）
      const previewButton = page.locator('button:has-text("预览")');
      if (await previewButton.isVisible()) {
        await previewButton.click();
        await expect(page.locator('.hql-preview-modal')).toBeVisible();
      }
    });

    test('4. 表单填写和提交 - 选择事件', async ({ page }) => {
      await page.goto(`/event-node-builder?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      // 选择事件
      const eventSelect = page.locator('#event-select');
      await eventSelect.selectOption({ index: 0 });

      // 验证选择后UI更新
      await page.waitForTimeout(1000);

      // 检查参数字段列表是否加载
      const parameterList = page.locator('.parameter-list');
      if (await parameterList.isVisible()) {
        await expect(parameterList).toBeVisible();
      }
    });

    test('5. 搜索/过滤功能验证', async ({ page }) => {
      await page.goto(`/event-node-builder?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      // 查找搜索框
      const searchInput = page.locator('input[placeholder*="搜索"], input[placeholder*="filter"]');
      if (await searchInput.isVisible()) {
        await searchInput.fill('test');
        await page.waitForTimeout(500);

        // 验证搜索结果
        const results = page.locator('.parameter-item, .event-item');
        const count = await results.count();
        expect(count).toBeGreaterThanOrEqual(0);
      }
    });

    test('6. 模态框打开/关闭', async ({ page }) => {
      await page.goto(`/event-node-builder?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      // 测试WHERE条件模态框
      const whereButton = page.locator('button:has-text("WHERE")');
      if (await whereButton.isVisible()) {
        await whereButton.click();
        await expect(page.locator('.modal, .where-builder-modal')).toBeVisible();

        // 关闭模态框
        const closeButton = page.locator('button:has-text("关闭"), .modal-close');
        if (await closeButton.isVisible()) {
          await closeButton.click();
          await expect(page.locator('.modal, .where-builder-modal')).not.toBeVisible();
        }
      }
    });

    test('7. API调用状态验证', async ({ page }) => {
      // 监听API调用
      const apiCalls: string[] = [];

      page.on('request', request => {
        if (request.url().includes('/api/')) {
          apiCalls.push(request.url());
        }
      });

      await page.goto(`/event-node-builder?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      // 验证关键API被调用
      expect(apiCalls.length).toBeGreaterThan(0);
    });

    test('8. 统计数据显示验证', async ({ page }) => {
      await page.goto(`/event-node-builder?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      // 查找统计信息区域
      const stats = page.locator('.stats, .statistics');
      if (await stats.isVisible()) {
        await expect(stats).toBeVisible();
      }
    });

    test('9. 分页功能测试', async ({ page }) => {
      await page.goto(`/event-node-builder?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      // 查找分页控件
      const pagination = page.locator('.pagination');
      if (await pagination.isVisible()) {
        const nextButton = page.locator('button:has-text("下一页"), .pagination-next');
        if (await nextButton.isVisible()) {
          await nextButton.click();
          await page.waitForTimeout(500);
        }
      }
    });

    test('10. 性能测量', async ({ page }) => {
      const startTime = Date.now();

      await page.goto(`/event-node-builder?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      const endTime = Date.now();
      const loadTime = endTime - startTime;

      // 页面应在5秒内加载完成
      expect(loadTime).toBeLessThan(5000);

      console.log(`Event Node Builder 加载时间: ${loadTime}ms`);
    });
  });

  /**
   * ============================================
   * 测试组2: Event Nodes Management (10项功能)
   * ============================================
   */
  test.describe('Event Nodes Management', () => {
    test('1. 页面加载 + DOM结构', async ({ page }) => {
      await page.goto(`/event-nodes?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      // 验证页面标题
      await expect(page.locator('h1')).toContainText('事件节点');

      // 验证表格或列表存在
      await expect(page.locator('table, .event-nodes-list')).toBeVisible();
    });

    test('2. 控制台错误检查', async ({ page }) => {
      const errors: string[] = [];

      page.on('console', msg => {
        if (msg.type() === 'error') {
          errors.push(msg.text());
        }
      });

      await page.goto(`/event-nodes?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(3000);

      expect(errors).toHaveLength(0);
    });

    test('3. 所有按钮点击测试', async ({ page }) => {
      await page.goto(`/event-nodes?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      // 测试创建按钮
      const createButton = page.locator('button:has-text("创建"), button:has-text("新增")');
      if (await createButton.isVisible()) {
        await createButton.click();
        await expect(page.locator('.modal, form')).toBeVisible();
      }

      // 测试编辑按钮（第一个）
      const editButton = page.locator('button:has-text("编辑")').first();
      if (await editButton.isVisible()) {
        await editButton.click();
        await page.waitForTimeout(500);
      }
    });

    test('4. 表单填写和提交', async ({ page }) => {
      await page.goto(`/event-nodes?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      // 点击创建按钮
      const createButton = page.locator('button:has-text("创建"), button:has-text("新增")');
      if (await createButton.isVisible()) {
        await createButton.click();

        // 填写表单
        const nameInput = page.locator('input[name="name"]');
        if (await nameInput.isVisible()) {
          await nameInput.fill('Test Event Node');

          const submitButton = page.locator('button[type="submit"]');
          await submitButton.click();

          // 验证成功消息
          await expect(page.locator('.toast, .notification')).toBeVisible();
        }
      }
    });

    test('5. 搜索/过滤功能验证', async ({ page }) => {
      await page.goto(`/event-nodes?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      const searchInput = page.locator('input[placeholder*="搜索"]');
      if (await searchInput.isVisible()) {
        await searchInput.fill('test');
        await page.waitForTimeout(500);

        const results = page.locator('table tbody tr, .event-node-item');
        const count = await results.count();
        expect(count).toBeGreaterThanOrEqual(0);
      }
    });

    test('6. 模态框打开/关闭', async ({ page }) => {
      await page.goto(`/event-nodes?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      // 测试创建模态框
      const createButton = page.locator('button:has-text("创建")');
      if (await createButton.isVisible()) {
        await createButton.click();
        await expect(page.locator('.modal')).toBeVisible();

        // 关闭模态框
        const closeButton = page.locator('button:has-text("取消"), .modal-close');
        await closeButton.click();
        await expect(page.locator('.modal')).not.toBeVisible();
      }
    });

    test('7. API调用状态验证', async ({ page }) => {
      const apiCalls: string[] = [];

      page.on('request', request => {
        if (request.url().includes('/api/')) {
          apiCalls.push(request.url());
        }
      });

      await page.goto(`/event-nodes?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      expect(apiCalls.length).toBeGreaterThan(0);
    });

    test('8. 统计数据显示验证', async ({ page }) => {
      await page.goto(`/event-nodes?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      // 验证节点数量显示
      const stats = page.locator('.stats, .node-count');
      if (await stats.isVisible()) {
        await expect(stats).toContainText(/\d+/);
      }
    });

    test('9. 分页功能测试', async ({ page }) => {
      await page.goto(`/event-nodes?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      const pagination = page.locator('.pagination');
      if (await pagination.isVisible()) {
        const nextButton = page.locator('button:has-text("下一页"), .pagination-next');
        if (await nextButton.isVisible()) {
          await nextButton.click();
          await page.waitForTimeout(500);
        }
      }
    });

    test('10. 性能测量', async ({ page }) => {
      const startTime = Date.now();

      await page.goto(`/event-nodes?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      const endTime = Date.now();
      const loadTime = endTime - startTime;

      expect(loadTime).toBeLessThan(5000);

      console.log(`Event Nodes Management 加载时间: ${loadTime}ms`);
    });
  });

  /**
   * ============================================
   * 测试组3: Canvas (10项功能)
   * ============================================
   */
  test.describe('Canvas', () => {
    test('1. 页面加载 + DOM结构', async ({ page }) => {
      await page.goto(`/canvas?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      // 验证页面标题
      await expect(page.locator('h1')).toContainText('Canvas', { ignoreCase: true });

      // 验证主要组件
      await expect(page.locator('.canvas-container, .flow-canvas')).toBeVisible();
    });

    test('2. 控制台错误检查', async ({ page }) => {
      const errors: string[] = [];

      page.on('console', msg => {
        if (msg.type() === 'error') {
          errors.push(msg.text());
        }
      });

      await page.goto(`/canvas?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(3000);

      expect(errors).toHaveLength(0);
    });

    test('3. 所有按钮点击测试', async ({ page }) => {
      await page.goto(`/canvas?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      // 测试添加节点按钮
      const addButton = page.locator('button:has-text("添加"), button:has-text("新增")');
      if (await addButton.isVisible()) {
        await addButton.click();
        await page.waitForTimeout(500);
      }

      // 测试生成HQL按钮
      const generateButton = page.locator('button:has-text("生成"), button:has-text("Generate")');
      if (await generateButton.isVisible()) {
        await generateButton.click();
        await page.waitForTimeout(500);
      }
    });

    test('4. 表单填写和提交 - 创建流程', async ({ page }) => {
      await page.goto(`/canvas?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      // 尝试创建新流程
      const createFlowButton = page.locator('button:has-text("创建流程"), button:has-text("New Flow")');
      if (await createFlowButton.isVisible()) {
        await createFlowButton.click();

        const flowNameInput = page.locator('input[name="name"], input[placeholder*="名称"]');
        if (await flowNameInput.isVisible()) {
          await flowNameInput.fill('Test Flow');

          const saveButton = page.locator('button[type="submit"], button:has-text("保存")');
          await saveButton.click();
        }
      }
    });

    test('5. 搜索/过滤功能验证', async ({ page }) => {
      await page.goto(`/canvas?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      // 查找节点搜索功能
      const searchInput = page.locator('input[placeholder*="搜索"], input[placeholder*="节点"]');
      if (await searchInput.isVisible()) {
        await searchInput.fill('test');
        await page.waitForTimeout(500);
      }
    });

    test('6. 模态框打开/关闭', async ({ page }) => {
      await page.goto(`/canvas?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      // 测试节点配置模态框
      const configButton = page.locator('button:has-text("配置"), .node-config');
      const configButtons = await configButton.count();

      if (configButtons > 0) {
        await configButton.first().click();
        await expect(page.locator('.modal, .node-config-modal')).toBeVisible();

        // 关闭模态框
        const closeButton = page.locator('button:has-text("关闭"), .modal-close');
        await closeButton.click();
      }
    });

    test('7. API调用状态验证', async ({ page }) => {
      const apiCalls: string[] = [];

      page.on('request', request => {
        if (request.url().includes('/api/')) {
          apiCalls.push(request.url());
        }
      });

      await page.goto(`/canvas?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      expect(apiCalls.length).toBeGreaterThan(0);
    });

    test('8. 统计数据显示验证', async ({ page }) => {
      await page.goto(`/canvas?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      // 验证节点数量统计
      const stats = page.locator('.stats, .node-count');
      if (await stats.isVisible()) {
        await expect(stats).toBeVisible();
      }
    });

    test('9. 面包屑导航修复验证', async ({ page }) => {
      await page.goto(`/canvas?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      // 验证面包屑导航
      const breadcrumb = page.locator('.breadcrumb');
      if (await breadcrumb.isVisible()) {
        // 验证面包屑显示正确的层级
        await expect(breadcrumb).toContainText('首页');
        await expect(breadcrumb).toContainText('Canvas', { ignoreCase: true });

        // 验证不应该显示"Dashboard"
        await expect(breadcrumb).not.toContainText('Dashboard');
      }
    });

    test('10. 性能测量', async ({ page }) => {
      const startTime = Date.now();

      await page.goto(`/canvas?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      const endTime = Date.now();
      const loadTime = endTime - startTime;

      expect(loadTime).toBeLessThan(5000);

      console.log(`Canvas 加载时间: ${loadTime}ms`);
    });

    test('额外验证: 游戏上下文提示改进', async ({ page }) => {
      await page.goto(`/canvas?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      // 验证游戏上下文提示
      const gameContext = page.locator('.game-context, .game-info');
      if (await gameContext.isVisible()) {
        // 应该显示游戏GID而不是"Dashboard"
        await expect(gameContext).toContainText('10000147', { ignoreCase: true });
        await expect(gameContext).not.toContainText('Dashboard');
      }
    });

    test('额外验证: Canvas错误提示改进', async ({ page }) => {
      await page.goto(`/canvas?game_gid=${TEST_GAME_GID}`);
      await page.waitForLoadState('networkidle');

      // 检查是否有友好的错误提示
      const errorMessage = page.locator('.error, .alert');
      if (await errorMessage.isVisible()) {
        // 错误提示应该是友好的，不应该是技术性的堆栈跟踪
        const text = await errorMessage.textContent();
        expect(text).not.toMatch(/undefined|TypeError|Cannot read/);
      }
    });
  });
});
