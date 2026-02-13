const fs = require('fs');

const reportPath = process.argv[2] || './test_results/event2table-test/detailed-report-2026-02-13T04-14-06-567Z.json';
const report = JSON.parse(fs.readFileSync(reportPath, 'utf-8'));

// 分析性能数据
const slowPages = report.pages
  .filter(p => p.metrics.loadTime > 3000)
  .sort((a, b) => b.metrics.loadTime - a.metrics.loadTime);

const normalPages = report.pages
  .filter(p => p.metrics.loadTime <= 3000 && p.metrics.loadTime > 0)
  .sort((a, b) => a.metrics.loadTime - b.metrics.loadTime);

// 收集所有控制台错误
const consoleErrors = [];
const errorMap = new Map();

report.pages.forEach(p => {
  if (p.consoleErrors && p.consoleErrors.length > 0) {
    p.consoleErrors.forEach(err => {
      consoleErrors.push({
        page: p.name,
        phase: p.phase,
        error: err.text,
        type: err.type
      });
      
      // 统计错误类型
      const key = err.text;
      if (!errorMap.has(key)) {
        errorMap.set(key, { count: 0, pages: [] });
      }
      const entry = errorMap.get(key);
      entry.count++;
      if (!entry.pages.includes(p.name)) {
        entry.pages.push(p.name);
      }
    });
  }
});

// 计算统计数据
const avgLoadTime = report.pages.reduce((sum, p) => sum + (p.metrics.loadTime || 0), 0) / report.pages.length;
const maxLoadTime = Math.max(...report.pages.map(p => p.metrics.loadTime || 0));
const minLoadTime = Math.min(...report.pages.filter(p => p.metrics.loadTime > 0).map(p => p.metrics.loadTime));

console.log('\n' + '='.repeat(80));
console.log('📊 Event2Table 全面测试结果分析');
console.log('='.repeat(80));

console.log('\n🎯 执行摘要:');
console.log(`   总页面数: ${report.summary.total}`);
console.log(`   平均加载时间: ${Math.round(avgLoadTime)}ms`);
console.log(`   最快页面: ${minLoadTime}ms`);
console.log(`   最慢页面: ${maxLoadTime}ms`);
console.log(`   控制台错误: ${consoleErrors.length} 个`);
console.log(`   唯一错误类型: ${errorMap.size} 种`);

console.log('\n🔴 性能严重问题 (>5000ms):');
slowPages.forEach((p, i) => {
  console.log(`   ${i+1}. ${p.name}: ${p.metrics.loadTime}ms (${p.priority})`);
});

console.log('\n🟢 性能良好页面 (<1000ms) - Top 10:');
normalPages.slice(0, 10).forEach((p, i) => {
  console.log(`   ${i+1}. ${p.name}: ${p.metrics.loadTime}ms`);
});

console.log('\n⚠️  控制台错误汇总:');
let idx = 1;
errorMap.forEach((value, key) => {
  console.log(`\n   ${idx}. [影响 ${value.count} 次, ${value.pages.length} 个页面]`);
  console.log(`      ${key.substring(0, 150)}${key.length > 150 ? '...' : ''}`);
  if (value.pages.length <= 5) {
    console.log(`      页面: ${value.pages.join(', ')}`);
  }
  idx++;
});

// 按阶段统计
console.log('\n📈 按阶段统计:');
for (let phase = 1; phase <= 5; phase++) {
  const phasePages = report.pages.filter(p => p.phase === phase);
  const phaseAvg = phasePages.reduce((sum, p) => sum + (p.metrics.loadTime || 0), 0) / phasePages.length;
  console.log(`   Phase ${phase}: ${phasePages.length} 页, 平均 ${Math.round(phaseAvg)}ms`);
}

console.log('\n' + '='.repeat(80));

// 生成建议
console.log('\n💡 关键优化建议:');

if (slowPages.length > 0) {
  console.log('\n1. 性能优化:');
  console.log('   - 对加载时间 >5s 的页面实施代码分割');
  console.log('   - 优化 Dashboard、Categories、ParameterDashboard 等慢页面');
  console.log('   - 使用 React.lazy() 和 Suspense 实现懒加载');
}

if (errorMap.size > 0) {
  console.log('\n2. 错误修复:');
  errorMap.forEach((value, key) => {
    if (key.includes('AddGameModal')) {
      console.log('   - 修复 AddGameModal 导出错误（影响多个页面）');
    }
  });
}

console.log('\n' + '='.repeat(80) + '\n');

// 保存分析结果
const analysis = {
  timestamp: new Date().toISOString(),
  summary: {
    totalPages: report.summary.total,
    avgLoadTime: Math.round(avgLoadTime),
    maxLoadTime,
    minLoadTime,
    consoleErrorCount: consoleErrors.length,
    uniqueErrorTypes: errorMap.size
  },
  slowPages: slowPages.map(p => ({ name: p.name, loadTime: p.metrics.loadTime, priority: p.priority })),
  errors: Array.from(errorMap.entries()).map(([error, data]) => ({
    error: error.substring(0, 200),
    count: data.count,
    pages: data.pages
  })),
  phaseStats: [1, 2, 3, 4, 5].map(phase => {
    const pages = report.pages.filter(p => p.phase === phase);
    return {
      phase,
      count: pages.length,
      avgLoadTime: Math.round(pages.reduce((sum, p) => sum + (p.metrics.loadTime || 0), 0) / pages.length)
    };
  })
};

fs.writeFileSync(
  './test_results/event2table-test/analysis-report.json',
  JSON.stringify(analysis, null, 2)
);

console.log('📄 分析报告已保存: ./test_results/event2table-test/analysis-report.json\n');
