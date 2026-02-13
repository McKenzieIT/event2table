#!/usr/bin/env node

/**
 * Event2Table 完全自动化交互测试
 * 测试所有关键功能的点击、表单、数据流
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const CONFIG = {
  baseURL: 'http://localhost:8888',
  headless: false,
  viewport: { width: 1920, height: 1080 },
  outputDir: './test_results/interactive-test',
  testFile: '/Users/mckenzie/Documents/event2table/uploads/【Star】biz事件列表.xlsx'
};

const testResults = {
  timestamp: new Date().toISOString(),
  tests: [],
  passed: 0,
  failed: 0,
  total: 0
};

function logTest(testName, status, details = '') {
  testResults.total++;
  if (status === 'PASS') {
    testResults.passed++;
    console.log(`  ✅ ${testName}`);
  } else {
    testResults.failed++;
    console.log(`  ❌ ${testName}: ${details}`);
  }
  testResults.tests.push({ name: testName, status, details });
}

async function testDashboard(browser) {
  console.log('\n🧪 测试 Dashboard 交互...');
  const context = await browser.newContext({ viewport: CONFIG.viewport });
  const page = await context.newPage();
  
  try {
    // 1. 测试加载
    await page.goto(`${CONFIG.baseURL}/`, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(2000);
    
    // 2. 测试快捷操作卡片 - 管理游戏
    try {
      const gamesCard = await page.locator('.action-card:has-text("管理游戏"), .dashboard-card:has-text("管理游戏")').first();
      if (await gamesCard.isVisible()) {
        await gamesCard.click();
        await page.waitForTimeout(2000);
        if (page.url().includes('/games')) {
          logTest('Dashboard-点击管理游戏卡片', 'PASS');
        } else {
          logTest('Dashboard-点击管理游戏卡片', 'FAIL', '未正确跳转');
        }
      } else {
        logTest('Dashboard-点击管理游戏卡片', 'FAIL', '找不到卡片');
      }
    } catch (e) {
      logTest('Dashboard-点击管理游戏卡片', 'FAIL', e.message);
    }
    
    // 3. 返回 Dashboard
    await page.goto(`${CONFIG.baseURL}/`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);
    
    // 4. 测试管理事件卡片
    try {
      const eventsCard = await page.locator('.action-card:has-text("管理事件"), .dashboard-card:has-text("管理事件")').first();
      if (await eventsCard.isVisible()) {
        await eventsCard.click();
        await page.waitForTimeout(2000);
        if (page.url().includes('/events')) {
          logTest('Dashboard-点击管理事件卡片', 'PASS');
        } else {
          logTest('Dashboard-点击管理事件卡片', 'FAIL', '未正确跳转');
        }
      } else {
        logTest('Dashboard-点击管理事件卡片', 'FAIL', '找不到卡片');
      }
    } catch (e) {
      logTest('Dashboard-点击管理事件卡片', 'FAIL', e.message);
    }
    
    await context.close();
  } catch (error) {
    logTest('Dashboard-整体测试', 'FAIL', error.message);
    await context.close();
  }
}

async function testImportEvents(browser) {
  console.log('\n🧪 测试导入事件功能...');
  const context = await browser.newContext({ viewport: CONFIG.viewport });
  const page = await context.newPage();
  
  try {
    // 1. 导航到导入页面
    await page.goto(`${CONFIG.baseURL}/#/import-events`, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(2000);
    
    // 2. 检查页面是否正确加载
    const pageTitle = await page.title();
    if (pageTitle.includes('导入') || await page.locator('h1:has-text("导入")').isVisible()) {
      logTest('ImportEvents-页面加载', 'PASS');
    } else {
      logTest('ImportEvents-页面加载', 'FAIL', '页面标题不正确');
    }
    
    // 3. 上传文件
    try {
      const fileInput = await page.locator('input[type="file"]').first();
      if (await fileInput.isVisible()) {
        await fileInput.setInputFiles(CONFIG.testFile);
        await page.waitForTimeout(1000);
        logTest('ImportEvents-文件上传', 'PASS');
        
        // 4. 点击预览按钮
        const previewBtn = await page.locator('button:has-text("预览"), button:has-text("preview"), .preview-btn').first();
        if (await previewBtn.isVisible()) {
          await previewBtn.click();
          await page.waitForTimeout(3000);
          
          // 5. 检查是否有预览结果或错误
          const errorMsg = await page.locator('.error-message, .toast-error, [role="alert"]').isVisible().catch(() => false);
          const previewTable = await page.locator('.preview-table, table, .import-preview').isVisible().catch(() => false);
          
          if (previewTable) {
            logTest('ImportEvents-预览功能', 'PASS');
          } else if (errorMsg) {
            const errorText = await page.locator('.error-message, .toast-error').textContent().catch(() => 'Unknown error');
            logTest('ImportEvents-预览功能', 'FAIL', `错误: ${errorText.substring(0, 100)}`);
          } else {
            logTest('ImportEvents-预览功能', 'FAIL', '无响应');
          }
        } else {
          logTest('ImportEvents-预览按钮', 'FAIL', '找不到按钮');
        }
      } else {
        logTest('ImportEvents-文件上传', 'FAIL', '找不到文件输入框');
      }
    } catch (e) {
      logTest('ImportEvents-文件上传', 'FAIL', e.message);
    }
    
    await context.close();
  } catch (error) {
    logTest('ImportEvents-整体测试', 'FAIL', error.message);
    await context.close();
  }
}

async function testGamesPage(browser) {
  console.log('\n🧪 测试 Games 页面...');
  const context = await browser.newContext({ viewport: CONFIG.viewport });
  const page = await context.newPage();
  
  try {
    // 1. 打开 Games 页面
    await page.goto(`${CONFIG.baseURL}/#/games`, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(2000);
    
    // 2. 检查游戏列表是否加载
    const gameRows = await page.locator('.game-item, .game-row, tr').count();
    if (gameRows > 0) {
      logTest('Games-列表加载', 'PASS', `${gameRows} 个游戏`);
    } else {
      logTest('Games-列表加载', 'FAIL', '没有游戏数据');
    }
    
    // 3. 测试点击第一个游戏
    try {
      const firstGame = await page.locator('.game-item, .game-row, tr').first();
      if (await firstGame.isVisible()) {
        await firstGame.click();
        await page.waitForTimeout(2000);
        
        // 检查是否跳转到事件页面或详情页
        if (page.url().includes('/events') || page.url().includes('/games/')) {
          logTest('Games-点击游戏行', 'PASS');
        } else {
          logTest('Games-点击游戏行', 'FAIL', '未跳转');
        }
      }
    } catch (e) {
      logTest('Games-点击游戏行', 'FAIL', e.message);
    }
    
    await context.close();
  } catch (error) {
    logTest('Games-整体测试', 'FAIL', error.message);
    await context.close();
  }
}

async function testEventsPage(browser) {
  console.log('\n🧪 测试 Events 页面...');
  const context = await browser.newContext({ viewport: CONFIG.viewport });
  const page = await context.newPage();
  
  try {
    // 1. 打开 Events 页面
    await page.goto(`${CONFIG.baseURL}/#/events`, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(2000);
    
    // 2. 检查事件列表
    const eventRows = await page.locator('.event-item, .event-row, tr').count();
    if (eventRows > 0) {
      logTest('Events-列表加载', 'PASS', `${eventRows} 个事件`);
    } else {
      logTest('Events-列表加载', 'FAIL', '没有事件数据');
    }
    
    await context.close();
  } catch (error) {
    logTest('Events-整体测试', 'FAIL', error.message);
    await context.close();
  }
}

async function testCanvasPage(browser) {
  console.log('\n🧪 测试 Canvas 页面...');
  const context = await browser.newContext({ viewport: CONFIG.viewport });
  const page = await context.newPage();
  
  try {
    // 1. 打开 Canvas 页面
    await page.goto(`${CONFIG.baseURL}/#/canvas`, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(3000);
    
    // 2. 检查画布是否加载
    const canvas = await page.locator('.react-flow, .canvas-container, canvas').first().isVisible().catch(() => false);
    if (canvas) {
      logTest('Canvas-画布加载', 'PASS');
    } else {
      logTest('Canvas-画布加载', 'FAIL', '画布未加载');
    }
    
    await context.close();
  } catch (error) {
    logTest('Canvas-整体测试', 'FAIL', error.message);
    await context.close();
  }
}

async function main() {
  console.log('\n' + '='.repeat(70));
  console.log('🚀 Event2Table 完全自动化交互测试');
  console.log('='.repeat(70));
  console.log(`\n📍 测试地址: ${CONFIG.baseURL}`);
  console.log(`📁 测试文件: ${CONFIG.testFile}\n`);

  // 确保输出目录存在
  if (!fs.existsSync(CONFIG.outputDir)) {
    fs.mkdirSync(CONFIG.outputDir, { recursive: true });
  }

  const browser = await chromium.launch({
    headless: CONFIG.headless,
    args: ['--start-maximized']
  });

  // 执行所有测试
  await testDashboard(browser);
  await testGamesPage(browser);
  await testEventsPage(browser);
  await testImportEvents(browser);
  await testCanvasPage(browser);

  await browser.close();

  // 保存结果
  const resultPath = path.join(CONFIG.outputDir, 'interactive-test-results.json');
  fs.writeFileSync(resultPath, JSON.stringify(testResults, null, 2));

  // 打印总结
  console.log('\n' + '='.repeat(70));
  console.log('📊 交互测试结果总结');
  console.log('='.repeat(70));
  console.log(`\n   总测试数: ${testResults.total}`);
  console.log(`   ✅ 通过: ${testResults.passed}`);
  console.log(`   ❌ 失败: ${testResults.failed}`);
  console.log(`   通过率: ${((testResults.passed/testResults.total)*100).toFixed(1)}%`);
  
  console.log('\n   详细结果:');
  testResults.tests.forEach(test => {
    const icon = test.status === 'PASS' ? '✅' : '❌';
    console.log(`   ${icon} ${test.name}`);
    if (test.details && test.status === 'FAIL') {
      console.log(`      → ${test.details}`);
    }
  });

  console.log(`\n💾 结果保存: ${resultPath}`);
  console.log('='.repeat(70) + '\n');

  return testResults;
}

main().then(results => {
  if (results.failed === 0) {
    console.log('🎉 所有交互测试通过！\n');
    process.exit(0);
  } else {
    console.log(`⚠️  ${results.failed} 个测试失败，请检查\n`);
    process.exit(1);
  }
}).catch(err => {
  console.error('❌ 测试执行失败:', err);
  process.exit(1);
});
