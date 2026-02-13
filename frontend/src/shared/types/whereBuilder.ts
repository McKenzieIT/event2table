/**
 * WHERE条件构建器类型定义
 */

/**
 * WHERE操作符类型
 */
export type WhereOperator =
  | '='
  | '!='
  | '>'
  | '<'
  | '>='
  | '<='
  | 'IN'
  | 'NOT IN'
  | 'LIKE'
  | 'NOT LIKE'
  | 'BETWEEN'
  | 'NOT BETWEEN'
  | 'IS NULL'
  | 'IS NOT NULL';

/**
 * WHERE条件项（单个条件）
 */
export interface WhereCondition {
  id: string;
  type: 'condition';
  field: string;           // 字段名：ds, role_id
  operator: WhereOperator; // 操作符
  value: any;              // 值（可以是字符串、数字、数组）
  logicalOp?: 'AND' | 'OR'; // 与前一个条件的逻辑关系
  dataType?: string;        // 字段数据类型（用于输入验证）
}

/**
 * WHERE分组（支持嵌套）
 */
export interface WhereGroup {
  id: string;
  type: 'group';
  logicalOp: 'AND' | 'OR'; // 组内逻辑关系
  children: (WhereCondition | WhereGroup)[];
  isCollapsed?: boolean;   // UI状态：是否折叠
}

/**
 * WHERE项（条件或分组）
 */
export type WhereItem = WhereCondition | WhereGroup;

/**
 * WHERE构建器状态
 */
export interface WhereState {
  conditions: WhereItem[];      // 顶层条件列表
  builderMode: 'simple' | 'advanced'; // 简单模式 vs 高级模式
  previewOpen: boolean;         // 是否展开预览
  draggedId: string | null;     // 正在拖拽的项ID
  dropTargetId: string | null;  // 拖放目标ID
}

/**
 * 判断是否为分组
 */
export function isWhereGroup(item: WhereItem): item is WhereGroup {
  return item.type === 'group';
}

/**
 * 判断是否为条件
 */
export function isWhereCondition(item: WhereItem): item is WhereCondition {
  return item.type === 'condition';
}
