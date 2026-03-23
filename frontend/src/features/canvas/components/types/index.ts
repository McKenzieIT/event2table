/**
 * Canvas Components TypeScript Type Definitions
 *
 * Complete type definitions for all Canvas components
 * @version 1.0.0
 * @date 2026-02-28
 */

import { Node, Edge } from 'reactflow';

import type { Game as GameData } from '@/shared/types/game-types';
import type { Field } from '@/shared/types/hql-types';

// Re-export types for use in other canvas components
export type { Field, GameData };

// ============================================================================
// Base Types
// ============================================================================

/**
 * Canvas component-specific game data structure
 */
export interface CanvasGameData {
  id: number;
  gid: number;
  name: string;
  ods_db: string;
  description?: string;
}

/**
 * Event configuration structure
 */
export interface EventConfig {
  id?: number;
  game_gid?: number;
  event_id?: number;
  event_name?: string;
  event_name_cn?: string;
  name_cn?: string;
  base_fields?: CanvasComponentField[];
  field_count?: number;
  description?: string;
  created_at?: string;
  updated_at?: string;
}

/**
 * Canvas component-specific Field structure
 * Renamed from Field to CanvasComponentField to avoid conflicts with shared Field type
 */
export interface CanvasComponentField {
  field_name: string;
  field_type: 'base' | 'param' | 'custom';
  alias?: string;
  json_path?: string;
  custom_expression?: string;
  fixed_value?: unknown;
  aggregate_func?: string;
  displayName?: string;
  name?: string;
  type?: string;
  source?: string;
}

/**
 * Re-export shared Field type for backward compatibility
 * This allows components that import Field from './types' to work correctly
 */
export type { Field as SharedField } from '@/shared/types/hql-types';

// ============================================================================
// Node Types (ReactFlow)
// ============================================================================

/**
 * Custom node data structure
 */
export interface CustomNodeData {
  label: string;
  icon?: string;
  eventCnName?: string;
  eventName?: string;
  fieldCount?: number;
  description?: string;
  baseFields?: CanvasComponentField[];
  configId?: number;
  config?: JoinConfig;
  eventConfig?: EventConfig;
  [key: string]: unknown;
}

/**
 * ReactFlow Node with custom data
 */
export type CanvasNode = Node<CustomNodeData>;

/**
 * ReactFlow Edge
 */
export type CanvasEdge = Edge;

// ============================================================================
// JOIN Configuration Types
// ============================================================================

/**
 * JOIN condition
 */
export interface JoinCondition {
  leftField: string;
  rightField: string;
  operator: '=' | '>' | '<' | '>=' | '<=' | '<>';
}

/**
 * JOIN configuration
 */
export interface JoinConfig {
  joinType: 'INNER' | 'LEFT' | 'RIGHT' | 'FULL OUTER';
  join_type?: 'INNER' | 'LEFT' | 'RIGHT' | 'FULL OUTER';
  conditions: JoinCondition[];
}

/**
 * Available fields for JOIN configuration
 */
export interface AvailableFields {
  left: Field[];
  right: Field[];
}

// ============================================================================
// Modal/Dialog Types
// ============================================================================

/**
 * Connection prompt modal props
 */
export interface ConnectionPromptModalProps {
  isOpen: boolean;
  onClose: () => void;
  sourceNode: {
    id: string;
    type: string;
    data: { label: string };
  };
  targetOptions: Array<{
    id: string;
    type: string;
    data: { label: string };
  }>;
  onConnect: (sourceId: string, targetId: string) => void;
  onSkip?: (nodeId: string) => void;
}

/**
 * Data preview modal props
 */
export interface DataPreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  sql?: string;
  outputFields?: Field[];
  gameData?: GameData;
}

/**
 * JOIN config modal props
 */
export interface JoinConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  node: CanvasNode;
  availableFields: AvailableFields;
  onApply: (config: JoinConfig) => void;
}

/**
 * Node detail modal props
 */
export interface NodeDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  node: CanvasNode;
}

/**
 * HQL result modal props
 */
export interface HQLResultModalProps {
  isOpen: boolean;
  onClose: () => void;
  hql?: string;
  onRegenerate?: () => void;
  gameData?: GameData;
  flowName?: string;
  outputFields?: Field[];
}

// ============================================================================
// Component Props Types
// ============================================================================

/**
 * Node selector props
 */
export interface NodeSelectorProps {
  nodes: CanvasNode[];
  onSelect?: (node: CanvasNode) => void;
  selectedId?: string;
  filterType?: string;
}

/**
 * Node sidebar props
 */
export interface NodeSidebarProps {
  gameData: GameData;
  savedConfigs: EventConfig[];
  onConfigsLoad?: (configs: EventConfig[]) => void;
  onAddNode?: (nodeData: Partial<CanvasNode>) => void;
}

/**
 * Search bar props
 */
export interface SearchBarProps {
  onSearch: (searchTerm: string) => void;
}

/**
 * Toolbar props
 */
export interface ToolbarProps {
  gameData: GameData;
  onExecute?: () => void;
  onLocateNodes?: () => void;
}

/**
 * Custom node props (ReactFlow custom node)
 */
export interface CustomNodeProps {
  data: CustomNodeData;
  selected?: boolean;
}

/**
 * Node context menu props
 */
export interface NodeContextMenuProps {
  position: { x: number; y: number };
  node: CanvasNode;
  onClose: () => void;
  onViewDetail: (node: CanvasNode) => void;
  onEdit?: (node: CanvasNode) => void;
  onDelete: (node: CanvasNode) => void;
}

/**
 * Properties panel props
 */
export interface PropertiesPanelProps {
  selectedNode: CanvasNode | null;
  nodes: CanvasNode[];
  edges: CanvasEdge[];
  onUpdateNode: (nodeId: string, updates: Partial<CustomNodeData>) => void;
  onConfigure?: (node: CanvasNode) => void;
  onClose: () => void;
}

/**
 * Canvas flow props
 */
export interface CanvasFlowProps {
  gameData: GameData;
  flowId?: number;
}

/**
 * App props
 */
export interface AppProps {
  gameData?: GameData;
}

// ============================================================================
// Data Preview Types
// ============================================================================

/**
 * Preview data response
 */
export interface PreviewDataResponse {
  success: boolean;
  data?: {
    columns: string[];
    rows: unknown[][];
    row_count: number;
    execution_time_ms: number;
  };
  message?: string;
}

// ============================================================================
// HQL Related Types
// ============================================================================

/**
 * SQL statistics
 */
export interface SQLStats {
  characterCount: number;
  lineCount: number;
  keywordCount: number;
}

/**
 * Flow execution payload
 */
export interface FlowExecutionPayload {
  flow_id?: number;
  flowData: {
    nodes: Partial<CanvasNode>[];
    edges: Partial<CanvasEdge>[];
  };
}

/**
 * Flow execution response
 */
export interface FlowExecutionResponse {
  success: boolean;
  hql?: string;
  output_fields?: Field[];
  message?: string;
  error?: string;
}

// ============================================================================
// Utility Types
// ============================================================================

/**
 * Connected node information
 */
export interface ConnectedNode {
  id: string;
  label: string;
  type: string;
}

/**
 * Connected nodes grouped by direction
 */
export interface ConnectedNodes {
  inputs: ConnectedNode[];
  outputs: ConnectedNode[];
}

/**
 * Flow save payload
 */
export interface FlowSavePayload {
  name: string;
  game_gid: number;
  game_id?: number;
  nodes: Partial<CanvasNode>[];
  edges: Partial<CanvasEdge>[];
}