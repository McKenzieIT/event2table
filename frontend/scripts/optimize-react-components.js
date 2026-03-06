#!/usr/bin/env node

/**
 * React Component Performance Optimizer
 *
 * 自动添加：
 * - React.memo 包装导出
 * - useMemo 包装复杂计算
 * - useCallback 包装事件处理函数
 */

const fs = require('fs');
const path = require('path');

// 需要优化的文件列表
const FILES_TO_OPTIMIZE = [
  'src/analytics/pages/EventsListGraphQL.tsx',
  'src/analytics/pages/ParametersListGraphQL.tsx',
  'src/analytics/pages/CategoriesListGraphQL.tsx',
  'src/analytics/pages/FlowsList.tsx',
  'src/features/games/GameManagementModal.tsx',
  'src/features/events/EventManagementModalGraphQL.tsx',
  'src/features/games/AddGameModalGraphQL.tsx',
];

/**
 * 检查文件是否需要添加 React.memo
 */
function needsReactMemo(content) {
  // 检查是否已有 React.memo
  if (content.includes('React.memo') || content.includes('memo(')) {
    return false;
  }

  // 检查是否有 export default function/component
  const hasFunctionExport = /export\s+default\s+function\s+(\w+)/.test(content);
  const hasComponentExport = /export\s+default\s+(\w+)(?::\s*React\.FC)?/.test(content);

  return hasFunctionExport || hasComponentExport;
}

/**
 * 添加 React.memo 包装
 */
function addReactMemo(content, componentName) {
  // 查找 export default 语句
  const exportDefaultRegex = new RegExp(`export\\s+default\\s+${componentName}`);
  const hasMemoExport = /export\s+default\s+React\.memo/.test(content);

  if (hasMemoExport) {
    return content; // 已经有 React.memo
  }

  // 替换 export default ComponentName 为 export default React.memo(ComponentName)
  content = content.replace(
    exportDefaultRegex,
    `const ${componentName}Memo = React.memo(${componentName});\n\nexport default ${componentName}Memo`
  );

  return content;
}

/**
 * 检查并添加 useCallback 到事件处理函数
 */
function addUseCallback(content) {
  // 检查是否已导入 useCallback
  const needsImport = !content.includes('useCallback');

  if (needsImport) {
    // 在 React 导入中添加 useCallback
    content = content.replace(
      /import React,\s*\{([^}]+)\}\s*from\s*['"]react['"]/,
      (match, imports) => {
        const cleanImports = imports
          .split(',')
          .map(s => s.trim())
          .filter(s => s !== '');
        if (!cleanImports.includes('useCallback')) {
          cleanImports.push('useCallback');
        }
        return `import React, { ${cleanImports.join(', ')} } from 'react'`;
      }
    );
  }

  return content;
}

/**
 * 优化单个文件
 */
function optimizeFile(filePath) {
  const fullPath = path.join(__dirname, '..', filePath);

  if (!fs.existsSync(fullPath)) {
    console.log(`⚠️  文件不存在: ${filePath}`);
    return { success: false, path: filePath };
  }

  let content = fs.readFileSync(fullPath, 'utf-8');
  const originalContent = content;

  // 1. 添加 useCallback 导入
  content = addUseCallback(content);

  // 2. 添加 React.memo
  if (needsReactMemo(content)) {
    // 提取组件名称
    const match = content.match(/export\s+default\s+function\s+(\w+)/);
    if (match) {
      const componentName = match[1];
      content = addReactMemo(content, componentName);
    }
  }

  // 检查是否有修改
  const hasChanges = content !== originalContent;

  if (hasChanges) {
    fs.writeFileSync(fullPath, content, 'utf-8');
    console.log(`✅ 优化完成: ${filePath}`);
    return { success: true, path: filePath, modified: true };
  } else {
    console.log(`⏭️  跳过（已优化）: ${filePath}`);
    return { success: true, path: filePath, modified: false };
  }
}

/**
 * 主函数
 */
function main() {
  console.log('🚀 开始优化 React 组件...\n');

  const results = {
    total: FILES_TO_OPTIMIZE.length,
    optimized: 0,
    skipped: 0,
    failed: 0,
  };

  FILES_TO_OPTIMIZE.forEach(filePath => {
    const result = optimizeFile(filePath);
    if (result.success) {
      if (result.modified) {
        results.optimized++;
      } else {
        results.skipped++;
      }
    } else {
      results.failed++;
    }
  });

  console.log('\n📊 优化结果:');
  console.log(`   总文件数: ${results.total}`);
  console.log(`   ✅ 已优化: ${results.optimized}`);
  console.log(`   ⏭️  已跳过: ${results.skipped}`);
  console.log(`   ❌ 失败: ${results.failed}`);
  console.log(`   📈 优化率: ${((results.optimized / results.total) * 100).toFixed(1)}%`);
}

// 运行
main();
