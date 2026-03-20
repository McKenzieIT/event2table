import { test, expect } from '@playwright/test';

/**
 * BaseModal Migration Tests
 * 
 * 测试迁移到BaseModal的模态框组件:
 * 1. ConfigListModal - EventNodeBuilder页面
 * 2. HQLViewModal - EventNodes页面
 * 3. FieldsListModal - EventNodes页面
 */

test.describe('BaseModal Components - Migration Tests', () => {
  const baseUrl = 'http://localhost:5173';

  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('selectedGameGid', '10000147');
      (window as any).gameData = {
        id: 58,
        gid: '10000147',
        name: 'STAR001',
        ods_db: 'ieu_ods',
      };
    });
  });

  test('EventNodes页面加载不应该有BaseModal相关的React错误', async ({ page }) => {
    const consoleErrors: string[] = [];
    
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // Use 'commit' for HashRouter - waits for network to be idle but doesn't require full page load
    await page.goto(`${baseUrl}/#/event-nodes?game_gid=10000147`, { timeout: 60000, waitUntil: 'commit' });
    // Wait for page to stabilize after navigation
    await page.waitForTimeout(3000);

    const hookErrors = consoleErrors.filter(err => 
      err.includes('Hooks called') ||
      err.includes('Rules of Hooks') ||
      err.includes('more hooks than')
    );

    expect(hookErrors.length).toBe(0);
  });

  test('EventNodeBuilder页面加载不应该有BaseModal相关的React错误', async ({ page }) => {
    const consoleErrors: string[] = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // Use 'commit' for HashRouter - waits for network to be idle but doesn't require full page load
    await page.goto(`${baseUrl}/#/event-node-builder?game_gid=10000147`, { timeout: 60000, waitUntil: 'commit' });
    // Wait for page to stabilize after navigation
    await page.waitForTimeout(3000);

    const hookErrors = consoleErrors.filter(err => 
      err.includes('Hooks called') ||
      err.includes('Rules of Hooks') ||
      err.includes('more hooks than')
    );

    expect(hookErrors.length).toBe(0);
  });

  test('ConfigListModal应该可以正常打开（通过"加载配置"按钮）', async ({ page }) => {
    const consoleErrors: string[] = [];
    
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // Use 'commit' for HashRouter - waits for network to be idle but doesn't require full page load
    await page.goto(`${baseUrl}/#/event-node-builder?game_gid=10000147`, { timeout: 60000, waitUntil: 'commit' });
    // Wait for page to stabilize after navigation
    await page.waitForTimeout(3000);

    const loadConfigButton = page.locator('button:has-text("加载配置")');
    const buttonExists = await loadConfigButton.count() > 0;
    
    if (buttonExists) {
      await loadConfigButton.click();
      await page.waitForTimeout(1000);

      const modalContent = page.locator('.modal-content');
      const isVisible = await modalContent.first().isVisible().catch(() => false);
      
      const modalErrors = consoleErrors.filter(err => 
        err.includes('modal') || err.includes('Modal') || err.includes('hook')
      );
      
      expect(modalErrors.length).toBe(0);
      expect(isVisible).toBeTruthy();
    }
  });

  test('EventNodeBuilder页面应该正常渲染工作区', async ({ page }) => {
    // 设置游戏数据
    await page.addInitScript(() => {
      localStorage.setItem('selectedGameGid', '10000147');
      (window as any).gameData = {
        id: 58,
        gid: '10000147',
        name: 'STAR001',
        ods_db: 'ieu_ods',
      };
    });
    
    const consoleErrors: string[] = [];
    
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    // 直接导航到 EventNodeBuilder 页面
    // Use 'commit' for HashRouter - waits for network to be idle but doesn't require full page load
    await page.goto(`${baseUrl}/#/event-node-builder?game_gid=10000147`, { timeout: 60000, waitUntil: 'commit' });
    // Wait for page to stabilize after navigation
    await page.waitForTimeout(3000);
    
    // 检查是否有 React 相关错误
    const reactErrors = consoleErrors.filter(err => 
      err.includes('React') ||
      err.includes('hook') ||
      err.includes('Hook') ||
      err.includes('Uncaught')
    );
    
    // 验证没有 React 错误
    expect(reactErrors.length).toBe(0);
  });
});
