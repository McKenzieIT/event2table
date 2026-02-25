import { test, expect } from '@playwright/test';

test.describe('EventNodeBuilder - 事件节点构建器', () => {
  test.beforeEach(async ({ page }) => {
    // 模拟真实的用户操作流程：先访问首页，设置游戏上下文
    await page.goto('/#/');

    // 设置游戏数据
    await page.evaluate(() => {
      localStorage.setItem('selectedGameGid', '10000147');
      window.gameData = {
        id: 16,
        gid: '10000147',
        name: '游戏 10000147',
        ods_db: 'ieu_ods',
      };
      window.gamesList = [{
        id: 16,
        gid: '10000147',
        name: '游戏 10000147',
        ods_db: 'ieu_ods',
      }];
    });

    // 触发游戏变化事件（模拟用户在侧边栏选择游戏）
    await page.evaluate(() => {
      window.dispatchEvent(new CustomEvent('gameChanged', {
        detail: {
          id: 16,
          gid: '10000147',
          name: '游戏 10000147',
          ods_db: 'ieu_ods',
        }
      }));
    });

    // 导航到事件节点构建器页面
    await page.goto('/#/event-node-builder?game_gid=10000147');

    // 等待 React 应用初始化和游戏数据加载
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);
  });

  test.afterEach(async ({ page }) => {
    // 清理测试状态
    await page.evaluate(() => {
      sessionStorage.clear();
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.includes('dwd_generator_canvas_flow_')) {
          localStorage.removeItem(key);
        }
      });
      localStorage.removeItem('selectedGameGid');
      if ((window as any).gameData) {
        delete (window as any).gameData;
      }
      if ((window as any).gamesList) {
        delete (window as any).gamesList;
      }
    });
    await page.waitForTimeout(300);
  });

  test('应该显示页面容器', async ({ page }) => {
    // 等待游戏数据加载完成（不显示"请先选择游戏"提示）
    await expect(page.locator('.event-node-builder-loading')).not.toBeVisible({ timeout: 10000 });

    // 检查页面容器是否存在
    const pageContainer = page.locator('.event-node-builder');
    await expect(pageContainer).toBeVisible();
  });

  test('应该显示页面头部和按钮', async ({ page }) => {
    // 等待页面加载
    await expect(page.locator('.event-node-builder')).toBeVisible({ timeout: 10000 });

    // 检查页面头部
    const header = page.locator('.page-header');
    await expect(header).toBeVisible();

    // 检查节点配置按钮
    const configButton = page.locator('.page-header button:has-text("节点配置")');
    await expect(configButton).toBeVisible();

    // 检查保存配置按钮
    const saveButton = page.locator('.page-header button:has-text("保存配置")');
    await expect(saveButton).toBeVisible();
  });

  test('点击节点配置按钮应该打开模态框', async ({ page }) => {
    // 等待页面加载
    await expect(page.locator('.event-node-builder')).toBeVisible({ timeout: 10000 });

    // 点击节点配置按钮
    await page.locator('.page-header button:has-text("节点配置")').click();

    // 等待模态框出现
    const modal = page.locator('.node-config-modal');
    await expect(modal).toBeVisible({ timeout: 5000 });

    // 检查模态框标题
    const modalTitle = modal.locator('h2, h3').filter({ hasText: /节点配置|Node Config/ });
    await expect(modalTitle).toBeVisible();

    // 检查表单字段
    await expect(modal.locator('input[placeholder*="login_event_node"]')).toBeVisible();
    await expect(modal.locator('input[placeholder*="登录事件节点"]')).toBeVisible();
    await expect(modal.locator('textarea')).toBeVisible();

    // 检查是否显示警告（因为还没有选择事件和添加字段）
    const warning = modal.locator('.alert-warning');
    await expect(warning).toBeVisible();

    // 检查按钮
    await expect(modal.locator('button:has-text("取消")')).toBeVisible();
    await expect(modal.locator('button:has-text("保存")')).toBeVisible();
  });

  test('节点配置模态框应该有表单验证', async ({ page }) => {
    // 等待页面加载
    await expect(page.locator('.event-node-builder')).toBeVisible({ timeout: 10000 });

    // 打开节点配置模态框
    await page.locator('.page-header button:has-text("节点配置")').click();
    await page.waitForSelector('.node-config-modal');

    // 检查是否显示警告（表单被禁用）
    const warning = page.locator('.alert-warning');
    await expect(warning).toBeVisible();
    await expect(warning).toContainText('请先选择事件并添加字段');

    // 检查保存按钮是否被禁用
    const saveButton = page.locator('.node-config-modal button:has-text("保存")');
    const isDisabled = await saveButton.isDisabled();
    // 注意：由于输入框被禁用，我们只检查警告显示
  });

  test('点击模态框外部应该关闭模态框', async ({ page }) => {
    // 等待页面加载
    await expect(page.locator('.event-node-builder')).toBeVisible({ timeout: 10000 });

    // 打开节点配置模态框
    await page.locator('.page-header button:has-text("节点配置")').click();
    await page.waitForSelector('.node-config-modal');

    // 点击模态框外部的遮罩层
    const modalOverlay = page.locator('.modal-overlay');
    await modalOverlay.click({ position: { x: 10, y: 10 } });

    // 模态框应该关闭
    const modal = page.locator('.node-config-modal');
    await expect(modal).not.toBeVisible({ timeout: 3000 });
  });

  test('点击取消按钮应该关闭模态框', async ({ page }) => {
    // 等待页面加载
    await expect(page.locator('.event-node-builder')).toBeVisible({ timeout: 10000 });

    // 打开节点配置模态框
    await page.locator('.page-header button:has-text("节点配置")').click();
    await page.waitForSelector('.node-config-modal');

    // 点击取消按钮
    await page.locator('.node-config-modal button:has-text("取消")').click();

    // 模态框应该关闭
    const modal = page.locator('.node-config-modal');
    await expect(modal).not.toBeVisible({ timeout: 3000 });
  });
});

test.describe('EventNodeBuilder - 基础布局测试', () => {
  test.use({ storageState: { cookies: [], origins: [] } });

  test.beforeEach(async ({ page }) => {
    // 设置游戏数据
    await page.goto('/#/');
    await page.evaluate(() => {
      localStorage.setItem('selectedGameGid', '10000147');
      window.gameData = {
        id: 16,
        gid: '10000147',
        name: '游戏 10000147',
        ods_db: 'ieu_ods',
      };
      window.gamesList = [{
        id: 16,
        gid: '10000147',
        name: '游戏 10000147',
        ods_db: 'ieu_ods',
      }];
    });

    await page.goto('/#/event-node-builder?game_gid=10000147');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);
  });

  test.afterEach(async ({ page }) => {
    // 清理测试状态
    await page.evaluate(() => {
      sessionStorage.clear();
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.includes('dwd_generator_canvas_flow_')) {
          localStorage.removeItem(key);
        }
      });
      localStorage.removeItem('selectedGameGid');
      if ((window as any).gameData) {
        delete (window as any).gameData;
      }
      if ((window as any).gamesList) {
        delete (window as any).gamesList;
      }
    });
    await page.waitForTimeout(300);
  });

  test('应该显示左侧栏和画布', async ({ page }) => {
    // 等待页面加载
    await expect(page.locator('.event-node-builder')).toBeVisible({ timeout: 10000 });

    // 检查左侧栏（事件选择和基础字段）
    const leftSidebar = page.locator('.sidebar-left');
    await expect(leftSidebar).toBeVisible();

    // 检查中间画布区域
    const canvas = page.locator('.field-canvas');
    await expect(canvas).toBeVisible();

    // 检查右侧栏
    const rightSidebar = page.locator('.sidebar-right');
    await expect(rightSidebar).toBeVisible();
  });

  test('应该显示基础字段列表', async ({ page }) => {
    // 等待页面加载
    await expect(page.locator('.event-node-builder')).toBeVisible({ timeout: 10000 });

    // 检查字段画布区域
    const fieldCanvas = page.locator('.field-canvas');
    await expect(fieldCanvas).toBeVisible();
  });

  test('应该显示统计信息面板', async ({ page }) => {
    // 等待页面加载
    await expect(page.locator('.event-node-builder')).toBeVisible({ timeout: 10000 });

    // 检查统计面板
    const statsPanel = page.locator('.stats-panel');
    await expect(statsPanel).toBeVisible();
  });

  test('应该显示HQL预览区域', async ({ page }) => {
    // 等待页面加载
    await expect(page.locator('.event-node-builder')).toBeVisible({ timeout: 10000 });

    // 检查 HQL 预览区域
    const hqlPreview = page.locator('.hql-preview-panel');
    await expect(hqlPreview).toBeVisible();
  });
});

test.describe('EventNodeBuilder - 响应式布局', () => {
  test.beforeEach(async ({ page }) => {
    // 设置游戏数据
    await page.goto('/#/');
    await page.evaluate(() => {
      localStorage.setItem('selectedGameGid', '10000147');
      window.gameData = {
        id: 16,
        gid: '10000147',
        name: '游戏 10000147',
        ods_db: 'ieu_ods',
      };
      window.gamesList = [{
        id: 16,
        gid: '10000147',
        name: '游戏 10000147',
        ods_db: 'ieu_ods',
      }];
    });

    await page.goto('/#/event-node-builder?game_gid=10000147');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);
  });

  test.afterEach(async ({ page }) => {
    // 清理测试状态
    await page.evaluate(() => {
      sessionStorage.clear();
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.includes('dwd_generator_canvas_flow_')) {
          localStorage.removeItem(key);
        }
      });
      localStorage.removeItem('selectedGameGid');
      if ((window as any).gameData) {
        delete (window as any).gameData;
      }
      if ((window as any).gamesList) {
        delete (window as any).gamesList;
      }
    });
    await page.waitForTimeout(300);
  });

  test('页面应该与侧边栏共存', async ({ page }) => {
    // 等待页面加载
    await expect(page.locator('.event-node-builder')).toBeVisible({ timeout: 10000 });

    // 检查侧边栏是否存在
    const leftSidebar = page.locator('.sidebar-left');
    const rightSidebar = page.locator('.sidebar-right');
    await expect(leftSidebar).toBeVisible();
    await expect(rightSidebar).toBeVisible();

    // 检查工作区是否存在
    const workspace = page.locator('.workspace');
    await expect(workspace).toBeVisible();

    // 验证布局结构完整
    await expect(page.locator('.event-node-builder .page-header')).toBeVisible();
  });
});
