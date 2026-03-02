// @ts-nocheck - TypeScript strict mode disabled for test files
/**
 * sqlFormatter.test.ts
 * Unit tests for SQL formatting utilities
 */

import { describe, it, expect, vi } from 'vitest';
import {
  formatHQL,
  formatHQLClean,
  compressSQL,
  validateBasicSQL,
  formatSQL,
  calculateSQLStats,
  SQLStats
} from './sqlFormatter';

describe('sqlFormatter', () => {
  describe('formatHQL', () => {
    it('should format basic SELECT query', () => {
      const input = 'select role_id, zone_id from ods_table where ds = 20240101';
      const result = formatHQL(input);
      expect(result).toContain('SELECT');
      expect(result).toContain('FROM');
      expect(result).toContain('WHERE');
    });

    it('should return empty string for empty input', () => {
      expect(formatHQL('')).toBe('');
      expect(formatHQL('   ')).toBe('   ');
    });

    it('should handle invalid SQL gracefully', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      const invalidSQL = 'not a valid query at all';
      const result = formatHQL(invalidSQL);
      expect(result).toBe(invalidSQL);
      expect(consoleSpy).toHaveBeenCalled();
      consoleSpy.mockRestore();
    });

    it('should format complex JOIN queries', () => {
      const input = 'select a.id, b.name from table_a a join table_b b on a.id = b.id';
      const result = formatHQL(input);
      expect(result).toContain('JOIN');
      expect(result).toContain('ON');
    });
  });

  describe('formatHQLClean', () => {
    it('should remove comments from SQL', () => {
      const input = `SELECT *
      FROM table
      -- This is a comment
      WHERE id = 1`;
      const result = formatHQLClean(input);
      expect(result).not.toContain('--');
    });

    it('should remove empty lines', () => {
      const input = `SELECT *
      FROM table


      WHERE id = 1`;
      const result = formatHQLClean(input);
      expect(result).not.to.match(/\n\n\n/);
    });

    it('should trim whitespace', () => {
      const input = '  SELECT   *   FROM   table  ';
      const result = formatHQLClean(input);
      expect(result).not.to.match(/^\s+/);
      expect(result).not.to.match(/\s+$/);
    });
  });

  describe('compressSQL', () => {
    it('should remove extra whitespace', () => {
      const input = 'SELECT   *   FROM    table     WHERE     id   =   1';
      const result = compressSQL(input);
      expect(result).toBe('SELECT * FROM table WHERE id = 1');
    });

    it('should handle newlines and tabs', () => {
      const input = 'SELECT *\nFROM\ttable\nWHERE id = 1';
      const result = compressSQL(input);
      expect(result).not.toContain('\n');
      expect(result).not.to.contains('\t');
    });

    it('should trim leading and trailing whitespace', () => {
      const input = '   SELECT * FROM table   ';
      const result = compressSQL(input);
      expect(result).toBe('SELECT * FROM table');
    });
  });

  describe('validateBasicSQL', () => {
    it('should return true for valid SELECT queries', () => {
      expect(validateBasicSQL('SELECT * FROM table')).toBe(true);
      expect(validateBasicSQL('select * from table')).toBe(true);
    });

    it('should return true for INSERT queries', () => {
      expect(validateBasicSQL('INSERT INTO table VALUES (1, 2)')).toBe(true);
    });

    it('should return true for CREATE statements', () => {
      expect(validateBasicSQL('CREATE VIEW view_name AS SELECT * FROM table')).toBe(true);
    });

    it('should return false for empty or invalid SQL', () => {
      expect(validateBasicSQL('')).toBe(false);
      expect(validateBasicSQL('   ')).toBe(false);
      expect(validateBasicSQL('not sql at all')).toBe(false);
    });

    it('should be case insensitive', () => {
      expect(validateBasicSQL('select * from table')).toBe(true);
      expect(validateBasicSQL('SELECT * FROM table')).toBe(true);
      expect(validateBasicSQL('SeLeCt * FrOm table')).toBe(true);
    });
  });

  describe('formatSQL', () => {
    it('should format SQL with uppercase keywords', () => {
      const input = 'select id, name from users where active = 1';
      const result = formatSQL(input);
      expect(result).toMatch(/SELECT/);
      expect(result).toMatch(/FROM/);
      expect(result).toMatch(/WHERE/);
    });

    it('should handle empty input', () => {
      expect(formatSQL('')).toBe('');
      expect(formatSQL(null as any)).toBe(null);
    });

    it('should fall back to simple formatting on error', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      const result = formatSQL('select');
      expect(result).toBeTruthy();
      consoleSpy.mockRestore();
    });
  });

  describe('calculateSQLStats', () => {
    it('should calculate character count', () => {
      const sql = 'SELECT * FROM table WHERE id = 1';
      const stats: SQLStats = calculateSQLStats(sql);
      expect(stats.characterCount).toBe(sql.length);
    });

    it('should calculate line count', () => {
      const sql = 'SELECT *\nFROM table\nWHERE id = 1';
      const stats: SQLStats = calculateSQLStats(sql);
      expect(stats.lineCount).toBe(3);
    });

    it('should count keywords', () => {
      const sql = 'SELECT id, name FROM users WHERE active = 1 ORDER BY name';
      const stats: SQLStats = calculateSQLStats(sql);
      expect(stats.keywordCount).toBeGreaterThan(0);
    });

    it('should handle empty input', () => {
      const stats: SQLStats = calculateSQLStats('');
      expect(stats.characterCount).toBe(0);
      expect(stats.lineCount).toBe(0);
      expect(stats.keywordCount).toBe(0);
    });

    it('should handle null input', () => {
      const stats: SQLStats = calculateSQLStats(null as any);
      expect(stats.characterCount).toBe(0);
      expect(stats.lineCount).toBe(0);
      expect(stats.keywordCount).toBe(0);
    });

    it('should be case insensitive for keyword counting', () => {
      const stats1: SQLStats = calculateSQLStats('SELECT * FROM table');
      const stats2: SQLStats = calculateSQLStats('select * from table');
      expect(stats1.keywordCount).toBe(stats2.keywordCount);
    });
  });

  describe('edge cases', () => {
    it('should handle SQL with comments', () => {
      const input = '-- Comment\nSELECT * FROM table';
      const result = formatHQL(input);
      expect(result).toContain('--');
    });

    it('should handle very long SQL statements', () => {
      const columns = Array.from({ length: 100 }, (_, i) => `col${i}`).join(', ');
      const input = `SELECT ${columns} FROM table`;
      const result = formatHQL(input);
      expect(result).toBeTruthy();
      expect(result.length).toBeGreaterThan(0);
    });

    it('should handle SQL with special characters', () => {
      const input = "SELECT * FROM table WHERE name = 'O\\'Reilly'";
      const result = formatHQL(input);
      expect(result).toContain('SELECT');
    });

    it('should handle SQL with subqueries', () => {
      const input = 'SELECT * FROM (SELECT id FROM table) AS sub';
      const result = formatHQL(input);
      expect(result).toContain('SELECT');
      expect(result).toContain('FROM');
    });
  });
});
