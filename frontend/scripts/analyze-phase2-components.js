#!/usr/bin/env node
/**
 * Phase 2 Component Optimization Analysis
 *
 * 分析 analytics/pages 组件的优化状态
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const COMPONENTS_DIR = path.join(__dirname, '../src/analytics/pages');

// 优化标记
const OPTIMIZED_MARKER = '⚡️ REACT PERF';
const TODO_MARKER = '⚠️ REACT PERF';

// 分析结果
const results = {
  optimized: [],      // 已优化
  needsOptimization: [], // 需要优化
  noHooks: [],        // 不需要Hooks（简单组件）
  unknown: []         // 未知状态
};

/**
 * 分析组件文件的优化状态
 */
function analyzeComponent(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const fileName = path.basename(filePath);

  // 检查是否已优化
  const hasOptimizedMarker = content.includes(OPTIMIZED_MARKER);
  const hasTodoMarker = content.includes(TODO_MARKER);

  // 检查是否使用了React性能Hooks
  const hasReactMemo = content.includes('React.memo');
  const hasUseCallback = content.includes('useCallback');
  const hasUseMemo = content.includes('useMemo');

  // 检查组件复杂度（行数）
  const lines = content.split('\n').length;
  const isComplex = lines > 50;

  // 分类
  if (hasOptimizedMarker || (hasReactMemo && (hasUseCallback || hasUseMemo))) {
    return {
      fileName,
      status: 'optimized',
      hasMemo: hasReactMemo,
      hasUseCallback,
      hasUseMemo,
      lines
    };
  } else if (hasTodoMarker) {
    return {
      fileName,
      status: 'needsOptimization',
      hasMemo: hasReactMemo,
      hasUseCallback,
      hasUseMemo,
      lines
    };
  } else if (!isComplex && !hasReactMemo && !hasUseCallback && !hasUseMemo) {
    // 简单组件，可能不需要优化
    return {
      fileName,
      status: 'noHooks',
      hasMemo: hasReactMemo,
      hasUseCallback,
      hasUseMemo,
      lines
    };
  } else {
    return {
      fileName,
      status: 'needsOptimization',
      hasMemo: hasReactMemo,
      hasUseCallback,
      hasUseMemo,
      lines
    };
  }
}

/**
 * 主函数
 */
function main() {
  console.log('📊 Phase 2 组件优化状态分析\n');

  // 读取所有.tsx文件
  const files = fs.readdirSync(COMPONENTS_DIR)
    .filter(f => f.endsWith('.tsx'))
    .map(f => path.join(COMPONENTS_DIR, f));

  console.log(`📁 分析 ${files.length} 个组件...\n`);

  // 分析每个组件
  files.forEach(filePath => {
    const result = analyzeComponent(filePath);

    switch (result.status) {
      case 'optimized':
        results.optimized.push(result);
        break;
      case 'needsOptimization':
        results.needsOptimization.push(result);
        break;
      case 'noHooks':
        results.noHooks.push(result);
        break;
      default:
        results.unknown.push(result);
    }
  });

  // 打印结果
  console.log('✅ 已优化组件 (' + results.optimized.length + '):');
  results.optimized.forEach(c => {
    console.log(`   ✓ ${c.fileName} (${c.lines} lines) - memo:${c.hasMemo} useCallback:${c.hasUseCallback} useMemo:${c.hasUseMemo}`);
  });

  console.log('\n⚠️  需要优化组件 (' + results.needsOptimization.length + '):');
  results.needsOptimization.forEach(c => {
    console.log(`   ✗ ${c.fileName} (${c.lines} lines) - memo:${c.hasMemo} useCallback:${c.hasUseCallback} useMemo:${c.hasUseMemo}`);
  });

  console.log('\n⏭️  简单组件/无需优化 (' + results.noHooks.length + '):');
  results.noHooks.forEach(c => {
    console.log(`   - ${c.fileName} (${c.lines} lines)`);
  });

  // 统计
  const total = files.length;
  const optimizedCount = results.optimized.length;
  const needsOptimizationCount = results.needsOptimization.length;
  const noHooksCount = results.noHooks.length;

  console.log('\n📈 统计摘要:');
  console.log(`   总组件数: ${total}`);
  console.log(`   已优化: ${optimizedCount} (${((optimizedCount / total) * 100).toFixed(1)}%)`);
  console.log(`   需要优化: ${needsOptimizationCount} (${((needsOptimizationCount / total) * 100).toFixed(1)}%)`);
  console.log(`   无需优化: ${noHooksCount} (${((noHooksCount / total) * 100).toFixed(1)}%)`);

  // 生成JSON报告
  const reportPath = path.join(__dirname, '../output/phase2-analysis.json');
  fs.mkdirSync(path.dirname(reportPath), { recursive: true });
  fs.writeFileSync(reportPath, JSON.stringify(results, null, 2));
  console.log(`\n📄 报告已保存: ${reportPath}`);

  return results;
}

// 运行分析
main();
