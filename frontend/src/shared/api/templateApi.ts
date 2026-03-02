// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
/**
 * Template API Client
 *
 * @module templateApi
 */

/**
 * 模板数据结构
 * TODO: 根据实际业务需求定义完整的模板结构
 */
export interface Template {
  id?: number;
  name: string;
  description?: string;
  gameGid: number;
  config?: Record<string, unknown>;
  createdAt?: string;
  updatedAt?: string;
}

/**
 * 模板列表查询选项
 */
export interface FetchTemplatesOptions {
  limit?: number;
  offset?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

/**
 * 模板保存结果
 */
export interface SaveTemplateResult {
  success: boolean;
  template?: Template;
  error?: string;
}

/**
 * 模板删除结果
 */
export interface DeleteTemplateResult {
  success: boolean;
  error?: string;
}

/**
 * Fetch templates for a game
 * @param gameGid - Game GID
 * @param options - Query options
 * @returns Promise<Template[]> - Templates array
 */
export async function fetchTemplates(
  gameGid: number,
  options: FetchTemplatesOptions = {}
): Promise<Template[]> {
  // Placeholder implementation - template feature not yet implemented
  console.warn('fetchTemplates is not implemented yet');
  return [];
}

/**
 * Fetch a single template by ID
 * @param templateId - Template ID
 * @returns Promise<Template | null> - Template object or null if not found
 */
export async function fetchTemplate(templateId: number): Promise<Template | null> {
  console.warn('fetchTemplate is not implemented yet');
  return null;
}

/**
 * Save a template (create or update)
 * @param templateData - Template data
 * @returns Promise<SaveTemplateResult> - Save result with template or error
 */
export async function saveTemplate(templateData: Template): Promise<SaveTemplateResult> {
  console.warn('saveTemplate is not implemented yet');
  return {
    success: false,
    error: 'Not implemented yet',
  };
}

/**
 * Delete a template
 * @param templateId - Template ID
 * @returns Promise<DeleteTemplateResult> - Delete result
 */
export async function deleteTemplate(templateId: number): Promise<DeleteTemplateResult> {
  console.warn('deleteTemplate is not implemented yet');
  return {
    success: false,
    error: 'Not implemented yet',
  };
}

/**
 * Export types for external use
 */
export type {
  Template,
  FetchTemplatesOptions,
  SaveTemplateResult,
  DeleteTemplateResult,
};
