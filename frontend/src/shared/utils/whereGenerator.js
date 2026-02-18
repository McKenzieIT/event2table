/**
 * WHERE子句生成器
 * 将WHERE条件对象转换为SQL WHERE子句
 */

import { isWhereGroup, isWhereCondition } from '@shared/types/whereBuilder';

/**
 * 生成完整的WHERE子句
 * @param {WhereItem[]} conditions - WHERE条件数组
 * @returns {string} SQL WHERE子句（不包含WHERE关键字）
 */
export function generateWhereClause(conditions) {
  if (!conditions || conditions.length === 0) {
    return '';
  }

  const clauses = conditions.map((item, index) => {
    // 第一个条件不需要logicalOp前缀
    const prefix = index > 0 && item.logicalOp ? `${item.logicalOp} ` : '';
    const clause = generateWhereItem(item);
    return prefix + clause;
  });

  return clauses.join(' ');
}

/**
 * 生成单个WHERE项（条件或分组）
 * @param {WhereItem} item - WHERE项
 * @returns {string} SQL片段
 */
function generateWhereItem(item) {
  if (isWhereCondition(item)) {
    return generateCondition(item);
  } else if (isWhereGroup(item)) {
    return generateGroup(item);
  }
  return '';
}

/**
 * 生成单个条件
 * @param {WhereCondition} condition - 条件对象
 * @returns {string} SQL条件片段
 */
function generateCondition(condition) {
  const { field, operator, value } = condition;

  switch (operator) {
    case '=':
    case '!=':
    case '>':
    case '<':
    case '>=':
    case '<=':
      return `${field} ${operator} '${escapeValue(value)}'`;

    case 'IN':
    case 'NOT IN':
      if (Array.isArray(value)) {
        const values = value.map(v => `'${escapeValue(v)}'`).join(', ');
        return `${field} ${operator} (${values})`;
      }
      return `${field} ${operator} ('${escapeValue(value)}')`;

    case 'BETWEEN':
    case 'NOT BETWEEN':
      if (Array.isArray(value) && value.length === 2) {
        return `${field} ${operator} '${value[0]}' AND '${value[1]}'`;
      }
      return `${field} ${operator} ? AND ?`;

    case 'LIKE':
    case 'NOT LIKE':
      return `${field} ${operator} '${escapeValue(value)}'`;

    case 'IS NULL':
      return `${field} IS NULL`;

    case 'IS NOT NULL':
      return `${field} IS NOT NULL`;

    default:
      return `${field} = '${escapeValue(value)}'`;
  }
}

/**
 * 生成分组
 * @param {WhereGroup} group - 分组对象
 * @returns {string} SQL分组片段（带括号）
 */
function generateGroup(group) {
  if (!group.children || group.children.length === 0) {
    return '';
  }

  const inner = group.children.map(child => generateWhereItem(child)).join(' ');
  return `(${inner})`;
}

/**
 * 转义SQL值
 * @param {any} value - 原始值
 * @returns {string} 转义后的值
 */
function escapeValue(value) {
  if (value === null || value === undefined) {
    return '';
  }
  return String(value)
    .replace(/'/g, "''")  // 转义单引号
    .replace(/\\/g, '\\\\'); // 转义反斜杠
}

/**
 * 计算WHERE条件的复杂度（用于性能监控）
 * @param {WhereItem[]} conditions - WHERE条件数组
 * @returns {number} 复杂度分数（嵌套层级 × 条件数）
 */
export function calculateWhereComplexity(conditions) {
  let complexity = 0;

  function countItems(items, depth = 1) {
    items.forEach(item => {
      complexity += depth;
      if (isWhereGroup(item) && item.children) {
        countItems(item.children, depth + 1);
      }
    });
  }

  countItems(conditions);
  return complexity;
}

/**
 * 验证WHERE条件配置
 * @param {WhereItem[]} conditions - WHERE条件数组
 * @returns {{ valid: boolean, errors: string[] }} 验证结果
 */
export function validateWhereConditions(conditions) {
  const errors = [];

  function validateItems(items, depth = 0) {
    if (depth > 5) {
      errors.push('嵌套层级超过5层');
      return;
    }

    items.forEach(item => {
      if (isWhereCondition(item)) {
        // 验证条件
        if (!item.field) {
          errors.push(`条件 ${item.id} 缺少字段`);
        }
        if (!item.operator) {
          errors.push(`条件 ${item.id} 缺少操作符`);
        }
        if (item.value === undefined || item.value === '') {
          errors.push(`条件 ${item.id} 缺少值`);
        }
      } else if (isWhereGroup(item)) {
        // 验证分组
        if (!item.children || item.children.length === 0) {
          errors.push(`分组 ${item.id} 为空`);
        }
        validateItems(item.children, depth + 1);
      }
    });
  }

  validateItems(conditions);

  return {
    valid: errors.length === 0,
    errors
  };
}
