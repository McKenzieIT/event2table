/**
 * Type definitions for HQL Preview Modal
 */

export interface CanvasField {
  id: string | number;
  fieldName: string;
  fieldType?: string;
  type?: 'basic' | 'fixed' | 'custom' | 'parameter';
}

export interface WhereCondition {
  id: string;
  field: string;
  operator: string;
  value: any;
  logicalOperator?: string;
  type?: 'condition' | 'group';
  conditions?: WhereCondition[];
}

export interface GameData {
  gid: number;
  ods_db?: string;
}

export interface SelectedEvent {
  id: number;
  event_name: string;
  name?: string;
  description?: string;
}
