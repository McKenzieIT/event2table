#!/usr/bin/env node

/**
 * 渐进式实时测试脚本 - 测试单个页面并保存结果
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const CONFIG = {
  baseURL: 'http://localhost:5173',
  headless: false,
  viewport: { width: 1920, height: 1080 },
  outputDir: './test_results/realtime-test'
};

async function testPage(pageName, pagePath) {
  if (!fs.existsSync(CONFIG.outputDir)) {
    fs.mkdirSync(CONFIG.outputDir, { recursive: true });
  }

  console.log(`\n🧪 正在测试: ${pageName}`);
  console.log(`   URL: ${CONFIG.baseURL}${pagePath}`);
  console.log('   请稍候...\n');

  const browser = await chromium.launch({
    headless: CONFIG.headless,
    args: ['--start-maximized']
  });

  const context = await browser.newContext({
    viewport: CONFIG.viewport
  });

  const page = await context.newPage();
  const consoleErrors = [];
  const networkErrors = [];

  // 监听错误
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push({
        type: 'console',
        message: msg.text(),
        time: new Date().toISOString()
      });
    }
  });

  page.on('pageerror', error => {
    consoleErrors.push({
      type: 'pageerror',
      message: error.message,
      stack: error.stack,
      time: new Date().toISOString()
    });
  });

  page.on('requestfailed', request => {
    networkErrors.push({
      url: request.url(),
      error: request.failure()?.errorText,
      time: new Date().toISOString()
    });
  });

  const result = {
    page: pageName,
    url: `${CONFIG.baseURL}${pagePath}`,
    timestamp: new Date().toISOString(),
    status: 'unknown',
    loadTime: 0,
    metrics: {},
    consoleErrors: [],
    networkErrors: [],
    screenshot: null
  };

  try {
    // 导航到页面
    const startTime = Date.now();
    await page.goto(`${CONFIG.baseURL}${pagePath}`, {
      waitUntil: 'networkidle',
      timeout: 30000
    });
    result.loadTime = Date.now() - startTime;
    result.status = 'success';

    // 等待渲染
    await page.waitForTimeout(2000);

    // 获取性能指标
    const metrics = await page.evaluate(() => {
      const nav = performance.getEntriesByType('navigation')[0];
      const paint = performance.getEntriesByType('paint');
      return {
        loadTime: nav ? nav.loadEventEnd - nav.startTime : 0,
        domContentLoaded: nav ? nav.domContentLoadedEventEnd - nav.startTime : 0,
        fcp: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0,
        lcp: paint.find(p => p.name === 'largest-contentful-paint')?.startTime || 0,
        resources: performance.getEntriesByType('resource').length,
        domNodes: document.querySelectorAll('*').length
      };
    });
    result.metrics = metrics;

    // 截图
    const screenshotPath = path.join(CONFIG.outputDir, `${pageName.toLowerCase()}-${Date.now()}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });
    result.screenshot = screenshotPath;

    // 收集错误
    result.consoleErrors = consoleErrors;
    result.networkErrors = networkErrors;

    // 保存结果
    const resultPath = path.join(CONFIG.outputDir, `result-${pageName.toLowerCase()}.json`);
    fs.writeFileSync(resultPath, JSON.stringify(result, null, 2));

    // 打印结果
    console.log('\n' + '='.repeat(60));
    console.log(`✅ ${pageName} 测试完成`);
    console.log('='.repeat(60));
    console.log(`   加载时间: ${result.loadTime}ms`);
    console.log(`   DOM就绪: ${metrics.domContentLoaded}ms`);
    console.log(`   FCP: ${metrics.fcp}ms`);
    console.log(`   资源数: ${metrics.resources}`);
    console.log(`   截图: ${screenshotPath}`);
    
    if (consoleErrors.length > 0) {
      console.log(`\n   ⚠️  控制台错误 (${consoleErrors.length}个):`);
      consoleErrors.forEach((err, idx) => {
        console.log(`      ${idx + 1}. [${err.type}] ${err.message?.substring(0, 80)}...`);
      });
    } else {
      console.log(`   ✅ 无控制台错误`);
    }
    
    if (networkErrors.length > 0) {
      console.log(`\n   ⚠️  网络错误 (${networkErrors.length}个):`);
      networkErrors.forEach((err, idx) => {
        console.log(`      ${idx + 1}. ${err.url?.substring(0, 60)}...`);
      });
    }
    
    console.log('='.repeat(60) + '\n');

    await browser.close();
    return result;

  } catch (error) {
    result.status = 'error';
    result.error = error.message;
    
    console.log('\n' + '='.repeat(60));
    console.log(`❌ ${pageName} 测试失败`);
    console.log('='.repeat(60));
    console.log(`   错误: ${error.message}`);
    console.log('='.repeat(60) + '\n');

    // 尝试截图错误状态
    try {
      const errorScreenshot = path.join(CONFIG.outputDir, `${pageName.toLowerCase()}-error.png`);
      await page.screenshot({ path: errorScreenshot, fullPage: true });
      result.screenshot = errorScreenshot;
      console.log(`   📸 错误截图已保存: ${errorScreenshot}\n`);
    } catch (e) {
      console.log(`   ⚠️  无法截图错误状态\n`);
    }

    await browser.close();
    return result;
  }
}

// 主函数
async function main() {
  const pageName = process.argv[2] || 'Dashboard';
  const pagePath = process.argv[3] || '/';
  
  await testPage(pageName, pagePath);
}

main();
