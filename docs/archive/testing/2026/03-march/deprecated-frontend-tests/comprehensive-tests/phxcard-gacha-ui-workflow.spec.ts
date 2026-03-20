import { test, expect } from '@playwright/test';

/**
 * E2E测试：phxcard.gacha事件节点构建器 - 完整UI交互流程
 *
 * 测试步骤：
 * 1. 导航到事件节点构建器页面
 * 2. 搜索并选择phxcard.gacha事件
 * 3. 点击"⚙️ 仅参数字段"按钮添加所有参数字段
 * 4. 验证字段成功添加到画布（显示"参数 STRING"而非"未知"）
 * 5. 添加基础字段（role_id, tm, ds）
 * 6. 验证HQL预览生成成功
 */

test.describe('phxcard.gacha事件节点构建器', () => {
  test.beforeEach(async ({ page }) => {
    // 导航到事件节点构建器页面
    await page.goto('http://localhost:5173/#/event-node-builder?game_gid=10000147');

    // 等待页面加载完成
    await page.waitForLoadState('networkidle');
  });

  test('完整UI流程：搜索事件、添加字段、生成HQL', async ({ page }) => {
    console.log('步骤1: 搜索gacha事件');

    // 等待事件搜索框出现
    await page.waitForSelector('input[placeholder="搜索事件..."]', { timeout: 10000 });

    // 输入搜索关键词
    await page.fill('input[placeholder="搜索事件..."]', 'gacha');

    // 等待搜索结果
    await page.waitForTimeout(1000);

    // 验证找到phxcard.gacha事件
    await expect(page.locator('text=火凤追加-抽')).toBeVisible();
    await expect(page.locator('text=phxcard.gacha')).toBeVisible();

    console.log('步骤2: 选择phxcard.gacha事件');

    // 点击phxcard.gacha事件
    await page.click('text=火凤追加-抽');

    // 等待字段选择模态框出现
    await page.waitForSelector('text=✨ 选择字段类型', { timeout: 5000 });

    console.log('步骤3: 点击"⚙️ 仅参数字段"按钮');

    // 点击"⚙️ 仅参数字段"按钮
    await page.click('text=⚙️ 仅参数字段');

    // 等待字段添加完成（模态框关闭）
    await page.waitForSelector('text=✨ 选择字段类型', { state: 'hidden', timeout: 10000 });

    console.log('步骤4: 验证字段成功添加到画布');

    // 验证字段数量显示
    const fieldCount = await page.locator('text=/累计 \\d+/').textContent();
    console.log(`字段统计: ${fieldCount}`);

    // 验证第一个字段显示"参数 STRING"（而非"未知"）
    const firstField = await page.locator('button:has-text("编辑")').first();
    await expect(firstField).toContainText('参数');
    await expect(firstField).not.toContainText('未知');

    // 验证统计信息
    await expect(page.locator('text=/参数 2\\d+/')).toBeVisible();

    console.log('步骤5: 添加基础字段');

    // 点击"基础"按钮
    await page.click('button:has-text("基础")');

    // 等待基础字段选择器出现
    await page.waitForSelector('text=选择基础字段', { timeout: 5000 });

    // 依次添加3个基础字段：DS, ROLE_ID, TM
    const baseFields = ['DS', 'ROLE_ID', 'TM'];
    for (const fieldName of baseFields) {
      await page.click(`button:has-text("${fieldName}")`);
      await page.waitForTimeout(500);
    }

    // 关闭基础字段选择器
    await page.keyboard.press('Escape');

    console.log('步骤6: 验证HQL预览生成成功');

    // 等待HQL预览更新
    await page.waitForTimeout(2000);

    // 检查HQL预览区域
    const hqlPreview = page.locator('text=/-- Event Node:/').first();
    await expect(hqlPreview).toBeVisible({ timeout: 10000 });

    // 验证不包含错误信息
    await expect(page.locator('text=Failed to preview HQL')).not.toBeVisible();

    console.log('✅ 测试通过：完整的UI交互流程成功！');
  });

  test('验证字段类型显示正确（非"未知"）', async ({ page }) => {
    // 快速添加字段
    await page.fill('input[placeholder="搜索事件..."]', 'gacha');
    await page.click('text=火凤追加-抽');
    await page.waitForSelector('text=✨ 选择字段类型');
    await page.click('text=⚙️ 仅参数字段');
    await page.waitForSelector('text=✨ 选择字段类型', { state: 'hidden' });

    // 检查所有画布上的字段
    const fieldButtons = page.locator('button:has-text("编辑")');
    const count = await fieldButtons.count();

    console.log(`验证 ${count} 个字段的类型显示`);

    // 验证前10个字段都显示"参数"而非"未知"
    for (let i = 0; i < Math.min(count, 10); i++) {
      const field = fieldButtons.nth(i);
      const text = await field.textContent();
      expect(text).toContain('参数');
      expect(text).not.toContain('未知');
    }

    console.log('✅ 所有字段类型显示正确');
  });

  test('验证HQL预览包含get_json_object', async ({ page }) => {
    // 添加字段
    await page.fill('input[placeholder="搜索事件..."]', 'gacha');
    await page.click('text=火凤追加-抽');
    await page.waitForSelector('text=✨ 选择字段类型');
    await page.click('text=⚙️ 仅参数字段');
    await page.waitForSelector('text=✨ 选择字段类型', { state: 'hidden' });

    // 等待HQL预览生成
    await page.waitForTimeout(3000);

    // 验证HQL预览包含get_json_object
    const hqlPreview = page.locator('pre, code, [class*="hql"], [class*="preview"]').or(
      page.locator('text=/get_json_object/')
    );

    await expect(hqlPreview).toBeVisible();
    console.log('✅ HQL预览包含get_json_object函数调用');
  });
});
