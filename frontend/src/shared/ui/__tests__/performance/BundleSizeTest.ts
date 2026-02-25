// @ts-nocheck - TypeScript检查暂禁用
/**
 * Bundle Size Analysis Tool
 *
 * Analyzes the bundle size of the @shared/ui component library.
 * Run with: npm run build
 * Then check the generated bundle in dist/assets/
 *
 * This script provides utilities to measure and report component sizes.
 */

import fs from 'fs';
import path from 'path';

interface BundleSizeInfo {
  fileName: string;
  size: number;
  sizeKB: number;
  sizeFormatted: string;
}

interface ComponentSize {
  componentName: string;
  filePath: string;
  size: number;
  sizeKB: number;
}

// ANSI color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  bold: '\x1b[1m',
};

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

function getFileSize(filePath: string): number {
  try {
    const stats = fs.statSync(filePath);
    return stats.size;
  } catch (error) {
    return 0;
  }
}

function analyzeComponentSourceFiles(): ComponentSize[] {
  const components = ['Button', 'Card', 'Input', 'Table', 'Modal', 'Badge'];
  const baseDir = '/Users/mckenzie/Documents/event2table/frontend/src/shared/ui';
  const results: ComponentSize[] = [];

  components.forEach(component => {
    const componentDir = path.join(baseDir, component);
    const jsxFile = path.join(componentDir, `${component}.jsx`);
    const tsxFile = path.join(componentDir, `${component}.tsx`);
    const cssFile = path.join(componentDir, `${component}.css`);

    let totalSize = 0;

    // Check .jsx or .tsx
    if (fs.existsSync(jsxFile)) {
      totalSize += getFileSize(jsxFile);
    } else if (fs.existsSync(tsxFile)) {
      totalSize += getFileSize(tsxFile);
    }

    // Add CSS size
    if (fs.existsSync(cssFile)) {
      totalSize += getFileSize(cssFile);
    }

    results.push({
      componentName: component,
      filePath: componentDir,
      size: totalSize,
      sizeKB: totalSize / 1024,
    });
  });

  return results;
}

function analyzeBundleSizes(baseDir: string): BundleSizeInfo[] {
  const distDir = path.join(baseDir, 'dist', 'assets');

  if (!fs.existsSync(distDir)) {
    console.log(`${colors.yellow}Bundle not found. Run 'npm run build' first.${colors.reset}`);
    return [];
  }

  const files = fs.readdirSync(distDir);
  const bundles: BundleSizeInfo[] = [];

  files.forEach(file => {
    if (file.endsWith('.js') || file.endsWith('.css')) {
      const filePath = path.join(distDir, file);
      const size = getFileSize(filePath);

      bundles.push({
        fileName: file,
        size,
        sizeKB: size / 1024,
        sizeFormatted: formatBytes(size),
      });
    }
  });

  return bundles.sort((a, b) => b.size - a.size);
}

function printBundleReport(bundles: BundleSizeInfo[]) {
  console.log(`\n${colors.bold}${colors.cyan}=== Bundle Size Analysis ===${colors.reset}\n`);

  if (bundles.length === 0) {
    console.log(`${colors.yellow}No bundles found. Run 'npm run build' first.${colors.reset}\n`);
    return;
  }

  const totalSize = bundles.reduce((sum, b) => sum + b.size, 0);
  const totalJS = bundles
    .filter(b => b.fileName.endsWith('.js'))
    .reduce((sum, b) => sum + b.size, 0);
  const totalCSS = bundles
    .filter(b => b.fileName.endsWith('.css'))
    .reduce((sum, b) => sum + b.size, 0);

  // Print individual bundles
  console.log(`${colors.bold}Individual Bundles:${colors.reset}`);
  bundles.forEach(bundle => {
    const percentage = ((bundle.size / totalSize) * 100).toFixed(1);
    const color = bundle.size > 100000 ? colors.red : bundle.size > 50000 ? colors.yellow : colors.green;

    console.log(`  ${bundle.fileName}`);
    console.log(`    Size: ${color}${bundle.sizeFormatted}${colors.reset} (${percentage}%)`);
  });

  // Print totals
  console.log(`\n${colors.bold}Totals:${colors.reset}`);
  console.log(`  Total JS:  ${colors.blue}${formatBytes(totalJS)}${colors.reset}`);
  console.log(`  Total CSS: ${colors.blue}${formatBytes(totalCSS)}${colors.reset}`);
  console.log(`  Total:     ${colors.bold}${formatBytes(totalSize)}${colors.reset}`);

  // Performance recommendations
  console.log(`\n${colors.bold}Analysis:${colors.reset}`);

  if (totalJS < 50000) {
    console.log(`  ${colors.green}✓${colors.reset} Bundle size is excellent (< 50KB)`);
  } else if (totalJS < 100000) {
    console.log(`  ${colors.yellow}⚠${colors.reset} Bundle size is acceptable (< 100KB)`);
  } else {
    console.log(`  ${colors.red}✗${colors.reset} Bundle size is large (> 100KB). Consider code splitting.`);
  }

  // Check for large individual bundles
  const largeBundles = bundles.filter(b => b.size > 50000);
  if (largeBundles.length > 0) {
    console.log(`\n${colors.yellow}Large bundles detected (> 50KB):${colors.reset}`);
    largeBundles.forEach(bundle => {
      console.log(`  - ${bundle.fileName}: ${formatBytes(bundle.size)}`);
    });
    console.log(`  ${colors.cyan}Tip: Consider dynamic imports for these bundles.${colors.reset}`);
  }

  console.log('');
}

function printComponentSourceReport(components: ComponentSize[]) {
  console.log(`\n${colors.bold}${colors.cyan}=== Component Source Size ===${colors.reset}\n`);

  const totalSize = components.reduce((sum, c) => sum + c.size, 0);

  components.forEach(component => {
    const percentage = ((component.size / totalSize) * 100).toFixed(1);
    const color = component.sizeKB > 20 ? colors.yellow : colors.green;

    console.log(`  ${component.componentName.padEnd(10)} ${color}${formatBytes(component.size).padStart(10)}${colors.reset} (${percentage}%)`);
  });

  console.log(`\n  ${'Total'.padEnd(10)} ${colors.bold}${formatBytes(totalSize).padStart(10)}${colors.reset}`);
  console.log('');
}

// Main execution
if (require.main === module) {
  const baseDir = '/Users/mckenzie/Documents/event2table/frontend';

  console.log(`${colors.bold}${colors.blue}
╔═══════════════════════════════════════════════════════════╗
║     @shared/ui Bundle Size Analyzer                      ║
╚═══════════════════════════════════════════════════════════╝
  ${colors.reset}`);

  // Analyze component source files
  const components = analyzeComponentSourceFiles();
  printComponentSourceReport(components);

  // Analyze bundle sizes
  const bundles = analyzeBundleSizes(baseDir);
  printBundleReport(bundles);

  // Generate JSON report
  const report = {
    timestamp: new Date().toISOString(),
    components: components.map(c => ({
      name: c.componentName,
      sizeKB: Math.round(c.sizeKB * 100) / 100,
    })),
    bundles: bundles.map(b => ({
      file: b.fileName,
      sizeKB: Math.round(b.sizeKB * 100) / 100,
    })),
    summary: {
      totalComponentSizeKB: Math.round(components.reduce((s, c) => s + c.sizeKB, 0) * 100) / 100,
      totalBundleSizeKB: Math.round(bundles.reduce((s, b) => s + b.sizeKB, 0) * 100) / 100,
    },
  };

  const reportPath = path.join(baseDir, 'bundle-size-report.json');
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  console.log(`${colors.cyan}Report saved to:${colors.reset} ${reportPath}\n`);
}

export {
  analyzeBundleSizes,
  analyzeComponentSourceFiles,
  formatBytes,
  getFileSize,
};
