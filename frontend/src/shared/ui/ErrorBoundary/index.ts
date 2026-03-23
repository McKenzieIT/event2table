/**
 * Error Boundary Component Exports
 * 错误边界组件导出
 */

export { ErrorBoundary } from './ErrorBoundary';
export type { 
  ErrorBoundaryProps, 
  FallbackProps, 
  ErrorInfo,
  CanvasErrorBoundaryProps,
  ErrorType,
  StandardizedError,
  ErrorHandler,
  ResetHandler,
} from './types';

// Re-export ErrorFallback from original ErrorBoundary
export { ErrorFallback } from '../ErrorBoundary';
