// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
/**
 * GameForm Shared Components
 * 统一的游戏表单组件,消除技术债务
 */

export { GameForm } from './GameForm';
export type { GameFormProps } from './GameForm';

export { default } from './GameForm';

export { ODSSelector } from './ODSSelector';
export type { ODSSelectorProps } from './ODSSelector';

export { useGameFormValidation } from './useGameFormValidation';
export type { UseGameFormValidationReturn, GameFormValidationRules } from './useGameFormValidation';

export { useGameFormToast } from './useGameFormToast';
export type { UseGameFormToastReturn } from './useGameFormToast';
