import { test, expect } from '@playwright/test';
import { navigateToPage, PAGE_PATHS } from '../helpers/url-helper';

/**
 * 灵活诊断测试 - 不依赖特定元素，直接查看页面状态
 */
test.describe('事件节点构建器 - 灵活诊断', () => {
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

  test('完整页面诊断', async ({ page }) => {
    // 访问页面
    await navigateToPage(page, PAGE_PATHS.EVENT_NODE_BUILDER, { gameGid: '10000147' });

    // 等待页面加载
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(5000);

    console.log('=== 页面诊断开始 ===\n');

    // 收集控制台日志
    const logs: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'log' || msg.type() === 'error') {
        const text = msg.text();
        logs.push(`[${msg.type()}] ${text}`);
        console.log(`[Console ${msg.type()}]`, text);
      }
    });

    // 诊断1: 检查页面结构
    console.log('\n--- 诊断1: 页面结构 ---');
    const bodyText = await page.evaluate(() => document.body.innerText);
    console.log('页面文本长度:', bodyText.length);
    console.log('页面文本预览:', bodyText.substring(0, 200));

    // 诊断2: 检查React根元素
    const reactRoot = page.locator('#app-root');
    const hasReactRoot = await reactRoot.count();
    console.log('React根元素存在:', hasReactRoot > 0);

    // 诊断3: 检查所有侧边栏
    const sidebars = await page.locator('.sidebar, .workspace').all();
    console.log('侧边栏/工作区数量:', sidebars.length);

    // 诊断4: 查找基础字段（使用多种选择器）
    console.log('\n--- 诊断2: 基础字段 ---');
    const baseFieldByData = await page.locator('[data-field]').count();
    const baseFieldByText = await page.locator('text="分区"').count();
    const baseFieldByClass = await page.locator('.base-field-item').count();

    console.log('通过[data-field]找到:', baseFieldByData);
    console.log('通过文本"分区"找到:', baseFieldByText);
    console.log('通过.base-field-item找到:', baseFieldByClass);

    // 诊断5: 检查字段画布
    console.log('\n--- 诊断3: 字段画布 ---');
    const canvas = page.locator('.field-canvas');
    const hasCanvas = await canvas.count();
    console.log('字段画布元素存在:', hasCanvas > 0);

    if (hasCanvas > 0) {
      const canvasText = await canvas.first().textContent();
      console.log('画布文本:', canvasText);

      const fieldItems = await page.locator('.field-item').count();
      console.log('字段卡片数量:', fieldItems);

      const emptyState = await page.locator('.empty-state').count();
      console.log('空状态元素:', emptyState > 0 ? '存在' : '不存在');
    }

    // 诊断6: 检查加载的JS文件
    console.log('\n--- 诊断4: 加载的文件 ---');
    const jsFile = await page.evaluate(() => {
      const scripts = Array.from(document.querySelectorAll('script[src*="/frontend/dist"]'));
      return scripts.map(s => s.src).filter(src => src.includes('index-'));
    });
    console.log('加载的JS文件:', jsFile.map(f => f.split('/').pop()));

    // 诊断7: 检查CSS变量
    console.log('\n--- 诊断5: CSS变量 ---');
    const cssVars = await page.evaluate(() => {
      const root = document.documentElement;
      const styles = window.getComputedStyle(root);
      return {
        spaceMd: styles.getPropertyValue('--en-space-md'),
        fieldBase: styles.getPropertyValue('--en-field-base'),
        hasGlassBg: styles.getPropertyValue('--glass-bg') !== '',
      };
    });
    console.log('CSS变量:', cssVars);

    // 诊断8: 尝试找到并点击基础字段
    console.log('\n--- 诊断6: 尝试操作 ---');

    // 方法1: 通过文本查找
    const dsText = page.getByText('分区', { exact: true });
    try {
      await expect(dsText).toBeVisible({ timeout: 3000 });
      console.log('✅ 找到"分区"文本');
      await dsText.dblclick();
      await page.waitForTimeout(1000);

      const fieldCountAfter = await page.locator('.field-item').count();
      console.log('双击后字段数量:', fieldCountAfter);

      if (fieldCountAfter > 0) {
        console.log('✅ 双击成功！字段已添加');
      } else {
        console.log('⚠️ 双击后字段数量仍为0');
      }
    } catch (e) {
      console.log('❌ 无法通过文本找到"分区"元素');
    }

    // 最终截图
    console.log('\n--- 保存截图 ---');
    await page.screenshot({
      path: 'test-results/diagnostic-screenshot.png',
      fullPage: true
    });
    console.log('✅ 截图已保存');

    // 打印所有控制台日志
    console.log('\n--- 控制台日志汇总 ---');
    logs.forEach(log => console.log(log));

    // 保存诊断报告
    const report = {
      timestamp: new Date().toISOString(),
      pageStructure: {
        bodyTextLength: bodyText.length,
        hasReactRoot: hasReactRoot > 0,
        sidebarCount: sidebars.length
      },
      fields: {
        byDataAttr: baseFieldByData,
        byText: baseFieldByText,
        byClass: baseFieldByClass
      },
      canvas: {
        exists: hasCanvas > 0,
        fieldCount: await page.locator('.field-item').count(),
        hasEmptyState: await page.locator('.empty-state').count() > 0
      },
      files: {
        jsFiles: jsFile.map(f => f.split('/').pop())
      },
      css: cssVars,
      consoleLogs: logs
    };

    console.log('\n=== 诊断报告 ===');
    console.log(JSON.stringify(report, null, 2));
  });
});
