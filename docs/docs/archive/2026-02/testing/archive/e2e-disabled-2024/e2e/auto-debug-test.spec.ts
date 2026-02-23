import { test, expect } from '@playwright/test';

/**
 * 自动化调试测试 - 完整流程测试并截图
 */
test.describe('事件节点构建器 - 自动化调试', () => {
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

  test('完整流程测试并截图', async ({ page }) => {
    console.log('=== 开始自动化测试 ===');

    // 访问React应用
    const url = 'http://127.0.0.1:5001/#/event-node-builder?game_gid=10000147&v=888';
    console.log('访问URL:', url);

    await page.goto(url, { waitUntil: 'networkidle' });
    await page.waitForTimeout(5000);

    console.log('页面已加载，等待5秒...');

    // 收集控制台日志
    const logs: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'log' || msg.type() === 'error' || msg.type() === 'warn') {
        const text = msg.text();
        logs.push(`[${msg.type().padEnd(8)}] ${text}`);
        console.log(`[Console ${msg.type().padEnd(8)}] ${text}`);
      }
    });

    // 截图1: 初始状态
    console.log('\n=== 截图1: 初始状态 ===');
    await page.screenshot({
      path: 'test-results/01-initial-state.png',
      fullPage: true
    });

    // 检查页面是否加载
    const bodyText = await page.evaluate(() => document.body.innerText);
    if (bodyText.includes('Internal Server Error') || bodyText.includes('500')) {
      console.error('❌ 页面显示500错误');
      console.log('这是Flask后端错误，应该访问React前端路由！');
      return;
    }

    // 检查React根元素
    const reactRoot = page.locator('#app-root');
    const hasReactRoot = await reactRoot.count();
    console.log('React根元素存在:', hasReactRoot > 0 ? '是' : '否');

    if (hasReactRoot === 0) {
      console.error('❌ React根元素不存在，应用未加载');
      return;
    }

    console.log('✅ React应用已加载');

    // 尝试找到并点击基础字段
    console.log('\n=== 测试双击基础字段 ===');

    // 方法1: 通过data属性查找
    let baseField = page.locator('[data-field="ds"]').first();

    if (await baseField.count() === 0) {
      console.log('方法1失败：[data-field="ds"]不存在');
      // 方法2: 通过文本查找
      baseField = page.getByText('分区', { exact: true }).first();
    }

    const fieldVisible = await baseField.isVisible().catch(() => false);
    console.log('基础字段可见:', fieldVisible);

    if (!fieldVisible) {
      console.error('❌ 基础字段不可见，可能是页面结构问题');
    } else {
      console.log('✅ 基础字段可见');

      // 截图2: 找到字段后的状态
      await baseField.scrollIntoViewIfNeeded();
      await page.waitForTimeout(500);
      await page.screenshot({
        path: 'test-results/02-found-field.png',
        fullPage: false
      });

      // 双击字段
      console.log('执行双击操作...');
      await baseField.dblclick();
      await page.waitForTimeout(2000);

      // 截图3: 双击后的状态
      await page.screenshot({
        path: 'test-results/03-after-doubleclick.png',
        fullPage: true
      });

      // 检查字段是否添加到画布
      const fieldItems = page.locator('.field-item');
      const fieldCount = await fieldItems.count();
      console.log('字段卡片数量:', fieldCount);

      if (fieldCount > 0) {
        console.log('✅ 成功！字段已添加到画布');

        // 获取第一个字段的内容
        const firstField = fieldItems.first();
        const fieldText = await firstField.textContent();
        console.log('第一个字段内容:', fieldText);

        // 截图4: 字段特写
        await firstField.screenshot({
          path: 'test-results/04-field-card-closeup.png'
        });

      } else {
        console.error('❌ 字段未添加到画布');

        // 检查画布区域
        const canvas = page.locator('.field-canvas');
        const canvasCount = await canvas.count();
        console.log('画布元素数量:', canvasCount);

        if (canvasCount > 0) {
          const canvasHTML = await canvas.first().innerHTML();
          console.log('画布HTML (前500字符):', canvasHTML.substring(0, 500));
        }
      }
    }

    // 最终截图
    console.log('\n=== 最终状态截图 ===');
    await page.screenshot({
      path: 'test-results/05-final-state.png',
      fullPage: true
    });

    // 检查控制台日志
    console.log('\n=== 控制台日志汇总 ===');
    const relevantLogs = logs.filter(log =>
      log.includes('[EventNodeBuilder]') ||
      log.includes('[BaseFieldsList]') ||
      log.includes('[useEventNodeBuilder]')
    );
    relevantLogs.forEach(log => console.log(log));

    // 打印页面HTML结构信息
    console.log('\n=== 页面结构信息 ===');
    const structure = await page.evaluate(() => {
      return {
        reactRoot: !!document.querySelector('#app-root'),
        hasSidebarLeft: !!document.querySelector('.sidebar-left'),
        hasFieldCanvas: !!document.querySelector('.field-canvas'),
        hasFieldItems: document.querySelectorAll('.field-item').length,
        hasEmptyState: !!document.querySelector('.empty-state'),
        hasBaseFieldDataAttr: document.querySelectorAll('[data-field]').length,
        hasBaseFieldClass: document.querySelectorAll('.base-field-item').length,
      };
    });
    console.log(JSON.stringify(structure, null, 2));

    // 诊断报告
    console.log('\n=== 诊断报告 ===');
    console.log('React应用:', structure.reactRoot ? '✅ 已加载' : '❌ 未加载');
    console.log('左侧边栏:', structure.hasSidebarLeft ? '✅ 存在' : '❌ 不存在');
    console.log('字段画布:', structure.hasFieldCanvas ? '✅ 存在' : '❌ 不存在');
    console.log('字段卡片:', structure.hasFieldItems > 0 ? `✅ ${structure.hasFieldItems}个` : '❌ 0个');
    console.log('空状态:', structure.hasEmptyState ? '⚠️ 显示' : '✅ 不显示');
    console.log('基础字段[data-field]:', structure.hasBaseFieldDataAttr);
    console.log('基础字段.base-field-item:', structure.hasBaseFieldClass);
  });
});
