/**
 * Canvas API Module
 *
 * API client for communicating with Flask backend
 *
 * @module canvasApi
 */

import type {
  FlowData,
  SavedFlow,
  EventConfig,
  ExecutionResult,
  HealthCheckResponse,
  ApiResponse,
  EventConfigQueryOptions,
  SaveFlowOptions,
} from '../types';

/**
 * Fetches list of event node configurations
 *
 * @param gameGid - Game GID
 * @returns Promise resolving to array of event configs
 * @throws Error when API request fails
 *
 * @example
 * ```ts
 * const configs = await listEventConfigs(10000147);
 * console.log(configs[0].name_cn); // "登录事件"
 * ```
 */
export async function listEventConfigs(
  gameGid: number
): Promise<EventConfig[]> {
  try {
    const response = await fetch(
      `/event_node_builder/api/list?game_gid=${gameGid}`
    );

    if (!response.ok) {
      throw new Error(`Failed to list event configs: ${response.statusText}`);
    }

    const result: ApiResponse<EventConfig[]> = await response.json();

    if (!result.success) {
      throw new Error(result.message || 'List event configs request failed');
    }

    if (!Array.isArray(result.data)) {
      throw new Error('Invalid API response: data.data is not an array');
    }

    return result.data;
  } catch (error) {
    console.error('[API] Failed to list event configs:', error);
    throw error;
  }
}

/**
 * Loads a single event node configuration
 *
 * @param configId - Configuration ID
 * @param gameGid - Game GID
 * @returns Promise resolving to event config data
 * @throws Error when API request fails
 *
 * @example
 * ```ts
 * const config = await loadEventConfig(456, 10000147);
 * console.log(config.fields); // Field list
 * ```
 */
export async function loadEventConfig(
  configId: number,
  gameGid: number
): Promise<EventConfig> {
  try {
    const response = await fetch(
      `/event_node_builder/api/load/${configId}?game_gid=${gameGid}`
    );

    if (!response.ok) {
      throw new Error(`Failed to load event config: ${response.statusText}`);
    }

    const result: ApiResponse<EventConfig> = await response.json();

    if (!result.success) {
      throw new Error(result.message || 'Load event config request failed');
    }

    return result.data;
  } catch (error) {
    console.error('[API] Failed to load event config:', error);
    throw error;
  }
}

/**
 * Saves a flow
 *
 * @param options - Save flow options containing game ID and flow data
 * @returns Promise resolving to saved flow
 * @throws Error when API request fails
 *
 * @example
 * ```ts
 * const flow = await saveFlow({
 *   gameId: 10000147,
 *   flowData: {
 *     nodes: [{ id: '1', type: 'event', x: 100, y: 100, data: {} }],
 *     edges: []
 *   }
 * });
 * console.log(flow.id); // New flow ID
 * ```
 */
export async function saveFlow(
  options: SaveFlowOptions
): Promise<SavedFlow> {
  const { gameId, flowData } = options;

  try {
    const response = await fetch('/canvas/api/flows/save', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        game_id: gameId,
        flow_data: flowData,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to save flow: ${response.statusText}`);
    }

    const result: ApiResponse<SavedFlow> = await response.json();

    if (!result.success) {
      throw new Error(result.message || 'Save flow request failed');
    }

    return result.data;
  } catch (error) {
    console.error('[API] Failed to save flow:', error);
    throw error;
  }
}

/**
 * Loads a saved flow
 *
 * @param flowId - Flow ID
 * @returns Promise resolving to flow data
 * @throws Error when API request fails
 *
 * @example
 * ```ts
 * const flow = await loadFlow(789);
 * console.log(flow.flow_data.nodes); // Node list
 * ```
 */
export async function loadFlow(flowId: number): Promise<SavedFlow> {
  try {
    const response = await fetch(`/canvas/api/flows/${flowId}`);

    if (!response.ok) {
      throw new Error(`Failed to load flow: ${response.statusText}`);
    }

    const result: ApiResponse<SavedFlow> = await response.json();

    if (!result.success) {
      throw new Error(result.message || 'Load flow request failed');
    }

    return result.data;
  } catch (error) {
    console.error('[API] Failed to load flow:', error);
    throw error;
  }
}

/**
 * Executes HQL generation
 *
 * @param flowData - Flow data to execute
 * @returns Promise resolving to execution result
 * @throws Error when API request fails
 *
 * @example
 * ```ts
 * const result = await executeFlow({
 *   nodes: [...],
 *   edges: [...]
 * });
 * console.log(result.hql); // "CREATE OR REPLACE VIEW..."
 * ```
 */
export async function executeFlow(flowData: FlowData): Promise<ExecutionResult> {
  try {
    const response = await fetch('/canvas/api/execute', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(flowData),
    });

    if (!response.ok) {
      throw new Error(`Failed to execute flow: ${response.statusText}`);
    }

    const result: ApiResponse<ExecutionResult> = await response.json();

    if (!result.success) {
      throw new Error(result.message || 'Execute flow request failed');
    }

    return result.data || (result as unknown as ExecutionResult);
  } catch (error) {
    console.error('[API] Failed to execute flow:', error);
    throw error;
  }
}

/**
 * Performs canvas health check
 *
 * @returns Promise resolving to health status
 * @throws Error when API request fails
 *
 * @example
 * ```ts
 * const health = await healthCheck();
 * console.log(health.healthy); // true
 * ```
 */
export async function healthCheck(): Promise<HealthCheckResponse> {
  try {
    const response = await fetch('/canvas/api/canvas/health');

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }

    const result: ApiResponse<HealthCheckResponse> = await response.json();

    if (!result.success) {
      throw new Error(result.message || 'Health check request failed');
    }

    return result.data || (result as unknown as HealthCheckResponse);
  } catch (error) {
    console.error('[API] Health check failed:', error);
    throw error;
  }
}
