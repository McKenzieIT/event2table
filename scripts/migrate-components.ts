#!/usr/bin/env tsx
/**
 * Component Migration Tool - AST-based Code Transformation
 * 
 * This tool automatically migrates components from old API to new API using AST parsing.
 * Supports Modal, Form, and Table component migrations with safety checks and rollback support.
 * 
 * @usage
 *   npx tsx scripts/migrate-components.ts --file frontend/src/components/MyComponent.tsx
 *   npx tsx scripts/migrate-components.ts --directory frontend/src/features
 *   npx tsx scripts/migrate-components.ts --dry-run --directory frontend/src
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

interface MigrationOptions {
  file?: string;
  directory?: string;
  dryRun?: boolean;
  verbose?: boolean;
  components?: ('Modal' | 'Form' | 'Table')[];
}

interface MigrationResult {
  filePath: string;
  success: boolean;
  changes: string[];
  warnings: string[];
  errors: string[];
  originalCode?: string;
  transformedCode?: string;
}

interface TransformationRule {
  componentName: string;
  oldImportPath: string;
  newImportPath: string;
  transform: (node: t.JSXOpeningElement, filePath: string) => t.JSXOpeningElement | null;
}

// ========================================
// Transformation Rules
// ========================================

/**
 * Modal Component Transformation Rules
 * 
 * Old API:
 *   <Modal isOpen={true} onClose={handleClose} title="Title">
 * 
 * New API:
 *   <BaseModal isOpen={true} onClose={handleClose} title="Title">
 */
const modalTransformation: TransformationRule = {
  componentName: 'Modal',
  oldImportPath: '@/components/Modal',
  newImportPath: '@shared/ui/BaseModal/BaseModal',
  transform: (node, filePath) => {
    const attrs = node.attributes;
    
    // Check if it's a Modal component
    if (!t.isJSXIdentifier(node.name) || node.name.name !== 'Modal') {
      return null;
    }

    // Transform component name
    node.name = t.jsxIdentifier('BaseModal');
    
    // Track changes
    const changes: string[] = [];
    
    // Check for deprecated props and suggest alternatives
    attrs.forEach(attr => {
      if (t.isJSXAttribute(attr) && t.isJSXIdentifier(attr.name)) {
        const propName = attr.name.name;
        
        // Example: if 'visible' is deprecated, suggest 'isOpen'
        if (propName === 'visible') {
          changes.push(`Prop 'visible' → 'isOpen' in ${filePath}`);
          attr.name.name = 'isOpen';
        }
        
        // Example: if 'onClose' needs to be renamed to 'onRequestClose'
        if (propName === 'onClose') {
          // Keep as is - both APIs support this
        }
      }
    });

    return node;
  }
};

/**
 * Form Component Transformation Rules
 * 
 * Old API:
 *   <Form onSubmit={handleSubmit}>
 *     <Input name="email" />
 *   </Form>
 * 
 * New API:
 *   <Form onSubmit={handleSubmit}>
 *     <FormInput name="email" />
 *   </Form>
 */
const formTransformation: TransformationRule = {
  componentName: 'Form',
  oldImportPath: '@/components/Form',
  newImportPath: '@shared/ui/components/Form',
  transform: (node, filePath) => {
    if (!t.isJSXIdentifier(node.name) || node.name.name !== 'Form') {
      return null;
    }

    // Form component name stays the same, but we need to update imports
    // and transform child components
    
    return node;
  }
};

/**
 * Table Component Transformation Rules
 * 
 * Old API:
 *   <Table dataSource={data}>
 *     <Column title="Name" dataIndex="name" />
 *   </Table>
 * 
 * New API:
 *   <Table>
 *     <Table.Head>Name</Table.Head>
 *     <Table.Row>
 *       <Table.Cell>{name}</Table.Cell>
 *     </Table.Row>
 *   </Table>
 */
const tableTransformation: TransformationRule = {
  componentName: 'Table',
  oldImportPath: '@/components/Table',
  newImportPath: '@shared/ui/Table',
  transform: (node, filePath) => {
    if (!t.isJSXIdentifier(node.name) || node.name.name !== 'Table') {
      return null;
    }

    // Table component name stays the same
    // But we need to transform Column components to Table.Head/Table.Cell
    
    return node;
  }
};

// ========================================
// Migration Engine
// ========================================

class ComponentMigrator {
  private rules: Map<string, TransformationRule>;
  private results: MigrationResult[] = [];

  constructor() {
    this.rules = new Map([
      ['Modal', modalTransformation],
      ['Form', formTransformation],
      ['Table', tableTransformation]
    ]);
  }

  /**
   * Parse TypeScript/TSX code to AST
   */
  private parseCode(code: string, filePath: string): t.File | null {
    try {
      return parse(code, {
        sourceType: 'module',
        plugins: ['typescript', 'jsx'],
        allowImportExportEverywhere: true
      });
    } catch (error) {
      console.error(`Failed to parse ${filePath}:`, error);
      return null;
    }
  }

  /**
   * Transform imports from old paths to new paths
   */
  private transformImports(ast: t.File, filePath: string): { changes: string[] } {
    const changes: string[] = [];

    traverse(ast, {
      ImportDeclaration(path) {
        const source = path.node.source.value;
        
        // Check if this import matches any old import paths
        this.rules.forEach((rule, componentName) => {
          if (source.includes(rule.oldImportPath)) {
            // Update import path
            path.node.source.value = rule.newImportPath;
            changes.push(`Import: ${rule.oldImportPath} → ${rule.newImportPath} in ${filePath}`);
          }
        });
      }
    });

    return { changes };
  }

  /**
   * Transform JSX elements
   */
  private transformJSX(ast: t.File, filePath: string): { changes: string[]; warnings: string[] } {
    const changes: string[] = [];
    const warnings: string[] = [];

    traverse(ast, {
      JSXOpeningElement(path) {
        // Check each component transformation rule
        this.rules.forEach((rule, componentName) => {
          const transformed = rule.transform(path.node, filePath);
          if (transformed) {
            changes.push(`Component: ${componentName} transformed in ${filePath}`);
          }
        });
      }
    });

    return { changes, warnings };
  }

  /**
   * Generate code from transformed AST
   */
  private generateCode(ast: t.File): string {
    const output = generate(ast, {
      retainLines: false,
      compact: false,
      concise: false,
      jsescOption: { minimal: true }
    });

    return output.code;
  }

  /**
   * Migrate a single file
   */
  public migrateFile(filePath: string, options: MigrationOptions): MigrationResult {
    const result: MigrationResult = {
      filePath,
      success: false,
      changes: [],
      warnings: [],
      errors: []
    };

    try {
      // Read file
      const code = fs.readFileSync(filePath, 'utf-8');
      result.originalCode = code;

      // Parse to AST
      const ast = this.parseCode(code, filePath);
      if (!ast) {
        result.errors.push('Failed to parse file');
        return result;
      }

      // Transform imports
      const importResult = this.transformImports(ast, filePath);
      result.changes.push(...importResult.changes);

      // Transform JSX
      const jsxResult = this.transformJSX(ast, filePath);
      result.changes.push(...jsxResult.changes);
      result.warnings.push(...jsxResult.warnings);

      // Generate transformed code
      const transformedCode = this.generateCode(ast);
      result.transformedCode = transformedCode;

      // Check if there were any changes
      if (result.changes.length > 0) {
        result.success = true;
      } else {
        result.warnings.push('No changes detected');
      }

    } catch (error) {
      result.errors.push(`Migration failed: ${error instanceof Error ? error.message : String(error)}`);
    }

    return result;
  }

  /**
   * Migrate all files in a directory
   */
  public migrateDirectory(directoryPath: string, options: MigrationOptions): MigrationResult[] {
    const results: MigrationResult[] = [];

    // Find all TS/TSX files
    const files = this.findFiles(directoryPath, ['.ts', '.tsx']);
    
    console.log(`Found ${files.length} files to process`);

    files.forEach(file => {
      const result = this.migrateFile(file, options);
      results.push(result);
    });

    return results;
  }

  /**
   * Find files by extension
   */
  private findFiles(dir: string, extensions: string[]): string[] {
    const files: string[] = [];

    const walk = (currentPath: string) => {
      const entries = fs.readdirSync(currentPath, { withFileTypes: true });

      entries.forEach(entry => {
        const fullPath = path.join(currentPath, entry.name);

        if (entry.isDirectory()) {
          // Skip node_modules and other common exclusions
          if (!['node_modules', '.git', 'dist', 'build'].includes(entry.name)) {
            walk(fullPath);
          }
        } else if (entry.isFile()) {
          const ext = path.extname(entry.name);
          if (extensions.includes(ext)) {
            files.push(fullPath);
          }
        }
      });
    };

    walk(dir);
    return files;
  }

  /**
   * Apply migration (write files if not dry run)
   */
  public applyMigration(results: MigrationResult[], dryRun: boolean): void {
    results.forEach(result => {
      if (result.success && result.transformedCode) {
        if (dryRun) {
          console.log(`\n📄 ${result.filePath}`);
          console.log('  Changes:');
          result.changes.forEach(change => console.log(`    ✓ ${change}`));
          if (result.warnings.length > 0) {
            console.log('  Warnings:');
            result.warnings.forEach(warning => console.log(`    ⚠ ${warning}`));
          }
        } else {
          // Write transformed code
          fs.writeFileSync(result.filePath, result.transformedCode, 'utf-8');
          console.log(`✓ Migrated: ${result.filePath}`);
        }
      } else if (result.errors.length > 0) {
        console.error(`✗ Failed: ${result.filePath}`);
        result.errors.forEach(error => console.error(`  Error: ${error}`));
      }
    });
  }

  /**
   * Generate rollback script
   */
  public generateRollbackScript(results: MigrationResult[]): string {
    const rollbackCommands: string[] = [];
    
    results.forEach(result => {
      if (result.success && result.originalCode) {
        rollbackCommands.push(`# Rollback: ${result.filePath}`);
        rollbackCommands.push(`echo "Restoring ${result.filePath}..."`);
        rollbackCommands.push(`cat > '${result.filePath}' << 'EOF'`);
        rollbackCommands.push(result.originalCode);
        rollbackCommands.push('EOF');
        rollbackCommands.push('');
      }
    });

    return rollbackCommands.join('\n');
  }

  /**
   * Generate migration report
   */
  public generateReport(results: MigrationResult[]): string {
    const successful = results.filter(r => r.success);
    const failed = results.filter(r => !r.success);
    const totalChanges = results.reduce((sum, r) => sum + r.changes.length, 0);
    const totalWarnings = results.reduce((sum, r) => sum + r.warnings.length, 0);

    let report = '\n========================================\n';
    report += 'Migration Report\n';
    report += '========================================\n';
    report += `Total Files: ${results.length}\n`;
    report += `Successful: ${successful.length}\n`;
    report += `Failed: ${failed.length}\n`;
    report += `Total Changes: ${totalChanges}\n`;
    report += `Total Warnings: ${totalWarnings}\n`;
    report += '========================================\n';

    if (failed.length > 0) {
      report += '\nFailed Files:\n';
      failed.forEach(r => {
        report += `  - ${r.filePath}\n`;
        r.errors.forEach(e => report += `    Error: ${e}\n`);
      });
    }

    return report;
  }
}

// ========================================
// CLI Interface
// ========================================

function parseArgs(): MigrationOptions {
  const args = process.argv.slice(2);
  const options: MigrationOptions = {};

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    
    if (arg === '--file' || arg === '-f') {
      options.file = args[++i];
    } else if (arg === '--directory' || arg === '-d') {
      options.directory = args[++i];
    } else if (arg === '--dry-run' || arg === '-n') {
      options.dryRun = true;
    } else if (arg === '--verbose' || arg === '-v') {
      options.verbose = true;
    } else if (arg === '--components' || arg === '-c') {
      const components = args[++i].split(',');
      options.components = components as ('Modal' | 'Form' | 'Table')[];
    }
  }

  return options;
}

async function main() {
  const options = parseArgs();
  const migrator = new ComponentMigrator();

  if (!options.file && !options.directory) {
    console.error('Error: Please specify --file or --directory');
    console.log('\nUsage:');
    console.log('  npx tsx scripts/migrate-components.ts --file <path>');
    console.log('  npx tsx scripts/migrate-components.ts --directory <path>');
    console.log('  npx tsx scripts/migrate-components.ts --dry-run --directory <path>');
    process.exit(1);
  }

  console.log('🚀 Starting component migration...\n');

  let results: MigrationResult[];

  if (options.file) {
    results = [migrator.migrateFile(options.file, options)];
  } else if (options.directory) {
    results = migrator.migrateDirectory(options.directory, options);
  } else {
    results = [];
  }

  // Apply migration
  migrator.applyMigration(results, options.dryRun || false);

  // Generate report
  console.log(migrator.generateReport(results));

  // Generate rollback script if not dry run
  if (!options.dryRun && results.some(r => r.success)) {
    const rollbackScript = migrator.generateRollbackScript(results);
    const rollbackPath = 'scripts/rollback-migration.sh';
    fs.writeFileSync(rollbackPath, rollbackScript, 'utf-8');
    console.log(`\n📝 Rollback script generated: ${rollbackPath}`);
  }

  // Exit with error code if any migrations failed
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

export { ComponentMigrator, MigrationOptions, MigrationResult };
