#!/usr/bin/env node

/**
 * 测试生产环境性能
 */

const { chromium } = require('playwright');

async function testProduction() {
  console.log('🚀 测试生产环境性能...\n');
  
  const browser = await chromium.launch({
    headless: false,
    args: ['--start-maximized']
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });

  const page = await context.newPage();

  // 记录性能数据
  const startTime = Date.now();
  
  await page.goto('http://localhost:5174/', {
    waitUntil: 'networkidle',
    timeout: 30000
  });
  
  const loadTime = Date.now() - startTime;
  
  // 等待渲染
  await page.waitForTimeout(2000);

  // 获取性能指标
  const metrics = await page.evaluate(() => {
    const nav = performance.getEntriesByType('navigation')[0];
    const resources = performance.getEntriesByType('resource');
    
    // 按类型统计
    let jsCount = 0, jsSize = 0;
    let cssCount = 0, cssSize = 0;
    
    resources.forEach(r => {
      if (r.name.endsWith('.js')) {
        jsCount++;
        jsSize += r.transferSize || 0;
      } else if (r.name.endsWith('.css')) {
        cssCount++;
        cssSize += r.transferSize || 0;
      }
    });
    
    return {
      loadTime: nav ? nav.loadEventEnd - nav.startTime : 0,
      domContentLoaded: nav ? nav.domContentLoadedEventEnd - nav.startTime : 0,
      fcp: performance.getEntriesByType('paint').find(p => p.name === 'first-contentful-paint')?.startTime || 0,
      jsCount,
      jsSize,
      cssCount,
      cssSize,
      totalResources: resources.length
    };
  });

  // 截图
  await page.screenshot({ 
    path: './test_results/realtime-test/dashboard-production.png', 
    fullPage: true 
  });

  console.log('='.repeat(60));
  console.log('📊 生产环境性能测试结果');
  console.log('='.repeat(60));
  console.log(`\n⏱️  时间指标:`);
  console.log(`   加载时间: ${metrics.loadTime}ms`);
  console.log(`   DOM就绪: ${metrics.domContentLoaded}ms`);
  console.log(`   FCP: ${metrics.fcp}ms`);
  
  console.log(`\n📦 资源加载:`);
  console.log(`   JS文件: ${metrics.jsCount}个, ${(metrics.jsSize / 1024).toFixed(2)}KB`);
  console.log(`   CSS文件: ${metrics.cssCount}个, ${(metrics.cssSize / 1024).toFixed(2)}KB`);
  console.log(`   总资源: ${metrics.totalResources}个`);
  
  // 与开发环境对比
  console.log(`\n📈 对比开发环境:`);
  console.log(`   JS文件: 250个 → ${metrics.jsCount}个 (${Math.round((1 - metrics.jsCount/250) * 100)}%↓)`);
  console.log(`   JS大小: 6490KB → ${(metrics.jsSize / 1024).toFixed(0)}KB (${Math.round((1 - metrics.jsSize/6490000) * 100)}%↓)`);
  
  console.log('\n' + '='.repeat(60));

  await browser.close();
  
  return {
    loadTime: metrics.loadTime,
    jsCount: metrics.jsCount,
    jsSize: metrics.jsSize,
    improvement: metrics.loadTime < 5000
  };
}

testProduction().then(result => {
  console.log('\n✅ 测试完成!');
  if (result.improvement) {
    console.log('🎉 性能已显著提升！');
  } else {
    console.log('⚠️  仍有优化空间');
  }
});
