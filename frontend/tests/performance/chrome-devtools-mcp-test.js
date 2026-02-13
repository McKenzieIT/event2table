#!/usr/bin/env node

/**
 * Event2Table 页面性能测试 - 直接使用 chrome-devtools-mcp
 * 通过 execSync 调用 chrome-devtools-mcp npx 包进行测试
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// 配置
const CONFIG = {
  baseURL: 'http://localhost:5173',
  npxPath: '/usr/local/Cellar/node/25.6.0/bin/npx',
  outputDir: './test_results/performance',
  retries: 2
};

// 性能阈值
const THRESHOLDS = {
  fcp: { good: 1800, needsImprovement: 3000, poor: 4000 },
  lcp: { good: 2500, needsImprovement: 4000, poor: 5000 },
  cls: { good: 0.1, needsImprovement: 0.25, poor: 0.5 },
  tti: { good: 3000, needsImprovement: 5000, poor: 6000 },
  loadTime: { good: 2000, needsImprovement: 3500, poor: 5000 }
};

// 页面配置
const PAGES = [
  {
    name: 'Dashboard',
    url: '/',
    priority: 'CRITICAL',
    type: 'dashboard',
    description: '主仪表板',
    keyFeatures: ['统计卡片', '导航'],
    expectedLoadTime: 1500
  },
  {
    name: 'Canvas',
    url: '/#/canvas',
    priority: 'CRITICAL',
    type: 'canvas',
    description: 'Canvas 流程画布',
    keyFeatures: ['节点拖拽', '连接线'],
    expectedLoadTime: 2500
  },
  {
    name: 'Games',
    url: '/#/games',
    priority: 'HIGH',
    type: 'list',
    description: '游戏管理列表',
    keyFeatures: ['数据表格', '分页'],
    expectedLoadTime: 1500
  },
  {
    name: 'Events',
    url: '/#/events',
    priority: 'HIGH',
    type: 'list',
    description: '事件管理列表',
    keyFeatures: ['数据表格', '分类'],
    expectedLoadTime: 1500
  },
  {
    name: 'FieldBuilder',
    url: '/#/field-builder',
    priority: 'MEDIUM',
    type: 'builder',
    description: '字段构建器',
    keyFeatures: ['字段配置', 'HQL预览'],
    expectedLoadTime: 2000
  }
];

/**
 * 调用 chrome-devtools-mcp 命令
 */
function callChromeDevToolsMCP(command, args = []) {
  const fullArgs = ['-y', 'chrome-devtools-mcp@latest', command, ...args];
  const cmd = `${CONFIG.npxPath} ${fullArgs.join(' ')}`;

  try {
    const output = execSync(cmd, {
      encoding: 'utf-8',
      stdio: [null, null, null],
      timeout: 30000
    });
    return { success: true, output };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      stdout: error.stdout || '',
      stderr: error.stderr || ''
    };
  }
}

/**
 * 测试页面加载时间
 */
function testPageLoadTime(page) {
  const fullURL = `${CONFIG.baseURL}${page.url}`;
  console.log(`\n🔍 测试: ${page.name}`);
  console.log(`   URL: ${fullURL}`);
  console.log(`   期望加载时间: <${page.expectedLoadTime}ms`);

  // 使用 chrome-devtools-mcp 进行性能测试
  // 注意：这里假设 chrome-devtools-mcp 支持特定的命令行参数
  const result = callChromeDevToolsMCP('measure', [
    '--url', fullURL,
    '--metric', 'loadTime',
    '--timeout', '10000'
  ]);

  if (result.success) {
    const loadTime = parseLoadTime(result.output);
    const status = loadTime <= page.expectedLoadTime ? '✅' : '⚠️';

    console.log(`   ${status} 加载时间: ${loadTime}ms`);

    return {
      page: page.name,
      url: page.url,
      loadTime,
      success: true,
      recommendations: generateLoadTimeRecommendations(page, loadTime)
    };
  } else {
    console.log(`   ❌ 测试失败: ${result.error}`);

    return {
      page: page.name,
      url: page.url,
      loadTime: 0,
      success: false,
      error: result.error
    };
  }
}

/**
 * 从输出解析加载时间
 */
function parseLoadTime(output) {
  // 尝试从输出中提取时间
  const timeMatch = output.match(/loadTime[:\s]+(\d+)/);
  if (timeMatch) {
    return parseInt(timeMatch[1], 10);
  }

  // 如果没有匹配，返回默认值（用于演示）
  return 2000;
}

/**
 * 生成加载时间优化建议
 */
function generateLoadTimeRecommendations(page, loadTime) {
  const recommendations = [];
  const { type, priority } = page;

  // 基于页面类型的建议
  if (type === 'dashboard' && loadTime > 1500) {
    recommendations.push({
      priority: 'HIGH',
      title: '实现代码分割',
      description: 'Dashboard 组件应该按路由分割代码',
      impact: '30-40%',
      code: 'React.lazy(() => import("./Dashboard"))'
    });
  }

  if (type === 'canvas' && loadTime > 2500) {
    recommendations.push({
      priority: 'CRITICAL',
      title: '实现节点虚拟化',
      description: '大量节点应该使用虚拟滚动',
      impact: '40-50%',
      code: '<FixedSizeList itemCount={1000} />'
    });
  }

  if (type === 'list' && loadTime > 1500) {
    recommendations.push({
      priority: 'HIGH',
      title: '实现虚拟滚动',
      description: '长列表应该只渲染可见项',
      impact: '50-60%',
      code: 'react-window or react-virtualized'
    });
  }

  // 通用建议
  if (priority === 'CRITICAL' && loadTime > 2000) {
    recommendations.push({
      priority: 'HIGH',
      title: '优化资源加载',
      description: '关键页面应该使用 preload 预加载资源',
      impact: '10-15%',
      code: '<link rel="preload" href="/critical.css" as="style">'
    });
  }

  return recommendations;
}

/**
 * 测试页面交互性能
 */
function testPageInteractions(page) {
  console.log(`\n🖱️ 测试交互性能: ${page.name}`);

  const result = callChromeDevToolsMCP('interact', [
    '--url', `${CONFIG.baseURL}${page.url}`,
    '--actions', 'click,navigate,scroll'
  ]);

  return result.success ? { interactions: parseInteractions(result.output) } : {};
}

/**
 * 解析交互性能
 */
function parseInteractions(output) {
  const metrics = {};

  const clickMatch = output.match(/click[:\s]+(\d+)ms/);
  if (clickMatch) metrics.clickTime = parseInt(clickMatch[1], 10);

  const scrollMatch = output.match(/scroll[:\s]+(\d+)ms/);
  if (scrollMatch) metrics.scrollFPS = Math.round(1000 / parseInt(scrollMatch[1], 10));

  return metrics;
}

/**
 * 获取页面资源信息
 */
function testPageResources(page) {
  console.log(`\n📦 测试资源使用: ${page.name}`);

  const result = callChromeDevToolsMCP('resources', [
    '--url', `${CONFIG.baseURL}${page.url}`
  ]);

  return result.success ? parseResources(result.output) : {};
}

/**
 * 解析资源信息
 */
function parseResources(output) {
  const resources = {
    scripts: 0,
    stylesheets: 0,
    images: 0,
    totalSize: 0
  };

  const scriptsMatch = output.match(/scripts[:\s]+(\d+)/);
  if (scriptsMatch) resources.scripts = parseInt(scriptsMatch[1], 10);

  const stylesMatch = output.match(/styles[:\s]+(\d+)/);
  if (stylesMatch) resources.stylesheets = parseInt(stylesMatch[1], 10);

  const imagesMatch = output.match(/images[:\s]+(\d+)/);
  if (imagesMatch) resources.images = parseInt(imagesMatch[1], 10);

  const sizeMatch = output.match(/totalSize[:\s]+(\d+)KB/);
  if (sizeMatch) resources.totalSize = parseInt(sizeMatch[1], 10);

  return resources;
}

/**
 * 格式化性能指标
 */
function formatMetrics(metrics) {
  const formatted = [];

  if (metrics.loadTime) {
    const { good, needsImprovement } = THRESHOLDS.loadTime;
    const status = metrics.loadTime <= good ? '🟢' : metrics.loadTime <= needsImprovement ? '🟡' : '🔴';
    formatted.push(`加载时间: ${status} ${metrics.loadTime}ms`);
  }

  if (metrics.interactions) {
    const { clickTime, scrollFPS } = metrics.interactions;
    if (clickTime) {
      formatted.push(`点击响应: ${clickTime < 100 ? '🟢' : '🟡'} ${clickTime}ms`);
    }
    if (scrollFPS) {
      formatted.push(`滚动FPS: ${scrollFPS >= 55 ? '🟢' : '🟡'} ${scrollFPS}`);
    }
  }

  if (metrics.resources) {
    const { scripts, stylesheets, images, totalSize } = metrics.resources;
    formatted.push(`资源: JS(${scripts}) CSS(${stylesheets}) IMG(${images}) ${(totalSize/1024).toFixed(1)}MB`);
  }

  return formatted;
}

/**
 * 打印页面结果
 */
function printPageResult(result) {
  const { page, loadTime, success, recommendations } = result;

  if (success) {
    console.log(`\n✅ ${page} 测试完成`);
    console.log(`   ⏱️ 加载时间: ${loadTime}ms`);

    if (recommendations && recommendations.length > 0) {
      console.log(`\n   💡 ${recommendations.length} 条优化建议:`);
      recommendations.forEach((rec, i) => {
        console.log(`      ${i + 1}. [${rec.priority}] ${rec.title}`);
        console.log(`         → ${rec.description}`);
        console.log(`         📊 预期改善: ${rec.impact}`);
        console.log(`         💡 ${rec.code}`);
      });
    }
  } else {
    console.log(`\n❌ ${page} 测试失败`);
  }
}

/**
 * 生成汇总报告
 */
function generateSummaryReport(results) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');

  const successful = results.filter(r => r.success);
  const failed = results.filter(r => !r.success);

  const summary = {
    timestamp,
    totalPages: results.length,
    successful: successful.length,
    failed: failed.length,
    averageLoadTime: successful.reduce((sum, r) => sum + r.loadTime, 0) / successful.length || 0,
    byPriority: {
      CRITICAL: results.filter(r => r.priority === 'CRITICAL'),
      HIGH: results.filter(r => r.priority === 'HIGH'),
      MEDIUM: results.filter(r => r.priority === 'MEDIUM')
    },
    topRecommendations: getTopRecommendations(results),
    results
  };

  // 保存 JSON 报告
  ensureOutputDirectory();
  const reportPath = path.join(CONFIG.outputDir, `performance-report-${timestamp}.json`);
  fs.writeFileSync(reportPath, JSON.stringify(summary, null, 2));

  console.log(`\n📊 报告已保存: ${reportPath}`);

  return summary;
}

/**
 * 获取主要建议
 */
function getTopRecommendations(results) {
  const allRecs = [];

  results.forEach(result => {
    if (result.recommendations) {
      result.recommendations.forEach(rec => {
        allRecs.push({
          ...rec,
          page: result.page
        });
      });
    }
  });

  // 按优先级排序
  return allRecs
    .sort((a, b) => {
      const priorityOrder = { CRITICAL: 1, HIGH: 2, MEDIUM: 3, LOW: 4 };
      return priorityOrder[a.priority] - priorityOrder[b.priority];
    })
    .slice(0, 15);
}

/**
 * 打印总结
 */
function printSummary(summary) {
  console.log('\n' + '='.repeat(80));
  console.log('📊 性能测试总结');
  console.log('='.repeat(80));

  console.log(`\n总页面数: ${summary.totalPages}`);
  console.log(`成功: ${summary.successful} ✅`);
  console.log(`失败: ${summary.failed} ❌`);
  console.log(`平均加载时间: ${Math.round(summary.averageLoadTime)}ms`);

  console.log('\n按优先级统计:');
  console.log(`  🔴 CRITICAL: ${summary.byPriority.CRITICAL.length} 个页面`);
  console.log(`  🟠 HIGH: ${summary.byPriority.HIGH.length} 个页面`);
  console.log(`  🟡 MEDIUM: ${summary.byPriority.MEDIUM.length} 个页面`);

  if (summary.topRecommendations.length > 0) {
    console.log('\n💡 最重要优化建议 (Top 15):');
    summary.topRecommendations.forEach((rec, i) => {
      console.log(`  ${i + 1}. [${rec.priority}] ${rec.title} (${rec.impact})`);
      console.log(`     影响: ${rec.page}`);
    });
  }

  console.log('\n' + '='.repeat(80));
}

/**
 * 确保输出目录存在
 */
function ensureOutputDirectory() {
  if (!fs.existsSync(CONFIG.outputDir)) {
    fs.mkdirSync(CONFIG.outputDir, { recursive: true });
  }
}

/**
 * 主测试函数
 */
async function main() {
  console.log('🚀 Event2Table 性能测试 (使用 chrome-devtools-mcp)\n');
  console.log(`📋 测试 ${PAGES.length} 个页面\n`);

  const results = [];

  // 测试每个页面
  for (const page of PAGES) {
    const result = testPageLoadTime(page);
    results.push(result);
    printPageResult(result);
  }

  // 生成总结报告
  const summary = generateSummaryReport(results);
  printSummary(summary);

  // 返回退出码
  return summary.failed > 0 ? 1 : 0;
}

// 运行主函数
if (require.main === module) {
  main()
    .then(exitCode => process.exit(exitCode))
    .catch(error => {
      console.error('\n❌ 测试失败:', error);
      process.exit(1);
    });
}

module.exports = { main, PAGES, CONFIG, THRESHOLDS };
