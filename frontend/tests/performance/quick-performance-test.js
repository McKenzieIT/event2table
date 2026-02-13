#!/usr/bin/env node

/**
 * Event2Table 快速性能测试
 * 直接使用 HTTP 客户端测试页面加载时间
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

// 配置
const CONFIG = {
  baseURL: 'http://localhost:5173',
  timeout: 10000,
  retries: 2
};

// 页面配置
const PAGES = [
  {
    name: 'Dashboard',
    url: '/',
    priority: 'CRITICAL',
    type: 'dashboard',
    description: '主仪表板 - 应用程序入口点',
    expectedLoadTime: 2000,
    features: ['统计卡片', '导航菜单', '快速访问链接']
  },
  {
    name: 'Canvas',
    url: '/#/canvas',
    priority: 'CRITICAL',
    type: 'canvas',
    description: 'Canvas 流程画布 - 核心功能',
    expectedLoadTime: 2500,
    features: ['节点拖拽', '连接线绘制', '实时预览', '缩放功能']
  },
  {
    name: 'Games',
    url: '/#/games',
    priority: 'HIGH',
    type: 'list',
    description: '游戏管理列表',
    expectedLoadTime: 1500,
    features: ['数据表格', '分页', '搜索过滤', '排序']
  },
  {
    name: 'Events',
    url: '/#/events',
    priority: 'HIGH',
    type: 'list',
    description: '事件管理列表',
    expectedLoadTime: 1500,
    features: ['数据表格', '分类筛选', '参数查看', '批量操作']
  }
];

/**
 * 测量页面加载时间
 */
function measurePageLoadTime(url) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    const fullURL = `${CONFIG.baseURL}${url}`;

    const options = {
      method: 'GET',
      timeout: CONFIG.timeout
    };

    const req = http.request(fullURL, options, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        const loadTime = Date.now() - startTime;
        resolve({
          loadTime,
          statusCode: res.statusCode,
          contentLength: data.length,
          headers: res.headers
        });
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    req.setTimeout(CONFIG.timeout, () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });

    req.end();
  });
}

/**
 * 生成优化建议
 */
function generateRecommendations(page, result) {
  const recommendations = [];
  const { loadTime, statusCode } = result;

  // 检查页面是否成功加载
  if (statusCode !== 200) {
    recommendations.push({
      priority: 'CRITICAL',
      title: '页面加载失败',
      description: `HTTP 状态码: ${statusCode}`,
      solution: '检查路由配置和组件导入'
    });
    return recommendations;
  }

  // 基于加载时间的建议
  if (loadTime > page.expectedLoadTime * 2) {
    recommendations.push({
      priority: 'CRITICAL',
      title: '加载时间严重超标',
      description: `当前 ${loadTime}ms 远超目标 ${page.expectedLoadTime}ms`,
      solution: '实现代码分割和懒加载',
      code: `const Dashboard = React.lazy(() => import('./Dashboard'));`,
      impact: '40-50% 改善'
    });
  } else if (loadTime > page.expectedLoadTime * 1.5) {
    recommendations.push({
      priority: 'HIGH',
      title: '加载时间过长',
      description: `当前 ${loadTime}ms 超出目标 ${page.expectedLoadTime}ms ${(Math.round((loadTime - page.expectedLoadTime) / page.expectedLoadTime * 100))}%`,
      solution: '优化初始加载资源',
      code: `<link rel="preload" href="/critical.css" as="style">`,
      impact: '20-30% 改善'
    });
  } else if (loadTime > page.expectedLoadTime) {
    recommendations.push({
      priority: 'MEDIUM',
      title: '加载时间略慢',
      description: `当前 ${loadTime}ms 略超目标 ${page.expectedLoadTime}ms`,
      solution: '优化资源加载顺序',
      impact: '10-15% 改善'
    });
  } else {
    recommendations.push({
      priority: 'LOW',
      title: '加载时间良好',
      description: `当前 ${loadTime}ms 符合预期 (<${page.expectedLoadTime}ms)`,
      solution: '保持当前优化',
      impact: '0-5% 改善'
    });
  }

  // 基于页面类型的特定建议
  if (page.type === 'dashboard') {
    recommendations.push({
      priority: 'HIGH',
      title: '实现代码分割',
      description: 'Dashboard 包含多个统计卡片，应该按路由分割代码',
      code: `const Dashboard = React.lazy(() => import('./pages/Dashboard'));`,
      impact: '30-40% 改善'
    });

    recommendations.push({
      priority: 'MEDIUM',
      title: '懒加载统计卡片',
      description: '非关键组件应该延迟加载',
      code: `const StatsCard = React.lazy(() => import('./StatsCard'));`,
      impact: '15-20% 改善'
    });
  }

  if (page.type === 'canvas') {
    recommendations.push({
      priority: 'CRITICAL',
      title: '实现节点虚拟化',
      description: 'Canvas 包含大量节点，使用虚拟化只渲染可见节点',
      code: `import { FixedSizeList } from 'react-window';<FixedSizeList itemCount={1000} itemSize={50} />`,
      impact: '40-50% 改善'
    });

    recommendations.push({
      priority: 'HIGH',
      title: '使用 React.memo 优化节点组件',
      description: '避免不必要的重渲染',
      code: `const CanvasNode = React.memo(({ data, onDrag }) => { ... });`,
      impact: '20-30% 改善'
    });
  }

  if (page.type === 'list') {
    recommendations.push({
      priority: 'HIGH',
      title: '实现虚拟滚动',
      description: '大数据列表应该使用虚拟滚动，只渲染可见项',
      code: `import { VariableSizeList as List } from 'react-window';<List height={600} itemCount={10000} itemSize={50} />`,
      impact: '50-60% 改善'
    });

    recommendations.push({
      priority: 'MEDIUM',
      title: '使用 React Query 缓存',
      description: '列表数据应该被缓存，避免重复请求',
      code: `const { data } = useQuery(['games'], fetchGames, { staleTime: 5 * 60 * 1000 });`,
      impact: '30-40% 改善'
    });
  }

  return recommendations.slice(0, 3); // 最多返回 3 条建议
}

/**
 * 打印页面结果
 */
function printPageResult(page, result, recommendations) {
  const { loadTime, statusCode } = result;
  const status = statusCode === 200 ? '✅' : '❌';

  console.log(`\n${status} ${page.name} (${page.priority})`);
  console.log(`   URL: ${page.url}`);
  console.log(`   描述: ${page.description}`);
  console.log(`   性能: ${loadTime}ms (目标: <${page.expectedLoadTime}ms)`);

  if (recommendations.length > 0) {
    console.log(`\n   💡 ${recommendations.length} 条优化建议:`);
    recommendations.forEach((rec, i) => {
      console.log(`      ${i + 1}. [${rec.priority}] ${rec.title}`);
      console.log(`         → ${rec.description}`);
      if (rec.code) {
        console.log(`         💡 ${rec.code}`);
      }
      console.log(`         📊 预期改善: ${rec.impact}`);
    });
  }
}

/**
 * 生成汇总报告
 */
function generateSummaryReport(results) {
  const timestamp = new Date().toISOString();
  const successful = results.filter(r => r.statusCode === 200);
  const failed = results.filter(r => r.statusCode !== 200);

  const summary = {
    timestamp,
    baseURL: CONFIG.baseURL,
    totalPages: results.length,
    successful: successful.length,
    failed: failed.length,
    averageLoadTime: successful.reduce((sum, r) => sum + r.loadTime, 0) / successful.length || 0,
    pages: results.map(r => ({
      name: r.page.name,
      url: r.page.url,
      loadTime: r.loadTime,
      statusCode: r.statusCode,
      success: r.statusCode === 200,
      expectedLoadTime: r.page.expectedLoadTime,
      withinTarget: r.loadTime <= r.page.expectedLoadTime,
      recommendations: r.recommendations
    })),
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
        if (!recCount[rec.title]) {
          recCount[rec.title] = {
            title: rec.title,
            count: 0,
            pages: [],
            priority: rec.priority,
            impact: rec.impact || 'N/A'
          };
        }
        recCount[rec.title].count++;
        recCount[rec.title].pages.push(result.page.name);
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
  console.log('\n' + '='.repeat(80));
  console.log('📊 Event2Table 性能测试总结');
  console.log('='.repeat(80));

  console.log(`\n测试时间: ${new Date(summary.timestamp).toLocaleString('zh-CN')}`);
  console.log(`测试地址: ${summary.baseURL}`);
  console.log(`总页面数: ${summary.totalPages}`);
  console.log(`成功: ${summary.successful} ✅`);
  console.log(`失败: ${summary.failed} ❌`);
  console.log(`平均加载时间: ${Math.round(summary.averageLoadTime)}ms`);

  console.log('\n按优先级统计:');
  console.log(`  🔴 CRITICAL: ${summary.pages.filter(p => p.page.priority === 'CRITICAL').length} 个页面`);
  console.log(`  🟠 HIGH: ${summary.pages.filter(p => p.page.priority === 'HIGH').length} 个页面`);
  console.log(`  🟡 MEDIUM: ${summary.pages.filter(p => p.page.priority === 'MEDIUM').length} 个页面`);
  console.log(`  🟢 LOW: ${summary.pages.filter(p => p.page.priority === 'LOW').length} 个页面`);

  if (summary.topRecommendations.length > 0) {
    console.log('\n💡 最重要优化建议 (Top 10):');
    summary.topRecommendations.forEach((rec, i) => {
      console.log(`\n  ${i + 1}. ${rec.title} [${rec.priority}]`);
      console.log(`     影响: ${rec.count} 个页面`);
      console.log(`     页面: ${rec.pages.slice(0, 3).join(', ')}${rec.pages.length > 3 ? '...' : ''}`);
      if (rec.impact) {
        console.log(`     预期改善: ${rec.impact}`);
      }
    });
  }

  console.log('\n' + '='.repeat(80));
}

/**
 * 保存 JSON 报告
 */
function saveJSONReport(summary) {
  const outputDir = './test_results/performance';

  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const reportPath = path.join(outputDir, `performance-report-${timestamp}.json`);

  fs.writeFileSync(reportPath, JSON.stringify(summary, null, 2));
  console.log(`\n📄 JSON 报告已保存: ${reportPath}`);

  return reportPath;
}

/**
 * 主函数
 */
async function main() {
  console.log('🚀 Event2Table 性能测试\n');
  console.log(`📍 测试地址: ${CONFIG.baseURL}`);
  console.log(`📋 测试页面数: ${PAGES.length}\n`);

  const results = [];

  // 测试每个页面
  for (const page of PAGES) {
    let result;
    let attempts = 0;

    while (attempts < CONFIG.retries) {
      attempts++;
      try {
        const measurement = await measurePageLoadTime(page.url);
        result = {
          page,
          result: measurement,
          success: measurement.statusCode === 200,
          attempts,
          recommendations: generateRecommendations(page, measurement)
        };
        break;
      } catch (error) {
        console.log(`   ⚠️  重试 ${attempts}/${CONFIG.retries} 失败: ${error.message}`);

        if (attempts >= CONFIG.retries) {
          result = {
            page,
            result: { loadTime: 0, statusCode: 0 },
            success: false,
            attempts,
            error: error.message,
            recommendations: [{
              priority: 'CRITICAL',
              title: '页面加载失败',
              description: error.message,
              solution: '检查服务器是否运行'
            }]
          };
        }

        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }

    results.push(result);
    printPageResult(page, result.result, result.recommendations);
  }

  // 生成总结报告
  const summary = generateSummaryReport(results);
  printSummary(summary);

  // 保存报告
  saveJSONReport(summary);

  // 退出码
  const exitCode = summary.failed > 0 ? 1 : 0;
  process.exit(exitCode);
}

// 运行测试
if (require.main === module) {
  main().catch(error => {
    console.error('\n❌ 测试运行失败:', error);
    process.exit(1);
  });
}

module.exports = { main, PAGES, CONFIG };
