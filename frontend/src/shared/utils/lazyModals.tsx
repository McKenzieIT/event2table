/**
 * Lazy Modal Loader Utility
 *
 * Provides code splitting and lazy loading for modal components
 * to reduce initial bundle size and improve page load performance.
 *
 * Usage:
 * import { LazyGameManagementModal, LazyEventManagementModal } from '@shared/utils/lazyModals';
 *
 * function App() {
 *   return (
 *     <Suspense fallback={<ModalSpinner />}>
 *       <LazyGameManagementModal isOpen={isOpen} onClose={handleClose} />
 *     </Suspense>
 *   );
 * }
 */

import React, { Suspense, lazy, ComponentType } from 'react';
import { Spinner } from '@shared/ui';

interface LazyModalWrapperProps {
  isOpen: boolean;
  [key: string]: any;
}

// Loading component for lazy modals
export const ModalSpinner: React.FC = () => (
  <div className="modal-loading-spinner">
    <Spinner size="lg" label="加载中..." />
  </div>
);

// Generic lazy modal wrapper
function createLazyModal<P extends object>(
  importFunc: () => Promise<{ default: ComponentType<P> }>
): React.FC<P & LazyModalWrapperProps> {
  const LazyComponent = lazy(importFunc);

  const LazyModalWrapper: React.FC<P & LazyModalWrapperProps> = (props) => {
    const { isOpen, ...rest } = props;

    if (!isOpen) {
      return null;
    }

    return (
      <Suspense fallback={<ModalSpinner />}>
        <LazyComponent {...(rest as P)} isOpen={isOpen} />
      </Suspense>
    );
  };

  LazyModalWrapper.displayName = 'LazyModalWrapper';
  return LazyModalWrapper;
}

// Lazy-loaded modal components
export const LazyGameManagementModalGraphQL = createLazyModal(
  () => import('../../features/games/GameManagementModalGraphQL')
);

export const LazyEventManagementModalGraphQL = createLazyModal(
  () => import('../../features/events/EventManagementModalGraphQL')
);

export const LazyAddEventModalGraphQL = createLazyModal(
  () => import('../../features/events/AddEventModalGraphQL')
);

export const LazyAddGameModalGraphQL = createLazyModal(
  () => import('../../features/games/AddGameModalGraphQL')
);

export const LazyCategoryManagementModal = createLazyModal(
  () => import('../../analytics/components/categories/CategoryManagementModal')
);

export const LazyCategoryModal = createLazyModal(
  () => import('../../analytics/components/categories/CategoryModal')
);

export const LazyCommonParamsModal = createLazyModal(
  () => import('../../analytics/components/parameters/CommonParamsModal')
);

export const LazyNodeConfigModal = createLazyModal(
  () => import('../../event-builder/components/modals/NodeConfigModal')
);

export const LazyFieldConfigModal = createLazyModal(
  () => import('../../event-builder/components/modals/FieldConfigModal')
);

export const LazyHQLResultModal = createLazyModal(
  () => import('../../features/canvas/components/HQLResultModal')
);

export const LazyJoinConfigModal = createLazyModal(
  () => import('../../features/canvas/components/JoinConfigModal')
);

export const LazyDataPreviewModal = createLazyModal(
  () => import('../../features/canvas/components/DataPreviewModal')
);

// Preload utility for critical modals
export function preloadModal(modalLoader: () => Promise<any>) {
  // Start loading the modal in the background
  modalLoader();
}

// Preload all critical modals
export function preloadCriticalModals() {
  preloadModal(() => import('../../features/games/GameManagementModalGraphQL'));
  preloadModal(() => import('../../features/events/AddEventModalGraphQL'));
  preloadModal(() => import('../../features/games/AddGameModalGraphQL'));
}

// Prefetch modals on user interaction
export function useModalPrefetch(modalLoader: () => Promise<any>, delay: number = 100) {
  const prefetchTimer = useRef<NodeJS.Timeout>();

  const startPrefetch = () => {
    if (prefetchTimer.current) {
      clearTimeout(prefetchTimer.current);
    }

    prefetchTimer.current = setTimeout(() => {
      preloadModal(modalLoader);
    }, delay);
  };

  const cancelPrefetch = () => {
    if (prefetchTimer.current) {
      clearTimeout(prefetchTimer.current);
    }
  };

  return { startPrefetch, cancelPrefetch };
}

export default createLazyModal;
