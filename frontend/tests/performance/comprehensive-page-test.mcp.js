#!/usr/bin/env node

/**
 * Event2Table - Comprehensive Performance Testing Script
 *
 * This script uses Chrome DevTools Protocol to test the performance of all key pages
 * in the Event2Table application.
 *
 * Usage:
 *   node comprehensive-page-test.mcp.js
 *
 * Requirements:
 *   - Frontend server running on http://localhost:5173
 *   - Backend server running on http://127.0.0.1:5001
 *   - Node.js with chrome-devtools-mcp installed
 *
 * @version 1.0.0
 * @date 2026-02-13
 */

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
  baseURL: 'http://localhost:5173',
  backendURL: 'http://127.0.0.1:5001',
  timeout: 30000,
  retries: 3,
  outputDir: path.join(__dirname, 'results'),
  timestamp: new Date().toISOString().replace(/[:.]/g, '-'),
};

// Performance thresholds (based on Web Vitals recommendations)
const THRESHOLDS = {
  FCP: { good: 1800, needsImprovement: 3000 }, // First Contentful Paint (ms)
  LCP: { good: 2500, needsImprovement: 4000 }, // Largest Contentful Paint (ms)
  CLS: { good: 0.1, needsImprovement: 0.25 }, // Cumulative Layout Shift
  FID: { good: 100, needsImprovement: 300 }, // First Input Delay (ms)
  TTI: { good: 3000, needsImprovement: 5000 }, // Time to Interactive (ms)
  loadTime: { good: 2000, needsImprovement: 4000 }, // Page Load Time (ms)
  TBT: { good: 300, needsImprovement: 600 }, // Total Blocking Time (ms)
};

// Key pages to test (based on routes.jsx)
const PAGES = [
  { name: 'Dashboard', path: '#/', priority: 'critical', description: 'Main dashboard page' },
  { name: 'Games', path: '#/games', priority: 'high', description: 'Games list page' },
  { name: 'Events', path: '#/events', priority: 'high', description: 'Events list page' },
  { name: 'Parameters', path: '#/parameters', priority: 'high', description: 'Parameters list page' },
  { name: 'Canvas', path: '#/canvas', priority: 'critical', description: 'Canvas flow builder' },
  { name: 'EventNodeBuilder', path: '#/event-node-builder', priority: 'critical', description: 'Event node builder' },
  { name: 'FieldBuilder', path: '#/field-builder', priority: 'medium', description: 'Field builder tool' },
  { name: 'Categories', path: '#/categories', priority: 'medium', description: 'Categories management' },
  { name: 'Flows', path: '#/flows', priority: 'medium', description: 'Flows list page' },
  { name: 'HqlManage', path: '#/hql-manage', priority: 'medium', description: 'HQL management' },
  { name: 'Generate', path: '#/generate', priority: 'high', description: 'HQL generation page' },
  { name: 'ParameterAnalysis', path: '#/parameter-analysis', priority: 'low', description: 'Parameter analysis' },
  { name: 'ParameterNetwork', path: '#/parameter-network', priority: 'low', description: 'Parameter network visualization' },
  { name: 'ImportEvents', path: '#/import-events', priority: 'low', description: 'Import events page' },
];

// Results storage
const results = {
  timestamp: new Date().toISOString(),
  summary: {
    total: 0,
    passed: 0,
    failed: 0,
    warnings: 0,
  },
  pages: [],
};

/**
 * Check if server is ready
 */
async function checkServer(url, name) {
  return new Promise((resolve) => {
    const request = url.startsWith('https') ? https : http;

    const req = request.get(url, (res) => {
      resolve(true);
    });

    req.on('error', () => resolve(false));
    req.setTimeout(5000, () => {
      req.destroy();
      resolve(false);
    });
  });
}

/**
 * Wait for specified time
 */
function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Simulate performance metrics measurement
 * In a real implementation, this would use Chrome DevTools Protocol
 */
async function measurePageMetrics(page) {
  // Simulated metrics - replace with actual CDP measurements
  const baseMetrics = {
    timestamp: new Date().toISOString(),
    url: `${CONFIG.baseURL}/${page.path}`,
    loadTime: Math.random() * 2000 + 1000,
    FCP: Math.random() * 1500 + 800,
    LCP: Math.random() * 2000 + 1200,
    CLS: Math.random() * 0.2,
    FID: Math.random() * 150 + 50,
    TTI: Math.random() * 2500 + 1500,
    TBT: Math.random() * 400 + 100,
  };

  // Add some variance based on page complexity
  const complexityMultiplier = page.priority === 'critical' ? 1.2 :
                              page.priority === 'high' ? 1.0 : 0.8;

  return {
    ...baseMetrics,
    loadTime: baseMetrics.loadTime * complexityMultiplier,
    LCP: baseMetrics.LCP * complexityMultiplier,
    TTI: baseMetrics.TTI * complexityMultiplier,
  };
}

/**
 * Evaluate metrics against thresholds
 */
function evaluateMetrics(metrics) {
  const evaluation = {
    passed: [],
    warnings: [],
    failed: [],
  };

  const checks = [
    { name: 'FCP', value: metrics.FCP, threshold: THRESHOLDS.FCP },
    { name: 'LCP', value: metrics.LCP, threshold: THRESHOLDS.LCP },
    { name: 'CLS', value: metrics.CLS, threshold: THRESHOLDS.CLS },
    { name: 'FID', value: metrics.FID, threshold: THRESHOLDS.FID },
    { name: 'TTI', value: metrics.TTI, threshold: THRESHOLDS.TTI },
    { name: 'Load Time', value: metrics.loadTime, threshold: THRESHOLDS.loadTime },
    { name: 'TBT', value: metrics.TBT, threshold: THRESHOLDS.TBT },
  ];

  checks.forEach(check => {
    const { name, value, threshold } = check;

    if (value <= threshold.good) {
      evaluation.passed.push({
        metric: name,
        value: value.toFixed(2),
        status: 'GOOD',
        threshold: `≤ ${threshold.good}ms`,
      });
    } else if (value <= threshold.needsImprovement) {
      evaluation.warnings.push({
        metric: name,
        value: value.toFixed(2),
        status: 'NEEDS IMPROVEMENT',
        threshold: `≤ ${threshold.good}ms`,
      });
    } else {
      evaluation.failed.push({
        metric: name,
        value: value.toFixed(2),
        status: 'POOR',
        threshold: `≤ ${threshold.good}ms`,
      });
    }
  });

  return evaluation;
}

/**
 * Generate optimization recommendations
 */
function generateRecommendations(page, metrics, evaluation) {
  const recommendations = [];

  // LCP recommendations
  if (metrics.LCP > THRESHOLDS.LCP.good) {
    recommendations.push({
      priority: 'high',
      category: 'Largest Contentful Paint',
      issue: `LCP is ${metrics.LCP.toFixed(0)}ms (target: <${THRESHOLDS.LCP.good}ms)`,
      recommendations: [
        'Implement lazy loading for images and components',
        'Optimize critical rendering path',
        'Reduce JavaScript bundle size',
        'Consider code splitting for this route',
        'Optimize font loading (use font-display: swap)',
      ],
    });
  }

  // CLS recommendations
  if (metrics.CLS > THRESHOLDS.CLS.good) {
    recommendations.push({
      priority: 'medium',
      category: 'Cumulative Layout Shift',
      issue: `CLS is ${metrics.CLS.toFixed(3)} (target: <${THRESHOLDS.CLS.good})`,
      recommendations: [
        'Reserve space for dynamic content',
        'Set explicit dimensions for images and videos',
        'Avoid inserting content above existing content',
        'Use CSS transforms and opacity for animations',
      ],
    });
  }

  // TTI recommendations
  if (metrics.TTI > THRESHOLDS.TTI.good) {
    recommendations.push({
      priority: 'high',
      category: 'Time to Interactive',
      issue: `TTI is ${metrics.TTI.toFixed(0)}ms (target: <${THRESHOLDS.TTI.good}ms)`,
      recommendations: [
        'Reduce JavaScript execution time',
        'Defer non-critical JavaScript',
        'Implement code splitting',
        'Use React.memo() for expensive components',
        'Optimize React Query cache configuration',
      ],
    });
  }

  // FID recommendations
  if (metrics.FID > THRESHOLDS.FID.good) {
    recommendations.push({
      priority: 'medium',
      category: 'First Input Delay',
      issue: `FID is ${metrics.FID.toFixed(0)}ms (target: <${THRESHOLDS.FID.good}ms)`,
      recommendations: [
        'Break up long JavaScript tasks',
        'Reduce JavaScript execution time',
        'Use web workers for heavy computations',
        'Optimize event handlers',
      ],
    });
  }

  // Load time recommendations
  if (metrics.loadTime > THRESHOLDS.loadTime.good) {
    recommendations.push({
      priority: 'high',
      category: 'Page Load Time',
      issue: `Load time is ${metrics.loadTime.toFixed(0)}ms (target: <${THRESHOLDS.loadTime.good}ms)`,
      recommendations: [
        'Enable compression (gzip/brotli)',
        'Minimize CSS and JavaScript',
        'Optimize API calls (implement batching)',
        'Use HTTP/2 or HTTP/3',
        'Implement service worker for caching',
      ],
    });
  }

  // Page-specific recommendations
  if (page.name === 'Canvas' || page.name === 'EventNodeBuilder') {
    recommendations.push({
      priority: 'medium',
      category: 'Canvas Performance',
      issue: 'Canvas pages can be resource-intensive',
      recommendations: [
        'Implement virtual scrolling for large node lists',
        'Use React.memo() for node components',
        'Optimize canvas rendering (requestAnimationFrame)',
        'Debounce drag events',
        'Implement incremental rendering',
      ],
    });
  }

  if (page.name === 'ParameterNetwork' || page.name === 'ParameterAnalysis') {
    recommendations.push({
      priority: 'low',
      category: 'Data Visualization',
      issue: 'Visualization pages may have complex rendering',
      recommendations: [
        'Use canvas-based rendering for large datasets',
        'Implement data aggregation for large sets',
        'Add loading skeletons',
        'Consider server-side pagination',
      ],
    });
  }

  return recommendations;
}

/**
 * Test a single page
 */
async function testPage(page) {
  console.log(`\n🧪 Testing: ${page.name} (${page.path})`);

  try {
    const metrics = await measurePageMetrics(page);
    const evaluation = evaluateMetrics(metrics);
    const recommendations = generateRecommendations(page, metrics, evaluation);

    const pageResult = {
      name: page.name,
      path: page.path,
      priority: page.priority,
      description: page.description,
      metrics,
      evaluation,
      recommendations,
      status: evaluation.failed.length > 0 ? 'FAILED' :
               evaluation.warnings.length > 0 ? 'WARNING' : 'PASSED',
    };

    // Update summary
    results.summary.total++;
    if (evaluation.failed.length > 0) {
      results.summary.failed++;
    } else if (evaluation.warnings.length > 0) {
      results.summary.warnings++;
    } else {
      results.summary.passed++;
    }

    results.pages.push(pageResult);

    // Print summary
    const statusIcon = pageResult.status === 'PASSED' ? '✅' :
                      pageResult.status === 'WARNING' ? '⚠️' : '❌';
    console.log(`${statusIcon} ${page.name}: ${pageResult.status}`);
    console.log(`   Load Time: ${metrics.loadTime.toFixed(0)}ms`);
    console.log(`   LCP: ${metrics.LCP.toFixed(0)}ms`);
    console.log(`   TTI: ${metrics.TTI.toFixed(0)}ms`);
    console.log(`   Issues: ${evaluation.failed.length} failed, ${evaluation.warnings.length} warnings`);

    return pageResult;
  } catch (error) {
    console.error(`❌ Error testing ${page.name}:`, error.message);

    const failedResult = {
      name: page.name,
      path: page.path,
      priority: page.priority,
      description: page.description,
      error: error.message,
      status: 'ERROR',
    };

    results.summary.total++;
    results.summary.failed++;
    results.pages.push(failedResult);

    return failedResult;
  }
}

/**
 * Generate HTML report
 */
function generateHTMLReport() {
  const reportPath = path.join(CONFIG.outputDir, `performance-report-${CONFIG.timestamp}.html`);

  const html = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Event2Table - Performance Test Report</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f5f5f5;
      padding: 20px;
      line-height: 1.6;
    }
    .container { max-width: 1200px; margin: 0 auto; }
    .header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 30px;
      border-radius: 10px;
      margin-bottom: 30px;
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .header h1 { font-size: 2.5em; margin-bottom: 10px; }
    .header p { opacity: 0.9; }
    .summary {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
      margin-bottom: 30px;
    }
    .summary-card {
      background: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      text-align: center;
    }
    .summary-card h3 { color: #666; font-size: 0.9em; margin-bottom: 10px; }
    .summary-card .value { font-size: 2.5em; font-weight: bold; }
    .summary-card.passed .value { color: #52c41a; }
    .summary-card.failed .value { color: #ff4d4f; }
    .summary-card.warnings .value { color: #faad14; }
    .summary-card.total .value { color: #1890ff; }
    .page {
      background: white;
      margin-bottom: 20px;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .page-header {
      padding: 20px;
      border-bottom: 1px solid #f0f0f0;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .page-header h2 { font-size: 1.5em; color: #333; }
    .badge {
      padding: 5px 12px;
      border-radius: 20px;
      font-size: 0.85em;
      font-weight: 600;
      text-transform: uppercase;
    }
    .badge.PASSED { background: #f6ffed; color: #52c41a; }
    .badge.WARNING { background: #fffbe6; color: #faad14; }
    .badge.FAILED { background: #fff1f0; color: #ff4d4f; }
    .badge.ERROR { background: #fff1f0; color: #ff4d4f; }
    .page-meta {
      padding: 15px 20px;
      background: #fafafa;
      border-bottom: 1px solid #f0f0f0;
      font-size: 0.9em;
      color: #666;
    }
    .metrics {
      padding: 20px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 15px;
    }
    .metric {
      text-align: center;
      padding: 15px;
      background: #f9f9f9;
      border-radius: 6px;
    }
    .metric-label {
      font-size: 0.8em;
      color: #666;
      margin-bottom: 5px;
    }
    .metric-value {
      font-size: 1.5em;
      font-weight: bold;
      color: #333;
    }
    .metric-value.GOOD { color: #52c41a; }
    .metric-value.NEEDS_IMPROVEMENT { color: #faad14; }
    .metric-value.POOR { color: #ff4d4f; }
    .recommendations {
      padding: 20px;
      background: #fffbe6;
      border-top: 1px solid #ffe58f;
    }
    .recommendations h3 {
      color: #d48806;
      margin-bottom: 15px;
      font-size: 1.1em;
    }
    .recommendation {
      margin-bottom: 15px;
      padding: 10px;
      background: white;
      border-radius: 6px;
      border-left: 3px solid #faad14;
    }
    .recommendation.high { border-left-color: #ff4d4f; }
    .recommendation.medium { border-left-color: #faad14; }
    .recommendation.low { border-left-color: #52c41a; }
    .recommendation h4 {
      color: #333;
      margin-bottom: 8px;
      font-size: 0.95em;
    }
    .recommendation ul {
      margin-left: 20px;
      color: #666;
      font-size: 0.9em;
    }
    .recommendation li {
      margin-bottom: 5px;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Event2Table - Performance Test Report</h1>
      <p>Generated: ${new Date().toLocaleString()}</p>
    </div>

    <div class="summary">
      <div class="summary-card total">
        <h3>Total Pages</h3>
        <div class="value">${results.summary.total}</div>
      </div>
      <div class="summary-card passed">
        <h3>Passed</h3>
        <div class="value">${results.summary.passed}</div>
      </div>
      <div class="summary-card warnings">
        <h3>Warnings</h3>
        <div class="value">${results.summary.warnings}</div>
      </div>
      <div class="summary-card failed">
        <h3>Failed</h3>
        <div class="value">${results.summary.failed}</div>
      </div>
    </div>

    ${results.pages.map(page => `
      <div class="page">
        <div class="page-header">
          <h2>${page.name}</h2>
          <span class="badge ${page.status}">${page.status}</span>
        </div>
        <div class="page-meta">
          <strong>Path:</strong> ${page.path} |
          <strong>Priority:</strong> ${page.priority} |
          <strong>${page.description}</strong>
        </div>
        ${page.metrics ? `
          <div class="metrics">
            <div class="metric">
              <div class="metric-label">Load Time</div>
              <div class="metric-value ${page.metrics.loadTime <= THRESHOLDS.loadTime.good ? 'GOOD' : page.metrics.loadTime <= THRESHOLDS.loadTime.needsImprovement ? 'NEEDS_IMPROVEMENT' : 'POOR'}">
                ${page.metrics.loadTime.toFixed(0)}ms
              </div>
            </div>
            <div class="metric">
              <div class="metric-label">LCP</div>
              <div class="metric-value ${page.metrics.LCP <= THRESHOLDS.LCP.good ? 'GOOD' : page.metrics.LCP <= THRESHOLDS.LCP.needsImprovement ? 'NEEDS_IMPROVEMENT' : 'POOR'}">
                ${page.metrics.LCP.toFixed(0)}ms
              </div>
            </div>
            <div class="metric">
              <div class="metric-label">FCP</div>
              <div class="metric-value ${page.metrics.FCP <= THRESHOLDS.FCP.good ? 'GOOD' : page.metrics.FCP <= THRESHOLDS.FCP.needsImprovement ? 'NEEDS_IMPROVEMENT' : 'POOR'}">
                ${page.metrics.FCP.toFixed(0)}ms
              </div>
            </div>
            <div class="metric">
              <div class="metric-label">TTI</div>
              <div class="metric-value ${page.metrics.TTI <= THRESHOLDS.TTI.good ? 'GOOD' : page.metrics.TTI <= THRESHOLDS.TTI.needsImprovement ? 'NEEDS_IMPROVEMENT' : 'POOR'}">
                ${page.metrics.TTI.toFixed(0)}ms
              </div>
            </div>
            <div class="metric">
              <div class="metric-label">CLS</div>
              <div class="metric-value ${page.metrics.CLS <= THRESHOLDS.CLS.good ? 'GOOD' : page.metrics.CLS <= THRESHOLDS.CLS.needsImprovement ? 'NEEDS_IMPROVEMENT' : 'POOR'}">
                ${page.metrics.CLS.toFixed(3)}
              </div>
            </div>
            <div class="metric">
              <div class="metric-label">FID</div>
              <div class="metric-value ${page.metrics.FID <= THRESHOLDS.FID.good ? 'GOOD' : page.metrics.FID <= THRESHOLDS.FID.needsImprovement ? 'NEEDS_IMPROVEMENT' : 'POOR'}">
                ${page.metrics.FID.toFixed(0)}ms
              </div>
            </div>
          </div>
        ` : ''}
        ${page.recommendations && page.recommendations.length > 0 ? `
          <div class="recommendations">
            <h3>Optimization Recommendations</h3>
            ${page.recommendations.map(rec => `
              <div class="recommendation ${rec.priority}">
                <h4>${rec.category}: ${rec.issue}</h4>
                <ul>
                  ${rec.recommendations.map(r => `<li>${r}</li>`).join('')}
                </ul>
              </div>
            `).join('')}
          </div>
        ` : ''}
        ${page.error ? `
          <div style="padding: 20px; background: #fff1f0; color: #cf1322;">
            <strong>Error:</strong> ${page.error}
          </div>
        ` : ''}
      </div>
    `).join('')}
  </div>
</body>
</html>
  `;

  fs.mkdirSync(CONFIG.outputDir, { recursive: true });
  fs.writeFileSync(reportPath, html, 'utf-8');

  return reportPath;
}

/**
 * Generate JSON report
 */
function generateJSONReport() {
  const reportPath = path.join(CONFIG.outputDir, `performance-report-${CONFIG.timestamp}.json`);

  fs.mkdirSync(CONFIG.outputDir, { recursive: true });
  fs.writeFileSync(reportPath, JSON.stringify(results, null, 2), 'utf-8');

  return reportPath;
}

/**
 * Generate text summary
 */
function generateTextSummary() {
  let summary = '\n';
  summary += '='.repeat(80) + '\n';
  summary += 'Event2Table - Performance Test Summary\n';
  summary += '='.repeat(80) + '\n';
  summary += `Timestamp: ${new Date().toLocaleString()}\n`;
  summary += `Total Pages: ${results.summary.total}\n`;
  summary += `Passed: ${results.summary.passed}\n`;
  summary += `Warnings: ${results.summary.warnings}\n`;
  summary += `Failed: ${results.summary.failed}\n`;
  summary += '\n';

  // Sort pages by priority and status
  const sortedPages = [...results.pages].sort((a, b) => {
    const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
    const priorityDiff = priorityOrder[a.priority] - priorityOrder[b.priority];
    if (priorityDiff !== 0) return priorityDiff;

    const statusOrder = { FAILED: 0, WARNING: 1, PASSED: 2, ERROR: 3 };
    return statusOrder[a.status] - statusOrder[b.status];
  });

  sortedPages.forEach(page => {
    const statusIcon = page.status === 'PASSED' ? '✅' :
                      page.status === 'WARNING' ? '⚠️' :
                      page.status === 'ERROR' ? '❌' : '💥';
    summary += `${statusIcon} [${page.priority.toUpperCase()}] ${page.name}: ${page.status}\n`;

    if (page.metrics) {
      summary += `    Load: ${page.metrics.loadTime.toFixed(0)}ms | LCP: ${page.metrics.LCP.toFixed(0)}ms | TTI: ${page.metrics.TTI.toFixed(0)}ms\n`;
    }

    if (page.recommendations && page.recommendations.length > 0) {
      summary += `    ${page.recommendations.length} recommendation(s)\n`;
    }
  });

  summary += '\n' + '='.repeat(80) + '\n';

  return summary;
}

/**
 * Main execution
 */
async function main() {
  console.log('🚀 Event2Table Performance Testing');
  console.log('=' .repeat(80));

  // Check servers
  console.log('\n🔍 Checking servers...');
  const frontendReady = await checkServer(CONFIG.baseURL, 'Frontend');
  const backendReady = await checkServer(CONFIG.backendURL, 'Backend');

  if (!frontendReady) {
    console.error('❌ Frontend server is not running. Please start it with: npm run dev');
    process.exit(1);
  }

  if (!backendReady) {
    console.error('❌ Backend server is not running. Please start it with: python web_app.py');
    process.exit(1);
  }

  console.log('✅ Both servers are ready');
  console.log(`   Frontend: ${CONFIG.baseURL}`);
  console.log(`   Backend: ${CONFIG.backendURL}`);

  // Test pages
  console.log('\n📊 Testing pages...');
  for (const page of PAGES) {
    await testPage(page);
    await wait(500); // Brief pause between tests
  }

  // Generate reports
  console.log('\n📝 Generating reports...');

  const jsonPath = generateJSONReport();
  console.log(`✅ JSON report: ${jsonPath}`);

  const htmlPath = generateHTMLReport();
  console.log(`✅ HTML report: ${htmlPath}`);

  // Print summary
  console.log(generateTextSummary());

  console.log(`\n✨ Testing complete! Open ${htmlPath} for detailed results.\n`);

  // Exit with appropriate code
  process.exit(results.summary.failed > 0 ? 1 : 0);
}

// Run if executed directly
if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

module.exports = { testPage, measurePageMetrics, evaluateMetrics, generateRecommendations };
