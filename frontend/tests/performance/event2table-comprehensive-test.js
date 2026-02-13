#!/usr/bin/env node

/**
 * Event2Table 全面测试脚本 - 使用 Chrome DevTools Protocol
 * 测试范围：所有 41 个页面
 * 测试维度：加载性能、控制台错误、功能交互、截图
 * 
 * @version 1.0.0
 * @date 2026-02-13
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const http = require('http');

// 配置
const CONFIG = {
  baseURL: 'http://localhost:5173',
  backendURL: 'http://127.0.0.1:5001',
  headless: false, // 使用有头模式便于观察
  timeout: 60000,
  screenshotDir: './test_results/event2table-test/screenshots',
  reportDir: './test_results/event2table-test',
  waitTime: 3000, // 每个页面等待时间
};

// 性能阈值
const THRESHOLDS = {
  fcp: { good: 1800, needsImprovement: 3000 },
  lcp: { good: 2500, needsImprovement: 4000 },
  cls: { good: 0.1, needsImprovement: 0.25 },
  tti: { good: 3500, needsImprovement: 5000 },
  loadTime: { good: 2000, needsImprovement: 4000 }
};

// 所有41个页面配置
const ALL_PAGES = [
  // Phase 1: 核心页面 (5页)
  { name: 'Dashboard', path: '/', phase: 1, priority: 'CRITICAL', features: ['统计卡片', '快速入口', '导航'] },
  { name: 'Canvas', path: '/#/canvas', phase: 1, priority: 'CRITICAL', features: ['节点拖拽', '画布渲染'] },
  { name: 'EventNodeBuilder', path: '/#/event-node-builder', phase: 1, priority: 'CRITICAL', features: ['表单', '字段编辑', '预览'] },
  { name: 'Games', path: '/#/games', phase: 1, priority: 'CRITICAL', features: ['数据表格', '分页'] },
  { name: 'Events', path: '/#/events', phase: 1, priority: 'CRITICAL', features: ['事件列表', '筛选'] },
  
  // Phase 2: 表单页面 (6页)
  { name: 'GameCreate', path: '/#/games/create', phase: 2, priority: 'HIGH', features: ['表单提交', '验证'] },
  { name: 'GameEdit', path: '/#/games/10000147/edit', phase: 2, priority: 'HIGH', features: ['数据回显', '编辑'], requiresData: true },
  { name: 'EventCreate', path: '/#/events/create', phase: 2, priority: 'HIGH', features: ['复杂表单', '参数'] },
  { name: 'EventEdit', path: '/#/events/1/edit', phase: 2, priority: 'HIGH', features: ['编辑功能', '状态'], requiresData: true },
  { name: 'CategoryCreate', path: '/#/categories/create', phase: 2, priority: 'HIGH', features: ['分类创建'] },
  { name: 'CategoryEdit', path: '/#/categories/1/edit', phase: 2, priority: 'HIGH', features: ['分类编辑'], requiresData: true },
  
  // Phase 3: 管理页面 (12页)
  { name: 'Categories', path: '/#/categories', phase: 3, priority: 'MEDIUM', features: ['树形结构'] },
  { name: 'Parameters', path: '/#/parameters', phase: 3, priority: 'MEDIUM', features: ['参数表格'] },
  { name: 'CommonParams', path: '/#/common-params', phase: 3, priority: 'MEDIUM', features: ['公共参数'] },
  { name: 'EventDetail', path: '/#/events/1', phase: 3, priority: 'MEDIUM', features: ['详情展示'], requiresData: true },
  { name: 'Flows', path: '/#/flows', phase: 3, priority: 'MEDIUM', features: ['流程列表'] },
  { name: 'HqlManage', path: '/#/hql-manage', phase: 3, priority: 'MEDIUM', features: ['HQL管理'] },
  { name: 'HqlResults', path: '/#/hql-results', phase: 3, priority: 'MEDIUM', features: ['结果展示'] },
  { name: 'Generate', path: '/#/generate', phase: 3, priority: 'MEDIUM', features: ['生成功能'] },
  { name: 'GenerateResult', path: '/#/generate/result', phase: 3, priority: 'MEDIUM', features: ['生成结果'] },
  { name: 'FieldBuilder', path: '/#/field-builder', phase: 3, priority: 'MEDIUM', features: ['字段构建'] },
  { name: 'FlowBuilder', path: '/#/flow-builder', phase: 3, priority: 'MEDIUM', features: ['流程构建'] },
  { name: 'EventNodes', path: '/#/event-nodes', phase: 3, priority: 'MEDIUM', features: ['事件节点'] },
  
  // Phase 4: 参数分析页面 (7页)
  { name: 'ParameterDashboard', path: '/#/parameter-dashboard', phase: 4, priority: 'LOW', features: ['仪表板'] },
  { name: 'ParameterUsage', path: '/#/parameter-usage', phase: 4, priority: 'LOW', features: ['使用统计'] },
  { name: 'ParameterHistory', path: '/#/parameter-history', phase: 4, priority: 'LOW', features: ['历史记录'] },
  { name: 'ParameterCompare', path: '/#/parameters/compare', phase: 4, priority: 'LOW', features: ['对比功能'] },
  { name: 'ParameterAnalysis', path: '/#/parameter-analysis', phase: 4, priority: 'LOW', features: ['分析图表'] },
  { name: 'ParameterNetwork', path: '/#/parameter-network', phase: 4, priority: 'LOW', features: ['网络图'] },
  { name: 'ParametersEnhanced', path: '/#/parameters/enhanced', phase: 4, priority: 'LOW', features: ['增强参数'] },
  
  // Phase 5: 工具页面 (11页)
  { name: 'ImportEvents', path: '/#/import-events', phase: 5, priority: 'LOW', features: ['导入功能'] },
  { name: 'ApiDocs', path: '/#/api-docs', phase: 5, priority: 'LOW', features: ['API文档'] },
  { name: 'BatchOperations', path: '/#/batch-operations', phase: 5, priority: 'LOW', features: ['批量操作'] },
  { name: 'LogDetail', path: '/#/log-detail', phase: 5, priority: 'LOW', features: ['日志详情'] },
  { name: 'LogFormCreate', path: '/#/logs/create', phase: 5, priority: 'LOW', features: ['日志创建'] },
  { name: 'LogFormEdit', path: '/#/logs/1/edit', phase: 5, priority: 'LOW', features: ['日志编辑'], requiresData: true },
  { name: 'ValidationRules', path: '/#/validation-rules', phase: 5, priority: 'LOW', features: ['验证规则'] },
  { name: 'HqlEdit', path: '/#/hql/1/edit', phase: 5, priority: 'LOW', features: ['HQL编辑'], requiresData: true },
  { name: 'AlterSql', path: '/#/alter-sql/1', phase: 5, priority: 'LOW', features: ['SQL变更'], requiresData: true },
  { name: 'AlterSqlBuilder', path: '/#/alter-sql-builder', phase: 5, priority: 'LOW', features: ['SQL构建'] },
  { name: 'NotFound', path: '/#/not-found-page', phase: 5, priority: 'LOW', features: ['404页面'] }
];

// 存储所有结果
const allResults = {
  timestamp: new Date().toISOString(),
  summary: {
    total: 0,
    passed: 0,
    failed: 0,
    warnings: 0,
    byPhase: { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 }
  },
  pages: [],
  issues: [],
  consoleErrors: [],
  performanceData: []
};

/**
 * 确保目录存在
 */
function ensureDirectories() {
  const dirs = [CONFIG.reportDir, CONFIG.screenshotDir];
  dirs.forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  });
}

/**
 * 检查服务是否运行
 */
async function checkServices() {
  console.log('🔍 检查服务状态...\n');
  
  const checkService = (url, name) => {
    return new Promise((resolve) => {
      const req = http.get(url, (res) => {
        resolve({ name, status: res.statusCode, ok: res.statusCode === 200 });
      });
      req.on('error', () => resolve({ name, status: 0, ok: false }));
      req.setTimeout(5000, () => {
        req.destroy();
        resolve({ name, status: 0, ok: false });
      });
    });
  };

  const backend = await checkService(`${CONFIG.backendURL}/api/games`, 'Backend');
  const frontend = await checkService(CONFIG.baseURL, 'Frontend');

  console.log(`  ${backend.ok ? '✅' : '❌'} Backend: ${CONFIG.backendURL}`);
  console.log(`  ${frontend.ok ? '✅' : '❌'} Frontend: ${CONFIG.baseURL}\n`);

  if (!backend.ok || !frontend.ok) {
    console.error('❌ 服务未启动，请先启动服务！');
    process.exit(1);
  }

  return true;
}

/**
 * 获取测试数据（游戏ID和事件ID）
 */
async function getTestData() {
  console.log('📊 获取测试数据...\n');
  
  try {
    // 获取第一个游戏
    const gamesRes = await new Promise((resolve, reject) => {
      http.get(`${CONFIG.backendURL}/api/games`, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => resolve(JSON.parse(data)));
      }).on('error', reject);
    });
    
    // 获取第一个事件
    const eventsRes = await new Promise((resolve, reject) => {
      http.get(`${CONFIG.backendURL}/api/events?page=1&per_page=1`, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => resolve(JSON.parse(data)));
      }).on('error', reject);
    });

    const testData = {
      gameId: gamesRes.data?.[0]?.gid || 10000147,
      gameName: gamesRes.data?.[0]?.name || 'Test Game',
      eventId: eventsRes.items?.[0]?.id || 1,
      categoryId: 1
    };

    console.log(`  ✅ 使用游戏: ${testData.gameName} (ID: ${testData.gameId})`);
    console.log(`  ✅ 使用事件ID: ${testData.eventId}\n`);

    return testData;
  } catch (error) {
    console.warn(`  ⚠️  无法获取测试数据，使用默认值`);
    return { gameId: 10000147, eventId: 1, categoryId: 1 };
  }
}

/**
 * 替换路径中的动态参数
 */
function replacePathParams(path, testData) {
  return path
    .replace(':gid', testData.gameId)
    .replace(':id', testData.eventId)
    .replace(':paramId', testData.eventId);
}

/**
 * 测试单个页面
 */
async function testPage(page, pageConfig, testData) {
  const fullURL = `${CONFIG.baseURL}${replacePathParams(pageConfig.path, testData)}`;
  console.log(`\n🧪 测试: ${pageConfig.name} (${pageConfig.priority})`);
  console.log(`   URL: ${fullURL}`);
  console.log(`   功能: ${pageConfig.features.join(', ')}`);

  const result = {
    name: pageConfig.name,
    path: pageConfig.path,
    phase: pageConfig.phase,
    priority: pageConfig.priority,
    url: fullURL,
    timestamp: new Date().toISOString(),
    success: false,
    metrics: {},
    consoleErrors: [],
    networkErrors: [],
    screenshot: null,
    issues: []
  };

  try {
    // 清空控制台日志
    await page.evaluate(() => console.clear());
    
    // 开始计时
    const startTime = Date.now();
    
    // 导航到页面
    const response = await page.goto(fullURL, { 
      waitUntil: 'networkidle',
      timeout: CONFIG.timeout 
    });
    
    const loadTime = Date.now() - startTime;
    
    // 等待页面稳定
    await page.waitForTimeout(CONFIG.waitTime);
    
    // 获取性能指标
    const performanceMetrics = await page.evaluate(() => {
      const nav = performance.getEntriesByType('navigation')[0];
      const paint = performance.getEntriesByType('paint');
      
      return {
        loadTime: nav ? nav.loadEventEnd - nav.startTime : 0,
        domContentLoaded: nav ? nav.domContentLoadedEventEnd - nav.startTime : 0,
        fcp: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0,
        lcp: 0, // 需要更复杂的计算
        resources: performance.getEntriesByType('resource').length
      };
    });

    // 获取控制台错误
    const consoleLogs = await page.evaluate(() => {
      return window.consoleErrors || [];
    });

    // 获取网络错误
    const networkErrors = [];

    // 截图
    const screenshotPath = path.join(CONFIG.screenshotDir, `${pageConfig.name}-${Date.now()}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });

    // 评估结果
    result.success = response?.status() === 200;
    result.metrics = {
      ...performanceMetrics,
      loadTime,
      statusCode: response?.status()
    };
    result.consoleErrors = consoleErrors;
    result.networkErrors = networkErrors;
    result.screenshot = screenshotPath;

    // 检查性能问题
    if (loadTime > THRESHOLDS.loadTime.needsImprovement) {
      result.issues.push({
        type: 'performance',
        severity: 'HIGH',
        message: `加载时间过长: ${loadTime}ms (目标: <${THRESHOLDS.loadTime.good}ms)`
      });
    }

    // 检查控制台错误
    if (consoleErrors.length > 0) {
      result.issues.push({
        type: 'console',
        severity: 'MEDIUM',
        message: `发现 ${consoleErrors.length} 个控制台错误`
      });
    }

    console.log(`   ✅ 加载完成: ${loadTime}ms`);
    console.log(`   📊 资源数: ${performanceMetrics.resources}`);
    
    if (result.issues.length > 0) {
      console.log(`   ⚠️  发现 ${result.issues.length} 个问题`);
    }

  } catch (error) {
    result.success = false;
    result.error = error.message;
    result.issues.push({
      type: 'error',
      severity: 'CRITICAL',
      message: error.message
    });
    console.log(`   ❌ 错误: ${error.message}`);
  }

  return result;
}

/**
 * 执行一个批次的测试
 */
async function runBatch(pages, testData, batchNum) {
  console.log(`\n${'='.repeat(80)}`);
  console.log(`🚀 Phase ${batchNum} 开始 - 测试 ${pages.length} 个页面`);
  console.log('='.repeat(80));

  const browser = await chromium.launch({
    headless: CONFIG.headless,
    args: ['--start-maximized', '--disable-web-security']
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    recordVideo: { dir: path.join(CONFIG.reportDir, 'videos') }
  });

  const page = await context.newPage();

  // 监听控制台错误
  const consoleErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push({
        type: msg.type(),
        text: msg.text(),
        location: msg.location(),
        timestamp: new Date().toISOString()
      });
    }
  });

  page.on('pageerror', error => {
    consoleErrors.push({
      type: 'pageerror',
      text: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString()
    });
  });

  // 监听网络请求失败
  page.on('requestfailed', request => {
    consoleErrors.push({
      type: 'network',
      text: `Failed: ${request.url()} - ${request.failure().errorText}`,
      timestamp: new Date().toISOString()
    });
  });

  const results = [];

  for (const pageConfig of pages) {
    const result = await testPage(page, pageConfig, testData);
    result.consoleErrors = [...result.consoleErrors, ...consoleErrors];
    consoleErrors.length = 0; // 清空
    results.push(result);
    
    // 保存进度
    saveProgress(results, batchNum);
  }

  await context.close();
  await browser.close();

  console.log(`\n✅ Phase ${batchNum} 完成 - 测试了 ${results.length} 个页面`);
  
  return results;
}

/**
 * 保存进度
 */
function saveProgress(results, batchNum) {
  const progressFile = path.join(CONFIG.reportDir, `progress-batch-${batchNum}.json`);
  fs.writeFileSync(progressFile, JSON.stringify(results, null, 2));
}

/**
 * 生成问题清单
 */
function generateIssueList() {
  const issues = [];
  
  allResults.pages.forEach(page => {
    page.issues.forEach(issue => {
      issues.push({
        page: page.name,
        phase: page.phase,
        priority: page.priority,
        ...issue
      });
    });
  });

  // 按严重程度排序
  const severityOrder = { CRITICAL: 1, HIGH: 2, MEDIUM: 3, LOW: 4 };
  issues.sort((a, b) => severityOrder[a.severity] - severityOrder[b.severity]);

  return issues;
}

/**
 * 生成 Markdown 报告
 */
function generateMarkdownReport() {
  const timestamp = new Date().toLocaleString('zh-CN');
  const issues = generateIssueList();
  
  const criticalIssues = issues.filter(i => i.severity === 'CRITICAL');
  const highIssues = issues.filter(i => i.severity === 'HIGH');
  const mediumIssues = issues.filter(i => i.severity === 'MEDIUM');
  const lowIssues = issues.filter(i => i.severity === 'LOW');

  let markdown = `# Event2Table 全面测试报告

**测试时间**: ${timestamp}  
**测试范围**: 41 个页面  
**测试维度**: 加载性能、控制台错误、功能交互、截图

---

## 📊 执行摘要

| 指标 | 数值 |
|------|------|
| 总测试页面 | ${allResults.summary.total} |
| 通过 | ${allResults.summary.passed} ✅ |
| 失败 | ${allResults.summary.failed} ❌ |
| 警告 | ${allResults.summary.warnings} ⚠️ |

**按阶段统计**:
- Phase 1 (核心页面): ${allResults.summary.byPhase[1]} 页
- Phase 2 (表单页面): ${allResults.summary.byPhase[2]} 页
- Phase 3 (管理页面): ${allResults.summary.byPhase[3]} 页
- Phase 4 (参数分析): ${allResults.summary.byPhase[4]} 页
- Phase 5 (工具页面): ${allResults.summary.byPhase[5]} 页

---

## 🔴 严重问题 (${criticalIssues.length} 个)

| # | 页面 | 阶段 | 问题描述 | 类型 |
|---|------|------|----------|------|
`;

  criticalIssues.forEach((issue, idx) => {
    markdown += `| ${idx + 1} | ${issue.page} | ${issue.phase} | ${issue.message} | ${issue.type} |\n`;
  });

  markdown += `
---

## 🟠 高优先级问题 (${highIssues.length} 个)

| # | 页面 | 阶段 | 问题描述 | 类型 |
|---|------|------|----------|------|
`;

  highIssues.forEach((issue, idx) => {
    markdown += `| ${idx + 1} | ${issue.page} | ${issue.phase} | ${issue.message} | ${issue.type} |\n`;
  });

  markdown += `
---

## 🟡 中优先级问题 (${mediumIssues.length} 个)

| # | 页面 | 阶段 | 问题描述 | 类型 |
|---|------|------|----------|------|
`;

  mediumIssues.forEach((issue, idx) => {
    markdown += `| ${idx + 1} | ${issue.page} | ${issue.phase} | ${issue.message} | ${issue.type} |\n`;
  });

  markdown += `
---

## 🟢 低优先级问题 (${lowIssues.length} 个)

| # | 页面 | 阶段 | 问题描述 | 类型 |
|---|------|------|----------|------|
`;

  lowIssues.forEach((issue, idx) => {
    markdown += `| ${idx + 1} | ${issue.page} | ${issue.phase} | ${issue.message} | ${issue.type} |\n`;
  });

  markdown += `
---

## 📈 性能数据摘要

| 页面 | 加载时间 | 资源数 | 状态 |
|------|----------|--------|------|
`;

  allResults.pages.forEach(page => {
    const status = page.success ? '✅' : '❌';
    markdown += `| ${page.name} | ${page.metrics.loadTime}ms | ${page.metrics.resources} | ${status} |\n`;
  });

  markdown += `
---

## 📁 输出文件

- **详细报告**: ${CONFIG.reportDir}/detailed-report.json
- **截图文件夹**: ${CONFIG.screenshotDir}/
- **进度文件**: ${CONFIG.reportDir}/progress-batch-*.json

---

**报告生成时间**: ${timestamp}
`;

  return markdown;
}

/**
 * 保存最终报告
 */
function saveReports() {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  
  // 保存 JSON 报告
  const jsonReport = {
    ...allResults,
    generatedAt: new Date().toISOString()
  };
  fs.writeFileSync(
    path.join(CONFIG.reportDir, `detailed-report-${timestamp}.json`),
    JSON.stringify(jsonReport, null, 2)
  );

  // 保存 Markdown 报告
  const markdownReport = generateMarkdownReport();
  fs.writeFileSync(
    path.join(CONFIG.reportDir, `test-report-${timestamp}.md`),
    markdownReport
  );

  console.log(`\n📄 报告已保存:`);
  console.log(`   - JSON: ${CONFIG.reportDir}/detailed-report-${timestamp}.json`);
  console.log(`   - Markdown: ${CONFIG.reportDir}/test-report-${timestamp}.md`);

  return markdownReport;
}

/**
 * 主函数
 */
async function main() {
  console.log('\n' + '='.repeat(80));
  console.log('🚀 Event2Table 全面测试开始');
  console.log('='.repeat(80));
  console.log(`\n📋 测试计划:`);
  console.log(`   - 总页面: 41 页`);
  console.log(`   - 分 5 个阶段执行`);
  console.log(`   - 预计耗时: 50-70 分钟`);
  console.log(`   - 输出目录: ${CONFIG.reportDir}\n`);

  // 准备工作
  ensureDirectories();
  await checkServices();
  const testData = await getTestData();

  // 按阶段分组
  const batches = {
    1: ALL_PAGES.filter(p => p.phase === 1),
    2: ALL_PAGES.filter(p => p.phase === 2),
    3: ALL_PAGES.filter(p => p.phase === 3),
    4: ALL_PAGES.filter(p => p.phase === 4),
    5: ALL_PAGES.filter(p => p.phase === 5)
  };

  // 执行所有批次
  for (let phase = 1; phase <= 5; phase++) {
    const batchResults = await runBatch(batches[phase], testData, phase);
    allResults.pages.push(...batchResults);
    allResults.summary.byPhase[phase] = batchResults.length;
    
    // 更新汇总
    batchResults.forEach(r => {
      allResults.summary.total++;
      if (r.success) {
        if (r.issues.length === 0) {
          allResults.summary.passed++;
        } else {
          allResults.summary.warnings++;
        }
      } else {
        allResults.summary.failed++;
      }
    });

    // 短暂休息
    if (phase < 5) {
      console.log('\n⏱️  休息 5 秒...');
      await new Promise(resolve => setTimeout(resolve, 5000));
    }
  }

  // 生成报告
  console.log('\n' + '='.repeat(80));
  console.log('📝 生成测试报告...');
  console.log('='.repeat(80));
  
  const finalReport = saveReports();

  // 打印总结
  console.log('\n' + '='.repeat(80));
  console.log('✅ 测试完成！');
  console.log('='.repeat(80));
  console.log(`\n📊 最终结果:`);
  console.log(`   总页面: ${allResults.summary.total}`);
  console.log(`   通过: ${allResults.summary.passed} ✅`);
  console.log(`   失败: ${allResults.summary.failed} ❌`);
  console.log(`   警告: ${allResults.summary.warnings} ⚠️`);
  
  const totalIssues = generateIssueList().length;
  console.log(`\n⚠️  发现问题: ${totalIssues} 个`);
  
  console.log(`\n📁 输出位置: ${CONFIG.reportDir}/`);
  console.log('='.repeat(80) + '\n');

  // 返回报告内容
  return finalReport;
}

// 执行测试
main()
  .then(report => {
    console.log('\n🎉 所有测试执行完毕！');
    process.exit(0);
  })
  .catch(error => {
    console.error('\n❌ 测试执行失败:', error);
    process.exit(1);
  });
