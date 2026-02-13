#!/usr/bin/env node

/**
 * 生产环境性能测试
 * 测试部署在 Nginx 的生产版本
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const CONFIG = {
  baseURL: 'http://localhost:8888',
  headless: false,
  viewport: { width: 1920, height: 1080 },
  outputDir: './test_results/production-deployment-test'
};

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

async function testPage(browser, pageConfig) {
  console.log(`\n🧪 测试: ${pageConfig.name}`);
  console.log(`   URL: ${CONFIG.baseURL}${pageConfig.path}`);

  const context = await browser.newContext({
    viewport: CONFIG.viewport
  });

  const page = await context.newPage();
  
  // 收集控制台错误
  const consoleErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
      console.log(`   🔴 控制台错误: ${msg.text().substring(0, 100)}`);
    }
  });

  page.on('pageerror', error => {
    consoleErrors.push(error.message);
    console.log(`   🔴 页面错误: ${error.message.substring(0, 100)}`);
  });

  const result = {
    page: pageConfig.name,
    url: `${CONFIG.baseURL}${pageConfig.path}`,
    timestamp: new Date().toISOString(),
    status: 'unknown',
    loadTime: 0,
    metrics: {},
    consoleErrors: [],
    resources: {}
  };

  try {
    // 导航到页面
    const startTime = Date.now();
    await page.goto(`${CONFIG.baseURL}${pageConfig.path}`, {
      waitUntil: 'networkidle',
      timeout: 30000
    });
    result.loadTime = Date.now() - startTime;
    result.status = 'success';

    // 等待渲染
    await page.waitForTimeout(2000);

    // 获取详细性能指标
    const metrics = await page.evaluate(() => {
      const nav = performance.getEntriesByType('navigation')[0];
      const resources = performance.getEntriesByType('resource');
      
      // 统计资源
      let jsCount = 0, jsSize = 0;
      let cssCount = 0, cssSize = 0;
      let apiCount = 0, apiTime = 0;
      
      resources.forEach(r => {
        if (r.name.endsWith('.js')) {
          jsCount++;
          jsSize += r.transferSize || 0;
        } else if (r.name.endsWith('.css')) {
          cssCount++;
          cssSize += r.transferSize || 0;
        } else if (r.name.includes('/api/')) {
          apiCount++;
          apiTime += r.duration || 0;
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
        cssCount,
        cssSize,
        apiCount,
        apiTime
      };
    });

    result.metrics = metrics;
    result.resources = {
      js: { count: metrics.jsCount, size: metrics.jsSize },
      css: { count: metrics.cssCount, size: metrics.cssSize },
      api: { count: metrics.apiCount, time: metrics.apiTime }
    };
    result.consoleErrors = consoleErrors;

    console.log(`   ✅ 加载成功: ${result.loadTime}ms`);
    console.log(`   📦 JS: ${metrics.jsCount}个文件 (${(metrics.jsSize/1024).toFixed(1)}KB)`);
    console.log(`   📊 FCP: ${metrics.fcp.toFixed(0)}ms`);
    
    if (consoleErrors.length === 0) {
      console.log(`   ✅ 无控制台错误`);
    } else {
      console.log(`   ⚠️  ${consoleErrors.length} 个错误`);
    }

    // 截图
    await page.screenshot({
      path: path.join(CONFIG.outputDir, `${pageConfig.name.toLowerCase()}-prod.png`),
      fullPage: true
    });

  } catch (error) {
    result.status = 'error';
    result.error = error.message;
    console.log(`   ❌ 加载失败: ${error.message}`);
  }

  await context.close();
  return result;
}

async function main() {
  console.log('\n' + '='.repeat(70));
  console.log('🚀 Event2Table 生产环境部署测试');
  console.log('='.repeat(70));
  console.log(`\n📍 生产地址: ${CONFIG.baseURL}\n`);

  ensureDir(CONFIG.outputDir);

  const browser = await chromium.launch({
    headless: CONFIG.headless,
    args: ['--start-maximized']
  });

  const pages = [
    { name: 'Dashboard', path: '/' },
    { name: 'Games', path: '/#/games' },
    { name: 'Events', path: '/#/events' },
    { name: 'Canvas', path: '/#/canvas' }
  ];

  const results = [];
  for (const pageConfig of pages) {
    const result = await testPage(browser, pageConfig);
    results.push(result);
  }

  await browser.close();

  // 保存结果
  const resultPath = path.join(CONFIG.outputDir, 'deployment-test-results.json');
  fs.writeFileSync(resultPath, JSON.stringify(results, null, 2));

  // 打印总结
  console.log('\n' + '='.repeat(70));
  console.log('📊 生产环境测试结果');
  console.log('='.repeat(70));

  let totalErrors = 0;
  results.forEach(r => {
    const status = r.status === 'success' ? '✅' : '❌';
    const errorCount = r.consoleErrors?.length || 0;
    totalErrors += errorCount;
    console.log(`${status} ${r.page.padEnd(12)}: ${r.loadTime.toString().padStart(5)}ms ${errorCount > 0 ? `(${errorCount} errors)` : ''}`);
  });

  const avgLoadTime = results
    .filter(r => r.status === 'success')
    .reduce((sum, r) => sum + r.loadTime, 0) / results.filter(r => r.status === 'success').length;

  console.log(`\n📈 统计:`);
  console.log(`   平均加载时间: ${avgLoadTime.toFixed(0)}ms`);
  console.log(`   总错误数: ${totalErrors}`);
  console.log(`   成功率: ${results.filter(r => r.status === 'success').length}/${results.length}`);

  // 性能评级
  console.log(`\n🏆 性能评级:`);
  if (avgLoadTime < 1000) {
    console.log(`   🟢 优秀 - 平均加载时间 < 1秒`);
  } else if (avgLoadTime < 2000) {
    console.log(`   🟡 良好 - 平均加载时间 < 2秒`);
  } else {
    console.log(`   🔴 需优化 - 平均加载时间 > 2秒`);
  }

  if (totalErrors === 0) {
    console.log(`   🟢 优秀 - 无控制台错误`);
  } else {
    console.log(`   🔴 需修复 - ${totalErrors} 个错误`);
  }

  console.log(`\n💾 结果保存: ${resultPath}`);
  console.log('='.repeat(70) + '\n');

  return { results, avgLoadTime, totalErrors };
}

main().then(({ avgLoadTime, totalErrors }) => {
  if (avgLoadTime < 2000 && totalErrors === 0) {
    console.log('🎉 生产环境测试通过！可以正式上线！\n');
    process.exit(0);
  } else {
    console.log('⚠️  生产环境存在问题，请修复后再上线\n');
    process.exit(1);
  }
}).catch(err => {
  console.error('❌ 测试失败:', err);
  process.exit(1);
});
