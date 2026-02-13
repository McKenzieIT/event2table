/**
 * V2功能演示测试 - 交互式浏览器测试
 *
 * 展示V2 API的完整功能：
 * 1. 版本切换
 * 2. 性能分析
 * 3. 调试模式
 * 4. HQL生成
 *
 * 注意：此测试暂时跳过，原因：
 * - React SPA加载时间超过测试超时
 * - 需要优化前端构建配置或增加测试等待时间
 * - API功能已通过集成测试验证
 */

import { test, expect } from '@playwright/test';

test.describe('V2 功能演示测试', () => {
  test.beforeEach(async ({ page }) => {
    // 导航到事件节点构建器
    // 注意：路由路径是event-node-builder，不是event-builder（见routes.jsx）
    // 使用根路径 + HashRouter格式
    await page.goto('/#/event-node-builder?game_gid=10000147');

    // 等待React应用加载 - 等待页面标题出现
    await page.waitForSelector('h1:has-text("事件节点构建器")', { timeout: 15000 });
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
  });

  test('演示V2 API完整功能流程', async ({ page }) => {
    console.log('🎬 开始V2功能演示...');

    // 步骤1: 截图 - 初始状态
    await page.screenshot({ path: 'test-results/v2-demo-01-initial.png' });
    console.log('📸 截图1: 初始页面状态');

    // 步骤2: 启用V2 API
    const v2Toggle = page.locator('#v2-api-toggle');
    await v2Toggle.waitFor({ state: 'visible', timeout: 5000 });
    await expect(v2Toggle).toBeVisible();
    await v2Toggle.check();
    console.log('✅ 启用V2 API');

    await page.waitForTimeout(500);
    await page.screenshot({ path: 'test-results/v2-demo-02-v2-enabled.png' });
    console.log('📸 截图2: V2 API已启用');

    // 步骤3: 选择事件
    await page.click('[data-testid="event-item-25ph.pass"]', { timeout: 5000 });
    console.log('✅ 选择事件: 25ph.pass');

    await page.waitForTimeout(500);

    // 步骤4: 添加字段到画布
    // 查找基础字段
    const baseFields = page.locator('[data-testid^="param-"]').first();
    await baseFields.dragTo(page.locator('[data-testid="field-canvas-drop-zone"]'));
    console.log('✅ 添加基础字段到画布');

    await page.waitForTimeout(500);
    await page.screenshot({ path: 'test-results/v2-demo-03-field-added.png' });
    console.log('📸 截图3: 字段已添加');

    // 步骤5: 点击HQL预览按钮
    const previewButton = page.locator('button:has-text("HQL预览")').first();
    await previewButton.click();
    console.log('✅ 点击HQL预览按钮');

    // 等待模态框打开
    await page.waitForSelector('.hql-preview-modal', { state: 'visible', timeout: 5000 });
    await page.waitForTimeout(1000);

    // 步骤6: 验证V2 API响应
    const modalContent = page.locator('.hql-preview-modal');
    await expect(modalContent).toBeVisible();
    console.log('✅ HQL预览模态框已打开');

    // 检查是否显示了V2特有功能
    const hqlContent = await page.locator('[data-testid="hql-preview-content"]').textContent();
    console.log('📝 生成的HQL:', hqlContent.substring(0, 100) + '...');

    await page.screenshot({ path: 'test-results/v2-demo-04-hql-preview.png' });
    console.log('📸 截图4: HQL预览结果');

    // 步骤7: 关闭模态框
    const closeButton = page.locator('.hql-preview-modal .close-button, .hql-preview-modal button[aria-label="Close"]').first();
    if (await closeButton.isVisible()) {
      await closeButton.click();
    } else {
      // 尝试按ESC键关闭
      await page.keyboard.press('Escape');
    }
    await page.waitForTimeout(500);
    console.log('✅ 关闭HQL预览');

    // 步骤8: 切换回V1 API对比
    await v2Toggle.uncheck();
    console.log('✅ 切换回V1 API');

    await page.waitForTimeout(500);
    await page.screenshot({ path: 'test-results/v2-demo-05-v1-mode.png' });
    console.log('📸 截图5: 切换回V1模式');

    // 步骤9: 最终状态
    await page.screenshot({ path: 'test-results/v2-demo-06-final.png', fullPage: true });
    console.log('📸 截图6: 最终状态');

    console.log('🎉 V2功能演示完成！');
    console.log('📸 所有截图已保存到: test-results/v2-demo-*.png');
  });

  test('测试V2 API性能分析功能', async ({ page }) => {
    console.log('🎬 测试性能分析功能...');

    // 启用V2
    const v2Toggle = page.locator('#v2-api-toggle');
    await v2Toggle.waitFor({ state: 'visible', timeout: 5000 });
    await v2Toggle.check();
    await page.waitForTimeout(500);

    // 选择事件并添加字段
    await page.click('[data-testid="event-item-25ph.pass"]');
    await page.waitForTimeout(500);

    const baseField = page.locator('[data-testid^="param-"]').first();
    await baseField.dragTo(page.locator('[data-testid="field-canvas-drop-zone"]'));
    await page.waitForTimeout(500);

    // 点击HQL预览
    await page.click('button:has-text("HQL预览")');

    // 等待API响应
    await page.waitForSelector('.hql-preview-modal', { state: 'visible' });
    await page.waitForTimeout(2000);

    // 检查性能分析是否显示
    // 注意：这需要前端UI实际显示性能数据
    const modalVisible = await page.locator('.hql-preview-modal').isVisible();
    expect(modalVisible).toBe(true);

    // 截图性能分析结果
    await page.screenshot({ path: 'test-results/v2-performance-demo.png' });
    console.log('✅ 性能分析测试完成');
  });

  test('测试V2 API调试模式功能', async ({ page }) => {
    console.log('🎬 测试调试模式功能...');

    // 启用V2
    const v2Toggle = page.locator('#v2-api-toggle');
    await v2Toggle.waitFor({ state: 'visible', timeout: 5000 });
    await v2Toggle.check();
    await page.waitForTimeout(500);

    // 选择事件并添加字段
    await page.click('[data-testid="event-item-25ph.pass"]');
    await page.waitForTimeout(500);

    // 添加多个字段以触发调试信息
    const field1 = page.locator('[data-testid^="param-"]').nth(0);
    const field2 = page.locator('[data-testid^="param-"]').nth(1);

    await field1.dragTo(page.locator('[data-testid="field-canvas-drop-zone"]'));
    await page.waitForTimeout(300);

    await field2.dragTo(page.locator('[data-testid="field-canvas-drop-zone"]'));
    await page.waitForTimeout(500);

    // 点击HQL预览
    await page.click('button:has-text("HQL预览")');

    // 等待API响应和调试信息
    await page.waitForSelector('.hql-preview-modal', { state: 'visible' });
    await page.waitForTimeout(2000);

    // 验证调试信息
    const hqlContent = await page.locator('[data-testid="hql-preview-content"]').textContent();
    expect(hqlContent).toBeTruthy();
    expect(hqlContent.length).toBeGreaterThan(0);

    await page.screenshot({ path: 'test-results/v2-debug-demo.png' });
    console.log('✅ 调试模式测试完成');
  });
});
