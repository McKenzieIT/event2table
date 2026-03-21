import type { Game } from '@shared/hooks/useGameContext';
import type { Event } from '@shared/types/api-types';

export interface OutletContext {
  currentGame?: Game | null;
}

export interface ConfirmState {
  open: boolean;
  onConfirm: () => void;
  title: string;
  message: string;
}

export interface ConfigData {
  game_gid: number;
  event_id: number;
  name_en: string;
  name_cn: string;
  description: string;
  base_fields: Array<{
    field_type: string;
    field_name: string;
    display_name: string;
    alias?: string;
    order: number;
    param_id?: number | null;
  }>;
  filter_conditions: string;
}

export interface FieldUpdate {
  fieldType?: string;
  fieldName?: string;
  displayName?: string;
  alias?: string;
  paramId?: number | null;
  jsonPath?: string | null;
}

export interface DragDropField {
  fieldType?: string;
  fieldName?: string;
  displayName?: string;
  paramId?: number | null;
  type?: string;
  name?: string;
  alias?: string;
  sourceId?: number | null;
  hive_type?: string;
  dataType?: string;
}

export interface ConfirmState {
  open: boolean;
  onConfirm: () => void;
  title: string;
  message: string;
}
