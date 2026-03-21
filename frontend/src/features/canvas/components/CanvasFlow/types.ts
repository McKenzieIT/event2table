import { Node, Edge } from 'reactflow';

/**
 * Extended Node data interface for Canvas nodes
 */
export interface CanvasNodeData {
  label?: string;
  configId?: number;
  config?: Record<string, unknown>;
  eventConfig?: {
    event_name?: string;
    event_name_cn?: string;
    fieldCount?: number;
    [key: string]: unknown;
  };
  eventData?: {
    fields?: Array<{
      name: string;
      type?: string;
      source?: string;
    }>;
    [key: string]: unknown;
  };
  [key: string]: unknown;
}

/**
 * Extended Node type with Canvas-specific data
 */
export type CanvasNode = Node<CanvasNodeData>;

/**
 * Available fields for JOIN configuration
 */
export interface AvailableFields {
  left: Array<{
    name: string;
    type?: string;
    source?: string;
  }>;
  right: Array<{
    name: string;
    type?: string;
    source?: string;
  }>;
}

/**
 * Saved config structure
 */
export interface SavedConfig {
  id: number;
  name: string;
  [key: string]: unknown;
}

/**
 * Flow data payload for save/execute
 */
export interface FlowDataPayload {
  name?: string;
  game_gid: number | string;
  game_id?: number;
  nodes: Array<{
    id: string;
    type: string;
    position: { x: number; y: number };
    data: CanvasNodeData;
  }>;
  edges: Array<{
    id: string;
    source: string;
    target: string;
  }>;
}

/**
 * Game data
 */
export interface GameData {
  gid: number;
  ods_db?: string;
  name?: string;
  id?: number;
}

/**
 * Canvas flow props
 */
export interface CanvasFlowProps {
  gameData: GameData;
  flowId?: number | string;
}
