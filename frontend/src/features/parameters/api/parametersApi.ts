/**
 * Parameters API Module
 *
 * API client for parameter management operations
 *
 * @module parametersApi
 */

import type {
  Parameter,
  ParameterDetails,
  FetchParametersOptions,
  ParametersListResponse,
  ParameterDetailsResponse,
} from '../types';

/**
 * Fetches all unique parameters for a game (deduplicated)
 *
 * @param gameGid - Game GID
 * @param options - Query options
 * @returns Promise resolving to array of parameters
 * @throws Error when API response is invalid or request fails
 *
 * @example
 * ```ts
 * const params = await fetchAllParameters(10000147, { page: 1, limit: 20 });
 * console.log(params[0].param_name); // "zone_id"
 * ```
 */
export async function fetchAllParameters(
  gameGid: number,
  options: FetchParametersOptions = {}
): Promise<Parameter[]> {
  const { page = 1, limit = 50, search = '', type = '' } = options;

  const params = new URLSearchParams({
    game_gid: gameGid.toString(),
    page: page.toString(),
    limit: limit.toString(),
  });

  if (search) params.append('search', search);
  if (type) params.append('type', type);

  const response = await fetch(`/api/parameters/all?${params}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch parameters: ${response.statusText}`);
  }

  const data: ParametersListResponse = await response.json();

  // Explicitly validate response structure
  if (!data.success) {
    throw new Error(data.message || 'Parameters API request failed');
  }

  // API returns structure: { success: true, data: { parameters: [...], has_more, page } }
  if (!data.data || !Array.isArray(data.data.parameters)) {
    throw new Error(
      'Invalid API response: data.data.parameters is not an array'
    );
  }

  return data.data.parameters;
}

/**
 * Fetches parameter details (cross-event usage)
 *
 * @param paramName - Parameter name
 * @param gameGid - Game GID
 * @returns Promise resolving to parameter details
 * @throws Error when parameter doesn't exist (404) or request fails
 *
 * @example
 * ```ts
 * const details = await fetchParameterDetails('zone_id', 10000147);
 * console.log(details.total_usage); // 15
 * console.log(details.usage_in_events.length); // 5 events
 * ```
 */
export async function fetchParameterDetails(
  paramName: string,
  gameGid: number
): Promise<ParameterDetails> {
  const response = await fetch(
    `/api/parameters/${encodeURIComponent(paramName)}/details?game_gid=${gameGid}`
  );

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error(`Parameter not found: ${paramName}`);
    }
    throw new Error(
      `Failed to fetch parameter details: ${response.statusText}`
    );
  }

  const data: ParameterDetailsResponse = await response.json();

  // Explicitly validate response structure
  if (!data.success) {
    throw new Error(data.message || 'Parameter details API request failed');
  }

  if (!data.data) {
    throw new Error('Invalid API response: missing data field');
  }

  return data.data;
}
