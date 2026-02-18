/**
 * useEventAllParams Hook
 * 获取事件的所有参数字段，并结合画布字段状态提供视觉标记
 *
 * @usage
 * const fieldsWithStatus = useEventAllParams(selectedEvent, canvasFields);
 */
import { useQuery } from '@tanstack/react-query';
import { fetchParams } from '@shared/api/eventNodeBuilderApi';
import { useMemo } from 'react';

// 基础字段定义
const BASE_FIELDS = [
  { value: 'ds', label: 'ds (分区)' },
  { value: 'role_id', label: 'role_id (角色ID)' },
  { value: 'account_id', label: 'account_id (账号ID)' },
  { value: 'utdid', label: 'utdid (设备ID)' },
  { value: 'tm', label: 'tm (上报时间)' },
  { value: 'ts', label: 'ts (时间戳)' },
];

/**
 * 获取事件的所有参数字段（包含已在画布的标记）
 *
 * @param {Object} selectedEvent - 当前选择的事件对象
 * @param {Array} canvasFields - 已添加到画布的字段数组
 * @returns {Object} { fields, paramCount, baseCount, isLoading, error }
 */
export function useEventAllParams(selectedEvent, canvasFields = []) {
  // 获取事件的所有参数
  const { data: allParams, isLoading, error } = useQuery({
    queryKey: ['event-params', selectedEvent?.id],
    queryFn: () => fetchParams(selectedEvent.id),
    enabled: !!selectedEvent,
    staleTime: 5 * 60 * 1000, // 5分钟内不重新请求
    cacheTime: 10 * 60 * 1000, // 缓存10分钟
  });

  // 合并字段状态
  const fieldsWithStatus = useMemo(() => {
    if (!allParams && !selectedEvent) {
      return [];
    }

    // 提取参数数组（fetchParams 返回 { success: true, data: [...] }）
    const params = allParams?.data || [];

    // 创建画布字段名的 Set，用于快速查找
    const canvasFieldNames = new Set(
      canvasFields.map(f => f.fieldName || f.name)
    );

    // 参数字段列表
    const paramFields = params.map(param => ({
      fieldName: param.param_name,
      displayName: param.param_name_cn || param.param_name,
      isFromCanvas: canvasFieldNames.has(param.param_name),
      group: 'parameter',
    }));

    // 基础字段列表
    const baseFields = BASE_FIELDS.map(field => ({
      fieldName: field.value,
      displayName: field.label,
      isFromCanvas: canvasFieldNames.has(field.value),
      group: 'base',
    }));

    // 合并：参数字段在前，基础字段在后
    return [...paramFields, ...baseFields];
  }, [allParams, selectedEvent, canvasFields]);

  return {
    fields: fieldsWithStatus,
    isLoading,
    error,
    paramCount: fieldsWithStatus.filter(f => f.group === 'parameter').length,
    baseCount: fieldsWithStatus.filter(f => f.group === 'base').length,
  };
}
