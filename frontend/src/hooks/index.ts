/**
 * Custom Hooks Index
 *
 * Re-export all custom hooks from shared module
 * This directory is kept for backward compatibility
 *
 * All hooks are now defined in @shared/hooks/
 */

// Re-export usePageVisibility hooks
export { usePageVisibility, usePollingInterval, useSmartPolling } from '../shared/hooks/usePageVisibility';

// Re-export useDebounce hook
export { useDebounce } from '../shared/hooks/useDebounce';