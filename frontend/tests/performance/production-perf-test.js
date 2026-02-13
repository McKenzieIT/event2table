#!/usr/bin/env node

/**
 * 生产环境性能测试
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const CONFIG = {
  baseURL: 'http://localhost:5174', // 生产服务器
  backendURL: 'http://127.0.0.1:5001',
  headless: false,
  viewport: { width: 1920, height: 1080 },
  outputDir: './test_results/production-test'
};

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

async function testPage(page, pageName, pagePath) {
  console.log(`\n🧪 测试: ${pageName}`);
  console.log(`   URL: ${CONFIG.baseURL}${pagePath}`);

  const result = {
    page: pageName,
    url: `${CONFIG.baseURL}${pagePath}`,
    timestamp: new Date().toISOString(),
    status: 'unknown',
    loadTime: 0,
    metrics: {},
    consoleErrors: [],
    resources: {}
  };

  try {
    const startTime = Date.now();
    await page.goto(`${CONFIG.baseURL}${pagePath}`, {
      waitUntil: 'networkidle',
      timeout: 30000
    });
    result.loadTime = Date.now() - startTime;
    result.status = 'success';

    // 等待渲染完成
    await page.waitForTimeout(2000);

    // 获取详细性能指标
    const metrics = await page.evaluate(() => {
      const nav = performance.getEntriesByType('navigation')[0];
      const resources = performance.getEntriesByType('resource');
      
      // 统计资源
      let jsCount = 0, jsSize = 0, jsLoadTime = 0;
      let cssCount = 0, cssSize = 0;
      let apiCount = 0, apiLoadTime = 0;
      
      resources.forEach(r => {
        if (r.name.endsWith('.js')) {
          jsCount++;
          jsSize += r.transferSize || 0;
          jsLoadTime += r.duration || 0;
        } else if (r.name.endsWith('.css')) {
          cssCount++;
          cssSize += r.transferSize || 0;
        } else if (r.name.includes('/api/')) {
          apiCount++;
          apiLoadTime += r.duration || 0;
        }
      });

      return {
        loadTime: nav ? nav.loadEventEnd - nav.startTime : 0,
        domContentLoaded: nav ? nav.domContentLoadedEventEnd - nav.startTime : 0,
        fcp: performance.getEntriesByType('paint').find(p => p.name === 'first-contentful-paint')?.startTime || 0,
        lcp: performance.getEntriesByType('paint').find(p => p.name === 'largest-contentful-paint')?.startTime || 0,
        totalResources: resources.length,
        jsCount,
        jsSize,
        jsLoadTime,
        cssCount,
        cssSize,
        apiCount,
        apiLoadTime
      };
    });

    result.metrics = metrics;
    result.resources = {
      js: { count: metrics.jsCount, size: metrics.jsSize, loadTime: metrics.jsLoadTime },
      css: { count: metrics.cssCount, size: metrics.cssSize },
      api: { count: metrics.apiCount, loadTime: metrics.apiLoadTime }
    };

    console.log(`   ✅ 加载成功: ${result.loadTime}ms`);
    console.log(`   📦 JS: ${metrics.jsCount}个文件, ${(metrics.jsSize/1024).toFixed(1)}KB`);
    console.log(`   📊 FCP: ${metrics.fcp.toFixed(0)}ms, DOM: ${metrics.domContentLoaded.toFixed(0)}ms`);

  } catch (error) {
    result.status = 'error';
    result.error = error.message;
    console.log(`   ❌ 加载失败: ${error.message}`);
  }

  return result;
}

async function main() {
  console.log('\n' + '='.repeat(70));
  console.log('🚀 Event2Table 生产环境性能测试');
  console.log('='.repeat(70));
  console.log(`\n📍 生产服务器: ${CONFIG.baseURL}`);
  console.log(`📍 后端API: ${CONFIG.backendURL}\n`);

  ensureDir(CONFIG.outputDir);

  const browser = await chromium.launch({
    headless: CONFIG.headless,
    args: ['--start-maximized']
  });

  const context = await browser.newContext({
    viewport: CONFIG.viewport
  });

  const page = await context.newPage();
  const results = [];

  // 测试页面列表
  const pages = [
    { name: 'Dashboard', path: '/' },
    { name: 'Games', path: '/#/games' },
    { name: 'Events', path: '/#/events' },
    { name: 'Canvas', path: '/#/canvas' }
  ];

  for (const p of pages) {
    const result = await testPage(page, p.name, p.path);
    results.push(result);
    
    // 截图
    if (result.status === 'success') {
      await page.screenshot({
        path: path.join(CONFIG.outputDir, `${p.name.toLowerCase()}-production.png`),
        fullPage: true
      });
    }
  }

  await browser.close();

  // 保存结果
  const resultPath = path.join(CONFIG.outputDir, 'production-test-results.json');
  fs.writeFileSync(resultPath, JSON.stringify(results, null, 2));

  // 打印总结
  console.log('\n' + '='.repeat(70));
  console.log('📊 测试结果总结');
  console.log('='.repeat(70));

  results.forEach(r => {
    const status = r.status === 'success' ? '✅' : '❌';
    const loadTime = r.loadTime || 0;
    console.log(`${status} ${r.page.padEnd(12)}: ${loadTime.toString().padStart(5)}ms`);
  });

  const avgLoadTime = results
    .filter(r => r.status === 'success')
    .reduce((sum, r) => sum + r.loadTime, 0) / results.filter(r => r.status === 'success').length;

  const totalJsSize = results.reduce((sum, r) => sum + (r.resources?.js?.size || 0), 0);

  console.log(`\n📈 统计:`);
  console.log(`   平均加载时间: ${avgLoadTime.toFixed(0)}ms`);
  console.log(`   JS总大小: ${(totalJsSize/1024).toFixed(1)}KB`);
  console.log(`   成功页面: ${results.filter(r => r.status === 'success').length}/${results.length}`);

  console.log(`\n💾 结果已保存: ${resultPath}`);
  console.log('='.repeat(70) + '\n');
}

main().catch(console.error);
