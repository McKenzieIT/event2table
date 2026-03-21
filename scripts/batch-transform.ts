#!/usr/bin/env tsx
/**
 * Batch Transform Tool - Enhanced AST-based Code Transformation
 * 
 * Features:
 * - Batch file processing with configurable rules
 * - Transformation preview (dry-run mode)
 * - Automatic rollback functionality
 * - Progress tracking and reporting
 * - Configurable transformation rules
 * 
 * @usage
 *   npx tsx scripts/batch-transform.ts --config transform-config.json
 *   npx tsx scripts/batch-transform.ts --directory frontend/src --dry-run
 *   npx tsx scripts/batch-transform.ts --file frontend/src/components/MyComponent.tsx --preview
 */

import * as fs from 'fs';
import * as path from 'path';
import { parse } from '@babel/parser';
import traverse from '@babel/traverse';
import generate from '@babel/generator';
import * as t from '@babel/types';

// ========================================
// Types and Interfaces
// ========================================

export interface TransformRule {
  id: string;
  name: string;
  description: string;
  componentPattern: string | RegExp;
  importTransform?: {
    from: string | RegExp;
    to: string;
  };
  propTransforms?: PropTransform[];
  componentRename?: {
    from: string;
    to: string;
  };
  enabled?: boolean;
}

export interface PropTransform {
  propName: string | RegExp;
  action: 'rename' | 'remove' | 'add' | 'transform';
  newName?: string;
  newValue?: string | ((oldValue: unknown) => unknown);
  condition?: (propValue: unknown) => boolean;
}

export interface TransformConfig {
  rules: TransformRule[];
  includePatterns: string[];
  excludePatterns: string[];
  fileExtensions: string[];
  backupDir?: string;
  maxBackups?: number;
}

export interface TransformResult {
  filePath: string;
  ruleId: string;
  success: boolean;
  changes: TransformChange[];
  warnings: string[];
  errors: string[];
  originalCode?: string;
  transformedCode?: string;
  backupPath?: string;
}

export interface TransformChange {
  type: 'import' | 'component' | 'prop' | 'other';
  description: string;
  line?: number;
  column?: number;
  before?: string;
  after?: string;
}

export interface BatchProgress {
  totalFiles: number;
  processedFiles: number;
  successfulFiles: number;
  failedFiles: number;
  skippedFiles: number;
  totalChanges: number;
  startTime: Date;
  endTime?: Date;
  currentFile?: string;
}

// ========================================
// Default Transformation Rules
// ========================================

const defaultRules: TransformRule[] = [
  {
    id: 'modal-to-basemodal',
    name: 'Modal to BaseModal Migration',
    description: 'Migrates Modal component to new BaseModal API',
    componentPattern: 'Modal',
    importTransform: {
      from: '@/components/Modal',
      to: '@shared/ui/components/BaseModal'
    },
    componentRename: {
      from: 'Modal',
      to: 'BaseModal'
    },
    propTransforms: [
      { propName: 'visible', action: 'rename', newName: 'isOpen' },
      { propName: 'onClose', action: 'rename', newName: 'onRequestClose' },
      { propName: 'closeOnOverlayClick', action: 'rename', newName: 'shouldCloseOnOverlayClick' }
    ],
    enabled: true
  },
  {
    id: 'table-migration',
    name: 'Table Component Migration',
    description: 'Migrates Table component to new API',
    componentPattern: 'Table',
    importTransform: {
      from: '@/components/Table',
      to: '@shared/ui/components/Table'
    },
    propTransforms: [
      { propName: 'dataSource', action: 'rename', newName: 'data' },
      { propName: 'loading', action: 'rename', newName: 'isLoading' }
    ],
    enabled: true
  },
  {
    id: 'form-migration',
    name: 'Form Component Migration',
    description: 'Migrates Form component to new API',
    componentPattern: 'Form',
    importTransform: {
      from: '@/components/Form',
      to: '@shared/ui/components/Form'
    },
    enabled: true
  },
  {
    id: 'select-migration',
    name: 'Select Component Migration',
    description: 'Migrates Select component to new API',
    componentPattern: 'Select',
    importTransform: {
      from: '@/components/Select',
      to: '@shared/ui/components/Select'
    },
    propTransforms: [
      { propName: 'value', action: 'rename', newName: 'selectedValue' },
      { propName: 'onChange', action: 'rename', newName: 'onSelectionChange' }
    ],
    enabled: true
  }
];

const defaultConfig: TransformConfig = {
  rules: defaultRules,
  includePatterns: ['frontend/src/**/*.tsx', 'frontend/src/**/*.ts'],
  excludePatterns: [
    '**/node_modules/**',
    '**/dist/**',
    '**/build/**',
    '**/*.test.tsx',
    '**/*.test.ts',
    '**/*.spec.tsx',
    '**/*.spec.ts'
  ],
  fileExtensions: ['.ts', '.tsx'],
  backupDir: 'scripts/.transform-backups',
  maxBackups: 10
};

// ========================================
// Batch Transformer Class
// ========================================

export class BatchTransformer {
  private config: TransformConfig;
  private results: TransformResult[] = [];
  private progress: BatchProgress;
  private backupManifest: Map<string, string> = new Map();

  constructor(config: Partial<TransformConfig> = {}) {
    this.config = { ...defaultConfig, ...config };
    this.progress = {
      totalFiles: 0,
      processedFiles: 0,
      successfulFiles: 0,
      failedFiles: 0,
      skippedFiles: 0,
      totalChanges: 0,
      startTime: new Date()
    };
  }

  /**
   * Parse TypeScript/TSX code to AST
   */
  private parseCode(code: string, filePath: string): t.File | null {
    try {
      return parse(code, {
        sourceType: 'module',
        plugins: ['typescript', 'jsx', 'decorators-legacy'],
        allowImportExportEverywhere: true,
        errorRecovery: true
      });
    } catch (error) {
      console.error(`Failed to parse ${filePath}:`, error);
      return null;
    }
  }

  /**
   * Apply a single transformation rule to an AST
   */
  private applyRule(
    ast: t.File,
    rule: TransformRule,
    filePath: string
  ): { changes: TransformChange[]; warnings: string[] } {
    const changes: TransformChange[] = [];
    const warnings: string[] = [];

    // Transform imports
    if (rule.importTransform) {
      traverse(ast, {
        ImportDeclaration: (traversePath) => {
          const source = traversePath.node.source.value;
          const fromPattern = rule.importTransform!.from;
          
          const matches = typeof fromPattern === 'string'
            ? source.includes(fromPattern)
            : fromPattern.test(source);

          if (matches) {
            const oldSource = source;
            traversePath.node.source.value = rule.importTransform!.to;
            changes.push({
              type: 'import',
              description: `Import path transformed`,
              before: oldSource,
              after: rule.importTransform!.to
            });
          }
        }
      });
    }

    // Transform JSX elements
    if (rule.componentPattern || rule.componentRename || rule.propTransforms) {
      traverse(ast, {
        JSXOpeningElement: (traversePath) => {
          const node = traversePath.node;
          
          // Check if this component matches the pattern
          if (!t.isJSXIdentifier(node.name)) return;
          
          const componentName = node.name.name;
          const pattern = rule.componentPattern;
          
          const matches = typeof pattern === 'string'
            ? componentName === pattern
            : pattern.test(componentName);

          if (!matches) return;

          // Rename component
          if (rule.componentRename && componentName === rule.componentRename.from) {
            node.name.name = rule.componentRename.to;
            changes.push({
              type: 'component',
              description: `Component renamed: ${rule.componentRename.from} → ${rule.componentRename.to}`
            });
          }

          // Transform props
          if (rule.propTransforms) {
            node.attributes = node.attributes.map(attr => {
              if (!t.isJSXAttribute(attr) || !t.isJSXIdentifier(attr.name)) {
                return attr;
              }

              const propName = attr.name.name;
              
              for (const propTransform of rule.propTransforms!) {
                const propMatches = typeof propTransform.propName === 'string'
                  ? propName === propTransform.propName
                  : propTransform.propName.test(propName);

                if (!propMatches) continue;

                switch (propTransform.action) {
                  case 'rename':
                    if (propTransform.newName) {
                      const oldName = propName;
                      attr.name.name = propTransform.newName;
                      changes.push({
                        type: 'prop',
                        description: `Prop renamed: ${oldName} → ${propTransform.newName}`
                      });
                    }
                    break;

                  case 'remove':
                    changes.push({
                      type: 'prop',
                      description: `Prop removed: ${propName}`
                    });
                    return null;

                  case 'add':
                    if (propTransform.newName && propTransform.newValue !== undefined) {
                      const value = typeof propTransform.newValue === 'function'
                        ? propTransform.newValue(null)
                        : propTransform.newValue;
                      
                      changes.push({
                        type: 'prop',
                        description: `Prop added: ${propTransform.newName}`
                      });
                      
                      return t.jsxAttribute(
                        t.jsxIdentifier(propTransform.newName),
                        typeof value === 'string'
                          ? t.stringLiteral(value)
                          : t.jsxExpressionContainer(t.booleanLiteral(Boolean(value)))
                      );
                    }
                    break;
                }
              }

              return attr;
            }).filter(Boolean) as Array<t.JSXAttribute | t.JSXSpreadAttribute>;
          }
        }
      });
    }

    return { changes, warnings };
  }

  /**
   * Create backup of original file
   */
  private createBackup(filePath: string, code: string): string | null {
    if (!this.config.backupDir) return null;

    try {
      // Ensure backup directory exists
      if (!fs.existsSync(this.config.backupDir)) {
        fs.mkdirSync(this.config.backupDir, { recursive: true });
      }

      // Create unique backup filename
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const basename = path.basename(filePath);
      const backupName = `${timestamp}_${basename}.backup`;
      const backupPath = path.join(this.config.backupDir, backupName);

      // Write backup
      fs.writeFileSync(backupPath, code, 'utf-8');
      this.backupManifest.set(filePath, backupPath);

      // Clean up old backups if needed
      this.cleanupOldBackups();

      return backupPath;
    } catch (error) {
      console.error(`Failed to create backup for ${filePath}:`, error);
      return null;
    }
  }

  /**
   * Clean up old backups to maintain maxBackups limit
   */
  private cleanupOldBackups(): void {
    if (!this.config.backupDir || !this.config.maxBackups) return;

    try {
      const backupDir = this.config.backupDir;
      const files = fs.readdirSync(backupDir)
        .filter(f => f.endsWith('.backup'))
        .map(f => ({
          name: f,
          path: path.join(backupDir, f),
          time: fs.statSync(path.join(backupDir, f)).mtime.getTime()
        }))
        .sort((a, b) => b.time - a.time);

      // Remove old backups beyond maxBackups
      if (files.length > this.config.maxBackups) {
        files.slice(this.config.maxBackups).forEach(f => {
          fs.unlinkSync(f.path);
        });
      }
    } catch (error) {
      console.error('Failed to cleanup old backups:', error);
    }
  }

  /**
   * Transform a single file
   */
  public transformFile(
    filePath: string,
    options: { dryRun?: boolean; preview?: boolean; rules?: string[] } = {}
  ): TransformResult[] {
    const results: TransformResult[] = [];
    const enabledRules = this.config.rules.filter(r => 
      r.enabled !== false && 
      (!options.rules || options.rules.includes(r.id))
    );

    try {
      // Read file
      const code = fs.readFileSync(filePath, 'utf-8');
      
      // Parse to AST
      const ast = this.parseCode(code, filePath);
      if (!ast) {
        results.push({
          filePath,
          ruleId: 'parse',
          success: false,
          changes: [],
          warnings: [],
          errors: ['Failed to parse file']
        });
        return results;
      }

      // Apply each enabled rule
      let currentCode = code;
      let currentAst = ast;

      for (const rule of enabledRules) {
        const ruleResult: TransformResult = {
          filePath,
          ruleId: rule.id,
          success: false,
          changes: [],
          warnings: [],
          errors: [],
          originalCode: currentCode
        };

        try {
          const { changes, warnings } = this.applyRule(currentAst, rule, filePath);
          ruleResult.changes = changes;
          ruleResult.warnings = warnings;

          if (changes.length > 0) {
            // Generate transformed code
            const output = generate(currentAst, {
              retainLines: false,
              compact: false,
              concise: false
            });

            ruleResult.transformedCode = output.code;
            ruleResult.success = true;
            currentCode = output.code;
          } else {
            ruleResult.warnings.push('No changes detected for this rule');
          }
        } catch (error) {
          ruleResult.errors.push(`Transformation failed: ${error instanceof Error ? error.message : String(error)}`);
        }

        results.push(ruleResult);
      }

    } catch (error) {
      results.push({
        filePath,
        ruleId: 'unknown',
        success: false,
        changes: [],
        warnings: [],
        errors: [`File processing failed: ${error instanceof Error ? error.message : String(error)}`]
      });
    }

    return results;
  }

  /**
   * Transform all files in a directory
   */
  public transformDirectory(
    directoryPath: string,
    options: { dryRun?: boolean; preview?: boolean; rules?: string[] } = {}
  ): TransformResult[] {
    const allResults: TransformResult[] = [];
    const files = this.findFiles(directoryPath);

    this.progress.totalFiles = files.length;
    this.progress.startTime = new Date();

    console.log(`Found ${files.length} files to process\n`);

    for (const file of files) {
      this.progress.currentFile = file;
      const fileResults = this.transformFile(file, options);
      allResults.push(...fileResults);
      this.progress.processedFiles++;

      // Update progress counters
      const fileSuccess = fileResults.some(r => r.success);
      if (fileSuccess) {
        this.progress.successfulFiles++;
      } else if (fileResults.every(r => r.warnings.length > 0 && r.changes.length === 0)) {
        this.progress.skippedFiles++;
      } else {
        this.progress.failedFiles++;
      }

      this.progress.totalChanges += fileResults.reduce((sum, r) => sum + r.changes.length, 0);

      // Show progress
      if (!options.dryRun && !options.preview) {
        const status = fileSuccess ? '✓' : (fileResults.every(r => r.changes.length === 0) ? '○' : '✗');
        console.log(`${status} ${file}`);
      }
    }

    this.progress.endTime = new Date();
    return allResults;
  }

  /**
   * Find files matching config patterns
   */
  private findFiles(directoryPath: string): string[] {
    const files: string[] = [];

    const walk = (currentPath: string) => {
      try {
        const entries = fs.readdirSync(currentPath, { withFileTypes: true });

        for (const entry of entries) {
          const fullPath = path.join(currentPath, entry.name);

          if (entry.isDirectory()) {
            // Check if directory is excluded
            const isExcluded = this.config.excludePatterns.some(pattern => {
              const regex = new RegExp(pattern.replace(/\*/g, '.*'));
              return regex.test(fullPath);
            });

            if (!isExcluded && !['node_modules', '.git', 'dist', 'build'].includes(entry.name)) {
              walk(fullPath);
            }
          } else if (entry.isFile()) {
            const ext = path.extname(entry.name);
            
            if (this.config.fileExtensions.includes(ext)) {
              // Check if file matches include patterns
              const matchesInclude = this.config.includePatterns.some(pattern => {
                const regex = new RegExp(pattern.replace(/\*/g, '.*').replace(/\?/g, '.'));
                return regex.test(fullPath);
              });

              // Check if file is excluded
              const isExcluded = this.config.excludePatterns.some(pattern => {
                const regex = new RegExp(pattern.replace(/\*/g, '.*').replace(/\?/g, '.'));
                return regex.test(fullPath);
              });

              if (matchesInclude && !isExcluded) {
                files.push(fullPath);
              }
            }
          }
        }
      } catch (error) {
        console.error(`Error walking directory ${currentPath}:`, error);
      }
    };

    walk(directoryPath);
    return files;
  }

  /**
   * Apply transformations (write files)
   */
  public applyTransformations(results: TransformResult[], dryRun: boolean): void {
    // Group results by file
    const fileGroups = new Map<string, TransformResult[]>();
    for (const result of results) {
      if (!fileGroups.has(result.filePath)) {
        fileGroups.set(result.filePath, []);
      }
      fileGroups.get(result.filePath)!.push(result);
    }

    // Apply transformations
    for (const [filePath, fileResults] of fileGroups) {
      const successfulResults = fileResults.filter(r => r.success && r.transformedCode);
      
      if (successfulResults.length === 0) continue;

      // Get the final transformed code (from the last successful transformation)
      const finalResult = successfulResults[successfulResults.length - 1];

      if (dryRun) {
        console.log(`\n📄 ${filePath}`);
        console.log('  Changes:');
        for (const result of successfulResults) {
          for (const change of result.changes) {
            console.log(`    ✓ [${result.ruleId}] ${change.description}`);
            if (change.before && change.after) {
              console.log(`      ${change.before} → ${change.after}`);
            }
          }
        }
      } else {
        // Create backup
        const backupPath = this.createBackup(filePath, finalResult.originalCode!);
        
        // Write transformed code
        fs.writeFileSync(filePath, finalResult.transformedCode!, 'utf-8');
        console.log(`✓ Transformed: ${filePath}${backupPath ? ` (backup: ${backupPath})` : ''}`);
      }
    }
  }

  /**
   * Rollback transformations
   */
  public rollback(backupDir?: string): number {
    const backupDirectory = backupDir || this.config.backupDir;
    if (!backupDirectory || !fs.existsSync(backupDirectory)) {
      console.log('No backup directory found');
      return 0;
    }

    let rolledBack = 0;

    for (const [originalPath, backupPath] of this.backupManifest) {
      try {
        if (fs.existsSync(backupPath)) {
          const backupContent = fs.readFileSync(backupPath, 'utf-8');
          fs.writeFileSync(originalPath, backupContent, 'utf-8');
          fs.unlinkSync(backupPath);
          console.log(`↩ Rolled back: ${originalPath}`);
          rolledBack++;
        }
      } catch (error) {
        console.error(`Failed to rollback ${originalPath}:`, error);
      }
    }

    this.backupManifest.clear();
    return rolledBack;
  }

  /**
   * Generate detailed report
   */
  public generateReport(results: TransformResult[]): string {
    const successful = results.filter(r => r.success);
    const failed = results.filter(r => r.errors.length > 0);
    const skipped = results.filter(r => r.warnings.length > 0 && r.changes.length === 0);

    const duration = this.progress.endTime && this.progress.startTime
      ? (this.progress.endTime.getTime() - this.progress.startTime.getTime()) / 1000
      : 0;

    let report = '\n' + '='.repeat(60) + '\n';
    report += 'Batch Transform Report\n';
    report += '='.repeat(60) + '\n\n';

    report += 'Summary:\n';
    report += `  Total Files: ${this.progress.totalFiles}\n`;
    report += `  Processed: ${this.progress.processedFiles}\n`;
    report += `  Successful: ${this.progress.successfulFiles}\n`;
    report += `  Failed: ${this.progress.failedFiles}\n`;
    report += `  Skipped: ${this.progress.skippedFiles}\n`;
    report += `  Total Changes: ${this.progress.totalChanges}\n`;
    report += `  Duration: ${duration.toFixed(2)}s\n\n`;

    // Group changes by rule
    const ruleStats = new Map<string, { count: number; files: string[] }>();
    for (const result of successful) {
      if (!ruleStats.has(result.ruleId)) {
        ruleStats.set(result.ruleId, { count: 0, files: [] });
      }
      const stats = ruleStats.get(result.ruleId)!;
      stats.count += result.changes.length;
      if (!stats.files.includes(result.filePath)) {
        stats.files.push(result.filePath);
      }
    }

    if (ruleStats.size > 0) {
      report += 'Changes by Rule:\n';
      for (const [ruleId, stats] of ruleStats) {
        report += `  ${ruleId}: ${stats.count} changes in ${stats.files.length} files\n`;
      }
      report += '\n';
    }

    if (failed.length > 0) {
      report += 'Failed Files:\n';
      for (const result of failed) {
        report += `  ✗ ${result.filePath}\n`;
        for (const error of result.errors) {
          report += `    Error: ${error}\n`;
        }
      }
      report += '\n';
    }

    report += '='.repeat(60) + '\n';

    return report;
  }

  /**
   * Generate rollback script
   */
  public generateRollbackScript(results: TransformResult[]): string {
    const script: string[] = [
      '#!/bin/bash',
      '# Auto-generated Rollback Script',
      `# Generated at: ${new Date().toISOString()}`,
      '',
      'set -e',
      '',
      'echo "Starting rollback..."',
      ''
    ];

    const fileGroups = new Map<string, TransformResult[]>();
    for (const result of results) {
      if (result.success && result.originalCode) {
        if (!fileGroups.has(result.filePath)) {
          fileGroups.set(result.filePath, []);
        }
        fileGroups.get(result.filePath)!.push(result);
      }
    }

    for (const [filePath, fileResults] of fileGroups) {
      const firstResult = fileResults[0];
      if (firstResult.originalCode) {
        script.push(`# Rollback: ${filePath}`);
        script.push(`cat > '${filePath}' << 'ROLLBACK_EOF'`);
        script.push(firstResult.originalCode);
        script.push('ROLLBACK_EOF');
        script.push(`echo "Restored: ${filePath}"`);
        script.push('');
      }
    }

    script.push('echo "Rollback complete!"');

    return script.join('\n');
  }

  /**
   * Export transformation configuration
   */
  public exportConfig(): string {
    return JSON.stringify(this.config, null, 2);
  }

  /**
   * Import transformation configuration
   */
  public importConfig(configJson: string): void {
    try {
      const config = JSON.parse(configJson);
      this.config = { ...defaultConfig, ...config };
    } catch (error) {
      console.error('Failed to import config:', error);
    }
  }
}

// ========================================
// CLI Interface
// ========================================

interface CLIOptions {
  file?: string;
  directory?: string;
  dryRun?: boolean;
  preview?: boolean;
  config?: string;
  rules?: string[];
  rollback?: boolean;
  backupDir?: string;
  verbose?: boolean;
}

function parseArgs(): CLIOptions {
  const args = process.argv.slice(2);
  const options: CLIOptions = {};

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    switch (arg) {
      case '--file':
      case '-f':
        options.file = args[++i];
        break;
      case '--directory':
      case '-d':
        options.directory = args[++i];
        break;
      case '--dry-run':
      case '-n':
        options.dryRun = true;
        break;
      case '--preview':
      case '-p':
        options.preview = true;
        break;
      case '--config':
      case '-c':
        options.config = args[++i];
        break;
      case '--rules':
      case '-r':
        options.rules = args[++i].split(',');
        break;
      case '--rollback':
        options.rollback = true;
        break;
      case '--backup-dir':
        options.backupDir = args[++i];
        break;
      case '--verbose':
      case '-v':
        options.verbose = true;
        break;
      case '--help':
      case '-h':
        printHelp();
        process.exit(0);
    }
  }

  return options;
}

function printHelp(): void {
  console.log(`
Batch Transform Tool - Enhanced AST-based Code Transformation

Usage:
  npx tsx scripts/batch-transform.ts [options]

Options:
  -f, --file <path>        Transform a single file
  -d, --directory <path>   Transform all files in directory
  -n, --dry-run            Preview changes without writing
  -p, --preview            Show detailed preview of changes
  -c, --config <path>      Load configuration from JSON file
  -r, --rules <ids>        Apply specific rules (comma-separated)
  --rollback               Rollback last transformation
  --backup-dir <path>      Custom backup directory
  -v, --verbose            Show detailed output
  -h, --help               Show this help message

Examples:
  # Preview changes in a directory
  npx tsx scripts/batch-transform.ts --directory frontend/src --dry-run

  # Transform a single file
  npx tsx scripts/batch-transform.ts --file frontend/src/components/MyComponent.tsx

  # Apply specific rules
  npx tsx scripts/batch-transform.ts --directory frontend/src --rules modal-to-basemodal,table-migration

  # Rollback last transformation
  npx tsx scripts/batch-transform.ts --rollback
`);
}

async function main() {
  const options = parseArgs();
  const transformer = new BatchTransformer();

  // Load config if provided
  if (options.config) {
    try {
      const configContent = fs.readFileSync(options.config, 'utf-8');
      transformer.importConfig(configContent);
    } catch (error) {
      console.error(`Failed to load config: ${options.config}`);
      process.exit(1);
    }
  }

  // Handle rollback
  if (options.rollback) {
    const count = transformer.rollback(options.backupDir);
    console.log(`Rolled back ${count} files`);
    process.exit(0);
  }

  // Validate input
  if (!options.file && !options.directory) {
    console.error('Error: Please specify --file or --directory');
    console.log('Use --help for usage information');
    process.exit(1);
  }

  console.log('🚀 Starting batch transformation...\n');

  let results: TransformResult[];

  if (options.file) {
    results = transformer.transformFile(options.file, {
      dryRun: options.dryRun,
      preview: options.preview,
      rules: options.rules
    });
  } else if (options.directory) {
    results = transformer.transformDirectory(options.directory, {
      dryRun: options.dryRun,
      preview: options.preview,
      rules: options.rules
    });
  } else {
    results = [];
  }

  // Apply transformations
  transformer.applyTransformations(results, options.dryRun || options.preview || false);

  // Generate report
  console.log(transformer.generateReport(results));

  // Generate rollback script if not dry run
  if (!options.dryRun && !options.preview && results.some(r => r.success)) {
    const rollbackScript = transformer.generateRollbackScript(results);
    const rollbackPath = 'scripts/rollback-transform.sh';
    fs.writeFileSync(rollbackPath, rollbackScript, 'utf-8');
    fs.chmodSync(rollbackPath, '755');
    console.log(`\n📝 Rollback script generated: ${rollbackPath}`);
  }

  // Exit with appropriate code
  const hasErrors = results.some(r => r.errors.length > 0);
  process.exit(hasErrors ? 1 : 0);
}

// Run if executed directly
if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

export { BatchTransformer, defaultRules, defaultConfig };
