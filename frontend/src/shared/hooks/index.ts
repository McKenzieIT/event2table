/**
 * Shared Hooks Index
 */

export { useSidebar } from './useSidebar';
export type { UseSidebarReturn } from './useSidebar';

export { useGameContext } from './useGameContext';
export type { UseGameContextReturn } from './useGameContext';

export { useConfirm } from './useConfirm';
export type { UseConfirmReturn, ConfirmOptions } from './useConfirm';

export { useChromeMCPCompatibleInput, useChromeMCPForm } from './useChromeMCPCompatibleInput';
export type {
  UseChromeMCPCompatibleInputOptions,
  UseChromeMCPCompatibleInputReturn,
  FormValuesFromFields,
} from './useChromeMCPCompatibleInput';

export { useConfirmDialog } from './useConfirmDialog';
export type { UseConfirmDialogReturn, ConfirmDialogOptions, DialogState } from './useConfirmDialog';

export { useEventNodesTable } from './useEventNodesTable';
export type { UseEventNodesTableReturn, EventNodesColumnDef } from './useEventNodesTable';

export { useEventNodeBuilder } from './useEventNodeBuilder';
export type {
  UseEventNodeBuilderReturn,
  CanvasField,
  WhereCondition,
  NodeConfig,
  SidebarCollapsed
} from './useEventNodeBuilder';

export { useFormValidation } from './useFormValidation';
export type { UseFormValidationReturn, ValidationRules } from './useFormValidation';

export { usePromiseConfirm } from './usePromiseConfirm';
export type { UsePromiseConfirmReturn, ConfirmOptions as PromiseConfirmOptions } from './usePromiseConfirm';

export { useRetry, useAsyncRetry } from './useRetry';
export type { RetryOptions, RetryState, RetryReturn } from './useRetry';

// Error Handling Hooks
export {
  useErrorHandler,
  type ErrorHandlerOptions,
  type ErrorHandlerState,
  type ErrorHandlerResult,
} from './useErrorHandler';

export {
  useAsyncAction,
  useAsyncActionWithParams,
  type AsyncState,
  type AsyncActionOptions,
  type AsyncActionResult,
} from './useAsyncAction';
