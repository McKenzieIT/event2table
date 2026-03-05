import { useLocation } from 'react-router-dom';

/**
 * Custom hook to properly parse URL query parameters with HashRouter
 *
 * HashRouter stores query parameters in the hash portion of the URL:
 * - Format: http://localhost:5173/#/flows?game_gid=10000147
 * - location.hash: "#/flows?game_gid=10000147"
 * - location.search: "" (empty with HashRouter)
 *
 * BrowserRouter stores query parameters in the search portion:
 * - Format: http://localhost:5173/flows?game_gid=10000147
 * - location.search: "?game_gid=10000147"
 *
 * This hook provides a unified way to access query params that works with both routers.
 */
export function useQueryParams(): URLSearchParams {
  const location = useLocation();

  // Try location.search first (for BrowserRouter)
  if (location.search) {
    return new URLSearchParams(location.search);
  }

  // Fallback: parse query params from hash (for HashRouter)
  // Hash format examples:
  // - #/flows?game_gid=10000147
  // - #/flows?game_gid=10000147&other=value
  // - #/flows?game_gid=10000147#anchor
  const hashMatch = location.hash.match(/\?([^#]+)/);
  if (hashMatch) {
    return new URLSearchParams(hashMatch[1]);
  }

  // No query params found
  return new URLSearchParams('');
}

/**
 * Convenience hook to get a specific query parameter
 *
 * @example
 * const gameGid = useQueryParam('game_gid');
 * const page = useQueryParam('page');
 */
export function useQueryParam(paramName: string): string | null {
  const params = useQueryParams();
  return params.get(paramName);
}
