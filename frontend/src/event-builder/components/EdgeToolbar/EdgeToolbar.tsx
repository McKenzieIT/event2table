// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
/**
 * EdgeToolbar Component
 * 底部边缘激活栏 - 鼠标靠近底部时从底部滑入
 */
import React, { useState, useCallback } from "react";
import EdgeToolbarButton from "./EdgeToolbarButton";
import QuickFieldTools from "./QuickFieldTools";
import FieldSelectorPanel from "../FieldSelectorPanel";

/**
 * Canvas Field interface
 */
interface CanvasField {
  id: string;
  fieldType: string;
  fieldName?: string;
  name: string;
  displayName?: string;
  alias?: string;
  dataType: string;
}

/**
 * EdgeToolbar Props interface
 */
interface EdgeToolbarProps {
  canvasFields?: CanvasField[];
  onAddBaseField: () => void;
  onAddCustomField: () => void;
  onAddFixedField: () => void;
  onQuickAddCommon: () => void;
  onQuickAddAll: () => void;
  onAddField: (field: CanvasField) => void;
}

export default function EdgeToolbar({
  canvasFields = [],
  onAddBaseField,
  onAddCustomField,
  onAddFixedField,
  onQuickAddCommon,
  onQuickAddAll,
  onAddField,
}: EdgeToolbarProps): React.JSX.Element {
  const [showQuickTools, setShowQuickTools] = useState<boolean>(false);
  const [showFieldSelector, setShowFieldSelector] = useState<boolean>(false);

  const handleToggleQuickTools = useCallback(() => {
    setShowQuickTools((prev) => !prev);
  }, []);

  const handleShowFieldSelector = useCallback(() => {
    setShowFieldSelector(true);
  }, []);

  const handleCloseFieldSelector = useCallback(() => {
    setShowFieldSelector(false);
  }, []);

  const handleQuickAdd = useCallback(
    (type: string) => {
      if (type === "common") {
        onQuickAddCommon();
      } else if (type === "all") {
        onQuickAddAll();
      }
    },
    [onQuickAddCommon, onQuickAddAll],
  );

  return (
    <>
      <div className="edge-toolbar">
        {/* 主要操作区 */}
        <div className="toolbar-section">
          <EdgeToolbarButton
            icon="bi-type"
            label="基础"
            title="添加基础字段"
            onClick={handleShowFieldSelector}
          />
          <EdgeToolbarButton
            icon="bi-code"
            label="自定义"
            title="添加自定义字段"
            onClick={onAddCustomField}
          />
          <EdgeToolbarButton
            icon="bi-pin"
            label="固定值"
            title="添加固定值字段"
            onClick={onAddFixedField}
          />
        </div>

        <div className="toolbar-divider" />

        {/* 快速工具区 */}
        <div className="toolbar-section toolbar-section--quick">
          <EdgeToolbarButton
            icon="bi-bolt"
            label="快速"
            title="快速添加工具"
            active={showQuickTools}
            onClick={handleToggleQuickTools}
          />

          {showQuickTools && <QuickFieldTools onQuickAdd={handleQuickAdd} />}
        </div>
      </div>

      {/* Field Selector Panel */}
      <FieldSelectorPanel
        isVisible={showFieldSelector}
        canvasFields={canvasFields}
        onAddField={onAddField}
        onClose={handleCloseFieldSelector}
      />
    </>
  );
}
