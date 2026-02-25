import { useQuery } from '@tanstack/react-query';
import { fetchParams } from '@shared/api/eventNodeBuilderApi';
import { useMemo } from 'react';

interface BaseField {
  value: string;
  label: string;
}

interface CanvasField {
  fieldName?: string;
  name?: string;
}

interface ParamData {
  param_name: string;
  param_name_cn?: string;
}

interface FieldWithStatus {
  fieldName: string;
  displayName: string;
  isFromCanvas: boolean;
  group: 'parameter' | 'base';
}

interface UseEventAllParamsResult {
  fields: FieldWithStatus[];
  isLoading: boolean;
  error: Error | null;
  paramCount: number;
  baseCount: number;
}

interface SelectedEvent {
  id: number;
}

const BASE_FIELDS: BaseField[] = [
  { value: 'ds', label: 'ds (分区)' },
  { value: 'role_id', label: 'role_id (角色ID)' },
  { value: 'account_id', label: 'account_id (账号ID)' },
  { value: 'utdid', label: 'utdid (设备ID)' },
  { value: 'tm', label: 'tm (上报时间)' },
  { value: 'ts', label: 'ts (时间戳)' },
];

export function useEventAllParams(
  selectedEvent: SelectedEvent | null,
  canvasFields: CanvasField[] = []
): UseEventAllParamsResult {
  const { data: allParams, isLoading, error } = useQuery({
    queryKey: ['event-params', selectedEvent?.id],
    queryFn: () => fetchParams(selectedEvent!.id),
    enabled: !!selectedEvent,
    staleTime: 5 * 60 * 1000,
    cacheTime: 10 * 60 * 1000,
  });

  const fieldsWithStatus = useMemo((): FieldWithStatus[] => {
    if (!allParams && !selectedEvent) {
      return [];
    }

    const params = (allParams as { data?: ParamData[] })?.data || [];

    const canvasFieldNames = new Set(
      canvasFields.map(f => f.fieldName || f.name || '')
    );

    const paramFields: FieldWithStatus[] = params.map(param => ({
      fieldName: param.param_name,
      displayName: param.param_name_cn || param.param_name,
      isFromCanvas: canvasFieldNames.has(param.param_name),
      group: 'parameter',
    }));

    const baseFields: FieldWithStatus[] = BASE_FIELDS.map(field => ({
      fieldName: field.value,
      displayName: field.label,
      isFromCanvas: canvasFieldNames.has(field.value),
      group: 'base',
    }));

    return [...paramFields, ...baseFields];
  }, [allParams, selectedEvent, canvasFields]);

  return {
    fields: fieldsWithStatus,
    isLoading,
    error: error as Error | null,
    paramCount: fieldsWithStatus.filter(f => f.group === 'parameter').length,
    baseCount: fieldsWithStatus.filter(f => f.group === 'base').length,
  };
}
