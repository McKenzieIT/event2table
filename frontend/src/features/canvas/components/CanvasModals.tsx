// ⚡️ REACT PERF - Canvas: Modals component with lazy loading
// Extracted from CanvasFlow.tsx for better maintainability

import React, { Suspense, memo } from 'react';
import { Spinner } from '@shared/ui';
import { LazyJoinConfigModal, LazyHQLResultModal } from '@shared/utils/lazyModals';
import { CanvasModalsProps } from './CanvasFlow.types';

/**
 * CanvasModals Component
 *
 * Manages all modal dialogs (JOIN config, HQL result)
 * Uses lazy loading to reduce initial bundle size
 */
const CanvasModals: React.FC<CanvasModalsProps> = memo(({
    showJoinConfig,
    showHQLResult,
    selectedNode,
    availableFields,
    generatedHQL,
    flowName,
    gameData,
    outputFields,
    onCloseJoinConfig,
    onJoinConfigApply,
    onCloseHQLResult,
    onRegenerateHQL
}) => {
    return (
        <>
            {/* JOIN configuration modal - Lazy loaded */}
            {showJoinConfig && (
                <Suspense fallback={<Spinner size="lg" label="加载中..." />}>
                    <LazyJoinConfigModal
                        isOpen={showJoinConfig}
                        onClose={onCloseJoinConfig}
                        node={selectedNode}
                        availableFields={availableFields}
                        onApply={onJoinConfigApply}
                        data-testid="join-config-modal"
                    />
                </Suspense>
            )}

            {/* HQL result modal - Lazy loaded */}
            {showHQLResult && (
                <Suspense fallback={<Spinner size="lg" label="加载中..." />}>
                    <LazyHQLResultModal
                        isOpen={showHQLResult}
                        onClose={onCloseHQLResult}
                        hql={generatedHQL}
                        flowName={flowName}
                        gameData={gameData}
                        onRegenerate={onRegenerateHQL}
                        outputFields={outputFields}
                        data-testid="hql-result-modal"
                    />
                </Suspense>
            )}
        </>
    );
});

CanvasModals.displayName = 'CanvasModals';

export default CanvasModals;
