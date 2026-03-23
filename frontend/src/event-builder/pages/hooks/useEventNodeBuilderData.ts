import { loadEventConfig } from '@features/canvas/api/canvasApi';
import { useToast } from '@features/canvas/components/hooks/useToast';
import type { CanvasField, WhereCondition } from '@shared/hooks/useEventNodeBuilder';
import type { Game } from '@shared/hooks/useGameContext';
import type { Event } from '@shared/types/api-types';
import { useMutation } from '@tanstack/react-query';
import { useEffect } from 'react';

import type { ConfigData } from '../EventNodeBuilder.types';


/**
 * LocalEventConfig interface for type safety (extended from canvas EventConfig)
 */
interface LocalEventConfig {
  id: number;
  game_gid: number;
  event_id: number;
  name: string;
  name_en?: string;
  name_cn?: string;
  description?: string;
  event?: Event;
  base_fields?: Array<{
    field_type: string;
    field_name: string;
    display_name: string;
    alias?: string;
    order: number;
    param_id?: number | null;
    hive_type?: string;
  }>;
  filter_conditions?: string | WhereCondition[];
}

// TODO: Create saveEventConfig function in canvasApi.ts
// For now, we'll create a temporary implementation
async function saveEventConfig(configData: any): Promise<any> {
  const response = await fetch('/event_node_builder/api/save', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(configData),
  });

  if (!response.ok) {
    throw new Error(`Failed to save event config: ${response.statusText}`);
  }

  const result = await response.json();

  if (!result.success) {
    throw new Error(result.message || 'Save event config request failed');
  }

  return result.data;
}

interface UseEventNodeBuilderDataProps {
  gameData?: Game | null;
  configIdParam: string | null;
  selectedEvent: Event | null;
  canvasFields: CanvasField[];
  nodeConfig: {
    nameEn: string;
    nameCn: string;
    description: string;
  };
  whereConditions: WhereCondition[];
  onSetSelectedEvent: (event: Event | null) => void;
  onSetCanvasFields: (fields: CanvasField[]) => void;
  onSetWhereConditions: (conditions: WhereCondition[]) => void;
  onSetNodeConfig: (config: { nameEn: string; nameCn: string; description: string }) => void;
}

export function useEventNodeBuilderData({
  gameData,
  configIdParam,
  selectedEvent,
  canvasFields,
  nodeConfig,
  whereConditions,
  onSetSelectedEvent,
  onSetCanvasFields,
  onSetWhereConditions,
  onSetNodeConfig,
}: UseEventNodeBuilderDataProps) {
  const { success, error } = useToast();

  // 保存配置 mutation
  const saveMutation = useMutation({
    mutationFn: async (configData: ConfigData) => {
      // 解析filter_conditions JSON字符串
      let parsedWhereConditions: WhereCondition[] = [];
      try {
        const filterObj = JSON.parse(configData.filter_conditions);
        parsedWhereConditions = filterObj.conditions || [];
      } catch (e) {
        console.warn('Failed to parse filter_conditions:', e);
      }

      // 转换为后端期望的SaveConfigRequest格式
      const requestData = {
        game_gid: configData.game_gid,
        event_id: configData.event_id,
        name: configData.name_en,
        config: {
          fields: configData.base_fields.map(f => ({
            field_name: f.field_name,
            display_name: f.display_name,
            data_type: 'string',
            is_required: false,
          })),
          where_conditions: parsedWhereConditions,
          name_cn: configData.name_cn,
          description: configData.description,
        },
      };
      return saveEventConfig(requestData as any);
    },
    onSuccess: (result) => {
      success(`配置 "${result.name_en || '配置'}" 保存成功！`);
    },
    onError: (err: Error) => {
      error('保存失败: ' + (err.message || '未知错误'));
    },
  });

  // 加载配置（编辑模式）
  useEffect(() => {
    if (configIdParam && gameData) {
      loadEventConfig(Number(configIdParam), Number(gameData.gid)).then(config => {
        if (config) {
          // 设置事件
          if ((config as LocalEventConfig).event) {
            onSetSelectedEvent((config as LocalEventConfig).event!);
          }
          // 设置字段
          if ((config as LocalEventConfig).base_fields && Array.isArray((config as LocalEventConfig).base_fields)) {
            onSetCanvasFields((config as LocalEventConfig).base_fields!.map((f: any, index: number) => ({
              id: String(Date.now() + index),
              fieldType: f.field_type,
              fieldName: f.field_name,
              displayName: f.display_name,
              alias: f.alias || '',
              order: index + 1,
              paramId: f.param_id,
              type: f.field_type === 'param' ? 'parameter' : f.field_type,
              name: f.field_name,
              dataType: f.hive_type || 'STRING',
              isEditable: true,
            })));
          }
          // 设置WHERE条件
          if ((config as LocalEventConfig).filter_conditions) {
            try {
              const where = typeof (config as LocalEventConfig).filter_conditions === 'string'
                ? JSON.parse((config as LocalEventConfig).filter_conditions as string)
                : (config as LocalEventConfig).filter_conditions;
              onSetWhereConditions(where as WhereCondition[]);
            } catch (e) {
              console.error('[EventNodeBuilder] Failed to parse WHERE conditions:', e);
            }
          }
          // 设置节点配置
          onSetNodeConfig({
            nameEn: (config as LocalEventConfig).name_en || '',
            nameCn: (config as LocalEventConfig).name_cn || '',
            description: (config as LocalEventConfig).description || '',
          });
        }
      }).catch(err => {
        console.error('[EventNodeBuilder] Failed to load config:', err);
      });
    }
  }, [configIdParam, gameData, onSetSelectedEvent, onSetCanvasFields, onSetWhereConditions, onSetNodeConfig]);

  return { saveMutation };
}