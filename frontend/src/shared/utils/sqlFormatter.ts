/**
 * SQL格式化工具
 * 使用sql-formatter库格式化Hive SQL语句
 */

import { format } from 'sql-formatter';

/**
 * 格式化SQL语言选项
 */
export const SQL_LANGUAGE = 'hive';

/**
 * 格式化SQL配置选项
 */
export const FORMAT_OPTIONS = {
  language: SQL_LANGUAGE,
  indent: '  ',
  linesBetweenQueries: 2,
  uppercase: true,
  positionals: true
};

/**
 * 格式化HQL语句
 *
 * @param sql - 原始SQL语句
 * @returns 格式化后的SQL语句
 *
 * @example
 * const formatted = formatHQL('SELECT * FROM table');
 * // Returns:
 * // SELECT
 * //   *
 * // FROM
 * //   table
 */
export function formatHQL(sql: string): string {
  if (!sql || sql.trim() === '') {
    return sql;
  }

  try {
    return format(sql, FORMAT_OPTIONS);
  } catch (error) {
    console.error('[formatHQL] 格式化失败:', error);
    // 如果格式化失败，返回原始SQL
    return sql;
  }
}

/**
 * 格式化HQL并移除多余注释
 *
 * @param sql - 原始SQL语句
 * @returns 格式化后的SQL语句
 */
export function formatHQLClean(sql: string): string {
  const formatted = formatHQL(sql);
  // 移除行尾注释
  return formatted.split('\n')
    .map(line => line.replace(/--.*$/, '').trim())
    .filter(line => line.length > 0)
    .join('\n');
}

/**
 * 压缩SQL（移除所有换行和多余空格）
 *
 * @param sql - 原始SQL语句
 * @returns 压缩后的SQL语句
 */
export function compressSQL(sql: string): string {
  return sql.replace(/\s+/g, ' ').trim();
}

/**
 * 验证SQL语法（基础验证）
 *
 * @param sql - SQL语句
 * @returns 是否有效
 */
export function validateBasicSQL(sql: string): boolean {
  if (!sql || sql.trim() === '') {
    return false;
  }

  // 检查基本的SQL关键字
  const sqlKeywords = [
    'SELECT', 'FROM', 'WHERE', 'JOIN', 'INSERT', 'UPDATE', 'DELETE',
    'CREATE', 'ALTER', 'DROP', 'VIEW', 'TABLE'
  ];

  const upperSQL = sql.toUpperCase();
  return sqlKeywords.some(keyword => upperSQL.includes(keyword));
}
