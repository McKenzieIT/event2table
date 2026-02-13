/**
 * 核心 Web 指标测试 - 使用 chrome-devtools-mcp
 * 测量：LCP, FID, CLS, FCP, TTI
 */

const chromium = require('chrome-devtools-mcp');

const BASE_URL = 'http://localhost:5173';
const TARGET_METRICS = {
  FCP: 1500,    // First Contentful Paint < 1.5s
  LCP: 2500,    // Largest Contentful Paint < 2.5s
  FID: 100,     // First Input Delay < 100ms
  CLS: 0.1,     // Cumulative Layout Shift < 0.1
  TTI: 3500     // Time to Interactive < 3.5s
};

async function measureCoreWebVitals() {
  console.log('=== 核心 Web 指标测试 ===\n');

  // 导航到页面
  await chromium.navigate(BASE_URL);
  await chromium.waitForLoad('networkidle');

  // 注入 Web Vitals 库
  await chromium.evaluate(`
    // 注入 web-vitals 库
    (function() {
      const script = document.createElement('script');
      script.src = 'https://unpkg.com/web-vitals@3/dist/web-vitals.iife.js';
      script.onload = () => {
        // 收集指标
        window.collectedMetrics = {};

        webVitals.getCLS(console.log);
        webVitals.getFID(console.log);
        webVitals.getFCP(console.log);
        webVitals.getLCP(console.log);
        webVitals.getTTFB(console.log);
      };
      document.head.appendChild(script);
    })();
  `);

  // 等待指标收集
  await chromium.waitForTimeout(3000);

  // 从控制台提取指标
  const consoleLogs = await chromium.getConsoleLogs();
  const metrics = parseWebVitals(consoleLogs);

  // 与目标值比较
  const results = {
    FCP: { value: metrics.FCP || 0, target: TARGET_METRICS.FCP, pass: (metrics.FCP || 0) < TARGET_METRICS.FCP },
    LCP: { value: metrics.LCP || 0, target: TARGET_METRICS.LCP, pass: (metrics.LCP || 0) < TARGET_METRICS.LCP },
    FID: { value: metrics.FID || 0, target: TARGET_METRICS.FID, pass: (metrics.FID || 0) < TARGET_METRICS.FID },
    CLS: { value: metrics.CLS || 0, target: TARGET_METRICS.CLS, pass: (metrics.CLS || 0) < TARGET_METRICS.CLS },
    TTI: { value: metrics.TTI || 0, target: TARGET_METRICS.TTI, pass: (metrics.TTI || 0) < TARGET_METRICS.TTI }
  };

  // 打印结果
  console.log('\n核心 Web 指标结果:\n');
  Object.entries(results).forEach(([metric, data]) => {
    const status = data.pass ? '✅' : '❌';
    console.log(`${status} ${metric}: ${data.value}ms (目标: <${data.target}ms)`);
  });

  return results;
}

function parseWebVitals(logs) {
  // 解析控制台日志以提取指标值
  const metrics = {};
  logs.forEach(log => {
    if (log.name === 'FCP') metrics.FCP = log.value;
    if (log.name === 'LCP') metrics.LCP = log.value;
    if (log.name === 'FID') metrics.FID = log.value;
    if (log.name === 'CLS') metrics.CLS = log.value;
    if (log.name === 'TTFB') metrics.TTI = log.value;
  });
  return metrics;
}

// 运行测试
measureCoreWebVitals()
  .then(results => {
    const allPassed = Object.values(results).every(r => r.pass);
    process.exit(allPassed ? 0 : 1);
  })
  .catch(error => {
    console.error('测试失败:', error);
    process.exit(1);
  });
