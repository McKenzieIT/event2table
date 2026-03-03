/**
 * GraphQL E2E 测试
 *
 * 使用Playwright进行端到端测试
 */

const { test, expect } = require('@playwright/test');

test.describe('GraphQL E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // 访问应用
    await page.goto('http://localhost:5001');
    
    // 等待应用加载完成
    await page.waitForSelector('[data-testid="app-loaded"]');
  });

  test('should display games list', async ({ page }) => {
    // 打开游戏管理模态框
    await page.click('[data-testid="open-game-management"]');
    
    // 等待模态框打开
    await page.waitForSelector('[data-testid="game-management-modal"]');
    
    // 等待游戏列表加载
    await page.waitForSelector('[data-testid="game-item"]');
    
    // 检查游戏列表是否显示
    const gameItems = await page.$$('[data-testid="game-item"]');
    expect(gameItems.length).toBeGreaterThan(0);
  });

  test('should search games', async ({ page }) => {
    // 打开游戏管理模态框
    await page.click('[data-testid="open-game-management"]');
    
    // 等待模态框打开
    await page.waitForSelector('[data-testid="game-management-modal"]');
    
    // 输入搜索关键词
    await page.fill('[data-testid="game-search-input"]', 'Game 1');
    
    // 等待搜索结果
    await page.waitForTimeout(500);
    
    // 检查搜索结果
    const gameItems = await page.$$('[data-testid="game-item"]');
    expect(gameItems.length).toBeGreaterThan(0);
  });

  test('should create a new game', async ({ page }) => {
    // 打开游戏管理模态框
    await page.click('[data-testid="open-game-management"]');
    
    // 等待模态框打开
    await page.waitForSelector('[data-testid="game-management-modal"]');
    
    // 点击添加游戏按钮
    await page.click('[data-testid="add-game-button"]');
    
    // 等待添加游戏模态框打开
    await page.waitForSelector('[data-testid="add-game-modal"]');
    
    // 填写表单
    await page.fill('[data-testid="game-gid-input"]', '9999');
    await page.fill('[data-testid="game-name-input"]', 'Test Game');
    await page.selectOption('[data-testid="game-odsdb-select"]', 'ieu_ods');
    
    // 提交表单
    await page.click('[data-testid="submit-game-button"]');
    
    // 等待成功提示
    await page.waitForSelector('[data-testid="success-toast"]');
  });
});
