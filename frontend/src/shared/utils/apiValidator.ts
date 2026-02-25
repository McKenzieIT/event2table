export interface ValidationResult<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
}

export function validateApiResponse(
  data: unknown,
  apiName: string = 'API'
): ValidationResult {
  if (!data || typeof data !== 'object') {
    return {
      success: false,
      error: `${apiName} response is not an object`
    };
  }

  if (!('success' in data)) {
    return {
      success: false,
      error: `${apiName} response missing 'success' field`
    };
  }

  const response = data as Record<string, unknown>;

  if (response.success === false) {
    return {
      success: false,
      error: (response.message as string) || `${apiName} request failed`
    };
  }

  if (!('data' in response)) {
    return {
      success: false,
      error: `${apiName} response missing 'data' field`
    };
  }

  return { success: true, data: response.data as unknown };
}

export function validateArrayResponse(
  data: unknown,
  apiName: string = 'API'
): ValidationResult<unknown[]> {
  const validated = validateApiResponse(data, apiName);

  if (!validated.success) {
    return validated;
  }

  if (!Array.isArray(validated.data)) {
    return {
      success: false,
      error: `${apiName} response data is not an array`
    };
  }

  return { success: true, data: validated.data };
}

export function assertApiResponse(data: unknown, apiName: string = 'API'): unknown {
  const validated = validateApiResponse(data, apiName);

  if (!validated.success) {
    throw new Error(validated.error);
  }

  return validated.data;
}

export function assertArrayResponse(data: unknown, apiName: string = 'API'): unknown[] {
  const validated = validateArrayResponse(data, apiName);

  if (!validated.success) {
    throw new Error(validated.error);
  }

  return validated.data;
}

export function safeParseJSON(
  jsonString: string,
  apiName: string = 'API'
): ValidationResult {
  try {
    const data = JSON.parse(jsonString);
    return { success: true, data };
  } catch (error) {
    return {
      success: false,
      error: `${apiName} response is not valid JSON: ${(error as Error).message}`
    };
  }
}

export function validateRequiredFields(
  obj: unknown,
  requiredFields: string[],
  objectName: string = 'Object'
): ValidationResult {
  if (typeof obj !== 'object' || obj === null) {
    return {
      success: false,
      error: `${objectName} is not an object`
    };
  }

  const objRecord = obj as Record<string, unknown>;
  const missing = requiredFields.filter(field => !(field in objRecord));

  if (missing.length > 0) {
    return {
      success: false,
      error: `${objectName} is missing required fields: ${missing.join(', ')}`
    };
  }

  return { success: true, data: obj };
}
