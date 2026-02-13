#!/usr/bin/env node

/**
 * Event2Table 页面性能测试 - 使用 chrome-devtools-mcp
 * 直接测量每个页面的实际性能并提供优化建议
 */

const chromium = require('chrome-devtools-mcp');

// 配置
const BASE_URL = 'http://localhost:5173';

// 页面配置（按优先级排序）
const PAGES = [
  {
    name: 'Dashboard',
    url: '/',
    priority: 'CRITICAL',
    type: 'dashboard',
    description: '主仪表板',
    features: ['统计卡片', '导航', '快速访问'],
    expectedLoadTime: 2000,
    recommendations: []
  },
  {
    name: 'Canvas',
    url: '/#/canvas',
    priority: 'CRITICAL',
    type: 'canvas',
    description: '流程画布',
    features: ['拖拽', '节点编辑', '实时预览'],
    expectedLoadTime: 2500,
    recommendations: []
  },
  {
    name: 'EventNodeBuilder',
    url: '/#/event-node-builder',
    priority: 'CRITICAL',
    type: 'builder',
    description: '事件节点构建器',
    features: ['表单验证', '字段编辑'],
    expectedLoadTime: 2500,
    recommendations: []
  },
  {
    name: 'Games',
    url: '/#/games',
    priority: 'HIGH',
    type: 'list',
    description: '游戏列表',
    features: ['表格', '分页', '搜索'],
    expectedLoadTime: 2000,
    recommendations: []
  },
  {
    name: 'Events',
    url: '/#/events',
    priority: 'HIGH',
    type: 'list',
    description: '事件列表',
    features: ['表格', '分类'],
    expectedLoadTime: 2000,
    recommendations: []
  },
  {
    name: 'Parameters',
    url: '/#/parameters',
    priority: 'HIGH',
    type: 'list',
    description: '参数列表',
    features: ['表格', '批量操作'],
    expectedLoadTime: 2000,
    recommendations: []
  },
  {
    name: 'FieldBuilder',
    url: '/#/field-builder',
    priority: 'MEDIUM',
    type: 'builder',
    description: '字段构建器',
    features: ['HQL预览', '字段配置'],
    expectedLoadTime: 2500,
    recommendations: []
  },
  {
    name: 'Categories',
    url: '/#/categories',
    priority: 'MEDIUM',
    type: 'list',
    description: '分类管理',
    features: ['树形结构'],
    expectedLoadTime: 2000,
    recommendations: []
  },
  {
    name: 'Flows',
    url: '/#/flows',
    priority: 'MEDIUM',
    type: 'list',
    description: '流程列表',
    features: ['状态跟踪'],
    expectedLoadTime: 2000,
    recommendations: []
  },
  {
    name: 'HqlManage',
    url: '/#/hql-manage',
    priority: 'MEDIUM',
    type: 'management',
    description: 'HQL 管理',
    features: ['历史记录', '版本对比'],
    expectedLoadTime: 2500,
    recommendations: []
  }
];

/**
 * 测量页面性能
 */
async function measurePagePerformance(page) {
  const fullURL = `${BASE_URL}${page.url}`;
  console.log(`\n🔍 测试: ${page.name} (${page.priority})`);
  console.log(`   URL: ${fullURL}`);

  try {
    // 导航到页面
    const startTime = Date.now();
    await chromium.navigate(fullURL);

    // 等待页面完全加载
    await chromium.waitForLoad('networkidle');

    // 获取实际加载时间
    const loadTime = Date.now() - startTime;

    // 尝试获取性能指标（如果支持）
    let metrics = { loadTime };

    try {
      // 获取页面标题（验证加载成功）
      const title = await chromium.evaluate('document.title');
      metrics.title = title;

      // 检查是否有错误
      const consoleErrors = await chromium.getConsoleLogs();
      metrics.errorCount = consoleErrors.filter(log => log.level === 'error').length;

      // 检查资源数量
      const resourceInfo = await chromium.evaluate(`
        ({
          scripts: document.querySelectorAll('script').length,
          links: document.querySelectorAll('link').length,
          images: document.querySelectorAll('img').length
        })
      `);
      metrics.resources = resourceInfo;

    } catch (e) {
      // 如果不支持高级指标，只使用基本加载时间
      console.log(`   ⚠️  性能指标部分可用`);
    }

    return {
      ...page,
      metrics,
      success: true
    };

  } catch (error) {
    console.log(`   ❌ 错误: ${error.message}`);
    return {
      ...page,
      metrics: { loadTime: 0 },
      success: false,
      error: error.message
    };
  }
}

/**
 * 生成优化建议
 */
function generateRecommendations(page, metrics) {
  const recommendations = [];
  const { loadTime, errorCount, resources } = metrics;

  // 基于加载时间的建议
  if (loadTime > page.expectedLoadTime * 1.5) {
    recommendations.push({
      priority: 'CRITICAL',
      action: '加载时间过长',
      description: `当前 ${loadTime}ms，建议 <${page.expectedLoadTime}ms`,
      solution: '实现代码分割和懒加载'
    });
  } else if (loadTime > page.expectedLoadTime) {
    recommendations.push({
      priority: 'HIGH',
      action: '加载时间略慢',
      description: `当前 ${loadTime}ms，目标 ${page.expectedLoadTime}ms`,
      solution: '优化初始加载资源'
    });
  }

  // 基于错误数量的建议
  if (errorCount > 0) {
    recommendations.push({
      priority: 'CRITICAL',
      action: '控制台错误',
      description: `发现 ${errorCount} 个错误`,
      solution: '修复组件导入和依赖问题'
    });
  }

  // 基于页面类型的建议
  switch (page.type) {
    case 'dashboard':
      recommendations.push({
        priority: 'MEDIUM',
        action: '实现 React Query',
        description: '仪表板数据应该被缓存',
        solution: 'const { data } = useQuery(["dashboard"], fetchDashboard);'
      });
      recommendations.push({
        priority: 'MEDIUM',
        action: '懒加载统计卡片',
        description: '非关键组件应该延迟加载',
        solution: 'const StatsCard = React.lazy(() => import("./StatsCard"));'
      });
      break;

    case 'canvas':
      recommendations.push({
        priority: 'HIGH',
        action: '优化节点渲染',
        description: '使用 React.memo 减少重渲染',
        solution: 'const CanvasNode = React.memo(({ data }) => { ... });'
      });
      recommendations.push({
        priority: 'MEDIUM',
        action: '实现虚拟滚动',
        description: '大量节点使用虚拟滚动',
        solution: '使用 react-window 或 react-virtualized'
      });
      recommendations.push({
        priority: 'HIGH',
        action: '防抖拖拽事件',
        description: '减少拖拽时的计算频率',
        solution: 'const debouncedDrag = debounce(handleDrag, 16);'
      });
      break;

    case 'list':
      recommendations.push({
        priority: 'HIGH',
        action: '实现虚拟化列表',
        description: '长列表应该使用虚拟滚动',
        solution: '<FixedSizeList itemCount={1000} itemSize={50} />'
      });
      recommendations.push({
        priority: 'MEDIUM',
        action: '添加数据分页',
        description: '服务器端分页减少数据量',
        solution: 'usePagination({ pageSize: 50 })'
      });
      break;

    case 'builder':
      recommendations.push({
        priority: 'MEDIUM',
        action: '添加骨架屏',
        description: '提升表单加载感知性能',
        solution: '<Skeleton loading={isLoading} />'
      });
      recommendations.push({
        priority: 'MEDIUM',
        action: '使用防抖验证',
        description: '减少输入验证频率',
        solution: 'const validateField = debounce(checkField, 300);'
      });
      break;
  }

  return recommendations;
}

/**
 * 打印页面结果
 */
function printPageResult(result) {
  const { name, priority, metrics, success, error } = result;
  const status = success ? '✅' : '❌';

  console.log(`${status} ${name} (${priority})`);

  if (success) {
    const score = metrics.loadTime <= result.expectedLoadTime ? '🟢 优秀' :
                 metrics.loadTime <= result.expectedLoadTime * 1.5 ? '🟡 良好' : '🔴 需优化';

    console.log(`   ${score}`);
    console.log(`   ⏱️  加载时间: ${metrics.loadTime}ms (目标: <${result.expectedLoadTime}ms)`);

    if (metrics.title) {
      console.log(`   📄 页面标题: ${metrics.title}`);
    }

    if (metrics.errorCount !== undefined) {
      console.log(`   🐛 错误数量: ${metrics.errorCount}`);
    }

    if (metrics.resources) {
      console.log(`   📦 资源: JS(${metrics.resources.scripts}) CSS(${metrics.resources.links}) IMG(${metrics.resources.images})`);
    }

    // 显示建议
    if (result.recommendations.length > 0) {
      console.log(`\n   💡 ${result.recommendations.length} 条优化建议:`);
      result.recommendations.slice(0, 3).forEach((rec, i) => {
        console.log(`      ${i + 1}. [${rec.priority}] ${rec.action}`);
        console.log(`         ${rec.description}`);
        console.log(`         💡 ${rec.solution}`);
      });
    }
  } else {
    console.log(`   ❌ 错误: ${error}`);
  }
}

/**
 * 生成汇总报告
 */
function generateSummaryReport(results) {
  const successful = results.filter(r => r.success);
  const failed = results.filter(r => !r.success);

  const summary = {
    total: results.length,
    successful: successful.length,
    failed: failed.length,
    averageLoadTime: successful.reduce((sum, r) => sum + r.metrics.loadTime, 0) / successful.length || 0,
    byPriority: {
      CRITICAL: results.filter(r => r.priority === 'CRITICAL'),
      HIGH: results.filter(r => r.priority === 'HIGH'),
      MEDIUM: results.filter(r => r.priority === 'MEDIUM'),
      LOW: results.filter(r => r.priority === 'LOW')
    },
    topRecommendations: getTopRecommendations(results)
  };

  return summary;
}

/**
 * 获取最常见建议
 */
function getTopRecommendations(results) {
  const recCount = {};

  results.forEach(result => {
    if (result.recommendations) {
      result.recommendations.forEach(rec => {
        if (!recCount[rec.action]) {
          recCount[rec.action] = {
            ...rec,
            count: 0,
            pages: []
          };
        }
        recCount[rec.action].count++;
        recCount[rec.action].pages.push(result.name);
      });
    }
  });

  return Object.values(recCount)
    .sort((a, b) => b.count - a.count)
    .slice(0, 10);
}

/**
 * 打印总结
 */
function printSummary(summary) {
  console.log('\n' + '='.repeat(70));
  console.log('📊 性能测试总结');
  console.log('='.repeat(70));

  console.log(`\n总页面数: ${summary.total}`);
  console.log(`✅ 成功: ${summary.successful}`);
  console.log(`❌ 失败: ${summary.failed}`);
  console.log(`⏱️  平均加载时间: ${Math.round(summary.averageLoadTime)}ms`);

  console.log('\n按优先级统计:');
  console.log(`  🔴 CRITICAL: ${summary.byPriority.CRITICAL.length} 个页面`);
  console.log(`  🟠 HIGH: ${summary.byPriority.HIGH.length} 个页面`);
  console.log(`  🟡 MEDIUM: ${summary.byPriority.MEDIUM.length} 个页面`);
  console.log(`  🟢 LOW: ${summary.byPriority.LOW.length} 个页面`);

  if (summary.topRecommendations.length > 0) {
    console.log('\n🔥 最常见优化建议:');
    summary.topRecommendations.slice(0, 5).forEach((rec, i) => {
      console.log(`\n  ${i + 1}. ${rec.action} [${rec.priority}]`);
      console.log(`     影响: ${rec.count} 个页面`);
      console.log(`     页面: ${rec.pages.slice(0, 3).join(', ')}${rec.pages.length > 3 ? '...' : ''}`);
      console.log(`     💡 ${rec.solution}`);
    });
  }

  console.log('\n' + '='.repeat(70));
}

/**
 * 主函数
 */
async function main() {
  console.log('🚀 Event2Table 页面性能测试');
  console.log(`🌐 测试地址: ${BASE_URL}`);
  console.log(`📋 测试页面数: ${PAGES.length}`);

  const results = [];

  for (const page of PAGES) {
    const measured = await measurePagePerformance(page);
    measured.recommendations = generateRecommendations(measured, measured.metrics);
    results.push(measured);
    printPageResult(measured);

    // 等待一下再测试下一个页面
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  // 生成总结
  const summary = generateSummaryReport(results);
  printSummary(summary);

  // 保存结果
  const outputDir = './test_results/performance';
  if (!require('fs').existsSync(outputDir)) {
    require('fs').mkdirSync(outputDir, { recursive: true });
  }

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const reportPath = `${outputDir}/performance-report-${timestamp}.json`;
  require('fs').writeFileSync(reportPath, JSON.stringify({
    timestamp: new Date().toISOString(),
    summary,
    results
  }, null, 2));

  console.log(`\n📄 报告已保存: ${reportPath}`);

  process.exit(summary.failed > 0 ? 1 : 0);
}

// 运行测试
if (require.main === module) {
  main().catch(error => {
    console.error('\n❌ 测试失败:', error);
    process.exit(1);
  });
}

module.exports = { main, PAGES, generateRecommendations };
