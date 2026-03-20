/**
 * Field Recommendation API Module
 *
 * API client for intelligent field recommendation operations
 *
 * @module fieldRecommendationApi
 */

/**
 * Field recommendation request interface
 */
export interface FieldRecommendationRequest {
  /** Parameter name to get recommendations for */
  paramName: string;
  /** Game GID for context */
  gameGid: number;
  /** Optional: event ID for more specific recommendations */
  eventId?: number;
}

/**
 * Field recommendation response interface
 */
export interface FieldRecommendationResponse {
  success: boolean;
  data: FieldRecommendationData;
  message?: string;
}

/**
 * Field recommendation data
 */
export interface FieldRecommendationData {
  /** Recommended field name */
  recommendedName: string;
  /** Recommended field type */
  recommendedType: string;
  /** Confidence score (0-1) */
  confidence: number;
  /** Alternative suggestions */
  alternatives: Array<{
    name: string;
    type: string;
    confidence: number;
  }>;
  /** Reason for recommendation */
  reason: string;
}

/**
 * Common field pattern interface
 */
export interface FieldPattern {
  /** Pattern name */
  name: string;
  /** Pattern description */
  description: string;
  /** Example values */
  examples: string[];
  /** Common field type for this pattern */
  fieldType: string;
}

/**
 * Common patterns response interface
 */
export interface CommonPatternsResponse {
  success: boolean;
  data: FieldPattern[];
  message?: string;
}

/**
 * Field type inference request interface
 */
export interface FieldTypeInferenceRequest {
  /** Parameter name to infer type for */
  paramName: string;
  /** Sample values for inference */
  sampleValues?: string[];
  /** Game GID for context */
  gameGid: number;
}

/**
 * Field type inference response interface
 */
export interface FieldTypeInferenceResponse {
  success: boolean;
  data: FieldTypeInferenceData;
  message?: string;
}

/**
 * Field type inference data
 */
export interface FieldTypeInferenceData {
  /** Inferred field type */
  inferredType: string;
  /** Confidence score (0-1) */
  confidence: number;
  /** Possible types with probabilities */
  possibleTypes: Array<{
    type: string;
    probability: number;
  }>;
  /** Reasoning for inference */
  reasoning: string;
}

/**
 * Get field recommendations for a parameter
 *
 * @param request - Field recommendation request
 * @returns Promise resolving to field recommendation data
 * @throws Error when API request fails
 *
 * @example
 * ```ts
 * const recommendation = await getRecommendations({
 *   paramName: 'user_id',
 *   gameGid: 10000147,
 *   eventId: 123
 * });
 * const recommendedName = recommendation.recommendedName;
 * ```
 */
export async function getRecommendations(
  request: FieldRecommendationRequest
): Promise<FieldRecommendationData> {
  const response = await fetch('/api/field-recommendations/recommend', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Failed to get field recommendations: ${response.statusText}`);
  }

  const result: FieldRecommendationResponse = await response.json();

  if (!result.success) {
    throw new Error(result.message || 'Field recommendation API request failed');
  }

  if (!result.data) {
    throw new Error('Invalid API response: missing data field');
  }

  return result.data;
}

/**
 * Get common field patterns
 *
 * @returns Promise resolving to array of common field patterns
 * @throws Error when API request fails
 *
 * @example
 * ```ts
 * const patterns = await getCommonPatterns();
 * const userIdPattern = patterns.find(p => p.name === 'user_id');
 * ```
 */
export async function getCommonPatterns(): Promise<FieldPattern[]> {
  const response = await fetch('/api/field-recommendations/patterns');

  if (!response.ok) {
    throw new Error(`Failed to get common patterns: ${response.statusText}`);
  }

  const result: CommonPatternsResponse = await response.json();

  if (!result.success) {
    throw new Error(result.message || 'Common patterns API request failed');
  }

  if (!result.data || !Array.isArray(result.data)) {
    throw new Error('Invalid API response: data is not an array');
  }

  return result.data;
}

/**
 * Infer field type for a parameter
 *
 * @param request - Field type inference request
 * @returns Promise resolving to field type inference data
 * @throws Error when API request fails
 *
 * @example
 * ```ts
 * const inference = await inferFieldType({
 *   paramName: 'user_id',
 *   gameGid: 10000147,
 *   sampleValues: ['123', '456', '789']
 * });
 * const inferredType = inference.inferredType;
 * ```
 */
export async function inferFieldType(
  request: FieldTypeInferenceRequest
): Promise<FieldTypeInferenceData> {
  const response = await fetch('/api/field-recommendations/types', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Failed to infer field type: ${response.statusText}`);
  }

  const result: FieldTypeInferenceResponse = await response.json();

  if (!result.success) {
    throw new Error(result.message || 'Field type inference API request failed');
  }

  if (!result.data) {
    throw new Error('Invalid API response: missing data field');
  }

  return result.data;
}
