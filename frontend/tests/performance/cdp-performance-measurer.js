#!/usr/bin/env node

/**
 * Event2Table - Chrome DevTools Protocol Performance Measurer
 *
 * This script uses Chrome DevTools Protocol to measure actual performance metrics
 * from the browser's perspective.
 *
 * Usage:
 *   node cdp-performance-measurer.js <url> [output-file]
 *
 * Example:
 *   node cdp-performance-measurer.js http://localhost:5173 results/dashboard.json
 *
 * @version 1.0.0
 * @date 2026-02-13
 */

const chromeLauncher = require('chrome-launcher');
const CDP = require('chrome-remote-interface');
const fs = require('fs');
const path = require('path');

/**
 * Measure page performance using Chrome DevTools Protocol
 */
async function measurePerformance(url) {
  let chrome;
  let client;

  try {
    console.log(`🚀 Launching Chrome...`);
    chrome = await chromeLauncher.launch({
      chromeFlags: [
        '--headless',
        '--disable-gpu',
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-web-security',
        '--disable-features=IsolateOrigins,site-per-process',
      ],
      logLevel: 'error',
    });

    console.log(`📡 Connecting to Chrome DevTools Protocol...`);
    client = await CDP({ port: chrome.port });

    const { Page, Performance, Network, Runtime, DOM } = client;

    // Enable required domains
    await Page.enable();
    await Performance.enable();
    await Network.enable();
    await Runtime.enable();
    // await DOM.enable();  // DOM enable can be slow, only enable if needed

    console.log(`🌐 Navigating to: ${url}`);

    // Track resource loading
    const resources = [];
    Network.requestWillBeSent((params) => {
      resources.push({
        url: params.request.url,
        type: params.type,
        timestamp: params.timestamp,
      });
    });

    // Navigate to page
    await Page.navigate({ url });

    // Wait for page load complete
    console.log(`⏳ Waiting for page load...`);
    await Page.loadEventFired();

    // Wait a bit more for dynamic content
    await new Promise(resolve => setTimeout(resolve, 2000));

    console.log(`📊 Collecting metrics...`);

    // Get performance metrics
    const metricsResult = await Performance.getMetrics();
    const metrics = {};
    metricsResult.metrics.forEach(m => {
      metrics[m.name] = m.value;
    });

    // Get navigation timing metrics
    const navigationTiming = {
      dns: metrics['DNSLookup'] || 0,
      tcp: metrics['TCPConnect'] || 0,
      request: metrics['RequestStart'] || 0,
      response: metrics['ResponseStart'] || 0,
      domLoading: metrics['DomLoading'] || 0,
      domInteractive: metrics['DomInteractive'] || 0,
      domContentLoaded: metrics['DomContentLoadedEventEnd'] || 0,
      loadComplete: metrics['LoadEventEnd'] || 0,
    };

    // Calculate timing metrics
    const navigationStart = metrics['NavigationStart'] || 0;
    const loadTime = navigationTiming.loadComplete - navigationStart;
    const domContentLoadedTime = navigationTiming.domContentLoaded - navigationStart;
    const domInteractiveTime = navigationTiming.domInteractive - navigationStart;

    // Get paint timing metrics
    const firstPaint = metrics['FirstPaint'] ? metrics['FirstPaint'] - navigationStart : null;
    const firstContentfulPaint = metrics['FirstContentfulPaint'] ?
      metrics['FirstContentfulPaint'] - navigationStart : null;
    const firstMeaningfulPaint = metrics['FirstMeaningfulPaint'] ?
      metrics['FirstMeaningfulPaint'] - navigationStart : null;

    // Get layout metrics
    const layoutMetrics = await Page.getLayoutMetrics();
    const layoutShift = layoutMetrics.layoutViewport;
    const contentSize = layoutMetrics.contentSize;

    // Calculate Core Web Vitals estimates
    // Note: These are approximations. For accurate metrics, use Web Vitals library
    const lcp = firstContentfulPaint || 0; // Approximation
    const cls = 0; // Would need to track layout shifts over time
    const fid = 0; // Would need user interaction

    // Get memory usage (if available)
    let memoryUsage = null;
    try {
      const memoryMetrics = await Runtime.evaluate({
        expression: 'performance.memory ? { used: performance.memory.usedJSHeapSize, total: performance.memory.totalJSHeapSize, limit: performance.memory.jsHeapSizeLimit } : null'
      });
      memoryUsage = memoryMetrics.result.value;
    } catch (e) {
      // Memory API not available
    }

    // Get resource count
    const resourceCount = resources.length;

    // Calculate performance score
    const score = calculatePerformanceScore({
      loadTime,
      fcp: firstContentfulPaint,
      lcp,
      domContentLoadedTime,
      resourceCount,
    });

    const result = {
      url,
      timestamp: new Date().toISOString(),
      metrics: {
        // Navigation timing
        loadTime: Math.round(loadTime),
        domContentLoadedTime: Math.round(domContentLoadedTime),
        domInteractiveTime: Math.round(domInteractiveTime),

        // Paint timing
        firstPaint: firstPaint ? Math.round(firstPaint) : null,
        firstContentfulPaint: firstContentfulPaint ? Math.round(firstContentfulPaint) : null,
        firstMeaningfulPaint: firstMeaningfulPaint ? Math.round(firstMeaningfulPaint) : null,

        // Core Web Vitals (approximate)
        lcp: Math.round(lcp),
        cls,
        fid,

        // Resource metrics
        resourceCount,
        domNodes: metrics['DomNodes'] || 0,
        recalcStyleCount: metrics['RecalcStyleCount'] || 0,
        layoutCount: metrics['LayoutCount'] || 0,

        // Memory
        memoryUsage: memoryUsage ? {
          used: Math.round(memoryUsage.used / 1024 / 1024),
          total: Math.round(memoryUsage.total / 1024 / 1024),
          limit: Math.round(memoryUsage.limit / 1024 / 1024),
        } : null,

        // Layout
        layout: {
          viewport: {
            width: layoutShift.width,
            height: layoutShift.height,
          },
          content: {
            width: Math.round(contentSize.width),
            height: Math.round(contentSize.height),
          },
        },
      },
      score,
      recommendations: generateRecommendations(result),
    };

    return result;
  } finally {
    if (client) {
      await client.close();
    }
    if (chrome) {
      await chrome.kill();
    }
  }
}

/**
 * Calculate performance score (0-100)
 */
function calculatePerformanceScore(metrics) {
  let score = 100;

  // Load time (target: < 2s)
  if (metrics.loadTime > 4000) {
    score -= 30;
  } else if (metrics.loadTime > 2000) {
    score -= 15;
  }

  // FCP (target: < 1.8s)
  if (metrics.fcp > 3000) {
    score -= 25;
  } else if (metrics.fcp > 1800) {
    score -= 10;
  }

  // LCP (target: < 2.5s)
  if (metrics.lcp > 4000) {
    score -= 25;
  } else if (metrics.lcp > 2500) {
    score -= 10;
  }

  // Resource count
  if (metrics.resourceCount > 100) {
    score -= 10;
  } else if (metrics.resourceCount > 50) {
    score -= 5;
  }

  return Math.max(0, Math.min(100, score));
}

/**
 * Generate optimization recommendations
 */
function generateRecommendations(result) {
  const recommendations = [];
  const { metrics } = result;

  // Load time recommendations
  if (metrics.loadTime > 3000) {
    recommendations.push({
      priority: 'high',
      category: 'Page Load Time',
      issue: `Page load time is ${metrics.loadTime}ms (target: <2000ms)`,
      solutions: [
        'Implement code splitting for large JavaScript bundles',
        'Lazy load non-critical components',
        'Optimize and compress images',
        'Minify CSS and JavaScript',
        'Enable gzip/brotli compression',
        'Consider server-side rendering for initial content',
      ],
    });
  }

  // FCP recommendations
  if (metrics.firstContentfulPaint > 1800) {
    recommendations.push({
      priority: 'high',
      category: 'First Contentful Paint',
      issue: `FCP is ${metrics.firstContentfulPaint}ms (target: <1800ms)`,
      solutions: [
        'Reduce render-blocking resources',
        'Inline critical CSS',
        'Preload critical resources',
        'Optimize critical rendering path',
        'Defer non-critical CSS/JS',
      ],
    });
  }

  // Resource count recommendations
  if (metrics.resourceCount > 50) {
    recommendations.push({
      priority: 'medium',
      category: 'Resource Count',
      issue: `${metrics.resourceCount} resources loaded (target: <50)`,
      solutions: [
        'Bundle CSS and JavaScript files',
        'Use CSS sprites for icons',
        'Implement lazy loading for images',
        'Consider using a CDN for static assets',
        'Remove unused dependencies',
      ],
    });
  }

  // Memory recommendations
  if (metrics.memoryUsage && metrics.memoryUsage.used > 100) {
    recommendations.push({
      priority: 'medium',
      category: 'Memory Usage',
      issue: `JS heap size is ${metrics.memoryUsage.used}MB`,
      solutions: [
        'Check for memory leaks in event listeners',
        'Use React.memo() to prevent unnecessary re-renders',
        'Implement virtualization for long lists',
        'Clean up subscriptions and timers',
        'Avoid large object allocations',
      ],
    });
  }

  // Layout recommendations
  if (metrics.layoutCount > 50) {
    recommendations.push({
      priority: 'low',
      category: 'Layout Thrashing',
      issue: `${metrics.layoutCount} layouts detected`,
      solutions: [
        'Batch DOM reads and writes',
        'Use React.cloneElement() instead of direct DOM manipulation',
        'Avoid forcing synchronous layouts',
        'Use CSS transforms instead of changing position',
      ],
    });
  }

  return recommendations;
}

/**
 * Main execution
 */
async function main() {
  const url = process.argv[2];
  const outputFile = process.argv[3];

  if (!url) {
    console.error('Usage: node cdp-performance-measurer.js <url> [output-file]');
    console.error('Example: node cdp-performance-measurer.js http://localhost:5173 results.json');
    process.exit(1);
  }

  try {
    console.log('🔬 Event2Table - CDP Performance Measurer');
    console.log('='.repeat(60));
    console.log('');

    const result = await measurePerformance(url);

    console.log('');
    console.log('✅ Performance Measurement Complete');
    console.log('');
    console.log('📊 Metrics:');
    console.log(`   Load Time: ${result.metrics.loadTime}ms`);
    console.log(`   FCP: ${result.metrics.firstContentfulPaint}ms`);
    console.log(`   LCP: ${result.metrics.lcp}ms`);
    console.log(`   Resources: ${result.metrics.resourceCount}`);
    console.log(`   Score: ${result.score}/100`);
    console.log('');

    if (result.recommendations.length > 0) {
      console.log('💡 Recommendations:');
      result.recommendations.forEach((rec, i) => {
        console.log(`   ${i + 1}. [${rec.priority.toUpperCase()}] ${rec.category}`);
        console.log(`      ${rec.issue}`);
        rec.solutions.slice(0, 2).forEach(solution => {
          console.log(`      - ${solution}`);
        });
      });
      console.log('');
    }

    // Save to file if specified
    if (outputFile) {
      const outputDir = path.dirname(outputFile);
      if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
      }
      fs.writeFileSync(outputFile, JSON.stringify(result, null, 2));
      console.log(`💾 Results saved to: ${outputFile}`);
    }

    // Output JSON to stdout for script parsing
    console.log('');
    console.log('---RESULTS---');
    console.log(JSON.stringify(result));
    console.log('---END-RESULTS---');

    process.exit(0);
  } catch (error) {
    console.error('❌ Error:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

module.exports = { measurePerformance, calculatePerformanceScore, generateRecommendations };
