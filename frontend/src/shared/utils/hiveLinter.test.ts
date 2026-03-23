// @ts-nocheck - TypeScript strict mode disabled for test files
/**
 * hiveLinter.test.ts
 * Unit tests for Hive SQL linter
 */

import { Diagnostic } from '@codemirror/lint';
import { describe, it, expect } from 'vitest';

import { lintHQL, createHiveLinter, validateHQLQuick } from './hiveLinter';

describe('hiveLinter', () => {
  describe('lintHQL', () => {
    it('should return empty array for empty input', () => {
      const result = lintHQL('');
      expect(result).toEqual([]);
    });

    it('should return empty array for whitespace-only input', () => {
      const result = lintHQL('   \n\n   ');
      expect(result).toEqual([]);
    });

    it('should detect unbalanced parentheses', () => {
      const sql = 'SELECT * FROM table WHERE (id = 1';
      const result = lintHQL(sql);
      const warning = result.find(d => d.message === 'Unbalanced parentheses detected');
      expect(warning).toBeDefined();
      expect(warning?.severity).toBe('warning');
    });

    it('should detect double comma syntax error', () => {
      const sql = 'SELECT id,, name FROM table';
      const result = lintHQL(sql);
      const error = result.find(d => d.message.includes('double comma'));
      expect(error).toBeDefined();
      expect(error?.severity).toBe('error');
    });

    it('should detect comma after opening parenthesis', () => {
      const sql = 'SELECT (, id) FROM table';
      const result = lintHQL(sql);
      const error = result.find(d => d.message.includes('comma after opening'));
      expect(error).toBeDefined();
      expect(error?.severity).toBe('error');
    });

    it('should warn about SELECT without FROM', () => {
      const sql = 'SELECT id, name';
      const result = lintHQL(sql);
      const warning = result.find(d => d.message.includes('FROM clause'));
      expect(warning).toBeDefined();
      expect(warning?.severity).toBe('warning');
    });

    it('should not warn about SELECT without FROM in UNION', () => {
      const sql = 'SELECT id FROM table1 UNION SELECT name FROM table2';
      const result = lintHQL(sql);
      const fromWarning = result.find(d => d.message.includes('FROM clause'));
      expect(fromWarning).toBeUndefined();
    });

    it('should not warn about SELECT without FROM in subquery', () => {
      const sql = 'SELECT * FROM (SELECT id FROM table)';
      const result = lintHQL(sql);
      const fromWarning = result.find(d => d.message.includes('FROM clause'));
      expect(fromWarning).toBeUndefined();
    });

    it('should detect unclosed string literals', () => {
      const sql = "SELECT * FROM table WHERE name = 'test";
      const result = lintHQL(sql);
      const error = result.find(d => d.message === 'Unclosed string literal');
      expect(error).toBeDefined();
      expect(error?.severity).toBe('error');
    });

    describe('Hive-specific validations', () => {
      it('should warn about LATERAL VIEW without EXPLODE', () => {
        const sql = 'SELECT * FROM table LATERAL VIEW some_func() AS col';
        const result = lintHQL(sql);
        const warning = result.find(d => d.message.includes('EXPLODE'));
        expect(warning).toBeDefined();
        expect(warning?.severity).toBe('warning');
      });

      it('should not warn about LATERAL VIEW with EXPLODE', () => {
        const sql = 'SELECT * FROM table LATERAL VIEW EXPLODE(arr) AS col';
        const result = lintHQL(sql);
        const explodeWarning = result.find(d => d.message.includes('should typically be used'));
        expect(explodeWarning).toBeUndefined();
      });

      it('should warn about window functions without OVER', () => {
        const sql = 'SELECT RANK() FROM table';
        const result = lintHQL(sql);
        const warning = result.find(d => d.message.includes('OVER clause'));
        expect(warning).toBeDefined();
        expect(warning?.severity).toBe('warning');
      });

      it('should not warn about window functions with OVER', () => {
        const sql = 'SELECT RANK() OVER (ORDER BY id) FROM table';
        const result = lintHQL(sql);
        const overWarning = result.find(d => d.message.includes('OVER clause'));
        expect(overWarning).toBeUndefined();
      });

      it('should suggest CREATE OR REPLACE VIEW', () => {
        const sql = 'CREATE VIEW view_name AS SELECT * FROM table';
        const result = lintHQL(sql);
        const info = result.find(d => d.message.includes('CREATE OR REPLACE'));
        expect(info).toBeDefined();
        expect(info?.severity).toBe('info');
      });

      it('should not suggest if already using CREATE OR REPLACE', () => {
        const sql = 'CREATE OR REPLACE VIEW view_name AS SELECT * FROM table';
        const result = lintHQL(sql);
        const info = result.find(d => d.message.includes('CREATE OR REPLACE'));
        expect(info).toBeUndefined();
      });
    });

    describe('multiple diagnostics', () => {
      it('should return multiple diagnostics for multiple issues', () => {
        const sql = "SELECT id,, name FROM table WHERE (value = 'test";
        const result = lintHQL(sql);
        expect(result.length).toBeGreaterThan(1);
      });

      it('should include different severity levels', () => {
        const sql = "CREATE VIEW v AS SELECT id,, name FROM table LATERAL VIEW func() AS col";
        const result = lintHQL(sql);
        const severities = new Set(result.map(d => d.severity));
        expect(severities.has('error')).toBe(true);
        expect(severities.has('warning') || severities.has('info')).toBe(true);
      });
    });

    describe('edge cases', () => {
      it('should ignore comment lines', () => {
        const sql = '-- This is a comment\nSELECT * FROM table';
        const result = lintHQL(sql);
        // Should not detect issues in comments
        expect(result.every(d => d.from >= sql.indexOf('SELECT'))).toBe(true);
      });

      it('should handle very long SQL statements', () => {
        const columns = Array.from({ length: 100 }, (_, i) => `col${i}`).join(', ');
        const sql = `SELECT ${columns} FROM table WHERE id = 1`;
        const result = lintHQL(sql);
        expect(Array.isArray(result)).toBe(true);
      });

      it('should handle SQL with multiple statements', () => {
        const sql = 'SELECT * FROM table1;\nSELECT * FROM table2;';
        const result = lintHQL(sql);
        expect(Array.isArray(result)).toBe(true);
      });

      it('should handle NULL values in conditions', () => {
        const sql = "SELECT * FROM table WHERE name IS NULL";
        const result = lintHQL(sql);
        const error = result.find(d => d.severity === 'error');
        expect(error).toBeUndefined();
      });
    });
  });

  describe('createHiveLinter', () => {
    it('should return a function', () => {
      const linter = createHiveLinter();
      expect(typeof linter).toBe('function');
    });

    it('should accept a view parameter', () => {
      const linter = createHiveLinter();
      const mockView = {
        state: {
          doc: {
            toString: () => 'SELECT * FROM table'
          }
        }
      };
      const result = linter(mockView);
      expect(Array.isArray(result)).toBe(true);
    });

    it('should return diagnostics from view content', () => {
      const linter = createHiveLinter();
      const mockView = {
        state: {
          doc: {
            toString: () => 'SELECT id,, name FROM table'
          }
        }
      };
      const result = linter(mockView);
      expect(result.length).toBeGreaterThan(0);
    });
  });

  describe('validateHQLQuick', () => {
    it('should return valid: true for correct SQL', () => {
      const result = validateHQLQuick('SELECT * FROM table WHERE id = 1');
      expect(result.valid).toBe(true);
      expect(result.errors).toEqual([]);
    });

    it('should return valid: false for SQL with errors', () => {
      const result = validateHQLQuick('SELECT id,, name FROM table');
      expect(result.valid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });

    it('should extract error messages', () => {
      const result = validateHQLQuick('SELECT id,, name FROM table');
      expect(result.errors.some(e => e.includes('double comma'))).toBe(true);
    });

    it('should include warnings separately from errors', () => {
      const result = validateHQLQuick('SELECT * FROM table WHERE (id = 1');
      expect(result.errors).toEqual([]);
      expect(result.warnings.length).toBeGreaterThan(0);
    });

    it('should handle empty input', () => {
      const result = validateHQLQuick('');
      expect(result.valid).toBe(true);
      expect(result.errors).toEqual([]);
      expect(result.warnings).toEqual([]);
    });

    it('should distinguish between errors and warnings', () => {
      const result = validateHQLQuick("CREATE VIEW v AS SELECT id,, name FROM table WHERE (id = 1");
      expect(result.errors.length).toBeGreaterThan(0); // double comma
      expect(result.warnings.length).toBeGreaterThan(0); // unbalanced parens + CREATE OR REPLACE
    });

    it('should return structured validation result', () => {
      const result = validateHQLQuick('SELECT * FROM table');
      expect(result).toHaveProperty('valid');
      expect(result).toHaveProperty('errors');
      expect(result).toHaveProperty('warnings');
      expect(Array.isArray(result.errors)).toBe(true);
      expect(Array.isArray(result.warnings)).toBe(true);
    });
  });

  describe('real-world scenarios', () => {
    it('should validate complex HQL queries', () => {
      const bizdate = '20240101';
      const hql = `CREATE OR REPLACE VIEW dwd_event_login AS
        SELECT
          ds,
          role_id,
          account_id,
          get_json_object(params, '$.zoneId') AS zone_id
        FROM ods_event_log
        WHERE ds = '${bizdate}'`;
      const result = validateHQLQuick(hql);
      expect(result.valid).toBe(true);
    });

    it('should detect issues in production-like queries', () => {
      const hql = `SELECT
        role_id,
        zone_id,,
        account_id
      FROM ods_table
      WHERE ds = 20240101`;
      const result = validateHQLQuick(hql);
      expect(result.valid).toBe(false);
      expect(result.errors.some(e => e.includes('double comma'))).toBe(true);
    });

    it('should handle queries with window functions', () => {
      const hql = `SELECT
        id,
        ROW_NUMBER() OVER (PARTITION BY role_id ORDER BY ds) AS rn
      FROM table`;
      const result = validateHQLQuick(hql);
      expect(result.valid).toBe(true);
    });

    it('should handle queries with LATERAL VIEW EXPLODE', () => {
      const hql = `SELECT
        id,
        col
      FROM table
      LATERAL VIEW EXPLODE(arr) exploded_table AS col`;
      const result = validateHQLQuick(hql);
      expect(result.valid).toBe(true);
    });
  });
});
