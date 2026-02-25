/**
 * SQL格式化工具
 * 使用sql-formatter库格式化Hive SQL语句
 */

import { format } from 'sql-formatter';

export const SQL_LANGUAGE = 'hive';

export const FORMAT_OPTIONS = {
  language: SQL_LANGUAGE,
  indent: '  ',
  linesBetweenQueries: 2,
  uppercase: true,
  positionals: true
};

export function formatHQL(sql: string): string {
  if (!sql || sql.trim() === '') {
    return sql;
  }

  try {
    return format(sql, FORMAT_OPTIONS);
  } catch (error) {
    console.error('[formatHQL] 格式化失败:', error);
    return sql;
  }
}

export function formatHQLClean(sql: string): string {
  const formatted = formatHQL(sql);
  return formatted.split('\n')
    .map(line => line.replace(/--.*$/, '').trim())
    .filter(line => line.length > 0)
    .join('\n');
}

export function compressSQL(sql: string): string {
  return sql.replace(/\s+/g, ' ').trim();
}

export function validateBasicSQL(sql: string): boolean {
  if (!sql || sql.trim() === '') {
    return false;
  }

  const sqlKeywords = [
    'SELECT', 'FROM', 'WHERE', 'JOIN', 'INSERT', 'UPDATE', 'DELETE',
    'CREATE', 'ALTER', 'DROP', 'VIEW', 'TABLE'
  ];

  const upperSQL = sql.toUpperCase();
  return sqlKeywords.some(keyword => upperSQL.includes(keyword));
}

export interface SQLStats {
  characterCount: number;
  lineCount: number;
  keywordCount: number;
}

const simpleFormatSQL = (sql: string): string => {
  if (!sql || typeof sql !== 'string') {
    return sql;
  }

  const keywords = [
    'SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT JOIN', 'RIGHT JOIN',
    'INNER JOIN', 'FULL OUTER JOIN', 'UNION', 'UNION ALL',
    'GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT', 'AND', 'OR', 'ON', 'AS'
  ];

  let formatted = sql;
  keywords.forEach(kw => {
    formatted = formatted.replace(new RegExp(`\\b${kw}\\b`, 'gi'), `\n${kw}`);
  });

  return formatted.trim();
};

export const formatSQL = (sql: string): string => {
  if (!sql || typeof sql !== 'string') {
    return sql;
  }

  try {
    return format(sql, {
      language: 'hive',
      indent: '    ',
      uppercase: true,
      linesBetweenQueries: 2,
    });
  } catch (error) {
    console.error('[formatSQL] Format error:', error);
    return simpleFormatSQL(sql);
  }
};

export const calculateSQLStats = (sql: string): SQLStats => {
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
