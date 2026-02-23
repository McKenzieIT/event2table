/**
 * BaseModal ESC关闭功能E2E测试
 * BaseModal ESC Close Functionality E2E Tests
 */

import { test, expect } from '@playwright/test';

test.describe('BaseModal ESC Close Functionality', () => {
  test.beforeEach(async ({ page }) => {
    // 导航到事件节点页面
    await page.goto('http://localhost:5001/event-nodes');

    // 等待页面加载
    await page.waitForLoadState('networkidle');
  });

  test.afterEach(async ({ page }) => {
    // 清理测试状态
    await page.evaluate(() => {
      sessionStorage.clear();
      localStorage.removeItem('eventNodeFilters');
      localStorage.removeItem('eventNodesSearchQuery');
    });
    await page.waitForTimeout(300);
  });

  test('QuickEditModal - 应该在无修改时通过ESC直接关闭', async ({ page }) => {
    // 等待表格加载
    await page.waitForSelector('table tbody tr', { timeout: 5000 });

    // 获取第一行
    const firstRow = page.locator('table tbody tr').first();
    const editButton = firstRow.locator('button').filter({ hasText: '快速编辑' });

    // 点击快速编辑按钮
    await editButton.click();

    // 等待模态框出现
    await expect(page.locator('.modal-content')).toBeVisible({ timeout: 3000 });

    // 按ESC键
    await page.keyboard.press('Escape');

    // 验证模态框关闭
    await expect(page.locator('.modal-content')).not.toBeVisible({ timeout: 2000 });
  });

  test('QuickEditModal - 应该在有修改时按ESC显示确认对话框', async ({ page }) => {
    // 等待表格加载
    await page.waitForSelector('table tbody tr', { timeout: 5000 });

    // 获取第一行
    const firstRow = page.locator('table tbody tr').first();
    const editButton = firstRow.locator('button').filter({ hasText: '快速编辑' });

    // 点击快速编辑按钮
    await editButton.click();

    // 等待模态框出现
    await expect(page.locator('.modal-content')).toBeVisible({ timeout: 3000 });

    // 修改中文名称
    const nameCnInput = page.locator('#name_cn');
    await nameCnInput.fill('测试修改');

    // 按ESC键
    await page.keyboard.press('Escape');

    // 验证确认对话框出现
    await expect(page.locator('text=有未保存的修改，确定要关闭吗？')).toBeVisible({ timeout: 2000 });

    // 点击"继续编辑"
    const continueButton = page.locator('button', { hasText: '继续编辑' });
    await continueButton.click();

    // 验证模态框仍然打开
    await expect(page.locator('.modal-content')).toBeVisible();

    // 验证输入框的值仍然存在
    await expect(nameCnInput).toHaveValue('测试修改');
  });

  test('QuickEditModal - 应该能通过确认对话框放弃修改', async ({ page }) => {
    // 等待表格加载
    await page.waitForSelector('table tbody tr', { timeout: 5000 });

    // 获取第一行
    const firstRow = page.locator('table tbody tr').first();
    const editButton = firstRow.locator('button').filter({ hasText: '快速编辑' });

    // 点击快速编辑按钮
    await editButton.click();

    // 等待模态框出现
    await expect(page.locator('.modal-content')).toBeVisible({ timeout: 3000 });

    // 修改中文名称
    const nameCnInput = page.locator('#name_cn');
    await nameCnInput.fill('测试修改');

    // 按ESC键
    await page.keyboard.press('Escape');

    // 验证确认对话框出现
    await expect(page.locator('text=有未保存的修改，确定要关闭吗？')).toBeVisible({ timeout: 2000 });

    // 点击"放弃修改"
    const discardButton = page.locator('button', { hasText: '放弃修改' });
    await discardButton.click();

    // 验证模态框关闭
    await expect(page.locator('.modal-content')).not.toBeVisible({ timeout: 2000 });
  });

  test('QuickEditModal - 在输入框中按ESC不应该关闭模态框', async ({ page }) => {
    // 等待表格加载
    await page.waitForSelector('table tbody tr', { timeout: 5000 });

    // 获取第一行
    const firstRow = page.locator('table tbody tr').first();
    const editButton = firstRow.locator('button').filter({ hasText: '快速编辑' });

    // 点击快速编辑按钮
    await editButton.click();

    // 等待模态框出现
    await expect(page.locator('.modal-content')).toBeVisible({ timeout: 3000 });

    // 点击输入框并输入内容
    const nameCnInput = page.locator('#name_cn');
    await nameCnInput.click();
    await nameCnInput.fill('测试内容');

    // 确保焦点仍在输入框中
    await nameCnnInput.focus();

    // 按ESC键
    await page.keyboard.press('Escape');

    // 验证模态框仍然打开（不应该关闭）
    await expect(page.locator('.modal-content')).toBeVisible({ timeout: 1000 });
  });
});

test.describe('HQLPreviewModal ESC Functionality', () => {
  test.beforeEach(async ({ page }) => {
    // 导航到事件节点列表
    await page.goto('http://localhost:5001/event-nodes');

    // 选择游戏（如果需要）
    const gameSelector = page.locator('[data-testid="game-select"]');
    if (await gameSelector.isVisible()) {
      await gameSelector.selectOption('1');
    }

    await page.waitForLoadState('networkidle');
  });

  test.afterEach(async ({ page }) => {
    // 清理测试状态
    await page.evaluate(() => {
      sessionStorage.clear();
      localStorage.removeItem('eventNodeFilters');
      localStorage.removeItem('eventNodesSearchQuery');
    });
    await page.waitForTimeout(300);
  });

  test('HQLPreviewModal - 应该能通过ESC直接关闭', async ({ page }) => {
    // 点击第一个节点的"在构建器中编辑"按钮
    const editButton = page.locator('button').filter({ hasText: /在构建器中编辑/i }).first();
    await editButton.click();

    // 等待构建器页面加载
    await page.waitForLoadState('networkidle', { timeout: 10000 });

    // 添加一个字段（如果还没有）
    const addFieldButton = page.locator('button', { hasText: /添加字段/i });
    if (await addFieldButton.isVisible()) {
      await addFieldButton.click();
      // 等待字段添加
      await page.waitForTimeout(500);
    }

    // 点击HQL预览按钮
    const previewButton = page.locator('button', { hasText: /HQL预览/i });
    await previewButton.click();

    // 等待模态框出现
    await expect(page.locator('.hql-preview-modal')).toBeVisible({ timeout: 3000 });

    // 按ESC键
    await page.keyboard.press('Escape');

    // 验证模态框关闭
    await expect(page.locator('.hql-preview-modal')).not.toBeVisible({ timeout: 2000 });
  });
});

test.describe('WhereBuilderModal ESC Functionality', () => {
  test.beforeEach(async ({ page }) => {
    // 导航到事件节点列表
    await page.goto('http://localhost:5001/event-nodes');
    await page.waitForLoadState('networkidle');
  });

  test.afterEach(async ({ page }) => {
    // 清理测试状态
    await page.evaluate(() => {
      sessionStorage.clear();
      localStorage.removeItem('eventNodeFilters');
      localStorage.removeItem('eventNodesSearchQuery');
    });
    await page.waitForTimeout(300);
  });

  test('WhereBuilderModal - 应该在无修改时通过ESC直接关闭', async ({ page }) => {
    // 点击第一个节点的"在构建器中编辑"按钮
    const editButton = page.locator('button').filter({ hasText: /在构建器中编辑/i }).first();
    await editButton.click();

    // 等待构建器页面加载
    await page.waitForLoadState('networkidle', { timeout: 10000 });

    // 点击WHERE条件按钮
    const whereButton = page.locator('button', { hasText: /WHERE条件/i });
    await whereButton.click();

    // 等待模态框出现
    await expect(page.locator('.where-builder-modal')).toBeVisible({ timeout: 3000 });

    // 不修改任何条件，直接按ESC键
    await page.keyboard.press('Escape');

    // 验证模态框关闭
    await expect(page.locator('.where-builder-modal')).nottoBeVisible({ timeout: 2000 });
  });

  test('WhereBuilderModal - 应该在有修改时按ESC显示确认对话框', async ({ page }) => {
    // 点击第一个节点的"在构建器中编辑"按钮
    const editButton = page.locator('button').filter({ hasText: /在构建器中编辑/i }).first();
    await editButton.click();

    // 等待构建器页面加载
    await page.waitForLoadState('networkidle', { timeout: 10000 });

    // 点击WHERE条件按钮
    const whereButton = page.locator('button', { hasText: /WHERE条件/i });
    await whereButton.click();

    // 等待模态框出现
    await expect(page.locator('.where-builder-modal')).toBeVisible({ timeout: 3000 });

    // 添加一个条件（简化：假设有添加条件的按钮）
    const addConditionButton = page.locator('button', { hasText: /添加条件|Add Condition/i });
    if (await addConditionButton.isVisible()) {
      await addConditionButton.click();
      await page.waitForTimeout(500);
    }

    // 按ESC键
    await page.keyboard.press('Escape');

    // 验证确认对话框出现
    await expect(page.locator('text=有未保存的WHERE条件修改，确定要关闭吗？')).toBeVisible({ timeout: 2000 });

    // 点击"继续编辑"
    const continueButton = page.locator('button', { hasText: '继续编辑' });
    await continueButton.click();

    // 验证模态框仍然打开
    await expect(page.locator('.where-builder-modal')).toBeVisible();
  });
});

test.describe('Modal Click Outside Functionality', () => {
  test.afterEach(async ({ page }) => {
    // 清理测试状态
    await page.evaluate(() => {
      sessionStorage.clear();
      localStorage.removeItem('eventNodeFilters');
      localStorage.removeItem('eventNodesSearchQuery');
    });
    await page.waitForTimeout(300);
  });

  test('应该能通过点击背景遮罩关闭模态框', async ({ page }) => {
    await page.goto('http://localhost:5001/event-nodes');
    await page.waitForLoadState('networkidle');

    // 打开快速编辑模态框
    const firstRow = page.locator('table tbody tr').first();
    const editButton = firstRow.locator('button').filter({ hasText: '快速编辑' });
    await editButton.click();

    // 等待模态框出现
    await expect(page.locator('.modal-content')).toBeVisible({ timeout: 3000 });

    // 点击背景遮罩（模态框外部的区域）
    const overlay = page.locator('.modal-overlay');
    await overlay.click({ position: { x: 10, y: 10 } });

    // 验证模态框关闭
    await expect(page.locator('.modal-content')).not.toBeVisible({ timeout: 2000 });
  });

  test('点击模态框内容不应该关闭', async ({ page }) => {
    await page.goto('http://localhost:5001/event-nodes');
    await page.waitForLoadState('networkidle');

    // 打开快速编辑模态框
    const firstRow = page.locator('table tbody tr').first();
    const editButton = firstRow.locator('button').filter({ hasText: '快速编辑' });
    await editButton.click();

    // 等待模态框出现
    await expect(page.locator('.modal-content')).toBeVisible({ timeout: 3000 });

    // 点击模态框内容区域（标题）
    const modalTitle = page.locator('.modal-title, .modal-header h5');
    await modalTitle.click();

    // 验证模态框仍然打开
    await expect(page.locator('.modal-content')).toBeVisible();
  });
});
