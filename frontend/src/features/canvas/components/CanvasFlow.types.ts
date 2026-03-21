// ⚡️ REACT PERF - Canvas: Type definitions for CanvasFlow component
// Extracted from CanvasFlow.tsx for better maintainability

import { Node, Edge } from 'reactflow';
import { GameData } from './utils/hqlGenerators';

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
 * Props for CanvasFlow component
 */
export interface CanvasFlowProps {
    gameData: GameData;
    flowId?: number | string;
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
 * Props for CanvasInfoPanel component
 */
export interface CanvasInfoPanelProps {
    nodeCount: number;
    edgeCount: number;
    isLoading: boolean;
}

/**
 * Props for CanvasModals component
 */
export interface CanvasModalsProps {
    showJoinConfig: boolean;
    showHQLResult: boolean;
    selectedNode: CanvasNode | null;
    availableFields: AvailableFields;
    generatedHQL: string;
    flowName: string;
    gameData: GameData;
    outputFields: unknown[];
    onCloseJoinConfig: () => void;
    onJoinConfigApply: (config: Record<string, unknown>) => void;
    onCloseHQLResult: () => void;
    onRegenerateHQL: () => void;
}
