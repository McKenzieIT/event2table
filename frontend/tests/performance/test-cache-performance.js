#!/usr/bin/env node

/**
 * 生产环境缓存测试 - 第二次访问（带缓存）
 */

const { chromium } = require('playwright');

async function testWithCache() {
  console.log('\n🚀 测试缓存后的性能...\n');
  
  const browser = await chromium.launch({
    headless: false,
    args: ['--start-maximized']
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });

  const page = await context.newPage();

  // 第一次访问 - 预热缓存
  console.log('  📍 第一次访问（预热缓存）...');
  await page.goto('http://localhost:8888/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  // 第二次访问 - 测试缓存性能
  console.log('  📍 第二次访问（带缓存）...');
  const startTime = Date.now();
  await page.goto('http://localhost:8888/', { waitUntil: 'networkidle' });
  const loadTime = Date.now() - startTime;
  await page.waitForTimeout(2000);

  // 获取性能指标
  const metrics = await page.evaluate(() => {
    const nav = performance.getEntriesByType('navigation')[0];
    return {
      loadTime: nav ? nav.loadEventEnd - nav.startTime : 0,
      fcp: performance.getEntriesByType('paint').find(p => p.name === 'first-contentful-paint')?.startTime || 0
    };
  });

  console.log('\n' + '='.repeat(60));
  console.log('📊 缓存后性能');
  console.log('='.repeat(60));
  console.log(`   加载时间: ${loadTime}ms`);
  console.log(`   FCP: ${metrics.fcp.toFixed(0)}ms`);
  console.log('='.repeat(60) + '\n');

  await browser.close();

  return { loadTime, fcp: metrics.fcp };
}

testWithCache().then(({ loadTime }) => {
  if (loadTime < 1000) {
    console.log('🎉 缓存后性能优秀！\n');
  } else {
    console.log('📝 缓存后性能良好\n');
  }
});
