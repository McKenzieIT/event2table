import { test, expect } from '@playwright/test';
import { filterNonCriticalErrors } from './helpers/wait-helpers';

/**
 * Console Errors Collection Test
 *
 * 测试所有页面并收集console错误信息
 */

const pages = [
  { name: 'Dashboard', url: 'http://localhost:5173/#/' },
  { name: 'Games管理', url: 'http://localhost:5173/#/games' },
  { name: 'Events管理', url: 'http://localhost:5173/#/events' },
  { name: 'EventNodeBuilder', url: 'http://localhost:5173/#/event-node-builder?game_gid=10000147' },
  { name: 'Canvas', url: 'http://localhost:5173/#/canvas?game_gid=10000147' },
  { name: 'Parameters', url: 'http://localhost:5173/#/parameters' },
  { name: 'Event Nodes', url: 'http://localhost:5173/#/event-nodes' },
  { name: 'Categories', url: 'http://localhost:5173/#/categories' },
  { name: 'Flows', url: 'http://localhost:5173/#/flows' },
  { name: 'Generate', url: 'http://localhost:5173/#/generate' },
  { name: 'HQL Results', url: 'http://localhost:5173/#/hql-results' },
  { name: 'HQL Manage', url: 'http://localhost:5173/#/hql-manage' },
  { name: 'Logs', url: 'http://localhost:5173/#/logs' },
  { name: 'Batch Operations', url: 'http://localhost:5173/#/batch-operations' },
  { name: 'Import Events', url: 'http://localhost:5173/#/import-events' },
  { name: 'Alter SQL', url: 'http://localhost:5173/#/alter-sql' },
  { name: 'API Docs', url: 'http://localhost:5173/#/api-docs' },
];

test.describe('Console Errors Collection', () => {
  pages.forEach(({ name, url }) => {
    test(`${name} - should load without console errors`, async ({ page }) => {
      const consoleErrors: string[] = [];
      const consoleWarnings: string[] = [];

      // 收集所有console错误和警告
      page.on('console', msg => {
        if (msg.type() === 'error') {
          consoleErrors.push(msg.text());
        }
        if (msg.type() === 'warning') {
          consoleWarnings.push(msg.text());
        }
      });

      // 导航到页面
      await page.goto(url, {
        timeout: 60000,
        waitUntil: 'commit'
      });

      // 等待页面稳定 - reduced from 2000 to 500
      await page.waitForTimeout(500);

      // 报告错误
      if (consoleErrors.length > 0) {
        console.log(`❌ ${name} - Console Errors (${consoleErrors.length}):`);
        consoleErrors.forEach(err => console.log(`  - ${err}`));
      } else {
        console.log(`✅ ${name} - No console errors`);
      }

      // 报告警告
      if (consoleWarnings.length > 0) {
        console.log(`⚠️  ${name} - Console Warnings (${consoleWarnings.length}):`);
        consoleWarnings.forEach(warning => console.log(`  - ${warning}`));
      }

      // 检查是否有critical错误 (过滤掉非关键错误)
      const criticalErrors = filterNonCriticalErrors(consoleErrors);
      expect(criticalErrors.length).toBe(0);
    });
  });
});
