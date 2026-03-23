// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

/**
 * BindToLibraryButton 组件 - 绑定到库按钮
 *
 * 为未绑定参数库的参数提供绑定按钮
 * 点击按钮打开 BindToLibraryModal 进行选择
 *
 * @example
 * <BindToLibraryButton
 *   paramId={123}
 *   paramName="accountId"
 *   templateId={1}
 * />
 */

import { Button } from '@shared/ui';
import React, { useState } from 'react';

import { BindToLibraryModal } from './BindToLibraryModal';

export interface BindToLibraryButtonProps {
  paramId: number;
  paramName: string;
  templateId: number;
}

export function BindToLibraryButton({ paramId, paramName, templateId }: BindToLibraryButtonProps) {
  const [showModal, setShowModal] = useState(false);

  return (
    <>
      <Button
        variant="outline-primary"
        size="sm"
        onClick={() => setShowModal(true)}
      >
        绑定到库
      </Button>
      {showModal && (
        <BindToLibraryModal
          paramId={paramId}
          paramName={paramName}
          templateId={templateId}
          onClose={() => setShowModal(false)}
        />
      )}
    </>
  );
}
