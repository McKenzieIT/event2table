/**
 * API Type Definitions
 */

/**
 * Standard API Response (Success)
 */
export interface ApiSuccessResponse<T = unknown> {
  success: true;
  data: T;
  message?: string;
  timestamp: string;
}

/**
 * Standard API Response (Error)
 */
export interface ApiErrorResponse {
  success: false;
  error: string;
  error_type?: string;
  details?: Record<string, string>;
  timestamp: string;
}

/**
 * Fetch Error Class
 */
export class FetchError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: ApiErrorResponse | unknown
  ) {
    super(message);
    this.name = 'FetchError';
  }

  /**
   * Create FetchError from fetch Response
   */
  static async fromResponse(response: Response): Promise<FetchError> {
    let data: unknown = null;

    try {
      data = await response.json();
    } catch {
      // Response body is not JSON or is empty
      try {
        data = await response.text();
      } catch {
        // Response body is not text
      }
    }

    const errorData = data as ApiErrorResponse;
    const message = errorData?.error || errorData?.message || `HTTP ${response.status}`;

    return new FetchError(message, response.status, data);
  }

  /**
   * Check if this is a specific error type
   */
  isValidation(): boolean {
    return this.status === 400 || this.status === 422;
  }

  isNotFound(): boolean {
    return this.status === 404;
  }

  isConflict(): boolean {
    return this.status === 409;
  }

  isServerError(): boolean {
    return this.status >= 500;
  }

  isNetworkError(): boolean {
    return this.status === 0;
  }
}

/**
 * API Request Options
 */
export interface ApiRequestOptions extends RequestInit {
  /** Automatically parse JSON response */
  parseJson?: boolean;
  /** Throw FetchError on non-OK response */
  throwOnError?: boolean;
  /** Request timeout in milliseconds */
  timeout?: number;
}

/**
 * API Client Configuration
 */
export interface ApiClientConfig {
  /** Base URL for all requests */
  baseURL?: string;
  /** Default headers */
  headers?: Record<string, string>;
  /** Request timeout (default: 30000ms) */
  timeout?: number;
  /** Enable debug logging */
  debug?: boolean;
}

/**
 * Pagination Parameters
 */
export interface PaginationParams {
  page?: number;
  per_page?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

/**
 * Paginated Response
 */
export interface PaginatedResponse<T> {
  items: T[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}
