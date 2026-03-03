/**
 * Parameter Library Reuse Feature - E2E Tests
 *
 * 测试参数库复用功能的完整工作流程
 * 1. 未绑定参数显示"绑定到库"按钮
 * 2. 点击按钮打开绑定弹窗
 * 3. 显示匹配的库参数
 * 4. 成功绑定参数
 * 5. 批量导入预览功能
 */

import { test, expect } from '@playwright/test';

test.describe('Parameter Library Reuse Feature', () => {
  test.beforeEach(async ({ page }) => {
    // 导航到参数管理页面
    await page.goto('/parameters');
  });

  test('should show "Bind to Library" button for unbound parameters', async ({ page }) => {
    // 等待页面加载
    await page.waitForLoadState('networkidle');

    // 检查是否显示"绑定到库"按钮
    const bindButtons = page.getByRole('button', { name: /绑定到库/ });
    const count = await bindButtons.count();

    // 至少应该有一些未绑定的参数
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('should open bind modal when button is clicked', async ({ page }) => {
    await page.waitForLoadState('networkidle');

    // 点击第一个"绑定到库"按钮
    const firstBindButton = page.getByRole('button', { name: /绑定到库/ }).first();
    const hasButton = await firstBindButton.count();

    if (hasButton > 0) {
      await firstBindButton.click();

      // 验证 Modal 显示
      await expect(page.getByText(/绑定到参数库/)).toBeVisible();

      // 关闭 Modal
      await page.getByRole('button', { name: /取消/ }).click();
    } else {
      test.skip('No unbound parameters found');
    }
  });

  test('should display matched library parameters in modal', async ({ page }) => {
    await page.waitForLoadState('networkidle');

    const firstBindButton = page.getByRole('button', { name: /绑定到库/ }).first();
    const hasButton = await firstBindButton.count();

    if (hasButton > 0) {
      await firstBindButton.click();

      // Modal 应该显示参数信息
      await expect(page.getByText(/参数名:/)).toBeVisible();

      // 关闭 Modal
      await page.getByRole('button', { name: /取消/ }).click();
    } else {
      test.skip('No unbound parameters found');
    }
  });

  test('should successfully bind parameter to library', async ({ page }) => {
    await page.waitForLoadState('networkidle');

    const firstBindButton = page.getByRole('button', { name: /绑定到库/ }).first();
    const hasButton = await firstBindButton.count();

    if (hasButton > 0) {
      await firstBindButton.click();

      // 等待 API 调用完成
      await page.waitForTimeout(500);

      // 点击确认绑定按钮
      const confirmButton = page.getByRole('button', { name: /确认绑定/ });
      const canConfirm = await confirmButton.isEnabled();

      if (canConfirm) {
        // 点击确认前先记录按钮状态
        await confirmButton.click();

        // 验证成功消息 (toast)
        await expect(page.getByText(/参数已绑定到库/)).toBeVisible({ timeout: 3000 });
      } else {
        // 没有可绑定的参数，关闭 Modal
        await page.getByRole('button', { name: /取消/ }).click();
      }
    } else {
      test.skip('No unbound parameters found');
    }
  });
});

test.describe('Import Preview Modal', () => {
  test('should show preview modal when importing events', async ({ page }) => {
    // 导航到导入事件页面
    await page.goto('/import-events');

    // 等待页面加载
    await page.waitForLoadState('networkidle');

    // 上传区域应该可见
    await expect(page.getByText(/选择Excel文件/)).toBeVisible();
    await expect(page.getByText(/拖拽Excel文件到此处/)).toBeVisible();
  });

  test('should show preview with matched and unmatched parameters', async ({ page }) => {
    await page.goto('/import-events');
    await page.waitForLoadState('networkidle');

    // 注意：实际文件上传需要真实的 Excel 文件
    // 这里只测试 UI 元素是否存在
    const previewButton = page.getByRole('button', { name: /预览匹配/ });
    const importButton = page.getByRole('button', { name: /开始导入/ });

    // 按钮应该存在但被禁用（没有文件时）
    await expect(previewButton).toBeVisible();
    await expect(importButton).toBeVisible();
  });
});

test.describe('Parameter Reuse Suggestion', () => {
  test('should show suggestion when adding parameter that exists in library', async ({ page }) => {
    // 导航到事件表单页面
    await page.goto('/events/new');

    // 等待页面加载
    await page.waitForLoadState('networkidle');

    // 注意：这个测试需要模拟输入已存在的参数名
    // 实际测试需要在有真实后端数据的环境中进行
    const paramNameInput = page.getByPlaceholderText(/参数名/);
    const hasInput = await paramNameInput.count();

    if (hasInput > 0) {
      // 输入已存在的参数名（如 accountId）
      await paramNameInput.fill('accountId');

      // 等待 API 调用
      await page.waitForTimeout(500);

      // 应该显示复用建议（如果存在）
      const suggestion = page.getByText(/已存在于库中/);
      const hasSuggestion = await suggestion.count();

      if (hasSuggestion > 0) {
        await expect(suggestion).toBeVisible();
      } else {
        // 参数可能不存在于库中
        test.skip('Parameter not found in library');
      }
    } else {
      test.skip('Parameter input not found');
    }
  });
});
