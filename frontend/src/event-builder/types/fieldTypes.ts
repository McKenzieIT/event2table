/**
 * Field Types for Event Builder
 */

/**
 * Field type enum
 */
export enum FieldType {
  PARAMETER = 'parameter',
  BASIC = 'basic',
  CUSTOM = 'custom',
  FIXED = 'fixed'
}

/**
 * Data type enum
 */
export enum DataType {
  STRING = 'STRING',
  BIGINT = 'BIGINT',
  INT = 'INT',
  DOUBLE = 'DOUBLE',
  BOOLEAN = 'BOOLEAN',
  DATE = 'DATE',
  TIMESTAMP = 'TIMESTAMP',
  ARRAY = 'ARRAY',
  MAP = 'MAP',
  JSON = 'JSON'
}

/**
 * Field interface
 */
export interface Field {
  id: string;
  type: FieldType | string;
  name: string;
  alias?: string;
  displayName?: string;
  dataType: DataType | string;
  isEditable?: boolean;
  sourceId?: string;
  mapping?: string;
  fixedValue?: string;
  fieldType?: string;
  fieldName?: string;
  paramId?: number | string | null;
  jsonPath?: string | null;
  hive_type?: string;
}

/**
 * Parameter interface
 */
export interface Parameter {
  id: string;
  name: string;
  alias?: string;
  dataType: DataType | string;
}
