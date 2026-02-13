#!/usr/bin/env node

/**
 * 深度性能分析脚本
 */

const { chromium } = require('playwright');

async function analyzePerformance() {
  console.log('🔍 深度性能分析...\n');
  
  const browser = await chromium.launch({
    headless: false,
    args: ['--start-maximized']
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });

  const page = await context.newPage();

  // 监听所有网络请求
  const networkData = [];
  page.on('request', request => {
    networkData.push({
      type: 'request',
      url: request.url(),
      method: request.method(),
      time: Date.now()
    });
  });

  page.on('response', async response => {
    networkData.push({
      type: 'response',
      url: response.url(),
      status: response.status(),
      time: Date.now()
    });
  });

  // 导航到页面
  const startTime = Date.now();
  await page.goto('http://localhost:5173/', {
    waitUntil: 'networkidle',
    timeout: 30000
  });
  const loadTime = Date.now() - startTime;

  // 等待一会儿
  await page.waitForTimeout(2000);

  // 获取详细的性能数据
  const performanceData = await page.evaluate(() => {
    const nav = performance.getEntriesByType('navigation')[0];
    const resources = performance.getEntriesByType('resource');
    
    // 按类型统计资源
    const stats = {
      script: { count: 0, size: 0 },
      stylesheet: { count: 0, size: 0 },
      image: { count: 0, size: 0 },
      fetch: { count: 0, size: 0 },
      other: { count: 0, size: 0 }
    };

    resources.forEach(r => {
      const type = r.initiatorType;
      if (stats[type]) {
        stats[type].count++;
        stats[type].size += r.transferSize || 0;
      } else {
        stats.other.count++;
        stats.other.size += r.transferSize || 0;
      }
    });

    return {
      navigation: {
        dns: nav.domainLookupEnd - nav.domainLookupStart,
        connect: nav.connectEnd - nav.connectStart,
        request: nav.responseStart - nav.requestStart,
        response: nav.responseEnd - nav.responseStart,
        dom: nav.domComplete - nav.domLoading,
        load: nav.loadEventEnd - nav.loadEventStart,
        total: nav.loadEventEnd - nav.startTime
      },
      resourceStats: stats
    };
  });

  console.log('='.repeat(60));
  console.log('📊 性能分析结果');
  console.log('='.repeat(60));
  
  console.log('\n⏱️  时间分解:');
  console.log(`   DNS查询: ${performanceData.navigation.dns}ms`);
  console.log(`   建立连接: ${performanceData.navigation.connect}ms`);
  console.log(`   请求等待: ${performanceData.navigation.request}ms`);
  console.log(`   响应接收: ${performanceData.navigation.response}ms`);
  console.log(`   DOM构建: ${performanceData.navigation.dom}ms`);
  console.log(`   总加载时间: ${performanceData.navigation.total}ms`);

  console.log('\n📦 资源统计:');
  Object.entries(performanceData.resourceStats).forEach(([type, data]) => {
    if (data.count > 0) {
      console.log(`   ${type}: ${data.count}个, ${(data.size / 1024).toFixed(2)}KB`);
    }
  });

  console.log('\n🌐 网络请求:');
  const apiRequests = networkData.filter(n => n.url.includes('/api/'));
  console.log(`   API请求数: ${apiRequests.length}`);
  apiRequests.forEach(req => {
    console.log(`   - ${req.url.split('/').pop()}: ${req.status || 'pending'}`);
  });

  console.log('\n' + '='.repeat(60));

  await browser.close();
}

analyzePerformance();
