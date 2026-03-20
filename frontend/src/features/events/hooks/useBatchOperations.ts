/**
 * useBatchOperations Hook
 *
 * 批量操作事件的hooks
 * 提供批量编辑、批量验证、批量删除等功能
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useToast } from '@shared/ui';
import type { Event } from '@shared/types/event-types';

/**
 * 批量编辑表单数据
 */
export interface BatchEditFormData {
  eventName?: string;
  eventNameCn?: string;
  categoryId?: number | null;
  description?: string;
  includeInCommonParams?: boolean;
}

/**
 * 批量编辑hook属性
 */
export interface UseBatchEditProps {
  /** 编辑成功后的回调 */
  onSuccess?: (updatedCount: number) => void;
  /** 编辑失败后的回调 */
  onError?: (error: Error) => void;
}

/**
 * 批量编辑hook
 */
export function useBatchEdit({ onSuccess, onError }: UseBatchEditProps = {}) {
  const queryClient = useQueryClient();
  const { success, error } = useToast();

  const mutation = useMutation({
    mutationFn: async (params: {
      eventIds: number[];
      formData: BatchEditFormData;
    }) => {
      const { eventIds, formData } = params;

      const updates = eventIds.map(eventId => {
        const update: any = { id: eventId };
        
        if (formData.eventName) update.event_name = formData.eventName;
        if (formData.eventNameCn) update.event_name_cn = formData.eventNameCn;
        if (formData.categoryId !== null && formData.categoryId !== undefined) {
          update.category_id = formData.categoryId;
        }
        if (formData.description) update.description = formData.description;
        if (formData.includeInCommonParams !== undefined) {
          update.include_in_common_params = formData.includeInCommonParams;
        }
        
        return update;
      });

      const response = await fetch('/api/events/batch', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ updates }),
      });

      if (!response.ok) {
        throw new Error('批量编辑失败');
      }

      return response.json();
    },
    onSuccess: (data: any) => {
      const updatedCount = data?.data?.updated_count ?? data?.updated_count ?? 0;
      success(`成功更新 ${updatedCount} 个事件`);
      onSuccess?.(updatedCount);
      
      // 失效相关查询缓存
      queryClient.invalidateQueries({ queryKey: ['events'] });
    },
    onError: (err: Error) => {
      const errorMessage = err.message || '批量编辑失败';
      error(errorMessage);
      onError?.(err);
    },
  });

  return {
    batchEdit: mutation.mutate,
    batchEditAsync: mutation.mutateAsync,
    isLoading: mutation.isPending,
    error: mutation.error,
  };
}

/**
 * 批量删除hook属性
 */
export interface UseBatchDeleteProps {
  /** 删除成功后的回调 */
  onSuccess?: (deletedCount: number) => void;
  /** 删除失败后的回调 */
  onError?: (error: Error) => void;
}

/**
 * 批量删除hook
 */
export function useBatchDelete({ onSuccess, onError }: UseBatchDeleteProps = {}) {
  const queryClient = useQueryClient();
  const { success, error } = useToast();

  const mutation = useMutation({
    mutationFn: async (eventIds: number[]) => {
      const response = await fetch('/api/events/batch', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: eventIds }),
      });

      if (!response.ok) {
        throw new Error('批量删除失败');
      }

      return response.json();
    },
    onSuccess: (data: any) => {
      const deletedCount = data?.data?.deleted_count ?? data?.deleted_count ?? 0;
      success(`成功删除 ${deletedCount} 个事件`);
      onSuccess?.(deletedCount);
      
      // 失效相关查询缓存
      queryClient.invalidateQueries({ queryKey: ['events'] });
    },
    onError: (err: Error) => {
      const errorMessage = err.message || '批量删除失败';
      error(errorMessage);
      onError?.(err);
    },
  });

  return {
    batchDelete: mutation.mutate,
    batchDeleteAsync: mutation.mutateAsync,
    isLoading: mutation.isPending,
    error: mutation.error,
  };
}

/**
 * 验证问题类型
 */
export enum ValidationIssueType {
  MISSING_NAME = 'MISSING_NAME',
  MISSING_CATEGORY = 'MISSING_CATEGORY',
  MISSING_SOURCE_TABLE = 'MISSING_SOURCE_TABLE',
  MISSING_TARGET_TABLE = 'MISSING_TARGET_TABLE',
  NO_PARAMETERS = 'NO_PARAMETERS',
  INVALID_NAME_FORMAT = 'INVALID_NAME_FORMAT',
}

/**
 * 验证问题
 */
export interface ValidationIssue {
  type: ValidationIssueType;
  eventId: number;
  eventName: string;
  message: string;
  severity: 'error' | 'warning';
  suggestion?: string;
}

/**
 * 验证结果
 */
export interface ValidationResult {
  totalEvents: number;
  validEvents: number;
  invalidEvents: number;
  issues: ValidationIssue[];
}

/**
 * 批量验证hook属性
 */
export interface UseBatchValidateProps {
  /** 验证完成后的回调 */
  onComplete?: (result: ValidationResult) => void;
}

/**
 * 批量验证hook
 */
export function useBatchValidate({ onComplete }: UseBatchValidateProps = {}) {
  const { success, warning } = useToast();

  const validateEvents = useCallback((events: Event[]): ValidationResult => {
    const allIssues: ValidationIssue[] = [];
    const validEventIds = new Set<number>();

    events.forEach(event => {
      const issues = validateSingleEvent(event);
      if (issues.length === 0) {
        validEventIds.add(event.id);
      } else {
        allIssues.push(...issues);
      }
    });

    const result: ValidationResult = {
      totalEvents: events.length,
      validEvents: validEventIds.size,
      invalidEvents: events.length - validEventIds.size,
      issues: allIssues,
    };

    // 显示验证结果通知
    if (result.invalidEvents === 0) {
      success(`所有 ${result.totalEvents} 个事件验证通过！`);
    } else {
      warning(`验证完成：${result.validEvents} 个通过，${result.invalidEvents} 个存在问题`);
    }

    onComplete?.(result);
    return result;
  }, [success, warning, onComplete]);

  return {
    validateEvents,
  };
}

/**
 * 验证单个事件
 */
function validateSingleEvent(event: Event): ValidationIssue[] {
  const issues: ValidationIssue[] = [];

  // 检查事件名称
  if (!event.eventName || event.eventName.trim() === '') {
    issues.push({
      type: ValidationIssueType.MISSING_NAME,
      eventId: event.id,
      eventName: event.eventNameCn || event.eventName || `#${event.id}`,
      message: '缺少事件英文名称',
      severity: 'error',
      suggestion: '请为事件添加英文名称',
    });
  } else if (!/^[a-zA-Z][a-zA-Z0-9_]*$/.test(event.eventName)) {
    issues.push({
      type: ValidationIssueType.INVALID_NAME_FORMAT,
      eventId: event.id,
      eventName: event.eventNameCn || event.eventName || `#${event.id}`,
      message: '事件名称格式不正确',
      severity: 'warning',
      suggestion: '事件名称应以字母开头，只能包含字母、数字和下划线',
    });
  }

  // 检查中文名称
  if (!event.eventNameCn || event.eventNameCn.trim() === '') {
    issues.push({
      type: ValidationIssueType.MISSING_NAME,
      eventId: event.id,
      eventName: event.eventName || `#${event.id}`,
      message: '缺少事件中文名称',
      severity: 'warning',
      suggestion: '建议为事件添加中文名称',
    });
  }

  // 检查分类
  if (!event.categoryId && !event.categoryName) {
    issues.push({
      type: ValidationIssueType.MISSING_CATEGORY,
      eventId: event.id,
      eventName: event.eventNameCn || event.eventName || `#${event.id}`,
      message: '未设置事件分类',
      severity: 'warning',
      suggestion: '建议为事件设置分类以便于管理',
    });
  }

  // 检查源表
  if (!event.sourceTable || event.sourceTable.trim() === '') {
    issues.push({
      type: ValidationIssueType.MISSING_SOURCE_TABLE,
      eventId: event.id,
      eventName: event.eventNameCn || event.eventName || `#${event.id}`,
      message: '未设置源表',
      severity: 'error',
      suggestion: '请为事件设置源表',
    });
  }

  // 检查目标表
  if (!event.targetTable || event.targetTable.trim() === '') {
    issues.push({
      type: ValidationIssueType.MISSING_TARGET_TABLE,
      eventId: event.id,
      eventName: event.eventNameCn || event.eventName || `#${event.id}`,
      message: '未设置目标表',
      severity: 'error',
      suggestion: '请为事件设置目标表',
    });
  }

  // 检查参数
  if (!event.fields || event.fields.length === 0) {
    issues.push({
      type: ValidationIssueType.NO_PARAMETERS,
      eventId: event.id,
      eventName: event.eventNameCn || event.eventName || `#${event.id}`,
      message: '事件没有配置参数',
      severity: 'warning',
      suggestion: '建议为事件添加必要的参数',
    });
  }

  return issues;
}

/**
 * 批量操作hook组合
 * 一次性导出所有批量操作hooks
 */
export function useBatchOperations() {
  const batchEdit = useBatchEdit();
  const batchDelete = useBatchDelete();
  const batchValidate = useBatchValidate();

  return {
    batchEdit,
    batchDelete,
    batchValidate,
  };
}
