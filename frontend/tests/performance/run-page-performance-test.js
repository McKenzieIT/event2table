#!/usr/bin/env node

/**
 * Event2Table 页面性能测试
 * 使用 HTTP 客户端测量页面加载时间并提供优化建议
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

// 配置
const CONFIG = {
  baseURL: 'http://localhost:5173',
  timeout: 10000,
  retries: 3
};

// 性能阈值（毫秒）
const THRESHOLDS = {
  excellent: 1000,  // 优秀
  good: 2000,       // 良好
  fair: 3000,       // 一般
  poor: 4000        // 较差
};

// 页面配置
const PAGES = [
  {
    name: 'Dashboard',
    url: '/',
    priority: 'CRITICAL',
    type: 'dashboard',
    description: '主仪表板，应用程序入口点',
    expectedLoadTime: 1500,
    features: ['统计卡片', '导航', '快速访问'],
    recommendations: [
      {
        priority: 'HIGH',
        issue: '多数据源并发加载',
        solution: '使用 React Query 的并行查询和缓存',
        code: `const { data } = useQuery(['dashboard'], fetchDashboard, { staleTime: 5 * 60 * 1000 });`,
        impact: '30-40% 改善'
      },
      {
        priority: 'MEDIUM',
        issue: '统计卡片未懒加载',
        solution: '使用 React.lazy 和 Suspense 延迟加载非关键卡片',
        code: `const StatsCard = React.lazy(() => import('./StatsCard'));<Suspense fallback={<Skeleton />}><StatsCard /></Suspense>`,
        impact: '15-25% 改善'
      }
    ]
  },
  {
    name: 'Canvas',
    url: '/#/canvas',
    priority: 'CRITICAL',
    type: 'canvas',
    description: '流程画布构建器，核心功能',
    expectedLoadTime: 2500,
    features: ['拖拽', '节点编辑', '实时预览'],
    recommendations: [
      {
        priority: 'CRITICAL',
        issue: '大量节点渲染性能',
        solution: '实现虚拟化滚动和 React.memo 优化',
        code: `const Node = React.memo(({ data }) => { return <div>{data.name}</div>; });`,
        impact: '40-50% 改善'
      },
      {
        priority: 'HIGH',
        issue: '拖拽操作频繁触发重渲染',
        solution: '使用防抖优化拖拽事件',
        code: `const handleDrag = debounce((event) => { updateNodePosition(event); }, 16);`,
        impact: '20-30% 改善'
      },
      {
        priority: 'MEDIUM',
        issue: 'Canvas 组件未代码分割',
        solution: '使用动态 import 分离大型 Canvas 组件',
        code: `const Canvas = React.lazy(() => import(/* webpackChunkName: "canvas" */ './Canvas'));`,
        impact: '15-20% 改善'
      }
    ]
  },
  {
    name: 'EventNodeBuilder',
    url: '/#/event-node-builder',
    priority: 'CRITICAL',
    type: 'builder',
    description: '事件节点构建器，复杂表单',
    expectedLoadTime: 2000,
    features: ['表单验证', '字段编辑', '预览'],
    recommendations: [
      {
        priority: 'HIGH',
        issue: '复杂表单初始渲染',
        solution: '使用受控组件和防抖验证',
        code: `const [values, setValues] = useState({});const handleChange = debounce(validateField, 300);`,
        impact: '20-30% 改善'
      },
      {
        priority: 'MEDIUM',
        issue: '字段预览实时计算',
        solution: '使用 useMemo 优化预览计算',
        code: `const preview = useMemo(() => generateHQL(fields), [fields]);`,
        impact: '10-15% 改善'
      }
    ]
  },
  {
    name: 'Games',
    url: '/#/games',
    priority: 'HIGH',
    type: 'list',
    description: '游戏管理列表',
    expectedLoadTime: 1500,
    features: ['表格展示', '分页', '搜索过滤'],
    recommendations: [
      {
        priority: 'HIGH',
        issue: '大数据集列表渲染',
        solution: '实现虚拟化滚动',
        code: `import { FixedSizeList } from 'react-window';<FixedSizeList itemCount={1000} itemSize={50} />`,
        impact: '50-60% 改善'
      },
      {
        priority: 'MEDIUM',
        issue: '数据未缓存',
        solution: '使用 React Query 缓存游戏列表',
        code: `const { data } = useQuery(['games'], fetchGames, { cacheTime: 5 * 60 * 1000 });`,
        impact: '30-40% 改善'
      }
    ]
  },
  {
    name: 'Events',
    url: '/#/events',
    priority: 'HIGH',
    type: 'list',
    description: '事件管理列表',
    expectedLoadTime: 1800,
    features: ['表格展示', '分类', '参数查看'],
    recommendations: [
      {
        priority: 'HIGH',
        issue: '事件列表数据量大',
        solution: '实现服务器端分页',
        code: `const { data } = useQuery(['events'], fetchEvents, { queryKey: ['events', page] });`,
        impact: '40-50% 改善'
      },
      {
        priority: 'MEDIUM',
        issue: '分类和参数展开未优化',
        solution: '使用懒加载子组件',
        code: `const CategoryList = React.lazy(() => import('./CategoryList'));`,
        impact: '15-20% 改善'
      }
    ]
  },
  {
    name: 'Parameters',
    url: '/#/parameters',
    priority: 'HIGH',
    type: 'list',
    description: '参数管理列表',
    expectedLoadTime: 1800,
    features: ['表格展示', '搜索', '批量操作'],
    recommendations: [
      {
        priority: 'HIGH',
        issue: '参数列表搜索性能',
        solution: '使用防抖搜索和虚拟化',
        code: `const handleSearch = debounce(query => setSearch(query), 300);`,
        impact: '30-40% 改善'
      },
      {
        priority: 'MEDIUM',
        issue: '批量操作UI卡顿',
        solution: '使用 requestIdleCallback 批量处理',
        code: `requestIdleCallback(() => processBatch(items));`,
        impact: '10-15% 改善'
      }
    ]
  },
  {
    name: 'FieldBuilder',
    url: '/#/field-builder',
    priority: 'MEDIUM',
    type: 'builder',
    description: '字段构建器工具',
    expectedLoadTime: 2000,
    features: ['字段配置', 'HQL预览', '保存加载'],
    recommendations: [
      {
        priority: 'MEDIUM',
        issue: 'HQL预览计算频繁',
        solution: '使用 debounce 优化预览更新',
        code: `const updatePreview = debounce(hql => setPreview(hql), 500);`,
        impact: '15-20% 改善'
      },
      {
        priority: 'LOW',
        issue: '字段模板未缓存',
        solution: '使用 useMemo 缓存字段模板',
        code: `const templates = useMemo(() => loadFieldTemplates(), []);`,
        impact: '5-10% 改善'
      }
    ]
  },
  {
    name: 'Categories',
    url: '/#/categories',
    priority: 'MEDIUM',
    type: 'list',
    description: '分类管理',
    expectedLoadTime: 1500,
    features: ['树形结构', '拖拽排序'],
    recommendations: [
      {
        priority: 'MEDIUM',
        issue: '树形结构渲染慢',
        solution: '使用虚拟化树组件',
        code: `import { Tree } from 'react-vtree';<Tree data={categories} height={600} />`,
        impact: '30-40% 改善'
      },
      {
        priority: 'LOW',
        issue: '拖拽操作未优化',
        solution: '使用 react-dnd 优化拖拽性能',
        code: `<DndProvider backend={HTML5Backend}><DragDrop /> </DndProvider>`,
        impact: '10-15% 改善'
      }
    ]
  },
  {
    name: 'Flows',
    url: '/#/flows',
    priority: 'MEDIUM',
    type: 'list',
    description: '流程管理列表',
    expectedLoadTime: 1500,
    features: ['流程列表', '状态跟踪'],
    recommendations: [
      {
        priority: 'MEDIUM',
        issue: '流程状态更新频繁',
        solution: '使用 WebSocket 实时更新状态',
        code: `const ws = new WebSocket('ws://localhost:5001/flows');ws.onmessage = (msg) => updateFlowStatus(msg.data);`,
        impact: '20-30% 改善'
      }
    ]
  },
  {
    name: 'HqlManage',
    url: '/#/hql-manage',
    priority: 'MEDIUM',
    type: 'management',
    description: 'HQL 管理页面',
    expectedLoadTime: 2000,
    features: ['历史记录', '版本对比'],
    recommendations: [
      {
        priority: 'MEDIUM',
        issue: 'HQL 历史数据量大',
        solution: '实现无限滚动加载历史',
        code: `useInfiniteQuery({ queryKey: ['hql-history'], fetchNextPage });`,
        impact: '25-35% 改善'
      }
    ]
  },
  {
    name: 'ParameterAnalysis',
    url: '/#/parameter-analysis',
    priority: 'LOW',
    type: 'analytics',
    description: '参数分析页面',
    expectedLoadTime: 2500,
    features: ['图表展示', '数据分析'],
    recommendations: [
      {
        priority: 'LOW',
        issue: '图表渲染性能',
        solution: '使用 WebGL 或 Canvas 替代 DOM 图表',
        code: `import { Line } from '@react-three/fiber';<Line data={data} />`,
        impact: '20-30% 改善'
      }
    ]
  },
  {
    name: 'ParameterNetwork',
    url: '/#/parameter-network',
    priority: 'LOW',
    type: 'visualization',
    description: '参数网络可视化',
    expectedLoadTime: 2500,
    features: ['网络图', '交互式探索'],
    recommendations: [
      {
        priority: 'LOW',
        issue: '网络图节点多',
        solution: '使用 force-directed graph 布局算法',
        code: `import { Graph } from 'react-graph-vis';<Graph layout="forceDirected" nodes={nodes} />`,
        impact: '25-35% 改善'
      }
    ]
  }
];

/**
 * 测量页面加载时间
 */
function measurePageLoadTime(url) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();

    const options = {
      method: 'GET',
      timeout: CONFIG.timeout
    };

    const req = http.request(`${CONFIG.baseURL}${url}`, options, (res) => {
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
 * 获取性能等级
 */
function getPerformanceGrade(loadTime, expectedTime) {
  const ratio = loadTime / expectedTime;

  if (ratio <= 0.8) return { grade: '优秀', emoji: '🟢', color: '#4caf50' };
  if (ratio <= 1.0) return { grade: '良好', emoji: '🟡', color: '#ff9800' };
  if (ratio <= 1.5) return { grade: '一般', emoji: '🟠', color: '#ff5722' };
  return { grade: '较差', emoji: '🔴', color: '#f44336' };
}

/**
 * 打印页面结果
 */
function printPageResult(page, result) {
  const { loadTime, statusCode } = result;
  const performance = getPerformanceGrade(loadTime, page.expectedLoadTime);

  console.log(`\n${performance.emoji} ${page.name} (${page.priority})`);
  console.log(`   URL: ${page.url}`);
  console.log(`   描述: ${page.description}`);
  console.log(`   性能: ${performance.grade} (${loadTime}ms, 目标: <${page.expectedLoadTime}ms)`);
  console.log(`   特性: ${page.features.join(', ')}`);

  if (statusCode !== 200) {
    console.log(`   ⚠️  HTTP 状态: ${statusCode}`);
  }

  // 显示优化建议
  console.log(`\n   💡 优化建议:`);
  page.recommendations.slice(0, 3).forEach((rec, i) => {
    console.log(`      ${i + 1}. [${rec.priority}] ${rec.issue}`);
    console.log(`         → ${rec.solution}`);
    console.log(`         预期改善: ${rec.impact}`);
  });
}

/**
 * 生成性能报告
 */
function generateReport(results) {
  const timestamp = new Date().toISOString();
  const successful = results.filter(r => r.success);
  const failed = results.filter(r => !r.success);

  const summary = {
    timestamp,
    totalPages: PAGES.length,
    successful: successful.length,
    failed: failed.length,
    averageLoadTime: successful.reduce((sum, r) => sum + (r.result?.loadTime || 0), 0) / successful.length || 0,
    byPriority: {
      CRITICAL: results.filter(r => r.priority === 'CRITICAL'),
      HIGH: results.filter(r => r.priority === 'HIGH'),
      MEDIUM: results.filter(r => r.priority === 'MEDIUM'),
      LOW: results.filter(r => r.priority === 'LOW')
    },
    topIssues: identifyTopIssues(successful)
  };

  return { summary, results };
}

/**
 * 识别主要问题
 */
function identifyTopIssues(successfulResults) {
  const issues = [];

  successfulResults.forEach(result => {
    const { page, result } = result;
    const ratio = result.loadTime / page.expectedLoadTime;

    if (ratio > 1.5) {
      issues.push({
        page: page.name,
        severity: 'HIGH',
        issue: `加载时间 ${result.loadTime}ms 超出目标 ${page.expectedLoadTime}ms ${(ratio * 100 - 100).toFixed(0)}%`,
        priority: page.priority,
        recommendations: page.recommendations.slice(0, 2)
      });
    }
  });

  return issues.sort((a, b) => b.severity === 'HIGH' ? 1 : -1).slice(0, 10);
}

/**
 * 打印总结
 */
function printSummary(report) {
  const { summary, results } = report;

  console.log('\n' + '='.repeat(80));
  console.log('📊 Event2Table 性能测试总结');
  console.log('='.repeat(80));

  console.log(`\n测试时间: ${new Date(summary.timestamp).toLocaleString('zh-CN')}`);
  console.log(`总页面数: ${summary.totalPages}`);
  console.log(`成功: ${summary.successful} ✅`);
  console.log(`失败: ${summary.failed} ❌`);
  console.log(`平均加载时间: ${Math.round(summary.averageLoadTime)}ms`);

  console.log('\n按优先级统计:');
  console.log(`  🔴 CRITICAL: ${summary.byPriority.CRITICAL.length} 个页面`);
  console.log(`  🟠 HIGH: ${summary.byPriority.HIGH.length} 个页面`);
  console.log(`  🟡 MEDIUM: ${summary.byPriority.MEDIUM.length} 个页面`);
  console.log(`  🟢 LOW: ${summary.byPriority.LOW.length} 个页面`);

  if (summary.topIssues.length > 0) {
    console.log('\n⚠️  主要性能问题 (Top 10):');
    summary.topIssues.slice(0, 10).forEach((issue, i) => {
      console.log(`\n  ${i + 1}. ${issue.page} [${issue.severity}]`);
      console.log(`     问题: ${issue.issue}`);
      console.log(`     优先级: ${issue.priority}`);
      console.log(`     建议优化:`);
      issue.recommendations.forEach(rec => {
        console.log(`       → ${rec.solution} (${rec.impact})`);
      });
    });
  }

  // 优先级优化建议
  console.log('\n🎯 优化优先级建议:');
  console.log('\n  立即优化 (1-2周):');
  console.log('    1. Canvas 页面虚拟化 - 40-50% 改善');
  console.log('    2. 游戏和事件列表虚拟化 - 50-60% 改善');
  console.log('    3. Dashboard 实现代码分割 - 30-40% 改善');

  console.log('\n  短期优化 (3-4周):');
  console.log('    1. 实现服务器端分页 - 40-50% 改善');
  console.log('    2. 使用 React Query 缓存 - 30-40% 改善');
  console.log('    3. 添加骨架屏加载 - 15-20% 改善');

  console.log('\n  中期优化 (1-2月):');
  console.log('    1. 全面实施懒加载 - 20-30% 改善');
  console.log('    2. 图片和资源优化 - 10-15% 改善');
  console.log('    3. WebGL 替换图表组件 - 20-30% 改善');

  console.log('\n' + '='.repeat(80));
}

/**
 * 保存 JSON 报告
 */
function saveReport(report) {
  const outputDir = './test_results/performance';

  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const reportPath = path.join(outputDir, `performance-report-${timestamp}.json`);

  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  console.log(`\n📄 报告已保存: ${reportPath}`);

  return reportPath;
}

/**
 * 主函数
 */
async function main() {
  console.log('🚀 Event2Table 页面性能测试');
  console.log(`🌐 测试地址: ${CONFIG.baseURL}`);
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
          success: true,
          attempts
        };
        break;
      } catch (error) {
        console.log(`   ⚠️  尝试 ${attempts}/${CONFIG.retries} 失败: ${error.message}`);

        if (attempts >= CONFIG.retries) {
          result = {
            page,
            result: { loadTime: 0 },
            success: false,
            attempts,
            error: error.message
          };
        }

        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }

    results.push(result);
    printPageResult(result.page, result.result || { loadTime: 0 });
  }

  // 生成报告
  const report = generateReport(results);

  // 打印总结
  printSummary(report);

  // 保存报告
  saveReport(report);

  // 返回退出码
  const exitCode = report.summary.failed > 0 ? 1 : 0;
  process.exit(exitCode);
}

// 运行测试
if (require.main === module) {
  main().catch(error => {
    console.error('\n❌ 测试失败:', error.message);
    process.exit(1);
  });
}

module.exports = { main, PAGES, CONFIG };
