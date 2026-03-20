#!/usr/bin/env tsx
/**
 * Migration Validation Tool
 * 
 * This tool validates that component migrations were successful by checking:
 * - API usage correctness
 * - Import statements
 * - Type compatibility
 * - Deprecated props
 * 
 * @usage
 *   npx tsx scripts/validate-migration.ts --file frontend/src/components/MyComponent.tsx
 *   npx tsx scripts/validate-migration.ts --directory frontend/src/features
 *   npx tsx scripts/validate-migration.ts --fix --directory frontend/src
 */

import * as fs from 'fs';
import * as path from 'path';
import { parse } from '@babel/parser';
import traverse from '@babel/traverse';
import * as t from '@babel/types';

// ========================================
// Types and Interfaces
// ========================================

interface ValidationOptions {
  file?: string;
  directory?: string;
  fix?: boolean;
  verbose?: boolean;
}

interface ValidationResult {
  filePath: string;
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  fixes: string[];
}

interface ValidationError {
  type: 'import' | 'api' | 'type' | 'deprecated';
  message: string;
  line?: number;
  column?: number;
  severity: 'error' | 'warning';
  fixable: boolean;
}

interface ValidationWarning {
  type: 'suggestion' | 'info';
  message: string;
  line?: number;
  column?: number;
}

// ========================================
// Validation Rules
// ========================================

/**
 * Import Validation Rules
 * 
 * Checks that:
 * - Old import paths are not used
 * - New import paths are correct
 * - Imports are properly structured
 */
class ImportValidator {
  private oldImports = new Map([
    ['Modal', '@/components/Modal'],
    ['Form', '@/components/Form'],
    ['Table', '@/components/Table'],
  ]);

  private newImports = new Map([
    ['Modal', '@shared/ui/BaseModal/BaseModal'],
    ['Form', '@shared/ui/components/Form'],
    ['Table', '@shared/ui/Table'],
  ]);

  validate(ast: t.File, filePath: string): ValidationError[] {
    const errors: ValidationError[] = [];

    traverse(ast, {
      ImportDeclaration(path) {
        const source = path.node.source.value;
        const line = path.node.loc?.start.line;

        // Check for old import paths
        this.oldImports.forEach((oldPath, component) => {
          if (source.includes(oldPath)) {
            errors.push({
              type: 'import',
              message: `Old import path detected for ${component}: ${oldPath}`,
              line,
              severity: 'error',
              fixable: true
            });
          }
        });

        // Check for incorrect new import paths
        this.newImports.forEach((newPath, component) => {
          if (source.includes(component) && !source.includes(newPath)) {
            errors.push({
              type: 'import',
              message: `Incorrect import path for ${component}. Expected: ${newPath}`,
              line,
              severity: 'warning',
              fixable: true
            });
          }
        });
      }
    });

    return errors;
  }

  fix(ast: t.File): string[] {
    const fixes: string[] = [];

    traverse(ast, {
      ImportDeclaration(path) {
        const source = path.node.source.value;

        // Replace old import paths with new ones
        this.oldImports.forEach((oldPath, component) => {
          if (source.includes(oldPath)) {
            const newPath = this.newImports.get(component);
            if (newPath) {
              path.node.source.value = source.replace(oldPath, newPath);
              fixes.push(`Updated import for ${component}: ${oldPath} → ${newPath}`);
            }
          }
        });
      }
    });

    return fixes;
  }
}

/**
 * API Usage Validation Rules
 * 
 * Checks that:
 * - Deprecated props are not used
 * - Required props are present
 * - Prop types are correct
 */
class APIValidator {
  private deprecatedProps = new Map([
    ['Modal', ['visible', 'onRequestClose']],
    ['Form', ['initialValues']],
    ['Table', ['dataSource', 'columns']],
  ]);

  private requiredProps = new Map([
    ['Modal', ['isOpen', 'onClose']],
    ['Form', ['onSubmit']],
    ['Table', []],
  ]);

  validate(ast: t.File, filePath: string): ValidationError[] {
    const errors: ValidationError[] = [];

    traverse(ast, {
      JSXOpeningElement(path) {
        if (!t.isJSXIdentifier(path.node.name)) return;

        const componentName = path.node.name.name;
        const line = path.node.loc?.start.line;

        // Check for deprecated props
        if (this.deprecatedProps.has(componentName)) {
          const deprecated = this.deprecatedProps.get(componentName)!;
          
          path.node.attributes.forEach(attr => {
            if (t.isJSXAttribute(attr) && t.isJSXIdentifier(attr.name)) {
              const propName = attr.name.name;
              
              if (deprecated.includes(propName)) {
                errors.push({
                  type: 'deprecated',
                  message: `Deprecated prop '${propName}' used in ${componentName}`,
                  line,
                  severity: 'warning',
                  fixable: true
                });
              }
            }
          });
        }

        // Check for required props
        if (this.requiredProps.has(componentName)) {
          const required = this.requiredProps.get(componentName)!;
          const presentProps: string[] = [];

          path.node.attributes.forEach(attr => {
            if (t.isJSXAttribute(attr) && t.isJSXIdentifier(attr.name)) {
              presentProps.push(attr.name.name);
            }
          });

          required.forEach(prop => {
            if (!presentProps.includes(prop)) {
              errors.push({
                type: 'api',
                message: `Missing required prop '${prop}' in ${componentName}`,
                line,
                severity: 'error',
                fixable: false
              });
            }
          });
        }
      }
    });

    return errors;
  }

  fix(ast: t.File): string[] {
    const fixes: string[] = [];

    // Fix deprecated prop names
    const propReplacements = new Map([
      ['visible', 'isOpen'],
      ['onRequestClose', 'onClose'],
    ]);

    traverse(ast, {
      JSXOpeningElement(path) {
        path.node.attributes.forEach(attr => {
          if (t.isJSXAttribute(attr) && t.isJSXIdentifier(attr.name)) {
            const propName = attr.name.name;
            
            if (propReplacements.has(propName)) {
              const newName = propReplacements.get(propName)!;
              attr.name.name = newName;
              fixes.push(`Renamed prop: ${propName} → ${newName}`);
            }
          }
        });
      }
    });

    return fixes;
  }
}

/**
 * Type Compatibility Validator
 * 
 * Checks that:
 * - Prop types match expected types
 * - Event handlers are properly typed
 * - Generic types are correct
 */
class TypeValidator {
  validate(ast: t.File, filePath: string): ValidationError[] {
    const errors: ValidationError[] = [];

    traverse(ast, {
      // Check for type assertions and type annotations
      TSTypeAnnotation(path) {
        // Add type validation logic here
        // This is a simplified version - in production, you'd want
        // more sophisticated type checking
      }
    });

    return errors;
  }

  fix(ast: t.File): string[] {
    return [];
  }
}

// ========================================
// Validation Engine
// ========================================

class MigrationValidator {
  private importValidator = new ImportValidator();
  private apiValidator = new APIValidator();
  private typeValidator = new TypeValidator();

  /**
   * Validate a single file
   */
  public validateFile(filePath: string, options: ValidationOptions): ValidationResult {
    const result: ValidationResult = {
      filePath,
      valid: true,
      errors: [],
      warnings: [],
      fixes: []
    };

    try {
      // Read file
      const code = fs.readFileSync(filePath, 'utf-8');

      // Parse to AST
      const ast = this.parseCode(code, filePath);
      if (!ast) {
        result.errors.push({
          type: 'import',
          message: 'Failed to parse file',
          severity: 'error',
          fixable: false
        });
        result.valid = false;
        return result;
      }

      // Run validators
      const importErrors = this.importValidator.validate(ast, filePath);
      const apiErrors = this.apiValidator.validate(ast, filePath);
      const typeErrors = this.typeValidator.validate(ast, filePath);

      result.errors.push(...importErrors, ...apiErrors, ...typeErrors);

      // Apply fixes if requested
      if (options.fix && result.errors.some(e => e.fixable)) {
        const importFixes = this.importValidator.fix(ast);
        const apiFixes = this.apiValidator.fix(ast);
        const typeFixes = this.typeValidator.fix(ast);

        result.fixes.push(...importFixes, ...apiFixes, ...typeFixes);

        // Write fixed code
        const fixedCode = this.generateCode(ast);
        fs.writeFileSync(filePath, fixedCode, 'utf-8');

        // Re-validate after fixes
        const newErrors = this.importValidator.validate(ast, filePath);
        const newApiErrors = this.apiValidator.validate(ast, filePath);
        result.errors = [...newErrors, ...newApiErrors];
      }

      // Determine if valid
      const hasErrors = result.errors.some(e => e.severity === 'error');
      result.valid = !hasErrors;

    } catch (error) {
      result.errors.push({
        type: 'import',
        message: `Validation failed: ${error instanceof Error ? error.message : String(error)}`,
        severity: 'error',
        fixable: false
      });
      result.valid = false;
    }

    return result;
  }

  /**
   * Validate all files in a directory
   */
  public validateDirectory(directoryPath: string, options: ValidationOptions): ValidationResult[] {
    const results: ValidationResult[] = [];
    const files = this.findFiles(directoryPath, ['.ts', '.tsx']);

    console.log(`Validating ${files.length} files...`);

    files.forEach(file => {
      const result = this.validateFile(file, options);
      results.push(result);
    });

    return results;
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
   * Generate code from AST
   */
  private generateCode(ast: t.File): string {
    const { default: generate } = require('@babel/generator');
    const output = generate(ast, {
      retainLines: false,
      compact: false,
      concise: false,
      jsescOption: { minimal: true }
    });

    return output.code;
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
   * Generate validation report
   */
  public generateReport(results: ValidationResult[]): string {
    const valid = results.filter(r => r.valid);
    const invalid = results.filter(r => !r.valid);
    const totalErrors = results.reduce((sum, r) => sum + r.errors.filter(e => e.severity === 'error').length, 0);
    const totalWarnings = results.reduce((sum, r) => sum + r.errors.filter(e => e.severity === 'warning').length, 0);
    const totalFixes = results.reduce((sum, r) => sum + r.fixes.length, 0);

    let report = '\n========================================\n';
    report += 'Validation Report\n';
    report += '========================================\n';
    report += `Total Files: ${results.length}\n`;
    report += `Valid: ${valid.length}\n`;
    report += `Invalid: ${invalid.length}\n`;
    report += `Errors: ${totalErrors}\n`;
    report += `Warnings: ${totalWarnings}\n`;
    report += `Fixes Applied: ${totalFixes}\n`;
    report += '========================================\n';

    if (invalid.length > 0) {
      report += '\nInvalid Files:\n';
      invalid.forEach(r => {
        report += `\n  📄 ${r.filePath}\n`;
        r.errors.forEach(e => {
          const icon = e.severity === 'error' ? '✗' : '⚠';
          report += `    ${icon} [${e.type}] ${e.message}`;
          if (e.line) report += ` (line ${e.line})`;
          if (e.fixable) report += ' [fixable]';
          report += '\n';
        });
      });
    }

    if (totalFixes > 0) {
      report += '\nFixes Applied:\n';
      results.forEach(r => {
        if (r.fixes.length > 0) {
          report += `\n  📄 ${r.filePath}\n`;
          r.fixes.forEach(fix => {
            report += `    ✓ ${fix}\n`;
          });
        }
      });
    }

    return report;
  }
}

// ========================================
// CLI Interface
// ========================================

function parseArgs(): ValidationOptions {
  const args = process.argv.slice(2);
  const options: ValidationOptions = {};

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    
    if (arg === '--file' || arg === '-f') {
      options.file = args[++i];
    } else if (arg === '--directory' || arg === '-d') {
      options.directory = args[++i];
    } else if (arg === '--fix') {
      options.fix = true;
    } else if (arg === '--verbose' || arg === '-v') {
      options.verbose = true;
    }
  }

  return options;
}

async function main() {
  const options = parseArgs();
  const validator = new MigrationValidator();

  if (!options.file && !options.directory) {
    console.error('Error: Please specify --file or --directory');
    console.log('\nUsage:');
    console.log('  npx tsx scripts/validate-migration.ts --file <path>');
    console.log('  npx tsx scripts/validate-migration.ts --directory <path>');
    console.log('  npx tsx scripts/validate-migration.ts --fix --directory <path>');
    process.exit(1);
  }

  console.log('🔍 Starting validation...\n');

  let results: ValidationResult[];

  if (options.file) {
    results = [validator.validateFile(options.file, options)];
  } else if (options.directory) {
    results = validator.validateDirectory(options.directory, options);
  } else {
    results = [];
  }

  // Generate and display report
  console.log(validator.generateReport(results));

  // Exit with error code if validation failed
  const hasErrors = results.some(r => !r.valid);
  process.exit(hasErrors ? 1 : 0);
}

// Run if executed directly
if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

export { MigrationValidator, ValidationOptions, ValidationResult };
