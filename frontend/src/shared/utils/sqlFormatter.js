/**
 * SQL Formatter Utility
 * Formats SQL/HQL queries for better readability
 *
 * @version 1.0.0
 * @date 2026-01-29
 */

import { format } from 'sql-formatter';

/**
 * Format SQL/HQL using sql-formatter library
 * @param {string} sql - Raw SQL query
 * @returns {string} Formatted SQL query
 */
export const formatSQL = (sql) => {
  if (!sql || typeof sql !== 'string') {
    return sql;
  }

  try {
    return format(sql, {
      language: 'hive',        // Hive SQL dialect
      indent: '    ',          // 4 spaces
      uppercase: true,         // Uppercase keywords
      linesBetweenQueries: 2,  // Empty line between queries
    });
  } catch (error) {
    console.error('[formatSQL] Format error:', error);
    return simpleFormatSQL(sql); // Fallback to simple formatter
  }
};

/**
 * Simple SQL formatter (fallback)
 * Adds line breaks before major keywords
 * @param {string} sql - Raw SQL query
 * @returns {string} Simply formatted SQL query
 */
const simpleFormatSQL = (sql) => {
  if (!sql || typeof sql !== 'string') {
    return sql;
  }

  const keywords = [
    'SELECT',
    'FROM',
    'WHERE',
    'JOIN',
    'LEFT JOIN',
    'RIGHT JOIN',
    'INNER JOIN',
    'FULL OUTER JOIN',
    'UNION',
    'UNION ALL',
    'GROUP BY',
    'ORDER BY',
    'HAVING',
    'LIMIT',
    'AND',
    'OR',
    'ON',
    'AS'
  ];

  let formatted = sql;
  keywords.forEach(kw => {
    formatted = formatted.replace(new RegExp(`\\b${kw}\\b`, 'gi'), `\n${kw}`);
  });

  return formatted.trim();
};

/**
 * Calculate SQL statistics
 * @param {string} sql - SQL query
 * @returns {Object} Statistics object with characterCount, lineCount, keywordCount
 */
export const calculateSQLStats = (sql) => {
  if (!sql || typeof sql !== 'string') {
    return { characterCount: 0, lineCount: 0, keywordCount: 0 };
  }

  const keywords = /\b(SELECT|FROM|WHERE|JOIN|AND|OR|GROUP BY|ORDER BY|HAVING)\b/gi;
  const matches = sql.match(keywords) || [];

  return {
    characterCount: sql.length,
    lineCount: sql.split('\n').length,
    keywordCount: matches.length
  };
};
