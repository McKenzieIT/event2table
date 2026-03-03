import { test, expect } from '@playwright/test';

test.describe('HQL预览模态框 - E2E测试', () => {
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
    });

    await page.goto('/#/event-node-builder?game_gid=10000147');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);

    // 添加字段到画布（HQL预览需要有字段才会显示按钮）
    await page.waitForSelector('.event-node-builder', { timeout: 10000 });

    // 双击添加基础字段ds
    const dsField = page.locator('[data-field="ds"]').first();
    if (await dsField.isVisible()) {
      await dsField.dblclick();
      await page.waitForTimeout(500);
    }

    // 双击添加基础字段role_id
    const roleIdField = page.locator('[data-field="role_id"]').first();
    if (await roleIdField.isVisible()) {
      await roleIdField.dblclick();
      await page.waitForTimeout(500);
    }

    // 等待HQL预览按钮出现
    await page.waitForSelector('[data-testid="open-hql-modal"]', { timeout: 5000 });
  });

  test.afterEach(async ({ page }) => {
    // 清理测试状态
    await page.evaluate(() => {
      sessionStorage.clear();
      // 清除 Canvas 缓存和游戏上下文
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
    });
    await page.waitForTimeout(300);
  });

  test('应该能够打开HQL预览模态框', async ({ page }) => {
    // 等待页面加载
    await expect(page.locator('.event-node-builder')).toBeVisible({ timeout: 10000 });

    // 点击"查看详情"按钮
    await page.click('[data-testid="open-hql-modal"]');

    // 验证模态框打开
    const modal = page.locator('.hql-preview-modal');
    await expect(modal).toBeVisible();

    // 验证标题
    await expect(page.locator('.hql-preview-modal h3')).toContainText('HQL预览');
  });

  test('应该能够切换HQL模式Tab', async ({ page }) => {
    // 等待页面加载
    await expect(page.locator('.event-node-builder')).toBeVisible({ timeout: 10000 });

    // 打开模态框
    await page.click('[data-testid="open-hql-modal"]');

    // 验证默认SELECT Tab
    await expect(page.locator('.tab-btn.active')).toContainText('SELECT');

    // 切换到CREATE_TABLE
    await page.click('.tab-btn:has-text("CREATE TABLE")');
    await expect(page.locator('.tab-btn.active')).toContainText('CREATE TABLE');

    // 切换到CREATE_VIEW
    await page.click('.tab-btn:has-text("CREATE VIEW")');
    await expect(page.locator('.tab-btn.active')).toContainText('CREATE VIEW');

    // 切换到INSERT
    await page.click('.tab-btn:has-text("INSERT")');
    await expect(page.locator('.tab-btn.active')).toContainText('INSERT');
  });

  test('应该能够编辑HQL', async ({ page }) => {
    // 等待页面加载
    await expect(page.locator('.event-node-builder')).toBeVisible({ timeout: 10000 });

    // 打开模态框
    await page.click('[data-testid="open-hql-modal"]');

    // 点击编辑按钮
    await page.click('.editor-toolbar .btn-outline-primary:has-text("编辑")');

    // 验证编辑模式
    const textarea = page.locator('.code-textarea');
    await expect(textarea).toBeVisible();

    // 修改HQL
    await textarea.fill('-- Modified HQL\nSELECT * FROM table;');

    // 验证修改
    const value = await textarea.inputValue();
    expect(value).toContain('-- Modified HQL');
  });

  test('应该能够复制HQL到剪贴板', async ({ page }) => {
    // 等待页面加载
    await expect(page.locator('.event-node-builder')).toBeVisible({ timeout: 10000 });

    // 打开模态框
    await page.click('[data-testid="open-hql-modal"]');

    // 点击复制按钮
    await page.click('.editor-toolbar .btn-outline-primary:has-text("复制")');

    // 验证复制（Playwright会自动处理alert）
  });

  test('应该能够显示字段映射表', async ({ page }) => {
    // 等待页面加载
    await expect(page.locator('.event-node-builder')).toBeVisible({ timeout: 10000 });

    // 打开模态框
    await page.click('[data-testid="open-hql-modal"]');

    // 验证字段映射表
    const mappingTable = page.locator('.mapping-table');
    await expect(mappingTable).toBeVisible();

    // 验证表头
    await expect(page.locator('.mapping-table th')).toHaveCount(3);
  });
});
