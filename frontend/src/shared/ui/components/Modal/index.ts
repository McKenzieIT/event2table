/**
 * Modal Component Exports
 * 
 * 统一Modal组件导出
 */

export { Modal } from './Modal';
export { default } from './Modal';

export type {
  ModalProps,
  ModalSize,
  ModalAnimation,
  ModalVariant,
  ModalConfirmConfig,
  UseModalReturn,
} from './Modal.types';

export { useModal } from '@shared/ui/hooks/useModal/useModal';
export type { UseModalOptions } from '@shared/ui/hooks/useModal/useModal';
