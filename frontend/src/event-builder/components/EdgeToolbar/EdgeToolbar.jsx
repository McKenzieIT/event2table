/**
 * EdgeToolbar Component
 * 底部边缘激活栏 - 鼠标靠近底部时从底部滑入
 */
import React, { useState, useCallback } from "react";
import PropTypes from "prop-types";
import EdgeToolbarButton from "./EdgeToolbarButton";
import QuickFieldTools from "./QuickFieldTools";
import FieldSelectorPanel from "../FieldSelectorPanel";

export default function EdgeToolbar({
  canvasFields = [],
  onAddBaseField,
  onAddCustomField,
  onAddFixedField,
  onQuickAddCommon,
  onQuickAddAll,
  onAddField,
}) {
  const [showQuickTools, setShowQuickTools] = useState(false);
  const [showFieldSelector, setShowFieldSelector] = useState(false);

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
    (type) => {
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

EdgeToolbar.propTypes = {
  canvasFields: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      fieldType: PropTypes.string.isRequired,
      fieldName: PropTypes.string,
      name: PropTypes.string.isRequired,
      displayName: PropTypes.string,
      alias: PropTypes.string,
      dataType: PropTypes.string.isRequired,
    }),
  ),
  onAddBaseField: PropTypes.func.isRequired,
  onAddCustomField: PropTypes.func.isRequired,
  onAddFixedField: PropTypes.func.isRequired,
  onQuickAddCommon: PropTypes.func.isRequired,
  onQuickAddAll: PropTypes.func.isRequired,
  onAddField: PropTypes.func.isRequired,
};
