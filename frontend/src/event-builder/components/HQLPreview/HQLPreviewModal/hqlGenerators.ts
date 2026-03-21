import type { CanvasField, WhereCondition, GameData, SelectedEvent } from '../types';

/**
 * Generate SELECT HQL
 */
export function generateSELECTHQL(
  fields: CanvasField[],
  whereConditions: WhereCondition[],
  gameData?: GameData,
  event?: SelectedEvent | null
): string {
  const fieldList = fields.map(f => `  ${f.fieldName}`).join(',\n');
  const whereClause = whereConditions.length > 0
    ? `WHERE\n  ${generateWhereClause(whereConditions)}`
    : '';

  return `SELECT\n${fieldList}\nFROM ${gameData?.ods_db || 'ieu_ods'}.ods_${gameData?.gid || '10000147'}_all_view\n${whereClause};`;
}

/**
 * Generate CREATE TABLE/VIEW HQL
 */
export function generateCREATEHQL(
  fields: CanvasField[],
  whereConditions: WhereCondition[],
  gameData?: GameData,
  event?: SelectedEvent | null,
  type: 'table' | 'view' = 'table'
): string {
  const fieldList = fields.map(f => `  ${f.fieldName}`).join(',\n');
  const tableName = `dwd_${event?.event_name || 'event'}_di`;

  return `CREATE ${type} IF NOT EXISTS ${tableName} AS\nSELECT\n${fieldList}\nFROM ${gameData?.ods_db || 'ieu_ods'}.ods_${gameData?.gid || '10000147'}_all_view;`;
}

/**
 * Generate INSERT HQL
 */
export function generateINSERTHQL(
  fields: CanvasField[],
  whereConditions: WhereCondition[],
  gameData?: GameData,
  event?: SelectedEvent | null
): string {
  const fieldList = fields.map(f => f.fieldName).join(', ');
  const tableName = `dwd_${event?.event_name || 'event'}_di`;
  const whereClause = whereConditions.length > 0
    ? `WHERE ${generateWhereClause(whereConditions)}`
    : '';

  return `INSERT OVERWRITE TABLE ${tableName}\nSELECT ${fieldList}\nFROM ${gameData?.ods_db || 'ieu_ods'}.ods_${gameData?.gid || '10000147'}_all_view\n${whereClause};`;
}

/**
 * Generate WHERE clause
 */
function generateWhereClause(conditions: WhereCondition[]): string {
  return conditions.map(c => `${c.field} ${c.operator} '${c.value}'`).join(' AND ');
}
