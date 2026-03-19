// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
/**
 * Template API Client
 *
 * @module templateApi
 */

import { client } from '@shared/graphql/client';
import {
  GET_TEMPLATES,
  GET_TEMPLATE,
  CREATE_TEMPLATE,
  UPDATE_TEMPLATE,
  DELETE_TEMPLATE,
} from '@shared/graphql/operations';

/**
 * 模板数据结构
 */
export interface Template {
  id?: number;
  name: string;
  content?: string;
  category?: string;
  description?: string;
  createdAt?: string;
  updatedAt?: string;
}

/**
 * 模板列表查询选项
 */
export interface FetchTemplatesOptions {
  gameGid?: number;
  category?: string;
  search?: string;
  limit?: number;
  offset?: number;
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
 * Fetch templates with optional filters
 * @param options - Query options
 * @returns Promise<Template[]> - Templates array
 */
export async function fetchTemplates(
  options: FetchTemplatesOptions = {}
): Promise<Template[]> {
  try {
    const { gameGid, category, search, limit = 50, offset = 0 } = options;

    const { data } = await client.query({
      query: GET_TEMPLATES,
      variables: {
        gameGid,
        category,
        search,
        limit,
        offset,
      },
      fetchPolicy: 'network-only',
    });

    return data?.templates || [];
  } catch (error) {
    console.error('[templateApi] Failed to fetch templates:', error);
    return [];
  }
}

/**
 * Fetch a single template by ID
 * @param templateId - Template ID
 * @returns Promise<Template | null> - Template object or null if not found
 */
export async function fetchTemplate(templateId: number): Promise<Template | null> {
  try {
    const { data } = await client.query({
      query: GET_TEMPLATE,
      variables: { id: templateId },
      fetchPolicy: 'network-only',
    });

    return data?.template || null;
  } catch (error) {
    console.error('[templateApi] Failed to fetch template:', error);
    return null;
  }
}

/**
 * Create a new template
 * @param templateData - Template data
 * @returns Promise<SaveTemplateResult> - Save result with template or error
 */
export async function createTemplate(templateData: Omit<Template, 'id' | 'createdAt' | 'updatedAt'>): Promise<SaveTemplateResult> {
  try {
    const { data } = await client.mutate({
      mutation: CREATE_TEMPLATE,
      variables: {
        name: templateData.name,
        content: templateData.content || '',
        category: templateData.category,
        description: templateData.description,
      },
    });

    if (data?.createTemplate?.ok) {
      return {
        success: true,
        template: data.createTemplate.template,
      };
    } else {
      return {
        success: false,
        error: data?.createTemplate?.errors?.join(', ') || 'Failed to create template',
      };
    }
  } catch (error) {
    console.error('[templateApi] Failed to create template:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * Update an existing template
 * @param templateId - Template ID
 * @param templateData - Template data to update
 * @returns Promise<SaveTemplateResult> - Save result with template or error
 */
export async function updateTemplate(
  templateId: number,
  templateData: Partial<Omit<Template, 'id' | 'createdAt' | 'updatedAt'>>
): Promise<SaveTemplateResult> {
  try {
    const { data } = await client.mutate({
      mutation: UPDATE_TEMPLATE,
      variables: {
        id: templateId,
        name: templateData.name,
        content: templateData.content,
        category: templateData.category,
        description: templateData.description,
      },
    });

    if (data?.updateTemplate?.ok) {
      return {
        success: true,
        template: data.updateTemplate.template,
      };
    } else {
      return {
        success: false,
        error: data?.updateTemplate?.errors?.join(', ') || 'Failed to update template',
      };
    }
  } catch (error) {
    console.error('[templateApi] Failed to update template:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * Save a template (create or update based on whether id exists)
 * @param templateData - Template data
 * @returns Promise<SaveTemplateResult> - Save result with template or error
 */
export async function saveTemplate(templateData: Template): Promise<SaveTemplateResult> {
  if (templateData.id) {
    return updateTemplate(templateData.id, templateData);
  } else {
    return createTemplate(templateData);
  }
}

/**
 * Delete a template
 * @param templateId - Template ID
 * @returns Promise<DeleteTemplateResult> - Delete result
 */
export async function deleteTemplate(templateId: number): Promise<DeleteTemplateResult> {
  try {
    const { data } = await client.mutate({
      mutation: DELETE_TEMPLATE,
      variables: { id: templateId },
    });

    if (data?.deleteTemplate?.ok) {
      return {
        success: true,
      };
    } else {
      return {
        success: false,
        error: data?.deleteTemplate?.errors?.join(', ') || 'Failed to delete template',
      };
    }
  } catch (error) {
    console.error('[templateApi] Failed to delete template:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * Search templates by query string
 * @param query - Search query
 * @param options - Additional query options
 * @returns Promise<Template[]> - Templates array matching the search
 */
export async function searchTemplates(
  query: string,
  options: Omit<FetchTemplatesOptions, 'search'> = {}
): Promise<Template[]> {
  return fetchTemplates({
    ...options,
    search: query,
  });
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
