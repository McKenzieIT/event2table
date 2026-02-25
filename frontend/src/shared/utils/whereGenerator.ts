import { isWhereGroup, isWhereCondition, WhereItem, WhereCondition, WhereGroup } from '@shared/types/whereBuilder';

export function generateWhereClause(conditions: WhereItem[]): string {
  if (!conditions || conditions.length === 0) {
    return '';
  }

  const clauses = conditions.map((item, index) => {
    const prefix = index > 0 && item.logicalOp ? `${item.logicalOp} ` : '';
    const clause = generateWhereItem(item);
    return prefix + clause;
  });

  return clauses.join(' ');
}

function generateWhereItem(item: WhereItem): string {
  if (isWhereCondition(item)) {
    return generateCondition(item);
  } else if (isWhereGroup(item)) {
    return generateGroup(item);
  }
  return '';
}

function generateCondition(condition: WhereCondition): string {
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

function generateGroup(group: WhereGroup): string {
  if (!group.children || group.children.length === 0) {
    return '';
  }

  const inner = group.children.map(child => generateWhereItem(child)).join(' ');
  return `(${inner})`;
}

function escapeValue(value: unknown): string {
  if (value === null || value === undefined) {
    return '';
  }
  return String(value)
    .replace(/'/g, "''")
    .replace(/\\/g, '\\\\');
}

export function calculateWhereComplexity(conditions: WhereItem[]): number {
  let complexity = 0;

  function countItems(items: WhereItem[], depth: number = 1): void {
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

export interface WhereValidationResult {
  valid: boolean;
  errors: string[];
}

export function validateWhereConditions(conditions: WhereItem[]): WhereValidationResult {
  const errors: string[] = [];

  function validateItems(items: WhereItem[], depth: number = 0): void {
    if (depth > 5) {
      errors.push('嵌套层级超过5层');
      return;
    }

    items.forEach(item => {
      if (isWhereCondition(item)) {
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
