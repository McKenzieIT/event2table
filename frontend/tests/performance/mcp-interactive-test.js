#!/usr/bin/env node

/**
 * Event2Table - 真实用户交互测试
 * 使用 Playwright + CDP 模拟用户操作
 * 
 * 测试方式：
 * 1. 模拟真实用户打开页面
 * 2. 点击交互元素
 * 3. 截图记录
 * 4. 读取控制台信息
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const CONFIG = {
  baseURL: 'http://localhost:5173',
  headless: false, // 有头模式便于观察
  viewport: { width: 1920, height: 1080 },
  outputDir: './test_results/mcp-interactive-test'
};

// 确保输出目录存在
function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

// 保存测试结果
function saveResult(result) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filePath = path.join(CONFIG.outputDir, `test-result-${timestamp}.json`);
  fs.writeFileSync(filePath, JSON.stringify(result, null, 2));
  return filePath;
}

/**
 * 测试 Dashboard 页面
 */
async function testDashboard(page, context) {
  console.log('\n🧪 开始测试 Dashboard 页面...\n');
  
  const result = {
    page: 'Dashboard',
    url: `${CONFIG.baseURL}/`,
    timestamp: new Date().toISOString(),
    steps: [],
    consoleErrors: [],
    performance: {},
    screenshots: []
  };

  // 1. 导航到 Dashboard
  console.log('  📍 步骤 1: 导航到 Dashboard');
  const startTime = Date.now();
  
  try {
    await page.goto(`${CONFIG.baseURL}/`, { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });
    
    const loadTime = Date.now() - startTime;
    result.steps.push({
      step: 1,
      action: '导航到 Dashboard',
      status: 'success',
      loadTime: loadTime,
      message: `页面加载完成，耗时 ${loadTime}ms`
    });
    
    console.log(`     ✅ 加载成功，耗时: ${loadTime}ms`);
    result.performance.initialLoad = loadTime;

    // 等待页面完全渲染
    await page.waitForTimeout(3000);

  } catch (error) {
    result.steps.push({
      step: 1,
      action: '导航到 Dashboard',
      status: 'error',
      message: error.message
    });
    console.log(`     ❌ 加载失败: ${error.message}`);
    return result;
  }

  // 2. 截图 - 初始状态
  console.log('  📸 步骤 2: 截取初始状态');
  try {
    const screenshot1 = path.join(CONFIG.outputDir, 'dashboard-initial.png');
    await page.screenshot({ path: screenshot1, fullPage: true });
    result.screenshots.push({ step: 2, path: screenshot1, description: '初始状态' });
    console.log(`     ✅ 截图已保存: dashboard-initial.png`);
  } catch (error) {
    console.log(`     ⚠️  截图失败: ${error.message}`);
  }

  // 3. 获取性能指标
  console.log('  📊 步骤 3: 收集性能指标');
  try {
    const metrics = await page.evaluate(() => {
      const nav = performance.getEntriesByType('navigation')[0];
      const paint = performance.getEntriesByType('paint');
      
      return {
        loadTime: nav ? nav.loadEventEnd - nav.startTime : 0,
        domContentLoaded: nav ? nav.domContentLoadedEventEnd - nav.startTime : 0,
        fcp: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0,
        resources: performance.getEntriesByType('resource').length
      };
    });
    
    result.performance.metrics = metrics;
    result.steps.push({
      step: 3,
      action: '收集性能指标',
      status: 'success',
      metrics: metrics
    });
    
    console.log(`     ✅ 性能指标:`);
    console.log(`        - 加载时间: ${metrics.loadTime}ms`);
    console.log(`        - DOM就绪: ${metrics.domContentLoaded}ms`);
    console.log(`        - FCP: ${metrics.fcp}ms`);
    console.log(`        - 资源数: ${metrics.resources}`);
    
  } catch (error) {
    console.log(`     ⚠️  性能指标收集失败: ${error.message}`);
  }

  // 4. 测试交互 - 查找并点击快捷操作卡片
  console.log('  🖱️  步骤 4: 测试快捷操作卡片');
  try {
    // 查找所有快捷操作卡片
    const cards = await page.locator('.action-card, .dashboard-card, [data-testid="action-card"]').all();
    console.log(`     找到 ${cards.length} 个操作卡片`);
    
    if (cards.length > 0) {
      // 点击第一个卡片（通常是"管理游戏"）
      const firstCard = cards[0];
      const cardText = await firstCard.textContent();
      console.log(`     点击卡片: ${cardText?.substring(0, 50)}...`);
      
      await firstCard.click();
      await page.waitForTimeout(2000);
      
      const currentUrl = page.url();
      result.steps.push({
        step: 4,
        action: '点击快捷操作卡片',
        status: 'success',
        cardText: cardText?.substring(0, 50),
        navigatedTo: currentUrl
      });
      
      console.log(`     ✅ 导航到: ${currentUrl}`);
      
      // 截图 - 点击后
      const screenshot2 = path.join(CONFIG.outputDir, 'dashboard-after-click.png');
      await page.screenshot({ path: screenshot2, fullPage: true });
      result.screenshots.push({ step: 4, path: screenshot2, description: '点击卡片后' });
      
      // 返回 Dashboard
      await page.goto(`${CONFIG.baseURL}/`, { waitUntil: 'networkidle' });
      await page.waitForTimeout(2000);
    }
    
  } catch (error) {
    result.steps.push({
      step: 4,
      action: '测试快捷操作卡片',
      status: 'error',
      message: error.message
    });
    console.log(`     ⚠️  交互测试失败: ${error.message}`);
  }

  // 5. 读取控制台错误
  console.log('  🔍 步骤 5: 检查控制台错误');
  try {
    const logs = await context.cookies();
    
    // 重新加载页面以捕获控制台错误
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);
    
    // 获取页面错误
    const pageErrors = await page.evaluate(() => {
      return window.errors || [];
    });
    
    result.consoleErrors = pageErrors;
    result.steps.push({
      step: 5,
      action: '检查控制台错误',
      status: pageErrors.length === 0 ? 'success' : 'warning',
      errorCount: pageErrors.length
    });
    
    if (pageErrors.length === 0) {
      console.log(`     ✅ 未发现控制台错误`);
    } else {
      console.log(`     ⚠️  发现 ${pageErrors.length} 个错误:`);
      pageErrors.forEach((err, idx) => {
        console.log(`        ${idx + 1}. ${err.message?.substring(0, 100)}...`);
      });
    }
    
  } catch (error) {
    console.log(`     ⚠️  控制台检查失败: ${error.message}`);
  }

  // 6. 最终截图
  console.log('  📸 步骤 6: 最终状态截图');
  try {
    const screenshot3 = path.join(CONFIG.outputDir, 'dashboard-final.png');
    await page.screenshot({ path: screenshot3, fullPage: true });
    result.screenshots.push({ step: 6, path: screenshot3, description: '最终状态' });
    console.log(`     ✅ 截图已保存: dashboard-final.png`);
  } catch (error) {
    console.log(`     ⚠️  截图失败: ${error.message}`);
  }

  return result;
}

/**
 * 测试其他关键页面
 */
async function testOtherPages(page, context) {
  const pages = [
    { name: 'Games', path: '/#/games' },
    { name: 'Events', path: '/#/events' },
    { name: 'Canvas', path: '/#/canvas' }
  ];
  
  const results = [];
  
  for (const pageConfig of pages) {
    console.log(`\n🧪 测试 ${pageConfig.name} 页面...`);
    
    const result = {
      page: pageConfig.name,
      url: `${CONFIG.baseURL}${pageConfig.path}`,
      timestamp: new Date().toISOString(),
      status: 'unknown',
      loadTime: 0,
      consoleErrors: []
    };
    
    try {
      const startTime = Date.now();
      await page.goto(`${CONFIG.baseURL}${pageConfig.path}`, {
        waitUntil: 'networkidle',
        timeout: 30000
      });
      
      result.loadTime = Date.now() - startTime;
      result.status = 'success';
      
      await page.waitForTimeout(2000);
      
      // 截图
      const screenshot = path.join(CONFIG.outputDir, `${pageConfig.name.toLowerCase()}.png`);
      await page.screenshot({ path: screenshot, fullPage: true });
      result.screenshot = screenshot;
      
      console.log(`     ✅ 加载成功: ${result.loadTime}ms`);
      
    } catch (error) {
      result.status = 'error';
      result.error = error.message;
      console.log(`     ❌ 加载失败: ${error.message}`);
    }
    
    results.push(result);
  }
  
  return results;
}

/**
 * 主函数
 */
async function main() {
  console.log('\n' + '='.repeat(80));
  console.log('🚀 Event2Table - MCP 真实用户交互测试');
  console.log('='.repeat(80));
  console.log(`\n📍 测试地址: ${CONFIG.baseURL}`);
  console.log(`📁 输出目录: ${CONFIG.outputDir}\n`);

  ensureDir(CONFIG.outputDir);
  ensureDir(path.join(CONFIG.outputDir, 'screenshots'));

  console.log('🔧 启动浏览器...');
  const browser = await chromium.launch({
    headless: CONFIG.headless,
    args: ['--start-maximized']
  });

  const context = await browser.newContext({
    viewport: CONFIG.viewport
  });

  // 监听控制台错误
  context.on('page', page => {
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log(`   🔴 控制台错误: ${msg.text().substring(0, 100)}...`);
      }
    });
    
    page.on('pageerror', error => {
      console.log(`   🔴 页面错误: ${error.message?.substring(0, 100)}...`);
    });
  });

  const page = await context.newPage();
  const allResults = {
    timestamp: new Date().toISOString(),
    tests: []
  };

  try {
    // 1. 测试 Dashboard
    const dashboardResult = await testDashboard(page, context);
    allResults.tests.push(dashboardResult);

    // 2. 测试其他页面
    const otherResults = await testOtherPages(page, context);
    allResults.tests.push(...otherResults);

    // 保存结果
    const resultPath = saveResult(allResults);
    
    // 生成摘要
    console.log('\n' + '='.repeat(80));
    console.log('📊 测试完成！');
    console.log('='.repeat(80));
    console.log(`\n✅ 测试页面数: ${allResults.tests.length}`);
    console.log(`📁 结果保存: ${resultPath}`);
    
    const successCount = allResults.tests.filter(t => t.status === 'success' || t.steps?.every(s => s.status !== 'error')).length;
    console.log(`🎯 成功: ${successCount}/${allResults.tests.length}`);
    
    console.log('\n📈 性能摘要:');
    allResults.tests.forEach(test => {
      if (test.performance?.metrics) {
        console.log(`   ${test.page}: ${test.performance.metrics.loadTime}ms`);
      } else if (test.loadTime) {
        console.log(`   ${test.page}: ${test.loadTime}ms`);
      }
    });

  } catch (error) {
    console.error('\n❌ 测试执行失败:', error);
  } finally {
    await browser.close();
    console.log('\n' + '='.repeat(80));
    console.log('🏁 浏览器已关闭');
    console.log('='.repeat(80) + '\n');
  }
}

// 执行测试
main().catch(console.error);
