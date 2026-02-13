/**
 * Hive SQL Linter
 *
 * Provides SQL syntax validation and error detection for Hive SQL.
 * Integrates with CodeMirror's lint extension for real-time feedback.
 */

import { Diagnostic } from '@codemirror/lint';

/**
 * SQL keywords for validation
 */
const SQL_KEYWORDS = [
  'SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'FULL',
  'ON', 'AND', 'OR', 'NOT', 'IN', 'LIKE', 'BETWEEN', 'NULL', 'IS', 'EXISTS',
  'GROUP', 'BY', 'HAVING', 'ORDER', 'ASC', 'DESC', 'LIMIT', 'OFFSET',
  'INSERT', 'UPDATE', 'DELETE', 'INTO', 'VALUES', 'SET',
  'CREATE', 'ALTER', 'DROP', 'TABLE', 'VIEW', 'INDEX', 'DATABASE',
  'UNION', 'ALL', 'DISTINCT', 'AS', 'WITH', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END',
  // Hive-specific
  'LATERAL', 'VIEW', 'EXPLODE', 'POSEXPLODE', 'CLUSTER', 'DISTRIBUTE', 'SORT',
  'OVER', 'PARTITION', 'RANK', 'ROW_NUMBER', 'DENSE_RANK', 'PERCENT_RANK', 'NTILE',
  'LEAD', 'LAG', 'FIRST_VALUE', 'LAST_VALUE', 'ARRAY', 'MAP', 'STRUCT', 'UNIONTYPE'
];

/**
 * Common function patterns for validation
 */
const FUNCTION_PATTERNS = [
  'get_json_object', 'nvl', 'coalesce', 'concat', 'split', 'substr', 'substring',
  'trim', 'upper', 'lower', 'length', 'to_date', 'date_format', 'from_unixtime',
  'unix_timestamp', 'year', 'month', 'day', 'hour', 'minute', 'second',
  'count', 'sum', 'avg', 'min', 'max', 'grouping', 'rollup', 'cube'
];

/**
 * Check for common SQL syntax errors
 */
function validateBasicSyntax(sql: string): Diagnostic[] {
  const diagnostics: Diagnostic[] = [];
  const lines = sql.split('\n');

  lines.forEach((line, lineIndex) => {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('--')) return;

    // Check for unbalanced parentheses
    const openParens = (line.match(/\(/g) || []).length;
    const closeParens = (line.match(/\)/g) || []).length;
    if (openParens !== closeParens) {
      diagnostics.push({
        from: sql.indexOf(line),
        to: sql.indexOf(line) + line.length,
        severity: 'warning',
        message: 'Unbalanced parentheses detected'
      });
    }

    // Check for common syntax errors
    if (trimmed.includes(',,') || trimmed.includes('(,')) {
      diagnostics.push({
        from: sql.indexOf(line),
        to: sql.indexOf(line) + line.length,
        severity: 'error',
        message: 'Syntax error: double comma or comma after opening parenthesis'
      });
    }

    // Check for SELECT without FROM (basic check)
    if (trimmed.toUpperCase().includes('SELECT') && !trimmed.toUpperCase().includes('FROM')) {
      // Ignore if it's a subquery or UNION
      if (!trimmed.toUpperCase().includes('UNION') && !trimmed.includes('(')) {
        diagnostics.push({
          from: sql.indexOf(line),
          to: sql.indexOf(line) + line.length,
          severity: 'warning',
          message: 'SELECT statement should typically include FROM clause'
        });
      }
    }

    // Check for missing quotes in string literals
    const stringMatches = line.match(/'[^']*'/g);
    if (stringMatches) {
      stringMatches.forEach(match => {
        if (match.endsWith("'")) return; // Properly closed
        diagnostics.push({
          from: sql.indexOf(line) + line.indexOf(match),
          to: sql.indexOf(line) + line.indexOf(match) + match.length,
          severity: 'error',
          message: 'Unclosed string literal'
        });
      });
    }
  });

  return diagnostics;
}

/**
 * Validate Hive SQL specific syntax
 */
function validateHiveSyntax(sql: string): Diagnostic[] {
  const diagnostics: Diagnostic[] = [];
  const upperSQL = sql.toUpperCase();

  // Check for LATERAL VIEW without EXPLODE
  if (upperSQL.includes('LATERAL VIEW') && !upperSQL.includes('EXPLODE') && !upperSQL.includes('POSEXPLODE')) {
    diagnostics.push({
      from: 0,
      to: sql.length,
      severity: 'warning',
      message: 'LATERAL VIEW should typically be used with EXPLODE or POSEXPLODE'
    });
  }

  // Check for window functions without OVER
  const windowFunctions = ['RANK', 'ROW_NUMBER', 'DENSE_RANK', 'PERCENT_RANK', 'NTILE', 'LEAD', 'LAG', 'FIRST_VALUE', 'LAST_VALUE'];
  windowFunctions.forEach(func => {
    const regex = new RegExp(`\\b${func}\\s*\\(`, 'gi');
    const matches = sql.match(regex);
    if (matches) {
      matches.forEach(match => {
        const index = sql.toUpperCase().indexOf(match);
        // Check if OVER is nearby
        const context = sql.substring(index, index + 100);
        if (!context.toUpperCase().includes('OVER')) {
          diagnostics.push({
            from: index,
            to: index + match.length,
            severity: 'warning',
            message: `Window function ${func} should be used with OVER clause`
          });
        }
      });
    }
  });

  // Check for CREATE VIEW without OR REPLACE
  if (upperSQL.includes('CREATE VIEW') && !upperSQL.includes('CREATE OR REPLACE VIEW')) {
    diagnostics.push({
      from: 0,
      to: sql.length,
      severity: 'info',
      message: 'Consider using CREATE OR REPLACE VIEW for safer view updates'
    });
  }

  return diagnostics;
}

/**
 * Main linting function for Hive SQL
 *
 * @param sql - SQL string to validate
 * @returns Array of diagnostics (errors, warnings, info)
 */
export function lintHQL(sql: string): Diagnostic[] {
  const diagnostics: Diagnostic[] = [];

  // Skip empty or whitespace-only SQL
  if (!sql || sql.trim().length === 0) {
    return diagnostics;
  }

  // Basic syntax validation
  diagnostics.push(...validateBasicSyntax(sql));

  // Hive-specific validation
  diagnostics.push(...validateHiveSyntax(sql));

  return diagnostics;
}

/**
 * Create a CodeMirror linter extension
 * This function returns a linter that can be used with @codemirror/lint
 */
export function createHiveLinter() {
  return (view: any) => {
    const sql = view.state.doc.toString();
    const diagnostics = lintHQL(sql);
    return diagnostics;
  };
}

/**
 * Quick validation for non-editor use (e.g., before save)
 *
 * @param sql - SQL string to validate
 * @returns Object with validation result and errors
 */
export function validateHQLQuick(sql: string): {
  valid: boolean;
  errors: string[];
  warnings: string[];
} {
  const diagnostics = lintHQL(sql);

  const errors = diagnostics
    .filter(d => d.severity === 'error')
    .map(d => d.message || 'Unknown error');

  const warnings = diagnostics
    .filter(d => d.severity === 'warning')
    .map(d => d.message || 'Unknown warning');

  return {
    valid: errors.length === 0,
    errors,
    warnings
  };
}
