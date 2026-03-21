import { FieldType, DataType } from '../../../types/fieldTypes';
import { generateId } from '@shared/utils/idGenerator';

/**
 * Field type definition
 */
export interface Field {
  id: string;
  type: string;
  name: string;
  alias?: string;
  displayName?: string;
  dataType: string;
  isEditable?: boolean;
  fieldType?: string;
  fieldName?: string;
  paramId?: number | string | null;
  jsonPath?: string | null;
  sourceId?: string;
  mapping?: string;
  fixedValue?: string;
  hive_type?: string;
}

/**
 * Parameter definition
 */
export interface Parameter {
  id: string;
  name: string;
  alias?: string;
  dataType: string;
}

/**
 * Create a basic field (ds, partition)
 */
export function createBasicField(): Field {
  return {
    id: generateId(),
    type: FieldType.BASIC,
    name: 'ds',
    displayName: '分区',
    alias: 'ds',
    dataType: DataType.STRING,
    isEditable: true,
    fieldType: 'base',
    fieldName: 'ds',
    paramId: null,
    jsonPath: null
  };
}

/**
 * Create a custom field
 */
export function createCustomField(): Field {
  return {
    id: generateId(),
    type: FieldType.CUSTOM,
    name: 'custom_field',
    displayName: '自定义字段',
    alias: 'custom_field',
    dataType: DataType.STRING,
    mapping: '',
    isEditable: true,
    fieldType: 'custom',
    fieldName: 'custom_field',
    paramId: null,
    jsonPath: null
  };
}

/**
 * Create a fixed value field
 */
export function createFixedField(): Field {
  return {
    id: generateId(),
    type: FieldType.FIXED,
    name: 'fixed_value',
    displayName: '固定值',
    alias: 'fixed_value',
    dataType: DataType.STRING,
    fixedValue: '',
    isEditable: true,
    fieldType: 'fixed',
    fieldName: 'fixed_value',
    paramId: null,
    jsonPath: null
  };
}

/**
 * Create a field from a parameter
 */
export function createFieldFromParameter(parameter: Parameter): Field {
  return {
    id: generateId(),
    type: FieldType.PARAMETER,
    sourceId: parameter.id,
    name: parameter.name,
    alias: parameter.alias || parameter.name,
    dataType: parameter.dataType,
    isEditable: true
  };
}

/**
 * Common base fields configuration
 */
export const COMMON_BASE_FIELDS = [
  { name: 'ds', displayName: '分区', alias: 'ds', dataType: DataType.STRING },
  { name: 'role_id', displayName: '角色ID', alias: 'role_id', dataType: DataType.BIGINT },
  { name: 'account_id', displayName: '账号ID', alias: 'account_id', dataType: DataType.BIGINT },
  { name: 'tm', displayName: '上报时间', alias: 'tm', dataType: DataType.STRING }
] as const;

/**
 * All base fields configuration
 */
export const ALL_BASE_FIELDS = [
  { name: 'ds', displayName: '分区', alias: 'ds', dataType: DataType.STRING },
  { name: 'role_id', displayName: '角色ID', alias: 'role_id', dataType: DataType.BIGINT },
  { name: 'account_id', displayName: '账号ID', alias: 'account_id', dataType: DataType.BIGINT },
  { name: 'utdid', displayName: '设备ID', alias: 'utdid', dataType: DataType.STRING },
  { name: 'tm', displayName: '上报时间', alias: 'tm', dataType: DataType.STRING },
  { name: 'ts', displayName: '上报时间戳', alias: 'ts', dataType: DataType.BIGINT },
  { name: 'envinfo', displayName: '环境信息', alias: 'envinfo', dataType: DataType.STRING }
] as const;

/**
 * Create a base field from configuration
 */
export function createBaseField(config: {
  name: string;
  displayName: string;
  alias: string;
  dataType: string;
}): Field {
  return {
    id: generateId(),
    type: FieldType.BASIC,
    name: config.name,
    displayName: config.displayName,
    alias: config.alias,
    dataType: config.dataType,
    isEditable: true,
    fieldType: 'base',
    fieldName: config.name,
    paramId: null,
    jsonPath: null
  };
}

/**
 * Get field type label for display
 */
export function getFieldTypeLabel(fieldType: string): string {
  const normalizedType = String(fieldType).toLowerCase();

  const typeLabels: Record<string, string> = {
    'param': '参数',
    'parameter': '参数',
    'base': '基础字段',
    'basic': '基础字段',
    'custom': '自定义字段',
    'fixed': '固定值'
  };

  return typeLabels[normalizedType] || '字段';
}

/**
 * Get field display name (alias > displayName > name > fieldName)
 */
export function getFieldDisplayName(field: Field): string {
  return field.alias || field.displayName || field.name || field.fieldName || '';
}

/**
 * Generate delete confirmation message for a field
 */
export function getDeleteMessage(field: Field): string {
  const fieldTypeValue = field.fieldType || field.type;
  const fieldType = getFieldTypeLabel(fieldTypeValue);
  const fieldName = getFieldDisplayName(field);

  return `确定要删除${fieldType}"${fieldName}"吗？`;
}

/**
 * Calculate field statistics
 */
export function calculateFieldStats(
  fields: Field[],
  whereConditions?: Array<{ id: string; field: string; operator: string; value: unknown }>
) {
  const baseFields = fields.filter(f => f.fieldType === 'base' || f.fieldType === FieldType.BASIC).length;
  const paramFields = fields.filter(f => f.fieldType === 'param' || f.fieldType === FieldType.PARAMETER).length;
  
  return {
    total: fields.length,
    baseFields,
    paramFields,
    whereCount: whereConditions ? whereConditions.length : 0,
  };
}
