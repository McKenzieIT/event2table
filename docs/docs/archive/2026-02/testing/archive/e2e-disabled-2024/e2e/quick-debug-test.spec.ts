import { test, expect } from '@playwright/test';
import { navigateToPage, PAGE_PATHS } from '../helpers/url-helper';

/**
 * 快速调试测试 - 诊断双击和拖拽问题
 */
test.describe('事件节点构建器 - 快速诊断', () => {
  test.afterEach(async ({ page }) => {
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
    });
    await page.waitForTimeout(300);
  });

  test('完整功能测试', async ({ page }) => {
    // 访问页面
    await navigateToPage(page, PAGE_PATHS.EVENT_NODE_BUILDER, { gameGid: '10000147' });

    // 等待页面加载
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);

    console.log('=== 页面已加载 ===');

    // 收集控制台日志
    const logs: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'log') {
        logs.push(msg.text());
        console.log('[Browser Console]', msg.text());
      }
    });

    // 测试1: 页面元素检查
    console.log('\n=== 测试1: 检查页面元素 ===');
    const baseField = page.locator('[data-field="ds"]').first();
    await expect(baseField).toBeVisible();
    console.log('✅ 基础字段元素存在');

    const canvas = page.locator('.field-canvas');
    await expect(canvas).toBeVisible();
    console.log('✅ 字段画布区域存在');

    // 测试2: 双击基础字段
    console.log('\n=== 测试2: 双击基础字段 ===');
    const fieldCountBefore = await page.locator('.field-item').count();
    console.log('双击前字段数量:', fieldCountBefore);

    await baseField.dblclick();
    await page.waitForTimeout(1000);

    const fieldCountAfter = await page.locator('.field-item').count();
    console.log('双击后字段数量:', fieldCountAfter);

    if (fieldCountAfter > fieldCountBefore) {
      console.log('✅ 双击成功！字段已添加到画布');
    } else {
      console.error('❌ 双击失败！字段未添加到画布');
    }

    // 测试3: 检查控制台日志
    console.log('\n=== 测试3: 检查控制台日志 ===');
    const hasBaseFieldLog = logs.some(log => log.includes('[BaseFieldsList]'));
    const hasEventBuilderLog = logs.some(log => log.includes('[EventNodeBuilder]'));
    const hasHookLog = logs.some(log => log.includes('[useEventNodeBuilder]'));

    console.log('有[BaseFieldsList]日志:', hasBaseFieldLog);
    console.log('有[EventNodeBuilder]日志:', hasEventBuilderLog);
    console.log('有[useEventNodeBuilder]日志:', hasHookLog);

    // 测试4: 检查字段卡片内容
    console.log('\n=== 测试4: 检查字段卡片 ===');
    if (fieldCountAfter > 0) {
      const firstField = page.locator('.field-item').first();
      const fieldText = await firstField.textContent();
      console.log('第一个字段卡片内容:', fieldText);
      console.log('✅ 字段卡片显示正常');
    } else {
      console.error('❌ 字段卡片未显示');
    }

    // 测试5: 检查JS文件版本
    console.log('\n=== 测试5: 检查JS文件版本 ===');
    const jsVersion = await page.evaluate(() => {
      const scripts = Array.from(document.querySelectorAll('script[src*="/frontend/dist"]'));
      const jsFile = scripts.find(s => s.src.includes('index-'));
      return jsFile ? jsFile.src.split('/').pop() : null;
    });
    console.log('加载的JS文件:', jsVersion);

    if (jsVersion === 'index-CGt4kuY9.js') {
      console.log('✅ JS文件版本正确');
    } else {
      console.error('❌ JS文件版本错误或旧版本被缓存');
    }

    // 测试6: 检查CSS变量
    console.log('\n=== 测试6: 检查CSS变量 ===');
    const cssVars = await page.evaluate(() => {
      const root = document.documentElement;
      return {
        spaceMd: getComputedStyle(root).getPropertyValue('--en-space-md'),
        fieldBase: getComputedStyle(root).getPropertyValue('--en-field-base'),
        bgCard: getComputedStyle(root).getPropertyValue('--en-bg-card'),
      };
    });
    console.log('CSS变量:', cssVars);

    if (cssVars.spaceMd && cssVars.spaceMd !== '') {
      console.log('✅ CSS变量已加载');
    } else {
      console.error('❌ CSS变量未加载');
    }

    // 测试7: 截图保存
    console.log('\n=== 测试7: 保存截图 ===');
    await page.screenshot({
      path: 'test-results/event-builder-screenshot.png',
      fullPage: true
    });
    console.log('✅ 截图已保存到 test-results/event-builder-screenshot.png');

    // 最终总结
    console.log('\n=== 测试总结 ===');
    console.log('页面加载:', '✅');
    console.log('双击功能:', fieldCountAfter > fieldCountBefore ? '✅' : '❌');
    console.log('控制台日志:', hasEventBuilderLog ? '✅' : '❌');
    console.log('JS版本:', jsVersion === 'index-CGt4kuY9.js' ? '✅' : '❌');
    console.log('CSS变量:', cssVars.spaceMd ? '✅' : '❌');

    // 期望结果
    expect(fieldCountAfter).toBeGreaterThan(fieldCountBefore);
  });
});
